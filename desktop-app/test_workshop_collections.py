"""Server map collections: validation, cache and snapshot fallback, counts and sizes, the help dialog data, and Map Cleaner protection by
collection membership. Fake Steam replies and fake folders only; LOCALAPPDATA is redirected so the real cache is never touched."""
import io
import json
import os
import tempfile
import unittest
from unittest import mock

import _test_isolation  # noqa: F401  (temp config; must come first)
import core_service
import custom_map_cleaner
import steam_paths
import workshop_collections as wc


class FakeResp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def reply(obj):
    return FakeResp(json.dumps(obj).encode())


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        patcher = mock.patch.dict(os.environ, {"LOCALAPPDATA": self.tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.tmp.cleanup)


class Validation(Base):
    def test_bundled_file_is_valid_and_has_every_server(self):
        cfg = wc.load_config()
        for sid in ("gfl", "possession", "mapeadores", "cola", "net4all", "rss"):
            self.assertIn(sid, cfg["servers"])
        self.assertTrue(cfg["assets"])
        self.assertTrue(all(e["id"].isdigit() for e in wc.all_entries(cfg)))

    def test_anything_that_is_not_a_plain_id_is_dropped(self):
        bad = {"servers": {"Evil Server!": [{"id": "123", "kind": "maps"}, {"id": "12345678; calc", "kind": "maps"}, {"id": "99999999", "kind": "exe"},
                                              {"id": "99999999", "kind": "maps", "label": "x" * 500, "community": "GFL<script>", "prefix": "ze_"}]},
               "assets": [{"id": "../../etc", "kind": "assets"}]}
        clean = wc.validate(bad)
        entries = clean["servers"]["evilserver"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["id"], "99999999")
        self.assertLessEqual(len(entries[0]["label"]), 80)
        self.assertEqual(entries[0]["community"], "gflscript")
        self.assertEqual(clean["assets"], [])
        self.assertIsNone(wc.validate({"servers": {}}))
        self.assertIsNone(wc.validate("nope"))

    def test_downloaded_list_is_used_only_when_valid(self):
        good = {"servers": {"gfl": [{"id": "111111111", "label": "New", "kind": "maps", "community": "gfl"}]}, "assets": []}
        with mock.patch.object(wc.urllib.request, "urlopen", return_value=FakeResp(json.dumps(good).encode())):
            self.assertTrue(wc.refresh_config())
        self.assertEqual(wc.load_config()["servers"]["gfl"][0]["id"], "111111111")
        with mock.patch.object(wc.urllib.request, "urlopen", return_value=FakeResp(b'{"servers": "broken"}')):
            self.assertFalse(wc.refresh_config())
        self.assertEqual(wc.load_config()["servers"]["gfl"][0]["id"], "111111111")          # the bad download did not replace the good copy


class Children(Base):
    def test_snapshot_is_the_offline_fallback_and_a_fetch_fills_the_cache(self):
        gfl = wc.entries_for("gfl")[0]["id"]
        self.assertGreater(len(wc.cached_children(gfl) or []), 300)                          # shipped snapshot, no network
        body = {"response": {"collectiondetails": [{"children": [{"publishedfileid": "1000001"}, {"publishedfileid": "x"}, {"publishedfileid": "1000002"}]}]}}
        with mock.patch.object(wc.urllib.request, "urlopen", return_value=reply(body)):
            self.assertEqual(wc.fetch_children(gfl), ["1000001", "1000002"])                 # non-numeric ids are ignored
        self.assertEqual(wc.cached_children(gfl), ["1000001", "1000002"])

    def test_network_failure_falls_back_to_what_is_known(self):
        gfl = wc.entries_for("gfl")[0]["id"]
        with mock.patch.object(wc.urllib.request, "urlopen", side_effect=OSError("offline")):
            self.assertIsNone(wc.fetch_children(gfl))
            self.assertGreater(len(wc.children(gfl)), 300)                                   # snapshot
        self.assertIsNone(wc.fetch_children("not-an-id"))


class Counts(Base):
    def test_state_counts_installed_items_and_puts_the_matching_collection_first(self):
        by_id = {"3667545564": ["1", "2", "3", "4"], "3688322493": ["10", "11"]}
        with mock.patch.object(wc, "children", side_effect=lambda cid, t=0: by_id.get(cid, ["500", "501"])):
            rows = wc.state("possession", {"1", "2", "11", "500"}, "zm_")
        self.assertEqual([r["id"] for r in rows][:2], ["3688322493", "3667545564"])        # zm map -> the zm collection first
        self.assertEqual((rows[0]["installed"], rows[0]["total"]), (1, 2))
        self.assertEqual((rows[1]["installed"], rows[1]["total"]), (2, 4))
        self.assertNotIn("3252070217", [r["id"] for r in rows])                              # the shared asset collection is no longer offered to users
        self.assertEqual([r["kind"] for r in rows if r["kind"] == "item"], ["item"] * 3)     # Possession's three asset packs are listed, after the maps

    def test_mode_shows_only_maps_or_only_asset_packs(self):
        with mock.patch.object(wc, "children", return_value=["1", "2"]):
            maps = wc.state("possession", {"3535955403"}, "", "maps")
            assets = wc.state("possession", {"3535955403"}, "", "assets")
        self.assertTrue(maps and all(r["kind"] in ("maps", "default") for r in maps))
        self.assertTrue(assets and all(r["kind"] == "item" for r in assets))
        by_id = {r["id"]: r for r in assets}
        self.assertEqual(by_id["3535955403"]["installed"], 1)                                # a single asset pack: installed or not
        self.assertEqual(by_id["3698341219"]["installed"], 0)
        self.assertEqual(by_id["3698341219"]["total"], 1)

    def test_size_counts_known_sizes_and_reports_hidden_items(self):
        details = {"response": {"publishedfiledetails": [
            {"publishedfileid": "1", "result": 1, "file_size": "100"}, {"publishedfileid": "2", "result": 1, "file_size": "300"},
            {"publishedfileid": "3", "result": 9}, {"publishedfileid": "4", "result": 1, "file_size": "5"}]}}
        with mock.patch.object(wc, "children", return_value=["1", "2", "3", "4"]), mock.patch.object(wc.urllib.request, "urlopen", return_value=reply(details)):
            r = wc.size_of_missing("123456", {"4"})
        self.assertEqual(r, {"missing": 3, "known": 2, "unknown": 1, "bytes": 400})
        with mock.patch.object(wc, "children", return_value=["1", "2", "3", "4"]), mock.patch.object(wc.urllib.request, "urlopen", side_effect=OSError("cached now")):
            self.assertEqual(wc.size_of_missing("123456", {"4"})["bytes"], 400)             # answered from the cache, no second request


class CoreDialog(Base):
    def setUp(self):
        super().setUp()
        self.core = core_service.Core()

    def test_catalog_marks_servers_that_have_collections(self):
        packs = {s["id"]: [p["kind"] for p in s["packs"]] for s in self.core.servers_catalog() if s["group"] == "global"}
        self.assertEqual(packs["gfl"], ["maps", "item"])                                    # map pack + its server asset pack
        self.assertEqual(packs["rss"], ["assets"])                                          # RSS has no map collection, only assets
        self.assertEqual(packs["mapeadores"], ["maps", "default", "item"])
        self.assertEqual(packs["possession"].count("item"), 3)
        self.assertNotIn("maps", packs["rss"])
        self.assertEqual(packs["cola"], ["maps", "item"])

    def test_map_help_returns_the_single_map_and_the_collections(self):
        with mock.patch.object(self.core, "installed_maps", return_value={"ids": {"1"}, "names": set(), "known": True}), \
                mock.patch.object(wc, "children", side_effect=lambda cid, t=0: ["1", "2", "3"]):
            h = self.core.map_help("possession", "workshop/5/ZM_Test_Map", "12345")
        self.assertEqual(h["map"], {"name": "zm_test_map", "wid": "12345"})
        self.assertTrue(h["collections"][0]["match"])
        self.assertEqual(h["collections"][0]["installed"], 1)
        self.assertIsNone(self.core.map_help("gfl")["map"])                                 # the Map pack link has no single map

    def test_only_known_collections_can_be_opened_or_measured(self):
        known = wc.entries_for("gfl")[0]["id"]
        with mock.patch.object(self.core, "open_url", return_value=True) as ou, mock.patch.object(self.core, "installed_maps", return_value={"ids": set()}):
            self.assertTrue(self.core.collection_open(known)["ok"])
            ou.assert_called_once_with(f"steam://url/CommunityFilePage/{known}")
            self.assertFalse(self.core.collection_open("999999999")["ok"])                   # an id that is not on the list is refused
            self.assertFalse(self.core.collection_open("1; calc")["ok"])
            self.assertFalse(self.core.collection_size("999999999")["ok"])
        self.assertEqual(ou.call_count, 1)


class GflReuploads(Base):
    """Owner 2026-11-11: GFL uploads its own copy of every map it runs, so GFL's collection is the basis: only an installed item of that
    collection counts, a same-named map from the mapper or another server does not."""
    GFL = {"100", "200", "300"}

    def installed(self, ids, id_names):
        return {"ids": set(ids), "names": {n for v in id_names.values() for n in v}, "id_names": id_names, "known": True}

    def status(self, installed, map_name="ze_foo_p"):
        core = core_service.Core()
        info = {"online": True, "map": map_name, "curr_players": 5, "bots": 0, "max_players": 64, "rtt": 40, "server_name": "GFL"}
        with mock.patch.object(core_service.server_browser, "query_server_info", return_value=info),                 mock.patch.object(core, "installed_maps", return_value=installed), mock.patch.object(wc, "map_ids", return_value=self.GFL),                 mock.patch.object(core_service.server_browser, "_get_s2ze_map_meta", return_value={"addon": "999"}),                 mock.patch.dict(core.paths, {"cs2_dir": "C:/cs2"}):
            return core.server_status("gfl")

    def test_only_gfls_own_item_counts_as_installed(self):
        ok = self.status(self.installed({"100", "7"}, {"100": {"ze_foo_p"}, "7": {"ze_bar"}}))
        self.assertFalse(ok["map_missing"])
        # the same map name is installed, but from another workshop item (the mapper's): GFL's copy is still missing
        other = self.status(self.installed({"7", "100"}, {"7": {"ze_foo_p"}, "100": {"ze_bar_p"}}))
        self.assertTrue(other["map_missing"] and other["map_reupload"])
        self.assertEqual(other["map_wid"], "")                                               # GFL's item id is hidden: no mapper page is offered
        self.assertEqual(other["map_pending"], 2)                                            # 200 and 300 of the collection are not installed

    def test_name_match_ignores_the_trailing_p_and_case(self):
        self.assertFalse(self.status(self.installed({"100"}, {"100": {"ze_foo_p"}}), "ZE_Foo")["map_missing"])

    def test_other_servers_are_unchanged(self):
        self.assertFalse(wc.reuploads("rss"))
        self.assertTrue(wc.reuploads("gfl"))

    def test_the_dialog_has_no_single_map_page_for_gfl_and_counts_what_is_missing(self):
        core = core_service.Core()
        with mock.patch.object(core, "installed_maps", return_value=self.installed({"100"}, {"100": {"ze_x"}})),                 mock.patch.object(wc, "map_ids", return_value=self.GFL), mock.patch.object(wc, "children", return_value=list(self.GFL)):
            h = core.map_help("gfl", "ze_foo_p", "999", "maps")
            self.assertIsNone(h["map"])
            self.assertTrue(h["reupload"])
            self.assertEqual(h["pending"], 2)
            self.assertFalse(core.map_help("gfl", "", "", "maps")["reupload"] and core.map_help("gfl", "", "", "maps")["map"])

    def test_new_maps_are_reported_after_a_baseline_and_clear_when_subscribed(self):
        ids = lambda *a: list(a)
        with mock.patch.object(wc, "children", return_value=ids("1", "2", "3")):
            first = wc.news("gfl", {"1", "2"}, None)                                          # first look: baseline only, "3" is not news
            self.assertEqual(first["new"], 0)
        with mock.patch.object(wc, "children", return_value=ids("1", "2", "3", "4", "5")):
            second = wc.news("gfl", {"1", "2"}, first["state"])
            self.assertEqual(second["new"], 2)                                                # 4 and 5 appeared after the baseline
            again = wc.news("gfl", {"1", "2"}, second["state"])
            self.assertEqual(again["new"], 2)                                                 # and stay news until subscribed
            done = wc.news("gfl", {"1", "2", "4"}, again["state"])
            self.assertEqual(done["new"], 1)
            self.assertEqual(done["missing"], 2)
            stranger = wc.news("gfl", set(), None)                                            # nobody who has no GFL map is told anything
            self.assertEqual(stranger["new"], 0)
        with mock.patch.object(wc, "children", return_value=None):
            self.assertFalse(wc.news("gfl", {"1"}, None)["known"])

    def test_the_cleaner_no_longer_calls_a_map_gfl_by_its_name(self):
        sig = next(iter(custom_map_cleaner.COMMUNITY_SERVER_ROSTERS["gfl"]["signature_maps"]), None)
        if sig:
            self.assertNotEqual(custom_map_cleaner.identify_community_for_map(sig, "42", sig)[0], "gfl")
        self.assertEqual(custom_map_cleaner.identify_community_for_map("x", "3793587501", "x")[0], "gfl")   # its asset pack still is


class ChinaChecked(Base):
    """Owner request 2026-11-11: Planet China gets the missing-map warning back (no map pack there: it links straight to the map's own page)."""

    def test_planet_china_servers_get_the_missing_map_warning_with_the_direct_map_id(self):
        core = core_service.Core()
        info = {"online": True, "map": "ze_not_on_this_pc", "curr_players": 5, "bots": 0, "max_players": 64, "rtt": 40, "server_name": "x"}
        with mock.patch.object(core_service.server_browser, "query_server_info", return_value=info),                 mock.patch.object(core, "installed_maps", return_value={"ids": set(), "names": set(), "known": True}),                 mock.patch.object(core_service.server_browser, "_get_s2ze_map_meta", return_value={"addon": "123456789"}),                 mock.patch.object(core, "_china_servers", return_value=[{"id": "exg_1", "name": "EXG", "host": "1.2.3.4", "port": 27015, "region": "x", "cluster": "c", "group": "china"}]),                 mock.patch.dict(core.paths, {"cs2_dir": "C:/cs2"}):
            china = core.server_status("exg_1")
            self.assertTrue(china["map_missing"])
            self.assertEqual(china["map_wid"], "123456789")                                   # the link opens the map's own workshop page
            gfl = core.server_status("gfl")
        self.assertTrue(gfl["map_missing"])                                                  # a global server with the same map still warns


class ExactIds(Base):
    """The RSS case: a map with the same name is installed, but it is another workshop item than the one the server uses."""

    def test_snapshot_has_the_rss_list_and_each_servers_own_ids(self):
        rss = wc.exact_map_id("rss", "ze_surf_facility_p")
        self.assertTrue(rss.isdigit())
        self.assertNotEqual(rss, "3554884666")                                                   # GFL's item with the same name is another workshop item
        self.assertEqual(wc.exact_map_id("rss", "ZE_SURF_FACILITY_P"), rss)                      # case does not matter
        self.assertEqual(wc.exact_map_id("rss", "ze_not_a_real_map"), "")
        self.assertEqual(wc.exact_map_id("gfl", "ze_surf_facility_p"), "")                       # GFL's list has no titles: falls back to the old check

    def test_rss_list_makes_rss_a_community_without_a_steam_collection(self):
        rss_id = wc.exact_map_id("rss", "ze_surf_facility_p")
        self.assertIn("rss", wc.communities_of(rss_id))

    def test_a_same_named_map_from_another_server_is_not_enough(self):
        core = core_service.Core()
        wid = wc.exact_map_id("rss", "ze_surf_facility_p")
        other = "3554884666"
        self.assertNotEqual(wid, other)
        with mock.patch.object(core, "installed_maps", return_value={"ids": {other}, "names": {"ze_surf_facility_p"}, "known": True}), \
                mock.patch.dict(core.paths, {"cs2_dir": "C:/cs2"}):
            r = core.map_check("ze_surf_facility_p", "rss")
            self.assertTrue(r["missing"])                                                       # RSS uses a different item than the one installed
            self.assertEqual(r["wid"], wid)                                                     # and the link opens the right one
        with mock.patch.object(core, "installed_maps", return_value={"ids": {wid}, "names": set(), "known": True}), \
                mock.patch.dict(core.paths, {"cs2_dir": "C:/cs2"}):
            self.assertFalse(core.map_check("ze_surf_facility_p", "rss")["missing"])


class AssetItems(Base):
    def test_single_asset_items_are_listed_protected_and_openable(self):
        for sid, wid in (("gfl", "3793587501"), ("mapeadores", "3157469866"), ("net4all", "3161970271"), ("cola", "3304608958")):
            self.assertIn(wid, [e["id"] for e in wc.entries_for(sid) if e["kind"] == "item"])
        self.assertTrue({"3793587501", "3157469866", "3161970271", "3304608958", "3535955403", "3698341219", "3333820862"} <= wc.asset_ids())
        core = core_service.Core()
        with mock.patch.object(core, "open_url", return_value=True) as ou, mock.patch.object(core, "installed_maps", return_value={"ids": set()}):
            self.assertTrue(core.collection_open("3793587501")["ok"])
            ou.assert_called_once_with("steam://url/CommunityFilePage/3793587501")

    def test_size_of_a_single_asset_item_is_its_own_size(self):
        details = {"response": {"publishedfiledetails": [{"publishedfileid": "3793587501", "result": 1, "file_size": "1000"}]}}
        with mock.patch.object(wc.urllib.request, "urlopen", return_value=reply(details)):
            r = wc.size_of_missing("3793587501", set())
        self.assertEqual((r["missing"], r["bytes"]), (1, 1000))
        self.assertEqual(wc.size_of_missing("3793587501", {"3793587501"})["missing"], 0)

    def test_an_asset_pack_is_deleted_only_when_the_user_allowed_it(self):
        with tempfile.TemporaryDirectory() as steam:
            ws = os.path.join(steam, "steamapps", "workshop", "content", "730")
            os.makedirs(os.path.join(ws, "1000004"))
            open(os.path.join(ws, "1000004", "1000004.vpk"), "wb").write(b"x" * 4000)
            core = core_service.Core()
            core.paths["steam_path"], core.paths["cs2_dir"] = steam, None
            for allow, gone in ((False, False), (True, True)):
                with mock.patch.object(steam_paths, "steam_libraries", return_value=[steam]), \
                        mock.patch.object(wc, "asset_ids", return_value={"1000004"}), mock.patch.object(wc, "communities_of", return_value=[]), \
                        mock.patch.object(custom_map_cleaner, "is_deletable_map_path", return_value=True):
                    items = custom_map_cleaner.scan_custom_maps(steam, None, set(), False)
                    pack = [i for i in items if i["id"] == "1000004"]
                    self.assertTrue(pack and pack[0]["is_server_asset"])
                    count, _, logs = custom_map_cleaner.delete_custom_maps(pack, allow_assets=allow)
                self.assertEqual(count, 1 if gone else 0, logs)
                self.assertEqual(os.path.exists(os.path.join(ws, "1000004")), not gone)


class CleanerProtection(Base):
    def test_protection_follows_collection_membership_and_assets_are_protected(self):
        with tempfile.TemporaryDirectory() as steam:
            ws = os.path.join(steam, "steamapps", "workshop", "content", "730")
            for wid, title in (("1000001", "ze_in_pse_and_cola"), ("1000002", "ze_in_net4all"), ("1000003", "ze_in_nothing"), ("1000004", "pack")):
                os.makedirs(os.path.join(ws, wid))
                open(os.path.join(ws, wid, wid + ".vpk"), "wb").write(b"x" * 4000)
                open(os.path.join(ws, wid, "publish_data.txt"), "w").write('"publish_data"\n{\n\t"title"\t\t"%s"\n}\n' % title)
            member = {"1000001": ["possession", "mapeadores_cola"], "1000002": ["net4all"]}
            with mock.patch.object(steam_paths, "steam_libraries", return_value=[steam]), \
                    mock.patch.object(wc, "communities_of", side_effect=lambda w: member.get(w, [])), \
                    mock.patch.object(wc, "asset_ids", return_value={"1000004"}), \
                    mock.patch.object(wc, "asset_title", return_value="Some server assets"):
                only_cola = {i["id"]: i for i in custom_map_cleaner.scan_custom_maps(steam, None, {"mapeadores_cola"}, False)}
                only_net = {i["id"]: i for i in custom_map_cleaner.scan_custom_maps(steam, None, {"net4all"}, False)}
                nothing = {i["id"]: i for i in custom_map_cleaner.scan_custom_maps(steam, None, set(), False)}
        self.assertTrue(only_cola["1000001"]["is_protected"])                               # in the PSE and cOLa collections: one tick is enough
        self.assertFalse(only_cola["1000002"]["is_protected"])
        self.assertTrue(only_net["1000002"]["is_protected"])
        self.assertFalse(nothing["1000001"]["is_protected"])                                # nothing ticked: deletable
        self.assertFalse(nothing["1000003"]["is_protected"])                                # in no collection: a temp download
        for scan in (only_cola, only_net, nothing):
            self.assertTrue(scan["1000004"]["is_server_asset"] and scan["1000004"]["is_protected"])
        self.assertEqual(nothing["1000004"]["name"], "Some server assets")


class CleanerGflOnlyAndAssetLists(Base):
    """Only GFL's own collection protects maps now; 'Active' covers the last 30 days; the owner's server asset lists are always protected."""

    ASSETS = {
        "gfl": {"3793587501"}, "possession": {"3535955403", "3698341219", "3333820862"},
        "rss": {"3782730321", "3782731016", "3782731693", "3782732358"}, "net4all": {"3161970271"},
        "mapeadores": {"3157469866"}, "cola": {"3304608958"},
    }
    RETIRED = {"3160448201", "3075687337", "3076940469", "3103181471"}

    def test_settings_only_know_gfl_whatever_an_old_config_holds(self):
        core = core_service.Core()
        core.config["cleaner_protected_comms"] = ["gfl", "possession", "rss", "mapeadores_cola", "net4all"]
        self.assertEqual(core.maps_settings()["communities"], ["gfl"])
        core.config["cleaner_protected_comms"] = ["possession", "rss"]
        self.assertEqual(core.maps_settings()["communities"], [])

    def test_every_listed_asset_pack_is_an_asset_and_retired_ones_are_not(self):
        for sid, ids in self.ASSETS.items():
            for wid in ids:
                self.assertTrue(custom_map_cleaner.is_asset_pack_or_custom("x", wid, "")[0], (sid, wid))
        for wid in self.RETIRED:
            self.assertNotIn(wid, custom_map_cleaner.KNOWN_SERVER_ASSETS)
            self.assertFalse(custom_map_cleaner.is_asset_pack_or_custom("x", wid, "ze_some_map")[0], wid)

    def test_recent_window_is_30_days_and_other_servers_do_not_protect(self):
        import time
        self.assertEqual(custom_map_cleaner.RECENT_DAYS, 30)
        with tempfile.TemporaryDirectory() as steam:
            ws = os.path.join(steam, "steamapps", "workshop", "content", "730")
            for wid, days in (("2000001", 29), ("2000002", 31), ("2000003", 100)):
                os.makedirs(os.path.join(ws, wid))
                f = os.path.join(ws, wid, wid + ".vpk")
                open(f, "wb").write(b"x" * 4000)
                open(os.path.join(ws, wid, "publish_data.txt"), "w").write('"publish_data"\n{\n\t"title"\t\t"ze_map_%s"\n}\n' % wid)
                t = time.time() - days * 86400
                os.utime(f, (t, t)); os.utime(os.path.join(ws, wid), (t, t)); os.utime(os.path.join(ws, wid, "publish_data.txt"), (t, t))
            member = {"2000003": ["possession"]}                      # in the PSE collection, but PSE no longer protects
            with mock.patch.object(steam_paths, "steam_libraries", return_value=[steam]),                     mock.patch.object(wc, "communities_of", side_effect=lambda w: member.get(w, [])),                     mock.patch.object(wc, "asset_ids", return_value=set()):
                rows = {i["id"]: i for i in custom_map_cleaner.scan_custom_maps(steam, None, None, True)}
        self.assertTrue(rows["2000001"]["is_protected"])               # played 29 days ago: Active
        self.assertFalse(rows["2000002"]["is_protected"])              # 31 days: not active
        self.assertFalse(rows["2000003"]["is_protected"])              # PSE collection member, old: deletable


if __name__ == "__main__":
    unittest.main()
