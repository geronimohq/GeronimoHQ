"""
GeronimoHQ - CS2 Zombie Escape Live Telemetry Relay API
High-performance async A2S query microservice for real-time web telemetry.
Deployable on Render, Railway, or Fly.io (Free Tier).
"""

import os
import time
import socket
import struct
import urllib.request
import json
import re
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GeronimoHQ CS2 Telemetry Relay", version="1.0.0")

# Enable CORS for geronimohq.com and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVERS = [
    # GLOBAL
    {"id": "gfl", "name": "GFL Clan Zombie Escape 24/7", "host": "74.91.124.21", "port": 27015, "allow_players": True},
    {"id": "possession", "name": "Possession Zombie Escape (PSE)", "host": "103.62.49.55", "port": 27015, "allow_players": True},
    {"id": "mapeadores", "name": "Mapeadores Zombie Escape", "host": "87.98.228.196", "port": 27040, "allow_players": True},
    {"id": "cola", "name": "cOLa-TeaM Zombie Escape", "host": "178.33.160.187", "port": 27015, "allow_players": True},
    {"id": "rss", "name": "RSS Zombie Escape", "host": "rsscs2.kr", "port": 27015, "allow_players": True},
    {"id": "net4all", "name": "Net4All.ru Zombie Escape", "host": "46.174.53.69", "port": 27019, "allow_players": True},

    # CHINA: EXG
    {"id": "exg_8", "name": "EXG ZE 装备 #8", "host": "202.189.10.89", "port": 27002, "allow_players": False},
    {"id": "exg_3", "name": "EXG ZE 装备 #3", "host": "202.189.4.122", "port": 27001, "allow_players": False},
    {"id": "exg_16", "name": "EXG ZE 装备 #16", "host": "202.189.10.208", "port": 27002, "allow_players": False},
    {"id": "exg_11", "name": "EXG ZE 装备 #11", "host": "202.189.10.208", "port": 27001, "allow_players": False},
    {"id": "exg_pve2", "name": "EXG PVE 模式 #2", "host": "202.189.5.229", "port": 27002, "allow_players": False},
    {"id": "exg_pve1", "name": "EXG PVE 模式 #1", "host": "202.189.5.229", "port": 27001, "allow_players": False},
    {"id": "exg_13", "name": "EXG ZE 装备 #13", "host": "202.189.5.227", "port": 27001, "allow_players": False},
    {"id": "exg_5", "name": "EXG ZE #5", "host": "202.189.4.230", "port": 27001, "allow_players": False},
    {"id": "exg_12", "name": "EXG ZE 装备 #12", "host": "202.189.5.225", "port": 27001, "allow_players": False},
    {"id": "exg_6", "name": "EXG ZE #6", "host": "202.189.4.230", "port": 27002, "allow_players": False},
    {"id": "exg_10", "name": "EXG ZE 装备 #10", "host": "202.189.10.203", "port": 27001, "allow_players": False},
    {"id": "exg_9", "name": "EXG ZE 装备 #9", "host": "202.189.5.221", "port": 27001, "allow_players": False},
    {"id": "exg_17", "name": "EXG ZE 装备 #17", "host": "202.189.5.225", "port": 27002, "allow_players": False},
    {"id": "exg_7", "name": "EXG ZE 装备 #7", "host": "202.189.10.196", "port": 27001, "allow_players": False},
    {"id": "exg_18", "name": "EXG ZE 装备 #18", "host": "202.189.5.227", "port": 27002, "allow_players": False},
    {"id": "exg_14", "name": "EXG 娱乐图服 #14", "host": "202.189.5.236", "port": 27001, "allow_players": False},

    # CHINA: FyS
    {"id": "fys_8", "name": "风云社 CS2 僵尸逃跑 #08", "host": "110.42.9.107", "port": 27085, "allow_players": False},
    {"id": "fys_3", "name": "风云社 CS2 僵尸逃跑 #03", "host": "110.42.9.139", "port": 27035, "allow_players": False},
    {"id": "fys_7", "name": "风云社 CS2 僵尸逃跑 #07", "host": "110.42.9.139", "port": 27075, "allow_players": False},
    {"id": "fys_1", "name": "风云社 CS2 僵尸逃跑 #01", "host": "110.42.9.155", "port": 27015, "allow_players": False},
    {"id": "fys_5", "name": "风云社 CS2 僵尸逃跑 #05", "host": "110.42.9.138", "port": 27055, "allow_players": False},
    {"id": "fys_4", "name": "风云社 CS2 僵尸逃跑 #04", "host": "110.42.9.138", "port": 27045, "allow_players": False},

    # CHINA: UB
    {"id": "ub_3", "name": "UB社区 CS2 僵尸逃跑 #03", "host": "110.42.9.188", "port": 27031, "allow_players": False},
    {"id": "ub_1", "name": "UB社区 CS2 僵尸逃跑 #01", "host": "110.42.9.188", "port": 27011, "allow_players": False},
    {"id": "ub_2", "name": "UB社区 CS2 僵尸逃跑 #02", "host": "110.42.9.188", "port": 27021, "allow_players": False},
    {"id": "ub_11", "name": "UB社区 CS2 僵尸逃跑 #11", "host": "110.42.9.195", "port": 27111, "allow_players": False},
    {"id": "ub_12", "name": "UB社区 CS2 僵尸逃跑 #12", "host": "110.42.9.195", "port": 27121, "allow_players": False},
    {"id": "ub_13", "name": "UB社区 CS2 僵尸逃跑 #13", "host": "110.42.9.195", "port": 27131, "allow_players": False},

    # CHINA: ZL
    {"id": "zl_2", "name": "僵尸乐园 CS2 ZE #2", "host": "110.42.9.181", "port": 27015, "allow_players": False},
    {"id": "zl_1", "name": "僵尸乐园 CS2 ZE #1", "host": "110.42.9.22", "port": 27016, "allow_players": False},
    {"id": "zl_3", "name": "僵尸乐园 CS2 ZE #3", "host": "110.42.9.181", "port": 27016, "allow_players": False},
    {"id": "zl_4", "name": "僵尸乐园 CS2 ZE #4", "host": "110.42.9.149", "port": 27015, "allow_players": False},
    {"id": "zl_5", "name": "僵尸乐园 CS2 ZE #5", "host": "110.42.9.149", "port": 27016, "allow_players": False},

    # CHINA: 93X
    {"id": "93x_1", "name": "93X 社区 CS2 ZE #1", "host": "43.142.148.163", "port": 27015, "allow_players": False},
    {"id": "93x_2", "name": "93X 社区 CS2 ZE #2", "host": "43.142.148.163", "port": 27016, "allow_players": False},
]

