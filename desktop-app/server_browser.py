"""
CS2 Zombie Escape Server Browser & Steam Connect Protocol Hub
Direct Game Server Connector (bypasses console) • Voice Chat Auto-Restart Workflow • Live A2S_INFO Queries
Built-in Silent Server Slot Sniper (Watches 64/64 full servers and auto-joins on slot opening)
ZE Graph REST Telemetry (Human/Zombie scores, Extends Left, Map Timer, Soundtrack, Thumbnails)
Attribution: queeniemella (InterStella0 - ZE Graph) & cybo (3D Map Viewer)
"""

import os
import sys
import json
import socket
import struct
import time
import subprocess
import threading
import datetime
import urllib.request
import urllib.parse
from typing import Dict, List, Any, Optional, Callable, Tuple
import core_logic

DEFAULT_SERVERS = [   {   'discord': 'https://discord.gg/gflze',
        'flag': '🇺🇸 US',
        'host': '74.91.124.21',
        'id': 'gfl',
        'is_featured': True,
        'name': 'GFL Clan Zombie Escape 24/7',
        'port': 27015,
        'region': 'North America (Chicago, US)',
        'website': 'https://gflclan.com'},
    {   'discord': 'https://discord.gg/pse',
        'flag': '🇯🇵 JP',
        'host': '103.62.49.55',
        'id': 'possession',
        'is_featured': False,
        'name': 'Possession Zombie Escape (PSE)',
        'port': 27015,
        'region': 'East Asia (Tokyo, JP)'},
    {   'discord': 'https://discord.gg/Mapeadores',
        'flag': '🇪🇺 EU',
        'host': '87.98.228.196',
        'id': 'mapeadores',
        'is_featured': False,
        'name': 'Mapeadores Zombie Escape',
        'port': 27040,
        'region': 'Europe (France / Spain)'},
    {   'discord': 'https://discord.gg/colateam',
        'flag': '🇪🇸 ES',
        'host': '178.33.160.187',
        'id': 'cola',
        'is_featured': False,
        'name': 'cOLa-TeaM Zombie Escape',
        'port': 27015,
        'region': 'Europe (Spain)'},
    {   'discord': 'https://discord.gg/rssze',
        'flag': '🇰🇷 KR',
        'host': '14.5.33.30',
        'domain': 'rsscs2.kr',
        'id': 'rss',
        'is_featured': False,
        'name': 'RSS Zombie Escape (Revenant)',
        'port': 27015,
        'region': 'East Asia (Seoul, KR)'},
    {   'flag': '🇷🇺 RU',
        'host': '46.174.54.231',
        'id': 'net4all',
        'is_featured': False,
        'name': 'Net4All.ru Zombie Escape',
        'port': 27015,
        'region': 'Eastern Europe (Moscow, RU)',
        'website': 'https://net4all.ru'}]

CHINA_CLUSTERS = [   {   'description': '16 Active Zombie Escape & PVE Nodes (source: bbs.darkrp.cn)',
        'id': 'exg',
        'name': 'EXG 社区 (EXG · 16 Nodes)',
        'region': 'Hong Kong / BGP Multi-Line',
        'servers': [   {'host': '202.189.10.89', 'id': 'exg_8', 'name': 'EXG ZE 装备 #8 (Main Cluster)', 'port': 27002},
                       {'host': '202.189.4.122', 'id': 'exg_3', 'name': 'EXG ZE 装备 #3', 'port': 27001},
                       {'host': '202.189.10.208', 'id': 'exg_16', 'name': 'EXG ZE 装备 #16', 'port': 27002},
                       {'host': '202.189.10.208', 'id': 'exg_11', 'name': 'EXG ZE 装备 #11', 'port': 27001},
                       {'host': '202.189.5.229', 'id': 'exg_pve2', 'name': 'EXG PVE 模式 #2', 'port': 27002},
                       {'host': '202.189.5.229', 'id': 'exg_pve1', 'name': 'EXG PVE 模式 #1', 'port': 27001},
                       {'host': '202.189.5.227', 'id': 'exg_13', 'name': 'EXG ZE 装备 #13', 'port': 27001},
                       {'host': '202.189.4.230', 'id': 'exg_5', 'name': 'EXG ZE #5', 'port': 27001},
                       {'host': '202.189.5.225', 'id': 'exg_12', 'name': 'EXG ZE 装备 #12', 'port': 27001},
                       {'host': '202.189.4.230', 'id': 'exg_6', 'name': 'EXG ZE #6', 'port': 27002},
                       {'host': '202.189.10.203', 'id': 'exg_10', 'name': 'EXG ZE 装备 #10', 'port': 27001},
                       {'host': '202.189.5.221', 'id': 'exg_9', 'name': 'EXG ZE 装备 #9', 'port': 27001},
                       {'host': '202.189.5.225', 'id': 'exg_17', 'name': 'EXG ZE 装备 #17', 'port': 27002},
                       {'host': '202.189.10.196', 'id': 'exg_7', 'name': 'EXG ZE 装备 #7', 'port': 27001},
                       {'host': '202.189.5.227', 'id': 'exg_18', 'name': 'EXG ZE 装备 #18', 'port': 27002},
                       {'host': '202.189.5.236', 'id': 'exg_14', 'name': 'EXG ZE 装备 #14', 'port': 27001}],
        'tag': 'EXG ZE'},
    {   'description': '6 Active Zombie Escape Nodes (source: bbs.fyscs.com)',
        'id': 'fys',
        'name': '风云社 (FyS · 6 Nodes)',
        'region': 'Mainland China / BGP Multi-Line',
        'servers': [   {'host': '110.42.9.107', 'id': 'fys_8', 'name': '【風雲】 僵尸逃跑 08#', 'port': 27085},
                       {'host': '110.42.9.139', 'id': 'fys_3', 'name': '【風雲】 僵尸逃跑 03#', 'port': 27035},
                       {'host': '110.42.9.139', 'id': 'fys_7', 'name': '【風雲】 僵尸逃跑 07#', 'port': 27075},
                       {'host': '110.42.9.155', 'id': 'fys_1', 'name': '【風雲】 僵尸逃跑 01#', 'port': 27015},
                       {'host': '110.42.9.138', 'id': 'fys_5', 'name': '【風雲】 僵尸逃跑 05#', 'port': 27055},
                       {'host': '110.42.9.138', 'id': 'fys_4', 'name': '【風雲】 僵尸逃跑 04#', 'port': 27045}],
        'tag': 'FyS ZE'},
    {   'description': '6 Active Zombie Escape Nodes (source: cs.moeub.cn)',
        'id': 'ub',
        'name': '萌UB (MoeUB · 6 Nodes)',
        'region': 'Mainland China / BGP Multi-Line',
        'servers': [   {'host': '110.42.9.188', 'id': 'ub_3', 'name': 'UB社区 CS2 僵尸逃跑 #03', 'port': 27031},
                       {'host': '110.42.9.188', 'id': 'ub_1', 'name': 'UB社区 CS2 僵尸逃跑 #01', 'port': 27011},
                       {'host': '110.42.9.188', 'id': 'ub_2', 'name': 'UB社区 CS2 僵尸逃跑 #02', 'port': 27021},
                       {'host': '110.42.9.195', 'id': 'ub_11', 'name': 'UB社区 CS2 僵尸逃跑 #11', 'port': 27111},
                       {'host': '110.42.9.195', 'id': 'ub_12', 'name': 'UB社区 CS2 僵尸逃跑 #12', 'port': 27121},
                       {'host': '110.42.9.195', 'id': 'ub_13', 'name': 'UB社区 CS2 僵尸逃跑 #13', 'port': 27131}],
        'tag': 'UB ZE'},
    {   'description': '5 Active Zombie Escape Nodes (source: bbs.zombieden.cn)',
        'id': 'zl',
        'name': '僵尸乐园 (ZL · 5 Nodes)',
        'region': 'Mainland China / BGP Multi-Line',
        'servers': [   {'host': '110.42.9.181', 'id': 'zl_2', 'name': '【僵尸乐园】 CS2 ZE #2', 'port': 27015},
                       {'host': '110.42.9.22', 'id': 'zl_1', 'name': '【僵尸乐园】 CS2 ZE #1', 'port': 27016},
                       {'host': '110.42.9.181', 'id': 'zl_3', 'name': '【僵尸乐园】 CS2 ZE #3', 'port': 27016},
                       {'host': '110.42.9.149', 'id': 'zl_4', 'name': '【僵尸乐园】 CS2 ZE #4', 'port': 27015},
                       {'host': '110.42.9.149', 'id': 'zl_5', 'name': '【僵尸乐园】 CS2 ZE #5', 'port': 27016}],
        'tag': 'ZL ZE'},
    {   'description': '2 Active Zombie Escape Nodes (source: 93x.net)',
        'id': '93x',
        'name': '93X 社区 (93X · 2 Nodes)',
        'region': 'Mainland China / BGP Multi-Line',
        'servers': [   {'host': '43.142.148.163', 'id': '93x_1', 'name': '93X Zombie Escape #1', 'port': 27015},
                       {'host': '43.142.148.163', 'id': '93x_2', 'name': '93X Zombie Escape #2', 'port': 27016}],
        'tag': '93X ZE'}]

