"""Retro (CS 1.6 / VGUI) skin: structural rules from the owner brief, checked on the real widget tree of
every page and dialog. Temp config, mocked network."""
import colorsys
import os
import re
import sys
import time
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _test_isolation  # noqa: E402,F401
import app  # noqa: E402
import retro_audit  # noqa: E402
import theme  # noqa: E402


class RetroSkin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = app.CS2TruePanoramaApp()
        cls.root.withdraw()

        def pump(s=0.3):
            end = time.time() + s
            while time.time() < end:
                cls.root.update(); time.sleep(0.02)
        cls.boxes = mock.patch.multiple(app.messagebox, showinfo=mock.DEFAULT, showwarning=mock.DEFAULT,
                                        showerror=mock.DEFAULT, askyesno=mock.DEFAULT)
        cls.boxes.start()
        cls.rows = retro_audit.collect(cls.root, pump)

    @classmethod
    def tearDownClass(cls):
        cls.boxes.stop()
        with mock.patch.object(app.os, "_exit", lambda code=0: None):
            cls.root.exit_application()

    def test_no_color_literals_outside_theme(self):
        bad = []
        for fn in os.listdir(HERE):
            # make_cs2_badge.py is a stand-alone icon generator (not imported by the app, not in the exe)
            if fn.endswith(".py") and not fn.startswith(("test_", "_test")) and fn not in ("theme.py", "retro_audit.py", "make_cs2_badge.py", "web_main.py"):
                with open(os.path.join(HERE, fn), encoding="utf-8") as fh:
                    for n, line in enumerate(fh, 1):
                        if re.search(r"""["']#[0-9A-Fa-f]{6}["']""", line):
                            bad.append(f"{fn}:{n}")
        self.assertEqual(bad, [], bad[:10])

    def test_every_text_widget_is_readable_and_accent_is_for_headings_only(self):
        v = retro_audit.violations(self.rows)
        msgs = []
        for kind, items in v.items():
            for it in items[:8]:
                r = it[1] if isinstance(it, tuple) else it
                msgs.append(f"{kind}: {r['where']} {r['cls']} fg {r['fg']} bg {r['bg']} {r['px']}px '{r['text']}'")
        print(f"\n[skin] {len(self.rows)} widgets checked on {len(set(r['where'] for r in self.rows))} pages/dialogs")
        self.assertEqual(msgs, [], "\n".join(msgs))

    def test_one_primary_button_per_screen(self):
        prim = retro_audit.primary_buttons(self.rows)
        print("\n[skin] primary (accent-filled) button per screen:", {k: v for k, v in prim.items()})
        for where, buttons in prim.items():
            self.assertLessEqual(len(buttons), 1, f"{where}: {buttons}")

    def test_only_one_red_surface_style(self):
        reds = [r for r in self.rows if r["cls"] == "Button" and r["bg"] in (theme.BAD.upper(), theme.WARN.upper())]
        self.assertTrue(all("DELETE" in r["text"].upper() for r in reds), [r["text"] for r in reds])

    def test_no_yellow_or_neon_on_any_widget(self):
        for r in self.rows:
            for col in (r["fg"], r["bg"]):
                if not col or col.upper() == theme.ACCENT.upper():
                    continue
                rr, gg, bb = (int(col[i:i + 2], 16) / 255 for i in (1, 3, 5))
                h, s, val = colorsys.rgb_to_hsv(rr, gg, bb)
                self.assertFalse(48 <= h * 360 <= 70 and s > 0.35 and val > 0.5, f"yellow {col} in {r['where']} '{r['text']}'")

    def test_fonts_and_type_scale(self):
        allowed_family = {theme.FONT_UI, theme.FONT_MONO, "Segoe UI Emoji", "Segoe UI Symbol"}
        sizes, families = set(), set()
        for r in self.rows:
            if any(ch.isalnum() for ch in r["text"]):
                families.add(r["family"]); sizes.add(r["pt"])
        print("\n[skin] font families in use:", sorted(families), "| point sizes:", sorted(sizes))
        # real text uses Verdana (or the Tk fallback for glyphs it lacks) and Consolas
        self.assertIn(theme.FONT_UI, families)
        self.assertTrue(sizes <= set(theme.TYPE_SCALE) | {7, 12, 13, 15, 16, 18, 20, 24}, sizes)

    def test_buttons_have_bevels_and_fields_are_inset(self):
        buttons = [r for r in self.rows if r["cls"] == "Button"]
        self.assertGreater(len(buttons), 20)
        self.assertTrue(all(b["relief"] in ("raised", "sunken") for b in buttons), [b["text"] for b in buttons if b["relief"] not in ("raised", "sunken")][:5])
        entries = [r for r in self.rows if r["cls"] == "Entry"]
        self.assertTrue(entries)
        self.assertTrue(all(e["relief"] == "sunken" and e["bg"] == theme.SURFACE_INSET.upper() for e in entries))

    def test_log_is_monospace_inset_with_colored_parts(self):
        con = self.root.console
        self.assertEqual(str(con.cget("relief")), "sunken")
        self.root.log("[SERVERS] hello")
        self.root.log("[SYSTEM] Could not read file")
        self.root.update()
        self.assertEqual(con.tag_cget("log_tag", "foreground").upper(), theme.CT_BLUE_TEXT.upper())
        self.assertEqual(con.tag_cget("log_err", "foreground").upper(), theme.BAD_TEXT.upper())
        self.assertEqual(con.tag_cget("log_ts", "foreground").upper(), theme.TEXT_SECONDARY.upper())

    def test_settings_text_not_clipped_wording(self):
        with open(os.path.join(HERE, "app.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertIn("Clicking [-] hides the window to the tray; clicking [X] closes the application completely.", src)


if __name__ == "__main__":
    _res = unittest.main(exit=False, verbosity=2)
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(0 if _res.result.wasSuccessful() else 1)
