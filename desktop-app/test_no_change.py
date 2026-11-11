"""Owner 2026-11-11: pressing Save / Apply / Restore when nothing would change must say so ("No changes were made"), not "saved".
Fake cfg folders, fake registry values and fake power plans only; nothing on this PC changes."""
import os
import tempfile
import threading
import time
import unittest
from unittest import mock

import _test_isolation  # noqa: F401  (temp config; must come first)
import app_config
import core_logic
import core_service


def cfg_dir():
    return tempfile.mkdtemp(dir=_test_isolation.TEMP_DIR)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, text):
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def wait_for(events, name, timeout=10):
    end = time.time() + timeout
    while time.time() < end:
        for e, d in list(events):
            if e == name:
                return d
        time.sleep(0.02)
    raise AssertionError(f"no '{name}' event")


class Autoexec(unittest.TestCase):
    def setUp(self):
        self.d = cfg_dir()
        self.path = os.path.join(self.d, "autoexec.cfg")
        self.core = core_service.Core()
        self.core.paths["cfg_dir"] = self.d

    def test_saving_unchanged_text_writes_nothing_and_keeps_the_backup(self):
        write(self.path, "bind a +jump\r\nfps_max 144\r\n")
        write(self.path + ".manual_bak", "OLDER VERSION")
        with mock.patch.object(app_config, "save_config", return_value=True):
            r = self.core.autoexec_save("bind a +jump\nfps_max 144\n")                  # the editor turns CRLF into LF: still the same text
        self.assertEqual((r["ok"], r["changed"]), (True, False))
        self.assertEqual(read(self.path + ".manual_bak"), "OLDER VERSION")                # the backup of the earlier version is not overwritten
        self.assertEqual(open(self.path, "rb").read(), b"bind a +jump\r\nfps_max 144\r\n")  # and the file is byte for byte as it was

    def test_a_real_edit_is_saved_with_a_backup(self):
        write(self.path, "bind a +jump\n")
        with mock.patch.object(app_config, "save_config", return_value=True):
            r = self.core.autoexec_save("bind a +jump\nbind b +duck\n")
        self.assertEqual((r["ok"], r["changed"]), (True, True))
        self.assertEqual(read(self.path), "bind a +jump\nbind b +duck\n")
        self.assertEqual(read(self.path + ".manual_bak"), "bind a +jump\n")

    def test_apply_twice_second_time_is_already_applied(self):
        write(self.path, "bind a +jump\n")
        ok, logs = core_logic.install_autoexec(self.d)
        self.assertTrue(ok and any(l.startswith("[SUCCESS]") for l in logs))
        first = read(self.path)
        ok, logs = core_logic.install_autoexec(self.d)
        self.assertTrue(ok)
        self.assertTrue(logs[-1].startswith("[ALREADY]"), logs)
        self.assertEqual(read(self.path), first)
        self.assertEqual(self.core.autoexec_install(), {"ok": True, "changed": False})

    def test_revert_when_it_already_matches_the_backup_or_is_already_clean(self):
        write(self.path, "// original\n")
        core_logic.install_autoexec(self.d)
        ok, logs = core_logic.restore_autoexec_backup(self.d)
        self.assertTrue(ok and logs[-1].startswith("[REVERTED]"))
        ok, logs = core_logic.restore_autoexec_backup(self.d)                            # now identical to the backup
        self.assertTrue(ok and logs[-1].startswith("[ALREADY]"), logs)
        os.remove(os.path.join(self.d, "autoexec_backup.cfg"))
        ok, logs = core_logic.restore_autoexec_backup(self.d)                            # no backup, no app block
        self.assertTrue(ok and logs[-1].startswith("[ALREADY]"), logs)
        self.assertFalse(self.core.autoexec_restore()["changed"])

    def test_fps_limit_same_value_is_already_set(self):
        write(self.path, "fps_max 144   // Framerate limit\nbind a +jump\n")
        before = read(self.path)
        ok, logs = core_logic.set_framerate_limit(self.d, 144)
        self.assertTrue(ok and logs[-1].startswith("[ALREADY]"))
        self.assertEqual(read(self.path), before)
        ok, logs = core_logic.set_framerate_limit(self.d, 200)
        self.assertTrue(ok and logs[-1].startswith("[AUTOEXEC]"))
        self.assertIn("fps_max 200", read(self.path))
        r = self.core.autoexec_fps(200)
        self.assertEqual((r["ok"], r["changed"]), (True, False))

    def test_ze_block_with_the_same_options_is_unchanged(self):
        opts = {"duck_key": "F7", "voice_mute_key": "F8"}
        first = core_logic.apply_ze_visual_and_hud_customizer(self.d, opts)
        self.assertTrue(first["success"] and not first.get("unchanged"))
        again = core_logic.apply_ze_visual_and_hud_customizer(self.d, opts)
        self.assertTrue(again["success"] and again["unchanged"])
        changed = core_logic.apply_ze_visual_and_hud_customizer(self.d, {"duck_key": "F9", "voice_mute_key": "F8"})
        self.assertTrue(changed["success"] and not changed.get("unchanged"))

    def test_a_file_longer_than_the_preview_is_flagged_so_it_is_not_cut_by_an_edit(self):
        write(self.path, "// x\n" * 20000)
        self.assertTrue(self.core.autoexec_state()["truncated"])
        write(self.path, "bind a +jump\n")
        self.assertFalse(self.core.autoexec_state()["truncated"])


