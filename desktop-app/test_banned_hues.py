"""
Automated Test: Approved Theme & Color Validation in Desktop App
Asserts that the user-approved tactical CS2 amber-orange (#E48716) is active,
and that old replaced greens (#43A857) or neon yellow/magenta do not regress.
"""

import unittest
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme
import _test_isolation  # noqa: E402,F401  (AUDIT: temp config, no registry; must come before app)
import app

BANNED_HEX_PATTERNS = [
    r'#FFE135', r'#FFF066', r'#FF2A85', r'#e879f9',
    r'#43A857', r'#52BC67', r'#368F49'
]

class TestApprovedThemePalette(unittest.TestCase):
    def test_theme_constants_use_approved_palette(self):
        """Verify theme.py constants use the user-approved CS2 amber-orange palette."""
        self.assertEqual(theme.COLOR_PRIMARY, "#E48716")
        self.assertEqual(theme.COLOR_PRIMARY_HOVER, "#F09527")
        self.assertEqual(theme.COLOR_PRIMARY_PRESSED, "#C5720E")
        self.assertEqual(theme.COLOR_TEXT_ON_PRIMARY, "#0A0E12")
        self.assertEqual(theme.COLOR_ACCENT, "#E48716")
        self.assertEqual(theme.COLOR_SUCCESS_PEPE, "#E48716")

    def test_app_py_source_no_old_green_or_neon_literals(self):
        """Scan app.py source code for old green or neon literals."""
        app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
        with open(app_path, "r", encoding="utf-8") as f:
            src = f.read()

        found = []
        for pat in BANNED_HEX_PATTERNS:
            matches = re.findall(pat, src, re.IGNORECASE)
            if matches:
                found.extend(matches)
        self.assertEqual(len(found), 0, f"Found old/unapproved color literals in app.py: {found}")

    def test_runtime_header_and_dashboard_colors(self):
        """Instantiate app headlessly and assert One-Click button & cards use approved amber-orange."""
        root = app.CS2TruePanoramaApp()
        root.withdraw()
        try:
            root.update_idletasks()
            self.assertEqual(app.ACCENT_ORANGE, theme.COLOR_PRIMARY)
            self.assertEqual(app.ACCENT_GREEN, theme.COLOR_PRIMARY)
            self.assertEqual(app.BG_WINDOW, theme.COLOR_BG)
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
