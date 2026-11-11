"""Finds the Steam Workshop page and the creator of every map that is being played right now, so the website never has to say
"Mapper not listed" for a map that is clearly on the workshop.

Input : public/data/live_servers.json (the maps on every server), src/data/zeMapCatalog.json (known maps with their workshop ids).
Output: public/data/map_workshop.json  { "maps": { "<map>": { "id": "<workshop id>", "mapper": "<creator name>", "t": <epoch> } },
                                          "creators": { "<steamid64>": "<name>" } }

How a map is found: the workshop id of the s2ze catalog when the map is in it; otherwise the Steam Workshop search for the exact
map name (the result whose title is exactly that name; when several maps share the name, the most subscribed one). The creator is
the public creator of that item (GetPublishedFileDetails needs no API key) and the creator's public profile name.

Best effort, like refresh_map_mappers.py: any network or parsing problem is reported and the script still exits 0, so a deploy
never fails because of it. Maps that could not be found are remembered for a day so every run does not ask Steam again.
Run by hand with --dry-run to see what it would write, --max N to change how many new maps one run may look up.
"""
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = os.path.join(ROOT, "public", "data", "live_servers.json")
CATALOG = os.path.join(ROOT, "src", "data", "zeMapCatalog.json")
OUT = os.path.join(ROOT, "public", "data", "map_workshop.json")
UA = "GeronimoHQ-workshop-resolver/1.0 (+https://geronimohq.com)"
SEARCH = "https://steamcommunity.com/workshop/browse/?appid=730&searchtext={q}&browsesort=textsearch&section=readytouseitems"
DETAILS = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
PROFILE = "https://steamcommunity.com/profiles/{sid}/?xml=1"
DEFAULT_MAX_NEW = 25
RETRY_MISSING_AFTER = 24 * 3600
MAP_NAME_RE = re.compile(r"^[a-z0-9_]{3,64}$")
ITEM_RE = re.compile(r'filedetails/\?id=(\d+)"[^>]*><img[^>]*?alt="([^"]*)"', re.I)
NAME_RE = re.compile(r"<steamID><!\[CDATA\[(.*?)\]\]></steamID>", re.S)
INVISIBLE = dict.fromkeys(map(ord, "​‌‍⁠﻿"), None)     # some authors pad titles with zero-width characters


def clean_title(t):
    return html.unescape(t or "").translate(INVISIBLE).strip().lower()


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
    """-> ids of the search results whose title is exactly `name` (in the order Steam lists them)."""
    want = clean_title(name)
    ids = []
    for wid, title in ITEM_RE.findall(page_html or ""):
        if clean_title(title) == want and wid not in ids:
            ids.append(wid)
    return ids


def parse_profile_name(xml_text):
    m = NAME_RE.search(xml_text or "")
    name = html.unescape(m.group(1)).strip() if m else ""
    return name if name and len(name) <= 80 and not any(c in name for c in "<>\n\r") else ""


def pick_best(details_json):
    """-> (id, creator steamid64) of the most subscribed visible item among the details, or None."""
    best = None
    for d in ((details_json or {}).get("response") or {}).get("publishedfiledetails") or []:
        if d.get("result") != 1 or str(d.get("banned", 0)) not in ("0", ""):
            continue
        subs = int(d.get("subscriptions") or 0)
        if best is None or subs > best[0]:
            best = (subs, str(d.get("publishedfileid")), str(d.get("creator") or ""))
    return (best[1], best[2]) if best else None


def get(url, data=None, timeout=15):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def details_for(ids):
    body = urllib.parse.urlencode([("itemcount", len(ids))] + [(f"publishedfileids[{i}]", w) for i, w in enumerate(ids)]).encode()
    return json.loads(get(DETAILS, body))


def lookup(name, catalog, creators, fetch=get, details=details_for, pause=1.0):
    """-> {"id", "mapper"} for one map, or None. Network goes through the `fetch`/`details` arguments so tests can fake Steam."""
    entry = catalog.get(name) if isinstance(catalog.get(name), dict) else None
    if entry and entry.get("addon"):
        return {"id": str(entry["addon"]), "mapper": entry.get("mapper") or ""}
    ids = parse_search(fetch(SEARCH.format(q=urllib.parse.quote(name))), name)[:5]
    if not ids:
        return None
    time.sleep(pause)
    best = pick_best(details(ids))
    if not best:
        return None
    wid, creator = best
    mapper = creators.get(creator, "")
    if creator and not mapper:
        time.sleep(pause)
        mapper = parse_profile_name(fetch(PROFILE.format(sid=creator)))
        if mapper:
            creators[creator] = mapper
    return {"id": wid, "mapper": mapper}


def main(argv):
    dry = "--dry-run" in argv
    limit = int(argv[argv.index("--max") + 1]) if "--max" in argv else DEFAULT_MAX_NEW
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
    creators = data.get("creators") if isinstance(data.get("creators"), dict) else {}
    now = int(time.time())
    todo = [m for m in maps if not (m in known and (known[m].get("id") or now - int(known[m].get("t", 0)) < RETRY_MISSING_AFTER))]
    print(f"[workshop] {len(maps)} map(s) in play, {len(todo)} to look up")
    changed = 0
    for name in todo[:limit]:
        try:
            r = lookup(name, catalog, creators)
        except Exception as e:
            print(f"[workshop] {name}: lookup failed ({e})")
            continue
        known[name] = {"id": r["id"], "mapper": r["mapper"], "t": now} if r else {"id": "", "mapper": "", "t": now}
        changed += 1
        print(f"[workshop] {name}: " + (f"{r['id']} by {r['mapper'] or '?'}" if r else "not found"))
        time.sleep(1.0)
    keep = set(maps)                       # only what is in play now (or was resolved earlier this week) stays, so the file does not grow forever
    known = {k: v for k, v in known.items() if k in keep or now - int(v.get("t", 0)) < 7 * 86400}
    if not changed:
        print("[workshop] nothing to write")
        return 0
    if dry:
        print(f"[workshop] dry run: would write {changed} entr(y/ies)")
        return 0
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"updated": now, "maps": known, "creators": creators}, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:                  # never fail a deploy over this
        print(f"[workshop] unexpected problem ({e}); nothing changed")
        sys.exit(0)
