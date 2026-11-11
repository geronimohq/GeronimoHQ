"""Steam launch options: read and write only CS2's own entry, in the account that logged in last (synthetic Steam folders only)."""
import os
import tempfile
import unittest
from unittest import mock

import _test_isolation  # noqa: F401  (temp config; must come first)
import core_logic
import core_service
import hardware_info
import steam_vdf


def localconfig(opts730=None, other="-windowed -novid", eol="\n", with_730=True):
    lines = ['"UserLocalConfigStore"', "{", '\t"Software"', "\t{", '\t\t"Valve"', "\t\t{", '\t\t\t"Steam"', "\t\t\t{", '\t\t\t\t"apps"', "\t\t\t\t{",
             '\t\t\t\t\t"570"', "\t\t\t\t\t{", f'\t\t\t\t\t\t"LaunchOptions"\t\t"{other}"', '\t\t\t\t\t\t"Playtime"\t\t"42"', "\t\t\t\t\t}"]
    if with_730:
        lines += ['\t\t\t\t\t"730"', "\t\t\t\t\t{", '\t\t\t\t\t\t"cloud"', "\t\t\t\t\t\t{", '\t\t\t\t\t\t\t"last_sync_state"\t\t"synchronized"', "\t\t\t\t\t\t}"]
        if opts730 is not None:
            lines.append(f'\t\t\t\t\t\t"LaunchOptions"\t\t"{opts730}"')
        lines.append("\t\t\t\t\t}")
    lines += ['\t\t\t\t\t"440"', "\t\t\t\t\t{", '\t\t\t\t\t\t"LaunchOptions"\t\t"-console"', "\t\t\t\t\t}", "\t\t\t\t}", "\t\t\t}", "\t\t}", "\t}", "}"]
    return eol.join(lines) + eol


class LaunchOptionsVdf(unittest.TestCase):
    def test_only_cs2_is_changed_and_everything_else_is_byte_identical(self):
        src = localconfig("-novid")
        out = steam_vdf.set_launch_options(src, "-novid -nojoy +fps_max 0")
        self.assertEqual(steam_vdf.get_launch_options(out, "730"), "-novid -nojoy +fps_max 0")
        self.assertEqual(steam_vdf.get_launch_options(out, "570"), "-windowed -novid")          # other games untouched
        self.assertEqual(steam_vdf.get_launch_options(out, "440"), "-console")
        self.assertEqual(out.replace("-novid -nojoy +fps_max 0", "-novid"), src)                 # nothing else moved

    def test_reading_never_returns_another_games_options(self):
        src = localconfig(opts730=None)                                                          # CS2 has no options; Dota and TF2 do
        self.assertIsNone(steam_vdf.get_launch_options(src, "730"))
        out = steam_vdf.set_launch_options(src, "-novid")                                         # inserted into CS2's block only
        self.assertEqual(steam_vdf.get_launch_options(out, "730"), "-novid")
        self.assertEqual(steam_vdf.get_launch_options(out, "570"), "-windowed -novid")
        self.assertEqual(steam_vdf.get_launch_options(out, "440"), "-console")

    def test_missing_cs2_block_is_created_inside_apps(self):
        out = steam_vdf.set_launch_options(localconfig(with_730=False), "-novid")
        self.assertEqual(steam_vdf.get_launch_options(out, "730"), "-novid")
        self.assertEqual(steam_vdf.get_launch_options(out, "570"), "-windowed -novid")

    def test_quotes_and_backslashes_are_escaped_and_read_back(self):
        nasty = r'+exec "my cfg" -path C:\games\cs2'
        out = steam_vdf.set_launch_options(localconfig("-novid"), nasty)
        self.assertEqual(steam_vdf.get_launch_options(out, "730"), nasty)
        steam_vdf.parse(out)                                                                     # the file is still well formed

    def test_windows_line_endings_are_preserved(self):
        src = localconfig("-novid", eol="\r\n")
        out = steam_vdf.set_launch_options(src, "-novid -nojoy")
        self.assertNotIn("\n", out.replace("\r\n", ""))                                          # still CRLF everywhere
        self.assertEqual(steam_vdf.get_launch_options(out, "730"), "-novid -nojoy")

    def test_unreadable_file_is_refused(self):
        for bad in ('"UserLocalConfigStore" { "Software" { ', "not vdf at all", '"a" "b" }'):
            with self.assertRaises(steam_vdf.VdfError):
                steam_vdf.set_launch_options(bad, "-novid")
        with self.assertRaises(steam_vdf.VdfError):
            steam_vdf.set_launch_options('"UserLocalConfigStore"\n{\n}\n', "-novid")           # no apps block at all


