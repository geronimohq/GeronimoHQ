"""Headless application core for the web-window front end (no Tkinter).

Everything here calls the same logic modules the Tk app uses (core_logic, server_browser, geo_estimate, app_config,
updater). The UI talks to this class through web_api.Api. Events (log lines, finished jobs) go out through `emit`.
"""
import concurrent.futures
import threading
import time
from typing import Any, Dict, List, Optional

import app_config
import core_logic
import geo_estimate
import server_browser
import version

REVERT_ALL_SUMMARY = (
    "This undoes:\n"
    "- Game DVR and fullscreen-optimization settings\n"
    "- autoexec.cfg: replaced by autoexec_backup.cfg (your file from before the app's first change; later edits are lost), "
    "or only the app's block is removed if there is no backup\n"
    "- power plan: back to the plan you had before the app changed it\n\n"
    "Not changed here: DNS (use Restore ISP Default), Steam launch options (the original is kept as localconfig.vdf.backup), "
    "deleted cache files."
)

TWEAK_KEYS = ("shaders", "dumps", "gamedvr", "fullscreen", "autoexec")


class Core:
    def __init__(self, emit=None):
        self.emit = emit or (lambda event, data: None)
        self.config: Dict[str, Any] = app_config.load_config()
        self.paths: Dict[str, Optional[str]] = {}
        self.log_buf: List[Dict[str, str]] = []
        self._lock = threading.Lock()
        self._busy: Optional[str] = None
        self._pool = concurrent.futures.ThreadPoolExecutor(max_workers=8, thread_name_prefix="srvq")
        try:
            self.paths = core_logic.find_cs2_paths()
        except Exception:
            self.paths = {}

    # ---------- logging ----------
    def log(self, msg: Any, tag: str = "SYSTEM") -> None:
        entry = {"t": time.strftime("%H:%M:%S"), "tag": tag, "msg": str(msg)}
        with self._lock:
            self.log_buf.append(entry)
            del self.log_buf[:-400]
        self.emit("log", entry)

    def log_history(self) -> List[Dict[str, str]]:
        with self._lock:
            return list(self.log_buf)

    # ---------- app info / settings ----------
    def app_info(self) -> Dict[str, Any]:
        days = None
        try:
            days = app_config.get_days_since_optimization(self.config)
        except Exception:
            pass
        persona = None
        try:
            persona = core_logic.get_steam_active_persona(self.paths.get("steam_path"))
        except Exception:
            pass
        return {
            "version": version.APP_VERSION,
            "build_date": version.BUILD_DATE,
            "admin": bool(core_logic.is_admin()),
            "cs2_found": bool(self.paths.get("cs2_dir")),
            "cfg_dir": self.paths.get("cfg_dir"),
            "persona": persona,
            "days_since_optimization": days,
            "refresh_seconds": int(self.config.get("web_refresh_seconds", 5) or 5),
        }

    def config_set(self, key: str, value: Any) -> bool:
        allowed = {"web_refresh_seconds": (1, 5, 15)}
        if key not in allowed or value not in allowed[key]:
            return False
        self.config[key] = value
        return bool(app_config.save_config(self.config))

    # ---------- servers ----------
    def _china_servers(self) -> List[Dict[str, Any]]:
        out = []
        for c in getattr(server_browser, "CHINA_CLUSTERS", []) or []:
            for s in c.get("servers", []):
                out.append({**s, "region": c.get("region", ""), "cluster": c.get("name", ""), "group": "china"})
        return out

    def servers_catalog(self) -> List[Dict[str, Any]]:
        out = []
        for s in server_browser.get_all_servers():
            out.append({"id": s.get("id"), "name": s.get("name"), "host": s.get("host"), "port": int(s.get("port") or 0),
                        "region": s.get("region") or "", "flag": s.get("flag") or "", "discord": s.get("discord") or "",
                        "featured": bool(s.get("is_featured")), "custom": bool(s.get("is_custom")), "group": "global", "cluster": ""})
        for s in self._china_servers():
            out.append({"id": s["id"], "name": s.get("name"), "host": s["host"], "port": int(s["port"]), "region": s["region"],
                        "flag": "", "discord": "", "featured": False, "custom": False, "group": "china", "cluster": s["cluster"]})
        return out

    def _find_server(self, sid: str) -> Optional[Dict[str, Any]]:
        for s in server_browser.get_all_servers():
            if s.get("id") == sid:
                return s
        for s in self._china_servers():
            if s.get("id") == sid:
                return s
        return None

    @staticmethod
    def _geo_rows(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [{"code": i["code"], "name": i["name"], "pct": i["percentage"], "count": i["count"]} for i in items]

    def server_status(self, sid: str) -> Dict[str, Any]:
        s = self._find_server(sid)
        if not s:
            return {"id": sid, "online": False, "error": "unknown server"}
        info = server_browser.query_server_info(s["host"], int(s["port"]))
        online = bool(info.get("online"))
        total = int(info.get("curr_players") or 0) if online else 0
        bots = min(int(info.get("bots") or 0), total) if online else 0
        humans = max(0, total - bots)
        geo = {"countries": [], "regions": []}
        if online and humans > 0:
            try:
                raw = server_browser.fetch_gfl_continents() if sid == "gfl" else None
                names = server_browser.backend_player_names(sid)
                items = geo_estimate.estimate_countries(s.get("region") or "", humans, names, (raw or {}).get("raw") if raw else None)
                geo = {"countries": self._geo_rows(items), "regions": self._geo_rows(geo_estimate.estimate_regions(items))}
            except Exception:
                pass
        return {"id": sid, "online": online, "map": info.get("map") if online else None, "players": total, "bots": bots,
                "humans": humans, "max": int(info.get("max_players") or 0), "ping": info.get("rtt") if online else None,
                "name_live": info.get("server_name") if online else None, "geo": geo, "at": time.time()}

    def servers_status_many(self, ids: List[str]) -> List[Dict[str, Any]]:
        return list(self._pool.map(lambda i: self._safe_status(i), ids))

    def _safe_status(self, sid: str) -> Dict[str, Any]:
        try:
            return self.server_status(sid)
        except Exception as e:  # one bad server never breaks the refresh
            return {"id": sid, "online": False, "error": str(e)}

    def gfl_match(self) -> Dict[str, Any]:
        try:
            m = server_browser.query_zegraph_match_now()
            return {"human_score": m.get("human_score", 0), "zombie_score": m.get("zombie_score", 0),
                    "extend_count": m.get("extend_count", 0), "started_sec": m.get("started_sec", 0), "map": m.get("map", "")}
        except Exception:
            return {}

    def servers_totals(self) -> Dict[str, Any]:
        try:
            t = server_browser.get_shared_totals()
            return {"humans": t.get("humans", 0), "bots": t.get("bots", 0), "online": t.get("online_servers", 0), "total": t.get("total_servers", 0)}
        except Exception:
            return {}

    def servers_add(self, name: str, host: str, port: int) -> Dict[str, Any]:
        name = (name or "").strip()
        if not name or not server_browser.validate_server_address(host, port):
            return {"ok": False, "error": "Enter a name and a valid host and port."}
        customs = [s for s in server_browser.get_all_servers() if s.get("is_custom")]
        sid = f"custom_{str(host).replace('.', '_')}_{int(port)}"
        if any(s.get("id") == sid for s in customs):
            return {"ok": False, "error": "That server is already in your list."}
        customs.append({"id": sid, "name": name, "host": str(host), "port": int(port), "flag": "", "region": "", "is_custom": True})
        ok = server_browser.save_servers(customs)
        self.log(f"Server saved: {name}", "SERVERS")
        return {"ok": bool(ok)}

    def servers_remove(self, sid: str) -> bool:
        customs = [s for s in server_browser.get_all_servers() if s.get("is_custom") and s.get("id") != sid]
        return bool(server_browser.save_servers(customs))

    # ---------- engine tweaks ----------
    def engine_state(self) -> Dict[str, Any]:
        plan = ("Balanced", "")
        try:
            plan = core_logic.get_active_power_plan()
        except Exception:
            pass
        auto = None
        try:
            auto = core_logic.get_autoexec_status(self.paths.get("cfg_dir"), self.config.get("autoexec_last_app_save"))
        except Exception:
            pass
        return {"power_plan": plan[0], "autoexec": auto, "cs2_found": bool(self.paths.get("cs2_dir")),
                "cs2_exe": bool(self.paths.get("cs2_exe")), "cfg_dir": bool(self.paths.get("cfg_dir"))}

    def _start_job(self, name: str, fn) -> Dict[str, Any]:
        with self._lock:
            if self._busy:
                return {"ok": False, "error": f"'{self._busy}' is still running."}
            self._busy = name

        def run():
            ok = True
            try:
                fn()
            except Exception as e:
                ok = False
                self.log(f"[ERROR] {name}: {e}")
            finally:
                with self._lock:
                    self._busy = None
                self.emit("job", {"name": name, "ok": ok})

        threading.Thread(target=run, daemon=True, name=f"job-{name}").start()
        return {"ok": True}

    def engine_apply(self, opts: Dict[str, Any]) -> Dict[str, Any]:
        opts = opts or {}

        def task():
            self.log("--- Starting optimization ---")
            if opts.get("gamedvr"):
                for l in core_logic.optimize_windows_game_dvr():
                    self.log(l)
            if opts.get("fullscreen") and self.paths.get("cs2_exe"):
                for l in core_logic.disable_fullscreen_optimizations(self.paths["cs2_exe"]):
                    self.log(l)
            if opts.get("autoexec") and self.paths.get("cfg_dir"):
                _ok, logs = core_logic.install_autoexec(self.paths["cfg_dir"])
                for l in logs:
                    self.log(l)
            plan = opts.get("power")
            if plan in ("balanced", "high"):
                core_logic.remember_power_plan(self.config)
                app_config.save_config(self.config)
                for l in core_logic.set_power_plan("balanced" if plan == "balanced" else "high"):
                    self.log(l)
            if opts.get("shaders"):
                files, freed, logs = core_logic.clean_shader_caches()
                for l in logs:
                    self.log(l)
                self.log(f"Shader cache purge: {files} files cleaned ({freed / (1024 * 1024):.2f} MB freed).")
            if opts.get("dumps"):
                _f, _b, logs = core_logic.clean_cs2_temp_dumps(self.paths.get("cs2_dir"))
                for l in logs:
                    self.log(l)
            app_config.update_optimization_timestamp(self.config)
            self.log("--- Optimization completed ---")

        return self._start_job("engine_apply", task)

    def engine_restore(self) -> Dict[str, Any]:
        def task():
            self.log("--- Restoring defaults ---")
            for l in core_logic.revert_windows_game_dvr():
                self.log(l)
            if self.paths.get("cs2_exe"):
                for l in core_logic.revert_fullscreen_optimizations(self.paths["cs2_exe"]):
                    self.log(l)
            if self.paths.get("cfg_dir"):
                _ok, logs = core_logic.restore_autoexec_backup(self.paths["cfg_dir"])
                for l in logs:
                    self.log(l)
            for l in core_logic.restore_previous_power_plan(self.config):
                self.log(l)
            app_config.save_config(self.config)
            self.log("--- Restore finished (see the lines above for each step) ---")

        return self._start_job("engine_restore", task)

    def power_set(self, plan: str) -> Dict[str, Any]:
        if plan not in ("balanced", "high"):
            return {"ok": False}
        core_logic.remember_power_plan(self.config)
        app_config.save_config(self.config)
        for l in core_logic.set_power_plan(plan):
            self.log(l)
        return {"ok": True, "plan": core_logic.get_active_power_plan()[0]}

    def restore_summary(self) -> str:
        return REVERT_ALL_SUMMARY
