"""Other-PC behaviour: missing WebView2, DNS adapter in any Windows language, GSI port fallback, updater in non-ASCII folders,
and the hand-off to an elevated copy that runs as another Windows account. Synthetic data only; nothing real is changed."""
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest import mock

import _test_isolation  # noqa: F401  (temp config; must come first)
import app_config
import core_logic
import core_service
import cs2_gsi
import updater
import web_main
import webview2_check


class WebView2(unittest.TestCase):
    def test_missing_runtime_is_detected_and_a_present_one_is_reported(self):
        with mock.patch.object(webview2_check.winreg, "OpenKey", side_effect=OSError), mock.patch.object(webview2_check.glob, "glob", return_value=[]):
            self.assertIsNone(webview2_check.runtime_version())
        with mock.patch.object(webview2_check.winreg, "OpenKey", side_effect=OSError), \
                mock.patch.object(webview2_check.glob, "glob", return_value=[r"C:\x\Microsoft\EdgeWebView\Application\150.1.2.3\msedgewebview2.exe"]):
            self.assertEqual(webview2_check.runtime_version(), "150.1.2.3")
        key = mock.MagicMock()
        key.__enter__.return_value = key
        with mock.patch.object(webview2_check.winreg, "OpenKey", return_value=key), mock.patch.object(webview2_check.winreg, "QueryValueEx", return_value=("157.0.1.2", 1)):
            self.assertEqual(webview2_check.runtime_version(), "157.0.1.2")
        with mock.patch.object(webview2_check.winreg, "OpenKey", return_value=key), mock.patch.object(webview2_check.winreg, "QueryValueEx", return_value=("0.0.0.0", 1)), \
                mock.patch.object(webview2_check.glob, "glob", return_value=[]):
            self.assertIsNone(webview2_check.runtime_version())

    def test_message_box_opens_the_download_page_only_on_yes(self):
        with mock.patch.object(webview2_check.os, "startfile") as sf, mock.patch("ctypes.windll.user32.MessageBoxW", return_value=6):
            webview2_check.explain_and_offer_install()
            sf.assert_called_once_with(webview2_check.DOWNLOAD_PAGE)
        with mock.patch.object(webview2_check.os, "startfile") as sf, mock.patch("ctypes.windll.user32.MessageBoxW", return_value=7):
            webview2_check.explain_and_offer_install()
            sf.assert_not_called()


class DnsAdapter(unittest.TestCase):
    GERMAN = ('Konfiguration der Schnittstelle "WLAN"\n    Statisch konfigurierte DNS-Server:    1.1.1.1\n'
              '                                          1.0.0.1\n    Mit welchem Suffix registrieren:      Nur primär\n')

    def fake_run(self, calls):
        def run(args, **kw):
            calls.append(args)
            if "show" in args:
                return SimpleNamespace(returncode=0, stdout=self.GERMAN, stderr="")
            return SimpleNamespace(returncode=0, stdout="OK", stderr="")
        return run

    def test_adapter_comes_from_the_default_route_not_from_english_words(self):
        calls = []
        with mock.patch.object(core_logic, "_default_route_interface_index", return_value=12), mock.patch.object(core_logic.subprocess, "run", side_effect=self.fake_run(calls)):
            info = core_logic.get_active_network_interface()
        self.assertEqual((info["interface_ref"], info["interface_name"], info["found"]), ("12", "WLAN", True))
        self.assertIn("Cloudflare", info["current_dns"])
        self.assertIn("name=12", calls[0])

    def test_apply_and_restore_use_the_adapter_index(self):
        calls = []
        with mock.patch.object(core_logic, "_default_route_interface_index", return_value=12), mock.patch.object(core_logic.subprocess, "run", side_effect=self.fake_run(calls)), \
                mock.patch.object(core_logic, "is_admin", return_value=True), mock.patch.object(core_logic, "flush_dns_cache", return_value=(True, [])):
            ok, logs = core_logic.apply_dns_provider("9.9.9.9", "149.112.112.112", "Quad9")
            ok2, _ = core_logic.restore_dns_to_dhcp()
        self.assertTrue(ok and ok2)
        sets = [c for c in calls if "set" in c or "add" in c]
        self.assertTrue(sets and all("name=12" in c for c in sets))
        self.assertTrue(any("WLAN" in l for l in logs))

    def test_failed_secondary_server_is_not_reported_as_success(self):
        def run(args, **kw):
            if "add" in args:
                return SimpleNamespace(returncode=1, stdout="denied", stderr="")
            return SimpleNamespace(returncode=0, stdout=self.GERMAN, stderr="")
        with mock.patch.object(core_logic, "_default_route_interface_index", return_value=12), mock.patch.object(core_logic.subprocess, "run", side_effect=run), \
                mock.patch.object(core_logic, "is_admin", return_value=True), mock.patch.object(core_logic, "flush_dns_cache", return_value=(True, [])):
            ok, logs = core_logic.apply_dns_provider("9.9.9.9", "149.112.112.112", "Quad9")
        self.assertTrue(ok)
        self.assertFalse(any("Secondary failover DNS set" in l for l in logs))
        self.assertTrue(any("could not be added" in l for l in logs))


