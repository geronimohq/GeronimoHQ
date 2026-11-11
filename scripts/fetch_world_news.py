"""Collects headlines for the website's World News Channel: disasters, war, science breakthroughs and aliens.

Output: public/data/world_news.json
  { "updated": <epoch>, "sources": [{"id","name","ok","count"}],
    "items": [ { "id", "title", "url", "source", "cat": "disaster|war|science|aliens", "t": <epoch>, "breaking": bool,
                 "signal": "M6.4" | "Orange alert" | "", "also": ["other outlet", ...] } ] }

This is NOT a crawl of the internet: it reads a short list of public syndication feeds (RSS and JSON that the publishers offer for
exactly this) and keeps the headline, the outlet, the time and the link. No article text and no images are copied. Nothing is verified
here; the page says so. "Breaking" is a heuristic: newer than 6 hours AND either a hard signal (USGS significant earthquake, GDACS
orange or red alert) or the same story in two different outlets.

Best effort, like the other scripts here: a feed that fails is skipped (its older items are kept while they are still fresh), a run in
which everything fails leaves the existing file alone, and the script always exits 0 so a deploy never fails because of it.
Run by hand with --dry-run to print a summary instead of writing the file.
"""
import email.utils
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "public", "data", "world_news.json")
UA = "GeronimoHQ-news-collector/1.0 (+https://geronimohq.com)"
PER_CATEGORY = 12
MAX_BREAKING = 8
BREAKING_WINDOW_S = 6 * 3600
CLUSTER_WINDOW_S = 12 * 3600
MAX_AGE_S = {"disaster": 3 * 86400, "war": 3 * 86400, "science": 7 * 86400, "aliens": 14 * 86400}
MAX_ITEMS_PER_FEED = 60
SIMILARITY = 0.45

# kind: rss (any RSS/Atom/RDF), usgs (GeoJSON), gdacs (RSS with alert levels), eonet (JSON)
# mode: how a headline is sorted into a category (see classify())
SOURCES = [
    {"id": "usgs", "name": "USGS", "kind": "usgs", "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.geojson", "hosts": ("usgs.gov",)},
    {"id": "gdacs", "name": "GDACS", "kind": "gdacs", "url": "https://www.gdacs.org/xml/rss.xml", "hosts": ("gdacs.org",)},
    {"id": "eonet", "name": "NASA EONET", "kind": "eonet", "url": "https://eonet.gsfc.nasa.gov/api/v3/events?status=open&days=3&limit=40", "hosts": ("nasa.gov",)},
    {"id": "bbc", "name": "BBC News", "kind": "rss", "mode": "world", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "hosts": ("bbc.co.uk", "bbc.com")},
    {"id": "aljazeera", "name": "Al Jazeera", "kind": "rss", "mode": "world", "url": "https://www.aljazeera.com/xml/rss/all.xml", "hosts": ("aljazeera.com",)},
    {"id": "dw", "name": "DW", "kind": "rss", "mode": "world", "url": "https://rss.dw.com/rdf/rss-en-world", "hosts": ("dw.com",)},
    {"id": "npr", "name": "NPR", "kind": "rss", "mode": "world", "url": "https://feeds.npr.org/1004/rss.xml", "hosts": ("npr.org",)},
    {"id": "france24", "name": "France 24", "kind": "rss", "mode": "world", "url": "https://www.france24.com/en/rss", "hosts": ("france24.com",)},
    {"id": "nasa", "name": "NASA", "kind": "rss", "mode": "science", "url": "https://www.nasa.gov/news-release/feed/", "hosts": ("nasa.gov",)},
    {"id": "nasasci", "name": "NASA Science", "kind": "rss", "mode": "science", "url": "https://science.nasa.gov/feed/", "hosts": ("nasa.gov",)},
    {"id": "sciencedaily", "name": "ScienceDaily", "kind": "rss", "mode": "science", "url": "https://www.sciencedaily.com/rss/top/science.xml", "hosts": ("sciencedaily.com",)},
    {"id": "seti", "name": "SETI Institute", "kind": "rss", "mode": "aliens", "url": "https://www.seti.org/rss.xml", "hosts": ("seti.org",)},
]

WAR_RE = re.compile(
    r"\b(wars?|invasion|invad\w+|air ?strikes?|missiles?|drone (?:strikes?|attacks?)|shell(?:ing|ed)|cease-?fire|truce|offensive|front ?lines?|"
    r"troops|artillery|rocket attacks?|hostages?|warships?|military strikes?|armed forces|battlefield|bombard\w+|conscription|peace talks)\b", re.I)
