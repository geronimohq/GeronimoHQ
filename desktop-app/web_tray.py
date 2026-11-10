"""System tray icon and single-instance handling for the web-window front end."""
import ctypes
import os
import sys
import threading
import time

SINGLE_INSTANCE_MUTEX_NAME = "Local\\CS2CommandCenter_App_SingleInstance_Mutex"       # same names as the classic app, so the two
SINGLE_INSTANCE_EVENT_NAME = "Local\\CS2CommandCenter_App_ShowEvent"                   # never run side by side


def check_single_instance():
    """Returns a mutex handle if this is the only instance; otherwise signals the running one to show itself and returns None."""
    kernel32 = ctypes.windll.kernel32
    elevated = "--elevated" in sys.argv
    for _ in range(20 if elevated else 1):
        mutex = kernel32.CreateMutexW(None, True, SINGLE_INSTANCE_MUTEX_NAME)
        if kernel32.GetLastError() != 183:      # ERROR_ALREADY_EXISTS
            return mutex
        kernel32.CloseHandle(mutex)
        if not elevated:
            h = kernel32.OpenEventW(0x0002, False, SINGLE_INSTANCE_EVENT_NAME)
            if h:
                kernel32.SetEvent(h)
                kernel32.CloseHandle(h)
            return None
        time.sleep(0.1)
    return None


def listen_for_show(on_show) -> None:
    """Background thread: another launch of the app asks this instance to come to the front."""
    kernel32 = ctypes.windll.kernel32
    h = kernel32.CreateEventW(None, False, False, SINGLE_INSTANCE_EVENT_NAME)
    if not h:
        return

    def loop():
        while True:
            if kernel32.WaitForSingleObject(h, 500) == 0:
                try:
                    on_show()
                except Exception:
                    pass

    threading.Thread(target=loop, daemon=True, name="show-event").start()


def tray_image():
    from PIL import Image, ImageDraw
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    for name in ("app.png",):
        p = os.path.join(base, name)
        if os.path.exists(p):
            try:
                return Image.open(p).resize((64, 64))
            except Exception:
                pass
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((4, 4, 60, 60), fill=(255, 158, 27, 255))
    d.text((16, 24), "CS2", fill=(20, 18, 4, 255))
    return img


class Tray:
    def __init__(self, api):
        self.api = api
        self.icon = None

    def start(self) -> bool:
        try:
            import pystray
            core = self.api.core
            menu = pystray.Menu(
                pystray.MenuItem("Open CS2 Command Center", lambda i, it: self.api.show_window(), default=True),
                pystray.MenuItem("Quick connect: GFL ZE", lambda i, it: core.server_connect("gfl")),
                pystray.MenuItem("Slot Sniper: toggle GFL", lambda i, it: self.api.toggle_gfl_sniper()),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Start with Windows", lambda i, it: self.api.toggle_startup(),
                                 checked=lambda it: bool(core.config.get("start_with_windows", False))),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit completely", lambda i, it: self.api.quit()),
            )
            self.icon = pystray.Icon("CS2CommandCenter", tray_image(), "CS2 Command Center", menu)
            self.icon.run_detached()
            return True
        except Exception:
            self.icon = None
            return False

    def stop(self) -> None:
        try:
            if self.icon:
                self.icon.stop()
        except Exception:
            pass
