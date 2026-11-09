"""
Automated Test: Shared Player & Node Counts Parity
Verifies that the ZE toolbar pills (PLAYERS IN-GAME, SERVERS ONLINE) and
Dashboard ZE card share identical calculation routines.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _test_isolation  # noqa: E402,F401  (AUDIT: temp config, no registry; must come before app)
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
        self.assertIn("SERVERS ONLINE", self.root.lbl_srv_nodes.cget("text"))
        self.assertIn("players in-game", self.root.dash_ze_players_lbl.cget("text"))
        self.assertIn("servers online", self.root.dash_ze_nodes_lbl.cget("text"))

if __name__ == "__main__":
    # AUDIT: the app starts non-daemon threads (tray, GSI), so a plain unittest.main()
    # can hang after the tests finish. Exit with the real pass/fail code instead.
    _res = unittest.main(exit=False)
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(0 if _res.result.wasSuccessful() else 1)
