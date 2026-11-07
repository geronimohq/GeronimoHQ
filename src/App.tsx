import React, { useState, useEffect } from 'react';
import { RetroGridCanvas } from './components/RetroGridCanvas';
import { CyberNavbar } from './components/CyberNavbar';
import { PepeHeroStage } from './components/PepeHeroStage';
import { BananaHeroStage } from './components/BananaHeroStage';
import { DownloadRamSection } from './components/DownloadRamSection';
import { RoamingMemeGremlin } from './components/RoamingMemeGremlin';
import { ServerRadarPreview } from './components/ServerRadarPreview';
import { CS2CommandCenterPreview } from './components/CS2CommandCenterPreview';
import { GeronimoDiscordPresence } from './components/GeronimoDiscordPresence';
import { DeployHudFooter } from './components/DeployHudFooter';
import { cyberSynth } from './utils/synthAudio';
import { ChevronDown, Cpu } from 'lucide-react';

export const App: React.FC = () => {
  const [theme, setTheme] = useState<'pepe' | 'banana'>('pepe');
  const [autoSwitchRemainingSec, setAutoSwitchRemainingSec] = useState<number | null>(120);
  const [gremlinEnabled, setGremlinEnabled] = useState<boolean>(true);
  const [transitionBanner, setTransitionBanner] = useState<string | null>(null);

  // Sync synthAudio mode whenever theme changes
  useEffect(() => {
    cyberSynth.setMode(theme);
  }, [theme]);

  // 2-Minute (120s) Automatic Smooth Transition from Pepe Retro-Futuristic to Banana Phone Theme
  useEffect(() => {
    if (autoSwitchRemainingSec === null) return;

    const timer = window.setInterval(() => {
      setAutoSwitchRemainingSec((prev) => {
        if (prev === null) return null;
        if (prev <= 1) {
          setTheme('banana');
          setTransitionBanner('🍌 2 MINUTES ELAPSED — SMOOTHLY TRANSITIONED TO BANANA PHONE THEME! RING RING RING!');
          window.setTimeout(() => setTransitionBanner(null), 6000);
          return null;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [autoSwitchRemainingSec]);

  const handleToggleTheme = () => {
    setAutoSwitchRemainingSec(null); // Stop auto-timer once user manually switches
    setTheme((prev) => {
      const next = prev === 'pepe' ? 'banana' : 'pepe';
      setTransitionBanner(
        next === 'banana'
          ? '🍌 ACTIVATED SECONDARY THEME: BANANA PHONE MODE!'
          : '🐸 RESTORED PRIMARY THEME: PEPE RETRO-FUTURISTIC MODE!'
      );
      window.setTimeout(() => setTransitionBanner(null), 4000);
      return next;
    });
  };

  return (
    <div
      className={`relative min-h-screen text-slate-100 flex flex-col font-tech transition-colors duration-1000 selection:bg-fuchsia-500 selection:text-white ${
        theme === 'banana' ? 'bg-[#090701]' : 'bg-[#05070d]'
      }`}
    >
      {/* 3D Wireframe Retro-Futuristic Background Grid (Adapts smoothly to Pepe or Banana Phone theme) */}
      <RetroGridCanvas
        glowColor={theme === 'banana' ? '#f59e0b' : '#ff007f'}
        gridColor={theme === 'banana' ? '#facc15' : '#00f0ff'}
      />

      {/* Interactive Roaming Pepe / Banana Character */}
      <RoamingMemeGremlin theme={theme} enabled={gremlinEnabled} />

      {/* Cyberpunk HUD Navbar */}
      <CyberNavbar
        theme={theme}
        onToggleTheme={handleToggleTheme}
        autoSwitchRemainingSec={autoSwitchRemainingSec}
        gremlinEnabled={gremlinEnabled}
        onToggleGremlin={() => setGremlinEnabled((prev) => !prev)}
      />

      {/* Smooth Theme Transition Toast Notification */}
      {transitionBanner && (
        <div className="fixed top-16 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-xl border border-yellow-400 bg-slate-950/95 text-yellow-300 font-cyber text-xs font-bold shadow-[0_0_25px_rgba(250,204,21,0.6)] animate-bounce">
          {transitionBanner}
        </div>
      )}

      {/* Main Content Area */}
      <main className="relative z-10 flex-grow flex flex-col items-center">
        
        {/* HERO TITLE & INTRO BANNER */}
        <div id="hero-stage" className="w-full max-w-5xl mx-auto pt-8 pb-4 px-4 text-center">
          
          {/* Top Status Pill */}
          <div
            className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-code mb-4 transition-all duration-700 ${
              theme === 'banana'
                ? 'bg-amber-950/80 border border-yellow-400/60 text-yellow-300 shadow-[0_0_15px_rgba(250,204,21,0.35)]'
                : 'bg-cyan-950/70 border border-cyan-400/50 text-cyan-300 shadow-[0_0_15px_rgba(0,240,255,0.3)]'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full animate-pulse ${
                theme === 'banana' ? 'bg-yellow-400' : 'bg-cyan-400'
              }`}
            />
            <span>
              {theme === 'banana'
                ? 'GERONIMO_HQ // BANANA PHONE HOTLINE ONLINE 🍌📞'
                : 'GERONIMO_HQ NEURAL LINK // ONLINE'}
            </span>
          </div>

          {/* Main Glitch / Cyber Title */}
          <h1
            className={`text-4xl sm:text-5xl md:text-6xl font-cyber font-black tracking-wider text-transparent bg-clip-text mb-3 transition-all duration-700 ${
              theme === 'banana'
                ? 'bg-gradient-to-r from-yellow-300 via-amber-400 to-red-400 drop-shadow-[0_0_25px_rgba(250,204,21,0.5)]'
                : 'bg-gradient-to-r from-cyan-400 via-fuchsia-400 to-lime-300 drop-shadow-[0_0_25px_rgba(0,240,255,0.4)]'
            }`}
          >
            GERONIMO<span className="text-white">HQ</span>
          </h1>

          <p className="max-w-2xl mx-auto text-sm sm:text-base md:text-lg font-tech text-slate-300 tracking-wide leading-relaxed">
            Personal Cyber-Hub &amp; Experimental Holo-Chamber for{' '}
            <strong className={theme === 'banana' ? 'text-yellow-400' : 'text-cyan-400'}>
              geronimohq.com
            </strong>
            . Featuring legendary animated memes, free cloud RAM downloads, live CS2 Zombie Escape server browser, and desktop gaming tools.
          </p>

          {/* Quick Info & Action Tags */}
          <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-3 mt-4 text-[11px] font-code">
            <button
              onClick={handleToggleTheme}
              data-gremlin-ignore="true"
              className={`px-3 py-1 rounded border cursor-pointer transition-all font-bold ${
                theme === 'banana'
                  ? 'bg-amber-950/90 border-yellow-400 text-yellow-300 shadow-[0_0_12px_rgba(250,204,21,0.4)]'
                  : 'bg-slate-900/80 border-cyan-500/40 text-cyan-300 hover:border-yellow-400'
              }`}
            >
              {theme === 'banana' ? '🐸 SWITCH TO PEPE THEME' : '🍌 SWITCH TO BANANA PHONE THEME'}
            </button>
            <a
              href="#download-ram"
              className="px-3 py-1 rounded bg-lime-950/80 border border-lime-400/60 text-lime-300 hover:bg-lime-900/80 flex items-center gap-1 font-bold"
            >
              <Cpu className="w-3 h-3" />
              <span>💾 DOWNLOAD FREE RAM (16GB-128GB)</span>
            </a>
            <a
              href="#server-radar"
              className="px-2.5 py-1 rounded bg-slate-900/80 border border-slate-800 text-fuchsia-300 hover:border-fuchsia-400"
            >
              🎮 ZE STEAM CONNECT
            </a>
            <a
              href="#cs2-command"
              className="px-2.5 py-1 rounded bg-slate-900/80 border border-slate-800 text-amber-300 hover:border-amber-400"
            >
              💻 CS2 DESKTOP APP
            </a>
          </div>
        </div>

        {/* HERO CENTER STAGE: SMOOTH TRANSITION BETWEEN PEPE HOLO STAGE & BANANA PHONE STAGE */}
        <div className="w-full transition-opacity duration-700">
          {theme === 'banana' ? <BananaHeroStage /> : <PepeHeroStage />}
        </div>

        {/* Down Indicator */}
        <div className="flex flex-col items-center my-3 text-slate-500 hover:text-cyan-400 transition-colors">
          <span className="text-[10px] font-code tracking-widest uppercase mb-1">
            SCROLL FOR DOWNLOAD MORE RAM, ZE SERVER RADAR &amp; CS2 APP
          </span>
          <ChevronDown className="w-4 h-4 animate-bounce text-cyan-400" />
        </div>

        {/* MEME MODULE: DOWNLOAD MORE RAM (16GB - 128GB Interactive UI for Geronimo's Discord Bio) */}
        <DownloadRamSection />

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
