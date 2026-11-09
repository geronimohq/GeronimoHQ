"""
GeronimoHQ - CS2 Zombie Escape Live Telemetry Relay API
High-performance async A2S query microservice for real-time web telemetry.
Deployable on Render, Railway, or Fly.io (Free Tier).
"""

import os
import hmac
import time
import socket
import struct
import threading
import urllib.request
import urllib.parse
import json
import re
from collections import deque
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ---------------------------------------------------------------------------
# Security configuration (all values come from environment variables on Render)
# ---------------------------------------------------------------------------
# GERONIMO_PRESENCE_TOKEN : shared secret the owner's desktop app sends in the
#                           X-Geronimo-Token header. If it is NOT set, presence
#                           updates are DISABLED (fail closed).
# ENABLE_API_DOCS=1       : re-enable /docs, /redoc and /openapi.json (off by default).
# TRUSTED_PROXY_HOPS      : how many proxies append to X-Forwarded-For (default 1).
# OWNER_PLAYER_NAMES      : comma list of exact in-game names that count as the owner
#                           when found in a server roster (default "geronimo").
PRESENCE_TOKEN = os.getenv("GERONIMO_PRESENCE_TOKEN", "").strip()
ENABLE_DOCS = os.getenv("ENABLE_API_DOCS", "") == "1"
try:
    TRUSTED_PROXY_HOPS = max(0, int(os.getenv("TRUSTED_PROXY_HOPS", "1")))
except ValueError:
    TRUSTED_PROXY_HOPS = 1
OWNER_PLAYER_NAMES = {n.strip().lower() for n in os.getenv("OWNER_PLAYER_NAMES", "geronimo").split(",") if n.strip()}

ALLOWED_ORIGINS = [
    "https://geronimohq.com",
    "https://www.geronimohq.com",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]
MAX_REQUEST_BYTES = 2048  # no endpoint needs a body; reject anything bigger

app = FastAPI(
    title="GeronimoHQ CS2 Telemetry Relay",
    version="1.1.0",
    docs_url="/docs" if ENABLE_DOCS else None,
    redoc_url="/redoc" if ENABLE_DOCS else None,
    openapi_url="/openapi.json" if ENABLE_DOCS else None,
)


def get_client_ip(request: Request) -> str:
    """Real client IP behind Render's proxy.

    A client can put anything in X-Forwarded-For, but each trusted proxy APPENDS the
    address it saw. So we read the entry TRUSTED_PROXY_HOPS from the right, never the
    left-most (spoofable) one. Falls back to the socket peer.
    """
    xff = request.headers.get("x-forwarded-for", "")
    parts = [p.strip() for p in xff.split(",") if p.strip()]
    if TRUSTED_PROXY_HOPS and len(parts) >= TRUSTED_PROXY_HOPS:
        return parts[-TRUSTED_PROXY_HOPS][:64]
    return (request.client.host if request.client else "unknown")[:64]


class RateLimiter:
    """Small in-memory sliding-window limiter (per key). Bounded memory."""

    def __init__(self, max_hits: int, window_s: float, max_keys: int = 5000):
        self.max_hits, self.window_s, self.max_keys = max_hits, window_s, max_keys
        self.hits: Dict[str, deque] = {}
        self.lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.time()
        with self.lock:
            if len(self.hits) > self.max_keys:  # prune idle keys
                for k in [k for k, q in self.hits.items() if not q or now - q[-1] > self.window_s]:
                    self.hits.pop(k, None)
                if len(self.hits) > self.max_keys:
                    self.hits.clear()
            q = self.hits.setdefault(key, deque())
            while q and now - q[0] > self.window_s:
                q.popleft()
            if len(q) >= self.max_hits:
                return False
            q.append(now)
            return True


