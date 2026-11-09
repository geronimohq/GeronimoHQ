// AUDIT P2-#2: ONE definition of "players online", shared with the backend
// (backend/api.py compute_player_totals) and the desktop app (server_browser.py).
//   players = HUMANS only (A2S "players" includes bots, so humans = players - bots)
//   counted only for servers that answered within TOTALS_MAX_AGE_S of the sample time
//   each host:port counted once
// The website prefers the backend's `totals` field and only computes here when the
// payload has none (older backend, or the static /data/live_servers.json snapshot).

export const TOTALS_MAX_AGE_S = 90;

export interface PlayerTotals {
  humans: number;
  bots: number;
  online_servers: number;
  total_servers: number;
  stale_servers: number;
  bots_unknown_servers: number;
  duplicates_dropped: number;
  max_age_s: number;
}

export interface TotalsInputRow {
  host?: string;
  port?: number;
  online?: boolean;
  curr_players?: number;
  bots?: number | null;
  sampled_at?: number | null;
}

export function computePlayerTotals(
  rows: TotalsInputRow[],
  nowSec: number,
  maxAgeS: number = TOTALS_MAX_AGE_S,
): PlayerTotals {
  const seen = new Set<string>();
  let humans = 0, bots = 0, online = 0, stale = 0, botsUnknown = 0, dupes = 0, total = 0;
  for (const r of rows) {
    const key = `${String(r.host ?? '').toLowerCase()}:${Number(r.port ?? 0)}`;
    if (seen.has(key)) { dupes += 1; continue; }
    seen.add(key);
    total += 1;
    const fresh = r.sampled_at == null || nowSec - Number(r.sampled_at) <= maxAgeS;
    const isOnline = Boolean(r.online) && fresh;
    if (Boolean(r.online) && !fresh) stale += 1;
    if (!isOnline) continue;
    const curr = Number(r.curr_players ?? 0) || 0;
    const known = r.bots !== undefined && r.bots !== null;
    const b = known ? Math.max(0, Number(r.bots)) : 0;
    online += 1;
    humans += Math.max(0, curr - b);
    bots += b;
    if (!known) botsUnknown += 1;
  }
  return {
    humans, bots, online_servers: online, total_servers: total, stale_servers: stale,
    bots_unknown_servers: botsUnknown, duplicates_dropped: dupes, max_age_s: maxAgeS,
  };
}

export interface DisplayTotals extends PlayerTotals {
  /** seconds between the data's sample time and now (browser clock) */
  ageSeconds: number;
  /** true when the numbers are older than TOTALS_MAX_AGE_S (show "as of …") */
  isSnapshot: boolean;
}

interface TotalsPayload {
  timestamp?: number;
  totals?: PlayerTotals;
  servers?: Record<string, { host?: string; port?: number; online?: boolean; curr_players?: number; bots?: number | null }>;
}

export function getDisplayTotals(payload: TotalsPayload | null | undefined, nowMs: number): DisplayTotals | null {
  if (!payload?.servers) return null;
  const sampled = Number(payload.timestamp ?? 0) || nowMs / 1000;
  // Freshness of each server is judged at the payload's own sample time; the age of
  // the whole payload is shown separately so a stale snapshot is never shown as "now".
  const base: PlayerTotals = payload.totals ?? computePlayerTotals(
    Object.entries(payload.servers).map(([id, s]) => ({
      host: s.host ?? id, port: s.port ?? 0, online: s.online, curr_players: s.curr_players,
      bots: s.bots, sampled_at: sampled,
    })),
    sampled,
  );
  const ageSeconds = Math.max(0, Math.round(nowMs / 1000 - sampled));
  return { ...base, ageSeconds, isSnapshot: ageSeconds > TOTALS_MAX_AGE_S };
}
