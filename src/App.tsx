import React, { useState, useEffect, useCallback } from 'react';
import { RetroGridCanvas } from './components/RetroGridCanvas';
import { CyberNavbar, scrollToSectionById } from './components/CyberNavbar';
import { PepeHeroStage } from './components/PepeHeroStage';
import { BananaHeroStage } from './components/BananaHeroStage';
import { DownloadRamSection } from './components/DownloadRamSection';
import { RoamingMemeGremlin } from './components/RoamingMemeGremlin';
import { ServerRadarPreview } from './components/ServerRadarPreview';
import { CS2AutoexecGeneratorSection } from './components/CS2AutoexecGeneratorSection';
import { CS2CommandCenterPreview } from './components/CS2CommandCenterPreview';
import { GeronimoDiscordPresence } from './components/GeronimoDiscordPresence';
import { DeployHudFooter } from './components/DeployHudFooter';
import { SecretGeronimoVault } from './components/SecretGeronimoVault';
import { ChaosAnomalyEngine } from './components/ChaosAnomalyEngine';
import { ChevronDown } from 'lucide-react';

const pickRandomBananaLoops = (): number => {
  const choices = [2, 3, 4];
  return choices[Math.floor(Math.random() * choices.length)];
};

export const App: React.FC = () => {
  // Randomize initial theme on open: either 'pepe' or 'banana'
  const [theme, setTheme] = useState<'pepe' | 'banana'>(() =>
    Math.random() < 0.5 ? 'pepe' : 'banana'
  );
  // Random loop count (2, 3, or 4 loops) before Banana Phone switches back to Pepe theme
  const [bananaTargetLoops, setBananaTargetLoops] = useState<number>(() => pickRandomBananaLoops());
  const [gremlinEnabled, setGremlinEnabled] = useState<boolean>(true);
  const [transitionBanner, setTransitionBanner] = useState<string | null>(null);
  const [isVaultOpen, setIsVaultOpen] = useState<boolean>(false);

  // Global Master Audio State (Persisted in localStorage; Defaults to 20% per Geronimo's request)
  const [masterVolume, setMasterVolume] = useState<number>(() => {
    try {
      const saved = localStorage.getItem('geronimo_master_vol');
      return saved !== null ? Math.max(0, Math.min(100, Number(saved))) : 20;
    } catch {
      return 20;
    }
  });

  const [isMasterMuted, setIsMasterMuted] = useState<boolean>(() => {
    try {
      return localStorage.getItem('geronimo_master_muted') === 'true';
    } catch {
      return false;
    }
  });

  const handleMasterVolumeChange = useCallback((newVol: number) => {
    const clamped = Math.max(0, Math.min(100, Math.round(newVol)));
    setMasterVolume(clamped);
    if (clamped > 0 && isMasterMuted) {
      setIsMasterMuted(false);
      try {
        localStorage.setItem('geronimo_master_muted', 'false');
      } catch {}
    }
    try {
      localStorage.setItem('geronimo_master_vol', String(clamped));
    } catch {}
  }, [isMasterMuted]);

  const handleToggleMasterMute = useCallback(() => {
    setIsMasterMuted((prev) => {
      const next = !prev;
      try {
        localStorage.setItem('geronimo_master_muted', String(next));
      } catch {}
      return next;
    });
  }, []);

  // Automatic Pepe -> Banana Phone transition after a random 2 minutes (120s) or 3 minutes (180s)
  useEffect(() => {
    if (theme !== 'pepe') return;

    const randomMinutes = Math.random() < 0.5 ? 2 : 3;
    const durationMs = randomMinutes * 60 * 1000;

    const timer = window.setTimeout(() => {
      setBananaTargetLoops(pickRandomBananaLoops());
      setTheme('banana');
      setTransitionBanner('🍌 SMOOTHLY TRANSITIONED TO BANANA PHONE THEME! RING RING RING!');
      window.setTimeout(() => setTransitionBanner(null), 5000);
    }, durationMs);

    return () => clearTimeout(timer);
  }, [theme]);

  // Handle direct URL hash navigation on initial page load (e.g., https://geronimohq.com/#download-ram)
  useEffect(() => {
    const handleInitialHash = () => {
      const rawHash = window.location.hash.replace('#', '').trim();
      if (rawHash) {
        // Small delay to ensure all DOM elements and images have completed initial mount/layout
        window.setTimeout(() => {
          scrollToSectionById(rawHash);
        }, 150);
      }
    };

    handleInitialHash();
    window.addEventListener('hashchange', handleInitialHash);
    return () => window.removeEventListener('hashchange', handleInitialHash);
  }, []);

  // Callback fired by BananaHeroStage right after the 2nd, 3rd, or 4th loop of Banana Phone music finishes completely
  const handleBananaLoopsFinished = useCallback(() => {
    setTheme('pepe');
    setTransitionBanner('🐸 BANANA PHONE LOOPS COMPLETE — SWITCHED BACK TO PEPE RETRO-FUTURISTIC THEME!');
    window.setTimeout(() => setTransitionBanner(null), 5000);
  }, []);

  const handleToggleTheme = () => {
    setTheme((prev) => {
      const next = prev === 'pepe' ? 'banana' : 'pepe';
      if (next === 'banana') {
        setBananaTargetLoops(pickRandomBananaLoops());
      }
      setTransitionBanner(
        next === 'banana'
          ? '🍌 ACTIVATED SECONDARY THEME: BANANA PHONE MODE!'
          : '🐸 ACTIVATED PRIMARY THEME: PEPE RETRO-FUTURISTIC MODE!'
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
        gremlinEnabled={gremlinEnabled}
        onToggleGremlin={() => setGremlinEnabled((prev) => !prev)}
        onOpenVault={() => setIsVaultOpen(true)}
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
        <div id="hero-stage" className="w-full max-w-5xl mx-auto pt-8 pb-4 px-4 text-center scroll-mt-32">
          
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
            . Featuring legendary animated memes, free cloud RAM downloads, live CS2 Zombie Escape server browser, Web Config Studio, and desktop gaming tools.
          </p>

          {/* Quick HUD Toolbar: Theme Toggle */}
          <div className="flex flex-wrap items-center justify-center gap-3 sm:gap-4 mt-4 text-[11px] font-code">
            <button
              onClick={handleToggleTheme}
              data-gremlin-ignore="true"
              className={`px-3 py-1.5 rounded-lg border cursor-pointer transition-all font-bold ${
                theme === 'banana'
                  ? 'bg-amber-950/90 border-yellow-400 text-yellow-300 shadow-[0_0_12px_rgba(250,204,21,0.4)]'
                  : 'bg-slate-900/80 border-cyan-500/40 text-cyan-300 hover:border-yellow-400'
              }`}
            >
              {theme === 'banana' ? '🐸 SWITCH TO PEPE THEME' : '🍌 SWITCH TO BANANA PHONE THEME'}
            </button>
          </div>
        </div>

        {/* HERO CENTER STAGE: SMOOTH TRANSITION BETWEEN PEPE HOLO STAGE & BANANA PHONE STAGE */}
        <div className="w-full transition-opacity duration-700">
          {theme === 'banana' ? (
            <BananaHeroStage
              targetLoops={bananaTargetLoops}
              onAllLoopsCompleted={handleBananaLoopsFinished}
              masterVolume={masterVolume}
              isMasterMuted={isMasterMuted}
              onToggleMasterMute={handleToggleMasterMute}
              onMasterVolumeChange={handleMasterVolumeChange}
            />
          ) : (
            <PepeHeroStage
              masterVolume={masterVolume}
              isMasterMuted={isMasterMuted}
              onToggleMasterMute={handleToggleMasterMute}
              onMasterVolumeChange={handleMasterVolumeChange}
            />
          )}
        </div>

        {/* Down Indicator */}
        <div className="flex flex-col items-center my-3 text-slate-500 hover:text-cyan-400 transition-colors">
          <span className="text-[10px] font-code tracking-widest uppercase mb-1">
            SCROLL FOR DOWNLOAD MORE RAM, ZE SERVER RADAR, CFG STUDIO &amp; CS2 APP
          </span>
          <ChevronDown className="w-4 h-4 animate-bounce text-cyan-400" />
        </div>

        {/* MEME MODULE: DOWNLOAD MORE RAM (16GB - 128GB Interactive UI + ZE Laser Mini-Game) */}
        <DownloadRamSection />

        {/* MODULE 1: ZOMBIE ESCAPE SERVER RADAR + 24H TIMELINE + MAP & LASER ENCYCLOPEDIA */}
        <ServerRadarPreview />

        {/* MODULE 2: INTERACTIVE WEB CS2 AUTOEXEC & ZE BINDS GENERATOR (#cfg-studio) */}
        <CS2AutoexecGeneratorSection />

        {/* MODULE 3: CS2 COMMAND CENTER DESKTOP SUITE (1-Click App Download v1.3.0) */}
        <CS2CommandCenterPreview />

      </main>

      {/* Floating Geronimo Discord-Style Live Presence (Fixed Lower-Left) */}
      <GeronimoDiscordPresence />

      {/* Interactive Random Chaos Anomaly Protocol Button */}
      <ChaosAnomalyEngine />

      {/* Classified Geronimo Secret Vault Chamber Modal */}
      <SecretGeronimoVault
        isOpen={isVaultOpen}
        onClose={() => setIsVaultOpen(false)}
      />

      {/* Clean Transmission / Contact Terminal Footer */}
      <DeployHudFooter />
    </div>
  );
};

export default App;
