"""
Fetch live A2S_INFO and A2S_PLAYER telemetry for CS2 Zombie Escape servers.
Outputs public/data/live_servers.json for web consumption.
"""

import os
import sys
import json
import time
import socket
import struct
import re
import urllib.request
import urllib.parse
import ssl
from typing import Dict, Any, List

try:
    from curl_cffi import requests as cffi_requests
except ImportError:
    cffi_requests = None

# AUDIT 1d-W3: keep certificate checks ON (the old code turned them off).
SSL_CTX = ssl.create_default_context()

ZEGRAPH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://zegraph.xyz/"
}

def fetch_gfl_intel(gfl_map: str):
    match_data = None
    musics_data = []

    # 1. Match now
    if cffi_requests:
        try:
            url = "https://zegraph.xyz/data/api/servers/65bdad6379cefd7ebcecce5c/match-now"
            r = cffi_requests.get(url, impersonate="chrome120", timeout=4.5)
            if r.status_code == 200:
                res = r.json()
                if res.get("code") == 0 and res.get("data"):
                    match_data = res.get("data")
        except Exception:
            pass
    else:
        try:
            url = "https://zegraph.xyz/data/api/servers/65bdad6379cefd7ebcecce5c/match-now"
            req = urllib.request.Request(url, headers=ZEGRAPH_HEADERS)
            with urllib.request.urlopen(req, timeout=4.0, context=SSL_CTX) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                if res.get("code") == 0 and res.get("data"):
                    match_data = res.get("data")
        except Exception:
            pass

    # 2. Musics
    # AUDIT 1d-W3: map name comes from a game server reply -> allow-list + URL-encode.
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

    return match_data, musics_data

