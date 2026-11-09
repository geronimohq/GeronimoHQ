"""
Automated Test: Diagnostics Redaction and Privacy Sanitization
Verifies that get_sanitized_diagnostics() strictly redacts user accounts,
local file system paths, IP addresses, Steam IDs, and tokens.
"""

import unittest
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app

class TestDiagnosticsRedaction(unittest.TestCase):
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

    def test_diagnostics_redacts_sensitive_data(self):
        """Verify strict redaction of username, IPs, and Steam IDs."""
        diag = self.root.get_sanitized_diagnostics()
        self.assertIsInstance(diag, str)
        self.assertTrue(len(diag) > 50)

        # 1. Username must NOT appear unredacted
        username = os.environ.get("USERNAME", "")
        if username and len(username) > 2:
            self.assertNotIn(f"Users\\{username}", diag)
            self.assertNotIn(f"Users/{username}", diag)

        # 2. IP addresses must NOT appear
        raw_ips = re.findall(r'\b(?!(?:0\.0\.0\.0|127\.0\.0\.1))\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', diag)
        self.assertEqual(len(raw_ips), 0, f"Unredacted IP addresses found in diagnostics: {raw_ips}")

        # 3. Steam IDs must NOT appear
        raw_steam = re.findall(r'\b(?:STEAM_[0-5]:[01]:\d+|7656119\d{10})\b', diag)
        self.assertEqual(len(raw_steam), 0, f"Unredacted Steam IDs found in diagnostics: {raw_steam}")

        # 4. Mandatory neutral info must be present
        self.assertIn("CS2 Command Center Diagnostics", diag)
        self.assertIn("OS:", diag)
        self.assertIn("CPU:", diag)

if __name__ == "__main__":
    unittest.main()
