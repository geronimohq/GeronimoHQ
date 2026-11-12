"""Read-only checks behind the 'Check' buttons on Engine Tweaks and PC Maintenance.

They read the real state of this PC right now (registry values, files, folder sizes, the Recycle Bin, the power plan) so a user can see what
a tweak or clean-up changed, before and after, without trusting the app's own log. Nothing here writes or deletes anything. Every row also
says how to check the same thing in Windows without this app.

Row: {"key", "label", "state": "ok" | "off" | "info" | "na", "value", "how"}
  ok   = the tweak is in place / nothing left to clean
  off  = not applied (the Windows default) / something can be cleaned
  info = a measurement, neither good nor bad
  na   = cannot be checked on this PC (for example CS2 not found)
"""
import glob
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import core_logic

try:
    import winreg
except ImportError:                                   # only for running the tests' pure helpers elsewhere
    winreg = None


def folder_size(path: str, older_than: Optional[float] = None) -> Tuple[int, int]:
    """(files, bytes) under path; with older_than (epoch seconds) only files last modified before it."""
    files = size = 0
    if not path or not os.path.isdir(path):
        return 0, 0
    for root, _dirs, names in os.walk(path):
        for n in names:
            try:
                st = os.stat(os.path.join(root, n))
            except OSError:
                continue
            if older_than is not None and st.st_mtime > older_than:
                continue
            files += 1
            size += st.st_size
    return files, size


def mb(n: int) -> str:
    return f"{n / (1024 * 1024):.1f} MB" if n < 1024 ** 3 else f"{n / (1024 ** 3):.2f} GB"


def _row(key: str, label: str, state: str, value: str, how: str) -> Dict[str, str]:
    return {"key": key, "label": label, "state": state, "value": value, "how": how}


