import os
import sys
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import custom_map_cleaner

class TestMapProtectionDummy(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="cs2_dummy_test_")
        self.workshop_dir = os.path.join(self.test_dir, "steamapps", "workshop", "content", "730")
        os.makedirs(self.workshop_dir, exist_ok=True)

        # 1. Create dummy GFL map folder (Workshop ID 3351648056)
        self.gfl_dir = os.path.join(self.workshop_dir, "3351648056")
        os.makedirs(self.gfl_dir, exist_ok=True)
        with open(os.path.join(self.gfl_dir, "ze_hell_p.vpk"), "wb") as f:
            f.write(b"VPK_DUMMY_DATA_GFL")

        # 2. Create dummy Possession map folder (3148016266)
        self.pse_dir = os.path.join(self.workshop_dir, "3148016266")
        os.makedirs(self.pse_dir, exist_ok=True)
        with open(os.path.join(self.pse_dir, "ze_alien_mountain_escape_p.vpk"), "wb") as f:
            f.write(b"VPK_DUMMY_DATA_PSE")

        # 3. Create dummy Server Asset Pack folder (3793587501)
        self.asset_dir = os.path.join(self.workshop_dir, "3793587501")
        os.makedirs(self.asset_dir, exist_ok=True)
        with open(os.path.join(self.asset_dir, "gfl_server_assets.vpk"), "wb") as f:
            f.write(b"VPK_DUMMY_DATA_ASSETS")

        # 4. Create dummy Temporary map folder (9999999999) - SAFE TO DELETE
        self.temp_dir = os.path.join(self.workshop_dir, "9999999999")
        os.makedirs(self.temp_dir, exist_ok=True)
        with open(os.path.join(self.temp_dir, "ze_temp_random_map.vpk"), "wb") as f:
            f.write(b"VPK_DUMMY_DATA_TEMP")

        # 5. Create dummy Official map
        self.official_vpk = os.path.join(self.test_dir, "de_dust2.vpk")
        with open(self.official_vpk, "wb") as f:
            f.write(b"VPK_DUMMY_DATA_OFFICIAL")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_protection_logic_blocks_protected_maps(self):
        """Verify that delete_custom_maps refuses to delete official maps and protected server assets."""
        items = [
            {
                "id": "3351648056",
                "name": "ze_hell_p",
                "path": self.gfl_dir,
                "is_subscribed": True,
                "is_protected": True,
                "is_server_asset": False,
                "size_bytes": 1024
            },
            {
                "id": "3793587501",
                "name": "gfl_server_assets",
                "path": self.asset_dir,
                "is_subscribed": True,
                "is_protected": True,
                "is_server_asset": True,
                "size_bytes": 1024
            },
            {
                "id": "de_dust2.vpk",
                "name": "de_dust2",
                "path": self.official_vpk,
                "is_subscribed": False,
                "is_protected": True,
                "is_server_asset": False,
                "size_bytes": 1024
            },
            {
                "id": "9999999999",
                "name": "ze_temp_random_map",
                "path": self.temp_dir,
                "is_subscribed": False,
                "is_protected": False,
                "is_server_asset": False,
                "size_bytes": 1024
            }
        ]

        deleted_count, freed_bytes, logs = custom_map_cleaner.delete_custom_maps(items)

        # Assert: Exactly 1 map was deleted (the unprotected temp map)
        self.assertEqual(deleted_count, 1)
        self.assertFalse(os.path.exists(self.temp_dir))

        # Assert: All protected items STILL EXIST
        self.assertTrue(os.path.exists(self.gfl_dir), "GFL collection map must NOT be deleted!")
        self.assertTrue(os.path.exists(self.asset_dir), "Server asset package must NOT be deleted!")
        self.assertTrue(os.path.exists(self.official_vpk), "Official Valve map must NOT be deleted!")

        print("\n[DUMMY TEST SUCCESS] 100% of protected maps/assets remained untouched!")
        for log in logs:
            print(f"  {log}")

if __name__ == "__main__":
    unittest.main()
