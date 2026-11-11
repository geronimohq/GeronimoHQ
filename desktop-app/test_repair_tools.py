"""SFC, DISM, WinSxS and TRIM must show progress and end with a verdict the user can trust.
Only fake child processes, fake CBS.log files and fake command output are used: no real Windows tool is ever started."""
import os
import sys
import tempfile
import time
import unittest
from unittest import mock

import _test_isolation  # noqa: F401  (temp config; must come first)
import app_config
import core_logic
import core_service


def wait_for(events, name, timeout=10):
    end = time.time() + timeout
    while time.time() < end:
        for e, d in list(events):
            if e == name:
                return d
        time.sleep(0.02)
    raise AssertionError(f"no '{name}' event")


class Streaming(unittest.TestCase):
    def child(self, code):
        return [sys.executable, "-I", "-c", code]

    def test_progress_is_read_while_the_tool_runs_and_the_result_is_decoded(self):
        code = ("import sys,time\n"
                "for p in (5,40,100):\n"
                "    sys.stdout.buffer.write(('Verification %d%% complete.\\r' % p).encode('utf-16-le')); sys.stdout.buffer.flush(); time.sleep(0.3)\n"
                "sys.stdout.buffer.write('Windows Resource Protection did not find any integrity violations.'.encode('utf-16-le'))\n")
        seen = []
        rc, out, timed_out = core_logic.run_tool(self.child(code), 30, seen.append)
        self.assertEqual((rc, timed_out), (0, False))
        self.assertEqual(seen, [5.0, 40.0, 100.0])
        self.assertIn("did not find any integrity violations", out)

    def test_dism_style_bar_percentages_are_read(self):
        code = "import sys\nsys.stdout.write('[=====                      20.0%                           ]\\r[==========62.3%==========]\\r')\n"
        seen = []
        core_logic.run_tool(self.child(code), 30, seen.append)
        self.assertEqual(seen[-1], 62.3)

    def test_a_hung_tool_is_stopped_at_the_limit(self):
        t0 = time.time()
        rc, _out, timed_out = core_logic.run_tool(self.child("import time; time.sleep(60)"), 1, lambda p: None)
        self.assertTrue(timed_out and rc is None)
        self.assertLess(time.time() - t0, 15)

    def test_a_missing_tool_is_reported(self):
        rc, out, timed_out = core_logic.run_tool(["no_such_tool_xyz"], 5, lambda p: None)
        self.assertIsNone(rc)
        self.assertIn("not found", out)


class CbsEvidence(unittest.TestCase):
    CLEAN = ["[SR] Verifying 100 components", "[SR] Verify complete", "[SR] Repairing 0 components", "[SR] Repair complete"]

    def test_parse(self):
        r = core_logic.parse_sr_lines(self.CLEAN)
        self.assertTrue(r["verify_complete"] and r["repair_complete"])
        self.assertEqual((r["repairing"], r["cannot_repair"]), (0, 0))
        r = core_logic.parse_sr_lines(["[SR] Verify complete", "[SR] Repairing 3 components", "[SR] Cannot repair member file [l:20]\"x.dll\" of y"])
        self.assertEqual((r["repairing"], r["cannot_repair"]), (3, 1))

    def test_only_what_was_added_during_the_run_counts(self):
        with tempfile.TemporaryDirectory() as d:
            log = os.path.join(d, "CBS.log")
            old = "2020 [SR] Cannot repair member file [l:1]\"old.dll\"\n"
            open(log, "w").write(old)
            with mock.patch.object(core_logic, "CBS_LOG", log):
                before = core_logic._cbs_size()
                with open(log, "a") as f:
                    f.write("\n".join("2026 info " + l for l in self.CLEAN) + "\nunrelated line\n")
                r = core_logic.cbs_evidence_since(before)
                self.assertEqual(r["cannot_repair"], 0)                       # the old failure is not blamed on this run
                self.assertTrue(r["verify_complete"])
                os.remove(log)
                self.assertIsNone(core_logic.cbs_evidence_since(before))       # unreadable log: no evidence, not a guess


