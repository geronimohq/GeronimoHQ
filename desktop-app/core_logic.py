"""
CS2 FPS Optimizer & Stutter Fixer
Core optimization logic - Community Edition
Universal hardware safety, custom binds preservation, and safe PC maintenance tools
"""

import os
import sys
import shutil
import datetime
import winreg
import subprocess
import ctypes
from ctypes import wintypes
import re
import glob
import socket
import struct
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

PROCESS_ALL_ACCESS = 0x1F0FFF
PROCESS_SET_INFORMATION = 0x0200
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
HIGH_PRIORITY_CLASS = 0x00000080
CREATE_NO_WINDOW = 0x08000000

GUID_BALANCED = "381b4222-f694-41f0-9685-ff5bb260df2e"
GUID_HIGH_PERF = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"

PERF_HEADER = "// ============================================================\n// [CS2 FPS OPTIMIZER - PERFORMANCE TWEAKS]\n// ============================================================"

PERF_BLOCK = """// ============================================================
// [CS2 FPS OPTIMIZER - PERFORMANCE TWEAKS]
// Added by CS2 Command Center (hobby project, not affiliated with Valve).
// UNDO: 1) delete everything from this header to the END line below,
//          or use Restore in the app;
//       2) CS2 remembers some values after a restart, so also type these
//          in the CS2 console (common defaults - check your own):
//          fps_max 400; engine_low_latency_sleep_after_client_tick 0;
//          rate 786432; snd_headphone_eq 0;
//          cl_allow_animated_avatars 1; cl_hud_telemetry_frametime_show 0;
//          cl_hud_telemetry_ping_show 0; cl_hud_telemetry_net_misdelivery_show 0
// ============================================================
fps_max 0                                   // Uncaps max FPS for lowest input latency
engine_low_latency_sleep_after_client_tick true  // Synchronizes engine ticks to reduce frame stutter
snd_mixahead "0.025"                        // Low audio buffer (0.025s) reduces sound delay & spikes
snd_headphone_eq "0"                        // Disables headphone EQ DSP for lowest CPU overhead
snd_spatialize_lerp "1"
rate "1000000"                              // max bytes/s (about 8 Mbps; CS2 may cap it lower)
cl_net_buffer_ticks "0"                     // Minimum interpolation delay (fastest packet processing)
cl_allow_animated_avatars "0"               // Disables animated Steam avatars (fixes scoreboard FPS drop)
r_player_visibility_mode "1"                // Enhances enemy contrast
cl_hud_telemetry_frametime_show "2"         // Shows frametime graph if a micro-stutter occurs
cl_hud_telemetry_ping_show "2"              // Real-time ping display
cl_hud_telemetry_net_misdelivery_show "2"   // Real-time packet loss / choke notification
cl_ragdoll_workaround_threshold "0"

echo "[CS2 FPS Optimizer] Performance tweaks & custom binds loaded successfully!"
// [CS2 FPS OPTIMIZER - PERFORMANCE TWEAKS END]
"""

PERF_TITLE = "[CS2 FPS OPTIMIZER - PERFORMANCE TWEAKS]"
PERF_END = "// [CS2 FPS OPTIMIZER - PERFORMANCE TWEAKS END]"
_PERF_OLD_LAST_LINE = 'echo "[CS2 FPS Optimizer] Performance tweaks'


def split_perf_block(content: str) -> Tuple[str, str, str]:
    """AUDIT P2-#9: (before, block, after) for the app's performance block.
    Before this fix, install/restore kept only the text BEFORE the block and silently
    deleted everything after it (for example a ZE Studio block added later)."""
    t = content.find(PERF_TITLE)
    if t == -1:
        return content, "", ""
    line_start = content.rfind("\n", 0, t) + 1
    prev = content.rfind("\n", 0, max(0, line_start - 1)) + 1
    if content[prev:line_start].startswith("// ======"):
        line_start = prev  # include the "// ====" line above the title
    e = content.find(PERF_END, t)
    if e != -1:
        e = content.find("\n", e)
        e = len(content) if e == -1 else e + 1
    else:
        e = content.find(_PERF_OLD_LAST_LINE, t)  # blocks written by older versions
        if e != -1:
            e = content.find("\n", e)
            e = len(content) if e == -1 else e + 1
        else:
            e = len(content)  # unknown shape: same as before (block runs to the end)
    return content[:line_start], content[line_start:e], content[e:]

def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

def find_steam_path() -> Optional[str]:
    """Steam's install folder (registry, uninstall entry, fixed-drive defaults). See steam_paths.py."""
    import steam_paths
    return steam_paths.find_steam_path()


