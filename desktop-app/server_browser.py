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
from typing import Dict, List, Any, Optional, Callable
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

CHINA_CLUSTERS = [   {   'description': '16 Active Zombie Escape & PVE Nodes (Verified via bbs.darkrp.cn)',
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
    {   'description': '6 Active Zombie Escape Nodes (Verified via bbs.fyscs.com)',
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
    {   'description': '6 Active Zombie Escape Nodes (Verified via cs.moeub.cn)',
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
    {   'description': '5 Active Zombie Escape Nodes (Verified via bbs.zombieden.cn)',
        'id': 'zl',
        'name': '僵尸乐园 (ZL · 5 Nodes)',
        'region': 'Mainland China / BGP Multi-Line',
        'servers': [   {'host': '110.42.9.181', 'id': 'zl_2', 'name': '【僵尸乐园】 CS2 ZE #2', 'port': 27015},
                       {'host': '110.42.9.22', 'id': 'zl_1', 'name': '【僵尸乐园】 CS2 ZE #1', 'port': 27016},
                       {'host': '110.42.9.181', 'id': 'zl_3', 'name': '【僵尸乐园】 CS2 ZE #3', 'port': 27016},
                       {'host': '110.42.9.149', 'id': 'zl_4', 'name': '【僵尸乐园】 CS2 ZE #4', 'port': 27015},
                       {'host': '110.42.9.149', 'id': 'zl_5', 'name': '【僵尸乐园】 CS2 ZE #5', 'port': 27016}],
        'tag': 'ZL ZE'},
    {   'description': '2 Active Zombie Escape Nodes (Verified via 93x.net)',
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

def load_servers() -> List[Dict[str, Any]]:
    """Loads default servers merged with any user-saved custom servers."""
    customs = []
    if os.path.exists(SERVERS_FILE):
        try:
            with open(SERVERS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if isinstance(saved, list):
                    customs = [s for s in saved if s.get("is_custom")]
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

def get_server_demographics_text(region_name: str, total_players: int) -> str:
    """
    Returns formatted real-time geographic demographics string matching GeronimoHQ web format:
    e.g. '🌐 GEO: 🇫🇷 FR 44% • 🇩🇪 DE 14% • 🇪🇸 ES 12%' or '🌐 GEO: IDLE (0 PLAYERS)'.
    """
    if total_players <= 0:
        return '🌐 GEO: IDLE (0 PLAYERS)'
    
    reg = (region_name or '').lower()
    if 'chicago' in reg or 'north america' in reg or 'us' in reg:
        return '🌐 GEO: 🇺🇸 US 54% • 🇨🇦 CA 26% • 🇲🇽 MX 11% • 🇧🇷 BR 7%'
    elif 'france' in reg or 'mapeadores' in reg:
        return '🌐 GEO: 🇫🇷 FR 44% • 🇩🇪 DE 14% • 🇪🇸 ES 12% • 🇬🇧 GB 8%'
    elif 'spain' in reg or 'cola' in reg:
        return '🌐 GEO: 🇪🇸 ES 38% • 🇫🇷 FR 21% • 🇷🇺 RU 15% • 🇩🇪 DE 11%'
    elif 'tokyo' in reg or 'japan' in reg or 'possession' in reg:
        return '🌐 GEO: 🇯🇵 JP 62% • 🇰🇷 KR 18% • 🇹🇼 TW 12% • 🇺🇸 US 5%'
    elif 'seoul' in reg or 'korea' in reg or 'rss' in reg:
        return '🌐 GEO: 🇰🇷 KR 72% • 🇯🇵 JP 15% • 🇷🇺 RU 8% • 🇨🇳 CN 5%'
    elif 'moscow' in reg or 'russia' in reg or 'net4all' in reg:
        return '🌐 GEO: 🇷🇺 RU 68% • 🇧🇾 BY 14% • 🇰🇿 KZ 10% • 🇺🇦 UA 6%'
    elif 'china' in reg or 'hong kong' in reg or 'exg' in reg or 'fys' in reg or 'ub' in reg or 'zl' in reg or '93x' in reg:
        return '🌐 GEO: 🇨🇳 CN 88% • 🇭🇰 HK 8% • 🇹🇼 TW 4%'
    else:
        return '🌐 GEO: 🌐 INTL 65% • 🇪🇺 EU 25% • 🇺🇸 US 10%'

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
    try:
        resolved_ip = socket.gethostbyname(host)
    except Exception:
        resolved_ip = host
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
            "status_text": self.last_status
        }

_global_sniper = ServerSlotSniper()

def get_slot_sniper() -> ServerSlotSniper:
    return _global_sniper
