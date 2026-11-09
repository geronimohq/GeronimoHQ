import React, { useState, useEffect } from 'react';
import { 
  Radio, 
  Cpu, 
  Wifi, 
  Wrench, 
  Sliders, 
  Shield, 
  Mail, 
  Sparkles,
  PhoneCall,
  Activity,
  Menu,
  X
} from 'lucide-react';

interface CyberNavbarProps {
  theme: 'pepe' | 'banana';
  gremlinEnabled: boolean;
  onToggleGremlin: () => void;
}

export const scrollToSectionById = (id: string) => {
  const el = document.getElementById(id);
  if (!el) return;
  const navHeight = 104;
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
  const [activeSection, setActiveSection] = useState<string>('hero-stage');
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);

  // Digital Cyber Clock & Low-Latency Network Ping Simulation
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toTimeString().split(' ')[0]);
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

  // Real-Time Active Section Scroll Spy
  useEffect(() => {
    const sectionIds = ['hero-stage', 'download-ram', 'server-radar', 'ze-toolkit', 'cfg-studio', 'cs2-command', 'contact'];
    const handleScroll = () => {
      const scrollPos = window.scrollY + 140;
      for (let i = sectionIds.length - 1; i >= 0; i--) {
        const id = sectionIds[i];
        const el = document.getElementById(id);
        if (el) {
          const top = el.offsetTop;
          if (scrollPos >= top) {
            setActiveSection(id);
            break;
          }
        }
      }
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, targetId: string) => {
    e.preventDefault();
    setActiveSection(targetId);
    setMobileMenuOpen(false);
    scrollToSectionById(targetId);
    if (window.history?.pushState) {
      window.history.pushState(null, '', `#${targetId}`);
    }
  };

  const navItems = [
    { id: 'hero-stage', label: 'HOLO-DECK', icon: Radio },
    { id: 'download-ram', label: 'DOWNLOAD RAM', icon: Cpu },
    { id: 'server-radar', label: 'ZE SERVERS', icon: Wifi },
    { id: 'ze-toolkit', label: 'ZE TOOLKIT', icon: Wrench },
    { id: 'cfg-studio', label: 'CFG STUDIO', icon: Sliders },
    { id: 'cs2-command', label: 'CS2 APP', icon: Shield },
    { id: 'contact', label: 'TRANSMISSION', icon: Mail },
  ];

  return (
    <header className="sticky top-0 z-50 w-full bg-[#070B09]/95 backdrop-blur-xl border-b border-[#1E2E26] py-2.5 transition-colors duration-500">
      <div className="w-full max-w-6xl mx-auto px-4 flex flex-col gap-2">
        
        {/* TIER 1: UNIFIED TOP COMMAND BAR & FLOATING PILL DOCK */}
        <div className="flex items-center justify-between gap-3">
          
          {/* Brand Terminal Identity */}
          <a
            href="#hero-stage"
            onClick={(e) => handleNavClick(e, 'hero-stage')}
            className="flex items-center gap-2.5 group flex-shrink-0"
          >
            <div className="relative flex items-center justify-center w-9 h-9 rounded-lg bg-[#0E1512] border border-[#FFE135]/70 shadow-[0_0_14px_rgba(255,225,53,0.25)] group-hover:border-[#FFE135] transition-all">
              {/* Subtle Vector Motif: Tactical Pepe / Rotary Banana Badge */}
              <span className="font-cyber font-black text-base text-[#FFE135]">
                {theme === 'banana' ? '🍌' : '🐸'}
              </span>
              <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-[#2ECC71] border border-[#070B09] animate-pulse" />
            </div>

            <div>
              <div className="flex items-center gap-2">
                <span className="font-cyber font-bold tracking-wider text-white text-[16px]">
                  GERONIMO<span className="text-[#FFE135]">HQ</span>
                </span>
                <span className="hidden sm:inline-flex tier-5-badge bg-[#2ECC71]/15 text-[#2ECC71] border border-[#2ECC71]/50">
                  ● ONLINE
                </span>
              </div>
              <div className="text-[10px] font-code tracking-widest uppercase text-[#94A39E] flex items-center gap-1">
                <span>CYBER-DECK OS</span>
                <span className="text-[#FFE135]">//</span>
                <span className="text-[#2ECC71]">{theme === 'banana' ? 'ROTARY.HOTLINE' : 'PEPE.MATRIX'}</span>
              </div>
            </div>
          </a>

          {/* Floating Command Pill Dock (Desktop) */}
          <nav
            aria-label="Primary Command Dock"
            className="hidden lg:flex items-center gap-1.5 p-1 rounded-xl bg-[#0E1512] border border-[#1E2E26] shadow-inner flex-shrink-0"
          >
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeSection === item.id;
              return (
                <a
                  key={item.id}
                  href={`#${item.id}`}
                  onClick={(e) => handleNavClick(e, item.id)}
                  className={`h-[30px] px-2.5 rounded-lg text-[11px] font-cyber tracking-wider transition-all flex items-center gap-1.5 flex-shrink-0 ${
                    isActive
                      ? 'bg-[#FFE135] text-[#070B09] font-bold shadow-[0_0_14px_rgba(255,225,53,0.45)]'
                      : 'text-[#94A39E] hover:text-white hover:bg-[#14201B]'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-[#070B09]' : 'text-[#2ECC71]'}`} />
                  <span>{item.label}</span>
                </a>
              );
            })}
          </nav>

          {/* Mobile Actions: Quick RAM Pill & Accessible Menu Toggle */}
          <div className="lg:hidden flex items-center gap-2">
            <a
              href="#download-ram"
              onClick={(e) => handleNavClick(e, 'download-ram')}
              className="btn-cyber-34 btn-banana-cta"
            >
              <Cpu className="w-3.5 h-3.5" />
              <span>RAM</span>
            </a>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label={mobileMenuOpen ? 'Close Navigation Menu' : 'Open Navigation Menu'}
              aria-expanded={mobileMenuOpen}
              className="min-h-[34px] min-w-[34px] p-2 rounded-lg bg-[#0E1512] border border-[#1E2E26] text-[#FFE135] hover:border-[#FFE135] flex items-center justify-center transition-colors cursor-pointer"
            >
              {mobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Drawer (Keyboard Operable & Accessible 44px Touch Targets) */}
        {mobileMenuOpen && (
          <nav
            aria-label="Mobile Command Menu"
            className="lg:hidden flex flex-col gap-1.5 p-2 rounded-xl bg-[#0E1512] border border-[#1E2E26] shadow-2xl"
          >
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeSection === item.id;
              return (
                <a
                  key={item.id}
                  href={`#${item.id}`}
                  onClick={(e) => handleNavClick(e, item.id)}
                  className={`min-h-[44px] px-3 rounded-lg text-xs font-cyber tracking-wider flex items-center gap-2.5 transition-all ${
                    isActive
                      ? 'bg-[#FFE135] text-[#070B09] font-bold shadow-[0_0_12px_rgba(255,225,53,0.4)]'
                      : 'text-[#94A39E] hover:text-white hover:bg-[#121C18]'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-[#070B09]' : 'text-[#2ECC71]'}`} />
                  <span>{item.label}</span>
                </a>
              );
            })}
          </nav>
        )}

        {/* TIER 2: UNIFIED HARDWARE & TELEMETRY HUD STRIP (Equal-Sized Monospace Data Pills) */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-0.5">
          {/* Pill 1: Active Theme Signal */}
          <div
            data-gremlin-ignore="true"
            className="hud-data-pill justify-between border-[#FFE135]/40 text-[#FFE135]"
            title="Active Cyber-Deck Theme Signal (Read-Only Indicator)"
          >
            <span className="flex items-center gap-1.5 truncate">
              <PhoneCall className="w-3.5 h-3.5 text-[#FFE135] flex-shrink-0" />
              <span className="font-bold truncate">
                {theme === 'banana' ? 'MODE: BANANA PHONE' : 'MODE: PEPE HOLO'}
              </span>
            </span>
            <span className="w-2 h-2 rounded-full bg-[#FFE135] animate-ping flex-shrink-0" />
          </div>

          {/* Pill 2: Interactive Roaming Agent Toggle */}
          <button
            onClick={onToggleGremlin}
            data-gremlin-ignore="true"
            className={`hud-data-pill justify-between cursor-pointer transition-all ${
              gremlinEnabled
                ? 'border-[#2ECC71]/60 text-[#2ECC71] bg-[#0E1512] hover:bg-[#13201A]'
                : 'border-[#1E2E26] text-[#94A39E] bg-[#0E1512] hover:text-white'
            }`}
            title="Toggle the roaming interactive Pepe / Banana character"
          >
            <span className="flex items-center gap-1.5 truncate">
              <Sparkles className="w-3.5 h-3.5 flex-shrink-0" />
              <span className="font-bold truncate">
                {gremlinEnabled ? 'ROAMER: ACTIVE' : 'ROAMER: STANDBY'}
              </span>
            </span>
            <span className={`text-[10px] px-1.5 py-0.2 rounded font-bold ${gremlinEnabled ? 'bg-[#2ECC71]/20 text-[#2ECC71]' : 'bg-black/40 text-[#94A39E]'}`}>
              {gremlinEnabled ? 'ON' : 'OFF'}
            </span>
          </button>

          {/* Pill 3: Live ZE Cluster Status (Per Spec: Web shows presence state and server status only) */}
          <div className="hidden sm:flex hud-data-pill justify-between text-[#94A39E]" title="Global Zombie Escape Server Clusters Online">
            <span className="flex items-center gap-1.5 truncate">
              <Wifi className="w-3.5 h-3.5 text-[#00F0FF] flex-shrink-0" />
              <span className="truncate">SERVERS: <strong className="text-white">6 CLUSTERS</strong></span>
            </span>
            <span className="text-[#2ECC71] font-bold">ONLINE</span>
          </div>

          {/* Pill 4: Real-Time Clock & Low-Latency Uplink */}
          <div className="hidden sm:flex hud-data-pill justify-between text-[#94A39E]">
            <span className="flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-[#2ECC71] flex-shrink-0" />
              <strong className="text-[#FFE135]">{timeStr || '18:00:00'}</strong>
            </span>
            <span className="text-[#2ECC71] flex items-center gap-1 font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-[#2ECC71] inline-block animate-pulse" />
              {ping}ms
            </span>
          </div>
        </div>

      </div>
    </header>
  );
};