# Website visitors poll /api/servers about every 5 s  -> 30/min leaves headroom.
# Owner heartbeat is about every 8 s (7.5/min)          -> 20/min.
# Per-server detail bypasses the big cache              -> 20/min.
LIMIT_SERVERS = RateLimiter(30, 60)
LIMIT_HEARTBEAT = RateLimiter(20, 60)
LIMIT_DETAIL = RateLimiter(20, 60)
LIMIT_OTHER = RateLimiter(60, 60)


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    # 1. Request size limits (declared body size, chunked bodies, long query strings)
    cl = request.headers.get("content-length")
    if (cl and (not cl.isdigit() or int(cl) > MAX_REQUEST_BYTES)) or "chunked" in request.headers.get("transfer-encoding", "").lower():
        return JSONResponse({"error": "request_too_large"}, status_code=413)
    if len(request.url.query) > 512:
        return JSONResponse({"error": "query_too_long"}, status_code=414)

    # 2. Rate limits by real client IP
    if request.method != "OPTIONS":
        ip = get_client_ip(request)
        path = request.url.path
        if path == "/api/servers":
            ok = LIMIT_SERVERS.allow(ip)
        elif path == "/api/presence/heartbeat":
            ok = LIMIT_HEARTBEAT.allow(ip)
        elif path.startswith("/api/servers/"):
            ok = LIMIT_DETAIL.allow(ip)
        else:
            ok = LIMIT_OTHER.allow(ip)
        if not ok:
            return JSONResponse({"error": "rate_limited"}, status_code=429, headers={"Retry-After": "10"})

    # 3. Never leak stack traces
    try:
        response = await call_next(request)
    except Exception:
        print("[ERROR] unhandled exception on", request.url.path)
        response = JSONResponse({"error": "internal_error"}, status_code=500)

    # 4. Security headers (JSON API: nothing should be framed, sniffed or cached by proxies)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    response.headers["Cache-Control"] = "no-store"
    return response


# CORS is added LAST so it is the outermost layer: preflights and 429/413 replies
# from the security middleware still carry the correct CORS headers.
# Exact origins only, no cookies/credentials needed by the website.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Geronimo-Token"],
    max_age=600,
)

