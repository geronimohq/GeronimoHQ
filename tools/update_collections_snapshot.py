"""Refreshes desktop-app/server_collections_snapshot.json. Public sources only, no keys:

- the child ids of every Steam collection in server_collections.json (GetCollectionDetails),
- item titles (GetPublishedFileDetails; hidden items have none),
- name_ids: for each server, map name -> the workshop id THAT server uses (from its own collections' titles, and for RSS from the map list
  on its website, which publishes name and workshop id for every map),
- community_ids: workshop ids per Map Cleaner protection group that has a list but no Steam collection (RSS).

Why name_ids matters: several different workshop items can carry the same map name (RSS and GFL both run a ze_surf_facility_p, but they are
different items). A map is only "installed" for a server when the id that server uses is installed.

    python tools/update_collections_snapshot.py
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "desktop-app"))
import workshop_collections as app_collections  # noqa: E402

API = "https://api.steampowered.com/ISteamRemoteStorage/"
RSS_MAP_PAGE = "https://rsscs2.kr/ze/"


def post(endpoint, data):
    req = urllib.request.Request(API + endpoint, data=urllib.parse.urlencode(data).encode(), headers={"User-Agent": "CS2CommandCenter/2"})
    return json.load(urllib.request.urlopen(req, timeout=40))["response"]


def titles_for(ids):
    out = {}
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        data = {"itemcount": len(chunk)}
        data.update({f"publishedfileids[{j}]": v for j, v in enumerate(chunk)})
        for d in post("GetPublishedFileDetails/v1/", data)["publishedfiledetails"]:
            if d.get("result") == 1 and d.get("title"):
                out[str(d["publishedfileid"])] = d["title"]
    return out


def rss_list():
    """name -> workshop id from the map list RSS publishes on its website (embedded as JSON in the page)."""
    req = urllib.request.Request(RSS_MAP_PAGE, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "ignore")
    data = json.loads(re.search(r'<script[^>]*id="maps-data"[^>]*>(.*?)</script>', html, re.S).group(1))
    out = {}
    for m in data["maps"]:
        if re.fullmatch(r"\d{6,12}", str(m.get("w", ""))) and m.get("n"):
            out.setdefault(str(m["n"]).lower(), str(m["w"]))
    return out


def main():
    cfg = app_collections.validate(json.load(open(os.path.join(ROOT, "desktop-app", "server_collections.json"), encoding="utf-8")))
    children, titles = {}, {}
    for e in app_collections.all_entries(cfg):
        if e["kind"] == "item":                  # a single asset pack: no children to list
            continue
        det = post("GetCollectionDetails/v1/", {"collectioncount": 1, "publishedfileids[0]": e["id"]})["collectiondetails"][0]
        ids = [str(c["publishedfileid"]) for c in det.get("children", [])]
        children[e["id"]] = ids
        titles.update(titles_for([i for i in ids if i not in titles]))
        print(f'{e["id"]} {e["label"]}: {len(ids)} items')
    name_ids = {}
    for sid, entries in cfg["servers"].items():
        names = {}
        for e in entries:
            if e["kind"] in ("maps", "default"):
                for i in children.get(e["id"], []):
                    if i in titles:
                        names.setdefault(titles[i].strip().lower(), i)
        if names:
            name_ids[sid] = names
    rss = rss_list()
    name_ids["rss"] = rss
    community_ids = {"rss": sorted(set(rss.values()))}
    print(f"RSS website list: {len(rss)} names, {len(community_ids['rss'])} ids")
    out = {"fetched": int(time.time()), "children": children, "titles": titles, "name_ids": name_ids, "community_ids": community_ids}
    path = os.path.join(ROOT, "desktop-app", "server_collections_snapshot.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
    print("wrote", path, os.path.getsize(path), "bytes;", {k: len(v) for k, v in name_ids.items()})


if __name__ == "__main__":
    main()
