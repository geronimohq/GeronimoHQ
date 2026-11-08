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

export interface GeronimoPresence {
  online: boolean;
  in_game: boolean;
  state: 'in_server' | 'main_menu' | 'other_game' | 'online' | 'offline';
  game: string | null;
  server_id: string | null;
  server_name: string | null;
  map: string;
  players: string;
  connect_url: string | null;
  player_duration?: number;
}

export interface GflMatchNow {
  human_score: number;
  zombie_score: number;
  extend_count: number;
  started_at: string;
  estimated_time_end?: string;
  server_time_end?: string;
  map: string;
  player_count: number;
}

export interface MapMusicEntry {
  id: string;
  name: string;
  duration: number;
  youtube_music?: string;
  youtube_video?: string;
  tags?: string[];
}

export interface LiveTelemetryPayload {
  timestamp: number;
  iso_time: string;
  total_servers: number;
  online_servers: number;
  geronimo_presence?: GeronimoPresence;
  gfl_match_now?: GflMatchNow | null;
  gfl_map_musics?: MapMusicEntry[];
  servers: Record<string, LiveServerInfo>;
}

// Optional Live Cloud Relay URL (Render / Railway)
const CLOUD_RELAY_URL = 'https://geronimohq-telemetry.onrender.com/api/servers';

// Module-level caches to guarantee zero flicker / flapping across periodic polling intervals
let cachedGflMatchNow: GflMatchNow | null = null;
let cachedGflMusics: { map: string; musics: MapMusicEntry[] } | null = null;
let lastMatchFetchTimestamp = 0;
let inFlightTelemetryPromise: Promise<LiveTelemetryPayload | null> | null = null;

// Initialize cache from sessionStorage if available
try {
  if (typeof window !== 'undefined' && window.sessionStorage) {
    const saved = window.sessionStorage.getItem('ze_cached_gfl_match_now');
    if (saved) {
      cachedGflMatchNow = JSON.parse(saved);
    }
  }
} catch {
  // ignore
}

