"""AUDIT Phase 3 - every backend endpoint through the real FastAPI app (TestClient).
No network: game-server A2S, Steam profile and zegraph calls are all mocked.
Needs: pip install -r requirements.txt httpx   (skips if FastAPI is not installed)."""
import importlib
import os
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    from fastapi.testclient import TestClient  # noqa: F401
    HAVE_FASTAPI = True
except Exception:
    HAVE_FASTAPI = False

ORIGIN = "https://geronimohq.com"


def fake_info(host, port, timeout=1.2):
    if host.startswith("110.42"):          # pretend the FyS/UB/ZL hosts are down
        return {"online": False, "status": "Timed Out", "map": "-", "players": "-/-", "curr_players": 0,
                "bots": 0, "humans": 0, "max_players": 0, "ping": "N/A", "rtt": 0}
    return {"online": True, "status": "Online", "name": "Test", "map": "ze_test_v1", "players": "10/64",
            "curr_players": 10, "bots": 2, "humans": 8, "max_players": 64, "ping": "50 ms", "rtt": 50}


@unittest.skipUnless(HAVE_FASTAPI, "FastAPI not installed")
class Endpoints(unittest.TestCase):
    def setUp(self):
        os.environ["GERONIMO_PRESENCE_TOKEN"] = "unit-test-token"
        os.environ.pop("ENABLE_API_DOCS", None)
        sys.modules.pop("api", None)
        self.api = importlib.import_module("api")
        self.patches = [
            mock.patch.object(self.api, "query_a2s_info", side_effect=fake_info),
            mock.patch.object(self.api, "query_a2s_players", return_value=[{"name": "p", "score": 1, "seconds": 120}]),
            mock.patch.object(self.api, "query_steam_profile_cached", return_value={"is_in_game": False, "is_cs2": False, "game_text": "", "is_online": False, "known": False}),  # real failure shape
            mock.patch.object(self.api, "fetch_gfl_intel", return_value=(None, [])),
        ]
        for p in self.patches:
            p.start()
        from fastapi.testclient import TestClient
        self.c = TestClient(self.api.app)

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        os.environ.pop("GERONIMO_PRESENCE_TOKEN", None)

    def test_health(self):
        r = self.c.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "online")
        self.assertEqual(r.headers.get("x-content-type-options"), "nosniff")

    def test_servers_schema_and_totals(self):
        r = self.c.get("/api/servers", headers={"Origin": ORIGIN})
        self.assertEqual(r.status_code, 200)
        d = r.json()
        for k in ("timestamp", "total_servers", "online_servers", "totals", "servers", "geronimo_presence"):
            self.assertIn(k, d)
        self.assertEqual(d["total_servers"], 41)
        self.assertEqual(d["totals"]["online_servers"], d["online_servers"])
        online = sum(1 for s in d["servers"].values() if s["online"])
        self.assertEqual(d["totals"]["humans"], 8 * online)          # bots removed
        s = d["servers"]["gfl"]
        for k in ("id", "host", "port", "online", "map", "curr_players", "bots", "humans", "max_players", "players_list"):
            self.assertIn(k, s)
        self.assertEqual(r.headers.get("access-control-allow-origin"), ORIGIN)
        self.assertIn(d["geronimo_presence"]["state"], ("in_server", "main_menu", "other_game", "online", "offline", "unknown"))

    def test_server_detail_and_errors(self):
        self.assertEqual(self.c.get("/api/servers/gfl").status_code, 200)
        self.assertEqual(self.c.get("/api/servers/not_a_server").status_code, 404)
        self.assertEqual(self.c.get("/api/servers/../../etc").status_code, 404)
        self.assertIn(self.c.get("/api/servers/" + "x" * 200).status_code, (404, 422))

    def test_presence_heartbeat(self):
        self.assertEqual(self.c.post("/api/presence/heartbeat?is_cs2_running=true").status_code, 401)
        self.assertEqual(self.c.post("/api/presence/heartbeat?is_cs2_running=true",
                                     headers={"X-Geronimo-Token": "wrong"}).status_code, 401)
        ok = self.c.post("/api/presence/heartbeat?is_cs2_running=true", headers={"X-Geronimo-Token": "unit-test-token"})
        self.assertEqual(ok.status_code, 200)

    def test_docs_hidden_and_methods(self):
        for path in ("/docs", "/redoc", "/openapi.json"):
            self.assertEqual(self.c.get(path).status_code, 404, path)
        self.assertEqual(self.c.post("/api/servers").status_code, 405)

    def test_cors_foreign_origin_not_allowed(self):
        r = self.c.get("/api/servers", headers={"Origin": "https://evil.example"})
        self.assertNotEqual(r.headers.get("access-control-allow-origin"), "https://evil.example")
        self.assertNotEqual(r.headers.get("access-control-allow-origin"), "*")

    def test_large_body_rejected(self):
        r = self.c.post("/api/presence/heartbeat", content=b"x" * 5000,
                        headers={"X-Geronimo-Token": "unit-test-token", "Content-Length": "5000"})
        self.assertEqual(r.status_code, 413)


if __name__ == "__main__":
    unittest.main(verbosity=2)
