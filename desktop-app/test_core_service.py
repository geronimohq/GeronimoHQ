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
    def test_refresh_rate_is_limited_to_1_5_15(self):
        core, _ = make_core()
        with mock.patch("app_config.save_config", return_value=True):
            self.assertTrue(core.config_set("web_refresh_seconds", 1))
            self.assertFalse(core.config_set("web_refresh_seconds", 2))
            self.assertFalse(core.config_set("something_else", 5))


if __name__ == "__main__":
    _res = unittest.main(exit=False, verbosity=2)
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(0 if _res.result.wasSuccessful() else 1)
