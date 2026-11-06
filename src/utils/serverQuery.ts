export interface PlayerEntry {
  name: string;
  score: number;
  time: string;
  seconds: number;
}

export interface LiveServerInfo {
  online: boolean;
  status: string;
  server_name: string;
  map: string;
  players: string;
  curr_players: number;
  max_players: number;
  ping: string;
  rtt: number;
  players_list: PlayerEntry[];
  has_player_roster: boolean;
}

export interface LiveTelemetryPayload {
  timestamp: number;
  iso_time: string;
  total_servers: number;
  online_servers: number;
  servers: Record<string, LiveServerInfo>;
}

export async function fetchLiveTelemetry(): Promise<LiveTelemetryPayload | null> {
  try {
    const res = await fetch(`/data/live_servers.json?t=${Date.now()}`, {
      cache: 'no-cache',
    });
    if (!res.ok) {
      return null;
    }
    const data: LiveTelemetryPayload = await res.json();
    return data;
  } catch (err) {
    console.warn('[Telemetry] Could not fetch live_servers.json:', err);
    return null;
  }
}