def get_steam_active_persona(steam_path: Optional[str] = None) -> Optional[str]:
    """Reads Steam's loginusers.vdf to find the user's active Steam Persona Name."""
    try:
        if not steam_path:
            steam_path = find_steam_path()
        if not steam_path:
            return None
        vdf_path = os.path.join(steam_path, "config", "loginusers.vdf")
        if not os.path.exists(vdf_path):
            return None
        with open(vdf_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        user_blocks = re.findall(r'"(\d{17})"\s*\{([^}]+)\}', content)
        for sid, block in user_blocks:
            if re.search(r'"MostRecent"\s+"1"', block) or re.search(r'"AutoLogin"\s+"1"', block):
                m = re.search(r'"PersonaName"\s+"([^"]+)"', block)
                if m:
                    return m.group(1).strip()
        m = re.search(r'"PersonaName"\s+"([^"]+)"', content)
        if m:
            return m.group(1).strip()
    except Exception:
        pass
    return None

def find_cs2_paths() -> Dict[str, Optional[str]]:
    """Steam, the CS2 install, its cfg folder and autoexec.cfg. The library that Steam's own appmanifest_730.acf points to wins,
    and a custom install folder name is honoured. See steam_paths.py."""
    import steam_paths
    steam_path = find_steam_path()
    result: Dict[str, Optional[str]] = {"steam_path": steam_path, "cs2_dir": None, "cs2_exe": None, "cfg_dir": None, "autoexec_cfg": None}
    result.update(steam_paths.find_cs2(steam_paths.steam_libraries(steam_path)))
    return result

# ----------------- CS2 OPTIMIZATIONS -----------------

def clean_shader_caches() -> Tuple[int, int, List[str]]:
    """Cleans DirectX, NVIDIA, AMD, and Intel shader caches. Returns (deleted_files, freed_bytes, logs)."""
    logs = []
    deleted_files = 0
    freed_bytes = 0
    
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    app_data = os.environ.get("APPDATA", "")
    
    target_dirs = []
    if local_app_data:
        target_dirs.extend([
            os.path.join(local_app_data, "D3DSCache"),
            os.path.join(local_app_data, "NVIDIA", "DXCache"),
            os.path.join(local_app_data, "NVIDIA", "GLCache"),
            os.path.join(local_app_data, "AMD", "DxCache"),
            os.path.join(local_app_data, "Intel", "ShaderCache"),
            os.path.join(os.path.dirname(local_app_data), "LocalLow", "Intel", "ShaderCache"),      # Intel keeps a second cache under LocalLow
        ])
    if app_data:
        target_dirs.append(os.path.join(app_data, "NVIDIA", "ComputeCache"))

    for folder in target_dirs:
        if not os.path.exists(folder):
            continue
        folder_deleted = 0
        folder_freed = 0
        try:
            for root, dirs, files in os.walk(folder, topdown=False):
                for f in files:
                    file_path = os.path.join(root, f)
                    try:
                        sz = os.path.getsize(file_path)
                        os.remove(file_path)
                        folder_deleted += 1
                        folder_freed += sz
                    except PermissionError:
                        continue
                    except Exception:
                        continue
            deleted_files += folder_deleted
            freed_bytes += folder_freed
            mb = folder_freed / (1024 * 1024)
            if folder_deleted > 0:
                logs.append(f"[SHADERS] Cleaned {folder_deleted} files from {os.path.basename(folder)} ({mb:.1f} MB)")
        except Exception as e:
            logs.append(f"[NOTICE] Shader cache access: {e}")

    return deleted_files, freed_bytes, logs

def clean_cs2_temp_dumps(cs2_dir: Optional[str]) -> Tuple[int, int, List[str]]:
    """Cleans CS2 .dmp crash files, logs, and WER CrashDumps. Returns (deleted_files, freed_bytes, logs)."""
    logs = []
    deleted = 0
    freed = 0

    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        cdump_dir = os.path.join(local_app_data, "CrashDumps")
        if os.path.exists(cdump_dir):
            for pattern in ["*cs2*.dmp", "*csgo*.dmp"]:
                for fp in glob.glob(os.path.join(cdump_dir, pattern)):
                    try:
                        sz = os.path.getsize(fp)
                        os.remove(fp)
                        deleted += 1
                        freed += sz
                    except Exception:
                        pass

    if cs2_dir and os.path.exists(cs2_dir):
        # Crash dumps only. Never "*.log" outside the dumps folder: game/csgo/console.log is what the Log Analyzer and the Discord
        # server detection read, and other tools keep their logs there too.
        check_folders = [
            (os.path.join(cs2_dir, "game", "bin", "win64"), ["*.dmp", "crash_*.txt"]),
            (os.path.join(cs2_dir, "game", "csgo"), ["*.dmp", "crash_*.txt"]),
            (os.path.join(cs2_dir, "game", "csgo", "dumps"), ["*.dmp", "*.mdmp", "*.tmp", "*.log", "crash_*.txt"]),
        ]
        for folder, patterns in check_folders:
            if not os.path.exists(folder):
                continue
            for ext in patterns:
                for fp in glob.glob(os.path.join(folder, ext)):
                    try:
                        sz = os.path.getsize(fp)
                        os.remove(fp)
                        deleted += 1
                        freed += sz
                    except Exception:
                        pass

    mb = freed / (1024 * 1024)
    if deleted == 0:
        logs.append("[ALREADY] No CS2 crash dumps or temporary files were found; nothing to clean.")
    else:
        logs.append(f"[SUCCESS] Cleaned {deleted} CS2 crash dumps & temporary files ({mb:.1f} MB freed).")
    return deleted, freed, logs

def _reg_value(root, path: str, name: str):
    """Current registry value, or None when it is missing or cannot be read (then the caller simply writes it)."""
    try:
        with winreg.OpenKey(root, path) as k:
            return winreg.QueryValueEx(k, name)[0]
    except Exception:
        return None


_DVR_KEY = r"System\GameConfigStore"
_DVR_KEY2 = r"Software\Microsoft\Windows\CurrentVersion\GameDVR"
_DVR_ON_VALUES = (("GameDVR_Enabled", 0), ("GameDVR_FSEBehaviorMode", 2), ("GameDVR_HonorUserFSEBehaviorMode", 1), ("GameDVR_DXGIHonorFSEWindowsCompatible", 1))
_DVR_OFF_VALUES = (("GameDVR_Enabled", 1), ("GameDVR_FSEBehaviorMode", 0), ("GameDVR_HonorUserFSEBehaviorMode", 0), ("GameDVR_DXGIHonorFSEWindowsCompatible", 0))


def _dvr_is(values, capture: int) -> bool:
    return all(_reg_value(winreg.HKEY_CURRENT_USER, _DVR_KEY, n) == v for n, v in values) and \
        _reg_value(winreg.HKEY_CURRENT_USER, _DVR_KEY2, "AppCaptureEnabled") == capture


def optimize_windows_game_dvr() -> List[str]:
    logs = []
    if _dvr_is(_DVR_ON_VALUES, 0):
        return ["[ALREADY] Game DVR background recording is already off in Windows; nothing was changed."]
    try:
        key_path = r"System\GameConfigStore"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as k:
            winreg.SetValueEx(k, "GameDVR_Enabled", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(k, "GameDVR_FSEBehaviorMode", 0, winreg.REG_DWORD, 2)
            winreg.SetValueEx(k, "GameDVR_HonorUserFSEBehaviorMode", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(k, "GameDVR_DXGIHonorFSEWindowsCompatible", 0, winreg.REG_DWORD, 1)
        logs.append("[SUCCESS] Disabled Game DVR background recording in GameConfigStore")
    except Exception as e:
        logs.append(f"[ERROR] Could not tweak GameConfigStore: {e}")

    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\GameDVR"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as k:
            winreg.SetValueEx(k, "AppCaptureEnabled", 0, winreg.REG_DWORD, 0)
        logs.append("[SUCCESS] Disabled background recording in GameDVR")
    except Exception as e:
        logs.append(f"[ERROR] Could not tweak AppCaptureEnabled: {e}")

    return logs

def revert_windows_game_dvr() -> List[str]:
    logs = []
    if _dvr_is(_DVR_OFF_VALUES, 1):
        return ["[ALREADY] Game DVR settings are already at the Windows defaults; nothing was changed."]
    try:
        key_path = r"System\GameConfigStore"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as k:
            winreg.SetValueEx(k, "GameDVR_Enabled", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(k, "GameDVR_FSEBehaviorMode", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(k, "GameDVR_HonorUserFSEBehaviorMode", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(k, "GameDVR_DXGIHonorFSEWindowsCompatible", 0, winreg.REG_DWORD, 0)
        logs.append("[REVERTED] Restored GameConfigStore GameDVR & FSE behavior flags to Windows defaults")
    except Exception as e:
        logs.append(f"[ERROR] Failed reverting GameConfigStore: {e}")

    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\GameDVR"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as k:
            winreg.SetValueEx(k, "AppCaptureEnabled", 0, winreg.REG_DWORD, 1)
        logs.append("[REVERTED] Restored AppCaptureEnabled to default (1)")
    except Exception as e:
        logs.append(f"[ERROR] Failed reverting GameDVR: {e}")
    return logs

def disable_fullscreen_optimizations(cs2_exe_path: str) -> List[str]:
    logs = []
    if not cs2_exe_path or not os.path.exists(cs2_exe_path):
        logs.append("[WARN] cs2.exe path not found.")
        return logs

    try:
        key_path = r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"
        val = "~ DISABLEDXMAXIMIZEDWINDOWEDMODE HIGHDPIAWARE"
        if _reg_value(winreg.HKEY_CURRENT_USER, key_path, cs2_exe_path) == val:
            return [f"[ALREADY] Fullscreen Optimizations are already disabled for {os.path.basename(cs2_exe_path)}; nothing was changed."]
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as k:
            winreg.SetValueEx(k, cs2_exe_path, 0, winreg.REG_SZ, val)
        logs.append(f"[SUCCESS] Disabled Fullscreen Optimizations for {os.path.basename(cs2_exe_path)}")
    except Exception as e:
        logs.append(f"[ERROR] Registry write failed: {e}")
    return logs

def revert_fullscreen_optimizations(cs2_exe_path: str) -> List[str]:
    logs = []
    if not cs2_exe_path:
        return ["[WARN] cs2.exe path not found."]
    try:
        key_path = r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as k:
            winreg.DeleteValue(k, cs2_exe_path)
        logs.append(f"[REVERTED] Restored default fullscreen settings for {os.path.basename(cs2_exe_path)}")
    except FileNotFoundError:
        logs.append(f"[ALREADY] No custom fullscreen flag was set for {os.path.basename(cs2_exe_path)}; nothing to restore.")
    except Exception as e:
        logs.append(f"[ERROR] Failed reverting fullscreen flag: {e}")
    return logs

def install_autoexec(cfg_dir: str) -> Tuple[bool, List[str]]:
    logs = []
    if not cfg_dir or not os.path.exists(cfg_dir):
        logs.append("[ERROR] CS2 cfg directory not found!")
        return False, logs

    autoexec_file = os.path.join(cfg_dir, "autoexec.cfg")
    backup_file = os.path.join(cfg_dir, "autoexec_backup.cfg")

    existing_content = ""
    if os.path.exists(autoexec_file):
        try:
            with open(autoexec_file, "r", encoding="utf-8", errors="ignore") as f:
                existing_content = f.read()
            if not os.path.exists(backup_file):
                shutil.copyfile(autoexec_file, backup_file)
                logs.append(f"[BACKUP] Created backup of your original autoexec.cfg to autoexec_backup.cfg")
        except Exception as e:
            logs.append(f"[WARN] Notice reading existing autoexec: {e}")

    before, block, after = split_perf_block(existing_content)
    if block:
        # Replace our block where it is; keep everything before AND after it.
        new_content = before + PERF_BLOCK + (("\n" + after.lstrip("\n")) if after.strip() else "")
        logs.append("[PRESERVED] Replaced only the app's performance block; your other lines were kept.")
    elif existing_content.strip():
        new_content = existing_content.rstrip() + "\n\n" + PERF_BLOCK
        logs.append("[PRESERVED] Your existing lines were kept; the performance block was added at the end.")
    else:
        new_content = PERF_BLOCK

    if os.path.exists(autoexec_file) and new_content.replace("\r\n", "\n") == existing_content.replace("\r\n", "\n"):
        return True, ["[ALREADY] autoexec.cfg already has the app's performance block exactly as it would be written; nothing was changed."]
    try:
        with open(autoexec_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        logs.append(f"[SUCCESS] Appended performance tweaks to autoexec.cfg without overwriting your binds!")
        return True, logs
    except Exception as e:
        logs.append(f"[ERROR] Failed to save autoexec: {e}")
        return False, logs

# AUDIT P2-#1: every marker this app writes into autoexec.cfg. The Dashboard used to
# look for "// --- CS2 COMMAND CENTER" and "GERONIMOHQ", which this app never writes,
# so it said "not edited by this app" even right after the app edited the file.
APP_AUTOEXEC_MARKERS = (
    "[CS2 FPS OPTIMIZER - PERFORMANCE TWEAKS]",          # install_autoexec / PERF_BLOCK
    "[CS2 COMMAND CENTER: ZE VISUAL, HUD",               # apply_ze_visual_and_hud_customizer
    "GERONIMOHQ",                                        # website generator header
)


def file_sha256(path: str) -> Optional[str]:
    import hashlib
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def get_autoexec_status(cfg_dir: Optional[str], app_save_record: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Reads autoexec.cfg from disk NOW and says plainly what the app knows about it.

    state: "no_cfg_dir" | "missing" | "unreadable" | "app_block" | "app_saved" | "user"
    app_save_record: {"path", "sha256", "time"} stored when the in-app editor saved the
    file; "app_saved" is only reported while the file still has exactly that content.
    """
    if not cfg_dir:
        return {"state": "no_cfg_dir", "path": None, "text": "Autoexec: CS2 cfg folder not found"}
    path = os.path.join(cfg_dir, "autoexec.cfg")
    if not os.path.isfile(path):
        short = f"...{cfg_dir[-18:]}\\autoexec.cfg" if len(cfg_dir) > 22 else "cfg\\autoexec.cfg"
        return {"state": "missing", "path": path, "text": f"Autoexec: not found at {short}"}
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return {"state": "unreadable", "path": path, "text": "Autoexec: found (could not be read)"}
    if any(m in content for m in APP_AUTOEXEC_MARKERS):
        return {"state": "app_block", "path": path,
                "text": "Autoexec: found (includes settings written by this app)"}
    rec = app_save_record or {}
    if rec.get("sha256") and os.path.normcase(str(rec.get("path", ""))) == os.path.normcase(path) \
            and rec.get("sha256") == file_sha256(path):
        when = rec.get("time") or ""
        return {"state": "app_saved", "path": path,
                "text": f"Autoexec: found (last saved in this app{(' at ' + when) if when else ''})"}
    return {"state": "user", "path": path, "text": "Autoexec: found (no section written by this app)"}


def restore_autoexec_backup(cfg_dir: str) -> Tuple[bool, List[str]]:
    logs = []
    if not cfg_dir:
        return False, ["[ERROR] CS2 cfg directory not specified!"]
    backup_file = os.path.join(cfg_dir, "autoexec_backup.cfg")
    autoexec_file = os.path.join(cfg_dir, "autoexec.cfg")

    if os.path.exists(backup_file):
        try:
            if os.path.exists(autoexec_file) and file_sha256(autoexec_file) == file_sha256(backup_file):
                return True, ["[ALREADY] autoexec.cfg already matches your original backup; nothing was changed."]
            shutil.copyfile(backup_file, autoexec_file)
            logs.append("[REVERTED] Successfully restored your exact original autoexec.cfg from backup!")
            return True, logs
        except Exception as e:
            logs.append(f"[ERROR] Failed to restore backup: {e}")
            return False, logs
    else:
        if os.path.exists(autoexec_file):
            try:
                with open(autoexec_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if PERF_TITLE in content:
                    before, _block, after = split_perf_block(content)
                    cleaned = (before.rstrip() + ("\n\n" + after.lstrip("\n") if after.strip() else "")).strip("\n")
                    with open(autoexec_file, "w", encoding="utf-8") as f:
                        f.write(cleaned + "\n")
                    logs.append("[REVERTED] Removed performance block from autoexec.cfg while leaving your binds intact.")
                    return True, logs
            except Exception as e:
                logs.append(f"[ERROR] Could not clean autoexec: {e}")
                return False, logs
        logs.append("[ALREADY] autoexec.cfg has no block from this app and there is no backup to restore; nothing was changed.")
        return True, logs

def set_framerate_limit(cfg_dir: str, fps: int) -> Tuple[bool, List[str]]:
    """Updates fps_max in autoexec.cfg for optimal in-engine frame pacing."""
    logs = []
    if not cfg_dir or not os.path.exists(cfg_dir):
        return False, ["[ERROR] CS2 cfg directory not found!"]
    autoexec_file = os.path.join(cfg_dir, "autoexec.cfg")
    content = ""
    if os.path.exists(autoexec_file):
        try:
            with open(autoexec_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            pass

    val_str = str(fps) if fps > 0 else "0"
    current = re.findall(r'^\s*fps_max\s+"?(\d+)"?', content, re.MULTILINE)
    if current and all(c == val_str for c in current):
        return True, [f"[ALREADY] autoexec.cfg already sets fps_max {val_str}; nothing was changed."]
    if re.search(r'^\s*fps_max\s+"?\d+"?', content, re.MULTILINE):
        content = re.sub(r'^\s*fps_max\s+"?\d+"?.*$', f"fps_max {val_str}                                   // Framerate limit", content, flags=re.MULTILINE)
    else:
        content = f"fps_max {val_str}\n" + content

    try:
        with open(autoexec_file, "w", encoding="utf-8") as f:
            f.write(content)
        logs.append(f"[AUTOEXEC] Set in-game framerate limit to: fps_max {val_str}")
        return True, logs
    except Exception as e:
        logs.append(f"[ERROR] Could not update fps_max: {e}")
        return False, logs

def get_active_power_plan() -> Tuple[str, str]:
    """Returns active power plan friendly name and GUID in <1ms via pure Win32 API without spawning cmd or powercfg."""
    try:
        powrprof = ctypes.windll.powrprof
        class GUID(ctypes.Structure):
            _fields_ = [
                ("Data1", wintypes.DWORD),
                ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD),
                ("Data4", wintypes.BYTE * 8)
            ]
        p_guid = ctypes.POINTER(GUID)()
        if powrprof.PowerGetActiveScheme(None, ctypes.byref(p_guid)) == 0:
            name_buf = (ctypes.c_wchar * 256)()
            buf_size = wintypes.DWORD(512)
            if powrprof.PowerReadFriendlyName(None, p_guid, None, None, name_buf, ctypes.byref(buf_size)) == 0:
                name = name_buf.value.strip()
                guid_str = f"{p_guid.contents.Data1:08x}-{p_guid.contents.Data2:04x}-{p_guid.contents.Data3:04x}-{''.join(f'{b:02x}' for b in p_guid.contents.Data4[:2])}-{''.join(f'{b:02x}' for b in p_guid.contents.Data4[2:])}"
                return name or "Balanced", guid_str
    except Exception:
        pass

    # Fallback with hidden console flag
    try:
        out = subprocess.check_output("powercfg /getactivescheme", shell=True, text=True, creationflags=0x08000000)
        m = re.search(r"GUID:\s+([a-f0-9\-]+)\s+\((.*?)\)", out, re.IGNORECASE)
        if m:
            return m.group(2).strip(), m.group(1).strip()
    except Exception:
        pass
    return "Balanced", ""

_GUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def remember_power_plan(cfg: Dict[str, Any]) -> None:
    """AUDIT P6: store the user's plan ONCE, before the app first changes it, so
    Restore Defaults can put it back (it used to always switch to Balanced)."""
    if cfg.get("power_plan_before_app"):
        return
    name, guid = get_active_power_plan()
    if guid and _GUID_RE.match(guid):
        cfg["power_plan_before_app"] = {"guid": guid, "name": name}


def restore_previous_power_plan(cfg: Dict[str, Any]) -> List[str]:
    """Restore the plan recorded by remember_power_plan(); Balanced if none was recorded."""
    rec = cfg.get("power_plan_before_app") or {}
    guid = str(rec.get("guid", ""))
    if not _GUID_RE.match(guid):
        logs = set_power_plan("balanced")
        logs.append("[INFO] No earlier power plan was recorded, so Balanced was set.")
        return logs
    try:
        if get_active_power_plan()[1].lower() == guid.lower():
            cfg.pop("power_plan_before_app", None)
            return [f"[ALREADY] Your power plan is already your previous plan ({rec.get('name') or guid}); nothing was changed."]
        res = subprocess.run(["powercfg", "/setactive", guid], capture_output=True, text=True,
                             creationflags=0x08000000)
        if res.returncode == 0:
            cfg.pop("power_plan_before_app", None)
            return [f"[SUCCESS] Power plan restored to your previous plan: {rec.get('name') or guid}"]
        return [f"[INFO] powercfg notice: {res.stderr or res.stdout}"]
    except Exception as e:
        return [f"[ERROR] Could not restore power plan: {e}"]


def decode_console(data: bytes) -> str:
    """Console tools write in the PC's OEM code page, and sfc writes UTF-16. Decode both instead of showing garbage in any language."""
    if not data:
        return ""
    if b"\x00" in data[:200]:
        try:
            return data.decode("utf-16-le", errors="replace").replace("\x00", "")
        except Exception:
            pass
    try:
        return data.decode("utf-8")                       # strict: valid UTF-8 is almost never produced by accident from OEM text
    except UnicodeDecodeError:
        pass
    try:
        oem = f"cp{ctypes.windll.kernel32.GetOEMCP()}"
        return data.decode(oem, errors="replace")
    except Exception:
        return data.decode("utf-8", errors="replace")


def _power_plan_guids() -> List[str]:
    rc, out, _ = run_tool(["powercfg", "/list"], 15)
    return [g.lower() for g in re.findall(r"[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}", out)] if rc == 0 else []


def set_power_plan(plan_mode: str) -> List[str]:
    logs = []
    want_balanced = plan_mode.lower() == "balanced"
    guid = GUID_BALANCED if want_balanced else GUID_HIGH_PERF
    target_name = "Balanced" if want_balanced else "High Performance"
    try:
        if get_active_power_plan()[1].lower() == guid.lower():
            return [f"[ALREADY] The power plan is already {target_name}; nothing was changed."]
        if guid.lower() not in _power_plan_guids() and not want_balanced:
            # Many laptops (Modern Standby) hide the High Performance plan. Windows can usually create it again from its built-in id.
            rc, out, _ = run_tool(["powercfg", "/duplicatescheme", GUID_HIGH_PERF], 15)
            new = re.search(r"[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}", out) if rc == 0 else None
            if new:
                guid = new.group(0)
                logs.append("[INFO] The High Performance plan was hidden on this PC, so it was created again.")
            else:
                logs.append("[ERROR] The High Performance power plan is not available on this PC (common on laptops). Your current plan was kept.")
                return logs
        rc, out, _ = run_tool(["powercfg", "/setactive", guid], 15)
        if rc == 0:
            logs.append(f"[SUCCESS] Power plan switched to: {target_name}")
        else:
            logs.append(f"[ERROR] Could not switch the power plan to {target_name}: {out.strip()[:200]}")
    except Exception as e:
        logs.append(f"[ERROR] Could not switch power plan: {e}")
    return logs

def save_launch_options(vdf_path: str, new_options: str) -> Tuple[bool, List[str]]:
    logs = []
    if not vdf_path or not os.path.exists(vdf_path):
        return False, ["[ERROR] Steam configuration file not found."]

    backup_vdf = vdf_path + ".backup"
    try:
        if not os.path.exists(backup_vdf):
            shutil.copyfile(vdf_path, backup_vdf)
            logs.append("[BACKUP] Created backup of Steam localconfig.vdf")

        import steam_vdf
        with open(vdf_path, "r", encoding="utf-8", errors="ignore", newline="") as f:      # newline="": keep the file's own line endings
            content = f.read()

        # Edit only CS2's own block (Software > Valve > Steam > apps > 730) and leave every other byte, and every other game, as it is.
        try:
            new_content = steam_vdf.set_launch_options(content, new_options, "730")
            if steam_vdf.get_launch_options(new_content, "730") != (new_options or "").strip().replace("\r", " ").replace("\n", " "):
                return False, ["[ERROR] Safety check failed: the edited file did not read back correctly. Nothing was written."]
        except steam_vdf.VdfError as e:
            return False, [f"[ERROR] Could not safely edit Steam's config ({e}). Nothing was written."]

        tmp_path = vdf_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8", newline="") as f:
            f.write(new_content)
        os.replace(tmp_path, vdf_path)

        logs.append(f"[SUCCESS] Updated CS2 Launch Options in Steam to: '{new_options}'")
        logs.append("[NOTE] If Steam was running, restart Steam to reflect the new launch options.")
        return True, logs
    except Exception as e:
        logs.append(f"[ERROR] Failed writing Steam launch options: {e}")
        return False, logs

class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_void_p),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", wintypes.WCHAR * 260)
    ]

def get_cs2_pids() -> List[int]:
    """Returns active cs2.exe process IDs via pure Win32 toolhelp snapshot (<5ms, zero console windows)."""
    pids = []
    try:
        TH32CS_SNAPPROCESS = 0x00000002
        kernel32 = ctypes.windll.kernel32
        h_snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if h_snap != -1 and h_snap != 0xFFFFFFFFFFFFFFFF:
            pe = PROCESSENTRY32W()
            pe.dwSize = ctypes.sizeof(PROCESSENTRY32W)
            if kernel32.Process32FirstW(h_snap, ctypes.byref(pe)):
                while True:
                    if pe.szExeFile.lower() == "cs2.exe":
                        pids.append(int(pe.th32ProcessID))
                    if not kernel32.Process32NextW(h_snap, ctypes.byref(pe)):
                        break
            kernel32.CloseHandle(h_snap)
    except Exception:
        pass
    return pids

def is_steam_running() -> bool:
    """Checks whether Steam (steam.exe) is actively running on the machine.
    Pure Win32: Zero subprocess overhead, <5ms latency."""
    try:
        # 1. Fast check for active Steam window
        if ctypes.windll.user32.FindWindowW("vguiPopupWindow", "Steam"):
            return True
        if ctypes.windll.user32.FindWindowW(None, "Steam"):
            return True

        # 2. Check running processes via Toolhelp32 snapshot
        TH32CS_SNAPPROCESS = 0x00000002
        kernel32 = ctypes.windll.kernel32
        h_snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if h_snap != -1 and h_snap != 0xFFFFFFFFFFFFFFFF:
            pe = PROCESSENTRY32W()
            pe.dwSize = ctypes.sizeof(PROCESSENTRY32W)
            if kernel32.Process32FirstW(h_snap, ctypes.byref(pe)):
                while True:
                    if pe.szExeFile.lower() in ("steam.exe", "steamwebhelper.exe"):
                        kernel32.CloseHandle(h_snap)
                        return True
                    if not kernel32.Process32NextW(h_snap, ctypes.byref(pe)):
                        break
            kernel32.CloseHandle(h_snap)
    except Exception:
        pass
    return False

def is_process_running(proc_name: str = "cs2.exe") -> bool:
    """Checks whether a process is running."""
    p_lower = proc_name.lower()
    if "cs2" in p_lower:
        return is_cs2_running()
    if "steam" in p_lower:
        return is_steam_running()
    return False

def is_cs2_running() -> bool:
    """Checks whether Counter-Strike 2 is actively running.
    Pure Win32: Zero subprocess overhead, zero flashing console windows, <5ms latency."""
    try:
        # 1. Fast check for the active CS2 SDL game window
        if ctypes.windll.user32.FindWindowW("SDL_app", "Counter-Strike 2"):
            return True
        if ctypes.windll.user32.FindWindowW(None, "Counter-Strike 2"):
            return True

        # 2. Check if cs2.exe exists in process snapshot
        pids = get_cs2_pids()
        if pids and len(pids) > 0:
            return True

        return False
    except Exception:
        return False

def boost_cs2_process() -> Tuple[bool, str]:
    """Elevates CS2 process priority using minimal native Win32 handles (PROCESS_SET_INFORMATION).
    Does not purge RAM working sets (that can make browsers, Discord and games stutter)."""
    try:
        cs2_pids = get_cs2_pids()
        if not cs2_pids:
            return False, "CS2 is not running yet. Launch CS2 first, then click Boost!"

        boosted_count = 0
        already_high = 0
        access_flags = PROCESS_SET_INFORMATION | PROCESS_QUERY_LIMITED_INFORMATION
        for pid in cs2_pids:
            try:
                handle = ctypes.windll.kernel32.OpenProcess(access_flags, False, pid)
                if not handle:
                    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_SET_INFORMATION, False, pid)
                if handle:
                    if ctypes.windll.kernel32.GetPriorityClass(handle) == HIGH_PRIORITY_CLASS:
                        already_high += 1
                    elif ctypes.windll.kernel32.SetPriorityClass(handle, HIGH_PRIORITY_CLASS):
                        boosted_count += 1
                    ctypes.windll.kernel32.CloseHandle(handle)
            except Exception:
                pass

        if boosted_count == 0 and already_high > 0:
            return True, "cs2.exe is already at HIGH CPU priority; nothing was changed (it resets when CS2 closes)."
        if boosted_count > 0:
            return True, f"Successfully elevated cs2.exe (PIDs: {boosted_count}) to HIGH CPU priority (resets when CS2 closes)."
        else:
            return False, "cs2.exe found, but priority elevation was blocked by OS permissions. Try running as Administrator."
    except Exception as e:
        return False, f"Boost error: {e}"

# ----------------- SAFE PC MAINTENANCE -----------------

TEMP_MIN_AGE_SECONDS = 24 * 3600


def clean_windows_temp_files() -> Tuple[int, int, List[str]]:
    """Cleans %TEMP% and %SystemRoot%\\Temp. Skips locked/open files safely."""
    logs = []
    deleted = 0
    freed = 0
    
    target_dirs = []
    user_temp = os.environ.get("TEMP", "")
    if user_temp and os.path.exists(user_temp):
        target_dirs.append(user_temp)
    
    win_temp = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "Temp")
    if os.path.exists(win_temp):
        target_dirs.append(win_temp)

    # Never touch this app's own unpacked files (a one-file exe lives in %TEMP%\_MEIxxxx while it runs, and so do other PyInstaller apps),
    # and leave files from the last 24 hours alone: they belong to programs that are running or installing right now.
    own_root = getattr(sys, "_MEIPASS", None)
    own_root = os.path.normcase(os.path.abspath(own_root)) if own_root else None
    cutoff = time.time() - TEMP_MIN_AGE_SECONDS

    def protected(path: str) -> bool:
        low = os.path.normcase(os.path.abspath(path))
        if own_root and (low == own_root or low.startswith(own_root + os.sep)):
            return True
        return any(part.startswith("_mei") for part in low.split(os.sep))

    for folder in target_dirs:
        folder_deleted = 0
        folder_freed = 0
        try:
            for root, dirs, files in os.walk(folder, topdown=False):
                if protected(root):
                    continue
                for f in files:
                    file_path = os.path.join(root, f)
                    try:
                        if os.path.getmtime(file_path) > cutoff:
                            continue
                        sz = os.path.getsize(file_path)
                        os.remove(file_path)
                        folder_deleted += 1
                        folder_freed += sz
                    except (PermissionError, OSError):
                        continue
            deleted += folder_deleted
            freed += folder_freed
        except Exception:
            pass

    mb = freed / (1024 * 1024)
    logs.append(f"[TEMP CLEAN] Purged {deleted} temporary scratch files ({mb:.1f} MB freed).")
    return deleted, freed, logs

def clean_discord_and_steam_cache(steam_path: Optional[str]) -> Tuple[int, int, List[str]]:
    """Cleans Discord media cache and Steam HTTP web cache without logging anyone out."""
    logs = []
    deleted = 0
    freed = 0

    cache_targets = []
    
    # Discord cache
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        discord_base = os.path.join(appdata, "discord")
        if os.path.exists(discord_base):
            cache_targets.extend([
                os.path.join(discord_base, "Cache", "Cache_Data"),
                os.path.join(discord_base, "Code Cache"),
                os.path.join(discord_base, "GPUCache")
            ])

    # Steam HTTP Cache
    if steam_path and os.path.exists(steam_path):
        steam_http = os.path.join(steam_path, "appcache", "httpcache")
        if os.path.exists(steam_http):
            cache_targets.append(steam_http)

    for folder in cache_targets:
        if not os.path.exists(folder):
            continue
        try:
            for root, dirs, files in os.walk(folder, topdown=False):
                for f in files:
                    file_path = os.path.join(root, f)
                    try:
                        sz = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted += 1
                        freed += sz
                    except (PermissionError, OSError):
                        continue
        except Exception:
            pass

    mb = freed / (1024 * 1024)
    logs.append(f"[APP CACHE] Cleaned {deleted} Discord & Steam web cache files ({mb:.1f} MB freed).")
    return deleted, freed, logs

def clean_windows_update_cache() -> Tuple[int, int, List[str]]:
    """Cleans SoftwareDistribution\\Download folder. Skips locked files safely."""
    logs = []
    deleted = 0
    freed = 0
    sw_dir = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "SoftwareDistribution", "Download")
    if os.path.exists(sw_dir):
        try:
            for root, dirs, files in os.walk(sw_dir, topdown=False):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        sz = os.path.getsize(fp)
                        os.remove(fp)
                        deleted += 1
                        freed += sz
                    except (PermissionError, OSError):
                        continue
                for d in dirs:
                    dp = os.path.join(root, d)
                    try:
                        os.rmdir(dp)
                    except (PermissionError, OSError):
                        continue
        except Exception:
            pass
    mb = freed / (1024 * 1024)
    logs.append(f"[UPDATE CACHE] Purged {deleted} obsolete Windows update download files ({mb:.1f} MB freed).")
    return deleted, freed, logs

def clean_explorer_thumbnail_cache() -> Tuple[int, int, List[str]]:
    """Cleans thumbnail and icon cache databases in %LOCALAPPDATA%\\Microsoft\\Windows\\Explorer."""
    logs = []
    deleted = 0
    freed = 0
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        exp_dir = os.path.join(local_app_data, "Microsoft", "Windows", "Explorer")
        if os.path.exists(exp_dir):
            for pattern in ["thumbcache_*.db", "iconcache_*.db"]:
                for fp in glob.glob(os.path.join(exp_dir, pattern)):
                    try:
                        sz = os.path.getsize(fp)
                        os.remove(fp)
                        deleted += 1
                        freed += sz
                    except (PermissionError, OSError):
                        continue
    mb = freed / (1024 * 1024)
    logs.append(f"[THUMBNAILS] Cleaned {deleted} thumbnail & icon cache files ({mb:.1f} MB freed).")
    return deleted, freed, logs

def empty_recycle_bin() -> Tuple[bool, List[str]]:
    """Empties the Windows Recycle Bin across all drives without prompts."""
    logs = []
    try:
        logs.append("[RECYCLE BIN] Purging Windows Recycle Bin across all drives...")
        ret = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
        if ret == 0 or ret == -2147418113:
            logs.append("[SUCCESS] Windows Recycle Bin has been completely emptied.")
            return True, logs
        else:
            logs.append(f"[INFO] Recycle Bin emptied (status code: {ret}).")
            return True, logs
    except Exception as e:
        logs.append(f"[ERROR] Could not empty Recycle Bin: {e}")
        return False, logs

def flush_dns_cache() -> Tuple[bool, List[str]]:
    """Flushes DNS resolver cache without resetting adapters or VPNs."""
    logs = []
    try:
        # Try PowerShell Clear-DnsClientCache
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Clear-DnsClientCache"],
            capture_output=True, text=True, creationflags=CREATE_NO_WINDOW
        )
        if res.returncode == 0:
            logs.append("[DNS] Successfully flushed Windows DNS resolver cache.")
            return True, logs
    except Exception:
        pass

    try:
        res2 = subprocess.run(
            ["ipconfig", "/flushdns"],
            capture_output=True, text=True, creationflags=CREATE_NO_WINDOW
        )
        if "Successfully" in res2.stdout or res2.returncode == 0:
            logs.append("[DNS] Successfully flushed DNS cache via ipconfig.")
            return True, logs
        else:
            logs.append(f"[DNS NOTICE] {res2.stdout.strip() or res2.stderr.strip() or 'Flushed'}")
            return True, logs
    except Exception as e:
        logs.append(f"[DNS ERROR] Failed to flush DNS: {e}")
        return False, logs

def launch_cleanmgr() -> Tuple[bool, str]:
    """Launches Microsoft Disk Cleanup (cleanmgr.exe)."""
    try:
        subprocess.Popen(["cleanmgr.exe"], creationflags=CREATE_NO_WINDOW)
        return True, "Launched official Windows Disk Cleanup (cleanmgr.exe)."
    except Exception as e:
        return False, f"Could not launch cleanmgr: {e}"

def get_drives_info() -> List[Dict[str, Any]]:
    """Scans storage drives for capacity, free space, and warning thresholds."""
    drives = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        root = f"{letter}:\\"
        if os.path.exists(root):
            try:
                usage = shutil.disk_usage(root)
                total_gb = usage.total / (1024 ** 3)
                free_gb = usage.free / (1024 ** 3)
                used_gb = total_gb - free_gb
                used_pct = (used_gb / total_gb) * 100 if total_gb > 0 else 0
                is_critical = used_pct >= 85.0
                drives.append({
                    "drive": f"{letter}:",
                    "total_gb": total_gb,
                    "free_gb": free_gb,
                    "used_gb": used_gb,
                    "used_pct": used_pct,
                    "is_critical": is_critical
                })
            except Exception:
                continue
    return drives

REPAIR_TITLES = {"trim": "SSD TRIM", "sfc": "System File Checker (SFC)", "dism": "DISM health restore", "winsxs": "DISM WinSxS clean-up"}
REPAIR_TAGS = {"trim": "TRIM", "sfc": "SFC", "dism": "DISM", "winsxs": "DISM"}
REPAIR_LIMIT_MIN = {"trim": 30, "sfc": 60, "dism": 90, "winsxs": 90}
CBS_LOG = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "Logs", "CBS", "CBS.log")
DISM_LOG = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "Logs", "DISM", "dism.log")


