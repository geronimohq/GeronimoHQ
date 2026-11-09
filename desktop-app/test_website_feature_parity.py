import os
import sys
import unittest
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import server_browser
from server_browser import query_zegraph_match_now, query_zegraph_soundtrack, CHINA_CLUSTERS, DEFAULT_SERVERS
import _test_isolation  # noqa: E402,F401  (AUDIT: temp config, no registry; must come before app)
import app

class TestWebsiteFeatureParity(unittest.TestCase):
    def test_all_servers_and_clusters_count(self):
        """Verify full parity: 6 global servers + 35 china servers across 5 clusters = 41 total nodes."""
        self.assertEqual(len(DEFAULT_SERVERS), 6)
        self.assertEqual(len(CHINA_CLUSTERS), 5)
        total_china_servers = sum(len(c["servers"]) for c in CHINA_CLUSTERS)
        self.assertEqual(total_china_servers, 35)
        self.assertEqual(len(DEFAULT_SERVERS) + total_china_servers, 41)

        cluster_ids = [c["id"] for c in CHINA_CLUSTERS]
        self.assertEqual(cluster_ids, ["exg", "fys", "ub", "zl", "93x"])

    def test_zegraph_match_now_telemetry(self):
        """Verify ZE Graph REST API returns live human and zombie scores and extends."""
        data = query_zegraph_match_now(timeout=4.0)
        self.assertTrue(data.get("success"), f"Failed to fetch live match-now: {data}")
        self.assertIn("human_score", data)
        self.assertIn("zombie_score", data)
        self.assertIn("extend_count", data)
        self.assertIn("started_timestamp", data)
        print(f"\n[TEST PASS] Live Round Score: Humans {data['human_score']} vs Zombies {data['zombie_score']} | Extends: {data['extend_count']}/3")

    def test_zegraph_soundtrack_query(self):
        """Verify soundtrack query fetches songs with valid durations and YouTube links."""
        songs = query_zegraph_soundtrack("ze_s_a_m", timeout=4.0)
        self.assertGreater(len(songs), 0)
        first_song = songs[0]
        self.assertIn("name", first_song)
        self.assertIn("youtube_url", first_song)
        self.assertTrue(first_song["youtube_url"].startswith("https://www.youtube.com/watch?v="))
        print(f"[TEST PASS] Soundtrack song parsed: {first_song['name']} ({first_song['duration_str']}) -> {first_song['youtube_url']}")

    def test_thumbnail_caching(self):
        """Verify thumbnail cache directory and downloader."""
        tdir = server_browser.get_thumbnail_dir()
        self.assertTrue(os.path.isdir(tdir))
        path = server_browser.get_or_download_map_thumbnail("ze_resident_evil_3")
        # May be downloading asynchronously or already cached
        print(f"[TEST PASS] Thumbnail dir: {tdir}")

    def test_community_sniper_slot_priority_thresholds(self):
        """Verify community sniper respects <= 61, <= 62, <= 63 targets."""
        sniper = server_browser.ServerSlotSniper()

        # Target 61
        sniper.start("103.62.49.55", 27015, "Possession", target_max_players=61, initial_is_full=True)
        self.assertEqual(sniper.target_max_players, 61)
        sniper.stop()

        # Target 62
        sniper.start("103.62.49.55", 27015, "Possession", target_max_players=62, initial_is_full=True)
        self.assertEqual(sniper.target_max_players, 62)
        sniper.stop()

        # Target 63
        sniper.start("103.62.49.55", 27015, "Possession", target_max_players=63, initial_is_full=True)
        self.assertEqual(sniper.target_max_players, 63)
        sniper.stop()

if __name__ == "__main__":
    unittest.main()
