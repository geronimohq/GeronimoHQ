"""Temp cleaner and crash-dump cleaner: what they must never delete (fake folders only; TEMP, SystemRoot and LOCALAPPDATA are redirected)."""
import os
import sys
import tempfile
import time
import unittest
from unittest import mock

import _test_isolation  # noqa: F401  (temp config; must come first)
import core_logic


def touch(path, age_seconds=0, data=b"x"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data)
    t = time.time() - age_seconds
    os.utime(path, (t, t))


class TempCleaner(unittest.TestCase):
    def test_own_unpacked_folder_other_mei_folders_and_recent_files_survive(self):
        with tempfile.TemporaryDirectory() as root:
            tmp = os.path.join(root, "Temp")
            winroot = os.path.join(root, "Windows")
            os.makedirs(os.path.join(winroot, "Temp"))
            two_days = 2 * 24 * 3600
            touch(os.path.join(tmp, "old_junk.tmp"), two_days)
            touch(os.path.join(tmp, "sub", "old_junk2.log"), two_days)
            touch(os.path.join(tmp, "recent.tmp"), 60)                                   # an installer writing right now
            touch(os.path.join(tmp, "_MEI12345", "web", "index.html"), two_days)          # another one-file app (or the elevated copy)
            own = os.path.join(tmp, "unpacked_by_pyinstaller")                            # this app's own folder, whatever it is called
            touch(os.path.join(own, "app.png"), two_days)
            touch(os.path.join(winroot, "Temp", "win_old.tmp"), two_days)
            with mock.patch.dict(os.environ, {"TEMP": tmp, "SystemRoot": winroot}), mock.patch.object(sys, "_MEIPASS", own, create=True):
                deleted, _freed, _logs = core_logic.clean_windows_temp_files()
            self.assertFalse(os.path.exists(os.path.join(tmp, "old_junk.tmp")))
            self.assertFalse(os.path.exists(os.path.join(tmp, "sub", "old_junk2.log")))
            self.assertFalse(os.path.exists(os.path.join(winroot, "Temp", "win_old.tmp")))
            self.assertEqual(deleted, 3)
            self.assertTrue(os.path.exists(os.path.join(tmp, "recent.tmp")))
            self.assertTrue(os.path.exists(os.path.join(tmp, "_MEI12345", "web", "index.html")))
            self.assertTrue(os.path.exists(os.path.join(own, "app.png")))


class DumpCleaner(unittest.TestCase):
    def test_console_log_and_other_logs_are_never_deleted(self):
        with tempfile.TemporaryDirectory() as root:
            cs2 = os.path.join(root, "Counter-Strike Global Offensive")
            csgo = os.path.join(cs2, "game", "csgo")
            touch(os.path.join(csgo, "console.log"))                                      # read by the Log Analyzer and the Discord detection
            touch(os.path.join(csgo, "other_tool.log"))
            touch(os.path.join(csgo, "crash_1.txt"))
            touch(os.path.join(csgo, "crash.dmp"))
            touch(os.path.join(cs2, "game", "bin", "win64", "cs2.dmp"))
            touch(os.path.join(cs2, "game", "bin", "win64", "cs2.exe"))
            touch(os.path.join(csgo, "dumps", "old.dmp"))
            touch(os.path.join(csgo, "dumps", "old.log"))
            with mock.patch.dict(os.environ, {"LOCALAPPDATA": os.path.join(root, "Local")}):
                deleted, _freed, _logs = core_logic.clean_cs2_temp_dumps(cs2)
            self.assertTrue(os.path.exists(os.path.join(csgo, "console.log")))
            self.assertTrue(os.path.exists(os.path.join(csgo, "other_tool.log")))
            self.assertTrue(os.path.exists(os.path.join(cs2, "game", "bin", "win64", "cs2.exe")))
            for gone in (("game", "csgo", "crash_1.txt"), ("game", "csgo", "crash.dmp"), ("game", "bin", "win64", "cs2.dmp"),
                         ("game", "csgo", "dumps", "old.dmp"), ("game", "csgo", "dumps", "old.log")):
                self.assertFalse(os.path.exists(os.path.join(cs2, *gone)), gone)
            self.assertEqual(deleted, 5)


if __name__ == "__main__":
    unittest.main()
