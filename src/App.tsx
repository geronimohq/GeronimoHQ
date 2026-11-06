import React from 'react';
import { RetroGridCanvas } from './components/RetroGridCanvas';
import { CyberNavbar } from './components/CyberNavbar';
import { PepeHeroStage } from './components/PepeHeroStage';
import { ServerRadarPreview } from './components/ServerRadarPreview';
import { CS2CommandCenterPreview } from './components/CS2CommandCenterPreview';
import { GeronimoDiscordPresence } from './components/GeronimoDiscordPresence';
import { DeployHudFooter } from './components/DeployHudFooter';
import { ChevronDown } from 'lucide-react';

export const App: React.FC = () => {
  return (
    <div className="relative min-h-screen bg-[#05070d] text-slate-100 flex flex-col font-tech selection:bg-fuchsia-500 selection:text-white">
      {/* 3D Wireframe Retro-Futuristic Background Grid */}
      <RetroGridCanvas glowColor="#ff007f" gridColor="#00f0ff" />

      {/* Cyberpunk HUD Navbar */}
      <CyberNavbar />

      {/* Main Content Area */}
      <main className="relative z-10 flex-grow flex flex-col items-center">
        
        {/* HERO TITLE & INTRO BANNER */}
        <div id="hero-stage" className="w-full max-w-5xl mx-auto pt-8 pb-4 px-4 text-center">
          
          {/* Top Status Pill */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/70 border border-cyan-400/50 text-cyan-300 text-xs font-code mb-4 shadow-[0_0_15px_rgba(0,240,255,0.3)]">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <span>GERONIMO_HQ NEURAL LINK // ONLINE</span>
          </div>

          {/* Main Glitch / Cyber Title */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-cyber font-black tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-fuchsia-400 to-lime-300 mb-3 drop-shadow-[0_0_25px_rgba(0,240,255,0.4)]">
            GERONIMO<span className="text-white">HQ</span>
          </h1>

          <p className="max-w-2xl mx-auto text-sm sm:text-base md:text-lg font-tech text-slate-300 tracking-wide leading-relaxed">
            Personal Cyber-Hub & Experimental Holo-Chamber for <strong className="text-cyan-400">geronimohq.com</strong>.
            Featuring legendary animated memes, live CS2 Zombie Escape server browser, and desktop gaming tools.
          </p>

          {/* Quick Info Tags */}
          <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-3 mt-4 text-[11px] font-code text-slate-400">
            <span className="px-2.5 py-1 rounded bg-slate-900/80 border border-slate-800 text-cyan-300">
              ⚡ RETRO-FUTURISTIC HUD
            </span>
            <span className="px-2.5 py-1 rounded bg-slate-900/80 border border-slate-800 text-fuchsia-300">
              🐸 3x ANIMATED PEPES
            </span>
            <span className="px-2.5 py-1 rounded bg-slate-900/80 border border-slate-800 text-lime-300">
              🎮 ZE STEAM CONNECT
            </span>
            <span className="px-2.5 py-1 rounded bg-slate-900/80 border border-slate-800 text-amber-300">
              💻 CS2 DESKTOP APP
            </span>
          </div>
        </div>

        {/* HERO CENTER STAGE: THREE ANIMATED PEPES ON 3D HOLO PEDESTAL */}
        <PepeHeroStage />

        {/* Down Indicator */}
        <div className="flex flex-col items-center my-4 text-slate-500 hover:text-cyan-400 transition-colors">
          <span className="text-[10px] font-code tracking-widest uppercase mb-1">
            SCROLL FOR ZE SERVER RADAR & TOOLS
          </span>
          <ChevronDown className="w-4 h-4 animate-bounce text-cyan-400" />
        </div>

        {/* MODULE 1: ZOMBIE ESCAPE SERVER RADAR (Primary Web Utility with Steam Connect) */}
        <ServerRadarPreview />

        {/* MODULE 2: CS2 COMMAND CENTER DESKTOP SUITE (1-Click App Download) */}
        <CS2CommandCenterPreview />

      </main>

      {/* Floating Geronimo Discord-Style Live Presence (Fixed Lower-Left) */}
      <GeronimoDiscordPresence />

      {/* Clean Transmission / Contact Terminal Footer */}
      <DeployHudFooter />
    </div>
  );
};

export default App;
