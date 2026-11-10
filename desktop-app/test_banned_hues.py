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
        """Retro skin: the owner-approved CS2 orange is the ONE accent; surfaces are muted olive."""
        self.assertEqual(theme.ACCENT, "#E48716")
        self.assertEqual(theme.ACCENT_HOVER, "#F09527")
        self.assertEqual(theme.ACCENT_PRESSED, "#C5720E")
        self.assertEqual(theme.COLOR_PRIMARY, theme.ACCENT)
        self.assertEqual(theme.TEXT_ON_ACCENT, "#14170F")
        for name, val in (("SURFACE_BASE", "#1C2119"), ("SURFACE_PANEL", "#262D22"), ("SURFACE_INSET", "#12160F"),
                          ("BEVEL_LIGHT", "#596652"), ("BEVEL_DARK", "#0C0E0A"), ("TEXT_PRIMARY", "#D5DACF"),
                          ("GOOD", "#5FA84C"), ("BAD", "#B8433A"), ("CT_BLUE", "#4F86B8"), ("T_GOLD", "#A8863F")):
            self.assertEqual(getattr(theme, name), val, name)
        # status is never the accent
        self.assertNotEqual(theme.COLOR_SUCCESS_PEPE, theme.ACCENT)
        self.assertNotEqual(theme.COLOR_SUCCESS, theme.ACCENT)

    def test_no_yellow_or_neon_in_theme(self):
        """No yellow / bright amber and no color above ~70 % saturation among the surface, text and status tokens."""
        import colorsys
        tokens = {n: getattr(theme, n) for n in dir(theme) if n.isupper() and isinstance(getattr(theme, n), str)
                  and re.fullmatch(r"#[0-9A-Fa-f]{6}", getattr(theme, n))}
        for name, hexv in tokens.items():
            r, g, b = (int(hexv[i:i + 2], 16) / 255 for i in (1, 3, 5))
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            hue = h * 360
            if name.startswith(("ACCENT", "COLOR_PRIMARY", "COLOR_ACCENT", "COLOR_FOCUS", "COLOR_TEXT_ON")):
                continue   # the approved orange (hue ~34, saturation ~87 %) is the single exception
            self.assertFalse(48 <= hue <= 70 and s > 0.35 and v > 0.5, f"{name} {hexv} looks yellow")
            self.assertLessEqual(s, 0.72, f"{name} {hexv} is too saturated for the muted palette")

    def test_app_py_source_no_old_green_or_neon_literals(self):
        """Scan app.py source code for old green or neon literals."""
        app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
        with open(app_path, "r", encoding="utf-8") as f:
            src = f.read()

        found = re.findall(r"""["']#[0-9A-Fa-f]{6}["']""", src)   # no color literal may live in app.py at all
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
            self.assertEqual(app.ACCENT_GREEN, theme.GOOD_TEXT)       # status text is green, never orange
            self.assertNotEqual(app.ACCENT_GREEN, app.ACCENT_ORANGE)
            self.assertEqual(app.BG_WINDOW, theme.SURFACE_BASE)
            self.assertEqual(app.BG_CONSOLE, theme.SURFACE_INSET)
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
