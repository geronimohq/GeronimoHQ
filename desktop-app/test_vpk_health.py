"""Workshop VPK health check and repair, tested on synthetic workshop folders (never the real library)."""
import os
import struct
import tempfile
import time
import unittest
from unittest import mock

import _test_isolation  # noqa: F401  (temp config; must come first)
import core_logic


def build_tree(files, arch):
    """VPK2 directory tree for files = [(name, length)] stored one after the other in archive `arch`."""
    out = b"vpk\x00" + b"maps\x00"
    off = 0
    for name, ln in files:
        out += name.encode() + b"\x00" + struct.pack("<IHHIIH", 0, 0, arch, off, ln, 0xFFFF)
        off += ln
    return out + b"\x00\x00\x00"


def write_single(path, payload=b"x" * 5000, truncate_to=None):
    tree = build_tree([("a", len(payload))], 0x7FFF)
    head = struct.pack("<IIIIIII", 0x55AA1234, 2, len(tree), len(payload), 0, 0, 0)
    data = head + tree + payload
    with open(path, "wb") as fh:
        fh.write(data if truncate_to is None else data[:truncate_to])


def write_multi(folder, wid, chunk_len=4000, make_chunk=True, short=False):
    tree = build_tree([("a", chunk_len)], 0)
    head = struct.pack("<IIIIIII", 0x55AA1234, 2, len(tree), 0, 0, 0, 0)
    with open(os.path.join(folder, f"{wid}_dir.vpk"), "wb") as fh:
        fh.write(head + tree)
    if make_chunk:
        with open(os.path.join(folder, f"{wid}_000.vpk"), "wb") as fh:
            fh.write(b"y" * (chunk_len // 2 if short else chunk_len))


class VpkHealth(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = self.tmp.name
        self.ws = os.path.join(root, "steamapps", "workshop", "content", "730")
        exe_dir = os.path.join(root, "steamapps", "common", "Counter-Strike Global Offensive", "game", "bin", "win64")
        os.makedirs(self.ws)
        os.makedirs(exe_dir)
        self.exe = os.path.join(exe_dir, "cs2.exe")
        open(self.exe, "wb").write(b"MZ")

    def tearDown(self):
        self.tmp.cleanup()

    def item(self, wid):
        p = os.path.join(self.ws, str(wid))
        os.makedirs(p, exist_ok=True)
        return p

    def scan(self):
        res = core_logic.scan_workshop_vpk_addons(None, self.exe)
        return {a["workshop_id"]: a for a in res["addons"]}, res

    def test_every_kind_of_damage_is_found_and_healthy_packs_pass(self):
        write_single(os.path.join(self.item(1001), "1001.vpk"))                                   # healthy single file
        write_multi(self.item(1002), 1002)                                                        # healthy index + archive part
        write_single(os.path.join(self.item(2001), "2001.vpk"), truncate_to=3000)                 # download stopped half way
        write_multi(self.item(2002), 2002, make_chunk=False)                                      # archive part missing
        write_multi(self.item(2003), 2003, short=True)                                            # archive part cut short
        open(os.path.join(self.item(2004), "2004.vpk"), "wb").write(b"\x00" * 200)                # wrong signature
        open(os.path.join(self.item(2005), "2005.vpk"), "wb").write(b"abc")                       # empty / truncated
        write_single(os.path.join(self.item(2006), "2006.vpk"))
        open(os.path.join(self.ws, "2006", "leftover.tmp"), "wb").write(b"1")                     # temp file from a stuck download
        self.item(2007)                                                                           # folder with nothing in it
        by, res = self.scan()
        for ok_id in ("1001", "1002"):
            self.assertEqual(by[ok_id]["status"], "Healthy", ok_id)
        for bad_id in ("2001", "2002", "2003", "2004", "2005", "2006", "2007"):
            self.assertNotEqual(by[bad_id]["status"], "Healthy", bad_id)
            self.assertTrue(by[bad_id]["detail"], bad_id)
        self.assertEqual(res["healthy_count"], 2)
        self.assertEqual(res["corrupted_count"], 7)
        self.assertIn("cut off", by["2001"]["detail"])
        self.assertIn("missing archive part", by["2002"]["detail"])
        self.assertIn("shorter", by["2003"]["detail"])

    def test_one_unreadable_folder_does_not_hide_the_rest(self):
        write_single(os.path.join(self.item(3001), "3001.vpk"))
        write_single(os.path.join(self.item(3002), "3002.vpk"))
        real = core_logic.os.walk
        calls = {"n": 0}

        def flaky(path, *a, **k):
            calls["n"] += 1
            if calls["n"] == 1:
                raise OSError("boom")
            return real(path, *a, **k)
        with mock.patch.object(core_logic.os, "walk", side_effect=flaky):
            by, res = self.scan()
        self.assertEqual(len(by), 1)                     # the other pack is still reported
        self.assertEqual(res["scan_errors"], 1)
        self.assertIn("skipped", res["message"])

    def test_repair_removes_only_old_damaged_workshop_folders(self):
        write_single(os.path.join(self.item(4001), "4001.vpk"))                                   # healthy: must stay
        write_single(os.path.join(self.item(4002), "4002.vpk"), truncate_to=3000)                 # damaged and old: removed
        write_single(os.path.join(self.item(4003), "4003.vpk"), truncate_to=3000)                 # damaged but just changed: kept
        old = time.time() - 7200
        for root, _, files in os.walk(os.path.join(self.ws, "4002")):
            for f in files:
                os.utime(os.path.join(root, f), (old, old))
        by, _ = self.scan()
        res = core_logic.repair_corrupted_workshop_addons([a for a in by.values() if a["status"] != "Healthy"])
        self.assertEqual(res["repaired"], 1)
        self.assertEqual(res["skipped"], 1)
        self.assertTrue(os.path.isdir(os.path.join(self.ws, "4001")))
        self.assertFalse(os.path.isdir(os.path.join(self.ws, "4002")))
        self.assertTrue(os.path.isdir(os.path.join(self.ws, "4003")))

    def test_repair_refuses_anything_that_is_not_a_workshop_item_folder(self):
        outside = os.path.join(self.tmp.name, "my730stuff")
        os.makedirs(outside)
        open(os.path.join(outside, "keep.txt"), "w").write("x")
        items = [{"status": "Corrupted", "path": outside, "workshop_id": "x", "mtime": 0},
                 {"status": "Corrupted", "path": self.ws, "workshop_id": "730", "mtime": 0}]        # the 730 folder itself
        res = core_logic.repair_corrupted_workshop_addons(items)
        self.assertEqual(res["repaired"], 0)
        self.assertTrue(os.path.exists(os.path.join(outside, "keep.txt")))
        self.assertTrue(os.path.isdir(self.ws))


if __name__ == "__main__":
    unittest.main()