# In-memory fast cache (3.5s TTL)
CACHE = {
    "timestamp": 0,
    "data": None
}
MAP_START_TIMES: Dict[str, Dict[str, Any]] = {}
THREAD_POOL = ThreadPoolExecutor(max_workers=24)

def query_a2s_info(host: str, port: int, timeout: float = 1.2) -> Dict[str, Any]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        target_ip = socket.gethostbyname(host)
        query = b"\xFF\xFF\xFF\xFF\x54Source Engine Query\x00"
        t0 = time.time()
        sock.sendto(query, (target_ip, port))
        data, _ = sock.recvfrom(4096)
        rtt = int((time.time() - t0) * 1000)

        # Challenge
        if len(data) >= 5 and data[4] == 0x41:
            challenge = data[5:9]
            sock.sendto(query + challenge, (target_ip, port))
            data, _ = sock.recvfrom(4096)
            rtt = int((time.time() - t0) * 1000)

        if len(data) > 5 and data[4] == 0x49:
            idx = 6
            name_end = data.find(b"\x00", idx)
            name = data[idx:name_end].decode("utf-8", errors="replace")
            idx = name_end + 1
            map_end = data.find(b"\x00", idx)
            map_name = data[idx:map_end].decode("utf-8", errors="replace")
            idx = map_end + 1
            folder_end = data.find(b"\x00", idx)
            idx = folder_end + 1
            game_end = data.find(b"\x00", idx)
            idx = game_end + 1
            idx += 2
            players = data[idx]
            max_players = data[idx + 1]
            return {
                "online": True,
                "status": "Online",
                "name": name,
                "map": map_name,
                "players": f"{players}/{max_players}",
                "curr_players": int(players),
                "max_players": int(max_players),
                "ping": f"{rtt} ms",
                "rtt": rtt
            }
    except Exception:
        pass
    finally:
        sock.close()

    return {
        "online": False,
        "status": "Offline",
        "map": "-",
        "players": "-/-",
        "curr_players": 0,
        "max_players": 0,
        "ping": "N/A",
        "rtt": 0
    }

