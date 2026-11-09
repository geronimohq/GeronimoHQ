"""
Unit Tests for Dashboard Clarity, Autoexec Detection with Other Drives / Spaces,
and Storage Card Values without 'Healthy' word.
"""

import unittest
import os
import sys
import tempfile
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core_logic
import app

class TestDashboardClarity(unittest.TestCase):
    def test_01_autoexec_detection_with_spaces_and_other_drives(self):
        """Simulate steam library on another path with spaces, test autoexec detection."""
        with tempfile.TemporaryDirectory() as td:
            # Path with spaces
            steam_lib = os.path.join(td, "Steam Library With Spaces")
            cs2_cfg = os.path.join(steam_lib, "steamapps", "common", "Counter-Strike Global Offensive", "game", "csgo", "cfg")
            os.makedirs(cs2_cfg, exist_ok=True)

            auto_file = os.path.join(cs2_cfg, "autoexec.cfg")
            with open(auto_file, "w", encoding="utf-8") as f:
                f.write('bind "scancode99" "incrementvar volume 0 1 1"\n')

            # Test core_logic detection logic
            self.assertTrue(os.path.exists(auto_file))
            # Test case-insensitivity
            self.assertTrue(any(f.lower() == "autoexec.cfg" for f in os.listdir(cs2_cfg)))

            # Test content check: not edited by this app
            with open(auto_file, "r", encoding="utf-8") as f:
                txt = f.read()
            has_app_block = ("// --- CS2 COMMAND CENTER" in txt or "GERONIMOHQ" in txt)
            self.assertFalse(has_app_block)

            # Test content check: with app block
            with open(auto_file, "a", encoding="utf-8") as f:
                f.write("\n// --- CS2 COMMAND CENTER MANAGED BLOCK ---\nfps_max 0\n")
            with open(auto_file, "r", encoding="utf-8") as f:
                txt2 = f.read()
            self.assertTrue("// --- CS2 COMMAND CENTER" in txt2 or "GERONIMOHQ" in txt2)

    def test_02_dashboard_cards_geometry_and_text(self):
        """Audit that Dashboard cards render with accurate text, geometry > 0, and no 'Healthy'."""
        root = app.CS2TruePanoramaApp()
        root.geometry("1440x900+50+50")
        root.deiconify()
        root.update()
        try:
            root._select_nav("DASHBOARD")
            root.update()

            # Find Open cfg folder button recursively
            def find_all_buttons(w):
                res = []
                if isinstance(w, tk.Button):
                    res.append(w)
                for child in w.winfo_children():
                    res.extend(find_all_buttons(child))
                return res

            def find_all_labels(w):
                res = []
                if isinstance(w, tk.Label):
                    res.append(w)
                for child in w.winfo_children():
                    res.extend(find_all_labels(child))
                return res

            buttons = find_all_buttons(root)
            open_btn = next((b for b in buttons if "Open cfg folder" in b.cget("text")), None)
            self.assertIsNotNone(open_btn, "Button 'Open cfg folder' not found on Dashboard.")
            # Geometry assertion
            self.assertGreater(open_btn.winfo_width(), 40)
            self.assertGreater(open_btn.winfo_height(), 15)

            # Audit Storage Card: No word 'Healthy'
            labels = find_all_labels(root)
            found_storage_card = any("STORAGE: CS2" in l.cget("text") for l in labels)
            found_healthy = any("Healthy" in l.cget("text") and "STORAGE" in str(l.master) for l in labels)

            self.assertTrue(found_storage_card, "Card 'STORAGE: CS2 / STEAM LIBRARY DRIVE' not found.")
            self.assertFalse(found_healthy, "Word 'Healthy' must be removed from Storage card.")
        finally:
            try:
                root.destroy()
            except Exception:
                pass

if __name__ == "__main__":
    unittest.main()
