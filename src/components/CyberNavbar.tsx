import React, { useState, useEffect } from 'react';
import { Volume2, VolumeX, Radio, Shield, Wifi, Mail, Cpu, Sparkles } from 'lucide-react';
import { cyberSynth } from '../utils/synthAudio';

interface CyberNavbarProps {
  theme: 'pepe' | 'banana';
  onToggleTheme: () => void;
  autoSwitchRemainingSec: number | null;
  gremlinEnabled: boolean;
  onToggleGremlin: () => void;
}

export const CyberNavbar: React.FC<CyberNavbarProps> = ({
  theme,
  onToggleTheme,
  autoSwitchRemainingSec,
  gremlinEnabled,
  onToggleGremlin,
}) => {
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

    const pingInterval = setInterval(() => {
      setPing(Math.floor(12 + Math.random() * 8));
    }, 4000);

    return () => {
      clearInterval(interval);
      clearInterval(pingInterval);
    };
  }, []);

  const toggleSound = () => {
    cyberSynth.setMode(theme);
    const state = cyberSynth.toggle();
    setIsPlayingSound(state);
  };

  const formatCountdown = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  return (
    <header
      className={`sticky top-0 z-50 w-full backdrop-blur-xl transition-colors duration-700 px-4 py-3 border-b ${
        theme === 'banana'
          ? 'bg-[#0c0902]/90 border-yellow-500/35'
          : 'bg-[#060810]/85 border-cyan-500/20'
      }`}
    >
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
        
        {/* Brand & Terminal Identifier */}
        <div className="flex items-center gap-3">
          <div
            className={`relative flex items-center justify-center w-9 h-9 rounded-lg border transition-all duration-700 ${
              theme === 'banana'
                ? 'bg-amber-950/70 border-yellow-400 shadow-[0_0_15px_rgba(250,204,21,0.5)]'
                : 'bg-cyan-950/60 border-cyan-400 shadow-[0_0_15px_rgba(0,240,255,0.4)]'
            }`}
          >
            <span
              className={`font-cyber font-black text-lg ${
                theme === 'banana' ? 'text-yellow-300' : 'text-cyan-300'
              }`}
            >
              {theme === 'banana' ? '🍌' : 'G'}
            </span>
            <div className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-lime-400 animate-ping" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-cyber font-black tracking-wider text-white text-base md:text-lg">
                GERONIMO
                <span className={theme === 'banana' ? 'text-yellow-400' : 'text-cyan-400'}>
                  HQ
                </span>
              </span>
              <span className="hidden sm:inline-block px-1.5 py-0.2 text-[9px] font-code bg-emerald-950/90 text-emerald-300 border border-emerald-500/50 rounded">
                ONLINE
              </span>
            </div>
            <div
              className={`text-[10px] font-code tracking-widest uppercase ${
                theme === 'banana' ? 'text-yellow-400/80' : 'text-cyan-400/80'
              }`}
            >
              {theme === 'banana' ? 'geronimohq.com // banana.phone' : 'geronimohq.com // sys.core'}
            </div>
          </div>
        </div>

        {/* Center Nav Anchors (Including DOWNLOAD RAM where Geronimo underlined!) */}
        <nav className="hidden xl:flex items-center gap-5 text-xs font-cyber tracking-wider text-slate-300">
          <a
            href="#hero-stage"
            className="hover:text-cyan-400 transition-colors flex items-center gap-1.5"
          >
            <Radio className="w-3.5 h-3.5 text-cyan-400" />
            HOLO-DECK
          </a>
          <a
            href="#download-ram"
            className="px-2.5 py-1 rounded-lg bg-lime-950/80 border border-lime-400/60 text-lime-300 hover:bg-lime-900/80 shadow-[0_0_12px_rgba(57,255,20,0.3)] transition-all flex items-center gap-1.5 font-bold"
          >
            <Cpu className="w-3.5 h-3.5 text-lime-400 animate-pulse" />
            DOWNLOAD RAM
          </a>
          <a
            href="#server-radar"
            className="hover:text-lime-400 transition-colors flex items-center gap-1.5"
          >
            <Wifi className="w-3.5 h-3.5 text-lime-400" />
            ZE SERVERS
          </a>
          <a
            href="#cs2-command"
            className="hover:text-fuchsia-400 transition-colors flex items-center gap-1.5"
          >
            <Shield className="w-3.5 h-3.5 text-fuchsia-400" />
            CS2 APP
          </a>
          <a
            href="#contact"
            className="hover:text-cyan-400 transition-colors flex items-center gap-1.5"
          >
            <Mail className="w-3.5 h-3.5 text-cyan-400" />
            TRANSMISSION
          </a>
        </nav>

        {/* Right HUD Controls: Download RAM quick-jump (mobile/tablet) + Theme Switcher + Gremlin Toggle + Synth + Clock */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Mobile/Tablet Download RAM Button */}
          <a
            href="#download-ram"
            className="xl:hidden flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-lime-950/80 border border-lime-400/60 text-lime-300 text-xs font-code font-bold"
          >
            <Cpu className="w-3.5 h-3.5 text-lime-400" />
            <span>RAM</span>
          </a>

          {/* Manual Theme Switcher (Pepe Retro-Futuristic <-> Banana Phone) */}
          <button
            onClick={onToggleTheme}
            data-gremlin-ignore="true"
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-code font-bold transition-all cursor-pointer ${
              theme === 'banana'
                ? 'bg-amber-950/90 border-yellow-400 text-yellow-300 shadow-[0_0_15px_rgba(250,204,21,0.5)]'
                : 'bg-cyan-950/80 border-cyan-400/70 text-cyan-300 hover:border-yellow-400 hover:text-yellow-300'
            }`}
            title="Switch between Pepe Retro-Futuristic Theme and Banana Phone Theme (Auto-switches after 2 minutes!)"
          >
            <span>{theme === 'banana' ? '🍌 THEME: BANANA PHONE' : '🐸 THEME: PEPE HOLO'}</span>
            {theme === 'pepe' && autoSwitchRemainingSec !== null && autoSwitchRemainingSec > 0 && (
              <span className="text-[10px] text-yellow-300 bg-slate-950/80 px-1.5 py-0.5 rounded border border-yellow-500/40">
                🍌 in {formatCountdown(autoSwitchRemainingSec)}
              </span>
            )}
          </button>

          {/* Roaming Character Toggle */}
          <button
            onClick={onToggleGremlin}
            data-gremlin-ignore="true"
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-xs font-code transition-all cursor-pointer ${
              gremlinEnabled
                ? 'bg-emerald-950/80 border-emerald-400/70 text-emerald-300'
                : 'bg-slate-900/80 border-slate-700 text-slate-400'
            }`}
            title="Toggle the roaming interactive Pepe / Banana character"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span className="hidden md:inline">{gremlinEnabled ? 'ROAMER: ON' : 'ROAMER: OFF'}</span>
          </button>

          {/* Synth Soundtrack Toggle */}
          <button
            onClick={toggleSound}
            data-gremlin-ignore="true"
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-xs font-code transition-all cursor-pointer ${
              isPlayingSound
                ? 'bg-fuchsia-950/80 border-fuchsia-400 text-fuchsia-300 shadow-[0_0_15px_rgba(255,0,127,0.5)] animate-pulse'
                : 'bg-slate-900/80 border-slate-700 text-slate-300 hover:border-cyan-500 hover:text-cyan-300'
            }`}
            title="Toggle Web Audio Synth / Banana Phone Melody"
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
            <span className={theme === 'banana' ? 'text-yellow-300 font-bold' : 'text-cyan-300 font-bold'}>
              {timeStr || '18:00:00'}
            </span>
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
