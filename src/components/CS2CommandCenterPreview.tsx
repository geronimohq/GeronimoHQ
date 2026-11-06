import React from 'react';
import { 
  Download, 
  Sliders, 
  Cpu, 
  ShieldCheck, 
  Target, 
  Zap, 
  CheckCircle2 
} from 'lucide-react';

export const CS2CommandCenterPreview: React.FC = () => {
  const downloadUrl = '/downloads/CS2_Command_Center.exe';

  return (
    <section id="cs2-command" className="relative w-full max-w-6xl mx-auto px-4 py-12">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8 border-b border-fuchsia-500/30 pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="px-2.5 py-0.5 text-[10px] font-code rounded bg-fuchsia-950/80 text-fuchsia-300 border border-fuchsia-500/50">
              MODULE 01 // DESKTOP APPLICATION
            </span>
            <span className="text-xs font-code text-slate-400">
              WINDOWS 10 / 11 64-BIT // PORTABLE EXE
            </span>
          </div>
          <h2 className="text-2xl md:text-3xl font-cyber font-black text-white tracking-wider flex items-center gap-3">
            CS2 COMMAND CENTER
            <span className="text-xs font-code px-2 py-0.5 bg-fuchsia-950 text-fuchsia-300 border border-fuchsia-500/50 rounded uppercase">
              v1.0.0
            </span>
          </h2>
          <p className="text-sm font-tech text-slate-300 mt-1 max-w-2xl">
            Want seamless PC integration without manual file editing? Download the official standalone desktop suite to configure Autoexec, pro binds, launch options, and slot sniping with zero hassle.
          </p>
        </div>

        {/* Primary Download CTA */}
        <div className="flex flex-col items-start md:items-end gap-1.5">
          <a
            href={downloadUrl}
            download="CS2_Command_Center.exe"
            className="flex items-center gap-2.5 px-6 py-3 bg-gradient-to-r from-fuchsia-600 via-pink-600 to-cyan-600 hover:from-fuchsia-500 hover:to-cyan-500 text-white font-cyber text-xs tracking-wider font-bold rounded-xl shadow-[0_0_25px_rgba(255,0,127,0.4)] transition-all transform hover:-translate-y-0.5 cursor-pointer"
          >
            <Download className="w-4 h-4 animate-bounce" />
            <span>DOWNLOAD APP (.EXE)</span>
          </a>
          <span className="text-[11px] font-code text-slate-400">
            Portable &bull; ~31 MB &bull; No installation required
          </span>
        </div>
      </div>

      {/* 4 Core Desktop Capabilities Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        
        {/* Capability 1: Autoexec & Binds */}
        <div className="p-5 rounded-xl border border-slate-800 bg-slate-950/60 backdrop-blur-md hover:border-fuchsia-500/60 transition-all group">
          <div className="w-10 h-10 rounded-lg bg-fuchsia-950/80 border border-fuchsia-500/40 flex items-center justify-center text-fuchsia-400 mb-3 group-hover:shadow-[0_0_15px_rgba(255,0,127,0.5)]">
            <Sliders className="w-5 h-5" />
          </div>
          <h3 className="font-cyber font-bold text-white text-sm mb-1.5">
            Autoexec & Binds
          </h3>
          <p className="text-xs text-slate-400 font-tech leading-relaxed mb-3">
            One-click installer writes directly into your Steam CS2 config folder. Includes pro jumpthrows, null-binds, sub-tick rates, and audio clarity.
          </p>
          <div className="text-[10px] font-code text-fuchsia-400 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            <span>Zero manual file copying</span>
          </div>
        </div>

        {/* Capability 2: Steam Launch Options */}
        <div className="p-5 rounded-xl border border-slate-800 bg-slate-950/60 backdrop-blur-md hover:border-cyan-500/60 transition-all group">
          <div className="w-10 h-10 rounded-lg bg-cyan-950/80 border border-cyan-500/40 flex items-center justify-center text-cyan-400 mb-3 group-hover:shadow-[0_0_15px_rgba(0,240,255,0.5)]">
            <Cpu className="w-5 h-5" />
          </div>
          <h3 className="font-cyber font-bold text-white text-sm mb-1.5">
            Launch Options Helper
          </h3>
          <p className="text-xs text-slate-400 font-tech leading-relaxed mb-3">
            Preconfigured presets for competitive baseline, high thread affinity, video splash skip (<code className="text-cyan-300">-novid</code>), and input latency tuning.
          </p>
          <div className="text-[10px] font-code text-cyan-400 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            <span>One-click clipboard sync</span>
          </div>
        </div>

        {/* Capability 3: Silent 64/64 Slot Sniper */}
        <div className="p-5 rounded-xl border border-slate-800 bg-slate-950/60 backdrop-blur-md hover:border-lime-500/60 transition-all group">
          <div className="w-10 h-10 rounded-lg bg-lime-950/80 border border-lime-500/40 flex items-center justify-center text-lime-400 mb-3 group-hover:shadow-[0_0_15px_rgba(57,255,20,0.5)]">
            <Target className="w-5 h-5" />
          </div>
          <h3 className="font-cyber font-bold text-white text-sm mb-1.5">
            Silent Slot Sniper
          </h3>
          <p className="text-xs text-slate-400 font-tech leading-relaxed mb-3">
            Monitors full 64/64 Zombie Escape servers in the background and automatically triggers a connection the instant a slot frees up.
          </p>
          <div className="text-[10px] font-code text-lime-400 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            <span>Runs in system tray</span>
          </div>
        </div>

        {/* Capability 4: GPU MPO & RAM Cleaner */}
        <div className="p-5 rounded-xl border border-slate-800 bg-slate-950/60 backdrop-blur-md hover:border-amber-500/60 transition-all group">
          <div className="w-10 h-10 rounded-lg bg-amber-950/80 border border-amber-500/40 flex items-center justify-center text-amber-400 mb-3 group-hover:shadow-[0_0_15px_rgba(251,191,36,0.5)]">
            <Zap className="w-5 h-5" />
          </div>
          <h3 className="font-cyber font-bold text-white text-sm mb-1.5">
            MPO & RAM Optimizer
          </h3>
          <p className="text-xs text-slate-400 font-tech leading-relaxed mb-3">
            Fixes Windows Multi-Plane Overlay (MPO) Alt-Tab black screens on AMD & NVIDIA GPUs, plus flushes standby memory cache before matches.
          </p>
          <div className="text-[10px] font-code text-amber-400 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            <span>Discord RPC support</span>
          </div>
        </div>

      </div>

      {/* Safety & VAC Compliance Guarantee Banner */}
      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs font-tech text-slate-400">
        <div className="flex items-center gap-2.5">
          <ShieldCheck className="w-5 h-5 text-emerald-400 flex-shrink-0" />
          <span>
            <strong className="text-white">100% VAC-Safe Guarantee:</strong> The desktop app modifies standard CS2 text config files (<code className="text-cyan-300">.cfg</code>) and uses Valve's official Steam protocols. It does not inject into game memory or modify DLLs.
          </span>
        </div>
        <a
          href={downloadUrl}
          download="CS2_Command_Center.exe"
          className="px-4 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-fuchsia-300 font-code text-xs border border-fuchsia-500/40 flex items-center gap-1.5 transition-colors flex-shrink-0"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Get Executable</span>
        </a>
      </div>
    </section>
  );
};
