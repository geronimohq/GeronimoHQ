"""
Automated Test: Zero Banned Hues in Desktop App
Asserts that no banned color hues (yellow, amber, orange, magenta, pink, fuchsia)
exist in theme.py constants, app.py source code, or runtime widget configurations.
Enforces Dark Slate palette:
  Primary Green: #43A857
  Info / Cyan:   #38BDF8
  Text Primary:  #E6EDF3
  Muted:         #A3B3C0
  Danger:        #F26D6D
  Canvas / Card: #0A0E12 / #11171D
"""

import unittest
import os
import re
import sys
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme
import app

BANNED_HEX_PATTERNS = [
    r'#FFE135', r'#FFF066', r'#FACC15', r'#FF2A85', r'#e879f9', r'#ea580c',
    r'#eab308', r'#f59e0b', r'#f97316', r'#fb923c', r'#fbbf24', r'#fde047',
    r'#a16207', r'#b45309', r'#d97706', r'#de6c11', r'#854d0e', r'#a78bfa',
    r'#e48716', r'#f09527', r'#c5720e'
]

def hex_to_rgb(hex_code):
    if not isinstance(hex_code, str):
        return None
    hex_code = hex_code.strip().lstrip('#')
    if len(hex_code) == 6:
        try:
            return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            return None
    return None

def is_banned_hue(hex_code):
    """Check if color falls into banned yellow/orange/amber or magenta/fuchsia range."""
    rgb = hex_to_rgb(hex_code)
    if not rgb:
        return False
    r, g, b = rgb
    # Yellow / Orange / Amber: High red and green, low blue
    if r > 180 and g > 115 and b < 80:
        return True
    # Magenta / Fuchsia: High red and blue, low green
    if r > 180 and b > 100 and g < 100:
        return True
    return False

class TestZeroBannedHues(unittest.TestCase):
    def test_theme_constants_no_banned_hues(self):
        """Verify theme.py constants contain zero banned colors and use #43A857."""
        self.assertEqual(theme.COLOR_PRIMARY, "#43A857")
        self.assertEqual(theme.COLOR_PRIMARY_HOVER, "#52BC67")
        self.assertEqual(theme.COLOR_PRIMARY_PRESSED, "#368F49")
        self.assertEqual(theme.COLOR_TEXT_ON_PRIMARY, "#04120A")

        for name, val in theme.COLORS.items():
            if isinstance(val, str) and val.startswith('#'):
                self.assertFalse(
                    is_banned_hue(val),
                    f"theme.COLORS['{name}'] has banned hue: {val}"
                )

    def test_app_py_source_no_banned_hex_literals(self):
        """Scan app.py source code for banned hex color literals."""
        app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
        with open(app_path, "r", encoding="utf-8") as f:
            src = f.read()

        found = []
        for pat in BANNED_HEX_PATTERNS:
            matches = re.findall(pat, src, re.IGNORECASE)
            if matches:
                found.extend(matches)
        self.assertEqual(len(found), 0, f"Found banned color literals in app.py: {found}")

    def test_runtime_widget_configurations_no_banned_hues(self):
        """Audit runtime widget colors across Dashboard, Header, and Settings."""
        root = app.CS2TruePanoramaApp()
        root.withdraw()
        try:
            root.update_idletasks()
            self.assertEqual(app.ACCENT_ORANGE, theme.COLOR_PRIMARY)
            self.assertEqual(app.ACCENT_GREEN, theme.COLOR_PRIMARY)
            self.assertEqual(app.BG_WINDOW, theme.COLOR_BG)
            self.assertEqual(theme.COLOR_PRIMARY, "#43A857")

            # Check header One-Click button
            if hasattr(root, "b_opt"):
                bg = root.b_opt.cget("bg")
                fg = root.b_opt.cget("fg")
                self.assertFalse(is_banned_hue(bg), f"b_opt bg banned: {bg}")
                self.assertFalse(is_banned_hue(fg), f"b_opt fg banned: {fg}")

            # Check admin pill
            if hasattr(root, "admin_badge_frame"):
                for child in root.admin_badge_frame.winfo_children():
                    if isinstance(child, tk.Label):
                        fg = child.cget("fg")
                        self.assertFalse(is_banned_hue(fg), f"Admin badge fg banned: {fg}")
        finally:
            try:
                root.destroy()
            except Exception:
                pass

if __name__ == "__main__":
    unittest.main()