def query_a2s_players(host: str, port: int, timeout: float = 1.8) -> List[Dict[str, Any]]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    players = []
    try:
        target_ip = socket.gethostbyname(host)
        challenge_query = b"\xFF\xFF\xFF\xFF\x55\xFF\xFF\xFF\xFF"
        sock.sendto(challenge_query, (target_ip, port))
        data, _ = sock.recvfrom(4096)
        if len(data) >= 9 and data[4] == 0x41:
            challenge = data[5:9]
            sock.sendto(b"\xFF\xFF\xFF\xFF\x55" + challenge, (target_ip, port))
            data, _ = sock.recvfrom(8192)

        if len(data) > 5 and data[4] == 0x44:
            count = data[5]
            idx = 6
            for _ in range(count):
                if idx >= len(data):
                    break
                idx += 1
                name_end = data.find(b"\x00", idx)
                if name_end == -1:
                    break
                pname = data[idx:name_end].decode("utf-8", errors="replace").strip()
                idx = name_end + 1
                if idx + 8 > len(data):
                    break
                score = struct.unpack("<i", data[idx:idx+4])[0]
                idx += 4
                duration = struct.unpack("<f", data[idx:idx+4])[0]
                idx += 4
                if pname:
                    mins = int(duration // 60)
                    secs = int(duration % 60)
                    players.append({
                        "name": pname,
                        "score": int(score),
                        "time": f"{mins:02d}:{secs:02d}",
                        "seconds": float(duration)
                    })
            players.sort(key=lambda x: x["score"], reverse=True)
    except Exception:
        pass
    finally:
        sock.close()
    return players

def fetch_single_server(s: Dict[str, Any]) -> Dict[str, Any]:
    sid = s["id"]
    info = query_a2s_info(s["host"], s["port"])
    player_list = []
    if s["allow_players"] and info["online"]:
        player_list = query_a2s_players(s["host"], s["port"])

    now_ts = int(time.time())
    current_map = info["map"]

    # Calculate actual map duration from players in the server
    # In Source/CS2, client connection duration resets on map change.
    # Therefore, the maximum player duration is the exact time spent on the map!
    max_player_dur = 0
    if player_list:
        valid_durs = [int(p.get("seconds", 0)) for p in player_list if p.get("seconds", 0) > 0]
        if valid_durs:
            max_player_dur = max(valid_durs)

    prev_map_data = MAP_START_TIMES.get(sid, {})
    if current_map and current_map != "-" and current_map == prev_map_data.get("map"):
        recorded_start = int(prev_map_data.get("start", now_ts))
        # If player durations show map has been running longer/differently by > 30s, synchronize to real player duration
        if max_player_dur > 0 and abs((now_ts - recorded_start) - max_player_dur) > 30:
            map_start = int(now_ts - max_player_dur)
            MAP_START_TIMES[sid]["start"] = map_start
        else:
            map_start = recorded_start
    else:
        # Map changed or initial discovery
        if max_player_dur > 0:
            map_start = int(now_ts - max_player_dur)
        else:
            map_start = int(now_ts)
        MAP_START_TIMES[sid] = {"map": current_map, "start": map_start}

    return {
        "id": sid,
        "host": s["host"],
        "port": s["port"],
        "online": info["online"],
        "status": info["status"],
        "server_name": info.get("name", s["name"]),
        "map": current_map,
        "players": info["players"],
        "curr_players": info["curr_players"],
        "max_players": info["max_players"],
        "ping": info["ping"],
        "rtt": info["rtt"],
        "players_list": player_list,
        "has_player_roster": bool(player_list),
        "map_start_time": int(map_start)
    }

STEAM_PROFILE_CACHE = {"timestamp": 0, "data": None}

def query_steam_profile_cached():
    now = time.time()
    if STEAM_PROFILE_CACHE["data"] and (now - STEAM_PROFILE_CACHE["timestamp"] < 30):
        return STEAM_PROFILE_CACHE["data"]

    try:
        url = "https://steamcommunity.com/profiles/76561198143793864/"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        html = urllib.request.urlopen(req, timeout=2.5).read().decode("utf-8", errors="ignore")

        in_game_header = re.search(r'profile_in_game_header.*?>(.*?)<', html, re.DOTALL)
        in_game_name = re.search(r'profile_in_game_name.*?>(.*?)<', html, re.DOTALL)

        header_text = in_game_header.group(1).strip() if in_game_header else ""
        game_text = in_game_name.group(1).strip() if in_game_name else ""

        is_in_game = "In-Game" in header_text or bool(game_text)
        is_cs2 = "Counter-Strike 2" in game_text or ("Counter-Strike" in game_text)
        is_online = "Online" in header_text or is_in_game

        res = {
            "is_in_game": is_in_game,
            "is_cs2": is_cs2,
            "game_text": game_text,
            "is_online": is_online
        }
        STEAM_PROFILE_CACHE["data"] = res
        STEAM_PROFILE_CACHE["timestamp"] = now
        return res
    except Exception:
        return STEAM_PROFILE_CACHE.get("data") or {
            "is_in_game": False,
            "is_cs2": False,
            "game_text": "",
            "is_online": True
        }

def get_geronimo_steam_status(server_results: Dict[str, Any]) -> Dict[str, Any]:
    # 1. Check if Geronimo is directly in any monitored server's active player list
    for sid, sdata in server_results.items():
        plist = sdata.get("players_list", [])
        for p in plist:
            pname = p.get("name", "").strip().lower()
            if "geronimo" in pname:
                return {
                    "online": True,
                    "in_game": True,
                    "state": "in_server", # "in_server" | "main_menu" | "other_game" | "online" | "offline"
                    "game": "Counter-Strike 2",
                    "server_id": sid,
                    "server_name": sdata.get("server_name", "Zombie Escape Server"),
                    "map": sdata.get("map", "-"),
                    "players": sdata.get("players", "-/-"),
                    "connect_url": f"steam://connect/{sdata.get('host', '')}:{sdata.get('port', '')}",
                    "player_duration": int(p.get("seconds", 0))
                }

    # 2. Check Steam profile status
    st = query_steam_profile_cached()

    if st.get("is_in_game") and st.get("is_cs2"):
        return {
            "online": True,
            "in_game": True,
            "state": "main_menu",
            "game": "Counter-Strike 2",
            "server_id": None,
            "server_name": "In Main Menu",
            "map": "In Main Menu",
            "players": "Solo / In Lobby",
            "connect_url": None,
            "player_duration": 0
        }
    elif st.get("is_in_game"):
        game_title = st.get("game_text") or "Playing on Steam"
        return {
            "online": True,
            "in_game": True,
            "state": "other_game",
            "game": game_title,
            "server_id": None,
            "server_name": None,
            "map": "Playing on Steam",
            "players": "In-Game",
            "connect_url": None,
            "player_duration": 0
        }
    else:
        is_on = st.get("is_online", True)
        return {
            "online": is_on,
            "in_game": False,
            "state": "online" if is_on else "offline",
            "game": "Steam Online",
            "server_id": None,
            "server_name": None,
            "map": "Status: Online",
            "players": "Chilling",
            "connect_url": None,
            "player_duration": 0
        }

import ssl

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

try:
    from curl_cffi import requests as cffi_requests
except ImportError:
    cffi_requests = None

ZEGRAPH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://zegraph.xyz/",
    "Origin": "https://zegraph.xyz"
}

