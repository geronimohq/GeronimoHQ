export interface GeoRow { code: string; name: string; pct: number; count: number }
export interface Pack { id: string; label: string; kind: 'maps' | 'assets' | 'default' | 'item' }
export interface MapHelp {
  map: { name: string; wid: string } | null;
  collections: { id: string; label: string; kind: string; total: number; installed: number; known: boolean; match: boolean }[];
  reupload?: boolean; pending?: number; map_name?: string;     // reupload: the server uploads its own copy of each map (GFL); pending: collection maps not installed
}
export interface MapsNews { known: boolean; new: number; missing: number; total: number }
export interface PackSize { ok: boolean; missing: number; known: number; unknown: number; bytes: number }
export interface Srv {
  id: string; name: string; host: string; port: number; region: string; flag: string; discord: string; website?: string;
  featured: boolean; custom: boolean; group: 'global' | 'china'; cluster: string; packs?: Pack[]; cluster_id?: string; cluster_desc?: string;
}
export interface Status {
  id: string; online: boolean; map?: string | null; players?: number; bots?: number; humans?: number; max?: number;
  ping?: number | null; geo?: { countries: GeoRow[]; regions: GeoRow[] }; at?: number; error?: string; map_since?: number; map_exact?: boolean; map_missing?: boolean; map_wid?: string; map_reupload?: boolean; map_pending?: number;
}
export interface AppInfo {
  version: string; build_date: string; admin: boolean; cs2_found: boolean; cfg_dir: string | null; persona: string | null;
  days_since_optimization: number | null; refresh_seconds: number;
}
export interface EngineState { power_plan: string; autoexec: { state: string; text: string } | null; cs2_found: boolean; cs2_exe: boolean; cfg_dir: boolean }
export interface LogLine { t: string; tag: string; msg: string }
export interface Match { human_score?: number; zombie_score?: number; extend_count?: number; started_sec?: number; map?: string }
export interface Drive { drive: string; total_gb: number; free_gb: number; used_gb: number; used_pct: number; is_critical: boolean }
export interface DashboardData {
  cs2_dir: string | null; cfg_dir: string | null; autoexec: { state: string; text: string } | null; drive: Drive | null;
  days_opt: number | null; days_maint: number | null;
}
export interface ToolRun { name: string; started: number; pct: number | null }
export interface ToolLast { at: string; status: string; ok: boolean; headline: string; seconds: number }
export interface ToolResult { tool: string; title: string; status: string; ok: boolean; headline: string; detail: string; next: string; evidence: string[]; seconds: number; log_file: string }
export interface MaintState { drives: Drive[]; admin: boolean; days_maint: number | null; tool_run: ToolRun | null; tool_last: Record<string, ToolLast> }
export interface SniperStatus { text: string; state: 'idle' | 'armed' | 'triggered' | 'cooldown'; target: string; active: boolean }
export interface PlayerRow { name: string; score: number; time: string; seconds?: number; index?: number }
export interface Track { name: string; duration: string; tags: string[]; url: string | null }
export interface LaunchState { current: string; vdf_found: boolean; warnings: string[]; recommended: string; suggestions: string[] }
export interface DnsProvider { id: string; name: string; primary: string; secondary: string; desc: string }
export interface DnsState { interface: string; current: string; found: boolean; providers: DnsProvider[]; admin: boolean }
export interface DnsResult { name: string; primary: string; secondary: string; avg_ms: number; jitter_ms: number; reachable: boolean; fastest: boolean; rank: number }
export interface AutoexecState { state: string; status: string; path: string | null; text: string; cfg: boolean; cfg_dir: string | null; personal_vm: boolean; personal_lines: string[]; truncated?: boolean }
export interface MpoState { gpu: string; vendor: string; disabled: boolean; badge: string; detail: string; reg_path: string }
export interface SettingsValues {
  start_with_windows: boolean; start_minimized: boolean; minimize_to_tray_on_close: boolean; open_on_page: string; sniper_sound_enabled: boolean;
  server_refresh_speed: string; discord_rpc_enabled: boolean; check_updates_on_startup: boolean; speeds: string[]; pages: string[];
}
export interface MapRow { id: string; name: string; status: string; type: string; sub: boolean; asset: boolean; protected: boolean; workshop: boolean; dupe: boolean; size: number; size_str: string; mtime: string }
export interface MapsSettings { communities: string[]; protect_recent: boolean }
export interface PresenceState { enabled: boolean; connected: boolean; status: string; details: string; state: string; buttons: string[]; cs2_running: boolean; tracked: string }
export interface UpdateInfo { available: boolean; version?: string; notes?: string; size?: number; message?: string; last?: string }
export interface HwInfo { cpu: string; gpu: string; profile: string; recommended_plan: 'balanced' | 'high' }
export interface AnalyzerResult { found: boolean; condebug?: boolean; message: string; file_size_mb: number; frame_hitch_events: number; shader_compile_events: number; net_jitter_events: number; vpk_load_events: number; last_map: string; recommendation: string; log_path: string; grade: string }
export interface VpkResult { message: string; healthy: number; corrupted: number; total_gb: number; bad: string[] }
