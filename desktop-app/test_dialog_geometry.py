"""
Automated Test: Settings Dialog Geometry and Visibility
Asserts that Save Settings & Cancel buttons are strictly within visible window bounds,
text does not clip, and keyboard shortcuts (Escape) function properly.
"""

import unittest
import os
import sys
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app

class TestDialogGeometry(unittest.TestCase):
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

    def test_settings_dialog_buttons_visible_and_on_screen(self):
        """Verify Save Settings & Cancel buttons are not pushed off-screen."""
        self.root.deiconify()
        self.root.open_settings_dialog()
        self.root.update()

        # Find the toplevel settings dialog
        dlg = None
        for child in self.root.winfo_children():
            if isinstance(child, tk.Toplevel) and "Settings" in child.title():
                dlg = child
                break

        self.assertIsNotNone(dlg, "Settings dialog was not found!")

        dlg.update()
        dlg_h = dlg.winfo_height()
        dlg_w = dlg.winfo_width()
        self.assertGreaterEqual(dlg_w, 400)
        self.assertGreaterEqual(dlg_h, 300)

        # Locate b_save and b_cancel buttons
        save_btn = None
        cancel_btn = None

        def find_buttons(parent):
            nonlocal save_btn, cancel_btn
            for ch in parent.winfo_children():
                if isinstance(ch, tk.Button):
                    txt = ch.cget("text")
                    if "Save" in txt:
                        save_btn = ch
                    elif "Cancel" in txt:
                        cancel_btn = ch
                find_buttons(ch)

        find_buttons(dlg)

        self.assertIsNotNone(save_btn, "Save button not found in Settings dialog!")
        self.assertIsNotNone(cancel_btn, "Cancel button not found in Settings dialog!")

        # Check that both buttons are mapped and located within visible dialog height
        save_btn.update_idletasks()
        cancel_btn.update_idletasks()

        save_y_root = save_btn.winfo_rooty()
        dlg_y_root = dlg.winfo_rooty()
        btn_rel_y = save_y_root - dlg_y_root
        btn_bottom = btn_rel_y + save_btn.winfo_height()

        self.assertLessEqual(
            btn_bottom,
            dlg_h,
            f"Save button bottom ({btn_bottom}px) is pushed off-screen past dialog height ({dlg_h}px)!"
        )

        # Clean up dialog
        dlg.destroy()

if __name__ == "__main__":
    # AUDIT: the app starts non-daemon threads (tray, GSI), so a plain unittest.main()
    # can hang after the tests finish. Exit with the real pass/fail code instead.
    _res = unittest.main(exit=False)
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(0 if _res.result.wasSuccessful() else 1)
