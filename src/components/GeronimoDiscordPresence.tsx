import React, { useState, useEffect } from 'react';
import { type LiveServerInfo, formatMapElapsed, getMapStartTime, fetchLiveTelemetry } from '../utils/serverQuery';
import { 
  Gamepad2, 
  Play, 
  Sparkles, 
  Clock, 
  Users, 
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  ExternalLink
} from 'lucide-react';

interface GeronimoDiscordPresenceProps {
  gflTelemetry?: LiveServerInfo;
}

export const GeronimoDiscordPresence: React.FC<GeronimoDiscordPresenceProps> = ({ gflTelemetry: propTelemetry }) => {
  const [internalTelemetry, setInternalTelemetry] = useState<LiveServerInfo | undefined>(propTelemetry);
  const [elapsedSeconds, setElapsedSeconds] = useState(6124); // Initial session time in seconds (~1h 42m)
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [nowSec, setNowSec] = useState(() => Math.floor(Date.now() / 1000));

  // Fetch telemetry if not passed via props
  useEffect(() => {
    if (propTelemetry) {
      setInternalTelemetry(propTelemetry);
      return;
    }
    const load = async () => {
      try {
        const data = await fetchLiveTelemetry();
        if (data?.servers?.['gfl']) {
          setInternalTelemetry(data.servers['gfl']);
        }
      } catch {
        // ignore
      }
    };
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, [propTelemetry]);

  // 1-second ticker for session time and map timer
  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
      setNowSec(Math.floor(Date.now() / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const gflTelemetry = propTelemetry || internalTelemetry;

  const formatElapsed = (totalSecs: number) => {
    const hrs = Math.floor(totalSecs / 3600);
    const mins = Math.floor((totalSecs % 3600) / 60);
    const secs = totalSecs % 60;
    if (hrs > 0) {
      return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')} elapsed`;
    }
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')} elapsed`;
  };

  const isPlayerOnGFL = Boolean(
    gflTelemetry?.players_list?.some((p) => p.name.toLowerCase().includes('geronimo'))
  );

  const currentMap = gflTelemetry?.map && gflTelemetry.map !== '-' ? gflTelemetry.map : 'ze_parking_p';
  const playerDisplay = gflTelemetry?.players && gflTelemetry.players !== '-/-' ? gflTelemetry.players : '62/64';

  // Live map start time & duration
  const mapStart = getMapStartTime('gfl', currentMap, gflTelemetry?.map_start_time);
  const mapDuration = Math.max(0, nowSec - mapStart);

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
          <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-[#23a55a] border-2 border-[#111214]" />
        </div>

        <div className="flex items-center gap-2 text-xs font-sans">
          <span className="font-bold text-white group-hover:text-indigo-300 transition-colors">
            Geronimo
          </span>
          <span className="text-[#949ba4] hidden sm:inline">&bull;</span>
          <span className="text-[#23a55a] font-medium hidden sm:inline flex items-center gap-1">
            <Gamepad2 className="w-3 h-3 inline" /> CS2 ZE
          </span>
          <span className="text-cyan-400 font-code text-[11px] hidden md:inline">
            ⏱️ {formatMapElapsed(mapDuration)}
          </span>
        </div>

        <ChevronUp className="w-4 h-4 text-slate-400 group-hover:text-white transition-transform group-hover:-translate-y-0.5 ml-1" />
      </aside>
    );
  }

  // Expanded Floating Rich Presence Card
  return (
    <aside 
      aria-label="Geronimo Discord Live Presence"
      className="fixed bottom-5 left-5 z-50 w-[calc(100vw-2.5rem)] sm:w-auto sm:max-w-md p-4 rounded-2xl bg-[#111214]/95 border border-[#2b2d31] hover:border-indigo-500/50 shadow-[0_16px_45px_rgba(0,0,0,0.85)] backdrop-blur-xl transition-all duration-300"
    >
      {/* Top Discord Activity Header */}
      <div className="flex items-center justify-between gap-2 border-b border-[#2b2d31] pb-2.5 mb-3">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-[#23a55a] animate-pulse inline-block" />
          <span className="text-[11px] font-sans font-bold tracking-wider text-[#dbdee1] uppercase">
            PLAYING A GAME
          </span>
        </div>

        {/* Minimize Button */}
        <button
          onClick={() => setIsCollapsed(true)}
          className="p-1 rounded hover:bg-[#2b2d31] text-slate-400 hover:text-white transition-colors cursor-pointer"
          title="Minimize to floating pill"
          aria-label="Minimize presence card"
        >
          <ChevronDown className="w-4 h-4" />
        </button>
      </div>

      {/* Main Profile & Rich Presence Card */}
      <div className="flex items-start sm:items-center gap-3.5">
        {/* Steam Avatar with Discord Green Status Dot */}
        <div className="relative flex-shrink-0">
          <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-full overflow-hidden border-2 border-[#23a55a] shadow-[0_0_15px_rgba(35,165,90,0.4)]">
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
          <div className="absolute bottom-0 right-0 w-3.5 h-3.5 sm:w-4 sm:h-4 rounded-full bg-[#23a55a] border-2 border-[#111214] flex items-center justify-center" title="Online & In-Game">
            <span className="w-1.5 h-1.5 rounded-full bg-white" />
          </div>
        </div>

        {/* Presence Body */}
        <div className="flex-1 min-w-0">
          {/* Username & Badges */}
          <div className="flex items-center gap-1.5 mb-0.5">
            <h4 className="text-sm sm:text-base font-bold font-sans text-white truncate">
              Geronimo
            </h4>
            <span className="px-1.5 py-0.2 rounded text-[10px] font-sans font-semibold bg-[#2b2d31] text-[#b5bac1]">
              HOST
            </span>
            {isPlayerOnGFL ? (
              <span className="px-1.5 py-0.2 rounded text-[10px] font-sans font-bold bg-[#23a55a]/20 text-[#23a55a] border border-[#23a55a]/40 flex items-center gap-1">
                <Sparkles className="w-2.5 h-2.5" /> IN-SERVER
              </span>
            ) : (
              <span className="px-1.5 py-0.2 rounded text-[10px] font-sans font-bold bg-[#5865f2]/20 text-[#5865f2] border border-[#5865f2]/30 flex items-center gap-1">
                <ShieldCheck className="w-2.5 h-2.5" /> GFL ZE
              </span>
            )}
          </div>

          {/* Game Title */}
          <div className="text-xs sm:text-sm font-bold font-sans text-[#f2f3f5] truncate flex items-center gap-1.5">
            <Gamepad2 className="w-3.5 h-3.5 text-[#5865f2]" />
            <span>Counter-Strike 2</span>
          </div>

          {/* Current Map & Live Map Timer */}
          <div className="text-xs font-sans text-[#949ba4] truncate flex items-center gap-1.5 mt-0.5">
            <span className="text-[#dbdee1] font-medium">Map:</span>
            <code className="text-[11px] text-[#5865f2] font-code bg-[#1e1f22] px-1.5 py-0.5 rounded font-bold truncate">
              {currentMap}
            </code>
            <span className="text-cyan-400 font-code text-[11px] font-semibold bg-cyan-950/60 px-1.5 py-0.5 rounded border border-cyan-500/30 flex items-center gap-1">
              <Clock className="w-2.5 h-2.5 text-cyan-400 animate-pulse" />
              {formatMapElapsed(mapDuration)}
            </span>
          </div>

          {/* Party & Elapsed Time */}
          <div className="text-[11px] font-sans text-[#949ba4] flex items-center gap-2 mt-1">
            <span className="flex items-center gap-1 text-[#b5bac1]">
              <Users className="w-3 h-3 text-[#23a55a]" />
              Party ({playerDisplay})
            </span>
            <span>&bull;</span>
            <span className="flex items-center gap-1">
              {formatElapsed(elapsedSeconds)}
            </span>
          </div>
        </div>
      </div>

      {/* Action Buttons: strictly ONE Profile link next to Join Game */}
      <div className="grid grid-cols-2 gap-2 mt-3 pt-2.5 border-t border-[#2b2d31]/80">
        <a
          href="steam://connect/74.91.124.21:27015"
          className="flex items-center justify-center gap-1.5 px-3 py-2 bg-[#5865f2] hover:bg-[#4752c4] text-white font-sans text-xs font-semibold rounded-lg shadow-md transition-all cursor-pointer transform hover:-translate-y-0.5"
          title="Launch CS2 and join Geronimo on GFL Clan ZE"
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
    </aside>
  );
};