class SfcVerdict(unittest.TestCase):
    def classify(self, rc, out, sr=None):
        return core_logic._classify_sfc(rc, out, sr, 125)

    def test_english_verdicts(self):
        r = self.classify(0, "Verification 100% complete. Windows Resource Protection did not find any integrity violations.")
        self.assertEqual((r["status"], r["ok"]), ("clean", True))
        self.assertIn("Windows said: Windows Resource Protection did not find", " ".join(r["evidence"]))
        self.assertNotIn("100%", " ".join(r["evidence"]))
        self.assertEqual(self.classify(0, "found corrupt files and successfully repaired them.")["status"], "repaired")
        self.assertIn("Restart", self.classify(0, "found corrupt files and successfully repaired them.")["next"])
        r = self.classify(0, "found corrupt files but was unable to fix some of them.")
        self.assertEqual((r["status"], r["ok"]), ("unfixable", False))
        self.assertIn("DISM", r["next"])
        self.assertEqual(self.classify(0, "There is a system repair pending which requires reboot to complete.")["status"], "reboot")
        self.assertEqual(self.classify(None, "sfc was not found on this PC")["status"], "failed")
        self.assertEqual(self.classify(5, "boom")["status"], "failed")

    def test_other_languages_are_decided_by_the_untranslated_cbs_lines(self):
        de = "Der Windows-Ressourcenschutz hat keine Integritätsverletzungen gefunden."
        clean = {"verify_complete": True, "repair_complete": True, "cannot_repair": 0, "repairing": 0, "lines": 4}
        self.assertEqual(self.classify(0, de, clean)["status"], "clean")
        self.assertEqual(self.classify(0, de, dict(clean, repairing=2))["status"], "repaired")
        r = self.classify(0, de, dict(clean, cannot_repair=1))
        self.assertEqual((r["status"], r["ok"]), ("unfixable", False))
        # nothing to confirm from: honest "could not confirm", never a silent success
        r = self.classify(0, de, None)
        self.assertEqual(r["status"], "unverified")
        self.assertIn("could not confirm", r["headline"])
        r = self.classify(0, de, {"verify_complete": False, "repair_complete": False, "cannot_repair": 0, "repairing": 0, "lines": 0})
        self.assertEqual(r["status"], "unverified")

    def test_a_failed_run_is_not_called_clean_because_of_old_log_lines(self):
        old = {"verify_complete": True, "repair_complete": True, "cannot_repair": 0, "repairing": 0, "lines": 4}
        self.assertEqual(self.classify(5, "irgendein Fehler", old)["status"], "failed")


class DismVerdict(unittest.TestCase):
    def test_success_and_repair_and_restart(self):
        r = core_logic._classify_dism("dism", 0, "[===100.0%===] The restore operation completed successfully. The operation completed successfully.", 600, None, None)
        self.assertEqual((r["status"], r["ok"]), ("clean", True))
        r = core_logic._classify_dism("dism", 0, "The component store corruption was repaired. The restore operation completed successfully.", 600, None, None)
        self.assertEqual(r["status"], "repaired")
        r = core_logic._classify_dism("dism", 3010, "The operation completed successfully. restart required", 60, None, None)
        self.assertTrue(r["ok"] and "Restart" in r["next"])

    def test_known_error_codes_give_advice(self):
        r = core_logic._classify_dism("dism", -2146498529, "Error: 0x800f081f The source files could not be found.", 90, None, None)   # 0x800F081F as Windows returns it
        self.assertEqual((r["status"], r["ok"]), ("failed", False))
        self.assertIn("internet", r["next"])
        self.assertIn("0x800F081F", " ".join(r["evidence"]))
        self.assertTrue(r["logs"][-1].startswith("[DISM ERROR]"))
        r = core_logic._classify_dism("dism", 12345, "weird", 90, None, None)
        self.assertEqual(r["status"], "failed")
        self.assertIn("dism.log", r["next"])

    def test_winsxs_shows_free_space_before_and_after_and_does_not_invent_a_number(self):
        gb = 1024 ** 3
        r = core_logic._classify_dism("winsxs", 0, "The operation completed successfully.", 300, 100 * gb, 101 * gb)
        self.assertIn("before 100.00 GB, after 101.00 GB (+1.00 GB)", " ".join(r["evidence"]))
        self.assertIn("does not report how much it freed", " ".join(r["evidence"]))
        r = core_logic._classify_dism("winsxs", 0, "ok", 300, None, None)
        self.assertNotIn("before", " ".join(r["evidence"]))


