"""
CS2 Command Center - theme (CS 1.6 / Source VGUI skin).

ONE source for every color, font and bevel used by the desktop app. No other file may contain
a color literal (tests/test_theme_contrast.py and test_retro_skin.py enforce it).

Design rules (owner brief, 2026-11-10; adjusted so every text color reaches 4.5:1):
  * muted olive surfaces, flat fills, 1-2 px bevels, no gradients / shadows / rounded corners
  * ONE accent (burnt orange #E48716, the owner-approved CS2 orange): section headings, active
    nav item, selected-row bar, and the single primary button per screen. Never body text,
    never a status.
  * status colors only on status elements; small status TEXT uses the *_TEXT variants
  * team colors reserved: CT blue = links / secondary actions / humans, T gold = zombies
Contrast: see tests/test_theme_contrast.py (prints the full table).
"""
import os
import tkinter as tk
from tkinter import ttk

# ---------------------------------------------------------------- surfaces
SURFACE_BASE = "#3A4034"     # window background
SURFACE_PANEL = "#474F40"    # cards, panels, sidebar
SURFACE_RAISED = "#4A5242"   # rows / list items sitting on a panel (a touch lighter)
SURFACE_INSET = "#262B22"    # log box, code preview, inputs, dropdowns
HOVER_LIGHTEN = 1.06         # hover = surface x 1.06 (no color change)

# ---------------------------------------------------------------- bevels
BEVEL_LIGHT = "#7C8574"      # top + left edge of raised elements
BEVEL_DARK = "#22261E"       # bottom + right edge of raised elements

# ---------------------------------------------------------------- text
TEXT_PRIMARY = "#D5DACF"
TEXT_SECONDARY = "#C4CABE"   # helper text (never dimmer; owner brief minimum was #A3AC9A, raised to pass 4.5:1)
TEXT_DISABLED = "#8A9284"    # disabled controls only (exempt from 4.5:1 by WCAG)
TEXT_ON_ACCENT = "#1E2219"   # dark text on accent / good fills
TEXT_ON_DARK_FILL = "#FFFFFF"  # light text on warn / bad fills

# ---------------------------------------------------------------- the ONE accent
ACCENT = "#E48716"
ACCENT_HOVER = "#F09527"
ACCENT_PRESSED = "#C5720E"

# ---------------------------------------------------------------- status (status elements only)
GOOD = "#6FAE5C"             # fill / icon / dot / border
WARN = "#AC5733"             # rust, never yellow
BAD = "#B8433A"
GOOD_TEXT = "#A6D499"        # small status TEXT
WARN_TEXT = "#EEBEA7"
BAD_TEXT = "#EFBCB7"

# ---------------------------------------------------------------- team colors (reserved)
CT_BLUE = "#6F8FB8"          # fills / icons / left borders
CT_BLUE_TEXT = "#BBCADE"     # links, secondary actions, humans (as text)
T_GOLD = "#B89A5E"
T_GOLD_TEXT = "#D7C6A4"      # zombies / T-side tags (as text)

# ---------------------------------------------------------------- fonts + type scale
def _pick_font(candidates, default):
    fonts = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
    files = {"Verdana": "verdana.ttf", "Tahoma": "tahoma.ttf", "Segoe UI": "segoeui.ttf",
             "Consolas": "consola.ttf", "Lucida Console": "lucon.ttf"}
    for name in candidates:
        if os.path.exists(os.path.join(fonts, files.get(name, ""))):
            return name
    return default


FONT_UI = _pick_font(("Verdana", "Tahoma", "Segoe UI"), "Segoe UI")
FONT_MONO = _pick_font(("Consolas", "Lucida Console"), "Courier New")

# Steps 11 / 12 / 13 / 15 / 18 px, written as points so they scale with Windows DPI
# (8 / 9 / 10 / 11 / 14 pt = 10.7 / 12 / 13.3 / 14.7 / 18.7 px at 96 DPI).
FS_11, FS_12, FS_13, FS_15, FS_18 = 8, 9, 10, 11, 14
TYPE_SCALE = (FS_11, FS_12, FS_13, FS_15, FS_18)

# old point sizes -> nearest type-scale step (used by the one-off migration and by font())
_PT_TO_STEP = {6: FS_11, 7: FS_11, 8: FS_11, 9: FS_12, 10: FS_13, 11: FS_13, 12: FS_15, 13: FS_15, 14: FS_18, 16: FS_18,
               18: FS_18}
_PX_TO_STEP = {11: FS_11, 12: FS_12, 13: FS_13, 14: FS_15, 15: FS_15, 16: FS_18, 18: FS_18}


