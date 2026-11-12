import React, { useState, useEffect, useRef } from 'react';
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
  Smile,
  Newspaper,
  Menu,
  X
} from 'lucide-react';

interface CyberNavbarProps {
  theme: 'pepe' | 'banana';
}

export const scrollToSectionById = (id: string) => {
  const targetTop = () => {
    const el = document.getElementById(id);
    if (!el) return null;
    const navEl = document.querySelector('header');
    const navHeight = navEl ? navEl.offsetHeight : 104;
    // Holo-deck and Transmission keep original spacing per user spec; other modules land snug (8px) below navbar
    const targetGap = (id === 'hero-stage' || id === 'contact') ? 16 : 8;
    return Math.max(0, el.getBoundingClientRect().top + window.pageYOffset - navHeight - targetGap);
  };
  const first = targetTop();
  if (first === null) return;
  window.scrollTo({ top: first, behavior: 'smooth' });

  // Sections above the target can still change height while the page scrolls (thumbnails, live server data, the news feed),
  // which used to leave the visitor a little above or below the section. When the scroll ends, land exactly; never fight the
  // visitor if they start scrolling themselves.
  let done = false;
  const stop = () => {
    done = true;
    window.removeEventListener('wheel', stop);
    window.removeEventListener('touchstart', stop);
    window.removeEventListener('keydown', stop);
  };
  const settle = () => {
    if (done) return;
    stop();
    const t = targetTop();
    if (t !== null && Math.abs(window.pageYOffset - t) > 4) window.scrollTo({ top: t, behavior: 'auto' });
  };
  window.addEventListener('wheel', stop, { once: true, passive: true });
  window.addEventListener('touchstart', stop, { once: true, passive: true });
  window.addEventListener('keydown', stop, { once: true });
  if ('onscrollend' in window) window.addEventListener('scrollend', settle, { once: true });
  window.setTimeout(settle, 1200);
};

/** The roamer toggle and the vibes pill (they live in the hero card, beside the theme switch). */
export const RoamerPill: React.FC<{ theme: 'pepe' | 'banana'; enabled: boolean; onToggle: () => void }> = ({ theme, enabled, onToggle }) => {
  const isBanana = theme === 'banana';
  return (
    <button
      onClick={onToggle}
      data-gremlin-ignore="true"
      className={`hud-data-pill flex justify-between min-w-[170px] h-[34px] cursor-pointer transition-all ${
        enabled
          ? (isBanana ? 'border-[#FFE135]/60 text-[#FFE135] bg-[#0E1512] hover:bg-[#2A260E]' : 'border-[#2ECC71]/60 text-[#2ECC71] bg-[#0E1512] hover:bg-[#122A1E]')
          : 'border-[#1E2E26] text-[#94A39E] bg-[#0E1512] hover:text-white'
      }`}
      title="Toggle the roaming interactive Pepe / Banana character"
    >
      <span className="flex items-center gap-1.5 truncate">
        <Sparkles className="w-3.5 h-3.5 flex-shrink-0" />
        <span className="font-bold truncate">{enabled ? 'ROAMER: ACTIVE' : 'ROAMER: STANDBY'}</span>
      </span>
      <span className={`text-[10px] px-1.5 rounded font-bold ${enabled ? (isBanana ? 'bg-[#FFE135]/20 text-[#FFE135]' : 'bg-[#2ECC71]/20 text-[#2ECC71]') : 'bg-black/40 text-[#94A39E]'}`}>
        {enabled ? 'ON' : 'OFF'}
      </span>
    </button>
  );
};

/** Deliberately useless and not a number shown elsewhere on the page; text and colours follow the theme. */
export const VibesPill: React.FC<{ theme: 'pepe' | 'banana' }> = ({ theme }) => {
  const isBanana = theme === 'banana';
  return (
    <div className="hud-data-pill flex justify-between min-w-[170px] h-[34px] text-[#94A39E]" title="Completely scientific, completely useless">
      <span className="flex items-center gap-1.5 truncate">
        <Smile className={`w-3.5 h-3.5 flex-shrink-0 ${isBanana ? 'text-[#FFE135]' : 'text-[#2ECC71]'}`} />
        <span className="truncate">VIBES: <strong className="text-white">GOOD</strong></span>
      </span>
      <span className={`font-bold flex-shrink-0 ${isBanana ? 'text-[#FFE135]' : 'text-[#2ECC71]'}`}>{isBanana ? 'PEEL-OK' : 'RIBBIT'}</span>
    </div>
  );
};

