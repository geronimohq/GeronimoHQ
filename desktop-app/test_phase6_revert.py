"""AUDIT Phase 6 - every tweak has a working undo, and Restore Defaults calls them.
Everything that would touch Windows is mocked: registry (winreg), powercfg (subprocess),
message boxes. Autoexec tests use a temp folder. Nothing on this PC changes."""
import os
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _test_isolation  # noqa: E402,F401
import app  # noqa: E402
import core_logic  # noqa: E402


class _FakeKey:
    def __enter__(self): return self
    def __exit__(self, *a): return False


def _capture_registry():
    writes = []
    p = [mock.patch.object(core_logic.winreg, "CreateKey", return_value=_FakeKey()),
         mock.patch.object(core_logic.winreg, "OpenKey", return_value=_FakeKey()),
         mock.patch.object(core_logic.winreg, "SetValueEx", side_effect=lambda k, name, r, t, v: writes.append((name, v))),
         mock.patch.object(core_logic.winreg, "DeleteValue", side_effect=lambda k, name: writes.append((name, "<deleted>")))]
    return p, writes


class TweakUndo(unittest.TestCase):
    def _run(self, fn, *args):
        patches, writes = _capture_registry()
        for x in patches:
            x.start()
        try:
            fn(*args)
        finally:
            for x in reversed(patches):
                x.stop()
        return dict(writes)

    def test_game_dvr_revert_sets_windows_defaults(self):
        on = self._run(core_logic.optimize_windows_game_dvr)
        off = self._run(core_logic.revert_windows_game_dvr)
        self.assertEqual(set(on), set(off), "revert must touch the same values")
        self.assertEqual(off["GameDVR_Enabled"], 1)
        self.assertEqual(off["AppCaptureEnabled"], 1)
        self.assertTrue(any(on[k] != off[k] for k in on))

    def test_fullscreen_optimizations_revert(self):
        exe = os.path.join(tempfile.mkdtemp(dir=_test_isolation.TEMP_DIR), "cs2.exe")
        open(exe, "wb").close()   # dummy file: the function checks that the path exists
        with mock.patch.object(core_logic, "_reg_value", return_value=None):
            on = self._run(core_logic.disable_fullscreen_optimizations, exe)
        with mock.patch.object(core_logic, "_reg_value", return_value=on.get(exe)):         # revert reads back what apply wrote
            off = self._run(core_logic.revert_fullscreen_optimizations, exe)
        self.assertIn(exe, on)
        self.assertIn(exe, off)
        self.assertNotEqual(on[exe], off[exe])

    def test_power_plan_restores_the_previous_plan(self):
        cfg = {}
        prev = "11111111-2222-3333-4444-555555555555"
        with mock.patch.object(core_logic, "get_active_power_plan", return_value=("My Plan", prev)):
            core_logic.remember_power_plan(cfg)
        with mock.patch.object(core_logic, "get_active_power_plan", return_value=("High Performance", "x")):
            core_logic.remember_power_plan(cfg)          # must NOT overwrite the first record
        self.assertEqual(cfg["power_plan_before_app"]["guid"], prev)
        ran = []
        with mock.patch.object(core_logic.subprocess, "run",
                               side_effect=lambda cmd, **k: ran.append(cmd) or mock.Mock(returncode=0, stdout="", stderr="")):
            logs = core_logic.restore_previous_power_plan(cfg)
        self.assertEqual(ran, [["powercfg", "/setactive", prev]])
        self.assertIn("My Plan", logs[0])
        self.assertNotIn("power_plan_before_app", cfg)

    def test_power_plan_bad_guid_never_reaches_the_shell(self):
        cfg = {"power_plan_before_app": {"guid": "x & calc", "name": "evil"}}
        with mock.patch.object(core_logic, "set_power_plan", return_value=["balanced"]) as sp, \
                mock.patch.object(core_logic.subprocess, "run") as run:
            core_logic.restore_previous_power_plan(cfg)
        run.assert_not_called()
        sp.assert_called_once_with("balanced")

    def test_autoexec_restore_from_backup(self):
        d = tempfile.mkdtemp(dir=_test_isolation.TEMP_DIR)
        with open(os.path.join(d, "autoexec.cfg"), "w", encoding="utf-8") as f:
            f.write("// original\n")
        core_logic.install_autoexec(d)
        ok, _ = core_logic.restore_autoexec_backup(d)
        self.assertTrue(ok)
        with open(os.path.join(d, "autoexec.cfg"), encoding="utf-8") as f:
            self.assertEqual(f.read(), "// original\n")


