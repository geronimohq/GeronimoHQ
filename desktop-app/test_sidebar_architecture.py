import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _test_isolation  # noqa: E402,F401  (AUDIT: temp config, no registry; must come before app)
import app

class TestSidebarArchitecture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = app.CS2TruePanoramaApp()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        try:
            # AUDIT: exit_application() ends with os._exit(0), which killed the test run
            # before unittest printed its result (failures were invisible, exit code 0).
            from unittest import mock
            with mock.patch.object(app.os, "_exit", lambda code=0: None):
                cls.root.exit_application()
        except Exception:
            pass

    def test_sidebar_initialization_and_dashboard(self):
        """Verify the app initializes with a sidebar containing the DASHBOARD module."""
        self.assertTrue(hasattr(self.root, "sidebar"))
        self.assertTrue(hasattr(self.root, "nav_items"))
        self.assertIn("DASHBOARD", self.root.nav_items)
        self.assertIn("SERVERS", self.root.nav_items)
        self.assertIn("ENGINE", self.root.nav_items)
        self.assertIn("AUTOEXEC", self.root.nav_items)

    def test_view_switching(self):
        """Verify switching between navigation views cleanly loads and renders."""
        self.root._select_nav("DASHBOARD")
        self.root.update_idletasks()
        self.assertEqual(self.root.current_page_key, "DASHBOARD")
        self.assertIn("DASHBOARD", self.root.pages)
        self.assertTrue(len(self.root.pages["DASHBOARD"].winfo_children()) > 0)

        # Switch to servers
        self.root._select_nav("SERVERS")
        self.root.update_idletasks()
        self.assertEqual(self.root.current_page_key, "SERVERS")
        self.assertIn("SERVERS", self.root.pages)

    def test_persistent_status_bar(self):
        """Verify persistent bottom status bar displays status indicators."""
        self.assertTrue(hasattr(self.root, "status_bar"))
        self.assertTrue(hasattr(self.root, "status_cs2_lbl"))
        self.assertTrue(hasattr(self.root, "status_sniper_lbl"))

if __name__ == "__main__":
    # AUDIT: the app starts non-daemon threads (tray, GSI), so a plain unittest.main()
    # can hang after the tests finish. Exit with the real pass/fail code instead.
    _res = unittest.main(exit=False)
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(0 if _res.result.wasSuccessful() else 1)