// In page order (the scroll spy relies on it). The mobile menu lists all of them; on desktop the two in SECOND_ROW sit under the brand row.
const NAV_ITEMS = [
  { id: 'hero-stage', label: 'HOLO-DECK', icon: Radio },
  { id: 'download-ram', label: 'DOWNLOAD RAM', icon: Cpu },
  { id: 'server-radar', label: 'ZE SERVERS', icon: Wifi },
  { id: 'ze-toolkit', label: 'ZE TOOLKIT', icon: Wrench },
  { id: 'world-news', label: 'WORLD NEWS', icon: Newspaper },
  { id: 'cfg-studio', label: 'CFG STUDIO', icon: Sliders },
  { id: 'cs2-command', label: 'CS2 APP', icon: Shield },
  { id: 'contact', label: 'TRANSMISSION', icon: Mail },
];
const SECOND_ROW = ['download-ram', 'world-news'];

export const CyberNavbar: React.FC<CyberNavbarProps> = ({ theme }) => {
  const isBanana = theme === 'banana';
  const [timeStr, setTimeStr] = useState<string>('');
  const [activeSection, setActiveSection] = useState<string>('hero-stage');
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);

  useEffect(() => {
    const updateNavHeight = () => {
      const nav = document.querySelector('header');
      if (nav) {
        document.documentElement.style.setProperty('--nav-height', `${nav.offsetHeight}px`);
      }
    };
    updateNavHeight();
    window.addEventListener('resize', updateNavHeight);
    return () => window.removeEventListener('resize', updateNavHeight);
  }, []);

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

  // AUDIT P3-03: removed a random 10-18 ms "ping" that was shown like a live measurement.

  // AUDIT P5 (keyboard): Esc closes the mobile menu.
  useEffect(() => {
    if (!mobileMenuOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setMobileMenuOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [mobileMenuOpen]);

  const isManualScrollingRef = useRef<boolean>(false);
  const scrollTimeoutRef = useRef<number | null>(null);

  // Real-Time Active Section Scroll Spy
  useEffect(() => {
    const sectionIds = NAV_ITEMS.map((i) => i.id);          // page order; the spy checks from the bottom up
    
    const handleScroll = () => {
      // 1. If manual smooth scroll is in progress from a nav click, ignore scroll-spy updates
      if (isManualScrollingRef.current) return;

      // 2. Bottom of the page check: force the last item ('contact' / TRANSMISSION) to be active
      const scrollY = window.scrollY || window.pageYOffset;
      const windowHeight = window.innerHeight;
      const docHeight = document.documentElement.scrollHeight;
      if (scrollY + windowHeight >= docHeight - 4) {
        setActiveSection('contact');
        return;
      }

      // 3. Top of page check: force 'hero-stage' if near top
      if (scrollY <= 50) {
        setActiveSection('hero-stage');
        return;
      }

      // 4. Standard section hit-testing from bottom up
      const scrollPos = scrollY + 140;
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

    // Set manual scrolling flag and lock scroll spy during animation
    isManualScrollingRef.current = true;
    if (scrollTimeoutRef.current) {
      window.clearTimeout(scrollTimeoutRef.current);
    }

    const resetManualScrolling = () => {
      isManualScrollingRef.current = false;
      window.removeEventListener('scrollend', resetManualScrolling);
      if (scrollTimeoutRef.current) {
        window.clearTimeout(scrollTimeoutRef.current);
        scrollTimeoutRef.current = null;
      }
    };

    // Use scrollend event with 1000ms timeout fallback
    if ('onscrollend' in window) {
      window.addEventListener('scrollend', resetManualScrolling, { once: true });
    }
    scrollTimeoutRef.current = window.setTimeout(resetManualScrolling, 1000);

    scrollToSectionById(targetId);
    if (window.history?.pushState) {
      window.history.pushState(null, '', `#${targetId}`);
    }
  };

  const navItems = NAV_ITEMS;
  const topItems = navItems.filter((i) => !SECOND_ROW.includes(i.id));
  const secondRowItems = navItems.filter((i) => SECOND_ROW.includes(i.id));

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
            <div className={`relative flex items-center justify-center w-9 h-9 rounded-lg bg-[#0E1512] border ${isBanana ? 'border-[#FFE135]/70 shadow-[0_0_14px_rgba(255,225,53,0.25)] group-hover:border-[#FFE135]' : 'border-[#2ECC71]/70 shadow-[0_0_14px_rgba(46,204,113,0.25)] group-hover:border-[#2ECC71]'} transition-all`}>
              {/* Subtle Vector Motif: Tactical Pepe / Rotary Banana Badge */}
              <span className={`font-cyber font-black text-base ${isBanana ? 'text-[#FFE135]' : 'text-[#2ECC71]'}`}>
                {theme === 'banana' ? '🍌' : '🐸'}
              </span>
              <span className={`absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full ${isBanana ? 'bg-[#FFE135]' : 'bg-[#2ECC71]'} border border-[#070B09] animate-pulse`} />
            </div>

            <div>
              <div className="flex items-center gap-2">
                <span className="font-cyber font-bold tracking-wider text-white text-[16px]">
                  GERONIMO<span className={isBanana ? 'text-[#FFE135]' : 'text-[#2ECC71]'}>HQ</span>
                </span>
                <span className={`hidden sm:inline-flex tier-5-badge ${isBanana ? 'bg-[#FFE135]/15 text-[#FFE135] border border-[#FFE135]/50' : 'bg-[#2ECC71]/15 text-[#2ECC71] border border-[#2ECC71]/50'}`}>
                  ● ONLINE
                </span>
              </div>
              <div className="text-[10px] font-code tracking-widest uppercase text-[#94A39E] hidden min-[420px]:flex items-center gap-1">
                <span>CYBER-DECK OS</span>
                <span className={isBanana ? 'text-[#FFE135]' : 'text-[#2ECC71]'}>//</span>
                <span className={isBanana ? 'text-[#FFE135]' : 'text-[#2ECC71]'}>{isBanana ? 'ROTARY.HOTLINE' : 'PEPE.MATRIX'}</span>
              </div>
            </div>
          </a>

          {/* Floating Command Pill Dock (Desktop) */}
          <nav
            aria-label="Primary Command Dock"
            className="hidden xl:flex items-center gap-1.5 p-1 rounded-xl bg-[#0E1512] border border-[#1E2E26] shadow-inner flex-shrink-0"
          >
            {topItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeSection === item.id;
              return (
                <a
                  key={item.id}
                  href={`#${item.id}`}
                  onClick={(e) => handleNavClick(e, item.id)}
                  className={`h-[30px] px-2.5 rounded-lg text-[11px] font-cyber tracking-wider transition-all flex items-center gap-1.5 flex-shrink-0 ${
                    isActive
                      ? (isBanana ? 'bg-[#FFE135] text-[#070B09] font-bold shadow-[0_0_14px_rgba(255,225,53,0.45)]' : 'bg-[#2ECC71] text-[#070B09] font-bold shadow-[0_0_14px_rgba(46,204,113,0.45)]')
                      : 'text-[#94A39E] hover:text-white hover:bg-[#14201B]'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-[#070B09]' : (isBanana ? 'text-[#FFE135]' : 'text-[#2ECC71]')}`} />
                  <span>{item.label}</span>
                </a>
              );
            })}
          </nav>

          {/* Mobile: menu toggle (every section, RAM included, is inside the menu) */}
          <div className="xl:hidden flex items-center gap-2">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label={mobileMenuOpen ? 'Close Navigation Menu' : 'Open Navigation Menu'}
              aria-expanded={mobileMenuOpen}
              className={`min-h-[34px] min-w-[34px] p-2 rounded-lg bg-[#0E1512] border border-[#1E2E26] ${isBanana ? 'text-[#FFE135] hover:border-[#FFE135]' : 'text-[#2ECC71] hover:border-[#2ECC71]'} flex items-center justify-center transition-colors cursor-pointer`}
            >
              {mobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Drawer (Keyboard Operable & Accessible 44px Touch Targets) */}
        {mobileMenuOpen && (
          <nav
            aria-label="Mobile Command Menu"
            className="xl:hidden flex flex-col gap-1.5 p-2 rounded-xl bg-[#0E1512] border border-[#1E2E26] shadow-2xl"
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
                      ? (isBanana ? 'bg-[#FFE135] text-[#070B09] font-bold shadow-[0_0_12px_rgba(255,225,53,0.4)]' : 'bg-[#2ECC71] text-[#070B09] font-bold shadow-[0_0_12px_rgba(46,204,113,0.4)]')
                      : 'text-[#94A39E] hover:text-white hover:bg-[#121C18]'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-[#070B09]' : (isBanana ? 'text-[#FFE135]' : 'text-[#2ECC71]')}`} />
                  <span>{item.label}</span>
                </a>
              );
            })}
          </nav>
        )}

        {/* TIER 2: theme signal, DOWNLOAD RAM and WORLD NEWS (desktop), clock. Same 4 columns as before, so the row lines up with the top bar. */}
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-2 pt-0.5">
          {/* Pill 1: Active Theme Signal */}
          <div
            data-gremlin-ignore="true"
            className={`hud-data-pill justify-between ${isBanana ? 'border-[#FFE135]/40 text-[#FFE135]' : 'border-[#2ECC71]/40 text-[#2ECC71]'}`}
            title="Active Cyber-Deck Theme Signal (Read-Only Indicator)"
          >
            <span className="flex items-center gap-1.5 truncate">
              <PhoneCall className={`w-3.5 h-3.5 flex-shrink-0 ${isBanana ? 'text-[#FFE135]' : 'text-[#2ECC71]'}`} />
              <span className="font-bold truncate">
                {isBanana ? 'MODE: BANANA PHONE' : 'MODE: PEPE HOLO'}
              </span>
            </span>
            <span className={`w-2 h-2 rounded-full animate-ping flex-shrink-0 ${isBanana ? 'bg-[#FFE135]' : 'bg-[#2ECC71]'}`} />
          </div>

          {secondRowItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;
            return (
              <a
                key={item.id}
                href={`#${item.id}`}
                onClick={(e) => handleNavClick(e, item.id)}
                className={`hidden xl:flex hud-data-pill font-cyber justify-center tracking-wider transition-all ${
                  isActive
                    ? (isBanana ? 'bg-[#FFE135] border-[#FFE135] text-[#070B09] font-bold shadow-[0_0_14px_rgba(255,225,53,0.45)]' : 'bg-[#2ECC71] border-[#2ECC71] text-[#070B09] font-bold shadow-[0_0_14px_rgba(46,204,113,0.45)]')
                    : (isBanana ? 'text-[#94A39E] hover:text-white hover:border-[#FFE135]/60' : 'text-[#94A39E] hover:text-white hover:border-[#2ECC71]/60')
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-[#070B09]' : (isBanana ? 'text-[#FFE135]' : 'text-[#2ECC71]')}`} />
                <span>{item.label}</span>
              </a>
            );
          })}

          {/* Pill 4: Real-Time Clock & Low-Latency Uplink */}
          <div className="flex hud-data-pill justify-between text-[#94A39E]">
            <span className="flex items-center gap-1.5">
              <Activity className={`w-3.5 h-3.5 flex-shrink-0 ${isBanana ? 'text-[#FFE135]' : 'text-[#2ECC71]'}`} />
              <strong className={isBanana ? 'text-[#FFE135]' : 'text-[#2ECC71]'}>{timeStr || '18:00:00'}</strong>
            </span>
            <span className={`flex items-center gap-1 font-bold ${isBanana ? 'text-[#FFE135]' : 'text-[#2ECC71]'}`}>
              <span className={`w-1.5 h-1.5 rounded-full inline-block animate-pulse ${isBanana ? 'bg-[#FFE135]' : 'bg-[#2ECC71]'}`} />
              LOCAL
            </span>
          </div>
        </div>

      </div>
    </header>
  );
};
