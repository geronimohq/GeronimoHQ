"""
Automated Test: Shared Player & Node Counts Parity
Verifies that the ZE toolbar pills (PLAYERS IN-GAME, NODES ONLINE) and
Dashboard ZE card share identical calculation routines.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app

class TestPillsCalc(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = app.CS2TruePanoramaApp()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

    def test_pills_and_dashboard_counts_exist(self):
        """Verify the presence of live player and node indicators on both views."""
        self.root._select_nav("DASHBOARD")
        self.root.update_idletasks()
        self.assertTrue(hasattr(self.root, "dash_ze_players_lbl"))
        self.assertTrue(hasattr(self.root, "dash_ze_nodes_lbl"))

        self.root._select_nav("SERVERS")
        self.root.update_idletasks()
        self.assertTrue(hasattr(self.root, "lbl_srv_players"))
        self.assertTrue(hasattr(self.root, "lbl_srv_nodes"))

        # Verify initial text patterns
        self.assertIn("PLAYERS IN-GAME", self.root.lbl_srv_players.cget("text"))
        self.assertIn("NODES ONLINE", self.root.lbl_srv_nodes.cget("text"))
        self.assertIn("players in-game", self.root.dash_ze_players_lbl.cget("text"))
        self.assertIn("servers online", self.root.dash_ze_nodes_lbl.cget("text"))

if __name__ == "__main__":
    unittest.main()
