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
PROFILE = '<?xml version="1.0"?><profile><steamID64>1</steamID64><steamID><![CDATA[贝拉•利恩特斯]]></steamID></profile>'


class Parse(unittest.TestCase):
    def test_exact_title_only_ignoring_case_and_zero_width_characters(self):
        self.assertEqual(r.parse_search(SEARCH_PAGE, "zm_festival"), ["3583521942", "3777566993"])
        self.assertEqual(r.parse_search(SEARCH_PAGE, "ZM_Festival"), ["3583521942", "3777566993"])
        self.assertEqual(r.parse_search(SEARCH_PAGE, "zm_fest"), [])
        self.assertEqual(r.parse_search("", "zm_festival"), [])

    def test_profile_name(self):
        self.assertEqual(r.parse_profile_name(PROFILE), "贝拉•利恩特斯")
        self.assertEqual(r.parse_profile_name("<profile></profile>"), "")
        self.assertEqual(r.parse_profile_name("<steamID><![CDATA[<b>x</b>]]></steamID>"), "")

    def test_map_key_and_current_maps(self):
        self.assertEqual(r.map_key("workshop/123/ZM_Test"), "zm_test")
        self.assertIsNone(r.map_key("bad name!"))
        self.assertIsNone(r.map_key(""))
        live = {"servers": {"a": {"map": "ze_a"}, "b": {"map": "ze_a"}, "c": {"map": "zm_b"}, "d": {}}}
        self.assertEqual(r.current_maps(live), ["ze_a", "zm_b"])

    def test_pick_best_prefers_the_most_subscribed_visible_item(self):
        d = {"response": {"publishedfiledetails": [
            {"publishedfileid": "1", "result": 1, "subscriptions": 5, "creator": "10"},
            {"publishedfileid": "2", "result": 1, "subscriptions": 900, "creator": "20"},
            {"publishedfileid": "3", "result": 1, "subscriptions": 5000, "creator": "30", "banned": 1},
            {"publishedfileid": "4", "result": 9, "subscriptions": 9999, "creator": "40"}]}}
        self.assertEqual(r.pick_best(d), ("2", "20"))
        self.assertIsNone(r.pick_best({}))


class Lookup(unittest.TestCase):
    def test_catalog_id_wins_and_needs_no_network(self):
        def boom(*a, **k):
            raise AssertionError("no network for a catalogued map")
        got = r.lookup("ze_known", {"ze_known": {"mapper": "Kuroki", "addon": "111"}}, {}, fetch=boom, details=boom, pause=0)
        self.assertEqual(got, {"id": "111", "mapper": "Kuroki"})

    def test_search_then_details_then_creator_name_cached(self):
        calls = []

        def fetch(url, *a, **k):
            calls.append(url)
            return PROFILE if "xml=1" in url else SEARCH_PAGE

        details = lambda ids: {"response": {"publishedfiledetails": [{"publishedfileid": ids[0], "result": 1, "subscriptions": 3, "creator": "76561198832662089"}]}}
        creators = {}
        got = r.lookup("zm_festival", {}, creators, fetch=fetch, details=details, pause=0)
        self.assertEqual(got, {"id": "3583521942", "mapper": "贝拉•利恩特斯"})
        self.assertEqual(creators, {"76561198832662089": "贝拉•利恩特斯"})
        calls.clear()
        r.lookup("zm_festival", {}, creators, fetch=fetch, details=details, pause=0)
        self.assertFalse(any("xml=1" in c for c in calls))              # the creator's name is remembered, not asked again

    def test_unknown_map_gives_none(self):
        self.assertIsNone(r.lookup("ze_nothing", {}, {}, fetch=lambda *a, **k: "<html></html>", details=lambda ids: {}, pause=0))


if __name__ == "__main__":
    unittest.main()
