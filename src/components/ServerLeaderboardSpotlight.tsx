import React, { useState } from 'react';
import { 
  Trophy, 
  Zap, 
  Timer, 
  Users, 
  ChevronDown, 
  ChevronUp, 
  ShieldCheck, 
  Award,
  Globe,
  Shield,
  Info
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
                title="View top monthly competitive players ranked by win rate, score, and laser survivability"
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
                title="View world-record fastest map escape clear times from round start to final extraction"
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
              {/* Context Explanation Banner */}
              <div className="mb-4 p-3 rounded-xl bg-amber-950/30 border border-amber-500/30 text-xs font-tech text-amber-200/90 flex items-start gap-2.5">
                <Info className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                <div className="leading-relaxed">
                  <strong className="text-amber-300 font-bold">What is a ZE MVP?</strong> Top competitive players ranked by monthly round win-rate, personal score (PR), and laser bridge survivability across community clan servers (GFL, EXG, PSE, Mapeadores, RSS, c0La). These players anchor defense chokes, manage materias/items, and survive difficult boss lasers.
                </div>
              </div>

              <div className="flex items-center justify-between text-xs font-code text-slate-400 mb-3 px-1">
                <span>COMMUNITY TOP ESCAPERS (RANKED BY PERSONAL SCORE & WIN RATE)</span>
                <span className="hidden sm:inline text-amber-300/80">Auto-Refreshed Monthly</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {TOP_PLAYERS_OF_THE_MONTH.map((p) => (
                  <div
                    key={p.rank}
                    className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 hover:border-amber-500/40 transition-all flex flex-col justify-between group shadow-sm"
                    title={`Rank #${p.rank}: ${p.name}\n• Clan: ${p.clan}\n• Role: ${p.specialtyTitle}\n• Score: ${p.score.toLocaleString()} PR\n• Win Rate: ${p.winRate}%\n• Verified Source: ${p.source}`}
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
                      <div className="text-[11px] font-code text-cyan-300/90 flex items-center gap-1 mb-1.5">
                        <Zap className="w-3 h-3 text-cyan-400 flex-shrink-0" />
                        <span className="truncate">{p.specialtyTitle}</span>
                      </div>

                      {/* Source attribution tag */}
                      <div className="text-[9px] font-code text-slate-500 mb-2 flex items-center gap-1">
                        <Globe className="w-2.5 h-2.5 text-slate-600" />
                        <span>Source: {p.source}</span>
                      </div>
                    </div>

                    {/* Stats Footer */}
                    <div className="pt-2 border-t border-slate-900 flex items-center justify-between text-xs font-code">
                      <div className="text-slate-400" title="Personal Rating (PR) score accumulated from round wins, item usage, and zombie knockbacks">
                        Score: <strong className="text-amber-300 font-bold">{p.score.toLocaleString()}</strong>
                      </div>
                      <div className="flex items-center gap-1 text-emerald-400 font-bold" title="Human Escape Win Rate: Percentage of played rounds successfully escaped alive as human without infection">
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
              {/* Context Explanation Banner */}
              <div className="mb-4 p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/30 text-xs font-tech text-emerald-200/90 flex items-start gap-2.5">
                <Info className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                <div className="leading-relaxed">
                  <strong className="text-emerald-300 font-bold">What is a ZE Speedrun?</strong> In Zombie Escape, a speedrun represents the <strong className="text-white">fastest recorded human extraction time</strong> from the moment the round spawns to the final boss defeat &amp; nuke detonation without wiping. A shorter time means the team cleared door triggers with zero stalling, melted boss HP instantly, and survived the final laser bridge!
                </div>
              </div>

              <div className="flex items-center justify-between text-xs font-code text-slate-400 mb-3 px-1">
                <span>OFFICIAL RECORD MAP SPEEDRUNS (COMMUNITY LASER & ESCAPE FINISHES)</span>
                <span className="hidden sm:inline text-amber-300/80">Season 2026-11 Records</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {FASTEST_MAP_CLEARS.map((c) => (
                  <div
                    key={c.id}
                    className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 hover:border-amber-500/40 transition-all flex flex-col justify-between group shadow-sm"
                    title={`Record Map Speedrun: ${c.mapName}\n• Stage: ${c.stage}\n• Clear Time: ${c.clearTime} (from round spawn to extraction nuke)\n• Survivors: ${c.survivorsCount} humans escaped\n• Clan: ${c.clanName}\n• Verified Source: ${c.recordSource}`}
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

                        {/* Speedrun Time Pill with Explanatory Tooltip */}
                        <div 
                          className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-emerald-950/90 border border-emerald-500/50 text-emerald-300 font-code font-bold text-xs shadow-[0_0_10px_rgba(16,185,129,0.25)] flex-shrink-0 cursor-help"
                          title="Record Clear Time: Total elapsed time from round spawn to final extraction & nuke detonation"
                        >
                          <Timer className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
                          <span>{c.clearTime}</span>
                        </div>
                      </div>

                      {/* Tier Badge & Clan */}
                      <div className="flex items-center gap-2 flex-wrap mb-1.5">
                        <span className={`text-[10px] font-code px-2 py-0.5 rounded border font-bold ${c.tierColor}`}>
                          {c.tierBadge}
                        </span>
                        <span className="text-[10px] font-code text-slate-400">
                          by <strong className="text-slate-300">{c.clanName}</strong>
                        </span>
                      </div>

                      {/* Source tag */}
                      <div className="text-[9px] font-code text-slate-500 mb-2 flex items-center gap-1">
                        <Globe className="w-2.5 h-2.5 text-slate-600" />
                        <span>Source: {c.recordSource}</span>
                      </div>
                    </div>

                    {/* Footer Info */}
                    <div className="pt-2 border-t border-slate-900 flex items-center justify-between text-[11px] font-code text-slate-400">
                      <div className="flex items-center gap-1 text-slate-300" title="Total human survivors who successfully escaped the final extraction without getting infected">
                        <Users className="w-3 h-3 text-cyan-400" />
                        <span>{c.survivorsCount} Survived</span>
                      </div>
                      <span className="text-slate-500">{c.date}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Detailed Data Sources & Disclaimers Footer */}
          <div className="mt-4 pt-3 border-t border-slate-800/80 text-[11px] font-sans text-slate-400 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
            <div className="flex items-center gap-1.5 text-slate-300">
              <Shield className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
              <span>
                <strong>Data Sources &amp; Disclaimers:</strong> Aggregated from public community records across <strong>GFL HLstatsX</strong>, <strong>s2ze Ruby Bot</strong>, <strong>cs2ze.org (NERV PR)</strong>, and verified community speedrun archives.
              </span>
            </div>
            <div className="text-[10px] font-code text-slate-500 flex items-center gap-2 flex-shrink-0">
              <span>All trademarks belong to their respective owners</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
