import type { Track, AnalyzerResult, AppInfo, AutoexecState, HwInfo, VpkResult, UpdateInfo, PresenceState, MapsSettings, MpoState, SettingsValues, DashboardData, DnsState, EngineState, LogLine, LaunchState, MaintState, Match, PlayerRow, SniperStatus, Srv, Status, MapHelp, PackSize } from './types';

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
  addServer: (name: string, host: string, port: number, region: string) => call<{ ok: boolean; error?: string }>('servers_add', name, host, port, region),
  removeServer: (id: string) => call<boolean>('servers_remove', id),
  soundtrack: (map: string) => call<{ map: string; tracks: Track[] }>('soundtrack', map),
  open3dMap: (map: string) => call<boolean>('open_3d_map', map),
  openYoutube: (title: string) => call<boolean>('open_youtube_search', title),
  dnsStatus: () => call<{ text: string; state: string }>('dns_status'),
  diagnostics: () => call<string>('diagnostics'),
  exeSha: () => call<string>('exe_sha256'),
  logClear: () => call<boolean>('log_clear'),
  about: () => call<{ version: string; build_date: string; last_update_check: string }>('about'),
  engineState: () => call<EngineState>('engine_state'),
  engineApply: (opts: Record<string, unknown>) => call<{ ok: boolean; error?: string }>('engine_apply', opts),
  engineRestore: () => call<{ ok: boolean; error?: string }>('engine_restore'),
  powerSet: (plan: 'balanced' | 'high') => call<{ ok: boolean; plan?: string }>('power_set', plan),
  restoreSummary: () => call<string>('restore_summary'),
  connect: (id: string) => call<{ ok: boolean; error?: string }>('server_connect', id),
  players: (id: string) => call<{ success: boolean; players: PlayerRow[]; error?: string; name?: string }>('server_players', id),
  sniperStart: (id: string, max: number) => call<{ ok: boolean; error?: string }>('sniper_start', id, max),
  sniperStop: () => call<{ ok: boolean }>('sniper_stop'),
  sniperStatus: () => call<SniperStatus>('sniper_status'),
  dashboard: () => call<DashboardData>('dashboard'),
  openPath: (kind: string) => call<boolean>('open_path', kind),
  openUrl: (url: string) => call<boolean>('open_url', url),
  relaunchAdmin: (page: string) => call<{ ok: boolean }>('relaunch_admin', page),
  sniperTiers: () => call<{ gfl: string; community: string }>('sniper_tiers'),
  sniperSetTier: (kind: 'gfl' | 'community', value: string) => call<{ gfl: string; community: string; ok: boolean }>('sniper_set_tier', kind, value),
  mapThumb: (map: string) => call<string>('map_thumb', map),
  maintState: () => call<MaintState>('maint_state'),
  maintRun: (opts: Record<string, boolean>) => call<{ ok: boolean; error?: string }>('maint_run', opts),
  maintTool: (name: string) => call<{ ok: boolean; error?: string }>('maint_tool', name),
  launchState: () => call<LaunchState>('launch_state'),
  launchSave: (o: string) => call<{ ok: boolean; error?: string }>('launch_save', o),
  boost: () => call<{ ok: boolean; msg: string }>('boost_run'),
  cs2Running: () => call<boolean>('cs2_running'),
  dnsState: () => call<DnsState>('dns_state'),
  dnsBenchmark: () => call<{ ok: boolean; error?: string }>('dns_benchmark'),
  dnsApply: (p: string, s: string, n: string) => call<{ ok: boolean; error?: string }>('dns_apply', p, s, n),
  dnsRestore: () => call<{ ok: boolean; error?: string }>('dns_restore'),
  autoexecState: () => call<AutoexecState>('autoexec_state'),
  autoexecInstall: () => call<{ ok: boolean; error?: string }>('autoexec_install'),
  autoexecRestore: () => call<{ ok: boolean; error?: string }>('autoexec_restore'),
  autoexecFps: (n: number) => call<{ ok: boolean; error?: string }>('autoexec_fps', n),
  mpo: () => call<MpoState>('mpo_state'),
  settingsGet: () => call<SettingsValues>('settings_get'),
  settingsSave: (v: Partial<SettingsValues>) => call<{ ok: boolean; startup_ok?: boolean; refresh_seconds: number }>('settings_save', v),
  settingsReset: () => call<{ ok: boolean }>('settings_reset'),
  setLastPage: (v: string) => call<void>('set_last_page', v),
  startPage: () => call<string>('start_page'),
  mapsSettings: () => call<MapsSettings>('maps_settings'),
  mapsScan: (c: string[], recent: boolean) => call<{ ok: boolean; error?: string }>('maps_scan', c, recent),
  mapsDelete: (ids: string[], communities: string[], protectRecent: boolean, allowAssets = false) => call<{ ok: boolean; error?: string }>('maps_delete', ids, communities, protectRecent, allowAssets),
  mapsBackup: () => call<{ ok: boolean; count: number; dir: string }>('maps_backup'),
  mapsRestore: () => call<{ ok: boolean; count: number }>('maps_restore'),
  presence: () => call<PresenceState>('presence_state'),
  presenceToggle: (on: boolean) => call<PresenceState>('presence_toggle', on),
  presenceClear: () => call<PresenceState>('presence_clear'),
  presenceStandby: () => call<PresenceState>('presence_standby'),
  presenceBroadcast: (id: string) => call<{ ok: boolean; error?: string }>('presence_broadcast', id),
  updateCheck: () => call<UpdateInfo>('update_check', true),
  updateSkip: (v: string) => call<boolean>('update_skip', v),
  updateInstall: () => call<{ ok: boolean; error?: string }>('update_install'),
  hw: () => call<HwInfo>('hw_info'),
  zeCustomizer: (o: Record<string, unknown>) => call<{ ok: boolean; message: string; keys: string[]; hud: number; vm: boolean }>('ze_customizer', o),
  autoexecSave: (t: string) => call<{ ok: boolean; error?: string; path?: string }>('autoexec_save', t),
  logAnalyze: () => call<AnalyzerResult>('log_analyze'),
  dnsCustom: (p: string, s: string) => call<{ ok: boolean; error?: string }>('dns_custom', p, s),
  vpkVerify: () => call<VpkResult>('vpk_verify'),
  vpkRepair: () => call<{ ok: boolean; count: number; skipped?: number; message: string }>('vpk_repair'),
  mapStats: () => call<{ count: number; gb: number }>('maps_quick_stats'),
  presenceRefresh: () => call<import('./types').PresenceState>('presence_refresh'),
  winMin: () => call<void>('win_minimize'),
  memTrim: (low: boolean) => call<void>('mem_trim', low),
  mapGet: (map: string, wid: string) => call<{ ok: boolean; kind: string }>('map_get', map, wid),
  mapHelp: (sid: string, map: string, wid: string, mode = '') => call<MapHelp>('map_help', sid, map, wid, mode),
  collectionSize: (id: string) => call<PackSize>('collection_size', id),
  collectionOpen: (id: string) => call<{ ok: boolean }>('collection_open', id),
  winMax: () => call<boolean>('win_maximize'),
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
    case 'server_connect': return { ok: true };
    case 'server_players': return { success: true, name: 'Sample', players: [{ name: 'Player One', score: 12, time: '10m 02s' }, { name: 'Player Two', score: 7, time: '04m 40s' }] };
    case 'sniper_start': case 'sniper_stop': return { ok: true };
    case 'sniper_status': return { text: '● SLOT SNIPER: IDLE', state: 'idle', target: '', active: false };
    case 'dashboard': return { cs2_dir: 'C:/cs2', cfg_dir: 'C:/cs2/cfg', autoexec: { state: 'app_block', text: 'Autoexec: found' }, drive: { drive: 'E:', total_gb: 1000, free_gb: 330, used_gb: 670, used_pct: 67, is_critical: false }, days_opt: 4, days_maint: 4 };
    case 'open_path': case 'open_url': return true;
    case 'relaunch_admin': return { ok: false };
    case 'maint_state': return { drives: [{ drive: 'C:', total_gb: 500, free_gb: 120, used_gb: 380, used_pct: 76, is_critical: false }, { drive: 'E:', total_gb: 1000, free_gb: 330, used_gb: 670, used_pct: 67, is_critical: false }], admin: false, days_maint: 4 };
    case 'maint_run': case 'maint_tool': setTimeout(() => window.__emit?.('job', { name: 'maint_run', ok: true }), 800); return { ok: true };
    case 'launch_state': return { current: '-novid -threads 4', vdf_found: true, warnings: ["'-threads' detected: Causes thread contention."], recommended: '-novid -nojoy', suggestions: [] };
    case 'launch_save': case 'autoexec_install': case 'autoexec_restore': case 'autoexec_fps': case 'dns_apply': case 'dns_restore': return { ok: true };
    case 'boost_run': return { ok: false, msg: 'CS2 is not running (sample).' };
    case 'cs2_running': return false;
    case 'dns_state': return { interface: 'Ethernet', current: 'Automatic (ISP / DHCP)', found: true, admin: false, providers: [{ id: 'cloudflare', name: 'Cloudflare Gaming (1.1.1.1)', primary: '1.1.1.1', secondary: '1.0.0.1', desc: 'Ultra-fast global edge network.' }] };
    case 'dns_benchmark': setTimeout(() => { window.__emit?.('dns_results', [{ name: 'Cloudflare Gaming (1.1.1.1)', primary: '1.1.1.1', secondary: '1.0.0.1', avg_ms: 12.4, jitter_ms: 1.1, reachable: true, fastest: true, rank: 1 }]); window.__emit?.('job', { name: 'dns_benchmark', ok: true }); }, 900); return { ok: true };
    case 'autoexec_state': return { state: 'app_block', status: 'Autoexec: found', path: 'C:/cs2/cfg/autoexec.cfg', text: '// sample\nrate 786432\nsnd_mixahead 0.025\nbind "F7" "say hi"\n', cfg: true };
    case 'mpo_state': return { gpu: 'AMD Radeon RX 6600 (sample)', vendor: 'AMD', disabled: true, badge: 'AMD RADEON \u2022 MPO DISABLED', detail: 'DisableOverlays = 0x1', reg_path: 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers' };
    case 'settings_get': return { start_with_windows: false, start_minimized: false, minimize_to_tray_on_close: true, open_on_page: 'Dashboard', sniper_sound_enabled: true, server_refresh_speed: 'Normal (5s)', discord_rpc_enabled: true, check_updates_on_startup: true, speeds: ['Live (1s)', 'Normal (5s)', 'Eco (15s)'], pages: ['Dashboard', 'Last used page'] };
    case 'settings_save': return { ok: true, refresh_seconds: 5 };
    case 'settings_reset': return { ok: true };
    case 'start_page': return 'servers';
    case 'set_last_page': return undefined;
    case 'maps_settings': return { communities: ['gfl', 'possession', 'rss', 'mapeadores_cola'], protect_recent: true };
    case 'maps_scan': setTimeout(() => { window.__emit?.('maps', [
      { id: '1', name: 'ze_sample_a', status: 'Subscribed (GFL ZE Collection)', type: 'subscribed', sub: true, asset: false, protected: true, workshop: true, dupe: false, size: 14000000, size_str: '13.4 MB', mtime: '2026-10-02 14:45' },
      { id: '2', name: 'ze_temp_b', status: 'Temp download', type: 'temp', sub: false, asset: false, protected: false, workshop: true, dupe: true, size: 2400000000, size_str: '2.24 GB', mtime: '2026-09-13 11:53' }]); window.__emit?.('job', { name: 'maps_scan', ok: true }); }, 600); return { ok: true };
    case 'maps_delete': setTimeout(() => window.__emit?.('maps_deleted', { count: 1, freed: 2400000000 }), 500); return { ok: true };
    case 'maps_backup': case 'maps_restore': return { ok: true, count: 0, dir: '' };
    case 'presence_state': case 'presence_toggle': case 'presence_clear': case 'presence_standby': return { enabled: true, connected: false, status: 'Standby (CS2 closed)', details: '', state: '', buttons: [], cs2_running: false, tracked: '' };
    case 'presence_broadcast': return { ok: true };
    case 'update_check': return { available: false, message: 'You are up to date (sample).', last: '' };
    case 'update_skip': return true;
    case 'map_help': return { map: { name: 'ze_demo_map', wid: '' }, collections: [{ id: '1', label: 'Demo collection', kind: 'maps', total: 100, installed: 40, known: true, match: true }] };
    case 'collection_size': return { ok: true, missing: 60, known: 60, unknown: 0, bytes: 12000000000 };
    case 'collection_open': return { ok: true };
    case 'update_install': return { ok: false, error: 'Updates install only in the packaged app.' };
    case 'hw_info': return { cpu: 'AMD Ryzen 7 5700X3D 8-Core Processor [3D V-Cache Detected]', gpu: 'AMD Radeon RX 6600', profile: 'AMD 3D V-Cache detected. Windows Balanced allows AMD CPPC to properly schedule game threads.', recommended_plan: 'balanced' };
    case 'ze_customizer': return { ok: true, message: 'Sample', keys: ['F7', 'F8'], hud: 0, vm: true };
    case 'autoexec_save': return { ok: true, path: 'C:/cs2/cfg/autoexec.cfg' };
    case 'log_analyze': return { found: false, message: 'console.log not found (sample).', file_size_mb: 0, frame_hitch_events: 0, shader_compile_events: 0, net_jitter_events: 0, vpk_load_events: 0, last_map: 'Unknown', recommendation: '', log_path: '', grade: '' };
    case 'dns_custom': return { ok: true };
    case 'vpk_verify': return { message: 'Verified 0 Workshop VPK packs: 1 Healthy, 0 Corrupted/Incomplete.', healthy: 1, corrupted: 0, total_gb: 0.07, bad: [] };
    case 'vpk_repair': return { ok: true, count: 0, message: 'No damaged Workshop VPK files were found. Nothing to remove.' };
    case 'maps_quick_stats': return { count: 373, gb: 87.6 };
    case 'presence_refresh': return { enabled: true, connected: false, status: 'Standby (CS2 closed)', details: '', state: '', buttons: [], cs2_running: false, tracked: '' };
    case 'sniper_tiers': return { gfl: 'mapper', community: '63' };
    case 'sniper_set_tier': return { gfl: 'mapper', community: String(args[1]), ok: true };
    case 'map_thumb': return '';
    case 'win_maximize': return false;
    case 'servers_remove': case 'open_3d_map': case 'open_youtube_search': case 'log_clear': return true;
    case 'soundtrack': return { map: String(args[0]), tracks: [{ name: 'Sample track', duration: '03:12', tags: ['stage 1'], url: null }] };
    case 'dns_status': return { text: '\u25CF DNS: Cloudflare Gaming (1.1.1.1)', state: 'provider' };
    case 'diagnostics': return 'CS2 Command Center Diagnostics (sample)';
    case 'exe_sha256': return 'SAMPLE';
    case 'about': return { version: '2.0.0-dev', build_date: '', last_update_check: 'Never' };
    case 'restore_summary': return 'This undoes the app\'s engine changes.';
    default: return undefined;
  }
}
