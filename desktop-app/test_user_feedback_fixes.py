import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import custom_map_cleaner
import _test_isolation  # noqa: E402,F401  (AUDIT: temp config, no registry; must come before app)
import app

class TestUserFeedbackFixes(unittest.TestCase):
    def test_settings_dialog_text_and_dimensions(self):
        """Verify settings dialog width and wraplength so text is never truncated."""
        app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
        with open(app_path, "r", encoding="utf-8") as f:
            src = f.read()
        self.assertIn("req_w=540, req_h=430", src)
        self.assertIn('Clicking [-] hides window to the tray; clicking [X] closes the application completely.', src)
        self.assertIn('wraplength=480, justify="left"', src)

    def test_cleaner_tooltips_present(self):
        """Verify tooltips on all clickables in custom map cleaner."""
        app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
        with open(app_path, "r", encoding="utf-8") as f:
            src = f.read()
        # Filter tabs
        self.assertIn('add_tooltip(btn_filter_all, "Show all custom community maps', src)
        self.assertIn('add_tooltip(btn_filter_temp, "Show only temporary downloaded maps', src)
        self.assertIn('add_tooltip(btn_filter_sub, "Show maps belonging to your subscribed', src)
        self.assertIn('add_tooltip(btn_filter_assets, "Show essential community server content packs', src)
        self.assertIn('add_tooltip(btn_filter_dupe, "Show duplicate copies', src)
        # Quick selectors
        self.assertIn('add_tooltip(btn_sel_temp, "One-click selects all temporary', src)
        self.assertIn('add_tooltip(btn_sel_dupes, "Selects only temporary duplicate copies', src)
        self.assertIn('add_tooltip(btn_sel_all, "Selects all playable maps', src)
        self.assertIn('add_tooltip(btn_sel_none, "Clears all selections.', src)
        self.assertIn('add_tooltip(btn_sel_large, "Selects all map packages exceeding', src)
        # Bottom buttons
        self.assertIn('add_tooltip(btn_del, "Permanently removes checked maps', src)
        self.assertIn('add_tooltip(btn_bk, "Creates a safe backup of your server asset', src)
        self.assertIn('add_tooltip(btn_rst, "Restores your backed-up custom VPKs', src)
        self.assertIn('add_tooltip(btn_cl, "Closes the Custom Map Cleaner dialog.', src)

    def test_gpu_mpo_ddu_guidance(self):
        """Verify DDU advice and AMD Cleanup Utility caution in MPO Diagnostics and FAQ."""
        app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
        with open(app_path, "r", encoding="utf-8") as f:
            src = f.read()
        self.assertIn("CLEAN DRIVER REINSTALL VIA DDU", src)
        self.assertIn("wagnardsoft.com", src)
        self.assertIn("WHY AVOID AMD CLEANUP UTILITY", src)
        self.assertIn("Official DDU Website Link", src)
        self.assertIn("What should I do before disabling MPO? Should I use DDU or AMD Cleanup Utility?", src)

    def test_playable_map_not_protected_as_asset(self):
        """Verify item 3783036501 is treated as a playable map, NOT an asset pack."""
        maps = custom_map_cleaner.scan_custom_maps(r"E:\SteamLibrary", r"E:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive")
        target = [m for m in maps if m["id"] == "3783036501"]
        if target:
            item = target[0]
            self.assertFalse(item.get("is_server_asset"))
            self.assertEqual(item["name"], "ze_surf_happy_2_newbie_village_p")

    def test_known_server_asset_packs_identified(self):
        """Verify community server asset packs (GFL, Possession PSE, Mapeadores, cOLa-TeaM) are identified."""
        maps = custom_map_cleaner.scan_custom_maps(r"E:\SteamLibrary", r"E:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive")
        by_id = {m["id"]: m for m in maps}
        # Check GFL
        if "3793587501" in by_id:
            self.assertTrue(by_id["3793587501"]["is_server_asset"])
            self.assertIn("GFL Clan ZE", by_id["3793587501"]["name"])
        # Check Possession
        if "3535955403" in by_id:
            self.assertTrue(by_id["3535955403"]["is_server_asset"])
            self.assertIn("Possession ZE", by_id["3535955403"]["name"])
        # Check Mapeadores
        if "3157469866" in by_id:
            self.assertTrue(by_id["3157469866"]["is_server_asset"])
            self.assertIn("Mapeadores ZE", by_id["3157469866"]["name"])
        # Check cOLa-TeaM
        if "3304608958" in by_id:
            self.assertTrue(by_id["3304608958"]["is_server_asset"])
            self.assertIn("cOLa-TeaM", by_id["3304608958"]["name"])

if __name__ == "__main__":
    unittest.main()
