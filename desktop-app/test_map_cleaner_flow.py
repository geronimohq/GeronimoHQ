"""Map Cleaner: scan never trips on asset packs, scans are not blocked by other jobs, and Delete re-checks protection right before deleting."""
import os
import re
import tempfile
import threading
import time
import unittest
from unittest import mock

import _test_isolation  # noqa: F401  (temp config; must come first)
import core_service
import custom_map_cleaner


def wait_for(events, name, timeout=10):
    end = time.time() + timeout
    while time.time() < end:
        for e, d in list(events):
            if e == name:
                return d
        time.sleep(0.02)
    raise AssertionError(f"no '{name}' event")


class ScanScope(unittest.TestCase):
    def test_asset_pack_first_does_not_break_the_scan(self):
        real_exists = os.path.exists
        with tempfile.TemporaryDirectory() as steam:
            ws = os.path.join(steam, "steamapps", "workshop", "content", "730")
            asset = os.path.join(ws, "3793587501")                                    # a known server asset pack: sorts first
            maps = os.path.join(ws, "9999999")
            for folder, body in ((asset, b"a" * 5000), (maps, b"m" * 5000)):
                os.makedirs(folder)
                open(os.path.join(folder, os.path.basename(folder) + ".vpk"), "wb").write(body)
            open(os.path.join(maps, "publish_data.txt"), "w").write('"publish_data"\n{\n\t"title"\t\t"ze_test_map"\n}\n')
            import steam_paths
            with mock.patch.object(steam_paths, "steam_libraries", return_value=[steam]):        # only the fake Steam folder; never this PC's libraries
                items = custom_map_cleaner.scan_custom_maps(steam, None, set(), False)
        by = {str(i["id"]): i for i in items}
        self.assertIn("3793587501", by)
        self.assertIn("9999999", by)
        self.assertTrue(by["3793587501"]["is_server_asset"])
        self.assertFalse(by["9999999"]["is_officially_subscribed"])                   # not inherited from the asset pack scanned before it


class ScanAndDeleteFlow(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.core = core_service.Core(emit=lambda e, d: self.events.append((e, d)))

    def test_scan_is_not_refused_while_another_job_runs_and_latest_request_wins(self):
        self.core._busy = "sfc"                                                       # a long SFC run holds the single job slot
        seen = []

        def fake_scan(steam, cs2, comms, recent):
            seen.append((set(comms), recent))
            time.sleep(0.15)
            return []
        with mock.patch.object(custom_map_cleaner, "scan_custom_maps", side_effect=fake_scan):
            self.assertTrue(self.core.maps_scan(["gfl"], True)["ok"])
            self.assertTrue(self.core.maps_scan(["gfl", "rss"], False)["ok"])          # arrives mid-scan
            self.assertTrue(self.core.maps_scan(["possession"], True)["ok"])           # arrives mid-scan, replaces the one before
            wait_for(self.events, "job")
            time.sleep(0.5)
        self.assertEqual(seen[0], ({"gfl"}, True))
        self.assertEqual(seen[-1], ({"possession"}, True))                            # the newest choices were the last scan
        self.assertLessEqual(len(seen), 2)                                            # the middle request was skipped

    def test_delete_rescans_with_current_protection_and_skips_what_is_now_protected(self):
        fresh = [{"id": 1, "is_protected": False, "is_server_asset": False, "path": "x1", "size_bytes": 10},
                 {"id": 2, "is_protected": True, "is_server_asset": False, "path": "x2", "size_bytes": 10},     # GFL map, protected right now
                 {"id": 3, "is_protected": False, "is_server_asset": True, "path": "x3", "size_bytes": 10}]     # asset pack
        self.core._maps = {"1": {}, "2": {}, "3": {}}                                  # what the last scan listed
        deleted = []

        def fake_delete(items):
            deleted.extend(str(m["id"]) for m in items)
            return len(items), 10 * len(items), []
        with mock.patch.object(custom_map_cleaner, "scan_custom_maps", return_value=fresh) as scan, \
                mock.patch.object(custom_map_cleaner, "delete_custom_maps", side_effect=fake_delete):
            r = self.core.maps_delete(["1", "2", "3", "4"], ["gfl", "rss"], True)       # the page's old rows said 2 and 3 were deletable
            self.assertTrue(r["ok"])
            done = wait_for(self.events, "maps_deleted")
        self.assertEqual(deleted, ["1"])
        self.assertEqual(done["skipped"], 2)                                           # 2 and 3; id 4 was never listed so it never got this far
        self.assertEqual(scan.call_args[0][2], {"gfl", "rss"})                        # the choices from the page, not stale ones
        self.assertTrue(scan.call_args[0][3])


if __name__ == "__main__":
    unittest.main()
