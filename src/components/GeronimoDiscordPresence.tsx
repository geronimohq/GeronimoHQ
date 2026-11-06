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
  } else if (presence?.online !== false) {
    state = 'online';
  } else {
    state = 'offline';
  }

  // Active Map, Server & Status
  const currentMap = state === 'in_server'
    ? (presence?.map && presence.map !== '-' && presence.map !== 'Idle' ? presence.map : (gflTelemetry?.map && gflTelemetry.map !== '-' ? gflTelemetry.map : 'ze_castlevania'))
    : (state === 'main_menu' ? 'In Main Menu' : state === 'other_game' ? (presence?.game || 'Steam Game') : 'Idle');

  // Player display matching server telemetry exactly
  const playerDisplay = state === 'in_server'
    ? (presence?.players && presence.players !== '-/-' && presence.players !== 'N/A' ? presence.players : (gflTelemetry?.players && gflTelemetry.players !== '-/-' ? gflTelemetry.players : '61/64'))
    : 'N/A';

  // Direct game connection link
  const connectUrl = presence?.connect_url || 'steam://connect/74.91.124.21:27015';

  // Live map start time & duration (only active when in server)
  const mapStart = getMapStartTime('gfl', currentMap, gflTelemetry?.map_start_time);
  const mapDuration = Math.max(0, nowSec - mapStart);
  const mapThumbnail = getMapThumbnailUrl(currentMap);

  // If collapsed: keep the exact same width w-[380px] sm:w-[415px] so there is zero horizontal jumping/distortion
  if (isCollapsed) {
    return (
      <aside 
        aria-label="Geronimo Live Status"
        className="fixed bottom-4 left-4 z-40 w-[380px] sm:w-[415px] max-w-[calc(100vw-2rem)] bg-[#111214]/95 hover:bg-[#181a1f] border border-[#2b2d31] hover:border-cyan-500/50 rounded-xl shadow-[0_12px_40px_rgba(0,0,0,0.85)] backdrop-blur-xl transition-all cursor-pointer group"
        onClick={() => setIsCollapsed(false)}
        title="Click to expand Geronimo's Live Presence"
      >
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3 min-w-0">
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
                state === 'in_server' ? 'bg-[#23a55a]' : state === 'main_menu' ? 'bg-amber-400' : state === 'other_game' ? 'bg-purple-400' : 'bg-[#23a55a]'
              }`} />
            </div>

            <div className="flex items-center gap-2 text-xs sm:text-sm font-sans min-w-0 truncate">
              <span className="font-bold text-white group-hover:text-cyan-300 transition-colors flex-shrink-0">
                Geronimo
              </span>
              <span className="text-[#949ba4]">&bull;</span>
              <span className="truncate font-medium">
                {state === 'in_server' ? (
                  <span className="text-[#23a55a] flex items-center gap-1.5 truncate">
                    <span>In ZE Server</span>
                    <span className="text-cyan-400 font-code font-bold">⏱️ {formatMapElapsed(mapDuration)}</span>
                  </span>
                ) : state === 'main_menu' ? (
                  <span className="text-amber-400">CS2 Menu</span>
                ) : state === 'other_game' ? (
                  <span className="text-purple-300 truncate">{presence?.game || 'In-Game'}</span>
                ) : (
                  <span className="text-slate-400">Idle</span>
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

  // Expanded Floating Rich Presence Card - Sized to perfect fit matching Geronimo's marker
  return (
    <aside 
      aria-label="Geronimo Discord Live Presence"
      className="fixed bottom-4 left-4 z-40 w-[380px] sm:w-[415px] max-w-[calc(100vw-2rem)] p-4 sm:p-4.5 rounded-xl bg-[#111214]/95 border border-[#2b2d31] hover:border-slate-700/80 shadow-[0_16px_50px_rgba(0,0,0,0.9)] backdrop-blur-xl transition-all duration-300 font-sans"
    >
      {/* Top Header */}
      <div className="flex items-center justify-between gap-2 border-b border-[#2b2d31]/80 pb-2.5 mb-3">
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full inline-block ${
            state === 'in_server' ? 'bg-[#23a55a] animate-pulse' : 
            state === 'main_menu' ? 'bg-amber-400' : 
            state === 'other_game' ? 'bg-purple-400' : 
            'bg-[#23a55a]'
          }`} />
          <span className="text-[11px] font-sans font-extrabold tracking-wider text-[#dbdee1] uppercase flex items-center gap-1.5">
            {state === 'in_server' ? 'PLAYING CS2 ZOMBIE ESCAPE' : 
             state === 'main_menu' ? 'COUNTER-STRIKE 2' : 
             state === 'other_game' ? `PLAYING ${presence?.game?.toUpperCase() || 'ON STEAM'}` : 
             'GERONIMO RADAR'}
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

      {/* Main Profile & Rich Presence Card */}
      <div className="flex items-center gap-3.5">
        {/* Steam Avatar with Status Dot */}
        <div className="relative flex-shrink-0">
          <div className="w-13 h-13 sm:w-14 sm:h-14 rounded-full overflow-hidden border-2 border-[#23a55a] shadow-[0_0_16px_rgba(35,165,90,0.4)]">
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
          <div className={`absolute bottom-0 right-0 w-3.5 h-3.5 sm:w-4 sm:h-4 rounded-full border-2 border-[#111214] flex items-center justify-center ${
            state === 'in_server' ? 'bg-[#23a55a]' : 
            state === 'main_menu' ? 'bg-amber-400' : 
            state === 'other_game' ? 'bg-purple-400' : 
            'bg-[#23a55a]'
          }`}>
            <span className="w-1.5 h-1.5 rounded-full bg-white" />
          </div>
        </div>

        {/* Presence Body */}
        <div className="flex-1 min-w-0">
          {/* Username & Badges */}
          <div className="flex items-center gap-1.5 mb-1 flex-wrap">
            <h4 className="text-base font-bold font-sans text-white truncate">
              Geronimo
            </h4>
            <span className="px-1.5 py-0.5 rounded text-[10px] font-sans font-semibold bg-[#2b2d31] text-[#b5bac1]">
              HOST
            </span>
            {state === 'in_server' ? (
              <span className="px-2 py-0.5 rounded text-[10px] font-sans font-bold bg-[#23a55a]/20 text-[#23a55a] border border-[#23a55a]/40 flex items-center gap-1">
                <Sparkles className="w-2.5 h-2.5" /> IN-SERVER
              </span>
            ) : state === 'main_menu' ? (
              <span className="px-2 py-0.5 rounded text-[10px] font-sans font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center gap-1">
                <Gamepad2 className="w-2.5 h-2.5" /> MAIN MENU
              </span>
            ) : state === 'other_game' ? (
              <span className="px-2 py-0.5 rounded text-[10px] font-sans font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40 flex items-center gap-1">
                <Flame className="w-2.5 h-2.5" /> IN-GAME
              </span>
            ) : (
              <span className="px-2 py-0.5 rounded text-[10px] font-sans font-bold bg-slate-800 text-slate-300 border border-slate-700 flex items-center gap-1">
                <Clock className="w-2.5 h-2.5 text-slate-400" /> IDLE
              </span>
            )}
          </div>

          {/* Activity / Game Title */}
          <div className="text-xs sm:text-sm font-bold font-sans text-[#f2f3f5] truncate flex items-center gap-1.5">
            {state === 'in_server' || state === 'main_menu' ? (
              <>
                <Gamepad2 className="w-4 h-4 text-[#5865f2] flex-shrink-0" />
                <span className="truncate">Counter-Strike 2</span>
              </>
            ) : state === 'other_game' ? (
              <>
                <Gamepad2 className="w-4 h-4 text-purple-400 flex-shrink-0" />
                <span className="truncate">{presence?.game || 'Steam Game'}</span>
              </>
            ) : (
              <>
                <Compass className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                <span className="truncate text-slate-300">Steam Community</span>
              </>
            )}
          </div>

          {/* Map or Status line */}
          <div className="text-xs font-sans text-[#949ba4] truncate flex items-center gap-1.5 mt-1">
            <span className="text-[#dbdee1] font-medium">{state === 'in_server' ? 'Map:' : 'Status:'}</span>
            {state === 'in_server' ? (
              <>
                <div className="w-7 h-4.5 rounded overflow-hidden border border-slate-700 flex-shrink-0 bg-slate-900 shadow-sm">
                  <img 
                    src={mapThumbnail} 
                    alt={currentMap} 
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      (e.target as HTMLElement).style.display = 'none';
                    }}
                  />
                </div>
                <code className="text-xs text-[#5865f2] font-code bg-[#1e1f22] px-2 py-0.5 rounded font-bold truncate max-w-[210px]">
                  {currentMap}
                </code>
              </>
            ) : state === 'main_menu' ? (
              <span className="text-amber-300/90 font-semibold px-2 py-0.5 bg-[#1e1f22] rounded text-xs border border-amber-500/30">
                In Main Menu
              </span>
            ) : state === 'other_game' ? (
              <span className="text-purple-300 font-semibold px-2 py-0.5 bg-[#1e1f22] rounded text-xs border border-purple-500/30">
                In-Game
              </span>
            ) : (
              <span className="text-slate-300 font-semibold px-2 py-0.5 bg-[#1e1f22] rounded text-xs border border-slate-800">
                Idle
              </span>
            )}
          </div>

          {/* Players count & Map Timer - ONLY VISIBLE WHEN IN SERVER */}
          {state === 'in_server' && (
            <div className="text-xs font-sans text-[#949ba4] flex items-center gap-2 mt-1.5">
              <span className="flex items-center gap-1.5 text-[#b5bac1]">
                <Users className="w-3.5 h-3.5 text-[#23a55a]" />
                Players: <strong className="text-white font-semibold">{playerDisplay}</strong>
              </span>
              <span>&bull;</span>
              <span className="text-cyan-400 font-code text-xs font-semibold bg-cyan-950/80 px-2 py-0.5 rounded border border-cyan-500/30 flex items-center gap-1">
                <Clock className="w-3 h-3 text-cyan-400 animate-pulse" />
                {formatMapElapsed(mapDuration)}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons - Comfortable Size & Spacing */}
      <div className="mt-3.5 pt-2.5 border-t border-[#2b2d31]/80">
        {state === 'in_server' ? (
          <div className="grid grid-cols-2 gap-2.5">
            <a
              href={connectUrl}
              className="flex items-center justify-center gap-1.5 px-3.5 py-2.5 bg-[#5865f2] hover:bg-[#4752c4] text-white font-sans text-xs font-bold rounded-lg shadow-sm transition-all cursor-pointer transform hover:-translate-y-0.5"
              title="Launch CS2 and join Geronimo on server"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Join Game</span>
            </a>
            <a
              href="https://steamcommunity.com/profiles/76561198143793864/"
              target="_blank"
              rel="noreferrer"
              className="flex items-center justify-center gap-1.5 px-3.5 py-2.5 bg-[#2b2d31] hover:bg-[#35373c] text-[#dbdee1] hover:text-white font-sans text-xs font-semibold rounded-lg transition-colors cursor-pointer border border-[#3f4147]/50"
              title="View Geronimo's Steam Community Profile"
            >
              <span>Steam Profile</span>
              <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
            </a>
          </div>
        ) : state === 'main_menu' ? (
          <div className="grid grid-cols-2 gap-2.5">
            <a
              href="steam://rungameid/730"
              className="flex items-center justify-center gap-1.5 px-3.5 py-2.5 bg-[#2b2d31] hover:bg-[#35373c] text-cyan-300 hover:text-white font-sans text-xs font-semibold rounded-lg transition-colors cursor-pointer border border-[#3f4147]/50"
              title="Launch Counter-Strike 2"
            >
              <Gamepad2 className="w-3.5 h-3.5 text-cyan-400" />
              <span>Launch CS2</span>
            </a>
            <a
              href="https://steamcommunity.com/profiles/76561198143793864/"
              target="_blank"
              rel="noreferrer"
              className="flex items-center justify-center gap-1.5 px-3.5 py-2.5 bg-[#2b2d31] hover:bg-[#35373c] text-[#dbdee1] hover:text-white font-sans text-xs font-semibold rounded-lg transition-colors cursor-pointer border border-[#3f4147]/50"
              title="View Geronimo's Steam Community Profile"
            >
              <span>Steam Profile</span>
              <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
            </a>
          </div>
        ) : (
          <a
            href="https://steamcommunity.com/profiles/76561198143793864/"
            target="_blank"
            rel="noreferrer"
            className="w-full flex items-center justify-center gap-1.5 px-3.5 py-2.5 bg-[#2b2d31] hover:bg-[#35373c] text-[#dbdee1] hover:text-white font-sans text-xs font-semibold rounded-lg transition-colors cursor-pointer border border-[#3f4147]/50"
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