def font(step=FS_12, weight="normal", mono=False, italic=False):
    """UI font tuple on the type scale."""
    style = weight + (" italic" if italic else "")
    return (FONT_MONO if mono else FONT_UI, step, style.strip())


def snap_size(size):
    """Map any old Tk size (pt if > 0, px if < 0) onto the type scale."""
    if size < 0:
        return _PX_TO_STEP.get(-size, FS_13 if -size < 14 else FS_18)
    return _PT_TO_STEP.get(size, FS_13 if size < 14 else FS_18)


# ---------------------------------------------------------------- color helpers
def lighten(hex_color, factor=HOVER_LIGHTEN):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(min(255, round(c * factor)) for c in (r, g, b))


def darken(hex_color, factor=0.85):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(round(c * factor) for c in (r, g, b))


def contrast(fg_hex, bg_hex):
    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    hi, lo = sorted((lum(fg_hex), lum(bg_hex)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


# ---------------------------------------------------------------- legacy names (kept so old imports keep working)
COLOR_BG = SURFACE_BASE
COLOR_PANEL = SURFACE_PANEL
COLOR_RAISED = SURFACE_RAISED
COLOR_BORDER = BEVEL_DARK
COLOR_BORDER_HOVER = BEVEL_LIGHT
COLOR_TEXT = TEXT_PRIMARY
COLOR_MUTED = TEXT_SECONDARY
COLOR_PRIMARY = ACCENT
COLOR_PRIMARY_HOVER = ACCENT_HOVER
COLOR_PRIMARY_PRESSED = ACCENT_PRESSED
COLOR_TEXT_ON_PRIMARY = TEXT_ON_ACCENT
COLOR_INFO = CT_BLUE_TEXT
COLOR_SUCCESS = GOOD
COLOR_DANGER = BAD_TEXT

COLOR_CANVAS = COLOR_BG
COLOR_BG_DARK = COLOR_BG
COLOR_BG_PANEL = COLOR_PANEL
COLOR_PANEL_ROW = COLOR_RAISED
COLOR_PANEL_HOVER = lighten(SURFACE_RAISED)
COLOR_TEXT_PRIMARY = COLOR_TEXT
COLOR_TEXT_MAIN = COLOR_TEXT
COLOR_TEXT_MUTED = COLOR_MUTED
COLOR_TEXT_SECONDARY = COLOR_MUTED
COLOR_ACCENT = COLOR_PRIMARY
COLOR_ACCENT_PEPE = COLOR_PRIMARY
COLOR_SUCCESS_PEPE = GOOD
COLOR_CYAN = COLOR_INFO
COLOR_TELEMETRY_CYAN = COLOR_INFO
COLOR_ALERT_MAGENTA = COLOR_DANGER
COLOR_FOCUS_RING = TEXT_PRIMARY
COLOR_PRIMARY_BANANA = COLOR_PRIMARY
COLOR_TEXT_ON_BANANA = COLOR_TEXT_ON_PRIMARY

COLORS = {
    "canvas": COLOR_CANVAS, "panel": COLOR_PANEL, "panel_row": COLOR_PANEL_ROW, "panel_hover": COLOR_PANEL_HOVER,
    "border": COLOR_BORDER, "border_hover": COLOR_BORDER_HOVER, "text_primary": COLOR_TEXT_PRIMARY,
    "text_muted": COLOR_TEXT_MUTED, "primary_banana": COLOR_PRIMARY, "text_on_banana": COLOR_TEXT_ON_PRIMARY,
    "success_pepe": COLOR_SUCCESS_PEPE, "alert_magenta": COLOR_ALERT_MAGENTA, "telemetry_cyan": COLOR_TELEMETRY_CYAN,
    "focus_ring": COLOR_FOCUS_RING, "bg": COLOR_BG, "raised": COLOR_RAISED, "primary": COLOR_PRIMARY,
    "primary_hover": COLOR_PRIMARY_HOVER, "primary_pressed": COLOR_PRIMARY_PRESSED,
    "text_on_primary": COLOR_TEXT_ON_PRIMARY, "info": COLOR_INFO, "success": COLOR_SUCCESS, "danger": COLOR_DANGER,
}


# ---------------------------------------------------------------- DPI helpers (unchanged API)
def get_dpi_scale(root=None):
    """Current screen DPI scale factor (1.0 = 96 DPI, 1.25 = 120 DPI, 1.5 = 144 DPI)."""
    try:
        if root is not None:
            return max(1.0, root.winfo_fpixels('1i') / 96.0)
    except Exception:
        pass
    return 1.0


def get_scaled_size(base_pt, scale):
    return int(round(base_pt * scale))


def get_tier_font(tier=1, scale=1.0, family=None):
    """5-tier typography (kept for old callers); sizes now sit on the 11/12/13/15/18 px scale.
    The DPI scale is applied by Tk itself (sizes are points), so `scale` is not applied again."""
    family = family or FONT_UI
    tiers = {1: (FS_15, "bold"), 2: (FS_13, "bold"), 3: (FS_13, "bold"), 4: (FS_12, "normal"), 5: (FS_11, "bold")}
    size, weight = tiers.get(tier, (FS_12, "normal"))
    return (family, size, weight)


# ---------------------------------------------------------------- ttk (clam) styles
def apply_retro_ttk(style: ttk.Style, root=None):
    """Retro / VGUI look for ttk widgets: flat olive fills, inset fields, bevel tabs."""
    try:
        style.theme_use("clam")
    except Exception:
        pass
    f_ui = font(FS_12)
    style.configure(".", background=SURFACE_PANEL, foreground=TEXT_PRIMARY, font=f_ui,
                    bordercolor=BEVEL_DARK, lightcolor=BEVEL_LIGHT, darkcolor=BEVEL_DARK,
                    focuscolor=TEXT_PRIMARY, troughcolor=SURFACE_INSET, relief="flat")
    style.map(".", foreground=[("disabled", TEXT_DISABLED)], background=[("disabled", SURFACE_PANEL)])

    # inputs / dropdowns: inset
    style.configure("TCombobox", fieldbackground=SURFACE_INSET, background=SURFACE_PANEL, foreground=TEXT_PRIMARY,
                    arrowcolor=TEXT_PRIMARY, bordercolor=BEVEL_DARK, lightcolor=BEVEL_DARK, darkcolor=BEVEL_LIGHT,
                    selectbackground=SURFACE_RAISED, selectforeground=TEXT_PRIMARY, padding=3, relief="flat")
    style.map("TCombobox",
              fieldbackground=[("readonly", SURFACE_INSET), ("disabled", SURFACE_PANEL)],
              foreground=[("disabled", TEXT_DISABLED), ("readonly", TEXT_PRIMARY)],
              selectbackground=[("readonly", SURFACE_INSET)], selectforeground=[("readonly", TEXT_PRIMARY)],
              background=[("active", lighten(SURFACE_PANEL)), ("pressed", SURFACE_INSET)],
              arrowcolor=[("disabled", TEXT_DISABLED)])
    style.configure("TEntry", fieldbackground=SURFACE_INSET, foreground=TEXT_PRIMARY, insertcolor=TEXT_PRIMARY,
                    bordercolor=BEVEL_DARK, lightcolor=BEVEL_DARK, darkcolor=BEVEL_LIGHT)

    # check / radio
    for name in ("TCheckbutton", "TRadiobutton"):
        style.configure(name, background=SURFACE_PANEL, foreground=TEXT_PRIMARY, indicatorcolor=SURFACE_INSET,
                        indicatorbackground=SURFACE_INSET, upperbordercolor=BEVEL_DARK, lowerbordercolor=BEVEL_LIGHT)
        style.map(name, indicatorcolor=[("selected", GOOD), ("disabled", SURFACE_PANEL)],
                  foreground=[("disabled", TEXT_DISABLED)], background=[("active", lighten(SURFACE_PANEL))])

    # scrollbars
    for orient in ("Vertical", "Horizontal"):
        for prefix in (f"{orient}.TScrollbar", f"{orient}.Dark.TScrollbar"):
            style.configure(prefix, background=SURFACE_RAISED, troughcolor=SURFACE_INSET, bordercolor=BEVEL_DARK,
                            arrowcolor=TEXT_PRIMARY, lightcolor=BEVEL_LIGHT, darkcolor=BEVEL_DARK, relief="raised",
                            arrowsize=14)
            style.map(prefix, background=[("active", lighten(SURFACE_RAISED)), ("pressed", SURFACE_INSET)])
    style.configure("Vertical.Dark.TScrollbar", background=SURFACE_RAISED)

    # tabs: bevel tabs, active tab = lighter surface (accent bar is drawn by the app)
    style.configure("TNotebook", background=SURFACE_BASE, bordercolor=BEVEL_DARK)
    style.configure("TNotebook.Tab", background=SURFACE_PANEL, foreground=TEXT_PRIMARY, padding=(12, 5),
                    bordercolor=BEVEL_DARK, lightcolor=BEVEL_LIGHT, darkcolor=BEVEL_DARK, font=f_ui)
    style.map("TNotebook.Tab", background=[("selected", SURFACE_RAISED), ("active", lighten(SURFACE_PANEL))],
              foreground=[("selected", TEXT_PRIMARY)])

    # tables
    style.configure("Treeview", background=SURFACE_INSET, fieldbackground=SURFACE_INSET, foreground=TEXT_PRIMARY,
                    bordercolor=BEVEL_DARK, font=font(FS_12))
    style.configure("Treeview.Heading", background=SURFACE_PANEL, foreground=TEXT_PRIMARY, relief="raised",
                    bordercolor=BEVEL_DARK, lightcolor=BEVEL_LIGHT, darkcolor=BEVEL_DARK, font=font(FS_12, "bold"))
    style.map("Treeview", background=[("selected", SURFACE_RAISED)], foreground=[("selected", TEXT_PRIMARY)])
    style.map("Treeview.Heading", background=[("active", lighten(SURFACE_PANEL))])

    # progress / scale
    style.configure("Horizontal.TProgressbar", background=GOOD, troughcolor=SURFACE_INSET, bordercolor=BEVEL_DARK)
    style.configure("Horizontal.TScale", background=SURFACE_PANEL, troughcolor=SURFACE_INSET)
    style.configure("TSeparator", background=BEVEL_DARK)

    if root is not None:
        # Drop-down list of every Combobox, and the right-click menus
        root.option_add("*TCombobox*Listbox.background", SURFACE_INSET)
        root.option_add("*TCombobox*Listbox.foreground", TEXT_PRIMARY)
        root.option_add("*TCombobox*Listbox.selectBackground", SURFACE_RAISED)
        root.option_add("*TCombobox*Listbox.selectForeground", TEXT_PRIMARY)
        root.option_add("*TCombobox*Listbox.font", f_ui)
        root.option_add("*TCombobox*Listbox.relief", "flat")
        root.option_add("*Menu.background", SURFACE_PANEL)
        root.option_add("*Menu.foreground", TEXT_PRIMARY)
        root.option_add("*Menu.activeBackground", SURFACE_RAISED)
        root.option_add("*Menu.activeForeground", TEXT_PRIMARY)
        root.option_add("*Menu.relief", "flat")


def apply_cyberdeck_theme(style: ttk.Style, root=None):
    """Old entry point (name kept): now applies the retro skin."""
    apply_retro_ttk(style, root)
    style.configure("Cyber.TFrame", background=SURFACE_BASE)
    style.configure("Panel.TFrame", background=SURFACE_PANEL, relief="flat")
    style.configure("PanelRow.TFrame", background=SURFACE_RAISED, relief="flat")
    style.configure("Tier1.TLabel", background=SURFACE_BASE, foreground=TEXT_PRIMARY, font=font(FS_15, "bold"))
    style.configure("Tier2.TLabel", background=SURFACE_PANEL, foreground=ACCENT, font=font(FS_13, "bold"))
    style.configure("Tier2Pepe.TLabel", background=SURFACE_PANEL, foreground=ACCENT, font=font(FS_13, "bold"))
    style.configure("Tier3.TLabel", background=SURFACE_PANEL, foreground=TEXT_PRIMARY, font=font(FS_13, "bold"))
    style.configure("Tier4.TLabel", background=SURFACE_PANEL, foreground=TEXT_SECONDARY, font=font(FS_12))
    style.configure("Tier5.TLabel", background=SURFACE_RAISED, foreground=TEXT_SECONDARY, font=font(FS_11, "bold", mono=True))
    style.configure("Cyber34.TButton", font=font(FS_13, "bold"), padding=(12, 6), relief="raised")
    style.configure("BananaCTA.TButton", font=font(FS_13, "bold"), padding=(14, 6), background=ACCENT,
                    foreground=TEXT_ON_ACCENT)
    style.configure("PepeCTA.TButton", font=font(FS_13, "bold"), padding=(14, 6), background=ACCENT,
                    foreground=TEXT_ON_ACCENT)
    style.configure("Cyber.Treeview", background=SURFACE_INSET, fieldbackground=SURFACE_INSET, foreground=TEXT_PRIMARY,
                    font=font(FS_12, mono=True), rowheight=int(26 * get_dpi_scale(root)))
    style.configure("Cyber.Treeview.Heading", background=SURFACE_PANEL, foreground=TEXT_PRIMARY, font=font(FS_13, "bold"))
    style.map("Cyber.Treeview", background=[("selected", SURFACE_RAISED)], foreground=[("selected", TEXT_PRIMARY)])
    style.configure("Cyber.TCombobox", fieldbackground=SURFACE_INSET, background=SURFACE_PANEL, foreground=TEXT_PRIMARY,
                    arrowcolor=TEXT_PRIMARY, font=font(FS_12))
    style.map("Cyber.TCombobox", fieldbackground=[("readonly", SURFACE_INSET)],
              selectbackground=[("readonly", SURFACE_INSET)], selectforeground=[("readonly", TEXT_PRIMARY)])
