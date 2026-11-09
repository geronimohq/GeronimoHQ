"""Regenerate src/data/zeMapMappers.json ({map: mapper}) from src/data/zeMapCatalog.json.
The website only needs mapper names; the full catalog (image URLs, addon ids) stays as source data."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "src", "data", "zeMapCatalog.json")
dst = os.path.join(ROOT, "src", "data", "zeMapMappers.json")
with open(src, encoding="utf-8") as f:
    full = json.load(f)
slim = {k: v["mapper"] for k, v in full.items()}
with open(dst, "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(slim, ensure_ascii=False, separators=(",", ":")))
print(f"{len(slim)} maps -> {dst}")
