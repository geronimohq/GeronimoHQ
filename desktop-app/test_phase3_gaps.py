"""AUDIT Phase 3 gaps (checked against audit/PHASES_3_7.md):
every page AND dialog opens without Tk errors, every clickable has a tooltip, no light-theme
leftovers, every tray item is wired. Temp config, mocked network, nothing launched (the tray's
Quick Connect is mocked: it would open steam://)."""
import os
import sys
import time
import unittest
from unittest import mock

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _test_isolation  # noqa: E402,F401
import app  # noqa: E402
import tkinter as tk  # noqa: E402
from tkinter import ttk  # noqa: E402

TOOLTIP_WIDGETS = set()
_orig_init = app.PanoramaTooltip.__init__


def _rec_init(self, widget, text, delay_ms=800):
    if widget is not None and str(text).strip():
        TOOLTIP_WIDGETS.add(str(widget))
    _orig_init(self, widget, text, delay_ms)


app.PanoramaTooltip.__init__ = _rec_init

CLICKABLE = (tk.Button, tk.Checkbutton, tk.Radiobutton, ttk.Button, ttk.Checkbutton, ttk.Combobox, ttk.Scale, tk.Scale)


def _lum(rgb16):
    r, g, b = [c / 65535 for c in rgb16]
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def walk(w):
    yield w
    for c in w.winfo_children():
        yield from walk(c)


def is_clickable(w):
    if isinstance(w, CLICKABLE):
        return True
    try:
        return str(w.cget("cursor")) == "hand2" and bool(w.bind("<Button-1>"))
    except Exception:
        return False


def label_of(w):
    for opt in ("text", "textvariable"):
        try:
            v = w.cget(opt)
            if opt == "textvariable" and v:
                v = w.getvar(v)
            if v:
                return str(v)[:50]
        except Exception:
            pass
    return w.winfo_class()


class Gaps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.errors = []
        cls.root = app.CS2TruePanoramaApp()
        cls.root.withdraw()
        cls.root.report_callback_exception = lambda e, v, tb: cls.errors.append(f"{e.__name__}: {v}")
        cls.boxes = mock.patch.multiple(app.messagebox, showinfo=mock.DEFAULT, showwarning=mock.DEFAULT,
                                        showerror=mock.DEFAULT, askyesno=mock.DEFAULT)
        cls.boxes.start()

    @classmethod
    def tearDownClass(cls):
        cls.boxes.stop()
        with mock.patch.object(app.os, "_exit", lambda code=0: None):
            cls.root.exit_application()

    def pump(self, s=0.3):
        end = time.time() + s
        while time.time() < end:
            self.root.update(); time.sleep(0.02)

    def build_everything(self):
        r = self.root
        for key in list(r.nav_items):
            r._select_nav(key); self.pump(0.2)
        dlgs = []
        tmp_cfg = os.path.join(_test_isolation.TEMP_DIR, "cfg_dummy"); os.makedirs(tmp_cfg, exist_ok=True)
        opens = [
            ("settings", lambda: r.open_settings_dialog()),
            ("add server", lambda: r.open_add_server_dialog()),
            ("players", lambda: r.open_players_dialog("74.91.124.21", 27015, "GFL Clan Zombie Escape")),
            ("soundtrack", lambda: r.open_soundtrack_dialog("ze_test_v1")),
            ("map cleaner", lambda: r.open_custom_map_cleaner_dialog()),
        ]
        for name, fn in opens:
            before = set(map(str, r.winfo_children()))
            with mock.patch.dict(r.paths, {"cfg_dir": tmp_cfg, "cs2_dir": tmp_cfg, "steam_path": tmp_cfg}):
                fn(); self.pump(0.5)
            new = [w for w in r.winfo_children() if isinstance(w, tk.Toplevel) and str(w) not in before]
            dlgs.append((name, new))
        return dlgs

    def test_pages_dialogs_tooltips_colours_tray(self):
        r = self.root
        dlgs = self.build_everything()
        opened = {n: len(w) for n, w in dlgs}
        missing_tip, light = [], []
        for w in walk(r):
            if isinstance(w, tk.Toplevel) and getattr(w, "_is_tooltip", False):
                continue
            if is_clickable(w) and str(w) not in TOOLTIP_WIDGETS:
                missing_tip.append(f"{w.winfo_class()}: {label_of(w)}")
            for opt in ("bg", "background"):
                try:
                    col = w.cget(opt)
                except Exception:
                    continue
                if col and _lum(w.winfo_rgb(col)) > 0.6 and not isinstance(w, tk.Toplevel):
                    light.append(f"{w.winfo_class()} bg={col}: {label_of(w)}")
                break
        # close every dialog with Esc (same path as the [X] button)
        for name, ws in dlgs:
            for d in ws:
                if d.winfo_exists():
                    cmd = d.protocol("WM_DELETE_WINDOW")
                    d.tk.call(cmd) if cmd else d.destroy()
        self.pump(0.3)
        # tray: each item's action runs (side effects mocked)
        tray = {}
        icon = getattr(r, "tray_icon", None)
        if icon is not None and getattr(icon, "menu", None):
            with mock.patch.object(r, "run_connect_workflow") as conn, \
                    mock.patch.object(r, "toggle_gfl_slot_sniper") as snip, \
                    mock.patch.object(r, "restore_from_tray") as rest, \
                    mock.patch.object(r, "_tray_toggle_startup") as start, \
                    mock.patch.object(r, "exit_application") as ex:
                for item in icon.menu.items:
                    if getattr(item, "text", None):
                        item(icon)
                self.pump(0.3)
                tray = {"open": rest.called, "quick_connect": conn.call_args[0][:2] if conn.called else None,
                        "sniper": snip.called, "startup": start.called, "exit": ex.called}
        report = {"dialogs_opened": opened, "missing_tooltips": len(missing_tip), "light_bg": len(light), "tray": tray}
        print("\n[G3] " + str(report))
        for m in sorted(set(missing_tip))[:60]:
            print("   no tooltip ->", m)
        for m in sorted(set(light))[:40]:
            print("   light bg   ->", m)
        self.assertEqual(self.errors, [], "\n".join(self.errors))
        self.assertTrue(all(v >= 1 for v in opened.values()), opened)
        self.assertEqual(tray.get("quick_connect"), ("74.91.124.21", 27015))
        self.assertTrue(tray["open"] and tray["sniper"] and tray["startup"] and tray["exit"], tray)
        self.assertEqual(missing_tip, [], f"{len(missing_tip)} clickables without tooltip")
        self.assertEqual(light, [], f"{len(light)} light-theme widgets")


if __name__ == "__main__":
    _res = unittest.main(exit=False, verbosity=2)
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(0 if _res.result.wasSuccessful() else 1)
