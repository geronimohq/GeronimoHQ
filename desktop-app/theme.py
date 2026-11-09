"""
Tactical Pepe Cyber-Deck - Dark Slate Desktop Theme Engine
Derives color palette, typography tiers, and widget styles for CS2 Command Center.
Strict Dark Slate palette:
  bg: #0A0E12
  panel: #11171D
  raised: #161E26
  border: #243241
  text: #E6EDF3
  muted: #A3B3C0
  primary: #43A857, hover #52BC67, pressed #368F49, text-on-primary #04120A
  info: #38BDF8
  success text: #43A857
  danger: #F26D6D
Banned: yellow, amber, orange, pink, magenta, fuchsia.
"""

import json
import os
import sys
import tkinter as tk
from tkinter import ttk, font

# Locate and parse design-tokens.json
TOKEN_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "design-tokens.json")

# Desktop Dark Slate Color Constants
COLOR_BG = "#0A0E12"
COLOR_PANEL = "#11171D"
COLOR_RAISED = "#161E26"
COLOR_BORDER = "#243241"
COLOR_BORDER_HOVER = "#364B60"
COLOR_TEXT = "#E6EDF3"
COLOR_MUTED = "#A3B3C0"
COLOR_PRIMARY = "#43A857"
COLOR_PRIMARY_HOVER = "#52BC67"
COLOR_PRIMARY_PRESSED = "#368F49"
COLOR_TEXT_ON_PRIMARY = "#04120A"
COLOR_INFO = "#38BDF8"
COLOR_SUCCESS = "#43A857"
COLOR_DANGER = "#F26D6D"

# Semantic and backward-compatible aliases
COLOR_CANVAS = COLOR_BG
COLOR_BG_DARK = COLOR_BG
COLOR_BG_PANEL = COLOR_PANEL
COLOR_PANEL_ROW = COLOR_RAISED
COLOR_PANEL_HOVER = COLOR_RAISED
COLOR_TEXT_PRIMARY = COLOR_TEXT
COLOR_TEXT_MAIN = COLOR_TEXT
COLOR_TEXT_MUTED = COLOR_MUTED
COLOR_TEXT_SECONDARY = COLOR_MUTED
COLOR_ACCENT = COLOR_PRIMARY
COLOR_ACCENT_PEPE = COLOR_PRIMARY
COLOR_SUCCESS_PEPE = COLOR_PRIMARY
COLOR_CYAN = COLOR_INFO
COLOR_TELEMETRY_CYAN = COLOR_INFO
COLOR_ALERT_MAGENTA = COLOR_DANGER
COLOR_FOCUS_RING = COLOR_PRIMARY
COLOR_PRIMARY_BANANA = COLOR_PRIMARY
COLOR_TEXT_ON_BANANA = COLOR_TEXT_ON_PRIMARY

COLORS = {
    "canvas": COLOR_CANVAS,
    "panel": COLOR_PANEL,
    "panel_row": COLOR_PANEL_ROW,
    "panel_hover": COLOR_PANEL_HOVER,
    "border": COLOR_BORDER,
    "border_hover": COLOR_BORDER_HOVER,
    "text_primary": COLOR_TEXT_PRIMARY,
    "text_muted": COLOR_TEXT_MUTED,
    "primary_banana": COLOR_PRIMARY,
    "text_on_banana": COLOR_TEXT_ON_PRIMARY,
    "success_pepe": COLOR_PRIMARY,
    "alert_magenta": COLOR_DANGER,
    "telemetry_cyan": COLOR_INFO,
    "focus_ring": COLOR_FOCUS_RING,
    "bg": COLOR_BG,
    "raised": COLOR_RAISED,
    "primary": COLOR_PRIMARY,
    "primary_hover": COLOR_PRIMARY_HOVER,
    "primary_pressed": COLOR_PRIMARY_PRESSED,
    "text_on_primary": COLOR_TEXT_ON_PRIMARY,
    "info": COLOR_INFO,
    "success": COLOR_SUCCESS,
    "danger": COLOR_DANGER,
}

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
    """Configure ttk Style with Dark Slate unified styling."""
    scale = get_dpi_scale(root)
    
    # Configure TFrame
    style.configure("Cyber.TFrame", background=COLOR_BG)
    style.configure("Panel.TFrame", background=COLOR_PANEL, relief="flat")
    style.configure("PanelRow.TFrame", background=COLOR_RAISED, relief="flat")
    
    # Configure TLabel
    style.configure("Tier1.TLabel",
                    background=COLOR_BG,
                    foreground=COLOR_TEXT,
                    font=get_tier_font(1, scale))
    
    style.configure("Tier2.TLabel",
                    background=COLOR_PANEL,
                    foreground=COLOR_PRIMARY,
                    font=get_tier_font(2, scale))
    
    style.configure("Tier2Pepe.TLabel",
                    background=COLOR_PANEL,
                    foreground=COLOR_PRIMARY,
                    font=get_tier_font(2, scale))
                    
    style.configure("Tier3.TLabel",
                    background=COLOR_PANEL,
                    foreground=COLOR_TEXT,
                    font=get_tier_font(3, scale))
                    
    style.configure("Tier4.TLabel",
                    background=COLOR_PANEL,
                    foreground=COLOR_MUTED,
                    font=get_tier_font(4, scale))
                    
    style.configure("Tier5.TLabel",
                    background=COLOR_RAISED,
                    foreground=COLOR_PRIMARY,
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
                    background=COLOR_PRIMARY,
                    foreground=COLOR_TEXT_ON_PRIMARY)

    style.configure("PepeCTA.TButton",
                    font=get_tier_font(3, scale),
                    padding=(14, 6),
                    background=COLOR_PRIMARY,
                    foreground=COLOR_TEXT_ON_PRIMARY)

    # Configure Treeview & Combobox
    style.configure("Cyber.Treeview",
                    background=COLOR_RAISED,
                    fieldbackground=COLOR_RAISED,
                    foreground=COLOR_TEXT,
                    font=get_tier_font(4, scale, family="Consolas"),
                    rowheight=int(26 * scale))
                    
    style.configure("Cyber.Treeview.Heading",
                    background=COLOR_PANEL,
                    foreground=COLOR_TEXT,
                    font=get_tier_font(2, scale))
                    
    style.map("Cyber.Treeview",
              background=[("selected", COLOR_PRIMARY)],
              foreground=[("selected", COLOR_TEXT_ON_PRIMARY)])

    style.configure("Cyber.TCombobox",
                    fieldbackground=COLOR_RAISED,
                    background=COLOR_PANEL,
                    foreground=COLOR_TEXT,
                    arrowcolor=COLOR_PRIMARY,
                    font=get_tier_font(4, scale))
                    
    style.map("Cyber.TCombobox",
              fieldbackground=[("readonly", COLOR_RAISED)],
              selectbackground=[("readonly", COLOR_PRIMARY)],
              selectforeground=[("readonly", COLOR_TEXT_ON_PRIMARY)])
