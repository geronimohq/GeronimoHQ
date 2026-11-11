import { useEffect, useMemo, useState } from 'react';

/**
 * World News Channel data. /data/world_news.json is written by scripts/fetch_world_news.py (headline, outlet, time and a link, taken from
 * public syndication feeds; nothing is verified here). Large earthquakes are also re-read from USGS in the browser every few minutes,
 * because that feed allows it and it is the one thing worth not waiting 30 minutes for.
 * Every string is validated and later rendered as plain text; links must be https.
 */
export type NewsCat = 'disaster' | 'war' | 'science' | 'aliens';

export interface NewsItem {
  id: string;
  title: string;
  url: string;
  source: string;
  cat: NewsCat;
  /** epoch seconds */
  t: number;
  breaking: boolean;
  /** "M6.4", "Orange alert" or "" */
  signal: string;
  /** other outlets that reported the same story */
  also: string[];
}

export interface WorldNewsData {
  /** epoch seconds the file was written */
  updated: number;
  items: NewsItem[];
}

export const NEWS_CATS: NewsCat[] = ['disaster', 'war', 'science', 'aliens'];
/** a story counts as breaking for this long after it was published, and only while the file itself is this fresh */
export const BREAKING_WINDOW_S = 6 * 3600;
/** the ticker is hidden when the data is older than this (the collector has been failing for a day) */
export const HIDE_AFTER_S = 24 * 3600;

const USGS_LIVE = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_day.geojson';
const USGS_POLL_MS = 5 * 60 * 1000;
const URL_RE = /^https:\/\/[A-Za-z0-9.-]+(?::\d+)?(?:\/[^\s"'<>\\]*)?$/;

function str(v: unknown, max: number): string {
  return typeof v === 'string' ? v.replace(/\s+/g, ' ').trim().slice(0, max) : '';
}

export function parseWorldNews(json: unknown): WorldNewsData | null {
  const raw = json as { updated?: unknown; items?: unknown } | null;
  if (!raw || typeof raw.updated !== 'number' || !Array.isArray(raw.items)) return null;
  const items: NewsItem[] = [];
  for (const r of raw.items.slice(0, 200) as Record<string, unknown>[]) {
    if (!r || typeof r !== 'object') continue;
    const title = str(r.title, 240);
    const url = str(r.url, 400);
    const cat = r.cat as NewsCat;
    if (!title || !URL_RE.test(url) || !NEWS_CATS.includes(cat) || typeof r.t !== 'number' || !(r.t > 0)) continue;
    items.push({
      id: str(r.id, 40) || url,
      title,
      url,
      source: str(r.source, 40) || 'Unknown',
      cat,
      t: r.t,
      breaking: r.breaking === true,
      signal: str(r.signal, 20),
      also: Array.isArray(r.also) ? (r.also as unknown[]).slice(0, 3).map((a) => str(a, 40)).filter(Boolean) : [],
    });
  }
  return { updated: raw.updated, items };
}

/** Significant earthquakes from the USGS GeoJSON (same shape the collector reads). */
export function parseUsgsLive(json: unknown): NewsItem[] {
  const feats = (json as { features?: unknown } | null)?.features;
  if (!Array.isArray(feats)) return [];
  const out: NewsItem[] = [];
  for (const f of feats.slice(0, 30) as { properties?: Record<string, unknown> }[]) {
    const p = f?.properties;
    if (!p || typeof p.mag !== 'number' || typeof p.time !== 'number') continue;
    const url = str(p.url, 400);
    const title = str(p.title, 240);
    if (!title || !URL_RE.test(url) || !/^https:\/\/earthquake\.usgs\.gov\//.test(url)) continue;
    out.push({ id: `usgs-${url}`, title, url, source: 'USGS', cat: 'disaster', t: Math.floor(p.time / 1000), breaking: true, signal: `M${p.mag.toFixed(1)}`, also: [] });
  }
  return out;
}

/** The file's items plus the live earthquakes it does not have yet (same link = same story). */
export function mergeLive(items: NewsItem[], live: NewsItem[]): NewsItem[] {
  const known = new Set(items.map((i) => i.url));
  return [...items, ...live.filter((l) => !known.has(l.url))];
}

export function isBreaking(item: NewsItem, nowS: number, updated: number): boolean {
  return item.breaking && nowS - item.t <= BREAKING_WINDOW_S && nowS - updated <= BREAKING_WINDOW_S;
}

export function timeAgo(t: number, nowS: number): string {
  const d = Math.max(0, nowS - t);
  if (d < 90) return 'just now';
  if (d < 3600) return `${Math.round(d / 60)} min ago`;
  if (d < 86400) return `${Math.round(d / 3600)} h ago`;
  return `${Math.round(d / 86400)} d ago`;
}

/** What the ticker shows: the breaking stories, or (when nothing is breaking) the newest headlines, labelled as such. null = hide the ticker. */
export function tickerContent(items: NewsItem[], nowS: number, updated: number): { mode: 'breaking' | 'latest'; items: NewsItem[] } | null {
  if (!items.length || nowS - updated > HIDE_AFTER_S) return null;
  const breaking = items.filter((i) => isBreaking(i, nowS, updated)).sort((a, b) => b.t - a.t).slice(0, 8);
  if (breaking.length) return { mode: 'breaking', items: breaking };
  const latest = items.filter((i) => nowS - i.t <= 2 * 86400).sort((a, b) => b.t - a.t).slice(0, 8);
  return latest.length ? { mode: 'latest', items: latest } : null;
}

let pending: Promise<WorldNewsData | null> | null = null;

function loadOnce(): Promise<WorldNewsData | null> {
  if (!pending) {
    pending = fetch('/data/world_news.json', { cache: 'no-cache' })
      .then((r) => (r.ok ? r.json() : null))
      .then(parseWorldNews)
      .catch(() => null);
  }
  return pending;
}

export interface WorldNews {
  loaded: boolean;
  /** null when the file could not be loaded */
  data: WorldNewsData | null;
  /** file items plus live earthquakes */
  items: NewsItem[];
  /** epoch seconds, refreshed every minute so "5 min ago" and the breaking window stay true while the page is open */
  nowS: number;
}

export function useWorldNews(): WorldNews {
  const [data, setData] = useState<WorldNewsData | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [live, setLive] = useState<NewsItem[]>([]);
  const [nowS, setNowS] = useState(() => Math.floor(Date.now() / 1000));

  useEffect(() => {
    let alive = true;
    void loadOnce().then((d) => { if (alive) { setData(d); setLoaded(true); } });
    const tick = setInterval(() => setNowS(Math.floor(Date.now() / 1000)), 60_000);
    const readUsgs = () => {
      if (document.visibilityState === 'hidden') return;
      fetch(USGS_LIVE, { cache: 'no-cache' })
        .then((r) => (r.ok ? r.json() : null))
        .then((j) => { if (alive) setLive(parseUsgsLive(j)); })
        .catch(() => undefined);
    };
    readUsgs();
    const poll = setInterval(readUsgs, USGS_POLL_MS);
    return () => { alive = false; clearInterval(tick); clearInterval(poll); };
  }, []);

  const items = useMemo(() => (data ? mergeLive(data.items, live) : live), [data, live]);
  return { loaded, data, items, nowS };
}
