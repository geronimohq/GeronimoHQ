"""CS2 Command Center, web-window front end. Run: python web_main.py   (UI files are built into ./web by desktop-ui)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def resource_dir() -> str:
    return getattr(sys, "_MEIPASS", HERE)


def log_line(msg: str) -> None:
    """Small startup log (app data folder) so a failed start can be diagnosed even though the exe has no console."""
    try:
        import time
        import app_config
        path = os.path.join(app_config.get_storage_dir(), "web_main.log")
        if os.path.exists(path) and os.path.getsize(path) > 200_000:
            os.remove(path)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
    except Exception:
        pass


def centered(w: int, h: int):
    """Top-left corner that puts a w x h window in the middle of the primary monitor's work area."""
    try:
        import ctypes
        from ctypes import wintypes
        r = wintypes.RECT()
        ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(r), 0)   # SPI_GETWORKAREA
        ww, wh = min(w, r.right - r.left), min(h, r.bottom - r.top)
        return ww, wh, r.left + (r.right - r.left - ww) // 2, r.top + (r.bottom - r.top - wh) // 2
    except Exception:
        return w, h, None, None


def main() -> int:
    try:
        return _main()
    except Exception:
        import traceback
        log_line("FATAL " + traceback.format_exc())
        raise


def _main() -> int:
    import webview
    from web_api import Api
    log_line(f"start args={sys.argv[1:]} frozen={getattr(sys, 'frozen', False)}")

    import web_tray
    mutex = True if os.environ.get("CS2CC_ALLOW_SECOND_INSTANCE") else web_tray.check_single_instance()   # env switch is for side-by-side testing only
    if mutex is None:
        log_line("another copy is running; asked it to show itself, exiting")
        return 0          # another copy is running; it was asked to show itself
    index = os.path.join(resource_dir(), "web", "index.html")
    if not os.path.exists(index):
        print(f"UI not built: {index} is missing. Run `npm run build` in desktop-ui.")
        return 2
    api = Api()
    hidden = "--minimized" in sys.argv
    ww, wh, wx, wy = centered(1400, 880)
    window = webview.create_window(
        "CS2 Command Center", url=index, js_api=api, width=ww, height=wh, x=wx, y=wy, min_size=(980, 640),
        frameless=True, easy_drag=False, background_color="#080a0e", text_select=False, hidden=hidden)
    api._attach(window)

    first = {"v": True}

    def on_shown():
        api.fix_window_style()                  # taskbar click minimizes, like any other window
        if first["v"]:
            first["v"] = False
            api.center_window()                 # only the first time, so restoring from the tray keeps your position

    def on_loaded():
        if "--elevated" in sys.argv:            # tell the standard copy that this elevated copy is up, so it can close
            api.signal_elevated_ready()
        log_line("window loaded")

    window.events.shown += on_shown
    window.events.loaded += on_loaded
    api.tray = web_tray.Tray(api)
    log_line("tray icon started" if api.tray.start() else "tray icon FAILED to start")
    web_tray.listen_for_show(api.show_window)
    import threading
    threading.Thread(target=lambda: (api.core.presence.start(), api.core.update_check_startup()), daemon=True, name="late-start").start()   # not needed for the first paint
    debug = bool(os.environ.get("CS2CC_DEBUG"))
    # WebView2 cannot share one data folder between a standard and an elevated process, so each gets its own.
    import app_config
    sp = os.path.join(app_config.get_storage_dir(), "webview2-admin" if "--elevated" in sys.argv else "webview2")
    os.makedirs(sp, exist_ok=True)
    if os.environ.get("CS2CC_BENCH"):
        webview.start(bench, window, debug=debug, storage_path=sp)
    elif os.environ.get("CS2CC_UPDATETEST"):
        webview.start(updatetest, (window, api), debug=debug, storage_path=sp)
    elif os.environ.get("CS2CC_SELFTEST"):
        webview.start(selftest, (window, api), debug=debug, storage_path=sp)
    else:
        webview.start(debug=debug, storage_path=sp)
    try:
        api.tray.stop()                       # a process that ends without this leaves a dead icon in the tray until the mouse passes over it
    except Exception:
        pass
    log_line("window closed")
    return 0


def updatetest(window, api) -> None:
    """Developer check (CS2CC_UPDATETEST=1): checks for an update and installs it, like pressing the two buttons, and logs each step."""
    import time
    time.sleep(6)
    r = api.update_check(True)
    if os.environ.get("CS2CC_UPDATETEST") == "quit":
        log_line("updatetest: quitting through Api.quit")
        api.quit()
        return
    log_line(f"updatetest check: {r}")
    if r.get("available"):
        log_line(f"updatetest install: {api.update_install()}")


def selftest(window, api) -> None:
    """Developer check (CS2CC_SELFTEST=1): calls every read-only API in this exact build and writes the result to cs2cc_selftest.txt in the temp folder."""
    import time
    import traceback
    time.sleep(4)
    names = ["app_info", "hw_info", "servers_catalog", "engine_state", "dashboard", "maint_state", "launch_state", "dns_state", "autoexec_state",
             "mpo_state", "settings_get", "maps_settings", "presence_state", "sniper_status", "start_page", "restore_summary", "log_history", "dns_status", "about", "diagnostics"]
    out = []
    for n in names:
        try:
            getattr(api, n)()
            out.append(f"ok   {n}")
        except Exception:
            out.append(f"FAIL {n}: {traceback.format_exc(limit=2).strip().splitlines()[-1]}")
    with open(os.path.join(os.environ.get("TEMP", "."), "cs2cc_selftest.txt"), "w", encoding="utf-8") as fh:
        fh.write(chr(10).join(out) + chr(10))
    window.destroy()


def bench(window) -> None:
    """Developer check: drag-resize the window 40 steps and report the page's frame gaps (CS2CC_BENCH=1)."""
    import time
    time.sleep(6)
    window.evaluate_js("window.__f=[];(function l(t){window.__f.push(t);requestAnimationFrame(l)})(performance.now())")
    steps = []
    for i in range(40):
        w, h = 1400 - (i % 20) * 15, 880 - (i % 12) * 10
        t0 = time.perf_counter()
        window.resize(w, h)
        time.sleep(0.016)
        steps.append((time.perf_counter() - t0) * 1000)
    time.sleep(0.3)
    gaps = window.evaluate_js("(function(){var f=window.__f,g=[];for(var i=1;i<f.length;i++)g.push(f[i]-f[i-1]);g.sort(function(a,b){return a-b});return [g.length,g[Math.floor(g.length/2)],g[Math.floor(g.length*.9)],g[g.length-1]]})()")
    steps.sort()
    out = (f"resize step ms: median {steps[len(steps)//2]:.1f} p90 {steps[int(len(steps)*.9)]:.1f} max {steps[-1]:.1f}\n"
           f"page frame gaps ms (count, median, p90, max): {gaps}\n")
    with open(os.path.join(os.environ.get("TEMP", "."), "cs2cc_bench.txt"), "w") as fh:
        fh.write(out)
    window.destroy()


if __name__ == "__main__":
    sys.exit(main())
