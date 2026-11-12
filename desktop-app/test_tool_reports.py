"""Text reports of SFC / DISM / TRIM runs and the 'Windows' record' openers. Reports go to a temp folder (CS2CC_REPORTS_DIR, set by
_test_isolation); CBS.log and dism.log are faked. Nothing here runs a Windows tool."""
import datetime
import os
import tempfile
import unittest
from unittest import mock

import _test_isolation  # noqa: F401  (temp config + temp reports folder; must come first)
import core_logic
import core_service
import tool_reports as tr

RES = {"tool": "sfc", "title": "System File Checker (SFC)", "status": "clean", "ok": True, "headline": "SFC check complete: Zero system file corruptions detected.",
       "detail": "Windows checked every protected system file and found nothing wrong.", "next": "", "evidence": ["Exit code: 0", "Took 1 min 33 s."],
       "seconds": 93, "log_file": tr.CBS_LOG, "sr_lines": ["2026-11-12 03:38:01, Info CSI 00000001 [SR] Verify complete"]}


class Reports(unittest.TestCase):
    def test_reports_never_go_to_the_real_documents_in_tests(self):
        self.assertIn("cs2cc_test_", tr.reports_dir())

    def test_report_text_has_result_evidence_sr_lines_and_where_windows_keeps_its_record(self):
        text = tr.build_text(RES, "v2.0.11", datetime.datetime(2026, 11, 12, 3, 38))
        for part in ("System File Checker (SFC) report", "12 November 2026, 03:38", "Zero system file corruptions", "Duration: 1 min 33 s",
                     "Exit code: 0", "[SR] Verify complete", 'findstr /c:"[SR]"', "v2.0.11"):
            self.assertIn(part, text)
        self.assertIn("event 258", tr.build_text(dict(RES, tool="trim", sr_lines=[]), ""))
        self.assertIn("dism.log", tr.build_text(dict(RES, tool="dism", sr_lines=[]), ""))

    def test_write_keeps_the_newest_ten_per_tool_and_only_opens_its_own_files(self):
        paths = [tr.write_report(RES, "", datetime.datetime(2026, 1, 1, 0, 0, i)) for i in range(13)]
        left = [f for f in os.listdir(tr.reports_dir()) if f.startswith("sfc_2")]               # every sfc report in the folder
        self.assertEqual(len(left), tr.KEEP_PER_TOOL)
        self.assertTrue(tr.is_report_path(paths[-1]))
        self.assertFalse(tr.is_report_path(paths[0]))                                    # pruned
        with open(paths[-1], encoding="utf-8-sig") as f:
            self.assertIn("Zero system file corruptions", f.read())
        outside = os.path.join(tempfile.gettempdir(), "x.txt")
        self.assertFalse(tr.is_report_path(outside))
        self.assertFalse(tr.is_report_path(os.path.join(tr.reports_dir(), "..", "x.txt")))
        self.assertFalse(tr.is_report_path(r"C:\Windows\System32\drivers\etc\hosts"))


