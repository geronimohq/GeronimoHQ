"""The read-only 'Check' panels (verify_state.py) and the clean-ups that used to report success when nothing happened.
Folders, registry values and the Recycle Bin are faked; nothing on this PC is changed."""
import os
import tempfile
import time
import unittest
from unittest import mock

import _test_isolation  # noqa: F401  (temp config; must come first)
import core_logic
import core_service
import verify_state as vs


def touch(path, size=10, age_s=0):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(b"x" * size)
    if age_s:
        t = time.time() - age_s
        os.utime(path, (t, t))


class Engine(unittest.TestCase):
    def test_reads_back_each_tweak(self):
        with tempfile.TemporaryDirectory() as t:
            exe = os.path.join(t, "game", "bin", "win64", "cs2.exe")
            touch(exe)
            cfg = os.path.join(t, "game", "csgo", "cfg")
            os.makedirs(cfg)
            with open(os.path.join(cfg, "autoexec.cfg"), "w") as f:
                f.write("bind x y\n// " + core_logic.PERF_TITLE + "\n")
            touch(os.path.join(t, "game", "csgo", "dumps", "a.dmp"), 2048)
            local = os.path.join(t, "local")
            touch(os.path.join(local, "NVIDIA", "DXCache", "a.bin"), 4096)
            paths = {"cs2_exe": exe, "cfg_dir": cfg, "cs2_dir": t, "steam_path": None}
            with mock.patch.dict(os.environ, {"LOCALAPPDATA": local, "APPDATA": os.path.join(t, "roam")}), \
                    mock.patch.object(core_logic, "_dvr_is", side_effect=lambda values, capture: capture == 0), \
                    mock.patch.object(core_logic, "_reg_value", return_value="~ DISABLEDXMAXIMIZEDWINDOWEDMODE HIGHDPIAWARE"), \
                    mock.patch.object(core_logic, "get_active_power_plan", return_value=("Balanced", "381b4222-f694-41f0-9685-ff5bb260df2e")):
                rows = {r["key"]: r for r in vs.engine_check(paths)}
        self.assertEqual(rows["gamedvr"]["state"], "ok")
        self.assertEqual(rows["fullscreen"]["state"], "ok")
        self.assertEqual(rows["autoexec"]["state"], "ok")
        self.assertEqual(rows["dumps"]["state"], "off")
        self.assertIn("1 file", rows["dumps"]["value"])
        self.assertEqual(rows["shaders"]["state"], "info")
        self.assertIn("1 files", rows["shaders"]["value"])
        self.assertEqual(rows["power"]["value"], "Balanced")
        self.assertTrue(all(r["how"] for r in rows.values() if r["state"] != "na"))      # every row says how to check it without the app

    def test_defaults_and_missing_cs2(self):
        with mock.patch.object(core_logic, "_dvr_is", side_effect=lambda values, capture: capture == 1), \
                mock.patch.object(core_logic, "get_active_power_plan", return_value=("High performance", "")):
            rows = {r["key"]: r for r in vs.engine_check({"cs2_exe": None, "cfg_dir": None, "cs2_dir": None})}
        self.assertEqual(rows["gamedvr"]["state"], "off")
        self.assertEqual(rows["fullscreen"]["state"], "na")
        self.assertEqual(rows["autoexec"]["state"], "na")


class Maintenance(unittest.TestCase):
    def test_measures_what_each_cleanup_would_remove(self):
        with tempfile.TemporaryDirectory() as t:
            temp = os.path.join(t, "temp")
            touch(os.path.join(temp, "old.tmp"), 100, age_s=3 * 86400)
            touch(os.path.join(temp, "new.tmp"), 100)                                     # under 24 h: the clean-up leaves it, so it is not counted
            sysroot = os.path.join(t, "win")
            touch(os.path.join(sysroot, "SoftwareDistribution", "Download", "u.cab"), 300)
            appdata = os.path.join(t, "roam")
            touch(os.path.join(appdata, "discord", "Cache", "Cache_Data", "c"), 50)
            with mock.patch.dict(os.environ, {"TEMP": temp, "SystemRoot": sysroot, "APPDATA": appdata, "LOCALAPPDATA": os.path.join(t, "loc")}), \
                    mock.patch.object(core_logic, "recycle_bin_info", return_value=(0, 0)):
                rows = {r["key"]: r for r in vs.maint_check({"steam_path": None})}
        self.assertEqual(rows["temp"]["value"], "1 files, 0 KB can be cleaned")
        self.assertEqual(rows["win_update"]["state"], "off")
        self.assertEqual(rows["discord_steam"]["state"], "off")
        self.assertEqual(rows["recycle"]["state"], "ok")
        self.assertEqual(rows["dns"]["state"], "info")

    def test_core_state_check(self):
        core = core_service.Core()
        with mock.patch.object(vs, "maint_check", return_value=[{"key": "x", "label": "X", "state": "ok", "value": "v", "how": "h"}]):
            r = core.state_check("maintenance")
        self.assertTrue(r["ok"])
        self.assertIn("1 in place", r["summary"])
        self.assertFalse(core.state_check("bogus")["ok"])


