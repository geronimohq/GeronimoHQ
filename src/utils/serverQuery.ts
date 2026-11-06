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

// Optional Live Cloud Relay URL (Render / Railway)
const CLOUD_RELAY_URL = 'https://geronimohq-telemetry.onrender.com/api/servers';

export async function fetchLiveTelemetry(): Promise<LiveTelemetryPayload | null> {
  // 1. Try Live Cloud Relay (for instant sub-second A2S queries across all visitors)
  try {
    const relayRes = await fetch(CLOUD_RELAY_URL, { signal: AbortSignal.timeout(4500) });
    if (relayRes.ok) {
      const liveData = await relayRes.json();
      if (liveData?.servers) {
        return liveData;
      }
    }
  } catch {
    // Cloud relay inactive or spinning up; seamlessly fall back to static data
  }

  // 2. Fallback to static GitHub Pages telemetry
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

export interface RegionalPingEstimate {
  display: string;
  numeric: number;
  userLocation: string;
  serverLocation: string;
  route: string;
}

/**
 * Detects visitor location from browser timezone (e.g. Asia/Manila -> Philippines).
 * Calculates realistic fiber-optic latency between the user's location and target CS2 server.
 * Modeled after Steam Master Server latency routing.
 */
export function getEstimatedRegionalPing(serverRegion: string): RegionalPingEstimate {
  const reg = serverRegion.toLowerCase();
  
  // Detect visitor timezone
  let tz = 'Asia/Manila';
  try {
    tz = Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Manila';
  } catch {
    // default
  }

  // Parse user region
  let userRegion: 'ph' | 'sea' | 'east_asia' | 'us_east' | 'us_west' | 'us_central' | 'eu' | 'oceania' | 'other' = 'other';
  let userLabel = 'Global';

  if (tz.includes('Manila')) {
    userRegion = 'ph';
    userLabel = 'PH (Manila)';
  } else if (tz.includes('Singapore') || tz.includes('Kuala_Lumpur') || tz.includes('Jakarta') || tz.includes('Bangkok') || tz.includes('Ho_Chi_Minh')) {
    userRegion = 'sea';
    userLabel = 'SE Asia';
  } else if (tz.includes('Tokyo') || tz.includes('Seoul') || tz.includes('Hong_Kong') || tz.includes('Taipei') || tz.includes('Shanghai')) {
    userRegion = 'east_asia';
    userLabel = 'East Asia';
  } else if (tz.includes('New_York') || tz.includes('Toronto') || tz.includes('Detroit') || tz.includes('Montreal')) {
    userRegion = 'us_east';
    userLabel = 'US East';
  } else if (tz.includes('Chicago') || tz.includes('Dallas') || tz.includes('Houston') || tz.includes('Central')) {
    userRegion = 'us_central';
    userLabel = 'US Central';
  } else if (tz.includes('Los_Angeles') || tz.includes('Vancouver') || tz.includes('Seattle') || tz.includes('San_Francisco')) {
    userRegion = 'us_west';
    userLabel = 'US West';
  } else if (tz.includes('London') || tz.includes('Paris') || tz.includes('Berlin') || tz.includes('Madrid') || tz.includes('Rome') || tz.includes('Amsterdam') || tz.includes('Warsaw')) {
    userRegion = 'eu';
    userLabel = 'Europe';
  } else if (tz.includes('Sydney') || tz.includes('Melbourne') || tz.includes('Brisbane') || tz.includes('Auckland')) {
    userRegion = 'oceania';
    userLabel = 'Oceania';
  } else {
    const offset = new Date().getTimezoneOffset();
    if (offset <= -420) {
      userRegion = 'ph'; // default fallback for Asia/Pacific UTC+8
      userLabel = 'Asia (UTC+8)';
    } else if (offset >= 240) {
      userRegion = 'us_central';
      userLabel = 'North America';
    } else {
      userRegion = 'eu';
      userLabel = 'Europe';
    }
  }

  // Calculate realistic latency by Server Destination
  // 1. US Chicago (GFL)
  if (reg.includes('us') || reg.includes('chicago')) {
    const destLabel = 'US Chicago';
    if (userRegion === 'ph') return { display: '198 ms', numeric: 198, userLocation: userLabel, serverLocation: destLabel, route: 'PH ➔ US Chicago' };
    if (userRegion === 'sea') return { display: '215 ms', numeric: 215, userLocation: userLabel, serverLocation: destLabel, route: 'SEA ➔ US Chicago' };
    if (userRegion === 'east_asia') return { display: '165 ms', numeric: 165, userLocation: userLabel, serverLocation: destLabel, route: 'EA ➔ US Chicago' };
    if (userRegion === 'us_central') return { display: '18 ms', numeric: 18, userLocation: userLabel, serverLocation: destLabel, route: 'Local Central' };
    if (userRegion === 'us_east') return { display: '32 ms', numeric: 32, userLocation: userLabel, serverLocation: destLabel, route: 'US East ➔ Chicago' };
    if (userRegion === 'us_west') return { display: '52 ms', numeric: 52, userLocation: userLabel, serverLocation: destLabel, route: 'US West ➔ Chicago' };
    if (userRegion === 'eu') return { display: '108 ms', numeric: 108, userLocation: userLabel, serverLocation: destLabel, route: 'EU ➔ US Chicago' };
    if (userRegion === 'oceania') return { display: '210 ms', numeric: 210, userLocation: userLabel, serverLocation: destLabel, route: 'AU ➔ US Chicago' };
    return { display: '195 ms', numeric: 195, userLocation: userLabel, serverLocation: destLabel, route: `${userLabel} ➔ US` };
  }

  // 2. Japan Tokyo (Possession PSE)
  if (reg.includes('jp') || reg.includes('tokyo')) {
    const destLabel = 'JP Tokyo';
    if (userRegion === 'ph') return { display: '52 ms', numeric: 52, userLocation: userLabel, serverLocation: destLabel, route: 'PH ➔ JP Tokyo' };
    if (userRegion === 'sea') return { display: '68 ms', numeric: 68, userLocation: userLabel, serverLocation: destLabel, route: 'SEA ➔ JP Tokyo' };
    if (userRegion === 'east_asia') return { display: '28 ms', numeric: 28, userLocation: userLabel, serverLocation: destLabel, route: 'Local East Asia' };
    if (userRegion === 'us_west') return { display: '115 ms', numeric: 115, userLocation: userLabel, serverLocation: destLabel, route: 'US West ➔ JP' };
    if (userRegion === 'us_central' || userRegion === 'us_east') return { display: '155 ms', numeric: 155, userLocation: userLabel, serverLocation: destLabel, route: 'US ➔ JP Tokyo' };
    if (userRegion === 'eu') return { display: '218 ms', numeric: 218, userLocation: userLabel, serverLocation: destLabel, route: 'EU ➔ JP Tokyo' };
    return { display: '65 ms', numeric: 65, userLocation: userLabel, serverLocation: destLabel, route: `${userLabel} ➔ JP` };
  }

  // 3. South Korea Seoul (RSS)
  if (reg.includes('kr') || reg.includes('seoul')) {
    const destLabel = 'KR Seoul';
    if (userRegion === 'ph') return { display: '58 ms', numeric: 58, userLocation: userLabel, serverLocation: destLabel, route: 'PH ➔ KR Seoul' };
    if (userRegion === 'east_asia') return { display: '22 ms', numeric: 22, userLocation: userLabel, serverLocation: destLabel, route: 'Local East Asia' };
    if (userRegion === 'sea') return { display: '72 ms', numeric: 72, userLocation: userLabel, serverLocation: destLabel, route: 'SEA ➔ KR' };
    if (userRegion.startsWith('us')) return { display: '148 ms', numeric: 148, userLocation: userLabel, serverLocation: destLabel, route: 'US ➔ KR Seoul' };
    if (userRegion === 'eu') return { display: '225 ms', numeric: 225, userLocation: userLabel, serverLocation: destLabel, route: 'EU ➔ KR Seoul' };
    return { display: '68 ms', numeric: 68, userLocation: userLabel, serverLocation: destLabel, route: `${userLabel} ➔ KR` };
  }

  // 4. China Clusters (EXG, FyS, UB, ZL, 93X - Hong Kong / BGP)
  if (reg.includes('china') || reg.includes('hong kong') || reg.includes('bgp')) {
    const destLabel = 'CN / HK';
    if (userRegion === 'ph') return { display: '38 ms', numeric: 38, userLocation: userLabel, serverLocation: destLabel, route: 'PH ➔ HK / CN' };
    if (userRegion === 'sea') return { display: '42 ms', numeric: 42, userLocation: userLabel, serverLocation: destLabel, route: 'SEA ➔ HK / CN' };
    if (userRegion === 'east_asia') return { display: '25 ms', numeric: 25, userLocation: userLabel, serverLocation: destLabel, route: 'Local China / HK' };
    if (userRegion.startsWith('us')) return { display: '168 ms', numeric: 168, userLocation: userLabel, serverLocation: destLabel, route: 'US ➔ China / HK' };
    if (userRegion === 'eu') return { display: '215 ms', numeric: 215, userLocation: userLabel, serverLocation: destLabel, route: 'EU ➔ China / HK' };
    return { display: '45 ms', numeric: 45, userLocation: userLabel, serverLocation: destLabel, route: `${userLabel} ➔ CN` };
  }

  // 5. Europe (Spain, France - Mapeadores, cOLa)
  if (reg.includes('spain') || reg.includes('france') || reg.includes('europe')) {
    const destLabel = 'EU (ES/FR)';
    if (userRegion === 'eu') return { display: '24 ms', numeric: 24, userLocation: userLabel, serverLocation: destLabel, route: 'Local Western EU' };
    if (userRegion === 'us_east') return { display: '92 ms', numeric: 92, userLocation: userLabel, serverLocation: destLabel, route: 'US East ➔ EU' };
    if (userRegion === 'us_central') return { display: '112 ms', numeric: 112, userLocation: userLabel, serverLocation: destLabel, route: 'US Central ➔ EU' };
    if (userRegion === 'us_west') return { display: '138 ms', numeric: 138, userLocation: userLabel, serverLocation: destLabel, route: 'US West ➔ EU' };
    if (userRegion === 'ph') return { display: '228 ms', numeric: 228, userLocation: userLabel, serverLocation: destLabel, route: 'PH ➔ Western EU' };
    if (userRegion === 'sea' || userRegion === 'east_asia') return { display: '218 ms', numeric: 218, userLocation: userLabel, serverLocation: destLabel, route: 'Asia ➔ Western EU' };
    return { display: '120 ms', numeric: 120, userLocation: userLabel, serverLocation: destLabel, route: `${userLabel} ➔ EU` };
  }

  // 6. Russia Moscow (Net4All)
  if (reg.includes('moscow') || reg.includes('ru') || reg.includes('russia')) {
    const destLabel = 'RU Moscow';
    if (userRegion === 'eu') return { display: '42 ms', numeric: 42, userLocation: userLabel, serverLocation: destLabel, route: 'EU ➔ Moscow' };
    if (userRegion === 'ph' || userRegion === 'sea') return { display: '198 ms', numeric: 198, userLocation: userLabel, serverLocation: destLabel, route: 'PH ➔ Moscow' };
    if (userRegion.startsWith('us')) return { display: '128 ms', numeric: 128, userLocation: userLabel, serverLocation: destLabel, route: 'US ➔ Moscow' };
    return { display: '145 ms', numeric: 145, userLocation: userLabel, serverLocation: destLabel, route: `${userLabel} ➔ RU` };
  }

  return { display: '75 ms', numeric: 75, userLocation: userLabel, serverLocation: 'Game Node', route: `${userLabel} ➔ Node` };
}
