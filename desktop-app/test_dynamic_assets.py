"""Dynamic server-asset detection: a workshop item whose VPK has content but no top-level maps/ folder is an asset pack, even when no list,
title or id names it (for example the packs a player picked up by joining a Chinese server). Fake VPK files only; the real config is untouched."""
import os
import struct
import tempfile
import unittest
from unittest import mock

import _test_isolation  # noqa: F401  (temp config; must come first)
import custom_map_cleaner as c
import steam_paths
import workshop_collections as wc


def make_vpk(path, files, version=2):
    """Writes a VPK whose directory tree lists `files` ({"models/a.vmdl_c": 10, ...}); data chunks are not needed for the tree."""
    tree = b""
    by_ext = {}
    for full in files:
        folder, _, name = full.rpartition("/")
        stem, _, ext = name.rpartition(".")
        by_ext.setdefault(ext, {}).setdefault(folder or " ", []).append(stem)
    for ext, folders in by_ext.items():
        tree += ext.encode() + b"\0"
        for folder, stems in folders.items():
            tree += folder.encode() + b"\0"
            for stem in stems:
                tree += stem.encode() + b"\0" + struct.pack("<IHHIIH", 0, 0, 0x7FFF, 0, 10, 0xFFFF)
            tree += b"\0"
        tree += b"\0"
    tree += b"\0"
    header = struct.pack("<II", 0x55AA1234, version) + struct.pack("<I", len(tree)) + (struct.pack("<IIII", 0, 0, 0, 0) if version == 2 else b"")
    with open(path, "wb") as f:
        f.write(header + tree)


def item(root, wid, title, files, name=None):
    folder = os.path.join(root, "steamapps", "workshop", "content", "730", wid)
    os.makedirs(folder)
    make_vpk(os.path.join(folder, name or f"{wid}_dir.vpk"), files)
    with open(os.path.join(folder, "publish_data.txt"), "w", encoding="utf-8") as f:
        f.write('"publish_data"\n{\n\t"title"\t\t"%s"\n}\n' % title)
    return folder


ASSETS = {"models/player/a.vmdl_c": 1, "materials/skin/b.vmat_c": 1, "sounds/c.vsnd_c": 1}