class TrimVerdict(unittest.TestCase):
    def test_trim(self):
        r = core_logic._classify_trim(0, "Retrim: Total space trimmed = 12.50 GB", 60)
        self.assertTrue(r["ok"])
        self.assertIn("12.50 GB", " ".join(r["evidence"]))
        r = core_logic._classify_trim(0, "done", 60)
        self.assertIn("did not state how much", " ".join(r["evidence"]))
        self.assertFalse(core_logic._classify_trim(1, "busy", 60)["ok"])


class RunRepair(unittest.TestCase):
    def test_needs_admin_and_never_touches_windows_without_it(self):
        with mock.patch.object(core_logic, "is_admin", return_value=False), mock.patch.object(core_logic, "run_tool") as rt:
            r = core_logic.run_repair("sfc")
        rt.assert_not_called()
        self.assertEqual((r["status"], r["ok"]), ("admin", False))
        self.assertTrue(r["logs"][-1].startswith("[ADMIN REQUIRED]"))

    def test_timeout_and_progress_callback_are_passed_on(self):
        got = {}

        def fake(args, timeout, on_progress=None):
            got.update(args=args, timeout=timeout, cb=on_progress)
            return None, "", True
        with mock.patch.object(core_logic, "is_admin", return_value=True), mock.patch.object(core_logic, "run_tool", side_effect=fake):
            r = core_logic.run_repair("dism", lambda p: None)
        self.assertEqual(got["args"], ["dism", "/online", "/cleanup-image", "/restorehealth"])
        self.assertEqual(got["timeout"], 90 * 60)
        self.assertIsNotNone(got["cb"])
        self.assertEqual(r["status"], "timeout")
        self.assertIn("stopped waiting", r["logs"][-1])

    def test_start_note_comes_first_and_the_verdict_last(self):
        with mock.patch.object(core_logic, "is_admin", return_value=True), mock.patch.object(core_logic, "run_tool", return_value=(0, "did not find any integrity violations", False)), \
                mock.patch.object(core_logic, "_cbs_size", return_value=None), mock.patch.object(core_logic, "cbs_evidence_since", return_value=None):
            r = core_logic.run_repair("sfc")
        self.assertTrue(r["logs"][0].startswith("[SFC] Scanning"))
        self.assertTrue(r["logs"][-1].startswith("[SUCCESS]"))


class ServiceFlow(unittest.TestCase):
    def test_progress_result_last_run_and_state(self):
        events = []
        core = core_service.Core(emit=lambda e, d: events.append((e, d)))
        core.config.pop("maint_tool_last", None)

        def fake(name, cb=None):
            cb(10.0)
            self.assertEqual(core.maint_state()["tool_run"]["pct"], 10.0)        # the screen can ask what is running while it runs
            return core_logic._result("sfc", "clean", True, "SFC check complete: Zero system file corruptions detected.", "d", "", ["Exit code: 0"], 61)
        with mock.patch.object(core_logic, "is_admin", return_value=True), mock.patch.object(core_logic, "run_repair", side_effect=fake), \
                mock.patch.object(app_config, "save_config", return_value=True):
            r = core.maint_tool("sfc")
            self.assertTrue(r["ok"] and r["started"] > 0)
            res = wait_for(events, "tool_result")
            wait_for(events, "job")
        self.assertEqual((res["status"], res["tool"]), ("clean", "sfc"))
        self.assertNotIn("logs", res)
        names = [e for e, _ in events]
        self.assertLess(names.index("tool_progress"), names.index("tool_result"))
        self.assertLess(names.index("tool_result"), names.index("job"))
        st = core.maint_state()
        self.assertIsNone(st["tool_run"])
        self.assertEqual(st["tool_last"]["sfc"]["status"], "clean")
        self.assertTrue(any("Zero system file corruptions" in l["msg"] for l in core.log_buf))

    def test_a_crash_inside_the_tool_still_clears_the_running_state(self):
        events = []
        core = core_service.Core(emit=lambda e, d: events.append((e, d)))
        with mock.patch.object(core_logic, "is_admin", return_value=True), mock.patch.object(core_logic, "run_repair", side_effect=RuntimeError("boom")):
            self.assertTrue(core.maint_tool("dism")["ok"])
            done = wait_for(events, "job")
        self.assertFalse(done["ok"])
        self.assertIsNone(core.maint_state()["tool_run"])
        self.assertIsNone(core._busy_long)


if __name__ == "__main__":
    unittest.main()