def _minutes(seconds: int) -> str:
    return f"{seconds // 60} min {seconds % 60} s" if seconds >= 60 else f"{seconds} s"


def _verdict_sentence(text: str) -> str:
    """The tool's own last sentence, without the 'Verification 45% complete.' progress noise."""
    tail = re.split(r"\d{1,3}(?:[.,]\d)?\s*%\s*complete\.?", text)[-1].strip()
    tail = re.sub(r"[\[\]=\s]*\d{1,3}(?:[.,]\d)?\s*%[\[\]=\s]*", " ", tail).strip()
    return tail[-220:]


def _cbs_size() -> Optional[int]:
    try:
        return os.path.getsize(CBS_LOG)
    except OSError:
        return None


def parse_sr_lines(lines: List[str]) -> Dict[str, Any]:
    """What SFC wrote to CBS.log ([SR] lines) during one run. These lines are not translated, so they work on any Windows language."""
    repairing = 0
    for l in lines:
        m = re.search(r"Repairing (\d+) components", l)
        if m:
            repairing = max(repairing, int(m.group(1)))
    return {"verify_complete": any("Verify complete" in l for l in lines),
            "repair_complete": any("Repair complete" in l for l in lines),
            "cannot_repair": sum(1 for l in lines if "Cannot repair member file" in l),
            "repairing": repairing, "lines": len(lines)}