GFL_INTEL_CACHE = {"timestamp": 0, "match": None, "musics": []}

def fetch_gfl_intel(gfl_map: str):
    now = time.time()
    # Cache for 4 seconds
    if GFL_INTEL_CACHE.get("match") is not None and (now - GFL_INTEL_CACHE.get("timestamp", 0) < 4.0):
        return GFL_INTEL_CACHE["match"], GFL_INTEL_CACHE["musics"]

    # Retain existing match data as fallback
    match_data = GFL_INTEL_CACHE.get("match")
    musics_data = GFL_INTEL_CACHE.get("musics", [])

    # 1. Match now (curl_cffi impersonating chrome to bypass Cloudflare TLS checks)
    if cffi_requests:
        try:
            url = "https://zegraph.xyz/data/api/servers/65bdad6379cefd7ebcecce5c/match-now"
            r = cffi_requests.get(url, impersonate="chrome120", timeout=4.5)
            if r.status_code == 200:
                res = r.json()
                if res.get("code") == 0 and res.get("data"):
                    match_data = res.get("data")
        except Exception as e:
            print(f"[CFFI_MATCH_ERROR] {e}")
    else:
        try:
            url = "https://zegraph.xyz/data/api/servers/65bdad6379cefd7ebcecce5c/match-now"
            req = urllib.request.Request(url, headers=ZEGRAPH_HEADERS)
            with urllib.request.urlopen(req, timeout=4.0, context=SSL_CTX) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                if res.get("code") == 0 and res.get("data"):
                    match_data = res.get("data")
        except Exception as e:
            print(f"[ZEGRAPH_MATCH_ERROR] {e}")

    # 2. Musics for current active map
    clean_map = gfl_map.strip() if gfl_map else ""
    if clean_map and clean_map != "-":
        if cffi_requests:
            try:
                murl = f"https://zegraph.xyz/data/api/servers/65bdad6379cefd7ebcecce5c/maps/{clean_map}/musics"
                mr = cffi_requests.get(murl, impersonate="chrome120", timeout=4.5)
                if mr.status_code == 200:
                    mres = mr.json()
                    if mres.get("code") == 0:
                        musics_data = mres.get("data", [])
            except Exception:
                musics_data = []
        else:
            try:
                murl = f"https://zegraph.xyz/data/api/servers/65bdad6379cefd7ebcecce5c/maps/{clean_map}/musics"
                req2 = urllib.request.Request(murl, headers=ZEGRAPH_HEADERS)
                with urllib.request.urlopen(req2, timeout=4.0, context=SSL_CTX) as resp2:
                    mres = json.loads(resp2.read().decode("utf-8"))
                    if mres.get("code") == 0:
                        musics_data = mres.get("data", [])
            except Exception:
                musics_data = []

    GFL_INTEL_CACHE["match"] = match_data
    GFL_INTEL_CACHE["musics"] = musics_data
    GFL_INTEL_CACHE["timestamp"] = now
    return match_data, musics_data

