import React, { useState, useEffect } from 'react';
import { 
  Radio, 
  Cpu, 
  Wifi, 
  Wrench, 
  Sliders, 
  Shield, 
  Mail, 
  Sparkles 
} from 'lucide-react';

interface CyberNavbarProps {
  theme: 'pepe' | 'banana';
  gremlinEnabled: boolean;
  onToggleGremlin: () => void;
}

export const scrollToSectionById = (id: string) => {
  const el = document.getElementById(id);
  if (!el) return;
  const navHeight = 76;
  const elementPosition = el.getBoundingClientRect().top + window.pageYOffset;
  const offsetPosition = Math.max(0, elementPosition - navHeight);
  window.scrollTo({
    top: offsetPosition,
    behavior: 'smooth'
  });
};

export const CyberNavbar: React.FC<CyberNavbarProps> = ({
  theme,
  gremlinEnabled,
  onToggleGremlin,
}) => {
  const [timeStr, setTimeStr] = useState<string>('');
  const [ping, setPing] = useState<number>(12);

  // Digital Cyber Clock & Low-Latency Network Ping Simulation
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(
        now.toTimeString().split(' ')[0]
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const pingInterval = setInterval(() => {
      setPing(Math.floor(10 + Math.random() * 8));
    }, 4000);
    return () => clearInterval(pingInterval);
  }, []);

  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, targetId: string) => {
    e.preventDefault();
    scrollToSectionById(targetId);
  };

  return (
    <header
      className={`sticky top-0 z-50 w-full backdrop-blur-xl transition-colors duration-700 px-4 py-2.5 border-b ${
        theme === 'banana'
          ? 'bg-[#0c0902]/90 border-yellow-500/35'
          : 'bg-[#060810]/85 border-cyan-500/20'
      }`}
    >
      <div className="max-w-6xl mx-auto flex items-center justify-between gap-4">
        
        {/* Brand & Terminal Identifier (Left Edge of max-w-6xl) */}
        <a
          href="#hero-stage"
          onClick={(e) => handleNavClick(e, 'hero-stage')}
          className="flex items-center gap-2.5 group flex-shrink-0"
        >
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
        </a>

        {/* Center Nav Anchors (Centered & Balanced across max-w-6xl) */}
        <nav className="hidden lg:flex items-center justify-center gap-2 xl:gap-3 text-[11px] xl:text-xs font-cyber tracking-wider text-slate-300 flex-1 px-2">
          <a
            href="#hero-stage"
            onClick={(e) => handleNavClick(e, 'hero-stage')}
            className="hover:text-cyan-400 transition-colors flex items-center gap-1.5 flex-shrink-0"
          >
            <Radio className="w-3.5 h-3.5 text-cyan-400" />
            <span>HOLO-DECK</span>
          </a>
          <a
            href="#download-ram"
            onClick={(e) => handleNavClick(e, 'download-ram')}
            className="px-2 py-0.5 rounded-lg bg-lime-950/80 border border-lime-400/60 text-lime-300 hover:bg-lime-900/80 shadow-[0_0_12px_rgba(57,255,20,0.3)] transition-all flex items-center gap-1 font-bold flex-shrink-0"
          >
            <Cpu className="w-3 h-3 text-lime-400 animate-pulse" />
            <span>DOWNLOAD RAM</span>
          </a>
          <a
            href="#server-radar"
            onClick={(e) => handleNavClick(e, 'server-radar')}
            className="hover:text-lime-400 transition-colors flex items-center gap-1.5 flex-shrink-0"
          >
            <Wifi className="w-3.5 h-3.5 text-lime-400" />
            <span>ZE SERVERS</span>
          </a>
          <a
            href="#ze-toolkit"
            onClick={(e) => handleNavClick(e, 'ze-toolkit')}
            className="hover:text-emerald-400 transition-colors flex items-center gap-1.5 flex-shrink-0"
          >
            <Wrench className="w-3.5 h-3.5 text-emerald-400" />
            <span>ZE TOOLKIT</span>
          </a>
          <a
            href="#cfg-studio"
            onClick={(e) => handleNavClick(e, 'cfg-studio')}
            className="hover:text-cyan-400 transition-colors flex items-center gap-1.5 flex-shrink-0"
          >
            <Sliders className="w-3.5 h-3.5 text-cyan-400" />
            <span>CFG STUDIO</span>
          </a>
          <a
            href="#cs2-command"
            onClick={(e) => handleNavClick(e, 'cs2-command')}
            className="hover:text-fuchsia-400 transition-colors flex items-center gap-1.5 flex-shrink-0"
          >
            <Shield className="w-3.5 h-3.5 text-fuchsia-400" />
            <span>CS2 APP</span>
          </a>
          <a
            href="#contact"
            onClick={(e) => handleNavClick(e, 'contact')}
            className="hover:text-cyan-400 transition-colors flex items-center gap-1.5 flex-shrink-0"
          >
            <Mail className="w-3.5 h-3.5 text-cyan-400" />
            <span>TRANSMISSION</span>
          </a>
        </nav>

        {/* Right HUD Controls: Theme Status Badge + Gremlin Toggle + Clock (Right Edge of max-w-6xl) */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {/* Mobile/Tablet Download RAM Button */}
          <a
            href="#download-ram"
            onClick={(e) => handleNavClick(e, 'download-ram')}
            className="lg:hidden flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-lime-950/80 border border-lime-400/60 text-lime-300 text-xs font-code font-bold"
          >
            <Cpu className="w-3.5 h-3.5 text-lime-400" />
            <span>RAM</span>
          </a>

          {/* Read-Only Active Theme Indicator Badge */}
          <div
            data-gremlin-ignore="true"
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-xs font-code font-bold select-none cursor-default ${
              theme === 'banana'
                ? 'bg-amber-950/90 border-yellow-400/80 text-yellow-300 shadow-[0_0_12px_rgba(250,204,21,0.35)]'
                : 'bg-cyan-950/75 border-cyan-400/60 text-cyan-300'
            }`}
            title="Current Active Theme (Read-Only Indicator)"
          >
            <span className="hidden sm:inline">{theme === 'banana' ? '🍌 THEME: BANANA PHONE' : '🐸 THEME: PEPE HOLO'}</span>
            <span className="sm:hidden">{theme === 'banana' ? '🍌 BANANA' : '🐸 PEPE'}</span>
          </div>

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
