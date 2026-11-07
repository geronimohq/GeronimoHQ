import React, { useState, useEffect } from 'react';
import { CryingPepe } from './pepes/CryingPepe';
import { LaughingPepe } from './pepes/LaughingPepe';
import { DancingPepe } from './pepes/DancingPepe';
import { cyberSynth } from '../utils/synthAudio';
import { Activity, Volume2, VolumeX } from 'lucide-react';

type PepeViewMode = 'all' | 'cry' | 'laugh' | 'dance';

export const PepeHeroStage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<PepeViewMode>('all');
  const [isMusicOn, setIsMusicOn] = useState<boolean>(true);

  // Automatically start Pepe Synth when PepeHeroStage mounts (and stop cleanly when unmounted or toggled off)
  useEffect(() => {
    if (isMusicOn) {
      cyberSynth.startSynth();
    } else {
      cyberSynth.stopSynth();
    }
    return () => {
      cyberSynth.stopSynth();
    };
  }, [isMusicOn]);

  return (
    <section className="relative w-full max-w-6xl mx-auto px-4 py-8 flex flex-col items-center">
      {/* HUD Header for Center Chamber */}
      <div className="w-full flex flex-wrap items-center justify-between gap-4 mb-6 border-b border-cyan-500/30 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping" />
          <span className="font-cyber text-sm tracking-widest text-cyan-300 font-bold uppercase">
            HOLO-CONTAINMENT CHAMBER // SECTOR-07
          </span>
          <span className="text-[10px] font-code px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-400 border border-cyan-500/40">
            SPECIMENS: 3 DETECTED
          </span>
        </div>

        {/* Pepe Music Toggle + Tab Filters (Matches Banana Phone Music Toggle UX) */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => setIsMusicOn((prev) => !prev)}
            data-gremlin-ignore="true"
            className={`px-3 py-1.5 text-xs font-code font-bold rounded-lg border flex items-center gap-1.5 cursor-pointer transition-all ${
              isMusicOn
                ? 'bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-400 shadow-[0_0_15px_rgba(255,0,127,0.45)]'
                : 'bg-slate-900/90 text-slate-400 border-slate-700 hover:border-fuchsia-400 hover:text-fuchsia-300'
            }`}
            title="Toggle Pepe Retro-Futuristic Synth Music ON or OFF"
          >
            {isMusicOn ? (
              <>
                <Volume2 className="w-4 h-4 text-fuchsia-400 animate-bounce" />
                <span>PEPE SYNTH MUSIC: ON (LOOPING)</span>
              </>
            ) : (
              <>
                <VolumeX className="w-4 h-4 text-slate-400" />
                <span>PEPE SYNTH MUSIC: OFF (CLICK TO PLAY)</span>
              </>
            )}
          </button>

          <div className="flex flex-wrap items-center gap-1 bg-slate-900/90 border border-slate-800 p-1 rounded-lg backdrop-blur-md">
            <button
              onClick={() => setActiveTab('all')}
              className={`px-3 py-1 text-xs font-code rounded transition-all cursor-pointer ${
                activeTab === 'all'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/60 shadow-[0_0_10px_rgba(0,240,255,0.4)]'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              [00] TRIPTYCH VIEW
            </button>
            <button
              onClick={() => setActiveTab('cry')}
              className={`px-3 py-1 text-xs font-code rounded transition-all cursor-pointer ${
                activeTab === 'cry'
                  ? 'bg-sky-500/20 text-sky-300 border border-sky-400/60 shadow-[0_0_10px_rgba(56,189,248,0.4)]'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              [01] SAD FROG
            </button>
            <button
              onClick={() => setActiveTab('laugh')}
              className={`px-3 py-1 text-xs font-code rounded transition-all cursor-pointer ${
                activeTab === 'laugh'
                  ? 'bg-fuchsia-500/20 text-fuchsia-300 border border-fuchsia-400/60 shadow-[0_0_10px_rgba(255,0,127,0.4)]'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              [02] MOCK LAUGH
            </button>
            <button
              onClick={() => setActiveTab('dance')}
              className={`px-3 py-1 text-xs font-code rounded transition-all cursor-pointer ${
                activeTab === 'dance'
                  ? 'bg-lime-500/20 text-lime-300 border border-lime-400/60 shadow-[0_0_10px_rgba(57,255,20,0.4)]'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              [03] PARTY RAVE
            </button>
          </div>
        </div>
      </div>

      {/* Main Holographic Projection Stage */}
      <div className="relative w-full min-h-[480px] md:min-h-[540px] flex items-center justify-center rounded-2xl border border-cyan-500/20 bg-gradient-to-b from-cyan-950/20 via-slate-950/60 to-[#04060b]/90 backdrop-blur-xl overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.8)]">
        
        {/* Sci-Fi Decorative Corner Brackets */}
        <div className="absolute top-3 left-3 w-6 h-6 border-t-2 border-l-2 border-cyan-400/80" />
        <div className="absolute top-3 right-3 w-6 h-6 border-t-2 border-r-2 border-cyan-400/80" />
        <div className="absolute bottom-3 left-3 w-6 h-6 border-b-2 border-l-2 border-cyan-400/80" />
        <div className="absolute bottom-3 right-3 w-6 h-6 border-b-2 border-r-2 border-cyan-400/80" />

        {/* Vertical Hologram Scanline Projector Beam */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <div className="absolute -inset-x-0 h-24 bg-gradient-to-b from-transparent via-cyan-400/15 to-transparent animate-holo-scan" />
          <div className="absolute inset-0 scanlines opacity-40" />
        </div>

        {/* 3D PERSPECTIVE NEON PEDESTAL (Bottom Floor) */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 w-80 md:w-[620px] h-40 pointer-events-none flex items-center justify-center [perspective:800px]">
          <div className="relative w-full h-full [transform:rotateX(72deg)] flex items-center justify-center">
            <div className="absolute w-[360px] md:w-[580px] h-[360px] md:h-[580px] rounded-full border border-cyan-500/30 animate-spin-slow shadow-[0_0_30px_rgba(0,240,255,0.2)]" />
            <div className="absolute w-[280px] md:w-[440px] h-[280px] md:h-[440px] rounded-full border border-dashed border-fuchsia-500/40 animate-spin-reverse-slow" />
            <div className="absolute w-[180px] md:w-[280px] h-[180px] md:h-[280px] rounded-full border-2 border-lime-400/50 bg-gradient-to-tr from-cyan-500/20 via-fuchsia-500/20 to-lime-500/20 shadow-[0_0_40px_rgba(57,255,20,0.4)]" />
          </div>
        </div>

        {/* Vertical Light Columns Rising from Pedestal */}
        <div className="absolute bottom-16 left-1/2 -translate-x-1/2 w-72 md:w-[540px] h-80 bg-gradient-to-t from-cyan-500/10 via-fuchsia-500/5 to-transparent pointer-events-none blur-xl" />

        {/* SPECIMEN DISPLAY LAYER */}
        <div className="relative z-10 w-full px-4 py-8 flex items-center justify-center">
          {activeTab === 'all' && (
            <div className="grid grid-cols-1 md:grid-cols-3 items-end justify-items-center gap-8 md:gap-4 w-full max-w-4xl">
              <div className="flex flex-col items-center w-full max-w-[240px]">
                <div className="text-[11px] font-code text-cyan-400 mb-2 flex items-center gap-1.5 opacity-80">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                  EMOTION: S_MAX_DESPAIR
                </div>
                <CryingPepe className="w-48 md:w-56" />
                <p className="mt-2 text-xs font-tech text-slate-400 text-center tracking-wide">
                  FeelsBadMan // Tears of 1v5 Clutch Loss
                </p>
              </div>

              <div className="flex flex-col items-center w-full max-w-[260px] -mt-4 md:-mt-8">
                <div className="text-[11px] font-code text-fuchsia-400 mb-2 flex items-center gap-1.5 opacity-90">
                  <span className="w-1.5 h-1.5 rounded-full bg-fuchsia-400 animate-ping" />
                  STATUS: LAUGH_POINT_ACTIVE
                </div>
                <LaughingPepe className="w-52 md:w-64" />
                <p className="mt-2 text-xs font-tech text-fuchsia-300 text-center tracking-wide">
                  PepeLaugh // Pointing at the whiffs
                </p>
              </div>

              <div className="flex flex-col items-center w-full max-w-[250px]">
                <div className="text-[11px] font-code text-lime-400 mb-2 flex items-center gap-1.5 opacity-90">
                  <span className="w-1.5 h-1.5 rounded-full bg-lime-400 animate-bounce" />
                  GROOVE: 128_BPM_SYNC
                </div>
                <DancingPepe className="w-48 md:w-56" />
                <p className="mt-2 text-xs font-tech text-lime-300 text-center tracking-wide">
                  PepePls // Vibing with RGB Visor
                </p>
              </div>
            </div>
          )}

          {activeTab === 'cry' && (
            <div className="flex flex-col md:flex-row items-center justify-center gap-8 max-w-2xl text-left">
              <div className="w-56 md:w-64">
                <CryingPepe isInspected={true} />
              </div>
              <div className="space-y-3 bg-slate-900/80 border border-sky-500/40 p-5 rounded-xl backdrop-blur-md">
                <div className="flex items-center justify-between">
                  <span className="font-cyber text-sky-400 text-sm font-bold">CRYING_PEPE // #001</span>
                  <span className="text-[10px] font-code bg-sky-950 text-sky-300 px-2 py-0.5 rounded border border-sky-600">CLASS: SAD</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed font-tech">
                  The quintessential embodiment of existential gaming sorrow. Experienced when whiffing a point-blank Zeus or losing 14-16 on overtime.
                </p>
                <div className="grid grid-cols-2 gap-2 text-[11px] font-code text-slate-400 border-t border-slate-800 pt-2">
                  <div>MOOD: <span className="text-cyan-300">Depressed</span></div>
                  <div>TEAR FLOW: <span className="text-cyan-300">8.4 L/hr</span></div>
                  <div>DEFENSE: <span className="text-cyan-300">Zero</span></div>
                  <div>HEART: <span className="text-cyan-300">PepeHands</span></div>
                </div>
                <p className="text-[11px] text-cyan-400 italic">💡 Tip: Click on Sad Pepe directly to comfort him!</p>
              </div>
            </div>
          )}

          {activeTab === 'laugh' && (
            <div className="flex flex-col md:flex-row items-center justify-center gap-8 max-w-2xl text-left">
              <div className="w-56 md:w-64">
                <LaughingPepe isInspected={true} />
              </div>
              <div className="space-y-3 bg-slate-900/80 border border-fuchsia-500/40 p-5 rounded-xl backdrop-blur-md">
                <div className="flex items-center justify-between">
                  <span className="font-cyber text-fuchsia-400 text-sm font-bold">LAUGHING_PEPE // #002</span>
                  <span className="text-[10px] font-code bg-fuchsia-950 text-fuchsia-300 px-2 py-0.5 rounded border border-fuchsia-600">CLASS: MOCKERY</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed font-tech">
                  He lacks critical information. Points directly at misfortune with unyielding vocal cords and an infectious giggle that dismantles egos across Twitch chat.
                </p>
                <div className="grid grid-cols-2 gap-2 text-[11px] font-code text-slate-400 border-t border-slate-800 pt-2">
                  <div>VOLUME: <span className="text-fuchsia-300">114 dB</span></div>
                  <div>MOCKERY: <span className="text-fuchsia-300">Unfiltered</span></div>
                  <div>TARGET: <span className="text-fuchsia-300">Sad Frog</span></div>
                  <div>MEME: <span className="text-fuchsia-300">KEKW / PepeLaugh</span></div>
                </div>
                <p className="text-[11px] text-fuchsia-400 italic">💡 Tip: Click on Laughing Pepe to spawn meme popups!</p>
              </div>
            </div>
          )}

          {activeTab === 'dance' && (
            <div className="flex flex-col md:flex-row items-center justify-center gap-8 max-w-2xl text-left">
              <div className="w-56 md:w-64">
                <DancingPepe isInspected={true} />
              </div>
              <div className="space-y-3 bg-slate-900/80 border border-lime-500/40 p-5 rounded-xl backdrop-blur-md">
                <div className="flex items-center justify-between">
                  <span className="font-cyber text-lime-400 text-sm font-bold">DANCING_PEPE // #003</span>
                  <span className="text-[10px] font-code bg-lime-950 text-lime-300 px-2 py-0.5 rounded border border-lime-600">CLASS: PARTY_RAVER</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed font-tech">
                  Equipped with dual RGB glowsticks and a high-spec neon wrap-around visor. Absorbs bass frequencies and converts them into perpetual dance energy.
                </p>
                <div className="grid grid-cols-2 gap-2 text-[11px] font-code text-slate-400 border-t border-slate-800 pt-2">
                  <div>TEMPO: <span className="text-lime-300">128 - 145 BPM</span></div>
                  <div>LIGHTING: <span className="text-lime-300">Cyber Visor</span></div>
                  <div>VIBE: <span className="text-lime-300">Immortal</span></div>
                  <div>STYLE: <span className="text-lime-300">PepePls Rave</span></div>
                </div>
                <p className="text-[11px] text-lime-400 italic">💡 Tip: Click Dancing Pepe to shoot cyber confetti bursts!</p>
              </div>
            </div>
          )}
        </div>

        {/* Bottom Stage Telemetry Bar */}
        <div className="absolute bottom-2 inset-x-4 flex items-center justify-between text-[10px] font-code text-slate-500 border-t border-slate-800/80 pt-2">
          <div className="flex items-center gap-3">
            <span className="text-cyan-400 flex items-center gap-1">
              <Activity className="w-3 h-3" /> STABILITY: 99.8%
            </span>
            <span className="hidden sm:inline text-slate-400">
              FIELD FREQ: 432.09 GHz
            </span>
          </div>
          <div className="flex items-center gap-2 text-slate-400">
            <span>INTERACTIVE: HOVER &amp; CLICK SPECIMENS</span>
          </div>
        </div>

      </div>
    </section>
  );
};
