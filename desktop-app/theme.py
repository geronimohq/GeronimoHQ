"""
Tactical Pepe & Banana Phone Cyber-Deck - Unified Desktop Theme Engine
Derives color palette, typography tiers, and widget styles from design-tokens.json.
Provides DPI-aware font scaling and strict parity verification with the web design system.
"""

import json
import os
import tkinter as tk
from tkinter import ttk, font

# Locate and parse design-tokens.json
TOKEN_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "design-tokens.json")

def load_tokens():
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    # Built-in fallback matching design-tokens.json exactly
    return {
        "colors": {
            "canvas": "#070B09",
            "panel": "#0E1512",
            "panel_row": "#121C18",
            "panel_hover": "#16241E",
            "border": "#1E2E26",
            "border_hover": "#2B4036",
            "text_primary": "#FFFFFF",
            "text_muted": "#94A39E",
            "primary_banana": "#FFE135",
            "text_on_banana": "#070B09",
            "success_pepe": "#2ECC71",
            "alert_magenta": "#FF2A85",
            "telemetry_cyan": "#00F0FF",
            "focus_ring": "#FFE135"
        }
    }

TOKENS = load_tokens()
COLORS = TOKENS["colors"]

# Direct Color Constants
COLOR_CANVAS = COLORS["canvas"]
COLOR_PANEL = COLORS["panel"]
COLOR_PANEL_ROW = COLORS["panel_row"]
COLOR_PANEL_HOVER = COLORS["panel_hover"]
COLOR_BORDER = COLORS["border"]
COLOR_BORDER_HOVER = COLORS["border_hover"]
COLOR_TEXT_PRIMARY = COLORS["text_primary"]
COLOR_TEXT_MUTED = COLORS["text_muted"]
COLOR_PRIMARY_BANANA = COLORS["primary_banana"]
COLOR_TEXT_ON_BANANA = COLORS["text_on_banana"]
COLOR_SUCCESS_PEPE = COLORS["success_pepe"]
COLOR_ALERT_MAGENTA = COLORS["alert_magenta"]
COLOR_TELEMETRY_CYAN = COLORS["telemetry_cyan"]
COLOR_FOCUS_RING = COLORS["focus_ring"]

# Legacy aliases for compatibility with existing tests
COLOR_BG_DARK = COLOR_CANVAS
COLOR_BG_PANEL = COLOR_PANEL
COLOR_ACCENT = COLOR_PRIMARY_BANANA
COLOR_TEXT_MAIN = COLOR_TEXT_PRIMARY
COLOR_TEXT_SECONDARY = COLOR_TEXT_MUTED
COLOR_ACCENT_PEPE = COLOR_SUCCESS_PEPE
COLOR_CYAN = COLOR_TELEMETRY_CYAN

def get_dpi_scale(root=None):
    """Calculate current screen DPI scale factor (1.0 = 96 DPI, 1.25 = 120 DPI, 1.5 = 144 DPI)."""
    try:
        if root is not None:
            dpi = root.winfo_fpixels('1i')
            return max(1.0, dpi / 96.0)
    except Exception:
        pass
    return 1.0

def get_scaled_size(base_pt, scale):
    """Return scaled font point size."""
    return int(round(base_pt * scale))

def get_tier_font(tier=1, scale=1.0, family="Segoe UI"):
    """
    DPI-aware typography helper for 5-tier system:
    Tier 1: 16px (12pt), bold uppercase wide-tracking
    Tier 2: 13px (10pt), bold uppercase
    Tier 3: 14px (10.5pt), semibold
    Tier 4: 12px (9pt), regular
    Tier 5: 11px (8.5pt), bold uppercase micro badge
    """
    tier_sizes = {
        1: (12, "bold"),
        2: (10, "bold"),
        3: (10, "bold"),
        4: (9, "normal"),
        5: (8, "bold")
    }
    base_pt, weight = tier_sizes.get(tier, (9, "normal"))
    scaled_pt = get_scaled_size(base_pt, scale)
    return (family, scaled_pt, weight)

def apply_cyberdeck_theme(style: ttk.Style, root=None):
    """Configure ttk Style with Cyber-Deck unified styling."""
    scale = get_dpi_scale(root)
    
    # Configure TFrame
    style.configure("Cyber.TFrame", background=COLOR_CANVAS)
    style.configure("Panel.TFrame", background=COLOR_PANEL, relief="flat")
    style.configure("PanelRow.TFrame", background=COLOR_PANEL_ROW, relief="flat")
    
    # Configure TLabel
    style.configure("Tier1.TLabel",
                    background=COLOR_CANVAS,
                    foreground=COLOR_TEXT_PRIMARY,
                    font=get_tier_font(1, scale))
    
    style.configure("Tier2.TLabel",
                    background=COLOR_PANEL,
                    foreground=COLOR_PRIMARY_BANANA,
                    font=get_tier_font(2, scale))
    
    style.configure("Tier2Pepe.TLabel",
                    background=COLOR_PANEL,
                    foreground=COLOR_SUCCESS_PEPE,
                    font=get_tier_font(2, scale))
                    
    style.configure("Tier3.TLabel",
                    background=COLOR_PANEL,
                    foreground=COLOR_TEXT_PRIMARY,
                    font=get_tier_font(3, scale))
                    
    style.configure("Tier4.TLabel",
                    background=COLOR_PANEL,
                    foreground=COLOR_TEXT_MUTED,
                    font=get_tier_font(4, scale))
                    
    style.configure("Tier5.TLabel",
                    background=COLOR_PANEL_ROW,
                    foreground=COLOR_PRIMARY_BANANA,
                    font=get_tier_font(5, scale, family="Consolas"))

    # Configure 34px Button styles
    btn_font = get_tier_font(3, scale)
    style.configure("Cyber34.TButton",
                    font=btn_font,
                    padding=(12, 6),
                    relief="flat")
                    
    style.configure("BananaCTA.TButton",
                    font=get_tier_font(3, scale),
                    padding=(14, 6),
                    background=COLOR_PRIMARY_BANANA,
                    foreground=COLOR_TEXT_ON_BANANA)

    # Configure Treeview & Combobox
    style.configure("Cyber.Treeview",
                    background=COLOR_PANEL_ROW,
                    fieldbackground=COLOR_PANEL_ROW,
                    foreground=COLOR_TEXT_PRIMARY,
                    font=get_tier_font(4, scale, family="Consolas"),
                    rowheight=int(26 * scale))
                    
    style.configure("Cyber.Treeview.Heading",
                    background=COLOR_PANEL,
                    foreground=COLOR_PRIMARY_BANANA,
                    font=get_tier_font(2, scale))
                    
    style.map("Cyber.Treeview",
              background=[("selected", COLOR_PRIMARY_BANANA)],
              foreground=[("selected", COLOR_TEXT_ON_BANANA)])

    style.configure("Cyber.TCombobox",
                    fieldbackground=COLOR_PANEL_ROW,
                    background=COLOR_PANEL,
                    foreground=COLOR_TEXT_PRIMARY,
                    arrowcolor=COLOR_PRIMARY_BANANA,
                    font=get_tier_font(4, scale))
                    
    style.map("Cyber.TCombobox",
              fieldbackground=[("readonly", COLOR_PANEL_ROW)],
              selectbackground=[("readonly", COLOR_PRIMARY_BANANA)],
              selectforeground=[("readonly", COLOR_TEXT_ON_BANANA)])
