"""Widget-tree audit for the retro skin (used by test_retro_skin.py and run standalone for a report).

Builds the app with a temp config and mocked network, opens every page and dialog, then checks every
widget that has both a text color and a fill color."""
import collections
import os
import sys
import time
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _hex(root, color):
    try:
        r, g, b = root.winfo_rgb(color)
        return "#%02X%02X%02X" % (r >> 8, g >> 8, b >> 8)
    except Exception:
        return None


def _walk(w):
    yield w
    for c in w.winfo_children():
        yield from _walk(c)


def collect(root_app, pump):
    """Returns (rows, primaries_by_page). rows: dicts for every text widget."""
    import theme
    rows = []

    def scan(container, where):
        for w in _walk(container):
            cls = w.winfo_class()
            if cls not in ("Label", "Button", "Checkbutton", "Radiobutton", "Entry", "Text", "Menubutton"):
                continue
            try:
                fg = _hex(root_app, w.cget("fg") if cls != "Entry" else w.cget("fg"))
                bg = _hex(root_app, w.cget("bg"))
                f = tkfont.Font(root=root_app, font=w.cget("font"))
                size, weight = f.actual("size"), f.actual("weight")
                px = -size if size < 0 else round(size * root_app.winfo_fpixels("1i") / 72)
                try:
                    txt = str(w.cget("text"))[:40]
                except Exception:
                    txt = ""
                try:
                    state = str(w.cget("state"))
                except Exception:
                    state = "normal"
                try:
                    relief = str(w.cget("relief"))
                except Exception:
                    relief = ""
                a = f.actual()
                rows.append(dict(where=where, cls=cls, fg=fg, bg=bg, px=px, bold=(weight == "bold"), text=txt,
                                 state=state, widget=w, relief=relief, family=a["family"], pt=a["size"]))
            except Exception:
                continue

    for key in list(root_app.nav_items):
        root_app._select_nav(key)
        pump(0.3)
        scan(root_app.pages[key], f"page:{key}")
    scan(root_app, "main")
    # dialogs (same chrome as the main window)
    import tempfile
    tmp = tempfile.mkdtemp(prefix="retro_cfg_")
    opens = [("settings", lambda: root_app.open_settings_dialog()),
             ("add_server", lambda: root_app.open_add_server_dialog()),
             ("players", lambda: root_app.open_players_dialog("74.91.124.21", 27015, "GFL Clan Zombie Escape")),
             ("soundtrack", lambda: root_app.open_soundtrack_dialog("ze_test_v1")),
             ("map_cleaner", lambda: root_app.open_custom_map_cleaner_dialog())]
    for name, fn in opens:
        before = set(map(str, root_app.winfo_children()))
        with mock.patch.dict(root_app.paths, {"cfg_dir": tmp, "cs2_dir": tmp, "steam_path": tmp}):
            fn()
            pump(0.6)
        for w in root_app.winfo_children():
            if isinstance(w, tk.Toplevel) and str(w) not in before:
                scan(w, f"dialog:{name}")
                try:
                    cmd = w.protocol("WM_DELETE_WINDOW")
                    w.tk.call(cmd) if cmd else w.destroy()
                except Exception:
                    pass
        pump(0.2)
    return rows


def primary_buttons(rows):
    """{where: [button texts]} for accent-filled buttons (page/dialog scope; the header button is 'main')."""
    import theme
    out = collections.defaultdict(list)
    for r in rows:
        if r["cls"] == "Button" and r["bg"] == theme.ACCENT.upper() and r["where"] != "main":
            out[r["where"]].append(r["text"])
    return out


def violations(rows):
    import theme
    out = collections.defaultdict(list)
    for r in rows:
        if not r["fg"] or not r["bg"] or r["state"] == "disabled":
            continue
        c = theme.contrast(r["fg"], r["bg"])
        large = r["px"] >= 24 or (r["px"] >= 18 and r["bold"])
        if r["fg"].upper() == theme.ACCENT.upper():
            if not any(ch.isalnum() for ch in r["text"]):
                continue   # icon-only label: the active nav icon may be accent
            # accent: headings only (bold, >= 15 px) and >= 3:1; never small body text
            if not (r["bold"] and r["px"] >= 15):
                out["accent-small-text"].append(r)
            elif c < 3.0:
                out["accent-contrast<3"].append(r)
            continue
        if c < (3.0 if large else 4.5):
            out["contrast"].append((round(c, 2), r))
    return out


if __name__ == "__main__":
    os.environ["CS2CC_TEST_NETWORK"] = "0"
    import _test_isolation  # noqa: F401
    import app
    root = app.CS2TruePanoramaApp()
    root.withdraw()

    def pump(s=0.3):
        end = time.time() + s
        while time.time() < end:
            root.update(); time.sleep(0.02)

    with mock.patch.multiple(app.messagebox, showinfo=mock.DEFAULT, showwarning=mock.DEFAULT,
                             showerror=mock.DEFAULT, askyesno=mock.DEFAULT):
        rows = collect(root, pump)
    v = violations(rows)
    print(f"widgets checked: {len(rows)}")
    for kind, items in v.items():
        print(f"\n== {kind}: {len(items)}")
        seen = set()
        for it in items:
            r = it[1] if isinstance(it, tuple) else it
            key = (r["fg"], r["bg"], r["text"])
            if key in seen:
                continue
            seen.add(key)
            c = f" {it[0]}" if isinstance(it, tuple) else ""
            print(f"  {r['where']:22} {r['cls']:12} fg {r['fg']} bg {r['bg']} {r['px']}px{' b' if r['bold'] else ''}{c}  '{r['text']}'")
            if len(seen) > 45:
                break
    with mock.patch.object(app.os, "_exit", lambda code=0: None):
        root.exit_application()
    sys.stdout.flush()
    os._exit(0)