def fetch_all_telemetry() -> Dict[str, Any]:
    futures = [THREAD_POOL.submit(fetch_single_server, s) for s in SERVERS]
    server_results = {}
    for f in futures:
        try:
            res = f.result()
            server_results[res["id"]] = res
        except Exception:
            pass

    geronimo_status = get_geronimo_steam_status(server_results)
    gfl_map = server_results.get("gfl", {}).get("map", "")
    match_now, map_musics = fetch_gfl_intel(gfl_map)

    return {
        "timestamp": int(time.time()),
        "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_servers": len(SERVERS),
        "online_servers": sum(1 for r in server_results.values() if r["online"]),
        "geronimo_presence": geronimo_status,
        "gfl_match_now": match_now,
        "gfl_map_musics": map_musics,
        "servers": server_results
    }

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "GeronimoHQ CS2 Telemetry Relay",
        "target": "https://geronimohq.com",
        "uptime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

@app.get("/api/servers")
def get_servers():
    now = time.time()
    # Return from fast in-memory cache if younger than 3.5 seconds
    if CACHE["data"] and (now - CACHE["timestamp"] < 3.5):
        return CACHE["data"]

    fresh_data = fetch_all_telemetry()
    CACHE["data"] = fresh_data
    CACHE["timestamp"] = now
    return fresh_data



@app.get("/api/servers/{server_id}")
def get_server_detail(server_id: str):
    target = next((s for s in SERVERS if s["id"] == server_id), None)
    if not target:
        return {"error": "Server not found"}
    return fetch_single_server(target)
