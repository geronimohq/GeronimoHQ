"""
Automated Test: Version Consistency & Single Source of Truth
Verifies that version.py is the single source of truth across all components.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import version
import app

class TestVersionConsistency(unittest.TestCase):
    def test_version_constants_defined(self):
        """Verify version.py exports valid APP_VERSION and BUILD_DATE."""
        self.assertTrue(hasattr(version, "APP_VERSION"))
        self.assertTrue(hasattr(version, "BUILD_DATE"))
        self.assertEqual(version.APP_VERSION, "1.5.0")
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
    unittest.main()
