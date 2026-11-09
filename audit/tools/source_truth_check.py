"""Checks whether distinctive string constants from desktop-app/*.py appear in the exe's
compressed PyInstaller payload (best-effort source-of-truth check; not a byte-level proof)."""
import ast, os, re, zlib, random
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
exe = open(os.path.join(ROOT, "public", "CS2_Command_Center.exe"), "rb").read()
blob = bytearray()
for m in re.finditer(rb"\x78\x9c|\x78\xda", exe):
    try:
        blob += zlib.decompressobj().decompress(exe[m.start():m.start() + 6_000_000])
    except Exception:
        pass
blob = bytes(blob)
random.seed(7)
for mod in ["app.py", "core_logic.py", "server_browser.py", "updater.py", "version.py", "theme.py", "custom_map_cleaner.py"]:
    src = open(os.path.join(ROOT, "desktop-app", mod), encoding="utf-8").read()
    consts = sorted({n.value for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Constant)
                     and isinstance(n.value, str) and 25 <= len(n.value) <= 120 and n.value.isascii()})
    sample = random.sample(consts, min(40, len(consts)))
    found = sum(1 for s in sample if s.encode() in blob)
    print(f"{mod:24s} {found}/{len(sample)} sampled string constants present in exe")
v = open(os.path.join(ROOT, "desktop-app", "version.py"), encoding="utf-8").read()
print("version.py:", re.findall(r"=\s*['\"]([^'\"]+)", v))