def cbs_evidence_since(offset: Optional[int]) -> Optional[Dict[str, Any]]:
    """Reads only what was added to CBS.log after offset (a size taken before the scan). None when the log cannot be read."""
    try:
        size = os.path.getsize(CBS_LOG)
        start = offset if (offset is not None and size >= offset) else 0       # smaller than before = Windows rotated the log
        start = max(start, size - 30 * 1024 * 1024)
        with open(CBS_LOG, "rb") as f:
            f.seek(start)
            data = f.read()
    except OSError:
        return None
    return parse_sr_lines([l for l in data.decode("utf-8", errors="replace").splitlines() if "[SR]" in l])


def _pct_in(text: str) -> Optional[float]:
    found = re.findall(r"(\d{1,3}(?:[.,]\d)?)\s*%", text)
    for raw in reversed(found):
        try:
            v = float(raw.replace(",", "."))
        except ValueError:
            continue
        if 0 <= v <= 100:
            return v
    return None


def run_tool(args: List[str], timeout: int, on_progress=None) -> Tuple[Optional[int], str, bool]:
    """Runs a console tool WITHOUT a shell (so a timeout really stops it). Returns (exit code, output text, timed_out).
    With on_progress(percent) the output is read while the tool runs, so the app can show the tool's own 'Verification 45% complete'."""
    if on_progress is None:
        try:
            res = subprocess.run(args, capture_output=True, timeout=timeout, creationflags=CREATE_NO_WINDOW)
            return res.returncode, decode_console(res.stdout or b"") + decode_console(res.stderr or b""), False
        except subprocess.TimeoutExpired:
            return None, "", True
        except FileNotFoundError:
            return None, f"{args[0]} was not found on this PC", False
        except Exception as e:
            return None, str(e), False
    try:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
    except FileNotFoundError:
        return None, f"{args[0]} was not found on this PC", False
    except Exception as e:
        return None, str(e), False
    buf = bytearray()

    def reader() -> None:
        last = None
        try:
            while True:
                chunk = proc.stdout.read1(4096)
                if not chunk:
                    break
                buf.extend(chunk)
                start = max(0, len(buf) - 1200)
                if b"\x00" in buf[:200] and start % 2:
                    start += 1                                                  # keep UTF-16 text on a 2-byte boundary
                pct = _pct_in(decode_console(bytes(buf[start:])))
                if pct is not None and pct != last:
                    last = pct
                    try:
                        on_progress(pct)
                    except Exception:
                        pass
        except Exception:
            pass

    t = threading.Thread(target=reader, daemon=True, name="tool-output")
    t.start()
    try:
        rc = proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            proc.kill()
            proc.wait(10)
        except Exception:
            pass
        t.join(5)
        return None, "", True
    finally:
        try:
            if proc.poll() is not None:
                t.join(10)
            proc.stdout.close()
        except Exception:
            pass
    return rc, decode_console(bytes(buf)), False


_DISM_HELP = {
    0x800F081F: ("Windows could not find the files it needs to repair itself.", "Connect to the internet, run Windows Update, restart, then try again."),
    0x800F0906: ("Windows could not download the repair files.", "Check your internet connection and try again."),
    0x800F0907: ("A policy on this PC blocks Windows from downloading the repair files.", "On a work or school PC, ask your administrator."),
    0x800F0922: ("Windows could not finish because the system reserved space or a pending update is blocking it.", "Restart the PC, let updates finish, then try again."),
    0x800F0915: ("The repair source Windows needs is not available.", "Run Windows Update, restart, then try again."),
    0x800F0831: ("A Windows update package needed for the repair is missing.", "Run Windows Update, restart, then try again."),
    0x800706BE: ("The Windows servicing service stopped responding.", "Restart the PC and try again."),
    0x800706BA: ("The Windows servicing service stopped responding.", "Restart the PC and try again."),
    0x80070005: ("Windows refused access.", "Close the app, start it with 'Relaunch as Administrator' and try again."),
    740: ("The tool needs Administrator rights.", "Use 'Relaunch as Administrator' and try again."),
    1726: ("The Windows servicing service stopped responding.", "Restart the PC and try again."),
    87: ("Windows did not accept the request.", "Restart the PC and try again."),
}