class StartupNotElevated(unittest.TestCase):
    """D-07 (owner decision): Start with Windows = normal user, no '/rl highest' task."""
    def test_enable_never_creates_elevated_task_and_removes_old_one(self):
        import importlib
        real = importlib.reload(importlib.import_module("app_config"))  # undo the test stub
        try:
            runs = []
            with mock.patch.object(real.winreg, "OpenKey", return_value=_FakeKey()),                     mock.patch.object(real.winreg, "SetValueEx"),                     mock.patch.object(real.winreg, "DeleteValue"),                     mock.patch("subprocess.run", side_effect=lambda cmd, **k: runs.append(cmd) or mock.Mock(returncode=0)):
                self.assertTrue(real.set_windows_startup(True, True))
                real.set_windows_startup(False)
            flat = [" ".join(map(str, c)) for c in runs]
            self.assertFalse(any("/create" in c for c in flat), flat)
            self.assertFalse(any("highest" in c for c in flat), flat)
            self.assertTrue(any("/delete" in c and "CS2CommandCenter_AutoStart" in c for c in flat), flat)
        finally:
            importlib.reload(_test_isolation)  # re-apply temp config + stubs


class LegacyTaskMigration(unittest.TestCase):
    def _run(self, exists_seq, delete_rc):
        import importlib
        real = importlib.reload(importlib.import_module("app_config"))
        try:
            seq = list(exists_seq)
            def fake(cmd, **k):
                if "/query" in cmd:
                    return mock.Mock(returncode=0 if seq.pop(0) else 1)
                return mock.Mock(returncode=delete_rc)
            with mock.patch("subprocess.run", side_effect=fake):
                return real.migrate_legacy_startup_task()
        finally:
            importlib.reload(_test_isolation)

    def test_no_task(self):
        self.assertEqual(self._run([False], 0), "none")

    def test_removed(self):
        self.assertEqual(self._run([True, False], 0), "removed")

    def test_needs_admin(self):
        self.assertEqual(self._run([True, True], 1), "needs_admin")


class RestoreDefaults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = app.CS2TruePanoramaApp()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        with mock.patch.object(app.os, "_exit", lambda code=0: None):
            cls.root.exit_application()

    def _patches(self, ask):
        class _Sync:
            def __init__(self, target=None, daemon=None, **k): self.t = target
            def start(self): self.t()
        return [mock.patch.object(app.messagebox, "askyesno", return_value=ask),
                mock.patch.object(app.messagebox, "showinfo"),
                mock.patch.object(app.threading, "Thread", _Sync),
                mock.patch.object(core_logic, "revert_windows_game_dvr", return_value=["dvr"]),
                mock.patch.object(core_logic, "revert_fullscreen_optimizations", return_value=["fso"]),
                mock.patch.object(core_logic, "restore_autoexec_backup", return_value=(True, ["auto"])),
                mock.patch.object(core_logic, "restore_previous_power_plan", return_value=["power"])]

    def test_calls_every_revert_after_confirm(self):
        r = self.root
        r.paths["cs2_exe"] = r"C:\Games\cs2.exe"
        r.paths["cfg_dir"] = _test_isolation.TEMP_DIR
        ps = self._patches(True)
        mocks = [p.start() for p in ps]
        try:
            r.run_revert_all()
            for m in mocks[3:]:
                self.assertTrue(m.called, m)
        finally:
            for p in reversed(ps):
                p.stop()

    def test_cancel_changes_nothing(self):
        ps = self._patches(False)
        mocks = [p.start() for p in ps]
        try:
            self.root.run_revert_all()
            for m in mocks[3:]:
                self.assertFalse(m.called, m)
        finally:
            for p in reversed(ps):
                p.stop()


if __name__ == "__main__":
    _res = unittest.main(exit=False, verbosity=2)
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(0 if _res.result.wasSuccessful() else 1)
