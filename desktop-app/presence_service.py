"""Discord Rich Presence + CS2 lifecycle manager for the web-window front end (port of the classic app's presence loop).

- CS2 closed: nothing is shown on Discord.
- CS2 running: shows the server you are on (found through the game's own GSI feed, your Steam persona in server rosters, or the map name)
  or "In Main Menu".
- Owner-only: when a presence_secret is set, a heartbeat tells the website whether CS2/Steam are running.
"""
import concurrent.futures
import threading
import time
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

import app_config
import core_logic
import cs2_gsi
import discord_rpc
import server_browser

Tracked = Tuple[str, int, str]
STANDBY_DETAILS, STANDBY_STATE = "In Main Menu • Standby", "CS2 Command Center"


class PresenceService:
    def __init__(self, core):
        self.core = core
        self.rpc = discord_rpc.get_discord_rpc()
        self.gsi_state: Dict[str, Any] = {}
        self.last_gsi = 0.0
        self.tracked: Optional[Tracked] = None
        self.tracked_since = 0.0
        self.session_start = 0
        self.status = "Standby"
        self.stop_event = threading.Event()
        self.wake = threading.Event()
        self.thread: Optional[threading.Thread] = None
        self._logged_act = None
        self._logged_map = ""
        self._menu_since = 0.0
        self._logged_miss = ""
        self._sent = ""

    # ---------- lifecycle ----------
    def start(self) -> None:
        cfg_dir = self.core.paths.get("cfg_dir")
        try:
            if cfg_dir:
                cs2_gsi.ensure_gsi_config_installed(cfg_dir)
            cs2_gsi.get_gsi_server(on_state_update=self._on_gsi).start()
        except Exception as e:
            self.core.log(f"[GSI] Live game state feed could not start: {e}")
        if not self.thread:
            self.thread = threading.Thread(target=self._loop, daemon=True, name="presence")
            self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        try:
            self.rpc.clear_activity()
            self.rpc.close()
        except Exception:
            pass
        try:
            cs2_gsi.get_gsi_server().stop()
        except Exception:
            pass

    # ---------- helpers ----------
    def _on_gsi(self, state: Dict[str, Any]) -> None:
        self.gsi_state = state
        self.last_gsi = time.time()
        act, mp = state.get("activity", ""), state.get("map_name", "")
        if act == "playing" and mp and (act != self._logged_act or mp != self._logged_map):
            self._logged_act, self._logged_map = act, mp
            self.core.log(f"[GSI] Live match detected: map={mp}", "SYSTEM")
        elif act == "menu" and act != self._logged_act:
            self._logged_act, self._logged_map = act, ""
            self.core.log("[GSI] CS2 returned to the main menu.", "SYSTEM")

    def _fresh(self, max_age: float = 5.0) -> bool:
        return (time.time() - self.last_gsi) < max_age

    def _servers(self) -> List[Dict[str, Any]]:
        return [s for s in self.core.servers_catalog()]

    def buttons(self, host: str, port: int) -> List[Dict[str, str]]:
        hp = f"{host}:{port}"
        btn1 = {"label": f"Server: {hp}", "url": f"https://geronimohq.com/connect?ip={hp}"}
        match = next((s for s in self._servers() if s["host"].lower() == str(host).lower() and int(s["port"]) == int(port)), None)
        if match:
            sid = str(match.get("id", "")).lower()
            url = match.get("discord")
            if url:
                labels = {"gfl": "GFL Community Discord", "possession": "PSE Community Discord", "mapeadores": "Mapeadores Discord",
                          "cola": "cOLa Community Discord", "rss": "RSS Community Discord"}
                tag = labels.get(sid) or f"{(sid.upper() if len(sid) <= 6 else str(match.get('name', '')).split()[0])} Discord"
                return [btn1, {"label": tag[:32], "url": url if str(url).startswith("http") else f"https://{url}"}]
            if match.get("group") == "china":
                return [btn1, {"label": f"{str(match.get('cluster', 'China')).split()[0][:14]} Portal", "url": "https://geronimohq.com"}]
        return [btn1, {"label": "GeronimoHQ Portal", "url": "https://geronimohq.com"}]

    def _parallel(self, fn, servers):
        """Runs fn(server) for every server at once (a sequential sweep of 40+ servers took over 20 s, and Discord showed the
        generic "Zombie Escape Server" card for that long after every map change). Results keep the catalog order."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
            return list(ex.map(lambda sv: self._safe(fn, sv), servers))

    @staticmethod
    def _safe(fn, sv):
        try:
            return fn(sv)
        except Exception:
            return None

    def _match_by_map(self, map_name: str) -> Optional[Tracked]:
        target = (map_name or "").split("/")[-1].lower().strip()
        if not target:
            return None
        servers = sorted(self._servers(), key=lambda x: x["id"] != "gfl")

        def one(sv):
            info = server_browser.query_server_info(sv["host"], int(sv["port"]), timeout=1.2)
            if info.get("online") and (info.get("map") or "").split("/")[-1].lower().strip() == target:
                return (sv["host"], int(sv["port"]), sv["name"], int(info.get("curr_players") or 0))
            return None

        first = self._safe(one, servers[0]) if servers and servers[0]['id'] == 'gfl' else None
        if first and first[3] > 0:
            return (first[0], first[1], first[2])        # the usual case, answered in about a second
        hits = [h for h in self._parallel(one, servers) if h]
        if not hits:
            return None
        best = hits[0]                       # GFL first, then catalog order; an empty server is a worse guess than a busy one
        if best[3] == 0:
            best = next((h for h in hits if h[3] > 0), best)
        return (best[0], best[1], best[2])

    def _scan_for_user(self, persona: str) -> Optional[Tracked]:
        target = (persona or "").lower().strip()
        if not target:
            return None
        servers = [sv for sv in sorted(self._servers(), key=lambda x: x["id"] != "gfl") if sv.get("group") != "china"]   # China rosters are shielded

        def one(sv):
            res = server_browser.query_server_players(sv["host"], int(sv["port"]), timeout=1.2)
            if res.get("success") and any(p.get("name", "").strip().lower() == target for p in res.get("players", [])):
                return (sv["host"], int(sv["port"]), sv["name"])
            return None

        return next((h for h in self._parallel(one, servers) if h), None)

    def _heartbeat(self, is_cs2: bool, is_steam: bool) -> None:
        secret = str(self.core.config.get("presence_secret", "") or "").strip()
        if not secret:
            return                      # only the owner's install talks to the website backend

        def _req():
            try:
                url = ("https://geronimohq-telemetry.onrender.com/api/presence/heartbeat?is_cs2_running="
                       f"{'true' if is_cs2 else 'false'}&is_steam_running={'true' if is_steam else 'false'}")
                urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "CS2CommandCenter/2.0", "X-Geronimo-Token": secret}), timeout=3.5)
            except Exception:
                pass

        threading.Thread(target=_req, daemon=True).start()

    # ---------- main loop ----------
    def _loop(self) -> None:
        was_running, last_scan, last_map, missing, last_hb = False, 0.0, "", 0, 0.0
        persona = None
        try:
            persona = core_logic.get_steam_active_persona(self.core.paths.get("steam_path"))
        except Exception:
            pass
        while not self.stop_event.is_set():
            self.wake.wait(2.0)
            self.wake.clear()
            if self.stop_event.is_set():
                break
            try:
                if not self.core.config.get("discord_rpc_enabled", True):
                    if self.rpc.connected:
                        self.rpc.clear_activity()
                        self.rpc.close()
                    self.status = "Presence is turned off"
                    continue
                running = core_logic.is_cs2_running() or self._fresh()
                steam = core_logic.is_steam_running() or running
                now = time.time()
                if now - last_hb >= 8.0:
                    last_hb = now
                    self._heartbeat(running, steam)

                if not running:
                    launching = self.tracked_since > 0 and (now - self.tracked_since) < 45.0
                    if not launching and (was_running or self.rpc.connected):
                        self.rpc.clear_activity()
                        self.rpc.close()
                        was_running, self.tracked, self.tracked_since, missing, last_map = False, None, 0.0, 0, ""
                        self._logged_act, self._logged_map = None, ""
                    self.status = "Standby (CS2 closed)"
                    continue

                cid = (self.core.config.get("discord_client_id") or app_config.DEFAULT_DISCORD_CLIENT_ID).strip() or app_config.DEFAULT_DISCORD_CLIENT_ID
                self.rpc.set_client_id(cid)
                if not was_running:
                    was_running = True
                    self.session_start = int(time.time())
                    self.rpc.connect()
                if not self.rpc.connected and not self.rpc.connect():
                    self.status = "Discord desktop app not detected"
                    continue
                sniping = server_browser.get_slot_sniper().is_active      # keep the card current, but leave the network to the sniper
                if not persona:
                    persona = core_logic.get_steam_active_persona(self.core.paths.get("steam_path"))

                gs = self.gsi_state
                gmap = (gs.get("map_name", "") or "").split("/")[-1].strip()
                act = gs.get("activity", "")
                if act == "menu" and not gmap and self.tracked is not None:
                    self._menu_since = self._menu_since or now      # a map change also looks like the menu for a moment: only reset after 25 s
                    if now - self._menu_since >= 25.0:
                        self.core.log("[DISCORD] Main menu detected, tracking reset to standby.")
                        self.tracked, missing, self._menu_since = None, 0, 0.0
                else:
                    self._menu_since = 0.0

                if self.tracked is not None:
                    host, port, name = self.tracked
                    in_grace = (now - self.tracked_since) < 30.0
                    if not sniping and not in_grace and persona and not (self._fresh() and act == "playing"):
                        res = server_browser.query_server_players(host, port, timeout=0.9)
                        if res.get("success"):
                            names = [p.get("name", "").strip().lower() for p in res.get("players", [])]
                            if persona.lower() in names:
                                missing = 0
                            else:
                                missing += 1
                                if missing >= 3:
                                    sw = self._scan_for_user(persona)
                                    if sw and sw[0] != host:
                                        self.tracked, self.tracked_since, missing, self.session_start = sw, time.time(), 0, int(time.time())
                                        self.core.log(f"[DISCORD] Player switched servers: {sw[2]}")
                                    else:
                                        self.tracked, missing = None, 0
                                        self.core.log("[DISCORD] Player left the server; back to Main Menu.")
                elif not sniping and now - last_scan > 3.0:
                    last_scan = now
                    joined = self._match_by_map(gmap) if gmap else None
                    if not joined and persona:
                        joined = self._scan_for_user(persona)
                    if joined:
                        self.tracked, self.tracked_since, missing, self.session_start = joined, time.time(), 0, int(time.time())
                        self.core.log(f"[DISCORD] Detected connected server: {joined[2]}")
                    elif act == "playing" and gmap and gmap != self._logged_miss:
                        self._logged_miss = gmap
                        self.core.log(f"[DISCORD] In a match on {gmap}, but no catalog server is on that map yet; showing the generic card and retrying every few seconds.")

                details, state, btns = STANDBY_DETAILS, STANDBY_STATE, None
                if self.tracked is not None:
                    host, port, name = self.tracked
                    info = server_browser.query_server_info(host, port, timeout=1.2)
                    mname = (info.get("map") if info.get("online") else "") or gmap or "Unknown"
                    pc = info.get("curr_players", 0) if info.get("online") else 0
                    mx = info.get("max_players", 64) if info.get("online") else 64
                    details, state = name, (f"Map: {mname} ({pc}/{mx} Players)" if pc else f"Map: {mname}")
                    btns = self.buttons(host, port)
                    if mname not in ("Unknown", last_map):
                        last_map = mname
                        self.core.log(f"[DISCORD] Live tracking: {name} [{state}]")
                elif act == "playing" and gmap:
                    details = "Zombie Escape Server" if gmap.startswith("ze_") else "Community Server"
                    state, btns = f"Map: {gmap}", [{"label": "GeronimoHQ Portal", "url": "https://geronimohq.com"}]
                self.rpc.set_activity(details=details, state=state, start_timestamp=self.session_start, large_image=None, buttons=btns)
                sig = f"{details}|{state.split(' (')[0]}|{[b.get('label') for b in (btns or [])]}"
                if sig != self._sent and (self.tracked is not None or act == "playing"):
                    self._sent = sig
                    self.core.log(f"[DISCORD] Card sent: {details} / {state} / buttons: {', '.join(b.get('label', '') for b in (btns or [])) or 'none'}")
                self.status = f"Active: {details}" if details != STANDBY_DETAILS else "Active: CS2 main menu"
            except Exception as e:  # the loop must never die
                self.status = f"Error: {e}"

    # ---------- actions used by the page ----------
    def snapshot(self) -> Dict[str, Any]:
        act = self.rpc.broadcast_snapshot()       # what Discord is REALLY showing (None when nothing is sent)
        btns = [b.get("label", "") for b in (act or {}).get("buttons", [])]
        return {"enabled": bool(self.core.config.get("discord_rpc_enabled", True)), "connected": bool(self.rpc.connected), "status": self.status,
                "details": (act or {}).get("details", ""), "state": (act or {}).get("state", ""), "buttons": btns,
                "cs2_running": bool(core_logic.is_cs2_running() or self._fresh()),
                "tracked": self.tracked[2] if self.tracked else ""}

    def clear(self) -> None:
        self.tracked = None
        self.rpc.clear_activity()
        self.rpc.close()
        self.status = "Cleared"
        self.core.log("[DISCORD] Rich presence cleared and Discord IPC closed.")

    def standby(self) -> None:
        self.tracked = None
        self.session_start = int(time.time())
        if self.rpc.connected:
            self.rpc.set_activity(details=STANDBY_DETAILS, state=STANDBY_STATE, start_timestamp=self.session_start, large_image=None)
        self.status = "Active: CS2 main menu"
        self.core.log("[DISCORD] Presence reset to: In Main Menu • Standby")

    def broadcast(self, host: str, port: int, name: str) -> Dict[str, Any]:
        if not self.core.config.get("discord_rpc_enabled", True):
            return {"ok": False, "error": "Turn on Discord Rich Presence first."}
        self.tracked, self.tracked_since, self.session_start = (host, int(port), name), time.time(), int(time.time())
        self.rpc.set_client_id((self.core.config.get("discord_client_id") or app_config.DEFAULT_DISCORD_CLIENT_ID).strip())
        info = server_browser.query_server_info(host, int(port), timeout=1.2)
        state = f"Map: {info.get('map', 'Unknown')} ({info.get('curr_players', 0)}/{info.get('max_players', 64)} Players)" if info.get("online") else "Zombie Escape Server"
        if not self.rpc.connected:
            self.rpc.connect()
        ok = self.rpc.set_activity(details=name, state=state, start_timestamp=self.session_start, large_image=None, buttons=self.buttons(host, int(port)))
        self.core.log(f"[DISCORD] Broadcasted to Discord: {name} | {state}")
        return {"ok": bool(ok), "error": "" if ok else "Could not reach the Discord desktop app."}
