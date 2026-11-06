import React, { useState, useEffect } from 'react';
import { Volume2, VolumeX, Radio, Shield, Wifi, Mail } from 'lucide-react';
import { cyberSynth } from '../utils/synthAudio';

export const CyberNavbar: React.FC = () => {
  const [isPlayingSound, setIsPlayingSound] = useState(false);
  const [timeStr, setTimeStr] = useState('');
  const [ping, setPing] = useState(14);

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(
        now.toLocaleTimeString('en-US', {
          hour12: false,
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        })
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);

    // Subtle ping fluctuation
    const pingInterval = setInterval(() => {
      setPing(Math.floor(12 + Math.random() * 8));
    }, 4000);

    return () => {
      clearInterval(interval);
      clearInterval(pingInterval);
    };
  }, []);

  const toggleSound = () => {
    const state = cyberSynth.toggle();
    setIsPlayingSound(state);
  };

  return (
    <header className="sticky top-0 z-50 w-full backdrop-blur-xl bg-[#060810]/85 border-b border-cyan-500/20 px-4 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Brand & Terminal Identifier */}
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-9 h-9 rounded-lg bg-cyan-950/60 border border-cyan-400 shadow-[0_0_15px_rgba(0,240,255,0.4)]">
            <span className="font-cyber font-black text-cyan-300 text-lg">G</span>
            <div className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-lime-400 animate-ping" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-cyber font-black tracking-wider text-white text-base md:text-lg">
                GERONIMO<span className="text-cyan-400">HQ</span>
              </span>
              <span className="hidden sm:inline-block px-1.5 py-0.2 text-[9px] font-code bg-emerald-950/90 text-emerald-300 border border-emerald-500/50 rounded">
                ONLINE
              </span>
            </div>
            <div className="text-[10px] font-code text-cyan-400/80 tracking-widest uppercase">
              geronimohq.com // sys.core
            </div>
          </div>
        </div>

        {/* Center Nav Anchors */}
        <nav className="hidden lg:flex items-center gap-6 text-xs font-cyber tracking-wider text-slate-300">
          <a
            href="#hero-stage"
            className="hover:text-cyan-400 transition-colors flex items-center gap-1.5"
          >
            <Radio className="w-3.5 h-3.5 text-cyan-400" />
            HOLO-DECK
          </a>
          <a
            href="#cs2-command"
            className="hover:text-fuchsia-400 transition-colors flex items-center gap-1.5"
          >
            <Shield className="w-3.5 h-3.5 text-fuchsia-400" />
            CS2 COMMAND
          </a>
          <a
            href="#server-radar"
            className="hover:text-lime-400 transition-colors flex items-center gap-1.5"
          >
            <Wifi className="w-3.5 h-3.5 text-lime-400" />
            ZE RADAR
          </a>
          <a
            href="#contact"
            className="hover:text-cyan-400 transition-colors flex items-center gap-1.5"
          >
            <Mail className="w-3.5 h-3.5 text-cyan-400" />
            TRANSMISSION
          </a>
        </nav>

        {/* Right HUD Controls: Synth Music Toggle + Clock & Ping */}
        <div className="flex items-center gap-3">
          {/* Synth Soundtrack Toggle */}
          <button
            onClick={toggleSound}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-code transition-all cursor-pointer ${
              isPlayingSound
                ? 'bg-fuchsia-950/80 border-fuchsia-400 text-fuchsia-300 shadow-[0_0_15px_rgba(255,0,127,0.5)] animate-pulse'
                : 'bg-slate-900/80 border-slate-700 text-slate-300 hover:border-cyan-500 hover:text-cyan-300'
            }`}
            title="Toggle Web Audio 80s Synthwave Soundtrack"
          >
            {isPlayingSound ? (
              <>
                <Volume2 className="w-3.5 h-3.5 text-fuchsia-400 animate-spin-slow" />
                <span className="hidden sm:inline">SYNTH: ON</span>
              </>
            ) : (
              <>
                <VolumeX className="w-3.5 h-3.5 text-slate-400" />
                <span className="hidden sm:inline">SYNTH: OFF</span>
              </>
            )}
          </button>

          {/* Real-time Clock & Ping */}
          <div className="hidden sm:flex flex-col items-end text-[10px] font-code text-slate-400 bg-slate-950/60 px-2.5 py-1 rounded border border-slate-800">
            <span className="text-cyan-300 font-bold">{timeStr || '18:00:00'}</span>
            <span className="text-emerald-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block" />
              {ping}ms
            </span>
          </div>
        </div>

      </div>
    </header>
  );
};
