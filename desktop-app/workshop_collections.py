"""Steam workshop collections of the Zombie Escape servers.

What it gives the app: for each server, which collections to point users to (its map list, default map, asset packs), how many of a
collection's items are already installed, and a rough download size, so a user is never sent to "subscribe to everything" blind.
It also gives the Map Cleaner exact membership (by workshop id) instead of hand-written lists.

Data sources, in this order: the live cache (refreshed at most once a day from Steam's public GetCollectionDetails, no key needed),
then the snapshot shipped inside the app. The list of collections itself comes from server_collections.json (bundled), optionally
replaced by a validated copy from geronimohq.com so a wrong link can be fixed without a new release. Only numeric ids are ever used.
"""
import json
import os
import re
import sys
import threading
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Set

HERE = os.path.dirname(os.path.abspath(__file__))
REMOTE_URL = "https://geronimohq.com/data/server_collections.json"
API = "https://api.steampowered.com/ISteamRemoteStorage/"
MAX_AGE = 24 * 3600
KINDS = ("maps", "assets", "default", "item")         # item = one workshop item (a server asset pack), not a collection
ASSET_KINDS = ("assets", "item")
_LOCK = threading.Lock()


def _resource(name: str) -> str:
    return os.path.join(getattr(sys, "_MEIPASS", HERE), name)


def _local_dir() -> str:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or HERE
    path = os.path.join(base, "CS2CommandCenter")
    os.makedirs(path, exist_ok=True)
    return path


def _read_json(path: str) -> Optional[Dict[str, Any]]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else None
    except (OSError, ValueError):
        return None


def _entry(raw: Any) -> Optional[Dict[str, str]]:
    if not isinstance(raw, dict) or not re.fullmatch(r"\d{6,12}", str(raw.get("id", ""))):
        return None
    kind = str(raw.get("kind", "maps"))
    if kind not in KINDS:
        return None
    out = {"id": str(raw["id"]), "label": str(raw.get("label", ""))[:80] or "Collection", "kind": kind,
           "community": re.sub(r"[^a-z_]", "", str(raw.get("community", "")).lower())[:24]}
    prefix = re.sub(r"[^a-z_]", "", str(raw.get("prefix", "")).lower())[:8]
    if prefix:
        out["prefix"] = prefix
    return out


def validate(cfg: Any) -> Optional[Dict[str, Any]]:
    """A cleaned copy of a collections file, or None when it is unusable. Anything that is not a plain numeric id is dropped."""
    if not isinstance(cfg, dict) or not isinstance(cfg.get("servers"), dict):
        return None
    servers: Dict[str, List[Dict[str, str]]] = {}
    for sid, items in cfg["servers"].items():
        sid = re.sub(r"[^a-z0-9_]", "", str(sid).lower())[:32]
        clean = [e for e in (_entry(x) for x in (items if isinstance(items, list) else [])) if e]
        if sid and clean:
            servers[sid] = clean
    shared = [e for e in (_entry(x) for x in (cfg.get("assets") if isinstance(cfg.get("assets"), list) else [])) if e]
    return {"servers": servers, "assets": shared} if servers else None


def load_config() -> Dict[str, Any]:
    """The collection list: the validated downloaded copy when there is one, else the one shipped with the app."""
    remote = validate(_read_json(os.path.join(_local_dir(), "server_collections.remote.json")))
    bundled = validate(_read_json(_resource("server_collections.json")))
    return remote or bundled or {"servers": {}, "assets": []}


