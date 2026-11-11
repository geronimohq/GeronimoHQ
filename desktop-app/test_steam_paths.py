"""Steam, library and CS2 discovery on layouts that differ from the developer's PC (synthetic folders only)."""
import os
import tempfile
import unittest
from unittest import mock

import _test_isolation  # noqa: F401  (temp config; must come first)
import core_logic
import core_service
import steam_paths


def make_cs2(lib, folder="Counter-Strike Global Offensive", manifest=True):
    exe = os.path.join(lib, "steamapps", "common", folder, "game", "bin", "win64", "cs2.exe")
    os.makedirs(os.path.dirname(exe))
    open(exe, "wb").write(b"MZ")
    os.makedirs(os.path.join(lib, "steamapps", "common", folder, "game", "csgo", "cfg"))
    if manifest:
        with open(os.path.join(lib, "steamapps", "appmanifest_730.acf"), "w", encoding="utf-8") as fh:
            fh.write('"AppState"\n{\n\t"appid"\t\t"730"\n\t"installdir"\t\t"%s"\n}\n' % folder)
    return exe


class Discovery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.steam = os.path.join(self.root, "My Games", "Steam ünï")                         # spaces and non-ASCII
        os.makedirs(os.path.join(self.steam, "steamapps"))
        self.lib2 = os.path.join(self.root, "Spiele", "Bibliothek")
        os.makedirs(os.path.join(self.lib2, "steamapps"))

    def tearDown(self):
        self.tmp.cleanup()

    def write_vdf(self, body):
        with open(os.path.join(self.steam, "steamapps", "libraryfolders.vdf"), "w", encoding="utf-8") as fh:
            fh.write(body)

    def test_new_format_libraries_with_escaped_backslashes(self):
        esc = self.lib2.replace("\\", "\\\\")
        self.write_vdf('"libraryfolders"\n{\n\t"0"\n\t{\n\t\t"path"\t\t"%s"\n\t}\n\t"1"\n\t{\n\t\t"path"\t\t"%s"\n\t\t"apps"\n\t\t{\n\t\t\t"730"\t\t"1"\n\t\t}\n\t}\n}\n' % (self.steam.replace("\\", "\\\\"), esc))
        libs = steam_paths.read_library_folders(self.steam)
        self.assertIn(self.lib2, libs)
        self.assertEqual(sum(1 for p in libs if os.path.normcase(p) == os.path.normcase(self.lib2)), 1)

    def test_old_format_libraries(self):
        self.write_vdf('"LibraryFolders"\n{\n\t"TimeNextStatsReport"\t\t"1234"\n\t"1"\t\t"%s"\n}\n' % self.lib2.replace("\\", "\\\\"))
        self.assertIn(self.lib2, steam_paths.read_library_folders(self.steam))

    def test_cs2_in_a_second_library_with_a_custom_folder_name(self):
        exe = make_cs2(self.lib2, folder="CS2 mine")
        self.write_vdf('"libraryfolders"\n{\n\t"1"\n\t{\n\t\t"path"\t\t"%s"\n\t}\n}\n' % self.lib2.replace("\\", "\\\\"))
        with mock.patch.object(steam_paths, "fixed_drives", return_value=[]):
            libs = steam_paths.steam_libraries(self.steam)
        found = steam_paths.find_cs2(libs)
        self.assertEqual(os.path.normcase(found["cs2_exe"]), os.path.normcase(exe))
        self.assertTrue(found["cfg_dir"])

    def test_the_library_steam_says_cs2_lives_in_beats_a_leftover_copy(self):
        make_cs2(self.steam, manifest=False)                                                   # leftover folder, no manifest
        exe2 = make_cs2(self.lib2)                                                             # real install (has appmanifest_730.acf)
        found = steam_paths.find_cs2([self.steam, self.lib2])
        self.assertEqual(os.path.normcase(found["cs2_exe"]), os.path.normcase(exe2))

    def test_only_cs2s_own_library_decides_whether_a_map_is_installed(self):
        make_cs2(self.lib2)
        core = core_service.Core()
        core.paths = {"steam_path": self.steam, "cs2_dir": os.path.join(self.lib2, "steamapps", "common", "Counter-Strike Global Offensive")}
        self.assertEqual([os.path.normcase(p) for p in core._steam_libraries()], [os.path.normcase(self.lib2)])

    def test_override_for_an_elevated_copy_and_steam_folder_shapes(self):
        with mock.patch.dict(os.environ, {"CS2CC_STEAM_PATH": self.steam}), mock.patch.object(steam_paths, "_reg_values", return_value=[]):
            self.assertEqual(os.path.normcase(steam_paths.find_steam_path()), os.path.normcase(self.steam))
        bare = os.path.join(self.root, "Bare")
        os.makedirs(bare)
        self.assertFalse(steam_paths._looks_like_steam(bare))
        open(os.path.join(bare, "steam.exe"), "wb").write(b"MZ")
        self.assertTrue(steam_paths._looks_like_steam(bare))

    def test_registry_value_names_differ_between_machines(self):
        with mock.patch.object(steam_paths, "_reg_values", return_value=[r"Z:\does\not\exist", self.steam]), mock.patch.object(steam_paths, "fixed_drives", return_value=[]), \
                mock.patch.dict(os.environ, {"CS2CC_STEAM_PATH": ""}):
            self.assertEqual(os.path.normcase(core_logic.find_steam_path()), os.path.normcase(self.steam))

    def test_only_fixed_drives_are_probed(self):
        real = steam_paths.fixed_drives()
        self.assertTrue(all(len(d) == 3 and d[1:] == ":\\" for d in real))
        with mock.patch.object(steam_paths.ctypes.windll.kernel32, "GetDriveTypeW", return_value=4):     # every drive looks like a network share
            self.assertEqual(steam_paths.fixed_drives(), [])


if __name__ == "__main__":
    unittest.main()
