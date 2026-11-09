"""Low-impact live backend probe (owner-owned asset). Counts every request; hard cap 30 total
for the whole audit — this script uses at most 9. Prints status, key headers, short bodies."""
import json, time, urllib.request, urllib.error, sys
BASE = "https://geronimohq-telemetry.onrender.com"
COUNT_FILE = "audit/.backend_request_count"
try:
    used = int(open(COUNT_FILE).read())
except Exception:
    used = 0

def req(method, path, headers=None, label=""):
    global used
    if used >= 30:
        print("BUDGET EXHAUSTED"); sys.exit(1)
    used += 1
    r = urllib.request.Request(BASE + path, method=method, headers={"User-Agent": "GeronimoHQ-audit/1.0", **(headers or {})})
    t = time.time()
    try:
        resp = urllib.request.urlopen(r, timeout=60)
        code, hdrs, body = resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        code, hdrs, body = e.code, dict(e.headers), e.read()
    except Exception as e:
        print(f"#{used} {label:28s} {method} {path} -> EXC {type(e).__name__}: {e}"); return None, {}, b""
    keep = {k: v for k, v in hdrs.items() if k.lower() in ("access-control-allow-origin", "access-control-allow-credentials",
            "access-control-allow-methods", "content-type", "server", "x-frame-options", "strict-transport-security",
            "x-content-type-options", "content-security-policy", "referrer-policy", "x-render-origin-server")}
    print(f"#{used} {label:28s} {method} {path} -> {code} in {time.time()-t:.1f}s  {keep}")
    return code, hdrs, body

c, h, b = req("GET", "/", label="health")
print("   body:", b[:200])
c, h, b = req("GET", "/api/servers", label="servers (may cold start)")
if b:
    d = json.loads(b)
    print("   keys:", list(d)[:12], "| total_servers", d.get("total_servers"), "online", d.get("online_servers"))
    p = d.get("geronimo_presence", {})
    print("   presence.state:", p.get("state"), "| servers in payload:", len(d.get("servers", {})))
    json.dump(d, open("audit/evidence_api_servers_before.json", "w", encoding="utf-8"), ensure_ascii=False)
for path in ("/docs", "/openapi.json", "/redoc"):
    c, h, b = req("GET", path, label="exposure " + path)
req("OPTIONS", "/api/presence/heartbeat", {"Origin": "https://evil.example", "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "x-geronimo-token"}, label="CORS preflight evil origin")
c, h, b = req("GET", "/api/presence/heartbeat?is_cs2_running=false&is_steam_running=false&in_menu=false",
              label="UNAUTH heartbeat (all false)")
print("   body:", b[:200])
c, h, b = req("GET", "/api/servers/does-not-exist", label="unknown server id")
print("   body:", b[:200])
open(COUNT_FILE, "w").write(str(used))
print("backend requests used so far:", used)
