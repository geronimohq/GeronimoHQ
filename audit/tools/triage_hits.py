"""Triage helper: show masked context for exe/history hits (values never printed)."""
import re, subprocess, zlib, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
data = open(os.path.join(ROOT, "public", "CS2_Command_Center.exe"), "rb").read()
pats = {"aws": rb"AKIA[0-9A-Z]{16}", "users": rb"C:\\\\?Users\\\\?Gala[A-Za-z0-9]*",
        "tok": rb"(?i)token\s*[=:]\s*['\"][^'\"\s]{12,}['\"]", "pw": rb"(?i)pass(?:word|wd)?\s*[=:]\s*['\"][^'\"\s]{12,}['\"]"}
seen = set()
for m in re.finditer(rb"\x78\x9c|\x78\xda", data):
    try:
        chunk = zlib.decompressobj().decompress(data[m.start():m.start() + 4_000_000])
    except Exception:
        continue
    for k, p in pats.items():
        for h in re.finditer(p, chunk):
            ctx = chunk[max(0, h.start() - 90):h.start()] + b"<<MASKED>>" + chunk[h.end():h.end() + 40]
            ctx = re.sub(rb"[^\x20-\x7e]", b".", ctx).decode()
            key = (k, ctx[:60])
            if key in seen:
                continue
            seen.add(key)
            print(f"[{k}] ...{ctx}...")
log = subprocess.run(["git", "show", "f3f2fa0", "--stat", "--format=%h %ad %s"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="ignore").stdout
print("--- history commit f3f2fa0:\n" + log[:600])
diff = subprocess.run(["git", "show", "f3f2fa0"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="ignore").stdout
for line in diff.splitlines():
    if re.search(r"\b7656119\d{10}\b", line) and "76561198143793864" not in line:
        print("   ", re.sub(r"7656119\d{10}", "7656…MASKED", line.strip())[:200])
