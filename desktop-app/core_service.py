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
        self._maps: Dict[str, Dict[str, Any]] = {}
        import presence_service
        self.presence = presence_service.PresenceService(self)      # created here, started by web_main (no threads in tests)
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
            "refresh_seconds": self._refresh_seconds(),
        }

    def config_set(self, key: str, value: Any) -> bool:
        """Only the list refresh speed can be set from the page (1, 5 or 15 seconds); it shares the classic app's setting."""
        names = {1: "Live (1s)", 5: "Normal (5s)", 15: "Eco (15s)"}
        if key != "web_refresh_seconds" or value not in names:
            return False
        self.config["server_refresh_speed"] = names[value]
        return bool(app_config.save_config(self.config))

    # ---------- servers ----------
    def _china_servers(self) -> List[Dict[str, Any]]:
        out = []
        for c in getattr(server_browser, "CHINA_CLUSTERS", []) or []:
            for s in c.get("servers", []):
                out.append({**s, "region": c.get("region", ""), "cluster": c.get("name", ""), "cluster_id": c.get("id", ""), "cluster_desc": c.get("description", ""), "group": "china"})
        return out

    def servers_catalog(self) -> List[Dict[str, Any]]:
        out = []
        for s in server_browser.get_all_servers():
            out.append({"id": s.get("id"), "name": s.get("name"), "host": s.get("host"), "port": int(s.get("port") or 0),
                        "region": s.get("region") or "", "flag": s.get("flag") or "", "discord": s.get("discord") or "", "website": s.get("website") or "",
                        "featured": bool(s.get("is_featured")), "custom": bool(s.get("is_custom")), "group": "global", "cluster": ""})
        for s in self._china_servers():
            out.append({"id": s["id"], "name": s.get("name"), "host": s["host"], "port": int(s["port"]), "region": s["region"],
                        "flag": "", "discord": "", "website": "", "featured": False, "custom": False, "group": "china", "cluster": s["cluster"],
                        "cluster_id": s.get("cluster_id", ""), "cluster_desc": s.get("cluster_desc", "")})
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
        cur_map = info.get("map") if online else None
        since, exact = self._map_clock(sid, cur_map, s["host"], int(s["port"]), humans)
        return {"id": sid, "online": online, "map": cur_map, "players": total, "bots": bots,
                "humans": humans, "max": int(info.get("max_players") or 0), "ping": info.get("rtt") if online else None,
                "name_live": info.get("server_name") if online else None, "geo": geo, "at": time.time(),
                "map_since": since, "map_exact": exact}

    @staticmethod
    def _probe_map_start(c: Dict[str, Any], host: str, port: int) -> None:
        try:
            r = server_browser.query_server_players(host, port)
            durs = [int(p.get("seconds") or 0) for p in (r.get("players") or []) if int(p.get("seconds") or 0) > 0]
            if durs:
                now = time.time()
                est = now - max(durs)
                if abs(est - c["start"]) > 30 or not c["exact"]:
                    c["start"], c["exact"] = est, True
        except Exception:
            pass
        finally:
            c["probing"] = False

    def _map_clock(self, sid: str, cur_map: Optional[str], host: Optional[str] = None, port: int = 0, humans: int = 0):
        """Per-server map start, kept for the life of the app (like 1.6.0): exact once a map change was seen,
        otherwise a lower bound from the first sighting. GFL uses the ZE Graph start time."""
        clocks = self.__dict__.setdefault("_map_clocks", {})
        if not cur_map:
            return 0, False
        c = clocks.get(sid)
        changed = c is None or c["map"] != cur_map
        if changed:
            c = {"map": cur_map, "start": time.time(), "exact": c is not None, "probed": 0.0, "probing": False}
            clocks[sid] = c
        # A player's connection time restarts on a map change, so the longest one is how long the map has run
        # (the website backend uses the same rule). Checked in the background on a new map and then every minute.
        if host and humans > 0 and not c["probing"] and time.time() - c["probed"] > (0 if changed else 60):
            c["probing"] = True
            c["probed"] = time.time()
            threading.Thread(target=self._probe_map_start, args=(c, host, port), daemon=True, name="map-clock").start()
        if sid == "gfl":
            try:
                m = server_browser.query_zegraph_match_now()
                ts = int(m.get("started_timestamp") or 0)
                if m.get("success") and ts > 0 and m.get("map") == cur_map:
                    return ts, True
            except Exception:
                pass
        return c["start"], c["exact"]

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
                    "extend_count": m.get("extend_count", 0), "started_sec": m.get("started_timestamp", 0) if m.get("success") else 0, "map": m.get("map", "")}
        except Exception:
            return {}

    def servers_totals(self) -> Dict[str, Any]:
        try:
            t = server_browser.get_shared_totals()
            return {"humans": t.get("humans", 0), "bots": t.get("bots", 0), "online": t.get("online_servers", 0), "total": t.get("total_servers", 0)}
        except Exception:
            return {}

    def servers_add(self, name: str, host: str, port: int, region: str = "Community") -> Dict[str, Any]:
        name = (name or "").strip()
        if not name or not server_browser.validate_server_address(host, port):
            return {"ok": False, "error": "Enter a name and a valid host and port."}
        customs = [s for s in server_browser.get_all_servers() if s.get("is_custom")]
        sid = f"custom_{str(host).replace('.', '_')}_{int(port)}"
        if any(s.get("id") == sid for s in customs):
            return {"ok": False, "error": "That server is already in your list."}
        customs.append({"id": sid, "name": name, "host": str(host), "port": int(port), "flag": "", "region": str(region or "Community")[:40], "is_custom": True})
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

    # ---------- server actions ----------
    def server_connect(self, sid: str) -> Dict[str, Any]:
        s = self._find_server(sid)
        if not s:
            return {"ok": False, "error": "Unknown server."}
        server_browser.connect_to_server(s["host"], int(s["port"]), s.get("name") or sid,
                                         log_callback=lambda m: self.log(m, "SERVERS"),
                                         completion_callback=lambda ok, msg: self.emit("connect", {"id": sid, "ok": ok, "msg": msg}))
        return {"ok": True}

    def server_players(self, sid: str) -> Dict[str, Any]:
        s = self._find_server(sid)
        if not s:
            return {"success": False, "players": [], "error": "Unknown server."}
        r = server_browser.query_server_players(s["host"], int(s["port"]))
        return {"success": bool(r.get("success")), "players": r.get("players", []), "error": r.get("error", ""), "name": s.get("name")}

    GFL_TIERS = {"normal": 61, "mapper": 62, "vip": 63}

    def sniper_tiers(self) -> Dict[str, Any]:
        raw = str(self.config.get("community_sniper_slot_target", "63"))
        comm = next((n for n in ("61", "62", "63") if n in raw), "63")
        gfl = self.config.get("gfl_sniper_tier", "mapper")
        return {"gfl": gfl if gfl in self.GFL_TIERS else "mapper", "community": comm}

    def sniper_set_tier(self, kind: str, value: str) -> Dict[str, Any]:
        if kind == "gfl" and value in self.GFL_TIERS:
            self.config["gfl_sniper_tier"] = value
        elif kind == "community" and str(value) in ("61", "62", "63"):
            self.config["community_sniper_slot_target"] = str(value)
        else:
            return {"ok": False}
        app_config.save_config(self.config)
        self.log(f"[SNIPER] {'GFL slot priority' if kind == 'gfl' else 'Sniper target'} set to {value}", "SERVERS")
        return self.sniper_tiers() | {"ok": True}

    def sniper_start(self, sid: str, max_players: Optional[int] = None) -> Dict[str, Any]:
        s = self._find_server(sid)
        if not s:
            return {"ok": False}
        tiers = self.sniper_tiers()
        max_players = self.GFL_TIERS[tiers["gfl"]] if sid == "gfl" else int(tiers["community"])
        if not core_logic.is_cs2_running():       # same rule as the classic app
            return {"ok": False, "error": "Counter-Strike 2 must be running to arm the Slot Sniper.\n\nLaunch CS2 first (or click Connect to open it), then arm the sniper. It watches the server and joins the moment a player leaves."}
        info = server_browser.query_server_info(s["host"], int(s["port"]))
        full = bool(info.get("online")) and int(info.get("curr_players") or 0) >= int(info.get("max_players") or 64)
        server_browser.get_slot_sniper().start(
            s["host"], int(s["port"]), s.get("name") or sid, target_max_players=int(max_players), tier_label="",
            status_cb=lambda state, text: self.emit("sniper", self.sniper_status()),
            success_cb=lambda h, p, n, cur, mx: self._sniper_fired(h, p, n, cur, mx, max_players), initial_is_full=full)
        try:
            if self.config.get("discord_rpc_enabled", True) and self.presence.rpc.connected:
                self.presence.rpc.set_activity(details=f"Sniping {s.get('name') or sid}", state=f"Active (Target: <={max_players})", start_timestamp=int(time.time()), large_image=None)
        except Exception:
            pass
        self.log(f"Slot Sniper armed for {s.get('name')} (join at <= {int(max_players)})", "SERVERS")
        return {"ok": True}

    def sniper_stop(self) -> Dict[str, Any]:
        server_browser.get_slot_sniper().stop()
        self.log("Slot Sniper disarmed", "SERVERS")
        return {"ok": True}

    def sniper_status(self) -> Dict[str, Any]:
        st = server_browser.get_slot_sniper().get_status()
        text, state = server_browser.sniper_status_bar(st)
        return {"text": text, "state": state, "target": st.get("target_name") or "", "active": bool(st.get("is_active"))}

    # ---------- dashboard, files, links, admin ----------
    def dashboard(self) -> Dict[str, Any]:
        cs2_dir = self.paths.get("cs2_dir") or self.paths.get("cs2_exe")
        drive = None
        if cs2_dir:
            letter = (cs2_dir[:2] or "").upper()
            for d in core_logic.get_drives_info():
                if d["drive"].upper().startswith(letter):
                    drive = d
        auto = None
        try:
            auto = core_logic.get_autoexec_status(self.paths.get("cfg_dir"), self.config.get("autoexec_last_app_save"))
        except Exception:
            pass
        return {"cs2_dir": self.paths.get("cs2_dir"), "cfg_dir": self.paths.get("cfg_dir"), "autoexec": auto, "drive": drive,
                "days_opt": app_config.get_days_since_optimization(self.config), "days_maint": app_config.get_days_since_maintenance(self.config)}

    def open_path(self, kind: str) -> bool:
        import os
        target = {"cfg": self.paths.get("cfg_dir"), "appdata": app_config.get_storage_dir()}.get(kind)
        if not target or not os.path.isdir(target):
            return False
        os.startfile(target)
        return True

    def open_url(self, url: str) -> bool:
        import os
        import webbrowser
        if not isinstance(url, str) or not url.startswith(("https://", "http://", "steam://")):
            return False
        try:
            if url.startswith("steam://"):
                os.startfile(url)
            else:
                webbrowser.open(url)
            return True
        except Exception:
            return False

    def relaunch_admin(self, page: str = "") -> Dict[str, Any]:
        """Asks Windows (UAC) to start an elevated copy that opens on `page`. The caller closes this copy when ok is true."""
        import ctypes
        import os
        import re
        import sys
        page = page if re.fullmatch(r"[a-z]{3,12}", str(page or "")) else ""
        extra = f"--elevated --page={page}" if page else "--elevated"
        exe = sys.executable
        if getattr(sys, "frozen", False):
            params = extra
        else:
            params = '"' + os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_main.py") + '" ' + extra
        try:
            app_config.save_config(self.config)
        except Exception:
            pass
        ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, 1)
        if ret > 32:
            return {"ok": True}
        self.log("[ADMIN] Elevation request was cancelled or declined. Continuing in standard mode.")
        return {"ok": False}

    # ---------- PC maintenance ----------
    def maint_state(self) -> Dict[str, Any]:
        return {"drives": core_logic.get_drives_info(), "admin": bool(core_logic.is_admin()),
                "days_maint": app_config.get_days_since_maintenance(self.config)}

    def maint_run(self, opts: Dict[str, Any]) -> Dict[str, Any]:
        opts = opts or {}

        def task():
            self.log("--- Starting PC cleanup ---")
            total = {"files": 0, "bytes": 0}

            def tally(res):
                files, nbytes, logs = res
                total["files"] += files
                total["bytes"] += nbytes
                for l in logs:
                    self.log(l)

            if opts.get("temp"):
                tally(core_logic.clean_windows_temp_files())
            if opts.get("win_update"):
                tally(core_logic.clean_windows_update_cache())
            if opts.get("discord_steam"):
                tally(core_logic.clean_discord_and_steam_cache(self.paths.get("steam_path")))
            if opts.get("thumb"):
                tally(core_logic.clean_explorer_thumbnail_cache())
            if opts.get("recycle"):
                _ok, logs = core_logic.empty_recycle_bin()
                for l in logs:
                    self.log(l)
            if opts.get("dns"):
                _ok, logs = core_logic.flush_dns_cache()
                for l in logs:
                    self.log(l)
            app_config.update_maintenance_timestamp(self.config)
            self.log(f"--- Cleanup finished: {total['files']} files, {total['bytes'] / (1024 * 1024):.1f} MB freed ---")

        return self._start_job("maint_run", task)

    def maint_tool(self, name: str) -> Dict[str, Any]:
        tools = {"cleanmgr": core_logic.launch_cleanmgr, "trim": core_logic.run_ssd_trim, "startup": core_logic.open_startup_apps,
                 "sfc": core_logic.run_sfc_scan, "dism": core_logic.run_dism_restore, "winsxs": core_logic.run_dism_component_cleanup}
        fn = tools.get(name)
        if not fn:
            return {"ok": False, "error": "Unknown tool."}
        if name in ("trim", "sfc", "dism", "winsxs") and not core_logic.is_admin():
            self.log("[ADMIN REQUIRED] This repair tool needs Administrator. Use Relaunch as Administrator.")
            return {"ok": False, "error": "Administrator is required for this tool."}

        def task():
            res = fn()
            logs = res[1] if isinstance(res[1], list) else [res[1]]
            for l in logs:
                self.log(l)

        return self._start_job(f"maint_{name}", task)

    # ---------- launch options ----------
    def launch_state(self) -> Dict[str, Any]:
        import hardware_info
        cur, vdf = hardware_info.get_current_launch_options(self.paths.get("steam_path"))
        analysis = hardware_info.analyze_launch_options(cur or "")
        return {"current": cur or "", "vdf_found": bool(vdf), "warnings": analysis.get("warnings", []),
                "recommended": analysis.get("recommended", ""), "suggestions": analysis.get("suggestions", [])}

    def launch_save(self, options: str) -> Dict[str, Any]:
        import hardware_info
        _cur, vdf = hardware_info.get_current_launch_options(self.paths.get("steam_path"))
        if not vdf:
            return {"ok": False, "error": "Steam localconfig.vdf was not found."}
        ok, logs = core_logic.save_launch_options(vdf, (options or "").strip())
        for l in logs:
            self.log(l)
        return {"ok": bool(ok)}

    # ---------- live booster & DNS ----------
    def boost_run(self) -> Dict[str, Any]:
        ok, msg = core_logic.boost_cs2_process()
        self.log(msg)
        return {"ok": bool(ok), "msg": msg}

    def cs2_running(self) -> bool:
        try:
            return bool(core_logic.is_cs2_running())
        except Exception:
            return False

    def dns_state(self) -> Dict[str, Any]:
        iface = core_logic.get_active_network_interface()
        return {"interface": iface.get("interface_name"), "current": iface.get("current_dns"), "found": bool(iface.get("found")),
                "providers": [dict(p) for p in core_logic.DNS_PROVIDERS], "admin": bool(core_logic.is_admin())}

    def dns_benchmark(self) -> Dict[str, Any]:
        def task():
            self.log("Benchmarking gaming DNS providers...")
            res = core_logic.benchmark_all_dns_providers()
            self.emit("dns_results", [{"name": r.get("name"), "primary": r.get("primary"), "secondary": r.get("secondary"),
                                       "avg_ms": round(float(r.get("avg_ms", 0)), 1), "jitter_ms": round(float(r.get("jitter_ms", 0)), 1),
                                       "reachable": bool(r.get("reachable")), "fastest": bool(r.get("is_fastest")), "rank": r.get("rank")} for r in res])
            self.log("DNS benchmark finished.")

        return self._start_job("dns_benchmark", task)

    def dns_apply(self, primary: str, secondary: str, name: str) -> Dict[str, Any]:
        if not core_logic.is_admin():
            return {"ok": False, "error": "Changing DNS needs Administrator. Use Relaunch as Administrator."}
        ok, logs = core_logic.apply_dns_provider(primary, secondary, name)
        for l in logs:
            self.log(l)
        return {"ok": bool(ok)}

    def dns_restore(self) -> Dict[str, Any]:
        if not core_logic.is_admin():
            return {"ok": False, "error": "Changing DNS needs Administrator. Use Relaunch as Administrator."}
        ok, logs = core_logic.restore_dns_to_dhcp()
        for l in logs:
            self.log(l)
        return {"ok": bool(ok)}

    # ---------- autoexec ----------
    def autoexec_state(self) -> Dict[str, Any]:
        import os
        st = core_logic.get_autoexec_status(self.paths.get("cfg_dir"), self.config.get("autoexec_last_app_save"))
        text = ""
        if st.get("path") and os.path.isfile(st["path"]):
            try:
                with open(st["path"], "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()[:60000]
            except Exception:
                pass
        personal = None
        try:
            personal = core_logic.detect_personal_viewmodel_in_autoexec(self.paths.get("cfg_dir"))
        except Exception:
            pass
        return {"state": st.get("state"), "status": st.get("text"), "path": st.get("path"), "text": text, "cfg": bool(self.paths.get("cfg_dir")),
                "cfg_dir": self.paths.get("cfg_dir"), "personal_vm": bool(personal and personal.get("has_personal_viewmodel")),
                "personal_lines": (personal or {}).get("lines", [])}

    def autoexec_install(self) -> Dict[str, Any]:
        if not self.paths.get("cfg_dir"):
            return {"ok": False, "error": "CS2 cfg folder not found."}
        ok, logs = core_logic.install_autoexec(self.paths["cfg_dir"])
        for l in logs:
            self.log(l)
        return {"ok": bool(ok)}

    def autoexec_restore(self) -> Dict[str, Any]:
        if not self.paths.get("cfg_dir"):
            return {"ok": False, "error": "CS2 cfg folder not found."}
        ok, logs = core_logic.restore_autoexec_backup(self.paths["cfg_dir"])
        for l in logs:
            self.log(l)
        return {"ok": bool(ok)}

    def autoexec_fps(self, fps: int) -> Dict[str, Any]:
        if not self.paths.get("cfg_dir"):
            return {"ok": False, "error": "CS2 cfg folder not found."}
        fps = int(fps)
        if not (0 <= fps <= 1000):
            return {"ok": False, "error": "Enter an FPS limit from 0 (unlimited) to 1000."}
        ok, logs = core_logic.set_framerate_limit(self.paths["cfg_dir"], fps)
        for l in logs:
            self.log(l)
        return {"ok": bool(ok)}

    # ---------- GPU / MPO ----------
    def mpo_state(self) -> Dict[str, Any]:
        import hardware_info
        gpu = hardware_info.get_gpu_info()
        diag = hardware_info.get_mpo_diagnostic(gpu.get("name", ""))
        return {"gpu": gpu.get("name"), "vendor": "NVIDIA" if gpu.get("is_nvidia") else "AMD" if gpu.get("is_amd") else "Intel" if gpu.get("is_intel") else "Other",
                "disabled": bool(diag.get("disabled")), "badge": str(diag.get("badge") or "").strip("[]"), "detail": diag.get("detail"), "reg_path": diag.get("reg_path")}

    # ---------- settings ----------
    SETTING_KEYS = tuple(app_config.SETTINGS_DEFAULTS.keys())

    def settings_get(self) -> Dict[str, Any]:
        vals = {k: self.config.get(k, d) for k, d in app_config.SETTINGS_DEFAULTS.items()}
        vals["speeds"] = list(app_config.REFRESH_SPEED_MS.keys())
        vals["pages"] = sorted(app_config.START_PAGES)
        return vals

    def settings_save(self, values: Dict[str, Any]) -> Dict[str, Any]:
        app_config.apply_settings(self.config, values or {})
        try:
            app_config.set_windows_startup(bool(self.config.get("start_with_windows")), bool(self.config.get("start_minimized")))
        except Exception as e:
            self.log(f"[SETTINGS] Windows startup could not be updated: {e}")
        ok = bool(app_config.save_config(self.config))
        self.log("Settings saved" if ok else "[SETTINGS] Settings could not be saved")
        return {"ok": ok, "refresh_seconds": self._refresh_seconds()}

    def settings_reset(self) -> Dict[str, Any]:
        app_config.reset_settings(self.config)
        ok = bool(app_config.save_config(self.config))
        self.log("Settings reset to defaults")
        return {"ok": ok}

    def _refresh_seconds(self) -> int:
        return max(1, int(app_config.refresh_interval_ms(self.config) / 1000))

    # ---------- lifecycle ----------
    PAGE_KEYS = {"dashboard": "DASHBOARD", "engine": "ENGINE", "mpo": "OS_DIAGNOSTICS", "autoexec": "AUTOEXEC", "launch": "LAUNCH",
                 "booster": "BOOST", "servers": "SERVERS", "maintenance": "MAINTENANCE", "discord": "DISCORD", "faq": "FAQ"}

    def set_last_page(self, page: str) -> None:
        key = self.PAGE_KEYS.get(page)
        if key:
            self.config["last_page_key"] = key

    def start_page(self) -> str:
        import re
        import sys
        for a in sys.argv[1:]:                       # an elevated relaunch resumes the tab you were on
            m = re.fullmatch(r"--page=([a-z]{3,12})", a)
            if m and m.group(1) in self.PAGE_KEYS:
                return m.group(1)
        if self.config.get("open_on_page") == "Last used page":
            inv = {v: k for k, v in self.PAGE_KEYS.items()}
            return inv.get(self.config.get("last_page_key"), "dashboard")
        return "dashboard"

    def shutdown(self) -> None:
        """Saves the last page and, only on the owner's install (presence_secret set), tells the website the app went offline."""
        try:
            app_config.save_config(self.config)
        except Exception:
            pass
        try:
            server_browser.get_slot_sniper().stop()
        except Exception:
            pass
        try:
            self.presence.stop()
        except Exception:
            pass
        secret = str(self.config.get("presence_secret", "") or "").strip()
        if secret:
            try:
                import urllib.request
                req = urllib.request.Request(
                    "https://geronimohq-telemetry.onrender.com/api/presence/heartbeat?is_cs2_running=false&is_steam_running=false",
                    headers={"User-Agent": "CS2CommandCenter/2.0", "X-Geronimo-Token": secret})
                urllib.request.urlopen(req, timeout=1.5)
            except Exception:
                pass

    # ---------- custom map cleaner ----------
    COMMUNITIES = ("gfl", "possession", "rss", "mapeadores_cola")

    def maps_settings(self) -> Dict[str, Any]:
        comms = self.config.get("cleaner_protected_comms", list(self.COMMUNITIES))
        return {"communities": [c for c in self.COMMUNITIES if c in comms], "protect_recent": bool(self.config.get("cleaner_protect_recent", True))}

    def maps_scan(self, communities: List[str], protect_recent: bool) -> Dict[str, Any]:
        import custom_map_cleaner
        comms = [c for c in (communities or []) if c in self.COMMUNITIES]
        self.config["cleaner_protected_comms"] = comms
        self.config["cleaner_protect_recent"] = bool(protect_recent)
        app_config.save_config(self.config)

        def task():
            items = custom_map_cleaner.scan_custom_maps(self.paths.get("steam_path"), self.paths.get("cs2_dir"), set(comms), bool(protect_recent))
            with self._lock:
                self._maps = {str(m.get("id")): m for m in items}      # the ONLY source of paths for delete/backup (never trust the page)
            rows = [{"id": str(m.get("id")), "name": m.get("name"), "status": m.get("status_label"), "type": m.get("status_type"),
                     "sub": bool(m.get("is_subscribed")), "asset": bool(m.get("is_server_asset")), "protected": bool(m.get("is_protected")),
                     "workshop": bool(m.get("is_workshop")), "dupe": bool(m.get("has_duplicate")), "size": int(m.get("size_bytes") or 0),
                     "size_str": m.get("size_str"), "mtime": m.get("mtime_str")} for m in items]
            self.emit("maps", rows)
            self.log(f"Map scan found {len(rows)} custom maps", "SYSTEM")

        return self._start_job("maps_scan", task)

    def maps_delete(self, ids: List[str]) -> Dict[str, Any]:
        import custom_map_cleaner
        with self._lock:
            items = [self._maps[i] for i in (ids or []) if i in getattr(self, "_maps", {})]
        if not items:
            return {"ok": False, "error": "Nothing selected."}

        def task():
            count, freed, logs = custom_map_cleaner.delete_custom_maps(items)
            for l in logs:
                self.log(l)
            self.log(f"[MAP CLEANER] Deleted {count} custom maps. Freed {freed / (1024 ** 3):.2f} GB.")
            self.emit("maps_deleted", {"count": count, "freed": freed})

        return self._start_job("maps_delete", task)

    def _vpk_backup_dir(self) -> str:
        import os
        return os.path.join(app_config.get_storage_dir(), "backups", "custom_assets")

    def maps_backup(self) -> Dict[str, Any]:
        import os
        import shutil
        dest = self._vpk_backup_dir()
        os.makedirs(dest, exist_ok=True)
        copied = 0
        for m in list(getattr(self, "_maps", {}).values()):
            if m.get("is_server_asset") or "3793587501" in str(m.get("id")):
                folder = m.get("path")
                if folder and os.path.isdir(folder):
                    for fl in os.listdir(folder):
                        if fl.endswith(".vpk"):
                            shutil.copy2(os.path.join(folder, fl), os.path.join(dest, f"{m['id']}_{fl}"))
                            copied += 1
        self.log(f"[BACKUP] Backed up {copied} custom server asset VPK(s) to {dest}")
        return {"ok": True, "count": copied, "dir": dest}

    def maps_restore(self) -> Dict[str, Any]:
        import os
        import shutil
        src_dir = self._vpk_backup_dir()
        if not os.path.isdir(src_dir) or not os.listdir(src_dir):
            return {"ok": True, "count": 0}
        restored = 0
        maps = getattr(self, "_maps", {})
        for f in os.listdir(src_dir):
            if f.endswith(".vpk") and "_" in f:
                wid, vpk_name = f.split("_", 1)
                m = maps.get(wid)
                if m and m.get("path") and os.path.isdir(m["path"]):
                    shutil.copy2(os.path.join(src_dir, f), os.path.join(m["path"], vpk_name))
                    restored += 1
        self.log(f"[RESTORE] Restored {restored} custom asset VPK(s)")
        return {"ok": True, "count": restored}

    # ---------- discord presence ----------
    def presence_state(self) -> Dict[str, Any]:
        return self.presence.snapshot()

    def presence_toggle(self, enabled: bool) -> Dict[str, Any]:
        self.config["discord_rpc_enabled"] = bool(enabled)
        app_config.save_config(self.config)
        if not enabled:
            self.presence.clear()
        return self.presence.snapshot()

    def presence_clear(self) -> Dict[str, Any]:
        self.presence.clear()
        return self.presence.snapshot()

    def presence_standby(self) -> Dict[str, Any]:
        self.presence.standby()
        return self.presence.snapshot()

    def presence_broadcast(self, sid: str) -> Dict[str, Any]:
        s = self._find_server(sid)
        if not s:
            return {"ok": False, "error": "Unknown server."}
        return self.presence.broadcast(s["host"], int(s["port"]), s.get("name") or sid)

    # ---------- updates (signed manifest, same updater module as the classic app) ----------
    def update_check(self, manual: bool = False) -> Dict[str, Any]:
        import updater
        if not manual and not self.config.get("check_updates_on_startup", True):
            return {"available": False, "message": "Update checks are turned off in Settings."}
        try:
            avail, manifest, msg = updater.fetch_update_manifest(current_ver=version.APP_VERSION)
        except Exception as e:
            return {"available": False, "message": f"Could not check for updates: {e}"}
        self.config["last_update_check_time"] = time.strftime("%Y-%m-%d %H:%M")
        app_config.save_config(self.config)
        if not (avail and manifest):
            return {"available": False, "message": msg or "You are up to date.", "last": self.config["last_update_check_time"]}
        self._pending_manifest = manifest
        skipped = manifest["version"] == self.config.get("skipped_update_version") and not manual
        return {"available": not skipped, "version": manifest["version"], "notes": manifest.get("notes", ""), "size": manifest.get("size", 0),
                "message": f"Update available: v{manifest['version']}", "last": self.config["last_update_check_time"]}

    def update_check_startup(self) -> None:
        """Background check at startup; tells the page only when there is something to show."""
        def run():
            r = self.update_check(manual=False)
            if r.get("available"):
                self.emit("update", r)
        threading.Thread(target=run, daemon=True, name="update-check").start()

    def update_skip(self, ver: str) -> bool:
        self.config["skipped_update_version"] = str(ver)
        return bool(app_config.save_config(self.config))

    def update_install(self) -> Dict[str, Any]:
        import os
        import sys
        import updater
        manifest = getattr(self, "_pending_manifest", None)
        if not manifest:
            return {"ok": False, "error": "No update is waiting. Check for updates first."}
        if not getattr(sys, "frozen", False):
            return {"ok": False, "error": "Updates install only in the packaged app."}
        server_browser.get_slot_sniper().stop()
        curr = os.path.abspath(sys.executable)
        new = curr + ".new"

        def task():
            self.log(f"[UPDATE] Downloading v{manifest['version']}...")
            ok, msg = updater.download_and_verify_binary(manifest, new)
            if not ok:
                self.log(f"[UPDATE ERROR] {msg}")
                raise RuntimeError(msg)
            self.log("[UPDATE] Download verified (size, SHA-256 and signature). Applying...")
            self.shutdown()
            updater.spawn_updater_helper_and_exit(curr, new)

        return self._start_job("update_install", task)

    # ---------- hardware banner ----------
    def hw_info(self) -> Dict[str, Any]:
        import hardware_info
        cpu, gpu = hardware_info.get_cpu_info(), hardware_info.get_gpu_info()
        tag = " [3D V-Cache Detected]" if cpu.get("is_x3d") else (" [Mobile]" if cpu.get("is_laptop") else "")
        return {"cpu": f"{cpu.get('name', '')}{tag}", "gpu": gpu.get("name", ""), "profile": cpu.get("power_reason", ""),
                "recommended_plan": "high" if str(cpu.get("recommended_power_plan", "")).lower().startswith("high") else "balanced"}

    # ---------- ZE customizer + manual autoexec edit ----------
    def ze_customizer(self, opts: Dict[str, Any]) -> Dict[str, Any]:
        opts = opts or {}
        try:
            hud = int(str(opts.get("hud_color", 0)).split()[0])
        except Exception:
            hud = 0
        clean = {"ze_laser_viewmodel": bool(opts.get("ze_laser_viewmodel", True)), "clean_telemetry_hud": bool(opts.get("clean_telemetry_hud", True)),
                 "hud_color": max(0, min(12, hud)), "hud_scale": 0.90, "radar_zoom": 0.40,
                 "duck_key": str(opts.get("duck_key") or "F7").strip()[:20], "voice_mute_key": str(opts.get("voice_mute_key") or "F8").strip()[:20]}
        res = core_logic.apply_ze_visual_and_hud_customizer(self.paths.get("cfg_dir"), clean)
        if isinstance(res, tuple):
            ok, logs = res
            res = {"success": ok, "message": logs[-1] if logs else "Updated autoexec.cfg", "logs": logs}
        self.log(f"[ZE CUSTOMIZER] {res.get('message')}")
        return {"ok": bool(res.get("success")), "message": res.get("message", ""), "keys": [clean["duck_key"], clean["voice_mute_key"]], "hud": clean["hud_color"], "vm": clean["ze_laser_viewmodel"]}

    def autoexec_save(self, text: str) -> Dict[str, Any]:
        import os
        import shutil
        cfg = self.paths.get("cfg_dir")
        if not cfg:
            return {"ok": False, "error": "Cannot locate the CS2 cfg folder."}
        path = os.path.join(cfg, "autoexec.cfg")
        try:
            if os.path.exists(path):
                try:
                    shutil.copy2(path, path + ".manual_bak")
                except Exception:
                    pass
            with open(path, "w", encoding="utf-8") as f:
                f.write(str(text))
            self.config["autoexec_last_app_save"] = {"path": path, "sha256": core_logic.file_sha256(path), "time": time.strftime("%Y-%m-%d %H:%M")}
            app_config.save_config(self.config)
            self.log(f"[AUTOEXEC] Manual changes saved to: {path}")
            return {"ok": True, "path": path}
        except Exception as e:
            return {"ok": False, "error": f"Failed to save autoexec.cfg: {e}"}

    # ---------- log analyzer, custom DNS, VPK health ----------
    def log_analyze(self) -> Dict[str, Any]:
        res = core_logic.analyze_cs2_session_logs(self.paths.get("cs2_exe"))
        if not res.get("found"):
            import hardware_info
            try:
                opts, _vdf = hardware_info.get_current_launch_options(self.paths.get("steam_path"))
            except Exception:
                opts = ""
            if "-condebug" in (opts or "").lower():
                res["message"] = ("-condebug is already in your Steam launch options, but CS2 has not written console.log yet "
                                  f"({res.get('log_path') or 'game/csgo/console.log'}).\n\nCS2 creates the file the next time it starts with that flag. "
                                  "Restart CS2 once (the flag only counts from a fresh start), play a session, then analyze again.")
                res["condebug"] = True
        self.log(f"[LOG ANALYZER] {str(res.get('message')).splitlines()[0]}")
        keys = ("found", "condebug", "message", "file_size_mb", "frame_hitch_events", "shader_compile_events", "net_jitter_events", "vpk_load_events",
                "last_map", "recommendation", "log_path", "grade")
        return {k: res.get(k) for k in keys}

    def dns_custom(self, primary: str, secondary: str) -> Dict[str, Any]:
        import ipaddress
        try:
            p = str(ipaddress.IPv4Address(str(primary).strip()))
            s2 = str(ipaddress.IPv4Address(str(secondary).strip())) if str(secondary).strip() else ""
        except Exception:
            return {"ok": False, "error": "Enter valid IPv4 addresses, for example 1.1.1.1 and 1.0.0.1."}
        return self.dns_apply(p, s2, "Custom DNS")

    def vpk_verify(self) -> Dict[str, Any]:
        res = core_logic.scan_workshop_vpk_addons(self.paths.get("steam_path"), self.paths.get("cs2_exe"))
        self._vpk_scan = res
        self.log(f"[VPK] {res.get('message')}")
        return {"message": res.get("message"), "healthy": res.get("healthy_count", 0), "corrupted": res.get("corrupted_count", 0),
                "total_gb": res.get("total_gb", 0), "bad": [a.get("name") or a.get("id") for a in res.get("addons", []) if a.get("status") != "Healthy"][:30]}

    def vpk_repair(self) -> Dict[str, Any]:
        scan = core_logic.scan_workshop_vpk_addons(self.paths.get("steam_path"), self.paths.get("cs2_exe"))
        bad = [a for a in scan.get("addons", []) if a.get("status") != "Healthy"]
        if not bad:
            return {"ok": True, "count": 0, "message": "No damaged Workshop VPK files were found. Nothing to remove."}
        res = core_logic.repair_corrupted_workshop_addons(bad)
        self.log(f"[VPK] {res.get('message')}")
        return {"ok": True, "count": len(bad), "message": res.get("message", "")}

    def maps_quick_stats(self) -> Dict[str, Any]:
        import custom_map_cleaner
        maps = custom_map_cleaner.scan_custom_maps(self.paths.get("steam_path"), self.paths.get("cs2_dir"))
        return {"count": len(maps), "gb": round(sum(m.get("size_bytes", 0) for m in maps) / (1024 ** 3), 1)}

    def presence_refresh(self) -> Dict[str, Any]:
        self.presence.wake.set()
        return self.presence.snapshot()

    # ---------- map thumbnails ----------
    def map_thumb(self, map_name: str) -> str:
        """data: URI of the cached map picture, or '' while it downloads (a 'thumb' event follows when it is ready)."""
        import base64
        if not map_name or map_name in ("-", "unknown", "none"):
            return ""

        def to_uri(path: str) -> str:
            try:
                with open(path, "rb") as f:
                    return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("ascii")
            except Exception:
                return ""

        def done(name, path):
            uri = to_uri(path)
            if uri:
                self.emit("thumb", {"map": map_name, "uri": uri})

        path = server_browser.get_or_download_map_thumbnail(map_name, callback=done)
        return to_uri(path) if path else ""

    def _sniper_fired(self, host: str, port: int, name: str, cur: int, mx: int, target: int) -> None:
        """A slot opened: the sniper already connected. Play the chime (if enabled) and let Discord show where you are going."""
        self.log(f"[SNIPER] Open slot detected on {name} ({cur}/{mx}, target <= {target}). Connected through the in-game console; 10 s cooldown started.", "SERVERS")
        if self.config.get("sniper_sound_enabled", True):
            def tone():
                try:
                    import os
                    import winsound
                    f = os.path.join(r"C:\Windows\Media", "Windows Information Bar.wav")
                    if os.path.exists(f):
                        winsound.PlaySound(f, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
                    else:
                        winsound.MessageBeep(winsound.MB_OK)
                except Exception:
                    pass
            threading.Thread(target=tone, daemon=True).start()
        try:
            self.presence.tracked, self.presence.tracked_since, self.presence.session_start = (host, port, name), time.time(), int(time.time())
            if self.config.get("discord_rpc_enabled", True) and self.presence.rpc.connected:
                self.presence.rpc.set_activity(details=name, state="Connected via Slot Sniper", start_timestamp=self.presence.session_start, large_image=None)
        except Exception:
            pass
        self.emit("sniper", self.sniper_status())

    # ---------- soundtrack, 3D map, links ----------
    def soundtrack(self, map_name: str) -> Dict[str, Any]:
        tracks = server_browser.query_zegraph_soundtrack(map_name or "")
        return {"map": map_name, "tracks": [{"name": t.get("name"), "duration": t.get("duration_str"), "tags": t.get("tags") or [], "url": t.get("youtube_url")} for t in tracks]}

    def open_3d_map(self, map_name: str) -> bool:
        clean = server_browser.clean_map_slug(map_name or "")
        url = f"https://maps.cybo.dev/?map={clean}" if clean and clean not in ("-", "unknown", "none") else "https://maps.cybo.dev/"
        return self.open_url(url)

    def open_youtube_search(self, title: str) -> bool:
        import urllib.parse
        return self.open_url("https://www.youtube.com/results?search_query=" + urllib.parse.quote(str(title)[:120]))

    # ---------- DNS status, diagnostics, checksum ----------
    _dns_cache = (0.0, {})

    def dns_status(self) -> Dict[str, Any]:
        """Text for the status bar, from the adapter's real DNS (cached 30 s: reading it runs netsh)."""
        at, val = self._dns_cache
        if time.time() - at < 30 and val:
            return val
        try:
            iface = core_logic.get_active_network_interface()
            text, state = core_logic.dns_status_bar(iface.get("current_dns", ""))
        except Exception:
            text, state = "DNS: unknown", "unknown"
        val = {"text": text, "state": state}
        self._dns_cache = (time.time(), val)
        return val

    def diagnostics(self) -> str:
        import os
        import platform
        import re
        import hardware_info
        cpu, gpu = hardware_info.get_cpu_info(), hardware_info.get_gpu_info()
        lines = [f"CS2 Command Center Diagnostics v{version.APP_VERSION} ({version.BUILD_DATE})",
                 f"OS: {platform.system()} {platform.release()} ({platform.architecture()[0]})",
                 f"Environment: Python {platform.python_version()} | Mode: {'Admin' if core_logic.is_admin() else 'Standard'}",
                 f"CPU: {cpu.get('name', 'Unknown CPU')}", f"GPU: {gpu.get('name', 'Unknown GPU')}",
                 f"CS2 Executable Status: {'Installed' if self.paths.get('cs2_exe') else 'Not Found'}",
                 f"Autoexec Status: {'Configured' if self.paths.get('autoexec_cfg') else 'Not Found'}",
                 f"Tracked Servers: {len(self.servers_catalog())} nodes"]
        text = "\n".join(lines)
        user = os.environ.get("USERNAME", "")
        if user:
            text = text.replace(user, "[USER_REDACTED]")
        text = re.sub(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "[IP_REDACTED]", text)
        return re.sub(r"\b(?:STEAM_[0-5]:[01]:\d+|7656119\d{10})\b", "[STEAM_ID_REDACTED]", text)

    def exe_sha256(self) -> str:
        import hashlib
        import os
        import sys
        path = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest().upper()

    def log_clear(self) -> bool:
        with self._lock:
            self.log_buf.clear()
        return True

    def about(self) -> Dict[str, Any]:
        return {"version": version.APP_VERSION, "build_date": version.BUILD_DATE, "last_update_check": self.config.get("last_update_check_time") or "Never"}
