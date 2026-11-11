"""Checks that the Microsoft Edge WebView2 runtime (what draws the app window) is installed, and explains what to do when it is not.

Without it pywebview silently falls back to an old engine and the window stays blank, which looks like a broken app. Windows 11 and
up-to-date Windows 10 have it; older or stripped-down Windows installs may not.
"""
import glob
import os
import winreg
from typing import Optional

CLIENT_GUID = "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"          # the Evergreen runtime's registration id
DOWNLOAD_PAGE = "https://developer.microsoft.com/microsoft-edge/webview2/"


def runtime_version() -> Optional[str]:
    """Installed runtime version like '157.0.4341.42', or None when it is not installed."""
    spots = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\\" + CLIENT_GUID),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\EdgeUpdate\Clients\\" + CLIENT_GUID),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\EdgeUpdate\Clients\\" + CLIENT_GUID),
    ]
    for hive, sub in spots:
        try:
            with winreg.OpenKey(hive, sub.replace("\\\\", "\\")) as k:
                ver = str(winreg.QueryValueEx(k, "pv")[0]).strip()
                if ver and ver != "0.0.0.0":
                    return ver
        except OSError:
            continue
    for base in (os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"), os.environ.get("ProgramFiles", r"C:\Program Files")):
        found = sorted(glob.glob(os.path.join(base, "Microsoft", "EdgeWebView", "Application", "*", "msedgewebview2.exe")))
        if found:
            return os.path.basename(os.path.dirname(found[-1]))
    return None


def explain_and_offer_install() -> None:
    """A plain message box (this is a windowed exe, so nothing printed would ever be seen) with a button to open Microsoft's download page."""
    try:
        import ctypes
        text = ("CS2 Command Center needs the Microsoft Edge WebView2 Runtime to draw its window, and it is not installed on this PC.\n\n"
                "It is a free Microsoft component. Open the download page now? Install the 'Evergreen Bootstrapper', then start CS2 Command Center again.")
        answer = ctypes.windll.user32.MessageBoxW(None, text, "CS2 Command Center", 0x00000004 | 0x00000030)    # MB_YESNO | MB_ICONWARNING
        if answer == 6:                                                                                         # IDYES
            os.startfile(DOWNLOAD_PAGE)
    except Exception:
        pass
