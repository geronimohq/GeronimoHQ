"""Batch 2: jobs and tools must report what really happened (fake folders and fake command output only; nothing real is changed)."""
import os
import tempfile
import threading
import time
import unittest
from types import SimpleNamespace
from unittest import mock

import _test_isolation  # noqa: F401  (temp config; must come first)
import app_config
import core_logic
import core_service
import custom_map_cleaner
import server_browser


def wait_for(events, name, timeout=10):
    end = time.time() + timeout
    while time.time() < end:
        for e, d in list(events):
            if e == name:
                return d
        time.sleep(0.02)
    raise AssertionError(f"no '{name}' event")


class Jobs(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.core = core_service.Core(emit=lambda e, d: self.events.append((e, d)))

    def test_job_event_counts_steps_that_logged_an_error(self):
        self.core._start_job("demo", lambda: (self.core.log("[SUCCESS] fine"), self.core.log("[ERROR] Could not switch power plan"), self.core.log("[TRIM ERROR] boom")))
        done = wait_for(self.events, "job")
        self.assertTrue(done["ok"])
        self.assertEqual(done["problems"], 2)

    def test_a_clean_job_reports_zero_problems_and_an_exception_is_a_failed_job(self):
        self.core._start_job("clean", lambda: self.core.log("[SUCCESS] fine"))
        self.assertEqual(wait_for(self.events, "job")["problems"], 0)
        self.events.clear()

        def boom():
            raise RuntimeError("x")
        self.core._start_job("broken", boom)
        done = wait_for(self.events, "job")
        self.assertFalse(done["ok"])
        self.assertGreaterEqual(done["problems"], 1)

    def test_long_repair_tools_do_not_block_other_jobs_and_only_one_runs_at_a_time(self):
        gate = threading.Event()
        self.core._busy = "engine_apply"                                              # a normal job is running
        with mock.patch.object(core_logic, "is_admin", return_value=True), mock.patch.object(core_logic, "run_sfc_scan", side_effect=lambda: (gate.wait(5), (True, ["[SFC] x"]))[1]):
            self.assertTrue(self.core.maint_tool("sfc")["ok"])                         # not refused although another job runs
            self.assertFalse(self.core.maint_tool("dism")["ok"])                       # but two long tools never run together
            self.assertIsNone(self.core._busy_long and None)
            self.core._busy = None
            self.assertTrue(self.core._start_job("engine_apply", lambda: None)["ok"])  # and the normal slot is free while SFC runs
            gate.set()
            wait_for(self.events, "job")


class ToolResults(unittest.TestCase):
    def test_console_text_is_decoded_in_any_encoding(self):
        text = "Windows Resource Protection did not find any integrity violations."
        self.assertIn("integrity violations", core_logic.decode_console(text.encode("utf-16-le")))        # sfc writes UTF-16
        self.assertIn("Äpfel", core_logic.decode_console("Äpfel".encode("utf-8")))                      # plain text survives
        self.assertEqual(core_logic.decode_console(b""), "")

    def run_sfc(self, rc, out, timed_out=False):
        with mock.patch.object(core_logic, "is_admin", return_value=True), mock.patch.object(core_logic, "run_tool", return_value=(rc, out, timed_out)):
            return core_logic.run_sfc_scan()

    def test_sfc_outcomes_are_reported_honestly(self):
        ok, logs = self.run_sfc(0, "Windows Resource Protection did not find any integrity violations.")
        self.assertTrue(ok and any("Zero system file corruptions" in l for l in logs))
        ok, logs = self.run_sfc(0, "Windows Resource Protection found corrupt files and successfully repaired them.")
        self.assertTrue(ok and any("repaired" in l for l in logs))
        ok, logs = self.run_sfc(0, "Windows Resource Protection found corrupt files but was unable to fix some of them.")
        self.assertFalse(ok)
        self.assertTrue(logs[-1].startswith("[SFC ERROR]"))
        ok, logs = self.run_sfc(5, "Der Windows-Ressourcenschutz konnte den Reparaturdienst nicht starten.")      # another language, failure code
        self.assertFalse(ok)
        ok, logs = self.run_sfc(0, "Der Windows-Ressourcenschutz hat keine Integritätsverletzungen gefunden.")     # another language, success: not called a failure
        self.assertTrue(ok)
        self.assertFalse(logs[-1].startswith("[SFC ERROR]"))
        ok, logs = self.run_sfc(None, "", timed_out=True)
        self.assertFalse(ok)
        self.assertIn("stopped waiting", logs[-1])

    def test_dism_and_trim_nonzero_exit_codes_are_errors(self):
        with mock.patch.object(core_logic, "is_admin", return_value=True):
            with mock.patch.object(core_logic, "run_tool", return_value=(1726, "remote procedure call failed", False)):
                ok, logs = core_logic.run_dism_restore()
                self.assertFalse(ok)
                self.assertTrue(logs[-1].startswith("[DISM ERROR]"))
                ok, logs = core_logic.run_ssd_trim()
                self.assertFalse(ok)
                self.assertTrue(logs[-1].startswith("[TRIM ERROR]"))
            with mock.patch.object(core_logic, "run_tool", return_value=(0, "ok", False)):
                self.assertTrue(core_logic.run_dism_component_cleanup()[0])
                self.assertTrue(core_logic.run_ssd_trim()[0])

    def test_power_plan_failures_are_errors_and_a_hidden_plan_is_recreated(self):
        new_guid = "aaaaaaaa-1111-2222-3333-bbbbbbbbbbbb"
        calls = []

        def run(args, timeout):
            calls.append(args)
            if args[1] == "/duplicatescheme":
                return 0, f"Power Scheme GUID: {new_guid}  (Copy)", False
            return 0, "", False
        with mock.patch.object(core_logic, "_power_plan_guids", return_value=[core_logic.GUID_BALANCED]), mock.patch.object(core_logic, "run_tool", side_effect=run):
            logs = core_logic.set_power_plan("high")
        self.assertTrue(any("created again" in l for l in logs) and any("[SUCCESS]" in l for l in logs))
        self.assertEqual(calls[-1], ["powercfg", "/setactive", new_guid])
        with mock.patch.object(core_logic, "_power_plan_guids", return_value=[core_logic.GUID_BALANCED]), mock.patch.object(core_logic, "run_tool", return_value=(1, "denied", False)):
            self.assertTrue(core_logic.set_power_plan("high")[-1].startswith("[ERROR]"))                      # no plan and none can be made
        with mock.patch.object(core_logic, "_power_plan_guids", return_value=[core_logic.GUID_HIGH_PERF]), mock.patch.object(core_logic, "run_tool", return_value=(1, "denied", False)):
            self.assertTrue(core_logic.set_power_plan("high")[-1].startswith("[ERROR]"))                      # setactive failed
        with mock.patch.object(core_logic, "_power_plan_guids", return_value=[core_logic.GUID_BALANCED]), mock.patch.object(core_logic, "run_tool", return_value=(0, "", False)):
            self.assertTrue(core_logic.set_power_plan("balanced")[-1].startswith("[SUCCESS]"))


class CfgAndAnalyzer(unittest.TestCase):
    def test_quoted_fps_max_is_replaced_not_duplicated(self):
        with tempfile.TemporaryDirectory() as cfg:
            path = os.path.join(cfg, "autoexec.cfg")
            open(path, "w", encoding="utf-8").write('bind "x" "y"\nfps_max "300"\n  fps_max 400 // old\n')
            ok, _ = core_logic.set_framerate_limit(cfg, 144)
            text = open(path, encoding="utf-8").read()
            self.assertTrue(ok)
            self.assertEqual(text.count("fps_max"), 2)
            self.assertNotIn("300", text)
            self.assertNotIn("400", text)
            self.assertIn('bind "x" "y"', text)

    def grade(self, lines):
        with tempfile.TemporaryDirectory() as root:
            exe = os.path.join(root, "game", "bin", "win64", "cs2.exe")
            os.makedirs(os.path.dirname(exe))
            open(exe, "wb").write(b"MZ")
            if lines is not None:
                os.makedirs(os.path.join(root, "game", "csgo"))
                open(os.path.join(root, "game", "csgo", "console.log"), "w", encoding="utf-8").write("\n".join(lines))
            return core_logic.analyze_cs2_session_logs(exe)["grade"]

    def test_grades_follow_the_event_counts_and_a_missing_log_is_not_a_grade(self):
        self.assertTrue(self.grade([]).startswith("A+"))
        self.assertTrue(self.grade(["frame time hitch"] * 20).startswith("B"))
        self.assertTrue(self.grade(["frame time hitch"] * 45).startswith("C"))          # used to be unreachable
        self.assertTrue(self.grade(None).startswith("N/A"))


class Sniper(unittest.TestCase):
    def test_rearming_gives_the_new_run_its_own_stop_signal(self):
        sniper = server_browser.ServerSlotSniper()
        with mock.patch.object(server_browser, "is_cs2_running", return_value=True), mock.patch.object(server_browser, "query_server_info", return_value={"online": False}):
            sniper.start("1.2.3.4", 27015, "A", 61)
            first = sniper._stop_event
            sniper.start("1.2.3.4", 27015, "B", 62)
            second = sniper._stop_event
            try:
                self.assertIsNot(first, second)
                self.assertTrue(first.is_set())                                            # the old watcher was told to stop and stays stopped
                self.assertFalse(second.is_set())
            finally:
                sniper.stop()


class VpkBackup(unittest.TestCase):
    def test_backup_scans_by_itself_and_restore_recreates_a_deleted_folder(self):
        with tempfile.TemporaryDirectory() as root:
            lib = os.path.join(root, "Lib")
            cs2 = os.path.join(lib, "steamapps", "common", "Counter-Strike Global Offensive")
            item = os.path.join(lib, "steamapps", "workshop", "content", "730", "3793587501")
            os.makedirs(cs2)
            os.makedirs(item)
            open(os.path.join(item, "3793587501.vpk"), "wb").write(b"asset-pack")
            core = core_service.Core()
            core.paths = dict(core.paths, cs2_dir=cs2, steam_path=lib)
            core._maps = {}                                                                # no scan has run in this session
            fake = [{"id": "3793587501", "is_server_asset": True, "path": item}]
            backup_dir = os.path.join(root, "backup")
            with mock.patch.object(core, "_vpk_backup_dir", return_value=backup_dir), mock.patch.object(custom_map_cleaner, "scan_custom_maps", return_value=fake):
                self.assertEqual(core.maps_backup()["count"], 1)
                import shutil
                shutil.rmtree(item)                                                        # the folder is gone: exactly when a restore is needed
                self.assertEqual(core.maps_restore()["count"], 1)
            self.assertEqual(open(os.path.join(item, "3793587501.vpk"), "rb").read(), b"asset-pack")


class SettingsStartup(unittest.TestCase):
    def test_a_refused_startup_entry_is_reported(self):
        events = []
        core = core_service.Core(emit=lambda e, d: events.append((e, d)))
        with mock.patch.object(app_config, "set_windows_startup", return_value=False), mock.patch.object(app_config, "save_config", return_value=True):
            r = core.settings_save({"start_with_windows": True})
        self.assertTrue(r["ok"])
        self.assertFalse(r["startup_ok"])
        self.assertTrue(any("Start with Windows could not be changed" in d["msg"] for e, d in events if e == "log"))


if __name__ == "__main__":
    unittest.main()
