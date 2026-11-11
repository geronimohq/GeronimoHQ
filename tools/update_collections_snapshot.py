"""Refreshes desktop-app/server_collections_snapshot.json: the child ids of every collection in server_collections.json, plus the titles of
the asset items (so the Map Cleaner can name them offline). Public Steam API, no key. Run it before a release when collections changed:

    python tools/update_collections_snapshot.py
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "desktop-app"))
import workshop_collections as app_collections  # noqa: E402

API = "https://api.steampowered.com/ISteamRemoteStorage/"


def post(endpoint, data):
    req = urllib.request.Request(API + endpoint, data=urllib.parse.urlencode(data).encode(), headers={"User-Agent": "CS2CommandCenter/2"})
    return json.load(urllib.request.urlopen(req, timeout=40))["response"]


def main():
    cfg = app_collections.validate(json.load(open(os.path.join(ROOT, "desktop-app", "server_collections.json"), encoding="utf-8")))
    children, titles = {}, {}
    for e in app_collections.all_entries(cfg):
        det = post("GetCollectionDetails/v1/", {"collectioncount": 1, "publishedfileids[0]": e["id"]})["collectiondetails"][0]
        ids = [str(c["publishedfileid"]) for c in det.get("children", [])]
        children[e["id"]] = ids
        print(f'{e["id"]} {e["label"]}: {len(ids)} items')
        if e["kind"] == "assets":
            for i in range(0, len(ids), 100):
                chunk = ids[i:i + 100]
                data = {"itemcount": len(chunk)}
                data.update({f"publishedfileids[{j}]": v for j, v in enumerate(chunk)})
                for d in post("GetPublishedFileDetails/v1/", data)["publishedfiledetails"]:
                    if d.get("result") == 1 and d.get("title"):
                        titles[str(d["publishedfileid"])] = d["title"]
    out = {"fetched": int(time.time()), "children": children, "titles": titles}
    path = os.path.join(ROOT, "desktop-app", "server_collections_snapshot.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
    print("wrote", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
