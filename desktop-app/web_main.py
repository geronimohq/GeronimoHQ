"""CS2 Command Center, web-window front end. Run: python web_main.py   (UI files are built into ./web by desktop-ui)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def resource_dir() -> str:
    return getattr(sys, "_MEIPASS", HERE)


def main() -> int:
    import webview
    from web_api import Api

    import web_tray
    mutex = True if os.environ.get("CS2CC_ALLOW_SECOND_INSTANCE") else web_tray.check_single_instance()   # env switch is for side-by-side testing only
    if mutex is None:
        return 0          # another copy is running; it was asked to show itself
    index = os.path.join(resource_dir(), "web", "index.html")
    if not os.path.exists(index):
        print(f"UI not built: {index} is missing. Run `npm run build` in desktop-ui.")
        return 2
    api = Api()
    hidden = "--minimized" in sys.argv
    window = webview.create_window(
        "CS2 Command Center", url=index, js_api=api, width=1400, height=880, min_size=(980, 640),
        frameless=True, easy_drag=False, background_color="#080a0e", text_select=False, hidden=hidden)
    api._attach(window)
    api.tray = web_tray.Tray(api)
    api.tray.start()
    web_tray.listen_for_show(api.show_window)
    api.core.presence.start()
    api.core.update_check_startup()
    debug = bool(os.environ.get("CS2CC_DEBUG"))
    if os.environ.get("CS2CC_BENCH"):
        webview.start(bench, window, debug=debug)
    elif os.environ.get("CS2CC_SELFTEST"):
        webview.start(selftest, (window, api), debug=debug)
    else:
        webview.start(debug=debug)
    return 0


def selftest(window, api) -> None:
    """Developer check (CS2CC_SELFTEST=1): calls every read-only API in this exact build and writes the result to cs2cc_selftest.txt in the temp folder."""
    import time
    import traceback
    time.sleep(4)
    names = ["app_info", "hw_info", "servers_catalog", "engine_state", "dashboard", "maint_state", "launch_state", "dns_state", "autoexec_state",
             "mpo_state", "settings_get", "maps_settings", "presence_state", "sniper_status", "start_page", "restore_summary", "log_history"]
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