def refresh_config(timeout: float = 6.0) -> bool:
    """Downloads the collection list from the website (only the numeric ids and labels are kept)."""
    try:
        req = urllib.request.Request(REMOTE_URL, headers={"User-Agent": "CS2CommandCenter/2"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read(200_000).decode("utf-8"))
        clean = validate(data)
        if not clean:
            return False
        with open(os.path.join(_local_dir(), "server_collections.remote.json"), "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        return True
    except Exception:
        return False


def all_entries(cfg: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
    cfg = cfg or load_config()
    seen, out = set(), []
    for items in list(cfg["servers"].values()) + [cfg.get("assets", [])]:
        for e in items:
            if e["id"] not in seen:
                seen.add(e["id"])
                out.append(e)
    return out


def entries_for(server_id: str, cfg: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
    """This server's own collections and asset packs. (The shared asset collection is not offered to users; it only protects its items in the Map Cleaner.)"""
    cfg = cfg or load_config()
    return list(cfg["servers"].get(server_id, []))


# ---------------------------------------------------------------- cache
def _cache_path() -> str:
    return os.path.join(_local_dir(), "collections_cache.json")


def _cache() -> Dict[str, Any]:
    c = _read_json(_cache_path()) or {}
    c.setdefault("children", {})
    c.setdefault("sizes", {})
    return c


def _save_cache(c: Dict[str, Any]) -> None:
    try:
        tmp = _cache_path() + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(c, fh)
        os.replace(tmp, _cache_path())
    except OSError:
        pass


def _snapshot() -> Dict[str, Any]:
    return _read_json(_resource("server_collections_snapshot.json")) or {"children": {}, "titles": {}}


def cached_children(cid: str) -> Optional[List[str]]:
    """Child ids from the live cache, else from the snapshot shipped with the app. Never touches the network."""
    with _LOCK:
        hit = _cache()["children"].get(cid)
    if hit and hit.get("ids"):
        return [str(x) for x in hit["ids"]]
    snap = _snapshot()["children"].get(cid)
    return [str(x) for x in snap] if snap else None


def fetch_children(cid: str, timeout: float = 8.0) -> Optional[List[str]]:
    if not re.fullmatch(r"\d{6,12}", cid):
        return None
    try:
        data = urllib.parse.urlencode({"collectioncount": 1, "publishedfileids[0]": cid}).encode()
        req = urllib.request.Request(API + "GetCollectionDetails/v1/", data=data, headers={"User-Agent": "CS2CommandCenter/2"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read(5_000_000).decode("utf-8"))
        det = body["response"]["collectiondetails"][0]
        ids = [str(c["publishedfileid"]) for c in det.get("children", []) if re.fullmatch(r"\d{6,12}", str(c.get("publishedfileid", "")))]
        if not ids:
            return None
        with _LOCK:
            c = _cache()
            c["children"][cid] = {"at": time.time(), "ids": ids}
            _save_cache(c)
        return ids
    except Exception:
        return None


def children(cid: str, timeout: float = 8.0) -> Optional[List[str]]:
    """Fresh when the live cache is younger than a day, otherwise tries Steam and falls back to whatever is known."""
    with _LOCK:
        hit = _cache()["children"].get(cid)
    if hit and hit.get("ids") and time.time() - float(hit.get("at", 0)) < MAX_AGE:
        return [str(x) for x in hit["ids"]]
    return fetch_children(cid, timeout) or cached_children(cid)


def refresh_all_async() -> None:
    """Background: refresh the list of collections and every collection older than a day. Safe to call at start-up."""
    def run():
        refresh_config()
        for e in all_entries():
            if e["kind"] == "item":
                continue
            with _LOCK:
                hit = _cache()["children"].get(e["id"])
            if not hit or time.time() - float(hit.get("at", 0)) >= MAX_AGE:
                fetch_children(e["id"], 10.0)
    threading.Thread(target=run, daemon=True, name="collections-refresh").start()


# ---------------------------------------------------------------- questions the app asks
def communities_of(wid: str) -> List[str]:
    """Map Cleaner protection groups whose map collection contains this workshop id (cache or snapshot only, never the network)."""
    out: List[str] = []
    for e in all_entries():
        if e["kind"] in ASSET_KINDS or not e["community"] or e["community"] in out:
            continue
        ids = cached_children(e["id"])
        if ids and wid in set(ids):
            out.append(e["community"])
    for comm, ids in (_snapshot().get("community_ids") or {}).items():      # groups with a published map list but no Steam collection (RSS)
        if comm not in out and wid in set(ids):
            out.append(comm)
    return out


def exact_map_id(server_id: str, map_name: str) -> str:
    """The workshop id THIS server uses for a map name ('' when unknown). Several different workshop items can carry the same map name, so a
    name that merely matches something installed is not proof that the server's own copy is installed."""
    names = (_snapshot().get("name_ids") or {}).get(server_id) or {}
    return str(names.get((map_name or "").strip().lower(), ""))


def asset_ids() -> Set[str]:
    """Every workshop id that belongs to a server asset collection (models, sounds, skins the servers need)."""
    found: Set[str] = set()
    for e in all_entries():
        if e["kind"] == "assets":
            found.update(cached_children(e["id"]) or [])
        elif e["kind"] == "item":
            found.add(e["id"])
    return found


def asset_title(wid: str) -> str:
    return str(_snapshot().get("titles", {}).get(wid, ""))


def _ids_of(entry_id: str) -> Optional[List[str]]:
    """The workshop ids behind an entry: the item itself for a single asset pack, else the collection's children."""
    if any(e["id"] == entry_id and e["kind"] == "item" for e in all_entries()):
        return [entry_id]
    return children(entry_id, 6.0)


def state(server_id: str, installed_ids: Set[str], map_prefix: str = "", mode: str = "") -> List[Dict[str, Any]]:
    """For the dialog: each collection or asset pack of this server with how many of its items are installed. Matching map prefix first.
    mode 'maps' = map lists only, 'assets' = asset packs only, '' = everything."""
    out = []
    for e in entries_for(server_id):
        is_asset = e["kind"] in ASSET_KINDS
        if (mode == "maps" and is_asset) or (mode == "assets" and not is_asset):
            continue
        ids = _ids_of(e["id"])
        row = dict(e)
        row["total"] = len(ids) if ids else 0
        row["installed"] = sum(1 for x in ids if x in installed_ids) if ids else 0
        row["known"] = bool(ids)
        row["match"] = bool(map_prefix and e.get("prefix") and map_prefix.startswith(e["prefix"]))
        out.append(row)
    out.sort(key=lambda r: (not r["match"], r["kind"] in ASSET_KINDS))
    return out


def size_of_missing(cid: str, installed_ids: Set[str], timeout: float = 15.0) -> Dict[str, Any]:
    """Rough download size of what is not installed yet, from the item details Steam shows publicly. Hidden items count as 'unknown'."""
    ids = [x for x in (_ids_of(cid) or []) if x not in installed_ids]
    with _LOCK:
        sizes = dict(_cache()["sizes"])
    todo = [x for x in ids if x not in sizes]
    try:
        for i in range(0, len(todo), 100):
            chunk = todo[i:i + 100]
            data = {"itemcount": len(chunk)}
            data.update({f"publishedfileids[{j}]": v for j, v in enumerate(chunk)})
            req = urllib.request.Request(API + "GetPublishedFileDetails/v1/", data=urllib.parse.urlencode(data).encode(), headers={"User-Agent": "CS2CommandCenter/2"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = json.loads(resp.read(8_000_000).decode("utf-8"))
            for d in body["response"]["publishedfiledetails"]:
                sizes[str(d.get("publishedfileid"))] = int(d.get("file_size") or 0) if d.get("result") == 1 else -1
        with _LOCK:
            c = _cache()
            c["sizes"].update(sizes)
            _save_cache(c)
    except Exception:
        pass
    known = [sizes[x] for x in ids if sizes.get(x, -1) > 0]
    return {"missing": len(ids), "known": len(known), "unknown": len(ids) - len(known), "bytes": int(sum(known))}
