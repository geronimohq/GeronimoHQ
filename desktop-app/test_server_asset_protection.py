import os
import sys
import unittest
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import custom_map_cleaner

class TestServerAssetProtection(unittest.TestCase):

    def test_gfl_asset_pack_detection(self):
        """Verify that GFL 3793587501 is detected as a protected Server Asset Pack."""
        # Simulated workshop item for GFL
        maps = custom_map_cleaner.scan_custom_maps(r"E:\SteamLibrary", r"E:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive")
        gfl_items = [m for m in maps if m["id"] == "3793587501"]
        self.assertTrue(len(gfl_items) > 0, "GFL Asset Pack 3793587501 should be detected")
        gfl = gfl_items[0]
        self.assertTrue(gfl.get("is_server_asset"), "Should have is_server_asset=True")
        self.assertTrue(gfl.get("is_protected"), "Should have is_protected=True")
        self.assertFalse(gfl.get("has_duplicate"), "Should NEVER be flagged as duplicate")
        self.assertIn("Server Assets & Content Pack", gfl["name"])
        self.assertIn("PROTECTED", gfl["status_label"])

    def test_custom_vpk_detection(self):
        """Verify that playable maps where users modify files (e.g. 3783036501 ze_surf_happy_2_newbie_village_p) are NOT falsely classified as server asset packs."""
        maps = custom_map_cleaner.scan_custom_maps(r"E:\SteamLibrary", r"E:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive")
        custom_items = [m for m in maps if m["id"] == "3783036501"]
        if custom_items:
            c = custom_items[0]
            self.assertFalse(c.get("is_server_asset"), "Playable maps must not be classified as server assets")
            self.assertEqual(c["name"], "ze_surf_happy_2_newbie_village_p")

    def test_delete_safeguard_blocks_server_assets(self):
        """Verify that delete_custom_maps refuses to delete Server Asset Packs."""
        fake_items = [
            {"id": "3793587501", "name": "GFL Server Assets", "path": r"E:\SteamLibrary\steamapps\workshop\content\730\3793587501", "is_server_asset": True, "size_bytes": 1000}
        ]
        count, freed, logs = custom_map_cleaner.delete_custom_maps(fake_items)
        self.assertEqual(count, 0, "Should NOT delete Server Asset Pack")
        self.assertEqual(freed, 0)
        self.assertTrue(any("BLOCKED" in l for l in logs))

if __name__ == "__main__":
    unittest.main()
