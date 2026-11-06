import React, { useState, useEffect } from 'react';
import { 
  type LiveServerInfo, 
  type GeronimoPresence,
  formatMapElapsed, 
  getMapStartTime, 
  fetchLiveTelemetry,
  getMapThumbnailUrl 
} from '../utils/serverQuery';
import { 
  Gamepad2, 
  Play, 
  Sparkles, 
  Clock, 
  Users, 
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Flame,
  Compass
} from 'lucide-react';

interface GeronimoDiscordPresenceProps {
  gflTelemetry?: LiveServerInfo;
  presence?: GeronimoPresence;
}

export const GeronimoDiscordPresence: React.FC<GeronimoDiscordPresenceProps> = ({ 
  gflTelemetry: propTelemetry,
  presence: propPresence
}) => {
  const [internalTelemetry, setInternalTelemetry] = useState<LiveServerInfo | undefined>(propTelemetry);
  const [internalPresence, setInternalPresence] = useState<GeronimoPresence | undefined>(propPresence);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [nowSec, setNowSec] = useState(() => Math.floor(Date.now() / 1000));

  // Fetch telemetry & presence if not passed via props
  useEffect(() => {
    if (propTelemetry) setInternalTelemetry(propTelemetry);
    if (propPresence) setInternalPresence(propPresence);
    if (propTelemetry && propPresence) return;

    const load = async () => {
      try {
        const data = await fetchLiveTelemetry();
        if (data?.servers?.['gfl']) {
          setInternalTelemetry(data.servers['gfl']);
        }
        if (data?.geronimo_presence) {
          setInternalPresence(data.geronimo_presence);
        }
      } catch {
        // ignore
      }
    };
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, [propTelemetry, propPresence]);

  const gflTelemetry = propTelemetry || internalTelemetry;
  const presence = propPresence || internalPresence;

  // 1-second ticker for live map timer
  useEffect(() => {
    const timer = setInterval(() => {
      setNowSec(Math.floor(Date.now() / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const isPlayerOnGFL = Boolean(
    gflTelemetry?.players_list?.some((p) => p.name.toLowerCase().includes('geronimo'))
  );

  // Determine current active presence state: 'in_server' | 'main_menu' | 'other_game' | 'online' | 'offline'
  let state: 'in_server' | 'main_menu' | 'other_game' | 'online' | 'offline' = 'online';
  if (presence?.state === 'in_server' || isPlayerOnGFL) {
    state = 'in_server';
  } else if (presence?.state === 'main_menu') {
    state = 'main_menu';
  } else if (presence?.state === 'other_game') {
    state = 'other_game';
  } else if (presence?.in_game) {
    state = 'main_menu';
  } else if (presence?.online !== false && presence?.state !== 'offline') {
    state = 'online';
  } else {
    state = 'offline';
  }

  // Active Map, Server & Status
  const currentMap = state === 'in_server'
    ? (presence?.map && presence.map !== '-' && presence.map !== 'Idle' ? presence.map : (gflTelemetry?.map && gflTelemetry.map !== '-' ? gflTelemetry.map : 'ze_eizures_b1_1'))
    : (state === 'main_menu' ? 'In Main Menu' : state === 'other_game' ? (presence?.game || 'Steam Game') : state === 'online' ? 'Idle' : 'Offline');

  // Player display matching server telemetry exactly
  const playerDisplay = state === 'in_server'
    ? (presence?.players && presence.players !== '-/-' && presence.players !== 'N/A' ? presence.players : (gflTelemetry?.players && gflTelemetry.players !== '-/-' ? gflTelemetry.players : '62/64'))
    : 'N/A';

  // Direct game connection link
  const connectUrl = presence?.connect_url || 'steam://connect/74.91.124.21:27015';

  // Live map start time & duration (only active when in server)
  const mapStart = getMapStartTime('gfl', currentMap, gflTelemetry?.map_start_time);
  const mapDuration = Math.max(0, nowSec - mapStart);
  const mapThumbnail = getMapThumbnailUrl(currentMap);

  // If collapsed: keep the exact same width w-[340px] so there is zero horizontal jumping/distortion
  if (isCollapsed) {
    return (
      <aside 
        aria-label="Geronimo Live Status"
        className="fixed bottom-4 left-4 z-40 w-[340px] max-w-[calc(100vw-2rem)] bg-[#111214]/95 hover:bg-[#181a1f] border border-[#2b2d31] hover:border-cyan-500/50 rounded-xl shadow-[0_12px_40px_rgba(0,0,0,0.85)] backdrop-blur-xl transition-all cursor-pointer group"
        onClick={() => setIsCollapsed(false)}
        title="Click to expand Geronimo's Live Presence"
      >
        <div className="flex items-center justify-between px-3.5 py-2.5">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="relative flex-shrink-0">
              <div className="w-8 h-8 rounded-full overflow-hidden border border-[#23a55a] shadow-[0_0_10px_rgba(35,165,90,0.4)]">
                <img
                  src="/images/geronimo_steam_avatar.jpg"
                  alt="Geronimo"
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = '/profile_avatar_edge_to_edge.jpg';
                  }}
                />
              </div>
              <span className={`absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-[#111214] ${
                state === 'in_server' ? 'bg-[#23a55a]' : state === 'main_menu' ? 'bg-amber-400' : state === 'other_game' ? 'bg-purple-400' : state === 'online' ? 'bg-[#23a55a]' : 'bg-slate-500'
              }`} />
            </div>

            <div className="flex items-center gap-1.5 text-xs font-sans min-w-0 truncate">
              <span className="font-bold text-white group-hover:text-cyan-300 transition-colors flex-shrink-0">
                Geronimo
              </span>
              <span className="text-[#949ba4]">&bull;</span>
              <span className="truncate font-medium">
                {state === 'in_server' ? (
                  <span className="text-[#23a55a] flex items-center gap-1 truncate">
                    <span>In ZE Server</span>
                    <span className="text-cyan-400 font-code font-bold ml-1">⏱️ {formatMapElapsed(mapDuration)}</span>
                  </span>
                ) : state === 'main_menu' ? (
                  <span className="text-amber-400">CS2 Menu</span>
                ) : state === 'other_game' ? (
                  <span className="text-purple-300 truncate">{presence?.game || 'In-Game'}</span>
                ) : state === 'online' ? (
                  <span className="text-slate-400">Idle on Steam</span>
                ) : (
                  <span className="text-slate-400">Offline</span>
                )}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-1 text-slate-400 group-hover:text-cyan-400 transition-colors flex-shrink-0 ml-2">
            <ChevronUp className="w-4 h-4 group-hover:-translate-y-0.5 transition-transform" />
          </div>
        </div>
      </aside>
    );
  }

  // Expanded Floating Rich Presence Card - Reverted to compact w-[340px] with enlarged contents
  return (
    <aside 
      aria-label="Geronimo Discord Live Presence"
      className="fixed bottom-4 left-4 z-40 w-[340px] max-w-[calc(100vw-2rem)] p-3.5 rounded-xl bg-[#111214]/95 border border-[#2b2d31] hover:border-slate-700/80 shadow-[0_14px_45px_rgba(0,0,0,0.88)] backdrop-blur-xl transition-all duration-300 font-sans"
    >
      {/* Top Header */}
      <div className="flex items-center justify-between gap-2 border-b border-[#2b2d31]/80 pb-2 mb-2.5">
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full inline-block ${
            state === 'in_server' ? 'bg-[#23a55a] animate-pulse' : 
            state === 'main_menu' ? 'bg-amber-400' : 
            state === 'other_game' ? 'bg-purple-400' : 
            state === 'online' ? 'bg-[#23a55a]' :
            'bg-slate-500'
          }`} />
          <span className="text-[10px] font-sans font-extrabold tracking-wider text-[#dbdee1] uppercase flex items-center gap-1.5">
            {state === 'in_server' ? 'PLAYING CS2 ZOMBIE ESCAPE' : 
             state === 'main_menu' ? 'COUNTER-STRIKE 2' : 
             state === 'other_game' ? `PLAYING ${presence?.game?.toUpperCase() || 'ON STEAM'}` : 
             state === 'online' ? 'ONLINE ON STEAM' :
             'OFFLINE ON STEAM'}
          </span>
        </div>

        {/* Minimize Button */}
        <button
          onClick={() => setIsCollapsed(true)}
          className="p-1 rounded hover:bg-[#2b2d31] text-slate-400 hover:text-white transition-colors cursor-pointer"
          title="Minimize live presence"
          aria-label="Minimize presence card"
        >
          <ChevronDown className="w-4 h-4" />
        </button>
      </div>

      {/* Main Profile Row */}
      <div className="flex items-center gap-3">
        {/* Steam Avatar with Status Dot */}
        <div className="relative flex-shrink-0">
          <div className="w-11 h-11 rounded-full overflow-hidden border-2 border-[#23a55a] shadow-[0_0_12px_rgba(35,165,90,0.35)]">
            <img
              src="/images/geronimo_steam_avatar.jpg"
              alt="Geronimo Steam Avatar"
              className="w-full h-full object-cover"
              onError={(e) => {
                (e.target as HTMLImageElement).src = '/profile_avatar_edge_to_edge.jpg';
              }}
            />
          </div>
          {/* Status Dot */}
          <div className={`absolute bottom-0 right-0 w-3.5 h-3.5 rounded-full border-2 border-[#111214] flex items-center justify-center ${
            state === 'in_server' ? 'bg-[#23a55a]' : 
            state === 'main_menu' ? 'bg-amber-400' : 
            state === 'other_game' ? 'bg-purple-400' : 
            state === 'online' ? 'bg-[#23a55a]' :
            'bg-slate-500'
          }`}>
            <span className="w-1 h-1 rounded-full bg-white" />
          </div>
        </div>

        {/* Presence Body */}
        <div className="flex-1 min-w-0">
          {/* Username & Badges */}
          <div className="flex items-center gap-1.5 mb-0.5 flex-wrap">
            <h4 className="text-sm font-bold font-sans text-white truncate">
              Geronimo
            </h4>
            <span className="px-1.5 py-0.2 rounded text-[9px] font-sans font-semibold bg-[#2b2d31] text-[#b5bac1]">
              HOST
            </span>
            {state === 'in_server' ? (
              <span className="px-1.5 py-0.2 rounded text-[9px] font-sans font-bold bg-[#23a55a]/20 text-[#23a55a] border border-[#23a55a]/40 flex items-center gap-1">
                <Sparkles className="w-2 h-2" /> IN-SERVER
              </span>
            ) : state === 'main_menu' ? (
              <span className="px-1.5 py-0.2 rounded text-[9px] font-sans font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center gap-1">
                <Gamepad2 className="w-2 h-2" /> MAIN MENU
              </span>
            ) : state === 'other_game' ? (
              <span className="px-1.5 py-0.2 rounded text-[9px] font-sans font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40 flex items-center gap-1">
                <Flame className="w-2 h-2" /> IN-GAME
              </span>
            ) : state === 'online' ? (
              <span className="px-1.5 py-0.2 rounded text-[9px] font-sans font-bold bg-slate-800 text-slate-300 border border-slate-700 flex items-center gap-1">
                <Clock className="w-2 h-2 text-slate-400" /> IDLE
              </span>
            ) : (
              <span className="px-1.5 py-0.2 rounded text-[9px] font-sans font-bold bg-slate-800 text-slate-400 border border-slate-700/60 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-slate-500 inline-block" /> OFFLINE
              </span>
            )}
          </div>

          {/* Activity Title */}
          <div className="text-xs font-bold font-sans text-[#f2f3f5] truncate flex items-center gap-1.5">
            {state === 'in_server' || state === 'main_menu' ? (
              <>
                <Gamepad2 className="w-3.5 h-3.5 text-[#5865f2] flex-shrink-0" />
                <span className="truncate">Counter-Strike 2</span>
              </>
            ) : state === 'other_game' ? (
              <>
                <Gamepad2 className="w-3.5 h-3.5 text-purple-400 flex-shrink-0" />
                <span className="truncate">{presence?.game || 'Steam Game'}</span>
              </>
            ) : state === 'online' ? (
              <>
                <Compass className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
                <span className="truncate text-slate-300">Steam Community</span>
              </>
            ) : (
              <>
                <span className="w-2.5 h-2.5 rounded-full bg-slate-500 flex-shrink-0" />
                <span className="truncate text-slate-400">Offline</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Enlarged Contents Block - Beautifully fills width with no awkward dead space */}
      {state === 'in_server' ? (
        <div className="mt-2.5 p-2 rounded-lg bg-[#18191c] border border-[#2b2d31]/80 flex items-center gap-2.5">
          {/* Prominent Map Thumbnail */}
          <div className="relative w-20 h-13 rounded-md overflow-hidden border border-slate-700/80 bg-slate-950 flex-shrink-0 shadow-sm group">
            <img 
              src={mapThumbnail} 
              alt={currentMap} 
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              onError={(e) => {
                (e.target as HTMLImageElement).src = '/images/hero_ze_backdrop.jpg';
              }}
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent pointer-events-none" />
            <span className="absolute bottom-0.5 left-1 text-[8px] font-cyber text-fuchsia-300 font-bold uppercase drop-shadow">
              MAP
            </span>
          </div>

          {/* Map Info & Telemetry */}
          <div className="flex-1 min-w-0">
            <span className="text-[10px] text-slate-400 uppercase font-semibold block leading-none mb-0.5">
              Active Map
            </span>
            <strong className="text-xs font-code font-bold text-fuchsia-300 truncate block leading-tight" title={currentMap}>
              {currentMap}
            </strong>
            
            <div className="flex items-center gap-2 text-[11px] font-sans text-slate-300 mt-1">
              <span className="flex items-center gap-1 text-[#b5bac1]">
                <Users className="w-3 h-3 text-[#23a55a]" />
                <strong className="text-white font-semibold">{playerDisplay}</strong>
              </span>
              <span className="text-slate-600">&bull;</span>
              <span className="text-cyan-400 font-code font-bold flex items-center gap-0.5 bg-cyan-950/70 px-1.5 py-0.2 rounded border border-cyan-500/30">
                <Clock className="w-2.5 h-2.5 text-cyan-400 animate-pulse" />
                {formatMapElapsed(mapDuration)}
              </span>
            </div>
          </div>
        </div>
      ) : state === 'main_menu' ? (
        <div className="mt-2.5 p-2 rounded-lg bg-[#18191c] border border-[#2b2d31]/80 flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center flex-shrink-0">
            <Gamepad2 className="w-4 h-4 text-amber-400" />
          </div>
          <div className="flex-1 min-w-0">
            <span className="text-[10px] text-slate-400 uppercase font-semibold block leading-none mb-0.5">
              Current Status
            </span>
            <span className="text-xs text-amber-300 font-semibold block truncate">
              Idle in CS2 Main Menu
            </span>
          </div>
        </div>
      ) : state === 'other_game' ? (
        <div className="mt-2.5 p-2 rounded-lg bg-[#18191c] border border-[#2b2d31]/80 flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center flex-shrink-0">
            <Flame className="w-4 h-4 text-purple-400" />
          </div>
          <div className="flex-1 min-w-0">
            <span className="text-[10px] text-slate-400 uppercase font-semibold block leading-none mb-0.5">
              Playing on Steam
            </span>
            <span className="text-xs text-purple-300 font-semibold block truncate">
              {presence?.game || 'In-Game'}
            </span>
          </div>
        </div>
      ) : state === 'online' ? (
        <div className="mt-2.5 p-2 rounded-lg bg-[#18191c] border border-[#2b2d31]/80 flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center flex-shrink-0">
            <Compass className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="flex-1 min-w-0">
            <span className="text-[10px] text-slate-400 uppercase font-semibold block leading-none mb-0.5">
              Current Status
            </span>
            <span className="text-xs text-slate-300 font-semibold block truncate">
              Idle on Steam
            </span>
          </div>
        </div>
      ) : (
        <div className="mt-2.5 p-2 rounded-lg bg-[#18191c] border border-[#2b2d31]/80 flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-slate-800/60 border border-slate-700/60 flex items-center justify-center flex-shrink-0">
            <span className="w-2.5 h-2.5 rounded-full bg-slate-500" />
          </div>
          <div className="flex-1 min-w-0">
            <span className="text-[10px] text-slate-400 uppercase font-semibold block leading-none mb-0.5">
              Current Status
            </span>
            <span className="text-xs text-slate-400 font-semibold block truncate">
              Offline
            </span>
          </div>
        </div>
      )}

      {/* Action Buttons - Snug, Comfortable Fit */}
      <div className="mt-2.5 pt-2 border-t border-[#2b2d31]/80">
        {state === 'in_server' ? (
          <div className="grid grid-cols-2 gap-2">
            <a
              href={connectUrl}
              className="flex items-center justify-center gap-1.5 px-3 py-2 bg-[#5865f2] hover:bg-[#4752c4] text-white font-sans text-xs font-bold rounded-lg shadow-sm transition-all cursor-pointer transform hover:-translate-y-0.5"
              title="Launch CS2 and join Geronimo on server"
            >
              <Play className="w-3 h-3 fill-current" />
              <span>Join Game</span>
            </a>
            <a
              href="https://steamcommunity.com/profiles/76561198143793864/"
              target="_blank"
              rel="noreferrer"
              className="flex items-center justify-center gap-1.5 px-3 py-2 bg-[#2b2d31] hover:bg-[#35373c] text-[#dbdee1] hover:text-white font-sans text-xs font-semibold rounded-lg transition-colors cursor-pointer border border-[#3f4147]/50"
              title="View Geronimo's Steam Community Profile"
            >
              <span>Steam Profile</span>
              <ExternalLink className="w-3 h-3 text-slate-400" />
            </a>
          </div>
        ) : state === 'main_menu' ? (
          <div className="grid grid-cols-2 gap-2">
            <a
              href="steam://rungameid/730"
              className="flex items-center justify-center gap-1.5 px-3 py-2 bg-[#2b2d31] hover:bg-[#35373c] text-cyan-300 hover:text-white font-sans text-xs font-semibold rounded-lg transition-colors cursor-pointer border border-[#3f4147]/50"
              title="Launch Counter-Strike 2"
            >
              <Gamepad2 className="w-3 h-3 text-cyan-400" />
              <span>Launch CS2</span>
            </a>
            <a
              href="https://steamcommunity.com/profiles/76561198143793864/"
              target="_blank"
              rel="noreferrer"
              className="flex items-center justify-center gap-1.5 px-3 py-2 bg-[#2b2d31] hover:bg-[#35373c] text-[#dbdee1] hover:text-white font-sans text-xs font-semibold rounded-lg transition-colors cursor-pointer border border-[#3f4147]/50"
              title="View Geronimo's Steam Community Profile"
            >
              <span>Steam Profile</span>
              <ExternalLink className="w-3 h-3 text-slate-400" />
            </a>
          </div>
        ) : (
          <a
            href="https://steamcommunity.com/profiles/76561198143793864/"
            target="_blank"
            rel="noreferrer"
            className="w-full flex items-center justify-center gap-1.5 px-3 py-2 bg-[#2b2d31] hover:bg-[#35373c] text-[#dbdee1] hover:text-white font-sans text-xs font-semibold rounded-lg transition-colors cursor-pointer border border-[#3f4147]/50"
            title="View Geronimo's Steam Community Profile"
          >
            <span>View Steam Profile</span>
            <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
          </a>
        )}
      </div>
    </aside>
  );
};