async function executeFetchLiveTelemetry(): Promise<LiveTelemetryPayload | null> {
  let payload: LiveTelemetryPayload | null = null;

  // 1. Try Live Cloud Relay (for instant sub-second A2S queries across all visitors)
  try {
    const relayRes = await fetch(CLOUD_RELAY_URL, { signal: AbortSignal.timeout(4500) });
    if (relayRes.ok) {
      const liveData = await relayRes.json();
      if (liveData?.servers) {
        payload = liveData;
      }
    }
  } catch {
    // Cloud relay inactive or spinning up; seamlessly fall back to static data
  }

  // 2. Fallback to static GitHub Pages telemetry
  if (!payload) {
    try {
      const res = await fetch(`/data/live_servers.json?t=${Date.now()}`, {
        cache: 'no-cache',
      });
      if (res.ok) {
        payload = await res.json();
      }
    } catch (err) {
      console.warn('[Telemetry] Could not fetch live_servers.json:', err);
    }
  }

  if (!payload) return null;

  // 3. Direct Browser GFL Intel Enrichment (Human Score, Zombie Score, Extends Left)
  // Cloudflare blocks datacenter IPs (like Render/AWS) with 403 Forbidden,
  // but client browsers have direct CORS access (Access-Control-Allow-Origin: https://geronimohq.com).
  // Strictly bypass browser HTTP cache with ?_t cache-buster and 'no-store' to eliminate the 3-5m delay!
  const now = Date.now();
  const shouldQueryZegraph = (now - lastMatchFetchTimestamp > 3500) || !cachedGflMatchNow;

  if (shouldQueryZegraph) {
    try {
      const matchRes = await fetch(`https://zegraph.xyz/data/api/servers/65bdad6379cefd7ebcecce5c/match-now?_t=${now}`, {
        cache: 'no-store',
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
        },
        signal: AbortSignal.timeout(4500),
      });
      if (matchRes.ok) {
        const matchJson = await matchRes.json();
        if (matchJson?.code === 0 && matchJson?.data) {
          cachedGflMatchNow = matchJson.data;
          lastMatchFetchTimestamp = now;
          try {
            if (typeof window !== 'undefined' && window.sessionStorage) {
              window.sessionStorage.setItem('ze_cached_gfl_match_now', JSON.stringify(cachedGflMatchNow));
            }
          } catch {
            // ignore
          }
        }
      }
    } catch {
      // Retain cachedGflMatchNow without zeroing out scores!
    }
  }

  // Authoritatively attach the best valid match data to prevent flapping
  if (cachedGflMatchNow) {
    payload.gfl_match_now = cachedGflMatchNow;
    if (cachedGflMatchNow.started_at && payload.servers?.gfl) {
      const startedSec = Math.floor(new Date(cachedGflMatchNow.started_at).getTime() / 1000);
      if (startedSec > 0) {
        payload.servers.gfl.map_start_time = startedSec;
      }
    }
  }

  // 4. Direct Browser GFL Soundtrack Intel Enrichment (cached per map)
  const activeMap = payload.servers?.gfl?.map || payload.gfl_match_now?.map;
  if (activeMap && activeMap !== '-') {
    if (cachedGflMusics && cachedGflMusics.map === activeMap) {
      payload.gfl_map_musics = cachedGflMusics.musics;
    } else {
      try {
        let mRes = await fetch(
          `https://zegraph.xyz/data/api/servers/65bdad6379cefd7ebcecce5c/maps/${encodeURIComponent(activeMap)}/musics`,
          { signal: AbortSignal.timeout(4000) }
        );
        let musicItems: MapMusicEntry[] = [];
        if (mRes.ok) {
          const mJson = await mRes.json();
          if (Array.isArray(mJson?.data)) {
            musicItems = mJson.data;
          }
        } else if (activeMap.endsWith('_p')) {
          const stripped = activeMap.slice(0, -2);
          mRes = await fetch(
            `https://zegraph.xyz/data/api/servers/65bdad6379cefd7ebcecce5c/maps/${encodeURIComponent(stripped)}/musics`,
            { signal: AbortSignal.timeout(4000) }
          );
          if (mRes.ok) {
            const mJson = await mRes.json();
            if (Array.isArray(mJson?.data)) {
              musicItems = mJson.data;
            }
          }
        }
        cachedGflMusics = { map: activeMap, musics: musicItems };
        payload.gfl_map_musics = musicItems;
      } catch {
        // Optional soundtrack enrichment
      }
    }
  }

  return payload;
}

/**
 * High-performance telemetry fetcher with in-flight Promise deduplication.
 * Prevents multiple concurrent components from making redundant requests to Render / zegraph.
 */
export function fetchLiveTelemetry(): Promise<LiveTelemetryPayload | null> {
  if (inFlightTelemetryPromise) {
    return inFlightTelemetryPromise;
  }
  inFlightTelemetryPromise = executeFetchLiveTelemetry().finally(() => {
    inFlightTelemetryPromise = null;
  });
  return inFlightTelemetryPromise;
}

/**
 * Returns the timestamp (in seconds) when the current map started.
 * Prioritizes the authoritative serverTimestamp (calibrated from live player connection durations)
 * and falls back to client-side localStorage tracking if unavailable.
 */
export function getMapStartTime(serverId: string, currentMap?: string, serverTimestamp?: number): number {
  if (!currentMap || currentMap === '-' || currentMap === 'Unknown') {
    return Math.floor(Date.now() / 1000);
  }
  const key = `ze_map_start_${serverId}`;
  const now = Math.floor(Date.now() / 1000);

  // 1. Authoritative serverTimestamp from Render A2S player duration calibration
  if (serverTimestamp && serverTimestamp > 0 && serverTimestamp <= now) {
    try {
      localStorage.setItem(key, JSON.stringify({ map: currentMap, startTime: serverTimestamp }));
    } catch {
      // ignore
    }
    return serverTimestamp;
  }

  // 2. Client fallback via localStorage
  try {
    const stored = localStorage.getItem(key);
    if (stored) {
      const parsed = JSON.parse(stored);
      if (parsed.map === currentMap && typeof parsed.startTime === 'number' && parsed.startTime <= now) {
        return parsed.startTime;
      }
    }
  } catch {
    // ignore
  }

  const startTime = now;
  try {
    localStorage.setItem(key, JSON.stringify({ map: currentMap, startTime }));
  } catch {
    // ignore
  }
  return startTime;
}

