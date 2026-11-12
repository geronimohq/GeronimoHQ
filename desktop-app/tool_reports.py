"""Plain-text reports of the long Windows tools (SFC, DISM health restore, DISM WinSxS clean-up, SSD TRIM), so a user can read, print or
share the result outside the app, plus a way to open the record Windows itself keeps for each tool.

Reports go to Documents\\CS2 Command Center\\Reports (the real Documents folder, also when OneDrive moved it); the newest 10 per tool are
kept. CS2CC_REPORTS_DIR overrides the folder (tests use it so they never write into the real Documents)."""
import datetime
import os
import re
import subprocess
from typing import Any, Dict, List, Optional

KEEP_PER_TOOL = 10
SYSTEM_ROOT = os.environ.get("SystemRoot", r"C:\Windows")
CBS_LOG = os.path.join(SYSTEM_ROOT, "Logs", "CBS", "CBS.log")
DISM_LOG = os.path.join(SYSTEM_ROOT, "Logs", "DISM", "dism.log")

TITLES = {"sfc": "System File Checker (SFC)", "dism": "DISM health restore", "winsxs": "DISM WinSxS clean-up", "trim": "SSD TRIM"}

# Where Windows keeps its own record of each tool, in words a user can follow without this app.
WINDOWS_RECORD = {
    "sfc": [f"SFC writes every step to {CBS_LOG} (lines marked [SR]).",
            "Microsoft's own way to read them: open Command Prompt as Administrator and run",
            '  findstr /c:"[SR]" %windir%\\Logs\\CBS\\CBS.log > "%userprofile%\\Desktop\\sfcdetails.txt"',
            "then open sfcdetails.txt on your Desktop. The app's 'Windows' record' button does the same for you."],
    "dism": [f"DISM writes every step to {DISM_LOG}.",
             "Open it with Notepad; the newest lines are at the bottom. The app's 'Windows' record' button opens its folder."],
    "winsxs": [f"DISM writes every step to {DISM_LOG}.",
               "Open it with Notepad; the newest lines are at the bottom. The app's 'Windows' record' button opens its folder."],
    "trim": ["Windows shows the last TRIM of each drive in 'Defragment and Optimize Drives' (Start menu, search 'Optimize'):",
             "the 'Last run' column and 'Current status: OK'. The app's 'Windows' record' button opens that window.",
             "Event Viewer also lists each run: Windows Logs > Application, source 'defrag' (event 258)."],
}


def _documents() -> Optional[str]:
    """The user's real Documents folder (follows a OneDrive or GPO redirect), or None."""
    try:
        import ctypes
        from ctypes import wintypes
        buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
        if ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf) == 0 and buf.value:      # CSIDL_PERSONAL
            return buf.value
    except Exception:
        pass
    home = os.path.expanduser("~")
    return os.path.join(home, "Documents") if home and home != "~" else None


def reports_dir(create: bool = True) -> str:
    base = os.environ.get("CS2CC_REPORTS_DIR")
    if not base:
        docs = _documents()
        if docs:
            base = os.path.join(docs, "CS2 Command Center", "Reports")
        else:
            import app_config
            base = os.path.join(app_config.get_storage_dir(), "Reports")
    if create:
        os.makedirs(base, exist_ok=True)
    return base


def _stamp(now: Optional[datetime.datetime] = None) -> str:
    return (now or datetime.datetime.now()).strftime("%Y-%m-%d_%H%M%S")


def build_text(res: Dict[str, Any], app_version: str = "", now: Optional[datetime.datetime] = None) -> str:
    tool = res.get("tool", "")
    when = (now or datetime.datetime.now()).strftime("%d %B %Y, %H:%M")
    lines: List[str] = [
        f"CS2 Command Center{(' ' + app_version) if app_version else ''} - {TITLES.get(tool, tool)} report",
        "=" * 72,
        f"Date:     {when}",
        f"Result:   {res.get('headline', '')}",
        f"Verdict:  {'OK' if res.get('ok') else 'Needs attention'} ({res.get('status', '')})",
    ]
    if res.get("seconds"):
        s = int(res["seconds"])
        lines.append(f"Duration: {s // 60} min {s % 60} s" if s >= 60 else f"Duration: {s} s")
    if res.get("detail"):
        lines += ["", "What this means:", f"  {res['detail']}"]
    if res.get("next"):
        lines += ["", "What to do next:", f"  {res['next']}"]
    ev = res.get("evidence") or []
    if ev:
        lines += ["", "How the app knows:"] + [f"  - {e}" for e in ev]
    sr = res.get("sr_lines") or []
    if sr:
        lines += ["", f"SFC's own lines from CBS.log for this run ({len(sr)} lines, newest last):"] + [f"  {l}" for l in sr]
    lines += ["", "Windows' own record of this tool:"] + [f"  {l}" for l in WINDOWS_RECORD.get(tool, [])]
    lines += ["", "This file was written by CS2 Command Center so you can keep, print or share the result. Deleting it changes nothing on your PC."]
    return "\r\n".join(lines) + "\r\n"


