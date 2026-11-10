"""Adds mapper names for NEW Zombie Escape maps to src/data/zeMapCatalog.json + zeMapMappers.json.

Source: the public s2ze.com pages (map page title = "<map> | CS2 Zombie Escape Map - <mapper>", the name of the
Steam Workshop author). New maps are discovered from the s2ze.com home page ("new and popular" list). Only maps
that are not in the catalog yet are fetched (a few requests per run, 1 s apart), existing entries are never changed.

Best effort: any network or parsing problem is reported and the script still exits 0, so a deploy never fails
because of it. Run by hand with --dry-run to see what it would add.
"""
import html
import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "src", "data", "zeMapCatalog.json")
MAPPERS = os.path.join(ROOT, "src", "data", "zeMapMappers.json")
HOME = "https://s2ze.com/"
UA = "GeronimoHQ-mapper-refresh/1.0 (+https://geronimohq.com)"
MAX_NEW_PER_RUN = 30

TITLE_RE = re.compile(r"<title>\s*([^|<]+?)\s*\|\s*CS2 Zombie Escape Map\s*-\s*([^<]+?)\s*</title>", re.I)
OG_IMAGE_RE = re.compile(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', re.I)
MAP_ID_RE = re.compile(r"/maps/(\d{6,})")
MAP_NAME_RE = re.compile(r"^[a-z0-9_]{3,64}$")


def parse_map_page(page_html):
    """-> (map_name, mapper, image) or None if the page is not a map page we understand."""
    m = TITLE_RE.search(page_html or "")
    if not m:
        return None
    name = html.unescape(m.group(1)).strip().lower()
    mapper = html.unescape(m.group(2)).strip()
    if not MAP_NAME_RE.match(name) or not mapper or len(mapper) > 80 or any(c in mapper for c in "<>\n\r"):
        return None
    img = OG_IMAGE_RE.search(page_html)
    return name, mapper, html.unescape(img.group(1)) if img else ""


def home_page_ids(home_html):
    seen = []
    for i in MAP_ID_RE.findall(home_html or ""):
        if i not in seen:
            seen.append(i)
    return seen


def add_new(catalog, found):
    """found: iterable of (map_name, mapper, image, addon_id). Adds only unknown map names. Returns added names."""
    added = []
    for name, mapper, image, addon in found:
        if name in catalog:
            continue
        catalog[name] = {"mapper": mapper, "image": image, "addon": addon}
        added.append(name)
    return added


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def main(argv):
    dry = "--dry-run" in argv
    try:
        with open(CATALOG, encoding="utf-8") as f:
            catalog = json.load(f)
    except Exception as e:
        print(f"[mappers] cannot read catalog: {e}")
        return 0
    known_ids = {str(v.get("addon")) for v in catalog.values() if isinstance(v, dict)}
    try:
        ids = [i for i in home_page_ids(fetch(HOME)) if i not in known_ids]
    except Exception as e:
        print(f"[mappers] s2ze.com home page not reachable ({e}); nothing changed")
        return 0
    print(f"[mappers] {len(ids)} map(s) on the home page that are not in the catalog")
    found = []
    for i in ids[:MAX_NEW_PER_RUN]:
        try:
            parsed = parse_map_page(fetch(f"https://s2ze.com/maps/{i}"))
        except Exception as e:
            print(f"[mappers] {i}: fetch failed ({e})")
            parsed = None
        if parsed:
            found.append((parsed[0], parsed[1], parsed[2], i))
            print(f"[mappers] {i}: {parsed[0]} -> {parsed[1]}")
        time.sleep(1.0)
    added = add_new(catalog, found)
    if not added:
        print("[mappers] nothing to add")
        return 0
    if dry:
        print(f"[mappers] dry run: would add {len(added)}")
        return 0
    with open(CATALOG, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(catalog, ensure_ascii=False, indent=2))
    slim = {k: v["mapper"] for k, v in catalog.items()}
    with open(MAPPERS, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(slim, ensure_ascii=False, separators=(",", ":")))
    print(f"[mappers] added {len(added)}: {', '.join(added)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
