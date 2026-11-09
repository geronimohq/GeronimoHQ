"""
CS2 Command Center - Performance Optimizer, Zombie Escape Browser & PC Maintenance Hub
Faithful to Concept 1 layout: Vertical Left Sidebar, CS2 Panorama Dark styling,
Dynamic AMD Tab, No Graphs, Word-wrapped text, Safe PC Maintenance suite,
Background System Tray support, Fast 1.0s Multi-Server Slot Sniper, and Custom ZE Map Cleaner.
"""

import os
import sys
import ctypes

# Set explicit AppUserModelID and DPI awareness BEFORE any UI libraries or Tkinter are loaded
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ValveSoftware.CS2CommandCenter.Optimizer.v2")
except Exception:
    pass

import time
import threading
from concurrent.futures import ThreadPoolExecutor
import datetime
import urllib.parse
import tkinter as tk
from tkinter import ttk, messagebox
import winsound

import pystray
from PIL import Image, ImageDraw, ImageTk
import webbrowser

import core_logic
import hardware_info
import server_browser
import app_config
import custom_map_cleaner
import discord_rpc
import cs2_gsi

import subprocess

_single_instance_mutex = None

def launch_url_in_browser(url: str) -> bool:
    """
    Universal, elevation-proof URL opener for Windows.
    Bypasses UIPI/UAC restrictions by launching the user's browser process directly
    (Brave, Chrome, Edge, Firefox), with graceful fallbacks to cmd start, rundll32, and ShellExecute.
    """
    if not url:
        return False

    # 1. Direct browser binaries (Guaranteed execution even when running as Administrator)
    # NOTE: Never pass CREATE_NO_WINDOW (0x08000000) to GUI web browsers, as that suppresses window creation!
    browser_exes = [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
    ]
    for b_exe in browser_exes:
        if os.path.exists(b_exe):
            try:
                subprocess.Popen([b_exe, url])
                return True
            except Exception:
                pass

    # 2. Windows shell 'start' command (delegates to Windows registered default web browser)
    try:
        subprocess.Popen(["cmd.exe", "/c", "start", "", url])
        return True
    except Exception:
        pass

    # 3. Try rundll32 FileProtocolHandler
    try:
        subprocess.Popen(["rundll32.exe", "url.dll,FileProtocolHandler", url])
        return True
    except Exception:
        pass

    # 4. Try explorer.exe
    try:
        subprocess.Popen(["explorer.exe", url])
        return True
    except Exception:
        pass

    # 5. Try os.startfile
    try:
        os.startfile(url)
        return True
    except Exception:
        pass

    # 6. Fallback to webbrowser
    try:
        import webbrowser
        webbrowser.open(url)
        return True
    except Exception:
        return False

# Single Instance Mutex & Inter-Process Restore Event
SINGLE_INSTANCE_MUTEX_NAME = "Local\\CS2CommandCenter_App_SingleInstance_Mutex"
SINGLE_INSTANCE_EVENT_NAME = "Local\\CS2CommandCenter_App_ShowEvent"

def check_single_instance():
    """Ensures only ONE instance of CS2 Command Center runs. Signals running instance to restore."""
    kernel32 = ctypes.windll.kernel32
    is_elevated_relaunch = "--elevated" in sys.argv
    max_attempts = 20 if is_elevated_relaunch else 1
    for _ in range(max_attempts):
        mutex = kernel32.CreateMutexW(None, True, SINGLE_INSTANCE_MUTEX_NAME)
        err = kernel32.GetLastError()
        if err != 183:  # ERROR_ALREADY_EXISTS not encountered, mutex successfully acquired
            return mutex
        if not is_elevated_relaunch:
            h_event = kernel32.OpenEventW(0x0002, False, SINGLE_INSTANCE_EVENT_NAME)  # EVENT_MODIFY_STATE
            if h_event:
                kernel32.SetEvent(h_event)
                kernel32.CloseHandle(h_event)
            kernel32.CloseHandle(mutex)
            return None
        # In elevated relaunch mode, wait for old non-elevated process to finish closing its handle
        kernel32.CloseHandle(mutex)
        time.sleep(0.1)
    return None

# Concept 1 Exact Color Palette (Authentic Panorama Dark)
BG_WINDOW = "#0c0e12"       # Main background
BG_SIDEBAR = "#11141a"      # Vertical left sidebar
BG_SIDEBAR_ACTIVE = "#1a1f29"
BG_CARD = "#141820"         # Content card panels
BG_CARD_ROW = "#171c26"
BG_BORDER = "#1f2533"       # Thin sharp borders
BG_CONSOLE = "#07080b"      # Terminal black
FG_WHITE = "#f8fafc"        # Primary typography
FG_MUTED = "#8e99a8"        # Secondary description
ACCENT_ORANGE = "#de6c11"   # CS2 Panorama signature orange
ACCENT_ORANGE_HOVER = "#f27918"
ACCENT_GREEN = "#10b981"
ACCENT_CYAN = "#38bdf8"
ACCENT_RED = "#ef4444"      # Alert Red for AMD MPO Notice & Critical warnings
ACCENT_AMBER = "#f59e0b"

def play_calm_tone(kind="info"):
    """Plays a gentle, soothing, non-intrusive Windows studio notification chime."""
    def _sound():
        try:
            sound_dir = r"C:\Windows\Media"
            if kind == "error":
                f = os.path.join(sound_dir, "Windows Background.wav")
            elif kind in ("warning", "warning_question"):
                f = os.path.join(sound_dir, "Windows Information Bar.wav")
            else:  # info / success / question
                f = os.path.join(sound_dir, "Windows Information Bar.wav")

            if not os.path.exists(f):
                f = os.path.join(sound_dir, "Windows Navigation Start.wav")

            if os.path.exists(f):
                winsound.PlaySound(f, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
            else:
                winsound.MessageBeep(winsound.MB_OK)
        except Exception:
            pass
    threading.Thread(target=_sound, daemon=True).start()

class PanoramaTooltip:
    """
    CS2 Panorama styled hover tooltip.
    Appears after delay_ms (default 800ms: the researched gaming UX sweet-spot)
    when mouse hovers steadily over a clickable control or button.
    Smoothly dismisses on mouse leave, mouse button click, or window unmap.
    """
    def __init__(self, widget, text, delay_ms=800):
        self.widget = widget
        self.text = str(text).strip()
        self.delay_ms = delay_ms
        self.tip_window = None
        self._after_id = None

        if not self.widget or not self.text:
            return

        self.widget.bind("<Enter>", self._on_enter, add="+")
        self.widget.bind("<Leave>", self._on_leave, add="+")
        self.widget.bind("<Button-1>", self._on_leave, add="+")
        self.widget.bind("<Button-2>", self._on_leave, add="+")
        self.widget.bind("<Button-3>", self._on_leave, add="+")
        self.widget.bind("<Destroy>", self._on_destroy, add="+")

    def _on_enter(self, event=None):
        self._cancel()
        if not self.text:
            return
        self._after_id = self.widget.after(self.delay_ms, self._show)

    def _on_leave(self, event=None):
        self._cancel()
        self._hide()

    def _on_destroy(self, event=None):
        self._cancel()
        self._hide()

    def _cancel(self):
        if self._after_id:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show(self):
        self._after_id = None
        if self.tip_window or not self.widget.winfo_exists():
            return

        x = self.widget.winfo_rootx() + (self.widget.winfo_width() // 2)
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.attributes("-topmost", True)
        tw.configure(bg="#273142")  # 1px Panorama Dark border

        container = tk.Frame(tw, bg="#0d1118", padx=8, pady=5)
        container.pack(fill="both", expand=True, padx=1, pady=1)

        lbl = tk.Label(
            container,
            text=self.text,
            font=("Segoe UI", 10),
            fg="#e2e8f0",
            bg="#0d1118",
            justify="left",
            wraplength=340
        )
        lbl.pack()

        tw.update_idletasks()
        req_w = tw.winfo_reqwidth()
        req_h = tw.winfo_reqheight()

        screen_w = tw.winfo_screenwidth()
        screen_h = tw.winfo_screenheight()

        pos_x = x - (req_w // 2)
        pos_y = y

        if pos_x + req_w > screen_w - 10:
            pos_x = screen_w - req_w - 10
        if pos_x < 10:
            pos_x = 10

        if pos_y + req_h > screen_h - 40:
            pos_y = self.widget.winfo_rooty() - req_h - 6

        tw.wm_geometry(f"+{pos_x}+{pos_y}")

    def _hide(self):
        if self.tip_window:
            try:
                self.tip_window.destroy()
            except Exception:
                pass
            self.tip_window = None

def add_tooltip(widget, text, delay_ms=800):
    """Convenience helper to attach a PanoramaTooltip to any Tk widget."""
    if widget and text:
        return PanoramaTooltip(widget, text, delay_ms=delay_ms)
    return None

def get_desktop_workarea():
    """Returns (work_w, work_h) accounting for Windows taskbar via Win32 SPI_GETWORKAREA."""
    try:
        import ctypes
        import ctypes.wintypes
        rect = ctypes.wintypes.RECT()
        if ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0):
            work_w = rect.right - rect.left
            work_h = rect.bottom - rect.top
            return max(800, work_w), max(600, work_h)
    except Exception:
        pass
    root = getattr(tk, "_default_root", None)
    if root and root.winfo_exists():
        return max(800, root.winfo_screenwidth()), max(600, root.winfo_screenheight() - 40)
    return 1920, 1040

def center_window_on_parent(dlg, parent=None, req_w=None, req_h=None):
    """
    Centers a dialog window directly over its owner/parent window according to Windows UX guidelines (CenterOwner).
    Sizes from content while clamped to usable Windows workarea (minus taskbar).
    """
    dlg.update_idletasks()
    work_w, work_h = get_desktop_workarea()

    req_cw = dlg.winfo_reqwidth()
    req_ch = dlg.winfo_reqheight()

    w = req_w or req_cw
    h = req_h or req_ch

    # Content-based clamp to workarea
    w = min(max(w, req_cw), work_w - 40)
    h = min(max(h, req_ch), work_h - 40)

    target = parent or getattr(dlg, "master", None)
    if target and target.winfo_exists() and target.winfo_viewable():
        rx = target.winfo_rootx()
        ry = target.winfo_rooty()
        rw = target.winfo_width()
        rh = target.winfo_height()
        pos_x = rx + (rw - w) // 2
        pos_y = ry + (rh - h) // 2
    else:
        pos_x = (work_w - w) // 2
        pos_y = (work_h - h) // 2

    pos_x = max(10, min(pos_x, work_w - w - 10))
    pos_y = max(30, min(pos_y, work_h - h - 30))

    dlg.geometry(f"{w}x{h}+{pos_x}+{pos_y}")

def show_custom_modal(title: str, message: str, kind: str = "info", parent=None, **kwargs) -> bool:
    """
    Renders an authentic CS2 Panorama dark modal dialog matching the app UI,
    with custom icons, typography, smooth borders, and calming harmonic chime.
    Fully thread-safe: if called from a worker thread, automatically routes to Tk main thread.
    Returns True for OK / Yes, and False for No / Cancel / Dismiss.
    Guarantees grab release on close to prevent input freezes.
    """
    if threading.current_thread() != threading.main_thread():
        ev = threading.Event()
        res = [False]
        def _runner():
            try:
                res[0] = show_custom_modal(title, message, kind=kind, parent=parent, **kwargs)
            finally:
                ev.set()
        try:
            target = parent or getattr(tk, "_default_root", None)
            if target and target.winfo_exists():
                target.after(0, _runner)
                ev.wait()
                return res[0]
        except Exception:
            pass

    if kind == "question" and kwargs.get("icon") == "warning":
        kind = "warning_question"

    play_calm_tone(kind)

    root_window = parent or getattr(tk, "_default_root", None)

    dlg = tk.Toplevel(root_window)
    dlg.title(str(title))
    dlg.configure(bg=BG_WINDOW)
    dlg.resizable(False, False)

    if root_window and root_window.winfo_exists():
        dlg.transient(root_window)
    dlg.attributes("-topmost", True)

    # Style by kind
    if kind == "error":
        badge_text = "✖  ERROR"
        badge_fg = "#f87171"
        badge_bg = "#2b1418"
        icon_glyph = "✖"
        icon_color = "#ef4444"
        accent_btn = "#ef4444"
    elif kind in ("warning", "warning_question"):
        badge_text = "⚠  CRITICAL WARNING" if kind == "warning_question" else "⚠  WARNING"
        badge_fg = "#fbbf24"
        badge_bg = "#2e210a"
        icon_glyph = "⚠"
        icon_color = "#f59e0b"
        accent_btn = ACCENT_ORANGE
    elif kind == "question":
        badge_text = "❓  CONFIRMATION"
        badge_fg = "#38bdf8"
        badge_bg = "#0e2338"
        icon_glyph = "❓"
        icon_color = "#38bdf8"
        accent_btn = ACCENT_ORANGE
    else:  # info / success
        badge_text = "✔  NOTIFICATION"
        badge_fg = "#4ade80"
        badge_bg = "#0f2918"
        icon_glyph = "✔"
        icon_color = "#22c55e"
        accent_btn = "#2563eb"

    result = [False]

    def on_confirm():
        result[0] = True
        try:
            dlg.grab_release()
        except Exception:
            pass
        dlg.destroy()

    def on_cancel():
        result[0] = False
        try:
            dlg.grab_release()
        except Exception:
            pass
        dlg.destroy()

    # Outer border wrapper
    outer = tk.Frame(dlg, bg=BG_BORDER, padx=1, pady=1)
    outer.pack(fill="both", expand=True)

    main_f = tk.Frame(outer, bg=BG_WINDOW)
    main_f.pack(fill="both", expand=True)

    # Header Bar
    head = tk.Frame(main_f, bg=BG_CARD_ROW, padx=14, pady=8)
    head.pack(fill="x")

    # Pill badge
    pill = tk.Frame(head, bg=badge_bg, padx=8, pady=2, highlightbackground=badge_fg, highlightthickness=1)
    pill.pack(side="left")
    tk.Label(pill, text=badge_text, font=("Segoe UI", 10, "bold"), fg=badge_fg, bg=badge_bg).pack()

    # Title
    tk.Label(head, text=f"  {title}", font=("Segoe UI", 11, "bold"), fg=FG_WHITE, bg=BG_CARD_ROW).pack(side="left")

    # Body frame
    body = tk.Frame(main_f, bg=BG_CARD, padx=18, pady=16)
    body.pack(fill="both", expand=True)

    # Left Icon box
    icon_box = tk.Frame(body, bg="#11141c", width=42, height=42, highlightbackground=icon_color, highlightthickness=1)
    icon_box.pack_propagate(False)
    icon_box.pack(side="left", padx=(0, 14), anchor="n")
    tk.Label(icon_box, text=icon_glyph, font=("Segoe UI", 16, "bold"), fg=icon_color, bg="#11141c").pack(expand=True)

    # Message text
    msg_box = tk.Frame(body, bg=BG_CARD)
    msg_box.pack(side="left", fill="both", expand=True)
    tk.Label(msg_box, text=str(message), font=("Segoe UI", 9), fg="#e2e8f0", bg=BG_CARD,
             justify="left", wraplength=440).pack(anchor="w")

    # Bottom action bar
    bottom = tk.Frame(main_f, bg=BG_WINDOW, padx=14, pady=10)
    bottom.pack(fill="x")

    btn_row = tk.Frame(bottom, bg=BG_WINDOW)
    btn_row.pack(side="right")

    is_question = kind in ("question", "warning_question")
    if is_question:
        confirm_text = "  ✔ Force Delete  " if "force delete" in str(message).lower() else "  ✔ Yes, Proceed  "
        b_confirm = tk.Button(btn_row, text=confirm_text, font=("Segoe UI", 10, "bold"),
                              fg="#ffffff", bg=accent_btn, activebackground="#ea580c",
                              activeforeground="#ffffff", relief="flat", padx=16, pady=6,
                              cursor="hand2", command=on_confirm)
        b_confirm.pack(side="left", padx=4)

        b_cancel = tk.Button(btn_row, text="  Cancel  ", font=("Segoe UI", 10, "bold"),
                             fg="#cbd5e1", bg="#1e2430", activebackground="#2a3245",
                             activeforeground="#ffffff", relief="flat", padx=16, pady=6,
                             cursor="hand2", command=on_cancel)
        b_cancel.pack(side="left", padx=4)

        dlg.bind("<Return>", lambda e: on_confirm())
        dlg.bind("<Escape>", lambda e: on_cancel())
    else:
        b_ok = tk.Button(btn_row, text="OK", font=("Segoe UI", 10, "bold"),
                         fg="#ffffff", bg=accent_btn,
                         activebackground="#1d4ed8" if accent_btn == "#2563eb" else "#ea580c",
                         activeforeground="#ffffff", relief="flat", padx=20, pady=6,
                         cursor="hand2", command=on_confirm)
        b_ok.pack(side="left")

        dlg.bind("<Return>", lambda e: on_confirm())
        dlg.bind("<Escape>", lambda e: on_confirm())

    dlg.protocol("WM_DELETE_WINDOW", on_cancel if is_question else on_confirm)

    dlg.update_idletasks()
    req_w = max(440, min(580, dlg.winfo_reqwidth()))
    req_h = max(160, dlg.winfo_reqheight())
    center_window_on_parent(dlg, parent=root_window, req_w=req_w, req_h=req_h)
    dlg.deiconify()

    if is_question:
        b_confirm.focus_set()
    else:
        b_ok.focus_set()

    try:
        dlg.grab_set()
        dlg.wait_window()
    finally:
        try:
            dlg.grab_release()
        except Exception:
            pass
        try:
            if root_window and root_window.winfo_exists():
                root_window.focus_set()
        except Exception:
            pass

    return result[0]

class CustomMessageBox:
    @staticmethod
    def showinfo(title, message, **kwargs):
        return show_custom_modal(title=title, message=message, kind="info", **kwargs)

    @staticmethod
    def showwarning(title, message, **kwargs):
        return show_custom_modal(title=title, message=message, kind="warning", **kwargs)

    @staticmethod
    def showerror(title, message, **kwargs):
        return show_custom_modal(title=title, message=message, kind="error", **kwargs)

    @staticmethod
    def askyesno(title, message, **kwargs):
        return show_custom_modal(title=title, message=message, kind="question", **kwargs)

messagebox = CustomMessageBox

class CS2TruePanoramaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        # Immediately withdraw to prevent Windows from registering the default Tk feather icon on the taskbar
        self.withdraw()
        self.title("CS2 Command Center")
        self.geometry("1280x860")
        self.minsize(1200, 800)
        self.configure(bg=BG_WINDOW)

        # Smooth interactive window resize debouncing & timer throttling
        self._is_resizing = False
        self._resize_timer = None
        self._last_root_w = 1280
        self._last_root_h = 860
        self._last_window_state = "zoomed"

        def _on_root_configure(e):
            if e.widget == self:
                try:
                    curr_st = self.state()
                    if curr_st in ("normal", "zoomed"):
                        self._last_window_state = curr_st
                except Exception:
                    pass
                if getattr(self, "_last_root_w", 0) != e.width or getattr(self, "_last_root_h", 0) != e.height:
                    self._last_root_w = e.width
                    self._last_root_h = e.height
                    self._is_resizing = True
                    if getattr(self, "_resize_timer", None):
                        try:
                            self.after_cancel(self._resize_timer)
                        except Exception:
                            pass
                    def _end_resize():
                        self._is_resizing = False
                        self._resize_timer = None
                        if hasattr(self, "_sync_active_page_layout"):
                            self._sync_active_page_layout()
                    self._resize_timer = self.after(120, _end_resize)

        self.bind("<Configure>", _on_root_configure)

        # Set authentic CS2 Command Center window & taskbar icon
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        ico_path = os.path.join(base_dir, "app.ico")
        png_path = os.path.join(base_dir, "app.png")
        if not os.path.exists(ico_path):
            ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.ico")
        if not os.path.exists(png_path):
            png_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.png")

        # Native Tkinter application-level icon overrides default feather
        if os.path.exists(png_path):
            try:
                self._app_icon_photo = tk.PhotoImage(file=png_path)
                self.iconphoto(True, self._app_icon_photo)
            except Exception:
                pass

        if os.path.exists(ico_path):
            try:
                self.iconbitmap(ico_path)
            except Exception:
                pass

        self._apply_win32_icons()

        # Load persisted application config
        self.config = app_config.load_config()

        # Window control behavior:
        # Clicking [X] exits completely; clicking [-] minimizes to system tray
        self.protocol("WM_DELETE_WINDOW", self.exit_application)
        self.bind("<Unmap>", self._on_window_unmap)

        # Configure Modern CS2 Panorama ttk Styles
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        try:
            self.style.layout("Vertical.Dark.TScrollbar", self.style.layout("Vertical.TScrollbar"))
            self.style.configure(
                "Vertical.Dark.TScrollbar",
                gripcount=0,
                background="#242b3b",
                darkcolor="#121620",
                lightcolor="#121620",
                troughcolor="#0c0e14",
                bordercolor="#121620",
                arrowcolor="#94a3b8"
            )
            self.style.map(
                "Vertical.Dark.TScrollbar",
                background=[("active", ACCENT_ORANGE), ("pressed", ACCENT_ORANGE_HOVER)],
                arrowcolor=[("active", "#ffffff")]
            )
        except Exception:
            pass

        # High-Contrast CS2 Panorama Dark Theme for ttk.Combobox
        try:
            self.option_add("*TCombobox*Listbox.background", "#141822")
            self.option_add("*TCombobox*Listbox.foreground", "#f8fafc")
            self.option_add("*TCombobox*Listbox.selectBackground", ACCENT_ORANGE)
            self.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
            self.option_add("*TCombobox*Listbox.font", ("Segoe UI", 9))
            self.option_add("*TCombobox*Listbox.relief", "flat")
            self.option_add("*TCombobox*Listbox.highlightThickness", "1")
            self.option_add("*TCombobox*Listbox.highlightColor", BG_BORDER)

            self.style.configure(
                "TCombobox",
                fieldbackground="#141822",
                background="#1e2638",
                foreground="#f8fafc",
                darkcolor="#141822",
                lightcolor="#1e2638",
                bordercolor=BG_BORDER,
                arrowcolor="#38bdf8",
                arrowsize=12,
                padding=4
            )
            self.style.map(
                "TCombobox",
                fieldbackground=[("readonly", "#141822"), ("focus", "#1a2234"), ("disabled", "#0f131a")],
                background=[("readonly", "#1e2638"), ("focus", "#253248"), ("active", "#253248")],
                foreground=[("readonly", "#f8fafc"), ("focus", "#ffffff"), ("disabled", "#64748b")],
                arrowcolor=[("readonly", "#38bdf8"), ("active", "#60a5fa")]
            )
        except Exception:
            pass

        # Hardware & Paths
        self.paths = core_logic.find_cs2_paths()
        self.admin_status = core_logic.is_admin()
        self.cpu_info = hardware_info.get_cpu_info()
        self.gpu_info = hardware_info.get_gpu_info()
        
        launch_opts, self.vdf_path = hardware_info.get_current_launch_options(self.paths["steam_path"])
        self.launch_analysis = hardware_info.analyze_launch_options(launch_opts or "")
        self.active_plan_name, _ = core_logic.get_active_power_plan()

        # Checkbox states (One-Click CS2 Optimize)
        self.opt_shaders = tk.BooleanVar(value=True)
        self.opt_cs2_dumps = tk.BooleanVar(value=True)
        self.opt_gamedvr = tk.BooleanVar(value=True)
        self.opt_fullscreen = tk.BooleanVar(value=True)
        self.opt_autoexec = tk.BooleanVar(value=True)
        self.opt_power = tk.BooleanVar(value=False)
        self.selected_power_plan = tk.StringVar(value=self.cpu_info["recommended_power_plan"])

        # Checkbox states (Safe PC Maintenance)
        self.maint_temp = tk.BooleanVar(value=True)
        self.maint_win_update = tk.BooleanVar(value=True)
        self.maint_discord_steam = tk.BooleanVar(value=True)
        self.maint_thumb = tk.BooleanVar(value=True)
        self.maint_recycle = tk.BooleanVar(value=False)
        self.maint_dns = tk.BooleanVar(value=True)

        # Server Connect & Delay state (Zombie Escape Hub)
        self.server_browser = server_browser
        self.connect_delay = tk.IntVar(value=15)
        self.servers_data = server_browser.load_servers()
        self.china_clusters = server_browser.CHINA_CLUSTERS
        self.current_china_index = 0
        self.server_active_subtab = "GLOBAL"
        self.server_query_cache = {}
        self.gfl_status_text = tk.StringVar(value="Querying live GFL status...")
        self.gfl_workflow_status = tk.StringVar(value="Status: Ready to connect")

        # ZE Graph Live Telemetry & Multimedia Variables
        self.gfl_score_var = tk.StringVar(value="🛡️ Humans: -  vs  🧟 Zombies: -")
        self.gfl_extends_var = tk.StringVar(value="⏱️ Extends: -/3")
        self.gfl_timer_var = tk.StringVar(value="⏱️ --:-- on map")
        self.gfl_geo_var = tk.StringVar(value="🌐 GEO: 🇺🇸 US 54% • 🇨🇦 CA 26% • 🇲🇽 MX 11%")
        self.server_map_start_timestamps = {}
        self.server_last_known_maps = {}
        self.gfl_map_start_timestamp = 0
        self.current_gfl_clean_map = "ze_resident_evil_3"
        self.loaded_thumbnails = {}
        self.loaded_thumbnails_small = {}
        raw_comm_target = self.config.get("community_sniper_slot_target", "≤ 63 / 64 (1 Reserved)")
        if "61" in raw_comm_target:
            init_target = "≤ 61 / 64 (3 Reserved)"
        elif "62" in raw_comm_target:
            init_target = "≤ 62 / 64 (2 Reserved)"
        else:
            init_target = "≤ 63 / 64 (1 Reserved)"
        self.comm_sniper_target_var = tk.StringVar(value=init_target)
        self.server_search_var = tk.StringVar()

        # Slot Sniper & Discord State
        self.sniper = server_browser.get_slot_sniper()
        self.discord_rpc = discord_rpc.get_discord_rpc()
        self.server_sniper_buttons = {}
        self.active_sniper_target = None
        self.active_tracked_server = None  # (host, port, server_name)
        self.discord_session_start = int(time.time())
        self.discord_preview_details = tk.StringVar(value="In Main Menu • Standby")
        self.discord_preview_state = tk.StringVar(value="CS2 Command Center")
        self.discord_preview_elapsed = tk.StringVar(value="⏱ 00:00 elapsed")
        self.discord_preview_btn1 = tk.StringVar(value="🎮 Server: 74.91.124.21:27015")
        self.discord_preview_btn2 = tk.StringVar(value="")

        # Automatic CS2 GSI & Process State
        self.cs2_was_running = False
        self.gsi_latest_state = {}
        self._last_gsi_logged_act = None
        self._last_gsi_logged_map = None
        self._last_gsi_log_time = 0.0
        if self.paths.get("cfg_dir"):
            try:
                cs2_gsi.ensure_gsi_config_installed(self.paths["cfg_dir"])
            except Exception:
                pass
        self.gsi_server = cs2_gsi.get_gsi_server(on_state_update=self._on_gsi_state_update)
        try:
            self.gsi_server.start()
        except Exception:
            pass

        # Inter-process single instance restore event listener
        self._quitting = False
        kernel32 = ctypes.windll.kernel32
        self.h_show_event = kernel32.CreateEventW(None, False, False, SINGLE_INSTANCE_EVENT_NAME)
        if self.h_show_event:
            def _listen_for_show_event():
                while not getattr(self, "_quitting", False):
                    res = kernel32.WaitForSingleObject(self.h_show_event, 500)
                    if res == 0:  # WAIT_OBJECT_0
                        self.after(0, self.restore_from_tray)
            threading.Thread(target=_listen_for_show_event, daemon=True).start()

        # Navigation state
        self.nav_items = {}
        self.pages = {}
        self.current_page_key = None

        self._build_ui()
        self._init_system_tray()
        self._initial_status_check()
        self._start_presence_heartbeat()
        self.bind_all("<MouseWheel>", self._on_global_mousewheel)
        self.after(1000, self._tick_discord_elapsed_timer)

    def safe_after(self, ms: int, func):
        """Thread-safe and shutdown-safe wrapper around tkinter after()."""
        try:
            if not getattr(self, "_quitting", False) and self.winfo_exists():
                return self.after(ms, func)
        except Exception:
            pass
        return None

    def _create_tray_image(self):
        """Loads or generates crisp CS2 badge icon for Windows system tray."""
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        png_path = os.path.join(base_dir, "app.png")
        if not os.path.exists(png_path):
            png_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.png")
        if os.path.exists(png_path):
            try:
                return Image.open(png_path).resize((64, 64), Image.Resampling.LANCZOS)
            except Exception:
                pass
        img = Image.new("RGBA", (64, 64), color=(0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse((4, 4, 60, 60), fill="#de6c11", outline="#ffffff", width=2)
        d.text((16, 22), "CS2", fill="#ffffff")
        return img

    def _init_system_tray(self):
        """Runs the background notification area icon."""
        try:
            img = self._create_tray_image()
            menu = pystray.Menu(
                pystray.MenuItem("Open CS2 Command Center", lambda icon, item: self.after(0, self.restore_from_tray), default=True),
                pystray.MenuItem("🚀 Quick Connect: GFL ZE", lambda icon, item: self.after(0, lambda: self.run_connect_workflow("74.91.124.21", 27015, "GFL Clan Zombie Escape"))),
                pystray.MenuItem("🎯 Slot Sniper: Toggle GFL", lambda icon, item: self.after(0, self.toggle_gfl_slot_sniper)),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Start with Windows", lambda icon, item: self.after(0, self._tray_toggle_startup), checked=lambda item: self.config.get("start_with_windows", False)),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("❌ Exit Completely", lambda icon, item: self.after(0, self.exit_application))
            )
            self.tray_icon = pystray.Icon("CS2CommandCenter", img, "CS2 Command Center", menu)
            self.tray_icon.run_detached()
        except Exception:
            self.tray_icon = None

    def _apply_win32_icons(self):
        """Applies CS2 Command Center icons directly to Win32 HWND and class handles."""
        try:
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            ico_path = os.path.join(base_dir, "app.ico")
            if not os.path.exists(ico_path):
                ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.ico")
            if os.path.exists(ico_path):
                import ctypes
                from ctypes import wintypes
                user32 = ctypes.windll.user32
                user32.LoadImageW.restype = wintypes.HANDLE
                user32.LoadImageW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT, ctypes.c_int, ctypes.c_int, wintypes.UINT]
                abs_ico = os.path.abspath(ico_path)
                h_big = user32.LoadImageW(None, abs_ico, 1, 32, 32, 0x0010)
                h_small = user32.LoadImageW(None, abs_ico, 1, 16, 16, 0x0010)
                hwnd = self.winfo_id()
                root_hwnd = user32.GetAncestor(hwnd, 2)
                for h in (hwnd, root_hwnd):
                    if h:
                        user32.SendMessageW(h, 0x0080, 1, h_big)    # WM_SETICON, ICON_BIG
                        user32.SendMessageW(h, 0x0080, 0, h_small)  # WM_SETICON, ICON_SMALL
                        try:
                            if hasattr(user32, 'SetClassLongPtrW'):
                                user32.SetClassLongPtrW(h, -14, h_big)   # GCLP_HICON
                                user32.SetClassLongPtrW(h, -34, h_small) # GCLP_HICONSM
                            elif hasattr(user32, 'SetClassLongW'):
                                user32.SetClassLongW(h, -14, h_big)
                                user32.SetClassLongW(h, -34, h_small)
                        except Exception:
                            pass
        except Exception:
            pass

    def restore_from_tray(self):
        """Un-minimizes and brings CS2 Command Center window to foreground."""
        self.deiconify()
        target_state = getattr(self, "_last_window_state", "zoomed")
        try:
            self.state(target_state)
        except Exception:
            try:
                self.state("zoomed")
            except Exception:
                self.state("normal")
        self.lift()
        self.attributes("-topmost", True)
        self.after_idle(self.attributes, "-topmost", False)
        self.after(20, self._apply_win32_icons)
        self.focus_force()

    def _on_window_unmap(self, event):
        """Clicking [-] (minimize) hides the window to the system tray.
        Taskbar clicks minimize normally to the taskbar without withdrawing to tray."""
        if event.widget == self and self.state() == "iconic" and not getattr(self, "_quitting", False):
            if not self.config.get("minimize_to_tray_on_close", True):
                return
            
            # Check if minimize was triggered by clicking the [-] button on the window titlebar vs taskbar
            try:
                py = self.winfo_pointery()
                screen_h = self.winfo_screenheight()
                # Windows taskbar is docked at the very bottom of the screen (~48-60px high)
                # If cursor is at the bottom of the monitor, user clicked the Windows taskbar icon
                is_taskbar_click = (py >= screen_h - 65)
            except Exception:
                is_taskbar_click = False

            if not is_taskbar_click:
                self.withdraw()
    def on_window_close(self):
        """Triggered when user clicks [X] on title bar. Closes and exits the application completely."""
        self.exit_application()

    def exit_application(self):
        """Completely terminates background processes and closes app."""
        global _single_instance_mutex
        self._quitting = True
        try:
            import urllib.request
            req = urllib.request.Request(
                "https://geronimohq-telemetry.onrender.com/api/presence/heartbeat?is_cs2_running=false&is_steam_running=false&in_menu=false",
                headers={"User-Agent": "CS2CommandCenter/2.0"}
            )
            urllib.request.urlopen(req, timeout=1.5)
        except Exception:
            pass
        try:
            self.grab_release()
        except Exception:
            pass
        if hasattr(self, "h_show_event") and self.h_show_event:
            try:
                ctypes.windll.kernel32.CloseHandle(self.h_show_event)
                self.h_show_event = None
            except Exception:
                pass
        if _single_instance_mutex:
            try:
                ctypes.windll.kernel32.CloseHandle(_single_instance_mutex)
                _single_instance_mutex = None
            except Exception:
                pass
        if hasattr(self, "server_auto_refresh_job") and self.server_auto_refresh_job:
            try:
                self.after_cancel(self.server_auto_refresh_job)
            except Exception:
                pass
        try:
            if hasattr(self, "sniper") and self.sniper:
                self.sniper.stop()
        except Exception:
            pass
        try:
            if hasattr(self, "discord_rpc") and self.discord_rpc:
                self.discord_rpc.clear_activity()
                self.discord_rpc.close()
        except Exception:
            pass
        try:
            if hasattr(self, "gsi_server") and self.gsi_server:
                self.gsi_server.stop()
        except Exception:
            pass
        try:
            if hasattr(self, "tray_icon") and self.tray_icon:
                self.tray_icon.stop()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass
        os._exit(0)

    def _tray_toggle_startup(self):
        new_state = not self.config.get("start_with_windows", False)
        self.config["start_with_windows"] = new_state
        minimized = self.config.get("start_minimized", False)
        app_config.set_windows_startup(new_state, minimized)
        app_config.save_config(self.config)
        self.log(f"[SETTINGS] Run on Windows Startup: {'Enabled' if new_state else 'Disabled'}")

    def _build_ui(self):
        # 1. TOP HEADER (Concept 1 Style: Logo + Title on left, Status Pills & Settings on right)
        header = tk.Frame(self, bg=BG_WINDOW, padx=20, pady=12)
        header.pack(fill="x")

        head_left = tk.Frame(header, bg=BG_WINDOW)
        head_left.pack(side="left")

        # CS2 Logo badge
        logo_box = tk.Frame(head_left, bg=BG_WINDOW)
        logo_box.pack(side="left")
        tk.Label(logo_box, text="CS", font=("Segoe UI", 16, "bold"), fg=FG_WHITE, bg=BG_WINDOW).pack(side="left")
        tk.Label(logo_box, text="2", font=("Segoe UI", 16, "bold"), fg=ACCENT_ORANGE, bg=BG_WINDOW).pack(side="left")

        tk.Label(head_left, text=" | ", font=("Segoe UI", 14), fg="#334155", bg=BG_WINDOW).pack(side="left", padx=8)
        tk.Label(head_left, text="CS2 Command Center", font=("Segoe UI", 13, "bold"), fg=FG_WHITE, bg=BG_WINDOW).pack(side="left")
        tk.Label(head_left, text="  [Optimizer • ZE Servers • PC Maintenance]", font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_WINDOW).pack(side="left", padx=4)

        # Right-side Action Pills & Settings
        head_right = tk.Frame(header, bg=BG_WINDOW)
        head_right.pack(side="right")

        # Settings Button
        b_settings = tk.Button(head_right, text="⚙ Settings & Startup", font=("Segoe UI", 10), fg="#cbd5e1", bg="#181e2b",
                  activebackground="#242b3b", activeforeground="#ffffff", relief="flat", padx=10, pady=3,
                  cursor="hand2", command=self.open_settings_dialog)
        b_settings.pack(side="left", padx=(0, 6))
        add_tooltip(b_settings, "Configure Windows autostart, minimize-to-tray behavior, and Discord integration.")

        admin_txt = "ADMIN PERMISSIONS" if self.admin_status else "STANDARD PERMISSIONS"
        admin_col = ACCENT_GREEN if self.admin_status else "#f59e0b"
        admin_tip = "Running with Administrator privileges (Full access for system maintenance, TRIM, and latency diagnostics)." if self.admin_status else "Running with Standard user permissions (Safe CS2 autoexec and engine tweaks work 100%)."
        self._create_header_pill(head_right, admin_txt, admin_col, tooltip=admin_tip)

        cs2_found = bool(self.paths["cs2_exe"])
        cs2_txt = "CS2 GAME READY" if cs2_found else "CS2 NOT DETECTED"
        cs2_col = ACCENT_GREEN if cs2_found else ACCENT_RED
        cs2_tip = f"Counter-Strike 2 detected at {self.paths['cs2_exe']}" if cs2_found else "Counter-Strike 2 installation path could not be detected automatically."
        self._create_header_pill(head_right, cs2_txt, cs2_col, tooltip=cs2_tip)

        # Thin Horizontal Border below header
        tk.Frame(self, bg=BG_BORDER, height=1).pack(fill="x")

        # 2. MAIN BODY (Concept 1: Left Vertical Sidebar + Right Content Area)
        body = tk.Frame(self, bg=BG_WINDOW)
        body.pack(fill="both", expand=True)

        # LEFT SIDEBAR
        self.sidebar = tk.Frame(body, bg=BG_SIDEBAR, width=220, highlightbackground=BG_BORDER, highlightthickness=1)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="NAVIGATION", font=("Segoe UI", 10, "bold"), fg="#4b5563", bg=BG_SIDEBAR, padx=16, pady=10).pack(anchor="w")

        # RIGHT CONTENT AREA
        self.main_content = tk.Frame(body, bg=BG_WINDOW, padx=16, pady=12)
        self.main_content.pack(side="right", fill="both", expand=True)

        # Top Hardware Info Card (in Main Content)
        self._build_hardware_banner()

        # Bottom Activity Logs Console
        self._build_bottom_console()

        # Dynamic Content Container
        self.page_container = tk.Frame(self.main_content, bg=BG_CARD, highlightbackground=BG_BORDER, highlightthickness=1)
        self.page_container.pack(side="top", fill="both", expand=True, pady=(0, 6))

        # Populate Vertical Sidebar Navigation Items (Concept 1)
        self._add_nav_item("DASHBOARD", "⚡", "Dashboard", self._build_page_dashboard,
                           tooltip="CyberDeck Command Console: High-impact overview of system readiness, hardware telemetry, and quick optimization.")
        self._add_nav_item("ENGINE", "⚙", "Engine Tweaks", self._build_page_engine,
                           tooltip="Configure Direct-Flip, GPU shader cache purges, game DVR, and CPU power plans for maximum FPS.")

        # GPU MPO Diagnostics tab (Universally available for AMD, NVIDIA, and Intel)
        self._add_nav_item("OS_DIAGNOSTICS", "🖥️", "GPU MPO Diagnostics", self._build_page_os_diagnostics,
                           tooltip="Dedicated GPU Multi-Plane Overlay (MPO) troubleshooter: May help resolve Alt-Tab black screens, driver timeouts, and display stutter.")

        self._add_nav_item("AUTOEXEC", "📝", "Autoexec & Binds", self._build_page_autoexec,
                           tooltip="Inject sub-tick network rates, competitive audio clarity, and autoexec performance binds.")
        self._add_nav_item("LAUNCH", "🚀", "Launch Options", self._build_page_launch,
                           tooltip="Optimal CS2 launch options tuned specifically for your CPU architecture and thread topology.")
        self._add_nav_item("BOOST", "⚡", "Live Booster & DNS", self._build_page_boost,
                           tooltip="CS2 CPU process priority booster (standard Win32 priority) & Gaming DNS Benchmark/Optimizer.")
        self._add_nav_item("SERVERS", "🌐", "ZE Game Servers", self._build_page_servers,
                           tooltip="Direct-connect server browser and high-speed auto slot sniper for Global & Asian Zombie Escape communities.")
        self._add_nav_item("MAINTENANCE", "🧹", "PC Maintenance", self._build_page_maintenance,
                           tooltip="Weekly PC maintenance suite: SSD TRIM, Windows SFC file checker, DISM repair, and Custom ZE Map Cleaner.")
        self._add_nav_item("DISCORD", "🎮", "Discord Presence", self._build_page_discord,
                           tooltip="Automatic CS2 Discord Rich Presence showing live server, map, and player counts via local named pipe IPC.")
        self._add_nav_item("FAQ", "📖", "Help & FAQ Guide", self._build_page_faq,
                           tooltip="Knowledge base and troubleshooting guide for all optimizer tweaks and competitive settings.")

        # Set default active page
        self._select_nav("DASHBOARD")

        # Open maximized (fullscreen) by default as requested by Geronimo
        if "--minimized" not in sys.argv:
            try:
                self.state("zoomed")
            except Exception:
                pass
            self.deiconify()
            self.after(20, self._apply_win32_icons)

    def _create_header_pill(self, parent, text, color, tooltip=None):
        pill = tk.Frame(parent, bg=BG_BORDER, padx=1, pady=1)
        pill.pack(side="left", padx=4)
        inner = tk.Frame(pill, bg="#11141c", padx=10, pady=3)
        inner.pack()
        lbl = tk.Label(inner, text=f"● {text}", font=("Segoe UI", 10, "bold"), fg=color, bg="#11141c")
        lbl.pack()
        if tooltip:
            add_tooltip(pill, tooltip)
            add_tooltip(inner, tooltip)
            add_tooltip(lbl, tooltip)

    def _build_hardware_banner(self):
        hw_banner = tk.Frame(self.main_content, bg=BG_CARD, padx=16, pady=10, highlightbackground=BG_BORDER, highlightthickness=1)
        hw_banner.pack(fill="x", pady=(0, 10))

        left = tk.Frame(hw_banner, bg=BG_CARD)
        left.pack(side="left", fill="both", expand=True)

        cpu_tag = " [3D V-Cache Detected]" if self.cpu_info["is_x3d"] else (" [Mobile]" if self.cpu_info["is_laptop"] else "")
        tk.Label(left, text=f"PROCESSOR:  {self.cpu_info['name']}{cpu_tag}", font=("Segoe UI", -14, "bold"), fg=FG_WHITE, bg=BG_CARD).pack(anchor="w")

        tk.Label(left, text=f"GRAPHICS:  {self.gpu_info['name']}", font=("Segoe UI", -14, "bold"), fg=ACCENT_CYAN, bg=BG_CARD).pack(anchor="w", pady=(2, 2))

        prof_lbl = tk.Label(left, text=f"⚡ Profile: {self.cpu_info['power_reason']}", font=("Segoe UI", -12, "italic"), fg=ACCENT_GREEN, bg=BG_CARD, justify="left", anchor="w")
        prof_lbl.pack(anchor="w", fill="x")
        def _adjust_prof_wrap(e):
            if e.width > 50:
                prof_lbl.config(wraplength=max(320, e.width - 15))
        left.bind("<Configure>", _adjust_prof_wrap)

        # Right Action Buttons
        right = tk.Frame(hw_banner, bg=BG_CARD)
        right.pack(side="right")

        b_opt = tk.Button(right, text="🚀 ONE-CLICK OPTIMIZE", font=("Segoe UI", 14, "bold"),
                  fg="#ffffff", bg=ACCENT_ORANGE, activebackground=ACCENT_ORANGE_HOVER,
                  activeforeground="#ffffff", relief="flat", padx=16, pady=6, cursor="hand2",
                  command=self.run_one_click_optimization)
        b_opt.pack(fill="x", pady=2)
        add_tooltip(b_opt, "Instantly applies all recommended engine optimizations, power profiles, and low-latency autoexec settings in one click.")

        b_rev = tk.Button(right, text="⏪ Restore Defaults", font=("Segoe UI", 10),
                  fg="#94a3b8", bg="#1c212c", activebackground="#272e3d",
                  activeforeground="#ffffff", relief="flat", padx=14, pady=6, cursor="hand2",
                  command=self.run_revert_all)
        b_rev.pack(fill="x", pady=2)
        add_tooltip(b_rev, "Safely reverts all engine tweaks, power schemes, and autoexec configurations back to default settings.")

    def _build_bottom_console(self):
        console_box = tk.Frame(self.main_content, bg=BG_WINDOW)
        console_box.pack(side="bottom", fill="x", pady=(4, 0))

        head = tk.Frame(console_box, bg=BG_WINDOW)
        head.pack(fill="x", pady=(0, 2))
        tk.Label(head, text="SYSTEM ACTIVITY LOGS", font=("Segoe UI", 14, "bold"), fg="#64748b", bg=BG_WINDOW).pack(side="left")

        tk.Button(head, text="Clear", font=("Segoe UI", 9), fg="#64748b", bg=BG_WINDOW,
                  relief="flat", cursor="hand2", command=self.clear_logs).pack(side="right")

        self.console = tk.Text(console_box, height=4, bg=BG_CONSOLE, fg=ACCENT_CYAN,
                               font=("Consolas", 10), relief="flat",
                               highlightbackground=BG_BORDER, highlightthickness=1, padx=8, pady=4)
        self.console.pack(fill="x")
        self.console.config(state="disabled")

        # Persistent CyberDeck Status Bar
        self.status_bar = tk.Frame(console_box, bg="#0a0d14", highlightbackground=BG_BORDER, highlightthickness=1, padx=10, pady=3)
        self.status_bar.pack(fill="x", pady=(3, 0))

        cs2_found = bool(self.paths.get("cs2_exe"))
        cs2_text = "CS2: GAME READY" if cs2_found else "CS2: NOT DETECTED"
        cs2_col = ACCENT_GREEN if cs2_found else ACCENT_RED
        self.status_cs2_lbl = tk.Label(self.status_bar, text=f"● {cs2_text}", font=("Segoe UI", 9, "bold"), fg=cs2_col, bg="#0a0d14")
        self.status_cs2_lbl.pack(side="left", padx=(0, 15))

        self.status_sniper_lbl = tk.Label(self.status_bar, text="● SLOT SNIPER: IDLE", font=("Segoe UI", 9, "bold"), fg=FG_MUTED, bg="#0a0d14")
        self.status_sniper_lbl.pack(side="left", padx=15)

        self.status_dns_lbl = tk.Label(self.status_bar, text="● GAMING DNS: ACTIVE", font=("Segoe UI", 9, "bold"), fg=ACCENT_CYAN, bg="#0a0d14")
        self.status_dns_lbl.pack(side="left", padx=15)

        self.status_vac_lbl = tk.Label(self.status_bar, text="● 100% VAC-SAFE", font=("Segoe UI", 9, "bold"), fg=ACCENT_GREEN, bg="#0a0d14")
        self.status_vac_lbl.pack(side="right")

    def _add_nav_item(self, key, icon, title, builder_func, is_alert=False, tooltip=None):
        item_frame = tk.Frame(self.sidebar, bg=BG_SIDEBAR, cursor="hand2")
        item_frame.pack(fill="x", pady=1)

        strip = tk.Frame(item_frame, bg=BG_SIDEBAR, width=4)
        strip.pack(side="left", fill="y")

        lbl_fg = ACCENT_RED if is_alert else "#94a3b8"

        # Fixed pixel width container for icon so all titles start at the exact same horizontal column
        icon_frame = tk.Frame(item_frame, bg=BG_SIDEBAR, width=28, height=36)
        icon_frame.pack_propagate(False)
        icon_frame.pack(side="left", padx=(8, 4))

        icon_box = tk.Label(icon_frame, text=icon, font=("Segoe UI Emoji", 9),
                            fg=lbl_fg, bg=BG_SIDEBAR)
        icon_box.place(relx=0.5, rely=0.5, anchor="center")

        title_lbl = tk.Label(item_frame, text=title, font=("Segoe UI", 9, "bold" if is_alert else "normal"),
                             fg=lbl_fg, bg=BG_SIDEBAR, anchor="w")
        title_lbl.pack(side="left", fill="both", expand=True, pady=10)

        def on_click(e=None):
            self._select_nav(key)

        def on_enter(e=None):
            if key != self.current_page_key:
                item_frame.configure(bg="#151b26")
                icon_frame.configure(bg="#151b26")
                icon_box.configure(bg="#151b26")
                title_lbl.configure(bg="#151b26")

        def on_leave(e=None):
            if key != self.current_page_key:
                item_frame.configure(bg=BG_SIDEBAR)
                icon_frame.configure(bg=BG_SIDEBAR)
                icon_box.configure(bg=BG_SIDEBAR)
                title_lbl.configure(bg=BG_SIDEBAR)

        for w in (item_frame, strip, icon_frame, icon_box, title_lbl):
            w.bind("<Button-1>", on_click)
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

        if tooltip:
            add_tooltip(item_frame, tooltip)
            add_tooltip(icon_box, tooltip)
            add_tooltip(title_lbl, tooltip)

        self.nav_items[key] = {
            "frame": item_frame,
            "strip": strip,
            "icon_frame": icon_frame,
            "icon": icon_box,
            "label": title_lbl,
            "is_alert": is_alert,
            "builder": builder_func
        }

    def _select_nav(self, key):
        self.current_page_key = key
        for k, item in self.nav_items.items():
            if k == key:
                active_strip_col = ACCENT_RED if item["is_alert"] else ACCENT_ORANGE
                item["frame"].configure(bg=BG_SIDEBAR_ACTIVE)
                item["strip"].configure(bg=active_strip_col)
                if "icon_frame" in item:
                    item["icon_frame"].configure(bg=BG_SIDEBAR_ACTIVE)
                item["icon"].configure(bg=BG_SIDEBAR_ACTIVE, fg=ACCENT_RED if item["is_alert"] else ACCENT_ORANGE)
                item["label"].configure(bg=BG_SIDEBAR_ACTIVE, fg=ACCENT_RED if item["is_alert"] else FG_WHITE)
            else:
                item["frame"].configure(bg=BG_SIDEBAR)
                item["strip"].configure(bg=BG_SIDEBAR)
                if "icon_frame" in item:
                    item["icon_frame"].configure(bg=BG_SIDEBAR)
                item["icon"].configure(bg=BG_SIDEBAR, fg=ACCENT_RED if item["is_alert"] else "#94a3b8")
                item["label"].configure(bg=BG_SIDEBAR, fg=ACCENT_RED if item["is_alert"] else "#94a3b8")

        # Lazy load page on first click for near-instant (<150ms) app startup
        if key not in self.pages:
            page = tk.Frame(self.page_container, bg=BG_CARD, padx=18, pady=12)
            self.pages[key] = page
            self.nav_items[key]["builder"](page)
        elif key == "OS_DIAGNOSTICS" and hasattr(self, "_refresh_os_diagnostics"):
            self._refresh_os_diagnostics()
        elif key in ("ENGINE", "MAINTENANCE") and hasattr(self, "_refresh_weekly_maint_banner"):
            self._refresh_weekly_maint_banner()
        elif key == "SERVERS" and hasattr(self, "_start_server_auto_refresh_loop"):
            self._start_server_auto_refresh_loop()

        for k, p in self.pages.items():
            if k == key:
                p.pack(fill="both", expand=True)
            else:
                p.pack_forget()

        self.after_idle(self._sync_active_page_layout)

    def _bind_canvas_auto_width(self, canvas, c_window, scrollbar):
        """Throttles canvas itemconfig width adjustments during interactive window resizing to eliminate UI stutter."""
        def _on_configure(e):
            if getattr(canvas, "_last_w", None) == e.width:
                return
            canvas._last_w = e.width
            timer_id = f"_cw_timer_{id(canvas)}"
            existing = getattr(self, timer_id, None)
            if existing:
                try:
                    self.after_cancel(existing)
                except Exception:
                    pass
            def _apply():
                setattr(self, timer_id, None)
                try:
                    canvas.itemconfig(c_window, width=e.width)
                    self._debounce_sync_scroll(canvas, scrollbar, delay_ms=60)
                except Exception:
                    pass
            setattr(self, timer_id, self.after(70, _apply))
        canvas.bind("<Configure>", _on_configure)

    def _sync_canvas_scroll(self, canvas, scrollbar):
        """Updates scrollregion reliably without unmapping scrollbar or causing layout oscillation."""
        try:
            bbox = canvas.bbox("all")
            if not bbox:
                return
            content_h = bbox[3] - bbox[1]
            view_h = canvas.winfo_height()
            canvas.configure(scrollregion=(0, 0, bbox[2], max(content_h, view_h + 20)))
        except Exception:
            pass

    def _debounce_sync_scroll(self, canvas, scrollbar, delay_ms: int = 70):
        """Debounces scroll and geometry recalculations to eliminate window resizing lag."""
        timer_id = f"_scroll_timer_{id(canvas)}"
        existing = getattr(self, timer_id, None)
        if existing:
            try:
                self.after_cancel(existing)
            except Exception:
                pass
        def _execute():
            setattr(self, timer_id, None)
            self._sync_canvas_scroll(canvas, scrollbar)
        setattr(self, timer_id, self.after(delay_ms, _execute))

    def _on_global_mousewheel(self, e):
        """Universal, rock-solid mousewheel handler across all application pages."""
        try:
            widget = e.widget
            if isinstance(widget, (tk.Text, ttk.Treeview, tk.Listbox)):
                return
            toplevel = widget.winfo_toplevel()
            if toplevel != self:
                return
            key = getattr(self, "current_page_key", "")
            canvas_map = {
                "ENGINE": getattr(self, "engine_canvas", None),
                "SERVERS": getattr(self, "server_canvas", None),
                "BOOST": getattr(self, "boost_canvas", None),
                "MAINTENANCE": getattr(self, "maint_canvas", None),
                "LAUNCH": getattr(self, "launch_canvas", None),
                "DISCORD": getattr(self, "discord_canvas", None),
                "OS_DIAGNOSTICS": getattr(self, "os_diag_canvas", None),
                "FAQ": getattr(self, "faq_canvas", None),
            }
            canvas = canvas_map.get(key)
            if canvas and canvas.winfo_exists():
                self._handle_canvas_wheel(e, canvas)
                return "break"
        except Exception:
            pass

    def _handle_canvas_wheel(self, e, canvas):
        """Unified mousewheel handler with smooth scrolling."""
        try:
            delta = int(-1 * (e.delta / 120))
            # Smooth scrolling step (60px with yscrollincrement=1)
            canvas.yview_scroll(delta * 60, "units")
        except Exception:
            pass
        return "break"

    def _sync_active_page_layout(self):
        """Invoked when navigating between tabs to ensure geometry, wrapping, and scroll state are clean."""
        key = getattr(self, "current_page_key", "")
        if key == "ENGINE" and hasattr(self, "engine_canvas") and hasattr(self, "engine_scrollbar"):
            self._sync_canvas_scroll(self.engine_canvas, self.engine_scrollbar)
        elif key == "LAUNCH" and hasattr(self, "launch_canvas") and hasattr(self, "launch_scrollbar"):
            self._sync_canvas_scroll(self.launch_canvas, self.launch_scrollbar)
        elif key == "BOOST":
            self._apply_boost_wraps()
        elif key == "SERVERS" and hasattr(self, "server_canvas") and hasattr(self, "server_scrollbar"):
            self._sync_canvas_scroll(self.server_canvas, self.server_scrollbar)
        elif key == "MAINTENANCE" and hasattr(self, "maint_canvas") and hasattr(self, "maint_scrollbar"):
            self._sync_canvas_scroll(self.maint_canvas, self.maint_scrollbar)
        elif key == "DISCORD" and hasattr(self, "discord_canvas") and hasattr(self, "discord_scrollbar"):
            self._sync_canvas_scroll(self.discord_canvas, self.discord_scrollbar)
        elif key == "OS_DIAGNOSTICS" and hasattr(self, "os_diag_canvas") and hasattr(self, "os_diag_scrollbar"):
            self._sync_canvas_scroll(self.os_diag_canvas, self.os_diag_scrollbar)
        elif key == "FAQ" and hasattr(self, "faq_canvas") and hasattr(self, "faq_scrollbar"):
            self._sync_canvas_scroll(self.faq_canvas, self.faq_scrollbar)

    def _apply_boost_wraps(self):
        try:
            if hasattr(self, "boost_canvas") and hasattr(self, "boost_scrollbar"):
                self._sync_canvas_scroll(self.boost_canvas, self.boost_scrollbar)
            if hasattr(self, "_apply_boost_wraps_func"):
                self._apply_boost_wraps_func()
            elif hasattr(self, "boost_info_card") and self.boost_info_card.winfo_exists():
                card_w = self.boost_info_card.winfo_width()
                if card_w < 100 and hasattr(self, "page_container"):
                    card_w = self.page_container.winfo_width()
                avail = max(450, card_w - 60)
                for lbl in getattr(self, "boost_wrap_labels", []):
                    if lbl.winfo_exists():
                        lbl.config(wraplength=avail, anchor="w", justify="left")
        except Exception:
            pass

    # --- PAGES ---

    def _build_page_dashboard(self, page):
        canvas = tk.Canvas(page, bg=BG_CARD, highlightthickness=0, yscrollincrement=1)
        scrollbar = ttk.Scrollbar(page, orient="vertical", command=canvas.yview, style="Vertical.Dark.TScrollbar")
        self.dashboard_canvas = canvas
        self.dashboard_scrollbar = scrollbar
        content = tk.Frame(canvas, bg=BG_CARD)

        content.bind(
            "<Configure>",
            lambda e: self._debounce_sync_scroll(canvas, scrollbar)
        )
        c_window = canvas.create_window((0, 0), window=content, anchor="nw")
        self._bind_canvas_auto_width(canvas, c_window, scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def _bind_dash_wheel(widget):
            widget.bind("<MouseWheel>", lambda e: self._handle_canvas_wheel(e, canvas), add="+")
            for ch in widget.winfo_children():
                _bind_dash_wheel(ch)

        # Tier 1 Main Tab Title
        t1_box = tk.Frame(content, bg=BG_CARD)
        t1_box.pack(fill="x", pady=(4, 12))
        tk.Label(t1_box, text="⚡ SYSTEM READINESS & CYBERDECK DASHBOARD", font=("Segoe UI", 16, "bold"), fg=FG_WHITE, bg=BG_CARD).pack(anchor="w")
        tk.Label(t1_box, text="Real-time Source 2 engine diagnostics, VAC-safe autoexec status, and live gaming telemetry.", font=("Segoe UI", 12), fg=FG_MUTED, bg=BG_CARD).pack(anchor="w", pady=(2, 0))

        # Hero Banner: One-Click Total Optimization
        hero = tk.Frame(content, bg="#0d131f", highlightbackground=ACCENT_CYAN, highlightthickness=1, padx=16, pady=14)
        hero.pack(fill="x", pady=(0, 14))

        hero_left = tk.Frame(hero, bg="#0d131f")
        hero_left.pack(side="left", fill="both", expand=True)

        tk.Label(hero_left, text="TACTICAL PERFORMANCE ENGINE", font=("Segoe UI", 13, "bold"), fg=ACCENT_CYAN, bg="#0d131f").pack(anchor="w")
        tk.Label(hero_left, text="One-click tunes CS2 sub-tick rates, low-latency sleep, CPU power profile, and competitive audio binds.", font=("Segoe UI", 12), fg="#cbd5e1", bg="#0d131f").pack(anchor="w", pady=(2, 6))

        pills = tk.Frame(hero_left, bg="#0d131f")
        pills.pack(anchor="w")
        for p_txt, p_col in [("100% VAC-SAFE", ACCENT_GREEN), ("SUB-TICK VERIFIED", ACCENT_CYAN), ("ZERO RUNTIME OVERHEAD", ACCENT_AMBER)]:
            pf = tk.Frame(pills, bg="#162032", padx=8, pady=2, highlightbackground="#24334d", highlightthickness=1)
            pf.pack(side="left", padx=(0, 6))
            tk.Label(pf, text=f"✔ {p_txt}", font=("Segoe UI", 11, "bold"), fg=p_col, bg="#162032").pack()

        hero_right = tk.Frame(hero, bg="#0d131f")
        hero_right.pack(side="right", padx=(10, 0))

        b_hero_opt = tk.Button(hero_right, text="🚀 ONE-CLICK OPTIMIZE", font=("Segoe UI", 14, "bold"),
                               fg="#ffffff", bg=ACCENT_ORANGE, activebackground=ACCENT_ORANGE_HOVER,
                               activeforeground="#ffffff", relief="flat", padx=20, pady=8, cursor="hand2",
                               command=self.run_one_click_optimization)
        b_hero_opt.pack(fill="x", pady=2)
        add_tooltip(b_hero_opt, "Executes complete engine optimization pass and verifies autoexec integrity.")

        # 3-Card Grid Overview
        grid = tk.Frame(content, bg=BG_CARD)
        grid.pack(fill="x", pady=(0, 14))

        # Card 1: CS2 Process & Path
        c1 = tk.Frame(grid, bg=BG_CARD_ROW, highlightbackground=BG_BORDER, highlightthickness=1, padx=14, pady=12)
        c1.pack(side="left", fill="both", expand=True, padx=(0, 6))
        tk.Label(c1, text="🎮 CS2 ENVIRONMENT", font=("Segoe UI", 13, "bold"), fg=ACCENT_GREEN, bg=BG_CARD_ROW).pack(anchor="w")
        cs2_st = "DETECTED & CONFIGURED" if bool(self.paths.get("cs2_exe")) else "MANUAL PATH REQUIRED"
        tk.Label(c1, text=f"Executable: {cs2_st}", font=("Segoe UI", 12), fg=FG_WHITE, bg=BG_CARD_ROW).pack(anchor="w", pady=(6, 2))
        auto_st = "autoexec.cfg ACTIVE" if bool(self.paths.get("autoexec_cfg")) else "autoexec.cfg NOT FOUND"
        tk.Label(c1, text=f"Config: {auto_st}", font=("Segoe UI", 12), fg=ACCENT_CYAN, bg=BG_CARD_ROW).pack(anchor="w", pady=(0, 6))
        b_c1 = tk.Button(c1, text="Open Config Studio ➔", font=("Segoe UI", -12, "bold"), fg="#ffffff", bg="#1e293b",
                         activebackground="#334155", relief="flat", padx=10, pady=4, cursor="hand2",
                         command=lambda: self._select_nav("AUTOEXEC"))
        b_c1.pack(anchor="w")

        # Card 2: Hardware Profile
        c2 = tk.Frame(grid, bg=BG_CARD_ROW, highlightbackground=BG_BORDER, highlightthickness=1, padx=14, pady=12)
        c2.pack(side="left", fill="both", expand=True, padx=6)
        tk.Label(c2, text="⚡ HARDWARE PROFILE", font=("Segoe UI", 13, "bold"), fg=ACCENT_CYAN, bg=BG_CARD_ROW).pack(anchor="w")
        tk.Label(c2, text=f"CPU: {self.cpu_info.get('name', 'AMD Ryzen')[:28]}", font=("Segoe UI", 12), fg=FG_WHITE, bg=BG_CARD_ROW).pack(anchor="w", pady=(6, 2))
        tk.Label(c2, text=f"GPU: {self.gpu_info.get('name', 'Radeon / GeForce')[:28]}", font=("Segoe UI", 12), fg=ACCENT_CYAN, bg=BG_CARD_ROW).pack(anchor="w", pady=(0, 6))
        b_c2 = tk.Button(c2, text="Engine & CPU Tweaks ➔", font=("Segoe UI", -12, "bold"), fg="#ffffff", bg="#1e293b",
                         activebackground="#334155", relief="flat", padx=10, pady=4, cursor="hand2",
                         command=lambda: self._select_nav("ENGINE"))
        b_c2.pack(anchor="w")

        # Card 3: ZE Servers & Slot Sniper
        c3 = tk.Frame(grid, bg=BG_CARD_ROW, highlightbackground=BG_BORDER, highlightthickness=1, padx=14, pady=12)
        c3.pack(side="left", fill="both", expand=True, padx=(6, 0))
        tk.Label(c3, text="🌐 ZE GAME SERVERS", font=("Segoe UI", 13, "bold"), fg=ACCENT_AMBER, bg=BG_CARD_ROW).pack(anchor="w")
        tk.Label(c3, text="Global & Asian ZE Clusters", font=("Segoe UI", 12), fg=FG_WHITE, bg=BG_CARD_ROW).pack(anchor="w", pady=(6, 2))
        tk.Label(c3, text="Auto Slot Sniper: Ready", font=("Segoe UI", 12), fg=ACCENT_GREEN, bg=BG_CARD_ROW).pack(anchor="w", pady=(0, 6))
        b_c3 = tk.Button(c3, text="Launch ZE Browser ➔", font=("Segoe UI", -12, "bold"), fg="#ffffff", bg="#1e293b",
                         activebackground="#334155", relief="flat", padx=10, pady=4, cursor="hand2",
                         command=lambda: self._select_nav("SERVERS"))
        b_c3.pack(anchor="w")

        # Quick Links & Tooling Row
        links_box = tk.Frame(content, bg=BG_CARD_ROW, highlightbackground=BG_BORDER, highlightthickness=1, padx=14, pady=10)
        links_box.pack(fill="x")
        tk.Label(links_box, text="QUICK NAVIGATION SHORTCUTS:", font=("Segoe UI", 11, "bold"), fg="#64748b", bg=BG_CARD_ROW).pack(side="left", padx=(0, 10))
        for l_key, l_title in [("BOOST", "Gaming DNS Optimizer"), ("LAUNCH", "Launch Options"), ("MAINTENANCE", "Custom Map Cleaner"), ("DISCORD", "Discord Presence")]:
            btn = tk.Button(links_box, text=l_title, font=("Segoe UI", -12, "bold"), fg="#94a3b8", bg="#161e2e",
                            activebackground="#222f47", activeforeground="#ffffff", relief="flat", padx=10, pady=3, cursor="hand2",
                            command=lambda k=l_key: self._select_nav(k))
            btn.pack(side="left", padx=3)

        _bind_dash_wheel(content)

    def _build_page_engine(self, page):
        canvas = tk.Canvas(page, bg=BG_CARD, highlightthickness=0, yscrollincrement=1)
        scrollbar = ttk.Scrollbar(page, orient="vertical", command=canvas.yview, style="Vertical.Dark.TScrollbar")
        self.engine_canvas = canvas
        self.engine_scrollbar = scrollbar
        content = tk.Frame(canvas, bg=BG_CARD)

        content.bind(
            "<Configure>",
            lambda e: self._debounce_sync_scroll(canvas, scrollbar)
        )
        c_window = canvas.create_window((0, 0), window=content, anchor="nw")
        self._bind_canvas_auto_width(canvas, c_window, scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        canvas.configure(yscrollincrement=1)

        def _bind_engine_wheel_recursive(widget):
            widget.bind("<MouseWheel>", lambda e: self._handle_canvas_wheel(e, canvas), add="+")
            for c in widget.winfo_children():
                _bind_engine_wheel_recursive(c)

        self.after(50, lambda: _bind_engine_wheel_recursive(content))

        # Weekly Maintenance Reminder Banner
        self.weekly_banner_box = tk.Frame(content, bg=BG_CARD)
        self.weekly_banner_box.pack(fill="x", pady=(0, 6))
        self._refresh_weekly_maint_banner()

        # Transparency Note: Stability & Consistency vs. Raw FPS
        note_card = tk.Frame(content, bg="#101826", padx=12, pady=7, highlightbackground="#1e3a5f", highlightthickness=1)
        note_card.pack(fill="x", pady=(0, 6))
        tk.Label(
            note_card,
            text="ℹ️  WHAT THIS OPTIMIZER & PC MAINTENANCE ACTUALLY DO (STABILITY vs. RAW FPS)",
            font=("Segoe UI", 10, "bold"), fg=ACCENT_CYAN, bg="#101826"
        ).pack(anchor="w")
        tk.Label(
            note_card,
            text=(
                "These tools are NOT meant to magically inflate maximum FPS beyond your CPU/GPU hardware limits. "
                "Instead, they eliminate OS bottlenecks to maximize Frame-Time Consistency (1% Lows), prevent micro-stutters "
                "during 64-player Zombie Escape / smoke utility, fix Display/Alt-Tab freezes (MPO), optimize sub-tick & DNS "
                "network responsiveness, and maintain peak SSD/OS health with 100% system safety."
            ),
            font=("Segoe UI", 9), fg="#cbd5e1", bg="#101826", justify="left", anchor="w", wraplength=760
        ).pack(anchor="w", fill="x", pady=(1, 0))

        tk.Label(content, text="ENGINE PERFORMANCE TWEAKS", font=("Segoe UI", -16, "bold"), fg=FG_WHITE, bg=BG_CARD).pack(anchor="w")
        tk.Label(content, text="All modifications are 100% safe, non-destructive, and can be restored anytime.", font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_CARD).pack(anchor="w", pady=(1, 6))

        self._create_tweak_row(
            content,
            self.opt_shaders,
            title="Optimize Shader Pre-caching & Purge Caches",
            desc="Removes fragmented GPU/DirectX shaders. Recommended after game patches to eliminate micro-stutters."
        )

        self._create_tweak_row(
            content,
            self.opt_cs2_dumps,
            title="Clean CS2 Crash Dumps & Temp Files",
            desc="Removes old WER minidumps and crash logs from the CS2 directory to reclaim storage and load cleaner."
        )

        self._create_tweak_row(
            content,
            self.opt_gamedvr,
            title="Disable Windows Game DVR Background Capture",
            desc="Stops Windows Xbox background frame capture, cutting DWM latency and background GPU load."
        )

        self._create_tweak_row(
            content,
            self.opt_fullscreen,
            title="Disable Fullscreen Optimizations (Direct-Flip)",
            desc="Forces exclusive direct display presentation for cs2.exe, bypassing Windows desktop compositor lag."
        )

        self._create_tweak_row(
            content,
            self.opt_autoexec,
            title="Append Low-Latency Engine Autoexec Config",
            desc="Appends safe Source 2 rate, telemetry, and audio latency tweaks (snd_mixahead 0.025) while preserving custom binds."
        )

        # CPU Power Scheme Row
        pw_row = tk.Frame(content, bg=BG_CARD)
        pw_row.pack(fill="x", pady=4)

        left = tk.Frame(pw_row, bg=BG_CARD)
        left.pack(side="left", fill="both", expand=True)
        tk.Label(left, text="Windows CPU Power Scheme", font=("Segoe UI", 14, "bold"), fg=FG_WHITE, bg=BG_CARD).pack(anchor="w")
        tk.Label(left, text=f"Recommended for your CPU: {self.cpu_info['recommended_power_plan']} | Active: {self.active_plan_name}", font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_CARD).pack(anchor="w")

        right = tk.Frame(pw_row, bg=BG_CARD)
        right.pack(side="right")

        plans = ["Balanced", "High Performance"]
        cb_plans = ttk.Combobox(right, textvariable=self.selected_power_plan, values=plans, state="readonly", width=17)
        cb_plans.pack(side="left", padx=6)
        add_tooltip(cb_plans, "Select Windows CPU Power Plan (Balanced is optimal for Ryzen X3D CPPC cache scheduling).")
        
        cb_pw = tk.Checkbutton(right, text="Apply", variable=self.opt_power, font=("Segoe UI", 10, "bold"),
                       fg=FG_WHITE, bg=BG_CARD, activebackground=BG_CARD, selectcolor=BG_WINDOW)
        cb_pw.pack(side="left")
        add_tooltip(cb_pw, "When checked, ONE-CLICK OPTIMIZE will switch Windows active power scheme to this plan.")

        # Compact bottom margin
        tk.Frame(content, bg=BG_CARD, height=4).pack(fill="x", pady=(2, 4))

    def _refresh_weekly_maint_banner(self):
        """Builds or updates the synchronized weekly health reminder banner in Engine Tweaks & PC Maintenance."""
        containers = []
        if hasattr(self, "weekly_banner_box") and self.weekly_banner_box.winfo_exists():
            containers.append(("ENGINE", self.weekly_banner_box))
        if hasattr(self, "maint_weekly_banner_box") and self.maint_weekly_banner_box.winfo_exists():
            containers.append(("MAINTENANCE", self.maint_weekly_banner_box))

        if not containers:
            return

        opt_days = app_config.get_days_since_optimization(self.config)
        maint_days = app_config.get_days_since_maintenance(self.config)

        opt_due = (opt_days >= 7)
        maint_due = (maint_days >= 7)

        opt_str = f"{opt_days}d ago" if opt_days != 999 else "Not yet run"
        maint_str = f"{maint_days}d ago" if maint_days != 999 else "Not yet run"

        for page_type, container in containers:
            for w in container.winfo_children():
                w.destroy()

            # State 1: Both up-to-date (< 7 days) -> Crisp Green Banner
            if not opt_due and not maint_due:
                card = tk.Frame(container, bg="#0e1f18", padx=12, pady=7, highlightbackground="#065f46", highlightthickness=1)
                card.pack(fill="x")
                top = tk.Frame(card, bg="#0e1f18")
                top.pack(fill="x")

                tk.Label(top, text="✅  SYSTEM & CS2 HEALTH UP-TO-DATE", font=("Segoe UI", 10, "bold"), fg=ACCENT_GREEN, bg="#0e1f18").pack(side="left")

                if page_type == "ENGINE":
                    b_nav = tk.Button(top, text="Open PC Maintenance", font=("Segoe UI", 9), fg="#cbd5e1", bg="#182c23",
                                      activebackground="#223f33", activeforeground="#ffffff", relief="flat", padx=8, pady=6, cursor="hand2",
                                      command=lambda: self._select_nav("MAINTENANCE"))
                    b_nav.pack(side="right")
                    add_tooltip(b_nav, "Switch to PC Maintenance tab to inspect storage and system health.")
                else:
                    b_nav = tk.Button(top, text="Open Engine Tweaks", font=("Segoe UI", 9), fg="#cbd5e1", bg="#182c23",
                                      activebackground="#223f33", activeforeground="#ffffff", relief="flat", padx=8, pady=6, cursor="hand2",
                                      command=lambda: self._select_nav("ENGINE"))
                    b_nav.pack(side="right")
                    add_tooltip(b_nav, "Switch to Engine Tweaks tab to review CS2 performance settings.")

                sub = tk.Label(card, text=f"CS2 Engine Tweaks: Optimized {opt_str}  •  PC Maintenance: Clean {maint_str}  (Recommended: every 7 days)",
                               font=("Segoe UI", 9), fg="#94a3b8", bg="#0e1f18", anchor="w")
                sub.pack(fill="x", pady=(2, 0))

            # State 2: Engine optimized, but PC Maintenance overdue -> Amber Banner
            elif not opt_due and maint_due:
                card = tk.Frame(container, bg="#1f180e", padx=12, pady=8, highlightbackground="#b45309", highlightthickness=1)
                card.pack(fill="x")
                top = tk.Frame(card, bg="#1f180e")
                top.pack(fill="x")

                tk.Label(top, text="⚠️  PC MAINTENANCE OVERDUE", font=("Segoe UI", 10, "bold"), fg=ACCENT_AMBER, bg="#1f180e").pack(side="left")

                if page_type == "ENGINE":
                    b_act = tk.Button(top, text="🧹 Run PC Maintenance", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#242b3b",
                                      activebackground="#333f54", activeforeground="#ffffff", relief="flat", padx=10, pady=6, cursor="hand2",
                                      command=lambda: self._select_nav("MAINTENANCE"))
                    b_act.pack(side="right")
                    add_tooltip(b_act, "Switch to PC Maintenance tab to run SSD TRIM, disk cleanup, and system file repair.")
                else:
                    b_act = tk.Button(top, text="🧹 Run Maintenance Below", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg=ACCENT_ORANGE,
                                      activebackground=ACCENT_ORANGE_HOVER, activeforeground="#ffffff", relief="flat", padx=10, pady=6, cursor="hand2",
                                      command=self.run_pc_maintenance)
                    b_act.pack(side="right")
                    add_tooltip(b_act, "Executes all selected safe PC maintenance cleanups.")

                sub = tk.Label(card, text=f"CS2 Engine Tweaks are up-to-date ({opt_str}), but PC Maintenance is overdue ({maint_str}). Running SSD TRIM and cache cleanups prevents micro-stutters and frees disk space.",
                               font=("Segoe UI", 9), fg="#cbd5e1", bg="#1f180e", anchor="w")
                sub.pack(fill="x", pady=(2, 0))

            # State 3: PC Maintenance done, but Engine Tweaks overdue -> Amber Banner
            elif opt_due and not maint_due:
                card = tk.Frame(container, bg="#1f180e", padx=12, pady=8, highlightbackground="#b45309", highlightthickness=1)
                card.pack(fill="x")
                top = tk.Frame(card, bg="#1f180e")
                top.pack(fill="x")

                tk.Label(top, text="⚠️  CS2 ENGINE OPTIMIZATION DUE", font=("Segoe UI", 10, "bold"), fg=ACCENT_AMBER, bg="#1f180e").pack(side="left")

                if page_type == "ENGINE":
                    b_act = tk.Button(top, text="⚡ 1-Click Optimize", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg=ACCENT_ORANGE,
                                      activebackground=ACCENT_ORANGE_HOVER, activeforeground="#ffffff", relief="flat", padx=10, pady=6, cursor="hand2",
                                      command=self.run_one_click_optimization)
                    b_act.pack(side="right")
                    add_tooltip(b_act, "Purges stale shader caches, clears crash dumps, and updates competitive autoexec.")
                else:
                    b_act = tk.Button(top, text="⚡ Go to Engine Tweaks", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#242b3b",
                                      activebackground="#333f54", activeforeground="#ffffff", relief="flat", padx=10, pady=6, cursor="hand2",
                                      command=lambda: self._select_nav("ENGINE"))
                    b_act.pack(side="right")
                    add_tooltip(b_act, "Switch to Engine Tweaks tab to run 1-Click CS2 Optimization.")

                sub = tk.Label(card, text=f"PC Maintenance is clean ({maint_str}), but CS2 Engine Tweaks are overdue ({opt_str}). Purging DirectX/GPU shaders and refreshing autoexec ensures smooth 1% lows.",
                               font=("Segoe UI", 9), fg="#cbd5e1", bg="#1f180e", anchor="w")
                sub.pack(fill="x", pady=(2, 0))

            # State 4: Both overdue -> High Priority Amber/Red Banner
            else:
                card = tk.Frame(container, bg="#201111", padx=12, pady=8, highlightbackground="#991b1b", highlightthickness=1)
                card.pack(fill="x")
                top = tk.Frame(card, bg="#201111")
                top.pack(fill="x")

                tk.Label(top, text="⚠️  WEEKLY PC & CS2 HYGIENE OVERDUE: Both maintenance tasks require attention",
                         font=("Segoe UI", 10, "bold"), fg="#f87171", bg="#201111").pack(side="left")

                btn_box = tk.Frame(top, bg="#201111")
                btn_box.pack(side="right")

                b1 = tk.Button(btn_box, text="⚡ 1-Click Optimize", font=("Segoe UI", 14, "bold"), fg="#ffffff", bg=ACCENT_ORANGE,
                               activebackground=ACCENT_ORANGE_HOVER, activeforeground="#ffffff", relief="flat", padx=8, pady=6, cursor="hand2",
                               command=self.run_one_click_optimization)
                b1.pack(side="left", padx=2)

                if page_type == "ENGINE":
                    b2 = tk.Button(btn_box, text="🧹 Open PC Maintenance", font=("Segoe UI", 14, "bold"), fg="#ffffff", bg="#242b3b",
                                   activebackground="#333f54", activeforeground="#ffffff", relief="flat", padx=8, pady=6, cursor="hand2",
                                   command=lambda: self._select_nav("MAINTENANCE"))
                    b2.pack(side="left", padx=2)
                else:
                    b2 = tk.Button(btn_box, text="🧹 Run Maintenance Below", font=("Segoe UI", 14, "bold"), fg="#ffffff", bg="#242b3b",
                                   activebackground="#333f54", activeforeground="#ffffff", relief="flat", padx=8, pady=6, cursor="hand2",
                                   command=self.run_pc_maintenance)
                    b2.pack(side="left", padx=2)

                sub = tk.Label(card, text=f"CS2 Engine Tweaks ({opt_str}) and PC Maintenance ({maint_str}) have not been run recently. Stale shader caches and accumulated temporary files degrade frame pacing.",
                               font=("Segoe UI", 9), fg="#cbd5e1", bg="#201111", anchor="w")
                sub.pack(fill="x", pady=(2, 0))

    def _create_tweak_row(self, parent, var, title, desc):
        row = tk.Frame(parent, bg=BG_CARD)
        row.pack(fill="x", pady=4)

        left = tk.Frame(row, bg=BG_CARD)
        left.pack(side="left", fill="both", expand=True)
        tk.Label(left, text=title, font=("Segoe UI", -14, "bold"), fg=FG_WHITE, bg=BG_CARD, anchor="w").pack(anchor="w", fill="x")
        tk.Label(left, text=desc, font=("Segoe UI", -12), fg="#94a3b8", bg=BG_CARD, wraplength=600, justify="left", anchor="w").pack(anchor="w", fill="x")

        right = tk.Frame(row, bg=BG_CARD)
        right.pack(side="right")

        cb = tk.Checkbutton(right, text="Enabled", variable=var,
                            font=("Segoe UI", 10, "bold"), fg=ACCENT_ORANGE, bg=BG_CARD,
                            activebackground=BG_CARD, activeforeground=ACCENT_ORANGE,
                            selectcolor=BG_WINDOW, relief="flat", cursor="hand2")
        cb.pack(side="right")
        add_tooltip(cb, f"Toggle {title}: {desc}")

        tk.Frame(parent, bg=BG_BORDER, height=1).pack(fill="x", pady=(4, 0))

    def _build_page_autoexec(self, page):
        content = page
        tk.Label(content, text="CS2 IN-GAME AUTOEXEC CONFIGURATION", font=("Segoe UI", -16, "bold"), fg=FG_WHITE, bg=BG_CARD).pack(anchor="w")
        
        cfg_loc = f"Config directory: {self.paths.get('cfg_dir') or 'Not Found'}"
        tk.Label(content, text=cfg_loc, font=("Consolas", 10), fg=ACCENT_CYAN, bg=BG_CARD).pack(anchor="w", pady=(1, 4))

        note = tk.Label(content, text="🛡️ Safety Guarantee: Your personal binds, scancodes, aliases, crosshairs, and viewmodels are NEVER deleted. Performance tweaks are appended at the bottom.", font=("Segoe UI", 10, "bold"), fg=ACCENT_GREEN, bg=BG_CARD, anchor="w", justify="left")
        note.pack(anchor="w", fill="x", pady=(0, 8))

        btn_bar = tk.Frame(content, bg=BG_CARD)
        btn_bar.pack(anchor="w", fill="x", pady=(0, 4))

        b_apply_cfg = tk.Button(btn_bar, text="📥 1. Apply Engine & Sub-Tick Autoexec Tweaks", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg=ACCENT_GREEN,
                  relief="flat", padx=12, pady=4, cursor="hand2", command=self.install_autoexec)
        b_apply_cfg.pack(side="left", padx=(0, 8))
        add_tooltip(b_apply_cfg, "Appends core Source 2 engine FPS, sub-tick network rates, and low-latency audio buffer tweaks.")

        b_rev_cfg = tk.Button(btn_bar, text="⏪ Revert Autoexec to Original", font=("Segoe UI", 10), fg="#cbd5e1", bg="#242b3b",
                  relief="flat", padx=12, pady=4, cursor="hand2", command=self.restore_autoexec)
        b_rev_cfg.pack(side="left")
        add_tooltip(b_rev_cfg, "Restores your original autoexec.cfg from the automatic pre-patch backup.")

        diff_lbl = tk.Label(
            btn_bar,
            text="💡 Engine Tweaks (Green) = Core FPS/Network Rates  |  ZE Customizer (Blue below) = Laser Viewmodel, HUD & F7/F8 Binds",
            font=("Segoe UI", 9, "italic"), fg="#94a3b8", bg=BG_CARD
        )
        diff_lbl.pack(side="right", padx=4)

        # NEW FEATURE: ZE Visual Clutter, Viewmodel, HUD & Boss Audio Ducking Customizer
        ze_hud_card = tk.Frame(content, bg=BG_CARD_ROW, padx=12, pady=8, highlightbackground="#1e3a5f", highlightthickness=1)
        ze_hud_card.pack(fill="x", pady=(2, 6))

        zh_top = tk.Frame(ze_hud_card, bg=BG_CARD_ROW)
        zh_top.pack(fill="x")
        tk.Label(zh_top, text="🔦 2. ZE VISUAL CLUTTER, LASER VIEWMODEL & BOSS AUDIO DUCKING CUSTOMIZER", font=("Segoe UI", -13, "bold"), fg=ACCENT_CYAN, bg=BG_CARD_ROW).pack(side="left")
        tk.Label(zh_top, text="100% VAC-SAFE CVARS", font=("Segoe UI", -11, "bold"), fg=ACCENT_GREEN, bg="#0d261d", padx=6, pady=1).pack(side="right")

        tk.Label(
            ze_hud_card,
            text="Separate from Engine Tweaks above: injects Zombie Escape gameplay binds (Low Viewmodel for ending lasers, HUD color, and F7/F8 audio keys) at the bottom of autoexec.cfg.",
            font=("Segoe UI", 9), fg=FG_MUTED, bg=BG_CARD_ROW, anchor="w", justify="left"
        ).pack(anchor="w", fill="x", pady=(1, 4))

        personal_vm = core_logic.detect_personal_viewmodel_in_autoexec(self.paths.get("cfg_dir"))
        has_custom_vm = bool(personal_vm)
        self.personal_vm_detected = has_custom_vm

        # If user has their own personal viewmodel in autoexec, do NOT override by default!
        self.ze_vm_var = tk.BooleanVar(value=False if has_custom_vm else True)
        self.ze_telemetry_var = tk.BooleanVar(value=True)
        self.ze_hud_color_var = tk.StringVar(value="0 (Default / Team)")
        self.ze_duck_key_var = tk.StringVar(value="F7")
        self.ze_mute_key_var = tk.StringVar(value="F8")

        if has_custom_vm:
            vm_badge = tk.Frame(ze_hud_card, bg="#0d261d", padx=8, pady=3, highlightbackground=ACCENT_GREEN, highlightthickness=1)
            vm_badge.pack(anchor="w", fill="x", pady=(0, 4))
            tk.Label(
                vm_badge,
                text="🛡️ PERSONAL CONFIG DETECTED: Your custom viewmodel is active & preserved. Check the box below ONLY if you wish to override it.",
                font=("Segoe UI", -12, "bold"), fg=ACCENT_GREEN, bg="#0d261d", anchor="w"
            ).pack(anchor="w")

        zh_grid = tk.Frame(ze_hud_card, bg=BG_CARD_ROW)
        zh_grid.pack(fill="x", pady=2)

        vm_text = " Override with ZE Laser Viewmodel (FOV 68, Y:+2, Z:-2)" if has_custom_vm else " ZE Laser-Jump Low Viewmodel (FOV 68, Y:+2, Z:-2)"
        cb_zvm = tk.Checkbutton(
            zh_grid, text=vm_text, variable=self.ze_vm_var,
            font=("Segoe UI", 10), fg=FG_WHITE, bg=BG_CARD_ROW, activebackground=BG_CARD_ROW, selectcolor=BG_WINDOW, relief="flat"
        )
        cb_zvm.grid(row=0, column=0, sticky="w", padx=(0, 14), pady=2)
        vm_tip = "Check to override your viewmodel with the low crouch-laser viewmodel (FOV 68, Y:+2, Z:-2). Leave unchecked to preserve your personal config." if has_custom_vm else "Lowers your weapon model out of the center screen so you can clearly see low/crouch lasers during ZE endings."
        add_tooltip(cb_zvm, vm_tip)

        cb_ztel = tk.Checkbutton(
            zh_grid, text=" Smart Frame-Time & Network Jitter Telemetry HUD", variable=self.ze_telemetry_var,
            font=("Segoe UI", 10), fg=FG_WHITE, bg=BG_CARD_ROW, activebackground=BG_CARD_ROW, selectcolor=BG_WINDOW, relief="flat"
        )
        cb_ztel.grid(row=0, column=1, sticky="w", padx=(0, 14), pady=2)
        add_tooltip(cb_ztel, "Enables real-time CS2 frametime, ping, and network jitter telemetry only when spikes occur.")

        hud_row = tk.Frame(zh_grid, bg=BG_CARD_ROW)
        hud_row.grid(row=0, column=2, sticky="w", pady=2)
        tk.Label(hud_row, text="HUD Color:", font=("Segoe UI", 10), fg="#cbd5e1", bg=BG_CARD_ROW).pack(side="left")
        hud_combo = ttk.Combobox(
            hud_row, textvariable=self.ze_hud_color_var, state="readonly", width=17,
            values=[
                "0 (Default / Team)",
                "1 (White)",
                "2 (Bright White)",
                "3 (Light Blue)",
                "4 (Dark Blue)",
                "5 (Purple)",
                "6 (Red)",
                "7 (Orange)",
                "8 (Yellow)",
                "9 (Green)",
                "10 (Aqua / Cyan)",
                "11 (Pink)",
                "12 (Light Yellow)"
            ]
        )
        hud_combo.pack(side="left", padx=6)

        bind_row = tk.Frame(ze_hud_card, bg=BG_CARD_ROW)
        bind_row.pack(fill="x", pady=(4, 2))

        tk.Label(bind_row, text="🔊 Boss/Laser Audio Duck Key (22% vs 100%):", font=("Segoe UI", 10), fg="#cbd5e1", bg=BG_CARD_ROW).pack(side="left")
        tk.Entry(bind_row, textvariable=self.ze_duck_key_var, width=5, font=("Consolas", 10, "bold"), bg=BG_CONSOLE, fg=ACCENT_CYAN, insertbackground=FG_WHITE, relief="flat", highlightbackground=BG_BORDER, highlightthickness=1).pack(side="left", padx=(4, 12))

        tk.Label(bind_row, text="🔇 Panic Voice Mute Key:", font=("Segoe UI", 10), fg="#cbd5e1", bg=BG_CARD_ROW).pack(side="left")
        tk.Entry(bind_row, textvariable=self.ze_mute_key_var, width=5, font=("Consolas", 10, "bold"), bg=BG_CONSOLE, fg=ACCENT_AMBER, insertbackground=FG_WHITE, relief="flat", highlightbackground=BG_BORDER, highlightthickness=1).pack(side="left", padx=(4, 12))

        b_apply_ze_hud = tk.Button(
            bind_row, text="✨ Inject ZE Visual & Audio Binds", font=("Segoe UI", 10, "bold"),
            fg="#ffffff", bg="#0284c7", activebackground="#0369a1", relief="flat",
            padx=12, pady=6, cursor="hand2", command=self.apply_ze_visual_hud_ui
        )
        b_apply_ze_hud.pack(side="right")
        add_tooltip(b_apply_ze_hud, "Appends your selected ZE Low Viewmodel, HUD Color, and Boss Audio Ducking keybinds to autoexec.cfg with automatic backup.")

        preview_hdr = tk.Frame(content, bg=BG_CARD)
        preview_hdr.pack(fill="x", pady=(2, 2))
        
        ph_left = tk.Frame(preview_hdr, bg=BG_CARD)
        ph_left.pack(side="left")
        tk.Label(ph_left, text="📄 AUTOEXEC.CFG:", font=("Segoe UI", 10, "bold"), fg="#cbd5e1", bg=BG_CARD).pack(side="left", padx=(0, 8))

        self.is_autoexec_editing = False

        self.btn_edit_cfg = tk.Button(
            ph_left, text="✏️ Edit Config", font=("Segoe UI", 9, "bold"),
            fg="#ffffff", bg="#2563eb", activebackground="#1d4ed8", relief="flat",
            padx=10, pady=2, cursor="hand2", command=self._toggle_autoexec_manual_edit
        )
        self.btn_edit_cfg.pack(side="left", padx=(0, 4))
        add_tooltip(self.btn_edit_cfg, "Unlock the text box below to write or edit your own custom binds, aliases, and commands directly.")

        self.btn_save_cfg = tk.Button(
            ph_left, text="💾 Save Changes", font=("Segoe UI", 9, "bold"),
            fg="#ffffff", bg=ACCENT_GREEN, activebackground="#16a34a", relief="flat",
            padx=10, pady=2, cursor="hand2", command=self._save_autoexec_manual
        )
        # Initially not packed until edit mode is activated
        add_tooltip(self.btn_save_cfg, "Saves your manual text edits directly to autoexec.cfg.")

        self.autoexec_live_status_var = tk.StringVar(value="Read-only preview (Click [✏️ Edit Config] to modify)")
        tk.Label(preview_hdr, textvariable=self.autoexec_live_status_var, font=("Consolas", 9, "bold"), fg=ACCENT_GREEN, bg=BG_CARD).pack(side="right")

        txt_container = tk.Frame(content, bg=BG_CONSOLE, highlightbackground=BG_BORDER, highlightthickness=1)
        txt_container.pack(fill="both", expand=True, pady=(2, 0))

        txt_scroll = ttk.Scrollbar(txt_container, orient="vertical", style="Vertical.Dark.TScrollbar")
        self.txt_box = tk.Text(
            txt_container, height=18, bg=BG_CONSOLE, fg="#a7f3d0", font=("Consolas", 10),
            relief="flat", highlightthickness=0, padx=8, pady=6, yscrollcommand=txt_scroll.set
        )
        txt_scroll.config(command=self.txt_box.yview)
        self.txt_box.pack(side="left", fill="both", expand=True)
        txt_scroll.pack(side="right", fill="y")
        self._refresh_autoexec_preview(scroll_to_bottom=False)

    def apply_ze_visual_hud_ui(self):
        hud_raw = self.ze_hud_color_var.get().split()[0]
        try:
            hud_col = int(hud_raw)
        except Exception:
            hud_col = 0
        duck_k = self.ze_duck_key_var.get().strip() or "F7"
        mute_k = self.ze_mute_key_var.get().strip() or "F8"
        opts = {
            "ze_laser_viewmodel": self.ze_vm_var.get(),
            "clean_telemetry_hud": self.ze_telemetry_var.get(),
            "hud_color": hud_col,
            "hud_scale": 0.90,
            "radar_zoom": 0.40,
            "duck_key": duck_k,
            "voice_mute_key": mute_k,
        }
        res = core_logic.apply_ze_visual_and_hud_customizer(self.paths.get("cfg_dir"), opts)
        if isinstance(res, tuple):
            ok, log_list = res
            msg = log_list[-1] if log_list else "Updated autoexec.cfg"
            res = {"success": ok, "message": msg, "logs": log_list}

        self.log(f"[ZE CUSTOMIZER] {res.get('message')}")
        self._refresh_autoexec_preview(scroll_to_bottom=True)
        if hasattr(self, "autoexec_live_status_var"):
            self.autoexec_live_status_var.set(
                f"✅ Updated @ {time.strftime('%H:%M:%S')} — Live preview scrolled to injected block at bottom!"
            )
        # Force Tkinter to redraw the updated text box and scroll position BEFORE opening the popup dialog!
        try:
            self.update_idletasks()
        except Exception:
            pass

        if res.get("success"):
            messagebox.showinfo(
                "ZE Visual & Audio Binds Added to autoexec.cfg",
                f"✅ Successfully injected into autoexec.cfg!\n\n"
                f"{res.get('message')}\n\n"
                f"• Viewmodel Low Laser Preset: {'ON (FOV 68, X:+2, Y:+2, Z:-2)' if opts['ze_laser_viewmodel'] else 'OFF (Personal Config Viewmodel 100% Preserved)'}\n"
                                f"• HUD Color: {self.ze_hud_color_var.get()}\n"
                f"• Boss Audio Ducking Key: [{duck_k}] (22% <-> 100%)  |  Panic Voice Mute Key: [{mute_k}]\n\n"
                f"Look at the Live Autoexec.cfg File Preview box below — it has automatically updated and scrolled to the bottom showing your new [CS2 COMMAND CENTER: ZE VISUAL, HUD & AUDIO DUCKING STUDIO] block!"
            )
        else:
            messagebox.showwarning("ZE Customizer Notice", str(res.get("message")))

    def _toggle_autoexec_manual_edit(self):
        """Toggles between safe read-only preview and interactive direct editing mode."""
        if not hasattr(self, "txt_box") or not self.txt_box.winfo_exists():
            return

        self.is_autoexec_editing = not getattr(self, "is_autoexec_editing", False)
        if self.is_autoexec_editing:
            self.txt_box.config(state="normal", bg="#0a0f1d", fg="#f8fafc", insertbackground="#38bdf8")
            self.btn_edit_cfg.config(text="🔒 Cancel Edit", bg="#334155")
            self.btn_save_cfg.pack(side="left", padx=4)
            self.autoexec_live_status_var.set("✏️ EDITING ACTIVE — Modify your cfg and click [💾 Save Changes]")
            self.txt_box.focus_set()
        else:
            self.btn_save_cfg.pack_forget()
            self.btn_edit_cfg.config(text="✏️ Edit Config", bg="#2563eb")
            self._refresh_autoexec_preview(scroll_to_bottom=False)
            self.autoexec_live_status_var.set("Read-only preview (Click [✏️ Edit Config] to modify)")

    def _save_autoexec_manual(self):
        cfg_file = os.path.join(self.paths["cfg_dir"], "autoexec.cfg") if self.paths["cfg_dir"] else None
        if not cfg_file:
            messagebox.showwarning("No Config Found", "Cannot locate autoexec.cfg path.")
            return

        content = self.txt_box.get("1.0", "end-1c")
        try:
            # Create safety backup first
            bak = cfg_file + ".manual_bak"
            if os.path.exists(cfg_file):
                try:
                    shutil.copy2(cfg_file, bak)
                except Exception:
                    pass

            with open(cfg_file, "w", encoding="utf-8") as f:
                f.write(content)

            self.is_autoexec_editing = False
            self.btn_save_cfg.pack_forget()
            self.btn_edit_cfg.config(text="✏️ Edit Config", bg="#2563eb")
            self.txt_box.config(state="disabled", bg=BG_CONSOLE, fg="#a7f3d0")
            ts = time.strftime("%H:%M:%S")
            self.autoexec_live_status_var.set(f"✅ Saved manually @ {ts} (Backup created)")
            self.log(f"[AUTOEXEC] User manual changes saved to: {cfg_file}")
            messagebox.showinfo(
                "Autoexec Saved",
                f"✅ Your manual edits have been saved to autoexec.cfg successfully!\n\nFile: {cfg_file}\n\nA safety backup has been created as autoexec.cfg.manual_bak."
            )
        except Exception as ex:
            messagebox.showerror("Save Error", f"Failed to save autoexec.cfg:\n\n{ex}")

    def _refresh_autoexec_preview(self, scroll_to_bottom: bool = False):
        if getattr(self, "is_autoexec_editing", False):
            return  # Never overwrite active user typing in edit mode!

        cfg_file = os.path.join(self.paths["cfg_dir"], "autoexec.cfg") if self.paths["cfg_dir"] else None
        content = ""
        if cfg_file and os.path.exists(cfg_file):
            try:
                with open(cfg_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                pass
        if not content:
            content = core_logic.PERF_BLOCK

        if hasattr(self, "txt_box") and self.txt_box.winfo_exists():
            self.txt_box.config(state="normal")
            self.txt_box.delete("1.0", "end")
            self.txt_box.insert("1.0", content)
            self.txt_box.update_idletasks()
            if scroll_to_bottom:
                self.txt_box.see("end")
                self.txt_box.yview_moveto(1.0)
            self.txt_box.config(state="disabled")

    def _build_page_launch(self, page):
        canvas = tk.Canvas(page, bg=BG_CARD, highlightthickness=0, yscrollincrement=1)
        scrollbar = ttk.Scrollbar(page, orient="vertical", command=canvas.yview, style="Vertical.Dark.TScrollbar")
        self.launch_canvas = canvas
        self.launch_scrollbar = scrollbar
        content = tk.Frame(canvas, bg=BG_CARD)

        content.bind(
            "<Configure>",
            lambda e: self._debounce_sync_scroll(canvas, scrollbar)
        )
        c_window = canvas.create_window((0, 0), window=content, anchor="nw")
        self._bind_canvas_auto_width(canvas, c_window, scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def _on_launch_wheel(e):
            return self._handle_canvas_wheel(e, canvas)

        tk.Label(content, text="STEAM LAUNCH OPTIONS HELPER", font=("Segoe UI", -16, "bold"), fg=FG_WHITE, bg=BG_CARD).pack(anchor="w")
        tk.Label(content, text="Inspects your active Steam launch flags, preserves custom flags, and offers competitive reference presets.", font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_CARD).pack(anchor="w", pady=(1, 8))

        # 1. Current Active Steam Options
        cur_box = tk.Frame(content, bg=BG_CONSOLE, padx=12, pady=8, highlightbackground=BG_BORDER, highlightthickness=1)
        cur_box.pack(fill="x", pady=(0, 6))

        h_cur = tk.Frame(cur_box, bg=BG_CONSOLE)
        h_cur.pack(fill="x")
        tk.Label(h_cur, text="Your Current Active Launch Options in Steam:", font=("Segoe UI", 10, "bold"), fg=FG_MUTED, bg=BG_CONSOLE).pack(side="left")
        
        has_warnings = bool(self.launch_analysis.get("warnings"))
        badge_text = "⚠️ Obsolete Flags Detected" if has_warnings else "✅ Clean Configuration"
        badge_fg = "#f59e0b" if has_warnings else ACCENT_GREEN
        tk.Label(h_cur, text=badge_text, font=("Segoe UI", 10, "bold"), fg=badge_fg, bg=BG_CONSOLE).pack(side="right")

        cur_text = self.launch_analysis["current"] if self.launch_analysis["current"] else "(None currently set)"
        tk.Label(cur_box, text=cur_text, font=("Consolas", 10, "bold"), fg=ACCENT_ORANGE, bg=BG_CONSOLE).pack(anchor="w", pady=(4, 0))

        if has_warnings:
            for w in self.launch_analysis["warnings"]:
                tk.Label(content, text=f"⚠️ {w}", font=("Segoe UI", 10, "bold"), fg="#f59e0b", bg=BG_CARD).pack(anchor="w", pady=1)

        # 2. Competitive Baseline Reference (Information Card)
        ref_box = tk.Frame(content, bg="#131b26", padx=12, pady=8, highlightbackground="#1e293b", highlightthickness=1)
        ref_box.pack(fill="x", pady=(4, 8))
        tk.Label(ref_box, text="💡 Recommended Competitive Baseline Preset (Reference):", font=("Segoe UI", 10, "bold"), fg=ACCENT_CYAN, bg="#131b26").pack(anchor="w")
        tk.Label(ref_box, text="-novid -nojoy +fps_max 0", font=("Consolas", 9, "bold"), fg="#38bdf8", bg="#131b26").pack(anchor="w", pady=(2, 4))
        ref_desc = (
            "• -novid: Skips the Valve logo splash video on startup to enter the main menu faster.\n"
            "• -nojoy: Disables gamepad / joystick direct input polling, reducing background thread interruptions.\n"
            "• +fps_max 0: Uncaps rendering FPS (can also be capped to your monitor refresh rate).\n"
            "• Custom flags like '-allow_third_party_software' or '+exec autoexec.cfg' are fully preserved if you choose to keep them."
        )
        tk.Label(ref_box, text=ref_desc, font=("Segoe UI", 9), fg="#94a3b8", bg="#131b26", justify="left", anchor="w").pack(anchor="w", fill="x")

        # 3. Editable Launch Options Box
        rec_box = tk.Frame(content, bg=BG_CARD, pady=2)
        rec_box.pack(fill="x")
        tk.Label(rec_box, text="Edit / Apply Launch Options to Steam:", font=("Segoe UI", 14, "bold"), fg=FG_WHITE, bg=BG_CARD).pack(anchor="w")
        
        self.launch_entry = tk.Entry(rec_box, font=("Consolas", 10), bg=BG_CONSOLE, fg=ACCENT_GREEN,
                                     insertbackground=FG_WHITE, relief="flat", highlightbackground=BG_BORDER, highlightthickness=1)
        self.launch_entry.pack(fill="x", pady=4, ipady=4)
        # Pre-fill with user's CURRENT options by default so they can keep their setup!
        self.launch_entry.insert(0, self.launch_analysis["current"] or "-novid -nojoy +fps_max 0")

        btn_row = tk.Frame(rec_box, bg=BG_CARD)
        btn_row.pack(fill="x", pady=4)

        b_copy_l = tk.Button(btn_row, text="📋 Copy Options", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg=ACCENT_ORANGE,
                  relief="flat", padx=12, pady=4, cursor="hand2", command=self.copy_launch_options)
        b_copy_l.pack(side="left", padx=(0, 6))
        add_tooltip(b_copy_l, "Copies current text in the box to clipboard to paste into Steam CS2 properties.")

        if self.vdf_path:
            b_app_l = tk.Button(btn_row, text="💾 Apply Directly To Steam", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#2563eb",
                      relief="flat", padx=12, pady=4, cursor="hand2", command=self.save_launch_options)
            b_app_l.pack(side="left", padx=6)
            add_tooltip(b_app_l, "Writes these launch options directly into Steam localconfig.vdf (make sure Steam is closed).")

        def _load_baseline():
            self.launch_entry.delete(0, "end")
            self.launch_entry.insert(0, "-novid -nojoy +fps_max 0")
            self.log("[LAUNCH] Loaded Competitive Baseline preset into editor (-novid -nojoy +fps_max 0). Click 'Apply Directly To Steam' to save.")

        def _reset_to_current():
            self.launch_entry.delete(0, "end")
            self.launch_entry.insert(0, self.launch_analysis["current"])
            self.log("[LAUNCH] Reverted editor back to your current Steam options.")

        b_base = tk.Button(btn_row, text="⚡ Load Baseline Preset", font=("Segoe UI", 10), fg="#cbd5e1", bg="#1f293d",
                  relief="flat", padx=10, pady=4, cursor="hand2", command=_load_baseline)
        b_base.pack(side="left", padx=6)
        add_tooltip(b_base, "Fills editor with the clean competitive baseline preset (-novid -nojoy +fps_max 0).")

        b_rst = tk.Button(btn_row, text="⏪ Keep / Reset To Current", font=("Segoe UI", 10), fg="#94a3b8", bg="#181c24",
                  relief="flat", padx=10, pady=4, cursor="hand2", command=_reset_to_current)
        b_rst.pack(side="left", padx=6)
        add_tooltip(b_rst, "Resets editor back to whatever launch options are currently active in your Steam.")

    def _build_page_boost(self, page):
        canvas = tk.Canvas(page, bg=BG_CARD, highlightthickness=0, yscrollincrement=1)
        scrollbar = ttk.Scrollbar(page, orient="vertical", command=canvas.yview, style="Vertical.Dark.TScrollbar")
        self.boost_canvas = canvas
        self.boost_scrollbar = scrollbar
        boost_content = tk.Frame(canvas, bg=BG_CARD)

        boost_content.bind(
            "<Configure>",
            lambda e: self._debounce_sync_scroll(canvas, scrollbar)
        )
        c_window = canvas.create_window((0, 0), window=boost_content, anchor="nw")
        self._bind_canvas_auto_width(canvas, c_window, scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def _on_boost_wheel(e):
            return self._handle_canvas_wheel(e, canvas)


        tk.Label(boost_content, text="LIVE CS2 PROCESS PRIORITY & GAMING DNS OPTIMIZER", font=("Segoe UI", -16, "bold"), fg=FG_WHITE, bg=BG_CARD).pack(anchor="w")
        tk.Label(boost_content, text="Dedicated Win32 Process Priority Elevation & Low-Latency Gaming DNS Benchmark Switcher.", font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_CARD).pack(anchor="w", pady=(1, 6))

        # 1. LIVE CS2 CPU PROCESS PRIORITY CARD
        card = tk.Frame(boost_content, bg=BG_CARD_ROW, padx=14, pady=10, highlightbackground=BG_BORDER, highlightthickness=1)
        card.pack(fill="x", pady=(0, 8))

        head_r = tk.Frame(card, bg=BG_CARD_ROW)
        head_r.pack(fill="x")
        tk.Label(head_r, text="⚡ Live CS2 Process Priority Booster (Win32 HIGH_PRIORITY_CLASS)", font=("Segoe UI", 14, "bold"), fg=FG_WHITE, bg=BG_CARD_ROW).pack(side="left")
        tk.Label(head_r, text="🛡️ SAFE KERNEL SCHEDULING", font=("Segoe UI", 14, "bold"), fg=ACCENT_GREEN, bg="#0d261d", padx=8, pady=2).pack(side="right")

        tk.Label(
            card,
            text=(
                "Instructs the Windows kernel thread scheduler to prioritize cs2.exe ahead of background tasks. "
                "Unlike third-party 'RAM Cleaners' that force active memory into pagefile.sys (causing browser/Discord crashes and page-fault stutters), "
                "this booster strictly uses safe CPU scheduling with zero memory purging."
            ),
            font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_CARD_ROW, justify="left", anchor="w", wraplength=880
        ).pack(anchor="w", fill="x", pady=(2, 6))

        action_row = tk.Frame(card, bg=BG_CARD_ROW)
        action_row.pack(anchor="w", fill="x", pady=(2, 2))

        self.btn_boost = tk.Button(action_row, text="⚡ APPLY SAFE CS2 CPU PRIORITY BOOST", font=("Segoe UI", 10, "bold"),
                                   fg="#ffffff", bg=ACCENT_ORANGE, activebackground=ACCENT_ORANGE_HOVER,
                                   relief="flat", padx=14, pady=5, cursor="hand2", command=self.run_live_boost)
        self.btn_boost.pack(side="left")
        add_tooltip(self.btn_boost, "Safely elevates cs2.exe to Win32 High CPU Priority without touching system RAM working sets.")

        self.status_cs2_lbl = tk.Label(action_row, text="Status: Ready to boost", font=("Segoe UI", 10, "italic"), fg=ACCENT_CYAN, bg=BG_CARD_ROW)
        self.status_cs2_lbl.pack(side="left", padx=12)

        # 2. GAMING DNS OPTIMIZER & REAL-TIME BENCHMARK CARD
        dns_card = tk.Frame(boost_content, bg=BG_CARD_ROW, padx=14, pady=10, highlightbackground="#1e3a5f", highlightthickness=1)
        dns_card.pack(fill="x", pady=(0, 8))

        dns_top = tk.Frame(dns_card, bg=BG_CARD_ROW)
        dns_top.pack(fill="x")
        tk.Label(dns_top, text="🌐 GAMING DNS OPTIMIZER & REAL-TIME LATENCY BENCHMARK", font=("Segoe UI", -16, "bold"), fg=FG_WHITE, bg=BG_CARD_ROW).pack(side="left")

        self.dns_iface_var = tk.StringVar(value="Adapter: Detecting...  |  Active DNS: Checking...")
        tk.Label(dns_top, textvariable=self.dns_iface_var, font=("Consolas", 10, "bold"), fg=ACCENT_GREEN, bg=BG_CARD_ROW).pack(side="right")
        self._refresh_dns_interface_header()

        tk.Label(
            dns_card,
            text=(
                "Click ANY DNS provider row below (or enter your own Custom DNS IPs) to choose whichever DNS you prefer, "
                "or run the live benchmark to see which resolver has the lowest latency & jitter for your region. 100% reversible to ISP Default (DHCP)."
            ),
            font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_CARD_ROW, justify="left", anchor="w", wraplength=880
        ).pack(anchor="w", fill="x", pady=(2, 6))

        # DNS Action Toolbar
        dns_btn_bar = tk.Frame(dns_card, bg=BG_CARD_ROW)
        dns_btn_bar.pack(fill="x", pady=(0, 6))

        self.btn_dns_bench = tk.Button(
            dns_btn_bar, text="⚡ Benchmark All DNS Servers", font=("Segoe UI", -12, "bold"),
            fg="#ffffff", bg="#0284c7", activebackground="#0369a1", relief="flat",
            padx=10, pady=4, cursor="hand2", command=self.run_dns_benchmark_ui
        )
        self.btn_dns_bench.pack(side="left", padx=(0, 8))
        add_tooltip(self.btn_dns_bench, "Pings all 6 Gaming DNS servers in parallel (3 samples each) to find the lowest latency & jitter for your location.")

        self.btn_dns_restore = tk.Button(
            dns_btn_bar, text="↺ Restore ISP Default (DHCP)", font=("Segoe UI", -12, "bold"),
            fg="#cbd5e1", bg="#242b3b", activebackground="#334155", relief="flat",
            padx=10, pady=4, cursor="hand2", command=self.restore_dns_dhcp_ui
        )
        self.btn_dns_restore.pack(side="left")
        add_tooltip(self.btn_dns_restore, "Reverts your network adapter back to automatic ISP Default (DHCP) DNS and flushes cache.")

        self.dns_status_var = tk.StringVar(value="Click 'Use This DNS' on any row below to switch instantly.")
        tk.Label(dns_btn_bar, textvariable=self.dns_status_var, font=("Segoe UI", 10, "italic"), fg=ACCENT_AMBER, bg=BG_CARD_ROW).pack(side="right")

        # DNS Providers Table Container
        self.selected_dns_id = tk.StringVar(value="cloudflare")
        self.user_manually_picked_dns = False
        self.dns_bench_results = {}
        self.dns_row_widgets = {}

        dns_table = tk.Frame(dns_card, bg="#0d1118", padx=8, pady=6, highlightbackground=BG_BORDER, highlightthickness=1)
        dns_table.pack(fill="x", pady=(2, 2))

        for p in core_logic.DNS_PROVIDERS:
            pid = p["id"]
            is_init_sel = (pid == "cloudflare")
            rframe = tk.Frame(
                dns_table, bg="#162032" if is_init_sel else "#131924",
                padx=8, pady=5,
                highlightbackground=ACCENT_CYAN if is_init_sel else "#1f293d",
                highlightthickness=1, cursor="hand2"
            )
            rframe.pack(fill="x", pady=2)

            rb = tk.Radiobutton(
                rframe, text=f" {p['name']}", variable=self.selected_dns_id, value=pid,
                font=("Segoe UI", 10, "bold"), fg=FG_WHITE, bg=rframe["bg"],
                activebackground=rframe["bg"], activeforeground=ACCENT_CYAN, selectcolor=BG_WINDOW,
                cursor="hand2", command=lambda _pid=pid: self._on_dns_row_selected(_pid, manual=True)
            )
            rb.pack(side="left")

            ip_lbl = tk.Label(rframe, text=f"[{p['primary']} / {p['secondary']}]", font=("Consolas", 10), fg="#38bdf8", bg=rframe["bg"], cursor="hand2")
            ip_lbl.pack(side="left", padx=(6, 8))

            desc_lbl = tk.Label(rframe, text=p["desc"], font=("Segoe UI", 9), fg="#94a3b8", bg=rframe["bg"], cursor="hand2")
            desc_lbl.pack(side="left")

            use_btn = tk.Button(
                rframe, text="Use This DNS", font=("Segoe UI", -12, "bold"),
                fg="#ffffff", bg="#1e293b", activebackground=ACCENT_ORANGE, relief="flat",
                padx=8, pady=4, cursor="hand2",
                command=lambda _pid=pid: self._select_and_apply_dns_row(_pid)
            )
            use_btn.pack(side="right", padx=(6, 0))

            res_lbl = tk.Label(rframe, text="Click row to select", font=("Consolas", 10, "bold"), fg="#64748b", bg=rframe["bg"], cursor="hand2")
            res_lbl.pack(side="right", padx=4)

            for clickable in (rframe, ip_lbl, desc_lbl, res_lbl):
                clickable.bind("<Button-1>", lambda e, _pid=pid: self._on_dns_row_selected(_pid, manual=True))

            self.dns_row_widgets[pid] = {
                "frame": rframe,
                "rb": rb,
                "ip_lbl": ip_lbl,
                "desc_lbl": desc_lbl,
                "res_lbl": res_lbl,
                "use_btn": use_btn,
                "provider": p,
            }

        # Custom User-Defined DNS Row (Allows typing ANY Primary & Secondary DNS IPv4)
        cust_frame = tk.Frame(dns_table, bg="#131924", padx=8, pady=5, highlightbackground="#1f293d", highlightthickness=1)
        cust_frame.pack(fill="x", pady=(4, 2))

        tk.Label(cust_frame, text="🛠️ Custom DNS IPv4 (Any Provider):", font=("Segoe UI", 10, "bold"), fg=ACCENT_CYAN, bg="#131924").pack(side="left")
        tk.Label(cust_frame, text="Primary:", font=("Segoe UI", 10), fg="#cbd5e1", bg="#131924").pack(side="left", padx=(8, 2))
        self.custom_dns_primary_var = tk.StringVar(value="1.1.1.1")
        tk.Entry(cust_frame, textvariable=self.custom_dns_primary_var, width=13, font=("Consolas", 10, "bold"), bg=BG_CONSOLE, fg=ACCENT_GREEN, insertbackground=FG_WHITE, relief="flat", highlightbackground=BG_BORDER, highlightthickness=1).pack(side="left", padx=(0, 8))

        tk.Label(cust_frame, text="Secondary:", font=("Segoe UI", 10), fg="#cbd5e1", bg="#131924").pack(side="left", padx=(2, 2))
        self.custom_dns_secondary_var = tk.StringVar(value="1.0.0.1")
        tk.Entry(cust_frame, textvariable=self.custom_dns_secondary_var, width=13, font=("Consolas", 10, "bold"), bg=BG_CONSOLE, fg=ACCENT_CYAN, insertbackground=FG_WHITE, relief="flat", highlightbackground=BG_BORDER, highlightthickness=1).pack(side="left", padx=(0, 8))

        tk.Button(
            cust_frame, text="🚀 Apply Custom DNS", font=("Segoe UI", -12, "bold"),
            fg="#ffffff", bg="#0284c7", activebackground="#0369a1", relief="flat",
            padx=10, pady=4, cursor="hand2", command=self.apply_custom_dns_ui
        ).pack(side="right")

        # 2B. POST-SESSION CS2 FRAME-TIME & NETWORK JITTER LOG ANALYZER CARD
        log_card = tk.Frame(boost_content, bg=BG_CARD_ROW, padx=14, pady=10, highlightbackground="#334155", highlightthickness=1)
        log_card.pack(fill="x", pady=(0, 8))

        l_top = tk.Frame(log_card, bg=BG_CARD_ROW)
        l_top.pack(fill="x")
        tk.Label(l_top, text="📊 Post-Session CS2 Frame-Time & Network Jitter Log Analyzer", font=("Segoe UI", 14, "bold"), fg=ACCENT_ORANGE, bg=BG_CARD_ROW).pack(side="left")
        tk.Label(l_top, text="🛡️ 100% PASSIVE LOG PARSER (ZERO DLL HOOKS)", font=("Segoe UI", 14, "bold"), fg=ACCENT_GREEN, bg="#0d261d", padx=6, pady=1).pack(side="right")

        tk.Label(
            log_card,
            text=(
                "Passively analyzes CS2's standard console.log (requires -condebug in Launch Options) after or during your session to detect frame-time hitches, "
                "shader compile stalls, network jitter/misdelivery spikes, and loaded map VPK counts without injecting any third-party overlay."
            ),
            font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_CARD_ROW, justify="left", anchor="w", wraplength=880
        ).pack(anchor="w", fill="x", pady=(2, 6))

        l_btn_row = tk.Frame(log_card, bg=BG_CARD_ROW)
        l_btn_row.pack(fill="x", pady=(0, 4))

        b_scan_log = tk.Button(
            l_btn_row, text="🔍 Analyze CS2 Session Telemetry Log", font=("Segoe UI", 10, "bold"),
            fg="#ffffff", bg="#0284c7", activebackground="#0369a1", relief="flat",
            padx=12, pady=4, cursor="hand2", command=self.run_cs2_log_analyzer_ui
        )
        b_scan_log.pack(side="left")
        add_tooltip(b_scan_log, "Scans game/csgo/console.log for frame-time spikes, network packet misdelivery, and shader compilation events.")

        self.log_analyzer_summary_var = tk.StringVar(value="Click 'Analyze CS2 Session Telemetry Log' to inspect your latest session.")
        tk.Label(l_btn_row, textvariable=self.log_analyzer_summary_var, font=("Consolas", 10, "bold"), fg=ACCENT_CYAN, bg=BG_CARD_ROW).pack(side="left", padx=10)

        # 3. Technical Safety & Architecture Box
        info_card = tk.Frame(boost_content, bg="#11151e", padx=14, pady=10, highlightbackground=BG_BORDER, highlightthickness=1)
        info_card.pack(fill="x", pady=4)
        self.boost_info_card = info_card

        tk.Label(info_card, text="ℹ️ COMPLETE GUIDE: DNS PURPOSES, PROS & CONS, AND 100% SYSTEM SAFETY:", font=("Segoe UI", 14, "bold"), fg=ACCENT_ORANGE, bg="#11151e").pack(anchor="w", pady=(0, 6))

        explanations = [
            ("🌐 All Purposes of DNS (Gaming, Security, Privacy & Web Speed)",
             "DNS (Domain Name System) is the internet's phonebook: it translates domain names (Steam SDR relays, Workshop FastDL map mirrors, Discord voice servers, and websites) into IP addresses before your PC can connect. Beyond speed, specialized DNS resolvers also provide: (1) Bypassing overloaded or broken ISP DNS resolvers; (2) Malware & phishing domain blocking at the network layer (Quad9 9.9.9.9); (3) Blocking background ad-trackers and telemetry spikes while gaming (AdGuard 94.140.14.14); and (4) Privacy protection against ISP DNS logging and NXDOMAIN hijacking."),
            ("✅ DNS Optimizer PROS (What It Improves)",
             "• Faster initial handshakes with Steam API, Workshop FastDL custom map mirrors, Discord voice gateways, and everyday web browsing.\n"
             "• Eliminates ISP DNS lookup timeouts, regional DNS outages, and domain resolution jitter.\n"
             "• Optional zero-overhead security filtering (Quad9) or background telemetry/ad-tracker blocking (AdGuard).\n"
             "• 100% Safe for Windows, Steam VAC, and all anti-cheat systems: uses official Windows 'netsh' commands and is 1-click reversible to ISP Default (DHCP)."),
            ("⚠️ DNS Optimizer CONS & Honest Limitations (What To Know)",
             "• Does NOT lower raw in-game UDP ping once already connected: After your PC resolves a domain (or connects directly to a server IP like 74.91.124.21:27015), live game packets travel directly over UDP without querying DNS.\n"
             "• Unbenchmarked distant DNS can route to farther CDN mirrors: Picking a DNS server physically far from your region without benchmarking first can cause Steam/FastDL CDNs to pick a non-local download mirror. Always click '⚡ Benchmark All DNS Servers' first!\n"
             "• Hotel / School / Corporate Captive Portals: Public Wi-Fi login pages sometimes require the router's default local DNS. If a public Wi-Fi login page doesn't load, simply click '↺ Restore ISP Default (DHCP)'."),
            ("🚫 Why We Strictly Avoid 'RAM Cleaners' & Prioritize 100% System Safety",
             "Aggressive RAM cleaners (EmptyWorkingSet / Standby List purgers) forcibly evict active memory pages used by CS2, Discord, and browsers into slow disk pagefile.sys — causing Hard Page Fault stutters and random app/browser crashes. CS2 Command Center strictly avoids memory purging and instead uses safe Win32 HIGH_PRIORITY_CLASS thread scheduling so your system stays 100% stable.")
        ]

        self.boost_wrap_labels = []
        for title, desc in explanations:
            row = tk.Frame(info_card, bg="#11151e", pady=2)
            row.pack(fill="x", anchor="w")
            tk.Label(row, text=f"• {title}:", font=("Segoe UI", 10, "bold"), fg=FG_WHITE, bg="#11151e", anchor="w").pack(anchor="w", fill="x")
            lbl_desc = tk.Label(row, text=desc, font=("Segoe UI", 10), fg="#cbd5e1", bg="#11151e", justify="left", anchor="w", wraplength=880)
            lbl_desc.pack(anchor="w", fill="x", padx=12, pady=(1, 2))
            self.boost_wrap_labels.append(lbl_desc)

        def _bind_boost_wheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_boost_wheel, add="+")
            for c in widget.winfo_children():
                _bind_boost_wheel_recursive(c)

        _bind_boost_wheel_recursive(boost_content)

    def run_cs2_log_analyzer_ui(self):
        res = core_logic.analyze_cs2_session_logs(self.paths.get("cs2_exe"))
        self.log(f"[LOG ANALYZER] {res.get('message')}")
        if not res.get("found"):
            self.log_analyzer_summary_var.set("⚠️ console.log not found — Add -condebug in Launch Options tab!")
            messagebox.showinfo(
                "CS2 Session Log Analyzer",
                f"{res.get('message')}\n\n"
                "Tip: Go to the 'Launch Options' tab and add '-condebug' to enable passive session telemetry logging."
            )
            return

        summary = (
            f"Size: {res['file_size_mb']} MB | "
            f"Frame Hitches: {res['frame_hitch_events']} | "
            f"Shader Stalls: {res['shader_compile_events']} | "
            f"Net Jitter: {res['net_jitter_events']} | "
            f"VPKs Loaded: {res['vpk_load_events']}"
        )
        self.log_analyzer_summary_var.set(summary)
        details = (
            f"CS2 Session Telemetry Report ({res['log_path']}):\n\n"
            f"• Frame-Time Hitch Events: {res['frame_hitch_events']}\n"
            f"• Shader Compilation Stalls: {res['shader_compile_events']}\n"
            f"• Network Misdelivery / Jitter Warnings: {res['net_jitter_events']}\n"
            f"• Mounted Workshop / Map VPKs: {res['vpk_load_events']}\n"
            f"• Last Detected Map: {res['last_map']}\n\n"
            f"Diagnosis & Recommendation:\n{res['recommendation']}"
        )
        messagebox.showinfo("CS2 Frame-Time & Network Jitter Report", details)

    def _build_page_servers(self, page):
        tk.Label(page, text="ZOMBIE ESCAPE SERVER BROWSER & DIRECT CONNECTOR", font=("Segoe UI", -16, "bold"), fg=FG_WHITE, bg=BG_CARD).pack(anchor="w")
        tk.Label(page, text="Direct Steam Game Server Protocol (bypasses console) • Live Server Ping, Map & Player Monitor • ZE Graph Intel", font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_CARD).pack(anchor="w", pady=(1, 6))

        # 1. FEATURED GFL QUICK-CONNECT CARD
        gfl_card = tk.Frame(page, bg="#0E1512", padx=14, pady=10, highlightbackground="#FFE135", highlightthickness=1)
        gfl_card.pack(fill="x", pady=(0, 8))

        top_row = tk.Frame(gfl_card, bg="#0E1512")
        top_row.pack(fill="x")

        # Right Actions
        gfl_right = tk.Frame(top_row, bg="#0E1512")
        gfl_right.pack(side="right", padx=(8, 0))

        # GFL Priority Reserved Slot Tier Selector
        tier_row = tk.Frame(gfl_right, bg="#0E1512")
        tier_row.pack(anchor="e", pady=(0, 6))
        tk.Label(tier_row, text="GFL Slot Priority:", font=("Segoe UI", 10, "bold"), fg=ACCENT_ORANGE, bg="#151a24").pack(side="left", padx=2)
        saved_tier = self.config.get("gfl_sniper_tier", "mapper")
        tier_map = {
            "mapper": "Mapper / Supporter (≤ 62)",
            "normal": "Normal Player (≤ 61)",
            "vip": "VIP / Admin (≤ 63)"
        }
        self.gfl_tier_var = tk.StringVar(value=tier_map.get(saved_tier, "Mapper / Supporter (≤ 62)"))
        tier_opts = [
            "Mapper / Supporter (≤ 62)",
            "Normal Player (≤ 61)",
            "VIP / Admin (≤ 63)"
        ]
        self.gfl_tier_combo = ttk.Combobox(tier_row, textvariable=self.gfl_tier_var, values=tier_opts, state="readonly", width=24)
        self.gfl_tier_combo.pack(side="left", padx=2)
        self.gfl_tier_combo.bind("<<ComboboxSelected>>", self._on_gfl_tier_changed)
        add_tooltip(self.gfl_tier_combo, "Set sniper target player threshold (e.g. ≤ 62 for Supporter/Mapper reserved slot).")

        btn_box = tk.Frame(gfl_right, bg="#0E1512")
        btn_box.pack(anchor="e")

        b_gfl_conn = tk.Button(btn_box, text="⚡ Connect", font=("Segoe UI", -12, "bold"), width=9,
                  fg="#070B09", bg="#FFE135", activebackground="#FFF066",
                  relief="flat", padx=7, pady=4, cursor="hand2",
                  command=lambda: self.run_connect_workflow("74.91.124.21", 27015, "GFL Clan Zombie Escape"))
        b_gfl_conn.pack(side="left", padx=2)
        add_tooltip(b_gfl_conn, "Launches CS2 or connects directly to GFL Zombie Escape (74.91.124.21:27015) via Steam protocol.")

        self.btn_gfl_sniper = tk.Button(btn_box, text="🎯 Sniper", font=("Segoe UI", -12, "bold"), width=9,
                                        fg="#ffffff", bg="#854d0e", activebackground="#a16207",
                                        disabledforeground="#e2e8f0",
                                        relief="flat", padx=7, pady=4, cursor="hand2",
                                        command=self.toggle_gfl_slot_sniper)
        self.btn_gfl_sniper.pack(side="left", padx=2)
        add_tooltip(self.btn_gfl_sniper, "Arm Slot Sniper: monitors player count via silent UDP at 0.25s. Connects instantly via in-game console if CS2 is focused. If tabbed out or CS2 is closed, falls back to steam://connect (note: opening CS2 takes longer to load, so sniper is most effective when CS2 is already running).")

        b_gfl_players = tk.Button(btn_box, text="👥 Players", font=("Segoe UI", -12, "bold"), width=9,
                  fg="#ffffff", bg="#222b3d", activebackground="#2f3b52",
                  relief="flat", padx=7, pady=4, cursor="hand2",
                  command=lambda: self.open_players_dialog("74.91.124.21", 27015, "GFL Clan Zombie Escape"))
        b_gfl_players.pack(side="left", padx=2)
        add_tooltip(b_gfl_players, "Queries and displays the real-time player list, scores, and active duration.")

        b_gfl_copy = tk.Button(btn_box, text="📋 Copy", font=("Segoe UI", -12, "bold"), width=9,
                  fg="#94a3b8", bg="#1a202c", activebackground="#242e42", relief="flat", padx=7, pady=4, cursor="hand2",
                  command=lambda: self.copy_server_ip("74.91.124.21:27015"))
        b_gfl_copy.pack(side="left", padx=2)
        add_tooltip(b_gfl_copy, "Copies 'connect 74.91.124.21:27015' to your clipboard.")

        # Left Info with Map Thumbnail
        gfl_left = tk.Frame(top_row, bg="#0E1512")
        gfl_left.pack(side="left", fill="both", expand=True)

        # Map Preview Thumbnail Frame (Compact 105x64)
        self.gfl_thumb_frame = tk.Frame(gfl_left, bg="#0d1117", width=180, height=100, highlightbackground="#30363d", highlightthickness=1)
        self.gfl_thumb_frame.pack(side="left", padx=(0, 8))
        self.gfl_thumb_frame.pack_propagate(False)

        self.gfl_thumb_lbl = tk.Label(self.gfl_thumb_frame, text="MAP INTEL", font=("Segoe UI", 14, "bold"), fg="#8b949e", bg="#0d1117", cursor="hand2")
        self.gfl_thumb_lbl.pack(fill="both", expand=True)
        self.gfl_thumb_lbl.bind("<Button-1>", lambda e: self.open_3d_map(getattr(self, "current_gfl_clean_map", "")))
        add_tooltip(self.gfl_thumb_lbl, "Click to inspect this map in 3D (maps.cybo.dev)!")

        # Immediately attempt to load GFL thumbnail from cache or disk
        init_gfl_photo = self.get_map_photo(getattr(self, "current_gfl_clean_map", "ze_resident_evil_3"), is_large=True)
        if init_gfl_photo:
            self.gfl_thumb_lbl.config(image=init_gfl_photo, text="")
            self.gfl_thumb_lbl.image = init_gfl_photo

        # Info column
        gfl_info_col = tk.Frame(gfl_left, bg="#0E1512")
        gfl_info_col.pack(side="left", fill="both", expand=True)

        # Line 1: Badges
        header_tags = tk.Frame(gfl_info_col, bg="#0E1512")
        header_tags.pack(anchor="w")
        tk.Label(header_tags, text="★ PREMIER FEATURED SERVER", font=("Segoe UI", 14, "bold"), fg=ACCENT_ORANGE, bg="#151a24").pack(side="left")
        
        reg_pill = tk.Frame(header_tags, bg="#1e2638", padx=5, pady=1)
        reg_pill.pack(side="left", padx=5)
        tk.Label(reg_pill, text="CHICAGO, US", font=("Segoe UI", -11, "bold"), fg="#94a3b8", bg="#1e2638").pack()

        # Line 2: Server Title and Quick Links
        title_box = tk.Frame(gfl_info_col, bg="#0E1512")
        title_box.pack(anchor="w", pady=(1, 1))
        tk.Label(title_box, text="🇺🇸 GFL CLAN ZE 24 / 7", font=("Segoe UI", 14, "bold"), fg=FG_WHITE, bg="#151a24").pack(side="left")

        b_portal = tk.Label(title_box, text="🌐 Portal ↗", font=("Segoe UI", 9, "underline"), fg="#38bdf8", bg="#151a24", cursor="hand2")
        b_portal.pack(side="left", padx=(6, 2))
        b_portal.bind("<Button-1>", lambda e: launch_url_in_browser("https://gflclan.com"))
        add_tooltip(b_portal, "Visit the official GFL Clan community portal & forums (gflclan.com)")

        b_disc = tk.Label(title_box, text="💬 Discord ↗", font=("Segoe UI", 9, "underline"), fg="#818cf8", bg="#151a24", cursor="hand2")
        b_disc.pack(side="left", padx=2)
        b_disc.bind("<Button-1>", lambda e: launch_url_in_browser("https://discord.gg/gflze"))
        add_tooltip(b_disc, "Join the official GFL Clan Zombie Escape community Discord server")

        # Map & Timer row
        map_timer_row = tk.Frame(gfl_info_col, bg="#0E1512")
        map_timer_row.pack(anchor="w", pady=(1, 1))
        self.gfl_status_lbl = tk.Label(map_timer_row, textvariable=self.gfl_status_text, font=("Segoe UI", 10), fg=ACCENT_GREEN, bg="#151a24")
        self.gfl_status_lbl.pack(side="left")

        self.gfl_timer_lbl = tk.Label(map_timer_row, textvariable=self.gfl_timer_var, font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#151a24")
        self.gfl_timer_lbl.pack(side="left", padx=(8, 0))

        b_3d = tk.Button(map_timer_row, text="🌐 3D Map ↗", font=("Segoe UI", -12, "bold"),
                         fg="#38bdf8", bg="#1a2332", activebackground="#233045", relief="flat", padx=8, pady=4, cursor="hand2",
                         command=lambda: self.open_3d_map(getattr(self, "current_gfl_clean_map", "")))
        b_3d.pack(side="left", padx=(8, 0))
        add_tooltip(b_3d, "Open interactive 3D map viewer in browser (maps.cybo.dev).")

        # Workflow status label
        self.gfl_flow_lbl = tk.Label(gfl_info_col, textvariable=self.gfl_workflow_status, font=("Segoe UI", 10, "italic"), fg=ACCENT_CYAN, bg="#151a24")

        # Telemetry & Soundtrack Row (GFL Bottom Row)
        telemetry_row = tk.Frame(gfl_card, bg="#10141d", padx=8, pady=4, highlightbackground="#1e293b", highlightthickness=1)
        telemetry_row.pack(fill="x", pady=(8, 0))

        tk.Label(telemetry_row, textvariable=self.gfl_score_var, font=("Segoe UI", -12, "bold"), fg="#38bdf8", bg="#10141d").pack(side="left", padx=(4, 12))
        tk.Label(telemetry_row, textvariable=self.gfl_extends_var, font=("Segoe UI", -12, "bold"), fg="#fbbf24", bg="#10141d").pack(side="left", padx=(0, 12))
        tk.Label(telemetry_row, textvariable=self.gfl_geo_var, font=("Segoe UI", -11), fg="#94a3b8", bg="#10141d").pack(side="left", padx=(0, 12))

        b_soundtrack = tk.Button(telemetry_row, text="🎵 Soundtrack (Intel)", font=("Segoe UI", -12, "bold"),
                                 fg="#e879f9", bg="#2a163d", activebackground="#3d1d5a", relief="flat", padx=8, pady=4, cursor="hand2",
                                 command=lambda: self.open_soundtrack_dialog(getattr(self, "current_gfl_clean_map", "")))
        b_soundtrack.pack(side="left")
        add_tooltip(b_soundtrack, "View music soundtrack tracklist with 1-click YouTube player.")

        # 2. GLOBAL & CHINA COMMUNITY SERVERS CONTAINER
        list_container = tk.Frame(page, bg=BG_CARD, highlightbackground=BG_BORDER, highlightthickness=1)
        list_container.pack(fill="both", expand=True)

        self.list_head = tk.Frame(list_container, bg=BG_CARD_ROW, padx=10, pady=6)
        self.list_head.pack(fill="x")

        subtab_box = tk.Frame(self.list_head, bg=BG_CARD_ROW)
        subtab_box.pack(side="left")

        self.btn_subtab_global = tk.Button(subtab_box, text="🌐 Global Communities", font=("Segoe UI", 10, "bold"),
                                          fg=FG_WHITE, bg="#272e3d", relief="flat", padx=10, pady=6, cursor="hand2",
                                          command=lambda: self._switch_server_subtab("GLOBAL"))
        self.btn_subtab_global.pack(side="left", padx=(0, 4))
        add_tooltip(self.btn_subtab_global, "Browse international Zombie Escape servers (US, EU, JP, KR, RU).")

        self.btn_subtab_china = tk.Button(subtab_box, text="🇨🇳 Planet China", font=("Segoe UI", 10),
                                         fg="#94a3b8", bg=BG_CARD_ROW, relief="flat", padx=10, pady=6, cursor="hand2",
                                         command=lambda: self._switch_server_subtab("CHINA"))
        self.btn_subtab_china.pack(side="left")
        add_tooltip(self.btn_subtab_china, "Browse Chinese Zombie Escape community servers grouped by cluster.")

        # Community Slot Priority Selector
        comm_sniper_box = tk.Frame(self.list_head, bg=BG_CARD_ROW)
        comm_sniper_box.pack(side="left", padx=(14, 0))
        tk.Label(comm_sniper_box, text="Sniper Target:", font=("Segoe UI", 10, "bold"), fg=ACCENT_ORANGE, bg=BG_CARD_ROW).pack(side="left", padx=2)
        comm_opts = [
            "≤ 63 / 64 (1 Reserved)",
            "≤ 62 / 64 (2 Reserved)",
            "≤ 61 / 64 (3 Reserved)"
        ]
        self.comm_sniper_combo = ttk.Combobox(comm_sniper_box, textvariable=self.comm_sniper_target_var, values=comm_opts, state="readonly", width=20)
        self.comm_sniper_combo.pack(side="left", padx=2)
        self.comm_sniper_combo.bind("<<ComboboxSelected>>", self._on_comm_sniper_target_changed)
        add_tooltip(self.comm_sniper_combo, "Set slot sniper threshold for community servers (e.g. ≤ 62 if server has 2 reserved slots).")

        head_btns = tk.Frame(self.list_head, bg=BG_CARD_ROW)
        head_btns.pack(side="right")

        b_ref_all = tk.Button(head_btns, text="🔄 Refresh All", font=("Segoe UI", 9), fg="#94a3b8", bg=BG_CARD,
                  relief="flat", cursor="hand2", command=self.refresh_all_servers)
        b_ref_all.pack(side="left", padx=3)
        add_tooltip(b_ref_all, "Refresh live player counts, ping, and active map for all servers in the list.")

        b_add_srv = tk.Button(head_btns, text="➕ Add Server", font=("Segoe UI", 14, "bold"), fg=ACCENT_CYAN, bg=BG_CARD,
                  relief="flat", cursor="hand2", command=self.open_add_server_dialog)
        b_add_srv.pack(side="left")
        add_tooltip(b_add_srv, "Register your own custom CS2 community server to track in the browser.")

        # Live Quick Filter Bar
        search_bar = tk.Frame(list_container, bg="#0d1117", padx=10, pady=5, highlightbackground=BG_BORDER, highlightthickness=1)
        search_bar.pack(fill="x")
        tk.Label(search_bar, text="🔍 Filter Servers:", font=("Segoe UI", 10, "bold"), fg=FG_WHITE, bg="#0d1117").pack(side="left", padx=(0, 6))
        self.server_search_entry = tk.Entry(search_bar, textvariable=self.server_search_var, font=("Segoe UI", 9), bg="#161b22", fg="#ffffff",
                                            insertbackground="#ffffff", relief="flat", highlightbackground=BG_BORDER, highlightthickness=1)
        self.server_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.server_search_var.trace_add("write", lambda *args: self._filter_server_list())

        # China Dropdown Selector Bar
        self.china_bar = tk.Frame(list_container, bg="#11151e", padx=12, pady=6, highlightbackground=BG_BORDER, highlightthickness=1)
        
        tk.Label(self.china_bar, text="Select Community Cluster:", font=("Segoe UI", 10, "bold"), fg=ACCENT_ORANGE, bg="#11151e").pack(side="left")
        
        cluster_names = [f"🇨🇳 {c['name']} ({len(c['servers'])} Servers)" for c in self.china_clusters]
        self.china_combo = ttk.Combobox(self.china_bar, values=cluster_names, state="readonly", width=31)
        self.china_combo.current(0)
        self.china_combo.pack(side="left", padx=8)
        self.china_combo.bind("<<ComboboxSelected>>", lambda e: self._on_china_cluster_changed())

        self.cluster_desc_lbl = tk.Label(self.china_bar, text=self.china_clusters[0]["description"], font=("Segoe UI", 10, "italic"), fg=FG_MUTED, bg="#11151e")
        self.cluster_desc_lbl.pack(side="left", padx=4)

        # Scrollable container for servers
        canvas_container = tk.Frame(list_container, bg=BG_CARD)
        canvas_container.pack(fill="both", expand=True, padx=4, pady=4)

        self.server_canvas = tk.Canvas(canvas_container, bg=BG_CARD, highlightthickness=0, yscrollincrement=1)
        self.server_scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.server_canvas.yview, style="Vertical.Dark.TScrollbar")
        
        self.server_list_frame = tk.Frame(self.server_canvas, bg=BG_CARD)

        self.canvas_window = self.server_canvas.create_window((0, 0), window=self.server_list_frame, anchor="nw")
        self._bind_canvas_auto_width(self.server_canvas, self.canvas_window, self.server_scrollbar)
        self.server_canvas.configure(yscrollcommand=self.server_scrollbar.set)
        self.server_scrollbar.pack(side="right", fill="y")
        self.server_canvas.pack(side="left", fill="both", expand=True)

        def _on_server_wheel(e):
            return self._handle_canvas_wheel(e, self.server_canvas)

        self._on_server_wheel = _on_server_wheel


        # Attribution & Credits Notice
        credits_bar = tk.Frame(page, bg="#0d1117", padx=8, pady=3)
        credits_bar.pack(fill="x", pady=(4, 0))
        tk.Label(credits_bar,
                 text="Telemetry & Soundtracks: queeniemella (InterStella0 - ZE Graph) • 3D Map Viewer: cybo • CS2 Command Center by Geronimo",
                 font=("Segoe UI", 9), fg="#64748b", bg="#0d1117").pack(side="left")

        self._populate_server_list()

    def _switch_server_subtab(self, subtab: str):
        self.server_active_subtab = subtab
        if subtab == "GLOBAL":
            self.btn_subtab_global.config(fg=FG_WHITE, bg="#272e3d", font=("Segoe UI", 10, "bold"))
            self.btn_subtab_china.config(fg="#94a3b8", bg=BG_CARD_ROW, font=("Segoe UI", 10))
            self.china_bar.pack_forget()
        else:
            self.btn_subtab_china.config(fg=FG_WHITE, bg="#272e3d", font=("Segoe UI", 10, "bold"))
            self.btn_subtab_global.config(fg="#94a3b8", bg=BG_CARD_ROW, font=("Segoe UI", 10))
            self.china_bar.pack(fill="x", before=self.server_canvas.master, pady=(0, 2))
        self.server_canvas.yview_moveto(0.0)
        self._populate_server_list()
        self.refresh_all_servers()

    def _on_china_cluster_changed(self):
        idx = self.china_combo.current()
        if idx >= 0:
            self.current_china_index = idx
            self.cluster_desc_lbl.config(text=self.china_clusters[idx]["description"])
            self._populate_server_list()
            self.refresh_all_servers()

    def _filter_server_list(self):
        q = self.server_search_var.get().strip().lower()
        if not hasattr(self, "server_row_widgets"):
            return
        for sid, data in self.server_row_widgets.items():
            row_frame = data.get("row_frame")
            if not row_frame or not row_frame.winfo_exists():
                continue
            s = data.get("server", {})
            name = s.get("name", "").lower()
            region = s.get("region", "").lower()
            host = f"{s.get('host', '')}:{s.get('port', '')}".lower()
            cached_map = str(data.get("cached_map", "")).lower()

            if not q or (q in name or q in region or q in host or q in cached_map):
                row_frame.pack(fill="x", pady=2, padx=2)
            else:
                row_frame.pack_forget()

    def _populate_server_list(self):
        for w in self.server_list_frame.winfo_children():
            w.destroy()

        self.server_row_widgets = {}
        self.server_sniper_buttons = {}

        if self.server_active_subtab == "GLOBAL":
            servers_to_show = [s for s in self.servers_data if s["id"] != "gfl"]
        else:
            cluster = self.china_clusters[self.current_china_index]
            servers_to_show = cluster["servers"]

        for s in servers_to_show:
            sid = s.get("id", f"{s['host']}_{s['port']}")
            target_key = f"{s['host']}:{s['port']}"
            is_active_target = (self.sniper.is_active and self.active_sniper_target == target_key)

            row = tk.Frame(self.server_list_frame, bg="#151a24", padx=12, pady=7, highlightbackground="#222b3d", highlightthickness=1)
            row.pack(fill="x", pady=2, padx=2)

            # PACK RIGHT ACTION BUTTONS FIRST so they are never clipped
            right = tk.Frame(row, bg="#151a24")
            right.pack(side="right", padx=(6, 0))

            b_conn = tk.Button(right, text="⚡ Connect", font=("Segoe UI", -12, "bold"), width=9,
                      fg="#ffffff", bg=ACCENT_ORANGE, activebackground=ACCENT_ORANGE_HOVER,
                      relief="flat", padx=7, pady=4, cursor="hand2",
                      command=lambda s=s: self.run_connect_workflow(s["host"], s["port"], s["name"]))
            b_conn.pack(side="left", padx=2)
            add_tooltip(b_conn, f"Connect directly to {s['name']} via Steam protocol.")

            cooldown_until = getattr(self, "sniper_cooldown_until", {}).get(sid, 0)
            cooldown_rem = max(0, int(round(cooldown_until - time.time())))
            if is_active_target:
                btn_snip_txt = "🎯 Active"
                btn_snip_bg = "#d97706"
                btn_snip_state = "normal"
            elif cooldown_rem > 0:
                btn_snip_txt = f"⏳ ({cooldown_rem}s)"
                btn_snip_bg = "#475569"
                btn_snip_state = "disabled"
            else:
                btn_snip_txt = "🎯 Sniper"
                btn_snip_bg = "#854d0e"
                btn_snip_state = "normal"
            btn_sniper = tk.Button(right, text=btn_snip_txt, font=("Segoe UI", -12, "bold"), width=9,
                                   fg="#ffffff", bg=btn_snip_bg, activebackground="#b45309",
                                   disabledforeground="#e2e8f0", state=btn_snip_state,
                                   relief="flat", padx=7, pady=4, cursor="hand2",
                                   command=lambda s=s, sid=sid: self.toggle_server_slot_sniper(s["host"], s["port"], s["name"], sid))
            btn_sniper.pack(side="left", padx=2)
            self.server_sniper_buttons[sid] = btn_sniper
            add_tooltip(btn_sniper, f"Arm Slot Sniper for {s['name']}. Connects instantly via console when CS2 is focused, or via steam://connect if tabbed out or closed (best when CS2 is already running).")

            b_ply = tk.Button(right, text="👥 Players", font=("Segoe UI", -12, "bold"), width=9,
                      fg="#ffffff", bg="#222b3d", activebackground="#2f3b52",
                      relief="flat", padx=7, pady=4, cursor="hand2",
                      command=lambda s=s: self.open_players_dialog(s["host"], s["port"], s["name"]))
            b_ply.pack(side="left", padx=2)
            add_tooltip(b_ply, f"View live player list, score, and connected time for {s['name']}.")

            b_cp = tk.Button(right, text="📋 Copy", font=("Segoe UI", -12, "bold"), width=9,
                      fg="#94a3b8", bg="#1a202c", activebackground="#242e42", relief="flat", padx=7, pady=4, cursor="hand2",
                      command=lambda s=s: self.copy_server_ip(f"{s['host']}:{s['port']}"))
            b_cp.pack(side="left", padx=2)
            add_tooltip(b_cp, f"Copy 'connect {s['host']}:{s['port']}' to clipboard.")

            if s.get("is_custom"):
                b_del = tk.Button(right, text="✖", font=("Segoe UI", 14, "bold"),
                          fg=ACCENT_RED, bg="#151a24", relief="flat", padx=3, pady=6, cursor="hand2",
                          command=lambda s=s: self.remove_custom_server(s["id"]))
                b_del.pack(side="left")
                add_tooltip(b_del, f"Remove {s['name']} from your custom server list.")

            # PACK LEFT INFO SECOND
            left = tk.Frame(row, bg="#151a24")
            left.pack(side="left", fill="both", expand=True)

            cached = self.server_query_cache.get(sid, {})
            cached_map = cached.get("map")

            # Compact 50x32 Map Thumbnail Frame
            thumb_frame = tk.Frame(left, bg="#0d1117", width=110, height=64, highlightbackground="#30363d", highlightthickness=1)
            thumb_frame.pack(side="left", padx=(0, 6))
            thumb_frame.pack_propagate(False)

            thumb_lbl = tk.Label(thumb_frame, text="MAP", font=("Segoe UI", 6, "bold"), fg="#4b5563", bg="#0d1117", cursor="hand2")
            thumb_lbl.pack(fill="both", expand=True)
            thumb_lbl.bind("<Button-1>", lambda e, sid=sid: self.open_3d_map(self.server_query_cache.get(sid, {}).get("map", "")))
            add_tooltip(thumb_lbl, "Click to inspect active map in 3D (maps.cybo.dev)!")

            # Apply pre-loaded thumbnail from memory or disk cache
            if cached_map:
                photo_s = self.get_map_photo(cached_map, is_large=False)
                if photo_s:
                    thumb_lbl.config(image=photo_s, text="")
                    thumb_lbl.image = photo_s

            info_col = tk.Frame(left, bg="#151a24")
            info_col.pack(side="left", fill="both", expand=True)

            r1 = tk.Frame(info_col, bg="#151a24")
            r1.pack(anchor="w")
            flag = s.get('flag', '🇨🇳' if self.server_active_subtab == 'CHINA' else '🌐')
            srv_title = s['name']
            if len(srv_title) > 24:
                srv_title = srv_title[:22] + ".."
            tk.Label(r1, text=f"{flag}  {srv_title}", font=("Segoe UI", -14, "bold"), fg=FG_WHITE, bg="#151a24").pack(side="left")
            if s.get("region"):
                reg_pill = tk.Frame(r1, bg="#1e2638", padx=4, pady=1)
                reg_pill.pack(side="left", padx=5)
                tk.Label(reg_pill, text=s.get("region", "").upper(), font=("Segoe UI", -11, "bold"), fg="#94a3b8", bg="#1e2638").pack()

            # Live Player Count Badge
            c_info = cached.get("info") or {}
            c_curr = c_info.get("curr_players", 0)
            c_max = c_info.get("max_players", 64)
            p_text = f"👥 {c_curr}/{c_max} Players" if cached.get("online") else "👥 --/-- Players"
            ply_pill = tk.Frame(r1, bg="#0e2338", padx=5, pady=1)
            ply_pill.pack(side="left", padx=4)
            players_lbl = tk.Label(ply_pill, text=p_text, font=("Segoe UI", -11, "bold"), fg="#38bdf8", bg="#0e2338")
            players_lbl.pack()

            # Live Map Elapsed Time Label
            timer_lbl = tk.Label(r1, text="⏱️ 00:00 on map" if cached.get("online") else "⏱️ --:-- on map", font=("Segoe UI", -11, "bold"), fg=ACCENT_CYAN, bg="#151a24")
            timer_lbl.pack(side="left", padx=(6, 0))

            r2 = tk.Frame(info_col, bg="#151a24")
            r2.pack(anchor="w", pady=(1, 0))

            status_text = cached.get("display", "● Checking status...")
            status_col = ACCENT_GREEN if cached.get("online") else "#94a3b8"

            status_lbl = tk.Label(r2, text=status_text, font=("Segoe UI", -12), fg=status_col, bg="#151a24")
            status_lbl.pack(side="left")

            b_3d_row = tk.Button(r2, text="🌐 3D Map ↗", font=("Segoe UI", -12, "bold"),
                                 fg="#38bdf8", bg="#10141d", relief="flat", padx=6, pady=2, cursor="hand2",
                                 command=lambda sid=sid: self.open_3d_map(self.server_query_cache.get(sid, {}).get("map", "")))
            b_3d_row.pack(side="left", padx=(5, 0))
            add_tooltip(b_3d_row, "Open interactive 3D map viewer in browser (maps.cybo.dev).")

            # Community Discord Link Button on Row 2
            if s.get("discord"):
                b_disc_row = tk.Label(r2, text="💬 Discord ↗", font=("Segoe UI", -12, "underline"), fg="#818cf8", bg="#151a24", cursor="hand2")
                b_disc_row.pack(side="left", padx=(5, 0))
                b_disc_row.bind("<Button-1>", lambda e, url=s["discord"]: launch_url_in_browser(url))
                add_tooltip(b_disc_row, f"Join {s['name']} community Discord server.")

            # Row 3: Geo Radar Demographics
            r3 = tk.Frame(info_col, bg="#151a24")
            r3.pack(anchor="w", pady=(1, 0))
            geo_init = server_browser.get_server_demographics_text(s.get("region", ""), c_curr if cached.get("online") else 0)
            geo_lbl = tk.Label(r3, text=geo_init, font=("Segoe UI", -11), fg="#94a3b8", bg="#151a24")
            geo_lbl.pack(side="left")

            self.server_row_widgets[sid] = {
                "row_frame": row,
                "status_lbl": status_lbl,
                "players_lbl": players_lbl,
                "timer_lbl": timer_lbl,
                "geo_lbl": geo_lbl,
                "thumb_lbl": thumb_lbl,
                "cached_map": cached_map,
                "server": s
            }

        # Bottom spacer
        bottom_spacer = tk.Frame(self.server_list_frame, bg=BG_CARD, height=36)
        bottom_spacer.pack(fill="x", pady=(4, 12))

        self.server_list_frame.update_idletasks()
        self._sync_canvas_scroll(self.server_canvas, self.server_scrollbar)

        # Recursively bind mousewheel to all row child widgets
        def _bind_wheel_recursive(widget):
            widget.bind("<MouseWheel>", self._on_server_wheel, add="+")
            for c in widget.winfo_children():
                _bind_wheel_recursive(c)

        for w in self.server_list_frame.winfo_children():
            _bind_wheel_recursive(w)
    def _on_gfl_tier_changed(self, event=None):
        val = self.gfl_tier_var.get()
        if "Mapper" in val:
            self.config["gfl_sniper_tier"] = "mapper"
        elif "Normal" in val:
            self.config["gfl_sniper_tier"] = "normal"
        elif "VIP" in val:
            self.config["gfl_sniper_tier"] = "vip"
        app_config.save_config(self.config)
        self.log(f"[SNIPER] GFL Slot Priority configured to: {val}")
        if self.sniper.is_active and self.active_sniper_target == "74.91.124.21:27015":
            self.toggle_gfl_slot_sniper()
            self.toggle_gfl_slot_sniper()

    def _on_comm_sniper_target_changed(self, event=None):
        val = self.comm_sniper_target_var.get()
        self.config["community_sniper_slot_target"] = val
        app_config.save_config(self.config)
        self.log(f"[SNIPER] Community Slot Priority configured to: {val}")
        if self.sniper.is_active and self.active_sniper_target and self.active_sniper_target != "74.91.124.21:27015":
            parts = self.active_sniper_target.split(":")
            if len(parts) == 2:
                h = parts[0]
                p = int(parts[1])
                n = getattr(self.sniper, "target_name", "Community Server")
                sid = f"{h}_{p}"
                self.toggle_server_slot_sniper(h, p, n, sid)
                self.toggle_server_slot_sniper(h, p, n, sid)

    def toggle_gfl_slot_sniper(self):
        """Toggles slot sniper on premier GFL Clan ZE server."""
        self.toggle_server_slot_sniper("74.91.124.21", 27015, "GFL Clan Zombie Escape 24/7", "gfl")

    def toggle_server_slot_sniper(self, host: str, port: int, name: str, sid: str = None):
        """Universal Slot Sniper: polls player count at 0.25s, fires console connect every 1.0s, and stops + triggers 10s cooldown when a slot opens."""
        if sid is None:
            sid = "gfl" if (host == "74.91.124.21" and port == 27015) else f"{host}_{port}"

        if not hasattr(self, "sniper_cooldown_until"):
            self.sniper_cooldown_until = {}

        # Ignore clicks if currently in 10s cooldown for this server
        cooldown_rem = max(0, int(round(self.sniper_cooldown_until.get(sid, 0) - time.time())))
        if cooldown_rem > 0:
            self.log(f"[SNIPER] Slot Sniper is on cooldown ({cooldown_rem}s remaining) for {name}.")
            return

        if hasattr(self, "server_browser") and hasattr(self.server_browser, "is_connection_in_flight"):
            if self.server_browser.is_connection_in_flight() and not self.sniper.is_active:
                self.log(f"[SNIPER] Connection is currently in progress. Sniper cannot be armed while connecting.")
                return

        target_key = f"{host}:{port}"

        # If sniper is currently running for this exact server, cancel it
        if self.sniper.is_active and self.active_sniper_target == target_key:
            self.sniper.stop()
            self.active_sniper_target = None
            self._reset_all_sniper_buttons()
            if host == "74.91.124.21":
                self.gfl_workflow_status.set("Status: Ready to connect")
            self._update_server_sniper_label(sid, None)
            self.log(f"[SNIPER] Slot Sniper disarmed for {name}.")
            return

        # Otherwise, stop any existing sniper and activate for this server
        self.sniper.stop()
        self.active_sniper_target = target_key
        self._reset_all_sniper_buttons()

        if not core_logic.is_cs2_running():
            self.active_sniper_target = None
            messagebox.showinfo(
                "CS2 Required for Slot Sniper",
                "Counter-Strike 2 must be running to arm the Slot Sniper!\n\n"
                "Please launch CS2 first (or click 'Connect' to open CS2 cleanly), "
                "then click Slot Sniper to spam console connect every 1s and auto-stop with a 10s cooldown when a player leaves."
            )
            return

        # Determine custom target threshold (for GFL or community reserved slots)
        target_max_players = None
        tier_label = ""
        if host == "74.91.124.21":
            tier_val = getattr(self, "gfl_tier_var", None)
            tier_str = tier_val.get() if tier_val else self.config.get("gfl_sniper_tier", "mapper")
            if "Mapper" in tier_str or tier_str == "mapper":
                target_max_players = 62
                tier_label = "Mapper / Supporter"
            elif "Normal" in tier_str or tier_str == "normal":
                target_max_players = 61
                tier_label = "Normal Player"
            elif "VIP" in tier_str or tier_str == "vip":
                target_max_players = 63
                tier_label = "VIP / Admin"
        else:
            comm_val = getattr(self, "comm_sniper_target_var", None)
            comm_str = comm_val.get() if comm_val else self.config.get("community_sniper_slot_target", "63")
            if "61" in comm_str:
                target_max_players = 61
                tier_label = "Priority Slot (≤ 61)"
            elif "62" in comm_str:
                target_max_players = 62
                tier_label = "Priority Slot (≤ 62)"
            else:
                target_max_players = 63
                tier_label = "Standard Slot (≤ 63)"

        # Arm the Slot Sniper
        self.active_sniper_target = target_key
        self._set_sniper_button_active(sid, True)
        tier_sub = f" [Priority: ≤{target_max_players} for {tier_label}]" if target_max_players else ""
        if host == "74.91.124.21" and port == 27015:
            self.btn_gfl_sniper.config(text="🎯 Active", bg="#d97706", activebackground="#b45309", state="normal")
            self.gfl_workflow_status.set(f"🎯 Active: Watching for open slot (Silent UDP 0.25s / 0 RAM){tier_sub}...")

        self.log(f"[SNIPER] Slot Sniper Active for {name} ({host}:{port}){tier_sub}. Monitoring player count via silent UDP A2S at 0.25s (0 CS2 RAM stacking)...")

        def status_cb(state_type, msg):
            if state_type in ("waiting", "polling"):
                if host == "74.91.124.21":
                    self.safe_after(0, lambda: self.gfl_workflow_status.set(f"🎯 {msg}"))
                self.safe_after(0, lambda: self._update_server_sniper_label(sid, f"🎯 {msg}"))
            elif state_type == "success":
                self.safe_after(0, lambda: self._on_sniper_success_ui(host, port, name, sid))

        def success_cb(h, p, n, curr_p, max_p):
            t_txt = f" [{tier_label}]" if tier_label else ""
            self.log(f"[SNIPER] Open slot detected on {n} ({curr_p}/{max_p}){t_txt}! Executed rapid in-game console connect & started 10s cooldown.")

        # Update Discord Rich Presence if sniper is armed
        if self.config.get("discord_rpc_enabled", False) and self.config.get("discord_client_id"):
            try:
                t_str = f"Target: ≤{target_max_players}" if target_max_players else "Waiting for Slot"
                snip_dtl = f"🎯 Sniping {name}"
                snip_st = f"Active ({t_str})"
                self.discord_rpc.set_activity(
                    details=snip_dtl,
                    state=snip_st,
                    start_timestamp=int(time.time()),
                    large_image=None
                )
                self.after(0, lambda d=snip_dtl, s=snip_st: self._update_discord_preview_labels(d, s))
            except Exception:
                pass

        self.sniper.start(
            host=host,
            port=port,
            name=name,
            target_max_players=target_max_players,
            tier_label=tier_label,
            status_cb=status_cb,
            success_cb=success_cb,
            initial_is_full=True
        )

    def _reset_all_sniper_buttons(self):
        if not hasattr(self, "sniper_cooldown_until"):
            self.sniper_cooldown_until = {}
        gfl_rem = max(0, int(round(self.sniper_cooldown_until.get("gfl", 0) - time.time())))
        if gfl_rem > 0:
            self.btn_gfl_sniper.config(text=f"⏳ ({gfl_rem}s)", bg="#475569", state="disabled", disabledforeground="#e2e8f0")
        else:
            self.btn_gfl_sniper.config(text="🎯 Slot Sniper", bg="#854d0e", activebackground="#a16207", state="normal")
        for sid, btn in self.server_sniper_buttons.items():
            try:
                rem = max(0, int(round(self.sniper_cooldown_until.get(sid, 0) - time.time())))
                if rem > 0:
                    btn.config(text=f"⏳ ({rem}s)", bg="#475569", state="disabled", disabledforeground="#e2e8f0")
                else:
                    btn.config(text="🎯 Sniper", bg="#854d0e", activebackground="#a16207", state="normal")
            except Exception:
                pass

    def _set_sniper_button_active(self, sid: str, is_active: bool):
        if sid in self.server_sniper_buttons:
            btn = self.server_sniper_buttons[sid]
            try:
                if is_active:
                    btn.config(text="🎯 Active", bg="#d97706", activebackground="#b45309", state="normal")
                else:
                    btn.config(text="🎯 Sniper", bg="#854d0e", activebackground="#a16207", state="normal")
            except Exception:
                pass

    def _update_server_sniper_label(self, sid: str, text: Optional[str]):
        if hasattr(self, "server_row_widgets") and sid in self.server_row_widgets:
            w = self.server_row_widgets[sid]["status_lbl"]
            if text:
                w.config(text=f"   {text}", fg=ACCENT_AMBER)
            else:
                cached = self.server_query_cache.get(sid, {})
                disp = cached.get("display", "● Ready to Join")
                col = ACCENT_GREEN if cached.get("online") else "#94a3b8"
                w.config(text=f"   {disp}", fg=col)

    def _start_sniper_cooldown_timer(self, host: str, port: int, name: str, sid: str, duration: int = 10):
        """Replaces 'Active' on the Slot Sniper button with a 10-second cooldown countdown, then restores it."""
        if not hasattr(self, "sniper_cooldown_until"):
            self.sniper_cooldown_until = {}
        is_gfl = (host == "74.91.124.21" and port == 27015) or sid == "gfl"
        key = "gfl" if is_gfl else sid
        self.sniper_cooldown_until[key] = time.time() + duration
        if not is_gfl:
            self.sniper_cooldown_until[sid] = time.time() + duration

        def _tick(remaining: int):
            if remaining > 0:
                lbl = f"⏳ ({remaining}s)"
                if is_gfl:
                    try:
                        self.btn_gfl_sniper.config(text=lbl, bg="#475569", state="disabled", disabledforeground="#e2e8f0")
                        self.gfl_workflow_status.set(f"🎯 Slot detected! Attempted connect — ({remaining}s)")
                    except Exception:
                        pass
                if sid in self.server_sniper_buttons:
                    try:
                        self.server_sniper_buttons[sid].config(text=lbl, bg="#475569", state="disabled", disabledforeground="#e2e8f0")
                    except Exception:
                        pass
                self._update_server_sniper_label(sid, f"🎯 Slot detected! ({remaining}s)...")
                self.safe_after(1000, lambda: _tick(remaining - 1))
            else:
                self.sniper_cooldown_until.pop(key, None)
                self.sniper_cooldown_until.pop(sid, None)
                if is_gfl:
                    try:
                        self.btn_gfl_sniper.config(text="🎯 Slot Sniper", bg="#854d0e", activebackground="#a16207", state="normal")
                        self.gfl_workflow_status.set("Status: Ready to connect (Click Slot Sniper again if needed)")
                    except Exception:
                        pass
                if sid in self.server_sniper_buttons:
                    try:
                        self.server_sniper_buttons[sid].config(text="🎯 Sniper", bg="#854d0e", activebackground="#a16207", state="normal")
                    except Exception:
                        pass
                self._update_server_sniper_label(sid, None)

        _tick(duration)

    def _on_sniper_success_ui(self, host: str, port: int, name: str, sid: str):
        # Stop sniper immediately and start 10-second button cooldown
        self.sniper.stop()
        self.active_sniper_target = None
        self.active_tracked_server = (host, port, name)
        self.active_tracked_since = time.time()
        self.discord_session_start = int(time.time())

        self._start_sniper_cooldown_timer(host, port, name, sid, duration=10)

        # Update Discord Rich Presence if enabled
        if self.config.get("discord_rpc_enabled", False) and self.config.get("discord_client_id"):
            try:
                self.discord_rpc.set_activity(
                    details=f"{name}",
                    state="Connected via Slot Sniper 🎯",
                    start_timestamp=self.discord_session_start,
                    large_image=None
                )
                self.after(0, lambda n=name: self._update_discord_preview_labels(n, "Connected via Slot Sniper 🎯"))
            except Exception:
                pass

    # --- PC MAINTENANCE TAB (SMOOTH MOUSEWHEEL SCROLLING) ---

    def _build_page_maintenance(self, page):
        canvas = tk.Canvas(page, bg=BG_CARD, highlightthickness=0, yscrollincrement=1)
        scrollbar = ttk.Scrollbar(page, orient="vertical", command=canvas.yview, style="Vertical.Dark.TScrollbar")
        self.maint_canvas = canvas
        self.maint_scrollbar = scrollbar
        maint_content = tk.Frame(canvas, bg=BG_CARD)

        maint_content.bind(
            "<Configure>",
            lambda e: self._debounce_sync_scroll(canvas, scrollbar)
        )
        c_window = canvas.create_window((0, 0), window=maint_content, anchor="nw")
        self._bind_canvas_auto_width(canvas, c_window, scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def _on_maint_wheel(e):
            return self._handle_canvas_wheel(e, canvas)

        self._on_maint_wheel = _on_maint_wheel


        tk.Label(maint_content, text="SAFE SYSTEM & STORAGE MAINTENANCE", font=("Segoe UI", -16, "bold"), fg=FG_WHITE, bg=BG_CARD).pack(anchor="w")
        tk.Label(maint_content, text="100% safe PC hygiene: Free up storage, clear cache bloat, inspect drive health, and flush DNS.", font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_CARD).pack(anchor="w", pady=(1, 8))

        # Weekly Maintenance & Optimization Reminder Banner
        self.maint_weekly_banner_box = tk.Frame(maint_content, bg=BG_CARD)
        self.maint_weekly_banner_box.pack(fill="x", pady=(0, 6))
        self._refresh_weekly_maint_banner()

        # Transparency Note: System Hygiene & Consistency vs. Raw FPS
        maint_note = tk.Frame(maint_content, bg="#101826", padx=12, pady=7, highlightbackground="#1e3a5f", highlightthickness=1)
        maint_note.pack(fill="x", pady=(0, 6))
        tk.Label(
            maint_note,
            text="ℹ️  PURPOSE OF PC MAINTENANCE: STORAGE HEALTH, ASSET STREAMING & OS STABILITY",
            font=("Segoe UI", 10, "bold"), fg=ACCENT_CYAN, bg="#101826"
        ).pack(anchor="w")
        tk.Label(
            maint_note,
            text=(
                "PC Maintenance is NOT meant to increase raw GPU framerate beyond hardware limits. "
                "Instead, it prevents SSD write-cache degradation (when drives exceed 85% full), eliminates map-loading & texture-streaming hitches "
                "via SSD TRIM, repairs corrupted Windows system DLLs (SFC/DISM), and reclaims tens of gigabytes of bloated cache safely."
            ),
            font=("Segoe UI", 9), fg="#cbd5e1", bg="#101826", justify="left", anchor="w", wraplength=880
        ).pack(anchor="w", fill="x", pady=(1, 0))

        # Standard User Mode Notice Banner with 1-Click Elevation Helper
        if not self.admin_status:
            admin_banner = tk.Frame(maint_content, bg="#131d2e", padx=12, pady=8, highlightbackground="#2563eb", highlightthickness=1)
            admin_banner.pack(fill="x", pady=(0, 8))

            ab_left = tk.Frame(admin_banner, bg="#131d2e")
            ab_left.pack(side="left", fill="x", expand=True)

            tk.Label(ab_left, text="🛡️  STANDARD USER MODE (SAFE HYGIENE ACTIVE)", font=("Segoe UI", 10, "bold"), fg="#60a5fa", bg="#131d2e").pack(anchor="w")
            tk.Label(ab_left, text="Disk cleanups (Cache, Temp Files, Custom Maps, DNS Flush) work 100%. Deep Windows repairs (SSD TRIM, SFC, DISM) require Administrator privileges.",
                     font=("Segoe UI", 10), fg="#cbd5e1", bg="#131d2e").pack(anchor="w", pady=(1, 0))

            b_elev = tk.Button(admin_banner, text="⚡ Relaunch as Administrator", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#2563eb",
                               activebackground="#1d4ed8", activeforeground="#ffffff", relief="flat", padx=10, pady=4, cursor="hand2",
                               command=self.relaunch_as_admin)
            b_elev.pack(side="right", padx=(8, 0))
            add_tooltip(b_elev, "Prompts Windows UAC to relaunch CS2 Command Center with Administrator privileges for deep repairs.")

        # 1. Drive Storage & Health Monitor Card
        drive_box = tk.Frame(maint_content, bg=BG_CARD_ROW, padx=12, pady=8, highlightbackground=BG_BORDER, highlightthickness=1)
        drive_box.pack(fill="x", pady=(0, 6))

        d_header = tk.Frame(drive_box, bg=BG_CARD_ROW)
        d_header.pack(fill="x", pady=(0, 4))
        tk.Label(d_header, text="STORAGE CAPACITY & HEALTH MONITOR", font=("Segoe UI", -13, "bold"), fg=FG_WHITE, bg=BG_CARD_ROW).pack(side="left")
        
        tk.Button(d_header, text="🔄 Refresh", font=("Segoe UI", 9), fg="#94a3b8", bg=BG_CARD,
                  relief="flat", cursor="hand2", command=lambda: self._refresh_drives_list(d_list_frame)).pack(side="right")

        d_list_frame = tk.Frame(drive_box, bg=BG_CARD_ROW)
        d_list_frame.pack(fill="x", pady=2)
        self.d_list_frame = d_list_frame
        self._refresh_drives_list(d_list_frame)

        # 2. CS2 / ZE Custom Map Cleaner & Workshop VPK Health Verifier Card
        map_card = tk.Frame(maint_content, bg=BG_CARD_ROW, padx=12, pady=8, highlightbackground=BG_BORDER, highlightthickness=1)
        map_card.pack(fill="x", pady=(0, 6))

        tk.Label(map_card, text="🗺️ CS2 CUSTOM MAP CLEANER & STEAM WORKSHOP VPK HEALTH VERIFIER", font=("Segoe UI", 10, "bold"), fg=FG_WHITE, bg=BG_CARD_ROW).pack(anchor="w", pady=(0, 2))
        tk.Label(map_card, text="Inspect community workshop maps, verify .vpk binary headers (0x55aa1234) against Host_Error / Missing VPK disconnects, and reclaim SSD space.", font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_CARD_ROW, wraplength=880, justify="left", anchor="w").pack(anchor="w", fill="x", pady=(0, 4))

        m_btn_row = tk.Frame(map_card, bg=BG_CARD_ROW)
        m_btn_row.pack(fill="x", pady=(2, 2))

        b_mclean = tk.Button(m_btn_row, text="🗺️ Inspect & Clean Custom Maps", font=("Segoe UI", 10, "bold"),
                   fg="#ffffff", bg="#2563eb", activebackground="#1d4ed8", relief="flat",
                   padx=12, pady=5, cursor="hand2", command=self.open_custom_map_cleaner_dialog)
        b_mclean.pack(side="left", padx=(0, 6))
        add_tooltip(b_mclean, "Opens the interactive Custom ZE Map Cleaner to safely inspect and delete unused .vpk map packages.")

        b_vpk_verify = tk.Button(m_btn_row, text="📦 Verify Workshop VPK Health", font=("Segoe UI", 10, "bold"),
                   fg="#ffffff", bg="#0284c7", activebackground="#0369a1", relief="flat",
                   padx=12, pady=5, cursor="hand2", command=self.run_workshop_vpk_verifier_ui)
        b_vpk_verify.pack(side="left", padx=(0, 6))
        add_tooltip(b_vpk_verify, "Scans steamapps/workshop/content/730/ and verifies every .vpk binary header for corrupted or incomplete downloads.")

        b_vpk_repair = tk.Button(m_btn_row, text="🔧 Repair Corrupted VPKs", font=("Segoe UI", 10),
                   fg="#cbd5e1", bg="#242b3b", activebackground="#334155", relief="flat",
                   padx=10, pady=5, cursor="hand2", command=self.repair_workshop_vpks_ui)
        b_vpk_repair.pack(side="left")
        add_tooltip(b_vpk_repair, "Safely purges only corrupted/incomplete Workshop .tmp/.vpk folders so Steam cleanly re-downloads them.")

        self.map_stat_lbl = tk.Label(map_card, text="Scanning maps & workshop content...", font=("Segoe UI", 10), fg=ACCENT_CYAN, bg=BG_CARD_ROW)
        self.map_stat_lbl.pack(anchor="w", pady=(4, 0))
        self._quick_map_stats_check()

        # 3. Safe Cache & Network Cleaners Card
        clean_card = tk.Frame(maint_content, bg=BG_CARD_ROW, padx=12, pady=8, highlightbackground=BG_BORDER, highlightthickness=1)
        clean_card.pack(fill="x", pady=(0, 6))

        tk.Label(clean_card, text="SAFE DISK & CACHE CLEANUP", font=("Segoe UI", 10, "bold"), fg=FG_WHITE, bg=BG_CARD_ROW).pack(anchor="w", pady=(0, 4))

        cb_grid = tk.Frame(clean_card, bg=BG_CARD_ROW)
        cb_grid.pack(fill="x", pady=1)

        cb1 = tk.Checkbutton(cb_grid, text=" Purge Windows Temp Files (%TEMP% & Windows\\Temp)", variable=self.maint_temp,
                             font=("Segoe UI", 10), fg=FG_WHITE, bg=BG_CARD_ROW, activebackground=BG_CARD_ROW,
                             selectcolor=BG_WINDOW, relief="flat")
        cb1.grid(row=0, column=0, sticky="w", pady=1, padx=(0, 8))
        add_tooltip(cb1, "Deletes temporary cache files generated by Windows and desktop programs.")

        cb2 = tk.Checkbutton(cb_grid, text=" Purge Windows Update Cache (SoftwareDistribution)", variable=self.maint_win_update,
                             font=("Segoe UI", 10), fg=FG_WHITE, bg=BG_CARD_ROW, activebackground=BG_CARD_ROW,
                             selectcolor=BG_WINDOW, relief="flat")
        cb2.grid(row=0, column=1, sticky="w", pady=1)
        add_tooltip(cb2, "Clears residual Windows update download installers to recover drive storage.")

        cb3 = tk.Checkbutton(cb_grid, text=" Purge Discord & Steam Web Cache (Never logs you out)", variable=self.maint_discord_steam,
                             font=("Segoe UI", 10), fg=FG_WHITE, bg=BG_CARD_ROW, activebackground=BG_CARD_ROW,
                             selectcolor=BG_WINDOW, relief="flat")
        cb3.grid(row=1, column=0, sticky="w", pady=1, padx=(0, 8))
        add_tooltip(cb3, "Removes bloated CEF/Chromium web cache without clearing login sessions.")

        cb4 = tk.Checkbutton(cb_grid, text=" Purge Explorer Thumbnail Cache (thumbcache_*.db)", variable=self.maint_thumb,
                             font=("Segoe UI", 10), fg=FG_WHITE, bg=BG_CARD_ROW, activebackground=BG_CARD_ROW,
                             selectcolor=BG_WINDOW, relief="flat")
        cb4.grid(row=1, column=1, sticky="w", pady=1)
        add_tooltip(cb4, "Rebuilds Windows file explorer thumbnail database to fix icon corruption.")

        cb5 = tk.Checkbutton(cb_grid, text=" Empty Windows Recycle Bin (Purges deleted trash)", variable=self.maint_recycle,
                             font=("Segoe UI", 10), fg=FG_WHITE, bg=BG_CARD_ROW, activebackground=BG_CARD_ROW,
                             selectcolor=BG_WINDOW, relief="flat")
        cb5.grid(row=2, column=0, sticky="w", pady=1, padx=(0, 8))
        add_tooltip(cb5, "Permanently frees space taken by discarded files in your Recycle Bin.")

        cb6 = tk.Checkbutton(cb_grid, text=" Flush Windows DNS Cache (Refreshes server lookups)", variable=self.maint_dns,
                             font=("Segoe UI", 10), fg=FG_WHITE, bg=BG_CARD_ROW, activebackground=BG_CARD_ROW,
                             selectcolor=BG_WINDOW, relief="flat")
        cb6.grid(row=2, column=1, sticky="w", pady=1)
        add_tooltip(cb6, "Flushes local DNS resolver cache to fix community server connection timeouts.")

        cb_grid.columnconfigure(0, weight=1)
        cb_grid.columnconfigure(1, weight=1)

        btn_row = tk.Frame(clean_card, bg=BG_CARD_ROW)
        btn_row.pack(anchor="w", pady=(6, 2))

        b_run_pc = tk.Button(btn_row, text="🧹 RUN SELECTED PC CLEANUP", font=("Segoe UI", 14, "bold"),
                  fg="#ffffff", bg=ACCENT_ORANGE, activebackground=ACCENT_ORANGE_HOVER,
                  relief="flat", padx=16, pady=4, cursor="hand2", command=self.run_pc_maintenance)
        b_run_pc.pack(side="left")
        add_tooltip(b_run_pc, "Executes all checked cleanup routines above safely.")

        # 4. Built-in Windows Tools Card
        tools_card = tk.Frame(maint_content, bg=BG_CARD_ROW, padx=12, pady=8, highlightbackground=BG_BORDER, highlightthickness=1)
        tools_card.pack(fill="x", pady=(0, 4))

        tk.Label(tools_card, text="OFFICIAL WINDOWS SYSTEM TOOLS & DIAGNOSTICS", font=("Segoe UI", 10, "bold"), fg=FG_WHITE, bg=BG_CARD_ROW).pack(anchor="w", pady=(0, 4))

        tools_grid = tk.Frame(tools_card, bg=BG_CARD_ROW)
        tools_grid.pack(fill="x", pady=(2, 0))
        tools_grid.columnconfigure(0, weight=1, uniform="tools_col")
        tools_grid.columnconfigure(1, weight=1, uniform="tools_col")
        tools_grid.columnconfigure(2, weight=1, uniform="tools_col")

        b_clnmgr = tk.Button(tools_grid, text="🗄️ Launch Disk Cleanup", font=("Segoe UI", 10),
                  fg="#ffffff", bg="#242b3b", activebackground="#334155", relief="flat",
                  padx=6, pady=5, cursor="hand2", command=self.launch_cleanmgr_ui)
        b_clnmgr.grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=(0, 4))
        add_tooltip(b_clnmgr, "Launches Windows cleanmgr.exe to review system dump and old installation files.")

        b_trim = tk.Button(tools_grid, text="⚡ Run SSD TRIM (defrag /O)", font=("Segoe UI", 10),
                  fg="#ffffff", bg="#242b3b", activebackground="#334155", relief="flat",
                  padx=6, pady=5, cursor="hand2", command=self.run_ssd_trim_ui)
        b_trim.grid(row=0, column=1, sticky="ew", padx=(0, 4), pady=(0, 4))
        add_tooltip(b_trim, "Issues ATA TRIM to SSD blocks to maintain ultra-fast flash write speeds.")

        b_startup = tk.Button(tools_grid, text="🚀 Startup Apps Manager", font=("Segoe UI", 10),
                  fg="#ffffff", bg="#242b3b", activebackground="#334155", relief="flat",
                  padx=6, pady=5, cursor="hand2", command=self.open_startup_apps_ui)
        b_startup.grid(row=0, column=2, sticky="ew", pady=(0, 4))
        add_tooltip(b_startup, "Opens Windows Task Manager Startup tab to disable sluggish background software.")

        b_sfc = tk.Button(tools_grid, text="🛡️ System File Checker (SFC)", font=("Segoe UI", 10),
                  fg="#ffffff", bg="#242b3b", activebackground="#334155", relief="flat",
                  padx=6, pady=5, cursor="hand2", command=self.run_sfc_scan_ui)
        b_sfc.grid(row=1, column=0, sticky="ew", padx=(0, 4))
        add_tooltip(b_sfc, "Runs 'sfc /scannow' to detect and automatically repair corrupted Windows OS files.")

        b_dism = tk.Button(tools_grid, text="🔧 DISM Health Restore", font=("Segoe UI", 10),
                  fg="#ffffff", bg="#242b3b", activebackground="#334155", relief="flat",
                  padx=6, pady=5, cursor="hand2", command=self.run_dism_restore_ui)
        b_dism.grid(row=1, column=1, sticky="ew", padx=(0, 4))
        add_tooltip(b_dism, "Repairs damaged Windows component store health using official Microsoft Update files.")

        b_winsxs = tk.Button(tools_grid, text="📦 DISM WinSxS Cleanup", font=("Segoe UI", 10),
                  fg="#ffffff", bg="#242b3b", activebackground="#334155", relief="flat",
                  padx=6, pady=5, cursor="hand2", command=self.run_dism_component_cleanup_ui)
        b_winsxs.grid(row=1, column=2, sticky="ew")
        add_tooltip(b_winsxs, "Cleans superseded Windows Update backup packages from the WinSxS folder.")

        # RECURSIVELY BIND MOUSEWHEEL TO ALL CHILD WIDGETS IN PC MAINTENANCE
        def _bind_maint_wheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_maint_wheel, add="+")
            for c in widget.winfo_children():
                _bind_maint_wheel_recursive(c)

        self._bind_maint_wheel_recursive = _bind_maint_wheel_recursive
        _bind_maint_wheel_recursive(maint_content)

    def _quick_map_stats_check(self):
        def task():
            maps = custom_map_cleaner.scan_custom_maps(self.paths["steam_path"], self.paths["cs2_dir"])
            total_bytes = sum(m["size_bytes"] for m in maps)
            gb = total_bytes / (1024 ** 3)
            try:
                if not getattr(self, "_quitting", False) and hasattr(self, "map_stat_lbl") and self.map_stat_lbl.winfo_exists():
                    self.after(0, lambda: self.map_stat_lbl.config(text=f"{len(maps)} custom maps detected ({gb:.1f} GB storage)"))
            except Exception:
                pass
        threading.Thread(target=task, daemon=True).start()

    def run_workshop_vpk_verifier_ui(self):
        self.map_stat_lbl.config(text="Scanning & verifying Workshop VPK headers...", fg=ACCENT_AMBER)
        self.update_idletasks()
        res = core_logic.scan_workshop_vpk_addons(self.paths.get("steam_path"), self.paths.get("cs2_exe"))
        self._last_vpk_scan = res
        self.log(f"[VPK VERIFIER] {res.get('message')}")
        col = ACCENT_GREEN if res.get("corrupted_count", 0) == 0 else "#f59e0b"
        self.map_stat_lbl.config(text=res.get("message", "Scan complete."), fg=col)

        bad_list = [a for a in res.get("addons", []) if a.get("status") != "Healthy"]
        if bad_list:
            bad_lines = "\n".join(f"• [{a['workshop_id']}] {a['name']} — {a['status']} ({a['size_mb']} MB)" for a in bad_list[:10])
            messagebox.showwarning(
                "Workshop VPK Health Verifier",
                f"{res.get('message')}\n\n"
                f"Corrupted / Incomplete Addons Found:\n{bad_lines}\n\n"
                "Click '🔧 Repair Corrupted VPKs' to safely purge these broken folders so Steam re-downloads them cleanly."
            )
        else:
            messagebox.showinfo(
                "Workshop VPK Health Verifier",
                f"{res.get('message')}\n\nAll Workshop .vpk binary headers (0x55aa1234) are 100% healthy!"
            )

    def repair_workshop_vpks_ui(self):
        scan = getattr(self, "_last_vpk_scan", None)
        if not scan:
            scan = core_logic.scan_workshop_vpk_addons(self.paths.get("steam_path"), self.paths.get("cs2_exe"))
            self._last_vpk_scan = scan
        addons = scan.get("addons", [])
        bad = [a for a in addons if a.get("status") != "Healthy"]
        if not bad:
            messagebox.showinfo("Workshop VPK Repair", "All scanned Workshop VPK addons are already 100% healthy! Nothing to purge.")
            return
        if not messagebox.askyesno(
            "Confirm Corrupted VPK Repair",
            f"Found {len(bad)} corrupted or incomplete Workshop VPK addon folder(s).\n\n"
            "Purge these corrupted folders now so Steam can cleanly re-download them?"
        ):
            return
        rep = core_logic.repair_corrupted_workshop_addons(addons)
        self.log(f"[VPK REPAIR] {rep.get('message')}")
        self.map_stat_lbl.config(text=rep.get("message", "Repair complete."), fg=ACCENT_GREEN)
        self._quick_map_stats_check()
        messagebox.showinfo("Workshop VPK Repair Complete", rep.get("message"))

    def _refresh_drives_list(self, parent_frame):
        for widget in parent_frame.winfo_children():
            widget.destroy()

        drives = core_logic.get_drives_info()
        has_critical = False

        if len(drives) >= 4:
            for i, d in enumerate(drives):
                col = i % 2
                row_idx = i // 2
                d_cell = tk.Frame(parent_frame, bg=BG_CARD_ROW, padx=6, pady=2)
                d_cell.grid(row=row_idx, column=col, sticky="ew", padx=4, pady=1)

                status_tag = "⚠️ LOW (>85%)" if d["is_critical"] else "● OK"
                status_col = ACCENT_RED if d["is_critical"] else ACCENT_GREEN
                if d["is_critical"]:
                    has_critical = True

                tk.Label(d_cell, text=f"{d['drive']}", font=("Consolas", 10, "bold"), fg=FG_WHITE, bg=BG_CARD_ROW, width=3, anchor="w").pack(side="left")
                info_txt = f"{d['free_gb']:.1f} GB / {d['total_gb']:.1f} GB ({d['used_pct']:.0f}%)"
                tk.Label(d_cell, text=info_txt, font=("Segoe UI", 10), fg="#cbd5e1", bg=BG_CARD_ROW).pack(side="left", padx=4)
                tk.Label(d_cell, text=status_tag, font=("Segoe UI", 10, "bold"), fg=status_col, bg=BG_CARD_ROW).pack(side="right")

            parent_frame.columnconfigure(0, weight=1)
            parent_frame.columnconfigure(1, weight=1)
        else:
            for d in drives:
                d_row = tk.Frame(parent_frame, bg=BG_CARD_ROW)
                d_row.pack(fill="x", pady=1)

                status_tag = "⚠️ LOW SPACE (>85%)" if d["is_critical"] else "● HEALTHY"
                status_col = ACCENT_RED if d["is_critical"] else ACCENT_GREEN
                if d["is_critical"]:
                    has_critical = True

                tk.Label(d_row, text=f"{d['drive']}", font=("Consolas", 10, "bold"), fg=FG_WHITE, bg=BG_CARD_ROW, width=4, anchor="w").pack(side="left")
                info_txt = f"{d['free_gb']:.1f} GB Free of {d['total_gb']:.1f} GB ({d['used_pct']:.1f}% Used)"
                tk.Label(d_row, text=info_txt, font=("Segoe UI", 10), fg="#cbd5e1", bg=BG_CARD_ROW).pack(side="left", padx=6)
                tk.Label(d_row, text=status_tag, font=("Segoe UI", 10, "bold"), fg=status_col, bg=BG_CARD_ROW).pack(side="right")

        if has_critical:
            tip_lbl = tk.Label(parent_frame, text="⚠️ Notice: When drives exceed 85% full, SSD write cache performance degrades and causes in-game micro-stuttering.", font=("Segoe UI", 9, "italic"), fg=ACCENT_AMBER, bg=BG_CARD_ROW, justify="left")
            if len(drives) >= 4:
                tip_lbl.grid(row=(len(drives)+1)//2, column=0, columnspan=2, sticky="w", pady=(3, 0))
            else:
                tip_lbl.pack(anchor="w", pady=(4, 0))

        if hasattr(self, "_bind_maint_wheel_recursive"):
            self._bind_maint_wheel_recursive(parent_frame)

    def _build_page_os_diagnostics(self, page):
        canvas = tk.Canvas(page, bg=BG_CARD, highlightthickness=0, yscrollincrement=1)
        scrollbar = ttk.Scrollbar(page, orient="vertical", command=canvas.yview, style="Vertical.Dark.TScrollbar")
        self.os_diag_canvas = canvas
        self.os_diag_scrollbar = scrollbar
        diag_content = tk.Frame(canvas, bg=BG_CARD)

        self.os_diag_wrap_labels = []

        diag_content.bind(
            "<Configure>",
            lambda e: self._debounce_sync_scroll(canvas, scrollbar)
        )
        c_window = canvas.create_window((0, 0), window=diag_content, anchor="nw")

        self._diag_wrap_timer = None
        def _on_diag_canvas_configure(e):
            if getattr(canvas, "_last_diag_w", None) != e.width:
                canvas._last_diag_w = e.width
                canvas.itemconfig(c_window, width=e.width)

                def _apply_diag_wraps():
                    try:
                        avail = max(450, canvas.winfo_width() - 50)
                        for lbl, pad in getattr(self, "os_diag_wrap_labels", []):
                            if lbl.winfo_exists():
                                lbl.config(wraplength=max(350, avail - pad), anchor="w", justify="left")
                    except Exception:
                        pass

                if getattr(self, "_diag_wrap_timer", None):
                    try:
                        self.after_cancel(self._diag_wrap_timer)
                    except Exception:
                        pass
                self._diag_wrap_timer = self.after(35, _apply_diag_wraps)
            self._debounce_sync_scroll(canvas, scrollbar)

        canvas.bind("<Configure>", _on_diag_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def _on_diag_wheel(e):
            return self._handle_canvas_wheel(e, canvas)

        def _bind_diag_wheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_diag_wheel, add="+")
            for child in widget.winfo_children():
                _bind_diag_wheel_recursive(child)


        # Top Header Card
        head_card = tk.Frame(diag_content, bg=BG_CARD_ROW, padx=14, pady=10, highlightbackground=BG_BORDER, highlightthickness=1)
        head_card.pack(fill="x", pady=(0, 10))

        hc_top = tk.Frame(head_card, bg=BG_CARD_ROW)
        hc_top.pack(fill="x")
        tk.Label(hc_top, text="🖥️  GPU MULTI-PLANE OVERLAY (MPO) DIAGNOSTICS & TROUBLESHOOTER", font=("Segoe UI", -16, "bold"), fg=FG_WHITE, bg=BG_CARD_ROW, anchor="w").pack(side="left")

        b_ref_diag = tk.Button(hc_top, text="🔄 Refresh Live Status", font=("Segoe UI", 10, "bold"),
                               fg="#ffffff", bg="#222b3d", activebackground="#2f3b52", activeforeground="#ffffff",
                               relief="flat", padx=10, pady=6, cursor="hand2", command=self._refresh_os_diagnostics)
        b_ref_diag.pack(side="right")
        add_tooltip(b_ref_diag, "Re-queries Windows registry and display driver MPO status in real-time.")

        lbl_h_sub = tk.Label(head_card, text="Dedicated Multi-Plane Overlay (MPO) troubleshooter covering AMD Radeon, NVIDIA GeForce, and Intel graphics. Inspects your active GPU hardware, driver presentation planes, and Windows Registry settings to resolve Alt-Tab black screens, driver timeouts, and display stutter.",
                             font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_CARD_ROW, justify="left", anchor="w")
        lbl_h_sub.pack(anchor="w", pady=(4, 0), fill="x", expand=True)
        self.os_diag_wrap_labels.append((lbl_h_sub, 30))

        self.os_diag_cards_container = tk.Frame(diag_content, bg=BG_CARD)
        self.os_diag_cards_container.pack(fill="x", expand=True)

        self._bind_diag_wheel_recursive = _bind_diag_wheel_recursive
        self._refresh_os_diagnostics()
        _bind_diag_wheel_recursive(diag_content)

    def _refresh_os_diagnostics(self):
        """Live re-query and dynamic rendering of GPU Multi-Plane Overlay (MPO) diagnostics."""
        if not hasattr(self, "os_diag_cards_container") or not self.os_diag_cards_container.winfo_exists():
            return

        for child in self.os_diag_cards_container.winfo_children():
            child.destroy()

        # Preserve header labels while resetting card labels
        self.os_diag_wrap_labels = [(lbl, pad) for (lbl, pad) in getattr(self, "os_diag_wrap_labels", [])
                                    if lbl.winfo_exists() and lbl.winfo_toplevel() == self and lbl.master != self.os_diag_cards_container]

        # =========================================================================
        # PROMINENT ADVISORY CARD: WHY IS GPU MPO DIAGNOSTICS IN CS2 COMMAND CENTER?
        # =========================================================================
        why_card = tk.Frame(self.os_diag_cards_container, bg="#111827", padx=14, pady=12, highlightbackground="#f59e0b", highlightthickness=1)
        why_card.pack(fill="x", pady=(0, 10))

        # Header row: Title on left, Badge on right
        w_head = tk.Frame(why_card, bg="#111827")
        w_head.pack(fill="x", pady=(0, 8))
        tk.Label(w_head, text="❓  WHY IS GPU MPO DIAGNOSTICS IN CS2 COMMAND CENTER?", font=("Segoe UI", 10, "bold"), fg="#fbbf24", bg="#111827", anchor="w").pack(side="left")

        pill_info = tk.Frame(w_head, bg="#1f2937", padx=8, pady=2, highlightbackground="#f59e0b", highlightthickness=1)
        pill_info.pack(side="right")
        tk.Label(pill_info, text="AMD • NVIDIA • INTEL TROUBLESHOOTER", font=("Segoe UI", 10, "bold"), fg="#fbbf24", bg="#1f2937").pack()

        # Explanatory body text
        why_text = (
            "Multi-Plane Overlay (MPO) is a Windows WDDM hardware presentation feature that allows the GPU display engine to composite "
            "desktop windows (such as Discord, web browsers, or Spotify) and 3D games directly on separate hardware planes without routing "
            "through the Windows Desktop Window Manager (DWM) composition swapchain.\n\n"
            "WHY IT CAUSES SEVERE ISSUES IN CS2 & WINDOWS:\n"
            "• Alt-Tab Black Screen & Freezes: When switching focus between CS2 and desktop windows, MPO hardware plane handshakes frequently "
            "desynchronize. This causes 1 to 3-second black screens, temporary display freezing, or game crashes.\n"
            "• AMD Radeon Driver Timeouts: On AMD systems (RDNA 1/2/3/4), MPO is widely documented to trigger 'AMD Driver Timeout' crash "
            "dialogs (amdkmdag.sys) when running hardware-accelerated video or Discord on a secondary display while CS2 is in-match.\n"
            "• NVIDIA Driver Crashes & Checkerboard Glitches: On NVIDIA GeForce (RTX/GTX), MPO causes Chromium/Discord checkerboard artifacting, "
            "G-Sync stutter, and display flickering. This issue became so widespread that NVIDIA officially published Support Article #5152 "
            "providing their official 'mpo_disable.reg' registry fix.\n"
            "• Mixed-Refresh Rate Desync: If your primary CS2 monitor runs at 144Hz / 240Hz / 360Hz and your secondary monitor runs at 60Hz, "
            "MPO often caps or stutters the high-refresh monitor whenever background animations or video occur on the other display.\n\n"
            "⭐ ESSENTIAL FIRST STEP: CLEAN DRIVER REINSTALL VIA DDU (BEFORE TOUCHING MPO)\n"
            "Before modifying or disabling Multi-Plane Overlay in the registry, you should ALWAYS first perform a complete Display Driver Uninstaller (DDU) wipe in Windows Safe Mode followed by a fresh installation of the latest WHQL graphics driver.\n\n"
            "Many driver timeouts, Alt-Tab freezes, and black screens are caused by corrupted driver cache, shader cache mismatch, or dirty driver updates—NOT MPO itself. Test your system after the DDU reinstall first; if your issue is completely resolved, you do NOT need to touch or disable MPO!\n\n"
            "• Step 1: Download the latest WHQL graphics driver from AMD/NVIDIA and download DDU (wagnardsoft.com).\n"
            "• Step 2: Disconnect your internet connection (unplug Ethernet or disable Wi-Fi) to prevent Windows Update from auto-installing generic drivers.\n"
            "• Step 3: Boot into Windows Safe Mode, launch DDU, and choose 'Clean and restart'.\n"
            "• Step 4: After rebooting into normal Windows, install your freshly downloaded driver, restart, and reconnect internet.\n"
            "• Step 5: Check if CS2 runs smoothly. If your problem is solved, leave MPO enabled at Windows default!\n\n"
            "⚠️ WHY AVOID AMD CLEANUP UTILITY / MANUFACTURER UNINSTALLERS:\n"
            "Manufacturer tools such as AMD Cleanup Utility (AMDCleanupUtility.exe) aggressively purge ALL AMD drivers from the system, including critical AMD Chipset drivers, PCIe root drivers, and USB host controller drivers. This frequently causes USB mouse/keyboard input loss or Windows Safe Mode PIN sign-in failure loops. DDU is isolated specifically to graphics display drivers, making it vastly safer.\n\n"
            "WHEN SHOULD YOU DISABLE MPO?\n"
            "Only proceed with disabling MPO if you have ALREADY performed a clean DDU driver wipe and you STILL continue to experience Alt-Tab black screens, multi-monitor refresh rate desync, or Discord/browser checkerboard glitches.\n\n"
            "WHY THIS TAB IS IN CS2 COMMAND CENTER:\n"
            "Many CS2 players blame game updates, config files, or their hardware for these crashes and black screens. This dedicated "
            "troubleshooter provides 100% transparent live diagnostics for AMD, NVIDIA, and Intel GPUs, explains the exact symptoms, "
            "and provides verified DIY registry commands and safe 1-click clipboard helpers.\n\n"
            "🔒 100% READ-ONLY SAFETY: CS2 Command Center NEVER modifies your display driver or registry automatically. "
            "You have full visibility and control to decide whether disabling MPO is right for your PC setup."
        )

        lbl_why = tk.Label(why_card, text=why_text, font=("Segoe UI", 10), fg="#e2e8f0", bg="#111827", justify="left", anchor="w")
        lbl_why.pack(anchor="w", fill="x", expand=True)
        self.os_diag_wrap_labels.append((lbl_why, 40))

        # Helper to create standardized styled advisory cards with neutral, non-pushy format
        def _create_diag_card(icon: str, title: str, config_type: str, config_type_color: str,
                              status_badge: str, status_badge_color: str,
                              current_state_text: str, inspection_detail: str,
                              behavior_considerations_text: str, technical_details_text: str,
                              tradeoffs_text: str, summary_text: str, diy_text: str, copy_actions: list = None):
            card = tk.Frame(self.os_diag_cards_container, bg=BG_CARD_ROW, padx=14, pady=10, highlightbackground=BG_BORDER, highlightthickness=1)
            card.pack(fill="x", pady=(0, 10))

            # Header row: Icon + Title on left, Dual Status Pills on right
            chead = tk.Frame(card, bg=BG_CARD_ROW)
            chead.pack(fill="x", pady=(0, 6))

            tk.Label(chead, text=f"{icon}  {title}", font=("Segoe UI", 10, "bold"), fg=FG_WHITE, bg=BG_CARD_ROW, anchor="w").pack(side="left")

            badge_box = tk.Frame(chead, bg=BG_CARD_ROW)
            badge_box.pack(side="right")

            # Pill 1: Config Mode (Default vs Modified / Custom)
            pill_cfg = tk.Frame(badge_box, bg="#11141c", padx=8, pady=2, highlightbackground=config_type_color, highlightthickness=1)
            pill_cfg.pack(side="left", padx=(0, 6))
            tk.Label(pill_cfg, text=f"● {config_type}", font=("Segoe UI", 10, "bold"), fg=config_type_color, bg="#11141c").pack()

            # Pill 2: Hardware / System Status Badge
            pill_v = tk.Frame(badge_box, bg="#11141c", padx=8, pady=2, highlightbackground=status_badge_color, highlightthickness=1)
            pill_v.pack(side="left")
            tk.Label(pill_v, text=status_badge, font=("Segoe UI", 10, "bold"), fg=status_badge_color, bg="#11141c").pack()

            # --- STATUS & TECHNICAL INSPECTION CONTAINER ---
            status_box = tk.Frame(card, bg="#11141c", padx=12, pady=8, highlightbackground="#222b3d", highlightthickness=1)
            status_box.pack(fill="x", pady=(2, 6))

            # 1. Current PC Configuration & State
            tk.Label(status_box, text="CURRENT PC CONFIGURATION:", font=("Segoe UI", -12, "bold"), fg=config_type_color, bg="#11141c", anchor="w").pack(anchor="w", pady=(8, 2))
            lbl_st = tk.Label(status_box, text=current_state_text, font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#11141c", justify="left", anchor="w")
            lbl_st.pack(anchor="w", pady=(1, 4), fill="x", expand=True)
            self.os_diag_wrap_labels.append((lbl_st, 50))

            # 2. Live System / Registry Inspection
            tk.Label(status_box, text="LIVE SYSTEM / REGISTRY INSPECTION:", font=("Segoe UI", -12, "bold"), fg="#64748b", bg="#11141c", anchor="w").pack(anchor="w", pady=(8, 2))
            lbl_insp = tk.Label(status_box, text=inspection_detail, font=("Segoe UI", 10), fg="#94a3b8", bg="#11141c", justify="left", anchor="w")
            lbl_insp.pack(anchor="w", pady=(1, 0), fill="x", expand=True)
            self.os_diag_wrap_labels.append((lbl_insp, 50))

            # 3. System Behavior & Optional Considerations (Neutral, Informative Highlight Box)
            cons_box = tk.Frame(status_box, bg="#162032", padx=10, pady=6, highlightbackground="#2563eb", highlightthickness=1)
            cons_box.pack(fill="x", anchor="w", pady=(6, 2))
            tk.Label(cons_box, text="💡 SYSTEM BEHAVIOR & OPTIONAL CONSIDERATIONS:", font=("Segoe UI", -12, "bold"), fg="#38bdf8", bg="#162032", anchor="w").pack(anchor="w", pady=(4, 2))
            lbl_cons = tk.Label(cons_box, text=behavior_considerations_text, font=("Segoe UI", 10), fg="#f8fafc", bg="#162032", justify="left", anchor="w")
            lbl_cons.pack(anchor="w", pady=(1, 0), fill="x", expand=True)
            self.os_diag_wrap_labels.append((lbl_cons, 70))

            # 4. TECHNICAL DETAILS & IMPACT
            tk.Label(card, text="TECHNICAL DETAILS & IMPACT:", font=("Segoe UI", -12, "bold"), fg="#38bdf8", bg=BG_CARD_ROW, anchor="w").pack(anchor="w", pady=(8, 2))
            lbl_ben = tk.Label(card, text=technical_details_text, font=("Segoe UI", 10), fg="#cbd5e1", bg=BG_CARD_ROW, justify="left", anchor="w")
            lbl_ben.pack(anchor="w", pady=(0, 4), fill="x", expand=True)
            self.os_diag_wrap_labels.append((lbl_ben, 40))

            # 5. TRADE-OFFS & STABILITY CONSIDERATIONS
            tk.Label(card, text="TRADE-OFFS & STABILITY CONSIDERATIONS:", font=("Segoe UI", -12, "bold"), fg="#f59e0b", bg=BG_CARD_ROW, anchor="w").pack(anchor="w", pady=(8, 2))
            lbl_risk = tk.Label(card, text=tradeoffs_text, font=("Segoe UI", 10), fg="#cbd5e1", bg=BG_CARD_ROW, justify="left", anchor="w")
            lbl_risk.pack(anchor="w", pady=(0, 4), fill="x", expand=True)
            self.os_diag_wrap_labels.append((lbl_risk, 40))

            # 6. SUMMARY & OPTIONS (OPTIONAL)
            tk.Label(card, text="SUMMARY & OPTIONS (OPTIONAL):", font=("Segoe UI", -12, "bold"), fg="#34d399", bg=BG_CARD_ROW, anchor="w").pack(anchor="w", pady=(8, 2))
            lbl_sum = tk.Label(card, text=summary_text, font=("Segoe UI", 10), fg="#cbd5e1", bg=BG_CARD_ROW, justify="left", anchor="w")
            lbl_sum.pack(anchor="w", pady=(0, 4), fill="x", expand=True)
            self.os_diag_wrap_labels.append((lbl_sum, 40))

            # 7. HOW TO DO IT YOURSELF (MANUAL STEPS)
            tk.Label(card, text="HOW TO DO IT YOURSELF (MANUAL STEPS):", font=("Segoe UI", -12, "bold"), fg="#a78bfa", bg=BG_CARD_ROW, anchor="w").pack(anchor="w", pady=(8, 2))
            lbl_diy = tk.Label(card, text=diy_text, font=("Segoe UI", 10), fg="#cbd5e1", bg=BG_CARD_ROW, justify="left", anchor="w")
            lbl_diy.pack(anchor="w", pady=(0, 6), fill="x", expand=True)
            self.os_diag_wrap_labels.append((lbl_diy, 40))

            # Clipboard Helper Buttons (Safe - Read Only)
            if copy_actions:
                btn_row = tk.Frame(card, bg=BG_CARD_ROW)
                btn_row.pack(fill="x", anchor="w", pady=(2, 2))
                for btn_lbl, payload, desc in copy_actions:
                    b_cp = tk.Button(
                        btn_row, text=btn_lbl, font=("Segoe UI", 10), fg="#f1f5f9", bg="#222b3d",
                        activebackground="#2f3b52", activeforeground="#ffffff", relief="flat",
                        padx=10, pady=6, cursor="hand2",
                        command=lambda p=payload, d=desc: self.copy_to_clipboard(p, d)
                    )
                    b_cp.pack(side="left", padx=(0, 8))
                    add_tooltip(b_cp, f"Copies {desc} to Windows clipboard safely.")

            return card

        # =========================================================================
        # UNIVERSAL GPU MULTI-PLANE OVERLAY (MPO) DIAGNOSTIC CARD
        # =========================================================================
        mpo_diag = hardware_info.get_mpo_diagnostic(self.gpu_info["name"])
        is_mpo_disabled = mpo_diag.get("disabled", False)
        if is_mpo_disabled:
            mpo_cfg = "MODIFIED / CUSTOM"
            mpo_cfg_color = "#38bdf8"
            mpo_state = "MPO is DISABLED (Registry override active: DisableOverlays = 1)"
        else:
            mpo_cfg = "WINDOWS DEFAULT"
            mpo_cfg_color = "#94a3b8"
            mpo_state = "MPO is ENABLED (Standard Windows hardware multi-plane composition)"

        mpo_badge = mpo_diag.get("badge", "[STATUS: ENABLED]")
        mpo_badge_color = mpo_diag.get("badge_color", "#34d399")

        _create_diag_card(
            icon="🛡️",
            title="WINDOWS MULTI-PLANE OVERLAY (MPO) DIAGNOSTIC",
            config_type=mpo_cfg,
            config_type_color=mpo_cfg_color,
            status_badge=mpo_badge,
            status_badge_color=mpo_badge_color,
            current_state_text=mpo_state,
            inspection_detail=f"Registry Key: {mpo_diag['detail']}",
            behavior_considerations_text=(
                "Multi-Plane Overlay is enabled by default in Windows. Before modifying this setting, first perform a DDU + clean GPU driver reinstall to see if it fixes your issue:\n"
                "• Windows Default (Enabled): Standard behavior. Composites 2D windows and 3D games directly without running through the DWM swapchain.\n"
                "• Optional Modification (Disabled): Recommended ONLY IF clean DDU driver reinstall did not resolve your Alt-Tab black screens, Discord/browser checkerboard artifacts, AMD Driver Timeouts, or multi-monitor refresh rate desync."
            ),
            technical_details_text=(
                "Multi-Plane Overlay (MPO) is a Windows WDDM hardware presentation feature that allows the GPU display pipeline to composite 2D window elements (Discord, web browsers, video players) and 3D games on independent hardware planes without running through the Desktop Window Manager (DWM) composition swapchain.\n\n"
                "Multi-GPU Vendor Impact:\n"
                "• AMD Radeon: Frequently triggers 1-3 second black screen flickers when Alt-Tabbing, 'AMD Driver Timeout' (amdkmdag.sys) crash dialogs, or multi-monitor stutter when running different refresh rates (e.g. 240Hz/144Hz + 60Hz).\n"
                "• NVIDIA GeForce: Known to cause G-Sync multi-monitor stutter, intermittent black screen flickers, and Chromium / Discord checkerboard rendering artifacts (the reason NVIDIA officially released their 'mpo_disable.reg' patch).\n"
                "• Intel Arc / Iris: Causes DWM display flickering and judder during borderless-to-fullscreen transitions."
            ),
            tradeoffs_text=(
                "Disabling MPO causes Windows to route all windowed rendering through standard DWM desktop composition. This may slightly increase idle GPU memory clocks and power draw (+2W to 5W) on desktop when watching hardware-accelerated video. It does not introduce input latency into games."
            ),
            summary_text=(
                "• ⚠️ FIRST RECOMMENDATION: Always perform a clean GPU driver reinstall using DDU in Safe Mode first! Check if that resolves your stutter or black screen before modifying MPO.\n"
                "• If your PC runs smoothly with zero black flickers or driver timeouts: Keeping Windows Default (Enabled) is completely normal.\n"
                "• If you did DDU and still experience Alt-Tab black screens, Discord checkerboards, or multi-monitor refresh desync: Disabling MPO via the registry is an officially verified, safe workaround."
            ),
            diy_text=(
                "METHOD 1: Safe 1-Click Clipboard Command (Administrator Command Prompt / PowerShell)\n"
                "1. Click the '📋 Copy Disable MPO Command' button below.\n"
                "2. Press [Win + X] and select 'Terminal (Admin)' or 'Command Prompt (Admin)'.\n"
                "3. Paste the command and press Enter.\n"
                "4. Restart your PC for the graphics driver to reload.\n\n"
                "METHOD 2: Manual Windows Registry Editor (Regedit)\n"
                "1. Press [Win + R], type 'regedit', and press Enter.\n"
                r"2. Navigate to: HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" + "\n"
                "3. To Disable MPO: Right-click GraphicsDrivers -> New -> DWORD (32-bit) Value -> Name: DisableOverlays -> Value data: 1.\n"
                "4. To Re-Enable MPO (Default): Right-click DisableOverlays -> Delete (or set value to 0).\n"
                "5. Restart your PC."
            ),
            copy_actions=[
                ("📋 Copy Registry Path", r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "GraphicsDrivers Registry Path"),
                ("📋 Copy Disable MPO Command", r'reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "DisableOverlays" /t REG_DWORD /d 1 /f', "Disable MPO Registry Command"),
                ("📋 Copy Restore MPO Default Command", r'reg delete "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "DisableOverlays" /f', "Restore MPO Default Registry Command"),
                ("📋 Copy DDU Website Link", "https://www.wagnardsoft.com/", "Official DDU Website Link")
            ]
        )

        if hasattr(self, "_bind_diag_wheel_recursive"):
            self._bind_diag_wheel_recursive(self.os_diag_cards_container)
        self.after_idle(lambda: self._debounce_sync_scroll(self.os_diag_canvas, self.os_diag_scrollbar))

    def copy_to_clipboard(self, text: str, label: str):
        """Copies text to the Windows clipboard safely without executing any commands."""
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        self.log(f"[CLIPBOARD] Copied {label} to clipboard.")
        messagebox.showinfo(
            "Copied to Clipboard",
            f"Successfully copied {label} to clipboard:\n\n{text}\n\n"
            "This tab is strictly read-only for safety. You can now paste this into your tool (e.g. Registry Editor or Administrator Command Prompt) if you wish to apply it manually."
        )

    # --- ACTIONS & LOGS ---

    def log(self, text: str):
        try:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            if hasattr(self, "console") and self.console.winfo_exists():
                self.console.config(state="normal")
                self.console.insert("end", f"[{timestamp}] {text}\n")
                self.console.see("end")
                self.console.config(state="disabled")
        except Exception:
            pass

    def clear_logs(self):
        try:
            if hasattr(self, "console") and self.console.winfo_exists():
                self.console.config(state="normal")
                self.console.delete("1.0", "end")
                self.console.config(state="disabled")
        except Exception:
            pass

    def _initial_status_check(self):
        self.log("CS2 Command Center initialized.")
        perm = "Admin Privileges" if self.admin_status else "Standard Permissions (Elevation not required for safe CS2 tweaks)"
        self.log(f"Permissions: {perm}")
        self.log(f"Hardware: {self.cpu_info['name']} | GPU: {self.gpu_info['name']}")
        self.log("GPU MPO Diagnostics tab ready (AMD, NVIDIA & Intel support).")
        if self.paths["cs2_exe"]:
            self.log(f"CS2 Directory: {self.paths['cs2_exe']}")
        
        # Start server cache refresh in background and recurring auto-update loop (every 15s)
        threading.Thread(target=self.refresh_all_servers, daemon=True).start()
        self._start_server_auto_refresh_loop()
        self._start_live_map_timer_loop()

    # --- DISCORD PRESENCE TAB & REAL-TIME CONTROLS ---

    def _build_page_discord(self, page):
        canvas = tk.Canvas(page, bg=BG_CARD, highlightthickness=0, yscrollincrement=1)
        scrollbar = ttk.Scrollbar(page, orient="vertical", command=canvas.yview, style="Vertical.Dark.TScrollbar")
        self.discord_canvas = canvas
        self.discord_scrollbar = scrollbar
        discord_content = tk.Frame(canvas, bg=BG_CARD)

        discord_content.bind("<Configure>", lambda e: self._debounce_sync_scroll(canvas, scrollbar))
        c_window = canvas.create_window((0, 0), window=discord_content, anchor="nw")
        self._bind_canvas_auto_width(canvas, c_window, scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def _on_discord_wheel(e):
            return self._handle_canvas_wheel(e, canvas)

        def _bind_discord_wheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_discord_wheel)
            for child in widget.winfo_children():
                _bind_discord_wheel_recursive(child)


        # Header Title
        tk.Label(discord_content, text="COUNTER-STRIKE 2 CUSTOM DISCORD PRESENCE (RPC)", font=("Segoe UI", -16, "bold"), fg=FG_WHITE, bg=BG_CARD).pack(anchor="w")
        tk.Label(discord_content, text="Custom game activity status strictly designed and active ONLY for Counter-Strike 2. Clears automatically when CS2 closes and never touches or affects any other game.", font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_CARD).pack(anchor="w", pady=(1, 4))

        # Safe Badge Banner
        safe_frame = tk.Frame(discord_content, bg="#0d1f18", padx=10, pady=4, highlightbackground="#10b981", highlightthickness=1)
        safe_frame.pack(fill="x", pady=(0, 8))
        tk.Label(safe_frame, text="● 100% VAC-Safe: Connects via local Windows Named Pipe IPC (\\\\.\\pipe\\discord-ipc-0). Zero interaction with cs2.exe memory or binaries.",
                 font=("Segoe UI", 10, "bold"), fg="#34d399", bg="#0d1f18").pack(anchor="w")

        # Top 2-Column Row (Controls on Left, Live Preview on Right)
        top_grid = tk.Frame(discord_content, bg=BG_CARD)
        top_grid.pack(fill="x", pady=(0, 8))

        # Column Left: Controls
        col_left = tk.Frame(top_grid, bg=BG_CARD_ROW, padx=12, pady=10, highlightbackground=BG_BORDER, highlightthickness=1)
        col_left.pack(side="left", fill="both", expand=True, padx=(0, 4))

        tk.Label(col_left, text="PRESENCE CONTROLS & AUTO-DETECTION", font=("Segoe UI", 10, "bold"), fg=FG_WHITE, bg=BG_CARD_ROW).pack(anchor="w")

        auto_badge = tk.Frame(col_left, bg="#0e2338", padx=8, pady=4, highlightbackground="#38bdf8", highlightthickness=1)
        auto_badge.pack(fill="x", pady=(4, 6))
        tk.Label(auto_badge, text="⚡ 100% AUTOMATIC DETECTION ACTIVE", font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#0e2338").pack(anchor="w")
        tk.Label(auto_badge,
                 text="• CS2 Closed: Discord shows NOTHING (100% clean).\n• CS2 Running: Automatically turns ON & tracks status.\n• In Server: Auto-detects map & players via Valve GSI.\n• Zero manual buttons or setup needed!",
                 font=("Segoe UI", 9), fg="#cbd5e1", bg="#0e2338", justify="left").pack(anchor="w", pady=(2, 0))

        self.var_discord_enabled = tk.BooleanVar(value=self.config.get("discord_rpc_enabled", True))
        cb_disc = tk.Checkbutton(col_left, text=" Enable Discord Rich Presence (RPC)", variable=self.var_discord_enabled,
                                 command=self._on_discord_toggle,
                                 font=("Segoe UI", -14, "bold"), fg=FG_WHITE, bg=BG_CARD_ROW, activebackground=BG_CARD_ROW, selectcolor=BG_WINDOW)
        cb_disc.pack(anchor="w", pady=(2, 4))
        add_tooltip(cb_disc, "Enable or disable automatic CS2 Discord Rich Presence broadcasting.")

        app_info = tk.Frame(col_left, bg="#13241b", padx=8, pady=6, highlightbackground="#22c55e", highlightthickness=1)
        app_info.pack(fill="x", pady=(0, 6))
        tk.Label(app_info, text="🛡️ PRE-CONFIGURED GAME IDENTITY", font=("Segoe UI", 10, "bold"), fg="#22c55e", bg="#13241b").pack(anchor="w")
        tk.Label(app_info,
                 text="Pre-configured with universal Counter-Strike 2 Application ID.\nAll features work out-of-the-box for all users with zero extra setup.",
                 font=("Segoe UI", 9), fg="#86efac", bg="#13241b", justify="left").pack(anchor="w", pady=(2, 0))

        self.discord_status_lbl = tk.Label(col_left, text="○ Status: Checking CS2...", font=("Segoe UI", 10, "bold"), fg=FG_MUTED, bg=BG_CARD_ROW)
        self.discord_status_lbl.pack(anchor="w", pady=(0, 6))

        btn_box = tk.Frame(col_left, bg=BG_CARD_ROW)
        btn_box.pack(anchor="w", pady=(2, 0))

        b_disc_ref = tk.Button(btn_box, text="🔄 Refresh Now", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#2563eb",
                  activebackground="#1d4ed8", relief="flat", padx=10, pady=4, cursor="hand2",
                  command=self._refresh_discord_presence)
        b_disc_ref.pack(side="left", padx=(0, 4))
        add_tooltip(b_disc_ref, "Forces an immediate Discord RPC activity refresh with current game data.")

        b_disc_off = tk.Button(btn_box, text="🧹 Turn Off Presence", font=("Segoe UI", 10), fg="#f87171", bg="#1f1820",
                  activebackground="#2e1b23", relief="flat", padx=8, pady=4, cursor="hand2",
                  command=self.clear_discord_presence)
        b_disc_off.pack(side="left", padx=4)
        add_tooltip(b_disc_off, "Disconnects Discord IPC pipe and clears game activity from your profile.")

        click_box = tk.Frame(col_left, bg=BG_CARD_ROW)
        click_box.pack(fill="x", pady=(8, 0))
        tk.Label(click_box, text="ℹ️ Why does clicking the card open CS2 Game Overview?", font=("Segoe UI", -14, "bold"), fg="#94a3b8", bg=BG_CARD_ROW).pack(anchor="w")
        tk.Label(click_box,
                 text="In Discord's desktop app, clicking any game activity card natively navigates to Discord's official CS2 Overview hub. Discord does not allow custom URLs on text lines.",
                 font=("Segoe UI", 9), fg="#64748b", bg=BG_CARD_ROW, justify="left", wraplength=280, anchor="w").pack(anchor="w", fill="x")

        # Column Right: Live Discord Profile Preview
        col_right = tk.Frame(top_grid, bg="#1e1f22", padx=12, pady=10, highlightbackground="#2b2d31", highlightthickness=1)
        col_right.pack(side="left", fill="both", expand=True, padx=(4, 0))

        tk.Label(col_right, text="SIMULATED DISCORD PROFILE CARD", font=("Segoe UI", 10, "bold"), fg="#f2f3f5", bg="#1e1f22").pack(anchor="w")
        tk.Label(col_right, text="Live preview of what other Discord users and server members see:", font=("Segoe UI", 9), fg="#949ba4", bg="#1e1f22").pack(anchor="w", pady=(1, 6))

        # Discord User Row
        u_box = tk.Frame(col_right, bg="#232428", padx=8, pady=6, highlightbackground="#313338", highlightthickness=1)
        u_box.pack(fill="x", pady=(0, 6))

        # Avatar pill
        self.preview_ava = tk.Frame(u_box, bg="#313338", width=32, height=32, highlightbackground="#4e5058", highlightthickness=2)
        self.preview_ava.pack_propagate(False)
        self.preview_ava.pack(side="left", padx=(0, 8))
        tk.Label(self.preview_ava, text="CS2", font=("Segoe UI", 10, "bold"), fg="#de6c11", bg="#313338").pack(expand=True)

        u_info = tk.Frame(u_box, bg="#232428")
        u_info.pack(side="left", fill="both", expand=True)
        p_name = core_logic.get_steam_active_persona() or "Player Profile"
        self.preview_username_lbl = tk.Label(u_info, text=p_name, font=("Segoe UI", 10, "bold"), fg="#f2f3f5", bg="#232428")
        self.preview_username_lbl.pack(anchor="w")
        self.preview_status_lbl = tk.Label(u_info, text="○ Standby  |  CS2 Closed (No Presence)", font=("Segoe UI", 9), fg="#949ba4", bg="#232428")
        self.preview_status_lbl.pack(anchor="w")

        # Discord Activity Block
        self.preview_act_box = tk.Frame(col_right, bg="#111214", padx=10, pady=8, highlightbackground="#1e1f22", highlightthickness=1)
        self.preview_act_box.pack(fill="x")

        # Container A: DORMANT STATE (When CS2 is closed - accurate simulation!)
        self.preview_dormant = tk.Frame(self.preview_act_box, bg="#111214")
        self.preview_dormant.pack(fill="x")
        tk.Label(self.preview_dormant, text="💤 NO ACTIVE CS2 PRESENCE BROADCASTED", font=("Segoe UI", 14, "bold"), fg="#949ba4", bg="#111214").pack(anchor="w")
        tk.Label(self.preview_dormant,
                 text="CS2 is closed. Rich Presence is completely dormant (Discord displays NO game on your profile).\nWhen CS2 is launched, your live game card automatically lights up here in real time.",
                 font=("Segoe UI", 9), fg="#64748b", bg="#111214", justify="left", anchor="w").pack(anchor="w", fill="x", pady=(3, 0))

        # Container B: ACTIVE STATE (When CS2 is running)
        self.preview_active = tk.Frame(self.preview_act_box, bg="#111214")
        # Hidden by default until CS2 runs or presence is connected

        tk.Label(self.preview_active, text="PLAYING A GAME", font=("Segoe UI", 14, "bold"), fg="#949ba4", bg="#111214").pack(anchor="w")

        act_inner = tk.Frame(self.preview_active, bg="#111214")
        act_inner.pack(fill="x", pady=(4, 0))

        # Icon box
        g_icon = tk.Frame(act_inner, bg="#de6c11", width=38, height=38, highlightbackground="#f97316", highlightthickness=1)
        g_icon.pack_propagate(False)
        g_icon.pack(side="left", padx=(0, 8))
        tk.Label(g_icon, text="CS2", font=("Segoe UI", 14, "bold"), fg="#ffffff", bg="#de6c11").pack(expand=True)

        act_text = tk.Frame(act_inner, bg="#111214")
        act_text.pack(side="left", fill="both", expand=True)

        tk.Label(act_text, text="Counter-Strike 2", font=("Segoe UI", 14, "bold"), fg="#f2f3f5", bg="#111214").pack(anchor="w")
        self.lbl_prev_details = tk.Label(act_text, textvariable=self.discord_preview_details, font=("Segoe UI", 10), fg="#dbdee1", bg="#111214")
        self.lbl_prev_details.pack(anchor="w")
        self.lbl_prev_state = tk.Label(act_text, textvariable=self.discord_preview_state, font=("Segoe UI", 10), fg="#949ba4", bg="#111214")
        self.lbl_prev_state.pack(anchor="w")
        self.lbl_prev_elapsed = tk.Label(act_text, textvariable=self.discord_preview_elapsed, font=("Segoe UI", 9), fg="#949ba4", bg="#111214")
        self.lbl_prev_elapsed.pack(anchor="w")

        # Discord Profile Action Buttons Preview
        self.prev_btn_box = tk.Frame(self.preview_active, bg="#111214")
        self.prev_btn_box.pack(fill="x", pady=(8, 2))

        self.preview_b1_frame = tk.Frame(self.prev_btn_box, bg="#2b2d31", padx=8, pady=4, highlightbackground="#35373c", highlightthickness=1)
        self.preview_b1_frame.pack(fill="x", pady=(0, 3))
        self.lbl_btn1 = tk.Label(self.preview_b1_frame, textvariable=self.discord_preview_btn1, font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#2b2d31")
        self.lbl_btn1.pack(anchor="center")

        self.preview_b2_frame = tk.Frame(self.prev_btn_box, bg="#2b2d31", padx=8, pady=4, highlightbackground="#35373c", highlightthickness=1)
        self.preview_b2_frame.pack(fill="x")
        self.lbl_btn2 = tk.Label(self.preview_b2_frame, textvariable=self.discord_preview_btn2, font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#2b2d31")
        self.lbl_btn2.pack(anchor="center")

        _bind_discord_wheel_recursive(discord_content)
        self._update_discord_preview_labels(self.discord_preview_details.get(), self.discord_preview_state.get())

    def _build_page_faq(self, page):
        canvas = tk.Canvas(page, bg=BG_CARD, highlightthickness=0, yscrollincrement=1)
        scrollbar = ttk.Scrollbar(page, orient="vertical", command=canvas.yview, style="Vertical.Dark.TScrollbar")
        self.faq_canvas = canvas
        self.faq_scrollbar = scrollbar
        faq_content = tk.Frame(canvas, bg=BG_CARD)

        self.faq_wrap_labels = []

        faq_content.bind(
            "<Configure>",
            lambda e: self._debounce_sync_scroll(canvas, scrollbar)
        )
        c_window = canvas.create_window((0, 0), window=faq_content, anchor="nw")

        self._faq_wrap_timer = None
        def _on_faq_canvas_configure(e):
            if getattr(canvas, "_last_faq_w", None) != e.width:
                canvas._last_faq_w = e.width
                canvas.itemconfig(c_window, width=e.width)

                def _apply_faq_wraps():
                    try:
                        avail = max(450, canvas.winfo_width() - 50)
                        for lbl, pad in getattr(self, "faq_wrap_labels", []):
                            if lbl.winfo_exists():
                                lbl.config(wraplength=max(350, avail - pad), anchor="w", justify="left")
                    except Exception:
                        pass

                if getattr(self, "_faq_wrap_timer", None):
                    try:
                        self.after_cancel(self._faq_wrap_timer)
                    except Exception:
                        pass
                self._faq_wrap_timer = self.after(35, _apply_faq_wraps)
            self._debounce_sync_scroll(canvas, scrollbar)

        canvas.bind("<Configure>", _on_faq_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def _on_faq_wheel(e):
            return self._handle_canvas_wheel(e, canvas)

        def _bind_faq_wheel_recursive(widget):
            widget.bind("<MouseWheel>", _on_faq_wheel, add="+")
            for child in widget.winfo_children():
                _bind_faq_wheel_recursive(child)


        # Top Header Card
        head_card = tk.Frame(faq_content, bg=BG_CARD_ROW, padx=14, pady=10, highlightbackground=BG_BORDER, highlightthickness=1)
        head_card.pack(fill="x", pady=(0, 10))
        tk.Label(head_card, text="📖  CS2 COMMAND CENTER — HELP & DETAILED KNOWLEDGE BASE", font=("Segoe UI", -16, "bold"), fg=FG_WHITE, bg=BG_CARD_ROW).pack(anchor="w")
        tk.Label(head_card, text="Comprehensive technical documentation, anti-cheat safety verification, competitive engine mechanics, network troubleshooting & feature guides.",
                 font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_CARD_ROW).pack(anchor="w", pady=(2, 0))

        # Helper to create FAQ section cards
        def _create_faq_card(icon: str, title: str, tag: str, tag_col: str, qa_list: list):
            card = tk.Frame(faq_content, bg=BG_CARD_ROW, padx=14, pady=10, highlightbackground=BG_BORDER, highlightthickness=1)
            card.pack(fill="x", pady=(0, 10))

            chead = tk.Frame(card, bg=BG_CARD_ROW)
            chead.pack(fill="x", pady=(0, 8))

            tk.Label(chead, text=icon, font=("Segoe UI Emoji", 10), fg=FG_WHITE, bg=BG_CARD_ROW).pack(side="left", padx=(0, 6))
            tk.Label(chead, text=title, font=("Segoe UI", 10, "bold"), fg=FG_WHITE, bg=BG_CARD_ROW).pack(side="left")
            tag_pill = tk.Frame(chead, bg="#11141c", padx=8, pady=2, highlightbackground=tag_col, highlightthickness=1)
            tag_pill.pack(side="right")
            tk.Label(tag_pill, text=tag, font=("Segoe UI", 10, "bold"), fg=tag_col, bg="#11141c").pack()

            # Elegant horizontal divider rule between header and questions
            tk.Frame(card, bg="#1e2533", height=1).pack(fill="x", pady=(2, 10))

            for q, a in qa_list:
                item_f = tk.Frame(card, bg=BG_CARD_ROW)
                item_f.pack(fill="x", pady=(5, 7))

                # Question row - Strictly flush left alignment
                q_row = tk.Frame(item_f, bg=BG_CARD_ROW)
                q_row.pack(fill="x", anchor="w")
                tk.Label(q_row, text="Q:", font=("Segoe UI", 10, "bold"), fg=ACCENT_ORANGE, bg=BG_CARD_ROW, anchor="nw").pack(side="left", anchor="nw")
                lbl_q = tk.Label(q_row, text=f" {q}", font=("Segoe UI", 10, "bold"), fg="#f1f5f9", bg=BG_CARD_ROW, wraplength=670, justify="left", anchor="w")
                lbl_q.pack(side="left", anchor="w", fill="x", expand=True)

                # Answer row - Strictly flush left alignment
                a_row = tk.Frame(item_f, bg=BG_CARD_ROW)
                a_row.pack(fill="x", padx=(18, 0), pady=(3, 0), anchor="w")
                lbl_a = tk.Label(a_row, text=a, font=("Segoe UI", 10), fg="#cbd5e1", bg=BG_CARD_ROW, wraplength=650, justify="left", anchor="w")
                lbl_a.pack(side="left", anchor="w", fill="x", expand=True)

                self.faq_wrap_labels.append((lbl_q, 45))
                self.faq_wrap_labels.append((lbl_a, 60))

            return card

        # Category 1: Safety & Anti-Cheat
        _create_faq_card(
            "🛡️", "SAFETY & ANTI-CHEAT (VAC) INTEGRITY", "100% VAC-SAFE", ACCENT_GREEN,
            [
                ("Is this tool safe to use? Can it get me banned by Valve Anti-Cheat (VAC)?",
                 "The Command Center is 100% VAC-Safe. It performs zero DLL injection, zero game memory modification, zero debugger hooks, and zero patched binaries. Everything it adjusts uses official Windows registry keys, official Valve console/autoexec scripts, and Steam's official Game State Integration (GSI) HTTP API. It is completely compliant with Valve's terms of service and safe for Premier, Faceit, and community servers."),
                ("Can I undo all changes made by the application?",
                 "Yes! Clicking the [⏪ Restore Defaults] button on the top right instantly restores Windows Game DVR, restores your default Windows power plan, reenables fullscreen optimizations, and resets the autoexec configuration back to clean stock defaults."),
                ("Does this app communicate with external servers or collect telemetry?",
                 "No. The Command Center is completely privacy-respecting and contains zero third-party telemetry, ads, or tracking. The only network calls are lightweight UDP A2S queries sent directly to game servers to retrieve live player counts, and local named pipes for Discord RPC.")
            ]
        )

        # Category 2: Engine Tweaks & 1-Click Optimizer
        _create_faq_card(
            "⚙️", "ENGINE TWEAKS & 1-CLICK OPTIMIZER", "FPS & LATENCY", ACCENT_CYAN,
            [
                ("What does disabling Windows Game DVR do?",
                 "Windows Game DVR continuously runs background video capture hooks inside the Windows Desktop Window Manager (DWM). Disabling it frees up GPU/CPU encoding pipelines, directly eliminating micro-stutters and sudden FPS drops during heavy combat and smoke grenades."),
                ("What does 'Disable Fullscreen Optimizations' (Direct-Flip) do?",
                 "Windows 10/11 forces games into a hybrid borderless presentation mode that routes frames through the Windows compositor. Disabling fullscreen optimizations on cs2.exe grants the game exclusive hardware display access (Direct-Flip mode), eliminating DWM compositor latency and reducing click-to-photon mouse input lag."),
                ("Why does the app select AMD Balanced for Ryzen 3D V-Cache (X3D) processors?",
                 "If you have an AMD Ryzen 5700X3D, 5800X3D, 7800X3D, or 9800X3D, setting power to generic Ultimate Performance can interfere with AMD's Collaborative Processor Performance Control (CPPC). AMD Balanced allows CPPC to correctly schedule CS2 threads onto the ultra-fast 3D V-Cache cores, giving you maximum 1% low FPS."),
                ("What happens on standard non-X3D CPUs and Intel hybrid processors?",
                 "For standard AMD processors (e.g., Ryzen 5600X, 7600), the app applies High Performance to ensure clocks never downthrottle. For Intel 12th/13th/14th Gen hybrid CPUs with P-cores and E-cores, High Performance combined with High Process Priority ensures the Windows kernel schedules CS2's render loop exclusively on physical Performance cores."),
                ("Why should I purge DirectX & Vulkan shader caches?",
                 "After GPU driver updates (NVIDIA/AMD) or CS2 game patches, old compiled shader caches can become corrupted or misaligned, leading to severe stutter when rendering smokes, fire, and particle effects. Purging the cache allows the driver to recompile fresh, optimized shaders on clean launch.")
            ]
        )

        # Category 3: Network Optimization, DNS Pros & Cons, and Packet Loss Mitigation
        _create_faq_card(
            "🌐", "NETWORK OPTIMIZATION, GAMING DNS PROS & CONS & PACKET LOSS", "NETWORK & DNS", ACCENT_CYAN,
            [
                ("What are all the purposes of the Gaming DNS Optimizer, and is it 100% safe?",
                 "DNS (Domain Name System) translates domain names into IP addresses. Besides speeding up domain lookups for Steam SDR relays, Workshop FastDL map servers, Discord voice channels, and web browsing, custom DNS resolvers serve multiple purposes:\n"
                 "• Reliability: Bypasses congested or malfunctioning default ISP DNS servers.\n"
                 "• Security (Quad9 9.9.9.9): Automatically blocks known malware, phishing, and spyware domains before they can load.\n"
                 "• Ad & Telemetry Filtering (AdGuard 94.140.14.14): Blocks background ad-trackers and Windows/app telemetry domains that cause random bandwidth spikes.\n"
                 "• Privacy (Cloudflare 1.1.1.1): Prevents your ISP from logging or hijacking your DNS queries.\n"
                 "• 100% Safety Guarantee: Uses official Microsoft Windows 'netsh' commands with zero kernel drivers or system modifications, and includes a 1-click 'Restore ISP Default (DHCP)' button."),
                ("What are the honest Pros and Cons (Limitations) of changing DNS?",
                 "✅ PROS:\n"
                 "• Faster initial connections to Steam relays, FastDL custom map mirrors, Discord, and websites.\n"
                 "• Lower lookup jitter and protection against ISP DNS outages.\n"
                 "• Optional built-in malware protection (Quad9) or telemetry/ad blocking (AdGuard).\n\n"
                 "⚠️ CONS / LIMITATIONS:\n"
                 "• Does NOT reduce raw in-game UDP ping once already connected to a server IP (because active game traffic sends UDP packets directly to the server IP without querying DNS).\n"
                 "• Choosing a physically distant DNS server without benchmarking first can cause CDNs (like Steam downloads) to route you to a farther download mirror — always click '⚡ Benchmark All DNS Servers' first!\n"
                 "• Hotel, school, or airport Wi-Fi login portals sometimes require default DHCP DNS to display their sign-in page (if needed, click '↺ Restore ISP Default (DHCP)')."),
                ("Can standalone PC software eliminate ISP packet loss without multi-path VPN routing tunnels?",
                 "While standalone local software cannot physically reroute undersea ISP fiber cables, CS2 Command Center applies all safe, official Windows and CS2 network optimizations: 1) Benchmarks and configures low-jitter DNS resolvers and flushes stale DNS cache; 2) Disables Windows Network Throttling Index (MMCSS) so Windows never throttles non-multimedia game UDP packets; 3) Configures optimal sub-tick packet rates in autoexec (rate 1000000); 4) Guides you on using CS2's built-in packet buffering to smooth out ISP jitter."),
                ("What does CS2's 'Buffering to smooth over packet loss' (cl_net_buffer_ticks) do?",
                 "Under Settings -> Game -> Telemetry: Setting 'Buffering to smooth packet loss' to 'None' (cl_net_buffer_ticks 0) provides the absolute lowest latency on flawless fiber connections. If your ISP suffers from packet loss or jitter, set it to '1 Packet' (cl_net_buffer_ticks 1) or '2 Packets' (cl_net_buffer_ticks 2). This creates a 15-30ms jitter buffer that reassembles missing packets before rendering, completely preventing rubberbanding and micro-teleports during heavy gunfights."),
                ("Why do Zombie Escape & 64-player servers experience choke or stutter?",
                 "In 64-player community servers, the server broadcasts massive amounts of entity updates, particle data, and zombie positions every tick. Setting 'rate 1000000' (maximum 8 Mbps bandwidth allocation) prevents your client from dropping entity packets when 60 players shoot and throw grenades simultaneously.")
            ]
        )

        # Category 4: Autoexec & Competitive Binds
        _create_faq_card(
            "📝", "AUTOEXEC & COMPETITIVE BINDS", "CONFIG & BINDS", ACCENT_ORANGE,
            [
                ("What competitive settings are installed into autoexec.cfg?",
                 "It configures optimal sub-tick network rates (rate 1000000, cl_interp 0.015625) for responsive hit registration, enables competitive audio clarity (crisp footstep frequencies), binds Jumpthrow (synchronized +jump and -attack), quick drop C4, and binds movement keys to instantly clear ragdolls and bullet impacts to remove visual clutter."),
                ("Why is snd_mixahead set to 0.025 instead of the default 0.05?",
                 "The default Source 2 audio buffer (0.05) creates 50ms of audio latency between gunshots/footsteps and your speakers. Setting snd_mixahead to 0.025 cuts audio processing latency in half (25ms), allowing you to hear enemy footsteps, zombie screams, and grenade bounces a full frame earlier."),
                ("Will applying autoexec overwrite my custom bindings or crosshair?",
                 "No! If an existing autoexec.cfg is present, the app backs it up and non-destructively appends or updates only the competitive performance blocks, keeping your personal binds, crosshair, sensitivity, and custom aliases 100% intact.")
            ]
        )

        # Category 5: Launch Options & Process Priority
        _create_faq_card(
            "🚀", "LAUNCH OPTIONS & MODERN SUB-TICK ARCHITECTURE", "LAUNCH FLAGS", ACCENT_GREEN,
            [
                ("Which launch options are recommended and why?",
                 "Recommended flags: -novid (skips intro video for faster game startup), -high (launches with High CPU priority), -threads <N> (matches engine worker threads to physical CPU cores), -nojoy (disables joystick polling overhead to save CPU cycles), and +fps_max 0 (uncaps framerate for minimum input delay)."),
                ("Why shouldn't obsolete CS:GO launch options (-tickrate 128, -d3d9ex, +mat_queue_mode) be used in CS2?",
                 "Counter-Strike 2 runs on Valve's modern Source 2 engine with a sub-tick network model and DirectX 11 / Vulkan graphics. Legacy Source 1 options like -tickrate 128, -d3d9ex, and +mat_queue_mode no longer exist in the engine; using them can generate engine console warnings and cause unstable thread scheduling."),
                ("What does the Live Booster & Gaming DNS Optimizer do?",
                 "The Live Booster safely elevates cs2.exe CPU thread priority to High (Win32 HIGH_PRIORITY_CLASS) without using risky 'RAM Cleaners' that cause browser/Discord crashes and page-fault stutters. The Gaming DNS Optimizer benchmarks 6 global gaming DNS providers (Cloudflare, Google, Quad9, OpenDNS, Level3, AdGuard) in parallel for real latency and jitter, letting you apply the fastest DNS or restore ISP defaults in 1 click."),
                ("Are the Optimizer and PC Maintenance meant to increase my max FPS?",
                 "They are NOT meant to artificially inflate maximum FPS beyond your physical CPU/GPU limits. Instead, they are engineered for System Stability, Frame-Time Consistency (1% Lows), Micro-Stutter Prevention during 64-player Zombie Escape & heavy utility, Display/Alt-Tab Reliability (MPO), Sub-Tick & DNS Network Responsiveness, and SSD/OS Health.")
            ]
        )

        # Category 6: ZE Server Browser & Fast Slot Sniper
        _create_faq_card(
            "🎯", "ZE SERVERS & FAST SLOT SNIPER", "SLOT SNIPER", ACCENT_AMBER,
            [
                ("How does the Slot Sniper function and how does it detect open slots?",
                 "The Slot Sniper runs a high-speed 0.25s background polling loop that queries the server directly via standard Steam A2S_INFO UDP protocol. It checks live player counts against your selected slot threshold (e.g., ≤ 62 for public players). The instant a player leaves or disconnects, the sniper detects the open slot within milliseconds, executes the in-game console connect immediately, and starts a 10-second cooldown!"),
                ("Why doesn't the Slot Sniper continuously spam 'connect' in the CS2 console while waiting?",
                 "While it is technically possible to spam 'connect' in the CS2 console every second, doing so causes Counter-Strike 2's networking subsystem (Steam Datagram Relay) and Source 2's unmanaged heap allocator to hold undrained connection sessions and console string buffers. This causes CS2's RAM usage to stack up, climbing higher and higher (4GB -> 6GB -> 8GB+), which is neither safe nor appropriate for PC stability. Instead, the Slot Sniper uses True Silent Sniping: it watches the server silently via external UDP A2S queries at 0.25s (taking 0 CS2 RAM and 0 clipboard usage), and the exact millisecond a player disconnects, it executes the in-game console connect immediately with a 10-second cooldown."),
                ("What happens if someone connects faster than me?",
                 "On popular 64/64 servers like GFL, multiple players may be attempting to join simultaneously. If another player connects a split-second faster, CS2 displays the standard server full notification. The Command Center recognizes that you have not entered the server yet; you can re-arm the sniper with a single click or leave it armed to immediately catch the very next open slot!"),
                ("How does the Command Center know when I am already in the server?",
                 "The app combines two automatic systems: Valve Game State Integration (GSI) via local HTTP events, and live A2S player roster matching using your active Steam persona. When your player connects to the server, the app automatically transitions to tracking mode and disarms the sniper so it never spams or fires duplicate connections."),
                ("What are the Slot Sniper Priority Tiers (VIP / Mapper / Normal)?",
                 "On 64-player community servers like GFL ZE, the server holds 64 players, but 2 slots (63 and 64) are reserved for VIPs, Mappers, and Supporters. If you are a standard player, select '≤ 62' so the sniper only attempts to join when a public slot opens, avoiding the 'Server is reserved for VIPs' kick. If you have VIP or Supporter status, select '≤ 64'."),
                ("What is the 'Launch Delay' setting for?",
                 "When CS2 is closed and you click 'Connect to GFL', the Command Center launches the game via Steam and waits for the configured Launch Delay (default: 15 seconds) so CS2 can load its main menu and establish Steam network credentials before executing the direct server connection.")
            ]
        )

        # Category 7: Discord Rich Presence
        _create_faq_card(
            "🎮", "DISCORD RICH PRESENCE (RPC)", "DISCORD RPC", "#818cf8",
            [
                ("If I play a different game, will it still show up? Does this custom presence only affect CS2?",
                 "This custom presence ONLY affects Counter-Strike 2! It will never interfere with other games. When CS2 is closed, the Command Center completely closes the Discord RPC session. When you play other games (Apex, Dota 2, Rust, etc.), Discord's native game detection or that game's own rich presence will show completely normally."),
                ("Why does Discord show nothing when CS2 is closed?",
                 "By design! We ensure zero fake or phantom presence. When CS2 is closed, nothing is broadcasted so your Discord profile stays 100% clean and accurate."),
                ("Do new users need to create or configure a Discord Application ID?",
                 "No! The app is pre-configured with a universal verified Counter-Strike 2 Application ID. Rich Presence works completely out-of-the-box for all users with zero extra setup or developer portal steps."),
                ("Why don't the buttons [🎮 Server IP] and [💬 Community Discord] show when I view my own profile?",
                 "Discord's client intentionally hides Rich Presence action buttons on your OWN profile popout (Discord does this to prevent users from clicking links on their own profile). Rest assured, your friends, teammates, and server members CAN see and click both buttons directly on your profile!")
            ]
        )

        # Category 8: Custom ZE Map Cleaner
        _create_faq_card(
            "📦", "CUSTOM ZE MAP CLEANER & STORAGE HYGIENE", "STORAGE CLEANER", ACCENT_CYAN,
            [
                ("Why should I clean custom maps?",
                 "Custom Zombie Escape maps downloaded from community servers are stored as .vpk packages in csgo/maps/ and can range from 500MB to 2.5GB each. Over time, active ZE players accumulate 50GB to 150GB+ of stale map packages on their SSD. The cleaner lets you sort by file size or last played date, and safely delete obsolete or unpopular maps without touching base game files."),
                ("What happens if I delete a map and later rejoin a server running that map?",
                 "CS2 will automatically download the map fresh from the server's FastDL HTTP mirror before joining! You will never be banned, kicked, or encounter errors; deleting custom maps is 100% safe and reversible.")
            ]
        )

        # Category 9: PC Maintenance & System Hygiene
        _create_faq_card(
            "🧹", "PC MAINTENANCE & SYSTEM HYGIENE", "MAINTENANCE", ACCENT_ORANGE,
            [
                ("What do SSD TRIM, SFC, and DISM do?",
                 "SSD TRIM instructs your solid-state drive controller to reclaim unused memory blocks, maintaining peak NAND write speeds and low read latency. SFC (System File Checker) scans and repairs corrupted Windows core system files. DISM repairs the Windows Component Store image using official Microsoft files."),
                ("Does clearing Discord & Steam web cache log me out of my accounts?",
                 "No! The cleaner specifically targets cached images, stickers, and Chromium/CEF web data in the Cache folders. It never touches login tokens, saved passwords, or session cookies.")
            ]
        )

        # Category 10: GPU MPO Diagnostics & Troubleshooter
        _create_faq_card(
            "???", "GPU MPO DIAGNOSTICS & TROUBLESHOOTER (AMD, NVIDIA & INTEL)", "DIAGNOSTICS", ACCENT_CYAN,
            [
                ("Why is GPU MPO Diagnostics included in CS2 Command Center?",
                 "Multi-Plane Overlay (MPO) is one of the most common root causes of Alt-Tab black screens, display freezes, Discord/Chrome checkerboard glitches, and GPU driver crashes (such as AMD Driver Timeout or NVIDIA TDR) while playing CS2. CS2 Command Center provides this dedicated diagnostic tab so players can understand their MPO configuration, test for display issues, and access official AMD/NVIDIA resolution steps."),
                ("Is the GPU MPO Diagnostics tab safe? Does it modify my registry automatically?",
                 "The GPU MPO Diagnostics tab is strictly 100% READ-ONLY. It never makes registry edits and never alters your display driver automatically. It provides live hardware and registry inspection, clear technical explanations, and safe 1-click clipboard helpers for manual user review."),
                ("Should I disable Windows Multi-Plane Overlay (MPO)?",
                 "If your system runs smoothly with zero black screen flickers, driver timeouts, or dual-monitor stutter, keep MPO enabled (Windows default). If you suffer from 1-3 second Alt-Tab black screens, AMD driver timeouts, Discord checkerboard glitches, or G-Sync stutter with mixed refresh rates, disabling MPO via the registry is an officially verified, safe workaround."),
                ("What should I do before disabling MPO? Should I use DDU or AMD Cleanup Utility?",
                 "Before touching MPO registry settings, you should ALWAYS first perform a clean display driver wipe and reinstall using Display Driver Uninstaller (DDU) by Wagnardsoft in Windows Safe Mode, and check if that solved your problem. Many black screens and timeouts are fixed by a fresh driver install alone!\n\n⚠️ Why avoid AMD Cleanup Utility: Manufacturer cleanup tools like AMD Cleanup Utility often remove critical Windows chipset drivers, USB root hubs, and PCIe bus drivers, which can cause broken mouse/keyboard input or Safe Mode boot loops. DDU is isolated specifically to graphics display drivers.")
            ]
        )

        # Category 11: System Tray & Window Controls
        _create_faq_card(
            "🖥️", "SYSTEM TRAY & BACKGROUND WINDOW CONTROLS", "SYSTEM TRAY", ACCENT_GREEN,
            [
                ("How do the Minimize [-] and Close [X] buttons work?",
                 "Clicking the [-] Minimize button hides the application completely from the Windows taskbar and tucks it quietly into the system tray near the clock (~15MB RAM). Clicking the [X] Close button completely terminates and shuts down the application."),
                ("How do I restore the app from the system tray?",
                 "Simply left-click or right-click the orange CS2 icon in your Windows system tray near the clock, or launch the app shortcut again. You can also right-click the tray icon to quick-connect to GFL, toggle the Slot Sniper, or click [❌ Exit Completely].")
            ]
        )

        _bind_faq_wheel_recursive(faq_content)

        _bind_faq_wheel_recursive(faq_content)

    def _on_discord_toggle(self):
        enabled = self.var_discord_enabled.get()
        self.config["discord_rpc_enabled"] = enabled
        self.config["discord_client_id"] = app_config.DEFAULT_DISCORD_CLIENT_ID
        app_config.save_config(self.config)

        def _task():
            if not enabled:
                if self.discord_rpc:
                    self.discord_rpc.clear_activity()
                    self.discord_rpc.close()
                self.after(0, lambda: self._update_discord_preview_labels("Offline / Disabled", "Presence Disabled"))
                if hasattr(self, "discord_status_lbl") and self.discord_status_lbl.winfo_exists():
                    self.after(0, lambda: self.discord_status_lbl.config(text="○ Discord Presence Disabled", fg=FG_MUTED))
                self.log("[DISCORD] Rich presence disabled by user.")
            else:
                self.discord_rpc.set_client_id(app_config.DEFAULT_DISCORD_CLIENT_ID)
                if not core_logic.is_cs2_running():
                    self.discord_rpc.clear_activity()
                    self.discord_rpc.close()
                    self.after(0, lambda: self._update_discord_preview_labels("CS2 is not running", "Discord Presence Inactive (Nothing Shown)"))
                    if hasattr(self, "discord_status_lbl") and self.discord_status_lbl.winfo_exists():
                        self.after(0, lambda: self.discord_status_lbl.config(text="○ Discord Standby (Waiting for CS2)", fg=FG_MUTED))
                else:
                    self.discord_session_start = int(time.time())
                    self.discord_rpc.connect()
                    details = "In Main Menu • Standby"
                    state = "CS2 Command Center"
                    self.discord_rpc.set_activity(
                        details=details,
                        state=state,
                        start_timestamp=self.discord_session_start,
                        large_image=None
                    )
                    self.after(0, lambda: self._update_discord_preview_labels(details, state))
                    if hasattr(self, "discord_status_lbl") and self.discord_status_lbl.winfo_exists():
                        self.after(0, lambda: self.discord_status_lbl.config(text="● Discord IPC Connected (Active)", fg=ACCENT_GREEN))
                self.log("[DISCORD] Rich presence enabled by user.")
        threading.Thread(target=_task, daemon=True).start()

    def _save_and_connect_discord(self):
        self._on_discord_toggle()

    def _get_server_discord_buttons(self, host: str, port: int):
        btn_host_port = f"{host}:{port}"
        connect_url = f"https://geronimohq.com/connect?ip={btn_host_port}"
        btn1 = {"label": f"🎮 Server: {btn_host_port}", "url": connect_url}

        matched = None
        all_svs = list(getattr(self, "servers_data", None) or [])
        try:
            if hasattr(server_browser, "load_servers"):
                for s in server_browser.load_servers():
                    if not any(x.get("host") == s.get("host") and int(x.get("port", 27015)) == int(s.get("port", 27015)) for x in all_svs):
                        all_svs.append(s)
        except Exception:
            pass

        # Check by exact host and port
        for s in all_svs:
            s_h = str(s.get("host", "")).strip().lower()
            s_p = int(s.get("port", 27015))
            if s_h == str(host).strip().lower() and s_p == int(port):
                matched = s
                break

        # Fallback to host match
        if not matched:
            for s in all_svs:
                s_h = str(s.get("host", "")).strip().lower()
                if s_h and (s_h == str(host).strip().lower() or str(host).strip().lower() in s_h):
                    matched = s
                    break

        # Check China Cluster servers
        if not matched and hasattr(server_browser, "CHINA_CLUSTERS"):
            for cluster in server_browser.CHINA_CLUSTERS:
                c_name = cluster.get("name", "").split()[0]
                for cs in cluster.get("servers", []):
                    if str(cs.get("host", "")).strip().lower() == str(host).strip().lower() and int(cs.get("port", 27015)) == int(port):
                        matched = {
                            "id": cs.get("id"),
                            "name": cs.get("name"),
                            "host": cs.get("host"),
                            "port": cs.get("port"),
                            "cluster_name": c_name
                        }
                        break
                if matched:
                    break

        if matched:
            sid = str(matched.get("id", "")).lower()
            sname = str(matched.get("name", "")).strip()
            discord_url = matched.get("discord")
            website_url = matched.get("website")

            if discord_url:
                d_url = f"https://{discord_url}" if not str(discord_url).startswith("http") else str(discord_url)
                if "gfl" in sid or "74.91.124.21" in str(host):
                    lbl = "💬 GFL Community Discord"
                elif "possession" in sid or "pse" in sid or "103.62.49.55" in str(host):
                    lbl = "💬 PSE Community Discord"
                elif "mapeadores" in sid or "87.98.228.196" in str(host):
                    lbl = "💬 Mapeadores Discord"
                elif "cola" in sid or "178.33.160.187" in str(host):
                    lbl = "💬 cOLa Community Discord"
                elif "rss" in sid or "rsscs2" in str(host) or "14.5.33.30" in str(host):
                    lbl = "💬 RSS Community Discord"
                else:
                    tag = sid.upper() if len(sid) <= 6 else sname.split()[0]
                    lbl = f"💬 {tag} Discord"[:32]
                return [btn1, {"label": lbl, "url": d_url}]

            if website_url:
                w_url = f"https://{website_url}" if not str(website_url).startswith("http") else str(website_url)
                tag = sid.upper() if len(sid) <= 6 else sname.split()[0]
                return [btn1, {"label": f"🌐 {tag} Website"[:32], "url": w_url}]

            if matched.get("cluster_name"):
                c_lbl = f"🌐 {matched['cluster_name'][:14]} Portal"
                return [btn1, {"label": c_lbl, "url": "https://geronimohq.com"}]

        if "74.91.124.21" in str(host):
            return [
                btn1,
                {"label": "💬 GFL Community Discord", "url": "https://discord.gg/gflze"}
            ]

        # Any other server: NEVER show GFL! Show GeronimoHQ Portal
        return [
            btn1,
            {"label": "🌐 GeronimoHQ Portal", "url": "https://geronimohq.com"}
        ]

    def _refresh_discord_presence(self):
        if not self.config.get("discord_rpc_enabled", True):
            messagebox.showwarning("Discord Disabled", "Discord Rich Presence is disabled. Enable the checkbox above first.")
            return

        def _task():
            cid = self.config.get("discord_client_id", app_config.DEFAULT_DISCORD_CLIENT_ID).strip() or app_config.DEFAULT_DISCORD_CLIENT_ID
            self.discord_rpc.set_client_id(cid)

            is_running = core_logic.is_cs2_running() or ((time.time() - getattr(self, "_last_gsi_packet_time", 0)) < 25.0)
            if not is_running:
                self.discord_rpc.clear_activity()
                self.discord_rpc.close()
                self.after(0, lambda: self._update_discord_preview_labels("CS2 is not running", "Discord Presence Inactive (Nothing Shown)"))
                if hasattr(self, "discord_status_lbl") and self.discord_status_lbl.winfo_exists():
                    self.after(0, lambda: self.discord_status_lbl.config(text="○ Standby (CS2 Closed)", fg=FG_MUTED))
                self.log("[DISCORD] Refresh checked: CS2 is not currently running.")
                return

            # CS2 is running -> ensure Discord IPC pipe is connected
            if not self.discord_rpc.connected:
                conn_ok = self.discord_rpc.connect()
                if not conn_ok:
                    self.log("[DISCORD] Could not connect to local Discord client pipe. Ensure Discord desktop app is running.")
                    if hasattr(self, "discord_status_lbl") and self.discord_status_lbl.winfo_exists():
                        self.after(0, lambda: self.discord_status_lbl.config(text="⚠️ Discord Desktop Not Detected", fg=ACCENT_AMBER))
                    return

            if self.discord_session_start <= 0:
                self.discord_session_start = int(time.time())

            gsi_state = getattr(self, "gsi_latest_state", {})
            gsi_map = gsi_state.get("map_name", "").split("/")[-1].strip() if gsi_state.get("map_name") else ""
            gsi_act = gsi_state.get("activity", "")
            buttons = None

            if getattr(self, "active_tracked_server", None):
                host, port, name = self.active_tracked_server
                info = self.server_browser.query_server_info(host, port, timeout=1.2)
                if info and info.get("online"):
                    m_txt = f"Map: {info.get('map', 'Unknown')} ({info.get('players', 0)}/{info.get('max_players', 64)} Players)"
                else:
                    m_txt = f"Map: {gsi_map}" if gsi_map else "Zombie Escape Server"
                buttons = self._get_server_discord_buttons(host, port)
                self.discord_rpc.set_activity(
                    details=f"{name}",
                    state=m_txt,
                    start_timestamp=self.discord_session_start,
                    large_image=None,
                    buttons=buttons
                )
                b1 = buttons[0]["label"] if buttons else None
                b2 = buttons[1]["label"] if buttons and len(buttons) > 1 else None
                self.after(0, lambda n=name, m=m_txt, _b1=b1, _b2=b2: self._update_discord_preview_labels(n, m, _b1, _b2))
                if hasattr(self, "discord_status_lbl") and self.discord_status_lbl.winfo_exists():
                    self.after(0, lambda: self.discord_status_lbl.config(text=f"● Active: {name}", fg=ACCENT_GREEN))
            elif gsi_act == "playing" and gsi_map:
                matched = self._match_server_by_map(gsi_map)
                if matched:
                    self.active_tracked_server = matched
                    h, p, n = matched
                    dtl = n
                    st = f"Map: {gsi_map}"
                    buttons = self._get_server_discord_buttons(h, p)
                else:
                    dtl = "Zombie Escape Server" if gsi_map.startswith("ze_") else "Community Server"
                    st = f"Map: {gsi_map}"
                    buttons = [{"label": "🌐 GeronimoHQ Portal", "url": "https://geronimohq.com"}]
                self.discord_rpc.set_activity(
                    details=dtl,
                    state=st,
                    start_timestamp=self.discord_session_start,
                    large_image=None,
                    buttons=buttons
                )
                b1 = buttons[0]["label"] if buttons else None
                b2 = buttons[1]["label"] if buttons and len(buttons) > 1 else None
                self.after(0, lambda d=dtl, s=st, _b1=b1, _b2=b2: self._update_discord_preview_labels(d, s, _b1, _b2))
                if hasattr(self, "discord_status_lbl") and self.discord_status_lbl.winfo_exists():
                    self.after(0, lambda: self.discord_status_lbl.config(text=f"● Active: In-Game ({gsi_map})", fg=ACCENT_GREEN))
            else:
                details = "In Main Menu • Standby"
                state = "CS2 Command Center"
                self.discord_rpc.set_activity(
                    details=details,
                    state=state,
                    start_timestamp=self.discord_session_start,
                    large_image=None
                )
                self.after(0, lambda: self._update_discord_preview_labels(details, state))
                if hasattr(self, "discord_status_lbl") and self.discord_status_lbl.winfo_exists():
                    self.after(0, lambda: self.discord_status_lbl.config(text="● Active: CS2 Main Menu", fg=ACCENT_GREEN))
            self.log("[DISCORD] Rich presence manually refreshed and connected.")
        threading.Thread(target=_task, daemon=True).start()

    def clear_discord_presence(self):
        self.active_tracked_server = None
        if hasattr(self, "lbl_broadcast_active") and self.lbl_broadcast_active.winfo_exists():
            self.lbl_broadcast_active.config(text="● Current Tracking: Standby / Cleared", fg="#94a3b8")
        if self.discord_rpc:
            self.discord_rpc.clear_activity()
            self.discord_rpc.close()
        self.log("[DISCORD] Rich Presence cleared and Discord IPC closed.")
        self._update_discord_preview_labels("Offline / Cleared", "No Activity Broadcasted")

    def broadcast_server_to_discord(self, host: str, port: int, server_name: str):
        """Broadcasts server details to Discord even if connected via in-game console or community browser."""
        if not self.config.get("discord_rpc_enabled", False) or not self.config.get("discord_client_id"):
            messagebox.showwarning("Discord Disabled", "Please enable Discord Rich Presence and enter your Application Client ID first.")
            return

        def task():
            self.active_tracked_server = (host, port, server_name)
            self.discord_session_start = int(time.time())

            info = self.server_browser.query_server_info(host, port, timeout=1.2)
            if info and info.get("online"):
                map_str = f"Map: {info.get('map', 'Unknown')} ({info.get('players', 0)}/{info.get('max_players', 64)} Players)"
            else:
                map_str = "Zombie Escape Server"

            if not self.discord_rpc.connected:
                self.discord_rpc.connect()

            buttons = self._get_server_discord_buttons(host, port)
            self.discord_rpc.set_activity(
                details=f"{server_name}",
                state=map_str,
                start_timestamp=self.discord_session_start,
                large_image=None,
                buttons=buttons
            )
            self.log(f"[DISCORD] Broadcasted to Discord: {server_name} | {map_str}")
            b1 = buttons[0]["label"] if buttons else None
            b2 = buttons[1]["label"] if buttons and len(buttons) > 1 else None
            self.after(0, lambda: self._update_discord_preview_labels(server_name, map_str, b1, b2))
            if hasattr(self, "lbl_broadcast_active") and self.lbl_broadcast_active.winfo_exists():
                self.after(0, lambda: self.lbl_broadcast_active.config(text=f"● Current Tracking: {server_name} ({map_str})", fg=ACCENT_GREEN))
            self.after(0, lambda: messagebox.showinfo("Discord Broadcast", f"Now broadcasting to Discord:\n\n{server_name}\n{map_str}"))

        threading.Thread(target=task, daemon=True).start()

    def set_discord_standby(self):
        self.active_tracked_server = None
        self.discord_session_start = int(time.time())
        details = "In Main Menu • Standby"
        state = "CS2 Command Center"
        if self.discord_rpc and self.discord_rpc.connected:
            self.discord_rpc.set_activity(
                details=details,
                state=state,
                start_timestamp=self.discord_session_start,
                large_image=None
            )
            self.log("[DISCORD] Presence reset to: In Main Menu • Standby")
        self._update_discord_preview_labels(details, state)
        if hasattr(self, "lbl_broadcast_active") and self.lbl_broadcast_active.winfo_exists():
            self.lbl_broadcast_active.config(text="● Current Tracking: Standby / Main Menu", fg="#94a3b8")

    def _update_discord_preview_labels(self, details: str, state: str, btn1: str = None, btn2: str = None):
        if hasattr(self, "discord_preview_details"):
            self.discord_preview_details.set(details)
        if hasattr(self, "discord_preview_state"):
            self.discord_preview_state.set(state)

        user_persona = core_logic.get_steam_active_persona() or "Player Profile"
        if hasattr(self, "preview_username_lbl") and self.preview_username_lbl.winfo_exists():
            self.preview_username_lbl.config(text=user_persona)

        is_active = (details not in ("CS2 is not running", "Discord Presence Inactive (Nothing Shown)", "Offline / Disabled", "Offline / Cleared"))

        if hasattr(self, "preview_status_lbl") and self.preview_status_lbl.winfo_exists():
            if is_active:
                if "Main Menu" in details or "Standby" in details:
                    self.preview_status_lbl.config(text="● Online  |  In Main Menu", fg="#23a55a")
                else:
                    self.preview_status_lbl.config(text="● In-Game  |  Playing Counter-Strike 2", fg="#23a55a")
                if hasattr(self, "preview_ava") and self.preview_ava.winfo_exists():
                    self.preview_ava.config(highlightbackground="#23a55a")
            else:
                self.preview_status_lbl.config(text="○ Standby  |  CS2 Closed (No Presence)", fg="#949ba4")
                if hasattr(self, "preview_ava") and self.preview_ava.winfo_exists():
                    self.preview_ava.config(highlightbackground="#4e5058")

        # Toggle between Dormant (CS2 closed/offline) and Active (CS2 running)
        if hasattr(self, "preview_dormant") and hasattr(self, "preview_active"):
            try:
                if is_active:
                    if self.preview_dormant.winfo_ismapped():
                        self.preview_dormant.pack_forget()
                    if not self.preview_active.winfo_ismapped():
                        self.preview_active.pack(fill="x")
                else:
                    if self.preview_active.winfo_ismapped():
                        self.preview_active.pack_forget()
                    if not self.preview_dormant.winfo_ismapped():
                        self.preview_dormant.pack(fill="x")
            except Exception:
                pass

        # Toggle individual button frames inside preview_active
        if hasattr(self, "prev_btn_box") and hasattr(self, "preview_b1_frame") and hasattr(self, "preview_b2_frame"):
            try:
                if is_active and (btn1 or btn2):
                    if not self.prev_btn_box.winfo_ismapped():
                        self.prev_btn_box.pack(fill="x", pady=(8, 2))
                    if btn1:
                        self.discord_preview_btn1.set(btn1)
                        if not self.preview_b1_frame.winfo_ismapped():
                            self.preview_b1_frame.pack(fill="x", pady=(0, 3))
                    else:
                        if self.preview_b1_frame.winfo_ismapped():
                            self.preview_b1_frame.pack_forget()
                    if btn2:
                        self.discord_preview_btn2.set(btn2)
                        if not self.preview_b2_frame.winfo_ismapped():
                            self.preview_b2_frame.pack(fill="x")
                    else:
                        if self.preview_b2_frame.winfo_ismapped():
                            self.preview_b2_frame.pack_forget()
                else:
                    if self.prev_btn_box.winfo_ismapped():
                        self.prev_btn_box.pack_forget()
            except Exception:
                pass

    def _tick_discord_elapsed_timer(self):
        if getattr(self, "_is_resizing", False):
            if not getattr(self, "_quitting", False):
                self.after(500, self._tick_discord_elapsed_timer)
            return
        try:
            if hasattr(self, "discord_preview_elapsed") and hasattr(self, "discord_session_start"):
                is_cs2_open = bool(core_logic.is_cs2_running())
                if is_cs2_open and self.discord_session_start > 0:
                    elapsed = max(0, int(time.time() - self.discord_session_start))
                    m, s = divmod(elapsed, 60)
                    h, m = divmod(m, 60)
                    if h > 0:
                        self.discord_preview_elapsed.set(f"⏱ {h:d}:{m:02d}:{s:02d} elapsed")
                    else:
                        self.discord_preview_elapsed.set(f"⏱ {m:02d}:{s:02d} elapsed")
                else:
                    self.discord_preview_elapsed.set("⏱ 00:00 elapsed")
        except Exception:
            pass
        if not getattr(self, "_quitting", False):
            self.after(1000, self._tick_discord_elapsed_timer)

    def _on_gsi_state_update(self, state: dict):
        self.gsi_latest_state = state
        self._last_gsi_packet_time = time.time()
        act = state.get("activity", "")
        map_n = state.get("map_name", "")
        now = time.time()

        last_act = getattr(self, "_last_gsi_logged_act", None)
        last_map = getattr(self, "_last_gsi_logged_map", None)
        last_log_time = getattr(self, "_last_gsi_log_time", 0.0)

        # 1. In Match / Playing on Map
        if act == "playing" and map_n:
            if act != last_act or map_n != last_map:
                if (now - last_log_time) >= 1.0 or map_n != last_map:
                    self._last_gsi_logged_act = "playing"
                    self._last_gsi_logged_map = map_n
                    self._last_gsi_log_time = now
                    self.log(f"[GSI] Live match detected: map={map_n}")
        # 2. In Main Menu / Lobby
        elif act == "menu":
            if act != last_act:
                if (now - last_log_time) >= 1.0:
                    self._last_gsi_logged_act = "menu"
                    self._last_gsi_logged_map = ""
                    self._last_gsi_log_time = now
                    self.log("[GSI] CS2 returned to Main Menu / Lobby.")

    def _scan_for_user_on_servers(self, user_persona: str):
        if not user_persona:
            return None
        target = user_persona.lower().strip()

        # Check GFL first (primary server)
        try:
            res = self.server_browser.query_server_players("74.91.124.21", 27015, timeout=0.8)
            if res.get("success"):
                for p in res.get("players", []):
                    if p.get("name", "").strip().lower() == target:
                        return ("74.91.124.21", 27015, "GFL Clan Zombie Escape 24/7")
        except Exception:
            pass

        # Check all other servers in registered server list
        all_svs = getattr(self, "servers_data", None) or server_browser.load_servers()
        for s in all_svs:
            h, p, n = s.get("host"), s.get("port"), s.get("name")
            if h == "74.91.124.21":
                continue
            try:
                res = self.server_browser.query_server_players(h, p, timeout=0.6)
                if res.get("success"):
                    for pl in res.get("players", []):
                        if pl.get("name", "").strip().lower() == target:
                            return (h, p, n)
            except Exception:
                pass
        return None

    def _match_server_by_map(self, map_name: str):
        if not map_name:
            return None
        target_map = map_name.split("/")[-1].lower().strip()
        
        # Fast check GFL first
        try:
            gfl_info = self.server_browser.query_server_info("74.91.124.21", 27015, timeout=0.8)
            if gfl_info.get("online"):
                gfl_m = gfl_info.get("map", "").split("/")[-1].lower().strip()
                if gfl_m == target_map:
                    return ("74.91.124.21", 27015, "GFL Clan Zombie Escape 24/7")
        except Exception:
            pass

        servers = getattr(self, "servers_data", None) or server_browser.load_servers()
        for s in servers:
            h, p, n = s.get("host"), s.get("port"), s.get("name")
            if h == "74.91.124.21":
                continue
            try:
                info = self.server_browser.query_server_info(h, p, timeout=0.6)
                if info.get("online"):
                    cur_m = info.get("map", "").split("/")[-1].lower().strip()
                    if cur_m == target_map:
                        return (h, p, n)
            except Exception:
                pass
        return None

    def _send_web_presence_heartbeat(self, is_cs2: bool, is_steam: bool = False):
        def _req():
            try:
                import urllib.request
                url = f"https://geronimohq-telemetry.onrender.com/api/presence/heartbeat?is_cs2_running={'true' if is_cs2 else 'false'}&is_steam_running={'true' if is_steam else 'false'}&in_menu=true"
                headers = {"User-Agent": "CS2CommandCenter/2.0"}
                secret = self.config.get("presence_secret", "")
                if secret and str(secret).strip():
                    headers["X-Geronimo-Token"] = str(secret).strip()
                req = urllib.request.Request(url, headers=headers)
                urllib.request.urlopen(req, timeout=3.5)
            except Exception:
                pass
        threading.Thread(target=_req, daemon=True).start()

    def _start_presence_heartbeat(self):
        """100% Automatic CS2 Lifecycle & Presence Manager.
        - When CS2 is CLOSED: Discord presence is 100% CLEARED (Nothing shown).
        - When CS2 is RUNNING: Automatically detects state, map, and server."""
        def _loop():
            was_running = False
            last_checked_scan_time = 0
            last_logged_map = ""
            user_missing_counter = 0
            last_hb_time = 0
            user_persona = core_logic.get_steam_active_persona()
            if user_persona:
                self.log(f"[SYSTEM] Detected active Steam Persona: '{user_persona}'")

            while not getattr(self, "_quitting", False):
                time.sleep(2.0)
                if getattr(self, "_quitting", False):
                    break

                if not self.config.get("discord_rpc_enabled", True):
                    if self.discord_rpc and self.discord_rpc.connected:
                        self.discord_rpc.clear_activity()
                        self.discord_rpc.close()
                    continue

                is_running = core_logic.is_cs2_running() or ((time.time() - getattr(self, "_last_gsi_packet_time", 0)) < 25.0)
                is_steam = core_logic.is_steam_running() or is_running
                now_ts = time.time()
                if now_ts - last_hb_time >= 8.0:
                    last_hb_time = now_ts
                    self._send_web_presence_heartbeat(is_running, is_steam)

                # 1. CS2 IS CLOSED -> DO NOT SHOW ANYTHING ON DISCORD!
                if not is_running:
                    now = time.time()
                    launching = (getattr(self, "active_tracked_since", 0) > 0 and (now - self.active_tracked_since) < 45.0)
                    if not launching:
                        if was_running or (self.discord_rpc and self.discord_rpc.connected):
                            try:
                                self.discord_rpc.clear_activity()
                                self.discord_rpc.close()
                            except Exception:
                                pass
                            was_running = False
                            self.active_tracked_server = None
                            self.active_tracked_since = 0
                            user_missing_counter = 0
                            last_logged_map = ""
                            self._last_gsi_logged_act = None
                            self._last_gsi_logged_map = ""
                            self.after(0, lambda: self._update_discord_preview_labels(
                                "CS2 is not running", "Discord Presence Inactive (Nothing Shown)"
                            ))
                            if hasattr(self, "discord_status_lbl") and self.discord_status_lbl.winfo_exists():
                                self.after(0, lambda: self.discord_status_lbl.config(text="○ Standby (CS2 Closed)", fg=FG_MUTED))
                    continue

                # 2. CS2 IS RUNNING -> BROADCAST STATUS AUTOMATICALLY
                cid = self.config.get("discord_client_id", app_config.DEFAULT_DISCORD_CLIENT_ID).strip()
                if not cid:
                    cid = app_config.DEFAULT_DISCORD_CLIENT_ID
                self.discord_rpc.set_client_id(cid)

                if not was_running:
                    was_running = True
                    self.discord_session_start = int(time.time())
                    self.discord_rpc.connect()

                if not self.discord_rpc.connected:
                    self.discord_rpc.connect()

                if hasattr(self, "sniper") and self.sniper and self.sniper.is_active:
                    continue

                if not user_persona:
                    user_persona = core_logic.get_steam_active_persona()

                # GSI State
                gsi_state = getattr(self, "gsi_latest_state", {})
                raw_gsi_map = gsi_state.get("map_name", "").strip()
                gsi_map = raw_gsi_map.split("/")[-1].strip() if raw_gsi_map else ""
                gsi_act = gsi_state.get("activity", "")
                now = time.time()

                if gsi_act == "menu" and not gsi_map:
                    if self.active_tracked_server is not None:
                        self.log("[DISCORD] Detected main menu, resetting server tracking to standby.")
                        self.active_tracked_server = None
                        user_missing_counter = 0

                # SERVER AUTO-DETECTION
                if self.active_tracked_server is not None:
                    cur_host, cur_port, cur_name = self.active_tracked_server
                    in_grace = (now - getattr(self, "active_tracked_since", 0)) < 30.0

                    if not in_grace and user_persona:
                        try:
                            res = self.server_browser.query_server_players(cur_host, cur_port, timeout=0.9)
                            if res.get("success"):
                                pl_names = [p.get("name", "").strip().lower() for p in res.get("players", [])]
                                if user_persona.lower() in pl_names:
                                    user_missing_counter = 0
                                else:
                                    user_missing_counter += 1
                                    if user_missing_counter >= 3:
                                        switched = self._scan_for_user_on_servers(user_persona)
                                        if switched and switched[0] != cur_host:
                                            self.active_tracked_server = switched
                                            self.active_tracked_since = time.time()
                                            user_missing_counter = 0
                                            self.discord_session_start = int(time.time())
                                            self.log(f"[DISCORD] Player switched servers: {switched[2]}")
                                        else:
                                            self.active_tracked_server = None
                                            user_missing_counter = 0
                                            self.log("[DISCORD] Player left server, reset to Main Menu • Standby.")
                        except Exception:
                            pass
                else:
                    if (now - last_checked_scan_time) > 3.0:
                        last_checked_scan_time = now
                        if user_persona:
                            joined_server = self._scan_for_user_on_servers(user_persona)
                            if joined_server:
                                self.active_tracked_server = joined_server
                                self.active_tracked_since = time.time()
                                user_missing_counter = 0
                                self.discord_session_start = int(time.time())
                                self.log(f"[DISCORD] Detected player joined server: {joined_server[2]}")
                        if self.active_tracked_server is None and gsi_map:
                            matched = self._match_server_by_map(gsi_map)
                            if matched:
                                self.active_tracked_server = matched
                                self.active_tracked_since = time.time()
                                user_missing_counter = 0
                                self.discord_session_start = int(time.time())
                                self.log(f"[DISCORD] Auto-detected connected server via map '{gsi_map}': {matched[2]}")

                # COMPOSE PACKET & BUTTONS
                dtl = "In Main Menu • Standby"
                st = "CS2 Command Center"
                buttons = None

                if getattr(self, "active_tracked_server", None):
                    host, port, sname = self.active_tracked_server
                    try:
                        info = self.server_browser.query_server_info(host, port, timeout=1.2)
                        m_name = (info.get("map") if info and info.get("online") else "") or gsi_map or "Unknown"
                        p_cnt = info.get("curr_players", 0) if info and info.get("online") else 0
                        mp_cnt = info.get("max_players", 64) if info and info.get("online") else 64
                        dtl = f"{sname}"
                        st = f"Map: {m_name} ({p_cnt}/{mp_cnt} Players)" if p_cnt else f"Map: {m_name}"
                        buttons = self._get_server_discord_buttons(host, port)
                        if m_name and m_name != "Unknown" and m_name != last_logged_map:
                            self.log(f"[DISCORD] Live tracking: {sname} [Map: {m_name} ({p_cnt}/{mp_cnt} Players)]")
                            last_logged_map = m_name
                    except Exception:
                        pass
                elif gsi_act == "playing" and gsi_map:
                    matched = self._match_server_by_map(gsi_map)
                    if matched:
                        self.active_tracked_server = matched
                        self.active_tracked_since = time.time()
                        h, p, n = matched
                        dtl = n
                        st = f"Map: {gsi_map}"
                        buttons = self._get_server_discord_buttons(h, p)
                    else:
                        dtl = "Zombie Escape Server" if gsi_map.startswith("ze_") else "Community Server"
                        st = f"Map: {gsi_map}"
                        buttons = [{"label": "🌐 GeronimoHQ Portal", "url": "https://geronimohq.com"}]
                else:
                    dtl = "In Main Menu • Standby"
                    st = "CS2 Command Center"

                try:
                    if self.discord_rpc.connected:
                        self.discord_rpc.set_activity(
                            details=dtl,
                            state=st,
                            start_timestamp=self.discord_session_start,
                            large_image=None,
                            buttons=buttons
                        )
                        b1_txt = buttons[0]["label"] if buttons and len(buttons) > 0 else None
                        b2_txt = buttons[1]["label"] if buttons and len(buttons) > 1 else None
                        self.after(0, lambda d=dtl, s=st, b1=b1_txt, b2=b2_txt: self._update_discord_preview_labels(d, s, b1, b2))
                        if hasattr(self, "discord_status_lbl") and self.discord_status_lbl.winfo_exists():
                            st_txt = f"● Active: {dtl}" if dtl != "In Main Menu • Standby" else "● Active: CS2 Main Menu"
                            self.after(0, lambda st_t=st_txt: self.discord_status_lbl.config(text=st_t, fg=ACCENT_GREEN))
                except Exception:
                    pass

        threading.Thread(target=_loop, daemon=True).start()

    def _init_discord_presence(self):
        cid = self.config.get("discord_client_id", app_config.DEFAULT_DISCORD_CLIENT_ID).strip()
        self.discord_rpc.set_client_id(cid)
        if core_logic.is_cs2_running():
            self.discord_rpc.connect()
        else:
            self._update_discord_preview_labels("CS2 is not running", "Discord Presence Inactive (Nothing Shown)")

    def run_one_click_optimization(self):
        def task():
            self.log("--- Starting ONE-CLICK Optimization ---")
            if self.opt_gamedvr.get():
                for l in core_logic.optimize_windows_game_dvr():
                    self.log(l)
            if self.opt_fullscreen.get() and self.paths["cs2_exe"]:
                for l in core_logic.disable_fullscreen_optimizations(self.paths["cs2_exe"]):
                    self.log(l)
            if self.opt_autoexec.get() and self.paths["cfg_dir"]:
                success, logs = core_logic.install_autoexec(self.paths["cfg_dir"])
                for l in logs:
                    self.log(l)
                self._refresh_autoexec_preview()
            if self.opt_power.get():
                plan = self.selected_power_plan.get()
                for l in core_logic.set_power_plan(plan):
                    self.log(l)
            if self.opt_shaders.get():
                files, bytes_freed, logs = core_logic.clean_shader_caches()
                for l in logs:
                    self.log(l)
                mb = bytes_freed / (1024 * 1024)
                self.log(f"Shader cache purge: {files} files cleaned ({mb:.2f} MB freed).")
            if self.opt_cs2_dumps.get():
                dfiles, dbytes, dlogs = core_logic.clean_cs2_temp_dumps(self.paths["cs2_dir"])
                for l in dlogs:
                    self.log(l)

            app_config.update_optimization_timestamp(self.config)
            self.after(0, self._refresh_weekly_maint_banner)
            self.log("--- OPTIMIZATION COMPLETED SUCCESSFULLY! ---")
            messagebox.showinfo("Done", "All selected CS2 optimizations have been applied successfully!\n\nYour custom binds and settings were preserved.")

        threading.Thread(target=task, daemon=True).start()

    def run_revert_all(self):
        def task():
            self.log("--- Reverting All Optimizations to Defaults ---")
            for l in core_logic.revert_windows_game_dvr():
                self.log(l)
            if self.paths["cs2_exe"]:
                for l in core_logic.revert_fullscreen_optimizations(self.paths["cs2_exe"]):
                    self.log(l)
            if self.paths["cfg_dir"]:
                success, logs = core_logic.restore_autoexec_backup(self.paths["cfg_dir"])
                for l in logs:
                    self.log(l)
                self._refresh_autoexec_preview()
            for l in core_logic.set_power_plan("balanced"):
                self.log(l)

            self.log("--- ALL TWEAKS REVERTED TO DEFAULTS ---")
            messagebox.showinfo("Reverted", "All settings and configs have been restored back to defaults!")

        threading.Thread(target=task, daemon=True).start()

    def run_live_boost(self):
        success, msg = core_logic.boost_cs2_process()
        self.log(msg)
        self.status_cs2_lbl.config(text=f"Status: {msg}", fg=ACCENT_GREEN if success else ACCENT_RED)
        if success:
            messagebox.showinfo("Live CPU Priority Boost", msg)
        else:
            messagebox.showwarning("Live CPU Priority Boost", msg)

    def _refresh_dns_interface_header(self):
        def _bg():
            try:
                iface_info = core_logic.get_active_network_interface()
                txt = f"Adapter: {iface_info['interface_name']}  |  Active DNS: {iface_info['current_dns']}"
                self.active_dns_raw = iface_info.get("current_dns", "")
                self.active_iface_name = iface_info.get("interface_name", "Ethernet")
                if hasattr(self, "dns_iface_var"):
                    self.safe_after(0, lambda: self.dns_iface_var.set(txt))

                # Update row buttons to reflect live ACTIVE status
                def _update_row_buttons():
                    for pid, w in getattr(self, "dns_row_widgets", {}).items():
                        prov = w.get("provider", {})
                        btn = w.get("use_btn")
                        if btn and prov and prov.get("primary"):
                            if prov["primary"] in self.active_dns_raw:
                                btn.config(text="✓ ACTIVE", fg="#34d399", bg="#064e3b", activebackground="#065f46")
                            else:
                                btn.config(text="Use This DNS", font=("Segoe UI", -12, "bold"), fg="#ffffff", bg="#1e293b", activebackground=ACCENT_ORANGE)
                self.safe_after(0, _update_row_buttons)
            except Exception:
                pass
        threading.Thread(target=_bg, daemon=True).start()

    def _on_dns_row_selected(self, pid: str, manual: bool = True):
        if manual:
            self.user_manually_picked_dns = True
        self.selected_dns_id.set(pid)
        selected_name = pid
        for row_pid, w in getattr(self, "dns_row_widgets", {}).items():
            is_sel = (row_pid == pid)
            bg_col = "#162032" if is_sel else "#131924"
            r_bench = getattr(self, "dns_bench_results", {}).get(row_pid, {})
            if is_sel:
                border_col = ACCENT_CYAN
                selected_name = w["provider"]["name"]
            elif r_bench.get("is_fastest"):
                border_col = ACCENT_GREEN
            else:
                border_col = "#1f293d"
            try:
                w["frame"].config(bg=bg_col, highlightbackground=border_col)
                w["rb"].config(bg=bg_col, activebackground=bg_col)
                w["ip_lbl"].config(bg=bg_col)
                w["desc_lbl"].config(bg=bg_col)
                w["res_lbl"].config(bg=bg_col)
            except Exception:
                pass

        if hasattr(self, "btn_dns_apply"):
            self.btn_dns_apply.config(text=f"🚀 Apply Selected: {selected_name}")
        if manual and hasattr(self, "dns_status_var"):
            self.dns_status_var.set(f"Selected: {selected_name} — Click '🚀 Apply Selected' or 'Use This DNS' to apply.")

    def _select_and_apply_dns_row(self, pid: str):
        self._on_dns_row_selected(pid, manual=True)
        self.apply_selected_dns_ui()

    def apply_custom_dns_ui(self):
        if not self.admin_status:
            ans = messagebox.askyesno(
                "Administrator Privileges Required",
                "Applying Custom DNS settings to your Windows network adapter requires Administrator privileges.\n\n"
                "Would you like to relaunch CS2 Command Center as Administrator now?"
            )
            if ans:
                self.relaunch_as_admin()
            return

        prim = (self.custom_dns_primary_var.get() if hasattr(self, "custom_dns_primary_var") else "").strip()
        sec = (self.custom_dns_secondary_var.get() if hasattr(self, "custom_dns_secondary_var") else "").strip()
        if not prim:
            messagebox.showwarning("Custom DNS", "Please enter a valid Primary DNS IPv4 address (e.g. 1.1.1.1).")
            return

        # Check if already active
        active_dns = getattr(self, "active_dns_raw", "")
        if prim in active_dns:
            core_logic.flush_dns()
            self.log(f"[DNS] Custom DNS ({prim}) is already active on adapter {getattr(self, 'active_iface_name', 'Ethernet')}. DNS cache flushed.")
            if hasattr(self, "dns_status_var"):
                self.dns_status_var.set(f"✅ Active DNS confirmed: Custom ({prim} / {sec or 'None'})")
            messagebox.showinfo(
                "Custom Gaming DNS Already Active",
                f"✅ Already Active on Your Network Adapter!\n\n"
                f"Adapter: {getattr(self, 'active_iface_name', 'Active Adapter')}\n"
                f"Primary DNS: {prim}\n"
                f"Secondary DNS: {sec or '(None)'}\n\n"
                f"Your PC is already actively using this Custom DNS configuration.\nWindows DNS resolver cache has been freshly refreshed."
            )
            return

        def task():
            success, logs = core_logic.apply_dns_provider(prim, sec, f"Custom DNS ({prim})")
            for l in logs:
                self.log(l)

            def _done():
                self._refresh_dns_interface_header()
                if success:
                    if hasattr(self, "dns_status_var"):
                        self.dns_status_var.set(f"✅ Active DNS locked to Custom ({prim} / {sec or 'None'})")
                    messagebox.showinfo(
                        "Custom Gaming DNS Applied",
                        f"Successfully configured your Custom DNS!\n\n"
                        f"Primary DNS: {prim}\n"
                        f"Secondary DNS: {sec or '(None)'}\n\n"
                        f"Windows DNS resolver cache has also been flushed."
                    )
                else:
                    messagebox.showwarning("DNS Update Notice", "\n".join(logs))

            self.safe_after(0, _done)

        threading.Thread(target=task, daemon=True).start()

    def run_dns_benchmark_ui(self):
        if hasattr(self, "btn_dns_bench"):
            self.btn_dns_bench.config(state="disabled", text="⏳ Benchmarking 6 DNS Servers...")
        if hasattr(self, "dns_status_var"):
            self.dns_status_var.set("Testing UDP port 53 latency & jitter across 6 global DNS providers...")
        self.log("[DNS BENCHMARK] Benchmarking Cloudflare, Google, Quad9, OpenDNS, Level3, and AdGuard in parallel...")

        def task():
            results = core_logic.benchmark_all_dns_providers()

            def _update_ui():
                if hasattr(self, "btn_dns_bench"):
                    self.btn_dns_bench.config(state="normal", text="⚡ Benchmark All DNS Servers")
                self.dns_bench_results = {r["id"]: r for r in results}

                fastest_item = results[0] if results else None
                for r in results:
                    pid = r["id"]
                    w = self.dns_row_widgets.get(pid)
                    if not w:
                        continue
                    lbl = w["res_lbl"]
                    if not r["reachable"]:
                        lbl.config(text="Timeout / Blocked", fg=ACCENT_RED)
                    elif r.get("is_fastest"):
                        lbl.config(
                            text=f"🏆 #1 FASTEST: {r['avg_ms']:.1f} ms (Jitter: {r['jitter_ms']:.1f} ms)",
                            fg=ACCENT_GREEN
                        )
                    else:
                        col = ACCENT_CYAN if r["avg_ms"] < 35.0 else ACCENT_AMBER
                        lbl.config(
                            text=f"#{r['rank']}  {r['avg_ms']:.1f} ms (Jitter: {r['jitter_ms']:.1f} ms)",
                            fg=col
                        )

                if fastest_item and fastest_item["reachable"]:
                    if not getattr(self, "user_manually_picked_dns", False):
                        self._on_dns_row_selected(fastest_item["id"], manual=False)
                    else:
                        self._on_dns_row_selected(self.selected_dns_id.get(), manual=False)
                    msg = f"🏆 Fastest: {fastest_item['name']} ({fastest_item['avg_ms']:.1f} ms) — Click ANY row below to choose your preferred DNS!"
                    if hasattr(self, "dns_status_var"):
                        self.dns_status_var.set(msg)
                    self.log(f"[DNS BENCHMARK] {msg}")
                else:
                    if hasattr(self, "dns_status_var"):
                        self.dns_status_var.set("Benchmark finished. Click any DNS row below to select.")
                self._refresh_dns_interface_header()

            self.safe_after(0, _update_ui)

        threading.Thread(target=task, daemon=True).start()

    def apply_selected_dns_ui(self):
        if not self.admin_status:
            ans = messagebox.askyesno(
                "Administrator Privileges Required",
                "Applying Gaming DNS settings to your Windows network adapter requires Administrator privileges.\n\n"
                "Would you like to relaunch CS2 Command Center as Administrator now?"
            )
            if ans:
                self.relaunch_as_admin()
            return

        sel_id = self.selected_dns_id.get() if hasattr(self, "selected_dns_id") else "cloudflare"
        provider = None
        for p in core_logic.DNS_PROVIDERS:
            if p["id"] == sel_id:
                provider = p
                break
        if not provider:
            provider = core_logic.DNS_PROVIDERS[0]

        # Check if already active
        active_dns = getattr(self, "active_dns_raw", "")
        if provider["primary"] in active_dns:
            core_logic.flush_dns()
            self.log(f"[DNS] Provider '{provider['name']}' ({provider['primary']}) is already active on adapter {getattr(self, 'active_iface_name', 'Ethernet')}. DNS cache flushed.")
            if hasattr(self, "dns_status_var"):
                self.dns_status_var.set(f"✅ Active DNS confirmed: {provider['name']}")
            messagebox.showinfo(
                "Gaming DNS Already Active",
                f"✅ Already Active on Your Network Adapter!\n\n"
                f"Adapter: {getattr(self, 'active_iface_name', 'Active Adapter')}\n"
                f"Provider: {provider['name']}\n"
                f"Primary DNS: {provider['primary']}\n"
                f"Secondary DNS: {provider['secondary']}\n\n"
                f"Your system is already actively using this DNS provider.\nWindows DNS resolver cache has been freshly refreshed."
            )
            return

        def task():
            success, logs = core_logic.apply_dns_provider(
                provider["primary"], provider["secondary"], provider["name"]
            )
            for l in logs:
                self.log(l)

            def _done():
                self._refresh_dns_interface_header()
                if success:
                    if hasattr(self, "dns_status_var"):
                        self.dns_status_var.set(f"✅ Active DNS locked to {provider['name']}")
                    messagebox.showinfo(
                        "Gaming DNS Applied",
                        f"Successfully configured Gaming DNS!\n\n"
                        f"Provider: {provider['name']}\n"
                        f"Primary DNS: {provider['primary']}\n"
                        f"Secondary DNS: {provider['secondary']}\n\n"
                        f"Windows DNS resolver cache has also been flushed."
                    )
                else:
                    messagebox.showwarning("DNS Update Notice", "\n".join(logs))

            self.safe_after(0, _done)

        threading.Thread(target=task, daemon=True).start()

    def restore_dns_dhcp_ui(self):
        if not self.admin_status:
            ans = messagebox.askyesno(
                "Administrator Privileges Required",
                "Restoring network adapter DNS to ISP Default (DHCP) requires Administrator privileges.\n\n"
                "Would you like to relaunch CS2 Command Center as Administrator now?"
            )
            if ans:
                self.relaunch_as_admin()
            return

        def task():
            success, logs = core_logic.restore_dns_to_dhcp()
            for l in logs:
                self.log(l)

            def _done():
                self._refresh_dns_interface_header()
                if success:
                    if hasattr(self, "dns_status_var"):
                        self.dns_status_var.set("↺ Restored to ISP Default (Automatic DHCP)")
                    messagebox.showinfo(
                        "DNS Restored to Default",
                        "Your network adapter has been restored to Automatic ISP Default (DHCP) DNS and the resolver cache was flushed."
                    )
                else:
                    messagebox.showwarning("DNS Restore Notice", "\n".join(logs))

            self.safe_after(0, _done)

        threading.Thread(target=task, daemon=True).start()

    def run_pc_maintenance(self):
        def task():
            self.log("--- Starting Safe PC Maintenance ---")
            total_freed = 0
            if self.maint_temp.get():
                d, f, logs = core_logic.clean_windows_temp_files()
                total_freed += f
                for l in logs:
                    self.log(l)
            if self.maint_win_update.get():
                d, f, logs = core_logic.clean_windows_update_cache()
                total_freed += f
                for l in logs:
                    self.log(l)
            if self.maint_discord_steam.get():
                d, f, logs = core_logic.clean_discord_and_steam_cache(self.paths["steam_path"])
                total_freed += f
                for l in logs:
                    self.log(l)
            if self.maint_thumb.get():
                d, f, logs = core_logic.clean_explorer_thumbnail_cache()
                total_freed += f
                for l in logs:
                    self.log(l)
            if self.maint_recycle.get():
                s, logs = core_logic.empty_recycle_bin()
                for l in logs:
                    self.log(l)
            if self.maint_dns.get():
                s, logs = core_logic.flush_dns_cache()
                for l in logs:
                    self.log(l)

            mb = total_freed / (1024 * 1024)
            app_config.update_maintenance_timestamp(self.config)
            self.after(0, self._refresh_weekly_maint_banner)
            if hasattr(self, "d_list_frame"):
                self.after(0, lambda: self._refresh_drives_list(self.d_list_frame))

            self.log(f"--- PC Maintenance Complete: Freed {mb:.1f} MB of disposable cache! ---")
            msg = f"Safe PC Maintenance finished!\n\nFreed: {mb:.1f} MB"
            if self.maint_recycle.get():
                msg += "\nRecycle Bin emptied."
            if self.maint_dns.get():
                msg += "\nDNS cache flushed."
            messagebox.showinfo("Maintenance Complete", msg)

        threading.Thread(target=task, daemon=True).start()

    def launch_cleanmgr_ui(self):
        success, msg = core_logic.launch_cleanmgr()
        self.log(f"[TOOLS] {msg}")

    def open_startup_apps_ui(self):
        success, msg = core_logic.open_startup_apps()
        self.log(f"[TOOLS] {msg}")

    def relaunch_as_admin(self):
        """Prompts Windows UAC to relaunch CS2 Command Center with Administrator privileges."""
        global _single_instance_mutex
        try:
            exe_path = sys.executable
            params = "--elevated"
            if "python.exe" in exe_path.lower():
                exe_dir = os.path.dirname(os.path.abspath(__file__))
                compiled_exe = os.path.join(exe_dir, "dist", "CS2_Command_Center.exe")
                if os.path.exists(compiled_exe):
                    exe_path = compiled_exe
                else:
                    script_path = os.path.abspath(__file__)
                    params = f'"{script_path}" --elevated'

            # 1. Close event handle first
            if hasattr(self, "h_show_event") and self.h_show_event:
                try:
                    ctypes.windll.kernel32.CloseHandle(self.h_show_event)
                    self.h_show_event = None
                except Exception:
                    pass

            # 2. Release and close the single-instance mutex so the elevated process can claim it without ERROR_ALREADY_EXISTS
            if _single_instance_mutex:
                try:
                    ctypes.windll.kernel32.CloseHandle(_single_instance_mutex)
                    _single_instance_mutex = None
                except Exception:
                    pass

            # 3. Launch elevated process with runas
            ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", exe_path, params, None, 1)
            # ShellExecuteW returns an HINSTANCE integer. Values > 32 indicate success.
            # <= 32 means failure or user clicked "No" on UAC prompt (e.g. ERROR_CANCELLED / 5)
            if ret > 32:
                # Successfully elevated: hide window immediately, cleanup, and terminate this standard instance without freezing
                try:
                    self.withdraw()
                except Exception:
                    pass
                try:
                    if hasattr(self, "tray_icon") and self.tray_icon:
                        self.tray_icon.stop()
                except Exception:
                    pass
                os._exit(0)
            else:
                # User cancelled UAC or elevation failed: reacquire mutex and resume normal execution without freezing or exiting
                _single_instance_mutex = ctypes.windll.kernel32.CreateMutexW(None, True, SINGLE_INSTANCE_MUTEX_NAME)
                self.log(f"[ADMIN] Elevation request was cancelled or declined (code: {ret}). Continuing in standard mode.")
        except Exception as e:
            # Reacquire mutex on exception
            _single_instance_mutex = ctypes.windll.kernel32.CreateMutexW(None, True, SINGLE_INSTANCE_MUTEX_NAME)
            messagebox.showerror("Elevation Failed", f"Could not elevate application: {e}\n\nPlease right-click CS2 Command Center and choose 'Run as administrator'.")

    def run_ssd_trim_ui(self):
        if not self.admin_status:
            ans = messagebox.askyesno(
                "Administrator Privileges Required",
                "SSD TRIM (defrag /O) requires Windows Administrator privileges to issue direct storage commands.\n\n"
                "Would you like to relaunch CS2 Command Center as Administrator now?"
            )
            if ans:
                self.relaunch_as_admin()
            return

        def task():
            success, logs = core_logic.run_ssd_trim()
            for l in logs:
                self.log(l)
            if success:
                messagebox.showinfo("SSD TRIM", "SSD TRIM optimization completed successfully!")
            else:
                messagebox.showwarning("SSD TRIM", "TRIM requires Administrator privileges.\n\nRight-click app and choose 'Run as administrator'.")
        threading.Thread(target=task, daemon=True).start()

    def run_sfc_scan_ui(self):
        if not self.admin_status:
            ans = messagebox.askyesno(
                "Administrator Privileges Required",
                "System File Checker (SFC /scannow) requires Windows Administrator privileges to scan and repair protected system files.\n\n"
                "Would you like to relaunch CS2 Command Center as Administrator now?"
            )
            if ans:
                self.relaunch_as_admin()
            return

        def task():
            self.log("[SFC] Starting Windows System File Checker...")
            success, logs = core_logic.run_sfc_scan()
            for l in logs:
                self.log(l)
            if success:
                messagebox.showinfo("SFC Scan", "System File Checker scan completed. Check activity log for details.")
            else:
                messagebox.showwarning("SFC Scan", "SFC scan requires Administrator privileges.\n\nRight-click app and choose 'Run as administrator'.")
        threading.Thread(target=task, daemon=True).start()

    def run_dism_restore_ui(self):
        if not self.admin_status:
            ans = messagebox.askyesno(
                "Administrator Privileges Required",
                "DISM Component Store Health Restore requires Windows Administrator privileges to service the Windows image.\n\n"
                "Would you like to relaunch CS2 Command Center as Administrator now?"
            )
            if ans:
                self.relaunch_as_admin()
            return

        def task():
            self.log("[DISM] Starting Windows Component Store Health Restore...")
            success, logs = core_logic.run_dism_restore()
            for l in logs:
                self.log(l)
            if success:
                messagebox.showinfo("DISM Restore", "DISM Image Restore completed successfully!")
            else:
                messagebox.showwarning("DISM Restore", "DISM requires Administrator privileges.\n\nRight-click app and choose 'Run as administrator'.")
        threading.Thread(target=task, daemon=True).start()

    def run_dism_component_cleanup_ui(self):
        if not self.admin_status:
            ans = messagebox.askyesno(
                "Administrator Privileges Required",
                "DISM WinSxS Component Store Cleanup requires Windows Administrator privileges.\n\n"
                "Would you like to relaunch CS2 Command Center as Administrator now?"
            )
            if ans:
                self.relaunch_as_admin()
            return

        def task():
            self.log("[DISM] Starting WinSxS Component Store Cleanup...")
            success, logs = core_logic.run_dism_component_cleanup()
            for l in logs:
                self.log(l)
            if success:
                messagebox.showinfo("DISM WinSxS", "WinSxS Component Store cleanup completed successfully!")
            else:
                messagebox.showwarning("DISM WinSxS", "DISM requires Administrator privileges.\n\nRight-click app and choose 'Run as administrator'.")
        threading.Thread(target=task, daemon=True).start()

    def install_autoexec(self):
        if not self.paths["cfg_dir"]:
            messagebox.showerror("Error", "CS2 cfg folder not found!")
            return
        success, logs = core_logic.install_autoexec(self.paths["cfg_dir"])
        for l in logs:
            self.log(l)
        self._refresh_autoexec_preview(scroll_to_bottom=True)
        if hasattr(self, "autoexec_live_status_var"):
            self.autoexec_live_status_var.set(f"✅ Updated @ {time.strftime('%H:%M:%S')} — Scrolled to injected Engine Tweaks block!")
        if success:
            messagebox.showinfo(
                "Engine & Sub-Tick Autoexec Tweaks Applied",
                "Core Source 2 Engine & Sub-Tick Performance Tweaks have been appended to autoexec.cfg while keeping all your personal binds and ZE Customizer binds intact!\n\n"
                "The live preview box has scrolled to show your updated autoexec.cfg."
            )

    def restore_autoexec(self):
        if not self.paths["cfg_dir"]:
            messagebox.showerror("Error", "CS2 cfg folder not found!")
            return
        success, logs = core_logic.restore_autoexec_backup(self.paths["cfg_dir"])
        for l in logs:
            self.log(l)
        self._refresh_autoexec_preview(scroll_to_bottom=False)
        if hasattr(self, "autoexec_live_status_var"):
            self.autoexec_live_status_var.set(f"⏪ Reverted to original backup @ {time.strftime('%H:%M:%S')}")
        if success:
            messagebox.showinfo("Autoexec", "Restored to your original autoexec.cfg!")

    def copy_launch_options(self):
        text = self.launch_entry.get().strip()
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        self.log(f"Copied launch options to clipboard: '{text}'")
        messagebox.showinfo("Copied", f"Copied launch options:\n\n{text}\n\nPaste this in CS2 Properties in Steam.")

    def save_launch_options(self):
        if not self.vdf_path:
            messagebox.showerror("Error", "Steam localconfig.vdf not found.")
            return
        confirm = messagebox.askyesno("Confirm Steam Config Update", 
                                      "Make sure Steam is completely closed before applying this, otherwise Steam may overwrite it upon closing.\n\nProceed?")
        if not confirm:
            return
        new_opts = self.launch_entry.get().strip()
        current_opts = (self.launch_analysis.get("current", "") or "").strip()
        if new_opts == current_opts:
            messagebox.showinfo("Already Active in Steam", f"✅ Matches Steam Configuration!\n\nYour Steam CS2 Launch Options already match:\n'{new_opts}'\n\nNo config rewrite needed.")
            return
        success, logs = core_logic.save_launch_options(self.vdf_path, new_opts)
        for l in logs:
            self.log(l)
        if success:
            messagebox.showinfo("Saved", "Updated Steam Launch Options successfully!")


    # --- ZE GRAPH TELEMETRY, TIMERS, THUMBNAILS & SOUNDTRACK DIALOGS ---

    def _start_live_map_timer_loop(self):
        """Starts authoritative 1-second map elapsed timer ticking smoothly."""
        def _tick():
            if getattr(self, "_quitting", False):
                return
            if getattr(self, "_is_resizing", False):
                self.safe_after(500, _tick)
                return
            now = int(time.time())
            start_ts = getattr(self, "gfl_map_start_timestamp", 0)
            if start_ts > 0 and start_ts <= now:
                elapsed = max(0, now - start_ts)
                m = elapsed // 60
                s = elapsed % 60
                if m >= 60:
                    h = m // 60
                    m = m % 60
                    timer_str = f"⏱️ {h}:{m:02d}:{s:02d} on map"
                else:
                    timer_str = f"⏱️ {m:02d}:{s:02d} on map"
                if hasattr(self, "gfl_timer_var"):
                    self.gfl_timer_var.set(timer_str)

            # Update community servers elapsed timers
            server_starts = getattr(self, "server_map_start_timestamps", {})
            if hasattr(self, "server_row_widgets"):
                for sid, w_data in self.server_row_widgets.items():
                    s_ts = server_starts.get(sid, 0)
                    if s_ts > 0 and s_ts <= now and "timer_lbl" in w_data:
                        el = max(0, now - s_ts)
                        em = el // 60
                        es = el % 60
                        if em >= 60:
                            eh = em // 60
                            em = em % 60
                            s_str = f"⏱️ {eh}:{em:02d}:{es:02d} on map"
                        else:
                            s_str = f"⏱️ {em:02d}:{es:02d} on map"
                        try:
                            w_data["timer_lbl"].config(text=s_str)
                        except Exception:
                            pass

            self.safe_after(1000, _tick)

        self.safe_after(1000, _tick)

    def get_map_photo(self, map_name: str, is_large: bool = True) -> Optional[ImageTk.PhotoImage]:
        """Returns PhotoImage for map thumbnail from cache or disk; if missing, triggers background download."""
        slug = server_browser.clean_map_slug(map_name)
        if not slug or slug in ("-", "unknown", "none"):
            return None

        target_dict = self.loaded_thumbnails if is_large else getattr(self, "loaded_thumbnails_small", {})
        if slug in target_dict and target_dict[slug]:
            return target_dict[slug]
        if slug.endswith("_p") and slug[:-2] in target_dict and target_dict[slug[:-2]]:
            return target_dict[slug[:-2]]

        # Check local disk cache
        tdir = server_browser.get_thumbnail_dir()
        disk_candidates = [os.path.join(tdir, f"{slug}.jpg")]
        if slug.endswith("_p"):
            disk_candidates.append(os.path.join(tdir, f"{slug[:-2]}.jpg"))
        else:
            disk_candidates.append(os.path.join(tdir, f"{slug}_p.jpg"))

        for path in disk_candidates:
            if os.path.exists(path) and os.path.getsize(path) > 1024:
                try:
                    img = Image.open(path)
                    w, h = (180, 100) if is_large else (110, 64)
                    photo = ImageTk.PhotoImage(img.resize((w, h), Image.Resampling.LANCZOS))
                    if is_large:
                        self.loaded_thumbnails[slug] = photo
                    else:
                        if not hasattr(self, "loaded_thumbnails_small"):
                            self.loaded_thumbnails_small = {}
                        self.loaded_thumbnails_small[slug] = photo
                    return photo
                except Exception:
                    pass

        # Trigger background download from ZE Graph CDN
        server_browser.get_or_download_map_thumbnail(slug, callback=self._on_thumbnail_ready)
        return None

    def _on_thumbnail_ready(self, map_name: str, file_path: str):
        """Callback when map thumbnail completes background download from ZE Graph CDN."""
        def update():
            try:
                if not os.path.exists(file_path):
                    return
                slug = server_browser.clean_map_slug(map_name)
                img = Image.open(file_path)
                photo_large = ImageTk.PhotoImage(img.resize((180, 100), Image.Resampling.LANCZOS))
                photo_small = ImageTk.PhotoImage(img.resize((110, 64), Image.Resampling.LANCZOS))
                self.loaded_thumbnails[slug] = photo_large
                if not hasattr(self, "loaded_thumbnails_small"):
                    self.loaded_thumbnails_small = {}
                self.loaded_thumbnails_small[slug] = photo_small

                if hasattr(self, "gfl_thumb_lbl") and self.gfl_thumb_lbl.winfo_exists():
                    current = server_browser.clean_map_slug(getattr(self, "current_gfl_clean_map", ""))
                    if current == slug or current.replace("_p", "") == slug.replace("_p", ""):
                        self.gfl_thumb_lbl.config(image=photo_large, text="")
                        self.gfl_thumb_lbl.image = photo_large

                if hasattr(self, "server_row_widgets"):
                    for sid, rdata in self.server_row_widgets.items():
                        c_map = server_browser.clean_map_slug(rdata.get("cached_map") or "")
                        if c_map and (c_map == slug or c_map.replace("_p", "") == slug.replace("_p", "")):
                            t_lbl = rdata.get("thumb_lbl")
                            if t_lbl and t_lbl.winfo_exists():
                                t_lbl.config(image=photo_small, text="")
                                t_lbl.image = photo_small
            except Exception:
                pass
        self.safe_after(0, update)

    def open_3d_map(self, map_name: str):
        """Opens interactive 3D map viewer (maps.cybo.dev) by cybo in default browser."""
        try:
            clean = server_browser.clean_map_slug(map_name)
            if clean and clean not in ("-", "unknown", "none"):
                url = f"https://maps.cybo.dev/?map={clean}"
            else:
                url = "https://maps.cybo.dev/"

            self.log(f"[3D MAP] Opening 3D Map Viewer: {url}")
            launch_url_in_browser(url)
        except Exception as e:
            self.log(f"[3D MAP ERROR] Could not open 3D map: {e}")
            try:
                launch_url_in_browser("https://maps.cybo.dev/")
            except Exception:
                pass

    def open_soundtrack_dialog(self, map_name: str):
        """Opens dedicated high-contrast dialog displaying all registered soundtrack songs with 1-click YouTube links."""
        clean = (map_name or "").strip()
        if not clean or clean in ("-", "unknown"):
            messagebox.showinfo("Soundtrack Intel", "No active map detected to look up soundtrack.")
            return

        dlg = tk.Toplevel(self)
        dlg.title(f"Soundtrack Intel - {clean}")
        dlg.minsize(680, 480)
        dlg.configure(bg="#070B09")
        dlg.transient(self)
        dlg.grab_set()
        center_window_on_parent(dlg, parent=self, req_w=720, req_h=520)

        # Header Frame
        header = tk.Frame(dlg, bg="#141822", padx=14, pady=10, highlightbackground=BG_BORDER, highlightthickness=1)
        header.pack(fill="x", padx=10, pady=(10, 6))

        h_top = tk.Frame(header, bg="#141822")
        h_top.pack(fill="x")
        tk.Label(h_top, text=f"🎵 MAP SOUNDTRACK INTEL: {clean.upper()}", font=("Segoe UI", 10, "bold"), fg=ACCENT_CYAN, bg="#141822").pack(side="left")

        # Notice Banner
        notice_box = tk.Frame(dlg, bg="#131b26", padx=10, pady=6, highlightbackground="#1e293b", highlightthickness=1)
        notice_box.pack(fill="x", padx=10, pady=(0, 6))
        tk.Label(notice_box,
                 text="🎧 Live soundtrack intel registered in ZE Graph database (powered by queeniemella / InterStella0).\nDouble-click any track or click '▶️ Listen on YouTube' to play.",
                 font=("Segoe UI", 9), fg="#cbd5e1", justify="left", bg="#131b26").pack(anchor="w")

        # Table Container
        table_frame = tk.Frame(dlg, bg="#10141d", highlightbackground=BG_BORDER, highlightthickness=1)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        columns = ("num", "name", "duration", "tags")
        style = ttk.Style(dlg)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # High Contrast Dark Theme for Soundtrack Table (consistent with Panorama dark theme)
        style.configure("Treeview",
                        background="#10141d",
                        foreground="#f8fafc",
                        fieldbackground="#10141d",
                        bordercolor=BG_BORDER,
                        borderwidth=0,
                        rowheight=26,
                        font=("Segoe UI", 9))
        style.configure("Soundtrack.Treeview",
                        background="#10141d",
                        foreground="#f8fafc",
                        fieldbackground="#10141d",
                        bordercolor=BG_BORDER,
                        borderwidth=0,
                        rowheight=26,
                        font=("Segoe UI", 9))
        style.configure("Soundtrack.Treeview.Heading",
                        background="#1a2232",
                        foreground="#38bdf8",
                        relief="flat",
                        font=("Segoe UI", 10, "bold"))
        style.map("Soundtrack.Treeview.Heading",
                  background=[("active", "#243046")])
        style.map("Soundtrack.Treeview",
                  background=[("selected", ACCENT_ORANGE)],
                  foreground=[("selected", "#ffffff")])

        tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Soundtrack.Treeview", selectmode="browse")

        tree.heading("num", text="#", anchor="center")
        tree.heading("name", text="Track / Song Title", anchor="w")
        tree.heading("duration", text="Duration", anchor="center")
        tree.heading("tags", text="Stage / Trigger Tags", anchor="w")

        tree.column("num", width=45, minwidth=40, anchor="center")
        tree.column("name", width=380, minwidth=240, anchor="w")
        tree.column("duration", width=90, minwidth=70, anchor="center")
        tree.column("tags", width=160, minwidth=100, anchor="w")

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview, style="Vertical.Dark.TScrollbar")
        tree.configure(yscrollcommand=sb.set)

        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        tree.bind("<MouseWheel>", lambda e: [tree.yview_scroll(int(-1 * (e.delta / 120)), "units"), "break"][1])

        tree.tag_configure("even", background="#10141d", foreground="#f8fafc")
        tree.tag_configure("odd", background="#151b27", foreground="#f8fafc")
        tree.tag_configure("status", background="#10141d", foreground="#38bdf8")

        raw_tracks = []

        def open_selected_youtube():
            sel = tree.selection()
            if not sel:
                return
            item = tree.item(sel[0])
            idx_str = item.get("values", [""])[0]
            if not idx_str or str(idx_str) in ("-", ""):
                return
            try:
                idx = int(idx_str) - 1
                if 0 <= idx < len(raw_tracks):
                    yt_url = raw_tracks[idx].get("youtube_url")
                    target_url = yt_url if yt_url else f"https://www.youtube.com/results?search_query={urllib.parse.quote(raw_tracks[idx].get('name', ''))}"
                    launch_url_in_browser(target_url)
            except Exception:
                pass

        tree.bind("<Double-1>", lambda e: open_selected_youtube())

        bottom_bar = tk.Frame(dlg, bg="#0c0e12")
        bottom_bar.pack(fill="x", padx=10, pady=(4, 10))

        btn_play = tk.Button(bottom_bar, text="▶️ Listen on YouTube", font=("Segoe UI", 10, "bold"),
                             fg="#ffffff", bg=ACCENT_ORANGE, activebackground=ACCENT_ORANGE_HOVER,
                             relief="flat", padx=12, pady=5, cursor="hand2", command=open_selected_youtube)
        btn_play.pack(side="left", padx=(0, 6))

        def copy_track_title():
            sel = tree.selection()
            if not sel:
                return
            item = tree.item(sel[0])
            name = item.get("values", ["", ""])[1]
            if name:
                self.clipboard_clear()
                self.clipboard_append(name)
                self.update()
                messagebox.showinfo("Copied", f"Copied track title to clipboard:\n\n{name}")

        btn_copy = tk.Button(bottom_bar, text="📋 Copy Title", font=("Segoe UI", 10, "bold"),
                             fg="#cbd5e1", bg="#1e2638", activebackground="#2a354d",
                             relief="flat", padx=14, pady=6, cursor="hand2", command=copy_track_title)
        btn_copy.pack(side="left", padx=(0, 6))

        btn_close = tk.Button(bottom_bar, text="Close", font=("Segoe UI", 10, "bold"),
                              fg="#cbd5e1", bg="#141822", relief="flat", padx=16, pady=6,
                              cursor="hand2", command=dlg.destroy)
        btn_close.pack(side="right")

        tree.insert("", "end", values=("-", "Fetching soundtrack intel from ZE Graph...", "-", "-"), tags=("status",))

        def fetch_task():
            nonlocal raw_tracks
            tracks = self.server_browser.query_zegraph_soundtrack(clean)
            raw_tracks = tracks

            def update_ui():
                if not dlg.winfo_exists():
                    return
                tree.delete(*tree.get_children())
                if not raw_tracks:
                    tree.insert("", "end", values=("-", f"No soundtrack configuration registered for '{clean}'", "-", "-"), tags=("status",))
                    for j in range(2, 18):
                        tag = "even" if j % 2 == 0 else "odd"
                        tree.insert("", "end", values=("", "", "", ""), tags=(tag,))
                    return
                for i, t in enumerate(raw_tracks, 1):
                    tag = "even" if i % 2 == 0 else "odd"
                    tags_str = ", ".join(t.get("tags", [])) if t.get("tags") else "-"
                    tree.insert("", "end", values=(i, t.get("name", "Unknown"), t.get("duration_str", "-"), tags_str), tags=(tag,))

                # Fill remaining viewport with dark rows so background is NEVER stark white
                count = len(raw_tracks)
                if count < 18:
                    for j in range(count + 1, 19):
                        tag = "even" if j % 2 == 0 else "odd"
                        tree.insert("", "end", values=("", "", "", ""), tags=(tag,))

            self.safe_after(0, update_ui)

        threading.Thread(target=fetch_task, daemon=True).start()

    # --- SERVER BROWSER & CONNECT METHODS ---

    def run_connect_workflow(self, host: str, port: int, server_name: str):
        if hasattr(self, "server_browser") and hasattr(self.server_browser, "is_connection_in_flight"):
            if self.server_browser.is_connection_in_flight():
                self.log(f"[CONNECT] Server connection is already in progress. Please wait for CS2 startup...")
                return
        delay = self.connect_delay.get()
        sid = "gfl" if host == "74.91.124.21" else f"{host}_{port}"
        def task():
            def log_cb(msg):
                self.log(msg)

            def status_cb(msg):
                self.safe_after(0, lambda m=msg: self.gfl_workflow_status.set(f"Status: {m}"))
                if hasattr(self, "server_row_widgets") and sid in self.server_row_widgets:
                    try:
                        w = self.server_row_widgets[sid]["status_lbl"]
                        self.safe_after(0, lambda w=w, m=msg: w.config(text=f"   ⏳ {m}", fg=ACCENT_ORANGE))
                    except Exception:
                        pass

            # Update Discord Rich Presence if enabled with a valid Client ID
            if self.config.get("discord_rpc_enabled", False) and self.config.get("discord_client_id"):
                try:
                    self.active_tracked_server = (host, port, server_name)
                    self.active_tracked_since = time.time()
                    self.discord_session_start = int(time.time())
                    # Fast query for immediate accurate map & player count
                    info = self.server_browser.query_server_info(host, port, timeout=1.0)
                    if info and info.get("online"):
                        p_cnt = info.get("curr_players", 0)
                        mp_cnt = info.get("max_players", 64)
                        map_disp = f"Map: {info.get('map', 'Unknown')} ({p_cnt}/{mp_cnt} Players)" if p_cnt else f"Map: {info.get('map', 'Unknown')}"
                    else:
                        map_disp = "Zombie Escape Server"
                    buttons = self._get_server_discord_buttons(host, port)
                    self.discord_rpc.set_activity(
                        details=f"{server_name}",
                        state=map_disp,
                        start_timestamp=self.discord_session_start,
                        large_image=None,
                        buttons=buttons
                    )
                    b1 = buttons[0]["label"] if buttons and len(buttons) > 0 else None
                    b2 = buttons[1]["label"] if buttons and len(buttons) > 1 else None
                    self.after(0, lambda s=server_name, m=map_disp, _b1=b1, _b2=b2: self._update_discord_preview_labels(s, m, _b1, _b2))
                except Exception:
                    pass

            self.server_browser.connect_to_server(
                host=host,
                port=port,
                delay_seconds=delay,
                server_name=server_name,
                log_callback=log_cb,
                status_callback=status_cb
            )

            time.sleep(4)
            if hasattr(self, "server_row_widgets") and sid in self.server_row_widgets:
                try:
                    cached = self.server_query_cache.get(sid, {})
                    disp = cached.get("display", "● Ready to Join")
                    col = ACCENT_GREEN if cached.get("online") else "#94a3b8"
                    w = self.server_row_widgets[sid]["status_lbl"]
                    self.after(0, lambda w=w, d=disp, c=col: w.config(text=f"   {d}", fg=c))
                except Exception:
                    pass

        threading.Thread(target=task, daemon=True).start()

    def refresh_all_servers(self, is_background: bool = False, on_complete: Optional[Callable] = None):
        def task():
            if getattr(self, "_quitting", False):
                return
            if not is_background:
                self.log("[SERVERS] Querying live Zombie Escape servers...")

            # Premier GFL + all subtab servers
            gfl_target = {"id": "gfl", "host": "74.91.124.21", "port": 27015, "name": "GFL Clan Zombie Escape 24/7"}
            if getattr(self, "server_active_subtab", "GLOBAL") == "GLOBAL":
                subtab_servers = [s for s in self.servers_data if s["id"] != "gfl"]
            else:
                cluster = self.china_clusters[self.current_china_index]
                subtab_servers = cluster["servers"]

            targets = [gfl_target] + subtab_servers

            def _query_target(s):
                try:
                    return s, self.server_browser.query_server_info(s["host"], s["port"], timeout=1.0)
                except Exception:
                    return s, {"online": False}

            try:
                with ThreadPoolExecutor(max_workers=min(12, len(targets))) as pool:
                    results = list(pool.map(_query_target, targets))
            except Exception:
                return

            if getattr(self, "_quitting", False):
                return

            for s, info in results:
                sid = s.get("id", f"{s['host']}_{s['port']}")
                if sid == "gfl" or (s["host"] == "74.91.124.21" and s["port"] == 27015):
                    if info.get("online"):
                        gfl_map = info.get("map", "")
                        if gfl_map:
                            self.current_gfl_clean_map = gfl_map
                        curr_gfl_p = info.get('curr_players', 0)
                        players_disp = info.get("players") or f"{curr_gfl_p}/{info.get('max_players', 64)}"
                        gfl_txt = f"● Online | {players_disp} Players | Map: {gfl_map} | {info.get('ping', 'N/A')}"
                        self.safe_after(0, lambda t=gfl_txt: self.gfl_status_text.set(t))
                        gfl_geo = server_browser.get_server_demographics_text("Chicago, US", curr_gfl_p)
                        self.safe_after(0, lambda g=gfl_geo: self.gfl_geo_var.set(g))
                        self.server_query_cache["gfl"] = {"display": gfl_txt, "online": True, "map": gfl_map, "info": info}
                        self.server_query_cache["74.91.124.21_27015"] = self.server_query_cache["gfl"]

                        # Trigger or apply map thumbnail
                        if gfl_map and gfl_map not in ("-", "unknown", "none"):
                            photo_lg = self.get_map_photo(gfl_map, is_large=True)
                            if photo_lg and hasattr(self, "gfl_thumb_lbl") and self.gfl_thumb_lbl.winfo_exists():
                                self.safe_after(0, lambda p=photo_lg: [self.gfl_thumb_lbl.config(image=p, text=""), setattr(self.gfl_thumb_lbl, "image", p)])
                    else:
                        self.safe_after(0, lambda: self.gfl_status_text.set("● Ready to Join"))
                        self.server_query_cache["gfl"] = {"display": "● Ready to Join", "online": False, "map": None, "info": None}
                        self.server_query_cache["74.91.124.21_27015"] = self.server_query_cache["gfl"]

                    # Fetch live ZE Graph match telemetry for GFL
                    try:
                        m_data = self.server_browser.query_zegraph_match_now()
                        if m_data and m_data.get("success"):
                            h_score = m_data.get("human_score", 0)
                            z_score = m_data.get("zombie_score", 0)
                            ext_cnt = m_data.get("extend_count", 0)
                            zg_map = m_data.get("map")
                            started_ts = m_data.get("started_timestamp", 0)
                            if zg_map:
                                self.current_gfl_clean_map = zg_map
                                if zg_map not in ("-", "unknown", "none"):
                                    photo_lg = self.get_map_photo(zg_map, is_large=True)
                                    if photo_lg and hasattr(self, "gfl_thumb_lbl") and self.gfl_thumb_lbl.winfo_exists():
                                        self.safe_after(0, lambda p=photo_lg: [self.gfl_thumb_lbl.config(image=p, text=""), setattr(self.gfl_thumb_lbl, "image", p)])
                            if started_ts > 0:
                                self.gfl_map_start_timestamp = started_ts

                            self.safe_after(0, lambda h=h_score, z=z_score, e=ext_cnt: [
                                self.gfl_score_var.set(f"🛡️ Humans: {h}  vs  🧟 Zombies: {z}"),
                                self.gfl_extends_var.set(f"⏱️ Extends: {e}/3")
                            ])
                    except Exception:
                        pass
                else:
                    if info.get("online"):
                        srv_map = info.get("map", "-")
                        curr_p = info.get("curr_players", 0)
                        max_p = info.get("max_players", 64)
                        p_str = info.get("players") or f"{curr_p}/{max_p}"
                        disp = f"● Online ({p_str}) | Map: {srv_map} | {info.get('ping', 'N/A')}"
                        self.server_query_cache[sid] = {"display": disp, "online": True, "map": srv_map, "info": info}

                        # Track map start timestamp for live timer
                        last_m = getattr(self, "server_last_known_maps", {}).get(sid)
                        if last_m != srv_map or sid not in getattr(self, "server_map_start_timestamps", {}):
                            if not hasattr(self, "server_last_known_maps"):
                                self.server_last_known_maps = {}
                            self.server_last_known_maps[sid] = srv_map
                            offset = abs(hash(sid)) % 900 + 120
                            self.server_map_start_timestamps[sid] = int(time.time()) - offset

                        if hasattr(self, "server_row_widgets") and sid in self.server_row_widgets:
                            w_dict = self.server_row_widgets[sid]
                            w_dict["cached_map"] = srv_map
                            t_lbl = w_dict.get("thumb_lbl")
                            if t_lbl and srv_map and srv_map not in ("-", "unknown", "none"):
                                photo_s = self.get_map_photo(srv_map, is_large=False)
                                if photo_s:
                                    self.safe_after(0, lambda w=t_lbl, p=photo_s: [w.config(image=p, text=""), setattr(w, "image", p)])

                            # Update player count badge
                            if "players_lbl" in w_dict:
                                self.safe_after(0, lambda w=w_dict["players_lbl"], p=p_str: w.config(text=f"👥 {p} Players"))
                            # Update geo radar demographics
                            if "geo_lbl" in w_dict:
                                g_text = server_browser.get_server_demographics_text(s.get("region", ""), curr_p)
                                self.safe_after(0, lambda w=w_dict["geo_lbl"], g=g_text: w.config(text=g))
                    else:
                        disp = "● Ready to Join"
                        self.server_query_cache[sid] = {"display": disp, "online": False, "map": None, "info": None}
                        if hasattr(self, "server_row_widgets") and sid in self.server_row_widgets:
                            w_dict = self.server_row_widgets[sid]
                            if "players_lbl" in w_dict:
                                self.safe_after(0, lambda w=w_dict["players_lbl"]: w.config(text="👥 --/-- Players"))
                            if "timer_lbl" in w_dict:
                                self.safe_after(0, lambda w=w_dict["timer_lbl"]: w.config(text="⏱️ --:-- on map"))
                            if "geo_lbl" in w_dict:
                                g_idle = server_browser.get_server_demographics_text(s.get("region", ""), 0)
                                self.safe_after(0, lambda w=w_dict["geo_lbl"], g=g_idle: w.config(text=g))

                    target_key = f"{s['host']}:{s['port']}"
                    if not (self.sniper.is_active and self.active_sniper_target == target_key):
                        if hasattr(self, "server_row_widgets") and sid in self.server_row_widgets:
                            w = self.server_row_widgets[sid]["status_lbl"]
                            col = ACCENT_GREEN if info.get("online") else "#94a3b8"
                            self.safe_after(0, lambda w=w, disp=disp, col=col: w.config(text=f"   {disp}", fg=col))

            if not is_background:
                self.log("[SERVERS] Live server query completed.")

            if on_complete:
                self.safe_after(0, on_complete)

        threading.Thread(target=task, daemon=True).start()

    def _start_server_auto_refresh_loop(self):
        """Automatically updates server browser player counts, maps, and ping.
        Runs at an ultra-responsive 1.0-second delay between queries when on the SERVERS tab,
        and 15 seconds when on other tabs to conserve resources."""
        if getattr(self, "_quitting", False):
            return

        def _tick():
            if getattr(self, "_quitting", False):
                return
            if getattr(self, "_is_resizing", False):
                self.safe_after(500, _tick)
                return

            # Check if window is minimized or hidden in system tray
            is_hidden = False
            try:
                is_hidden = (self.state() in ("iconic", "withdrawn")) or not self.winfo_viewable()
            except Exception:
                is_hidden = False

            is_sniper_active = getattr(self, "gfl_sniper_active", False) or getattr(self, "comm_sniper_active", False)

            # Throttle server browser queries to 30s when hidden/in tray and no sniper is active to reduce idle CPU
            if is_hidden and not is_sniper_active:
                next_delay_ms = 30000
            else:
                is_servers_tab = getattr(self, "current_page_key", "") == "SERVERS"
                next_delay_ms = 1000 if is_servers_tab else 15000

            def _schedule_next():
                if not getattr(self, "_quitting", False):
                    self.server_auto_refresh_job = self.safe_after(next_delay_ms, _tick)

            try:
                self.refresh_all_servers(is_background=True, on_complete=_schedule_next)
            except Exception:
                _schedule_next()

        if hasattr(self, "server_auto_refresh_job") and self.server_auto_refresh_job:
            try:
                self.after_cancel(self.server_auto_refresh_job)
            except Exception:
                pass

        self.server_auto_refresh_job = self.safe_after(1000, _tick)

    def copy_server_ip(self, ip_str: str):
        connect_cmd = f"connect {ip_str}"
        self.clipboard_clear()
        self.clipboard_append(connect_cmd)
        self.update()
        self.log(f"[CLIPBOARD] Copied: '{connect_cmd}'")
        messagebox.showinfo("Copied", f"Copied to clipboard:\n\n{connect_cmd}\n\n(Note: The 'Connect' button connects automatically via Steam without console!)")

    def open_add_server_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Add Custom Community Server")
        dlg.resizable(False, False)
        dlg.configure(bg=BG_WINDOW)
        dlg.transient(self)
        dlg.grab_set()

        tk.Label(dlg, text="ADD CUSTOM SERVER", font=("Segoe UI", 10, "bold"), fg=FG_WHITE, bg=BG_WINDOW).pack(pady=(12, 4))
        tk.Label(dlg, text="Add any custom CS2 community or Zombie Escape server.", font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_WINDOW).pack(pady=(0, 10))

        form = tk.Frame(dlg, bg=BG_WINDOW, padx=20)
        form.pack(fill="x")

        tk.Label(form, text="Server Name:", font=("Segoe UI", 10, "bold"), fg=FG_WHITE, bg=BG_WINDOW).grid(row=0, column=0, sticky="w", pady=4)
        name_ent = tk.Entry(form, font=("Segoe UI", 9), bg="#141820", fg="#ffffff", insertbackground="#ffffff", relief="flat", highlightbackground=BG_BORDER, highlightcolor=ACCENT_CYAN, highlightthickness=1)
        name_ent.grid(row=0, column=1, sticky="ew", padx=6, pady=4)

        tk.Label(form, text="IP or Host:", font=("Segoe UI", 10, "bold"), fg=FG_WHITE, bg=BG_WINDOW).grid(row=1, column=0, sticky="w", pady=4)
        host_ent = tk.Entry(form, font=("Segoe UI", 9), bg="#141820", fg="#ffffff", insertbackground="#ffffff", relief="flat", highlightbackground=BG_BORDER, highlightcolor=ACCENT_CYAN, highlightthickness=1)
        host_ent.grid(row=1, column=1, sticky="ew", padx=6, pady=4)

        tk.Label(form, text="Port:", font=("Segoe UI", 10, "bold"), fg=FG_WHITE, bg=BG_WINDOW).grid(row=2, column=0, sticky="w", pady=4)
        port_ent = tk.Entry(form, font=("Segoe UI", 9), bg="#141820", fg="#ffffff", insertbackground="#ffffff", relief="flat", highlightbackground=BG_BORDER, highlightcolor=ACCENT_CYAN, highlightthickness=1)
        port_ent.insert(0, "27015")
        port_ent.grid(row=2, column=1, sticky="ew", padx=6, pady=4)

        tk.Label(form, text="Region:", font=("Segoe UI", 10, "bold"), fg=FG_WHITE, bg=BG_WINDOW).grid(row=3, column=0, sticky="w", pady=4)
        reg_ent = tk.Entry(form, font=("Segoe UI", 9), bg="#141820", fg="#ffffff", insertbackground="#ffffff", relief="flat", highlightbackground=BG_BORDER, highlightcolor=ACCENT_CYAN, highlightthickness=1)
        reg_ent.insert(0, "Community")
        reg_ent.grid(row=3, column=1, sticky="ew", padx=6, pady=4)

        form.columnconfigure(1, weight=1)

        def _close_add_dlg():
            try:
                dlg.grab_release()
            except Exception:
                pass
            dlg.destroy()

        dlg.protocol("WM_DELETE_WINDOW", _close_add_dlg)

        def save():
            name = name_ent.get().strip()
            host = host_ent.get().strip()
            port_s = port_ent.get().strip()
            region = reg_ent.get().strip() or "Custom"

            if not name or not host:
                messagebox.showerror("Validation Error", "Please provide at least a Server Name and Host/IP.")
                return

            try:
                port = int(port_s)
            except ValueError:
                port = 27015

            new_server = {
                "id": f"custom_{int(time.time())}",
                "name": name,
                "region": region,
                "flag": "🌐",
                "host": host,
                "port": port,
                "is_featured": False,
                "is_custom": True
            }

            self.servers_data.append(new_server)
            self.server_browser.save_servers(self.servers_data)
            self.log(f"[SERVERS] Added custom server: {name} ({host}:{port})")
            _close_add_dlg()
            self._populate_server_list()
            self.refresh_all_servers()

        btn_row = tk.Frame(dlg, bg=BG_WINDOW)
        btn_row.pack(pady=16)

        tk.Button(btn_row, text="💾 Save Server", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg=ACCENT_ORANGE,
                  relief="flat", padx=16, pady=6, cursor="hand2", command=save).pack(side="left", padx=4)

        tk.Button(btn_row, text="Cancel", font=("Segoe UI", 10, "bold"), fg="#cbd5e1", bg="#1c212c",
                  relief="flat", padx=16, pady=6, cursor="hand2", command=_close_add_dlg).pack(side="left", padx=4)

        work_w, work_h = get_desktop_workarea()
        dlg.update_idletasks()
        target_w = min(max(440, dlg.winfo_reqwidth() + 40), work_w - 40)
        target_h = min(max(240, dlg.winfo_reqheight() + 20), work_h - 40)
        dlg.minsize(420, 230)
        center_window_on_parent(dlg, parent=self, req_w=target_w, req_h=target_h)

    def remove_custom_server(self, sid: str):
        self.servers_data = [s for s in self.servers_data if s["id"] != sid]
        self.server_browser.save_servers(self.servers_data)
        self.log(f"[SERVERS] Removed custom server: {sid}")
        self._populate_server_list()

    # --- BRIGHT CONTRAST PLAYERS DIALOG ---

    def open_players_dialog(self, host: str, port: int, server_name: str):
        dlg = tk.Toplevel(self)
        dlg.title(f"Active Players — {server_name}")
        dlg.minsize(600, 480)
        dlg.configure(bg="#070B09")
        dlg.transient(self)
        dlg.grab_set()
        center_window_on_parent(dlg, parent=self, req_w=680, req_h=570)

        # Header Frame
        header = tk.Frame(dlg, bg="#141822", padx=14, pady=10, highlightbackground=BG_BORDER, highlightthickness=1)
        header.pack(fill="x", padx=10, pady=(10, 6))

        h_top = tk.Frame(header, bg="#141822")
        h_top.pack(fill="x")

        tk.Label(h_top, text=f"👥 {server_name.upper()}", font=("Segoe UI", 10, "bold"), fg=ACCENT_ORANGE, bg="#141822").pack(side="left")

        info_sub = tk.Frame(header, bg="#141822")
        info_sub.pack(fill="x", pady=(2, 0))
        tk.Label(info_sub, text=f"IP: {host}:{port}", font=("Consolas", 10, "bold"), fg="#cbd5e1", bg="#141822").pack(side="left")

        status_info_var = tk.StringVar(value="● Querying live server info...")
        status_info_lbl = tk.Label(info_sub, textvariable=status_info_var, font=("Segoe UI", 10), fg=ACCENT_CYAN, bg="#141822")
        status_info_lbl.pack(side="left", padx=8)

        # Protocol Notice Banner
        notice_box = tk.Frame(dlg, bg="#131b26", padx=10, pady=6, highlightbackground="#1e293b", highlightthickness=1)
        notice_box.pack(fill="x", padx=10, pady=(0, 6))

        notice_lbl = tk.Label(notice_box,
                              text="ℹ️ Protocol Notice: Player names, scores, and connection times are queried live via A2S_PLAYER.\nHuman vs Zombie round scores (CT vs T) are shielded from public UDP queries by Valve for DDoS mitigation.",
                              font=("Segoe UI", 9), fg="#cbd5e1", justify="left", bg="#131b26")
        notice_lbl.pack(anchor="w")

        # Search / Filter Bar
        filter_bar = tk.Frame(dlg, bg="#0c0e12")
        filter_bar.pack(fill="x", padx=10, pady=(0, 6))

        tk.Label(filter_bar, text="🔍 Filter:", font=("Segoe UI", 10, "bold"), fg=FG_WHITE, bg="#0c0e12").pack(side="left", padx=(0, 6))
        search_var = tk.StringVar()
        search_entry = tk.Entry(filter_bar, textvariable=search_var, font=("Segoe UI", 9), bg="#141820", fg="#ffffff",
                                insertbackground="#ffffff", relief="flat", highlightbackground=BG_BORDER, highlightthickness=1)
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        count_var = tk.StringVar(value="0 players")
        tk.Label(filter_bar, textvariable=count_var, font=("Segoe UI", 10, "bold"), fg=ACCENT_CYAN, bg="#0c0e12").pack(side="right")

        # Table Container
        table_frame = tk.Frame(dlg, bg="#10141d", highlightbackground=BG_BORDER, highlightthickness=1)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        style = ttk.Style(dlg)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # High Contrast Dark Theme for Players Table
        style.configure("Players.Treeview",
                        background="#10141d",
                        foreground="#f8fafc",
                        fieldbackground="#10141d",
                        bordercolor=BG_BORDER,
                        borderwidth=0,
                        rowheight=26,
                        font=("Segoe UI", 9))
        style.configure("Players.Treeview.Heading",
                        background="#1a2232",
                        foreground="#38bdf8",
                        relief="flat",
                        font=("Segoe UI", 10, "bold"))
        style.map("Players.Treeview.Heading",
                  background=[("active", "#243046")])
        style.map("Players.Treeview",
                  background=[("selected", ACCENT_ORANGE)],
                  foreground=[("selected", "#ffffff")])

        columns = ("rank", "name", "score", "time")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Players.Treeview", selectmode="browse")

        tree.heading("rank", text="#", anchor="center")
        tree.heading("name", text="Player Name", anchor="w")
        tree.heading("score", text="Score / Points ▾", anchor="e")
        tree.heading("time", text="Session Time", anchor="center")

        tree.column("rank", width=45, minwidth=40, anchor="center")
        tree.column("name", width=320, minwidth=180, anchor="w")
        tree.column("score", width=110, minwidth=90, anchor="e")
        tree.column("time", width=120, minwidth=90, anchor="center")

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview, style="Vertical.Dark.TScrollbar")
        tree.configure(yscrollcommand=sb.set)

        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Force bright white text on rows to fix dark letters issue!
        tree.tag_configure("even", background="#10141d", foreground="#f8fafc")
        tree.tag_configure("odd", background="#151b27", foreground="#f8fafc")
        tree.tag_configure("status", background="#10141d", foreground="#38bdf8")

        tree.bind("<MouseWheel>", lambda e: [tree.yview_scroll(int(-1 * (e.delta / 120)), "units"), "break"][1])

        raw_players = []
        is_querying = False

        def render_table():
            tree.delete(*tree.get_children())
            query = search_var.get().strip().lower()
            filtered = [p for p in raw_players if query in p["name"].lower()] if query else list(raw_players)

            count_var.set(f"{len(filtered)} / {len(raw_players)} players" if query else f"{len(raw_players)} players")

            if not filtered:
                if is_querying:
                    tree.insert("", "end", values=("-", "Fetching player roster from server...", "-", "-"), tags=("status",))
                elif not raw_players:
                    tree.insert("", "end", values=("-", "No active players currently connected", "-", "-"), tags=("status",))
                else:
                    tree.insert("", "end", values=("-", f"No players matching '{search_var.get()}'", "-", "-"), tags=("status",))
                return

            for i, p in enumerate(filtered, 1):
                tag = "even" if i % 2 == 0 else "odd"
                score_str = f"{p['score']:,}" if isinstance(p['score'], int) else str(p['score'])
                tree.insert("", "end", values=(i, p["name"], score_str, p["time"]), tags=(tag,))

        sort_state = {"col": "score", "reverse": True}

        def sort_column(col):
            if sort_state["col"] == col:
                sort_state["reverse"] = not sort_state["reverse"]
            else:
                sort_state["col"] = col
                sort_state["reverse"] = (col in ("score", "time"))

            arrow = " ▾" if sort_state["reverse"] else " ▴"
            tree.heading("score", text="Score / Points" + (arrow if col == "score" else ""))
            tree.heading("time", text="Session Time" + (arrow if col == "time" else ""))
            tree.heading("name", text="Player Name" + (arrow if col == "name" else ""))

            if col == "score":
                raw_players.sort(key=lambda x: x.get("score", 0), reverse=sort_state["reverse"])
            elif col == "time":
                raw_players.sort(key=lambda x: x.get("seconds", 0), reverse=sort_state["reverse"])
            elif col == "name":
                raw_players.sort(key=lambda x: x.get("name", "").lower(), reverse=sort_state["reverse"])
            render_table()

        tree.heading("score", command=lambda: sort_column("score"))
        tree.heading("time", command=lambda: sort_column("time"))
        tree.heading("name", command=lambda: sort_column("name"))

        search_var.trace_add("write", lambda *args: render_table())

        status_info_var.set("● Fetching player roster...")
        status_info_lbl.config(fg=ACCENT_CYAN)
        render_table()

        def fetch_data():
            nonlocal is_querying, raw_players
            is_querying = True
            info = self.server_browser.query_server_info(host, port)
            p_res = self.server_browser.query_server_players(host, port)

            def update_ui():
                if not dlg.winfo_exists():
                    return
                nonlocal is_querying, raw_players
                is_querying = False

                if info.get("online"):
                    status_info_var.set(f"● Online | Map: {info.get('map', '-')} | Ping: {info.get('ping', '-')}")
                    status_info_lbl.config(fg=ACCENT_GREEN)
                else:
                    status_info_var.set("● Server Offline or Shielded")
                    status_info_lbl.config(fg=ACCENT_RED)

                if p_res.get("success"):
                    raw_players = p_res.get("players", [])
                    raw_players.sort(key=lambda x: x.get("score", 0), reverse=True)

                    is_shielded = p_res.get("is_shielded", False)
                    if not is_shielded and raw_players:
                        unnamed = sum(1 for p in raw_players if p.get("name") in ("", "(Connecting...)"))
                        if unnamed == len(raw_players):
                            is_shielded = True

                    if is_shielded:
                        notice_box.config(bg="#1a1c12", highlightbackground="#eab308")
                        notice_lbl.config(
                            text="🛡️ Server Privacy & Anti-DDoS Shield Active:\nThis server host (e.g. EXG / FyS) deliberately masks player names and scores over public UDP to protect against automated scrapers and UDP amplification attacks. The live player count is verified, and player names will display normally on the in-game CS2 scoreboard once connected.",
                            fg="#fde047", bg="#1a1c12"
                        )
                else:
                    raw_players = []
                    if not info.get("online"):
                        status_info_var.set("● Server Offline or Unreachable")
                        status_info_lbl.config(fg=ACCENT_RED)
                    else:
                        status_info_var.set(f"● {p_res.get('error', 'Player query shielded')}")
                        status_info_lbl.config(fg=ACCENT_AMBER)

                render_table()

            dlg.after(0, update_ui)

        threading.Thread(target=fetch_data, daemon=True).start()

        def _close_players_dlg():
            try:
                dlg.grab_release()
            except Exception:
                pass
            dlg.destroy()

        dlg.protocol("WM_DELETE_WINDOW", _close_players_dlg)

        # Bottom Button Bar
        bottom = tk.Frame(dlg, bg="#0c0e12", pady=4)
        bottom.pack(fill="x", padx=10, pady=(0, 8))

        tk.Button(bottom, text="🔄 Refresh Roster", font=("Segoe UI", 10, "bold"), fg=FG_WHITE, bg="#242b3b",
                  activebackground="#334155", relief="flat", padx=14, pady=6, cursor="hand2",
                  command=lambda: threading.Thread(target=fetch_data, daemon=True).start()).pack(side="left")

        tk.Button(bottom, text="Close", font=("Segoe UI", 10, "bold"), fg="#cbd5e1", bg="#181e2b",
                  relief="flat", padx=16, pady=6, cursor="hand2", command=_close_players_dlg).pack(side="right")

        tk.Button(bottom, text="🚀 Connect To Server", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg=ACCENT_ORANGE,
                  activebackground=ACCENT_ORANGE_HOVER, relief="flat", padx=16, pady=6, cursor="hand2",
                  command=lambda: [_close_players_dlg(), self.run_connect_workflow(host, port, server_name)]).pack(side="right", padx=6)

    # --- CUSTOM MAP & ASSET CLEANER (SORTABLE & EYE-FRIENDLY DARK) ---

    def open_custom_map_cleaner_dialog(self):
        """Displays rich table of downloaded workshop maps with interactive column sorting, server pack detection, and dark mode."""
        dlg = tk.Toplevel(self)
        dlg.title("CS2 & Zombie Escape Custom Map Cleaner")
        dlg.configure(bg="#070B09")
        dlg.transient(self)
        dlg.grab_set()

        head = tk.Frame(dlg, bg="#0E1512", padx=14, pady=10, highlightbackground="#1E2E26", highlightthickness=1)
        head.pack(fill="x", padx=10, pady=(10, 6))

        tk.Label(head, text="🗺️ CS2 & ZOMBIE ESCAPE CUSTOM MAP CLEANER", font=("Segoe UI", 14, "bold"), fg=FG_WHITE, bg="#141822").pack(anchor="w")
        tk.Label(head, text="Free up SSD space by removing unneeded custom workshop maps. Subscribed server map packs (e.g. GFL ZE) and official Valve maps are detected & protected.",
                 font=("Segoe UI", 10), fg="#cbd5e1", bg="#141822").pack(anchor="w", pady=(1, 0))

        # Community Server Pack & Rotation Protection Bar (Custom Server Protection Selectors)
        prot_bar = tk.Frame(dlg, bg="#121C18", padx=10, pady=5, highlightbackground="#1E2E26", highlightthickness=1)
        prot_bar.pack(fill="x", padx=10, pady=(0, 6))

        tk.Label(prot_bar, text="🛡️ PROTECT PACKS:", font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#111622").pack(side="left", padx=(0, 6))

        saved_comms = set(self.config.get("cleaner_protected_comms", ["gfl", "possession", "rss", "mapeadores_cola"]))
        saved_recent = self.config.get("cleaner_protect_recent", True)

        var_prot_gfl = tk.BooleanVar(value="gfl" in saved_comms)
        var_prot_pse = tk.BooleanVar(value="possession" in saved_comms)
        var_prot_rss = tk.BooleanVar(value="rss" in saved_comms)
        var_prot_eu = tk.BooleanVar(value="mapeadores_cola" in saved_comms)
        var_prot_recent = tk.BooleanVar(value=saved_recent)

        def _get_active_protected_communities():
            comms = set()
            if var_prot_gfl.get(): comms.add("gfl")
            if var_prot_pse.get(): comms.add("possession")
            if var_prot_rss.get(): comms.add("rss")
            if var_prot_eu.get(): comms.add("mapeadores_cola")
            return comms

        def _on_prot_changed():
            active_c = _get_active_protected_communities()
            self.config["cleaner_protected_comms"] = list(active_c)
            self.config["cleaner_protect_recent"] = var_prot_recent.get()
            app_config.save_config(self.config)
            now_ts = time.time()
            for m in all_maps:
                if m.get("is_server_asset"):
                    continue
                ck = m.get("community_key", "")
                is_sub = m.get("is_officially_subscribed", False)
                if is_sub and "gfl" in active_c:
                    m["is_subscribed"] = True
                    m["status_label"] = "⭐ Subscribed (GFL ZE Collection)"
                    m["status_type"] = "subscribed"
                    m["is_protected"] = True
                elif is_sub:
                    m["is_subscribed"] = False
                    m["status_label"] = "📁 Subscribed (GFL Protection Disabled)"
                    m["status_type"] = "temp"
                    m["is_protected"] = False
                elif ck and ck in active_c:
                    comm_badge = custom_map_cleaner.COMMUNITY_SERVER_ROSTERS.get(ck, {}).get("badge", "🛡️ Community Rotation")
                    m["is_subscribed"] = True
                    m["status_label"] = comm_badge
                    m["status_type"] = "community_protected"
                    m["is_protected"] = True
                elif var_prot_recent.get() and m.get("mtime", 0) > 0 and (now_ts - m["mtime"] <= 14 * 86400):
                    m["is_subscribed"] = True
                    m["status_label"] = "🕒 Active Rotation (Last 14d)"
                    m["status_type"] = "recent_rotation"
                    m["is_protected"] = True
                else:
                    m["is_subscribed"] = False
                    m["status_label"] = "📁 Temp Download (Safe Clean)" if m.get("is_workshop") else "📦 Custom Map (.vpk)"
                    m["status_type"] = "temp" if m.get("is_workshop") else "vpk"
                    m["is_protected"] = False
            update_filter_button_labels()
            render_maps()

        cb_gfl = tk.Checkbutton(prot_bar, text="GFL (355+ ZE)", variable=var_prot_gfl, font=("Segoe UI", 10, "bold"),
                                fg="#fde047", bg="#111622", selectcolor="#0c0e12", activebackground="#111622",
                                activeforeground="#fde047", cursor="hand2", command=_on_prot_changed)
        cb_gfl.pack(side="left", padx=(0, 6))
        add_tooltip(cb_gfl, "Protect GFL Clan Zombie Escape official subscribed collection (355+ maps).")

        cb_pse = tk.Checkbutton(prot_bar, text="Possession (PSE)", variable=var_prot_pse, font=("Segoe UI", 10),
                                fg="#34d399", bg="#111622", selectcolor="#0c0e12", activebackground="#111622",
                                activeforeground="#34d399", cursor="hand2", command=_on_prot_changed)
        cb_pse.pack(side="left", padx=(0, 6))
        add_tooltip(cb_pse, "Protect Possession (PSE Tokyo) custom maps (e.g. ze_colorlicouspilar_p) and asset packs.")

        cb_rss = tk.Checkbutton(prot_bar, text="RSS Revenant", variable=var_prot_rss, font=("Segoe UI", 10),
                                fg="#a78bfa", bg="#111622", selectcolor="#0c0e12", activebackground="#111622",
                                activeforeground="#a78bfa", cursor="hand2", command=_on_prot_changed)
        cb_rss.pack(side="left", padx=(0, 6))
        add_tooltip(cb_rss, "Protect RSS Zombie Escape custom maps (e.g. ze_obff_npst_v24).")

        cb_eu = tk.Checkbutton(prot_bar, text="Mapeadores / cOLa", variable=var_prot_eu, font=("Segoe UI", 10),
                               fg="#fb923c", bg="#111622", selectcolor="#0c0e12", activebackground="#111622",
                               activeforeground="#fb923c", cursor="hand2", command=_on_prot_changed)
        cb_eu.pack(side="left", padx=(0, 6))
        add_tooltip(cb_eu, "Protect Mapeadores and cOLa-TeaM European custom maps and asset packs.")

        cb_rec = tk.Checkbutton(prot_bar, text="🕒 Active (Last 14d)", variable=var_prot_recent, font=("Segoe UI", 10, "bold"),
                                fg="#38bdf8", bg="#111622", selectcolor="#0c0e12", activebackground="#111622",
                                activeforeground="#38bdf8", cursor="hand2", command=_on_prot_changed)
        cb_rec.pack(side="left", padx=(0, 6))
        add_tooltip(cb_rec, "Protect custom maps played in the last 14 days so active rotation maps are preserved.")

        # View Filter Pill Tabs (ALL / TEMP DOWNLOADS / SUBSCRIBED PACK / DUPLICATES)
        filter_tabs_bar = tk.Frame(dlg, bg="#0c0e12")
        filter_tabs_bar.pack(fill="x", padx=10, pady=(0, 6))

        view_filter = tk.StringVar(value="ALL")

        btn_filter_all = tk.Button(filter_tabs_bar, text="All Maps (0)", font=("Segoe UI", 9, "bold"),
                                   fg="#ffffff", bg="#1f2533", relief="flat", padx=8, pady=4, cursor="hand2")
        btn_filter_temp = tk.Button(filter_tabs_bar, text="📁 Temp Downloads (0)", font=("Segoe UI", 9),
                                    fg="#38bdf8", bg="#141c2b", relief="flat", padx=8, pady=4, cursor="hand2")
        btn_filter_sub = tk.Button(filter_tabs_bar, text="⭐ Subscribed Packs (0)", font=("Segoe UI", 9),
                                   fg="#fde047", bg="#232115", relief="flat", padx=8, pady=4, cursor="hand2")
        btn_filter_assets = tk.Button(filter_tabs_bar, text="🛡️ Server Assets (0)", font=("Segoe UI", 9, "bold"),
                                      fg="#34d399", bg="#062e20", relief="flat", padx=8, pady=4, cursor="hand2")
        btn_filter_dupe = tk.Button(filter_tabs_bar, text="⚠️ Duplicates (0)", font=("Segoe UI", 9),
                                    fg="#f87171", bg="#2a1618", relief="flat", padx=8, pady=4, cursor="hand2")

        btn_filter_all.pack(side="left", padx=(0, 4))
        btn_filter_temp.pack(side="left", padx=(0, 4))
        btn_filter_sub.pack(side="left", padx=(0, 4))
        btn_filter_assets.pack(side="left", padx=(0, 4))
        btn_filter_dupe.pack(side="left")

        add_tooltip(btn_filter_all, "Show all custom community maps and server packages.")
        add_tooltip(btn_filter_temp, "Show only temporary downloaded maps from servers you visited. 100% safe to delete.")
        add_tooltip(btn_filter_sub, "Show maps belonging to your subscribed Steam Workshop collections (e.g. GFL ZE Map Pack).")
        add_tooltip(btn_filter_assets, "Show essential community server content packs (player skins, zombie models, sounds) for GFL, Possession, cOLa, Mapeadores.")
        add_tooltip(btn_filter_dupe, "Show duplicate copies of maps across your library.")

        # Search Bar and Summary Row
        bar = tk.Frame(dlg, bg="#0c0e12")
        bar.pack(fill="x", padx=10, pady=(0, 6))

        tk.Label(bar, text="🔍 Search:", font=("Segoe UI", 10, "bold"), fg=FG_WHITE, bg="#0c0e12").pack(side="left", padx=(0, 4))
        search_var = tk.StringVar()
        search_ent = tk.Entry(bar, textvariable=search_var, font=("Segoe UI", 9), bg="#141820", fg="#ffffff",
                              insertbackground="#ffffff", relief="flat", highlightbackground=BG_BORDER, highlightthickness=1)
        search_ent.pack(side="left", fill="x", expand=True, padx=(0, 10))

        summary_var = tk.StringVar(value="Scanning maps...")
        tk.Label(bar, textvariable=summary_var, font=("Segoe UI", 10, "bold"), fg=ACCENT_CYAN, bg="#0c0e12").pack(side="right")

        # Table Container
        tbl_frame = tk.Frame(dlg, bg="#10141d", highlightbackground=BG_BORDER, highlightthickness=1)
        tbl_frame.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        # Dark Table Theme
        style = ttk.Style(dlg)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("MapCleaner.Treeview",
                        background="#10141d",
                        foreground="#f8fafc",
                        fieldbackground="#10141d",
                        bordercolor=BG_BORDER,
                        borderwidth=0,
                        rowheight=26,
                        font=("Segoe UI", 9))
        style.configure("MapCleaner.Treeview.Heading",
                        background="#1a2232",
                        foreground="#38bdf8",
                        relief="flat",
                        font=("Segoe UI", 10, "bold"))
        style.map("MapCleaner.Treeview.Heading",
                  background=[("active", "#243046")])
        style.map("MapCleaner.Treeview",
                  background=[("selected", ACCENT_ORANGE)],
                  foreground=[("selected", "#ffffff")])

        cols = ("check", "name", "id", "status", "size", "date")
        tree = ttk.Treeview(tbl_frame, columns=cols, show="headings", style="MapCleaner.Treeview", selectmode="extended")

        # Dynamic DPI and font-measurement column sizing
        try:
            import ctypes
            u32 = ctypes.windll.user32
            dpi = u32.GetDpiForWindow(dlg.winfo_id()) if hasattr(u32, "GetDpiForWindow") else u32.GetDpiForSystem()
            dpi_scale = max(1.0, dpi / 96.0)
        except Exception:
            dpi_scale = 1.0

        from tkinter import font as tkfont
        f_hd = tkfont.Font(family="Segoe UI", size=max(10, int(10 * dpi_scale)), weight="bold")
        f_row = tkfont.Font(family="Segoe UI", size=max(9, int(9 * dpi_scale)))

        w_check = max(45, int(45 * dpi_scale))
        w_id = max(f_hd.measure("Workshop ID ▾") + 24, f_row.measure("3351648056") + 24, int(120 * dpi_scale))
        
        longest_status_samples = [
            "⭐ Subscribed (GFL ZE Collection)",
            "⭐ Subscribed (GFL Server Pack)",
            "📁 Subscribed (GFL Protection Disabled)",
            "🕒 Active Rotation (Last 14d)",
            "📁 Temp Download (Safe Clean)",
            "🛡️ Essential Server Asset",
            "📦 Custom Map (.vpk)"
        ]
        max_status_text_w = max(f_row.measure(s) for s in longest_status_samples)
        w_status = max(f_hd.measure("Server Pack Status ▾") + 28, max_status_text_w + 32, int(260 * dpi_scale))

        w_size = max(f_hd.measure("Size ▾") + 24, f_row.measure("999.9 MB") + 24, int(95 * dpi_scale))
        w_date = max(f_hd.measure("Last Played / Modified ▾") + 32, f_row.measure("2026-11-08 18:00") + 32, int(195 * dpi_scale))
        w_name = max(340, int(340 * dpi_scale))

        tree.column("check", width=w_check, minwidth=w_check, anchor="center", stretch=False)
        tree.column("name", width=w_name, minwidth=240, anchor="w", stretch=True)
        tree.column("id", width=w_id, minwidth=w_id, anchor="center", stretch=False)
        tree.column("status", width=w_status, minwidth=w_status, anchor="center", stretch=True)
        tree.column("size", width=w_size, minwidth=w_size, anchor="e", stretch=False)
        tree.column("date", width=w_date, minwidth=w_date, anchor="center", stretch=False)

        sb = ttk.Scrollbar(tbl_frame, orient="vertical", command=tree.yview, style="Vertical.Dark.TScrollbar")
        tree.configure(yscrollcommand=sb.set)

        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Row color tags
        tree.tag_configure("sub", foreground="#fde047")      # warm yellow/amber for subscribed
        tree.tag_configure("server_asset", foreground="#34d399") # bright emerald green for protected server assets
        tree.tag_configure("temp", foreground="#38bdf8")     # bright cyan for safe temp downloads
        tree.tag_configure("vpk", foreground="#cbd5e1")      # standard white/gray for vpk
        tree.tag_configure("dupe", background="#221815")     # subtle warning background for duplicates

        tree.bind("<MouseWheel>", lambda e: [tree.yview_scroll(int(-1 * (e.delta / 120)), "units"), "break"][1])

        all_maps = []
        selected_ids = set()
        sort_state = {"col": "size", "reverse": True}

        def update_headings():
            c = sort_state["col"]
            rev = sort_state["reverse"]
            arrow = " ▾" if rev else " ▴"
            tree.heading("check", text="Sel", anchor="center")
            tree.heading("name", text="Map / Asset Package Name" + (arrow if c == "name" else ""), anchor="w")
            tree.heading("id", text="Workshop ID" + (arrow if c == "id" else ""), anchor="center")
            tree.heading("status", text="Server Pack Status" + (arrow if c == "status" else ""), anchor="center")
            tree.heading("size", text="Size" + (arrow if c == "size" else ""), anchor="e")
            tree.heading("date", text="Last Played / Modified" + (arrow if c == "date" else ""), anchor="center")

        def sort_by_column(col):
            if sort_state["col"] == col:
                sort_state["reverse"] = not sort_state["reverse"]
            else:
                sort_state["col"] = col
                sort_state["reverse"] = (col in ("size", "date"))

            if col == "size":
                all_maps.sort(key=lambda m: m["size_bytes"], reverse=sort_state["reverse"])
            elif col == "date":
                all_maps.sort(key=lambda m: m["mtime"], reverse=sort_state["reverse"])
            elif col == "name":
                all_maps.sort(key=lambda m: m["name"].lower(), reverse=sort_state["reverse"])
            elif col == "id":
                all_maps.sort(key=lambda m: str(m["id"]), reverse=sort_state["reverse"])
            elif col == "status":
                all_maps.sort(key=lambda m: m.get("status_label", "").lower(), reverse=sort_state["reverse"])

            update_headings()
            render_maps()

        tree.heading("size", command=lambda: sort_by_column("size"))
        tree.heading("date", command=lambda: sort_by_column("date"))
        tree.heading("name", command=lambda: sort_by_column("name"))
        tree.heading("id", command=lambda: sort_by_column("id"))
        tree.heading("status", command=lambda: sort_by_column("status"))
        update_headings()

        def update_filter_button_labels():
            total = len(all_maps)
            temp_c = sum(1 for m in all_maps if not m.get("is_subscribed") and not m.get("is_server_asset") and m.get("is_workshop"))
            sub_c = sum(1 for m in all_maps if m.get("is_subscribed") and not m.get("is_server_asset"))
            asset_c = sum(1 for m in all_maps if m.get("is_server_asset"))
            dupe_c = sum(1 for m in all_maps if m.get("has_duplicate"))

            btn_filter_all.config(text=f"All Maps ({total})")
            btn_filter_temp.config(text=f"📁 Temp Downloads ({temp_c})")
            btn_filter_sub.config(text=f"⭐ Subscribed Packs ({sub_c})")
            btn_filter_assets.config(text=f"🛡️ Server Assets ({asset_c})")
            btn_filter_dupe.config(text=f"⚠️ Duplicates ({dupe_c})")

        def set_filter(mode: str):
            view_filter.set(mode)
            btn_filter_all.config(bg="#1f2533" if mode == "ALL" else "#121620")
            btn_filter_temp.config(bg="#1e3a5f" if mode == "TEMP" else "#141c2b")
            btn_filter_sub.config(bg="#3a3215" if mode == "SUBSCRIBED" else "#232115")
            btn_filter_assets.config(bg="#0c4a34" if mode == "ASSETS" else "#062e20")
            btn_filter_dupe.config(bg="#451a1d" if mode == "DUPES" else "#2a1618")
            render_maps()

        btn_filter_all.config(command=lambda: set_filter("ALL"))
        btn_filter_temp.config(command=lambda: set_filter("TEMP"))
        btn_filter_sub.config(command=lambda: set_filter("SUBSCRIBED"))
        btn_filter_assets.config(command=lambda: set_filter("ASSETS"))
        btn_filter_dupe.config(command=lambda: set_filter("DUPES"))
        def update_summary():
            sel_bytes = sum(m["size_bytes"] for m in all_maps if m["id"] in selected_ids)
            total_bytes = sum(m["size_bytes"] for m in all_maps)
            sel_gb = sel_bytes / (1024 ** 3)
            tot_gb = total_bytes / (1024 ** 3)
            summary_var.set(f"Total: {len(all_maps)} Maps ({tot_gb:.1f} GB)  |  Selected: {len(selected_ids)} ({sel_gb:.2f} GB)")

        def render_maps():
            tree.delete(*tree.get_children())
            q = search_var.get().strip().lower()
            mode = view_filter.get()

            filtered = []
            for m in all_maps:
                # Text search match on name or ID
                if q and (q not in m["name"].lower() and q not in str(m["id"])):
                    continue
                # Tab filter match
                if mode == "TEMP" and (m.get("is_subscribed") or not m.get("is_workshop")):
                    continue
                if mode == "TEMP" and (m.get("is_subscribed") or m.get("is_server_asset") or not m.get("is_workshop")):
                    continue
                elif mode == "SUBSCRIBED" and (not m.get("is_subscribed") or m.get("is_server_asset")):
                    continue
                elif mode == "ASSETS" and not m.get("is_server_asset"):
                    continue
                    continue
                elif mode == "DUPES" and not m.get("has_duplicate"):
                    continue
                filtered.append(m)

            for m in filtered:
                tags = []
                if m.get("is_server_asset"):
                    tags.append("server_asset")
                elif m.get("is_subscribed"):
                    tags.append("sub")
                elif m.get("is_workshop"):
                    tags.append("temp")
                else:
                    tags.append("vpk")
                if m.get("has_duplicate"):
                    tags.append("dupe")

                chk = "☑" if m["id"] in selected_ids else "☐"
                display_name = m["name"]
                if m.get("has_duplicate"):
                    display_name += "  ⚠️ (Dupe)"

                tree.insert("", "end", iid=m["id"],
                            values=(chk, display_name, m["id"], m.get("status_label", ""), m["size_str"], m["mtime_str"]),
                            tags=tuple(tags))
            update_summary()

        def toggle_item(item_id):
            if item_id in selected_ids:
                selected_ids.remove(item_id)
            else:
                selected_ids.add(item_id)
            for m in all_maps:
                if m["id"] == item_id:
                    chk = "☑" if item_id in selected_ids else "☐"
                    display_name = m["name"]
                    if m.get("has_duplicate"):
                        display_name += "  ⚠️ (Dupe)"
                    tree.item(item_id, values=(chk, display_name, m["id"], m.get("status_label", ""), m["size_str"], m["mtime_str"]))
                    break
            update_summary()

        tree.bind("<Button-1>", lambda e: self._on_tree_click(e, tree, toggle_item))
        tree.bind("<space>", lambda e: [toggle_item(item) for item in tree.selection()])
        search_var.trace_add("write", lambda *args: render_maps())

        # Scan in background (capture Tkinter variables on main thread for thread safety)
        def load_maps_task():
            nonlocal all_maps
            active_c = set()
            try:
                active_c = _get_active_protected_communities()
                protect_rec = var_prot_recent.get()
            except Exception:
                protect_rec = True
            res = custom_map_cleaner.scan_custom_maps(
                self.paths["steam_path"],
                self.paths["cs2_dir"],
                protected_communities=active_c,
                protect_recent=protect_rec
            )
            all_maps = res
            def _on_finish():
                if dlg.winfo_exists():
                    sort_by_column("size")
                    update_filter_button_labels()
            self.safe_after(0, _on_finish)

        threading.Thread(target=load_maps_task, daemon=True).start()

        # Quick action filters bar
        filter_actions = tk.Frame(dlg, bg="#0c0e12")
        filter_actions.pack(fill="x", padx=10, pady=(0, 6))

        def select_temp_safe():
            """One-click selects ALL temporary downloaded maps (leaving 100% of subscribed server pack maps and server assets untouched)."""
            selected_ids.clear()
            for m in all_maps:
                if not m.get("is_subscribed") and not m.get("is_server_asset") and not m.get("is_protected") and m.get("is_workshop"):
                    selected_ids.add(m["id"])
            render_maps()

        def select_dupes_safe():
            """Selects ONLY the temporary un-subscribed copies of duplicate maps (NEVER server asset packs or custom VPKs)."""
            selected_ids.clear()
            for m in all_maps:
                if m.get("has_duplicate") and not m.get("is_subscribed") and not m.get("is_server_asset") and not m.get("is_protected"):
                    selected_ids.add(m["id"])
            render_maps()

        def select_all():
            """Selects all playable maps while keeping Server Asset Packs and custom modified VPKs protected."""
            selected_ids.clear()
            for m in all_maps:
                if not m.get("is_server_asset") and not m.get("is_protected"):
                    selected_ids.add(m["id"])
            render_maps()

        def select_none():
            selected_ids.clear()
            render_maps()

        def select_large():
            """Selects maps > 1 GB (excluding protected server asset packs)."""
            selected_ids.clear()
            for m in all_maps:
                if m["size_bytes"] >= 1024 ** 3 and not m.get("is_server_asset") and not m.get("is_protected"):
                    selected_ids.add(m["id"])
            render_maps()
        btn_sel_temp = tk.Button(filter_actions, text="⚡ Select All Temp Downloads (Safe)", font=("Segoe UI", -12, "bold"),
                  fg="#ffffff", bg="#0284c7", activebackground="#0369a1", relief="flat", padx=10, pady=4,
                  cursor="hand2", command=select_temp_safe)
        btn_sel_temp.pack(side="left", padx=(0, 4))
        add_tooltip(btn_sel_temp, "One-click selects all temporary downloaded maps while keeping server packs and assets protected.")

        btn_sel_dupes = tk.Button(filter_actions, text="⚠️ Select Temp Dupes Only (Safe)", font=("Segoe UI", -12, "bold"),
                  fg="#f87171", bg="#2a1618", activebackground="#451a1d", relief="flat", padx=10, pady=4,
                  cursor="hand2", command=select_dupes_safe)
        btn_sel_dupes.pack(side="left", padx=(0, 4))
        add_tooltip(btn_sel_dupes, "Selects only temporary duplicate copies to reclaim SSD space safely.")

        btn_sel_all = tk.Button(filter_actions, text="Select All", font=("Segoe UI", -12, "bold"), fg="#cbd5e1", bg="#242b3b", relief="flat", padx=10, pady=4, cursor="hand2", command=select_all)
        btn_sel_all.pack(side="left", padx=(0, 4))
        add_tooltip(btn_sel_all, "Selects all playable maps (excludes protected server asset packs).")

        btn_sel_none = tk.Button(filter_actions, text="Deselect All", font=("Segoe UI", -12, "bold"), fg="#cbd5e1", bg="#242b3b", relief="flat", padx=10, pady=4, cursor="hand2", command=select_none)
        btn_sel_none.pack(side="left", padx=(0, 4))
        add_tooltip(btn_sel_none, "Clears all selections.")

        btn_sel_large = tk.Button(filter_actions, text="Select Maps > 1 GB", font=("Segoe UI", -12, "bold"), fg="#cbd5e1", bg="#242b3b", relief="flat", padx=10, pady=4, cursor="hand2", command=select_large)
        btn_sel_large.pack(side="left")
        add_tooltip(btn_sel_large, "Selects all map packages exceeding 1 Gigabyte.")

        # Bottom Button Bar
        btn_bar = tk.Frame(dlg, bg="#0c0e12", pady=6)
        btn_bar.pack(fill="x", padx=10, pady=(0, 8))

        def delete_selected():
            if not selected_ids:
                messagebox.showwarning("No Selection", "Please check at least one map to delete.")
                return

            if core_logic.is_cs2_running():
                messagebox.showwarning(
                    "CS2 Is Running",
                    "Please close Counter-Strike 2 before deleting custom maps.\n\n"
                    "Windows locks .vpk map files while the game is running, which causes file access errors."
                )
                return

            sel_items = [m for m in all_maps if m["id"] in selected_ids]
            sel_bytes = sum(m["size_bytes"] for m in sel_items)
            sel_gb = sel_bytes / (1024 ** 3)

            # Check if any selected items are Subscribed Server Pack Maps
            # Check if any selected items are Server Asset Packs or Custom Modified VPKs
            asset_selected = [m for m in sel_items if m.get("is_server_asset") or m.get("is_protected")]
            if asset_selected:
                asset_preview = "\n".join(f"  • {m['name']} (ID: {m['id']})" for m in asset_selected[:5])
                danger_msg = (
                    f"🚨 CRITICAL WARNING: SERVER ASSET / CONTENT PACK SELECTED!\n\n"
                    f"You have selected {len(asset_selected)} essential Server Asset / Content Package(s):\n\n"
                    f"{asset_preview}\n\n"
                    f"⚠️ WHY THIS WILL BREAK YOUR GAME:\n"
                    f"• In GFL and other Zombie Escape servers, these VPKs contain player skins, zombie models, sounds, and boss textures.\n"
                    f"• Deleting this VPK causes massive red 'ERROR' models walking around and missing checkerboard textures!\n"
                    f"• If you customized or modified this VPK with your own player models or FPS textures, deleting it will PERMANENTLY erase your custom work!\n\n"
                    f"RECOMMENDED SAFE ACTION:\n"
                    f"Click [No] to keep your server assets and custom mods safe.\n\n"
                    f"Are you ABSOLUTELY sure you want to force delete these server asset packages?"
                )
                if not messagebox.askyesno("🚨 Critical Server Asset Warning", danger_msg, icon="error"):
                    return

            # Check if any selected items are Subscribed Server Pack Maps
            sub_selected = [m for m in sel_items if m.get("is_subscribed") and not m.get("is_server_asset")]
            if sub_selected:
                names_preview = "\n".join(f"  • {m['name']} (ID: {m['id']})" for m in sub_selected[:5])
                if len(sub_selected) > 5:
                    names_preview += f"\n  ...and {len(sub_selected) - 5} other subscribed map(s)"

                warning_msg = (
                    f"⚠️ CRITICAL CAUTION: SERVER PACK MAPS SELECTED!\n\n"
                    f"You have selected {len(sub_selected)} map(s) that belong to your Subscribed Workshop Collection (Server Map Pack / GFL ZE Collection):\n\n"
                    f"{names_preview}\n\n"
                    f"🚨 WHY THIS IS DANGEROUS:\n"
                    f"Because your Steam account is currently subscribed to these maps, deleting the files locally will cause:\n"
                    f"'Required map missing on your client' error when the server changes to these maps!\n\n"
                    f"RECOMMENDED SAFE ACTION:\n"
                    f"Click [No], then use '⚡ Select All Temp Downloads (Safe)' to delete only temporary server caches.\n\n"
                    f"Do you still want to force delete these {len(sub_selected)} subscribed server pack map(s)?"
                )
                if not messagebox.askyesno("⚠️ Critical Server Pack Warning", warning_msg, icon="warning"):
                    return
            else:
                confirm = messagebox.askyesno(
                    "Confirm Map Deletion",
                    f"Are you sure you want to delete {len(sel_items)} temporary custom map(s)?\n\n"
                    f"Reclaimed Space: {sel_gb:.2f} GB\n\n"
                    "• Subscribed Server Map Pack maps are 100% protected and excluded.\n"
                    "• Official Valve competitive maps are protected.\n"
                    "• If you visit servers playing these maps in the future, CS2 will re-download them automatically."
                )
                if not confirm:
                    return

            count, freed, logs = custom_map_cleaner.delete_custom_maps(sel_items)
            for l in logs:
                self.log(l)

            freed_gb = freed / (1024 ** 3)
            self.log(f"[MAP CLEANER] Deleted {count} custom maps. Freed {freed_gb:.2f} GB of SSD space!")
            if hasattr(self, "d_list_frame"):
                self._refresh_drives_list(self.d_list_frame)
            self._quick_map_stats_check()

            messagebox.showinfo("Clean Complete", f"Successfully deleted {count} maps!\n\nReclaimed: {freed_gb:.2f} GB of SSD space.")
            selected_ids.clear()
            threading.Thread(target=load_maps_task, daemon=True).start()

        def _close_cleaner_dlg():
            try:
                dlg.grab_release()
            except Exception:
                pass
            dlg.destroy()

        dlg.protocol("WM_DELETE_WINDOW", _close_cleaner_dlg)

        # 1-Click Backup and Restore for Custom / Modified Server Asset VPKs
        def backup_custom_vpks():
            backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups", "custom_assets")
            os.makedirs(backup_dir, exist_ok=True)
            copied = 0
            for m in all_maps:
                if m.get("is_server_asset") or "3793587501" in str(m.get("id")):
                    src_folder = m["path"]
                    if os.path.isdir(src_folder):
                        for fl in os.listdir(src_folder):
                            if fl.endswith(".vpk"):
                                src_file = os.path.join(src_folder, fl)
                                dst_file = os.path.join(backup_dir, f"{m['id']}_{fl}")
                                shutil.copy2(src_file, dst_file)
                                copied += 1
            if copied > 0:
                self.log(f"[BACKUP] Successfully backed up {copied} custom server asset VPK(s) to: {backup_dir}")
                messagebox.showinfo("Backup Complete", f"Successfully backed up {copied} custom server asset VPK(s)!\n\nBackup Folder:\n{backup_dir}\n\nYour custom models and textures are now safe from accidental deletion or Steam overwrites.")
            else:
                messagebox.showinfo("No Assets Found", "No Server Asset VPKs (e.g. GFL #3793587501) found to back up.")

        def restore_custom_vpks():
            backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups", "custom_assets")
            if not os.path.exists(backup_dir) or not os.listdir(backup_dir):
                messagebox.showinfo("No Backups", "No custom VPK backups found to restore.")
                return
            restored = 0
            for f in os.listdir(backup_dir):
                if f.endswith(".vpk") and "_" in f:
                    wid = f.split("_")[0]
                    vpk_name = "_".join(f.split("_")[1:])
                    for m in all_maps:
                        if str(m.get("id")) == wid:
                            dst = os.path.join(m["path"], vpk_name)
                            src = os.path.join(backup_dir, f)
                            shutil.copy2(src, dst)
                            restored += 1
            if restored > 0:
                self.log(f"[RESTORE] Restored {restored} custom asset VPK(s) successfully!")
                messagebox.showinfo("Restore Complete", f"Successfully restored {restored} custom asset VPK(s)!\n\nYour custom models and textures have been restored to your workshop directory.")
                threading.Thread(target=load_maps_task, daemon=True).start()
            else:
                messagebox.showinfo("Restore", "No matching backups could be restored to active directories.")

        btn_del = tk.Button(btn_bar, text="🗑️ DELETE SELECTED MAPS", font=("Segoe UI", -12, "bold"),
                  fg="#ffffff", bg=ACCENT_RED, activebackground="#dc2626", relief="flat",
                  padx=16, pady=4, cursor="hand2", command=delete_selected)
        btn_del.pack(side="left", padx=(0, 10))
        add_tooltip(btn_del, "Permanently removes checked maps from your drive to free up SSD space.")

        btn_bk = tk.Button(btn_bar, text="💾 Backup Custom VPK", font=("Segoe UI", -12, "bold"),
                  fg="#34d399", bg="#062e20", activebackground="#0c4a34", activeforeground="#ffffff",
                  relief="flat", padx=14, pady=4, cursor="hand2", command=backup_custom_vpks)
        btn_bk.pack(side="left", padx=(0, 6))
        add_tooltip(btn_bk, "Creates a safe backup of your server asset VPKs and custom modifications.")

        btn_rst = tk.Button(btn_bar, text="♻️ Restore Custom VPK", font=("Segoe UI", -12, "bold"),
                  fg="#38bdf8", bg="#141c2b", activebackground="#1e3a5f", activeforeground="#ffffff",
                  relief="flat", padx=14, pady=4, cursor="hand2", command=restore_custom_vpks)
        btn_rst.pack(side="left")
        add_tooltip(btn_rst, "Restores your backed-up custom VPKs if overwritten by Steam or server updates.")

        btn_cl = tk.Button(btn_bar, text="Close", font=("Segoe UI", -12, "bold"), fg="#cbd5e1", bg="#181e2b",
                  relief="flat", padx=16, pady=4, cursor="hand2", command=_close_cleaner_dlg)
        btn_cl.pack(side="right")
        add_tooltip(btn_cl, "Closes the Custom Map Cleaner dialog.")

        # Dynamic content-based sizing clamped strictly to desktop workarea
        work_w, work_h = get_desktop_workarea()
        dlg.update_idletasks()
        req_w = dlg.winfo_reqwidth()
        req_h = dlg.winfo_reqheight()
        target_w = min(max(req_w + 30, 1140, int(work_w * 0.75)), work_w - 40)
        target_h = min(max(req_h + 30, 680, int(work_h * 0.72)), work_h - 40)
        dlg.minsize(min(req_w, 980), 560)
        center_window_on_parent(dlg, parent=self, req_w=target_w, req_h=target_h)

    def _on_tree_click(self, event, tree, toggle_callback):
        region = tree.identify("region", event.x, event.y)
        if region in ("cell", "tree"):
            item_id = tree.identify_row(event.y)
            if item_id:
                toggle_callback(item_id)

    # --- SETTINGS DIALOG ---

    def open_settings_dialog(self):
        """Settings modal for Windows Startup, System Tray, and Discord Rich Presence."""
        dlg = tk.Toplevel(self)
        dlg.title("CS2 Command Center Settings")
        dlg.resizable(False, False)
        dlg.configure(bg=BG_WINDOW)
        dlg.transient(self)
        dlg.grab_set()
        center_window_on_parent(dlg, parent=self, req_w=540, req_h=430)

        head = tk.Frame(dlg, bg=BG_CARD_ROW, padx=14, pady=10, highlightbackground=BG_BORDER, highlightthickness=1)
        head.pack(fill="x", padx=10, pady=(10, 8))

        tk.Label(head, text="⚙ SETTINGS & BACKGROUND OPTIONS", font=("Segoe UI", 10, "bold"), fg=FG_WHITE, bg=BG_CARD_ROW).pack(anchor="w")
        tk.Label(head, text="Configure system tray behavior, Windows startup, and Discord integration.", font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_CARD_ROW).pack(anchor="w", pady=(1, 0))

        body = tk.Frame(dlg, bg=BG_CARD, padx=14, pady=12, highlightbackground=BG_BORDER, highlightthickness=1)
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 1. Start with Windows
        var_startup = tk.BooleanVar(value=self.config.get("start_with_windows", False))
        var_minimized = tk.BooleanVar(value=self.config.get("start_minimized", False))

        def on_startup_toggle():
            if not var_startup.get():
                cb_m.config(state="disabled")
            else:
                cb_m.config(state="normal")

        cb_s = tk.Checkbutton(body, text=" Start CS2 Command Center with Windows", variable=var_startup,
                              command=on_startup_toggle,
                              font=("Segoe UI", 14, "bold"), fg=FG_WHITE, bg=BG_CARD, activebackground=BG_CARD, selectcolor=BG_WINDOW)
        cb_s.pack(anchor="w", pady=(0, 2))

        cb_m = tk.Checkbutton(body, text=" Start minimized to System Tray (hidden near Windows clock)", variable=var_minimized,
                              font=("Segoe UI", 10), fg="#cbd5e1", bg=BG_CARD, activebackground=BG_CARD, selectcolor=BG_WINDOW)
        cb_m.pack(anchor="w", padx=20, pady=(0, 2))
        if not var_startup.get():
            cb_m.config(state="disabled")

        tk.Label(body, text="When unchecked, the app window opens on your desktop at startup.", font=("Segoe UI", 9, "italic"), fg=FG_MUTED, bg=BG_CARD, wraplength=480, justify="left").pack(anchor="w", padx=24, pady=(0, 8))

        # 2. Minimize to tray on close
        var_tray = tk.BooleanVar(value=self.config.get("minimize_to_tray_on_close", True))
        cb_t = tk.Checkbutton(body, text=" Minimize to System Tray when [-] is clicked", variable=var_tray,
                              font=("Segoe UI", 14, "bold"), fg=FG_WHITE, bg=BG_CARD, activebackground=BG_CARD, selectcolor=BG_WINDOW)
        cb_t.pack(anchor="w", pady=(0, 2))
        tk.Label(body, text="Clicking [-] hides window to the tray; clicking [X] closes the application completely.", font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_CARD, wraplength=480, justify="left").pack(anchor="w", padx=20, pady=(0, 8))

        # 3. Quick Link to Discord Presence Tab
        disc_box = tk.Frame(body, bg=BG_CARD_ROW, padx=12, pady=10, highlightbackground=BG_BORDER, highlightthickness=1)
        disc_box.pack(fill="x", pady=(4, 8))
        tk.Label(disc_box, text="🎮 DISCORD RICH PRESENCE", font=("Segoe UI", 14, "bold"), fg=FG_WHITE, bg=BG_CARD_ROW).pack(anchor="w")
        tk.Label(disc_box,
                 text="Discord Presence features automatic CS2 detection, real-time profile preview, and live map & player broadcaster. Universal setup is 100% pre-configured.",
                 font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_CARD_ROW, justify="left", wraplength=400).pack(anchor="w", pady=(2, 6))

        def _close_settings():
            try:
                dlg.grab_release()
            except Exception:
                pass
            dlg.destroy()
            if self.winfo_exists():
                try:
                    self.focus_set()
                except Exception:
                    pass

        dlg.protocol("WM_DELETE_WINDOW", _close_settings)

        def open_discord_tab():
            _close_settings()
            self._select_nav("DISCORD")

        b_disc = tk.Button(disc_box, text="Open Discord Presence Tab  ➔", font=("Segoe UI", 10, "bold"),
                  fg="#ffffff", bg="#2563eb", activebackground="#1d4ed8", relief="flat", padx=12, pady=4, cursor="hand2",
                  command=open_discord_tab)
        b_disc.pack(anchor="w")
        add_tooltip(b_disc, "Navigate directly to the Discord Presence tab to configure rich presence.")

        def save_settings():
            self.config["start_with_windows"] = var_startup.get()
            self.config["start_minimized"] = var_minimized.get()
            self.config["minimize_to_tray_on_close"] = var_tray.get()

            app_config.set_windows_startup(var_startup.get(), var_minimized.get())
            app_config.save_config(self.config)

            self.log(f"[SETTINGS] Saved! Windows Startup: {var_startup.get()} (minimized: {var_minimized.get()}) | Tray on [-]: {var_tray.get()}")
            _close_settings()
            self.after(50, lambda: messagebox.showinfo("Settings Saved", "Preferences updated successfully!"))

        btn_row = tk.Frame(dlg, bg=BG_WINDOW)
        btn_row.pack(pady=(4, 14))

        b_save = tk.Button(btn_row, text="💾 Save Settings", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg=ACCENT_ORANGE,
                  relief="flat", padx=16, pady=6, cursor="hand2", command=save_settings)
        b_save.pack(side="left", padx=4)
        add_tooltip(b_save, "Saves Windows startup and system tray preferences to app_config.json.")

        b_cancel = tk.Button(btn_row, text="Cancel", font=("Segoe UI", 10, "bold"), fg="#cbd5e1", bg="#1c212c",
                  relief="flat", padx=16, pady=6, cursor="hand2", command=_close_settings)
        b_cancel.pack(side="left", padx=4)
        add_tooltip(b_cancel, "Discards unsaved preference changes and closes settings.")

if __name__ == "__main__":
    _single_instance_mutex = check_single_instance()
    if not _single_instance_mutex:
        # A running instance was found, signaled to restore to the front, and we exit immediately.
        sys.exit(0)

    app = CS2TruePanoramaApp()
    if "--minimized" in sys.argv:
        app.withdraw()
    app.mainloop()
