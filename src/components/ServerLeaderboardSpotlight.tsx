import React, { useState } from 'react';
import { 
  Trophy, 
  Zap, 
  Timer, 
  Users, 
  ChevronDown, 
  ChevronUp, 
  ShieldCheck, 
  Flame,
  Award
} from 'lucide-react';
import { 
  TOP_PLAYERS_OF_THE_MONTH, 
  FASTEST_MAP_CLEARS, 
  ZE_SEASON_INFO 
} from '../data/zeLeaderboard';

export const ServerLeaderboardSpotlight: React.FC = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [activeTab, setActiveTab] = useState<'mvps' | 'speedruns'>('mvps');

  return (
    <div className="mb-6 rounded-2xl border border-amber-500/30 bg-gradient-to-br from-slate-950/95 via-slate-900/90 to-amber-950/20 backdrop-blur-md shadow-[0_0_25px_rgba(251,191,36,0.12)] overflow-hidden transition-all">
      {/* Header Bar */}
      <div className="p-4 border-b border-amber-500/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-400/40 shadow-[0_0_12px_rgba(251,191,36,0.3)]">
            <Trophy className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <h3 className="font-cyber font-black text-sm md:text-base text-white tracking-wide flex items-center gap-2">
              <span>COMMUNITY LEADERBOARD SPOTLIGHT</span>
              <span className="text-[10px] font-code px-2 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-500/40 font-bold hidden sm:inline">
                MONTHLY MVPS & SPEEDRUNS
              </span>
            </h3>
            <div className="text-xs font-code text-slate-400 flex items-center gap-2 mt-0.5">
              <span className="text-amber-300/90">{ZE_SEASON_INFO.seasonName}</span>
              <span>&bull;</span>
              <span className="text-emerald-400 font-semibold">{ZE_SEASON_INFO.daysRemaining} days left</span>
            </div>
          </div>
        </div>

        {/* Action Controls: Tabs & Collapse */}
        <div className="flex items-center gap-2 self-end sm:self-auto">
          {!isCollapsed && (
            <div className="flex items-center bg-slate-950 border border-slate-800 rounded-lg p-0.5 font-code text-xs">
              <button
                onClick={() => setActiveTab('mvps')}
                className={`px-3 py-1.5 rounded-md font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                  activeTab === 'mvps'
                    ? 'bg-amber-500 text-slate-950 shadow-[0_0_10px_rgba(251,191,36,0.4)]'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Award className="w-3.5 h-3.5" />
                <span>Top MVPs</span>
              </button>
              <button
                onClick={() => setActiveTab('speedruns')}
                className={`px-3 py-1.5 rounded-md font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                  activeTab === 'speedruns'
                    ? 'bg-amber-500 text-slate-950 shadow-[0_0_10px_rgba(251,191,36,0.4)]'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Timer className="w-3.5 h-3.5" />
                <span>Speedruns</span>
              </button>
            </div>
          )}

          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-400 hover:text-white transition-colors cursor-pointer"
            title={isCollapsed ? 'Expand Spotlight' : 'Minimize Spotlight'}
          >
            {isCollapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Expandable Body */}
      {!isCollapsed && (
        <div className="p-4 sm:p-5">
          {activeTab === 'mvps' ? (
            /* TAB 1: TOP MVPS OF THE MONTH */
            <div>
              <div className="flex items-center justify-between text-xs font-code text-slate-400 mb-3 px-1">
                <span>COMMUNITY TOP ZE ESCAPERS (RANKED BY PERSONAL SCORE & WIN RATE)</span>
                <span className="hidden sm:inline text-amber-300/80">Auto-Refreshed Monthly</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {TOP_PLAYERS_OF_THE_MONTH.map((p) => (
                  <div
                    key={p.rank}
                    className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 hover:border-amber-500/40 transition-all flex flex-col justify-between group"
                  >
                    <div>
                      {/* Top Rank Header */}
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <div className="flex items-center gap-1.5">
                          <span className="text-lg leading-none">{p.medal}</span>
                          <span className="font-cyber font-bold text-white text-sm group-hover:text-amber-300 transition-colors">
                            {p.name}
                          </span>
                        </div>
                        <span className="text-[10px] font-code px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-300 font-bold flex items-center gap-1">
                          <span>{p.flag}</span>
                          <span>{p.clan}</span>
                        </span>
                      </div>

                      {/* Specialty Title */}
                      <div className="text-[11px] font-code text-cyan-300/90 flex items-center gap-1 mb-2.5">
                        <Zap className="w-3 h-3 text-cyan-400 flex-shrink-0" />
                        <span className="truncate">{p.specialtyTitle}</span>
                      </div>
                    </div>

                    {/* Stats Footer */}
                    <div className="pt-2 border-t border-slate-900 flex items-center justify-between text-xs font-code">
                      <div className="text-slate-400">
                        Score: <strong className="text-amber-300 font-bold">{p.score.toLocaleString()}</strong>
                      </div>
                      <div className="flex items-center gap-1 text-emerald-400 font-bold">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        <span>{p.winRate}% Win</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            /* TAB 2: FASTEST MAP SPEEDRUN CLEARS */
            <div>
              <div className="flex items-center justify-between text-xs font-code text-slate-400 mb-3 px-1">
                <span>OFFICIAL RECORD MAP SPEEDRUNS (COMMUNITY LASER & ESCAPE FINISHES)</span>
                <span className="hidden sm:inline text-amber-300/80">Season 2026-11 Records</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {FASTEST_MAP_CLEARS.map((c) => (
                  <div
                    key={c.id}
                    className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 hover:border-amber-500/40 transition-all flex flex-col justify-between group"
                  >
                    <div>
                      {/* Map Title & Clear Time */}
                      <div className="flex items-start justify-between gap-2 mb-1.5">
                        <div className="min-w-0">
                          <h4 className="font-cyber font-bold text-white text-sm group-hover:text-amber-300 transition-colors truncate">
                            {c.mapName}
                          </h4>
                          <div className="text-[11px] font-code text-slate-400 truncate">
                            {c.stage}
                          </div>
                        </div>

                        {/* Speedrun Time Pill */}
                        <div className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-emerald-950/90 border border-emerald-500/50 text-emerald-300 font-code font-bold text-xs shadow-[0_0_10px_rgba(16,185,129,0.25)] flex-shrink-0">
                          <Timer className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
                          <span>{c.clearTime}</span>
                        </div>
                      </div>

                      {/* Tier Badge & Clan */}
                      <div className="flex items-center gap-2 flex-wrap mb-2">
                        <span className={`text-[10px] font-code px-2 py-0.5 rounded border font-bold ${c.tierColor}`}>
                          {c.tierBadge}
                        </span>
                        <span className="text-[10px] font-code text-slate-400">
                          by <strong className="text-slate-300">{c.clanName}</strong>
                        </span>
                      </div>
                    </div>

                    {/* Footer Info */}
                    <div className="pt-2 border-t border-slate-900 flex items-center justify-between text-[11px] font-code text-slate-400">
                      <div className="flex items-center gap-1 text-slate-300">
                        <Users className="w-3 h-3 text-cyan-400" />
                        <span>{c.survivorsCount} Humans Survived</span>
                      </div>
                      <span className="text-slate-500">{c.date}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Footer Note */}
          <div className="mt-4 pt-3 border-t border-slate-800/80 text-[11px] font-sans text-slate-500 flex items-center gap-1.5">
            <Flame className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
            <span>
              Community records synchronized from monthly community scrims, s2ze Ruby Bot logs, and NERV CS2ZE season archives.
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
