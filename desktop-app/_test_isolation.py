"""AUDIT: import this BEFORE `import app` in every test that creates the app.

It redirects the app's settings file to a temp folder and stubs Windows startup
(registry Run key + Task Scheduler), so tests never change the owner's real
%APPDATA%\\CS2CommandCenter\\command_center_config.json or the registry.
(Found in Phase 3: exit_application() saves the last page, and older tests used
the real config.)
"""
import atexit
import os
import shutil
import tempfile

import app_config

TEMP_DIR = tempfile.mkdtemp(prefix="cs2cc_test_")
REAL_CONFIG_FILE = app_config.CONFIG_FILE
app_config.CONFIG_FILE = os.path.join(TEMP_DIR, "command_center_config.json")
app_config.set_windows_startup = lambda enabled, minimized=False: True
app_config.is_windows_startup_enabled = lambda: False
app_config.is_windows_startup_minimized = lambda: False
app_config.migrate_legacy_startup_task = lambda: "none"  # never touch the real Task Scheduler
atexit.register(shutil.rmtree, TEMP_DIR, True)

# AUDIT rule D: app tests must not query real game servers, the backend or zegraph.
# Set CS2CC_TEST_NETWORK=1 to allow live network (e.g. a deliberate end-to-end run).
if os.environ.get("CS2CC_TEST_NETWORK") != "1":
    import server_browser as _sb

    def _fake_info(host, port, timeout=1.8):
        return {"online": True, "status": "Online", "server_name": "test", "map": "ze_test_v1",
                "players": "64/64", "curr_players": 64, "max_players": 64, "bots": 0,
                "ping": "1 ms", "rtt": 1}  # full server, like GFL at peak

    _sb.query_server_info = _fake_info
    _sb.query_server_players = lambda *a, **k: {"online": True, "players": []}
    _sb.query_zegraph_match_now = lambda *a, **k: {"success": False}
    _sb.query_zegraph_soundtrack = lambda *a, **k: []
    _sb.fetch_backend_servers = lambda *a, **k: None
    _sb.fetch_gfl_continents = lambda *a, **k: None
    _sb.get_or_download_map_thumbnail = lambda *a, **k: None