def write_report(res: Dict[str, Any], app_version: str = "", now: Optional[datetime.datetime] = None) -> str:
    """Writes the report and keeps only the newest KEEP_PER_TOOL per tool. Returns the file path."""
    tool = res.get("tool", "tool")
    folder = reports_dir()
    path = os.path.join(folder, f"{tool}_{_stamp(now)}.txt")
    with open(path, "w", encoding="utf-8-sig", newline="") as f:        # BOM so Notepad shows any non-English text correctly
        f.write(build_text(res, app_version, now))
    prune(tool, folder)
    return path


def prune(tool: str, folder: Optional[str] = None) -> None:
    folder = folder or reports_dir()
    mine = sorted(f for f in os.listdir(folder) if re.fullmatch(rf"{re.escape(tool)}_\d{{4}}-\d{{2}}-\d{{2}}_\d{{6}}\.txt", f))
    for old in mine[:-KEEP_PER_TOOL]:
        try:
            os.remove(os.path.join(folder, old))
        except OSError:
            pass


def is_report_path(path: str) -> bool:
    """Only files this module wrote may be opened from the page."""
    try:
        folder = os.path.normcase(os.path.abspath(reports_dir(create=False)))
        p = os.path.normcase(os.path.abspath(path))
    except (TypeError, ValueError):
        return False
    return os.path.dirname(p) == folder and p.endswith(".txt") and os.path.isfile(path)


def sfc_details(limit_bytes: int = 30 * 1024 * 1024) -> Dict[str, Any]:
    """Microsoft's documented way to read SFC's result: every [SR] line of CBS.log, saved to a text file. CBS.log can usually only be
    read as Administrator."""
    try:
        size = os.path.getsize(CBS_LOG)
        with open(CBS_LOG, "rb") as f:
            f.seek(max(0, size - limit_bytes))
            data = f.read()
    except PermissionError:
        return {"ok": False, "error": "Windows only lets Administrator read CBS.log. Use Relaunch as Administrator, or run the findstr command from the report."}
    except OSError:
        return {"ok": False, "error": f"CBS.log was not found at {CBS_LOG}. SFC may not have run on this PC yet."}
    lines = [l for l in data.decode("utf-8", errors="replace").splitlines() if "[SR]" in l]
    if not lines:
        return {"ok": False, "error": "CBS.log has no SFC lines yet. Run SFC first."}
    path = os.path.join(reports_dir(), f"sfc_cbs_details_{_stamp()}.txt")
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        f.write("\r\n".join(["SFC lines ([SR]) from " + CBS_LOG, "Same as: findstr /c:\"[SR]\" %windir%\\Logs\\CBS\\CBS.log", ""] + lines) + "\r\n")
    return {"ok": True, "path": path, "lines": len(lines)}


def open_windows_record(tool: str, opener=None) -> Dict[str, Any]:
    """Opens Windows' own record of a tool: SFC's [SR] lines, the DISM log folder, or Optimize Drives (Last run) for TRIM."""
    opener = opener or os.startfile
    try:
        if tool == "sfc":
            r = sfc_details()
            if r["ok"]:
                opener(r["path"])
            return r
        if tool in ("dism", "winsxs"):
            if not os.path.isfile(DISM_LOG):
                return {"ok": False, "error": f"dism.log was not found at {DISM_LOG}. DISM may not have run on this PC yet."}
            subprocess.Popen(["explorer.exe", f"/select,{DISM_LOG}"])
            return {"ok": True, "path": DISM_LOG}
        if tool == "trim":
            subprocess.Popen([os.path.join(SYSTEM_ROOT, "System32", "dfrgui.exe")])
            return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": f"Windows could not open it: {e}"}
    return {"ok": False, "error": "Unknown tool."}
