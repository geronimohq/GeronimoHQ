"""JS-callable API for the web-window front end (pywebview js_api).

Every public method here is reachable from the page as `window.pywebview.api.<name>(...)` and returns a promise.
Keep methods thin: real work lives in core_service.Core.
"""
import ctypes
import json
import os
import threading
import time
from ctypes import wintypes
from typing import Any, Dict, List

from core_service import Core


class Api:
    def __init__(self):
        self._window = None
        self.core = Core(emit=self._emit)

    # wiring (not exposed: leading underscore)
    def _attach(self, window) -> None:
        self._window = window

    def _emit(self, event: str, data: Any) -> None:
        w = self._window
        if not w:
            return
        try:
            w.evaluate_js(f"window.__emit && window.__emit({json.dumps(event)}, {json.dumps(data)})")
        except Exception:
            pass

    # window controls
    def win_minimize(self) -> None:
        """[-]: hides to the tray when "Minimize to the system tray" is on, otherwise a normal minimize to the taskbar."""
        if not self._window:
            return
        try:
            tray = getattr(self, "tray", None)
            if self.core.config.get("minimize_to_tray_on_close", True):
                if tray and not tray.icon:
                    tray.start()                  # the icon failed earlier: try once more before giving up on the tray
                if tray and tray.icon:
                    self._window.hide()
                    self.core.log("Window hidden to the tray")
                    self.mem_trim(True)
                    return
            self._window.minimize()
            self.mem_trim(True)
        except Exception:
            pass

    def _hwnd(self) -> int:
        return int(self._window.native.Handle.ToInt64())

    def win_maximize(self) -> bool:
        """Maximize into the monitor's WORK area (the taskbar stays visible); a second call restores the old size."""
        if not self._window:
            return False
        try:
            user32 = ctypes.windll.user32
            hwnd = self._hwnd()
            if getattr(self, "_max_rect", None):
                l, t, r, b = self._max_rect
                self._max_rect = None
                user32.SetWindowPos(hwnd, 0, l, t, r - l, b - t, 0x0004 | 0x0010)
                self._emit("maximized", False)
                return False

            class MONITORINFO(ctypes.Structure):
                _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT), ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]

            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            self._max_rect = (rect.left, rect.top, rect.right, rect.bottom)
            mon = user32.MonitorFromWindow(hwnd, 2)             # MONITOR_DEFAULTTONEAREST
            info = MONITORINFO()
            info.cbSize = ctypes.sizeof(MONITORINFO)
            user32.GetMonitorInfoW(mon, ctypes.byref(info))
            w = info.rcWork
            user32.SetWindowPos(hwnd, 0, w.left, w.top, w.right - w.left, w.bottom - w.top, 0x0004 | 0x0010)
            self._emit("maximized", True)
            return True
        except Exception as e:
            self.core.log(f"[WINDOW] maximize failed: {e}")
            return False

    def win_resize(self, edge: str) -> None:
        """Called on mouse-down on a resize handle (n s e w ne nw se sw). A frameless Windows form has no native
        edge dragging, so follow the cursor until the left button is released."""
        if os.environ.get("CS2CC_DEBUG_RESIZE"):
            with open(os.path.join(os.environ.get("TEMP", "."), "cs2cc_resize.txt"), "a") as fh:
                fh.write("win_resize called: " + edge + "\n")
        if edge in ("n", "s", "e", "w", "ne", "nw", "se", "sw") and self._window:
            threading.Thread(target=self._resize_loop, args=(edge,), daemon=True, name="win-resize").start()

    def _resize_loop(self, edge: str) -> None:
        try:
            user32 = ctypes.windll.user32
            hwnd = int(self._window.native.Handle.ToInt64())
            rect, pt = wintypes.RECT(), wintypes.POINT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            user32.GetCursorPos(ctypes.byref(pt))
            sx, sy = pt.x, pt.y
            l, t, r, b = rect.left, rect.top, rect.right, rect.bottom
            min_w, min_h = 980, 640
            while user32.GetAsyncKeyState(0x01) & 0x8000:
                user32.GetCursorPos(ctypes.byref(pt))
                dx, dy = pt.x - sx, pt.y - sy
                nl, nt, nr, nb = l, t, r, b
                if "w" in edge:
                    nl = min(l + dx, r - min_w)
                if "e" in edge:
                    nr = max(r + dx, l + min_w)
                if "n" in edge:
                    nt = min(t + dy, b - min_h)
                if "s" in edge:
                    nb = max(b + dy, t + min_h)
                user32.SetWindowPos(hwnd, 0, nl, nt, nr - nl, nb - nt, 0x0004 | 0x0010)  # no z-order change, no activate
                time.sleep(0.006)
        except Exception as e:  # never break the UI; leave a trace for debugging
            self.core.log(f"[WINDOW] resize failed: {e}")

    def mem_trim(self, low: bool = True) -> None:
        """While the window is hidden or minimized: ask WebView2 for its low-memory mode and hand unused pages back to Windows
        (they come back on demand). Normal mode again as soon as the window is shown."""
        def work():
            try:
                import System
                from Microsoft.Web.WebView2.Core import CoreWebView2MemoryUsageTargetLevel as L

                def setlevel():
                    self._window.native.webview.CoreWebView2.MemoryUsageTargetLevel = L.Low if low else L.Normal
                self._window.native.Invoke(System.Action(setlevel))
            except Exception:
                pass
            if low:
                time.sleep(2.0)
                self._empty_working_sets()
        threading.Thread(target=work, daemon=True, name="mem-trim").start()

    @staticmethod
    def _empty_working_sets() -> None:
        """EmptyWorkingSet on this process and every process it started (the WebView2 helpers)."""
        try:
            k32, psapi = ctypes.windll.kernel32, ctypes.windll.psapi

            class PE(ctypes.Structure):
                _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD), ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_void_p),
                            ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD), ("th32ParentProcessID", wintypes.DWORD),
                            ("pcPriClassBase", ctypes.c_long), ("dwFlags", wintypes.DWORD), ("szExeFile", ctypes.c_wchar * 260)]
            snap = k32.CreateToolhelp32Snapshot(0x2, 0)
            pairs, e = [], PE()
            e.dwSize = ctypes.sizeof(PE)
            ok = k32.Process32FirstW(snap, ctypes.byref(e))
            while ok:
                pairs.append((e.th32ProcessID, e.th32ParentProcessID))
                ok = k32.Process32NextW(snap, ctypes.byref(e))
            k32.CloseHandle(snap)
            mine, grew = {os.getpid()}, True
            while grew:
                grew = False
                for pid, parent in pairs:
                    if parent in mine and pid not in mine:
                        mine.add(pid)
                        grew = True
            for pid in mine:
                h = k32.OpenProcess(0x0500, False, pid)       # PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION
                if h:
                    psapi.EmptyWorkingSet(h)
                    k32.CloseHandle(h)
        except Exception:
            pass

    def show_window(self) -> None:
        if self._window:
            try:
                self._window.show()
                self._window.restore()
                self.fix_window_style()
                self.mem_trim(False)
            except Exception:
                pass

    def win_close(self) -> None:
        """[X] always closes the application completely (the tray is for [-])."""
        self.quit()

    def quit(self) -> None:
        self.core.shutdown()
        if getattr(self, "tray", None):
            self.tray.stop()
        try:
            if self._window:
                self._window.destroy()
        finally:
            threading.Timer(1.5, lambda: os._exit(0)).start()

    def toggle_gfl_sniper(self) -> None:
        st = self.core.sniper_status()
        if st.get("active"):
            self.core.sniper_stop()
        else:
            self.core.sniper_start("gfl", 62)

    def toggle_startup(self) -> None:
        self.core.settings_save({"start_with_windows": not bool(self.core.config.get("start_with_windows", False)),
                                 "start_minimized": bool(self.core.config.get("start_minimized", False))})

    def set_last_page(self, page: str) -> None:
        self.core.set_last_page(page)

    def start_page(self) -> str:
        return self.core.start_page()

    # app
    def app_info(self) -> Dict[str, Any]:
        return self.core.app_info()

    def log_history(self) -> List[Dict[str, str]]:
        return self.core.log_history()

    def config_set(self, key: str, value: Any) -> bool:
        return self.core.config_set(key, value)

    # servers
    def servers_catalog(self) -> List[Dict[str, Any]]:
        return self.core.servers_catalog()

    def servers_status_many(self, ids: List[str]) -> List[Dict[str, Any]]:
        return self.core.servers_status_many(list(ids or []))

    def gfl_match(self) -> Dict[str, Any]:
        return self.core.gfl_match()

    def servers_totals(self) -> Dict[str, Any]:
        return self.core.servers_totals()

    def servers_add(self, name: str, host: str, port: int, region: str = "Community") -> Dict[str, Any]:
        return self.core.servers_add(name, host, int(port), region)

    def servers_remove(self, sid: str) -> bool:
        return self.core.servers_remove(sid)

    # engine tweaks
    def engine_state(self) -> Dict[str, Any]:
        return self.core.engine_state()

    def engine_apply(self, opts: Dict[str, Any]) -> Dict[str, Any]:
        return self.core.engine_apply(opts)

    def engine_restore(self) -> Dict[str, Any]:
        return self.core.engine_restore()

    def power_set(self, plan: str) -> Dict[str, Any]:
        return self.core.power_set(plan)

    def restore_summary(self) -> str:
        return self.core.restore_summary()

    # server actions
    def server_connect(self, sid: str) -> Dict[str, Any]:
        return self.core.server_connect(sid)

    def server_players(self, sid: str) -> Dict[str, Any]:
        return self.core.server_players(sid)

    def sniper_start(self, sid: str, max_players: int = 0) -> Dict[str, Any]:
        return self.core.sniper_start(sid)

    def sniper_tiers(self) -> Dict[str, Any]:
        return self.core.sniper_tiers()

    def sniper_set_tier(self, kind: str, value: str) -> Dict[str, Any]:
        return self.core.sniper_set_tier(kind, value)

    def map_thumb(self, map_name: str) -> str:
        return self.core.map_thumb(map_name)

    def sniper_stop(self) -> Dict[str, Any]:
        return self.core.sniper_stop()

    def sniper_status(self) -> Dict[str, Any]:
        return self.core.sniper_status()

    # dashboard, files, links, admin
    def dashboard(self) -> Dict[str, Any]:
        return self.core.dashboard()

    def open_path(self, kind: str) -> bool:
        return self.core.open_path(kind)

    def open_url(self, url: str) -> bool:
        return self.core.open_url(url)

    def relaunch_admin(self, page: str = "") -> Dict[str, Any]:
        """Starts an elevated copy on the same tab. This copy stays open until the elevated one reports that it is up, so
        a declined prompt or a failed start never leaves you without the app."""
        import web_tray
        flag = self._ready_flag()
        try:
            os.remove(flag)
        except OSError:
            pass
        web_tray.release_mutex()                    # the elevated copy must be able to take the single-instance lock
        r = self.core.relaunch_admin(page)          # blocks while Windows shows its permission prompt
        if not r.get("ok"):
            web_tray.reacquire_mutex()
            return r

        def wait_then_quit():
            for _ in range(120):                    # up to 30 s
                if os.path.exists(flag):
                    self.core.log("[ADMIN] Elevated copy is running; closing this one.")
                    try:
                        if self._window:
                            self._window.hide()
                        if getattr(self, "tray", None):
                            self.tray.stop()
                    finally:
                        os._exit(0)
                time.sleep(0.25)
            web_tray.reacquire_mutex()
            self.core.log("[ADMIN] The elevated copy did not start in time; staying open as a standard user. See web_main.log in the app data folder.")

        threading.Thread(target=wait_then_quit, daemon=True, name="relaunch-wait").start()
        return r

    def _ready_flag(self) -> str:
        import app_config
        return os.path.join(app_config.get_storage_dir(), "elevated_ready.flag")

    def signal_elevated_ready(self) -> None:
        try:
            with open(self._ready_flag(), "w") as fh:
                fh.write("ready")
        except Exception:
            pass

    def center_window(self) -> None:
        """Centre the window (its real size) in the primary monitor's work area."""
        try:
            user32 = ctypes.windll.user32
            hwnd = self._hwnd()
            r, wa = wintypes.RECT(), wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(r))
            user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(wa), 0)
            w, h = r.right - r.left, r.bottom - r.top
            x = wa.left + max(0, (wa.right - wa.left - w) // 2)
            y = wa.top + max(0, (wa.bottom - wa.top - h) // 2)
            user32.SetWindowPos(hwnd, 0, x, y, 0, 0, 0x0001 | 0x0004 | 0x0010)     # keep size, no z-order change, no activate
        except Exception as e:
            self.core.log(f"[WINDOW] centering failed: {e}")

    def fix_window_style(self) -> None:
        """A frameless Windows form has no minimize box, so a click on its taskbar button did nothing. Add it back."""
        try:
            user32 = ctypes.windll.user32
            hwnd = self._hwnd()
            style = user32.GetWindowLongW(hwnd, -16)
            user32.SetWindowLongW(hwnd, -16, style | 0x00020000 | 0x00080000)      # WS_MINIMIZEBOX | WS_SYSMENU
            user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0004 | 0x0020)   # keep size/position, apply the frame change
        except Exception as e:
            self.core.log(f"[WINDOW] style fix failed: {e}")

    # PC maintenance
    def maint_state(self) -> Dict[str, Any]:
        return self.core.maint_state()

    def maint_run(self, opts: Dict[str, Any]) -> Dict[str, Any]:
        return self.core.maint_run(opts)

    def maint_tool(self, name: str) -> Dict[str, Any]:
        return self.core.maint_tool(name)

    # launch options
    def launch_state(self) -> Dict[str, Any]:
        return self.core.launch_state()

    def launch_save(self, options: str) -> Dict[str, Any]:
        return self.core.launch_save(options)

    # live booster & DNS
    def boost_run(self) -> Dict[str, Any]:
        return self.core.boost_run()

    def cs2_running(self) -> bool:
        return self.core.cs2_running()

    def dns_state(self) -> Dict[str, Any]:
        return self.core.dns_state()

    def dns_benchmark(self) -> Dict[str, Any]:
        return self.core.dns_benchmark()

    def dns_apply(self, primary: str, secondary: str, name: str) -> Dict[str, Any]:
        return self.core.dns_apply(primary, secondary, name)

    def dns_restore(self) -> Dict[str, Any]:
        return self.core.dns_restore()

    # autoexec
    def autoexec_state(self) -> Dict[str, Any]:
        return self.core.autoexec_state()

    def autoexec_install(self) -> Dict[str, Any]:
        return self.core.autoexec_install()

    def autoexec_restore(self) -> Dict[str, Any]:
        return self.core.autoexec_restore()

    def autoexec_fps(self, fps: int) -> Dict[str, Any]:
        return self.core.autoexec_fps(int(fps))

    # GPU / MPO and settings
    def mpo_state(self) -> Dict[str, Any]:
        return self.core.mpo_state()

    def settings_get(self) -> Dict[str, Any]:
        return self.core.settings_get()

    def settings_save(self, values: Dict[str, Any]) -> Dict[str, Any]:
        return self.core.settings_save(values)

    def settings_reset(self) -> Dict[str, Any]:
        return self.core.settings_reset()

    # custom map cleaner
    def maps_settings(self) -> Dict[str, Any]:
        return self.core.maps_settings()

    def maps_scan(self, communities: List[str], protect_recent: bool) -> Dict[str, Any]:
        return self.core.maps_scan(list(communities or []), bool(protect_recent))

    def maps_delete(self, ids: List[str]) -> Dict[str, Any]:
        return self.core.maps_delete(list(ids or []))

    def maps_backup(self) -> Dict[str, Any]:
        return self.core.maps_backup()

    def maps_restore(self) -> Dict[str, Any]:
        return self.core.maps_restore()

    # discord presence
    def presence_state(self) -> Dict[str, Any]:
        return self.core.presence_state()

    def presence_toggle(self, enabled: bool) -> Dict[str, Any]:
        return self.core.presence_toggle(bool(enabled))

    def presence_clear(self) -> Dict[str, Any]:
        return self.core.presence_clear()

    def presence_standby(self) -> Dict[str, Any]:
        return self.core.presence_standby()

    def presence_broadcast(self, sid: str) -> Dict[str, Any]:
        return self.core.presence_broadcast(sid)

    # updates
    def update_check(self, manual: bool = True) -> Dict[str, Any]:
        return self.core.update_check(bool(manual))

    def update_skip(self, ver: str) -> bool:
        return self.core.update_skip(ver)

    def update_install(self) -> Dict[str, Any]:
        return self.core.update_install()

    # hardware banner, ZE customizer, manual autoexec edit, analyzer, custom DNS, VPK health
    def hw_info(self) -> Dict[str, Any]:
        return self.core.hw_info()

    def ze_customizer(self, opts: Dict[str, Any]) -> Dict[str, Any]:
        return self.core.ze_customizer(opts)

    def autoexec_save(self, text: str) -> Dict[str, Any]:
        return self.core.autoexec_save(text)

    def log_analyze(self) -> Dict[str, Any]:
        return self.core.log_analyze()

    def dns_custom(self, primary: str, secondary: str) -> Dict[str, Any]:
        return self.core.dns_custom(primary, secondary)

    def vpk_verify(self) -> Dict[str, Any]:
        return self.core.vpk_verify()

    def vpk_repair(self) -> Dict[str, Any]:
        return self.core.vpk_repair()

    def maps_quick_stats(self) -> Dict[str, Any]:
        return self.core.maps_quick_stats()

    def presence_refresh(self) -> Dict[str, Any]:
        return self.core.presence_refresh()

    # soundtrack, 3D map, DNS status, about
    def soundtrack(self, map_name: str) -> Dict[str, Any]:
        return self.core.soundtrack(map_name)

    def open_3d_map(self, map_name: str) -> bool:
        return self.core.open_3d_map(map_name)

    def open_youtube_search(self, title: str) -> bool:
        return self.core.open_youtube_search(title)

    def dns_status(self) -> Dict[str, Any]:
        return self.core.dns_status()

    def diagnostics(self) -> str:
        return self.core.diagnostics()

    def exe_sha256(self) -> str:
        return self.core.exe_sha256()

    def log_clear(self) -> bool:
        return self.core.log_clear()

    def about(self) -> Dict[str, Any]:
        return self.core.about()
