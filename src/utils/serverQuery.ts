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
  map_start_time?: number;
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

/**
 * Persists and returns the timestamp (in seconds) when the current map started.
 * Resets back to current time whenever the map changes.
 */
export function getMapStartTime(serverId: string, currentMap?: string, serverTimestamp?: number): number {
  if (!currentMap || currentMap === '-' || currentMap === 'Unknown') {
    return Math.floor(Date.now() / 1000);
  }
  const key = `ze_map_start_${serverId}`;
  try {
    const stored = localStorage.getItem(key);
    if (stored) {
      const parsed = JSON.parse(stored);
      if (parsed.map === currentMap && typeof parsed.startTime === 'number') {
        return parsed.startTime;
      }
    }
  } catch {
    // ignore localStorage errors
  }

  const startTime = serverTimestamp || Math.floor(Date.now() / 1000);
  try {
    localStorage.setItem(key, JSON.stringify({ map: currentMap, startTime }));
  } catch {
    // ignore
  }
  return startTime;
}

/**
 * Formats elapsed seconds into MM:SS (or H:MM:SS if > 1 hour)
 */
export function formatMapElapsed(totalSeconds: number): string {
  if (totalSeconds < 0) totalSeconds = 0;
  const hrs = Math.floor(totalSeconds / 3600);
  const mins = Math.floor((totalSeconds % 3600) / 60);
  const secs = totalSeconds % 60;
  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Estimates realistic ping based on server region and visitor timezone/locale.
 * Browsers cannot send raw UDP/ICMP packets, so this prevents misleading cloud-datacenter pings.
 */
export function getEstimatedRegionalPing(region: string): { display: string; label: string } {
  const reg = region.toLowerCase();
  const offset = new Date().getTimezoneOffset(); // In minutes: Asia is -420 to -540, NA is 240 to 480, EU is -120 to 60

  const isAsia = offset <= -360;
  const isNA = offset >= 240 && offset <= 540;
  const isEU = offset >= -120 && offset <= 120;

  if (reg.includes('us') || reg.includes('chicago')) {
    if (isNA) return { display: '~28 ms', label: 'Local NA' };
    if (isAsia) return { display: '~185 ms', label: 'Trans-Pacific' };
    if (isEU) return { display: '~105 ms', label: 'Trans-Atlantic' };
    return { display: '~190 ms', label: 'Global Est.' };
  }

  if (reg.includes('jp') || reg.includes('tokyo') || reg.includes('kr') || reg.includes('seoul') || reg.includes('china') || reg.includes('hong kong') || reg.includes('bgp')) {
    if (isAsia) return { display: '~38 ms', label: 'Local Asia' };
    if (isNA) return { display: '~145 ms', label: 'Trans-Pacific' };
    if (isEU) return { display: '~220 ms', label: 'Trans-Eurasia' };
    return { display: '~65 ms', label: 'Global Est.' };
  }

  if (reg.includes('eu') || reg.includes('spain') || reg.includes('france') || reg.includes('moscow') || reg.includes('ru')) {
    if (isEU) return { display: '~32 ms', label: 'Local EU' };
    if (isNA) return { display: '~115 ms', label: 'Trans-Atlantic' };
    if (isAsia) return { display: '~235 ms', label: 'Trans-Eurasia' };
    return { display: '~130 ms', label: 'Global Est.' };
  }

  return { display: '~65 ms', label: 'Estimated' };
}
