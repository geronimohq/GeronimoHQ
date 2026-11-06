"""
GeronimoHQ - CS2 Zombie Escape Live Telemetry Relay API
High-performance async A2S query microservice for real-time web telemetry.
Deployable on Render, Railway, or Fly.io (Free Tier).
"""

import os
import time
import socket
import struct
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
    prev_map_data = MAP_START_TIMES.get(sid, {})
    if current_map and current_map != "-" and current_map == prev_map_data.get("map"):
        map_start = prev_map_data.get("start", now_ts)
    else:
        map_start = now_ts
        MAP_START_TIMES[sid] = {"map": current_map, "start": map_start}

    return {
        "id": sid,
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
        "map_start_time": map_start
    }

def fetch_all_telemetry() -> Dict[str, Any]:
    futures = [THREAD_POOL.submit(fetch_single_server, s) for s in SERVERS]
    server_results = {}
    for f in futures:
        try:
            res = f.result()
            server_results[res["id"]] = res
        except Exception:
            pass

    return {
        "timestamp": int(time.time()),
        "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_servers": len(SERVERS),
        "online_servers": sum(1 for r in server_results.values() if r["online"]),
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
