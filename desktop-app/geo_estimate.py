"""
Geo estimate for a ZE server: a Python port of the website's src/utils/serverDemographics.ts
(getServerDemographics, country part). Same inputs, same rules, same numbers, so the app's
GEO line matches geronimohq.com (owner request, 2026-11-10).

It is an ESTIMATE, not a measurement:
  1. player names are scanned for scripts / clan tags (Hangul -> KR, Cyrillic -> RU, [PH] -> PH ...)
  2. everyone else is spread over countries by a time-of-day activity curve per region
  3. for GFL only, the split is aligned to ZEGraph's measured continent counts
Only counts and names already published by the game servers are used; no player is shown.
"""
import math
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

COUNTRY_METAS: Dict[str, Dict[str, str]] = {
    "US": {"name": "United States", "flag": "🇺🇸", "continent": "NA"},
    "CA": {"name": "Canada", "flag": "🇨🇦", "continent": "NA"},
    "VN": {"name": "Vietnam", "flag": "🇻🇳", "continent": "ASIA"},
    "PH": {"name": "Philippines", "flag": "🇵🇭", "continent": "ASIA"},
    "JP": {"name": "Japan", "flag": "🇯🇵", "continent": "ASIA"},
    "KR": {"name": "South Korea", "flag": "🇰🇷", "continent": "ASIA"},
    "CN": {"name": "China", "flag": "🇨🇳", "continent": "ASIA"},
    "ID": {"name": "Indonesia", "flag": "🇮🇩", "continent": "ASIA"},
    "IN": {"name": "India", "flag": "🇮🇳", "continent": "ASIA"},
    "UK": {"name": "United Kingdom", "flag": "🇬🇧", "continent": "EU"},
    "FR": {"name": "France", "flag": "🇫🇷", "continent": "EU"},
    "DE": {"name": "Germany", "flag": "🇩🇪", "continent": "EU"},
    "ES": {"name": "Spain", "flag": "🇪🇸", "continent": "EU"},
    "PL": {"name": "Poland", "flag": "🇵🇱", "continent": "EU"},
    "RU": {"name": "Russia", "flag": "🇷🇺", "continent": "EU"},
    "BR": {"name": "Brazil / LatAm", "flag": "🇧🇷", "continent": "LATAM"},
    "OTHER": {"name": "Other Regions", "flag": "🌎", "continent": "OTHER"},
}

_I = re.IGNORECASE
_VN_CHARS = re.compile("[àáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]", _I)


def _tag(words: str, tags: str) -> re.Pattern:
    return re.compile(r"\b(" + words + r")\b|[\[(_](" + tags + r")[\])_]", _I)


_RULES = [
    ("VN", lambda n, l: bool(_VN_CHARS.search(n) or _tag("vn|vie|vietnam|viet", "vn|vie").search(l)
                             or re.search(r"(?:duy|huy|nguyen|tran|hoang|phan|vu|viet|banh)", l, _I))),
    ("JP", lambda n, l: bool(re.search("[぀-ヿ]", n) or _tag("jp|jpn|japan", "jp|jpn").search(l)
                             or re.search(r"(?:kakashi|riku|dojima|daishin|kuroki|kitsune)", l, _I)
                             or re.search(r"kun\b|san\b", l, _I))),
    ("KR", lambda n, l: bool(re.search("[가-힯]", n) or _tag("kr|kor|korea", "kr|kor").search(l))),
    ("CN", lambda n, l: bool(re.search("[一-鿿]", n) or _tag("cn|chn|china", "cn|chn").search(l))),
    ("PH", lambda n, l: bool(_tag("ph|phl|pinoy|pilipinas", "ph|phl").search(l) or "geronimo" in l)),
    ("ID", lambda n, l: bool(_tag("id|ina|indo|indonesia", "id|ina").search(l) or "kaleng" in l)),
    ("IN", lambda n, l: bool(_tag("in|ind|india", "in|ind").search(l) or re.search(r"(?:rajesh|darinda|singh|kumar)", l, _I))),
    ("RU", lambda n, l: bool(re.search("[Ѐ-ӿ]", n) or _tag("ru|rus|russia", "ru|rus").search(l)
                             or re.search(r"(?:alexey|vladimir)", l, _I))),
    ("BR", lambda n, l: bool(_tag("br|bra|brasil|brazil|arg|argentina|cl|latam", "br|bra|arg|cl|latam").search(l))),
    ("FR", lambda n, l: bool(_tag("fr|fra|france", "fr|fra").search(l))),
    ("DE", lambda n, l: bool(_tag("de|ger|germany", "de|ger").search(l))),
    ("UK", lambda n, l: bool(_tag("uk|gb|britain", "uk|gb").search(l))),
    ("ES", lambda n, l: bool(_tag("es|esp|spain", "es|esp").search(l))),
    ("PL", lambda n, l: bool(_tag("pl|poland", "pl|pol").search(l))),
    ("US", lambda n, l: bool(_tag("us|usa", "us|usa|na").search(l))),
    ("CA", lambda n, l: bool(_tag("ca|can|canada", "ca|can").search(l))),
]


