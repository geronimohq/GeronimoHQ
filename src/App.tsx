import React, { useState, useEffect, useCallback, lazy, Suspense } from 'react';
import { RetroGridCanvas } from './components/RetroGridCanvas';
import { CyberNavbar, scrollToSectionById } from './components/CyberNavbar';
import { PepeHeroStage } from './components/PepeHeroStage';
import { BananaHeroStage } from './components/BananaHeroStage';
import { DownloadRamSection } from './components/DownloadRamSection';
import { ServerRadarPreview } from './components/ServerRadarPreview';
import { CS2AutoexecGeneratorSection } from './components/CS2AutoexecGeneratorSection';
import { CS2CommandCenterPreview } from './components/CS2CommandCenterPreview';
import { DeployHudFooter } from './components/DeployHudFooter';
import { ChevronDown, PhoneCall, Radio, ShieldCheck } from 'lucide-react';

// AUDIT P4: floating overlays (no navbar anchors inside) load as separate chunks after the
// first paint, so the main bundle the visitor waits for is smaller.
const RoamingMemeGremlin = lazy(() => import('./components/RoamingMemeGremlin').then((m) => ({ default: m.RoamingMemeGremlin })));
const GeronimoDiscordPresence = lazy(() => import('./components/GeronimoDiscordPresence').then((m) => ({ default: m.GeronimoDiscordPresence })));
const ChaosAnomalyEngine = lazy(() => import('./components/ChaosAnomalyEngine').then((m) => ({ default: m.ChaosAnomalyEngine })));

const pickRandomBananaLoops = (): number => {
  const choices = [2, 3, 4];
  return choices[Math.floor(Math.random() * choices.length)];
};

