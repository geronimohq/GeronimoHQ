export interface GeoRow { code: string; name: string; pct: number; count: number }
export interface Srv {
  id: string; name: string; host: string; port: number; region: string; flag: string; discord: string;
  featured: boolean; custom: boolean; group: 'global' | 'china'; cluster: string;
}
export interface Status {
  id: string; online: boolean; map?: string | null; players?: number; bots?: number; humans?: number; max?: number;
  ping?: number | null; geo?: { countries: GeoRow[]; regions: GeoRow[] }; at?: number; error?: string;
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
export interface MaintState { drives: Drive[]; admin: boolean; days_maint: number | null }
export interface SniperStatus { text: string; state: 'idle' | 'armed' | 'triggered' | 'cooldown'; target: string; active: boolean }
export interface PlayerRow { name: string; score: number; time: string }
export interface LaunchState { current: string; vdf_found: boolean; warnings: string[]; recommended: string; suggestions: string[] }
export interface DnsProvider { id: string; name: string; primary: string; secondary: string; desc: string }
export interface DnsState { interface: string; current: string; found: boolean; providers: DnsProvider[]; admin: boolean }
export interface DnsResult { name: string; primary: string; secondary: string; avg_ms: number; jitter_ms: number; reachable: boolean; fastest: boolean; rank: number }
export interface AutoexecState { state: string; status: string; path: string | null; text: string; cfg: boolean }