def get_storage_dir() -> str:
    """Returns persistent app storage directory in %APPDATA%/CS2CommandCenter."""
    app_data = os.getenv("APPDATA")
    if app_data:
        base = os.path.join(app_data, "CS2CommandCenter")
    elif getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(__file__)
    os.makedirs(base, exist_ok=True)
    return base

SERVERS_FILE = os.path.join(get_storage_dir(), "custom_servers.json")

# AUDIT 1c-D1: one shared check for every host:port the app connects to.
# The host ends up in "steam://connect/HOST:PORT" (opened through Windows) and in the
# CS2 console as "connect HOST:PORT". Without a check, text such as "1.2.3.4;quit" or
# "x&calc" could run extra console or Windows commands.
import re as _re
_HOSTNAME_RE = _re.compile(r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*$")
_IPV4_RE = _re.compile(r"^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$")


def validate_server_address(host: Any, port: Any) -> Optional[tuple]:
    """Returns (host, port) when the pair is a plain IPv4/hostname and a port 1-65535, else None."""
    try:
        host = str(host).strip()
        if isinstance(port, bool):
            return None
        port = int(str(port).strip())
    except Exception:
        return None
    if not (1 <= port <= 65535):
        return None
    if _IPV4_RE.match(host) or (_HOSTNAME_RE.match(host) and not host.replace(".", "").isdigit()):
        return host, port
    return None

def load_servers() -> List[Dict[str, Any]]:
    """Loads default servers merged with any user-saved custom servers."""
    customs = []
    if os.path.exists(SERVERS_FILE):
        try:
            with open(SERVERS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if isinstance(saved, list):
                    customs = [s for s in saved if isinstance(s, dict) and s.get("is_custom")
                               and validate_server_address(s.get("host"), s.get("port"))]
        except Exception:
            pass
    return list(DEFAULT_SERVERS) + customs

def get_all_servers() -> List[Dict[str, Any]]:
    """Alias for load_servers() to return all registered servers."""
    return load_servers()

def save_servers(servers: List[Dict[str, Any]]) -> bool:
    """Saves server list to local JSON file."""
    try:
        with open(SERVERS_FILE, "w", encoding="utf-8") as f:
            json.dump(servers, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


# Connection In-Flight Mutex to prevent duplicate connect attempts
_connection_lock = threading.Lock()
_connection_in_flight = False
_connection_in_flight_since = 0.0

def is_connection_in_flight() -> bool:
    global _connection_in_flight, _connection_in_flight_since
    with _connection_lock:
        if _connection_in_flight and (time.time() - _connection_in_flight_since > 18.0):
            _connection_in_flight = False
            _connection_in_flight_since = 0.0
        return _connection_in_flight

def set_connection_in_flight(active: bool):
    global _connection_in_flight, _connection_in_flight_since
    with _connection_lock:
        _connection_in_flight = active
        _connection_in_flight_since = time.time() if active else 0.0

# ==============================================================================
# ZE GRAPH CLOUD TELEMETRY & MULTIMEDIA CLIENT
# Direct REST Telemetry (Human Score, Zombie Score, Extends Left, Started At)
# Map Soundtrack Intel & Map Preview Thumbnail Caching
# Author: GeronimoHQ & queeniemella (InterStella0)
# ==============================================================================

_GFL_ZEGRAPH_SERVER_ID = "65bdad6379cefd7ebcecce5c"
_cached_match_now: Dict[str, Any] = {}
_last_match_fetch_time: float = 0.0
_cached_soundtracks: Dict[str, List[Dict[str, Any]]] = {}
_thumbnail_cache: Dict[str, Optional[str]] = {}
_thumbnail_downloading: set = set()

def query_zegraph_match_now(timeout: float = 3.5, force_refresh: bool = False) -> Dict[str, Any]:
    """
    Fetches real-time GFL Zombie Escape match telemetry (Human score, Zombie score, Extends).
    Uses anti-stale caching to guarantee zero UI flickering across periodic polling loops.
    """
    global _cached_match_now, _last_match_fetch_time
    now = time.time()
    if not force_refresh and _cached_match_now and (now - _last_match_fetch_time < 2.5):
        return dict(_cached_match_now)

    url = f"https://zegraph.xyz/data/api/servers/{_GFL_ZEGRAPH_SERVER_ID}/match-now?_t={int(now * 1000)}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "CS2CommandCenter/1.0",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                payload = json.loads(resp.read().decode("utf-8"))
                if payload.get("code") == 0 and payload.get("data"):
                    d = payload["data"]
                    started_at = d.get("started_at", "")
                    started_sec = 0
                    if started_at:
                        try:
                            dt = datetime.datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                            started_sec = int(dt.timestamp())
                        except Exception:
                            pass

                    _cached_match_now = {
                        "human_score": int(d.get("human_score", 0)),
                        "zombie_score": int(d.get("zombie_score", 0)),
                        "extend_count": int(d.get("extend_count", 0)),
                        "map": d.get("map", ""),
                        "player_count": int(d.get("player_count", 0)),
                        "started_at": started_at,
                        "started_timestamp": started_sec,
                        "success": True,
                        "fetched_at": now
                    }
                    _last_match_fetch_time = now
                    return dict(_cached_match_now)
    except Exception:
        pass

    # If fetch failed or network timed out, return last cached match to prevent zeroing scores
    if _cached_match_now:
        fallback = dict(_cached_match_now)
        fallback["success"] = False
        return fallback

    return {
        "human_score": 0,
        "zombie_score": 0,
        "extend_count": 0,
        "map": "",
        "player_count": 0,
        "started_at": "",
        "started_timestamp": 0,
        "success": False,
        "fetched_at": 0
    }

def query_zegraph_soundtrack(map_name: str, timeout: float = 3.5) -> List[Dict[str, Any]]:
    """
    Fetches soundtrack configuration for a given map from the ZE Graph database.
    Includes song name, duration (seconds and MM:SS), YouTube video/music links, and stage tags.
    """
    clean_map = map_name.strip().lower()
    if not clean_map or clean_map in ("-", "unknown"):
        return []

    if clean_map in _cached_soundtracks:
        return _cached_soundtracks[clean_map]

    def _fetch_for_name(target_name: str) -> List[Dict[str, Any]]:
        url = f"https://zegraph.xyz/data/api/servers/{_GFL_ZEGRAPH_SERVER_ID}/maps/{urllib.parse.quote(target_name)}/musics"
        req = urllib.request.Request(url, headers={"User-Agent": "CS2CommandCenter/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    payload = json.loads(resp.read().decode("utf-8"))
                    data = payload.get("data")
                    if isinstance(data, list):
                        tracks = []
                        for item in data:
                            dur_sec = int(item.get("duration", 0))
                            dur_str = f"{dur_sec // 60:02d}:{dur_sec % 60:02d}" if dur_sec > 0 else "-"
                            yt_id = item.get("youtube_music") or item.get("youtube_video")
                            tracks.append({
                                "id": item.get("id"),
                                "name": item.get("name", "Unknown Track"),
                                "duration_sec": dur_sec,
                                "duration_str": dur_str,
                                "youtube_id": yt_id,
                                "youtube_url": f"https://www.youtube.com/watch?v={yt_id}" if yt_id else None,
                                "tags": item.get("tags", [])
                            })
                        return tracks
        except Exception:
            pass
        return []

    tracks = _fetch_for_name(clean_map)
    if not tracks and clean_map.endswith("_p"):
        tracks = _fetch_for_name(clean_map[:-2])

    _cached_soundtracks[clean_map] = tracks
    return tracks

def get_thumbnail_dir() -> str:
    """Returns local thumbnail cache directory."""
    tdir = os.path.join(get_storage_dir(), "thumbnails")
    os.makedirs(tdir, exist_ok=True)
    return tdir

def clean_map_slug(map_name: str) -> str:
    """Strips workshop directories, file extensions, and slashes to get pure map slug."""
    if not map_name:
        return ""
    clean = map_name.strip().lower()
    if "/" in clean:
        clean = clean.split("/")[-1]
    if "\\" in clean:
        clean = clean.split("\\")[-1]
    if clean.endswith(".vpk"):
        clean = clean[:-4]
    return clean.strip()

_S2ZE_CACHE_MAPS = None

def _get_s2ze_map_meta(clean_map: str):
    global _S2ZE_CACHE_MAPS
    if _S2ZE_CACHE_MAPS is None:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 's2ze_maps_cache.json')
        if os.path.exists(p):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    _S2ZE_CACHE_MAPS = json.load(f)
            except Exception:
                _S2ZE_CACHE_MAPS = {}
        else:
            _S2ZE_CACHE_MAPS = {}
    
    clean = clean_map.lower().strip()
    if clean in _S2ZE_CACHE_MAPS:
        return _S2ZE_CACHE_MAPS[clean]
    stripped = clean.replace('_p', '')
    if stripped in _S2ZE_CACHE_MAPS:
        return _S2ZE_CACHE_MAPS[stripped]
    return None

def get_server_demographics(region_name: str, total_players: int, geo: Optional[Dict[str, Any]] = None,
                            names: Optional[List[str]] = None, max_items: int = 4, mode: str = "country"):
    """GEO line + tooltip, same method as geronimohq.com (owner request 2026-11-10): an ESTIMATE from
    player-name signals + a time-of-day model per region, aligned to ZEGraph's measured
    continents for GFL. See geo_estimate.py (a line-by-line port of serverDemographics.ts;
    a test checks both give the same numbers). mode = "country" or "region". Only counts/names the
    servers already publish are used; no player is shown. Returns (text, tooltip)."""
    if total_players <= 0:
        return "🌐 GEO: server empty", "No players on the server right now."
    import geo_estimate
    raw = (geo or {}).get("raw") if isinstance(geo, dict) else None
    items = geo_estimate.estimate_countries(region_name, total_players, names or [], raw)
    if not items:
        return "🌐 GEO: no estimate", "Not enough data for an estimate."
    if mode == "region":
        items = geo_estimate.estimate_regions(items)
    label = "By Region" if mode == "region" else "By Country"
    parts = [f"{it['code']} {it['percentage']}%" for it in items[:max_items]]
    more = len(items) - max_items
    tail = f" · +{more} more" if more > 0 else ""
    text = "🌐 GEO (estimate): " + " · ".join(parts) + tail
    lines = [f"{it['name']}: {it['percentage']}% (~{it['count']} players)" for it in items]
    tip = (f"Live geographic demographics ({label}), an estimate:" + chr(10) + chr(10).join(lines) + chr(10)
           + "Based on player-name signals and the time-of-day activity of each region." + chr(10)
           + "No individual player is identified.")
    return text, tip


def get_server_demographics_text(region_name: str, total_players: int, geo: Optional[Dict[str, Any]] = None,
                                 names: Optional[List[str]] = None, max_items: int = 4, mode: str = "country") -> str:
    return get_server_demographics(region_name, total_players, geo, names, max_items, mode)[0]


_CONTINENT_SHORT = {"North America": "N. America", "South America": "S. America"}
_GEO_CACHE: Dict[str, Any] = {"at": 0.0, "data": None}
GEO_CACHE_S = 300
_GFL_CONTINENTS_URL = "https://zegraph.xyz/data/api/radars/65bdad6379cefd7ebcecce5c/live_statistics/continents"


def parse_zegraph_continents(payload: Any) -> Optional[Dict[str, Any]]:
    """ZEGraph continent stats -> {"sample", "total", "top": [(name, pct), ...]}.
    sample = players with a known country (contain_countries); percentages use it."""
    data = (payload or {}).get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        return None
    conts = [c for c in (data.get("continents") or []) if isinstance(c, dict) and int(c.get("count") or 0) > 0]
    sample = int(data.get("contain_countries") or sum(int(c["count"]) for c in conts))
    total = int(data.get("total_count") or sample)
    if sample <= 0 or not conts:
        return {"ok": True, "sample": 0, "total": total, "top": [], "raw": data}
    top = sorted(((_CONTINENT_SHORT.get(c.get("name"), c.get("name") or "Other"),
                   round(100 * int(c["count"]) / sample)) for c in conts), key=lambda x: -x[1])
    return {"ok": True, "sample": sample, "total": total, "top": top, "raw": data}


def fetch_gfl_continents(timeout: float = 4.0, now: Optional[float] = None) -> Optional[Dict[str, Any]]:
    """Same source as the website's geo radar (ZEGraph live continents for GFL).
    Cached 5 min; if offline, returns the last good value with its age; else None."""
    now = time.time() if now is None else now
    cached = _GEO_CACHE.get("data")
    if cached and now - _GEO_CACHE["at"] < GEO_CACHE_S:
        return dict(cached, age_s=now - _GEO_CACHE["at"])
    try:
        req = urllib.request.Request(_GFL_CONTINENTS_URL, headers={"User-Agent": "CS2CommandCenter/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            parsed = parse_zegraph_continents(json.loads(resp.read(65536).decode("utf-8", "replace")))
        if parsed:
            _GEO_CACHE.update(at=now, data=parsed)
            return dict(parsed, age_s=0.0)
    except Exception:
        pass
    if cached:
        return dict(cached, age_s=now - _GEO_CACHE["at"])  # offline fallback: last known, with age
    return None


# AUDIT P2-#2/#5: the app reads the SAME backend the website uses, with a cache and an
# offline fallback (direct A2S of the catalog). Read-only GET; sends no user data.
BACKEND_SERVERS_URL = "https://geronimohq-telemetry.onrender.com/api/servers"
TOTALS_CACHE_S = 60
_TOTALS_CACHE: Dict[str, Any] = {"at": 0.0, "totals": None, "source": None}
_LAST_BACKEND: Dict[str, Any] = {"at": 0.0, "payload": None}


def backend_player_names(server_id: str, max_age_s: float = 600) -> List[str]:
    """Player names for a server from the last backend /api/servers payload (the same
    data the website uses for its geo radar). Empty if none or older than 10 min."""
    p = _LAST_BACKEND.get("payload")
    if not p or time.time() - _LAST_BACKEND.get("at", 0) > max_age_s:
        return []
    s = ((p.get("servers") or {}).get(server_id) or {})
    return [str(x.get("name", "")) for x in (s.get("players_list") or []) if isinstance(x, dict)]


def fetch_backend_servers(timeout: float = 6.0) -> Optional[Dict[str, Any]]:
    try:
        req = urllib.request.Request(BACKEND_SERVERS_URL, headers={"User-Agent": "CS2CommandCenter/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return None
            data = json.loads(resp.read(4 * 1024 * 1024).decode("utf-8", "replace"))
        return data if isinstance(data, dict) and isinstance(data.get("servers"), dict) else None
    except Exception:
        return None


def get_shared_totals(now: Optional[float] = None, fetch_backend=None, query_direct=None) -> Dict[str, Any]:
    """Totals for the Dashboard card AND the ZE Game Servers pills (one function).
    Order: fresh cache (60 s) -> backend /api/servers -> direct A2S of the catalog."""
    now = time.time() if now is None else now
    if _TOTALS_CACHE["totals"] and now - _TOTALS_CACHE["at"] < TOTALS_CACHE_S:
        return dict(_TOTALS_CACHE["totals"], source=_TOTALS_CACHE["source"])
    fetch_backend = fetch_backend or fetch_backend_servers
    query_direct = query_direct or query_catalog_rows
    payload = fetch_backend()
    if payload:
        _LAST_BACKEND["payload"], _LAST_BACKEND["at"] = payload, now
        t = payload.get("totals")
        if not isinstance(t, dict) or "humans" not in t:
            # Older backend without `totals`: apply the same rule to its rows.
            t = compute_player_totals(totals_rows_from_api(payload, received_at=now), now=now)
        source = "backend"
    else:
        t = compute_player_totals(query_direct(), now=now)
        source = "direct"
    t = {k: v for k, v in t.items() if k != "rows"}
    _TOTALS_CACHE.update(at=now, totals=t, source=source)
    return dict(t, source=source)

def get_or_download_map_thumbnail(map_name: str, callback: Optional[Callable[[str, str], None]] = None) -> Optional[str]:
    """
    Returns local path to cached map thumbnail (.jpg).
    If missing, initiates asynchronous background download from ZE Graph CDN and returns None.
    Once downloaded, invokes optional callback(map_name, local_path).
    """
    clean_map = clean_map_slug(map_name)
    if not clean_map or clean_map in ("-", "unknown", "none"):
        return None

    tdir = get_thumbnail_dir()
    
    # Check disk for direct match or _p variants
    possible_disk_paths = [os.path.join(tdir, f"{clean_map}.jpg")]
    if clean_map.endswith("_p"):
        possible_disk_paths.append(os.path.join(tdir, f"{clean_map[:-2]}.jpg"))
    else:
        possible_disk_paths.append(os.path.join(tdir, f"{clean_map}_p.jpg"))

    for p in possible_disk_paths:
        if os.path.exists(p) and os.path.getsize(p) > 1024:
            if callback:
                try:
                    callback(clean_map, p)
                except Exception:
                    pass
            return p

    local_path = possible_disk_paths[0]

    # Check memory cache
    if clean_map in _thumbnail_cache and _thumbnail_cache[clean_map]:
        if os.path.exists(_thumbnail_cache[clean_map]):
            if callback:
                try:
                    callback(clean_map, _thumbnail_cache[clean_map])
                except Exception:
                    pass
            return _thumbnail_cache[clean_map]

    if clean_map in _thumbnail_downloading:
        return None

    _thumbnail_downloading.add(clean_map)

    def _worker():
        try:
            candidate_urls = [
                f"https://geronimohq.com/images/maps/{clean_map}.jpg",
            ]
            meta = _get_s2ze_map_meta(clean_map)
            if meta and meta.get("image"):
                candidate_urls.append(meta["image"])

            candidate_urls.append(f"https://zegraph.xyz/thumbnails/medium/workshop--{clean_map}.jpg")
            candidate_urls.append(f"https://zegraph.xyz/thumbnails/medium/730_cs2--{clean_map}.jpg")
            if clean_map.endswith("_p"):
                candidate_urls.append(f"https://zegraph.xyz/thumbnails/medium/730_cs2--{clean_map[:-2]}.jpg")
                candidate_urls.append(f"https://zegraph.xyz/thumbnails/medium/workshop--{clean_map[:-2]}.jpg")
            else:
                candidate_urls.append(f"https://zegraph.xyz/thumbnails/medium/730_cs2--{clean_map}_p.jpg")
                candidate_urls.append(f"https://zegraph.xyz/thumbnails/medium/workshop--{clean_map}_p.jpg")
            candidate_urls.append(f"https://zegraph.xyz/thumbnails/medium/730--{clean_map}.jpg")

            downloaded = False
            for url in candidate_urls:
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "CS2CommandCenter/1.0"})
                    with urllib.request.urlopen(req, timeout=3.5) as resp:
                        if resp.status == 200:
                            data = resp.read()
                            if len(data) > 1024:
                                with open(local_path, "wb") as f:
                                    f.write(data)
                                downloaded = True
                                break
                except Exception:
                    continue

            if downloaded:
                _thumbnail_cache[clean_map] = local_path
                if callback:
                    try:
                        callback(clean_map, local_path)
                    except Exception:
                        pass
            else:
                _thumbnail_cache[clean_map] = None
        finally:
            _thumbnail_downloading.discard(clean_map)

    threading.Thread(target=_worker, daemon=True).start()
    return None

_ROSTER_CACHE: Dict[Tuple[str, int], Tuple[float, Optional[int]]] = {}


def query_server_info(host: str, port: int, timeout: float = 1.8) -> Dict[str, Any]:
    """
    Queries Source Engine A2S_INFO via UDP packet.
    Handles challenge response (0x41) and returns live server name, map, players, and ping.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    
    # Resolve domain if needed
    try:
        target_ip = socket.gethostbyname(host)
    except Exception as e:
        sock.close()
        return {
            "online": False,
            "status": "DNS Error",
            "map": "Unknown",
            "players": "-/-",
            "curr_players": 0,
            "max_players": 0,
            "ping": "N/A",
            "error": str(e)
        }

    query = b"\xFF\xFF\xFF\xFF\x54Source Engine Query\x00"
    t0 = time.time()
    try:
        sock.sendto(query, (target_ip, port))
        data, _ = sock.recvfrom(4096)
        rtt = int((time.time() - t0) * 1000)

        # Handle challenge response (0x41)
        if len(data) >= 5 and data[4] == 0x41:
            challenge = data[5:9]
            query_with_challenge = b"\xFF\xFF\xFF\xFF\x54Source Engine Query\x00" + challenge
            t0 = time.time()
            sock.sendto(query_with_challenge, (target_ip, port))
            data, _ = sock.recvfrom(4096)
            rtt = int((time.time() - t0) * 1000)

        # Parse A2S_INFO header (0x49)
        if len(data) > 5 and data[4] == 0x49:
            idx = 6  # skip protocol
            
            # Server name
            name_end = data.find(b"\x00", idx)
            name = data[idx:name_end].decode("utf-8", errors="replace")
            idx = name_end + 1
            
            # Map name
            map_end = data.find(b"\x00", idx)
            map_name = data[idx:map_end].decode("utf-8", errors="replace")
            idx = map_end + 1
            
            # Folder
            folder_end = data.find(b"\x00", idx)
            idx = folder_end + 1
            
            # Game name
            game_end = data.find(b"\x00", idx)
            idx = game_end + 1
            
            # ID (short)
            idx += 2
            
            # Players, Max Players, Bots
            players = data[idx]
            max_players = data[idx + 1]
            bots = data[idx + 2]
            # Some servers (Net4All, FYS) report bots=0 but count bots in "players". A2S_PLAYER lists humans
            # only, so when its roster is smaller than players - bots, the difference is bots.
            if players > 0 and bots == 0:
                try:
                    # the roster answer is cached for 10 s so fast refresh rates do not double the query rate
                    hit = _ROSTER_CACHE.get((host, port))
                    if hit and time.time() - hit[0] < 10:
                        roster_count = hit[1]
                    else:
                        roster = query_server_players(host, port, timeout=1.5)
                        roster_count = roster.get("count", 0) if roster.get("success") else None
                        _ROSTER_CACHE[(host, port)] = (time.time(), roster_count)
                    if roster_count is not None and roster_count < players:
                        bots = players - roster_count
                except Exception:
                    pass

            return {
                "online": True,
                "status": "Online",
                "server_name": name,
                "map": map_name,
                "players": f"{players}/{max_players}",
                "curr_players": players,
                "max_players": max_players,
                "bots": bots,
                "ping": f"{rtt} ms",
                "rtt": rtt
            }
    except socket.timeout:
        return {
            "online": False,
            "status": "Timed Out",
            "map": "-",
            "players": "-/-",
            "curr_players": 0,
            "max_players": 0,
            "ping": "N/A",
            "error": "Timeout"
        }
    except Exception as e:
        return {
            "online": False,
            "status": "Offline",
            "map": "-",
            "players": "-/-",
            "curr_players": 0,
            "max_players": 0,
            "ping": "N/A",
            "error": str(e)
        }
    finally:
        sock.close()

    return {
        "online": False,
        "status": "Invalid Response",
        "map": "-",
        "players": "-/-",
        "curr_players": 0,
        "max_players": 0,
        "ping": "N/A"
    }

def query_server_players(host: str, port: int, timeout: float = 2.5) -> Dict[str, Any]:
    """
    Queries live player roster via Source Engine A2S_PLAYER protocol.
    Step 1: Send A2S_PLAYER query (header 0x55 + 0xFFFFFFFF challenge).
    Step 2: Server responds with challenge (header 0x41 + 4-byte token).
    Step 3: Send A2S_PLAYER query again with received challenge token.
    Step 4: Server responds with A2S_PLAYER payload (header 0x44).
    Parses and returns list of players sorted by score descending.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)

    try:
        target_ip = socket.gethostbyname(host)
    except Exception as e:
        sock.close()
        return {"success": False, "error": f"DNS resolution failed: {e}", "players": []}

    try:
        # Step 1: Request Challenge
        req_challenge = b"\xFF\xFF\xFF\xFF\x55\xFF\xFF\xFF\xFF"
        sock.sendto(req_challenge, (target_ip, port))
        data, _ = sock.recvfrom(4096)

        # Step 2: Extract Challenge Token (header 0x41)
        if len(data) >= 9 and data[4] == 0x41:
            challenge_token = data[5:9]
            req_players = b"\xFF\xFF\xFF\xFF\x55" + challenge_token
            sock.sendto(req_players, (target_ip, port))
            data, _ = sock.recvfrom(8192)

        # Step 3: Parse A2S_PLAYER Response (header 0x44)
        if len(data) > 5 and data[4] == 0x44:
            num_players = data[5]
            idx = 6
            players = []

            for _ in range(num_players):
                if idx >= len(data):
                    break
                p_idx = data[idx]
                idx += 1

                # Player name (null-terminated string)
                name_end = data.find(b"\x00", idx)
                if name_end == -1:
                    break
                raw_name = data[idx:name_end]
                name = raw_name.decode("utf-8", errors="replace").strip()
                idx = name_end + 1

                if idx + 8 > len(data):
                    break

                # Score (int32) and Duration (float32)
                score = struct.unpack("<i", data[idx:idx + 4])[0]
                idx += 4
                dur_float = struct.unpack("<f", data[idx:idx + 4])[0]
                idx += 4

                total_seconds = int(max(0.0, dur_float))
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                if hours > 0:
                    time_str = f"{hours}h {minutes:02d}m {seconds:02d}s"
                else:
                    time_str = f"{minutes:02d}m {seconds:02d}s"

                display_name = name if name else "[Connecting...]"
                players.append({
                    "index": p_idx,
                    "name": display_name,
                    "score": score,
                    "time": time_str,
                    "seconds": total_seconds
                })

            players.sort(key=lambda x: x["score"], reverse=True)
            return {"success": True, "count": len(players), "players": players}

    except socket.timeout:
        return {"success": False, "error": "Query timed out (Server may shield UDP A2S_PLAYER).", "players": []}
    except Exception as e:
        return {"success": False, "error": str(e), "players": []}
    finally:
        sock.close()

    return {"success": False, "error": "Invalid response from server", "players": []}

def is_cs2_running() -> bool:
    """Checks if cs2.exe is currently active in <5ms without spawning cmd/tasklist."""
    try:
        return core_logic.is_cs2_running()
    except Exception:
        return False

is_cs2_open = is_cs2_running

def _copy_clipboard_fast(text: str):
    """Copies text to Windows clipboard instantly using 64-bit safe Win32 API."""
    try:
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32

        kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
        kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
        kernel32.GlobalLock.restype = wintypes.LPVOID
        kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
        kernel32.GlobalUnlock.restype = wintypes.BOOL
        kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]

        user32.OpenClipboard.restype = wintypes.BOOL
        user32.OpenClipboard.argtypes = [wintypes.HWND]
        user32.EmptyClipboard.restype = wintypes.BOOL
        user32.SetClipboardData.restype = wintypes.HANDLE
        user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
        user32.CloseClipboard.restype = wintypes.BOOL

        if user32.OpenClipboard(None):
            user32.EmptyClipboard()
            data = text.encode("utf-16le") + b"\x00\x00"
            h_mem = kernel32.GlobalAlloc(0x0002, len(data))  # GMEM_MOVEABLE
            if h_mem:
                ptr = kernel32.GlobalLock(h_mem)
                if ptr:
                    ctypes.memmove(ptr, data, len(data))
                    kernel32.GlobalUnlock(h_mem)
                    user32.SetClipboardData(13, h_mem)  # CF_UNICODETEXT
            user32.CloseClipboard()
            return True
    except Exception:
        pass
    return False

def direct_connect(host: str, port: int) -> bool:
    """Connects to server via native Steam URL protocol (bypasses console)."""
    if not validate_server_address(host, port):
        return False
    try:
        resolved_ip = socket.gethostbyname(host)
    except Exception:
        resolved_ip = host
    if not validate_server_address(resolved_ip, port):
        return False
    cmd = f"connect {resolved_ip}:{port}"
    _copy_clipboard_fast(cmd)
    url = f"steam://connect/{resolved_ip}:{port}"
    try:
        os.startfile(url)
        return True
    except Exception:
        pass
    try:
        subprocess.Popen(["cmd.exe", "/c", "start", "", url], creationflags=0x08000000)
        return True
    except Exception:
        return False

def fast_console_connect(host: str, port: int, restore_previous_window: bool = True) -> bool:
    """Connects to server using direct in-engine console execution for fastest possible connection.
    Bypasses Steam coordinator delay, copies connect command to clipboard, submits via console,
    and immediately restores the user's previous foreground window so CS2 loads in the background."""
    if not validate_server_address(host, port):
        return False
    cmd = f"connect {host}:{port}"
    _copy_clipboard_fast(cmd)

    try:
        import ctypes
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        hwnd = user32.FindWindowW("SDL_app", "Counter-Strike 2")
        if not hwnd:
            hwnd = user32.FindWindowW(None, "Counter-Strike 2")
        if hwnd:
            fg_hwnd = user32.GetForegroundWindow()
            was_other_window = bool(fg_hwnd and fg_hwnd != hwnd)
            cur_thread = kernel32.GetCurrentThreadId()
            fg_thread = user32.GetWindowThreadProcessId(fg_hwnd, None) if fg_hwnd else 0
            target_thread = user32.GetWindowThreadProcessId(hwnd, None)

            # Attach thread input to bypass Windows focus stealing restrictions
            if fg_thread and fg_thread != cur_thread:
                user32.AttachThreadInput(cur_thread, fg_thread, True)
            if target_thread and target_thread != cur_thread:
                user32.AttachThreadInput(cur_thread, target_thread, True)

            user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            user32.SetForegroundWindow(hwnd)
            user32.BringWindowToTop(hwnd)

            if fg_thread and fg_thread != cur_thread:
                user32.AttachThreadInput(cur_thread, fg_thread, False)
            if target_thread and target_thread != cur_thread:
                user32.AttachThreadInput(cur_thread, target_thread, False)

            time.sleep(0.15)

            # Alt-Tab Keystroke Safety Guard:
            # If Windows blocks bringing CS2 to foreground (e.g. user interacting with elevated app or alt-tabbed),
            # abort console keystrokes immediately to avoid typing into another app, and fallback to direct Steam protocol!
            if user32.GetForegroundWindow() != hwnd:
                return direct_connect(host, port)

            VK_OEM_3 = 0xC0    # `~` tilde key
            VK_CONTROL = 0x11
            VK_V = 0x56
            VK_RETURN = 0x0D
            VK_BACK = 0x08

            # 1. Open Console
            user32.keybd_event(VK_OEM_3, 0, 0, 0)
            user32.keybd_event(VK_OEM_3, 0, 2, 0)
            time.sleep(0.20)

            # 2. Clear any stray tilde character by sending backspace
            user32.keybd_event(VK_BACK, 0, 0, 0)
            user32.keybd_event(VK_BACK, 0, 2, 0)
            time.sleep(0.04)

            # 3. Paste `connect host:port` from clipboard (Ctrl+V)
            user32.keybd_event(VK_CONTROL, 0, 0, 0)
            user32.keybd_event(VK_V, 0, 0, 0)
            time.sleep(0.04)
            user32.keybd_event(VK_V, 0, 2, 0)
            user32.keybd_event(VK_CONTROL, 0, 2, 0)
            time.sleep(0.08)

            # 4. Press Enter to submit
            user32.keybd_event(VK_RETURN, 0, 0, 0)
            user32.keybd_event(VK_RETURN, 0, 2, 0)
            time.sleep(0.12)

            # 6. If user was tabbed out in another window, restore their previous window immediately
            # so CS2 connects and loads the map in the background!
            if restore_previous_window and was_other_window and user32.IsWindow(fg_hwnd):
                try:
                    time.sleep(0.05)
                    if target_thread and target_thread != cur_thread:
                        user32.AttachThreadInput(cur_thread, target_thread, True)
                    if fg_thread and fg_thread != cur_thread:
                        user32.AttachThreadInput(cur_thread, fg_thread, True)
                    user32.SetForegroundWindow(fg_hwnd)
                    user32.BringWindowToTop(fg_hwnd)
                    if fg_thread and fg_thread != cur_thread:
                        user32.AttachThreadInput(cur_thread, fg_thread, False)
                    if target_thread and target_thread != cur_thread:
                        user32.AttachThreadInput(cur_thread, target_thread, False)
                except Exception:
                    pass
            return True
    except Exception:
        pass

    return direct_connect(host, port)

def connect_to_server(
    host: str,
    port: int,
    server_name: str,
    delay_seconds: float = 0.0,
    status_callback: Optional[Callable[[str], None]] = None,
    log_callback: Optional[Callable[[str], None]] = None,
    completion_callback: Optional[Callable[[bool, str], None]] = None
) -> threading.Thread:
    """
    Executes the server connection workflow strictly via Steam Game Server protocol.
    Scenario 1 (CS2 is closed): Launches CS2 cleanly via steam://run/730 -> waits 15s -> connects via steam://connect/
    Scenario 2 (CS2 is open): Connects immediately via steam://connect/ with 0s delay (no console injection).
    """
    def _worker():
        def _log(msg: str):
            if log_callback:
                log_callback(msg)
        if not validate_server_address(host, port):
            _log(f"[CONNECT] Refused: not a valid host:port ({str(host)[:40]!r}).")
            if completion_callback:
                completion_callback(False, "Invalid server address")
            return

        def _status(msg: str):
            if status_callback:
                status_callback(msg)

        try:
            cmd = f"connect {host}:{port}"
            _copy_clipboard_fast(cmd)
            _log(f"[CONNECT] Prepared connect command: '{cmd}'")

            set_connection_in_flight(True)
            try:
                resolved_ip = socket.gethostbyname(host)
            except Exception:
                resolved_ip = host

            cmd = f"connect {resolved_ip}:{port}"
            _copy_clipboard_fast(cmd)

            cs2_running = is_cs2_running()

            if not cs2_running:
                # SCENARIO 1: CS2 is CLOSED -> Launch cleanly via steam://run/730, wait 15s for lobby, then connect
                _status("CS2 is closed. Launching CS2 cleanly via Steam...")
                _log("[CONNECT] Scenario 1: CS2 is closed. Launching CS2 cleanly via steam://run/730 (bypasses server full check)...")
                try:
                    os.startfile("steam://run/730")
                except Exception:
                    subprocess.Popen(["cmd.exe", "/c", "start", "", "steam://run/730"], creationflags=0x08000000)

                _log("[CONNECT] Waiting 15 seconds for CS2 engine to reach main lobby...")
                for sec in range(15, 0, -1):
                    _status(f"CS2 starting up... ({sec}s remaining before joining {server_name})")
                    time.sleep(1.0)

                _status(f"Connecting to {server_name} via Steam Game Server...")
                _log(f"[CONNECT] 15s startup delay complete. Connecting to {resolved_ip}:{port} via Steam Game Server...")
                success = direct_connect(resolved_ip, port)
                if success:
                    _status(f"Connected to {server_name} via Steam Game Server!")
                    _log(f"[CONNECT] Connection dispatched to Steam Game Server for {server_name} ({resolved_ip}:{port}).")
                else:
                    _status(f"Steam connect dispatch failed for {server_name}.")

            else:
                # SCENARIO 2: CS2 is OPEN -> Connect immediately via Steam Game Server (0s delay, no console injection)
                _status(f"CS2 is running. Connecting to {server_name} via Steam Game Server...")
                _log(f"[CONNECT] Scenario 2: CS2 is running. Connecting directly to {resolved_ip}:{port} via Steam Game Server...")
                success = direct_connect(resolved_ip, port)
                if success:
                    _status(f"Connected to {server_name} via Steam Game Server!")
                    _log(f"[CONNECT] Connection dispatched to Steam Game Server for {server_name} ({resolved_ip}:{port}).")
                else:
                    _status(f"Steam connection dispatch failed for {server_name}.")

            if completion_callback:
                completion_callback(True, f"Connected to {server_name}")

        except Exception as e:
            _status(f"Connect failed: {e}")
            _log(f"[ERROR] Connect workflow failed: {e}")
            if completion_callback:
                completion_callback(False, str(e))
        finally:
            time.sleep(2.0)
            set_connection_in_flight(False)

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    return thread

# ==============================================================================
# SERVER SLOT SNIPER
# Watches full servers silently via low-overhead UDP A2S_INFO.
# Supports custom slot priority thresholds (<= 61, <= 62, <= 63) for GFL and
# community servers. The instant a slot opens (players <= target), it fires ONE
# connection request, sounds an audible alert, and immediately disarms.
# ==============================================================================

class ServerSlotSniper:
    def __init__(self):
        self.target_host: Optional[str] = None
        self.target_port: int = 27015
        self.target_name: str = ""
        self.target_max_players: Optional[int] = None
        self.tier_label: str = ""
        self.is_active: bool = False
        self.has_seen_full: bool = False
        self.thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.last_status: str = "Idle"
        self.last_fired_time: float = 0.0
        self.status_callback: Optional[Callable[[str, str], None]] = None
        self.success_callback: Optional[Callable[[str, int, str, int, int], None]] = None

    def start(
        self,
        host: str,
        port: int,
        name: str,
        target_max_players: Optional[int] = None,
        tier_label: str = "",
        status_cb: Optional[Callable[[str, str], None]] = None,
        success_cb: Optional[Callable[[str, int, str, int, int], None]] = None,
        initial_is_full: bool = False
    ) -> bool:
        """Starts active silent slot sniping: monitors player count via UDP A2S at 0.25s (0 CS2 RAM stacking), connects via console the instant a slot opens."""
        self.stop()
        self.target_host = host
        self.target_port = port
        self.target_name = name
        self.target_max_players = target_max_players
        self.tier_label = tier_label
        self.is_active = True
        self.has_seen_full = initial_is_full
        self._stop_event.clear()
        self.status_callback = status_cb
        self.success_callback = success_cb
        tier_info = f" [Priority: ≤ {target_max_players}]" if target_max_players else ""
        self.last_status = f"Active: Watching {name}{tier_info} via silent UDP (0 RAM)..."

        if self.status_callback:
            self.status_callback("active", self.last_status)

        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        """Immediately stops the sniper and cancels background polling."""
        self.is_active = False
        self.has_seen_full = False
        self._stop_event.set()
        self.last_status = "Sniper Disarmed"
        if self.status_callback:
            self.status_callback("stopped", "Slot Sniper disarmed.")

    def _run_loop(self):
        # OPTION 1: True Silent Slot Sniper
        # Polls live player count at lowest & safest UDP A2S_INFO interval (0.25s) with 0 CS2 interaction.
        # Leaves CS2 completely calm (0 RAM stacking, 0 SDR session leaks, 0 clipboard spam).
        # The exact millisecond a player leaves (curr_p <= target_limit), it fires in-game console connect
        # and triggers the 10-second cooldown timer.
        poll_interval = 0.25
        check_count = 0
        consecutive_timeouts = 0

        while not self._stop_event.is_set():
            # If CS2 was closed while sniper was running, stop safely
            if not is_cs2_running():
                self.is_active = False
                self._stop_event.set()
                if self.status_callback:
                    self.status_callback("stopped", "CS2 closed — Slot Sniper stopped.")
                break

            check_count += 1

            # 1. Detect live player count at lowest & safest UDP A2S_INFO timeout (0.45s)
            info = query_server_info(self.target_host, self.target_port, timeout=0.45)
            if self._stop_event.is_set():
                break

            if info.get("online"):
                consecutive_timeouts = 0
                poll_interval = 0.25
                curr_p = info.get("curr_players", 0)
                max_p = info.get("max_players", 64)
                map_name = info.get("map", "-")

                target_limit = (
                    self.target_max_players
                    if (self.target_max_players and self.target_max_players > 0)
                    else max(0, max_p - 1)
                )
                is_full = (curr_p > target_limit)
                tier_txt = f" ({self.tier_label})" if self.tier_label else ""

                # 2. A player left! Slot is open (curr_p <= target_limit):
                # Instantly execute in-engine console connect, stop the sniper loop, and start 10s cooldown.
                if not is_full:
                    self.is_active = False
                    self._stop_event.set()
                    self.last_fired_time = time.time()

                    fast_console_connect(self.target_host, self.target_port, restore_previous_window=False)

                    if self.success_callback:
                        self.success_callback(self.target_host, self.target_port, self.target_name, curr_p, max_p)

                    if self.status_callback:
                        msg = f"Slot open ({curr_p}/{max_p} ≤ {target_limit}{tier_txt}) [Map: {map_name}]! Connected via console — 10s cooldown active."
                        self.status_callback("success", msg)
                    break

                # 3. Server is still full: stay silent (0 console spam, 0 CS2 RAM stacking)
                status_msg = (
                    f"Active: Sniping {self.target_name} | Players: {curr_p}/{max_p} "
                    f"(Target ≤ {target_limit}{tier_txt}) | Silent UDP (0 RAM) | Map: {map_name}"
                )
                if self.status_callback:
                    self.status_callback("waiting", status_msg)
            else:
                consecutive_timeouts += 1
                if consecutive_timeouts >= 3:
                    # Adaptive backoff: smoothly scale up to 1.0s to avoid flooding during network hiccups or rate limits
                    poll_interval = min(1.0, 0.25 + (consecutive_timeouts - 2) * 0.25)
                if self.status_callback:
                    self.status_callback("waiting", f"Active: Sniping {self.target_name} (Checking player count via UDP)...")

            if self._stop_event.wait(poll_interval):
                break

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_active": self.is_active,
            "target_host": self.target_host,
            "target_port": self.target_port,
            "target_name": self.target_name,
            "target_max_players": self.target_max_players,
            "last_fired_time": self.last_fired_time,
            "status_text": self.last_status
        }


# --------------------------------------------------------------------------- #
# AUDIT P2-#2: ONE definition of "players online". Kept byte-identical with
# backend/api.py:compute_player_totals (a test checks both give the same result).
#   players = HUMANS only (A2S "players" byte includes bots, so humans = players - bots)
#   counted only for servers that answered within TOTALS_MAX_AGE_S seconds
#   each (ip, port) counted once (aliases like rsscs2.kr:27015 == 14.5.33.30:27015)
# --------------------------------------------------------------------------- #
TOTALS_MAX_AGE_S = 90


def compute_player_totals(rows, now=None, max_age_s=TOTALS_MAX_AGE_S):
    """rows: iterable of dicts with keys: id, host, port, ip (optional), online,
    curr_players, bots (optional), max_players, sampled_at (unix time, optional).
    Returns dict: humans, bots, online_servers, total_servers, stale_servers,
    bots_unknown_servers, duplicates_dropped, rows (per-server table)."""
    now = time.time() if now is None else float(now)
    seen = set()
    out_rows = []
    humans = bots_total = online = stale = bots_unknown = dupes = 0
    for r in rows:
        key = (str(r.get("ip") or r.get("host") or "").lower(), int(r.get("port") or 0))
        if key in seen:
            dupes += 1
            continue
        seen.add(key)
        sampled = r.get("sampled_at")
        fresh = sampled is None or (now - float(sampled)) <= max_age_s
        is_online = bool(r.get("online")) and fresh
        curr = int(r.get("curr_players") or 0)
        b = r.get("bots")
        if b is None:
            b_val, b_known = 0, False
        else:
            b_val, b_known = max(0, int(b)), True
        h = max(0, curr - b_val) if is_online else 0
        if bool(r.get("online")) and not fresh:
            stale += 1
        if is_online:
            online += 1
            humans += h
            bots_total += b_val
            if not b_known:
                bots_unknown += 1
        out_rows.append({"id": r.get("id"), "host": r.get("host"), "port": r.get("port"),
                         "online": is_online, "humans": h, "bots": b_val if is_online else 0,
                         "bots_known": b_known, "max_players": int(r.get("max_players") or 0),
                         "stale": bool(r.get("online")) and not fresh})
    return {"humans": humans, "bots": bots_total, "online_servers": online,
            "total_servers": len(out_rows), "stale_servers": stale,
            "bots_unknown_servers": bots_unknown, "duplicates_dropped": dupes,
            "max_age_s": max_age_s, "rows": out_rows}


def totals_rows_from_api(payload, received_at=None):
    """Rows for compute_player_totals from a backend /api/servers payload. Uses the
    payload's own timestamp as the sample time (a stale cache is NOT 'online now')."""
    servers = (payload or {}).get("servers") or {}
    ts = payload.get("timestamp") if isinstance(payload, dict) else None
    rows = []
    for sid, s in servers.items():
        rows.append({"id": sid, "host": s.get("host"), "port": s.get("port"), "online": s.get("online"),
                     "curr_players": s.get("curr_players", 0), "bots": s.get("bots"),
                     "max_players": s.get("max_players", 0),
                     "sampled_at": ts if ts is not None else received_at})
    return rows


def catalog_servers():
    """The fixed catalog used for totals (same 41 entries as backend/api.py SERVERS).
    User-added custom servers are not part of the shared total."""
    out = [dict(s) for s in DEFAULT_SERVERS]
    for c in CHINA_CLUSTERS:
        out.extend(dict(s) for s in c["servers"])
    return out


def query_catalog_rows(timeout: float = 1.2, workers: int = 16):
    """Direct A2S_INFO to every catalog server (UDP, read-only). Rows for compute_player_totals."""
    from concurrent.futures import ThreadPoolExecutor

    def _one(s):
        try:
            ip = socket.gethostbyname(s["host"])
        except Exception:
            ip = s["host"]
        info = query_server_info(s["host"], s["port"], timeout=timeout)
        return {"id": s["id"], "host": s["host"], "ip": ip, "port": s["port"], "online": info.get("online"),
                "curr_players": info.get("curr_players", 0), "bots": info.get("bots") if info.get("online") else None,
                "max_players": info.get("max_players", 0), "map": info.get("map"), "sampled_at": time.time()}

    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(_one, catalog_servers()))


def format_totals(t):
    """Short display strings shared by the Dashboard card and the ZE Game Servers pills."""
    if not t or not t.get("total_servers"):
        return "— players in-game", "— servers online"
    if t.get("source") == "direct" and not t.get("online_servers"):
        # AUDIT P3: backend unreachable AND no server answered = most likely no internet.
        # Do not show "0 players / 0 online" as if the servers were empty.
        return "— players (no connection)", "server data unavailable"
    extra = " (bots unknown)" if t.get("bots_unknown_servers") else ""
    return (f"{t['humans']} players in-game{extra}",
            f"{t['online_servers']} / {t['total_servers']} servers online")


SNIPER_TRIGGERED_SECONDS = 3
SNIPER_COOLDOWN_SECONDS = 10


def sniper_status_bar(status: Dict[str, Any], now: Optional[float] = None) -> Tuple[str, str]:
    """AUDIT P2-#3: (text, state) for the bottom status bar, from the sniper's REAL state.
    state is one of: idle | armed | triggered | cooldown."""
    now = time.time() if now is None else now
    fired = float(status.get("last_fired_time") or 0)
    since = now - fired if fired else None
    if status.get("is_active"):
        name = (status.get("target_name") or "").strip() or f"{status.get('target_host')}:{status.get('target_port')}"
        if len(name) > 28:
            name = name[:27] + "…"
        lim = status.get("target_max_players")
        thr = f" (join at ≤ {lim})" if lim else " (join at first free slot)"
        return f"● SLOT SNIPER: ARMED — {name}{thr}", "armed"
    if since is not None and 0 <= since < SNIPER_TRIGGERED_SECONDS:
        return "● SLOT SNIPER: TRIGGERED — connecting", "triggered"
    if since is not None and 0 <= since < SNIPER_COOLDOWN_SECONDS:
        return f"● SLOT SNIPER: COOLDOWN ({int(SNIPER_COOLDOWN_SECONDS - since + 0.999)}s)", "cooldown"
    return "● SLOT SNIPER: IDLE", "idle"

_global_sniper = ServerSlotSniper()

def get_slot_sniper() -> ServerSlotSniper:
    return _global_sniper