def query_a2s_info(host: str, port: int, timeout: float = 1.4) -> Dict[str, Any]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    
    try:
        target_ip = socket.gethostbyname(host)
    except Exception as e:
        sock.close()
        return {
            "online": False,
            "status": "DNS Error",
            "map": "-",
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
            
            # Steam AppID (2 bytes)
            idx += 2
            
            # Players, Max Players, Bots (AUDIT P2-#2: players byte includes bots)
            players = data[idx]
            max_players = data[idx + 1]
            bots = data[idx + 2] if len(data) > idx + 2 else 0

            return {
                "bots": int(bots),
                "humans": max(0, int(players) - int(bots)),
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
    except Exception as e:
        return {
            "online": False,
            "status": "Offline / Query Blocked",
            "map": "-",
            "players": "-/-",
            "curr_players": 0,
            "max_players": 0,
            "ping": "Timeout",
            "error": str(e)
        }
    finally:
        sock.close()

    return {
        "online": False,
        "status": "Offline",
        "map": "-",
        "players": "-/-",
        "curr_players": 0,
        "max_players": 0,
        "ping": "Err"
    }

def query_a2s_roster_count(host: str, port: int, timeout: float = 1.5):
    """Number of entries in the A2S_PLAYER reply (humans only), or None if the server did not answer."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        target_ip = socket.gethostbyname(host)
        sock.sendto(b"\xFF\xFF\xFF\xFF\x55\xFF\xFF\xFF\xFF", (target_ip, port))
        data, addr = sock.recvfrom(4096)
        if addr[0] != target_ip:
            return None
        if len(data) >= 9 and data[4] == 0x41:
            sock.sendto(b"\xFF\xFF\xFF\xFF\x55" + data[5:9], (target_ip, port))
            data, addr = sock.recvfrom(8192)
            if addr[0] != target_ip:
                return None
        if len(data) > 5 and data[4] == 0x44:
            return int(data[5])
    except Exception:
        return None
    finally:
        sock.close()
    return None

def query_a2s_players(host: str, port: int, timeout: float = 2.0) -> List[Dict[str, Any]]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    players = []
    try:
        ip = socket.gethostbyname(host)
        sock.sendto(b"\xFF\xFF\xFF\xFF\x55\xFF\xFF\xFF\xFF", (ip, port))
        data, _ = sock.recvfrom(16384)
        if len(data) >= 9 and data[4] == 0x41:
            challenge = data[5:9]
            sock.sendto(b"\xFF\xFF\xFF\xFF\x55" + challenge, (ip, port))
            data, _ = sock.recvfrom(16384)

        if len(data) >= 6 and data[4] == 0x44:
            num = data[5]
            idx = 6
            for _ in range(num):
                if idx >= len(data):
                    break
                idx += 1
                ne = data.find(b"\x00", idx)
                if ne == -1:
                    break
                name = data[idx:ne].decode("utf-8", errors="replace").strip()
                idx = ne + 1
                if idx + 8 > len(data):
                    break
                score, duration = struct.unpack("<if", data[idx:idx+8])
                idx += 8
                if not name:
                    name = "(Connecting...)"
                
                mins, secs = divmod(int(duration), 60)
                hrs, mins = divmod(mins, 60)
                time_str = f"{hrs}h {mins:02d}m" if hrs > 0 else f"{mins}m {secs:02d}s"
                players.append({
                    "name": name,
                    "score": int(score),
                    "time": time_str,
                    "seconds": float(duration)
                })
            players.sort(key=lambda x: x["score"], reverse=True)
    except Exception:
        pass
    finally:
        sock.close()
    return players

# AUDIT P2-#2: byte-identical copy of desktop-app/server_browser.py compute_player_totals
# (test_phase2_bugs checks it). Humans only, fresh servers only, each (ip, port) once.
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


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(repo_root, "public", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "live_servers.json")

    # Master list of all servers to query
    servers = [
        # GLOBAL
        {"id": "gfl", "host": "74.91.124.21", "port": 27015, "allow_players": True},
        {"id": "possession", "host": "103.62.49.55", "port": 27015, "allow_players": True},
        {"id": "mapeadores", "host": "87.98.228.196", "port": 27040, "allow_players": True},
        {"id": "cola", "host": "178.33.160.187", "port": 27015, "allow_players": True},
        {"id": "rss", "host": "rsscs2.kr", "port": 27015, "allow_players": True},
        {"id": "net4all", "host": "46.174.53.69", "port": 27019, "allow_players": True},

        # CHINA: EXG
        {"id": "exg_8", "host": "202.189.10.89", "port": 27002, "allow_players": False},
        {"id": "exg_3", "host": "202.189.4.122", "port": 27001, "allow_players": False},
        {"id": "exg_16", "host": "202.189.10.208", "port": 27002, "allow_players": False},
        {"id": "exg_11", "host": "202.189.10.208", "port": 27001, "allow_players": False},
        {"id": "exg_pve2", "host": "202.189.5.229", "port": 27002, "allow_players": False},
        {"id": "exg_pve1", "host": "202.189.5.229", "port": 27001, "allow_players": False},
        {"id": "exg_13", "host": "202.189.5.227", "port": 27001, "allow_players": False},
        {"id": "exg_5", "host": "202.189.4.230", "port": 27001, "allow_players": False},
        {"id": "exg_12", "host": "202.189.5.225", "port": 27001, "allow_players": False},
        {"id": "exg_6", "host": "202.189.4.230", "port": 27002, "allow_players": False},
        {"id": "exg_10", "host": "202.189.10.203", "port": 27001, "allow_players": False},
        {"id": "exg_9", "host": "202.189.5.221", "port": 27001, "allow_players": False},
        {"id": "exg_17", "host": "202.189.5.225", "port": 27002, "allow_players": False},
        {"id": "exg_7", "host": "202.189.10.196", "port": 27001, "allow_players": False},
        {"id": "exg_18", "host": "202.189.5.227", "port": 27002, "allow_players": False},
        {"id": "exg_14", "host": "202.189.5.236", "port": 27001, "allow_players": False},

        # CHINA: FyS
        {"id": "fys_8", "host": "110.42.9.107", "port": 27085, "allow_players": False},
        {"id": "fys_3", "host": "110.42.9.139", "port": 27035, "allow_players": False},
        {"id": "fys_7", "host": "110.42.9.139", "port": 27075, "allow_players": False},
        {"id": "fys_1", "host": "110.42.9.155", "port": 27015, "allow_players": False},
        {"id": "fys_5", "host": "110.42.9.138", "port": 27055, "allow_players": False},
        {"id": "fys_4", "host": "110.42.9.138", "port": 27045, "allow_players": False},

        # CHINA: MoeUB
        {"id": "ub_3", "host": "110.42.9.188", "port": 27031, "allow_players": False},
        {"id": "ub_1", "host": "110.42.9.188", "port": 27011, "allow_players": False},
        {"id": "ub_2", "host": "110.42.9.188", "port": 27021, "allow_players": False},
        {"id": "ub_11", "host": "110.42.9.195", "port": 27111, "allow_players": False},
        {"id": "ub_12", "host": "110.42.9.195", "port": 27121, "allow_players": False},
        {"id": "ub_13", "host": "110.42.9.195", "port": 27131, "allow_players": False},

        # CHINA: ZombieLand
        {"id": "zl_2", "host": "110.42.9.181", "port": 27015, "allow_players": False},
        {"id": "zl_1", "host": "110.42.9.22", "port": 27016, "allow_players": False},
        {"id": "zl_3", "host": "110.42.9.181", "port": 27016, "allow_players": False},
        {"id": "zl_4", "host": "110.42.9.149", "port": 27015, "allow_players": False},
        {"id": "zl_5", "host": "110.42.9.149", "port": 27016, "allow_players": False},

        # CHINA: 93X
        {"id": "93x_1", "host": "43.142.148.163", "port": 27015, "allow_players": False},
        {"id": "93x_2", "host": "43.142.148.163", "port": 27016, "allow_players": False},
    ]

    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    existing_servers = {}
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing_servers = json.load(f).get("servers", {})
        except Exception:
            pass

    results = {}
    now_ts = int(time.time())
    print(f"Querying {len(servers)} servers via A2S UDP...")

    for s in servers:
        sid = s["id"]
        info = query_a2s_info(s["host"], s["port"], timeout=1.3)
        # Some servers (Net4All, FYS) report bots=0 but count bots in "players"; A2S_PLAYER lists humans only.
        if info.get("online") and info.get("curr_players", 0) > 0 and info.get("bots", 0) == 0:
            _rc = query_a2s_roster_count(s["host"], s["port"])
            if _rc is not None and _rc < info["curr_players"]:
                info["bots"] = info["curr_players"] - _rc
                info["humans"] = _rc
        player_list = []
        if s["allow_players"] and info.get("online"):
            player_list = query_a2s_players(s["host"], s["port"], timeout=2.8)
            if not player_list:
                time.sleep(0.2)
                player_list = query_a2s_players(s["host"], s["port"], timeout=2.8)

        current_map = info.get("map", "-")
        prev_info = existing_servers.get(sid, {})
        prev_map = prev_info.get("map")
        prev_start = prev_info.get("map_start_time")

        # Derive actual map duration from players in the server
        max_player_dur = 0
        if player_list:
            valid_durs = [p.get("seconds", 0) for p in player_list if p.get("seconds", 0) > 0]
            if valid_durs:
                max_player_dur = max(valid_durs)

        if current_map and current_map != "-" and current_map == prev_map and prev_start:
            if max_player_dur > 0 and abs((now_ts - prev_start) - max_player_dur) > 30:
                map_start_time = now_ts - max_player_dur
            else:
                map_start_time = prev_start
        else:
            if max_player_dur > 0:
                map_start_time = now_ts - max_player_dur
            else:
                map_start_time = now_ts

        results[sid] = {
            "online": info.get("online", False),
            "status": info.get("status", "Offline"),
            "server_name": info.get("name", ""),
            "map": current_map,
            "players": info.get("players", "-/-"),
            "curr_players": info.get("curr_players", 0),
            "bots": info.get("bots") if info.get("online") else None,
            "humans": info.get("humans", 0),
            "host": s["host"],
            "port": s["port"],
            "max_players": info.get("max_players", 0),
            "ping": info.get("ping", "N/A"),
            "rtt": info.get("rtt", 0),
            "players_list": player_list,
            "has_player_roster": s["allow_players"] and bool(player_list),
            "map_start_time": map_start_time
        }
        status_sym = "✓" if info.get("online") else "✗"
        print(f" {status_sym} [{sid}] {s['host']}:{s['port']} -> Map: {info.get('map')} | Players: {info.get('players')}")

    gfl_map = results.get("gfl", {}).get("map", "")
    match_now, map_musics = fetch_gfl_intel(gfl_map)

    _now = time.time()
    _totals = compute_player_totals(
        [{"id": k, "host": v["host"], "port": v["port"], "online": v["online"], "curr_players": v["curr_players"],
          "bots": v.get("bots"), "max_players": v["max_players"], "sampled_at": _now} for k, v in results.items()],
        now=_now)
    _totals.pop("rows", None)

    payload = {
        "timestamp": int(time.time()),
        "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_servers": len(servers),
        "online_servers": _totals["online_servers"],
        "totals": _totals,  # AUDIT P2-#2: same rule as backend /api/servers
        "catalog_targets": sorted(list(set([f"{s['host']}:{s['port']}" for s in servers] + ["rsscs2.kr:27015"]))),
        "gfl_match_now": match_now,
        "gfl_map_musics": map_musics,
        "servers": results
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"\nSaved live telemetry to {output_file} successfully.")

if __name__ == "__main__":
    main()
