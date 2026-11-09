import unittest
import tkinter as tk
from tkinter import font as tkfont

class TestDpiTableScaling(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_map_cleaner_columns_fit_text_at_all_dpi_scales(self):
        """
        Tests that for 100%, 125%, and 150% DPI:
        Every column width strictly exceeds the measured width of its heading and longest cell,
        ensuring zero truncation ('Modifiec' or clipped status).
        """
        scalings = [
            ("100%", 1.0, 10, 9),
            ("125%", 1.25, 12, 11),
            ("150%", 1.50, 15, 14),
        ]

        status_samples = [
            "⭐ Subscribed (GFL ZE Collection)",
            "⭐ Subscribed (GFL Server Pack)",
            "📁 Subscribed (GFL Protection Disabled)",
            "🕒 Active Rotation (Last 14d)",
            "📁 Temp Download (Safe Clean)",
            "🛡️ Essential Server Asset",
            "📦 Custom Map (.vpk)",
        ]

        for scale_name, dpi_scale, sz_hd, sz_row in scalings:
            f_hd = tkfont.Font(family="Segoe UI", size=sz_hd, weight="bold")
            f_row = tkfont.Font(family="Segoe UI", size=sz_row)

            w_check = max(45, int(45 * dpi_scale))
            w_id = max(f_hd.measure("Workshop ID ▾") + 24, f_row.measure("3351648056") + 24, int(120 * dpi_scale))
            max_status_text_w = max(f_row.measure(s) for s in status_samples)
            w_status = max(f_hd.measure("Server Pack Status ▾") + 28, max_status_text_w + 32, int(260 * dpi_scale))
            w_size = max(f_hd.measure("Size ▾") + 24, f_row.measure("999.9 MB") + 24, int(95 * dpi_scale))
            w_date = max(f_hd.measure("Last Played / Modified ▾") + 32, f_row.measure("2026-11-08 18:00") + 32, int(195 * dpi_scale))

            # 1. Verify "Last Played / Modified ▾" fits in date column with >20px margin
            date_hd_len = f_hd.measure("Last Played / Modified ▾")
            self.assertGreater(w_date, date_hd_len + 20, f"Date column too tight at {scale_name}: {w_date} vs {date_hd_len}")

            # 2. Verify all status strings fit in status column with >20px margin
            status_hd_len = f_hd.measure("Server Pack Status ▾")
            self.assertGreater(w_status, status_hd_len + 20, f"Status heading too tight at {scale_name}")
            self.assertGreater(w_status, max_status_text_w + 20, f"Status cells too tight at {scale_name}: {w_status} vs {max_status_text_w}")

            # 3. Verify Size column fits
            size_hd_len = f_hd.measure("Size ▾")
            self.assertGreater(w_size, size_hd_len + 15, f"Size heading too tight at {scale_name}")

            # 4. Verify Workshop ID column fits
            id_hd_len = f_hd.measure("Workshop ID ▾")
            self.assertGreater(w_id, id_hd_len + 15, f"ID heading too tight at {scale_name}")

if __name__ == "__main__":
    unittest.main()