class GsiPort(unittest.TestCase):
    def test_busy_port_falls_back_and_the_config_names_the_port_that_worked(self):
        blocker = socket.socket()
        blocker.bind(("127.0.0.1", 0))
        busy = blocker.getsockname()[1]
        blocker.listen(1)
        server = cs2_gsi.CS2GSIServer(port=busy)
        try:
            self.assertTrue(server.start())
            self.assertNotEqual(server.port, busy)
            with tempfile.TemporaryDirectory() as cfg:
                self.assertTrue(cs2_gsi.ensure_gsi_config_installed(cfg, server.port))
                text = open(os.path.join(cfg, cs2_gsi.GSI_CONFIG_NAMES[0]), encoding="utf-8").read()
                self.assertIn(f"127.0.0.1:{server.port}/", text)
        finally:
            server.stop()
            blocker.close()


class UpdaterNonAscii(unittest.TestCase):
    def test_helper_swaps_the_file_in_a_folder_with_non_ascii_characters(self):
        base = tempfile.mkdtemp()
        odd = os.path.join(base, "Тест Üser ñ с пробелами")
        os.makedirs(odd)
        exe = os.path.join(odd, "CS2_Command_Center.exe")
        new = exe + ".new"
        stand_in = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "whoami.exe")
        shutil.copy(stand_in, exe)
        shutil.copy(stand_in, new)
        with open(new, "ab") as fh:
            fh.write(b"NEWVERSION")
        before = os.path.getsize(exe)
        with mock.patch.object(updater.subprocess, "Popen"), mock.patch.object(updater.sys, "exit", side_effect=SystemExit), mock.patch.object(updater.os, "getpid", return_value=999999):
            with self.assertRaises(SystemExit):
                updater.spawn_updater_helper_and_exit(exe, new)
        proc = subprocess.Popen(["cmd.exe", "/c", os.path.join(odd, "_geronimo_updater.bat")], creationflags=0x08000000, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        swapped = False
        try:
            for _ in range(20):
                time.sleep(0.5)
                if os.path.exists(exe + ".old") and os.path.getsize(exe) > before:
                    swapped = True
                    break
        finally:
            subprocess.call(["taskkill", "/T", "/F", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
            shutil.rmtree(base, ignore_errors=True)
        self.assertTrue(swapped, "the update helper could not rename files in a folder with non-ASCII characters")


class ElevatedHandoff(unittest.TestCase):
    def test_relaunch_passes_appdata_steam_and_user(self):
        core = core_service.Core()
        core.paths = dict(core.paths, steam_path=r"D:\Spiele\Steam ünï")
        with mock.patch("ctypes.windll.shell32.ShellExecuteW", return_value=42) as sh, mock.patch("app_config.save_config", return_value=True), mock.patch.object(sys, "frozen", True, create=True):
            self.assertTrue(core.relaunch_admin("booster")["ok"])
        params = sh.call_args[0][3]
        self.assertIn("--elevated --page=booster", params)
        self.assertIn('"--appdata=', params)
        self.assertIn('"--steam=D:\\Spiele\\Steam ünï"', params)
        self.assertIn('"--user=', params)

    def test_elevated_copy_adopts_the_original_users_folders(self):
        with tempfile.TemporaryDirectory() as tmp:
            steam = os.path.join(tmp, "Steam")
            roaming = os.path.join(tmp, "Roaming")
            os.makedirs(steam)
            os.makedirs(roaming)
            argv = ["web_main.py", "--elevated", f"--appdata={roaming}", f"--steam={steam}", "--user=Original"]
            with mock.patch.object(sys, "argv", argv), mock.patch.dict(os.environ, {"APPDATA": r"C:\Users\Admin\AppData\Roaming"}, clear=False):
                web_main._apply_elevation_handoff()
                self.assertEqual(os.environ["APPDATA"], roaming)
                self.assertEqual(os.environ["CS2CC_STEAM_PATH"], steam)
                self.assertEqual(os.environ["CS2CC_ORIGINAL_USER"], "Original")
            for k in ("CS2CC_STEAM_PATH", "CS2CC_ORIGINAL_USER"):
                os.environ.pop(k, None)

    def test_bad_handoff_values_are_ignored(self):
        with mock.patch.object(sys, "argv", ["web_main.py", r"--appdata=Z:\nope", r"--steam=Z:\nope"]), mock.patch.dict(os.environ, {"APPDATA": r"C:\keep"}, clear=False):
            web_main._apply_elevation_handoff()
            self.assertEqual(os.environ["APPDATA"], r"C:\keep")
            self.assertNotIn("CS2CC_STEAM_PATH", os.environ)


class ConfigSafety(unittest.TestCase):
    def test_corrupt_config_is_kept_and_simultaneous_saves_stay_valid(self):
        import json
        import threading
        real = app_config.CONFIG_FILE
        with tempfile.TemporaryDirectory() as tmp:
            app_config.CONFIG_FILE = os.path.join(tmp, "config.json")
            try:
                open(app_config.CONFIG_FILE, "w", encoding="utf-8").write("{ not json")
                cfg = app_config.load_config()
                self.assertTrue(os.path.exists(app_config.CONFIG_FILE + ".corrupt"))               # the damaged file is not lost
                self.assertTrue(cfg)                                                               # defaults are still returned
                errors = []

                def save(i):
                    if not app_config.save_config({"n": i, "pad": "x" * 5000}):
                        errors.append(i)
                threads = [threading.Thread(target=save, args=(i,)) for i in range(30)]
                [t.start() for t in threads]
                [t.join() for t in threads]
                self.assertEqual(errors, [])
                self.assertIn("n", json.load(open(app_config.CONFIG_FILE, encoding="utf-8")))     # always a complete, valid file
                self.assertFalse([f for f in os.listdir(tmp) if f.endswith(".tmp")])
            finally:
                app_config.CONFIG_FILE = real


if __name__ == "__main__":
    unittest.main()