WAR_NOT_RE = re.compile(
    r"\b(trade|price|culture|turf|bidding|tariff|star|cold|console|streaming|browser) wars?\b|war of words|war on (?:drugs|terror|woke)|"
    r"world war|nazi|armistice|remembrance|anniversary|veterans?\b|museum|documentary|\bfilm\b|^(?:watch|listen|video|podcast)\b", re.I)
DISASTER_RE = re.compile(
    r"\b(earthquakes?|quakes?|tsunamis?|hurricanes?|typhoons?|cyclones?|tornado(?:es)?|floods?|flooding|wildfires?|bush ?fires?|eruptions?|erupts?|"
    r"volcano(?:es)?|landslides?|mudslides?|avalanches?|heat ?waves?|blizzards?|storm surge|death toll|evacuat\w+)\b", re.I)
DISASTER_NOT_RE = re.compile(r"\bflood(?:ed|s)? (?:of|with) (?:messages|calls|complaints|cash|offers)|\bevacuat\w+ (?:drill|exercise)", re.I)
SCIENCE_RE = re.compile(
    r"\b(breakthroughs?|discover(?:y|ies|ed|s)|first[- ]ever|scientists|researchers|new (?:species|planet|element|particle|treatment|vaccine|cure|material|"
    r"antibiotic|dinosaur)|telescope|webb|jwst|fusion|quantum|crispr|cure|vaccine|black holes?|dark matter|dark energy|exoplanets?|asteroids?|"
    r"comet|supernova|gravitational waves?|fossils?|record-breaking|nobel|artemis|mars|lunar|moon|proton|neutrino|genome|superconduct\w+)\b", re.I)
ALIEN_RE = re.compile(
    r"\b(aliens?|extraterrestrials?|ufos?|uaps?|unidentified (?:anomalous|aerial)|techno-?signatures?|bio-?signatures?|seti|"
    r"fermi paradox|panspermia|habitable (?:world|planet|zone)s?|signs? of (?:alien |past |ancient |microbial )?life|alien life)\b", re.I)
SETI_TOPIC_RE = re.compile(r"\b(life|habitable|exoplanets?|atmospheres?|signals?|radio|fast radio bursts?|biosignatures?|technosignatures?|extraterrestrial|alien)\b", re.I)
SETI_NOT_RE = re.compile(r"picture of the day|the search:", re.I)
ALIEN_NOT_RE = re.compile(r"illegal aliens?|alien species|invasive|alien enemies|alien registration|aliens? (?:act|tort)|resident aliens?", re.I)
STOPWORDS = frozenset("""about after again against also been before being between both could during from have into just more most other over said says
than that their them then there these they this those through under until very what when where which while will with would your the and for are but not you
has had was were its it's his her who whom how why can may might must shall off out new news live updates update latest""".split())


