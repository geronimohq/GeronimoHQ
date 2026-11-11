"""
CS2 Command Center - Configuration & Windows Startup Manager
Manages weekly maintenance tracking, system tray preferences, and Windows Startup registry keys.
"""

import os
import sys
import json
import winreg
import datetime
import threading
import shutil
from typing import Dict, Any

def get_storage_dir() -> str:
    """Returns persistent app storage directory in %APPDATA%/CS2CommandCenter."""
    app_data = os.getenv("APPDATA")
    if app_data:
        base = os.path.join(app_data, "CS2CommandCenter")
    elif getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(__file__)
    os.makedirs(base, exist_ok=True)
    return base

CONFIG_FILE = os.path.join(get_storage_dir(), "command_center_config.json")
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_REG_NAME = "CS2CommandCenter"
DEFAULT_DISCORD_CLIENT_ID = "1567758921429422231"

DEFAULT_CONFIG = {
    "last_maintenance_timestamp": None,
    "last_optimization_timestamp": None,
    "start_with_windows": False,
    "start_minimized": False,
    "minimize_to_tray_on_close": True,
    "discord_rpc_enabled": True,
    "discord_client_id": DEFAULT_DISCORD_CLIENT_ID,
    "gfl_sniper_tier": "mapper"
}

# AUDIT P2-#6: every user-facing setting in the Settings dialog, with its default.
# One list used by Save, Reset and the round-trip test, so a setting can no longer be
# shown in the dialog but left out of the save (that was the "check for updates" bug).
SETTINGS_DEFAULTS: Dict[str, Any] = {
    "start_with_windows": False,
    "start_minimized": False,
    "minimize_to_tray_on_close": True,
    "open_on_page": "Dashboard",
    "sniper_sound_enabled": True,
    "server_refresh_speed": "Normal (5s)",
    # AUDIT P3-01: the Settings "Share with Discord" tick now drives the REAL switch
    # (discord_rpc_enabled, also on the Discord tab). The old key discord_presence_share
    # and the sniper volume slider were saved but never used by anything.
    "discord_rpc_enabled": True,
    "check_updates_on_startup": True,
}

# Server query interval on the ZE Game Servers page, per the "Server query speed" setting.
REFRESH_SPEED_MS = {"Live (1s)": 1000, "Normal (5s)": 5000, "Eco (15s)": 15000}


def refresh_interval_ms(cfg: Dict[str, Any]) -> int:
    return REFRESH_SPEED_MS.get(str(cfg.get("server_refresh_speed", "Normal (5s)")), 5000)


START_PAGES = {"Dashboard", "Last used page"}


def start_page_key(cfg: Dict[str, Any], valid_keys) -> str:
    """Page to open at start: Dashboard, or the page used last time (if it still exists)."""
    if cfg.get("open_on_page") == "Last used page":
        last = cfg.get("last_page_key")
        if last in valid_keys:
            return last
    return "DASHBOARD"


def apply_settings(cfg: Dict[str, Any], values: Dict[str, Any]) -> Dict[str, Any]:
    """Copies known settings from `values` into `cfg` (unknown keys are ignored)."""
    for key, default in SETTINGS_DEFAULTS.items():
        if key in values:
            val = values[key]
            if key == "open_on_page" and val not in START_PAGES:
                val = default
            if key == "server_refresh_speed" and val not in REFRESH_SPEED_MS:
                val = default
            if isinstance(default, bool):
                val = bool(val)
            elif isinstance(default, int):
                try:
                    val = max(0, min(100, int(round(float(val)))))
                except (TypeError, ValueError):
                    val = default
            cfg[key] = val
    return cfg


