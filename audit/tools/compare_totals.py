"""AUDIT P2-#2 evidence: compare player/server totals, all sources in the same minute.

Sources:
  A. direct A2S_INFO to each of the 41 catalog servers (+ the rsscs2.kr alias of RSS)
  B. ONE request to the live backend /api/servers (counts toward the 30-request budget)
Old rules (before the fix):
  app      : fixed text "646 players" / "34 / 41" (never computed)
  website  : sum of the `players` field (includes bots) over servers with online=true,
             no freshness check, "?? 33" when missing
New rule: server_browser.compute_player_totals (humans only, fresh only, each ip:port once)

Run:  python audit/tools/compare_totals.py  > audit/evidence_phase2_totals.md
"""
import os
import sys
import json
import time
import socket
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "desktop-app"))
import server_browser as sb  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main():
    t0 = time.time()
    direct = sb.query_catalog_rows(timeout=1.5)
    alias = sb.query_server_info("rsscs2.kr", 27015, timeout=1.5)
    try:
        alias_ip = socket.gethostbyname("rsscs2.kr")
    except Exception:
        alias_ip = "?"
    t_direct = time.time()
    backend = None
    try:
        req = urllib.request.Request(sb.BACKEND_SERVERS_URL, headers={"User-Agent": "GeronimoHQ-audit/1"})
        with urllib.request.urlopen(req, timeout=25) as r:
            backend = json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:
        backend_err = str(e)
    t_backend = time.time()

    print("# Phase 2 bug #2 - player and server totals, same minute\n")
    print(f"Run: {time.strftime('%Y-%m-%d %H:%M:%S %z')} · direct A2S finished +{t_direct - t0:.1f}s · "
          f"backend answered +{t_backend - t0:.1f}s · backend requests used: 1\n")
    print(f"Alias check: `rsscs2.kr` resolves to `{alias_ip}` (catalog RSS entry is `14.5.33.30:27015`); "
          f"alias query online={alias.get('online')} players={alias.get('players')} bots={alias.get('bots')}\n")

    bmap = (backend or {}).get("servers", {}) if backend else {}
    print("## Per server\n")
    print("| id | host:port | direct online | direct players (incl. bots) | direct bots | direct humans | backend online | backend players | backend bots field |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in direct:
        b = bmap.get(r["id"], {})
        hum = max(0, (r["curr_players"] or 0) - (r["bots"] or 0)) if r["online"] else 0
        print(f"| {r['id']} | {r['host']}:{r['port']} | {'yes' if r['online'] else 'no'} | {r['curr_players'] if r['online'] else '-'} | "
              f"{r['bots'] if r['online'] else '-'} | {hum if r['online'] else '-'} | "
              f"{'yes' if b.get('online') else ('no' if b else 'n/a')} | {b.get('curr_players', '-') if b.get('online') else '-'} | "
              f"{b.get('bots', 'absent') if b else 'n/a'} |")

    print("\n## Totals\n")
    print("| Source / rule | players shown | servers online |")
    print("|---|---|---|")
    print("| BEFORE app Dashboard + ZE Game Servers (hard-coded text) | 646 | 34 / 41 |")
    if backend:
        old_web = sum(int(str(s.get('players', '0/0')).split('/')[0] or 0) for s in bmap.values() if s.get('online'))
        print(f"| BEFORE website (sum of `players` incl. bots, live backend) | {old_web} | {backend.get('online_servers')} / {len(bmap)} |")
        nt = sb.compute_player_totals(sb.totals_rows_from_api(backend), now=time.time())
        flag = f" (bots unknown on {nt['bots_unknown_servers']} servers: live backend is the pre-audit code)" if nt["bots_unknown_servers"] else ""
        print(f"| AFTER shared rule on live backend data | {nt['humans']}{flag} | {nt['online_servers']} / {nt['total_servers']} |")
    else:
        print(f"| live backend | not reachable: {backend_err} | - |")
    dt = sb.compute_player_totals(direct, now=time.time())
    print(f"| AFTER shared rule on direct A2S (humans; bots = {dt['bots']}) | {dt['humans']} | {dt['online_servers']} / {dt['total_servers']} |")
    raw = sum(r['curr_players'] for r in direct if r['online'])
    print(f"| direct A2S, players incl. bots (for comparison) | {raw} | - |")
    with_alias = sb.compute_player_totals(direct + [{"id": "rss_alias", "host": "rsscs2.kr", "ip": alias_ip, "port": 27015,
                                                     "online": alias.get('online'), "curr_players": alias.get('curr_players', 0),
                                                     "bots": alias.get('bots'), "max_players": alias.get('max_players', 0),
                                                     "sampled_at": time.time()}], now=time.time())
    print(f"| shared rule, catalog + rsscs2.kr alias added (double-count check) | {with_alias['humans']} (duplicates dropped: {with_alias['duplicates_dropped']}) | {with_alias['online_servers']} / {with_alias['total_servers']} |")


if __name__ == "__main__":
    main()
