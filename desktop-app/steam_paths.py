"""Finds Steam, its game libraries and Counter-Strike 2 on any PC, without assuming this PC's layout.

Order of trust: an explicit override (used when an elevated copy is started on behalf of another account), then what Steam itself recorded
(registry, its own libraryfolders.vdf and appmanifest_730.acf), then common install folders on fixed drives only (network and removable
drives are never probed, so an offline share cannot slow the start).
"""
import ctypes
import glob
import os
import re
import winreg
from typing import Dict, List, Optional

import steam_vdf

CS2_APPID = "730"
DEFAULT_CS2_FOLDER = "Counter-Strike Global Offensive"


def fixed_drives() -> List[str]:
    """Drive roots like 'C:\\' that are real fixed disks."""
    out: List[str] = []
    try:
        mask = ctypes.windll.kernel32.GetLogicalDrives()
        for i in range(26):
            if mask & (1 << i):
                root = f"{chr(65 + i)}:\\"
                if ctypes.windll.kernel32.GetDriveTypeW(root) == 3:      # DRIVE_FIXED
                    out.append(root)
    except Exception:
        pass
    return out


def _looks_like_steam(path: Optional[str]) -> bool:
    return bool(path) and os.path.isdir(path) and (os.path.isfile(os.path.join(path, "steam.exe")) or os.path.isdir(os.path.join(path, "steamapps")))


def _reg_values() -> List[str]:
    """Every Steam folder the registry mentions (HKCU first, then both HKLM views, then the uninstall entry)."""
    found: List[str] = []
    spots = [
        (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", 0, ("SteamPath", "InstallPath")),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Valve\Steam", winreg.KEY_WOW64_64KEY, ("InstallPath", "SteamPath")),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Valve\Steam", winreg.KEY_WOW64_32KEY, ("InstallPath", "SteamPath")),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Valve\Steam", 0, ("InstallPath", "SteamPath")),
    ]
    for hive, sub, view, names in spots:
        try:
            with winreg.OpenKey(hive, sub, 0, winreg.KEY_READ | view) as k:
                for name in names:
                    try:
                        found.append(str(winreg.QueryValueEx(k, name)[0]))
                    except OSError:
                        pass
        except OSError:
            pass
    for view in (winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam", 0, winreg.KEY_READ | view) as k:
                for name in ("InstallLocation", "UninstallString", "DisplayIcon"):
                    try:
                        val = str(winreg.QueryValueEx(k, name)[0]).strip('"')
                        found.append(val if name == "InstallLocation" else os.path.dirname(val))
                    except OSError:
                        pass
        except OSError:
            pass
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", 0, winreg.KEY_READ) as k:
            exe = str(winreg.QueryValueEx(k, "SteamExe")[0])
            found.append(os.path.dirname(exe))
    except OSError:
        pass
    return found


def find_steam_path() -> Optional[str]:
    override = os.environ.get("CS2CC_STEAM_PATH", "").strip()
    candidates: List[str] = [override] if override else []
    candidates += _reg_values()
    for drive in fixed_drives():
        for sub in (r"Program Files (x86)\Steam", r"Program Files\Steam", "Steam", r"Games\Steam", r"Games\SteamLibrary"):
            candidates.append(os.path.join(drive, sub))
    for c in candidates:
        c = os.path.normpath(c) if c else c
        if _looks_like_steam(c):
            return c
    return None


def read_library_folders(steam_path: Optional[str]) -> List[str]:
    """Library folders recorded in steamapps/libraryfolders.vdf (new format with "path", and the old format with plain values)."""
    libs: List[str] = []
    if not steam_path:
        return libs
    vdf = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    try:
        with open(vdf, "r", encoding="utf-8", errors="ignore") as fh:
            text = fh.read()
    except OSError:
        return libs
    try:
        root = steam_vdf.parse(text)
        lf = next((n for n in root if n.key.lower() == "libraryfolders"), None)
        for n in (lf.children or []) if lf else []:
            if n.value and re.fullmatch(r"\d+", n.key):
                libs.append(n.value)                               # old format: "1" "D:\Games\Steam"
            elif n.children is not None:
                p = n.child("path")
                if p is not None and p.value:
                    libs.append(p.value)
    except steam_vdf.VdfError:
        libs = [m.replace("\\\\", "\\") for m in re.findall(r'"path"\s+"([^"]+)"', text)]
    return libs


def steam_libraries(steam_path: Optional[str] = None) -> List[str]:
    """Every library folder that exists: Steam's own folder, the ones Steam lists, and X:\\SteamLibrary on fixed drives."""
    steam_path = steam_path or find_steam_path()
    out: List[str] = []
    seen = set()

    def add(p: Optional[str]) -> None:
        if not p:
            return
        p = os.path.normpath(p)
        key = os.path.normcase(os.path.abspath(p))
        if key not in seen and os.path.isdir(p):
            seen.add(key)
            out.append(p)

    add(steam_path)
    for p in read_library_folders(steam_path):
        add(p)
    for drive in fixed_drives():
        add(os.path.join(drive, "SteamLibrary"))
    return out


def _installdir_from_manifest(lib: str) -> Optional[str]:
    acf = os.path.join(lib, "steamapps", f"appmanifest_{CS2_APPID}.acf")
    try:
        with open(acf, "r", encoding="utf-8", errors="ignore") as fh:
            root = steam_vdf.parse(fh.read())
        state = next((n for n in root if n.key.lower() == "appstate"), None)
        d = state.child("installdir") if state else None
        return d.value if d is not None and d.value else None
    except (OSError, steam_vdf.VdfError):
        return None


def find_cs2(libraries: List[str]) -> Dict[str, Optional[str]]:
    """The CS2 install. A library whose appmanifest_730.acf says CS2 lives there wins over a leftover folder in another library."""
    ranked: List[tuple] = []
    for lib in libraries:
        folder = _installdir_from_manifest(lib)
        names = [folder] if folder else []
        names.append(DEFAULT_CS2_FOLDER)
        for name in names:
            cs2_dir = os.path.join(lib, "steamapps", "common", name)
            exe = os.path.join(cs2_dir, "game", "bin", "win64", "cs2.exe")
            if os.path.isfile(exe):
                ranked.append((0 if folder else 1, cs2_dir, exe))
                break
    result: Dict[str, Optional[str]] = {"cs2_dir": None, "cs2_exe": None, "cfg_dir": None, "autoexec_cfg": None}
    if not ranked:
        return result
    ranked.sort(key=lambda r: r[0])
    _, cs2_dir, exe = ranked[0]
    result["cs2_dir"], result["cs2_exe"] = cs2_dir, exe
    cfg = os.path.join(cs2_dir, "game", "csgo", "cfg")
    if os.path.isdir(cfg):
        result["cfg_dir"] = cfg
        for name in os.listdir(cfg):
            if name.lower() == "autoexec.cfg":
                result["autoexec_cfg"] = os.path.join(cfg, name)
                break
    return result


def library_of(cs2_dir: Optional[str]) -> Optional[str]:
    """...\\<library>\\steamapps\\common\\<game>  ->  ...\\<library>"""
    if not cs2_dir:
        return None
    lib = os.path.dirname(os.path.dirname(os.path.dirname(os.path.normpath(cs2_dir))))
    return lib if os.path.isdir(lib) else None


def workshop_dirs(libraries: List[str]) -> List[str]:
    out = []
    for lib in libraries:
        d = os.path.join(lib, "steamapps", "workshop", "content", CS2_APPID)
        if os.path.isdir(d):
            out.append(d)
    return out