SERVERS = [
    # GLOBAL
    {"id": "gfl", "name": "GFL Clan Zombie Escape 24/7", "host": "74.91.124.21", "port": 27015, "allow_players": True},
    {"id": "possession", "name": "Possession Zombie Escape (PSE)", "host": "103.62.49.55", "port": 27015, "allow_players": True},
    {"id": "mapeadores", "name": "Mapeadores Zombie Escape", "host": "87.98.228.196", "port": 27040, "allow_players": True},
    {"id": "cola", "name": "cOLa-TeaM Zombie Escape", "host": "178.33.160.187", "port": 27015, "allow_players": True},
    {"id": "rss", "name": "RSS Zombie Escape", "host": "14.5.33.30", "port": 27015, "allow_players": True},
    {"id": "net4all", "name": "Net4All.ru Zombie Escape", "host": "46.174.54.231", "port": 27015, "allow_players": True},

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
THREAD_POOL = ThreadPoolExecutor(max_workers=16)
REFRESH_LOCK = threading.Lock()  # only one full A2S sweep at a time (no thundering herd)

def query_a2s_info(host: str, port: int, timeout: float = 1.2) -> Dict[str, Any]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        target_ip = socket.gethostbyname(host)
        query = b"\xFF\xFF\xFF\xFF\x54Source Engine Query\x00"
        t0 = time.time()
        sock.sendto(query, (target_ip, port))
        data, addr = sock.recvfrom(4096)
        if addr[0] != target_ip:
            raise ValueError("reply from unexpected address")
        rtt = int((time.time() - t0) * 1000)

        # Challenge
        if len(data) >= 9 and data[4] == 0x41:
            challenge = data[5:9]
            sock.sendto(query + challenge, (target_ip, port))
            data, addr = sock.recvfrom(4096)
            if addr[0] != target_ip:
                raise ValueError("reply from unexpected address")
            rtt = int((time.time() - t0) * 1000)

        if len(data) > 5 and data[4] == 0x49:
            idx = 6
            name_end = data.find(b"\x00", idx)
            name = data[idx:name_end].decode("utf-8", errors="replace")[:128]
            idx = name_end + 1
            map_end = data.find(b"\x00", idx)
            map_name = data[idx:map_end].decode("utf-8", errors="replace")[:64]
            idx = map_end + 1
            folder_end = data.find(b"\x00", idx)
            idx = folder_end + 1
            game_end = data.find(b"\x00", idx)
            idx = game_end + 1
            idx += 2
            players = data[idx]
            max_players = data[idx + 1]
            bots = data[idx + 2] if len(data) > idx + 2 else 0
            humans = max(0, int(players) - int(bots))
            return {
                "online": True,
                "status": "Online",
                "name": name,
                "map": map_name,
                "players": f"{players}/{max_players}",
                "curr_players": int(players),
                "bots": int(bots),
                "humans": humans,
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
        "bots": 0,
        "humans": 0,
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
        data, addr = sock.recvfrom(4096)
        if addr[0] != target_ip:
            raise ValueError("reply from unexpected address")
        if len(data) >= 9 and data[4] == 0x41:
            challenge = data[5:9]
            sock.sendto(b"\xFF\xFF\xFF\xFF\x55" + challenge, (target_ip, port))
            data, addr = sock.recvfrom(8192)
            if addr[0] != target_ip:
                raise ValueError("reply from unexpected address")

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
        "bots": info.get("bots", 0),
        "humans": info.get("humans", info["curr_players"]),
        "max_players": info["max_players"],
        "ping": info["ping"],
        "rtt": info["rtt"],
        "players_list": player_list,
        "has_player_roster": bool(player_list),
        "map_start_time": int(map_start)
    }

# In-memory Steam profile and local desktop heartbeat cache
STEAM_PROFILE_CACHE = {"timestamp": 0, "data": None}
LOCAL_HEARTBEAT = {
    "timestamp": 0,
    "is_online": False,
    "is_cs2": False,
    "in_menu": False,
    "game": None
}

@app.get("/api/presence/heartbeat")
@app.post("/api/presence/heartbeat")
def presence_heartbeat(
    request: Request,
    is_cs2_running: bool = False,
    is_steam_running: bool = False,
    in_menu: bool = True,
    game: str = "Counter-Strike 2"
):
    """Accepts presence heartbeat ONLY from the owner's desktop app.

    - No GERONIMO_PRESENCE_TOKEN configured on the server -> 503 (fail closed).
    - Missing or wrong X-Geronimo-Token header             -> 401.
    The token value is never logged or echoed.
    """
    global LOCAL_HEARTBEAT
    if not PRESENCE_TOKEN:
        return JSONResponse({"error": "presence_updates_disabled"}, status_code=503)
    supplied = request.headers.get("x-geronimo-token", "")
    if not supplied or not hmac.compare_digest(supplied.encode("utf-8"), PRESENCE_TOKEN.encode("utf-8")):
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    if len(game) > 64 or not re.fullmatch(r"[\w \-:.'!&()]*", game):
        return JSONResponse({"error": "invalid_game"}, status_code=422)

    now = time.time()
    is_online = bool(is_cs2_running or is_steam_running)
    LOCAL_HEARTBEAT = {
        "timestamp": now,
        "is_online": is_online,
        "is_cs2": bool(is_cs2_running),
        "in_menu": bool(in_menu),
        "game": game if is_cs2_running else None
    }
    return {"status": "ok", "received": True, "is_online": is_online, "valid_seconds": 25}

def query_steam_profile_cached():
    now = time.time()
    # Cache for 10 seconds to ensure rapid updates
    if STEAM_PROFILE_CACHE["data"] and (now - STEAM_PROFILE_CACHE["timestamp"] < 10):
        return STEAM_PROFILE_CACHE["data"]

    try:
        url = "https://steamcommunity.com/profiles/76561198143793864/"
        html = ""
        # 1. Use curl_cffi impersonating modern browser to bypass Cloudflare / Akamai rate-limits & TLS blocks
        try:
            r = cffi_requests.get(url, impersonate="chrome120", timeout=3.5)
            if r.status_code == 200:
                html = r.text
        except Exception:
            pass

        if not html:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            html = urllib.request.urlopen(req, timeout=2.5).read().decode("utf-8", errors="ignore")

        # Check persona status directly in Steam Community HTML
        is_in_game = ("Currently In-Game" in html) or ('class="profile_in_game persona in-game"' in html) or ('profile_in_game persona in-game' in html)
        is_online_now = ("Currently Online" in html) or ('class="profile_in_game persona online"' in html) or ('profile_in_game persona online' in html)
        is_offline_now = ("Currently Offline" in html) or ('class="profile_in_game persona offline"' in html) or ('profile_in_game persona offline' in html)

        if is_in_game:
            is_online = True
            known = True
        elif is_online_now:
            is_online = True
            is_in_game = False
            known = True
        elif is_offline_now:
            is_online = False
            is_in_game = False
            known = True
        else:
            # Page loaded but no persona marker (Steam layout change, captcha, private
            # profile...). We genuinely do not know -> never pretend "offline".
            is_online = False
            known = False

        game_text = ""
        in_game_name = re.search(r'profile_in_game_name.*?>(.*?)<', html, re.DOTALL)
        if in_game_name:
            game_text = in_game_name.group(1).strip()
        elif is_in_game:
            if "Counter-Strike 2" in html or "Counter-Strike" in html:
                game_text = "Counter-Strike 2"

        is_cs2 = "Counter-Strike 2" in game_text or ("Counter-Strike" in game_text)

        res = {
            "is_in_game": is_in_game,
            "is_cs2": is_cs2,
            "game_text": game_text[:64],
            "is_online": is_online,
            "known": known and bool(html),
        }
        STEAM_PROFILE_CACHE["data"] = res
        STEAM_PROFILE_CACHE["timestamp"] = now
        return res
    except Exception:
        # Use the last good answer for up to 2 minutes, then admit we don't know.
        if STEAM_PROFILE_CACHE.get("data") and now - STEAM_PROFILE_CACHE["timestamp"] < 120:
            return STEAM_PROFILE_CACHE["data"]
        return {
            "is_in_game": False,
            "is_cs2": False,
            "game_text": "",
            "is_online": False,
            "known": False,
        }

def get_geronimo_steam_status(server_results: Dict[str, Any]) -> Dict[str, Any]:
    now = time.time()
    has_recent_heartbeat = LOCAL_HEARTBEAT.get("timestamp", 0) > 0 and (now - LOCAL_HEARTBEAT["timestamp"] < 25)
    # If the owner's authenticated app says CS2 is NOT running, a roster name match
    # must be someone else using the same name.
    heartbeat_denies_cs2 = has_recent_heartbeat and not LOCAL_HEARTBEAT.get("is_cs2")

    # 1. Owner's exact in-game name in a monitored server roster (A2S gives names only,
    #    not SteamIDs, so this is a best-effort match; see OWNER_PLAYER_NAMES).
    # AUDIT 1b-R5: anyone can set their in-game name to "Geronimo". Only trust a
    # roster name match when an owner-only signal also says CS2 is running:
    # the authenticated heartbeat, or the owner's public Steam profile.
    heartbeat_confirms_cs2 = has_recent_heartbeat and bool(LOCAL_HEARTBEAT.get("is_cs2"))
    roster_trusted = (not heartbeat_denies_cs2) and (
        heartbeat_confirms_cs2 or bool(query_steam_profile_cached().get("is_cs2"))
    )
    for sid, sdata in (server_results if roster_trusted else {}).items():
        plist = sdata.get("players_list", [])
        for p in plist:
            pname = p.get("name", "").strip().lower()
            if pname in OWNER_PLAYER_NAMES:
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

    # 2. Owner's desktop app heartbeat (authenticated with GERONIMO_PRESENCE_TOKEN)
    if has_recent_heartbeat and LOCAL_HEARTBEAT.get("is_cs2"):
        return {
            "online": True,
            "in_game": True,
            "state": "main_menu",
            "game": "Counter-Strike 2",
            "server_id": None,
            "server_name": "Main Menu",
            "map": "Main Menu",
            "players": "Solo",
            "connect_url": "steam://rungameid/730",
            "player_duration": 0
        }

    # 3. Check public Steam profile status (independent of the desktop app)
    st = query_steam_profile_cached()

    if st.get("is_in_game") and st.get("is_cs2"):
        return {
            "online": True,
            "in_game": True,
            "state": "main_menu",
            "game": "Counter-Strike 2",
            "server_id": None,
            "server_name": "Main Menu",
            "map": "Main Menu",
            "players": "Solo",
            "connect_url": "steam://rungameid/730",
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
            "map": game_title,
            "players": "In-Game",
            "connect_url": None,
            "player_duration": 0
        }

    # Geronimo is online on Steam if either the local desktop app detects steam.exe, OR Steam community profile indicates online
    is_steam_online = (has_recent_heartbeat and LOCAL_HEARTBEAT.get("is_online")) or st.get("is_online")

    if is_steam_online:
        return {
            "online": True,
            "in_game": False,
            "state": "online",
            "game": "Steam Community",
            "server_id": None,
            "server_name": None,
            "map": "Idle",
            "players": "N/A",
            "connect_url": None,
            "player_duration": 0
        }

    # Neither the app heartbeat nor the Steam profile gave a usable answer:
    # report "unknown" (the website shows Standby), never a fake "offline".
    if not st.get("known", True) and not has_recent_heartbeat:
        return {
            "online": False,
            "in_game": False,
            "state": "unknown",
            "game": "Unknown",
            "server_id": None,
            "server_name": None,
            "map": "Unknown",
            "players": "N/A",
            "connect_url": None,
            "player_duration": 0
        }

    # Geronimo is offline if Steam is closed and no games are running
    return {
        "online": False,
        "in_game": False,
        "state": "offline",
        "game": "Offline",
        "server_id": None,
        "server_name": None,
        "map": "Offline",
        "players": "N/A",
        "connect_url": None,
        "player_duration": 0
    }

import ssl

# AUDIT 1b-R2: certificate checks stay ON (the old code turned them off).
SSL_CTX = ssl.create_default_context()

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
    # AUDIT 1b-R3: the map name comes from a game server's reply. Only allow a
    # normal map name and URL-encode it before it goes into a URL path.
    clean_map = gfl_map.strip() if gfl_map else ""
    if not re.fullmatch(r"[A-Za-z0-9_.\-]{1,64}", clean_map):
        clean_map = ""
    clean_map = urllib.parse.quote(clean_map, safe="")
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

# --------------------------------------------------------------------------- #
# AUDIT P2-#2: ONE definition of "players online". This block is a byte-identical
# copy of desktop-app/server_browser.py (test_phase2_bugs checks it). Humans only,
# servers that answered within TOTALS_MAX_AGE_S, each (ip, port) once.
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

    sampled_at = time.time()
    totals = compute_player_totals(
        [{"id": r["id"], "host": r["host"], "port": r["port"], "online": r["online"],
          "curr_players": r["curr_players"], "bots": r.get("bots"), "max_players": r["max_players"],
          "sampled_at": sampled_at} for r in server_results.values()],
        now=sampled_at)
    totals.pop("rows", None)

    return {
        "timestamp": int(time.time()),
        "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_servers": len(SERVERS),
        "online_servers": totals["online_servers"],
        "totals": totals,  # AUDIT P2-#2: the ONE total the website and app display
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

    # AUDIT 1b-R1: REFRESH_LOCK was defined but never used. Only one request runs
    # the full A2S sweep; others wait and then reuse its fresh cache.
    with REFRESH_LOCK:
        now = time.time()
        if CACHE["data"] and (now - CACHE["timestamp"] < 3.5):
            return CACHE["data"]
        fresh_data = fetch_all_telemetry()
        CACHE["data"] = fresh_data
        CACHE["timestamp"] = time.time()
        return fresh_data



DETAIL_CACHE: Dict[str, Dict[str, Any]] = {}
DETAIL_LOCK = threading.Lock()


@app.get("/api/servers/{server_id}")
def get_server_detail(server_id: str):
    # AUDIT 1b-R4: only ids from the fixed catalog (no user host:port), 404 for
    # unknown ids, and a 5 s cache so callers cannot trigger a UDP query per request.
    if not re.fullmatch(r"[a-z0-9_]{1,32}", server_id or ""):
        return JSONResponse({"error": "server_not_found"}, status_code=404)
    target = next((s for s in SERVERS if s["id"] == server_id), None)
    if not target:
        return JSONResponse({"error": "server_not_found"}, status_code=404)
    with DETAIL_LOCK:
        hit = DETAIL_CACHE.get(server_id)
        if hit and time.time() - hit["t"] < 5.0:
            return hit["data"]
        data = fetch_single_server(target)
        DETAIL_CACHE[server_id] = {"t": time.time(), "data": data}
        return data
