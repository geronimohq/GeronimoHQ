"""Offline tests for scripts/resolve_workshop_maps.py (Steam is faked, no network)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve_workshop_maps as r  # noqa: E402

SEARCH_PAGE = (
    '<a href="https://steamcommunity.com/sharedfiles/filedetails/?id=3583521942" class="x" style="--c:1"><img src="a.jpg" alt="zm_festival" loading="lazy"/></a>'
    '<a href="https://steamcommunity.com/sharedfiles/filedetails/?id=3648327879" class="x"><img src="b.jpg" alt="zm_prisonbreak"/></a>'
    '<a href="https://steamcommunity.com/sharedfiles/filedetails/?id=3777566993" class="x"><img src="c.jpg" alt="z&#xFEFF;m_fes&#x200B;tival"/></a>'
)
SALTFISH_PAGE = (
    '<a href="https://steamcommunity.com/sharedfiles/filedetails/?id=3182860799"><img alt="ze_surf_saltfish_cs2"/></a>'
    '<a href="https://steamcommunity.com/sharedfiles/filedetails/?id=3124799228"><img alt="ze_surf_saltfish_cs2"/></a>'
    '<a href="https://steamcommunity.com/sharedfiles/filedetails/?id=3386114661"><img alt="ze_surf_happy"/></a>'
)


def item_page(*names):
    blocks = "".join(
        '<div class="friendBlock persona offline"><a class="friendBlockLinkOverlay" href="x"></a><div class="friendBlockContent">\n\t\t\t\t%s<br>\n\t\t\t\t'
        '<span class="friendSmallText">Offline</span></div></div>' % n for n in names)
    return ('<div class="rightSectionTopTitle condensed">Created by</div><div class="rightDetailsBlock"><div class="creatorsBlock">%s</div></div></div>'
            '<div class="panel"><div class="parentCollectionsNumOthers">See all 12 collections</div></div>' % blocks)


class Parse(unittest.TestCase):
    def test_exact_title_only_ignoring_case_and_zero_width_characters(self):
        self.assertEqual(r.parse_search(SEARCH_PAGE, "zm_festival"), ["3583521942", "3777566993"])
        self.assertEqual(r.parse_search(SEARCH_PAGE, "ZM_Festival"), ["3583521942", "3777566993"])
        self.assertEqual(r.parse_search(SEARCH_PAGE, "zm_fest"), [])
        self.assertEqual(r.parse_search("", "zm_festival"), [])

    def test_a_title_that_differs_only_by_a_suffix_is_the_same_map_but_exact_comes_first(self):
        self.assertEqual(r.parse_search(SALTFISH_PAGE, "ze_surf_saltfish"), ["3182860799", "3124799228"])
        mixed = SALTFISH_PAGE + '<a href="https://steamcommunity.com/sharedfiles/filedetails/?id=1"><img alt="ze_surf_saltfish"/></a>'
        self.assertEqual(r.parse_search(mixed, "ze_surf_saltfish")[0], "1")
        self.assertEqual(r.parse_search(SALTFISH_PAGE, "ze_surf_happy_v2"), ["3386114661"])
        self.assertEqual(r.parse_search(SALTFISH_PAGE, "ze_surf"), [])           # a prefix of another name is not the same map

    def test_creators_exactly_as_the_item_page_lists_them(self):
        self.assertEqual(r.parse_creators(item_page("K", "Waffel", "chinny")), ["K", "Waffel", "chinny"])
        self.assertEqual(r.parse_creators(item_page("贝拉•利恩特斯")), ["贝拉•利恩特斯"])
        self.assertEqual(r.parse_creators(item_page("A &amp; B", "A &amp; B")), ["A & B"])      # unescaped, no duplicates
        self.assertEqual(r.parse_creators("<html>no creators here</html>"), [])
        self.assertEqual(r.parse_creators(""), [])
        self.assertEqual(len(r.parse_creators(item_page(*[f"n{i}" for i in range(20)]))), r.MAX_CREATORS)

    def test_map_key_and_current_maps(self):
        self.assertEqual(r.map_key("workshop/123/ZM_Test"), "zm_test")
        self.assertIsNone(r.map_key("bad name!"))
        self.assertIsNone(r.map_key(""))
        live = {"servers": {"a": {"map": "ze_a"}, "b": {"map": "ze_a"}, "c": {"map": "zm_b"}, "d": {}}}
        self.assertEqual(r.current_maps(live), ["ze_a", "zm_b"])

    def test_pick_best_prefers_the_most_subscribed_visible_item(self):
        d = {"response": {"publishedfiledetails": [
            {"publishedfileid": "1", "result": 1, "subscriptions": 5},
            {"publishedfileid": "2", "result": 1, "subscriptions": 900},
            {"publishedfileid": "3", "result": 1, "subscriptions": 5000, "banned": 1},
            {"publishedfileid": "4", "result": 9, "subscriptions": 9999}]}}
        self.assertEqual(r.pick_best(d), "2")
        self.assertIsNone(r.pick_best({}))


class Lookup(unittest.TestCase):
    def test_catalog_id_skips_the_search_and_the_name_comes_from_the_page_not_the_catalog(self):
        calls = []

        def fetch(url, *a, **k):
            calls.append(url)
            return item_page("xm1000")                       # the catalog still says the creator's old name
        got = r.lookup("zm_summer_house_night", {"zm_summer_house_night": {"mapper": "Error.vmdl", "addon": "3430766349"}}, fetch=fetch, details=None, pause=0)
        self.assertEqual(got, {"id": "3430766349", "mapper": "xm1000", "src": "page"})
        self.assertEqual(calls, ["https://steamcommunity.com/sharedfiles/filedetails/?id=3430766349"])

    def test_search_then_page(self):
        def fetch(url, *a, **k):
            return item_page("贝拉•利恩特斯") if "filedetails" in url else SEARCH_PAGE
        details = lambda ids: {"response": {"publishedfiledetails": [{"publishedfileid": ids[0], "result": 1, "subscriptions": 3}]}}
        self.assertEqual(r.lookup("zm_festival", {}, fetch=fetch, details=details, pause=0), {"id": "3583521942", "mapper": "贝拉•利恩特斯", "src": "page"})

    def test_suffix_variant_found_by_search(self):
        def fetch(url, *a, **k):
            return item_page("Saltfish Maker") if "filedetails" in url else SALTFISH_PAGE
        details = lambda ids: {"response": {"publishedfiledetails": [
            {"publishedfileid": "3182860799", "result": 1, "subscriptions": 10}, {"publishedfileid": "3124799228", "result": 1, "subscriptions": 400}]}}
        got = r.lookup("ze_surf_saltfish", {}, fetch=fetch, details=details, pause=0)
        self.assertEqual((got["id"], got["mapper"]), ("3124799228", "Saltfish Maker"))      # most subscribed of the two

    def test_page_unreadable_keeps_id_and_the_older_name_and_is_retried(self):
        def fetch(url, *a, **k):
            raise OSError("steam down")
        got = r.lookup("ze_x", {}, fetch=fetch, details=None, pause=0, known_id="123456789", old_mapper="Old Name")
        self.assertEqual(got, {"id": "123456789", "mapper": "Old Name", "src": "none"})
        self.assertTrue(r.needs_lookup("ze_x", {"ze_x": {"id": "123456789", "mapper": "Old Name", "src": "none", "t": 10**10}}, 10**10 + 5))

    def test_unknown_map_gives_none(self):
        self.assertIsNone(r.lookup("ze_nothing", {}, fetch=lambda *a, **k: "<html></html>", details=lambda ids: {}, pause=0))


class Schedule(unittest.TestCase):
    def test_new_missing_old_and_unread_entries_are_looked_up_fresh_ones_are_not(self):
        now = 1_000_000
        known = {
            "fresh": {"id": "1", "src": "page", "t": now - 100},
            "old": {"id": "2", "src": "page", "t": now - r.REFRESH_AFTER - 1},
            "unread": {"id": "3", "src": "catalog", "t": now - 100},
            "miss_recent": {"id": "", "src": "none", "t": now - 100},
            "miss_old": {"id": "", "src": "none", "t": now - r.RETRY_MISSING_AFTER - 1},
        }
        self.assertEqual([m for m in ("new", *known) if r.needs_lookup(m, known, now)], ["new", "old", "unread", "miss_old"])


if __name__ == "__main__":
    unittest.main()
