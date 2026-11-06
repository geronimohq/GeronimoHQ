import React, { useState, useEffect } from 'react';
import { type LiveServerInfo } from '../utils/serverQuery';
import { 
  Gamepad2, 
  ExternalLink, 
  Play, 
  Sparkles, 
  Clock, 
  Users, 
  ShieldCheck 
} from 'lucide-react';

interface GeronimoDiscordPresenceProps {
  gflTelemetry?: LiveServerInfo;
}

export const GeronimoDiscordPresence: React.FC<GeronimoDiscordPresenceProps> = ({ gflTelemetry }) => {
  const [elapsedSeconds, setElapsedSeconds] = useState(6124); // Initial session time in seconds (~1h 42m)

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

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

  return (
    <div className="w-full max-w-xl mx-auto my-6 p-4 rounded-2xl bg-[#111214] border border-[#2b2d31] shadow-[0_12px_32px_rgba(0,0,0,0.6)] backdrop-blur-md">
      {/* Top Discord Activity Header */}
      <div className="flex items-center justify-between gap-2 border-b border-[#2b2d31] pb-3 mb-3.5">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-[#23a55a] animate-pulse inline-block" />
          <span className="text-[11px] font-sans font-bold tracking-wider text-[#dbdee1] uppercase">
            PLAYING A GAME
          </span>
        </div>
        <a
          href="https://steamcommunity.com/profiles/76561198143793864/"
          target="_blank"
          rel="noreferrer"
          className="text-[11px] font-sans font-medium text-[#949ba4] hover:text-[#5865f2] flex items-center gap-1 transition-colors"
        >
          Steam Profile <ExternalLink className="w-3 h-3" />
        </a>
      </div>

      {/* Main Profile & Rich Presence Card */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
        {/* Steam Avatar with Discord Green Status Dot */}
        <div className="relative flex-shrink-0">
          <div className="w-16 h-16 rounded-full overflow-hidden border-2 border-[#23a55a] shadow-[0_0_15px_rgba(35,165,90,0.4)]">
            <img
              src="/images/geronimo_steam_avatar.jpg"
              alt="Geronimo Steam Avatar"
              className="w-full h-full object-cover"
              onError={(e) => {
                // Fallback to Pepe avatar if local fails
                (e.target as HTMLImageElement).src = '/profile_avatar_edge_to_edge.jpg';
              }}
            />
          </div>
          {/* Status Dot */}
          <div className="absolute bottom-0 right-0 w-4 h-4 rounded-full bg-[#23a55a] border-2 border-[#111214] flex items-center justify-center" title="Online & In-Game">
            <span className="w-1.5 h-1.5 rounded-full bg-white" />
          </div>
        </div>

        {/* Presence Body */}
        <div className="flex-1 min-w-0">
          {/* Username & Badges */}
          <div className="flex items-center gap-2 mb-0.5">
            <h4 className="text-base font-bold font-sans text-white hover:text-[#5865f2] transition-colors truncate">
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
          <div className="text-sm font-bold font-sans text-[#f2f3f5] truncate flex items-center gap-1.5">
            <Gamepad2 className="w-4 h-4 text-[#5865f2]" />
            <span>Counter-Strike 2</span>
          </div>

          {/* Details / Mode */}
          <div className="text-xs font-sans text-[#dbdee1] truncate">
            Zombie Escape 24/7 &bull; GFL Clan
          </div>

          {/* Current Map & Server */}
          <div className="text-xs font-sans text-[#949ba4] truncate flex items-center gap-2 mt-0.5">
            <span className="text-[#dbdee1] font-semibold">Map:</span>
            <code className="text-xs text-[#5865f2] font-code bg-[#1e1f22] px-1.5 py-0.5 rounded">
              {currentMap}
            </code>
            <span>&bull;</span>
            <span className="flex items-center gap-1 text-[#b5bac1]">
              <Users className="w-3 h-3 text-[#23a55a]" />
              Party ({playerDisplay})
            </span>
          </div>

          {/* Elapsed Timer */}
          <div className="text-xs font-sans text-[#949ba4] flex items-center gap-1 mt-1">
            <Clock className="w-3 h-3 text-[#949ba4]" />
            <span>{formatElapsed(elapsedSeconds)}</span>
          </div>
        </div>

        {/* 1-Click Join Button */}
        <div className="w-full sm:w-auto flex sm:flex-col gap-2 flex-shrink-0 mt-2 sm:mt-0">
          <a
            href="steam://connect/74.91.124.21:27015"
            className="flex-1 sm:flex-initial flex items-center justify-center gap-1.5 px-4 py-2 bg-[#5865f2] hover:bg-[#4752c4] text-white font-sans text-xs font-semibold rounded-lg shadow-md transition-all cursor-pointer transform hover:-translate-y-0.5"
            title="Launch CS2 and join Geronimo on GFL Clan ZE"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Join Game</span>
          </a>
          <a
            href="https://steamcommunity.com/profiles/76561198143793864/"
            target="_blank"
            rel="noreferrer"
            className="flex-1 sm:flex-initial flex items-center justify-center gap-1 px-3 py-1.5 bg-[#2b2d31] hover:bg-[#35373c] text-[#dbdee1] font-sans text-xs rounded-lg transition-colors"
          >
            Profile
          </a>
        </div>
      </div>
    </div>
  );
};