# ----------------------------------------------------------------------------------------------------------------------------------
def engine_check(paths: Dict[str, Optional[str]]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    hkcu = winreg.HKEY_CURRENT_USER if winreg else None

    # Game DVR (Windows background recording)
    if hkcu is not None and core_logic._dvr_is(core_logic._DVR_ON_VALUES, 0):
        rows.append(_row("gamedvr", "Windows Game DVR background recording", "ok", "Off (set by the tweak)",
                         "Windows Settings > Gaming > Captures: 'Record what happened' is off."))
    elif hkcu is not None and core_logic._dvr_is(core_logic._DVR_OFF_VALUES, 1):
        rows.append(_row("gamedvr", "Windows Game DVR background recording", "off", "On (Windows default)",
                         "Windows Settings > Gaming > Captures: 'Record what happened'."))
    else:
        rows.append(_row("gamedvr", "Windows Game DVR background recording", "info", "Partly changed (by Windows Settings or another tool)",
                         "Windows Settings > Gaming > Captures."))

    # Fullscreen optimizations for cs2.exe
    exe = paths.get("cs2_exe")
    if not exe or not os.path.isfile(exe):
        rows.append(_row("fullscreen", "Fullscreen optimizations off for cs2.exe", "na", "CS2 was not found on this PC", ""))
    else:
        val = core_logic._reg_value(hkcu, r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers", exe) if hkcu is not None else None
        on = bool(val) and "DISABLEDXMAXIMIZEDWINDOWEDMODE" in str(val).upper()
        rows.append(_row("fullscreen", "Fullscreen optimizations off for cs2.exe", "ok" if on else "off",
                         "Disabled (set by the tweak)" if on else "Windows default (enabled)",
                         f"Right-click {exe} > Properties > Compatibility: 'Disable fullscreen optimizations' is ticked."))

    # Autoexec performance block
    cfg = paths.get("cfg_dir")
    if not cfg or not os.path.isdir(cfg):
        rows.append(_row("autoexec", "Performance block in autoexec.cfg", "na", "CS2's cfg folder was not found", ""))
    else:
        path = os.path.join(cfg, "autoexec.cfg")
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                has = core_logic.PERF_TITLE in f.read()
        except OSError:
            has = False
        rows.append(_row("autoexec", "Performance block in autoexec.cfg", "ok" if has else "off",
                         "Present" if has else ("autoexec.cfg has no block from this app" if os.path.isfile(path) else "autoexec.cfg does not exist yet"),
                         f"Open {path} in Notepad and look for '{core_logic.PERF_TITLE}'."))

    # Shader caches (a measurement: drivers refill them while you play)
    files = size = 0
    found = []
    for d in core_logic.shader_cache_dirs():
        f, s = folder_size(d)
        if os.path.isdir(d):
            found.append(d)
        files += f
        size += s
    rows.append(_row("shaders", "GPU shader caches", "info", f"{files} files, {mb(size)} now" if found else "No shader cache folders on this PC",
                     "Right after cleaning this is close to 0; the driver rebuilds it while you play, which is normal. "
                     "Folders: " + (", ".join(found) if found else "none")))

    # CS2 crash dumps
    cs2 = paths.get("cs2_dir")
    dumps = 0
    dump_bytes = 0
    patterns = []
    local = os.environ.get("LOCALAPPDATA", "")
    if local:
        patterns += [os.path.join(local, "CrashDumps", "*cs2*.dmp"), os.path.join(local, "CrashDumps", "*csgo*.dmp")]
    if cs2:
        patterns += [os.path.join(cs2, "game", "bin", "win64", "*.dmp"), os.path.join(cs2, "game", "csgo", "*.dmp"),
                     os.path.join(cs2, "game", "csgo", "dumps", "*.dmp"), os.path.join(cs2, "game", "csgo", "dumps", "*.mdmp")]
    for pat in patterns:
        for fp in glob.glob(pat):
            try:
                dump_bytes += os.path.getsize(fp)
                dumps += 1
            except OSError:
                pass
    rows.append(_row("dumps", "CS2 crash dumps", "ok" if dumps == 0 else "off",
                     "None left" if dumps == 0 else f"{dumps} file(s), {mb(dump_bytes)} can be cleaned",
                     "Folders: %LOCALAPPDATA%\\CrashDumps and CS2's game\\csgo\\dumps."))

    # Power plan (informational: the right plan depends on the CPU)
    name, _guid = core_logic.get_active_power_plan()
    rows.append(_row("power", "Active Windows power plan", "info", name or "Unknown",
                     "Control Panel > Power Options (or Settings > System > Power on Windows 11)."))
    return rows


# ----------------------------------------------------------------------------------------------------------------------------------
def maint_check(paths: Dict[str, Optional[str]], now: Optional[float] = None) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    now = now or time.time()
    cutoff = now - core_logic.TEMP_MIN_AGE_SECONDS

    f1, s1 = folder_size(os.environ.get("TEMP", ""), cutoff)
    f2, s2 = folder_size(os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "Temp"), cutoff)
    n, b = f1 + f2, s1 + s2
    rows.append(_row("temp", "Temp files older than 24 hours", "ok" if n == 0 else "off", "None" if n == 0 else f"{n} files, {mb(b)}",
                     "Press Win+R, type %TEMP% and press Enter. Files that a program still has open are always skipped."))

    sw = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "SoftwareDistribution", "Download")
    n, b = folder_size(sw)
    rows.append(_row("win_update", "Windows Update download cache", "ok" if n == 0 else "off", "Empty" if n == 0 else f"{n} files, {mb(b)}",
                     f"{sw} (clearing it needs Administrator)."))

    total_n = total_b = 0
    appdata = os.environ.get("APPDATA", "")
    targets = []
    if appdata:
        base = os.path.join(appdata, "discord")
        targets += [os.path.join(base, "Cache", "Cache_Data"), os.path.join(base, "Code Cache"), os.path.join(base, "GPUCache")]
    steam = paths.get("steam_path")
    if steam:
        targets.append(os.path.join(steam, "appcache", "httpcache"))
    for t in targets:
        n, b = folder_size(t)
        total_n += n
        total_b += b
    rows.append(_row("discord_steam", "Discord and Steam web caches", "ok" if total_n == 0 else "off",
                     "Empty" if total_n == 0 else f"{total_n} files, {mb(total_b)}",
                     "Discord and Steam fill these again while they run; your logins are not in them."))

    exp = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Explorer")
    n = b = 0
    for pat in ("thumbcache_*.db", "iconcache_*.db"):
        for fp in glob.glob(os.path.join(exp, pat)):
            try:
                b += os.path.getsize(fp)
                n += 1
            except OSError:
                pass
    rows.append(_row("thumb", "Explorer thumbnail caches", "info", f"{n} files, {mb(b)}",
                     "Explorer keeps some of these open and rebuilds them as you browse folders, so they never reach 0."))

    rb = core_logic.recycle_bin_info()
    if rb is None:
        rows.append(_row("recycle", "Recycle Bin", "na", "Windows did not report it", "Open the Recycle Bin on the desktop."))
    else:
        rows.append(_row("recycle", "Recycle Bin", "ok" if rb[0] == 0 else "off", "Empty" if rb[0] == 0 else f"{rb[0]} item(s), {mb(rb[1])}",
                         "Open the Recycle Bin on the desktop."))

    rows.append(_row("dns", "DNS cache", "na", "Not measurable",
                     "Windows refills the DNS cache within seconds of any connection, so there is nothing lasting to check. "
                     "To flush it yourself: Command Prompt, ipconfig /flushdns."))
    return rows


def summary(rows: List[Dict[str, Any]]) -> str:
    ok = sum(1 for r in rows if r["state"] == "ok")
    off = sum(1 for r in rows if r["state"] == "off")
    return f"{ok} in place or clean, {off} not applied or can be cleaned, {len(rows) - ok - off} for information."
