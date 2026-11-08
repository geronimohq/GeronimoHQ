import React, { useState, useMemo } from 'react';
import { getServerDemographics } from '../utils/serverDemographics';
import { Globe, Flag } from 'lucide-react';

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
  const [viewMode, setViewMode] = useState<'country' | 'continent'>('country');

  const demographics = useMemo(
    () => getServerDemographics(serverRegion, totalPlayers, playerNames),
    [serverRegion, totalPlayers, playerNames]
  );

  const { dominantCountry, dominantContinent, countries, continents, summary } = demographics;

  const activeItems = viewMode === 'country' ? countries : continents;
  const activeDominant = viewMode === 'country' ? dominantCountry : dominantContinent;

  if (totalPlayers <= 0) {
    return (
      <div className={`rounded-xl border border-slate-800 bg-slate-950/75 p-3 font-code text-xs text-slate-500 flex items-center justify-between shadow-sm ${compact ? 'w-full' : 'w-full sm:w-[330px]'}`}>
        <div className="flex items-center gap-2">
          <Globe className="w-4 h-4 text-slate-600" />
          <span className="font-bold tracking-wider">GEO RADAR</span>
        </div>
        <span className="text-[11px] text-slate-600 font-semibold">IDLE (0 PLAYERS)</span>
      </div>
    );
  }

  const tooltipText = activeItems
    .map((r) => `${r.flag} ${r.name}: ${r.percentage}% (~${r.count} players)`)
    .join('\n');

  return (
    <div
      className={`rounded-xl border border-cyan-500/30 bg-slate-950/90 backdrop-blur-md p-3 font-code transition-all hover:border-cyan-400/60 shadow-[0_0_15px_rgba(0,240,255,0.1)] ${
        compact ? 'w-full' : 'w-full sm:w-[330px]'
      }`}
      title={`Live Geographic Demographics (${viewMode === 'country' ? 'By Country' : 'By Continent'}):\n${tooltipText}\n• ${summary}\n• Blended from datacenter physical IP routing & player clan tags.`}
    >
      {/* Header Row: Title & Toggle */}
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-1.5 text-xs font-bold text-cyan-300 uppercase tracking-wider font-cyber">
          <Globe className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
          <span>GEO RADAR</span>
        </div>

        {/* View Mode Toggle: Country vs Continent */}
        <div className="flex items-center bg-slate-900 border border-slate-700/80 rounded-md p-0.5">
          <button
            onClick={() => setViewMode('country')}
            className={`px-1.5 py-0.5 text-[9px] font-bold rounded transition-colors flex items-center gap-1 cursor-pointer ${
              viewMode === 'country'
                ? 'bg-cyan-500 text-slate-950 shadow-[0_0_8px_rgba(0,240,255,0.4)]'
                : 'text-slate-400 hover:text-white'
            }`}
            title="Show breakdown by individual countries"
          >
            <Flag className="w-2.5 h-2.5" />
            <span>Country</span>
          </button>
          <button
            onClick={() => setViewMode('continent')}
            className={`px-1.5 py-0.5 text-[9px] font-bold rounded transition-colors flex items-center gap-1 cursor-pointer ${
              viewMode === 'continent'
                ? 'bg-cyan-500 text-slate-950 shadow-[0_0_8px_rgba(0,240,255,0.4)]'
                : 'text-slate-400 hover:text-white'
            }`}
            title="Show breakdown by continental regions"
          >
            <Globe className="w-2.5 h-2.5" />
            <span>Region</span>
          </button>
        </div>
      </div>

      {/* Dominant Player Pill */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] text-slate-400 uppercase tracking-wider">Top Demographic:</span>
        <div className="flex items-center gap-1 text-[10px] font-bold bg-cyan-950/90 text-cyan-200 border border-cyan-500/40 px-2 py-0.5 rounded shadow-sm">
          <span>👑</span>
          <span className="truncate max-w-[170px]">
            {activeDominant.flag} {activeDominant.code} ({activeDominant.percentage}%)
          </span>
        </div>
      </div>

      {/* Thick Heightened Segmented Bar (12px / h-3) */}
      <div className="w-full h-3 rounded-full overflow-hidden flex bg-slate-900 border border-slate-700/80 mb-2.5 shadow-inner">
        {activeItems.map((r) => (
          <div
            key={r.code}
            style={{ width: `${r.percentage}%`, backgroundColor: r.color }}
            className="h-full transition-all duration-500 first:rounded-l-full last:rounded-r-full hover:brightness-125 border-r border-slate-950/40 last:border-0 relative group"
            title={`${r.flag} ${r.name}: ${r.percentage}% (~${r.count} players)`}
          />
        ))}
      </div>

      {/* Breakdown Pills */}
      <div className="flex items-center justify-between text-[11px] text-slate-300 font-code gap-1 flex-wrap">
        {activeItems.slice(0, 4).map((r) => (
          <span
            key={r.code}
            className="flex items-center gap-1 bg-slate-900/90 border border-slate-800 px-1.5 py-0.5 rounded text-[10px]"
            title={`${r.flag} ${r.name}: ${r.percentage}% (~${r.count} players)`}
          >
            <span style={{ color: r.color }} className="font-black text-xs leading-none">&bull;</span>
            <span>{r.flag}</span>
            <span className="font-bold text-slate-200">{r.percentage}%</span>
          </span>
        ))}
        {activeItems.length > 4 && (
          <span className="text-[10px] text-slate-400 font-medium" title={tooltipText}>
            +{activeItems.length - 4} more
          </span>
        )}
      </div>
    </div>
  );
};
