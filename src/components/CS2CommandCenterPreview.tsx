import React, { useState } from 'react';
import { 
  Crosshair, 
  Download, 
  Sliders, 
  Cpu 
} from 'lucide-react';

export const CS2CommandCenterPreview: React.FC = () => {
  const [copiedLaunchCmd, setCopiedLaunchCmd] = useState(false);

  const handleCopyCmd = () => {
    navigator.clipboard.writeText('+exec autoexec.cfg -novid -high -threads 8 +fps_max 0');
    setCopiedLaunchCmd(true);
    setTimeout(() => setCopiedLaunchCmd(false), 2000);
  };

  return (
    <section id="cs2-command" className="relative w-full max-w-6xl mx-auto px-4 py-12">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8 border-b border-fuchsia-500/30 pb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 text-[10px] font-code rounded bg-fuchsia-950/80 text-fuchsia-300 border border-fuchsia-500/50">
              MODULE 01 // DESKTOP SUITE
            </span>
            <span className="text-xs font-code text-slate-400">
              BUILD: v0.9.4-RC // WINDOWS 64-BIT
            </span>
          </div>
          <h2 className="text-2xl md:text-3xl font-cyber font-black text-white tracking-wider flex items-center gap-3">
            CS2 COMMAND CENTER
            <span className="text-xs font-code px-2 py-1 bg-amber-950 text-amber-300 border border-amber-500/40 rounded uppercase">
              COMING SOON
            </span>
          </h2>
          <p className="text-sm font-tech text-slate-300 mt-1 max-w-2xl">
            All-in-one desktop companion app for Counter-Strike 2. Streamlined autoexec manager, pro crosshair repository, grenade lineup coordinates, and custom practice server configs.
          </p>
        </div>

        {/* Action Button */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => alert('CS2 Command Center closed beta drops soon! Sign up below or stay tuned to geronimohq.com.')}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-fuchsia-600 to-cyan-600 hover:from-fuchsia-500 hover:to-cyan-500 text-white font-cyber text-xs tracking-wider font-bold rounded-lg shadow-[0_0_20px_rgba(255,0,127,0.4)] transition-all transform hover:-translate-y-0.5 cursor-pointer"
          >
            <Download className="w-4 h-4" />
            GET BETA ACCESS
          </button>
        </div>
      </div>

      {/* Feature Showcase Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Card 1: Autoexec & Binds Manager */}
        <div className="relative p-5 rounded-xl border border-slate-800 bg-slate-950/60 backdrop-blur-md hover:border-fuchsia-500/60 transition-all group">
          <div className="w-10 h-10 rounded-lg bg-fuchsia-950/80 border border-fuchsia-500/40 flex items-center justify-center text-fuchsia-400 mb-4 group-hover:shadow-[0_0_15px_rgba(255,0,127,0.5)]">
            <Sliders className="w-5 h-5" />
          </div>
          <h3 className="font-cyber font-bold text-white text-base mb-2">
            Autoexec & Bind Studio
          </h3>
          <p className="text-xs text-slate-400 font-tech leading-relaxed mb-4">
            Visual editor for jumpthrow aliases, null-binds, volume clutch toggles, and viewmodel FOV calibrations with instant sync to your Steam directory.
          </p>
          <div className="bg-[#05070f] p-2.5 rounded border border-slate-800/80 font-code text-[11px] text-slate-300 flex items-center justify-between">
            <span className="text-fuchsia-300 truncate">bind "mouse4" "+jumpaction"</span>
            <span className="text-[10px] text-emerald-400">SYNCED</span>
          </div>
        </div>

        {/* Card 2: Pro Crosshairs & Lineup Radar */}
        <div className="relative p-5 rounded-xl border border-slate-800 bg-slate-950/60 backdrop-blur-md hover:border-cyan-500/60 transition-all group">
          <div className="w-10 h-10 rounded-lg bg-cyan-950/80 border border-cyan-500/40 flex items-center justify-center text-cyan-400 mb-4 group-hover:shadow-[0_0_15px_rgba(0,240,255,0.5)]">
            <Crosshair className="w-5 h-5" />
          </div>
          <h3 className="font-cyber font-bold text-white text-base mb-2">
            Tactical Grenade Alignments
          </h3>
          <p className="text-xs text-slate-400 font-tech leading-relaxed mb-4">
            Interactive visual database of Mirage, Inferno, Nuke, Anubis, and Dust2 smoke lineups with first-person video previews and crosshair placement guides.
          </p>
          <div className="flex items-center gap-2 text-[11px] font-code text-cyan-400">
            <span className="w-2 h-2 rounded-full bg-cyan-400" />
            <span>OVER 240+ TESTED SUB-TICK LINEUPS</span>
          </div>
        </div>

        {/* Card 3: Instant Practice Server Host */}
        <div className="relative p-5 rounded-xl border border-slate-800 bg-slate-950/60 backdrop-blur-md hover:border-lime-500/60 transition-all group">
          <div className="w-10 h-10 rounded-lg bg-lime-950/80 border border-lime-500/40 flex items-center justify-center text-lime-400 mb-4 group-hover:shadow-[0_0_15px_rgba(57,255,20,0.5)]">
            <Cpu className="w-5 h-5" />
          </div>
          <h3 className="font-cyber font-bold text-white text-base mb-2">
            Practice Server Bot Host
          </h3>
          <p className="text-xs text-slate-400 font-tech leading-relaxed mb-4">
            One-click warm-up server launcher with infinite ammo, grenade trajectory camera, bot placement toggles, and rethrow commands loaded automatically.
          </p>
          <button
            onClick={handleCopyCmd}
            className="w-full bg-[#05070f] hover:bg-slate-900 p-2 rounded border border-slate-800 font-code text-[11px] text-lime-300 flex items-center justify-between transition-colors cursor-pointer"
          >
            <span className="truncate">COPY RECOMMENDED LAUNCH OPTS</span>
            <span className="text-[10px] text-slate-400 font-bold">
              {copiedLaunchCmd ? 'COPIED!' : 'CLICK'}
            </span>
          </button>
        </div>

      </div>
    </section>
  );
};
