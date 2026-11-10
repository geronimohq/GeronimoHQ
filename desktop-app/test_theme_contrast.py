"""Contrast table for the retro theme. Every text token must reach 4.5:1 on every surface it can sit on
(owner rule 8); the accent only needs 3:1 because it is limited to large bold headings; filled buttons
need 4.5:1 for their label. Prints the full table (saved as audit evidence)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme

SURFACES = {"base": theme.SURFACE_BASE, "panel": theme.SURFACE_PANEL, "raised": theme.SURFACE_RAISED,
            "inset": theme.SURFACE_INSET}
BODY_TEXT = {"text-primary": theme.TEXT_PRIMARY, "text-secondary": theme.TEXT_SECONDARY,
             "ct-blue-text": theme.CT_BLUE_TEXT, "t-gold-text": theme.T_GOLD_TEXT, "good-text": theme.GOOD_TEXT,
             "warn-text": theme.WARN_TEXT, "bad-text": theme.BAD_TEXT}
FILLS = {  # (label color, fill)
    "text-on-accent / accent": (theme.TEXT_ON_ACCENT, theme.ACCENT),
    "text-on-accent / accent-hover": (theme.TEXT_ON_ACCENT, theme.ACCENT_HOVER),
    "text-on-accent / good": (theme.TEXT_ON_ACCENT, theme.GOOD),
    "text-on-dark-fill / bad": (theme.TEXT_ON_DARK_FILL, theme.BAD),
    "text-on-dark-fill / warn": (theme.TEXT_ON_DARK_FILL, theme.WARN),
    "text-on-dark-fill / bad hover": (theme.TEXT_ON_DARK_FILL, theme.lighten(theme.BAD, 1.06)),
}


class ThemeContrast(unittest.TestCase):
    def test_table(self):
        print("\nTEXT vs SURFACE (ratio)               " + "  ".join(f"{k:>7}" for k in SURFACES))
        failures = []
        for name, fg in BODY_TEXT.items():
            row = []
            for sname, bg in SURFACES.items():
                r = theme.contrast(fg, bg)
                row.append(f"{r:7.2f}")
                if r < 4.5:
                    failures.append(f"{name} on {sname}: {r:.2f}")
            print(f"{name:14} {fg}                  " + "  ".join(row))
        print("accent (headings only, bold >= 15 px, needs 3:1)")
        for sname in ("base", "panel", "inset"):
            r = theme.contrast(theme.ACCENT, SURFACES[sname])
            print(f"  accent {theme.ACCENT} on {sname}: {r:.2f}")
            if r < 3.0:
                failures.append(f"accent on {sname}: {r:.2f}")
        print("LABEL on FILL")
        for name, (fg, bg) in FILLS.items():
            r = theme.contrast(fg, bg)
            print(f"  {name:32} {r:.2f}")
            if r < 4.5:
                failures.append(f"{name}: {r:.2f}")
        # hover = +6 % lighter surface: every text token must still pass on it
        for sname in ("panel", "raised"):
            for name, fg in BODY_TEXT.items():
                r = theme.contrast(fg, theme.lighten(SURFACES[sname]))
                if r < 4.5:
                    failures.append(f"{name} on hovered {sname}: {r:.2f}")
        self.assertEqual(failures, [], "\n".join(failures))

    def test_disabled_text_is_exempt_but_still_dimmer_than_secondary(self):
        self.assertLess(theme.contrast(theme.TEXT_DISABLED, theme.SURFACE_PANEL),
                        theme.contrast(theme.TEXT_SECONDARY, theme.SURFACE_PANEL))

    def test_type_scale(self):
        self.assertEqual(theme.TYPE_SCALE, (8, 9, 10, 11, 14))   # 11 / 12 / 13 / 15 / 18 px at 96 DPI
        for old in (6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, -11, -12, -13, -14, -16):
            self.assertIn(theme.snap_size(old), theme.TYPE_SCALE)


if __name__ == "__main__":
    _res = unittest.main(exit=False, verbosity=2)
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(0 if _res.result.wasSuccessful() else 1)
