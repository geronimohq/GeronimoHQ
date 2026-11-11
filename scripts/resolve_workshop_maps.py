"""Finds the Steam Workshop page and the creators of every map that is being played right now, exactly as Steam shows them, so the website
never says "Mapper not listed" for a map that is on the workshop and never shows a creator name that Steam no longer shows.

Input : public/data/live_servers.json (the maps on every server), src/data/zeMapCatalog.json (known maps with their workshop ids).
Output: public/data/map_workshop.json
          { "maps": { "<map>": { "id": "<workshop id>", "mapper": "<creators as Steam lists them>", "src": "page", "t": <epoch> } } }

How a map is found: the workshop id of the s2ze catalog when the map is in it; otherwise the Steam Workshop search (the result whose title
is exactly the map name; failing that, whose title is the same name apart from a suffix such as _cs2, _p or _v2; when several items
qualify, the most subscribed one). The creators are read from that item's own workshop page ("Created by"), because the catalog's names
go stale when a mapper renames their Steam profile and the public API only gives one of several co-creators. Entries are checked again
after a few days so renamed profiles are picked up.

Best effort, like refresh_map_mappers.py: any network or parsing problem is reported and the script still exits 0, so a deploy
never fails because of it. Maps that could not be found are remembered for a day so every run does not ask Steam again.
Run by hand with --dry-run to see what it would write, --max N to change how many lookups one run may do.
"""
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = os.path.join(ROOT, "public", "data", "live_servers.json")
CATALOG = os.path.join(ROOT, "src", "data", "zeMapCatalog.json")
OUT = os.path.join(ROOT, "public", "data", "map_workshop.json")
UA = "GeronimoHQ-workshop-resolver/1.1 (+https://geronimohq.com)"
SEARCH = "https://steamcommunity.com/workshop/browse/?appid=730&searchtext={q}&browsesort=textsearch&section=readytouseitems"
DETAILS = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
ITEM_PAGE = "https://steamcommunity.com/sharedfiles/filedetails/?id={id}"
DEFAULT_MAX_LOOKUPS = 45
RETRY_MISSING_AFTER = 24 * 3600
REFRESH_AFTER = 3 * 24 * 3600
MAX_CREATORS = 6
MAP_NAME_RE = re.compile(r"^[a-z0-9_]{3,64}$")
ITEM_RE = re.compile(r'filedetails/\?id=(\d+)"[^>]*><img[^>]*?alt="([^"]*)"', re.I)
CREATORS_BLOCK_RE = re.compile(r'class="creatorsBlock">(.*?)(?:class="parentCollectionsNumOthers"|class="stats_table"|<div id="profileBlock")', re.S)
CREATOR_NAME_RE = re.compile(r'class="friendBlockContent">\s*(.*?)\s*<br', re.S)
SUFFIX_RE = re.compile(r"(?:_cs2|_p|_v\d+[a-z0-9_]*|_final|_beta\d*|_rc\d+|_fix\d*|_remake|_new)$")
INVISIBLE = dict.fromkeys(map(ord, "​‌‍⁠﻿"), None)     # some authors pad titles with zero-width characters


def clean_title(t):
    return html.unescape(t or "").translate(INVISIBLE).strip().lower()


def base_title(t):
    """A title without version-like suffixes: 'ze_surf_saltfish_cs2' -> 'ze_surf_saltfish'."""
    t = clean_title(t)
    for _ in range(3):
        n = SUFFIX_RE.sub("", t)
        if n == t:
            break
        t = n
    return t


def map_key(raw):
    """'workshop/123/ZM_Foo' -> 'zm_foo'; None when it does not look like a map name."""
    k = (raw or "").replace("\\", "/").split("/")[-1].strip().lower()
    return k if MAP_NAME_RE.match(k) else None


def current_maps(live):
    out = []
    for s in (live.get("servers") or {}).values():
        k = map_key((s or {}).get("map"))
        if k and k not in out:
            out.append(k)
    return out


def parse_search(page_html, name):
    """-> ids of the search results that are this map: exact title matches first, then titles that differ only by a suffix."""
    want, want_base = clean_title(name), base_title(name)
    exact, loose = [], []
    for wid, title in ITEM_RE.findall(page_html or ""):
        t = clean_title(title)
        if t == want:
            if wid not in exact:
                exact.append(wid)
        elif base_title(t) == want_base and wid not in loose:
            loose.append(wid)
    return exact + [w for w in loose if w not in exact]


def parse_creators(page_html):
    """-> the creator names of a workshop item page, in the order Steam lists them ([] when the page has no creators block)."""
    block = CREATORS_BLOCK_RE.search(page_html or "")
    if not block:
        return []
    names = []
    for raw in CREATOR_NAME_RE.findall(block.group(1)):
        n = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]*>", "", raw))).strip()
        if n and n not in names:
            names.append(n[:60])
    return names[:MAX_CREATORS]


