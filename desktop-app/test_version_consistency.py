"""
Automated Test: Version Consistency & Single Source of Truth
Verifies that version.py is the single source of truth across all components.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import version
import _test_isolation  # noqa: E402,F401  (AUDIT: temp config, no registry; must come before app)
import app

class TestVersionConsistency(unittest.TestCase):
    def test_version_constants_defined(self):
        """Verify version.py exports valid APP_VERSION and BUILD_DATE."""
        self.assertTrue(hasattr(version, "APP_VERSION"))
        self.assertTrue(hasattr(version, "BUILD_DATE"))
        self.assertEqual(version.APP_VERSION, "2.0.3")
        self.assertTrue(len(version.BUILD_DATE) >= 8)

    def test_diagnostics_includes_version(self):
        """Verify diagnostics output contains version from version.py."""
        root = app.CS2TruePanoramaApp()
        root.withdraw()
        try:
            diag = root.get_sanitized_diagnostics()
            self.assertIn(f"v{version.APP_VERSION}", diag)
            self.assertIn(f"({version.BUILD_DATE})", diag)
        finally:
            try:
                root.destroy()
            except Exception:
                pass

if __name__ == "__main__":
    # AUDIT: the app starts non-daemon threads (tray, GSI), so a plain unittest.main()
    # can hang after the tests finish. Exit with the real pass/fail code instead.
    _res = unittest.main(exit=False)
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(0 if _res.result.wasSuccessful() else 1)