def _result(tool: str, status: str, ok: bool, headline: str, detail: str = "", nxt: str = "", evidence: Optional[List[str]] = None,
            seconds: int = 0, log_file: str = "") -> Dict[str, Any]:
    tag = REPAIR_TAGS[tool]
    ev = list(evidence or [])
    logs = [f"[INFO] {e}" for e in ev]
    if status in ("unverified",):
        logs.append(f"[{tag}] {headline}")
    elif ok:
        logs.append(f"[SUCCESS] {headline}")
    elif status == "admin":
        logs.append(f"[ADMIN REQUIRED] {headline}")
    else:
        logs.append(f"[{tag} ERROR] {headline}")
    return {"tool": tool, "title": REPAIR_TITLES[tool], "status": status, "ok": ok, "headline": headline, "detail": detail, "next": nxt,
            "evidence": ev, "seconds": seconds, "log_file": log_file, "logs": logs}


def _classify_sfc(rc: Optional[int], out: str, sr: Optional[Dict[str, Any]], seconds: int) -> Dict[str, Any]:
    text = " ".join(out.split())
    low = text.lower()
    ev = []
    said = _verdict_sentence(text)
    if said:
        ev.append(f"Windows said: {said}")
    ev.append(f"Exit code: {rc}")
    if sr and sr["verify_complete"]:
        ev.append(f"CBS.log shows the scan reached its end; {sr['repairing']} component(s) needed repair, {sr['cannot_repair']} file(s) could not be repaired.")
    elif sr is not None:
        ev.append("CBS.log has no 'scan finished' line for this run.")
    ev.append(f"Took {_minutes(seconds)}.")
    f = dict(seconds=seconds, log_file=CBS_LOG)
    if rc is None:
        return _result("sfc", "failed", False, f"Failed running SFC scan: {text}", "Windows did not start the scan.", "Restart the PC and try again.", ev, **f)
    unfixable_text = "unable to fix" in low or "could not perform the requested operation" in low
    if "did not find any integrity violations" in low:
        return _result("sfc", "clean", True, "SFC check complete: Zero system file corruptions detected.",
                       "Windows checked every protected system file and found nothing wrong. No changes were made.", "", ev, **f)
    if "successfully repaired them" in low:
        return _result("sfc", "repaired", True, "SFC check complete: Found and repaired corrupted system files!",
                       "Windows found damaged system files and replaced them with good copies.",
                       "Restart the PC so the repaired files are used.", ev, **f)
    if "pending which requires reboot" in low or "repair pending" in low:
        return _result("sfc", "reboot", False, "SFC could not run because Windows is waiting for a restart.", "An earlier update or repair has to finish first.",
                       "Restart the PC, then run SFC again.", ev, **f)
    if "could not start the repair service" in low:
        return _result("sfc", "failed", False, "SFC could not start Windows' repair service.", "The scan did not run.",
                       "Restart the PC and try again.", ev, **f)
    if unfixable_text:
        return _result("sfc", "unfixable", False, f"SFC found a problem it could not fix: {said or text[-220:]}",
                       "Windows found damaged system files but could not replace some of them.",
                       "Run 'DISM health restore' first, restart, then run SFC again. Details are in the lines marked [SR] in " + CBS_LOG, ev, **f)
    if rc != 0:
        return _result("sfc", "failed", False, f"SFC stopped with code {rc}: {text[-220:]}", "The scan did not finish.", "Restart the PC and try again.", ev, **f)
    if sr and sr["verify_complete"]:                                              # another Windows language: use the untranslated CBS.log lines instead
        if sr["cannot_repair"] > 0:
            return _result("sfc", "unfixable", False, f"SFC found a problem it could not fix ({sr['cannot_repair']} file(s)).",
                           "Windows found damaged system files but could not replace some of them.",
                           "Run 'DISM health restore' first, restart, then run SFC again. Details are in the lines marked [SR] in " + CBS_LOG, ev, **f)
        if sr["repairing"] > 0:
            return _result("sfc", "repaired", True, "SFC check complete: Found and repaired corrupted system files!",
                           "Windows replaced damaged system files (confirmed from CBS.log).", "Restart the PC so the repaired files are used.", ev, **f)
        return _result("sfc", "clean", True, "SFC check complete: Zero system file corruptions detected.",
                       "Confirmed from CBS.log: the scan finished and nothing needed repair.", "", ev, **f)
    return _result("sfc", "unverified", True, f"SFC finished, but the app could not confirm the result. Windows reported: {said or text[-220:] or 'nothing'}",
                   "The scan ended without an error code, but its message is in a language the app does not know and CBS.log could not confirm it.",
                   "To see what SFC found, open " + CBS_LOG + " and look at the lines marked [SR].", ev, **f)


def _classify_dism(tool: str, rc: Optional[int], out: str, seconds: int, free_before: Optional[int], free_after: Optional[int]) -> Dict[str, Any]:
    text = " ".join(out.split())
    low = text.lower()
    label = {"dism": "Windows Component Store check and repair", "winsxs": "WinSxS component clean-up"}[tool]
    ev = []
    said = _verdict_sentence(text)
    if said:
        ev.append(f"Windows said: {said}")
    code = "none" if rc is None else (f"{rc} (0x{rc & 0xFFFFFFFF:08X})" if rc else "0")
    ev.append(f"Exit code: {code}")
    if tool == "winsxs" and free_before is not None and free_after is not None:
        d = (free_after - free_before) / (1024 ** 3)
        ev.append(f"Free space on C: before {free_before / (1024 ** 3):.2f} GB, after {free_after / (1024 ** 3):.2f} GB ({'+' if d >= 0 else ''}{d:.2f} GB). DISM does not report how much it freed.")
    ev.append(f"Took {_minutes(seconds)}.")
    f = dict(seconds=seconds, log_file=DISM_LOG)
    if rc is None:
        return _result(tool, "failed", False, f"{label} failed to start: {text}", "", "Restart the PC and try again.", ev, **f)
    if rc in (0, 3010):
        restart = "Restart the PC to finish the changes." if rc == 3010 else ""
        if tool == "dism":
            if "was repaired" in low:
                return _result(tool, "repaired", True, "DISM restore completed: Windows found damage in the Component Store and repaired it.",
                               "Windows fixed the files that Windows Update and SFC rely on.", (restart + " Run SFC once more to double-check.").strip(), ev, **f)
            return _result(tool, "clean", True, "DISM restore completed: Windows Component Store is healthy.",
                           "Windows finished the check with no error. Nothing it could not fix.", restart or "If SFC could not fix files before, run SFC again now.", ev, **f)
        return _result(tool, "done", True, "DISM WinSxS component cleanup completed successfully.",
                       "Windows removed older, superseded copies of update files. Nothing it is using was removed.", restart, ev, **f)
    why, fix = _DISM_HELP.get(rc & 0xFFFFFFFF, _DISM_HELP.get(rc, ("", "")))
    ev_code = f"0x{rc & 0xFFFFFFFF:08X}"
    return _result(tool, "failed", False, f"{label} returned code {rc}: {text[-250:]}",
                   why or f"Windows stopped with error {ev_code}.", fix or f"Restart the PC and try again. Details are in {DISM_LOG}.", ev, **f)


def _classify_trim(rc: Optional[int], out: str, seconds: int) -> Dict[str, Any]:
    text = " ".join(out.split())
    ev = []
    trimmed = re.findall(r"(?i)total space trimmed\s*=?\s*([\d.,]+\s*[KMGT]?B)", text)
    ev.append(f"Windows reported trimming: {', '.join(trimmed)}" if trimmed else "Windows did not state how much was trimmed (normal when the drive was already trimmed).")
    ev.append(f"Exit code: {rc}")
    ev.append(f"Took {_minutes(seconds)}.")
    f = dict(seconds=seconds)
    if rc == 0:
        return _result("trim", "done", True, "Completed SSD TRIM optimization for all connected volumes.",
                       "Windows optimized each drive in the way that suits it (SSD: TRIM, hard disk: defragment).", "", ev, **f)
    return _result("trim", "failed", False, f"defrag returned code {rc}: {text[-250:]}", "Windows stopped before finishing.", "Close other disk tools and try again.", ev, **f)


def run_repair(tool: str, on_progress=None) -> Dict[str, Any]:
    """Runs one of the long Windows tools (sfc, dism, winsxs, trim) and returns a plain-language verdict with the evidence behind it.
    The verdict comes from the tool's own output, its exit code and (for SFC) the untranslated CBS.log lines of this run."""
    title = REPAIR_TITLES[tool]
    if not is_admin():
        return _result(tool, "admin", False, f"{title} requires Administrator privileges.", "", "Use 'Relaunch as Administrator' and try again.")
    limit = REPAIR_LIMIT_MIN[tool]
    started = time.time()
    if tool == "sfc":
        cbs_before = _cbs_size()
        args = ["sfc", "/scannow"]
        note = "[SFC] Scanning Windows protected system files (sfc /scannow). This takes several minutes and can pause for a long time; that is normal."
    elif tool == "dism":
        args = ["dism", "/online", "/cleanup-image", "/restorehealth"]
        note = "[DISM] Checking and repairing the Windows Component Store (dism /restorehealth). This can take 10-30 minutes and often sits at 20% or 62.3%; that is normal."
    elif tool == "winsxs":
        args = ["dism", "/online", "/cleanup-image", "/startcomponentcleanup"]
        note = "[DISM] Purging superseded Windows update components from WinSxS. This can take several minutes."
    else:
        args = ["defrag", "/C", "/O"]
        note = "[TRIM] Running media-specific TRIM optimization (defrag /C /O)..."
    free_before = None
    if tool == "winsxs":
        try:
            free_before = shutil.disk_usage(os.environ.get("SystemDrive", "C:") + "\\").free
        except OSError:
            pass
    rc, out, timed_out = run_tool(args, limit * 60, on_progress)
    seconds = int(time.time() - started)
    if timed_out:
        r = _result(tool, "timeout", False, f"{title} did not finish within {limit} minutes, so the app stopped waiting.",
                    "The scan was stopped by the app.", "Restart the PC and try again.", seconds=seconds)
    elif tool == "sfc":
        r = _classify_sfc(rc, out, cbs_evidence_since(cbs_before), seconds)
    elif tool in ("dism", "winsxs"):
        free_after = None
        if tool == "winsxs":
            try:
                free_after = shutil.disk_usage(os.environ.get("SystemDrive", "C:") + "\\").free
            except OSError:
                pass
        r = _classify_dism(tool, rc, out, seconds, free_before, free_after)
    else:
        r = _classify_trim(rc, out, seconds)
    r["logs"].insert(0, note)
    return r


def run_ssd_trim() -> Tuple[bool, List[str]]:
    r = run_repair("trim")
    return r["ok"], r["logs"]


def run_sfc_scan() -> Tuple[bool, List[str]]:
    r = run_repair("sfc")
    return r["ok"], r["logs"]


def run_dism_restore() -> Tuple[bool, List[str]]:
    r = run_repair("dism")
    return r["ok"], r["logs"]


def run_dism_component_cleanup() -> Tuple[bool, List[str]]:
    r = run_repair("winsxs")
    return r["ok"], r["logs"]


def open_startup_apps() -> Tuple[bool, str]:
    """Opens Windows native Startup Apps settings page."""
    try:
        subprocess.Popen(["cmd", "/c", "start", "ms-settings:startupapps"], shell=True, creationflags=CREATE_NO_WINDOW)
        return True, "Opened official Windows Startup Apps Manager."
    except Exception as e:
        return False, f"Could not open Startup Apps: {e}"

# ----------------- SAFE GAMING DNS OPTIMIZER & BENCHMARK -----------------

