import React, { useState, useEffect } from 'react';
import { Gift } from 'lucide-react';
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

export const SCAM_ADS_CATALOG: ScamAdConfig[] = [
  {
    id: 'millionth-visitor',
    badge: '⭐ 1,000,000th VISITOR! ⭐',
    badgeBg: 'bg-red-600',
    badgeFg: 'text-white',
    emojis: '🎁📱💰',
    headline: 'YOU WON (1) FREE BITCOIN & IPHONE 18 PRO MAX!',
    headlineColor: 'text-black',
    subBadge: 'EXPIRES IN: 00:45',
    subBg: 'bg-black',
    subFg: 'text-yellow-300 border-yellow-400',
    btnText: 'CLAIM NOW >>',
    btnBg: 'bg-blue-600 hover:bg-blue-700',
    gradient: 'from-yellow-300 via-amber-400 to-red-500',
    borderColor: 'border-red-600',
    shadow: 'shadow-[0_0_25px_rgba(250,204,21,0.85)]',
    prizeName: 'iPhone 18 Pro Max & 1 Bitcoin',
  },
  {
    id: 'cs2-dragon-lore',
    badge: '⚡ CS2 SECRET DROP ⚡',
    badgeBg: 'bg-fuchsia-700',
    badgeFg: 'text-white',
    emojis: '🔫💎🔥',
    headline: 'AWP DRAGON LORE (FACTORY NEW) SOUVENIR UNLOCKED!',
    headlineColor: 'text-white',
    subBadge: 'GABEN SELECTED YOUR IP',
    subBg: 'bg-black',
    subFg: 'text-fuchsia-300 border-fuchsia-400',
    btnText: 'TRANSFER TO STEAM >>',
    btnBg: 'bg-emerald-600 hover:bg-emerald-700',
    gradient: 'from-cyan-400 via-fuchsia-500 to-indigo-700',
    borderColor: 'border-fuchsia-500',
    shadow: 'shadow-[0_0_25px_rgba(236,72,153,0.85)]',
    prizeName: 'AWP Dragon Lore FN Souvenir',
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
    headline: 'FREE NVIDIA RTX 5090 Ti TITAN 64GB READY!',
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
    headline: 'HOT ZE PLAYERS IN YOUR AREA WANT TO 1v1!',
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
    headline: 'ELON MUSK GIFTED YOU A CYBERTRUCK CYBERBEAST!',
    headlineColor: 'text-black',
    subBadge: 'STAINLESS STEEL GUARANTEED',
    subBg: 'bg-black',
    subFg: 'text-cyan-300 border-cyan-400',
    btnText: 'PICK UP KEYS >>',
    btnBg: 'bg-zinc-900 hover:bg-zinc-800',
    gradient: 'from-slate-200 via-zinc-400 to-slate-300',
    borderColor: 'border-zinc-700',
    shadow: 'shadow-[0_0_25px_rgba(203,213,225,0.7)]',
    prizeName: 'CyberTruck Cyberbeast Edition',
  },
  {
    id: 'vbucks-billion',
    badge: '🛸 FORTNITE & ROBUX 🛸',
    badgeBg: 'bg-blue-600',
    badgeFg: 'text-white',
    emojis: '💎⛏️🍕',
    headline: 'DOWNLOAD 10,000,000 V-BUCKS & 1,000,000 ROBUX!',
    headlineColor: 'text-blue-950',
    subBadge: 'NO PARENTAL PERMISSION NEEDED',
    subBg: 'bg-black',
    subFg: 'text-cyan-400 border-cyan-400',
    btnText: 'DOWNLOAD V-BUCKS >>',
    btnBg: 'bg-yellow-500 hover:bg-yellow-600 text-black',
    gradient: 'from-sky-300 via-cyan-400 to-blue-500',
    borderColor: 'border-blue-600',
    shadow: 'shadow-[0_0_25px_rgba(56,189,248,0.85)]',
    prizeName: '10,000,000 V-Bucks Direct Inject',
  },
  {
    id: 'secret-fbi',
    badge: '🕶️ CLASSIFIED INTELLIGENCE 🕶️',
    badgeBg: 'bg-neutral-900',
    badgeFg: 'text-amber-400',
    emojis: '🕵️‍♂️📂🔒',
    headline: 'TOP SECRET DOSSIER ON GERONIMO REVEALED!',
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
    headline: 'UNLIMITED EXTRA CHEESE PIZZA DELIVERED DAILY!',
    headlineColor: 'text-amber-950',
    subBadge: 'HOT BOX DELIVERY: 10 MIN',
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
    headline: 'YOUR MOTHERBOARD IS AT 1,420°C RIGHT NOW!',
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
    headline: 'SECRET CS2 CONSOLE COMMAND GIVES 999 FPS!',
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
  },
  {
    id: 'nigerian-prince',
    badge: '👑 ROYAL WIRE TRANSFER 👑',
    badgeBg: 'bg-amber-700',
    badgeFg: 'text-yellow-200',
    emojis: '🏰💎✉️',
    headline: 'PRINCE ABIDEMI WANTS TO SEND YOU $42,000,000!',
    headlineColor: 'text-yellow-950',
    subBadge: 'REQUIRES $5 STEAM GIFT CARD',
    subBg: 'bg-black',
    subFg: 'text-yellow-400 border-yellow-500',
    btnText: 'ACCEPT INHERITANCE >>',
    btnBg: 'bg-emerald-600 hover:bg-emerald-700',
    gradient: 'from-amber-200 via-yellow-300 to-amber-500',
    borderColor: 'border-amber-600',
    shadow: 'shadow-[0_0_25px_rgba(217,119,6,0.85)]',
    prizeName: '$42,000,000 Royal Gold Wire',
  },
  {
    id: 'cs2-knife-gold',
    badge: '🔪 CS2 CASE SIMULATOR 🔪',
    badgeBg: 'bg-yellow-600',
    badgeFg: 'text-black',
    emojis: '📦✨🗡️',
    headline: '★ BUTTERFLY KNIFE DOPPLER SAPPHIRE WON!',
    headlineColor: 'text-white',
    subBadge: 'CHANCE: 0.0000001%',
    subBg: 'bg-indigo-950',
    subFg: 'text-blue-300 border-blue-400',
    btnText: 'SEND TRADE OFFER >>',
    btnBg: 'bg-blue-600 hover:bg-blue-700',
    gradient: 'from-indigo-900 via-blue-900 to-purple-900',
    borderColor: 'border-cyan-400',
    shadow: 'shadow-[0_0_25px_rgba(96,165,250,0.9)]',
    prizeName: '★ Butterfly Knife Doppler Sapphire',
  },
  {
    id: 'free-ram-stick',
    badge: '💾 PHYSICAL RAM DELIVERY 💾',
    badgeBg: 'bg-cyan-700',
    badgeFg: 'text-white',
    emojis: '🚚📦🧠',
    headline: '512GB DDR6 9600MHz RGB TRIDENT Z ON TRUCK!',
    headlineColor: 'text-cyan-950',
    subBadge: 'TRACKING NUMBER: #RAM-420',
    subBg: 'bg-black',
    subFg: 'text-cyan-400 border-cyan-400',
    btnText: 'SIGN FOR PARCEL >>',
    btnBg: 'bg-cyan-600 hover:bg-cyan-700',
    gradient: 'from-cyan-200 via-sky-300 to-blue-400',
    borderColor: 'border-cyan-500',
    shadow: 'shadow-[0_0_25px_rgba(6,182,212,0.85)]',
    prizeName: '512GB DDR6 9600MHz Kit',
  },
  {
    id: 'gaben-interview',
    badge: '🎙️ VALVE HEADQUARTERS 🎙️',
    badgeBg: 'bg-neutral-800',
    badgeFg: 'text-white',
    emojis: '🏢☕🍕',
    headline: 'GABE NEWELL HIRED YOU AS CS2 LEAD DESIGNER!',
    headlineColor: 'text-white',
    subBadge: 'SALARY: 10,000 CS2 CASES/YR',
    subBg: 'bg-black',
    subFg: 'text-orange-400 border-orange-400',
    btnText: 'START MONDAY >>',
    btnBg: 'bg-orange-600 hover:bg-orange-700',
    gradient: 'from-neutral-800 via-stone-800 to-zinc-900',
    borderColor: 'border-orange-500',
    shadow: 'shadow-[0_0_25px_rgba(249,115,22,0.8)]',
    prizeName: 'Valve CS2 Senior Architect Badge',
  },
  {
    id: 'mako-reactor-core',
    badge: '☢️ ZE SPECIAL LOOT ☢️',
    badgeBg: 'bg-green-700',
    badgeFg: 'text-white',
    emojis: '🧪🔋💥',
    headline: 'MAKO REACTOR ULTIMA MATERIA INVENTORY DROP!',
    headlineColor: 'text-green-950',
    subBadge: 'CAST TIME: 0.1 SECONDS',
    subBg: 'bg-black',
    subFg: 'text-emerald-400 border-emerald-400',
    btnText: 'EQUIP MATERIA >>',
    btnBg: 'bg-emerald-600 hover:bg-emerald-700',
    gradient: 'from-emerald-300 via-green-400 to-teal-500',
    borderColor: 'border-emerald-500',
    shadow: 'shadow-[0_0_25px_rgba(16,185,129,0.9)]',
    prizeName: 'FFVII Ultima Materia Core',
  },
  {
    id: 'subtick-god',
    badge: '⚡ SUB-TICK PURITY ⚡',
    badgeBg: 'bg-yellow-400',
    badgeFg: 'text-black',
    emojis: '🎯🕒⚡',
    headline: 'YOUR CS2 PING HAS BEEN REDUCED TO -5 MS!',
    headlineColor: 'text-yellow-950',
    subBadge: 'YOU SHOOT BEFORE THEY SPAWN',
    subBg: 'bg-black',
    subFg: 'text-yellow-300 border-yellow-400',
    btnText: 'TIME TRAVEL >>',
    btnBg: 'bg-yellow-500 hover:bg-yellow-600 text-black',
    gradient: 'from-yellow-200 via-amber-300 to-yellow-400',
    borderColor: 'border-yellow-500',
    shadow: 'shadow-[0_0_25px_rgba(234,179,8,0.9)]',
    prizeName: 'Quantum Negative Ping Router',
  },
  {
    id: 'pepe-synth-vinyl',
    badge: '🎵 SYNTHWAVE MASTER TAPE 🎵',
    badgeBg: 'bg-fuchsia-800',
    badgeFg: 'text-white',
    emojis: '📼🎧🪩',
    headline: 'SIGNED GERONIMO PEPE SYNTH 24-HOUR CASSETTE!',
    headlineColor: 'text-fuchsia-950',
    subBadge: 'PURE BASSLINE OVERLOAD',
    subBg: 'bg-black',
    subFg: 'text-fuchsia-400 border-fuchsia-400',
    btnText: 'INSERT TAPE >>',
    btnBg: 'bg-fuchsia-600 hover:bg-fuchsia-700',
    gradient: 'from-fuchsia-200 via-pink-300 to-rose-400',
    borderColor: 'border-fuchsia-500',
    shadow: 'shadow-[0_0_25px_rgba(217,70,239,0.85)]',
    prizeName: 'Pure Gold Pepe Synth Tape',
  },
  {
    id: 'steam-deck-oled',
    badge: '🕹️ VALVE HANDHELD 🕹️',
    badgeBg: 'bg-indigo-700',
    badgeFg: 'text-white',
    emojis: '🎮🖥️✨',
    headline: 'FREE STEAM DECK 2TB OLED SPECIAL EDITION!',
    headlineColor: 'text-indigo-950',
    subBadge: 'INCLUDES PRE-INSTALLED CS2',
    subBg: 'bg-black',
    subFg: 'text-indigo-300 border-indigo-400',
    btnText: 'SHIP HANDHELD >>',
    btnBg: 'bg-indigo-600 hover:bg-indigo-700',
    gradient: 'from-indigo-200 via-sky-300 to-indigo-400',
    borderColor: 'border-indigo-500',
    shadow: 'shadow-[0_0_25px_rgba(99,102,241,0.85)]',
    prizeName: 'Steam Deck OLED 2TB Edition',
  },
  {
    id: 'bhop-macro-mouse',
    badge: '🐇 CS2 MOVEMENT HAX 🐇',
    badgeBg: 'bg-teal-700',
    badgeFg: 'text-white',
    emojis: '🖱️🦘🌪️',
    headline: 'INFINITE BHOP SCROLL WHEEL MOUSE (0 FRICTION)!',
    headlineColor: 'text-teal-950',
    subBadge: 'GAINS 400 VELOCITY INSTANTLY',
    subBg: 'bg-black',
    subFg: 'text-teal-300 border-teal-400',
    btnText: 'SPIN WHEEL >>',
    btnBg: 'bg-teal-600 hover:bg-teal-700',
    gradient: 'from-teal-200 via-emerald-300 to-teal-400',
    borderColor: 'border-teal-500',
    shadow: 'shadow-[0_0_25px_rgba(20,184,166,0.85)]',
    prizeName: 'Ball-Bearing Scroll Wheel Mouse',
  },
  {
    id: 'airhorn-dj-deck',
    badge: '📢 MLG NOSTALGIA 📢',
    badgeBg: 'bg-red-600',
    badgeFg: 'text-white',
    emojis: '🎺🕶️ Doritos',
    headline: 'MLG ILLUMINATI SOUNDBOARD & DORITOS CANNON!',
    headlineColor: 'text-red-950',
    subBadge: '360 NO SCOPE HITMARKER READY',
    subBg: 'bg-black',
    subFg: 'text-red-400 border-red-500',
    btnText: 'BLOW AIRHORN >>',
    btnBg: 'bg-red-600 hover:bg-red-700',
    gradient: 'from-red-300 via-orange-400 to-yellow-500',
    borderColor: 'border-red-600',
    shadow: 'shadow-[0_0_25px_rgba(239,68,68,0.9)]',
    prizeName: 'MLG Triple Airhorn Controller',
  },
  {
    id: 'free-boba-tea',
    badge: '🧋 LIFETIME BOBA PASS 🧋',
    badgeBg: 'bg-amber-800',
    badgeFg: 'text-white',
    emojis: '🧋🍡🥤',
    headline: 'UNLIMITED BROWN SUGAR BOBA MILK TEA FOR LIFE!',
    headlineColor: 'text-amber-950',
    subBadge: 'WARM TAPIOCA GUARANTEED',
    subBg: 'bg-black',
    subFg: 'text-amber-300 border-amber-400',
    btnText: 'DRINK BOBA >>',
    btnBg: 'bg-amber-600 hover:bg-amber-700',
    gradient: 'from-amber-100 via-yellow-200 to-amber-300',
    borderColor: 'border-amber-500',
    shadow: 'shadow-[0_0_25px_rgba(217,119,6,0.85)]',
    prizeName: 'Brown Sugar Boba VIP Card',
  },
  {
    id: 'anti-alt-tab-shield',
    badge: '🛡️ ZERO CRASH CERTIFICATE 🛡️',
    badgeBg: 'bg-emerald-800',
    badgeFg: 'text-white',
    emojis: '💻⚡🛡️',
    headline: 'NEVER CRASH ON ALT-TAB IN CS2 EVER AGAIN!',
    headlineColor: 'text-emerald-950',
    subBadge: 'MPO REPAIR PROTOCOL LOADED',
    subBg: 'bg-black',
    subFg: 'text-emerald-300 border-emerald-400',
    btnText: 'INSTALL SHIELD >>',
    btnBg: 'bg-emerald-600 hover:bg-emerald-700',
    gradient: 'from-emerald-200 via-teal-300 to-cyan-400',
    borderColor: 'border-emerald-600',
    shadow: 'shadow-[0_0_25px_rgba(16,185,129,0.85)]',
    prizeName: 'Direct-Flip Anti-Crash Module',
  }
];