def reset_settings(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Restores Settings-dialog defaults IN PLACE, keeping everything else
    (presence_secret, discord_client_id, timestamps, sniper targets...).
    The old reset replaced the whole dict and silently deleted those keys."""
    for key, default in SETTINGS_DEFAULTS.items():
        cfg[key] = default
    return cfg


def load_config() -> Dict[str, Any]:
    cfg = dict(DEFAULT_CONFIG)
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if isinstance(saved, dict):
                    cfg.update(saved)
        except Exception:
            # An unreadable config used to reset every setting silently. Keep the damaged file so nothing is lost for good.
            try:
                shutil.copyfile(CONFIG_FILE, CONFIG_FILE + ".corrupt")
            except Exception:
                pass
    if not cfg.get("discord_client_id"):
        cfg["discord_client_id"] = DEFAULT_DISCORD_CLIENT_ID
    # Synchronize startup state with actual Windows registry
    cfg["start_with_windows"] = is_windows_startup_enabled()
    if cfg["start_with_windows"]:
        cfg["start_minimized"] = is_windows_startup_minimized()
    return cfg

_SAVE_LOCK = threading.Lock()


def save_config(cfg: Dict[str, Any]) -> bool:
    # AUDIT 1c-D6: atomic write (temp file + replace) so a crash or a full disk can
    # never leave a half-written config that silently resets every setting.
    # The lock and the per-thread temp name keep two saves at the same moment (Settings and a finishing job) from clobbering each other.
    tmp = f"{CONFIG_FILE}.{threading.get_ident()}.tmp"
    try:
        with _SAVE_LOCK:
            snapshot = json.dumps(cfg, indent=2)
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(snapshot)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, CONFIG_FILE)
        return True
    except Exception:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass
        return False

def get_days_since_maintenance(cfg: Dict[str, Any]) -> int:
    """Returns number of days since last maintenance, or 999 if never performed."""
    ts_str = cfg.get("last_maintenance_timestamp")
    if not ts_str:
        return 999
    try:
        dt = datetime.datetime.fromisoformat(ts_str)
        delta = datetime.datetime.now() - dt
        return max(0, delta.days)
    except Exception:
        return 999

def update_maintenance_timestamp(cfg: Dict[str, Any]) -> bool:
    cfg["last_maintenance_timestamp"] = datetime.datetime.now().isoformat()
    return save_config(cfg)

def get_days_since_optimization(cfg: Dict[str, Any]) -> int:
    """Returns number of days since last CS2 engine optimization, or 999 if never performed."""
    ts_str = cfg.get("last_optimization_timestamp")
    if not ts_str:
        return 999
    try:
        dt = datetime.datetime.fromisoformat(ts_str)
        delta = datetime.datetime.now() - dt
        return max(0, delta.days)
    except Exception:
        return 999

def update_optimization_timestamp(cfg: Dict[str, Any]) -> bool:
    cfg["last_optimization_timestamp"] = datetime.datetime.now().isoformat()
    return save_config(cfg)

def is_windows_startup_enabled() -> bool:
    """Checks if app is registered in HKCU Run registry key."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, APP_REG_NAME)
            return bool(val)
    except Exception:
        return False

def is_windows_startup_minimized() -> bool:
    """Checks if registered startup command contains --minimized."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, APP_REG_NAME)
            return "--minimized" in str(val)
    except Exception:
        return False

LEGACY_TASK_NAME = "CS2CommandCenter_AutoStart"


def legacy_elevated_task_exists() -> bool:
    import subprocess
    try:
        r = subprocess.run(["schtasks", "/query", "/tn", LEGACY_TASK_NAME], capture_output=True,
                           timeout=5, creationflags=0x08000000)
        return r.returncode == 0
    except Exception:
        return False


def migrate_legacy_startup_task() -> str:
    """AUDIT D-07 migration, run once in the background at app start: remove the elevated
    logon task older versions created. Returns "none" | "removed" | "needs_admin"."""
    if not legacy_elevated_task_exists():
        return "none"
    if remove_legacy_elevated_task() and not legacy_elevated_task_exists():
        return "removed"
    return "needs_admin"


def remove_legacy_elevated_task() -> bool:
    """Deletes the elevated logon task older versions created (no-op if it does not exist)."""
    import subprocess
    try:
        r = subprocess.run(["schtasks", "/delete", "/tn", LEGACY_TASK_NAME, "/f"],
                           capture_output=True, timeout=5, creationflags=0x08000000)
        return r.returncode == 0
    except Exception:
        return False


def set_windows_startup(enabled: bool, minimized: bool = False) -> bool:
    """
    Registers or unregisters the app executable in HKCU Run registry key.
    Automatically prevents Windows Explorer from silently suppressing startup by clearing
    any conflicting RUNASADMIN flags in AppCompatFlags Layers.
    """
    import subprocess
    exe_path = sys.executable
    # If running from python script directly, use pythonw or executable
    compiled_exe = None
    if "python.exe" in exe_path.lower():
        exe_dir = os.path.dirname(__file__)
        compiled_exe = os.path.join(exe_dir, "dist", "CS2_Command_Center.exe")
        if os.path.exists(compiled_exe):
            exe_path = compiled_exe

    success = False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            if enabled:
                cmd = f'"{exe_path}" --minimized' if minimized else f'"{exe_path}"'
                winreg.SetValueEx(key, APP_REG_NAME, 0, winreg.REG_SZ, cmd)
                success = True
            else:
                try:
                    winreg.DeleteValue(key, APP_REG_NAME)
                except FileNotFoundError:
                    pass
                success = True
    except Exception:
        pass

    # Ensure Windows Explorer does not silently block HKCU Run startup due to RUNASADMIN compatibility flags
    try:
        compat_key_path = r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, compat_key_path, 0, winreg.KEY_SET_VALUE) as k:
            for p in [exe_path, compiled_exe]:
                if p:
                    try:
                        winreg.DeleteValue(k, p)
                    except FileNotFoundError:
                        pass
    except Exception:
        pass

    # AUDIT D-07 (owner decision 2026-11-10): start as a normal user. Older versions ALSO
    # created a Task Scheduler task "/rl highest" (Administrator at every logon, and a second
    # copy next to the Run key). That task is no longer created, and any old one is removed.
    remove_legacy_elevated_task()

    return success