DNS_PROVIDERS: List[Dict[str, str]] = [
    {
        "id": "cloudflare",
        "name": "Cloudflare Gaming (1.1.1.1)",
        "primary": "1.1.1.1",
        "secondary": "1.0.0.1",
        "desc": "Ultra-fast global edge network; top choice for Valve Steam SDR & FastDL.",
    },
    {
        "id": "google",
        "name": "Google Public DNS (8.8.8.8)",
        "primary": "8.8.8.8",
        "secondary": "8.8.4.4",
        "desc": "Rock-solid global reliability with Direct CDN peering for game assets.",
    },
    {
        "id": "quad9",
        "name": "Quad9 Security (9.9.9.9)",
        "primary": "9.9.9.9",
        "secondary": "149.112.112.112",
        "desc": "Low-latency IBM/PCH routing with built-in malicious domain blocking.",
    },
    {
        "id": "opendns",
        "name": "Cisco OpenDNS (208.67.222.222)",
        "primary": "208.67.222.222",
        "secondary": "208.67.220.220",
        "desc": "Enterprise Cisco backbone routing with high uptime and smart caching.",
    },
    {
        "id": "level3",
        "name": "Level3 Backbone (4.2.2.1)",
        "primary": "4.2.2.1",
        "secondary": "4.2.2.2",
        "desc": "Direct Tier-1 ISP internet backbone resolvers for minimal hop counts.",
    },
    {
        "id": "adguard",
        "name": "AdGuard Gaming DNS (94.140.14.14)",
        "primary": "94.140.14.14",
        "secondary": "94.140.15.15",
        "desc": "Blocks background telemetry & ad-trackers that cause bandwidth spikes.",
    },
]

def _default_route_interface_index() -> Optional[int]:
    """Index of the adapter Windows really uses to reach the internet (the default route), asked from Windows directly, so it does not
    depend on the language of any command output and ignores idle, virtual (Hyper-V, VPN) and disconnected adapters."""
    import socket
    import struct
    for probe in ("8.8.8.8", "1.1.1.1"):
        try:
            idx = ctypes.c_ulong(0)
            dest = struct.unpack("<L", socket.inet_aton(probe))[0]
            if ctypes.windll.iphlpapi.GetBestInterface(dest, ctypes.byref(idx)) == 0 and idx.value > 1:      # 1 = loopback
                return int(idx.value)
        except Exception:
            continue
    return None


def _legacy_english_interface() -> Optional[str]:
    """Old method, kept only as a fallback: first 'Enabled / Connected' row of netsh's table (English Windows only)."""
    try:
        res = subprocess.run(["netsh", "interface", "show", "interface"], capture_output=True, text=True, timeout=5, creationflags=CREATE_NO_WINDOW)
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 4 and parts[0].lower() == "enabled" and parts[1].lower() == "connected":
                    name = " ".join(parts[3:]).strip()
                    if name:
                        return name
    except Exception:
        pass
    return None


def get_active_network_interface() -> Dict[str, Any]:
    """The adapter that carries the default route and its current DNS. 'interface_ref' is what netsh is given (the adapter index,
    which netsh accepts in place of a name, so localized adapter names and Windows languages do not matter)."""
    info: Dict[str, Any] = {
        "interface_name": "Ethernet",
        "interface_ref": "Ethernet",
        "current_dns": "Automatic (ISP / DHCP)",
        "found": False,
    }
    idx = _default_route_interface_index()
    if idx:
        info["interface_ref"] = str(idx)
        info["interface_name"] = f"adapter #{idx}"
        info["found"] = True
    else:
        legacy = _legacy_english_interface()
        if legacy:
            info["interface_ref"] = info["interface_name"] = legacy
            info["found"] = True

    try:
        res_dns = subprocess.run(
            ["netsh", "interface", "ipv4", "show", "dnsservers", f'name={info["interface_ref"]}'],
            capture_output=True, text=True, timeout=5, creationflags=CREATE_NO_WINDOW
        )
        if res_dns.returncode == 0:
            out = res_dns.stdout
            quoted = re.search(r'"([^"]+)"', out)               # the adapter's own name is quoted in the first line, in every language
            if quoted:
                info["interface_name"] = quoted.group(1)
            ips = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", out)
            if "DHCP" in out.upper():
                if ips:
                    info["current_dns"] = f"Automatic DHCP ({ips[0]})"
                else:
                    info["current_dns"] = "Automatic (ISP / DHCP)"
            elif ips:
                matched_provider = None
                for p in DNS_PROVIDERS:
                    if ips[0] == p["primary"]:
                        matched_provider = p["name"]
                        break
                if matched_provider:
                    info["current_dns"] = f"{matched_provider} [{', '.join(ips[:2])}]"
                else:
                    info["current_dns"] = f"Custom Static [{', '.join(ips[:2])}]"
    except Exception:
        pass

    return info

def dns_status_bar(current_dns: Optional[str]) -> Tuple[str, str]:
    """AUDIT P2-#3: status-bar text from the adapter's REAL DNS (was hard-coded "ACTIVE").
    state: unknown | provider | automatic | custom"""
    cur = (current_dns or "").strip()
    if not cur:
        return "● DNS: checking…", "unknown"
    for p in DNS_PROVIDERS:
        if cur.startswith(p["name"]):
            return f"● DNS: {p['name']}", "provider"
    if cur.lower().startswith("automatic"):
        return "● DNS: automatic (router / ISP)", "automatic"
    m = re.search(r"\[([^\]]+)\]", cur)
    return f"● DNS: custom ({m.group(1).split(',')[0].strip() if m else cur})", "custom"


def _measure_single_dns_latency(ip: str, samples: int = 3) -> Tuple[float, float]:
    """Measures real UDP DNS resolution latency (port 53 query for api.steampowered.com)
    with TCP port 53 fallback. Returns (avg_ms, jitter_ms)."""
    # Build standard DNS A-record query packet for api.steampowered.com
    tx_id = 0x4748  # 'GH'
    header = struct.pack(">HHHHHH", tx_id, 0x0100, 1, 0, 0, 0)
    qname = b""
    for label in ["api", "steampowered", "com"]:
        qname += struct.pack("B", len(label)) + label.encode("ascii")
    qname += b"\x00"
    question = qname + struct.pack(">HH", 1, 1)
    packet = header + question

    rtts: List[float] = []
    for _ in range(samples):
        # 1. Try direct UDP DNS query on port 53
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1.2)
        try:
            t0 = time.perf_counter()
            sock.sendto(packet, (ip, 53))
            data, _ = sock.recvfrom(512)
            t1 = time.perf_counter()
            if data and len(data) >= 12:
                rtts.append((t1 - t0) * 1000.0)
                continue
        except Exception:
            pass
        finally:
            try:
                sock.close()
            except Exception:
                pass

        # 2. Fallback: TCP handshake on port 53
        tsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tsock.settimeout(1.2)
        try:
            t0 = time.perf_counter()
            tsock.connect((ip, 53))
            t1 = time.perf_counter()
            rtts.append((t1 - t0) * 1000.0)
        except Exception:
            pass
        finally:
            try:
                tsock.close()
            except Exception:
                pass

    if not rtts:
        return 999.0, 99.0

    avg_ms = sum(rtts) / len(rtts)
    if len(rtts) > 1:
        diffs = [abs(rtts[i] - rtts[i - 1]) for i in range(1, len(rtts))]
        jitter_ms = sum(diffs) / len(diffs)
    else:
        jitter_ms = 0.5
    return round(avg_ms, 1), round(jitter_ms, 1)

def benchmark_all_dns_providers() -> List[Dict[str, Any]]:
    """Benchmarks all 6 Gaming DNS providers in parallel and returns sorted results (fastest first)."""
    results: List[Dict[str, Any]] = []

    def _bench_worker(provider: Dict[str, str]) -> Dict[str, Any]:
        avg_ms, jitter_ms = _measure_single_dns_latency(provider["primary"], samples=3)
        return {
            **provider,
            "avg_ms": avg_ms,
            "jitter_ms": jitter_ms,
            "reachable": avg_ms < 900.0,
        }

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(_bench_worker, p) for p in DNS_PROVIDERS]
        for fut in as_completed(futures):
            try:
                results.append(fut.result())
            except Exception:
                pass

    results.sort(key=lambda x: (x["avg_ms"], x["jitter_ms"]))
    for idx, item in enumerate(results):
        item["rank"] = idx + 1
        item["is_fastest"] = (idx == 0 and item["reachable"])
    return results

def apply_dns_provider(primary_ip: str, secondary_ip: str, provider_name: str) -> Tuple[bool, List[str]]:
    """Applies the chosen DNS provider to the active Windows network adapter and flushes DNS cache."""
    logs: List[str] = []
    if not is_admin():
        logs.append("[ADMIN REQUIRED] Changing Windows network adapter DNS requires Administrator privileges.")
        return False, logs

    iface_info = get_active_network_interface()
    iface = iface_info["interface_ref"]
    shown = iface_info["interface_name"]
    logs.append(f"[DNS OPTIMIZER] Configuring active adapter '{shown}' -> {provider_name}...")

    try:
        res1 = subprocess.run(
            ["netsh", "interface", "ip", "set", "dns", f"name={iface}", "static", primary_ip, "primary"],
            capture_output=True, text=True, timeout=8, creationflags=CREATE_NO_WINDOW
        )
        if res1.returncode != 0:
            # Fallback syntax for older/newer Windows builds
            res1 = subprocess.run(
                ["netsh", "interface", "ipv4", "set", "dnsservers", f"name={iface}", "static", primary_ip, "primary"],
                capture_output=True, text=True, timeout=8, creationflags=CREATE_NO_WINDOW
            )
        if res1.returncode != 0:
            err = (res1.stdout or res1.stderr or "Unknown netsh error").strip()
            logs.append(f"[ERROR] Could not set primary DNS ({primary_ip}): {err}")
            return False, logs

        logs.append(f"[SUCCESS] Primary DNS set to {primary_ip} on '{shown}'.")

        if secondary_ip:
            res2 = subprocess.run(
                ["netsh", "interface", "ip", "add", "dns", f"name={iface}", secondary_ip, "index=2"],
                capture_output=True, text=True, timeout=8, creationflags=CREATE_NO_WINDOW
            )
            if res2.returncode != 0:
                res2 = subprocess.run(
                    ["netsh", "interface", "ipv4", "add", "dnsservers", f"name={iface}", secondary_ip, "index=2"],
                    capture_output=True, text=True, timeout=8, creationflags=CREATE_NO_WINDOW
                )
            if res2.returncode == 0:
                logs.append(f"[SUCCESS] Secondary failover DNS set to {secondary_ip}.")
            else:
                logs.append(f"[WARN] The secondary DNS ({secondary_ip}) could not be added: {(res2.stdout or res2.stderr or '').strip()}")

        _, flush_logs = flush_dns_cache()
        logs.extend(flush_logs)
        logs.append(f"[COMPLETE] Active Gaming DNS is now locked to {provider_name}!")
        return True, logs
    except Exception as e:
        logs.append(f"[ERROR] Exception applying DNS: {e}")
        return False, logs

def restore_dns_to_dhcp() -> Tuple[bool, List[str]]:
    """Restores the active network adapter's DNS settings back to automatic ISP Default (DHCP)."""
    logs: List[str] = []
    if not is_admin():
        logs.append("[ADMIN REQUIRED] Restoring network adapter DNS requires Administrator privileges.")
        return False, logs

    iface_info = get_active_network_interface()
    iface = iface_info["interface_ref"]
    shown = iface_info["interface_name"]
    logs.append(f"[DNS RESTORE] Reverting adapter '{shown}' to Automatic ISP DNS (DHCP)...")

    try:
        res = subprocess.run(
            ["netsh", "interface", "ip", "set", "dns", f"name={iface}", "source=dhcp"],
            capture_output=True, text=True, timeout=8, creationflags=CREATE_NO_WINDOW
        )
        if res.returncode != 0:
            res = subprocess.run(
                ["netsh", "interface", "ipv4", "set", "dnsservers", f"name={iface}", "source=dhcp"],
                capture_output=True, text=True, timeout=8, creationflags=CREATE_NO_WINDOW
            )
        if res.returncode == 0 or "already" in (res.stdout or "").lower():
            logs.append(f"[REVERTED] Restored '{shown}' to Automatic ISP Default (DHCP).")
            _, flush_logs = flush_dns_cache()
            logs.extend(flush_logs)
            return True, logs
        else:
            err = (res.stdout or res.stderr or "Unknown error").strip()
            logs.append(f"[WARN] netsh returned: {err}")
            return False, logs
    except Exception as e:
        logs.append(f"[ERROR] Failed restoring DNS to DHCP: {e}")
        return False, logs


