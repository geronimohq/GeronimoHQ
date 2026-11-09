"""
AUDIT Phase 3 - functional checks. Safe on the owner's PC: config redirected to temp,
registry / Task Scheduler / pop-ups stubbed, no file cleaning runs (cleaners are mocked),
GSI tests use free ports (never 3000).
"""
import os
import sys
import time
import shutil
import tempfile
import unittest
from unittest import mock

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import app_config  # noqa: E402

_TMP = tempfile.mkdtemp(prefix="cs2cc_p3_")
app_config.CONFIG_FILE = os.path.join(_TMP, "command_center_config.json")
app_config.set_windows_startup = lambda enabled, minimized=False: True
app_config.is_windows_startup_enabled = lambda: False
app_config.is_windows_startup_minimized = lambda: False

import app  # noqa: E402
import core_logic  # noqa: E402
import cs2_gsi  # noqa: E402


def _quiet():
    return mock.patch.multiple(app.messagebox, showinfo=mock.DEFAULT, showwarning=mock.DEFAULT,
                               showerror=mock.DEFAULT, askyesno=mock.DEFAULT)


class AppBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.errors = []
        cls.root = app.CS2TruePanoramaApp()
        cls.root.withdraw()
        cls.root.report_callback_exception = lambda exc, val, tb: cls.errors.append(f"{exc.__name__}: {val}")

    @classmethod
    def tearDownClass(cls):
        try:
            with mock.patch.object(app.os, "_exit", lambda code=0: None):
                cls.root.exit_application()
        except Exception:
            pass


class P3_01_SettingsDoSomething(AppBase):
    def test_start_page(self):
        keys = {"DASHBOARD", "SERVERS", "FAQ"}
        self.assertEqual(app_config.start_page_key({"open_on_page": "Dashboard", "last_page_key": "FAQ"}, keys), "DASHBOARD")
        self.assertEqual(app_config.start_page_key({"open_on_page": "Last used page", "last_page_key": "FAQ"}, keys), "FAQ")
        self.assertEqual(app_config.start_page_key({"open_on_page": "Last used page", "last_page_key": "GONE"}, keys), "DASHBOARD")

    def test_refresh_speed(self):
        self.assertEqual(app_config.refresh_interval_ms({"server_refresh_speed": "Live (1s)"}), 1000)
        self.assertEqual(app_config.refresh_interval_ms({"server_refresh_speed": "Eco (15s)"}), 15000)
        self.assertEqual(app_config.refresh_interval_ms({}), 5000)

    def test_sniper_sound_follows_setting(self):
        r = self.root
        with mock.patch.object(app, "play_calm_tone") as tone, mock.patch.object(r.sniper, "stop"), \
                mock.patch.object(r, "_start_sniper_cooldown_timer", create=True), _quiet():
            r.config["sniper_sound_enabled"] = True
            try:
                r._on_sniper_success_ui("1.2.3.4", 27015, "Test", "x")
            except Exception:
                pass
            self.assertTrue(tone.called)
            tone.reset_mock()
            r.config["sniper_sound_enabled"] = False
            try:
                r._on_sniper_success_ui("1.2.3.4", 27015, "Test", "x")
            except Exception:
                pass
            self.assertFalse(tone.called)

    def test_settings_discord_tick_is_the_real_switch(self):
        r = self.root
        r.config["discord_rpc_enabled"] = True
        with _quiet(), mock.patch.object(r, "_on_discord_toggle") as toggle:
            r.open_settings_dialog()
            r._settings_dialog_vars["discord_rpc_enabled"].set(False)
            r._settings_dialog_save()
        self.assertFalse(r.config["discord_rpc_enabled"])
        self.assertTrue(toggle.called or not hasattr(r, "var_discord_enabled"))
        r.config["discord_rpc_enabled"] = True

    def test_no_dead_settings_left(self):
        with open(os.path.join(HERE, "app.py"), encoding="utf-8") as fh:
            src = fh.read()
        for key in app_config.SETTINGS_DEFAULTS:
            uses = src.count(f'"{key}"')
            self.assertGreaterEqual(uses, 1, key)
        for dead in ("discord_presence_share", "sniper_sound_volume"):
            self.assertNotIn(f'"{dead}"', src)


class P3_02_NoInventedMapTime(unittest.TestCase):
    def test_source(self):
        with open(os.path.join(HERE, "app.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertNotIn("hash(sid)", src)
        self.assertIn('pre = "" if getattr(self, "server_map_start_exact", {}).get(sid) else "≥ "', src)


class P3_D13_GsiPortBusy(unittest.TestCase):
    def test_port_clash_is_reported(self):
        a = cs2_gsi.CS2GSIServer(port=0)
        self.assertTrue(a.start())
        try:
            b = cs2_gsi.CS2GSIServer(port=a.httpd.server_address[1])
            self.assertFalse(b.start())
            self.assertIn("already in use", b.last_error)
        finally:
            a.stop()


class P3_D12_MaintenanceAsksFirst(AppBase):
    def test_cancel_deletes_nothing(self):
        r = self.root
        with _quiet() as boxes, mock.patch.object(core_logic, "clean_windows_temp_files") as clean, \
                mock.patch.object(app.threading, "Thread") as th:
            boxes["askyesno"].return_value = False
            r.maint_temp.set(True)
            r.run_pc_maintenance()
            boxes["askyesno"].assert_called_once()
            msg = boxes["askyesno"].call_args[0][1]
            self.assertIn("Windows temp files", msg)
            th.assert_not_called()
            clean.assert_not_called()

    def test_nothing_ticked(self):
        r = self.root
        saved = [v.get() for v in (r.maint_temp, r.maint_win_update, r.maint_discord_steam, r.maint_thumb, r.maint_recycle, r.maint_dns)]
        for v in (r.maint_temp, r.maint_win_update, r.maint_discord_steam, r.maint_thumb, r.maint_recycle, r.maint_dns):
            v.set(False)
        with _quiet() as boxes, mock.patch.object(app.threading, "Thread") as th:
            r.run_pc_maintenance()
            boxes["askyesno"].assert_not_called()
            th.assert_not_called()
        for v, s in zip((r.maint_temp, r.maint_win_update, r.maint_discord_steam, r.maint_thumb, r.maint_recycle, r.maint_dns), saved):
            v.set(s)


class P3_Smoke_EveryPage(AppBase):
    def test_every_page_builds_without_errors(self):
        r = self.root
        with _quiet():
            for key in list(r.nav_items.keys()):
                r._select_nav(key)
                r.update_idletasks()
                end = time.time() + 0.4
                while time.time() < end:
                    r.update()
                    time.sleep(0.02)
                self.assertIn(key, r.pages)
        self.assertEqual(self.errors, [], "\n".join(self.errors))
        print(f"\n[smoke] {len(r.nav_items)} pages opened, 0 Tk callback errors")


if __name__ == "__main__":
    try:
        _res = unittest.main(exit=False, verbosity=2)
        ok = _res.result.wasSuccessful()
    finally:
        shutil.rmtree(_TMP, ignore_errors=True)
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(0 if ok else 1)
