"""
Unit Test: Token Parity & Contrast Validation
Verifies that desktop-app/theme.py and design-tokens.json share 100% identical color definitions,
and validates that all required contrast thresholds (4.5:1 body, 3:1 UI) are met.
"""

import unittest
import json
import os
import sys

# Add desktop-app to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "desktop-app"))
import theme

def relative_luminance(hex_color):
    """Calculate relative luminance for contrast ratio calculation (WCAG 2.1)."""
    hex_color = hex_color.lstrip('#')
    r, g, b = [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    
    def transform(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        
    R, G, B = transform(r), transform(g), transform(b)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B

def contrast_ratio(color1, color2):
    """Compute contrast ratio between two hex colors."""
    lum1 = relative_luminance(color1)
    lum2 = relative_luminance(color2)
    brightest = max(lum1, lum2)
    darkest = min(lum1, lum2)
    return (brightest + 0.05) / (darkest + 0.05)

class TestDesignTokenParity(unittest.TestCase):
    def setUp(self):
        token_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "design-tokens.json")
        with open(token_path, "r", encoding="utf-8") as f:
            self.tokens = json.load(f)
            
    def test_theme_color_parity(self):
        """The desktop app now has its own retro olive palette (owner request, 2026-11-10) while
        design-tokens.json stays the WEBSITE's token file. What both still share is the accent:
        the owner-approved CS2 orange and its hover / pressed shades."""
        colors = self.tokens["colors"]
        self.assertEqual(theme.ACCENT, colors["primary"])
        self.assertEqual(theme.ACCENT_HOVER, colors["primary_hover"])
        self.assertEqual(theme.ACCENT_PRESSED, colors["primary_pressed"])

    def test_contrast_ratios(self):
        """Verify that all text and UI elements meet minimum contrast thresholds."""
        colors = self.tokens["colors"]
        canvas = colors["canvas"]
        panel = colors["panel"]
        banana = colors["primary_banana"]
        
        # 1. Body text on canvas (> 4.5:1)
        ratio_primary = contrast_ratio(colors["text_primary"], canvas)
        self.assertGreaterEqual(ratio_primary, 4.5, f"White on canvas: {ratio_primary:.2f}:1")
        
        ratio_muted = contrast_ratio(colors["text_muted"], canvas)
        self.assertGreaterEqual(ratio_muted, 4.5, f"Muted on canvas: {ratio_muted:.2f}:1")
        
        # 2. Text on banana yellow: dark text must pass > 4.5:1
        ratio_dark_on_banana = contrast_ratio(colors["text_on_banana"], banana)
        self.assertGreaterEqual(ratio_dark_on_banana, 4.5, f"Dark text on banana: {ratio_dark_on_banana:.2f}:1")
        
        # 3. UI Accents on canvas (> 3:1)
        ratio_pepe = contrast_ratio(colors["success_pepe"], canvas)
        self.assertGreaterEqual(ratio_pepe, 3.0, f"Pepe green on canvas: {ratio_pepe:.2f}:1")
        
        ratio_magenta = contrast_ratio(colors["alert_magenta"], canvas)
        self.assertGreaterEqual(ratio_magenta, 3.0, f"Magenta on canvas: {ratio_magenta:.2f}:1")
        
        ratio_cyan = contrast_ratio(colors["telemetry_cyan"], canvas)
        self.assertGreaterEqual(ratio_cyan, 3.0, f"Cyan on canvas: {ratio_cyan:.2f}:1")

if __name__ == "__main__":
    unittest.main()