class WindowsSettings(unittest.TestCase):
    def test_game_dvr_already_off_and_already_default(self):
        on = {("System\\GameConfigStore", "GameDVR_Enabled"): 0, ("System\\GameConfigStore", "GameDVR_FSEBehaviorMode"): 2,
              ("System\\GameConfigStore", "GameDVR_HonorUserFSEBehaviorMode"): 1, ("System\\GameConfigStore", "GameDVR_DXGIHonorFSEWindowsCompatible"): 1,
              ("Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR", "AppCaptureEnabled"): 0}
        with mock.patch.object(core_logic, "_reg_value", side_effect=lambda root, path, name: on.get((path, name))), mock.patch.object(core_logic.winreg, "CreateKey") as ck:
            logs = core_logic.optimize_windows_game_dvr()
        ck.assert_not_called()                                                           # nothing is written when it is already off
        self.assertTrue(logs[0].startswith("[ALREADY]"))
        off = {k: (1 if v == 0 else 0) for k, v in on.items()}
        off[("System\\GameConfigStore", "GameDVR_FSEBehaviorMode")] = 0
        off[("System\\GameConfigStore", "GameDVR_HonorUserFSEBehaviorMode")] = 0
        off[("System\\GameConfigStore", "GameDVR_DXGIHonorFSEWindowsCompatible")] = 0
        off[("System\\GameConfigStore", "GameDVR_Enabled")] = 1
        off[("Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR", "AppCaptureEnabled")] = 1
        with mock.patch.object(core_logic, "_reg_value", side_effect=lambda root, path, name: off.get((path, name))), mock.patch.object(core_logic.winreg, "CreateKey") as ck:
            logs = core_logic.revert_windows_game_dvr()
        ck.assert_not_called()
        self.assertTrue(logs[0].startswith("[ALREADY]"))

    def test_game_dvr_is_still_written_when_a_value_differs_or_is_unknown(self):
        with mock.patch.object(core_logic, "_reg_value", return_value=None), mock.patch.object(core_logic.winreg, "CreateKey") as ck, mock.patch.object(core_logic.winreg, "SetValueEx"):
            logs = core_logic.optimize_windows_game_dvr()
        self.assertTrue(ck.called)
        self.assertTrue(any(l.startswith("[SUCCESS]") for l in logs))

    def test_fullscreen_optimizations_already_disabled(self):
        exe = os.path.join(cfg_dir(), "cs2.exe")
        open(exe, "wb").close()
        with mock.patch.object(core_logic, "_reg_value", return_value="~ DISABLEDXMAXIMIZEDWINDOWEDMODE HIGHDPIAWARE"), mock.patch.object(core_logic.winreg, "CreateKey") as ck:
            logs = core_logic.disable_fullscreen_optimizations(exe)
        ck.assert_not_called()
        self.assertTrue(logs[0].startswith("[ALREADY]"))
        with mock.patch.object(core_logic.winreg, "OpenKey", side_effect=FileNotFoundError):
            self.assertTrue(core_logic.revert_fullscreen_optimizations(exe)[0].startswith("[ALREADY]"))

    def test_power_plan_already_active(self):
        with mock.patch.object(core_logic, "get_active_power_plan", return_value=("Balanced", core_logic.GUID_BALANCED)), mock.patch.object(core_logic, "run_tool") as rt:
            logs = core_logic.set_power_plan("balanced")
        rt.assert_not_called()                                                           # powercfg is never even started
        self.assertTrue(logs[0].startswith("[ALREADY]"))
        cfg = {"power_plan_before_app": {"guid": core_logic.GUID_BALANCED, "name": "Balanced"}}
        with mock.patch.object(core_logic, "get_active_power_plan", return_value=("Balanced", core_logic.GUID_BALANCED)), mock.patch.object(core_logic.subprocess, "run") as run:
            logs = core_logic.restore_previous_power_plan(cfg)
        run.assert_not_called()
        self.assertTrue(logs[0].startswith("[ALREADY]"))
        self.assertNotIn("power_plan_before_app", cfg)

    def test_no_crash_dumps_found_is_not_a_success_with_zero(self):
        with mock.patch.dict(os.environ, {"LOCALAPPDATA": cfg_dir()}):
            deleted, _freed, logs = core_logic.clean_cs2_temp_dumps(None)
        self.assertEqual(deleted, 0)
        self.assertTrue(logs[-1].startswith("[ALREADY]"))


