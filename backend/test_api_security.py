"""Security tests for backend/api.py (audit Phase 1b).

Runs with plain Python, no network, no FastAPI install needed:
    python backend/test_api_security.py
If FastAPI is not installed, tiny stand-ins are used so the module can be imported
and its functions called directly. No real game server, Steam or zegraph request
is made: every network function is replaced with a fake.
"""
import ast
import importlib
import os
import ssl
import sys
import types
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _install_fastapi_stubs():
    try:
        import fastapi  # noqa: F401
        return False
    except ImportError:
        pass

    class JSONResponse:
        def __init__(self, content=None, status_code=200, headers=None):
            self.body, self.status_code, self.headers = content, status_code, dict(headers or {})

    class FastAPI:
        def __init__(self, **kw):
            self.kw = kw

        def _deco(self, *a, **k):
            return lambda f: f

        get = post = middleware = _deco

        def add_middleware(self, cls, **kw):
            self.cors = kw

    class Request:
        def __init__(self, headers=None, client_host="10.0.0.1"):
            self.headers = {k.lower(): v for k, v in (headers or {}).items()}
            self.client = types.SimpleNamespace(host=client_host)

    fa = types.ModuleType("fastapi")
    fa.FastAPI, fa.Request = FastAPI, Request
    mw = types.ModuleType("fastapi.middleware")
    cors = types.ModuleType("fastapi.middleware.cors")
    cors.CORSMiddleware = object
    resp = types.ModuleType("fastapi.responses")
    resp.JSONResponse = JSONResponse
    sys.modules.update({"fastapi": fa, "fastapi.middleware": mw,
                        "fastapi.middleware.cors": cors, "fastapi.responses": resp})
    return True


STUBBED = _install_fastapi_stubs()


def load_api(token=""):
    os.environ["GERONIMO_PRESENCE_TOKEN"] = token
    sys.modules.pop("api", None)
    return importlib.import_module("api")


def req(api, headers=None, host="10.0.0.1"):
    if STUBBED:
        return sys.modules["fastapi"].Request(headers=headers, client_host=host)
    # Real FastAPI: build a genuine Starlette request (was None, which crashed 3 tests).
    from starlette.requests import Request
    raw = [(k.lower().encode("latin-1"), str(v).encode("latin-1")) for k, v in (headers or {}).items()]
    return Request({"type": "http", "method": "GET", "path": "/", "headers": raw,
                    "client": (host, 12345), "query_string": b""})


def status_of(r):
    return getattr(r, "status_code", 200)


class TokenTests(unittest.TestCase):
    def test_no_secret_configured_fails_closed(self):
        api = load_api("")
        r = api.presence_heartbeat(req(api, {"X-Geronimo-Token": "anything"}), is_cs2_running=True)
        self.assertEqual(status_of(r), 503)
        self.assertEqual(api.LOCAL_HEARTBEAT["timestamp"], 0)

    def test_missing_or_wrong_token_rejected(self):
        api = load_api("owner-secret-value")
        self.assertEqual(status_of(api.presence_heartbeat(req(api, {}), is_cs2_running=True)), 401)
        self.assertEqual(status_of(api.presence_heartbeat(req(api, {"X-Geronimo-Token": "nope"}), is_cs2_running=True)), 401)
        self.assertEqual(api.LOCAL_HEARTBEAT["timestamp"], 0, "rejected call must not change presence")

    def test_correct_token_accepted(self):
        api = load_api("owner-secret-value")
        r = api.presence_heartbeat(req(api, {"X-Geronimo-Token": "owner-secret-value"}), is_cs2_running=True)
        self.assertEqual(r["status"], "ok")
        self.assertTrue(api.LOCAL_HEARTBEAT["is_cs2"])

    def test_uses_compare_digest(self):
        src = open(os.path.join(HERE, "api.py"), encoding="utf-8").read()
        self.assertIn("hmac.compare_digest", src)


