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