class JobSummary(unittest.TestCase):
    def test_the_job_event_counts_steps_that_found_nothing_to_change(self):
        events = []
        core = core_service.Core(emit=lambda e, d: events.append((e, d)))
        core._start_job("demo", lambda: (core.log("[ALREADY] Game DVR is already off"), core.log("[ALREADY] Fullscreen already disabled")))
        done = wait_for(events, "job")
        self.assertEqual((done["already"], done["changed"], done["problems"]), (2, 0, 0))
        events.clear()
        core._start_job("demo2", lambda: (core.log("[ALREADY] x"), core.log("[SUCCESS] Power plan switched to: Balanced")))
        done = wait_for(events, "job")
        self.assertEqual((done["already"], done["changed"]), (1, 1))

    def test_one_click_optimize_on_a_pc_that_is_already_optimized_reports_nothing_changed(self):
        events = []
        core = core_service.Core(emit=lambda e, d: events.append((e, d)))
        core.paths.update(cs2_exe=None, cfg_dir=None, cs2_dir=None)
        with mock.patch.object(core_logic, "optimize_windows_game_dvr", return_value=["[ALREADY] dvr"]), mock.patch.object(core_logic, "remember_power_plan"), \
                mock.patch.object(core_logic, "set_power_plan", return_value=["[ALREADY] power"]), mock.patch.object(core_logic, "clean_shader_caches", return_value=(0, 0, [])), \
                mock.patch.object(app_config, "save_config", return_value=True), mock.patch.object(app_config, "update_optimization_timestamp"):
            core.engine_apply({"gamedvr": True, "power": "balanced", "shaders": True})
            done = wait_for(events, "job")
        self.assertEqual((done["changed"], done["problems"]), (0, 0))
        self.assertEqual(done["already"], 3)                                             # dvr, power and "no shader files found"

    def test_boost_already_high_says_so(self):
        with mock.patch.object(core_logic, "get_cs2_pids", return_value=[111]), mock.patch.object(core_logic.ctypes, "windll", create=True) as wl:
            wl.kernel32.OpenProcess.return_value = 5
            wl.kernel32.GetPriorityClass.return_value = core_logic.HIGH_PRIORITY_CLASS
            ok, msg = core_logic.boost_cs2_process()
        self.assertTrue(ok and "already at HIGH" in msg)
        wl.kernel32.SetPriorityClass.assert_not_called()


if __name__ == "__main__":
    unittest.main()
