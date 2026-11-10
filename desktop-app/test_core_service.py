"""Headless core used by the web-window front end: no real game servers, no real Windows changes, temp config."""
import os
import sys
import threading
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _test_isolation  # noqa: E402,F401  (temp config; must come first)
import core_logic  # noqa: E402
import core_service  # noqa: E402
import server_browser  # noqa: E402


def make_core():
    events = []
    with mock.patch.object(core_logic, "find_cs2_paths", return_value={"steam_path": "S", "cs2_dir": "D", "cs2_exe": "E", "cfg_dir": "C", "autoexec_cfg": None}):
        core = core_service.Core(emit=lambda ev, data: events.append((ev, data)))
    return core, events


class Servers(unittest.TestCase):
    def test_catalog_has_global_and_china_groups(self):
        core, _ = make_core()
        cat = core.servers_catalog()
        self.assertEqual(sum(1 for s in cat if s["group"] == "china"), 35)
        self.assertTrue(any(s["featured"] and s["id"] == "gfl" for s in cat))
        self.assertEqual(len({s["id"] for s in cat}), len(cat))          # ids are unique

    def test_status_counts_humans_and_builds_both_geo_views(self):
        core, _ = make_core()
        info = {"online": True, "map": "ze_x", "curr_players": 20, "bots": 15, "max_players": 65, "rtt": 141, "server_name": "n"}
        with mock.patch.object(server_browser, "query_server_info", return_value=info), \
             mock.patch.object(server_browser, "backend_player_names", return_value=[]):
            st = core.server_status("net4all")
        self.assertEqual((st["players"], st["bots"], st["humans"]), (20, 15, 5))
        self.assertTrue(st["geo"]["countries"] and st["geo"]["regions"])
        self.assertLessEqual(len(st["geo"]["regions"]), len(st["geo"]["countries"]))

    def test_all_bots_means_no_geo_estimate(self):
        core, _ = make_core()
        info = {"online": True, "map": "m", "curr_players": 16, "bots": 16, "max_players": 65, "rtt": 100}
        with mock.patch.object(server_browser, "query_server_info", return_value=info):
            st = core.server_status("net4all")
        self.assertEqual(st["humans"], 0)
        self.assertEqual(st["geo"], {"countries": [], "regions": []})

    def test_offline_and_unknown_servers_do_not_raise(self):
        core, _ = make_core()
        with mock.patch.object(server_browser, "query_server_info", return_value={"online": False}):
            self.assertFalse(core.server_status("gfl")["online"])
        self.assertFalse(core.server_status("nope")["online"])
        with mock.patch.object(server_browser, "query_server_info", side_effect=RuntimeError("boom")):
            rows = core.servers_status_many(["gfl", "possession"])
        self.assertEqual([r["online"] for r in rows], [False, False])      # one failure never breaks the refresh

    def test_add_server_validates_address(self):
        core, _ = make_core()
        self.assertFalse(core.servers_add("", "1.2.3.4", 27015)["ok"])
        self.assertFalse(core.servers_add("x", "not a host!", 27015)["ok"])
        with mock.patch.object(server_browser, "save_servers", return_value=True) as save:
            self.assertTrue(core.servers_add("My ZE", "1.2.3.4", 27015)["ok"])
        self.assertTrue(save.call_args[0][0][-1]["is_custom"])