class Tree(unittest.TestCase):
    def test_top_dirs_of_a_map_and_of_an_asset_pack(self):
        with tempfile.TemporaryDirectory() as t:
            make_vpk(os.path.join(t, "m.vpk"), {"maps/ze_x.vpk": 1, "materials/maps/n.vtex_c": 1, "models/a.vmdl_c": 1}, version=2)
            make_vpk(os.path.join(t, "a.vpk"), ASSETS, version=1)
            self.assertEqual(c.vpk_top_dirs(os.path.join(t, "m.vpk")), {"maps", "materials", "models"})
            self.assertEqual(c.vpk_top_dirs(os.path.join(t, "a.vpk")), {"models", "materials", "sounds"})

    def test_garbage_and_truncated_files_are_unknown_not_a_crash(self):
        with tempfile.TemporaryDirectory() as t:
            open(os.path.join(t, "g.vpk"), "wb").write(b"not a vpk at all" * 10)
            make_vpk(os.path.join(t, "a.vpk"), ASSETS)
            data = open(os.path.join(t, "a.vpk"), "rb").read()
            open(os.path.join(t, "cut.vpk"), "wb").write(data[: len(data) // 2])
            open(os.path.join(t, "empty.vpk"), "wb").close()
            for n in ("g.vpk", "cut.vpk", "empty.vpk", "missing.vpk"):
                self.assertIsNone(c.vpk_top_dirs(os.path.join(t, n)))


class Classification(unittest.TestCase):
    def test_unlisted_pack_with_any_title_is_an_asset_pack(self):
        with tempfile.TemporaryDirectory() as t:
            f1 = item(t, "9000001", "僵尸逃跑服务器素材", ASSETS)                      # Chinese title, id and name in no list
            f2 = item(t, "9000002", "", ASSETS, name="9000002.vpk")                    # no title at all, single-file VPK
            for f, wid, title in ((f1, "9000001", "僵尸逃跑服务器素材"), (f2, "9000002", "")):
                ok, name, _ = c.is_asset_pack_or_custom(f, wid, title)
                self.assertTrue(ok, wid)
                self.assertIn("Server Asset Pack", name)

    def test_asset_pack_that_has_maps_in_a_texture_path_is_still_an_asset_pack(self):
        with tempfile.TemporaryDirectory() as t:
            f = item(t, "9000003", "Some Content", {**ASSETS, "materials/maps/normal_map.vtex_c": 1})   # the old byte scan saw "maps/" and said: a map
            self.assertTrue(c.is_asset_pack_or_custom(f, "9000003", "Some Content")[0])

    def test_maps_are_never_locked(self):
        with tempfile.TemporaryDirectory() as t:
            f1 = item(t, "9000004", "Backrooms Insomnia", {**ASSETS, "maps/backrooms.vpk": 1})          # no ze_ prefix, but it has maps/
            f2 = item(t, "9000005", "ze_looks_like_assets", ASSETS)                                      # map prefix wins, as before
            self.assertFalse(c.is_asset_pack_or_custom(f1, "9000004", "Backrooms Insomnia")[0])
            self.assertFalse(c.is_asset_pack_or_custom(f2, "9000005", "ze_looks_like_assets")[0])

    def test_unreadable_item_is_not_called_an_asset(self):
        with tempfile.TemporaryDirectory() as t:
            f = os.path.join(t, "steamapps", "workshop", "content", "730", "9000006")
            os.makedirs(f)
            open(os.path.join(f, "9000006_dir.vpk"), "wb").write(b"\0" * 5000)
            self.assertFalse(c.is_asset_pack_or_custom(f, "9000006", "Whatever")[0])


class ScanProtectsThem(unittest.TestCase):
    def test_scan_marks_an_unlisted_pack_as_protected_server_asset(self):
        with tempfile.TemporaryDirectory() as steam:
            item(steam, "9000007", "上海ZE资源包", ASSETS)
            item(steam, "9000008", "ze_a_map", {"maps/ze_a_map.vpk": 1, "models/a.vmdl_c": 1})
            with mock.patch.object(steam_paths, "steam_libraries", return_value=[steam]), \
                    mock.patch.object(wc, "communities_of", return_value=[]), mock.patch.object(wc, "asset_ids", return_value=set()):
                rows = {r["id"]: r for r in c.scan_custom_maps(steam, None, {"gfl"}, False)}
        self.assertTrue(rows["9000007"]["is_server_asset"] and rows["9000007"]["is_protected"])
        self.assertFalse(rows["9000008"]["is_server_asset"])
        self.assertFalse(rows["9000008"]["is_protected"])
        self.assertEqual(rows["9000008"]["status_label"], "📁 Not protected")


class Labels(unittest.TestCase):
    def test_unprotected_maps_say_not_played_in_30_days_and_non_gfl_subscribed_says_only_subscribed(self):
        with tempfile.TemporaryDirectory() as steam:
            for wid, title in (("9100001", "ze_old_one"), ("9100002", "ze_cola_sub")):
                item(steam, wid, title, {"maps/%s.vpk" % title: 1})
            import time
            old = time.time() - 90 * 86400
            for wid in ("9100001", "9100002"):
                d = os.path.join(steam, "steamapps", "workshop", "content", "730", wid)
                for fn in os.listdir(d):
                    os.utime(os.path.join(d, fn), (old, old))
                os.utime(d, (old, old))
            member = {"9100002": ["mapeadores_cola"]}
            with mock.patch.object(steam_paths, "steam_libraries", return_value=[steam]), \
                    mock.patch.object(wc, "communities_of", side_effect=lambda w: member.get(w, [])), mock.patch.object(wc, "asset_ids", return_value=set()), \
                    mock.patch.object(c, "get_subscribed_workshop_ids", return_value={"9100002"}):
                rows = {r["id"]: r for r in c.scan_custom_maps(steam, None, {"gfl"}, True)}
        self.assertEqual(rows["9100001"]["status_label"], "📁 Not played in 30+ days")
        self.assertEqual(rows["9100002"]["status_label"], "📁 Subscribed")                # no server name, not protected
        self.assertFalse(rows["9100002"]["is_protected"])


if __name__ == "__main__":
    unittest.main()