export const FakeRetroScamAds: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [step, setStep] = useState(1);
  const [isSpinning, setIsSpinning] = useState(false);
  const [wheelAngle, setWheelAngle] = useState(0);
  const [countdown, setCountdown] = useState(45);
  const [selectedCaptcha, setSelectedCaptcha] = useState<number[]>([]);
  const [quizAnswer, setQuizAnswer] = useState<number | null>(null);
  const [calibratingProgress, setCalibratingProgress] = useState(98.1);
  const [closeAttempts, setCloseAttempts] = useState(0);

  // High-Variance Non-Repeating Shuffled Indices
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
  // Randomly cycles both banners independently every 5.5 to 7.5 seconds!
  useEffect(() => {
    const leftTimer = setInterval(() => {
      setLeftAdIndex((prev) => {
        let next = Math.floor(Math.random() * SCAM_ADS_CATALOG.length);
        if (next === prev) next = (next + 3) % SCAM_ADS_CATALOG.length;
        return next;
      });
    }, 5800);

    const rightTimer = setInterval(() => {
      setRightAdIndex((prev) => {
        let next = Math.floor(Math.random() * SCAM_ADS_CATALOG.length);
        if (next === prev) next = (next + 7) % SCAM_ADS_CATALOG.length;
        return next;
      });
    }, 7200);

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
    setQuizAnswer(null);
    setCalibratingProgress(98.1);
  };

  const rerollLeft = (e: React.MouseEvent) => {
    e.stopPropagation();
    setLeftAdIndex((prev) => {
      let next = Math.floor(Math.random() * SCAM_ADS_CATALOG.length);
      if (next === prev) next = (next + 1) % SCAM_ADS_CATALOG.length;
      return next;
    });
  };

  const rerollRight = (e: React.MouseEvent) => {
    e.stopPropagation();
    setRightAdIndex((prev) => {
      let next = Math.floor(Math.random() * SCAM_ADS_CATALOG.length);
      if (next === prev) next = (next + 1) % SCAM_ADS_CATALOG.length;
      return next;
    });
  };

  const handleSpin = () => {
    if (isSpinning) return;
    setIsSpinning(true);
    // Rigged spin: always lands just past the jackpot into "EXTRA VERIFICATION REQUIRED"
    const targetAngle = wheelAngle + 1800 + Math.floor(Math.random() * 4) * 45 + 25;
    setWheelAngle(targetAngle);

    setTimeout(() => {
      setIsSpinning(false);
      setStep(2);
    }, 3000);
  };

  const handleCaptchaSubmit = () => {
    if (selectedCaptcha.length === 0) {
      alert("⚠️ Error: You must select at least one banana hologram to prove you are human!");
      return;
    }
    setStep(3);
  };

  const handleQuizSubmit = (optIndex: number) => {
    setQuizAnswer(optIndex);
    setTimeout(() => {
      setStep(4);
      // Slowly calibrate progress to 99.8%
      let cur = 98.1;
      const progTimer = setInterval(() => {
        cur += 0.3;
        if (cur >= 99.8) {
          clearInterval(progTimer);
          setTimeout(() => setStep(5), 1000);
        } else {
          setCalibratingProgress(Number(cur.toFixed(1)));
        }
      }, 300);
    }, 600);
  };

  const handleClaimFinalPrize = () => {
    confetti({
      particleCount: 120,
      spread: 100,
      origin: { y: 0.6 },
      colors: ['#ffe600', '#f59e0b', '#00ffcc', '#ff007f', '#10b981']
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
      alert(`🚨 WAIT! Are you sure? If you leave now, your guaranteed ${activeAd.prizeName} will be forfeited to player #420 in 5 seconds!`);
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
        <div className="text-[9px] font-mono font-bold text-amber-300 bg-black/90 px-2 py-0.5 rounded-t border border-amber-400/50 uppercase tracking-widest shadow select-none">
          PARODY MEME // NO REAL PRIZE
        </div>
        <div 
          onClick={() => openModalWithAd(leftAd)}
          className={`relative w-44 p-2.5 bg-gradient-to-b ${leftAd.gradient} rounded-b-lg border-2 border-dashed ${leftAd.borderColor} ${leftAd.shadow} cursor-pointer hover:scale-105 active:scale-95 transition-all text-center select-none animate-pulse`}
          title={`Click to open parody meme claim wizard for ${leftAd.prizeName} (Satirical joke - zero real files or prizes)`}
        >
          {/* Quick RNG Reroll Pill */}
          <button
            onClick={rerollLeft}
            className="absolute -top-2 -right-2 bg-black/80 hover:bg-black text-[9px] text-yellow-300 font-mono px-1.5 py-0.5 rounded border border-yellow-400 shadow z-10 cursor-pointer"
            title="Roll next scam ad (High RNG)"
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
        <div className="text-[9px] font-mono font-bold text-cyan-300 bg-black/90 px-2 py-0.5 rounded-t border border-cyan-400/50 uppercase tracking-widest shadow select-none">
          PARODY MEME // NO REAL PRIZE
        </div>
        <div 
          onClick={() => openModalWithAd(rightAd)}
          className={`relative w-44 p-2.5 bg-gradient-to-b ${rightAd.gradient} rounded-b-lg border-2 border-dashed ${rightAd.borderColor} ${rightAd.shadow} cursor-pointer hover:scale-105 active:scale-95 transition-all text-center select-none animate-pulse`}
          title={`Click to open parody meme claim wizard for ${rightAd.prizeName} (Satirical joke - zero real files or prizes)`}
        >
          {/* Quick RNG Reroll Pill */}
          <button
            onClick={rerollRight}
            className="absolute -top-2 -left-2 bg-black/80 hover:bg-black text-[9px] text-cyan-300 font-mono px-1.5 py-0.5 rounded border border-cyan-400 shadow z-10 cursor-pointer"
            title="Roll next scam ad (High RNG)"
          >
            🎲 RNG
          </button>

          <div className={`${rightAd.badgeBg} ${rightAd.badgeFg} font-black text-[9px] tracking-wider px-1 py-0.5 rounded uppercase mb-1 truncate`}>
            {rightAd.badge}
          </div>
          <div className="flex justify-center my-1 text-2xl animate-bounce">
            {rightAd.emojis}
          </div>
          <div className={`font-extrabold ${rightAd.headlineColor} text-[11px] leading-tight drop-shadow-sm font-sans uppercase min-h-[32px] flex items-center justify-center`}>
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

      {/* INTERACTIVE RETRO SCAM ENDLESS TASK MODAL */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-sm animate-fadeIn">
          <div className="relative w-full max-w-lg bg-slate-900 border-4 border-yellow-400 rounded-xl shadow-[0_0_50px_rgba(250,204,21,0.5)] overflow-hidden font-sans">
            {/* Retro Windows 98 Style Title Bar */}
            <div className="bg-gradient-to-r from-blue-800 to-blue-600 px-3 py-1.5 flex items-center justify-between text-white border-b-2 border-yellow-400 select-none">
              <div className="flex items-center gap-2">
                <Gift className="w-4 h-4 text-yellow-300 animate-spin" />
                <span className="font-bold text-xs tracking-wider">
                  OFFICIAL CLAIM WIZARD // PARODY DISPATCHER (0 REAL BYTES)
                </span>
              </div>
              <button 
                onClick={handleTrollClose}
                className="w-5 h-5 bg-red-600 hover:bg-red-700 text-white font-bold text-xs flex items-center justify-center border border-white cursor-pointer"
                title="Attempt to Close (Risky!)"
              >
                ✕
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-5 text-center text-slate-100">
              {/* STAGE 1: THE RIGGED ROULETTE */}
              {step === 1 && (
                <div className="space-y-4">
                  <div className="inline-block bg-yellow-400 text-black font-black text-xs px-3 py-1 rounded-full uppercase tracking-widest animate-pulse">
                    STEP 1 OF 5: LUCKY WHEEL OF DESTINY
                  </div>
                  <h3 className="text-xl font-black text-yellow-300 drop-shadow">
                    SPIN TO UNLOCK: {activeAd.prizeName.toUpperCase()}!
                  </h3>
                  <p className="text-xs text-slate-300">
                    Every visitor gets 100% chance of winning today. Spin the wheel to allocate your prize!
                  </p>

                  {/* Roulette Graphic */}
                  <div className="relative w-48 h-48 mx-auto my-3 flex items-center justify-center">
                    <div 
                      className="w-full h-full rounded-full border-4 border-yellow-400 shadow-lg transition-transform ease-out flex items-center justify-center"
                      style={{ 
                        transform: `rotate(${wheelAngle}deg)`,
                        transitionDuration: isSpinning ? '3.0s' : '0s',
                        background: 'conic-gradient(#ef4444 0% 12.5%, #f59e0b 12.5% 25%, #10b981 25% 37.5%, #3b82f6 37.5% 50%, #8b5cf6 50% 62.5%, #ec4899 62.5% 75%, #06b6d4 75% 87.5%, #eab308 87.5% 100%)'
                      }}
                    >
                      <div className="w-16 h-16 rounded-full bg-slate-900 border-2 border-white flex items-center justify-center text-xl">
                        🎰
                      </div>
                    </div>
                    {/* Fixed Pointer */}
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 text-2xl filter drop-shadow">
                      🔻
                    </div>
                  </div>

                  <button
                    onClick={handleSpin}
                    disabled={isSpinning}
                    className="w-full py-3 bg-gradient-to-r from-amber-500 to-yellow-400 hover:from-amber-600 hover:to-yellow-500 text-black font-black text-sm rounded-lg shadow-lg cursor-pointer transform hover:scale-102 transition-all uppercase tracking-wider"
                  >
                    {isSpinning ? 'SPINNING WHEEL... PRAY TO GABEN!' : '🎲 SPIN THE WHEEL FOR FREE!'}
                  </button>
                </div>
              )}

              {/* STAGE 2: IMPOSSIBLE HUMAN CAPTCHA */}
              {step === 2 && (
                <div className="space-y-4">
                  <div className="inline-block bg-yellow-400 text-black font-black text-xs px-3 py-1 rounded-full uppercase tracking-widest">
                    STEP 2 OF 5: ROBOT BOT FILTER (CAPTCHA)
                  </div>
                  <h3 className="text-lg font-black text-yellow-300">
                    SELECT ALL BANANA HOLOGRAMS THAT ARE TELEPHONES:
                  </h3>
                  <p className="text-xs text-slate-300">
                    To prevent Russian botnets from taking your {activeAd.prizeName}, please click the correct tiles:
                  </p>

                  {/* 3x3 Grid Captcha */}
                  <div className="grid grid-cols-3 gap-2 max-w-xs mx-auto my-3">
                    {['🍌', '📞', '🍌', '🐸', '🍌', '💾', '🍌', '🍔', '🍌'].map((emoji, idx) => {
                      const isSelected = selectedCaptcha.includes(idx);
                      return (
                        <button
                          key={idx}
                          type="button"
                          onClick={() => {
                            if (isSelected) {
                              setSelectedCaptcha((prev) => prev.filter((i) => i !== idx));
                            } else {
                              setSelectedCaptcha((prev) => [...prev, idx]);
                            }
                          }}
                          className={`h-20 rounded-lg text-3xl flex items-center justify-center border-2 transition-all cursor-pointer ${
                            isSelected 
                              ? 'bg-yellow-400/30 border-yellow-400 scale-95 shadow-[0_0_15px_rgba(250,204,21,0.6)]' 
                              : 'bg-slate-800 border-slate-700 hover:border-slate-500'
                          }`}
                        >
                          {emoji}
                        </button>
                      );
                    })}
                  </div>

                  <button
                    onClick={handleCaptchaSubmit}
                    className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-lg uppercase tracking-wider cursor-pointer shadow"
                  >
                    VERIFY HUMAN TELEPHONE STATUS &gt;&gt;
                  </button>
                </div>
              )}

              {/* STAGE 3: QUICK CYBER QUIZ */}
              {step === 3 && (
                <div className="space-y-4">
                  <div className="inline-block bg-yellow-400 text-black font-black text-xs px-3 py-1 rounded-full uppercase tracking-widest">
                    STEP 3 OF 5: SYSTEM ELIGIBILITY SURVEY
                  </div>
                  <h3 className="text-base font-black text-yellow-300">
                    WHICH STATEMENT BEST DESCRIBES YOUR CURRENT GAMING RIG?
                  </h3>
                  <p className="text-xs text-slate-300">
                    Survey helps configure delivery bandwidth for {activeAd.prizeName}:
                  </p>

                  <div className="space-y-2 max-w-sm mx-auto text-left">
                    {[
                      'A) I have 128GB of cloud RAM downloaded from GeronimoHQ.',
                      'B) My CS2 runs at 800 FPS using direct Direct-Flip optimizations.',
                      'C) I unboxed an AWP Dragon Lore during my lunch break.',
                      'D) All of the above, plus I listen to Banana Phone on 24/7 loop.'
                    ].map((opt, i) => (
                      <button
                        key={i}
                        onClick={() => handleQuizSubmit(i)}
                        className={`w-full p-2.5 rounded-lg border text-xs font-semibold transition-all cursor-pointer text-left ${
                          quizAnswer === i 
                            ? 'bg-emerald-600 border-emerald-400 text-white' 
                            : 'bg-slate-800 border-slate-700 hover:border-yellow-400 text-slate-200'
                        }`}
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* STAGE 4: FAKE LOADING & INJECTION */}
              {step === 4 && (
                <div className="space-y-4 py-4">
                  <div className="inline-block bg-yellow-400 text-black font-black text-xs px-3 py-1 rounded-full uppercase tracking-widest">
                    STEP 4 OF 5: ENCRYPTING PRIZE DISPATCH
                  </div>
                  <h3 className="text-lg font-black text-yellow-300">
                    CALIBRATING QUANTUM CLOUD PIPELINE...
                  </h3>
                  <p className="text-xs text-slate-300">
                    Binding {activeAd.prizeName} directly to your Windows hardware ID...
                  </p>

                  <div className="max-w-md mx-auto my-3 p-3 bg-black rounded-lg border border-slate-700 text-left font-mono text-[10px] text-green-400 space-y-1">
                    <div>&gt; CONNECTING: srv-74.91.124.21.gflclan.com... OK</div>
                    <div>&gt; INJECTING: zero_latency_driver_x64.sys... OK</div>
                    <div>&gt; BYPASSING: Steam Trade Hold Cooldown... BYPASSED!</div>
                    <div>&gt; COMPRESSING: 1,000,000 banana megabytes... [{calibratingProgress}%]</div>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-slate-800 rounded-full h-4 overflow-hidden border border-slate-700 p-0.5">
                    <div 
                      className="bg-gradient-to-r from-yellow-400 to-emerald-400 h-full rounded-full transition-all duration-300"
                      style={{ width: `${calibratingProgress}%` }}
                    />
                  </div>
                  <div className="text-xs font-mono text-yellow-300">
                    STATUS: {calibratingProgress}% COMPLETE (DO NOT CLOSE THIS TAB)
                  </div>
                </div>
              )}

              {/* STAGE 5: FINAL TROLL CLAIM */}
              {step === 5 && (
                <div className="space-y-4 py-2 animate-bounce-subtle">
                  <div className="inline-block bg-emerald-500 text-black font-black text-xs px-3 py-1 rounded-full uppercase tracking-widest">
                    🎉 PRIZE CLAIM READY // 100% CERTIFIED
                  </div>
                  <h3 className="text-2xl font-black text-yellow-300">
                    CONGRATULATIONS!
                  </h3>
                  <p className="text-xs text-slate-200">
                    You survived all scam hurdles! Your <strong className="text-emerald-400">{activeAd.prizeName}</strong> has been saved under your session clearance frequency.
                  </p>

                  <div className="p-3.5 bg-yellow-400/10 border-2 border-yellow-400 rounded-xl space-y-1">
                    <div className="text-xs font-mono text-yellow-300 font-bold">
                      REDEEM CODE: <span className="text-white bg-black px-2 py-0.5 rounded border border-yellow-400">GERONIMO-BANANA-420-CS2</span>
                    </div>
                    <div className="text-[10px] text-slate-400">
                      Take this code to the RAM Holo-Chamber or the Secret Vault to finalize dispatch!
                    </div>
                  </div>

                  <button
                    onClick={handleClaimFinalPrize}
                    className="w-full py-3 bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white font-black text-sm rounded-lg shadow-lg cursor-pointer transform hover:scale-102 transition-all uppercase tracking-wider"
                  >
                    🚀 DOWNLOAD FREE RAM & SEAL PRIZE NOW!
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
