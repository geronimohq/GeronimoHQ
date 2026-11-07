import React, { useState, useEffect } from 'react';
import { 
  Gift, 
  AlertTriangle 
} from 'lucide-react';
import confetti from 'canvas-confetti';

interface ScamAdConfig {
  id: string;
  badge: string;
  badgeBg: string;
  badgeFg: string;
  emojis: string;
  headline: string;
  headlineColor: string;
  subBadge: string;
  subBg: string;
  subFg: string;
  btnText: string;
  btnBg: string;
  gradient: string;
  borderColor: string;
  shadow: string;
  prizeName: string;
}

const SCAM_ADS_CATALOG: ScamAdConfig[] = [
  {
    id: 'millionth-visitor',
    badge: '⭐ 1,000,000th VISITOR! ⭐',
    badgeBg: 'bg-red-600',
    badgeFg: 'text-white',
    emojis: '🎁📱💰',
    headline: 'YOU WON (1) FREE BITCOIN & IPHONE 18!',
    headlineColor: 'text-black',
    subBadge: 'EXPIRES IN: 00:45',
    subBg: 'bg-black',
    subFg: 'text-yellow-300 border-yellow-400',
    btnText: 'CLAIM NOW >>',
    btnBg: 'bg-blue-600 hover:bg-blue-700',
    gradient: 'from-yellow-300 via-amber-400 to-red-500',
    borderColor: 'border-red-600',
    shadow: 'shadow-[0_0_25px_rgba(250,204,21,0.85)]',
    prizeName: 'iPhone 18 & 1 Bitcoin',
  },
  {
    id: 'cs2-dragon-lore',
    badge: '⚡ CS2 SECRET DROP ⚡',
    badgeBg: 'bg-fuchsia-700',
    badgeFg: 'text-white',
    emojis: '🔫💎🔥',
    headline: 'AWP DRAGON LORE (FACTORY NEW) UNLOCKED!',
    headlineColor: 'text-white',
    subBadge: 'GABEN SELECTED YOUR IP',
    subBg: 'bg-black',
    subFg: 'text-fuchsia-300 border-fuchsia-400',
    btnText: 'TRANSFER TO STEAM >>',
    btnBg: 'bg-emerald-600 hover:bg-emerald-700',
    gradient: 'from-cyan-400 via-fuchsia-500 to-indigo-700',
    borderColor: 'border-fuchsia-500',
    shadow: 'shadow-[0_0_25px_rgba(236,72,153,0.85)]',
    prizeName: 'AWP Dragon Lore FN',
  },
  {
    id: 'pc-viruses',
    badge: '🚨 CRITICAL SYSTEM ALERT 🚨',
    badgeBg: 'bg-yellow-400',
    badgeFg: 'text-black',
    emojis: '☣️💻💥',
    headline: 'YOUR PC HAS 9,999 TROJANS DETECTED!',
    headlineColor: 'text-yellow-300',
    subBadge: 'WINDOWS DEFENDER PANICKING',
    subBg: 'bg-red-950',
    subFg: 'text-red-400 border-red-500',
    btnText: 'CLEAN COMPUTER NOW >>',
    btnBg: 'bg-red-600 hover:bg-red-700',
    gradient: 'from-red-900 via-black to-red-800',
    borderColor: 'border-red-500',
    shadow: 'shadow-[0_0_25px_rgba(239,68,68,0.9)]',
    prizeName: 'Antivirus Pro 2004 Ultra Clean',
  },
  {
    id: 'rtx-5090',
    badge: '🎮 HARDWARE GIVEAWAY 🎮',
    badgeBg: 'bg-emerald-600',
    badgeFg: 'text-white',
    emojis: '⚡🖥️🚀',
    headline: 'FREE NVIDIA RTX 5090 Ti TITAN OC READY!',
    headlineColor: 'text-emerald-950',
    subBadge: 'ZERO TARIFFS APPLIED',
    subBg: 'bg-black',
    subFg: 'text-emerald-400 border-emerald-400',
    btnText: 'CONFIRM ADDRESS >>',
    btnBg: 'bg-green-600 hover:bg-green-700',
    gradient: 'from-emerald-300 via-teal-400 to-green-500',
    borderColor: 'border-green-600',
    shadow: 'shadow-[0_0_25px_rgba(16,185,129,0.85)]',
    prizeName: 'NVIDIA RTX 5090 Ti Titan',
  },
  {
    id: 'dust2-singles',
    badge: '💋 REGIONAL ZE RADAR 💋',
    badgeBg: 'bg-pink-600',
    badgeFg: 'text-white',
    emojis: '👩‍🦰🎯💘',
    headline: 'HOT SINGLES IN YOUR DUST2 SERVER WANT TO 1v1!',
    headlineColor: 'text-pink-950',
    subBadge: 'DISTANCE: 0.4 METERS AWAY',
    subBg: 'bg-pink-950',
    subFg: 'text-pink-300 border-pink-400',
    btnText: 'OPEN CHAT NOW >>',
    btnBg: 'bg-pink-600 hover:bg-pink-700',
    gradient: 'from-pink-300 via-rose-400 to-red-400',
    borderColor: 'border-pink-500',
    shadow: 'shadow-[0_0_25px_rgba(244,63,94,0.85)]',
    prizeName: 'VIP 1v1 Server Invite Pass',
  },
  {
    id: 'tesla-truck',
    badge: '🏎️ TESLA VIP DROP 🏎️',
    badgeBg: 'bg-zinc-800',
    badgeFg: 'text-white',
    emojis: '🏎️🔋🤖',
    headline: 'ELON MUSK GIFTED YOU A CYBERTRUCK!',
    headlineColor: 'text-black',
    subBadge: 'STAINLESS STEEL GUARANTEED',
    subBg: 'bg-black',
    subFg: 'text-cyan-300 border-cyan-400',
    btnText: 'PICK UP KEYS >>',
    btnBg: 'bg-zinc-900 hover:bg-zinc-800',
    gradient: 'from-slate-200 via-zinc-400 to-slate-300',
    borderColor: 'border-zinc-700',
    shadow: 'shadow-[0_0_25px_rgba(203,213,225,0.7)]',
    prizeName: 'CyberTruck Foundation Edition',
  },
  {
    id: 'vbucks-billion',
    badge: '🛸 FORTNITE & ROBUX 🛸',
    badgeBg: 'bg-blue-600',
    badgeFg: 'text-white',
    emojis: '💎⛏️🍕',
    headline: 'DOWNLOAD 1,000,000 V-BUCKS & 100,000 ROBUX!',
    headlineColor: 'text-blue-950',
    subBadge: 'NO PARENTAL PERMISSION NEEDED',
    subBg: 'bg-black',
    subFg: 'text-cyan-400 border-cyan-400',
    btnText: 'DOWNLOAD V-BUCKS >>',
    btnBg: 'bg-yellow-500 hover:bg-yellow-600 text-black',
    gradient: 'from-sky-300 via-cyan-400 to-blue-500',
    borderColor: 'border-blue-600',
    shadow: 'shadow-[0_0_25px_rgba(56,189,248,0.85)]',
    prizeName: '1,000,000 V-Bucks Direct Inject',
  },
  {
    id: 'secret-fbi',
    badge: '🕶️ CLASSIFIED INTELLIGENCE 🕶️',
    badgeBg: 'bg-neutral-900',
    badgeFg: 'text-amber-400',
    emojis: '🕵️‍♂️📂🔒',
    headline: 'TOP SECRET DOSSIER ON GERONIMO FOUND!',
    headlineColor: 'text-green-400',
    subBadge: 'LEVEL 5 CLEARANCE REQUIRED',
    subBg: 'bg-black',
    subFg: 'text-emerald-400 border-emerald-500',
    btnText: 'DECRYPT FILES >>',
    btnBg: 'bg-emerald-700 hover:bg-emerald-800',
    gradient: 'from-black via-zinc-900 to-neutral-900',
    borderColor: 'border-emerald-500',
    shadow: 'shadow-[0_0_25px_rgba(16,185,129,0.7)]',
    prizeName: 'Declassified Holo-File #730',
  },
  {
    id: 'free-pizza',
    badge: '🍕 LIFETIME PIZZA PASS 🍕',
    badgeBg: 'bg-amber-600',
    badgeFg: 'text-white',
    emojis: '🍕🧀🥤',
    headline: 'UNLIMITED EXTRA CHEESE PIZZA FOR LIFE!',
    headlineColor: 'text-amber-950',
    subBadge: 'HOT BOX DELIVERY: 12 MIN',
    subBg: 'bg-black',
    subFg: 'text-amber-300 border-amber-400',
    btnText: 'EAT PIZZA NOW >>',
    btnBg: 'bg-orange-600 hover:bg-orange-700',
    gradient: 'from-yellow-200 via-amber-300 to-orange-400',
    borderColor: 'border-orange-500',
    shadow: 'shadow-[0_0_25px_rgba(245,158,11,0.85)]',
    prizeName: 'Lifetime Stuffed Crust Pass',
  },
  {
    id: 'motherboard-heat',
    badge: '☢️ THERMAL CRISIS ☢️',
    badgeBg: 'bg-red-700',
    badgeFg: 'text-white',
    emojis: '🌡️🔥🚒',
    headline: 'YOUR MOTHERBOARD IS AT 1,420°C!',
    headlineColor: 'text-white',
    subBadge: 'DOWNLOAD WATER COOLING NOW',
    subBg: 'bg-black',
    subFg: 'text-cyan-300 border-cyan-400',
    btnText: 'EXTINGUISH GPU >>',
    btnBg: 'bg-cyan-600 hover:bg-cyan-700',
    gradient: 'from-red-600 via-rose-700 to-orange-600',
    borderColor: 'border-yellow-400',
    shadow: 'shadow-[0_0_25px_rgba(239,68,68,0.95)]',
    prizeName: 'Virtual Liquid Nitrogen Hose',
  },
  {
    id: 'chattering-bananas',
    badge: '🍌 WHOLESALE SHIPMENT 🍌',
    badgeBg: 'bg-yellow-500',
    badgeFg: 'text-black',
    emojis: '🍌📞💃',
    headline: '1,000 CHATTERING BANANA PHONES INCOMING!',
    headlineColor: 'text-yellow-950',
    subBadge: 'RING RING RING NON-STOP',
    subBg: 'bg-black',
    subFg: 'text-yellow-300 border-yellow-400',
    btnText: 'ACCEPT CARGO >>',
    btnBg: 'bg-amber-500 hover:bg-amber-600 text-black',
    gradient: 'from-yellow-300 via-yellow-400 to-amber-500',
    borderColor: 'border-yellow-600',
    shadow: 'shadow-[0_0_25px_rgba(234,179,8,0.9)]',
    prizeName: '1,000 Chattering Banana Plushies',
  },
  {
    id: 'fps-glitch',
    badge: '⚙️ VALVE HATES THIS ⚙️',
    badgeBg: 'bg-purple-800',
    badgeFg: 'text-white',
    emojis: '⚡📈👑',
    headline: 'SECRET CS2 CONSOLE COMMAND GIVES 800 FPS!',
    headlineColor: 'text-purple-950',
    subBadge: '100% NO BAN GUARANTEE*',
    subBg: 'bg-black',
    subFg: 'text-purple-300 border-purple-400',
    btnText: 'REVEAL COMMAND >>',
    btnBg: 'bg-purple-600 hover:bg-purple-700',
    gradient: 'from-purple-300 via-fuchsia-400 to-purple-500',
    borderColor: 'border-purple-600',
    shadow: 'shadow-[0_0_25px_rgba(168,85,247,0.85)]',
    prizeName: 'Zero-Latency Engine Config',
  }
];