class Engine(unittest.TestCase):
    def _patches(self):
        names = ["optimize_windows_game_dvr", "disable_fullscreen_optimizations", "install_autoexec", "clean_shader_caches",
                 "clean_cs2_temp_dumps", "set_power_plan", "remember_power_plan", "revert_windows_game_dvr",
                 "revert_fullscreen_optimizations", "restore_autoexec_backup", "restore_previous_power_plan"]
        ps = {}
        for n in names:
            ps[n] = mock.patch.object(core_logic, n, return_value=[f"{n} ok"]).start()
        ps["install_autoexec"].return_value = (True, ["autoexec ok"])
        ps["clean_shader_caches"].return_value = (3, 1024 * 1024, ["shaders ok"])
        ps["clean_cs2_temp_dumps"].return_value = (1, 10, ["dumps ok"])
        ps["restore_autoexec_backup"].return_value = (True, ["restored"])
        self.addCleanup(mock.patch.stopall)
        return ps

    def _wait_job(self, events, name):
        for _ in range(200):
            if any(e[0] == "job" and e[1]["name"] == name for e in events):
                return
            threading.Event().wait(0.02)
        self.fail("job did not finish")

    def test_apply_runs_only_the_selected_tweaks_and_emits_done(self):
        ps = self._patches()
        core, events = make_core()
        with mock.patch("app_config.save_config", return_value=True), mock.patch("app_config.update_optimization_timestamp", return_value=True):
            self.assertTrue(core.engine_apply({"shaders": True, "gamedvr": True})["ok"])
            self._wait_job(events, "engine_apply")
        ps["clean_shader_caches"].assert_called_once()
        ps["optimize_windows_game_dvr"].assert_called_once()
        ps["install_autoexec"].assert_not_called()
        ps["clean_cs2_temp_dumps"].assert_not_called()
        self.assertIn(("job", {"name": "engine_apply", "ok": True}), events)
        self.assertTrue(any(e[0] == "log" for e in events))

    def test_second_job_is_refused_while_one_runs(self):
        self._patches()
        core, events = make_core()
        gate = threading.Event()
        with mock.patch.object(core_logic, "optimize_windows_game_dvr", side_effect=lambda: (gate.wait(2), ["slow"])[1]), \
             mock.patch("app_config.update_optimization_timestamp", return_value=True):
            self.assertTrue(core.engine_apply({"gamedvr": True})["ok"])
            second = core.engine_apply({"shaders": True})
            gate.set()
            self._wait_job(events, "engine_apply")
        self.assertFalse(second["ok"])

    def test_restore_calls_every_revert(self):
        ps = self._patches()
        core, events = make_core()
        with mock.patch("app_config.save_config", return_value=True):
            core.engine_restore()
            self._wait_job(events, "engine_restore")
        for n in ("revert_windows_game_dvr", "revert_fullscreen_optimizations", "restore_autoexec_backup", "restore_previous_power_plan"):
            ps[n].assert_called_once()

    def test_power_plan_only_accepts_known_values(self):
        self._patches()
        core, _ = make_core()
        self.assertFalse(core.power_set("ultimate")["ok"])


class Settings(unittest.TestCase):
    def test_refresh_rate_is_limited_to_1_5_15_and_shares_the_classic_setting(self):
        core, _ = make_core()
        with mock.patch("app_config.save_config", return_value=True):
            self.assertTrue(core.config_set("web_refresh_seconds", 1))
            self.assertEqual(core.config["server_refresh_speed"], "Live (1s)")
            self.assertEqual(core._refresh_seconds(), 1)
            self.assertFalse(core.config_set("web_refresh_seconds", 2))
            self.assertFalse(core.config_set("something_else", 5))

    def test_settings_roundtrip_ignores_unknown_keys_and_never_touches_the_registry(self):
        core, _ = make_core()
        with mock.patch("app_config.save_config", return_value=True), mock.patch("app_config.set_windows_startup", return_value=True) as startup:
            r = core.settings_save({"start_minimized": True, "server_refresh_speed": "Eco (15s)", "presence_secret": "x", "bogus": 1})
        self.assertTrue(r["ok"])
        self.assertEqual(r["refresh_seconds"], 15)
        self.assertTrue(core.config["start_minimized"])
        self.assertNotEqual(core.config.get("presence_secret"), "x")      # secrets cannot be set from the page
        startup.assert_called_once()
        vals = core.settings_get()
        self.assertEqual(vals["server_refresh_speed"], "Eco (15s)")
        self.assertIn("Live (1s)", vals["speeds"])

    def test_reset_keeps_the_presence_secret(self):
        core, _ = make_core()
        core.config["presence_secret"] = "keepme"
        with mock.patch("app_config.save_config", return_value=True):
            core.settings_reset()
        self.assertEqual(core.config["presence_secret"], "keepme")


class Presence(unittest.TestCase):
    def test_buttons_use_the_server_discord_or_the_portal(self):
        core, _ = make_core()
        gfl = core.presence.buttons("74.91.124.21", 27015)
        self.assertEqual(len(gfl), 2)
        self.assertIn("GFL", gfl[1]["label"])
        other = core.presence.buttons("9.9.9.9", 27015)
        self.assertIn("geronimohq.com", other[1]["url"])      # never another community's Discord
        self.assertTrue(gfl[0]["url"].startswith("https://geronimohq.com/connect?ip="))

    def test_snapshot_is_empty_when_nothing_was_sent_to_discord(self):
        core, _ = make_core()
        with mock.patch.object(core.presence.rpc, "broadcast_snapshot", return_value=None), mock.patch.object(core_logic, "is_cs2_running", return_value=False):
            snap = core.presence_state()
        self.assertEqual((snap["details"], snap["state"], snap["buttons"]), ("", "", []))
        self.assertFalse(snap["cs2_running"])

    def test_match_by_map_picks_the_server_playing_that_map(self):
        core, _ = make_core()

        def fake_info(host, port, timeout=1.8):
            return {"online": True, "map": "ze_target" if host == "103.62.49.55" else "ze_other"}
        with mock.patch.object(server_browser, "query_server_info", side_effect=fake_info):
            hit = core.presence._match_by_map("maps/ze_target")
        self.assertEqual(hit[0], "103.62.49.55")

    def test_toggle_off_clears_the_presence_and_saves(self):
        core, _ = make_core()
        with mock.patch("app_config.save_config", return_value=True), mock.patch.object(core.presence, "clear") as clear:
            core.presence_toggle(False)
        clear.assert_called_once()
        self.assertFalse(core.config["discord_rpc_enabled"])


