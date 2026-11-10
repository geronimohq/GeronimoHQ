"""Offline tests for scripts/refresh_map_mappers.py (no network)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refresh_map_mappers as r  # noqa: E402

PAGE = ('<html><head><title>ze_radio_tower | CS2 Zombie Escape Map - Onono_Imouto</title>'
        '<meta property="og:image" content="https://example.com/a.jpg?x=1&amp;y=2"></head></html>')


class Parse(unittest.TestCase):
    def test_map_page(self):
        self.assertEqual(r.parse_map_page(PAGE), ("ze_radio_tower", "Onono_Imouto", "https://example.com/a.jpg?x=1&y=2"))

    def test_rejects_other_pages_and_bad_names(self):
        self.assertIsNone(r.parse_map_page("<title>Page not found | Ruby Bot Ze</title>"))
        self.assertIsNone(r.parse_map_page("<title>../../x | CS2 Zombie Escape Map - Bob</title>"))
        self.assertIsNone(r.parse_map_page("<title>ze_ok | CS2 Zombie Escape Map - </title>"))
        self.assertIsNone(r.parse_map_page(""))

    def test_home_ids_deduplicated_in_order(self):
        self.assertEqual(r.home_page_ids('<a href="/maps/3836768028"></a><a href="/maps/"></a><a href="/maps/3836768028"></a><a href="/maps/3091057104">'),
                         ["3836768028", "3091057104"])

    def test_add_new_never_overwrites(self):
        cat = {"ze_old": {"mapper": "Keep", "image": "", "addon": "1"}}
        added = r.add_new(cat, [("ze_old", "Other", "", "2"), ("ze_new", "Nobody", "", "3")])
        self.assertEqual(added, ["ze_new"])
        self.assertEqual(cat["ze_old"]["mapper"], "Keep")
        self.assertEqual(cat["ze_new"], {"mapper": "Nobody", "image": "", "addon": "3"})


if __name__ == "__main__":
    unittest.main()