export const FakeRetroScamAds: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [step, setStep] = useState(1);
  const [isSpinning, setIsSpinning] = useState(false);
  const [wheelAngle, setWheelAngle] = useState(0);
  const [countdown, setCountdown] = useState(45);
  const [selectedCaptcha, setSelectedCaptcha] = useState<number[]>([]);
  const [calibratingProgress, setCalibratingProgress] = useState(98.1);
  const [closeAttempts, setCloseAttempts] = useState(0);

  // RNG Banner Indices
  const [leftAdIndex, setLeftAdIndex] = useState<number>(() => Math.floor(Math.random() * SCAM_ADS_CATALOG.length));
  const [rightAdIndex, setRightAdIndex] = useState<number>(() => {
    let r = Math.floor(Math.random() * SCAM_ADS_CATALOG.length);
    while (r === 0 && SCAM_ADS_CATALOG.length > 1) {
      r = Math.floor(Math.random() * SCAM_ADS_CATALOG.length);
    }
    return r;
  });
  const [activeAd, setActiveAd] = useState<ScamAdConfig>(SCAM_ADS_CATALOG[0]);

  // Dynamic High-Variance RNG Rotation Timer:
  // Randomly cycles both banners independently every 7 to 10 seconds!
  useEffect(() => {
    const leftTimer = setInterval(() => {
      setLeftAdIndex((prev) => {
        let next = Math.floor(Math.random() * SCAM_ADS_CATALOG.length);
        if (next === prev) next = (next + 1) % SCAM_ADS_CATALOG.length;
        return next;
      });
    }, 7500);

    const rightTimer = setInterval(() => {
      setRightAdIndex((prev) => {
        let next = Math.floor(Math.random() * SCAM_ADS_CATALOG.length);
        if (next === prev) next = (next + 2) % SCAM_ADS_CATALOG.length;
        return next;
      });
    }, 9200);

    return () => {
      clearInterval(leftTimer);
      clearInterval(rightTimer);
    };
  }, []);

  // Fake ticking countdown timer
  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => (prev > 1 ? prev - 1 : 59));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const openModalWithAd = (ad: ScamAdConfig) => {
    setActiveAd(ad);
    setIsOpen(true);
    setStep(1);
    setWheelAngle(0);
    setSelectedCaptcha([]);
    setCalibratingProgress(98.1);
  };

  const rerollLeft = (e: React.MouseEvent) => {
    e.stopPropagation();
    setLeftAdIndex((prev) => (prev + 1) % SCAM_ADS_CATALOG.length);
  };

  const rerollRight = (e: React.MouseEvent) => {
    e.stopPropagation();
    setRightAdIndex((prev) => (prev + 1) % SCAM_ADS_CATALOG.length);
  };

  const handleSpin = () => {
    if (isSpinning) return;
    setIsSpinning(true);
    // Rigged spin: always lands just past the jackpot into "SPIN AGAIN / SURVEY REQUIRED"
    const targetAngle = wheelAngle + 1800 + 45;
    setWheelAngle(targetAngle);

    setTimeout(() => {
      setIsSpinning(false);
      setStep(2);
    }, 3200);
  };

  const handleCaptchaSubmit = () => {
    if (selectedCaptcha.length === 0) {
      alert("⚠️ Error: You must select at least one banana hologram to prove you are human!");
      return;
    }
    setStep(3);

    // Slowly calibrate progress
    let cur = 98.1;
    const progTimer = setInterval(() => {
      cur += 0.2;
      if (cur >= 99.8) {
        clearInterval(progTimer);
        setTimeout(() => setStep(4), 1000);
      } else {
        setCalibratingProgress(Number(cur.toFixed(1)));
      }
    }, 350);
  };

  const handleClaimFinalPrize = () => {
    confetti({
      particleCount: 80,
      spread: 90,
      origin: { y: 0.6 },
      colors: ['#ffe600', '#f59e0b', '#00ffcc', '#ff007f']
    });
    setIsOpen(false);
    // Scroll down to the RAM download holo-chamber
    const el = document.getElementById('download-ram');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleTrollClose = () => {
    if (closeAttempts < 2) {
      setCloseAttempts((c) => c + 1);
      alert(`🚨 WAIT! Are you sure? If you leave now, your ${activeAd.prizeName} will be transferred to another visitor in 5 seconds!`);
    } else {
      setIsOpen(false);
      setCloseAttempts(0);
    }
  };

  const leftAd = SCAM_ADS_CATALOG[leftAdIndex] || SCAM_ADS_CATALOG[0];
  const rightAd = SCAM_ADS_CATALOG[rightAdIndex] || SCAM_ADS_CATALOG[1];

  return (
    <>
      {/* LEFT RETRO FLOATING SCAM BANNER (Desktop Gutters) */}
      <div className="hidden xl:flex fixed left-3 top-1/2 -translate-y-1/2 z-30 flex-col items-center group">
        <div 
          onClick={() => openModalWithAd(leftAd)}
          className={`relative w-44 p-2.5 bg-gradient-to-b ${leftAd.gradient} rounded-lg border-2 border-dashed ${leftAd.borderColor} ${leftAd.shadow} cursor-pointer hover:scale-105 active:scale-95 transition-all text-center select-none animate-pulse`}
          title={`Click to claim your guaranteed ${leftAd.prizeName}!`}
        >
          {/* Quick RNG Reroll Pill */}
          <button
            onClick={rerollLeft}
            className="absolute -top-2 -right-2 bg-black/80 hover:bg-black text-[9px] text-yellow-300 font-mono px-1.5 py-0.5 rounded border border-yellow-400 shadow z-10 cursor-pointer"
            title="Roll next scam ad (RNG)"
          >
            🎲 RNG
          </button>

          <div className={`${leftAd.badgeBg} ${leftAd.badgeFg} font-black text-[9px] tracking-wider px-1 py-0.5 rounded uppercase mb-1 truncate`}>
            {leftAd.badge}
          </div>
          <div className="flex justify-center my-1 text-2xl animate-bounce">
            {leftAd.emojis}
          </div>
          <div className={`font-extrabold ${leftAd.headlineColor} text-[11px] leading-tight drop-shadow-sm font-sans uppercase min-h-[32px] flex items-center justify-center`}>
            {leftAd.headline}
          </div>
          <div className={`mt-1.5 py-0.5 px-1 ${leftAd.subBg} ${leftAd.subFg} font-mono text-[8px] font-bold rounded border truncate`}>
            {leftAd.subBadge.includes('00:') ? `EXPIRES IN: 00:${countdown < 10 ? `0${countdown}` : countdown}` : leftAd.subBadge}
          </div>
          <button className={`mt-2 w-full py-1 ${leftAd.btnBg} text-white font-bold text-[10px] rounded shadow tracking-wide uppercase cursor-pointer`}>
            {leftAd.btnText}
          </button>
        </div>
      </div>

      {/* RIGHT RETRO FLOATING SCAM BANNER (Desktop Gutters) */}
      <div className="hidden xl:flex fixed right-3 top-1/2 -translate-y-1/2 z-30 flex-col items-center group">
        <div 
          onClick={() => openModalWithAd(rightAd)}
          className={`relative w-44 p-2.5 bg-gradient-to-b ${rightAd.gradient} rounded-lg border-2 border-dashed ${rightAd.borderColor} ${rightAd.shadow} cursor-pointer hover:scale-105 active:scale-95 transition-all text-center select-none animate-pulse`}
          title={`Click to claim your guaranteed ${rightAd.prizeName}!`}
        >
          {/* Quick RNG Reroll Pill */}
          <button
            onClick={rerollRight}
            className="absolute -top-2 -left-2 bg-black/80 hover:bg-black text-[9px] text-cyan-300 font-mono px-1.5 py-0.5 rounded border border-cyan-400 shadow z-10 cursor-pointer"
            title="Roll next scam ad (RNG)"
          >
            🎲 RNG
          </button>

          <div className={`${rightAd.badgeBg} ${rightAd.badgeFg} font-black text-[9px] tracking-wider px-1 py-0.5 rounded uppercase mb-1 truncate`}>
            {rightAd.badge}
          </div>
          <div className="flex justify-center my-1 text-2xl animate-spin" style={{ animationDuration: '4.5s' }}>
            {rightAd.emojis.slice(0, 2) || '🎡'}
          </div>
          <div className={`font-extrabold ${rightAd.headlineColor} text-[11px] leading-tight drop-shadow-md font-sans uppercase min-h-[32px] flex items-center justify-center`}>
            {rightAd.headline}
          </div>
          <div className={`mt-1.5 py-0.5 px-1 ${rightAd.subBg} ${rightAd.subFg} font-mono text-[8px] font-bold rounded border truncate`}>
            {rightAd.subBadge.includes('00:') ? `EXPIRES IN: 00:${countdown < 10 ? `0${countdown}` : countdown}` : rightAd.subBadge}
          </div>
          <button className={`mt-2 w-full py-1 ${rightAd.btnBg} text-white font-bold text-[10px] rounded shadow tracking-wide uppercase cursor-pointer`}>
            {rightAd.btnText}
          </button>
        </div>
      </div>

      {/* THE ENDLESS SCAM SURVEY HOLO-TERMINAL MODAL */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="relative w-full max-w-lg bg-[#000080] border-4 border-[#c0c0c0] shadow-[0_0_50px_rgba(0,0,0,0.9)] font-sans text-black overflow-hidden rounded-none">
            
            {/* Windows 98 / Early 2000s Classic Blue Window Title Bar */}
            <div className="bg-gradient-to-r from-[#000080] via-[#1084d0] to-[#000080] text-white font-bold text-xs px-2 py-1.5 flex items-center justify-between select-none">
              <div className="flex items-center gap-1.5">
                <Gift className="w-4 h-4 text-yellow-300" />
                <span className="tracking-wide uppercase">
                  OFFICIAL {activeAd.prizeName.toUpperCase()} CLAIM TERMINAL // STEP {step} OF 99
                </span>
              </div>
              <button 
                onClick={handleTrollClose}
                className="w-5 h-5 bg-[#c0c0c0] text-black font-bold text-xs flex items-center justify-center border-t border-l border-white border-b-2 border-r-2 border-black active:border-t-2 active:border-l-2 active:border-b active:border-r cursor-pointer"
              >
                ✕
              </button>
            </div>

            {/* Window Content Body */}
            <div className="p-4 bg-[#c0c0c0]">
              
              {/* STEP 1: RIGGED WHEEL */}
              {step === 1 && (
                <div className="flex flex-col items-center text-center">
                  <h3 className="text-base font-black text-red-700 uppercase tracking-tight mb-1">
                    🎉 YOU HAVE (1) COMPLIMENTARY PRIZE SPIN! 🎉
                  </h3>
                  <p className="text-xs text-gray-800 mb-3">
                    Click <strong>SPIN</strong> below to secure your <strong>{activeAd.prizeName}</strong>!
                  </p>

                  {/* Wheel Graphic */}
                  <div className="relative w-44 h-44 my-2 flex items-center justify-center">
                    {/* Fixed Pointer Needle */}
                    <div className="absolute -top-3 z-20 text-red-600 text-xl font-black">
                      ▼
                    </div>
                    {/* Rotating Wheel */}
                    <div 
                      className="w-40 h-40 rounded-full border-4 border-black relative overflow-hidden transition-transform ease-out shadow-lg"
                      style={{ 
                        transform: `rotate(${wheelAngle}deg)`,
                        transitionDuration: isSpinning ? '3.2s' : '0s',
                        background: 'conic-gradient(#facc15 0deg 90deg, #3b82f6 90deg 180deg, #ef4444 180deg 270deg, #10b981 270deg 360deg)'
                      }}
                    >
                      <div className="absolute inset-0 flex items-center justify-center text-[10px] font-black text-white">
                        <span className="absolute top-2 text-black">1 BTC 💰</span>
                        <span className="absolute bottom-2 text-white">PRIZE 📱</span>
                        <span className="absolute left-2 text-white">128GB RAM</span>
                        <span className="absolute right-1 text-black">SPIN AGAIN 🔄</span>
                      </div>
                    </div>
                    {/* Center Peg */}
                    <div className="absolute w-8 h-8 rounded-full bg-white border-2 border-black flex items-center justify-center z-10 font-bold text-[10px]">
                      ⭐
                    </div>
                  </div>

                  <button
                    onClick={handleSpin}
                    disabled={isSpinning}
                    className={`mt-4 px-6 py-2.5 text-sm font-black uppercase text-white rounded border-2 border-black tracking-wider transition-all ${
                      isSpinning 
                        ? 'bg-gray-500 cursor-not-allowed' 
                        : 'bg-red-600 hover:bg-red-700 active:scale-95 cursor-pointer shadow-[0_4px_0_#000]'
                    }`}
                  >
                    {isSpinning ? 'SPINNING RIGGED WHEEL...' : '👉 CLICK TO SPIN NOW! 👈'}
                  </button>
                </div>
              )}

              {/* STEP 2: PARODY CAPTCHA */}
              {step === 2 && (
                <div className="flex flex-col text-left">
                  <div className="p-2 bg-yellow-100 border border-yellow-500 rounded text-xs text-yellow-900 mb-3 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
                    <span><strong>ALMOST WON!</strong> Arrow landed on &quot;Spin Again / Survey Verification Required&quot;!</span>
                  </div>

                  <h4 className="font-bold text-xs text-gray-900 uppercase mb-1">
                    Human Security Check (Question 1 of 47):
                  </h4>
                  <p className="text-[11px] text-gray-700 mb-2">
                    Select all images that contain a <strong>Dancing Banana vibrating at exactly 440 Hz</strong>:
                  </p>

                  <div className="grid grid-cols-3 gap-2 my-2">
                    {[
                      { id: 1, label: 'Banana 1', emoji: '🍌' },
                      { id: 2, label: 'Banana 2', emoji: '🍌' },
                      { id: 3, label: 'Pepe', emoji: '🐸' },
                      { id: 4, label: 'Telephone', emoji: '📞' },
                      { id: 5, label: 'Banana 3', emoji: '🍌' },
                      { id: 6, label: 'Computer RAM', emoji: '💾' },
                    ].map((item) => {
                      const isSel = selectedCaptcha.includes(item.id);
                      return (
                        <div
                          key={item.id}
                          onClick={() => {
                            setSelectedCaptcha((prev) => 
                              isSel ? prev.filter((x) => x !== item.id) : [...prev, item.id]
                            );
                          }}
                          className={`p-3 text-center border-2 rounded cursor-pointer transition-all select-none ${
                            isSel 
                              ? 'bg-blue-200 border-blue-600 font-bold' 
                              : 'bg-white border-gray-400 hover:bg-gray-50'
                          }`}
                        >
                          <div className="text-2xl mb-1">{item.emoji}</div>
                          <div className="text-[10px] text-gray-800">{item.label}</div>
                          <input 
                            type="checkbox" 
                            checked={isSel} 
                            readOnly 
                            className="mt-1 pointer-events-none"
                          />
                        </div>
                      );
                    })}
                  </div>

                  <button
                    onClick={handleCaptchaSubmit}
                    className="mt-3 w-full py-2 bg-blue-700 hover:bg-blue-800 text-white font-bold text-xs uppercase rounded border-2 border-black shadow-[0_3px_0_#000] active:translate-y-0.5 cursor-pointer"
                  >
                    Verify &amp; Continue &gt;&gt;
                  </button>
                </div>
              )}

              {/* STEP 3: FAKE SATELLITE CALIBRATION PROGRESS BAR */}
              {step === 3 && (
                <div className="flex flex-col text-center py-4">
                  <div className="text-3xl mb-2 animate-bounce">
                    🛰️📡
                  </div>
                  <h4 className="font-bold text-sm text-gray-900 uppercase mb-1">
                    Calibrating Quantum Delivery Satellite...
                  </h4>
                  <p className="text-xs text-gray-700 mb-3">
                    Locking GPS coordinates to beam your <strong>{activeAd.prizeName}</strong> to your chair:
                  </p>

                  <div className="w-full bg-gray-300 border-2 border-gray-600 h-6 p-0.5 rounded overflow-hidden">
                    <div 
                      className="bg-blue-600 h-full text-white text-[10px] font-bold flex items-center justify-center transition-all duration-300"
                      style={{ width: `${calibratingProgress}%` }}
                    >
                      {calibratingProgress}%
                    </div>
                  </div>

                  <p className="mt-3 text-[10px] text-gray-600 italic">
                    Please do not close this window or turn off your computer...
                  </p>
                </div>
              )}

              {/* STEP 4: HILARIOUS FINAL REVEAL & CONVERSION */}
              {step === 4 && (
                <div className="flex flex-col items-center text-center py-2">
                  <div className="text-4xl mb-2">
                    🏆🎉
                  </div>
                  <h3 className="text-base font-black text-emerald-800 uppercase tracking-tight mb-1">
                    CONGRATULATIONS, CHAMPION!
                  </h3>
                  <p className="text-xs text-gray-800 mb-3">
                    You have successfully passed the grueling 2000s verification gauntlet!
                  </p>

                  <div className="p-3 bg-white border-2 border-gray-500 rounded text-left text-xs mb-4 w-full">
                    <div className="font-bold text-red-600 mb-1">
                      ⚠️ PRIZE CONVERSION NOTICE:
                    </div>
                    <p className="text-gray-700 text-[11px] leading-relaxed">
                      Due to international holo-shipping restrictions, your <strong>{activeAd.prizeName}</strong> has been automatically converted into <strong>128 Gigabytes of 100% Free Pure Holographic RAM</strong> in the GeronimoHQ Holo-Chamber!
                    </p>
                  </div>

                  <button
                    onClick={handleClaimFinalPrize}
                    className="w-full py-2.5 bg-green-600 hover:bg-green-700 text-white font-black text-sm uppercase rounded border-2 border-black shadow-[0_4px_0_#000] active:translate-y-0.5 cursor-pointer tracking-wider"
                  >
                    🚀 DOWNLOAD MY 128GB RAM NOW!
                  </button>
                </div>
              )}

            </div>
          </div>
        </div>
      )}
    </>
  );
};