class SteamAccounts(unittest.TestCase):
    def make_steam(self, tmp, recent_id):
        users = {76561198000000001: "0", 76561198000000002: "0"}
        users[recent_id] = "1"
        body = "\n".join(f'\t"{sid}"\n\t{{\n\t\t"AccountName"\t\t"u{sid}"\n\t\t"MostRecent"\t\t"{flag}"\n\t}}' for sid, flag in users.items())
        os.makedirs(os.path.join(tmp, "config"))
        open(os.path.join(tmp, "config", "loginusers.vdf"), "w", encoding="utf-8").write('"users"\n{\n' + body + "\n}\n")
        for sid, label in ((76561198000000001, "-first"), (76561198000000002, "-second")):
            d = os.path.join(tmp, "userdata", str(sid - steam_vdf.STEAMID64_BASE), "config")
            os.makedirs(d)
            open(os.path.join(d, "localconfig.vdf"), "w", encoding="utf-8").write(localconfig(label))

    def test_the_account_that_logged_in_last_is_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.make_steam(tmp, 76561198000000002)
            opts, vdf = hardware_info.get_current_launch_options(tmp)
            self.assertEqual(opts, "-second")
            self.assertIn(str(76561198000000002 - steam_vdf.STEAMID64_BASE), vdf)

    def test_save_writes_only_that_account_and_keeps_a_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.make_steam(tmp, 76561198000000001)
            _opts, vdf = hardware_info.get_current_launch_options(tmp)
            ok, _logs = core_logic.save_launch_options(vdf, "-novid -nojoy")
            self.assertTrue(ok)
            self.assertTrue(os.path.exists(vdf + ".backup"))
            self.assertEqual(hardware_info.get_current_launch_options(tmp)[0], "-novid -nojoy")
            other = os.path.join(tmp, "userdata", str(76561198000000002 - steam_vdf.STEAMID64_BASE), "config", "localconfig.vdf")
            self.assertEqual(steam_vdf.get_launch_options(open(other, encoding="utf-8").read(), "730"), "-second")
            text = open(vdf, encoding="utf-8").read()
            self.assertEqual(steam_vdf.get_launch_options(text, "570"), "-windowed -novid")

    def test_a_broken_file_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "localconfig.vdf")
            open(path, "w", encoding="utf-8").write('"UserLocalConfigStore" { "Software" {')
            ok, logs = core_logic.save_launch_options(path, "-novid")
            self.assertFalse(ok)
            self.assertEqual(open(path, encoding="utf-8").read(), '"UserLocalConfigStore" { "Software" {')


class LaunchSaveRefusesWhileSteamRuns(unittest.TestCase):
    def test_steam_running_blocks_the_save(self):
        core = core_service.Core()
        with mock.patch.object(hardware_info, "get_current_launch_options", return_value=("", "x.vdf")), \
                mock.patch.object(core_logic, "is_steam_running", return_value=True), \
                mock.patch.object(core_logic, "save_launch_options") as save:
            r = core.launch_save("-novid")
        self.assertFalse(r["ok"])
        self.assertIn("Steam is running", r["error"])
        save.assert_not_called()


if __name__ == "__main__":
    unittest.main()