class CorsAndIpTests(unittest.TestCase):
    def test_cors_exact_origins_only(self):
        api = load_api()
        self.assertNotIn("*", api.ALLOWED_ORIGINS)
        for o in api.ALLOWED_ORIGINS:
            self.assertRegex(o, r"^(https://(www\.)?geronimohq\.com|http://(localhost|127\.0\.0\.1):\d+)$")
        if STUBBED:
            self.assertEqual(api.app.cors["allow_origins"], api.ALLOWED_ORIGINS)
            self.assertFalse(api.app.cors["allow_credentials"])

    def test_spoofed_xff_ignored(self):
        api = load_api()
        r = req(api, {"X-Forwarded-For": "1.1.1.1, 203.0.113.9"})
        self.assertEqual(api.get_client_ip(r), "203.0.113.9")  # right-most = added by Render

    def test_rate_limiter(self):
        api = load_api()
        rl = api.RateLimiter(3, 60)
        self.assertEqual([rl.allow("a") for _ in range(4)], [True, True, True, False])
        self.assertTrue(rl.allow("b"))


class NoArbitraryHostTests(unittest.TestCase):
    def test_no_route_takes_host_or_port(self):
        tree = ast.parse(open(os.path.join(HERE, "api.py"), encoding="utf-8").read())
        routes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for d in node.decorator_list:
                    if isinstance(d, ast.Call) and getattr(d.func, "attr", "") in ("get", "post"):
                        routes.append(node)
        self.assertGreaterEqual(len(routes), 4)
        for fn in routes:
            names = {a.arg.lower() for a in fn.args.args}
            self.assertFalse(names & {"host", "port", "ip", "addr", "address", "target", "url"},
                             f"{fn.name} takes a user-supplied address")

    def test_detail_unknown_id_404_and_catalog_only(self):
        api = load_api()
        called = []
        api.fetch_single_server = lambda s: called.append(s["host"]) or {"id": s["id"]}
        self.assertEqual(status_of(api.get_server_detail("../../etc")), 404)
        self.assertEqual(status_of(api.get_server_detail("8.8.8.8:53")), 404)
        self.assertEqual(status_of(api.get_server_detail("nope")), 404)
        self.assertEqual(called, [])
        api.get_server_detail("gfl"); api.get_server_detail("gfl")
        self.assertEqual(called, ["74.91.124.21"], "second call must come from the 5 s cache")


class PresenceStateTests(unittest.TestCase):
    def _api(self, steam):
        api = load_api("owner-secret-value")
        api.query_steam_profile_cached = lambda: steam
        return api

    def test_steam_unknown_gives_unknown_not_offline(self):
        api = self._api({"is_in_game": False, "is_cs2": False, "is_online": False, "known": False})
        self.assertEqual(api.get_geronimo_steam_status({})["state"], "unknown")

    def test_steam_offline_gives_offline(self):
        api = self._api({"is_in_game": False, "is_cs2": False, "is_online": False, "known": True})
        self.assertEqual(api.get_geronimo_steam_status({})["state"], "offline")

    def test_name_impersonation_ignored(self):
        api = self._api({"is_in_game": False, "is_cs2": False, "is_online": False, "known": True})
        fake = {"gfl": {"players_list": [{"name": "Geronimo", "seconds": 5}], "host": "1.2.3.4", "port": 1}}
        self.assertNotEqual(api.get_geronimo_steam_status(fake)["state"], "in_server")

    def test_name_match_trusted_when_owner_signal_says_cs2(self):
        api = self._api({"is_in_game": True, "is_cs2": True, "is_online": True, "known": True})
        real = {"gfl": {"players_list": [{"name": "Geronimo", "seconds": 5}], "host": "1.2.3.4", "port": 1}}
        self.assertEqual(api.get_geronimo_steam_status(real)["state"], "in_server")


class OutboundTests(unittest.TestCase):
    def test_tls_verification_on(self):
        api = load_api()
        self.assertEqual(api.SSL_CTX.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(api.SSL_CTX.check_hostname)

    def test_map_name_cannot_inject_url(self):
        api = load_api()
        urls = []

        class Fake:
            status_code = 500

        api.cffi_requests = types.SimpleNamespace(get=lambda u, **k: urls.append(u) or Fake())
        api.GFL_INTEL_CACHE.update({"timestamp": 0, "match": None})
        api.fetch_gfl_intel("../../admin?x=1#")
        self.assertFalse(any("admin" in u for u in urls), urls)
        api.GFL_INTEL_CACHE.update({"timestamp": 0, "match": None})
        api.fetch_gfl_intel("ze_good_map_v1")
        self.assertTrue(any(u.endswith("/maps/ze_good_map_v1/musics") for u in urls), urls)


if __name__ == "__main__":
    print("fastapi stubbed:", STUBBED)
    unittest.main(verbosity=2)