/**
 * Formats elapsed seconds into clean integer MM:SS (or H:MM:SS if >= 1 hour).
 * Strictly floors the seconds to avoid any sub-second fractions or decimals.
 */
export function formatMapElapsed(totalSeconds: number): string {
  if (totalSeconds < 0 || isNaN(totalSeconds)) totalSeconds = 0;
  const floored = Math.floor(totalSeconds);
  const hrs = Math.floor(floored / 3600);
  const mins = Math.floor((floored % 3600) / 60);
  const secs = floored % 60;
  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Returns the primary CDN thumbnail image URL for a given CS2 Zombie Escape map from zegraph.xyz.
 * Preserves the actual map name while stripping any workshop directory prefixes.
 */
export function getMapThumbnailUrl(mapName?: string): string {
  if (!mapName || mapName === '-' || mapName === 'Unknown') {
    return '/images/map_placeholder.svg';
  }
  let clean = mapName.trim().toLowerCase();
  // Strip workshop path prefix if any (e.g. workshop/12345/ze_map -> ze_map)
  if (clean.includes('/')) {
    clean = clean.split('/').pop() || clean;
  }
  return `https://zegraph.xyz/thumbnails/medium/730_cs2--${clean}.jpg`;
}

/**
 * Universal multi-prefix error cascade for zegraph.xyz map thumbnails:
 * 1. 730_cs2--<map>.jpg (standard CS2 release)
 * 2. workshop--<map>.jpg (CS2 community workshop maps, e.g. zm_dust_v3, ze_scp, ze_obj_blue_depth)
 * 3. 730_cs2--<stripped>.jpg (stripped _p / version suffix, e.g. ze_fapescape_rote)
 * 4. 730--<map>.jpg (legacy CS:GO archive)
 * 5. /images/map_placeholder.svg (sleek fallback placeholder)
 */
export function handleMapImageFallback(e: React.SyntheticEvent<HTMLImageElement, Event>) {
  const target = e.target as HTMLImageElement;
  const currentSrc = target.src;
  if (currentSrc.includes('730_cs2--')) {
    target.src = currentSrc.replace('730_cs2--', 'workshop--');
  } else if (currentSrc.includes('workshop--')) {
    const match = currentSrc.match(/workshop--(.+?)\.jpg$/);
    if (match && /_(?:p|v\d+[\w]*|[a-z]\d+[\w]*|rc\d+|beta\d*|final|test)$/i.test(match[1])) {
      const stripped = match[1].replace(/_(?:p|v\d+[\w]*|[a-z]\d+[\w]*|rc\d+|beta\d*|final|test)$/i, '');
      target.src = currentSrc.replace(`workshop--${match[1]}.jpg`, `730_cs2--${stripped}.jpg`);
    } else {
      target.src = currentSrc.replace('workshop--', '730--');
    }
  } else if (currentSrc.includes('730--')) {
    target.src = '/images/map_placeholder.svg';
  } else {
    target.src = '/images/map_placeholder.svg';
  }
}

/**
 * Returns the 3D map viewer URL hosted by cybo at maps.cybo.dev.
 */
export function getMap3DViewerUrl(mapName?: string): string {
  if (!mapName || mapName === '-' || mapName === 'Unknown') {
    return 'https://maps.cybo.dev/';
  }
  return `https://maps.cybo.dev/?map=${encodeURIComponent(mapName.trim())}`;
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
