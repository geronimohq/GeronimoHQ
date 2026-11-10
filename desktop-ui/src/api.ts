import type { AppInfo, EngineState, LogLine, Match, Srv, Status } from './types';

type Fn = (...a: unknown[]) => Promise<unknown>;
declare global {
  interface Window { pywebview?: { api: Record<string, Fn> }; __emit?: (ev: string, data: unknown) => void }
}

/** Python -> page events (log lines, finished jobs). */
const listeners = new Map<string, Set<(d: never) => void>>();
window.__emit = (ev, data) => listeners.get(ev)?.forEach((f) => (f as (d: unknown) => void)(data));
export function on<T>(ev: string, cb: (d: T) => void): () => void {
  if (!listeners.has(ev)) listeners.set(ev, new Set());
  listeners.get(ev)!.add(cb as (d: never) => void);
  return () => listeners.get(ev)?.delete(cb as (d: never) => void);
}

/** Resolves when the native bridge exists; after 1.5 s the page assumes a plain browser and uses sample data. */
const ready = new Promise<void>((res) => {
  if (window.pywebview?.api) return res();
  window.addEventListener('pywebviewready', () => res());
  setTimeout(res, 1500);
});
export const isNative = () => !!window.pywebview?.api;

async function call<T>(name: string, ...args: unknown[]): Promise<T> {
  await ready;
  const fn = window.pywebview?.api?.[name];
  if (fn) return (await fn(...args)) as T;
  return (await mock(name, ...args)) as T;
}

export const api = {
  appInfo: () => call<AppInfo>('app_info'),
  logHistory: () => call<LogLine[]>('log_history'),
  setRefresh: (s: number) => call<boolean>('config_set', 'web_refresh_seconds', s),
  catalog: () => call<Srv[]>('servers_catalog'),
  statusMany: (ids: string[]) => call<Status[]>('servers_status_many', ids),
  gflMatch: () => call<Match>('gfl_match'),
  totals: () => call<{ humans?: number; bots?: number; online?: number; total?: number }>('servers_totals'),
  addServer: (name: string, host: string, port: number) => call<{ ok: boolean; error?: string }>('servers_add', name, host, port),
  engineState: () => call<EngineState>('engine_state'),
  engineApply: (opts: Record<string, unknown>) => call<{ ok: boolean; error?: string }>('engine_apply', opts),
  engineRestore: () => call<{ ok: boolean; error?: string }>('engine_restore'),
  powerSet: (plan: 'balanced' | 'high') => call<{ ok: boolean; plan?: string }>('power_set', plan),
  restoreSummary: () => call<string>('restore_summary'),
  winMin: () => call<void>('win_minimize'),
  winMax: () => call<void>('win_maximize'),
  winClose: () => call<void>('win_close'),
  winResize: (edge: string) => call<void>('win_resize', edge),
};

/* ---------- sample data for running the page in a normal browser ---------- */
const MOCK_SRV: Srv[] = [
  { id: 'gfl', name: 'GFL Clan Zombie Escape 24/7', host: '74.91.124.21', port: 27015, region: 'North America (Chicago, US)', flag: 'US', discord: '', featured: true, custom: false, group: 'global', cluster: '' },
  { id: 'possession', name: 'Possession Zombie Escape (PSE)', host: '103.62.49.55', port: 27015, region: 'East Asia (Tokyo, JP)', flag: 'JP', discord: '', featured: false, custom: false, group: 'global', cluster: '' },
  { id: 'net4all', name: 'Net4All.ru Zombie Escape', host: '46.174.54.231', port: 27015, region: 'Europe (Russia)', flag: 'RU', discord: '', featured: false, custom: false, group: 'global', cluster: '' },
];
const countries = [{ code: 'US', name: 'United States', pct: 49, count: 30 }, { code: 'CA', name: 'Canada', pct: 9, count: 5 }, { code: 'BR', name: 'Brazil / LatAm', pct: 6, count: 4 }, { code: 'UK', name: 'United Kingdom', pct: 6, count: 4 }, { code: 'OTHER', name: 'Other Regions', pct: 30, count: 19 }];
const regions = [{ code: 'NA', name: 'North America', pct: 58, count: 35 }, { code: 'EU', name: 'Europe', pct: 17, count: 10 }, { code: 'LATAM', name: 'Latin America', pct: 6, count: 4 }, { code: 'OTHER', name: 'Other Regions', pct: 19, count: 12 }];
async function mock(name: string, ...args: unknown[]): Promise<unknown> {
  switch (name) {
    case 'app_info': return { version: '2.0.0-dev', build_date: '', admin: false, cs2_found: true, cfg_dir: 'C:/cs2/cfg', persona: 'Geronimo', days_since_optimization: 4, refresh_seconds: 5 };
    case 'log_history': return [{ t: '00:00:00', tag: 'SYSTEM', msg: 'Sample data: not running inside the desktop window.' }];
    case 'servers_catalog': return MOCK_SRV;
    case 'servers_status_many': return (args[0] as string[]).map((id) => id === 'net4all'
      ? { id, online: true, map: 'ze_undersea_temple', players: 16, bots: 15, humans: 1, max: 65, ping: 141, geo: { countries, regions } }
      : { id, online: true, map: id === 'gfl' ? 'ze_atix_panic_2017_p' : 'zm_pudding_mill_xmas', players: id === 'gfl' ? 62 : 0, bots: 0, humans: id === 'gfl' ? 62 : 0, max: 64, ping: 120 + Math.round(Math.random() * 40), geo: id === 'gfl' ? { countries, regions } : { countries: [], regions: [] } });
    case 'gfl_match': return { human_score: 0, zombie_score: 5, extend_count: 0, started_sec: Math.floor(Date.now() / 1000) - 1180 };
    case 'servers_totals': return { humans: 120, bots: 16, online: 30, total: 41 };
    case 'servers_add': return { ok: true };
    case 'engine_state': return { power_plan: 'Balanced', autoexec: { state: 'app_block', text: 'Autoexec: found' }, cs2_found: true, cs2_exe: true, cfg_dir: true };
    case 'engine_apply': case 'engine_restore': setTimeout(() => window.__emit?.('job', { name, ok: true }), 800); return { ok: true };
    case 'power_set': return { ok: true, plan: 'Balanced' };
    case 'restore_summary': return 'This undoes the app\'s engine changes.';
    default: return undefined;
  }
}