class MapCleaner(unittest.TestCase):
    ROWS = [{"id": "111", "name": "ze_a", "path": "X:/w/111", "size_bytes": 5, "status_label": "Temp", "status_type": "temp", "is_workshop": True},
            {"id": "222", "name": "ze_b", "path": "X:/w/222", "size_bytes": 7, "status_label": "Temp", "status_type": "temp", "is_workshop": True}]

    def _scan(self, core, events):
        import custom_map_cleaner
        with mock.patch.object(custom_map_cleaner, "scan_custom_maps", return_value=list(self.ROWS)), mock.patch("app_config.save_config", return_value=True):
            self.assertTrue(core.maps_scan(["gfl"], True)["ok"])
            for _ in range(200):
                if any(e[0] == "job" and e[1]["name"] == "maps_scan" for e in events):
                    break
                threading.Event().wait(0.02)

    def test_scan_emits_rows_without_paths(self):
        core, events = make_core()
        self._scan(core, events)
        rows = next(d for e, d in events if e == "maps")
        self.assertEqual([r["id"] for r in rows], ["111", "222"])
        self.assertTrue(all("path" not in r for r in rows))     # the page never learns or sends filesystem paths

    def test_delete_only_acts_on_scanned_items(self):
        import custom_map_cleaner
        core, events = make_core()
        self._scan(core, events)
        self.assertFalse(core.maps_delete(["999", "../../windows"])["ok"])        # unknown ids are refused
        with mock.patch.object(custom_map_cleaner, "delete_custom_maps", return_value=(1, 5, ["[CLEANED]"])) as dele:
            self.assertTrue(core.maps_delete(["111", "999"])["ok"])
            for _ in range(200):
                if any(e[0] == "maps_deleted" for e in events):
                    break
                threading.Event().wait(0.02)
        sent = dele.call_args[0][0]
        self.assertEqual([m["id"] for m in sent], ["111"])


class Updates(unittest.TestCase):
    MANIFEST = {"version": "9.9.9", "notes": "n", "size": 1, "url": "https://geronimohq.com/x.exe", "sha256": "0" * 64, "signature": "0" * 128}

    def test_available_update_is_reported_and_remembered(self):
        import updater
        core, _ = make_core()
        with mock.patch.object(updater, "fetch_update_manifest", return_value=(True, dict(self.MANIFEST), "ok")), mock.patch("app_config.save_config", return_value=True):
            r = core.update_check(manual=True)
        self.assertTrue(r["available"])
        self.assertEqual(r["version"], "9.9.9")

    def test_skipped_version_is_not_announced_at_startup_but_is_on_manual_check(self):
        import updater
        core, _ = make_core()
        core.config["skipped_update_version"] = "9.9.9"
        with mock.patch.object(updater, "fetch_update_manifest", return_value=(True, dict(self.MANIFEST), "ok")), mock.patch("app_config.save_config", return_value=True):
            self.assertFalse(core.update_check(manual=False)["available"])
            self.assertTrue(core.update_check(manual=True)["available"])

    def test_startup_check_respects_the_setting_and_network_errors(self):
        import updater
        core, _ = make_core()
        core.config["check_updates_on_startup"] = False
        with mock.patch.object(updater, "fetch_update_manifest") as f:
            self.assertFalse(core.update_check(manual=False)["available"])
            f.assert_not_called()
        core.config["check_updates_on_startup"] = True
        with mock.patch.object(updater, "fetch_update_manifest", side_effect=OSError("offline")):
            self.assertFalse(core.update_check(manual=True)["available"])

    def test_install_needs_a_checked_update_and_the_packaged_app(self):
        core, _ = make_core()
        self.assertFalse(core.update_install()["ok"])               # nothing pending
        core._pending_manifest = dict(self.MANIFEST)
        self.assertFalse(core.update_install()["ok"])               # not frozen (running from source)


if __name__ == "__main__":
    _res = unittest.main(exit=False, verbosity=2)
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(0 if _res.result.wasSuccessful() else 1)
