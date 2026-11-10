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
        if self._window:
            self._window.minimize()

    def win_maximize(self) -> None:
        if not self._window:
            return
        try:
            if getattr(self, "_max", False):
                self._window.restore()
            else:
                self._window.maximize()
            self._max = not getattr(self, "_max", False)
        except Exception:
            pass

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

    def win_close(self) -> None:
        if self._window:
            self._window.destroy()

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

    def servers_add(self, name: str, host: str, port: int) -> Dict[str, Any]:
        return self.core.servers_add(name, host, int(port))

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
