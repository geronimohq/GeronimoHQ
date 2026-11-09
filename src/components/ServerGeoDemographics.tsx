import React, { useState, useMemo } from 'react';
import { getServerDemographics } from '../utils/serverDemographics';
import type { ZegraphContinentStats } from '../utils/serverQuery';
import { Globe, Flag, Zap } from 'lucide-react';

interface ServerGeoDemographicsProps {
  serverRegion: string;
  totalPlayers: number;
  playerNames?: string[];
  compact?: boolean;
  zegraphContinents?: ZegraphContinentStats | null;
}

export const ServerGeoDemographics: React.FC<ServerGeoDemographicsProps> = ({
  serverRegion,
  totalPlayers,
  playerNames = [],
  compact = false,
  zegraphContinents,
}) => {
  const [viewMode, setViewMode] = useState<'country' | 'continent' | 'latency'>('country');

  const demographics = useMemo(
    () => getServerDemographics(serverRegion, totalPlayers, playerNames, zegraphContinents),
    [serverRegion, totalPlayers, playerNames, zegraphContinents]
  );

  const { dominantCountry, dominantContinent, dominantLatency, countries, continents, latencies, summary } = demographics;

  const activeItems = viewMode === 'country' ? countries : viewMode === 'continent' ? continents : latencies;
  const activeDominant = viewMode === 'country' ? dominantCountry : viewMode === 'continent' ? dominantContinent : dominantLatency;

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
    .map((r) => `${r.flag} ${r.name}: ${r.percentage}% (~${r.count} players)${r.pingRange ? ` [Ping: ${r.pingRange}]` : ''}`)
    .join('\n');

  const maxPills = compact ? 5 : 5;

  return (
    <div
      className={`rounded-xl border border-cyan-500/30 bg-slate-950/90 backdrop-blur-md p-3 font-code transition-all hover:border-cyan-400/60 shadow-[0_0_15px_rgba(0,240,255,0.1)] ${
        compact ? 'w-full' : 'w-full sm:w-[330px]'
      }`}
      title={`Live Geographic Demographics (${viewMode === 'country' ? 'By Country' : viewMode === 'continent' ? 'By Region' : 'By Ping Spectrum'}):\n${tooltipText}\n• ${summary}\n• Real-time diurnal activity curve & active roster signal analysis.`}
    >
      {/* Header Row: Title & Toggle */}
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-1.5 text-xs font-bold text-cyan-300 uppercase tracking-wider font-cyber">
          <Globe className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
          <span>GEO RADAR</span>
        </div>

        {/* View Mode Toggle: Country vs Continent vs Ping */}
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
          <button
            onClick={() => setViewMode('latency')}
            className={`px-1.5 py-0.5 text-[9px] font-bold rounded transition-colors flex items-center gap-1 cursor-pointer ${
              viewMode === 'latency'
                ? 'bg-cyan-500 text-slate-950 shadow-[0_0_8px_rgba(0,240,255,0.4)]'
                : 'text-slate-400 hover:text-white'
            }`}
            title="Show breakdown by scoreboard ping spectrum (<70ms vs 120-200ms+)"
          >
            <Zap className="w-2.5 h-2.5" />
            <span>Ping</span>
          </button>
        </div>
      </div>

      {/* Dominant Demographic Pill */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] text-slate-400 uppercase tracking-wider">
          {viewMode === 'latency' ? 'Scoreboard Ping:' : 'Top Demographic:'}
        </span>
        <div
          className="flex items-center gap-1 text-[10px] font-bold bg-cyan-950/90 text-cyan-200 border border-cyan-500/40 px-2 py-0.5 rounded shadow-sm max-w-[210px] truncate"
          title={`${activeDominant.flag} ${activeDominant.name} (${activeDominant.percentage}% of players)${activeDominant.pingRange ? ` • Ping: ${activeDominant.pingRange}` : ''}`}
        >
          <span>{viewMode === 'latency' ? '⚡' : '👑'}</span>
          <span className="truncate">
            {activeDominant.flag} {viewMode === 'latency' ? activeDominant.name : `${activeDominant.code} (${activeDominant.percentage}%)`}
          </span>
          {viewMode !== 'latency' && activeDominant.pingRange && (
            <span className="text-[9px] text-cyan-300/80 font-mono hidden sm:inline">
              [{activeDominant.pingRange}]
            </span>
          )}
        </div>
      </div>

      {/* Thick Heightened Segmented Bar (12px / h-3) */}
      <div className="w-full h-3 rounded-full overflow-hidden flex bg-slate-900 border border-slate-700/80 mb-2.5 shadow-inner">
        {activeItems.map((r) => (
          <div
            key={r.code}
            style={{ width: `${r.percentage}%`, backgroundColor: r.color }}
            className="h-full transition-all duration-500 first:rounded-l-full last:rounded-r-full hover:brightness-125 border-r border-slate-950/40 last:border-0 relative group"
            title={`${r.flag} ${r.name}: ${r.percentage}% (~${r.count} players)${r.pingRange ? ` • Est. Ping: ${r.pingRange}` : ''}${r.description ? `\n• ${r.description}` : ''}`}
          />
        ))}
      </div>

      {/* Breakdown Pills: Left-aligned, covering width, with +more on the far right */}
      <div className="w-full flex items-center justify-between text-[11px] text-slate-300 font-code gap-1">
        <div className="flex items-center gap-1.5 flex-wrap min-w-0 flex-1">
          {activeItems.slice(0, maxPills).map((r) => (
            <span
              key={r.code}
              className="flex items-center gap-1 bg-slate-900/90 border border-slate-800 px-1.5 py-0.5 rounded text-[10px] whitespace-nowrap flex-shrink-0"
              title={`${r.flag} ${r.name}: ${r.percentage}% (~${r.count} players)${r.pingRange ? ` • Ping: ${r.pingRange}` : ''}${r.description ? `\n• ${r.description}` : ''}`}
            >
              <span style={{ color: r.color }} className="font-black text-xs leading-none">&bull;</span>
              <span>{r.flag}</span>
              <span className="font-bold text-slate-200">{r.percentage}%</span>
              {viewMode === 'latency' && (
                <span className="text-[9px] text-cyan-400 font-mono">({r.pingRange})</span>
              )}
            </span>
          ))}
        </div>
        {activeItems.length > maxPills && (
          <span
            className="ml-auto text-[10px] text-slate-400 hover:text-cyan-300 transition-colors font-medium whitespace-nowrap pl-1.5 flex-shrink-0 cursor-help"
            title={tooltipText}
          >
            +{activeItems.length - maxPills} more
          </span>
        )}
      </div>
    </div>
  );
};