# ----------------------------------------------------------------------------------------------------------------------
# small helpers (pure, tested offline)
# ----------------------------------------------------------------------------------------------------------------------
def clean_text(raw, limit=220):
    text = re.sub(r"<[^>]*>", " ", html.unescape(raw or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def safe_url(url, hosts):
    """https only (http on a known host is upgraded), and the host must belong to the source: never a link the feed could redirect elsewhere."""
    url = (url or "").strip()
    if url.startswith("http://"):
        url = "https://" + url[len("http://"):]
    m = re.match(r"^https://([A-Za-z0-9.-]+)(?::\d+)?(?:/|$)", url)
    if not m or len(url) > 400 or any(c in url for c in ' "<>\\\n\r\t'):
        return ""
    host = m.group(1).lower()
    return url if any(host == h or host.endswith("." + h) for h in hosts) else ""


def parse_time(value):
    value = (value or "").strip()
    if not value:
        return 0
    try:
        return int(email.utils.parsedate_to_datetime(value).timestamp())
    except (TypeError, ValueError, IndexError):
        pass
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    except ValueError:
        return 0


def _local(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def parse_feed(xml_text):
    """-> [{"title","link","t","summary"}] from RSS 2.0, RSS 1.0 (RDF) or Atom. [] for anything unusable, including documents with a DTD or entities."""
    if not xml_text or re.search(r"<!(?:DOCTYPE|ENTITY)", xml_text, re.I):
        return []
    try:
        root = ET.fromstring(xml_text.lstrip("﻿").encode("utf-8"))
    except (ET.ParseError, ValueError):
        return []
    out = []
    for node in root.iter():
        if _local(node.tag) not in ("item", "entry"):
            continue
        fields = {}
        for child in node:
            name = _local(child.tag)
            if name == "link":
                fields.setdefault("link", (child.get("href") or child.text or "").strip())
            elif name in ("title", "description", "summary", "pubDate", "date", "published", "updated") and name not in fields:
                fields[name] = child.text or ""
        title = clean_text(fields.get("title"), 200)
        if not title or not fields.get("link"):
            continue
        out.append({
            "title": title, "link": fields["link"],
            "t": parse_time(fields.get("pubDate") or fields.get("published") or fields.get("date") or fields.get("updated")),
            "summary": clean_text(fields.get("description") or fields.get("summary"), 300),
        })
    return out[:MAX_ITEMS_PER_FEED]


def classify(title, summary, mode):
    """The categories a headline belongs to. `world` feeds (general news) only give war, disaster and alien stories; `science` feeds give science
    and alien stories; the SETI feed is about aliens by definition."""
    cats = []
    if mode == "world":
        if WAR_RE.search(title) and not WAR_NOT_RE.search(title):
            cats.append("war")
        if DISASTER_RE.search(title) and not DISASTER_NOT_RE.search(title):
            cats.append("disaster")
    text = f"{title} {summary}"
    if mode in ("world", "science") and ALIEN_RE.search(text) and not ALIEN_NOT_RE.search(text):
        cats.append("aliens")
    elif mode == "aliens" and SETI_TOPIC_RE.search(text) and not SETI_NOT_RE.search(title):
        cats.append("aliens")                                       # the SETI feed also carries newsletters and picture-of-the-day posts
    if mode == "science" and "aliens" not in cats and SCIENCE_RE.search(text):
        cats.append("science")
    if mode == "science" and "aliens" in cats and SCIENCE_RE.search(title):
        cats.append("science")
    return cats


def tokens(title):
    return frozenset(w for w in re.findall(r"[a-z0-9]{4,}", title.lower()) if w not in STOPWORDS)


def similar(a, b):
    if len(a) < 3 or len(b) < 3:
        return False
    return len(a & b) / float(len(a | b)) >= SIMILARITY


def item_id(url):
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]


def build_items(candidates, now):
    """candidates: [{"title","url","source","source_id","cat","t","signal","hard"}] -> the items written to the file.
    Same story in several outlets becomes one item (the newest) that lists the others in `also`; a story is breaking when it is fresh and has a hard
    signal or was reported by two different outlets."""
    fresh = [c for c in candidates if c["t"] and 0 <= now - c["t"] <= MAX_AGE_S[c["cat"]]]
    fresh.sort(key=lambda c: -c["t"])
    clusters = []                                                   # each: {"cat", "members": [...], "tok": [...]}
    for c in fresh:
        tok = tokens(c["title"])
        for cl in clusters:
            if cl["cat"] == c["cat"] and abs(cl["members"][0]["t"] - c["t"]) <= CLUSTER_WINDOW_S and any(similar(tok, t) for t in cl["tok"]):
                cl["members"].append(c)
                cl["tok"].append(tok)
                break
        else:
            clusters.append({"cat": c["cat"], "members": [c], "tok": [tok]})
    items = []
    for cl in clusters:
        members = cl["members"]
        lead = members[0]
        outlets = {m["source_id"] for m in members}
        hard = any(m["hard"] for m in members)
        breaking = now - lead["t"] <= BREAKING_WINDOW_S and (hard or len(outlets) >= 2)
        also = []
        for m in members[1:]:
            if m["source"] != lead["source"] and m["source"] not in also:
                also.append(m["source"])
        signal = next((m["signal"] for m in members if m["signal"]), "")
        items.append({"id": item_id(lead["url"]), "title": lead["title"], "url": lead["url"], "source": lead["source"], "cat": cl["cat"],
                      "t": lead["t"], "breaking": breaking, "signal": signal, "also": also[:3]})
    out = []
    for cat in ("disaster", "war", "science", "aliens"):
        mine = sorted((i for i in items if i["cat"] == cat), key=lambda i: (not i["breaking"], -i["t"]))
        out.extend(sorted(mine[:PER_CATEGORY], key=lambda i: -i["t"]))
    for extra in sorted((i for i in out if i["breaking"]), key=lambda i: -i["t"])[MAX_BREAKING:]:
        extra["breaking"] = False                                   # a wall of "breaking" is no longer breaking
    return out


# ----------------------------------------------------------------------------------------------------------------------
# source readers
# ----------------------------------------------------------------------------------------------------------------------
def from_usgs(text, src):
    out = []
    for f in (json.loads(text).get("features") or []):
        p = f.get("properties") or {}
        url = safe_url(p.get("url"), src["hosts"])
        mag = p.get("mag")
        if not url or mag is None or not p.get("time"):
            continue
        out.append({"title": clean_text(p.get("title") or f"M {mag} earthquake", 200), "url": url, "t": int(p["time"] / 1000), "cat": "disaster",
                    "signal": f"M{float(mag):.1f}", "hard": True})
    return out


def from_gdacs(text, src):
    out = []
    for it in parse_feed(text):
        m = re.search(r"\b(Orange|Red)\b", it["title"])
        if not m:
            continue                                                # Green alerts are routine (hundreds of wildfires); only orange/red count
        url = safe_url(it["link"], src["hosts"])
        if url:
            out.append({"title": it["title"], "url": url, "t": it["t"], "cat": "disaster", "signal": f"{m.group(1)} alert", "hard": True})
    return out


def from_eonet(text, src):
    out = []
    for ev in (json.loads(text).get("events") or []):
        cats = {c.get("id") for c in ev.get("categories") or []}
        if not cats & {"volcanoes", "severeStorms", "floods", "earthquakes", "landslides"}:
            continue
        dates = [g.get("date") for g in ev.get("geometry") or [] if g.get("date")]
        t = max((parse_time(d) for d in dates), default=0)
        url = safe_url(ev.get("link"), src["hosts"])
        if t and url and ev.get("title"):
            out.append({"title": clean_text(ev["title"], 200), "url": url, "t": t, "cat": "disaster", "signal": "", "hard": False})
    return out


def from_rss(text, src):
    out = []
    for it in parse_feed(text):
        url = safe_url(it["link"], src["hosts"])
        if not url or not it["t"]:
            continue
        for cat in classify(it["title"], it["summary"], src["mode"]):
            out.append({"title": it["title"], "url": url, "t": it["t"], "cat": cat, "signal": "", "hard": False})
    return out


READERS = {"usgs": from_usgs, "gdacs": from_gdacs, "eonet": from_eonet, "rss": from_rss}


def get(url, timeout=15, retries=2):
    """One request. On 429/503 it waits as long as the server asks (at most 30 s) and tries again: it never tries to look like a browser."""
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json, application/xml, text/xml, */*"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read(8 * 1024 * 1024).decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < retries:
                try:
                    wait = int(e.headers.get("Retry-After") or 15)
                except ValueError:
                    wait = 15
                time.sleep(max(5, min(wait, 30)))
                continue
            raise


def collect(fetch=get, sources=SOURCES, pause=1.0):
    """-> (candidates, status). `fetch` is injectable so tests never touch the network."""
    candidates, status = [], []
    for src in sources:
        try:
            rows = READERS[src["kind"]](fetch(src["url"]), src)
            for r in rows:
                r["source"], r["source_id"] = src["name"], src["id"]
            candidates.extend(rows)
            status.append({"id": src["id"], "name": src["name"], "ok": True, "count": len(rows)})
        except Exception as e:                                      # one dead or odd feed must never stop the others
            print(f"[news] {src['id']}: failed ({type(e).__name__}: {e})")
            status.append({"id": src["id"], "name": src["name"], "ok": False, "count": 0})
        time.sleep(pause)
    return candidates, status


def carry_over(previous, status, now):
    """Items of sources that failed this run, taken from the file written before, while they are still fresh enough."""
    failed = {s["name"] for s in status if not s["ok"]}
    out = []
    for it in previous:
        if it.get("source") in failed and it.get("cat") in MAX_AGE_S and 0 <= now - int(it.get("t", 0)) <= MAX_AGE_S[it["cat"]]:
            out.append({"title": it["title"], "url": it["url"], "t": int(it["t"]), "cat": it["cat"], "signal": it.get("signal", ""), "hard": bool(it.get("signal")),
                        "source": it["source"], "source_id": it["source"]})
    return out


def main(argv):
    dry = "--dry-run" in argv
    now = int(time.time())
    try:
        with open(OUT, encoding="utf-8") as f:
            previous = json.load(f).get("items") or []
    except Exception:
        previous = []
    candidates, status = collect()
    if not any(s["ok"] for s in status):
        print("[news] no source answered; the existing file is left as it is")
        return 0
    candidates += carry_over(previous, status, now)
    items = build_items(candidates, now)
    per = {c: sum(1 for i in items if i["cat"] == c) for c in MAX_AGE_S}
    print(f"[news] {len(items)} items {per}, {sum(1 for i in items if i['breaking'])} breaking; sources ok: "
          f"{sum(1 for s in status if s['ok'])}/{len(status)}")
    if dry:
        for i in items[:40]:
            print(f"  {'*' if i['breaking'] else ' '} [{i['cat']:8}] {i['source']:14} {i['title'][:90]}")
        return 0
    if not items:
        print("[news] nothing fresh; the existing file is left as it is")
        return 0
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"updated": now, "sources": status, "items": items}, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:                  # never fail a deploy over this
        print(f"[news] unexpected problem ({e}); nothing changed")
        sys.exit(0)