class HonestCleanups(unittest.TestCase):
    def test_recycle_bin_already_empty_is_not_called_emptied(self):
        with mock.patch.object(core_logic, "recycle_bin_info", return_value=(0, 0)), \
                mock.patch.object(core_logic.ctypes.windll.shell32, "SHEmptyRecycleBinW") as empty:
            ok, logs = core_logic.empty_recycle_bin()
        self.assertTrue(ok)
        self.assertTrue(logs[0].startswith("[ALREADY]"))
        empty.assert_not_called()

    def test_recycle_bin_is_checked_after_emptying(self):
        with mock.patch.object(core_logic, "recycle_bin_info", side_effect=[(3, 3 * 1048576), (0, 0)]), \
                mock.patch.object(core_logic.ctypes.windll.shell32, "SHEmptyRecycleBinW", return_value=0):
            ok, logs = core_logic.empty_recycle_bin()
        self.assertTrue(ok)
        self.assertIn("3 item(s)", logs[0])
        with mock.patch.object(core_logic, "recycle_bin_info", side_effect=[(3, 10), (2, 5)]), \
                mock.patch.object(core_logic.ctypes.windll.shell32, "SHEmptyRecycleBinW", return_value=0):
            ok, logs = core_logic.empty_recycle_bin()
        self.assertFalse(ok)
        self.assertIn("still holds 2", logs[0])

    def test_dns_failure_is_reported_as_failure(self):
        bad = mock.Mock(returncode=1, stdout="", stderr="Access is denied.")
        with mock.patch.object(core_logic.subprocess, "run", return_value=bad):
            ok, logs = core_logic.flush_dns_cache()
        self.assertFalse(ok)
        self.assertIn("did not flush", logs[-1])

    def test_windows_update_cache_says_it_needs_administrator(self):
        with mock.patch.object(core_logic, "is_admin", return_value=False), mock.patch.object(core_logic.os, "remove") as rm:
            n, freed, logs = core_logic.clean_windows_update_cache()
        self.assertEqual((n, freed), (0, 0))
        self.assertIn("Administrator", logs[0])
        rm.assert_not_called()


class FullscreenKeepsUserFlags(unittest.TestCase):
    def _run(self, fn, current):
        writes = []
        class K:
            def __enter__(self): return self
            def __exit__(self, *a): return False
        with mock.patch.object(core_logic, "_reg_value", return_value=current),                 mock.patch.object(core_logic.winreg, "CreateKey", return_value=K()), mock.patch.object(core_logic.winreg, "OpenKey", return_value=K()),                 mock.patch.object(core_logic.winreg, "SetValueEx", side_effect=lambda k, n, r, t, v: writes.append(("set", v))),                 mock.patch.object(core_logic.winreg, "DeleteValue", side_effect=lambda k, n: writes.append(("delete", n))),                 mock.patch.object(core_logic.os.path, "exists", return_value=True):
            logs = fn(r"C:\Games\cs2.exe")
        return logs, writes

    def test_apply_adds_only_its_flag_and_keeps_run_as_admin(self):
        logs, w = self._run(core_logic.disable_fullscreen_optimizations, "~ RUNASADMIN")
        self.assertEqual(w, [("set", "~ RUNASADMIN DISABLEDXMAXIMIZEDWINDOWEDMODE")])
        self.assertIn("kept", logs[0])
        logs, w = self._run(core_logic.disable_fullscreen_optimizations, None)
        self.assertEqual(w, [("set", "~ DISABLEDXMAXIMIZEDWINDOWEDMODE")])

    def test_revert_removes_only_its_flag(self):
        _, w = self._run(core_logic.revert_fullscreen_optimizations, "~ RUNASADMIN DISABLEDXMAXIMIZEDWINDOWEDMODE")
        self.assertEqual(w, [("set", "~ RUNASADMIN")])
        _, w = self._run(core_logic.revert_fullscreen_optimizations, "~ DISABLEDXMAXIMIZEDWINDOWEDMODE")
        self.assertEqual(w, [("delete", r"C:\Games\cs2.exe")])
        _, w = self._run(core_logic.revert_fullscreen_optimizations, "~ DISABLEDXMAXIMIZEDWINDOWEDMODE HIGHDPIAWARE")   # what older versions wrote
        self.assertEqual(w, [("delete", r"C:\Games\cs2.exe")])
        logs, w = self._run(core_logic.revert_fullscreen_optimizations, "~ RUNASADMIN")                              # not ours: untouched
        self.assertEqual(w, [])
        self.assertTrue(logs[0].startswith("[ALREADY]"))


class WindowsUpdateCacheLeavesFreshFiles(unittest.TestCase):
    def test_files_from_the_last_two_hours_are_kept(self):
        with tempfile.TemporaryDirectory() as t:
            dl = os.path.join(t, "SoftwareDistribution", "Download")
            touch(os.path.join(dl, "old.cab"), 100, age_s=5 * 3600)
            touch(os.path.join(dl, "busy.cab"), 100)
            with mock.patch.dict(os.environ, {"SystemRoot": t}), mock.patch.object(core_logic, "is_admin", return_value=True):
                n, _freed, _logs = core_logic.clean_windows_update_cache()
            self.assertEqual(n, 1)
            self.assertTrue(os.path.exists(os.path.join(dl, "busy.cab")))
            self.assertFalse(os.path.exists(os.path.join(dl, "old.cab")))


if __name__ == "__main__":
    unittest.main()
