import os
import sys
import time
import datetime
import urllib.request
import urllib.parse
import json

_GFL_ZEGRAPH_SERVER_ID = "65bdad6379cefd7ebcecce5c"
_cached_match_now = {}
_last_match_fetch_time = 0.0
_cached_soundtracks = {}

def query_zegraph_match_now(timeout: float = 3.5, force_refresh: bool = False):
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
    except Exception as e:
        print("Fetch error:", e)

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

def query_zegraph_soundtrack(map_name: str, timeout: float = 3.5):
    clean_map = map_name.strip().lower()
    if not clean_map or clean_map in ("-", "unknown"):
        return []

    if clean_map in _cached_soundtracks:
        return _cached_soundtracks[clean_map]

    def _fetch_for_name(target_name: str):
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

if __name__ == "__main__":
    print("Testing match-now...")
    m = query_zegraph_match_now()
    print("Match-Now Result:", m)
    assert m["success"] is True
    print(f"Humans: {m['human_score']} vs Zombies: {m['zombie_score']} | Extends: {m['extend_count']}/3")

    print("\nTesting soundtrack for ze_s_a_m...")
    songs = query_zegraph_soundtrack("ze_s_a_m")
    print(f"Tracks found: {len(songs)}")
    assert len(songs) > 0
    print("First song:", songs[0])
    print("All tests passed!")