def pick_best(details_json):
    """-> id of the most subscribed visible item among the details, or None."""
    best = None
    for d in ((details_json or {}).get("response") or {}).get("publishedfiledetails") or []:
        if d.get("result") != 1 or str(d.get("banned", 0)) not in ("0", ""):
            continue
        subs = int(d.get("subscriptions") or 0)
        if best is None or subs > best[0]:
            best = (subs, str(d.get("publishedfileid")))
    return best[1] if best else None


def get(url, data=None, timeout=15, retries=2):
    """One request; when Steam answers 429/503 (too many requests) it waits as long as Steam asks (at most 30 s) and tries again."""
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < retries:
                try:
                    wait = int(e.headers.get("Retry-After") or 15)
                except ValueError:
                    wait = 15
                time.sleep(max(5, min(wait, 30)))
                continue
            raise


def details_for(ids):
    body = urllib.parse.urlencode([("itemcount", len(ids))] + [(f"publishedfileids[{i}]", w) for i, w in enumerate(ids)]).encode()
    return json.loads(get(DETAILS, body))


def lookup(name, catalog, fetch=get, details=details_for, pause=1.5, known_id="", old_mapper=""):
    """-> {"id", "mapper", "src"} for one map, or None. Network goes through the `fetch`/`details` arguments so tests can fake Steam.
    `known_id` is an id found on an earlier run: only the creators are read again."""
    entry = catalog.get(name) if isinstance(catalog.get(name), dict) else None
    wid = known_id or (str(entry["addon"]) if entry and entry.get("addon") else "")
    if not wid:
        ids = parse_search(fetch(SEARCH.format(q=urllib.parse.quote(name))), name)[:5]
        if not ids:
            return None
        if len(ids) > 1:
            time.sleep(pause)
            wid = pick_best(details(ids)) or ids[0]
        else:
            wid = ids[0]
    names = []
    try:
        time.sleep(pause)
        names = parse_creators(fetch(ITEM_PAGE.format(id=wid)))
    except Exception:
        names = []
    if names:
        return {"id": wid, "mapper": ", ".join(names), "src": "page"}
    # The page could not be read this time: keep the id (the link still works) and the best older name we have; it is tried again next run
    return {"id": wid, "mapper": old_mapper or (entry.get("mapper", "") if entry else ""), "src": "catalog" if entry else "none"}


def needs_lookup(name, known, now):
    k = known.get(name)
    if not k:
        return True
    age = now - int(k.get("t", 0))
    if not k.get("id"):
        return age >= RETRY_MISSING_AFTER                      # not found earlier: try again after a day
    return k.get("src") != "page" or age >= REFRESH_AFTER      # found, but not read from the page yet, or a few days old


def main(argv):
    dry = "--dry-run" in argv
    limit = int(argv[argv.index("--max") + 1]) if "--max" in argv else DEFAULT_MAX_LOOKUPS
    try:
        with open(LIVE, encoding="utf-8") as f:
            maps = current_maps(json.load(f))
    except Exception as e:
        print(f"[workshop] cannot read live_servers.json ({e}); nothing changed")
        return 0
    try:
        with open(CATALOG, encoding="utf-8") as f:
            catalog = json.load(f)
    except Exception:
        catalog = {}
    try:
        with open(OUT, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
    known = data.get("maps") if isinstance(data.get("maps"), dict) else {}
    now = int(time.time())
    todo = [m for m in maps if needs_lookup(m, known, now)]
    todo.sort(key=lambda m: (m in known, int((known.get(m) or {}).get("t", 0))))      # new maps first, then the oldest entries
    print(f"[workshop] {len(maps)} map(s) in play, {len(todo)} to look up")
    changed = 0
    for name in todo[:limit]:
        try:
            old = known.get(name) or {}
            r = lookup(name, catalog, known_id=old.get("id", ""), old_mapper=old.get("mapper", ""))
        except Exception as e:
            print(f"[workshop] {name}: lookup failed ({e})")
            continue
        known[name] = {"id": r["id"], "mapper": r["mapper"], "src": r["src"], "t": now} if r else {"id": "", "mapper": "", "src": "none", "t": now}
        changed += 1
        print(f"[workshop] {name}: " + (f"{r['id']} by {r['mapper'] or '?'} ({r['src']})" if r else "not found"))
        time.sleep(1.5)
    keep = set(maps)                       # only what is in play now (or was resolved earlier this week) stays, so the file does not grow forever
    known = {k: v for k, v in known.items() if k in keep or now - int(v.get("t", 0)) < 7 * 86400}
    if not changed:
        print("[workshop] nothing to write")
        return 0
    if dry:
        print(f"[workshop] dry run: would write {changed} entr(y/ies)")
        return 0
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"updated": now, "maps": known}, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:                  # never fail a deploy over this
        print(f"[workshop] unexpected problem ({e}); nothing changed")
        sys.exit(0)
