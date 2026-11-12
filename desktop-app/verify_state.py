"""Read-only checks behind the 'Check' buttons on Engine Tweaks and PC Maintenance.

They read the real state of this PC right now (registry values, files, folder sizes, the Recycle Bin, the power plan) so a user can see what
a tweak or clean-up changed, before and after, without trusting the app's own log. Nothing here writes or deletes anything. Every row also
says how to check the same thing in Windows without this app.

Row: {"key", "label", "state": "ok" | "off" | "info" | "na", "value", "detail", "how"}
  value  = one short line shown under the tweak / clean-up ("Now: ...")
  detail = what is in there: folders and sizes, registry values, file dates
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
    if n < 1024 * 1024:
        return f"{max(0, round(n / 1024))} KB"
    return f"{n / (1024 * 1024):.1f} MB" if n < 1024 ** 3 else f"{n / (1024 ** 3):.2f} GB"


def _row(key: str, label: str, state: str, value: str, how: str, detail: str = "") -> Dict[str, str]:
    return {"key": key, "label": label, "state": state, "value": value, "how": how, "detail": detail}


def _when(ts: float) -> str:
    import datetime
    return datetime.datetime.fromtimestamp(ts).strftime("%d %b %Y %H:%M") if ts else "unknown"


def _breakdown(parts: List[Tuple[str, int, int]]) -> str:
    """'NVIDIA DXCache 60.2 MB (80 files); D3DSCache 5.9 MB (5 files)' for the parts that hold anything."""
    shown = [f"{name} {mb(b)} ({n} files)" for name, n, b in sorted(parts, key=lambda p: -p[2]) if n]
    return "; ".join(shown) if shown else "all empty"


# ----------------------------------------------------------------------------------------------------------------------------------
def engine_check(paths: Dict[str, Optional[str]]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    hkcu = winreg.HKEY_CURRENT_USER if winreg else None

    # Game DVR (Windows background recording)
    raw = []
    if hkcu is not None:
        for name, _v in core_logic._DVR_ON_VALUES:
            raw.append(f"{name}={core_logic._reg_value(hkcu, core_logic._DVR_KEY, name)}")
        raw.append(f"AppCaptureEnabled={core_logic._reg_value(hkcu, core_logic._DVR_KEY2, 'AppCaptureEnabled')}")
    dvr_detail = "Registry (HKEY_CURRENT_USER): " + ", ".join(raw) + ". The tweak sets GameDVR_Enabled=0 and AppCaptureEnabled=0." if raw else ""
    if hkcu is not None and core_logic._dvr_is(core_logic._DVR_ON_VALUES, 0):
        rows.append(_row("gamedvr", "Windows Game DVR background recording", "ok", "Off (set by the tweak)",
                         "Windows Settings > Gaming > Captures: 'Record what happened' is off.", dvr_detail))
    elif hkcu is not None and core_logic._dvr_is(core_logic._DVR_OFF_VALUES, 1):
        rows.append(_row("gamedvr", "Windows Game DVR background recording", "off", "On (Windows default)",
                         "Windows Settings > Gaming > Captures: 'Record what happened'.", dvr_detail))
    else:
        rows.append(_row("gamedvr", "Windows Game DVR background recording", "info", "Partly changed (by Windows Settings or another tool)",
                         "Windows Settings > Gaming > Captures.", dvr_detail))

    # Fullscreen optimizations for cs2.exe
    exe = paths.get("cs2_exe")
    if not exe or not os.path.isfile(exe):
        rows.append(_row("fullscreen", "Fullscreen optimizations off for cs2.exe", "na", "CS2 was not found on this PC", ""))
    else:
        val = core_logic._reg_value(hkcu, r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers", exe) if hkcu is not None else None
        on = bool(val) and "DISABLEDXMAXIMIZEDWINDOWEDMODE" in str(val).upper()
        rows.append(_row("fullscreen", "Fullscreen optimizations off for cs2.exe", "ok" if on else "off",
                         "Disabled (set by the tweak)" if on else "Windows default (enabled)",
                         f"Right-click {exe} > Properties > Compatibility: 'Disable fullscreen optimizations' is ticked.",
                         f"Registry value for {exe}: {val!r}" if val else f"No compatibility flag is set for {exe}."))

    # Autoexec performance block
    cfg = paths.get("cfg_dir")
    if not cfg or not os.path.isdir(cfg):
        rows.append(_row("autoexec", "Performance block in autoexec.cfg", "na", "CS2's cfg folder was not found", ""))
    else:
        path = os.path.join(cfg, "autoexec.cfg")
        lines = 0
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            has = core_logic.PERF_TITLE in text
            lines = sum(1 for l in text.splitlines() if l.strip() and not l.strip().startswith("//"))
        except OSError:
            has = False
        ae_detail = (f"{path}: {mb(os.path.getsize(path))}, {lines} command lines, last changed {_when(os.path.getmtime(path))}. "
                     f"A backup of your original is kept as autoexec_backup.cfg ({'present' if os.path.isfile(os.path.join(cfg, 'autoexec_backup.cfg')) else 'not made yet'}).") \
            if os.path.isfile(path) else f"{path} does not exist yet."
        rows.append(_row("autoexec", "Performance block in autoexec.cfg", "ok" if has else "off",
                         "Present" if has else ("autoexec.cfg has no block from this app" if os.path.isfile(path) else "autoexec.cfg does not exist yet"),
                         f"Open {path} in Notepad and look for '{core_logic.PERF_TITLE}'.", ae_detail))

    # Shader caches (a measurement: drivers refill them while you play)
    files = size = 0
    found = []
    parts = []
    for d in core_logic.shader_cache_dirs():
        f, sz = folder_size(d)
        if os.path.isdir(d):
            found.append(d)
            vendor = os.path.basename(os.path.dirname(d))
            parts.append(("DirectX D3DSCache" if os.path.basename(d) == "D3DSCache" else f"{vendor} {os.path.basename(d)}", f, sz))
        files += f
        size += sz
    rows.append(_row("shaders", "GPU shader caches", "info", f"{files} files, {mb(size)}" if found else "No shader cache folders on this PC",
                     "Right after cleaning this is close to 0; the driver rebuilds it while you play, which is normal. Files the driver has open are skipped. "
                     "Folders: " + (", ".join(found) if found else "none"),
                     _breakdown(parts) if found else ""))

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
    newest = 0.0
    for pat in patterns:
        for fp in glob.glob(pat):
            try:
                dump_bytes += os.path.getsize(fp)
                newest = max(newest, os.path.getmtime(fp))
                dumps += 1
            except OSError:
                pass
    rows.append(_row("dumps", "CS2 crash dumps", "ok" if dumps == 0 else "off",
                     "None left" if dumps == 0 else f"{dumps} file(s), {mb(dump_bytes)} can be cleaned",
                     "Folders: %LOCALAPPDATA%\\CrashDumps and CS2's game\\csgo\\dumps.",
                     f"Newest dump: {_when(newest)}. Only crash dumps and crash_*.txt are cleaned; console.log is never touched." if dumps else
                     "Only crash dumps and crash_*.txt are cleaned; console.log is never touched."))

    # Power plan (informational: the right plan depends on the CPU)
    name, guid = core_logic.get_active_power_plan()
    rows.append(_row("power", "Active Windows power plan", "info", name or "Unknown",
                     "Control Panel > Power Options (or Settings > System > Power on Windows 11).", f"Plan id {guid}" if guid else ""))
    return rows


# ----------------------------------------------------------------------------------------------------------------------------------
def maint_check(paths: Dict[str, Optional[str]], now: Optional[float] = None) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    now = now or time.time()
    cutoff = now - core_logic.TEMP_MIN_AGE_SECONDS

    user_t = os.environ.get("TEMP", "")
    win_t = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "Temp")
    f1, s1 = folder_size(user_t, cutoff)
    f2, s2 = folder_size(win_t, cutoff)
    a1, b1 = folder_size(user_t)
    a2, b2 = folder_size(win_t)
    n, b = f1 + f2, s1 + s2
    rows.append(_row("temp", "Temp files older than 24 hours", "ok" if n == 0 else "off", "Nothing to clean" if n == 0 else f"{n} files, {mb(b)} can be cleaned",
                     "Press Win+R, type %TEMP% and press Enter. Files that a program still has open are always skipped.",
                     f"Your temp folder ({user_t}): {mb(s1)} older than 24 h of {mb(b1)} in total. Windows\\Temp: {mb(s2)} of {mb(b2)} "
                     f"(only Administrator can clean most of it). {max(0, a1 + a2 - n)} newer files are left alone on purpose: running programs and installers may still need them."))

    sw = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "SoftwareDistribution", "Download")
    n, b = folder_size(sw)
    admin = core_logic.is_admin()
    rows.append(_row("win_update", "Windows Update download cache", "ok" if n == 0 else "off",
                     "Empty" if n == 0 else f"{n} files, {mb(b)}" + ("" if admin else " (needs Administrator to clean)"),
                     f"{sw}. Only already downloaded update installers are removed; Windows downloads again whatever it still needs.",
                     "Running as Administrator: this clean-up will work." if admin else "Not running as Administrator: this clean-up is skipped and says so. Use Relaunch as Administrator."))

    total_n = total_b = 0
    appdata = os.environ.get("APPDATA", "")
    targets = []
    if appdata:
        base = os.path.join(appdata, "discord")
        targets += [os.path.join(base, "Cache", "Cache_Data"), os.path.join(base, "Code Cache"), os.path.join(base, "GPUCache")]
    steam = paths.get("steam_path")
    if steam:
        targets.append(os.path.join(steam, "appcache", "httpcache"))
    parts = []
    for t in targets:
        n, b = folder_size(t)
        total_n += n
        total_b += b
        parts.append(("Steam web cache" if "httpcache" in t else "Discord " + os.path.basename(t), n, b))
    rows.append(_row("discord_steam", "Discord and Steam web caches", "ok" if total_n == 0 else "off",
                     "Empty" if total_n == 0 else f"{total_n} files, {mb(total_b)}",
                     "Discord and Steam fill these again while they run; your logins are not in them.",
                     _breakdown(parts) + ". Logins, settings and downloads are in other folders and are never touched."))

    exp = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Explorer")
    n = b = 0
    tn = tb = 0
    for pat in ("thumbcache_*.db", "iconcache_*.db"):
        for fp in glob.glob(os.path.join(exp, pat)):
            try:
                sz = os.path.getsize(fp)
            except OSError:
                continue
            b += sz
            n += 1
            if pat.startswith("thumb"):
                tn, tb = tn + 1, tb + sz
    rows.append(_row("thumb", "Explorer thumbnail caches", "info", f"{n} files, {mb(b)}",
                     "Explorer keeps some of these open and rebuilds them as you browse folders, so they never reach 0.",
                     f"Thumbnails {mb(tb)} ({tn} files), icons {mb(b - tb)} ({n - tn} files) in {exp}. Only worth cleaning when pictures or icons show wrong."))

    rb = core_logic.recycle_bin_info()
    if rb is None:
        rows.append(_row("recycle", "Recycle Bin", "na", "Windows did not report it", "Open the Recycle Bin on the desktop."))
    else:
        rows.append(_row("recycle", "Recycle Bin", "ok" if rb[0] == 0 else "off", "Empty" if rb[0] == 0 else f"{rb[0]} item(s), {mb(rb[1])}",
                         "Open the Recycle Bin on the desktop.",
                         "Emptying it is permanent: look inside first if you might still need something. It is off by default for that reason."))

    rows.append(_row("dns", "DNS cache", "info", "Refills within seconds",
                     "Windows refills the DNS cache within seconds of any connection, so there is nothing lasting to check. "
                     "To flush it yourself: Command Prompt, ipconfig /flushdns."))
    return rows


def summary(rows: List[Dict[str, Any]]) -> str:
    ok = sum(1 for r in rows if r["state"] == "ok")
    off = sum(1 for r in rows if r["state"] == "off")
    return f"{ok} in place or clean, {off} not applied or can be cleaned, {len(rows) - ok - off} for information."
