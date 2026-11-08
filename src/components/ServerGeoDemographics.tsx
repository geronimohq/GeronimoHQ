import React, { useMemo } from 'react';
import { getServerDemographics } from '../utils/serverDemographics';
import { Globe } from 'lucide-react';

interface ServerGeoDemographicsProps {
  serverRegion: string;
  totalPlayers: number;
  playerNames?: string[];
  compact?: boolean;
}

export const ServerGeoDemographics: React.FC<ServerGeoDemographicsProps> = ({
  serverRegion,
  totalPlayers,
  playerNames = [],
  compact = false,
}) => {
  const demographics = useMemo(
    () => getServerDemographics(serverRegion, totalPlayers, playerNames),
    [serverRegion, totalPlayers, playerNames]
  );

  const { dominant, regions, summary } = demographics;

  if (totalPlayers <= 0) {
    return (
      <div className={`rounded-xl border border-slate-800 bg-slate-950/60 p-2 font-code text-[11px] text-slate-500 flex items-center justify-between ${compact ? 'w-full' : 'w-full sm:w-[260px]'}`}>
        <div className="flex items-center gap-1.5">
          <Globe className="w-3.5 h-3.5 text-slate-600" />
          <span>GEO RADAR</span>
        </div>
        <span className="text-[10px] text-slate-600">IDLE (0 PLAYERS)</span>
      </div>
    );
  }

  const tooltipText = regions.map((r) => `${r.flag} ${r.name}: ${r.percentage}% (~${r.count} players)`).join('\n');

  return (
    <div
      className={`rounded-xl border border-cyan-500/25 bg-slate-950/85 backdrop-blur-md p-2.5 font-code transition-all hover:border-cyan-400/50 shadow-sm ${
        compact ? 'w-full' : 'w-full sm:w-[270px]'
      }`}
      title={`Live Geographic Demographics:\n${tooltipText}\n• ${summary}\n• Based on datacenter telemetry, routing, & active roster tags.`}
    >
      {/* Header Row: Title & Dominant Region */}
      <div className="flex items-center justify-between gap-1.5 mb-1.5">
        <div className="flex items-center gap-1.5 text-[10px] font-bold text-cyan-300 uppercase tracking-wider">
          <Globe className="w-3 h-3 text-cyan-400 animate-pulse" />
          <span>GEO RADAR</span>
        </div>
        <div className="flex items-center gap-1 text-[9px] font-bold bg-cyan-950/80 text-cyan-200 border border-cyan-500/30 px-1.5 py-0.5 rounded shadow-sm">
          <span>👑</span>
          <span className="truncate max-w-[130px]">{dominant.flag} {dominant.code} ({dominant.percentage}%)</span>
        </div>
      </div>

      {/* Segmented Distribution Bar */}
      <div className="w-full h-1.5 rounded-full overflow-hidden flex bg-slate-900 border border-slate-800/80 mb-2">
        {regions.map((r) => (
          <div
            key={r.code}
            style={{ width: `${r.percentage}%`, backgroundColor: r.color }}
            className="h-full transition-all duration-500 first:rounded-l-full last:rounded-r-full hover:brightness-125"
            title={`${r.flag} ${r.name}: ${r.percentage}%`}
          />
        ))}
      </div>

      {/* Continental Breakdown Pills */}
      <div className="flex items-center justify-between text-[9px] text-slate-400 font-code gap-1">
        {regions.slice(0, 4).map((r) => (
          <span key={r.code} className="flex items-center gap-0.5 truncate" title={`${r.name} (~${r.count} players)`}>
            <span style={{ color: r.color }} className="font-bold">&bull;</span>
            <span>{r.flag}</span>
            <span className="font-semibold text-slate-300">{r.percentage}%</span>
          </span>
        ))}
      </div>
    </div>
  );
};