export const App: React.FC = () => {
  // Handle direct CS2 Steam Connect Trampoline (e.g., /connect?ip=74.91.124.21:27015)
  useEffect(() => {
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const ipParam = urlParams.get('connect') || urlParams.get('ip') || (window.location.pathname.startsWith('/connect') ? (urlParams.get('server') || '74.91.124.21:27015') : null);
      if (ipParam) {
        const cleanIp = ipParam.replace(/[^0-9a-zA-Z.:-]/g, '').trim().slice(0, 120);
        if (cleanIp && !window.location.pathname.startsWith('/connect')) {
          // AUDIT 1d-W1: never launch Steam straight from the home page. Hand off to
          // /connect/, which validates host:port, only auto-connects to catalog
          // servers, and asks the visitor to click for anything else.
          window.location.replace(`/connect/?ip=${encodeURIComponent(cleanIp)}`);
        }
      }
    } catch {}
  }, []);

  const [theme, setTheme] = useState<'pepe' | 'banana'>(() =>
    Math.random() < 0.5 ? 'pepe' : 'banana'
  );
  // Random loop count (2, 3, or 4 loops) before Banana Phone switches back to Pepe theme
  const [bananaTargetLoops, setBananaTargetLoops] = useState<number>(() => pickRandomBananaLoops());
  const [gremlinEnabled, setGremlinEnabled] = useState<boolean>(true);
  const [transitionBanner, setTransitionBanner] = useState<string | null>(null);

  // Global Master Audio State (Persisted in localStorage; Defaults to 15% per Geronimo's request)
  const [masterVolume, setMasterVolume] = useState<number>(() => {
    try {
      const saved = localStorage.getItem('geronimo_master_vol');
      return saved !== null ? Math.max(0, Math.min(100, Number(saved))) : 15;
    } catch {
      return 15;
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

  // Symmetrical Theme Switching Cycle:
  // Pepe (exact 3m 16s track) <-> Banana Phone (exact 3m 16s track) with identical transition & audio lifecycle
  useEffect(() => {
    const THEME_TRACK_DURATION_MS = (3 * 60 + 16) * 1000; // 196,000 ms (3m 16s)
    const timer = window.setTimeout(() => {
      if (theme === 'pepe') {
        setTheme('banana');
        setTransitionBanner('🍌 3:16 COMPLETE — SMOOTHLY SWITCHED TO BANANA PHONE THEME!');
      } else {
        setTheme('pepe');
        setTransitionBanner('🐸 3:16 COMPLETE — SMOOTHLY SWITCHED TO PEPE THEME!');
      }
      window.setTimeout(() => setTransitionBanner(null), 5000);
    }, THEME_TRACK_DURATION_MS);
    return () => clearTimeout(timer);
  }, [theme]);

  // Handle direct URL hash navigation on initial page load (e.g., https://geronimohq.com/#download-ram)
  useEffect(() => {
    const handleInitialHash = () => {
      const rawHash = window.location.hash.replace('#', '').trim();
      if (rawHash) {
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
    <div data-theme={theme} className={`relative min-h-screen text-white flex flex-col font-tech ${theme === "banana" ? "bg-[#070B09] selection:bg-[#FFE135] selection:text-[#070B09]" : "bg-[#060B07] selection:bg-[#2ECC71] selection:text-[#070B09]"}`}>

      {/* 3D Wireframe Retro-Futuristic Background Grid (Tactical Pepe Green & Cyber Banana Yellow) */}
      <RetroGridCanvas
        glowColor={theme === 'banana' ? '#FFE135' : '#2ECC71'}
        gridColor={theme === 'banana' ? '#FACC15' : '#27AE60'}
      />

      {/* AUDIT P5: keyboard users can jump past the navbar */}
      <a href="#main-content" className="skip-link">Skip to content</a>

      {/* Interactive Roaming Pepe / Banana Character */}
      <Suspense fallback={null}>
        <RoamingMemeGremlin theme={theme} enabled={gremlinEnabled} />
      </Suspense>

      {/* Unified Top Command Dock & Telemetry Strip */}
      <CyberNavbar
        theme={theme}
        gremlinEnabled={gremlinEnabled}
        onToggleGremlin={() => setGremlinEnabled((prev) => !prev)}
      />

      {/* Smooth Theme Transition Toast Notification */}
      {transitionBanner && (
        <div className={`fixed top-24 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-xl border ${theme === "banana" ? "border-[#FFE135] bg-[#0E1512]/95 text-[#FFE135] shadow-[0_0_25px_rgba(255,225,53,0.5)]" : "border-[#2ECC71] bg-[#07130A]/95 text-[#2ECC71] shadow-[0_0_25px_rgba(46,204,113,0.5)]"} font-cyber text-xs font-bold animate-bounce`}>
          {transitionBanner}
        </div>
      )}

      {/* Main Content Area */}
      <main id="main-content" tabIndex={-1} className="relative z-10 flex-grow flex flex-col items-center outline-none">
        
        {/* ASYMMETRIC BENTO-GRID COMMAND HEADER */}
        <div id="hero-stage" className="w-full max-w-6xl mx-auto pt-6 pb-2 px-4 scroll-mt-32">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-3">
            
            {/* Left Bento Card (8 Cols): Main Cyber-Deck Identity & Command Actions */}
            <div className={`lg:col-span-8 bento-card ${theme === "banana" ? "bento-accent-banana" : "bento-accent-pepe"} relative overflow-hidden flex flex-col justify-between`}>
              {/* Subtle Tactical Frog / Rotary SVG Watermark */}
              <svg
                viewBox="0 0 120 120"
                className={`absolute -right-6 -bottom-6 w-40 h-40 opacity-[0.04] pointer-events-none ${theme === "banana" ? "text-[#FFE135]" : "text-[#2ECC71]"}`}
                fill="currentColor"
              >
                <circle cx="60" cy="60" r="50" stroke="currentColor" strokeWidth="4" fill="none" strokeDasharray="8 6" />
                <circle cx="42" cy="45" r="10" />
                <circle cx="78" cy="45" r="10" />
                <path d="M35 75 Q60 95 85 75" stroke="currentColor" strokeWidth="6" fill="none" strokeLinecap="round" />
              </svg>

              <div>
                <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                  <span className="tier-2-header flex items-center gap-1.5">
                    <Radio className={`w-3.5 h-3.5 ${theme === "banana" ? "text-[#FFE135]" : "text-[#2ECC71]"}`} />
                    <span>TACTICAL PEPE &amp; BANANA PHONE CYBER-DECK // SYS.CORE</span>
                  </span>
                  <span className={`tier-5-badge ${theme === "banana" ? "bg-[#FFE135]/15 text-[#FFE135] border border-[#FFE135]/40" : "bg-[#2ECC71]/15 text-[#2ECC71] border border-[#2ECC71]/40"}`}>
                    ● UPLINK ONLINE
                  </span>
                </div>

                <div className="flex flex-wrap items-baseline gap-3 mb-2">
                  <h1 className="tier-1-title">
                    GERONIMO<span className={theme === "banana" ? "text-[#FFE135]" : "text-[#2ECC71]"}>HQ</span> COMMAND SUITE
                  </h1>
                  <span className={`text-xs font-code ${theme === "banana" ? "text-[#FFE135]" : "text-[#2ECC71]"}`}>
                    [geronimohq.com]
                  </span>
                </div>

                <p className="tier-4-body max-w-2xl">
                  Unified retro-cyberpunk command deck for <strong className={theme === "banana" ? "text-[#FFE135]" : "text-[#E48716]"}>geronimohq.com</strong>. Blending interactive Pepe &amp; Rotary Banana Phone holo-chambers, live CS2 Zombie Escape server telemetry, a Config Studio, and the standalone <strong className={theme === "banana" ? "text-[#FFE135]" : "text-[#2ECC71]"}>CS2 Command Center</strong> desktop utility.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-2.5 mt-4 pt-3 border-t border-[#1E2E26]">
                <button
                  onClick={handleToggleTheme}
                  data-gremlin-ignore="true"
                  className={`btn-cyber-34 ${theme === "banana" ? "btn-banana-cta" : "btn-pepe-cta"}`}
                >
                  <PhoneCall className="w-3.5 h-3.5" />
                  <span>{theme === 'banana' ? '🐸 SWITCH TO PEPE HOLO' : '🍌 SWITCH TO BANANA PHONE'}</span>
                </button>
              </div>
            </div>

            {/* Right Bento Card (4 Cols): Rotary Banana Hotline & Pepe Telemetry Diagnostics */}
            <div className={`lg:col-span-4 bento-card ${theme === "banana" ? "bento-accent-banana" : "bento-accent-pepe"} flex flex-col justify-between`}>
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <span className="tier-2-header-pepe flex items-center gap-1.5">
                    <PhoneCall className={`w-3.5 h-3.5 ${theme === "banana" ? "text-[#FFE135]" : "text-[#2ECC71]"}`} />
                    <span>ROTARY SIGNAL &amp; AUDIO</span>
                  </span>
                  <span className={`tier-5-badge ${theme === "banana" ? "bg-[#FFE135]/15 text-[#FFE135] border border-[#FFE135]/40" : "bg-[#2ECC71]/15 text-[#2ECC71] border border-[#2ECC71]/40"}`}>
                    3:16 CYCLE
                  </span>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-[#070B09] border border-[#1E2E26]">
                    <span className="tier-4-body">Active Holo-Deck</span>
                    <span className={`tier-3-label ${theme === "banana" ? "text-[#FFE135]" : "text-[#2ECC71]"}`}>
                      {theme === 'banana' ? '🍌 Banana Hotline' : '🐸 Pepe Matrix'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-[#070B09] border border-[#1E2E26]">
                    <span className="tier-4-body">Audio Synchronization</span>
                    <span className={`tier-5-badge ${theme === "banana" ? "bg-[#FFE135]/15 text-[#FFE135] border border-[#FFE135]/40" : "bg-[#2ECC71]/15 text-[#2ECC71] border border-[#2ECC71]/40"}`}>
                      {isMasterMuted ? 'MUTED' : `ACTIVE (${masterVolume}%)`}
                    </span>
                  </div>

                  <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-[#070B09] border border-[#1E2E26]">
                    <span className="tier-4-body">Game memory access</span>
                    <span className={`tier-5-badge ${theme === "banana" ? "bg-[#FFE135]/15 text-[#FFE135] border border-[#FFE135]/40" : "bg-[#2ECC71]/15 text-[#2ECC71] border border-[#2ECC71]/40"}`}>
                      <ShieldCheck className="w-3 h-3" /> NONE
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-3 pt-2.5 border-t border-[#1E2E26] flex items-center justify-between text-[11px] font-code text-[#94A39E]">
                <span>TICK: 64 + SUB-TICK</span>
                <span className={`${theme === "banana" ? "text-[#FFE135]" : "text-[#2ECC71]"} font-bold`}>STATUS: OPTIMAL</span>
              </div>
            </div>

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
        <div className="flex flex-col items-center my-2 text-[#94A39E] hover:text-[#FFE135] transition-colors">
          <span className="text-[11px] font-code tracking-widest uppercase mb-1">
            SCROLL FOR BENTO MODULES: RAM DOWNLOADER, ZE SERVER RADAR, CFG STUDIO &amp; DESKTOP SUITE
          </span>
          <ChevronDown className={`w-4 h-4 animate-bounce ${theme === "banana" ? "text-[#FFE135]" : "text-[#2ECC71]"}`} />
        </div>

        {/* MEME MODULE: DOWNLOAD MORE RAM (16GB - 128GB Interactive UI + ZE Laser Mini-Game) */}
        <DownloadRamSection />

        {/* MODULE 1: ZOMBIE ESCAPE SERVER RADAR + 24H TIMELINE + MAP & LASER ENCYCLOPEDIA */}
        <ServerRadarPreview />

        {/* MODULE 2: INTERACTIVE WEB CS2 AUTOEXEC & ZE BINDS GENERATOR (#cfg-studio) */}
        <CS2AutoexecGeneratorSection />

        {/* MODULE 3: CS2 COMMAND CENTER DESKTOP SUITE (1-Click App Download v2.0.5) */}
        <CS2CommandCenterPreview />

      </main>

      {/* Floating Geronimo Discord-Style Live Presence (Fixed Lower-Left) */}
      <Suspense fallback={null}>
        <GeronimoDiscordPresence />
      </Suspense>
      {/* Interactive Random Chaos Anomaly Protocol Button */}
      <Suspense fallback={null}>
        <ChaosAnomalyEngine />
      </Suspense>
      {/* Clean Transmission / Contact Terminal Footer */}
      <DeployHudFooter />
    </div>
  );
};

export default App;
