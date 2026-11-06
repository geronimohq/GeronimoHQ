import React, { useState } from 'react';
import { 
  Users, 
  MapPin, 
  Activity, 
  Copy, 
  Check, 
  Skull, 
  ShieldAlert 
} from 'lucide-react';

export const ServerRadarPreview: React.FC = () => {
  const [copiedServer, setCopiedServer] = useState(false);
  const serverIp = 'connect ze.geronimohq.com:27015';

  const handleCopyIp = () => {
    navigator.clipboard.writeText(serverIp);
    setCopiedServer(true);
    setTimeout(() => setCopiedServer(false), 2000);
  };

  return (
    <section id="server-radar" className="relative w-full max-w-6xl mx-auto px-4 py-12">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8 border-b border-lime-500/30 pb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 text-[10px] font-code rounded bg-lime-950/80 text-lime-300 border border-lime-500/50">
              MODULE 02 // TELEMETRY LINK
            </span>
            <span className="text-xs font-code text-slate-400">
              COMMUNITY SERVERS // 128 TICK
            </span>
          </div>
          <h2 className="text-2xl md:text-3xl font-cyber font-black text-white tracking-wider flex items-center gap-3">
            ZOMBIE ESCAPE RADAR
            <span className="text-xs font-code px-2 py-1 bg-emerald-950 text-emerald-300 border border-emerald-500/40 rounded uppercase animate-pulse">
              LIVE MONITOR
            </span>
          </h2>
          <p className="text-sm font-tech text-slate-300 mt-1 max-w-2xl">
            Real-time server status, map rotation, player contagion telemetry, and instant connect commands for our custom CS2 Zombie Escape hub.
          </p>
        </div>

        {/* Quick Connect Command */}
        <button
          onClick={handleCopyIp}
          className="flex items-center gap-2 px-4 py-2 bg-slate-900 border border-lime-500/50 hover:border-lime-400 text-lime-300 font-code text-xs rounded-lg transition-all shadow-[0_0_15px_rgba(57,255,20,0.2)] cursor-pointer"
        >
          {copiedServer ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4 text-lime-400" />}
          <span>{copiedServer ? 'IP COPIED TO CLIPBOARD!' : 'COPY CONNECT CONSOLE IP'}</span>
        </button>
      </div>

      {/* Live Server Status Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Main Server Card (2 cols) */}
        <div className="lg:col-span-2 relative p-6 rounded-2xl border border-lime-500/30 bg-gradient-to-br from-slate-950/80 via-slate-900/60 to-emerald-950/20 backdrop-blur-xl overflow-hidden shadow-[0_0_30px_rgba(0,0,0,0.6)]">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-emerald-400 animate-ping" />
              <span className="font-cyber font-bold text-white text-base md:text-lg">
                [GERONIMO] ZOMBIE ESCAPE 24/7 | CLUSTER #01
              </span>
            </div>
            <span className="text-[11px] font-code px-2 py-0.5 bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 rounded">
              STATUS: NOMINAL // 128 TICK
            </span>
          </div>

          {/* Current Map & Objective Details */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <div className="bg-[#05070e] p-3 rounded-xl border border-slate-800">
              <div className="text-[10px] font-code text-slate-400 mb-1 flex items-center gap-1.5">
                <MapPin className="w-3 h-3 text-cyan-400" /> CURRENT MAP
              </div>
              <div className="text-sm font-cyber font-bold text-cyan-300 truncate">
                ze_predator_ultimate_p3
              </div>
              <div className="text-[10px] text-slate-500 font-code">Stage 4: Alien Base Escape</div>
            </div>

            <div className="bg-[#05070e] p-3 rounded-xl border border-slate-800">
              <div className="text-[10px] font-code text-slate-400 mb-1 flex items-center gap-1.5">
                <Users className="w-3 h-3 text-lime-400" /> PLAYERS ONLINE
              </div>
              <div className="text-sm font-cyber font-bold text-lime-300">
                58 / 64 Survivors
              </div>
              <div className="text-[10px] text-slate-500 font-code">6 slots available</div>
            </div>

            <div className="bg-[#05070e] p-3 rounded-xl border border-slate-800">
              <div className="text-[10px] font-code text-slate-400 mb-1 flex items-center gap-1.5">
                <Activity className="w-3 h-3 text-fuchsia-400" /> SERVER HEALTH
              </div>
              <div className="text-sm font-cyber font-bold text-fuchsia-300">
                18ms // 0% Loss
              </div>
              <div className="text-[10px] text-slate-500 font-code">Dallas / US-Central</div>
            </div>
          </div>

          {/* Player Capacity Bar */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-code">
              <span className="text-slate-400">INFECTION CONTAGION LEVEL</span>
              <span className="text-lime-400 font-bold">90.6% CAPACITY</span>
            </div>
            <div className="w-full h-3 bg-slate-900 rounded-full overflow-hidden p-0.5 border border-slate-800">
              <div
                className="h-full bg-gradient-to-r from-emerald-500 via-lime-400 to-amber-500 rounded-full transition-all"
                style={{ width: '90.6%' }}
              />
            </div>
          </div>

          {/* Quick Connect Snippet */}
          <div className="mt-5 pt-4 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs font-code">
            <span className="text-slate-400">CS2 CONSOLE COMMAND:</span>
            <code className="text-lime-300 bg-black/60 px-2.5 py-1 rounded border border-slate-800 select-all">
              {serverIp}
            </code>
          </div>
        </div>

        {/* Secondary Card: Up Next Maps & Leaderboards */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-950/60 backdrop-blur-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Skull className="w-4 h-4 text-fuchsia-400" />
              <h3 className="font-cyber font-bold text-white text-sm">UPCOMING MAP ROTATION</h3>
            </div>
            <ul className="space-y-2 text-xs font-code">
              <li className="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/80">
                <span className="text-slate-300">1. ze_frostdrake_tower_v1</span>
                <span className="text-cyan-400 text-[10px]">NEXT</span>
              </li>
              <li className="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/80">
                <span className="text-slate-300">2. ze_shroomforest_v4_5</span>
                <span className="text-slate-500 text-[10px]">VOTED</span>
              </li>
              <li className="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/80">
                <span className="text-slate-300">3. ze_santassination_v3</span>
                <span className="text-slate-500 text-[10px]">QUEUE</span>
              </li>
            </ul>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800/80 text-[11px] font-tech text-slate-400">
            <div className="flex items-center gap-1.5 text-lime-400 mb-1">
              <ShieldAlert className="w-3.5 h-3.5" /> FastDL enabled with custom boss health HUD.
            </div>
            Auto-connect directly from this dashboard anytime!
          </div>
        </div>

      </div>
    </section>
  );
};