def country_from_name(raw: str) -> Optional[str]:
    if not raw or raw == "Connecting...":
        return None
    name = raw.strip()
    lower = name.lower()
    for code, test in _RULES:
        if test(name, lower):
            return code
    return None


def _diurnal(local_hour: float) -> float:
    angle = ((local_hour - 21) * 2 * math.pi) / 24
    return 0.20 + 0.80 * ((math.cos(angle) + 1) / 2)


def _js_round(x: float) -> int:
    return int(math.floor(x + 0.5))  # Math.round


def estimate_countries(server_region: str, total_players: int, player_names: Optional[List[str]] = None,
                       continents: Optional[Dict[str, Any]] = None,
                       now: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """Returns [{"code","name","flag","percentage","count"}...] sorted by share, like the website."""
    if total_players <= 0:
        return []
    now = now or datetime.now(timezone.utc)
    utc_hour = now.hour + now.minute / 60
    na_d = _diurnal((utc_hour - 6 + 24) % 24)
    eu_d = _diurnal((utc_hour + 1) % 24)
    asia_d = _diurnal((utc_hour + 8) % 24)
    latam_d = _diurnal((utc_hour - 3 + 24) % 24)

    counts = {c: 0.0 for c in COUNTRY_METAS}
    attributed = 0
    for n in player_names or []:
        c = country_from_name(n)
        if c:
            counts[c] += 1
            attributed += 1
    unattributed = max(0, total_players - attributed)

    reg = (server_region or "").lower()
    is_na = "us" in reg or "chicago" in reg or "north america" in reg or reg == "na"
    is_eu = any(k in reg for k in ("france", "fr", "spain", "es", "eu"))
    is_asia = any(k in reg for k in ("japan", "tokyo", "jp", "korea", "kr", "china", "cn", "hong kong"))  # AUDIT: China clusters

    # Chinese community clusters (EXG, FyS ...) are 'Hong Kong / BGP Multi-Line' or 'Mainland China / BGP Multi-Line': Chinese-language communities,
    # so the estimate is mostly China. (They used to get the generic Asia split, which put Japan first on every Chinese server.)
    is_china = "bgp" in reg or "mainland" in reg or "hong kong" in reg

    if is_china:
        w = {"CN": 3.4 * asia_d, "KR": 0.12 * asia_d, "JP": 0.10 * asia_d, "VN": 0.10 * asia_d, "PH": 0.06 * asia_d, "ID": 0.04 * asia_d,
             "US": 0.10 * na_d, "UK": 0.05 * eu_d, "RU": 0.05 * eu_d, "OTHER": 0.10}
    elif is_na:
        w = {"US": 1.6 * na_d * 0.85, "CA": 1.6 * na_d * 0.15, "UK": 0.9 * eu_d * 0.22, "DE": 0.9 * eu_d * 0.20,
             "FR": 0.9 * eu_d * 0.18, "ES": 0.9 * eu_d * 0.15, "RU": 0.9 * eu_d * 0.15, "PL": 0.9 * eu_d * 0.10,
             "VN": 0.7 * asia_d * 0.22, "PH": 0.7 * asia_d * 0.22, "JP": 0.7 * asia_d * 0.16, "CN": 0.7 * asia_d * 0.14,
             "ID": 0.7 * asia_d * 0.10, "IN": 0.7 * asia_d * 0.08, "KR": 0.7 * asia_d * 0.08, "BR": 0.5 * latam_d,
             "OTHER": 0.3}
    elif is_eu:
        w = {"FR": 1.8 * eu_d * 0.30, "DE": 1.8 * eu_d * 0.22, "ES": 1.8 * eu_d * 0.18, "UK": 1.8 * eu_d * 0.15,
             "RU": 1.8 * eu_d * 0.10, "PL": 1.8 * eu_d * 0.05, "US": 0.6 * na_d * 0.85, "CA": 0.6 * na_d * 0.15,
             "BR": 0.4 * latam_d, "VN": 0.3 * asia_d, "PH": 0.3 * asia_d, "JP": 0.3 * asia_d, "OTHER": 0.25}
    elif is_asia:
        w = {"JP": 1.8 * asia_d * 0.35, "KR": 1.8 * asia_d * 0.20, "CN": 1.8 * asia_d * 0.20, "VN": 1.8 * asia_d * 0.12,
             "PH": 1.8 * asia_d * 0.10, "ID": 1.8 * asia_d * 0.08, "RU": 0.4 * eu_d, "US": 0.4 * na_d,
             "UK": 0.3 * eu_d, "OTHER": 0.2}
    else:
        w = {"RU": 1.2 * eu_d, "PL": 1.0 * eu_d, "DE": 0.8 * eu_d, "US": 0.4 * na_d, "CN": 0.4 * asia_d, "OTHER": 0.3}
    s = sum(w.values()) or 1
    for code, weight in w.items():
        counts[code] += (weight / s) * unattributed

    data = (continents or {}).get("data") if isinstance(continents, dict) and "data" in continents else continents
    conts = (data or {}).get("continents") if isinstance(data, dict) else None
    if conts:
        total_contain = (data.get("contain_countries") or sum(c.get("count", 0) for c in conts) or 1)
        target = {"ASIA": 0.0, "EU": 0.0, "NA": 0.0, "LATAM": 0.0, "OTHER": 0.0}
        for c in conts:
            pct = (c.get("count", 0) / total_contain) * 100
            nm = c.get("name")
            key = {"Asia": "ASIA", "Europe": "EU", "North America": "NA", "South America": "LATAM"}.get(nm, "OTHER")
            target[key] = (target[key] + pct) if key == "OTHER" else pct
        for cont in ("ASIA", "EU", "NA", "LATAM", "OTHER"):
            if target[cont] > 0:
                codes = [c for c in counts if COUNTRY_METAS[c]["continent"] == cont]
                cur = sum(counts[c] for c in codes)
                if cur > 0:
                    f = target[cont] / cur
                    for c in codes:
                        counts[c] *= f

    total = sum(counts.values()) or 1
    items = []
    for code, cnt in counts.items():   # dict order == website object order (stable sort ties)
        pct = _js_round((cnt / total) * 100)
        if pct > 0:
            m = COUNTRY_METAS.get(code, COUNTRY_METAS["OTHER"])
            items.append({"code": code, "name": m["name"], "flag": m["flag"], "percentage": pct,
                          "count": max(1, _js_round((pct / 100) * total_players))})
    items.sort(key=lambda it: -it["percentage"])
    return items


REGION_METAS = {"NA": ("North America", "🌎"), "EU": ("Europe", "🌍"), "ASIA": ("Asia", "🌏"),
                "LATAM": ("Latin America", "🌎"), "OTHER": ("Other Regions", "🌐")}


def estimate_regions(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Country estimate rows -> continent rows (same shape), sorted by share. Mirrors the website's Region view."""
    agg: Dict[str, Dict[str, Any]] = {}
    for it in items or []:
        cont = COUNTRY_METAS.get(it["code"], COUNTRY_METAS["OTHER"])["continent"]
        a = agg.setdefault(cont, {"percentage": 0, "count": 0})
        a["percentage"] += it["percentage"]
        a["count"] += it["count"]
    out = []
    for cont, a in agg.items():
        name, flag = REGION_METAS.get(cont, REGION_METAS["OTHER"])
        out.append({"code": cont, "name": name, "flag": flag, "percentage": a["percentage"], "count": a["count"]})
    out.sort(key=lambda r: -r["percentage"])
    return out