# ==============================================================================
# 10. STEAM WORKSHOP ADDON & VPK HEALTH VERIFIER (CS2 AppID 730)
# ==============================================================================

KNOWN_ZE_WORKSHOP_PACKS = {
    "3070290649": "GFL / Community ZE Shared Content Pack",
    "3070321829": "Zombie Escape Core Models & Sounds Pack",
    "3100548291": "Mapeadores / Global ZE Asset Pack",
}

def _extract_vpk_hint_name(vpk_path: str) -> str:
    """Reads the first 64KB of a _dir.vpk to detect embedded map names (e.g. ze_...) or asset categories."""
    try:
        with open(vpk_path, "rb") as f:
            chunk = f.read(65536)
        # Look for ze_ or zm_ or cs_ map identifiers
        m = re.search(rb"(ze_[a-zA-Z0-9_]{3,42}|zm_[a-zA-Z0-9_]{3,42})", chunk)
        if m:
            return m.group(1).decode("ascii", errors="ignore")
        if b"soundevents" in chunk and b"models" in chunk:
            return "ZE Server Models & Soundpack VPK"
        if b"models" in chunk:
            return "Custom Player / Boss Models VPK"
        if b"materials" in chunk or b"particles" in chunk:
            return "Custom Materials & Particles VPK"
    except Exception:
        pass
    return "CS2 Workshop Addon Pack"

def check_vpk_integrity(vpk_path: str) -> Tuple[bool, str]:
    """Deep check of a VPK v2 index file (a single <id>.vpk or a <id>_dir.vpk): parses the directory tree and verifies that the data it points to
    is really on disk. Header size fields must fit the file, and every archive part (<id>_000.vpk, ...) must exist and be at least as long as the
    furthest byte the tree needs. A download that stopped half way keeps a valid header, so the 4-byte magic check alone cannot see it."""
    try:
        size = os.path.getsize(vpk_path)
        with open(vpk_path, "rb") as fh:
            head = fh.read(28)
            if len(head) < 28:
                return False, "file shorter than a VPK header"
            sig, ver = struct.unpack("<II", head[:8])
            if sig != 0x55AA1234:
                return False, "invalid VPK signature"
            if ver != 2:
                return True, ""                                  # other versions: signature check only
            tree, fds, amd5, omd5, sigsec = struct.unpack("<IIIII", head[8:28])
            if 28 + tree > size:
                return False, "directory tree is cut off"
            data = fh.read(tree)
        pos = 0
        extents: Dict[int, int] = {}

        def cstr() -> bytes:
            nonlocal pos
            end = data.index(b"\x00", pos)
            val = data[pos:end]
            pos = end + 1
            return val

        while True:
            if not cstr():
                break                                            # empty extension: end of tree
            while True:
                if not cstr():
                    break                                        # empty path: next extension
                while True:
                    if not cstr():
                        break                                    # empty filename: next path
                    _crc, preload, arch, off, ln, term = struct.unpack_from("<IHHIIH", data, pos)
                    pos += 18 + preload
                    if term != 0xFFFF:
                        return False, "directory entry is damaged"
                    if ln:
                        extents[arch] = max(extents.get(arch, 0), off + ln)
        base = vpk_path[:-8] if vpk_path.lower().endswith("_dir.vpk") else None
        for arch, need in extents.items():
            if arch == 0x7FFF:                                   # data stored inside this same file, after the tree
                if 28 + tree + need > size:
                    return False, "file data is cut off (file is shorter than its index says)"
            else:
                if base is None:
                    return False, "index points to archive parts that do not exist"
                part = f"{base}_{arch:03d}.vpk"
                if not os.path.isfile(part):
                    return False, f"missing archive part {os.path.basename(part)}"
                if os.path.getsize(part) < need:
                    return False, f"{os.path.basename(part)} is shorter than its index says (incomplete download)"
        if 0x7FFF in extents or fds:
            total = 28 + tree + fds + amd5 + omd5 + sigsec
            if size < total:
                return False, "file is shorter than its header says"
        return True, ""
    except (ValueError, struct.error, IndexError):
        return False, "directory index cannot be read"
    except OSError as e:
        return False, f"read error ({e.__class__.__name__})"


def scan_workshop_vpk_addons(steam_path: Optional[str], cs2_exe: Optional[str]) -> Dict[str, Any]:
    """Scans Steam Workshop content folders (steamapps/workshop/content/730) and verifies VPK header integrity."""
    import steam_paths
    candidate_dirs = []
    libs = steam_paths.steam_libraries(steam_path)
    cs2_lib = steam_paths.library_of(os.path.abspath(os.path.join(os.path.dirname(cs2_exe), "..", "..", "..")) if cs2_exe and os.path.exists(cs2_exe) else None)
    if cs2_lib:
        libs = [cs2_lib] + [l for l in libs if os.path.normcase(os.path.abspath(l)) != os.path.normcase(os.path.abspath(cs2_lib))]
    candidate_dirs = steam_paths.workshop_dirs(libs)

    addons: List[Dict[str, Any]] = []
    total_bytes = 0
    healthy_count = 0
    corrupted_count = 0

    scan_errors = 0
    for ws_root in candidate_dirs:
        try:
            entries = list(os.scandir(ws_root))
        except Exception:
            continue
        for entry in entries:
            try:
                if not entry.is_dir():
                    continue
                ws_id = entry.name
                folder_path = entry.path
                folder_size = 0
                vpk_files = []
                temp_files = []
                latest_mtime = 0.0

                for root_d, _, files in os.walk(folder_path):
                    for fname in files:
                        fpath = os.path.join(root_d, fname)
                        try:
                            st = os.stat(fpath)
                            folder_size += st.st_size
                            if st.st_mtime > latest_mtime:
                                latest_mtime = st.st_mtime
                            low = fname.lower()
                            if low.endswith(".vpk"):
                                vpk_files.append((fpath, st.st_size))
                            elif low.endswith((".tmp", ".download", ".patch")):
                                temp_files.append(fpath)
                        except Exception:
                            pass

                total_bytes += folder_size
                status = "Healthy"
                status_label = "✅ Healthy VPK"
                detail = ""
                hint_name = KNOWN_ZE_WORKSHOP_PACKS.get(ws_id, "")

                if temp_files or not vpk_files:
                    status = "Incomplete / Temp Lock"
                    status_label = "⚠️ Incomplete / Temp Lock"
                    detail = "leftover temporary download files" if temp_files else "no .vpk file in the folder"
                    corrupted_count += 1
                else:
                    # Check VPK magic bytes (0x55aa1234 -> \x34\x12\xaa\x55) on main VPK
                    dir_vpks = [p for p, sz in vpk_files if p.lower().endswith("_dir.vpk")] or [vpk_files[0][0]]
                    for vp in dir_vpks:
                        try:
                            if os.path.getsize(vp) < 28:
                                status = "Corrupted (Empty / Truncated)"
                                status_label = "🔴 Empty / Truncated VPK"
                                detail = f"{os.path.basename(vp)} is only {os.path.getsize(vp)} bytes"
                                corrupted_count += 1
                                break
                            with open(vp, "rb") as vf:
                                magic = vf.read(4)
                            if magic != b"\x34\x12\xaa\x55":
                                status = "Corrupted (Invalid Header)"
                                status_label = "🔴 Invalid VPK Header"
                                detail = f"{os.path.basename(vp)} does not start with the VPK signature"
                                corrupted_count += 1
                                break
                            ok_deep, why = check_vpk_integrity(vp)
                            if not ok_deep:
                                status = "Corrupted (Incomplete Data)"
                                status_label = "🔴 Incomplete data"
                                detail = f"{os.path.basename(vp)}: {why}"
                                corrupted_count += 1
                                break
                            if not hint_name:
                                hint_name = _extract_vpk_hint_name(vp)
                        except Exception:
                            status = "Corrupted (Read Error)"
                            status_label = "🔴 Read Error / Locked"
                            detail = f"{os.path.basename(vp)} could not be read"
                            corrupted_count += 1
                            break

                if status == "Healthy":
                    healthy_count += 1

                if not hint_name:
                    hint_name = f"Workshop Pack #{ws_id}"

                date_str = datetime.datetime.fromtimestamp(latest_mtime).strftime("%Y-%m-%d") if latest_mtime > 0 else "Unknown"
                addons.append({
                    "workshop_id": ws_id,
                    "name": hint_name,
                    "path": folder_path,
                    "size_bytes": folder_size,
                    "size_mb": round(folder_size / (1024 * 1024), 1),
                    "vpk_count": len(vpk_files),
                    "date": date_str,
                    "status": status,
                    "status_label": status_label,
                    "detail": detail,
                    "mtime": latest_mtime,
                })
            except Exception:
                scan_errors += 1                       # one unreadable folder must not hide the other packs

    addons.sort(key=lambda x: (x["status"] == "Healthy", -x["size_bytes"]))
    total_gb = round(total_bytes / (1024 ** 3), 2)
    msg = f"Verified {len(addons)} Workshop VPK packs ({total_gb} GB): {healthy_count} Healthy, {corrupted_count} Corrupted/Incomplete."
    if scan_errors:
        msg += f" {scan_errors} folder(s) could not be read and were skipped."
    return {
        "addons": addons,
        "total_count": len(addons),
        "healthy_count": healthy_count,
        "corrupted_count": corrupted_count,
        "total_gb": total_gb,
        "workshop_dirs": candidate_dirs,
        "scan_errors": scan_errors,
        "message": msg,
    }

def _is_reparse_point(path: str) -> bool:
    """True for symlinks and junctions: repair must never follow those out of the workshop folder."""
    try:
        if os.path.islink(path):
            return True
        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
        return attrs != -1 and bool(attrs & 0x400)
    except Exception:
        return False


def repair_corrupted_workshop_addons(addons: List[Dict[str, Any]], recent_seconds: float = 900.0) -> Dict[str, Any]:
    """Removes only damaged or stuck-incomplete Workshop folders so Steam can download them cleanly again.
    Safety rules: the folder must be exactly <library>/steamapps/workshop/content/730/<numeric id>, must not be a link or junction,
    and must not have changed in the last 15 minutes (Steam may still be downloading it)."""
    import time as _time
    repaired = 0
    skipped = 0
    freed_bytes = 0
    logs: List[str] = []
    for item in addons:
        if item.get("status") == "Healthy":
            continue
        p = item.get("path", "")
        norm = os.path.normpath(p) if p else ""
        parent = os.path.dirname(norm)
        ok_shape = (bool(norm) and os.path.basename(norm).isdigit() and os.path.basename(parent) == "730"
                    and os.path.basename(os.path.dirname(parent)).lower() == "content"
                    and os.path.basename(os.path.dirname(os.path.dirname(parent))).lower() == "workshop")
        if not ok_shape or not os.path.isdir(norm):
            logs.append(f"[WARN] Skipped {p!r}: not a Steam workshop item folder.")
            skipped += 1
            continue
        if _is_reparse_point(norm):
            logs.append(f"[WARN] Skipped {p}: it is a link, not a real folder.")
            skipped += 1
            continue
        if _time.time() - float(item.get("mtime") or 0) < recent_seconds:
            logs.append(f"[VPK REPAIR] Skipped {item.get('workshop_id')}: changed in the last 15 minutes, Steam may still be downloading it.")
            skipped += 1
            continue
        try:
            sz = item.get("size_bytes", 0)
            shutil.rmtree(norm, ignore_errors=False)
            repaired += 1
            freed_bytes += sz
            logs.append(f"[VPK REPAIR] Removed broken Workshop pack {item.get('workshop_id')} ({item.get('name')}). Steam can download it again.")
        except Exception as e:
            logs.append(f"[WARN] Could not remove {p}: {e}")
            skipped += 1
    if repaired == 0 and skipped == 0:
        msg = "All installed Workshop VPK packs passed header & integrity checks! Zero corrupted packs found."
        logs.append(f"[VPK VERIFIER] {msg}")
    else:
        msg = f"Repaired {repaired} corrupted Workshop VPK folder(s) ({round(freed_bytes / (1024 * 1024), 1)} MB freed)."
        if repaired:
            msg += " Steam downloads a subscribed map again on its next check or when you join a server that needs it."
        if skipped:
            msg += f" {skipped} left alone (recently changed, not a plain workshop folder, or could not be removed)."
    return {
        "repaired": repaired,
        "skipped": skipped,
        "freed_bytes": freed_bytes,
        "logs": logs,
        "message": msg,
    }


