"""
CS2 Game State Integration (GSI) Listener for CS2 Command Center
100% VAC-Safe: Valve's official built-in Game State Integration HTTP protocol.
Automatically receives real-time map, mode, and activity events directly from cs2.exe.
"""

import os
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Callable, Dict, Any

GSI_CONFIG_NAMES = ["gamestate_integration_cs2commandcenter.cfg", "gamestate_integration_cc.cfg"]
DEFAULT_GSI_PORT = 3000

GSI_CONFIG_CONTENT = """"CS2 Command Center GSI"
{
    "uri"           "http://127.0.0.1:3000/"
    "timeout"       "5.0"
    "buffer"        "0.1"
    "throttle"      "0.1"
    "heartbeat"     "1.0"
    "data"
    {
        "provider"              "1"
        "map"                   "1"
        "round"                 "1"
        "player_id"             "1"
        "player_state"          "1"
        "player_match_stats"    "1"
    }
}
"""

def ensure_gsi_config_installed(cfg_dir: str) -> bool:
    """Installs the official Valve GSI configuration into cs2 cfg folder."""
    if not cfg_dir or not os.path.exists(cfg_dir):
        return False
    success = False
    for cfg_name in GSI_CONFIG_NAMES:
        target_path = os.path.join(cfg_dir, cfg_name)
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(GSI_CONFIG_CONTENT.strip())
            success = True
        except Exception:
            pass
    return success

class _GSIRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
            if body and hasattr(self.server, "on_payload"):
                payload = json.loads(body.decode("utf-8", errors="replace"))
                self.server.on_payload(payload)
        except Exception:
            pass

    def log_message(self, format, *args):
        # Suppress HTTP server console output
        pass

class CS2GSIServer:
    def __init__(self, port: int = DEFAULT_GSI_PORT, on_state_update: Optional[Callable[[Dict[str, Any]], None]] = None):
        self.port = port
        self.on_state_update = on_state_update
        self.httpd: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self.running = False
        self.current_state: Dict[str, Any] = {
            "activity": "menu",
            "map_name": "",
            "map_phase": "",
            "player_name": ""
        }

    def _handle_payload(self, payload: Dict[str, Any]):
        player = payload.get("player", {})
        map_info = payload.get("map", {})
        raw_map = map_info.get("name", "").strip()
        map_name = raw_map.split("/")[-1].strip() if raw_map else ""
        map_phase = map_info.get("phase", "")
        player_name = player.get("name", "")

        activity = player.get("activity", "")
        if not activity:
            activity = "playing" if map_name else "menu"

        self.current_state = {
            "activity": activity,
            "map_name": map_name,
            "map_phase": map_phase,
            "player_name": player_name,
            "raw": payload
        }
        if self.on_state_update:
            try:
                self.on_state_update(self.current_state)
            except Exception:
                pass

    def start(self) -> bool:
        if self.running:
            return True
        try:
            self.httpd = HTTPServer(("127.0.0.1", self.port), _GSIRequestHandler)
            self.httpd.on_payload = self._handle_payload
            self.running = True
            self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
            self.thread.start()
            return True
        except Exception:
            self.running = False
            return False

    def stop(self):
        self.running = False
        if self.httpd:
            try:
                self.httpd.shutdown()
                self.httpd.server_close()
            except Exception:
                pass
            self.httpd = None

_global_gsi: Optional[CS2GSIServer] = None

def get_gsi_server(on_state_update: Optional[Callable[[Dict[str, Any]], None]] = None) -> CS2GSIServer:
    global _global_gsi
    if _global_gsi is None:
        _global_gsi = CS2GSIServer(on_state_update=on_state_update)
    elif on_state_update:
        _global_gsi.on_state_update = on_state_update
    return _global_gsi
