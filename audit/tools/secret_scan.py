"""Masked regex secret scanner for GeronimoHQ audit.

Scans: (1) full git history (all commits, all branches), (2) tracked working tree,
(3) built website dist/, (4) exe strings (ASCII + UTF-16LE).
Never prints secret values: every hit is masked to first 4 chars + length.
Usage: python audit/tools/secret_scan.py
"""
import os
import re
import subprocess
import sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

PATTERNS = {
    "discord_webhook": r"https://(?:ptb\.|canary\.)?discord(?:app)?\.com/api/webhooks/\d+/[\w-]{20,}",
    "discord_bot_token": r"[MN][A-Za-z\d]{23,25}\.[\w-]{6}\.[\w-]{27,}",
    "github_token": r"gh[pousr]_[A-Za-z0-9]{36,}",
    "aws_key": r"AKIA[0-9A-Z]{16}",
    "google_api_key": r"AIza[0-9A-Za-z_\-]{35}",
    "slack_token": r"xox[baprs]-[0-9A-Za-z-]{10,}",
    "private_key_block": r"-----BEGIN (?:RSA |EC |OPENSSH |ED25519 )?PRIVATE KEY-----",
    "steam_web_api_key": r"(?i)steam[_-]?(?:web)?[_-]?api[_-]?key\s*[=:]\s*['\"]?[0-9A-F]{32}",
    "generic_secret_assign": r"(?i)(?:secret|password|passwd|api[_-]?key|token)\s*[=:]\s*['\"][^'\"\s]{12,}['\"]",
    "presence_secret_value": r"(?i)presence_secret['\"]?\s*[:=]\s*['\"][^'\"]{6,}['\"]",
    "user_path": r"[A-Za-z]:\\\\?Users\\\\?[A-Za-z0-9_.\- ]+",
    "private_ip": r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b",
    "steam_id64": r"\b7656119\d{10}\b",
}
PUBLIC_OWNER_STEAMID = "76561198143793864"  # public profile link, allowed
COMPILED = {k: re.compile(v) for k, v in PATTERNS.items()}


def mask(v: str) -> str:
    v = v.strip()
    if len(v) <= 6:
        return "*" * len(v)
    return f"{v[:4]}…(len={len(v)})"


def scan_text(text: str, where: str, hits):
    for name, rx in COMPILED.items():
        for m in rx.finditer(text):
            val = m.group(0)
            if name == "steam_id64" and val == PUBLIC_OWNER_STEAMID:
                continue
            if name == "user_path":
                # keep only the folder name masked, not the whole path
                val = re.sub(r"(Users\\\\?)([^\\\s]+)", lambda mm: mm.group(1) + mask(mm.group(2)), val)
                hits[name].add((where, val))
                continue
            hits[name].add((where, mask(val)))


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="ignore").stdout


def scan_history(hits):
    log = git("log", "--all", "-p", "--no-color", "--format=COMMIT %h")
    commit = "?"
    for line in log.splitlines():
        if line.startswith("COMMIT "):
            commit = line[7:]
            continue
        if line.startswith("+") and not line.startswith("+++"):
            scan_text(line, f"history:{commit}", hits)


def scan_tree(hits):
    for rel in git("ls-files").splitlines():
        p = os.path.join(ROOT, rel)
        if not os.path.isfile(p) or os.path.getsize(p) > 5_000_000:
            continue
        with open(p, "rb") as f:
            data = f.read()
        if b"\x00" in data[:4096]:
            continue
        scan_text(data.decode("utf-8", "ignore"), f"tree:{rel}", hits)


def scan_dist(hits):
    d = os.path.join(ROOT, "dist")
    for base, _, files in os.walk(d):
        for fn in files:
            if fn.endswith((".js", ".html", ".css", ".json", ".map", ".txt")):
                p = os.path.join(base, fn)
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    scan_text(f.read(), "dist:" + os.path.relpath(p, ROOT), hits)


def exe_strings(path):
    with open(path, "rb") as f:
        data = f.read()
    for m in re.finditer(rb"[\x20-\x7e]{6,}", data):
        yield m.group(0).decode("ascii")
    for m in re.finditer(rb"(?:[\x20-\x7e]\x00){6,}", data):
        yield m.group(0).decode("utf-16le", "ignore")


def scan_exe(hits):
    p = os.path.join(ROOT, "public", "CS2_Command_Center.exe")
    if os.path.exists(p):
        # PyInstaller compresses .pyc payloads (zlib), so plain strings only cover the
        # bootloader + uncompressed parts; we also decompress zlib streams best-effort.
        for s in exe_strings(p):
            scan_text(s, "exe:strings", hits)
        import zlib
        with open(p, "rb") as f:
            data = f.read()
        n = 0
        for m in re.finditer(rb"\x78\x9c|\x78\xda", data):
            try:
                chunk = zlib.decompressobj().decompress(data[m.start():m.start() + 4_000_000])
            except Exception:
                continue
            if len(chunk) < 64:
                continue
            n += 1
            txt = " ".join(x.decode("ascii") for x in re.findall(rb"[\x20-\x7e]{6,}", chunk))
            scan_text(txt, "exe:zlib", hits)
        print(f"[info] exe: decompressed {n} zlib streams")


def main():
    hits = defaultdict(set)
    for fn in (scan_history, scan_tree, scan_dist, scan_exe):
        fn(hits)
    total = 0
    for name in PATTERNS:
        items = sorted(hits.get(name, []))
        if not items:
            print(f"[{name}] 0 hits")
            continue
        locs = defaultdict(set)
        for where, val in items:
            locs[val].add(where.split(":")[0] + ":" + where.split(":", 1)[1][:60])
        print(f"[{name}] {len(locs)} distinct value(s)")
        for val, w in list(locs.items())[:12]:
            total += 1
            print(f"    {val}  <- {sorted(w)[:4]}{' …' if len(w) > 4 else ''}")
    print(f"TOTAL distinct flagged values: {total}")


if __name__ == "__main__":
    sys.exit(main())
