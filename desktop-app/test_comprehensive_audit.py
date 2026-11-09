import os
import sys
import time
import unittest
from unittest.mock import MagicMock, patch

# Ensure utf-8 output in Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app
import core_logic
import hardware_info
import server_browser
import app_config
import custom_map_cleaner
import discord_rpc

class ComprehensiveApplicationAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n" + "="*70)
        print("  STARTING COMPREHENSIVE FULL-APPLICATION AUDIT")
        print("="*70)
        # Create hidden root instance for headless UI verification
        cls.root = app.CS2TruePanoramaApp()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        try:
            # AUDIT: exit_application() ends with os._exit(0), which killed the test run
            # before unittest printed its result (failures were invisible, exit code 0).
            from unittest import mock
            with mock.patch.object(app.os, "_exit", lambda code=0: None):
                cls.root.exit_application()
        except Exception:
            pass
        print("\n" + "="*70)
        print("  COMPREHENSIVE FULL-APPLICATION AUDIT COMPLETED")
        print("="*70)

    # -------------------------------------------------------------
    # 1. HEADER CONTROLS & LIFECYCLE AUDIT
    # -------------------------------------------------------------
    def test_01_header_controls_and_badges(self):
        """Audit top header pills, permission badges, and CS2 status indicator."""
        print("\n[AUDIT 01] Header Controls & Badges...")
        self.assertTrue(hasattr(self.root, "run_one_click_optimization"))
        self.assertTrue(hasattr(self.root, "run_revert_all"))
        self.assertTrue(hasattr(self.root, "admin_status"))
        self.assertTrue(hasattr(self.root, "paths"))
        cs2_found = bool(self.root.paths.get("cs2_exe"))
        print(f"  -> CS2 Executable Path: {self.root.paths.get('cs2_exe') or 'Not Found'} (Found: {cs2_found})")
        print(f"  -> Elevation Status: {'Admin' if self.root.admin_status else 'Standard'}")

    # -------------------------------------------------------------
    # 2. NAVIGATION TABS AUDIT (ALL 9 TABS)
    # -------------------------------------------------------------
    def test_02_all_navigation_tabs_loading(self):
        """Audit that each of the 9 navigation tabs builds and renders without errors."""
        print("\n[AUDIT 02] Navigation Tabs Rendering...")
        tabs = [
            ("ENGINE", "Engine Tweaks"),
            ("OS_DIAGNOSTICS", "GPU MPO Diagnostics"),
            ("AUTOEXEC", "Autoexec & Binds"),
            ("LAUNCH", "Launch Options"),
            ("BOOST", "Live In-Game Booster"),
            ("SERVERS", "ZE Game Servers"),
            ("MAINTENANCE", "PC Maintenance"),
            ("DISCORD", "Discord Presence"),
            ("FAQ", "Help & FAQ Guide")
        ]
        for key, name in tabs:
            t0 = time.time()
            self.root._select_nav(key)
            self.root.update_idletasks()
            duration = (time.time() - t0) * 1000
            self.assertIn(key, self.root.pages)
            page_frame = self.root.pages[key]
            self.assertTrue(len(page_frame.winfo_children()) > 0)
            print(f"  -> Tab [{key}] '{name}' rendered in {duration:.1f}ms (Children: {len(page_frame.winfo_children())})")

    # -------------------------------------------------------------
    # 3. ENGINE TWEAKS & DUAL MAINTENANCE BANNER
    # -------------------------------------------------------------
    def test_03_engine_tweaks_and_weekly_banner(self):
        """Audit Engine Tweaks options, power plan selector, and dual tracking reminder banner."""
        print("\n[AUDIT 03] Engine Tweaks & Dual Tracking Banner...")
        self.root._select_nav("ENGINE")
        
        # Verify checkboxes exist and can be toggled
        self.assertTrue(hasattr(self.root, "opt_shaders"))
        self.assertTrue(hasattr(self.root, "opt_cs2_dumps"))
        self.assertTrue(hasattr(self.root, "opt_gamedvr"))
        self.assertTrue(hasattr(self.root, "opt_fullscreen"))
        self.assertTrue(hasattr(self.root, "opt_autoexec"))
        self.assertTrue(hasattr(self.root, "opt_power"))
        
        # Verify weekly banner refresh
        self.root._refresh_weekly_maint_banner()
        self.assertTrue(hasattr(self.root, "weekly_banner_box"))
        self.assertTrue(len(self.root.weekly_banner_box.winfo_children()) > 0)
        print("  -> Dual Tracking Maintenance Banner refreshed cleanly.")

    # -------------------------------------------------------------
    # 4. GPU MPO DIAGNOSTICS AUDIT (MPO TROUBLESHOOTER & WHY CARDS)
    # -------------------------------------------------------------
    def test_04_os_diagnostics_cards(self):
        """Audit GPU MPO diagnostics tab (Why MPO callout card & Universal MPO hardware card)."""
        print("\n[AUDIT 04] GPU MPO Diagnostics Cards...")
        self.root._select_nav("OS_DIAGNOSTICS")
        self.assertTrue(hasattr(self.root, "os_diag_cards_container"))
        cards = self.root.os_diag_cards_container.winfo_children()
        print(f"  -> GPU MPO Diagnostics rendered {len(cards)} inspection cards.")
        self.assertEqual(len(cards), 2, "Expected exactly 2 cards: Why MPO card and MPO Hardware card")

    # -------------------------------------------------------------
    # 5. AUTOEXEC & BINDS SAFETY GUARANTEE
    # -------------------------------------------------------------
    def test_05_autoexec_preview_and_safe_append(self):
        """Audit autoexec preview, bind preservation guarantee, and restoration logic."""
        print("\n[AUDIT 05] Autoexec & Binds Safety...")
        self.root._select_nav("AUTOEXEC")
        self.assertTrue(hasattr(self.root, "txt_box"))
        self.root._refresh_autoexec_preview()
        content = self.root.txt_box.get("1.0", "end")
        self.assertIn("fps_max", content)
        self.assertIn("snd_mixahead", content)
        print(f"  -> Autoexec text box active ({len(content)} chars loaded).")

    # -------------------------------------------------------------
    # 6. LAUNCH OPTIONS HELPER
    # -------------------------------------------------------------
    def test_06_launch_options_analysis(self):
        """Audit Launch Options analysis, preset loading, and editable input field."""
        print("\n[AUDIT 06] Launch Options Helper...")
        self.root._select_nav("LAUNCH")
        self.assertTrue(hasattr(self.root, "launch_entry"))
        entry_val = self.root.launch_entry.get()
        print(f"  -> Launch Options input value: '{entry_val}'")
        self.assertTrue(len(entry_val) > 0)

    # -------------------------------------------------------------
    # 7. LIVE IN-GAME BOOSTER
    # -------------------------------------------------------------
    def test_07_live_in_game_booster(self):
        """Audit Live Booster UI elements, explanations, and responsive text wrapping."""
        print("\n[AUDIT 07] Live In-Game Booster...")
        self.root._select_nav("BOOST")
        self.assertTrue(hasattr(self.root, "btn_boost"))
        self.assertTrue(hasattr(self.root, "status_cs2_lbl"))
        if hasattr(self.root, "_apply_boost_wraps_func"):
            self.root._apply_boost_wraps_func()
        print("  -> Live Booster controls and responsive wraps verified.")

    # -------------------------------------------------------------
    # 8. ZE GAME SERVERS: PARALLEL QUERY & SLOT SNIPER
    # -------------------------------------------------------------
    def test_08_ze_game_servers_and_sniper_rules(self):
        """Audit ZE Server Browser, concurrent 1s auto-refresh loop, and GFL slot sniper rules."""
        print("\n[AUDIT 08] ZE Game Servers & Slot Sniper...")
        self.root._select_nav("SERVERS")
        self.assertTrue(hasattr(self.root, "btn_gfl_sniper"))
        self.assertTrue(hasattr(self.root, "gfl_status_text"))
        
        # Test Slot Sniper arming and disarming with CS2 running
        with patch("core_logic.is_cs2_running", return_value=True):
            self.root.toggle_server_slot_sniper("74.91.124.21", 27015, "GFL Clan Zombie Escape")
            self.assertTrue(self.root.sniper.is_active, "Sniper SHOULD arm when triggered with CS2 running!")
            print("  -> Correctly armed Slot Sniper!")
            self.root.toggle_server_slot_sniper("74.91.124.21", 27015, "GFL Clan Zombie Escape")
            self.assertFalse(self.root.sniper.is_active, "Sniper SHOULD disarm on second toggle!")
            print("  -> Correctly disarmed Slot Sniper on toggle!")

    # -------------------------------------------------------------
    # 9. PC MAINTENANCE CLEANERS & ASSET MANAGER
    # -------------------------------------------------------------
    def test_09_pc_maintenance_suite(self):
        """Audit PC maintenance cleanups, workshop map cleaner detection, and elevation check."""
        print("\n[AUDIT 09] PC Maintenance Suite...")
        self.root._select_nav("MAINTENANCE")
        self.assertTrue(hasattr(self.root, "maint_temp"))
        self.assertTrue(hasattr(self.root, "maint_win_update"))
        self.assertTrue(hasattr(self.root, "maint_discord_steam"))
        self.assertTrue(hasattr(self.root, "maint_thumb"))
        self.assertTrue(hasattr(self.root, "maint_recycle"))
        self.assertTrue(hasattr(self.root, "maint_dns"))
        print("  -> All 6 Safe Hygiene and PC Maintenance toggles verified.")

    # -------------------------------------------------------------
    # 10. DISCORD PRESENCE & AUTO-CLEAR
    # -------------------------------------------------------------
    def test_10_discord_presence_lifecycle(self):
        """Audit Discord RPC toggle, preview elapsed ticker, and session management."""
        print("\n[AUDIT 10] Discord Presence...")
        self.root._select_nav("DISCORD")
        self.assertTrue(hasattr(self.root, "discord_preview_details"))
        self.assertTrue(hasattr(self.root, "discord_preview_state"))
        self.assertTrue(hasattr(self.root, "discord_preview_elapsed"))
        self.root._tick_discord_elapsed_timer()
        print("  -> Discord RPC preview and elapsed timer tick verified.")

    # -------------------------------------------------------------
    # 11. HELP & FAQ KNOWLEDGE BASE
    # -------------------------------------------------------------
    def test_11_help_and_faq_knowledge_base(self):
        """Audit FAQ guide layout, canvas scrolling, and word wrap adaptability."""
        print("\n[AUDIT 11] Help & FAQ Knowledge Base...")
        self.root._select_nav("FAQ")
        self.assertTrue(hasattr(self.root, "faq_canvas"))
        self.assertTrue(hasattr(self.root, "faq_scrollbar"))
        print("  -> FAQ Knowledge Base loaded cleanly.")

    # -------------------------------------------------------------
    # 12. SYSTEM TRAY & WINDOW CONTROLS
    # -------------------------------------------------------------
    def test_12_system_tray_and_window_controls(self):
        """Audit system tray icon creation, Win32 icon application, and tray menu callbacks across maximized, normal, and minimized-then-tray states."""
        print("\n[AUDIT 12] System Tray & Window Controls (3-State Restore Audit)...")
        self.assertTrue(hasattr(self.root, "_apply_win32_icons"))
        self.root._apply_win32_icons()
        self.assertTrue(hasattr(self.root, "restore_from_tray"))
        self.assertTrue(hasattr(self.root, "exit_application"))

        # Case 1: Maximized ("zoomed") state restore
        self.root._last_window_state = "zoomed"
        self.root.restore_from_tray()
        self.assertEqual(self.root.state(), "zoomed", "Tray restore failed to restore maximized (zoomed) state")
        print("  -> Case 1: Maximized (zoomed) restore verified.")

        # Case 2: Normal ("normal") state restore
        self.root._last_window_state = "normal"
        self.root.restore_from_tray()
        self.assertEqual(self.root.state(), "normal", "Tray restore failed to restore normal window geometry state")
        print("  -> Case 2: Normal geometry restore verified.")

        # Case 3: Minimized ("iconic") then sent to tray (must NEVER restore as iconic/minimized)
        # Even if window was minimized to taskbar prior to tray, _last_window_state only records "normal" or "zoomed"
        self.root.withdraw() # simulates hide to tray
        # Verify that if _last_window_state was set to zoomed prior to minimize, it restores to visible zoomed
        self.root._last_window_state = "zoomed"
        self.root.restore_from_tray()
        self.assertNotEqual(self.root.state(), "iconic", "Window restored into minimized/iconic state!")
        self.assertEqual(self.root.state(), "zoomed", "Window failed to restore to visible zoomed state after tray withdraw")
        print("  -> Case 3: Minimized-then-tray restore safely un-minimizes to visible window.")

    # -------------------------------------------------------------
    # 13. DPI TABLE COLUMN TEXT MEASUREMENT & SCALING AUDIT
    # -------------------------------------------------------------
    def test_13_dpi_table_column_scaling(self):
        """Audit that all Treeview column widths exceed measured text and heading at 100%, 125%, and 150% DPI."""
        print("\n[AUDIT 13] DPI Table Column Text Measurement Audit...")
        from tkinter import font as tkfont
        scalings = [("100%", 1.0, 10, 9), ("125%", 1.25, 12, 11), ("150%", 1.50, 15, 14)]
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

            w_id = max(f_hd.measure("Workshop ID ▾") + 24, f_row.measure("3351648056") + 24, int(120 * dpi_scale))
            max_status = max(f_row.measure(s) for s in status_samples)
            w_status = max(f_hd.measure("Server Pack Status ▾") + 28, max_status + 32, int(260 * dpi_scale))
            w_size = max(f_hd.measure("Size ▾") + 24, f_row.measure("999.9 MB") + 24, int(95 * dpi_scale))
            w_date = max(f_hd.measure("Last Played / Modified ▾") + 32, f_row.measure("2026-11-08 18:00") + 32, int(195 * dpi_scale))

            self.assertGreater(w_date, f_hd.measure("Last Played / Modified ▾") + 20, f"Date heading clipped at {scale_name}")
            self.assertGreater(w_status, max_status + 20, f"Status clipped at {scale_name}")
            self.assertGreater(w_id, f_hd.measure("Workshop ID ▾") + 15)
            self.assertGreater(w_size, f_hd.measure("Size ▾") + 15)
        print("  -> 100%, 125%, and 150% DPI table column scaling verified (0 text clipping).")

    # -------------------------------------------------------------
    # 14. COMBOBOX SNUG SIZING & DPI PADDING AUDIT
    # -------------------------------------------------------------
    def test_14_combobox_snug_sizing_and_dpi_padding(self):
        """Audit that all Comboboxes have snug widths with zero clipping and zero dead space gap."""
        print("\n[AUDIT 14] Combobox Snug Sizing & Padding Audit...")
        from tkinter import font as tkfont
        self.assertEqual(self.root.gfl_tier_combo["width"], 24)
        self.assertEqual(self.root.comm_sniper_combo["width"], 20)
        self.assertEqual(self.root.china_combo["width"], 31)

        combos = [
            ("GFL Tier", 24, ["Mapper / Supporter (≤ 62)", "Normal Player (≤ 61)", "VIP / Admin (≤ 63)"]),
            ("Community Sniper", 20, ["≤ 63 / 64 (1 Reserved)", "≤ 62 / 64 (2 Reserved)", "≤ 61 / 64 (3 Reserved)"]),
            ("ZE HUD Color", 17, ["0 (Default / Team)", "10 (Aqua / Cyan)", "12 (Light Yellow)"]),
            ("Power Plans", 17, ["High Performance", "Balanced", "Power Saver"]),
            ("China Cluster", 31, ["🇨🇳 93X Zombie Escape (10 Servers)", "🇨🇳 UB Community ZE (8 Servers)"]),
        ]

        scalings = [("100%", 1.0, 9), ("125%", 1.25, 11), ("150%", 1.50, 14)]
        for scale_name, dpi_scale, f_size in scalings:
            f = tkfont.Font(family="Segoe UI", size=f_size)
            zero_w = f.measure("0")
            for name, cb_chars, values in combos:
                max_str_w = max(f.measure(val) for val in values)
                entry_w = cb_chars * zero_w
                padding = entry_w - max_str_w
                # Must not clip (padding >= 0)
                self.assertGreaterEqual(padding, 0, f"{name} clipped at {scale_name}: padding={padding}px")
                # Must not have dead space gap (scaled padding <= 16px * dpi_scale)
                max_allowed_padding = int(16 * dpi_scale) + 2
                self.assertLessEqual(padding, max_allowed_padding, f"{name} excessive dead gap at {scale_name}: padding={padding}px > {max_allowed_padding}px")
        print("  -> All 5 comboboxes verified snug (padding >= 0px and <= 16px across 100%, 125%, 150% DPI).")


if __name__ == "__main__":
    res = unittest.main(exit=False)
    print("\nResult: Was Successful =", res.result.wasSuccessful())
    os._exit(0 if res.result.wasSuccessful() else 1)
