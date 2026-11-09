"""Audit Phase 1c security tests for the desktop app.

Safe to run anywhere: no CS2, Steam, Discord, registry write or real map is touched.
Uses temp folders, fake network functions and AST extraction for code inside app.py.
    python desktop-app/test_security_phase1c.py
"""
import ast
import http.client
import json
import os
import sys
import tempfile
import threading
import types
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# Non-Windows CI: give core_logic a dummy winreg so the modules import.
if "winreg" not in sys.modules:
    try:
        import winreg  # noqa: F401
    except ImportError:
        sys.modules["winreg"] = types.ModuleType("winreg")
os.environ.setdefault("APPDATA", tempfile.mkdtemp(prefix="cc_appdata_"))

import server_browser  # noqa: E402
import custom_map_cleaner  # noqa: E402
import cs2_gsi  # noqa: E402
import app_config  # noqa: E402

APP_SRC = open(os.path.join(HERE, "app.py"), encoding="utf-8").read()
APP_TREE = ast.parse(APP_SRC)


def extract(name, ns, cls=None):
    """Compile one function (optionally a method of class `cls`) from app.py into ns."""
    nodes = APP_TREE.body
    if cls:
        nodes = next(n for n in APP_TREE.body if isinstance(n, ast.ClassDef) and n.name == cls).body
    fn = next(n for n in nodes if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "app.py", "exec"), ns)
    return ns[name]


def main_class():
    for n in APP_TREE.body:
        if isinstance(n, ast.ClassDef) and any(
                isinstance(m, ast.FunctionDef) and m.name == "_send_web_presence_heartbeat" for m in n.body):
            return n.name
    raise AssertionError("heartbeat method not found")


class ServerAddressTests(unittest.TestCase):
    def test_valid(self):
        v = server_browser.validate_server_address
        self.assertEqual(v("74.91.124.21", "27015"), ("74.91.124.21", 27015))
        self.assertEqual(v("rsscs2.kr", 27015), ("rsscs2.kr", 27015))

    def test_invalid(self):
        v = server_browser.validate_server_address
        for host, port in [("1.2.3.4;quit", 27015), ("x&calc", 27015), ("a b", 1), ("", 27015),
                           ("1.2.3.4", 0), ("1.2.3.4", 99999), ("1.2.3.4", "abc"),
                           ("<script>", 27015), ("javascript:alert(1)", 1), ("999.1.1.1", 27015),
                           ("-bad.com", 27015), ("1.2.3.4\nquit", 27015), ("1.2.3.4", True)]:
            self.assertIsNone(v(host, port), (host, port))

    def test_connect_functions_refuse_bad_host(self):
        opened = []
        server_browser.os.startfile = lambda u: opened.append(u)  # fake, never launches Steam
        server_browser._copy_clipboard_fast = lambda c: opened.append(c)
        self.assertFalse(server_browser.direct_connect("1.2.3.4&calc", 27015))
        self.assertFalse(server_browser.fast_console_connect("1.2.3.4;quit", 27015))
        self.assertEqual(opened, [])

    def test_bad_saved_custom_server_dropped(self):
        tmp = tempfile.mkdtemp()
        f = os.path.join(tmp, "custom_servers.json")
        json.dump([{"is_custom": True, "host": "1.2.3.4;quit", "port": 27015, "name": "evil"},
                   {"is_custom": True, "host": "1.2.3.4", "port": 27015, "name": "ok"}], open(f, "w"))
        old = server_browser.SERVERS_FILE
        server_browser.SERVERS_FILE = f
        try:
            names = [s["name"] for s in server_browser.load_servers() if s.get("is_custom")]
        finally:
            server_browser.SERVERS_FILE = old
        self.assertEqual(names, ["ok"])


class UrlOpenerTests(unittest.TestCase):
    def test_only_plain_web_links(self):
        ns = {}
        const = next(n for n in APP_TREE.body if isinstance(n, ast.Assign)
                     and getattr(n.targets[0], "id", "") == "_UNSAFE_URL_CHARS")
        exec(compile(ast.Module(body=[const], type_ignores=[]), "app.py", "exec"), ns)
        extract("_is_safe_launch_url", ns)
        ok = ns["_is_safe_launch_url"]
        self.assertTrue(ok("https://discord.gg/gflze"))
        self.assertTrue(ok("https://www.youtube.com/results?search_query=a%20b"))
        for bad in ["file:///C:/Windows/System32/calc.exe", "steam://install/1", "https://x.com/&calc",
                    "https://x.com/|dir", "javascript:alert(1)", "C:\\evil.exe", "https://a b"]:
            self.assertFalse(ok(bad), bad)


class MapCleanerTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="cc_maps_")
        self.ws = os.path.join(self.root, "steamapps", "workshop", "content", "730")
        self.maps = os.path.join(self.root, "game", "csgo", "maps")
        os.makedirs(os.path.join(self.ws, "123456"))
        os.makedirs(self.maps)
        open(os.path.join(self.ws, "123456", "a.vpk"), "w").write("x")
        open(os.path.join(self.maps, "ze_custom.vpk"), "w").write("x")
        self.outside = os.path.join(self.root, "important")
        os.makedirs(self.outside)
        open(os.path.join(self.outside, "keep.txt"), "w").write("x")

    def test_shapes(self):
        ok = custom_map_cleaner.is_deletable_map_path
        self.assertTrue(ok(os.path.join(self.ws, "123456")))
        self.assertTrue(ok(os.path.join(self.maps, "ze_custom.vpk")))
        self.assertFalse(ok(self.outside))
        self.assertFalse(ok(self.ws))
        self.assertFalse(ok(os.path.join(self.ws, "123456", "..", "..", "..", "..", "..", "important")))

    def test_symlink_refused(self):
        link = os.path.join(self.ws, "999999")
        try:
            os.symlink(self.outside, link, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks not allowed on this machine")
        self.assertFalse(custom_map_cleaner.is_deletable_map_path(link))
        n, _, logs = custom_map_cleaner.delete_custom_maps([{"path": link, "name": "evil", "id": "999999"}])
        self.assertEqual(n, 0)
        self.assertTrue(os.path.exists(os.path.join(self.outside, "keep.txt")))

    def test_delete_outside_blocked_inside_ok(self):
        n, _, logs = custom_map_cleaner.delete_custom_maps([{"path": self.outside, "name": "x", "id": "1"}])
        self.assertEqual(n, 0)
        self.assertTrue(os.path.exists(self.outside))
        n, _, _ = custom_map_cleaner.delete_custom_maps([{"path": os.path.join(self.ws, "123456"), "name": "t", "id": "123456"}])
        self.assertEqual(n, 1)


class GsiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.got = []
        cls.srv = cs2_gsi.CS2GSIServer(port=0)
        from http.server import HTTPServer
        cls.httpd = HTTPServer(("127.0.0.1", 0), cs2_gsi._GSIRequestHandler)
        cls.httpd.on_payload = cls.got.append
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()
        cls.port = cls.httpd.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def post(self, body, headers=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=3)
        c.request("POST", "/", body=body, headers=headers or {})
        return c.getresponse().status

    def test_binds_localhost_only(self):
        self.assertIn('("127.0.0.1", self.port)', open(os.path.join(HERE, "cs2_gsi.py"), encoding="utf-8").read())

    def test_valid_payload(self):
        self.assertEqual(self.post(json.dumps({"map": {"name": "ze_x"}})), 200)
        self.assertIn({"map": {"name": "ze_x"}}, self.got)

    def test_browser_origin_rejected(self):
        before = len(self.got)
        self.assertEqual(self.post(json.dumps({"fake": 1}), {"Origin": "https://evil.example"}), 403)
        self.assertEqual(len(self.got), before)

    def test_oversize_rejected(self):
        self.assertEqual(self.post("x" * (70 * 1024)), 413)


class OwnerOnlyHeartbeatTests(unittest.TestCase):
    def _run(self, cfg):
        sent = []
        fake_urlreq = types.SimpleNamespace(
            Request=lambda url, headers=None: (url, headers),
            urlopen=lambda req, timeout=0: sent.append(req))
        urllib_pkg = types.ModuleType("urllib")
        urllib_pkg.request = fake_urlreq
        saved = {k: sys.modules.get(k) for k in ("urllib", "urllib.request")}
        sys.modules["urllib"], sys.modules["urllib.request"] = urllib_pkg, fake_urlreq

        class ImmediateThread:
            def __init__(self, target=None, daemon=None):
                self.t = target

            def start(self):
                self.t()

        ns = {"threading": types.SimpleNamespace(Thread=ImmediateThread)}
        fn = extract("_send_web_presence_heartbeat", ns, cls=main_class())
        try:
            fn(types.SimpleNamespace(config=cfg), True, True)
        finally:
            for k, v in saved.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v
        return sent

    def test_fresh_install_sends_nothing(self):
        self.assertEqual(self._run({}), [])
        self.assertEqual(self._run({"presence_secret": "   "}), [])

    def test_owner_install_sends_token(self):
        sent = self._run({"presence_secret": "owner-token"})
        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0][1].get("X-Geronimo-Token"), "owner-token")

    def test_exit_ping_is_owner_only(self):
        fn = next(n for n in ast.walk(APP_TREE) if isinstance(n, ast.FunctionDef) and n.name == "exit_application")
        src = ast.get_source_segment(APP_SRC, fn)
        i_url = src.index("api/presence/heartbeat")
        self.assertIn("if secret:", src[:i_url])


class ConfigTests(unittest.TestCase):
    def test_atomic_round_trip(self):
        tmp = tempfile.mkdtemp()
        old = app_config.CONFIG_FILE
        app_config.CONFIG_FILE = os.path.join(tmp, "cfg.json")
        try:
            self.assertTrue(app_config.save_config({"check_updates_on_start": True, "x": 1}))
            self.assertEqual(json.load(open(app_config.CONFIG_FILE)), {"check_updates_on_start": True, "x": 1})
            self.assertFalse(os.path.exists(app_config.CONFIG_FILE + ".tmp"))
        finally:
            app_config.CONFIG_FILE = old


class NoMemoryAccessTests(unittest.TestCase):
    def test_no_process_memory_or_injection_apis(self):
        bad = ("ReadProcessMemory", "WriteProcessMemory", "CreateRemoteThread", "VirtualAllocEx",
               "NtWriteVirtualMemory", "SetWindowsHookEx", "PROCESS_VM_READ", "PROCESS_VM_WRITE")
        for f in os.listdir(HERE):
            if f.endswith(".py") and not f.startswith("test_"):
                src = open(os.path.join(HERE, f), encoding="utf-8").read()
                for b in bad:
                    self.assertNotIn(b, src, f"{b} in {f}")

    def test_no_unsafe_deserialization(self):
        for f in os.listdir(HERE):
            if f.endswith(".py") and not f.startswith("test_"):
                tree = ast.parse(open(os.path.join(HERE, f), encoding="utf-8").read())
                for n in ast.walk(tree):
                    if isinstance(n, ast.Call):
                        name = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
                        mod = getattr(getattr(n.func, "value", None), "id", "")
                        self.assertNotIn(name, ("eval", "exec"), f"{name} in {f}")
                        self.assertFalse(mod in ("pickle", "marshal") and name in ("load", "loads"), f)
                        self.assertFalse(mod == "yaml" and name == "load", f)


if __name__ == "__main__":
    unittest.main(verbosity=2)