# ==============================================================================
# 11. ZE VISUAL CLUTTER, VIEWMODEL, HUD & AUDIO DUCKING CUSTOMIZER
# ==============================================================================

def apply_ze_visual_and_hud_customizer(cfg_dir: str, opts: Dict[str, Any]) -> Dict[str, Any]:
    """Adds (or replaces) the app's marked ZE viewmodel / HUD colour / audio-toggle block in autoexec.cfg."""
    logs: List[str] = []
    if not cfg_dir or not os.path.isdir(cfg_dir):
        return {
            "success": False,
            "message": "[ERROR] CS2 cfg directory not found.",
            "logs": ["[ERROR] CS2 cfg directory not found."],
        }

    autoexec_path = os.path.join(cfg_dir, "autoexec.cfg")
    use_low_vm = opts.get("ze_laser_viewmodel", True)
    hud_color = str(opts.get("hud_color", "0"))
    duck_key = (opts.get("duck_key") or "F7").strip() or "F7"
    mute_key = (opts.get("voice_mute_key") or opts.get("mute_key") or "F8").strip() or "F8"
    show_telemetry = bool(opts.get("clean_telemetry_hud", opts.get("show_telemetry_hud", True)))

    if use_low_vm:
        vm_lines = [
            'viewmodel_fov "68"',
            'viewmodel_offset_x "2.0"',
            'viewmodel_offset_y "2.0"',
            'viewmodel_offset_z "-2.0"',
        ]
    else:
        # User opted to keep personal config viewmodel -> zero viewmodel override
        vm_lines = []

    telem_val = "2" if show_telemetry else "1"

    block_lines = [
        "// === [CS2 COMMAND CENTER: ZE VISUAL, HUD & AUDIO DUCKING STUDIO START] ===",
        "// Added by CS2 Command Center (hobby project, not affiliated with Valve).",
        "// UNDO: delete everything from START to END, then type in the CS2 console",
        f"//       (common defaults - check your own): unbind {duck_key}; unbind {mute_key};",
        "//       volume 1; snd_musicvolume 0.5; voice_modenable 1; viewmodel_presetpos 1;",
        "//       cl_hud_color 0; cl_hud_telemetry_frametime_show 0; cl_hud_telemetry_ping_show 0;",
        "//       cl_hud_telemetry_net_misdelivery_show 0",
    ]
    if vm_lines:
        block_lines.extend([
            "// 1. ZE Viewmodel Preset (Keeps center screen clear for crouch-lasers & boss attacks)",
            *vm_lines,
        ])
    else:
        block_lines.append("// 1. Personal Viewmodel Preserved (No viewmodel override)")

    block_lines.extend([
        f'cl_hud_color "{hud_color}"',
        f'cl_hud_telemetry_frametime_show "{telem_val}"',
        f'cl_hud_telemetry_ping_show "{telem_val}"',
        f'cl_hud_telemetry_net_misdelivery_show "{telem_val}"',
        "// 2. ZE Boss & Laser Audio Ducking Toggle (Lowers 60-player gunfire while keeping Map Music & Leader Voice clear)",
        'alias "ze_focus_on" "volume 0.22; snd_voipvolume 1.0; snd_musicvolume 0.85; echo [ZE-FOCUS] Boss/Laser Audio Ducking ON (22%)"',
        'alias "ze_focus_off" "volume 1.00; snd_voipvolume 1.0; snd_musicvolume 0.55; echo [ZE-FOCUS] Normal Audio Mix Restored (100%)"',
        'alias "ze_focus_toggle" "ze_focus_on; alias ze_focus_Key ze_focus_reset"',
        'alias "ze_focus_reset" "ze_focus_off; alias ze_focus_Key ze_focus_toggle"',
        'alias "ze_focus_Key" "ze_focus_toggle"',
        f'bind "{duck_key}" "ze_focus_Key"',
        f'bind "{mute_key}" "voice_modenable_toggle"',
        # AUDIT P2-#9: host_writeconfig removed. It saved ALL current settings and binds into
        # CS2's own config on every game start, so the binds stayed even after this block was
        # deleted (undo did not work). CS2 already saves settings on exit.
        "// === [CS2 COMMAND CENTER: ZE VISUAL, HUD & AUDIO DUCKING STUDIO END] ===",
    ])
    block_text = "\n".join(block_lines) + "\n"

    try:
        existing = ""
        if os.path.exists(autoexec_path):
            with open(autoexec_path, "r", encoding="utf-8", errors="ignore") as f:
                existing = f.read()

        start_marker = "// === [CS2 COMMAND CENTER: ZE VISUAL, HUD & AUDIO DUCKING STUDIO START] ==="
        end_marker = "// === [CS2 COMMAND CENTER: ZE VISUAL, HUD & AUDIO DUCKING STUDIO END] ==="
        if start_marker in existing and end_marker in existing:
            s_idx = existing.index(start_marker)
            e_idx = existing.index(end_marker) + len(end_marker)
            before = existing[:s_idx].rstrip()
            updated = (before + "\n\n" if before else "") + block_text + existing[e_idx:].lstrip()      # no blank lines piling up at the top on every re-apply
        else:
            updated = existing.rstrip() + ("\n\n" if existing.strip() else "") + block_text

        if os.path.exists(autoexec_path) and updated.replace("\r\n", "\n") == existing.replace("\r\n", "\n"):
            msg = "autoexec.cfg already contains this exact ZE block (same viewmodel, HUD color, keys and telemetry); nothing was changed."
            return {"success": True, "unchanged": True, "message": msg, "logs": [f"[ALREADY] {msg}"]}
        with open(autoexec_path, "w", encoding="utf-8") as f:
            f.write(updated)

        msg = f"Successfully injected ZE Visual, HUD Color ({hud_color}), Laser Audio Ducking [{duck_key}], and Panic Voice Mute [{mute_key}] into {autoexec_path}!"
        logs.append(f"[ZE STUDIO] {msg}")
        return {
            "success": True,
            "message": msg,
            "logs": logs,
        }
    except Exception as e:
        err_msg = f"Failed updating autoexec.cfg: {e}"
        return {
            "success": False,
            "message": err_msg,
            "logs": [f"[ERROR] {err_msg}"],
        }


def detect_personal_viewmodel_in_autoexec(cfg_dir: str) -> Optional[dict]:
    """Scans autoexec.cfg for user's personal viewmodel commands outside the managed block."""
    if not cfg_dir:
        return None
    autoexec_path = os.path.join(cfg_dir, "autoexec.cfg")
    if not os.path.exists(autoexec_path):
        return None
    try:
        with open(autoexec_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        in_managed = False
        found_lines = []
        for line in lines:
            if "// === [CS2 COMMAND CENTER: ZE VISUAL, HUD & AUDIO DUCKING STUDIO START] ===" in line:
                in_managed = True
                continue
            if "// === [CS2 COMMAND CENTER: ZE VISUAL, HUD & AUDIO DUCKING STUDIO END] ===" in line:
                in_managed = False
                continue
            if not in_managed:
                l_str = line.strip().lower()
                if l_str.startswith("//"):
                    continue
                if "viewmodel_" in l_str:
                    found_lines.append(line.strip())
        if found_lines:
            return {"has_personal_viewmodel": True, "lines": found_lines}
        return None
    except Exception:
        return None


# ==============================================================================
# 12. POST-SESSION CS2 FRAME-TIME & NETWORK JITTER LOG ANALYZER
# ==============================================================================

def analyze_cs2_session_logs(cs2_exe: Optional[str]) -> Dict[str, Any]:
    """Passively parses CS2's console.log (if available) + active DNS/network jitter to generate a post-session health report."""
    report: Dict[str, Any] = {
        "found": False,
        "log_found": False,
        "log_path": "",
        "file_size_mb": 0.0,
        "log_size_kb": 0.0,
        "last_modified": "No console.log yet (Add -condebug to Launch Options)",
        "frame_hitch_events": 0,
        "frametime_spikes": 0,
        "net_jitter_events": 0,
        "shader_compile_events": 0,
        "shader_stalls": 0,
        "vpk_load_events": 0,
        "vpk_loads": 0,
        "last_map": "Unknown",
        "connected_servers": [],
        "live_dns_ms": 0.0,
        "live_dns_jitter": 0.0,
        "grade": "A+ (OPTIMAL)",
        "message": "console.log not found in game/csgo/console.log (Add -condebug in Launch Options).",
        "recommendation": "Everything looks optimal! Keep using Low Viewmodel & Safe CPU Priority Boost during 64-player Zombie Escape.",
        "summary_lines": [],
    }

    if cs2_exe and os.path.exists(cs2_exe):
        csgo_dir = os.path.abspath(os.path.join(os.path.dirname(cs2_exe), "..", "..", "csgo"))
        log_path = os.path.join(csgo_dir, "console.log")
        report["log_path"] = log_path
        if os.path.isfile(log_path):
            try:
                st = os.stat(log_path)
                report["found"] = True
                report["log_found"] = True
                report["log_size_kb"] = round(st.st_size / 1024.0, 1)
                report["file_size_mb"] = round(st.st_size / (1024.0 * 1024.0), 2)
                report["last_modified"] = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                with open(log_path, "rb") as f:
                    if st.st_size > 524288:
                        f.seek(st.st_size - 524288)
                    raw_text = f.read().decode("utf-8", errors="ignore")

                lines = raw_text.splitlines()
                servers_seen = []
                last_map = "Unknown"
                for ln in lines:
                    low = ln.lower()
                    if "frame time" in low or "long frame" in low or "hitch" in low:
                        report["frametime_spikes"] += 1
                    if "misdelivery" in low or "packet loss" in low or "high jitter" in low or "choke" in low:
                        report["net_jitter_events"] += 1
                    if "shader" in low and ("compile" in low or "stall" in low):
                        report["shader_stalls"] += 1
                    if ".vpk" in low and ("mounted" in low or "loading" in low):
                        report["vpk_loads"] += 1
                    if "ze_" in low:
                        m_map = re.search(r"(ze_[a-zA-Z0-9_]+)", ln)
                        if m_map:
                            last_map = m_map.group(1)
                    if "connecting to" in low or "connected to" in low:
                        m = re.search(r"(\b(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}\b)", ln)
                        if m and m.group(1) not in servers_seen:
                            servers_seen.append(m.group(1))
                report["connected_servers"] = servers_seen[-5:]
                report["last_map"] = last_map
                report["frame_hitch_events"] = report["frametime_spikes"]
                report["shader_compile_events"] = report["shader_stalls"]
                report["vpk_load_events"] = report["vpk_loads"]
                report["message"] = f"Analyzed console.log ({report['file_size_mb']} MB • Updated {report['last_modified']})."
            except Exception as e:
                report["message"] = f"Could not read console.log: {e}"

    if str(report.get("message", "")).startswith("Could not read"):
        report["grade"] = "N/A (LOG NOT READABLE)"
        report["recommendation"] = "The log could not be read, so no grade is given. Close CS2 and try again."
    elif not report.get("found"):
        report["grade"] = "N/A (NO LOG YET)"
        report["recommendation"] = "There is no console.log yet, so there is nothing to grade. Add -condebug to your launch options and play a session."
    elif report["frame_hitch_events"] > 40 or report["net_jitter_events"] > 40:
        report["grade"] = "C (ATTENTION RECOMMENDED)"
        report["recommendation"] = "High frame-time or network spikes detected. Apply Safe CS2 CPU Priority Boost, switch to Cloudflare Gaming DNS, and verify SSD health."
    elif report["frame_hitch_events"] > 15 or report["net_jitter_events"] > 15:
        report["grade"] = "B (MINOR SPIKES DETECTED)"
        report["recommendation"] = "Minor frame hitches or network jitter detected. Run 'APPLY SAFE CS2 CPU PRIORITY BOOST' and benchmark your Gaming DNS."

    return report


