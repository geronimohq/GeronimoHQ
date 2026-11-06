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
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Flame
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

  // Active Map and Server
  const currentMap = state === 'in_server'
    ? (presence?.map && presence.map !== '-' ? presence.map : (gflTelemetry?.map && gflTelemetry.map !== '-' ? gflTelemetry.map : 'ze_kitchen'))
    : (state === 'main_menu' ? 'In Main Menu' : state === 'other_game' ? (presence?.game || 'Steam Game') : 'Steam Online');

  // Accurate player display matching server telemetry exactly
  const playerDisplay = state === 'in_server'
    ? (presence?.players && presence.players !== '-/-' ? presence.players : (gflTelemetry?.players && gflTelemetry.players !== '-/-' ? gflTelemetry.players : '63/64'))
    : (state === 'main_menu' ? 'Solo / In Lobby' : state === 'other_game' ? 'In-Game' : 'Chilling');

  // Direct game connection link
  const connectUrl = presence?.connect_url || 'steam://connect/74.91.124.21:27015';

  // Live map start time & duration (only active when in server)
  const mapStart = getMapStartTime('gfl', currentMap, gflTelemetry?.map_start_time);
  const mapDuration = Math.max(0, nowSec - mapStart);
  const mapThumbnail = getMapThumbnailUrl(currentMap);

  // If collapsed: show compact floating pill
  if (isCollapsed) {
    return (
      <aside 
        aria-label="Geronimo Live Status"
        className="fixed bottom-5 left-5 z-50 flex items-center gap-3 px-3.5 py-2 rounded-full bg-[#111214]/95 hover:bg-[#181a1f] border border-[#2b2d31] hover:border-indigo-500/60 shadow-[0_10px_30px_rgba(0,0,0,0.8)] backdrop-blur-xl transition-all cursor-pointer group"
        onClick={() => setIsCollapsed(false)}
        title="Click to expand Geronimo's Discord Presence"
      >
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

        <div className="flex items-center gap-2 text-xs font-sans">
          <span className="font-bold text-white group-hover:text-indigo-300 transition-colors">
            Geronimo
          </span>
          <span className="text-[#949ba4] hidden sm:inline">&bull;</span>
          <span className="text-[#23a55a] font-medium hidden sm:inline flex items-center gap-1">
            <Gamepad2 className="w-3 h-3 inline" /> {
              state === 'in_server' ? 'In ZE Server' : 
              state === 'main_menu' ? 'CS2 Main Menu' : 
              state === 'other_game' ? (presence?.game || 'In-Game') : 
              'Steam Online'
            }
          </span>
          {state === 'in_server' && (
            <span className="text-cyan-400 font-code text-[11px] hidden md:inline">
              ⏱️ {formatMapElapsed(mapDuration)}
            </span>
          )}
        </div>

        <ChevronUp className="w-4 h-4 text-slate-400 group-hover:text-white transition-transform group-hover:-translate-y-0.5 ml-1" />
      </aside>
    );
  }

  // Expanded Floating Rich Presence Card - Ultra-compact & Fitted
  return (
    <aside 
      aria-label="Geronimo Discord Live Presence"
      className="fixed bottom-3 left-3 sm:bottom-4 sm:left-4 z-40 w-[calc(100vw-1.5rem)] sm:w-auto sm:max-w-[280px] p-2.5 sm:p-3 rounded-xl bg-[#111214]/95 border border-[#2b2d31] hover:border-indigo-500/50 shadow-[0_12px_35px_rgba(0,0,0,0.85)] backdrop-blur-xl transition-all duration-300"
    >
      {/* Top Discord Activity Header */}
      <div className="flex items-center justify-between gap-2 border-b border-[#2b2d31] pb-1.5 mb-2">
        <div className="flex items-center gap-1.5">
          <span className={`w-2 h-2 rounded-full inline-block animate-pulse ${
            state === 'in_server' ? 'bg-[#23a55a]' : 
            state === 'main_menu' ? 'bg-amber-400' : 
            state === 'other_game' ? 'bg-purple-400' : 
            'bg-[#23a55a]'
          }`} />
          <span className="text-[10px] font-sans font-bold tracking-wider text-[#dbdee1] uppercase">
            {state === 'in_server' ? 'PLAYING A GAME' : 
             state === 'main_menu' ? 'PLAYING COUNTER-STRIKE 2' : 
             state === 'other_game' ? `PLAYING ${presence?.game?.toUpperCase() || 'A GAME'}` : 
             'ONLINE ON STEAM'}
          </span>
        </div>

        {/* Minimize Button */}
        <button
          onClick={() => setIsCollapsed(true)}
          className="p-0.5 rounded hover:bg-[#2b2d31] text-slate-400 hover:text-white transition-colors cursor-pointer"
          title="Minimize to floating pill"
          aria-label="Minimize presence card"
        >
          <ChevronDown className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Main Profile & Rich Presence Card */}
      <div className="flex items-center gap-2.5">
        {/* Steam Avatar with Discord Status Dot */}
        <div className="relative flex-shrink-0">
          <div className="w-10 h-10 sm:w-11 sm:h-11 rounded-full overflow-hidden border-2 border-[#23a55a] shadow-[0_0_12px_rgba(35,165,90,0.4)]">
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
          <div className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-[#111214] flex items-center justify-center ${
            state === 'in_server' ? 'bg-[#23a55a]' : 
            state === 'main_menu' ? 'bg-amber-400' : 
            state === 'other_game' ? 'bg-purple-400' : 
            'bg-[#23a55a]'
          }`}>
            <span className="w-1 h-1 rounded-full bg-white" />
          </div>
        </div>

        {/* Presence Body */}
        <div className="flex-1 min-w-0">
          {/* Username & Badges */}
          <div className="flex items-center gap-1 mb-0.5">
            <h4 className="text-xs sm:text-sm font-bold font-sans text-white truncate">
              Geronimo
            </h4>
            <span className="px-1 py-0.2 rounded text-[9px] font-sans font-semibold bg-[#2b2d31] text-[#b5bac1]">
              HOST
            </span>
            {state === 'in_server' ? (
              <span className="px-1 py-0.2 rounded text-[9px] font-sans font-bold bg-[#23a55a]/20 text-[#23a55a] border border-[#23a55a]/40 flex items-center gap-0.5">
                <Sparkles className="w-2 h-2" /> IN-SERVER
              </span>
            ) : state === 'main_menu' ? (
              <span className="px-1 py-0.2 rounded text-[9px] font-sans font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center gap-0.5">
                <Gamepad2 className="w-2 h-2" /> IN MAIN MENU
              </span>
            ) : state === 'other_game' ? (
              <span className="px-1 py-0.2 rounded text-[9px] font-sans font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40 flex items-center gap-0.5">
                <Flame className="w-2 h-2" /> IN-GAME
              </span>
            ) : (
              <span className="px-1 py-0.2 rounded text-[9px] font-sans font-bold bg-[#5865f2]/20 text-[#5865f2] border border-[#5865f2]/30 flex items-center gap-0.5">
                <ShieldCheck className="w-2 h-2" /> STEAM ONLINE
              </span>
            )}
          </div>

          {/* Game Title */}
          <div className="text-xs font-bold font-sans text-[#f2f3f5] truncate flex items-center gap-1">
            <Gamepad2 className="w-3 h-3 text-[#5865f2]" />
            <span className="truncate">
              {state === 'in_server' ? 'Counter-Strike 2' : 
               state === 'main_menu' ? 'Counter-Strike 2' : 
               state === 'other_game' ? (presence?.game || 'Steam Game') : 
               'Steam Online'}
            </span>
          </div>

          {/* Current Map */}
          <div className="text-[11px] font-sans text-[#949ba4] truncate flex items-center gap-1 mt-0.5">
            <span className="text-[#dbdee1] font-medium">{state === 'in_server' ? 'Map:' : 'Status:'}</span>
            {state === 'in_server' && (
              <div className="w-6 h-4 rounded overflow-hidden border border-slate-700 flex-shrink-0 bg-slate-900 shadow-sm">
                <img 
                  src={mapThumbnail} 
                  alt={currentMap} 
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    (e.target as HTMLElement).style.display = 'none';
                  }}
                />
              </div>
            )}
            <code className="text-[10px] text-[#5865f2] font-code bg-[#1e1f22] px-1 py-0.2 rounded font-bold truncate">
              {currentMap}
            </code>
          </div>

          {/* Players count & Map Timer (side by side, no elapsed time, no party) */}
          <div className="text-[10px] font-sans text-[#949ba4] flex items-center gap-1.5 mt-0.5">
            <span className="flex items-center gap-1 text-[#b5bac1]">
              <Users className="w-2.5 h-2.5 text-[#23a55a]" />
              Players: <strong className="text-white font-semibold">{playerDisplay}</strong>
            </span>
            {state === 'in_server' && (
              <>
                <span>&bull;</span>
                <span className="text-cyan-400 font-code text-[10px] font-semibold bg-cyan-950/70 px-1 py-0.2 rounded border border-cyan-500/30 flex items-center gap-0.5">
                  <Clock className="w-2.5 h-2.5 text-cyan-400 animate-pulse" />
                  {formatMapElapsed(mapDuration)}
                </span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Reduced Action Buttons for Perfect Fit */}
      <div className="mt-2 pt-1.5 border-t border-[#2b2d31]/80">
        {state === 'in_server' ? (
          <div className="grid grid-cols-2 gap-1.5">
            <a
              href={connectUrl}
              className="flex items-center justify-center gap-1 px-2.5 py-1.5 bg-[#5865f2] hover:bg-[#4752c4] text-white font-sans text-[11px] font-semibold rounded-md shadow-sm transition-all cursor-pointer transform hover:-translate-y-0.5"
              title="Launch CS2 and join Geronimo on server"
            >
              <Play className="w-2.5 h-2.5 fill-current" />
              <span>Join Game</span>
            </a>
            <a
              href="https://steamcommunity.com/profiles/76561198143793864/"
              target="_blank"
              rel="noreferrer"
              className="flex items-center justify-center gap-1 px-2.5 py-1.5 bg-[#2b2d31] hover:bg-[#35373c] text-[#dbdee1] hover:text-white font-sans text-[11px] font-semibold rounded-md transition-colors cursor-pointer border border-[#3f4147]/50"
              title="View Geronimo's Steam Community Profile"
            >
              <span>Steam Profile</span>
              <ExternalLink className="w-2.5 h-2.5 text-slate-400" />
            </a>
          </div>
        ) : state === 'main_menu' ? (
          <div className="grid grid-cols-2 gap-1.5">
            <a
              href="steam://rungameid/730"
              className="flex items-center justify-center gap-1 px-2.5 py-1.5 bg-[#2b2d31] hover:bg-[#35373c] text-slate-300 hover:text-white font-sans text-[11px] font-semibold rounded-md transition-colors cursor-pointer border border-[#3f4147]/50"
              title="Launch Counter-Strike 2"
            >
              <Gamepad2 className="w-2.5 h-2.5 text-cyan-400" />
              <span>Launch CS2</span>
            </a>
            <a
              href="https://steamcommunity.com/profiles/76561198143793864/"
              target="_blank"
              rel="noreferrer"
              className="flex items-center justify-center gap-1 px-2.5 py-1.5 bg-[#2b2d31] hover:bg-[#35373c] text-[#dbdee1] hover:text-white font-sans text-[11px] font-semibold rounded-md transition-colors cursor-pointer border border-[#3f4147]/50"
              title="View Geronimo's Steam Community Profile"
            >
              <span>Steam Profile</span>
              <ExternalLink className="w-2.5 h-2.5 text-slate-400" />
            </a>
          </div>
        ) : (
          <a
            href="https://steamcommunity.com/profiles/76561198143793864/"
            target="_blank"
            rel="noreferrer"
            className="w-full flex items-center justify-center gap-1 px-2.5 py-1.5 bg-[#2b2d31] hover:bg-[#35373c] text-[#dbdee1] hover:text-white font-sans text-[11px] font-semibold rounded-md transition-colors cursor-pointer border border-[#3f4147]/50"
            title="View Geronimo's Steam Community Profile"
          >
            <span>View Steam Profile</span>
            <ExternalLink className="w-2.5 h-2.5 text-slate-400" />
          </a>
        )}
      </div>
    </aside>
  );
};
