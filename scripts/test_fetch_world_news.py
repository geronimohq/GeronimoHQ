"""Offline tests for scripts/fetch_world_news.py (feeds are faked, no network)."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_world_news as n  # noqa: E402

NOW = 1_800_000_000
H = 3600


def rfc(t):
    import email.utils
    return email.utils.formatdate(t, usegmt=True)


def rss(*items, root='<rss version="2.0"><channel>', end="</channel></rss>"):
    body = "".join("<item><title>%s</title><link>%s</link><pubDate>%s</pubDate><description>%s</description></item>" % i for i in items)
    return root + body + end


SRC_WORLD = {"id": "bbc", "name": "BBC News", "kind": "rss", "mode": "world", "hosts": ("bbc.co.uk",)}
SRC_SCI = {"id": "nasa", "name": "NASA", "kind": "rss", "mode": "science", "hosts": ("nasa.gov",)}
SRC_SETI = {"id": "seti", "name": "SETI Institute", "kind": "rss", "mode": "aliens", "hosts": ("seti.org",)}


def cand(title, source, t, cat="war", hard=False, signal=""):
    return {"title": title, "url": f"https://x.example/{abs(hash((title, source)))}", "source": source, "source_id": source, "cat": cat, "t": t, "signal": signal, "hard": hard}


class Helpers(unittest.TestCase):
    def test_clean_text_strips_tags_entities_and_caps_length(self):
        self.assertEqual(n.clean_text("<p>Fish &amp; <b>chips</b>\n  now</p>"), "Fish & chips now")
        self.assertTrue(n.clean_text("x" * 500, 50).endswith("…") and len(n.clean_text("x" * 500, 50)) == 50)

    def test_safe_url_is_https_on_the_sources_own_host_only(self):
        hosts = ("bbc.co.uk",)
        self.assertEqual(n.safe_url("https://www.bbc.co.uk/news/1", hosts), "https://www.bbc.co.uk/news/1")
        self.assertEqual(n.safe_url("http://www.bbc.co.uk/news/1", hosts), "https://www.bbc.co.uk/news/1")        # upgraded
        for bad in ("javascript:alert(1)", "https://evil.example/bbc.co.uk", "https://bbc.co.uk.evil.example/x", "ftp://bbc.co.uk/x", "",
                    "https://www.bbc.co.uk/a b", 'https://www.bbc.co.uk/"><script>', "//www.bbc.co.uk/x"):
            self.assertEqual(n.safe_url(bad, hosts), "", bad)

    def test_parse_time_rfc822_and_iso(self):
        self.assertEqual(n.parse_time("Wed, 11 Nov 2026 19:45:03 GMT"), 1794426303)
        self.assertEqual(n.parse_time("2026-11-11T19:45:03Z"), 1794426303)
        self.assertEqual(n.parse_time("garbage"), 0)
        self.assertEqual(n.parse_time(""), 0)

    def test_parse_feed_rss_atom_rdf(self):
        self.assertEqual([i["title"] for i in n.parse_feed(rss(("A", "https://a.example/1", rfc(NOW), "d")))], ["A"])
        atom = ('<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>B</title><link href="https://b.example/2"/>'
                '<updated>2026-11-11T19:45:03Z</updated><summary>s</summary></entry></feed>')
        got = n.parse_feed(atom)
        self.assertEqual((got[0]["title"], got[0]["link"], got[0]["t"]), ("B", "https://b.example/2", 1794426303))
        rdf = ('<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/" xmlns:dc="http://purl.org/dc/elements/1.1/">'
               '<item><title>C</title><link>https://c.example/3</link><dc:date>2026-11-11T19:45:03Z</dc:date></item></rdf:RDF>')
        self.assertEqual(n.parse_feed(rdf)[0]["title"], "C")

    def test_parse_feed_refuses_dtd_entities_and_garbage(self):
        bomb = '<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "aaaa">]>' + rss(("&a;", "https://a.example/1", rfc(NOW), ""))
        self.assertEqual(n.parse_feed(bomb), [])
        self.assertEqual(n.parse_feed("not xml at all"), [])
        self.assertEqual(n.parse_feed(""), [])


class Classify(unittest.TestCase):
    def test_war_disaster_science_aliens(self):
        self.assertEqual(n.classify("Airstrikes hit the city as ceasefire talks stall", "", "world"), ["war"])
        self.assertEqual(n.classify("Magnitude 7 earthquake and tsunami warning", "", "world"), ["disaster"])
        self.assertEqual(n.classify("Scientists discover a new species of frog", "", "science"), ["science"])
        self.assertIn("aliens", n.classify("Astronomers look for technosignatures", "", "science"))
        self.assertEqual(n.classify("Football club wins the cup", "", "world"), [])

    def test_known_false_friends_are_left_out(self):
        for t in ("Trade war: new tariffs announced", "Star Wars sequel gets a date", "Armistice Day: remembering the end of World War I",
                  "Watch: boy receives prosthetic legs after drone attack", "Victims of Nazi war crimes honoured"):
            self.assertEqual(n.classify(t, "", "world"), [], t)
        self.assertEqual(n.classify("Illegal aliens bill passes the senate", "", "world"), [])
        self.assertEqual(n.classify("Invasive alien species spread in lakes", "", "science"), [])

    def test_world_feeds_do_not_leak_science_and_seti_newsletters_are_skipped(self):
        self.assertEqual(n.classify("Scientists discover a new species of frog", "", "world"), [])
        self.assertEqual(n.classify("Planetary Picture of the Day - Week of November 2", "life on other worlds", "aliens"), [])
        self.assertEqual(n.classify("Searching for biosignatures in exoplanet atmospheres", "", "aliens"), ["aliens"])


class Build(unittest.TestCase):
    def test_same_story_in_two_outlets_is_one_breaking_item_listing_the_other(self):
        c = [cand("Ceasefire collapses as missiles hit the capital overnight", "BBC News", NOW - 1 * H),
             cand("Missiles hit the capital overnight as ceasefire collapses", "Al Jazeera", NOW - 2 * H)]
        out = n.build_items(c, NOW)
        self.assertEqual(len(out), 1)
        self.assertTrue(out[0]["breaking"])
        self.assertEqual((out[0]["source"], out[0]["also"]), ("BBC News", ["Al Jazeera"]))

    def test_one_outlet_alone_is_not_breaking_but_a_hard_signal_is(self):
        out = n.build_items([cand("Troops advance near the border after offensive", "BBC News", NOW - H)], NOW)
        self.assertFalse(out[0]["breaking"])
        quake = n.build_items([cand("M 6.8 - Pacific", "USGS", NOW - H, "disaster", True, "M6.8")], NOW)
        self.assertTrue(quake[0]["breaking"])
        self.assertEqual(quake[0]["signal"], "M6.8")

    def test_old_items_are_never_breaking_and_ancient_ones_are_dropped(self):
        c = [cand("M 6.8 - Pacific", "USGS", NOW - 8 * H, "disaster", True), cand("Old news", "BBC News", NOW - 30 * 86400)]
        out = n.build_items(c, NOW)
        self.assertEqual(len(out), 1)
        self.assertFalse(out[0]["breaking"])                                                       # 8 hours old: recent, not breaking
        self.assertEqual(n.build_items([cand("Future item", "BBC News", NOW + 5 * H)], NOW), [])  # clock-skewed dates are not trusted

    def test_different_stories_are_not_merged_and_per_category_cap_holds(self):
        c = [cand("Floods hit the northern region", "BBC News", NOW - H, "disaster"), cand("Volcano erupts on the island", "DW", NOW - H, "disaster")]
        self.assertEqual(len(n.build_items(c, NOW)), 2)
        many = [cand(f"Unique story number {i} about different places {chr(97 + i)}{chr(98 + i)}{chr(99 + i)}", "BBC News", NOW - i * 60) for i in range(30)]
        self.assertLessEqual(len(n.build_items(many, NOW)), n.PER_CATEGORY)

    def test_breaking_is_capped(self):
        c = [cand(f"Quake {chr(65 + i)}{chr(66 + i)}{chr(67 + i)}{chr(68 + i)} region{i} strikes coast", "USGS", NOW - 60, "disaster", True) for i in range(11)]
        out = n.build_items(c, NOW)
        self.assertLessEqual(sum(1 for i in out if i["breaking"]), n.MAX_BREAKING)


class Readers(unittest.TestCase):
    def test_usgs(self):
        data = {"features": [{"properties": {"mag": 6.4, "title": "M 6.4 - Solomon Islands", "time": (NOW - H) * 1000, "url": "https://earthquake.usgs.gov/e/1"}},
                             {"properties": {"mag": 6.0, "title": "bad link", "time": NOW * 1000, "url": "https://evil.example/1"}}]}
        rows = n.from_usgs(json.dumps(data), {"hosts": ("usgs.gov",)})
        self.assertEqual([(r["signal"], r["hard"], r["cat"]) for r in rows], [("M6.4", True, "disaster")])

    def test_gdacs_keeps_orange_and_red_only(self):
        feed = rss(("Green earthquake (Magnitude 5.6M) in Guatemala", "http://www.gdacs.org/report.aspx?eventid=1", rfc(NOW), ""),
                   ("Orange tropical cyclone ABC in Philippines", "http://www.gdacs.org/report.aspx?eventid=2", rfc(NOW), ""))
        rows = n.from_gdacs(feed, {"hosts": ("gdacs.org",)})
        self.assertEqual([(r["signal"], r["url"].startswith("https://")) for r in rows], [("Orange alert", True)])

    def test_eonet_wanted_categories_only(self):
        ev = {"events": [
            {"title": "Typhoon X", "link": "https://eonet.gsfc.nasa.gov/api/v3/events/1", "categories": [{"id": "severeStorms"}], "geometry": [{"date": "2026-11-11T10:00:00Z"}]},
            {"title": "Wildfire Y", "link": "https://eonet.gsfc.nasa.gov/api/v3/events/2", "categories": [{"id": "wildfires"}], "geometry": [{"date": "2026-11-11T10:00:00Z"}]}]}
        self.assertEqual([r["title"] for r in n.from_eonet(json.dumps(ev), {"hosts": ("nasa.gov",)})], ["Typhoon X"])

    def test_rss_reader_classifies_and_keeps_only_the_sources_hosts(self):
        feed = rss(("Airstrikes continue as truce talks fail", "https://www.bbc.co.uk/news/1", rfc(NOW - H), ""),
                   ("Airstrikes continue elsewhere", "https://evil.example/2", rfc(NOW - H), ""),
                   ("Recipe of the day", "https://www.bbc.co.uk/news/3", rfc(NOW - H), ""))
        rows = n.from_rss(feed, SRC_WORLD)
        self.assertEqual([(r["cat"], r["title"][:9]) for r in rows], [("war", "Airstrike")])


class Collect(unittest.TestCase):
    def test_one_failing_source_does_not_stop_the_others_and_is_reported(self):
        def fetch(url):
            if "bad" in url:
                raise OSError("down")
            return rss(("Airstrikes hit the city", "https://www.bbc.co.uk/news/1", rfc(NOW - H), ""))
        sources = [dict(SRC_WORLD, url="https://feeds.example/bad"), dict(SRC_WORLD, id="bbc2", name="BBC 2", url="https://feeds.example/good")]
        cands, status = n.collect(fetch=fetch, sources=sources, pause=0)
        self.assertEqual([(s["id"], s["ok"]) for s in status], [("bbc", False), ("bbc2", True)])
        self.assertEqual(len(cands), 1)

    def test_failed_sources_keep_their_older_fresh_items_only(self):
        prev = [{"title": "Old but fresh", "url": "https://www.bbc.co.uk/x", "source": "BBC News", "cat": "war", "t": NOW - 5 * H, "signal": ""},
                {"title": "Too old", "url": "https://www.bbc.co.uk/y", "source": "BBC News", "cat": "war", "t": NOW - 10 * 86400, "signal": ""},
                {"title": "Other source", "url": "https://www.dw.com/z", "source": "DW", "cat": "war", "t": NOW - H, "signal": ""}]
        kept = n.carry_over(prev, [{"name": "BBC News", "ok": False}, {"name": "DW", "ok": True}], NOW)
        self.assertEqual([k["title"] for k in kept], ["Old but fresh"])


if __name__ == "__main__":
    unittest.main()
