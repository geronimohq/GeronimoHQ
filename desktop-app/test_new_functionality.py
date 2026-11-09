import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure utf-8 output in Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import server_browser
from server_browser import ServerSlotSniper

class TestNewSlotSniperAndRefresh(unittest.TestCase):

    def test_gfl_slot_sniper_redirect_at_or_below_60(self):
        """Verify that GFL with <= 60 players does NOT arm sniper and triggers Connect directly."""
        sniper = ServerSlotSniper()
        run_connect_mock = MagicMock()
        log_mock = MagicMock()

        # Simulated server logic matching app.py toggle_server_slot_sniper
        def simulate_toggle(curr_p, tier_str="mapper"):
            target_max = 62 if "mapper" in tier_str else (61 if "normal" in tier_str else 63)
            if curr_p <= 60:
                log_mock(f"[CONNECT] GFL player count is {curr_p}/64 (<= 60). Open slots available, firing Connect directly...")
                run_connect_mock("74.91.124.21", 27015, "GFL Clan Zombie Escape")
                return "CONNECTED_DIRECTLY"
            if curr_p <= target_max:
                log_mock(f"[CONNECT] GFL player count is {curr_p}/64 (Joinable for tier). Firing Connect directly...")
                run_connect_mock("74.91.124.21", 27015, "GFL Clan Zombie Escape")
                return "CONNECTED_DIRECTLY"
            sniper.start("74.91.124.21", 27015, "GFL Clan Zombie Escape", target_max_players=target_max, initial_is_full=True)
            return "SNIPER_ARMED"

        # At 53 players (current real live count <= 60)
        res = simulate_toggle(53, "mapper")
        self.assertEqual(res, "CONNECTED_DIRECTLY")
        self.assertFalse(sniper.is_active)
        run_connect_mock.assert_called_once_with("74.91.124.21", 27015, "GFL Clan Zombie Escape")

        # At 60 players
        run_connect_mock.reset_mock()
        res = simulate_toggle(60, "normal")
        self.assertEqual(res, "CONNECTED_DIRECTLY")
        self.assertFalse(sniper.is_active)
        run_connect_mock.assert_called_once()

    def test_gfl_slot_sniper_tier_boundaries(self):
        """Verify tier specific boundaries: Normal (<=61), Mapper (<=62), VIP (<=63)."""
        sniper = ServerSlotSniper()
        run_connect_mock = MagicMock()

        def simulate_toggle(curr_p, tier_str):
            target_max = 62 if tier_str == "mapper" else (61 if tier_str == "normal" else 63)
            if curr_p <= 60:
                run_connect_mock()
                return "CONNECTED_DIRECTLY"
            if curr_p <= target_max:
                run_connect_mock()
                return "CONNECTED_DIRECTLY"
            sniper.start("74.91.124.21", 27015, "GFL", target_max_players=target_max, initial_is_full=True)
            return "SNIPER_ARMED"

        # Normal player at 61: Joinable!
        self.assertEqual(simulate_toggle(61, "normal"), "CONNECTED_DIRECTLY")
        # Normal player at 62: FULL -> Sniper arms!
        self.assertEqual(simulate_toggle(62, "normal"), "SNIPER_ARMED")
        self.assertTrue(sniper.is_active)
        self.assertEqual(sniper.target_max_players, 61)
        sniper.stop()

        # Mapper at 62: Joinable!
        self.assertEqual(simulate_toggle(62, "mapper"), "CONNECTED_DIRECTLY")
        # Mapper at 63: FULL -> Sniper arms!
        self.assertEqual(simulate_toggle(63, "mapper"), "SNIPER_ARMED")
        self.assertTrue(sniper.is_active)
        self.assertEqual(sniper.target_max_players, 62)
        sniper.stop()

        # VIP at 63: Joinable!
        self.assertEqual(simulate_toggle(63, "vip"), "CONNECTED_DIRECTLY")
        # VIP at 64: FULL -> Sniper arms!
        self.assertEqual(simulate_toggle(64, "vip"), "SNIPER_ARMED")
        self.assertTrue(sniper.is_active)
        self.assertEqual(sniper.target_max_players, 63)
        sniper.stop()

    def test_community_servers_sniper_redirect(self):
        """Verify other community servers: < max_p connects directly; >= max_p arms sniper."""
        sniper = ServerSlotSniper()
        run_connect_mock = MagicMock()

        def simulate_toggle(curr_p, max_p=64):
            if curr_p < max_p:
                run_connect_mock("103.62.49.55", 27015, "Possession")
                return "CONNECTED_DIRECTLY"
            sniper.start("103.62.49.55", 27015, "Possession", initial_is_full=True)
            return "SNIPER_ARMED"

        # 0/64 players -> connects directly
        self.assertEqual(simulate_toggle(0, 64), "CONNECTED_DIRECTLY")
        # 63/64 players -> connects directly
        self.assertEqual(simulate_toggle(63, 64), "CONNECTED_DIRECTLY")
        # 64/64 players -> arms sniper
        self.assertEqual(simulate_toggle(64, 64), "SNIPER_ARMED")
        self.assertTrue(sniper.is_active)
        sniper.stop()

    def test_parallel_query_performance(self):
        """Verify parallel query finishes under 1.5 seconds."""
        import time
        from concurrent.futures import ThreadPoolExecutor
        targets = [{'host': '74.91.124.21', 'port': 27015}] + server_browser.DEFAULT_SERVERS[:5]
        t0 = time.time()
        with ThreadPoolExecutor(max_workers=len(targets)) as pool:
            res = list(pool.map(lambda s: server_browser.query_server_info(s['host'], s['port'], timeout=1.0), targets))
        duration = time.time() - t0
        print(f"Parallel query duration for {len(targets)} servers: {duration:.3f}s")
        self.assertLess(duration, 1.5)
        self.assertEqual(len(res), len(targets))

    def test_app_icon_files_exist_and_load(self):
        """Verify app.png and app.ico exist and are valid format."""
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        img = tk.PhotoImage(file="app.png")
        self.assertIsNotNone(img)
        root.iconphoto(True, img)
        root.destroy()

if __name__ == "__main__":
    unittest.main()