class WindowsRecord(unittest.TestCase):
    def test_sfc_details_extracts_the_sr_lines_like_findstr(self):
        with tempfile.TemporaryDirectory() as t:
            log = os.path.join(t, "CBS.log")
            with open(log, "w", encoding="utf-8") as f:
                f.write("Info CBS other line\nInfo CSI 1 [SR] Verifying 100 components\nInfo CSI 2 [SR] Verify complete\nInfo CBS end\n")
            opened = []
            with mock.patch.object(tr, "CBS_LOG", log):
                r = tr.open_windows_record("sfc", opener=opened.append)
            self.assertTrue(r["ok"])
            self.assertEqual(r["lines"], 2)
            self.assertEqual(opened, [r["path"]])
            with open(r["path"], encoding="utf-8-sig") as f:
                body = f.read()
            self.assertIn("Verify complete", body)
            self.assertNotIn("other line", body)

    def test_sfc_details_explains_missing_or_locked_log(self):
        with mock.patch.object(tr, "CBS_LOG", os.path.join(tempfile.gettempdir(), "nope", "CBS.log")):
            self.assertIn("not found", tr.sfc_details()["error"])
        with mock.patch("builtins.open", side_effect=PermissionError()), mock.patch("os.path.getsize", return_value=10):
            self.assertIn("Administrator", tr.sfc_details()["error"])

    def test_dism_opens_the_log_folder_and_trim_opens_optimize_drives(self):
        with tempfile.TemporaryDirectory() as t:
            log = os.path.join(t, "dism.log")
            open(log, "w").close()
            with mock.patch.object(tr, "DISM_LOG", log), mock.patch.object(tr.subprocess, "Popen") as pop:
                self.assertTrue(tr.open_windows_record("dism")["ok"])
                self.assertEqual(pop.call_args[0][0], ["explorer.exe", f"/select,{log}"])
        with mock.patch.object(tr.subprocess, "Popen") as pop:
            self.assertTrue(tr.open_windows_record("trim")["ok"])
            self.assertTrue(pop.call_args[0][0][0].lower().endswith("dfrgui.exe"))
        self.assertFalse(tr.open_windows_record("bogus")["ok"])


class CoreWiring(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.core = core_service.Core(emit=lambda e, d: self.events.append((e, d)))

    def test_a_finished_run_writes_a_report_and_report_opens_only_that_file(self):
        res = dict(RES, logs=["[SUCCESS] done"])
        with mock.patch.object(core_logic, "is_admin", return_value=True), mock.patch.object(core_logic, "run_repair", return_value=res):
            self.assertTrue(self.core.maint_tool("sfc")["ok"])
            for _ in range(200):
                if any(e == "tool_result" for e, _ in self.events):
                    break
                import time
                time.sleep(0.02)
        result = next(d for e, d in self.events if e == "tool_result")
        self.assertNotIn("sr_lines", result)                                   # big, stays out of the page
        self.assertTrue(tr.is_report_path(result["report"]))
        self.assertEqual(self.core.config["maint_tool_last"]["sfc"]["report"], result["report"])
        with mock.patch("os.startfile") as start:
            self.assertTrue(self.core.maint_tool_open("sfc", "report")["ok"])
            start.assert_called_once_with(result["report"])
        self.core.config["maint_tool_last"]["sfc"]["report"] = r"C:\Windows\win.ini"         # a tampered config never opens other files
        with mock.patch("os.startfile") as start:
            self.assertFalse(self.core.maint_tool_open("sfc", "report")["ok"])
            start.assert_not_called()
        self.assertFalse(self.core.maint_tool_open("notatool", "report")["ok"])
        self.assertFalse(self.core.maint_tool_open("sfc", "elsewhere")["ok"])

    def test_sfc_run_attaches_its_own_cbs_lines_and_trim_asks_for_progress(self):
        calls = []

        def fake_run(args, timeout, on_progress=None):
            calls.append(args)
            return 0, "Windows Resource Protection did not find any integrity violations.", False
        sr = {"verify_complete": True, "repair_complete": False, "cannot_repair": 0, "repairing": 0, "lines": 1, "sr_text": ["[SR] Verify complete"]}
        with mock.patch.object(core_logic, "is_admin", return_value=True), mock.patch.object(core_logic, "run_tool", side_effect=fake_run), \
                mock.patch.object(core_logic, "cbs_evidence_since", return_value=sr), mock.patch.object(core_logic, "_cbs_size", return_value=0):
            r = core_logic.run_repair("sfc")
            core_logic.run_repair("trim")
        self.assertEqual(r["sr_lines"], ["[SR] Verify complete"])
        self.assertEqual(calls[-1], ["defrag", "/C", "/O", "/U"])
        self.assertEqual(core_logic._pct_in("Retrim:  45% complete."), 45.0)


if __name__ == "__main__":
    unittest.main()
