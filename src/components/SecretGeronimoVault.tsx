import React, { useState } from 'react';
import { 
  Lock, 
  Unlock, 
  ShieldAlert, 
  X, 
  Terminal, 
  Copy, 
  Check, 
  Volume2, 
  Award, 
  Zap, 
  Skull, 
  Dices, 
  Gift
} from 'lucide-react';
import { safeConfetti } from '../utils/motion';

interface SecretGeronimoVaultProps {
  isOpen: boolean;
  onClose: () => void;
}

interface VaultLootDrop {
  name: string;
  tier: 'COMMON' | 'RARE' | 'EPIC' | 'LEGENDARY' | 'MYTHIC';
  desc: string;
  icon: string;
  odds: string;
  borderColor: string;
  textColor: string;
  badgeBg: string;
}

const VAULT_LOOT_TABLE: VaultLootDrop[] = [
  // COMMON (40%)
  {
    name: '1x Pixel Banana Peel',
    tier: 'COMMON',
    desc: 'Mildly slippery. Gives +1 velocity when stepped on in Zombie Escape.',
    icon: '🍌',
    odds: '40%',
    borderColor: 'border-slate-600',
    textColor: 'text-slate-300',
    badgeBg: 'bg-slate-700 text-slate-200'
  },
  {
    name: 'Default Source 2 Smoke Grenade',
    tier: 'COMMON',
    desc: 'Volumetric, dynamic, and completely blocks the view of 60 zombies.',
    icon: '💨',
    odds: '40%',
    borderColor: 'border-slate-600',
    textColor: 'text-slate-300',
    badgeBg: 'bg-slate-700 text-slate-200'
  },
  {
    name: 'Empty Decoy Grenade Canister',
    tier: 'COMMON',
    desc: 'Makes loud fake gunfire sounds for 15 seconds to scare teammates.',
    icon: '🥫',
    odds: '40%',
    borderColor: 'border-slate-600',
    textColor: 'text-slate-300',
    badgeBg: 'bg-slate-700 text-slate-200'
  },
  {
    name: 'Used Windows Pagefile.sys Fragment',
    tier: 'COMMON',
    desc: 'Zero-overhead swap buffer evicted cleanly without hard page faults.',
    icon: '📄',
    odds: '40%',
    borderColor: 'border-slate-600',
    textColor: 'text-slate-300',
    badgeBg: 'bg-slate-700 text-slate-200'
  },
  {
    name: '120ms Routing Hop to Stockholm',
    tier: 'COMMON',
    desc: 'Adds a tiny regional scenic detour to your CS2 packet routing.',
    icon: '🌐',
    odds: '40%',
    borderColor: 'border-slate-600',
    textColor: 'text-slate-300',
    badgeBg: 'bg-slate-700 text-slate-200'
  },

  // RARE (30%)
  {
    name: 'Sub-Tick Packet Harmonizer',
    tier: 'RARE',
    desc: 'Aligns in-game user commands with server ticks for laser-precise hit registration.',
    icon: '🎯',
    odds: '30%',
    borderColor: 'border-blue-500',
    textColor: 'text-blue-300',
    badgeBg: 'bg-blue-600 text-white'
  },
  {
    name: '32GB Cloud RAM Direct Injector',
    tier: 'RARE',
    desc: 'Instantly inflates virtual memory without touching physical DDR5 chips.',
    icon: '💾',
    odds: '30%',
    borderColor: 'border-blue-500',
    textColor: 'text-blue-300',
    badgeBg: 'bg-blue-600 text-white'
  },
  {
    name: "Cybo's 3D Dimension Compass",
    tier: 'RARE',
    desc: 'Rotates camera angles 360 degrees around any ZE map thumbnail.',
    icon: '🧭',
    odds: '30%',
    borderColor: 'border-blue-500',
    textColor: 'text-blue-300',
    badgeBg: 'bg-blue-600 text-white'
  },
  {
    name: 'GFL FastDL Turbo Accelerator',
    tier: 'RARE',
    desc: 'Downloads 400MB custom ZE map assets in under 3.5 seconds.',
    icon: '⚡',
    odds: '30%',
    borderColor: 'border-blue-500',
    textColor: 'text-blue-300',
    badgeBg: 'bg-blue-600 text-white'
  },

  // EPIC (18%)
  {
    name: 'Stattrak Negev Loudness Multiplier',
    tier: 'EPIC',
    desc: 'Makes the 150-round continuous spray echo across the entire server.',
    icon: '🔫',
    odds: '18%',
    borderColor: 'border-purple-500',
    textColor: 'text-purple-300',
    badgeBg: 'bg-purple-600 text-white'
  },
  {
    name: 'Mako Reactor Meltdown Coolant Rod',
    tier: 'EPIC',
    desc: 'Stops Bahamut from casting Megaflare for 8 crucial escape seconds.',
    icon: '☢️',
    odds: '18%',
    borderColor: 'border-purple-500',
    textColor: 'text-purple-300',
    badgeBg: 'bg-purple-600 text-white'
  },
  {
    name: 'Infinite BHop Velocity Token',
    tier: 'EPIC',
    desc: 'Permits continuous scroll-wheel hops with zero stamina friction penalty.',
    icon: '🦘',
    odds: '18%',
    borderColor: 'border-purple-500',
    textColor: 'text-purple-300',
    badgeBg: 'bg-purple-600 text-white'
  },
  {
    name: 'Anti-Alt-Tab Display Presentation Relic',
    tier: 'EPIC',
    desc: 'Bypasses Windows Desktop Window Manager composition overhead permanently.',
    icon: '🚀',
    odds: '18%',
    borderColor: 'border-purple-500',
    textColor: 'text-purple-300',
    badgeBg: 'bg-purple-600 text-white'
  },

  // LEGENDARY (9%)
  {
    name: '24K Solid Gold Banana Phone Hotline',
    tier: 'LEGENDARY',
    desc: 'Forged from pure cyber-gold. Ring ring ring ring ring ring ring, BANANA PHONE!',
    icon: '🍌✨',
    odds: '9%',
    borderColor: 'border-amber-400',
    textColor: 'text-amber-300',
    badgeBg: 'bg-amber-500 text-black font-black'
  },
  {
    name: "Gaben's Blessed Souvenir Package #730",
    tier: 'LEGENDARY',
    desc: 'Guarantees Factory New exterior and zero scratches on your next case unbox.',
    icon: '👑',
    odds: '9%',
    borderColor: 'border-amber-400',
    textColor: 'text-amber-300',
    badgeBg: 'bg-amber-500 text-black font-black'
  },
  {
    name: "Queeniemella's Master Audio Tape (1.16x Loudness)",
    tier: 'LEGENDARY',
    desc: 'The complete uncut 3m16s lossless darksynth master recording.',
    icon: '📼',
    odds: '9%',
    borderColor: 'border-amber-400',
    textColor: 'text-amber-300',
    badgeBg: 'bg-amber-500 text-black font-black'
  },
  {
    name: "Pantcake's VPK Editor Master Key",
    tier: 'LEGENDARY',
    desc: 'Grants access to clean, non-corruptible custom CS2 client asset archives.',
    icon: '🗝️',
    odds: '9%',
    borderColor: 'border-amber-400',
    textColor: 'text-amber-300',
    badgeBg: 'bg-amber-500 text-black font-black'
  },

  // MYTHIC GOD TIER (3%)
  {
    name: '★ GERONIMO COMMAND CENTER ARCHITECT CROWN ★',
    tier: 'MYTHIC',
    desc: 'The ultimate badge of honor. Grants permanent VIP immortality across GeronimoHQ.',
    icon: '👑💎🔥',
    odds: '3%',
    borderColor: 'border-rose-500 animate-pulse',
    textColor: 'text-rose-300 font-black',
    badgeBg: 'bg-gradient-to-r from-red-600 to-fuchsia-600 text-white font-black'
  },
  {
    name: '★ 1000 FPS PERMANENT HARDWARE OVERCLOCK ★',
    tier: 'MYTHIC',
    desc: 'Freezes GPU junction temperature at 42°C forever with zero thermal throttling.',
    icon: '⚡🏎️💥',
    odds: '3%',
    borderColor: 'border-rose-500 animate-pulse',
    textColor: 'text-rose-300 font-black',
    badgeBg: 'bg-gradient-to-r from-rose-600 via-pink-600 to-purple-600 text-white font-black'
  }
];

export const SecretGeronimoVault: React.FC<SecretGeronimoVaultProps> = ({ isOpen, onClose }) => {
  const [unlocked, setUnlocked] = useState(false);
  const [isHacking, setIsHacking] = useState(false);
  const [hackProgress, setHackProgress] = useState(0);
  const [passcode, setPasscode] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [copiedBind, setCopiedBind] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'loot_rng' | 'artifacts' | 'binds' | 'shame' | 'soundboard'>('loot_rng');

  // RNG Loot Box State
  const [isRollingLoot, setIsRollingLoot] = useState(false);
  const [currentLootDrop, setCurrentLootDrop] = useState<VaultLootDrop | null>(null);
  const [rollCount, setRollCount] = useState(0);
  const [lootHistory, setLootHistory] = useState<VaultLootDrop[]>([]);

  // Play synthetic Web Audio tones
  const playVaultSynth = (type: 'beep' | 'grant' | 'alarm' | 'bong' | 'banana' | 'loot_roll' | 'loot_win') => {
    try {
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof window.AudioContext }).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();

      if (type === 'beep') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(440, ctx.currentTime);
        gain.gain.setValueAtTime(0.08, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.1);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.1);
      } else if (type === 'grant') {
        const freqs = [523.25, 659.25, 783.99, 1046.5];
        freqs.forEach((f, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(f, ctx.currentTime + idx * 0.08);
          gain.gain.setValueAtTime(0.12, ctx.currentTime + idx * 0.08);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + idx * 0.08 + 0.35);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(ctx.currentTime + idx * 0.08);
          osc.stop(ctx.currentTime + idx * 0.08 + 0.4);
        });
      } else if (type === 'alarm') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(300, ctx.currentTime);
        osc.frequency.linearRampToValueAtTime(600, ctx.currentTime + 0.2);
        osc.frequency.linearRampToValueAtTime(300, ctx.currentTime + 0.4);
        gain.gain.setValueAtTime(0.1, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.4);
      } else if (type === 'loot_roll') {
        for (let i = 0; i < 6; i++) {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(400 + i * 80, ctx.currentTime + i * 0.06);
          gain.gain.setValueAtTime(0.1, ctx.currentTime + i * 0.06);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.06 + 0.05);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(ctx.currentTime + i * 0.06);
          osc.stop(ctx.currentTime + i * 0.06 + 0.06);
        }
      } else if (type === 'loot_win') {
        [523.25, 659.25, 783.99, 1046.5, 1318.5].forEach((f, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(f, ctx.currentTime + idx * 0.08);
          gain.gain.setValueAtTime(0.18, ctx.currentTime + idx * 0.08);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + idx * 0.08 + 0.4);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(ctx.currentTime + idx * 0.08);
          osc.stop(ctx.currentTime + idx * 0.08 + 0.45);
        });
      }
    } catch {
      // AudioContext unavailable
    }
  };

  const handleBruteForce = () => {
    setIsHacking(true);
    setHackProgress(0);
    setErrorMsg(null);
    playVaultSynth('alarm');

    const interval = setInterval(() => {
      setHackProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsHacking(false);
          setUnlocked(true);
          playVaultSynth('grant');
          return 100;
        }
        playVaultSynth('beep');
        return prev + 15;
      });
    }, 120);
  };

  const handlePasscodeSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const clean = passcode.trim().toLowerCase();
    const validCodes = ['banana', 'geronimo', '42069', 'ze', 'cybo', 'gfl', 'pepe', '1337', 'secret'];

    if (validCodes.includes(clean) || clean.length >= 3) {
      setUnlocked(true);
      setErrorMsg(null);
      playVaultSynth('grant');
    } else {
      setErrorMsg('⚠️ ACCESS DENIED: Invalid clearance frequency. Try "BANANA", "GERONIMO", or Brute-Force!');
      playVaultSynth('alarm');
    }
  };

  const handleCopyBind = (cmd: string, id: string) => {
    navigator.clipboard.writeText(cmd);
    setCopiedBind(id);
    playVaultSynth('beep');
    setTimeout(() => setCopiedBind(null), 2500);
  };

  const handleRollLoot = () => {
    if (isRollingLoot) return;
    setIsRollingLoot(true);
    playVaultSynth('loot_roll');

    // Roll random index
    const randIdx = Math.floor(Math.random() * VAULT_LOOT_TABLE.length);
    const wonItem = VAULT_LOOT_TABLE[randIdx];

    setTimeout(() => {
      setIsRollingLoot(false);
      setCurrentLootDrop(wonItem);
      setRollCount((c) => c + 1);
      setLootHistory((prev) => [wonItem, ...prev.slice(0, 9)]);
      playVaultSynth('loot_win');

      if (wonItem.tier === 'LEGENDARY' || wonItem.tier === 'MYTHIC') {
        safeConfetti({
          particleCount: 100,
          spread: 80,
          origin: { y: 0.6 },
          colors: ['#ffe600', '#f59e0b', '#ec4899', '#3b82f6']
        });
      }
    }, 1200);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-950/85 backdrop-blur-md animate-fadeIn">
      {/* Outer Hologram Container */}
      <div
        className={`relative w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-2xl border transition-all duration-500 shadow-2xl flex flex-col ${
          unlocked
            ? 'bg-slate-950/95 border-amber-400/80 shadow-[0_0_50px_rgba(251,191,36,0.3)]'
            : 'bg-[#080b12]/95 border-red-500/70 shadow-[0_0_50px_rgba(239,68,68,0.3)]'
        }`}
      >
        {/* Top Header Bar */}
        <div
          className={`px-5 py-3.5 border-b flex items-center justify-between transition-colors ${
            unlocked
              ? 'bg-amber-950/40 border-amber-500/40'
              : 'bg-red-950/40 border-red-500/40'
          }`}
        >
          <div className="flex items-center gap-2.5">
            {unlocked ? (
              <Unlock className="w-5 h-5 text-amber-400 animate-bounce" />
            ) : (
              <Lock className="w-5 h-5 text-red-400 animate-pulse" />
            )}
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-cyber font-black text-sm sm:text-base tracking-wider text-white">
                  {unlocked
                    ? 'CLASSIFIED VAULT // CLEARED FOR GERONIMO V.I.P'
                    : 'CLASSIFIED GERONIMO VAULT // LEVEL-5 RESTRICTED'}
                </h3>
                <span
                  className={`text-[9px] font-code px-2 py-0.5 rounded font-bold uppercase ${
                    unlocked
                      ? 'bg-amber-400 text-slate-950 animate-pulse'
                      : 'bg-red-500/20 text-red-300 border border-red-500/50'
                  }`}
                >
                  {unlocked ? '🔓 ACCESS GRANTED' : '🔒 CLEARANCE LOCKED'}
                </span>
              </div>
              <p className="text-[10px] font-code text-slate-400">
                {unlocked
                  ? 'Welcome operative. All forbidden binds, RNG drops, and golden artifacts decrypted.'
                  : 'Encrypted under 4096-bit Pepe quantum cypher. Authorized entities only.'}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-400 hover:text-white transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* LOCKED STATE VIEW */}
        {!unlocked ? (
          <div className="p-6 flex flex-col items-center text-center space-y-6">
            <div className="w-24 h-24 rounded-full border-2 border-red-500/60 bg-red-950/30 flex items-center justify-center relative shadow-[0_0_30px_rgba(239,68,68,0.3)]">
              <ShieldAlert className="w-12 h-12 text-red-500 animate-pulse" />
              <div className="absolute inset-0 rounded-full border border-red-400 animate-ping opacity-25" />
            </div>

            <div className="max-w-md space-y-2">
              <h4 className="text-xl font-cyber font-bold text-red-400">
                ENTER CLEARANCE FREQUENCY
              </h4>
              <p className="text-xs text-slate-300 font-tech leading-relaxed">
                Vault contains classified CS2 binds, unreleased Banana Phone audio tapes, and high-frequency RNG relics. Enter your secret passcode or execute a brute-force bypass.
              </p>
            </div>

            {errorMsg && (
              <div className="p-3 rounded-lg bg-red-950/80 border border-red-500/80 text-red-300 text-xs font-code max-w-md animate-shake">
                {errorMsg}
              </div>
            )}

            {/* Passcode Form */}
            <form onSubmit={handlePasscodeSubmit} className="w-full max-w-sm space-y-3">
              <div className="relative">
                <input
                  type="text"
                  value={passcode}
                  onChange={(e) => setPasscode(e.target.value)}
                  placeholder="Enter passcode (e.g. BANANA or GERONIMO)"
                  disabled={isHacking}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700 text-white font-code text-sm placeholder:text-slate-500 focus:outline-none focus:border-amber-400 text-center tracking-wider"
                />
              </div>

              <button
                type="submit"
                disabled={isHacking}
                className="w-full py-2.5 bg-gradient-to-r from-amber-500 to-yellow-400 hover:from-amber-600 hover:to-yellow-500 text-slate-950 font-cyber font-bold text-xs rounded-xl shadow-[0_0_20px_rgba(251,191,36,0.4)] transition-all cursor-pointer"
              >
                AUTHORIZE ACCESS FREQUENCY
              </button>
            </form>

            {/* Hack & Bypass Buttons */}
            <div className="w-full max-w-sm space-y-2">
              <div className="flex items-center gap-2">
                <div className="flex-1 h-px bg-slate-800" />
                <span className="text-[10px] font-code text-slate-500 uppercase">OR BYPASS</span>
                <div className="flex-1 h-px bg-slate-800" />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={handleBruteForce}
                  disabled={isHacking}
                  className="px-3 py-2 bg-red-950/70 hover:bg-red-900/80 border border-red-500/50 hover:border-red-400 text-red-200 font-cyber text-xs rounded-xl transition-all cursor-pointer flex items-center justify-center gap-1.5"
                >
                  <Terminal className="w-3.5 h-3.5 text-red-400" />
                  <span>{isHacking ? `HACKING [${hackProgress}%]...` : "BRUTE-FORCE HACK"}</span>
                </button>

                <button
                  onClick={() => {
                    setPasscode('BANANA');
                    setUnlocked(true);
                    playVaultSynth('grant');
                  }}
                  disabled={isHacking}
                  className="px-3 py-2 bg-yellow-950/70 hover:bg-yellow-900/80 border border-yellow-400/50 hover:border-yellow-300 text-yellow-200 font-cyber text-xs rounded-xl transition-all cursor-pointer flex items-center justify-center gap-1.5"
                >
                  <span>🍌 BANANA PASSCODE</span>
                </button>
              </div>
            </div>
          </div>
        ) : (
          /* UNLOCKED VAULT CHAMBER */
          <div className="p-5 space-y-4">
            {/* Vault Tabs */}
            <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 pb-3">
              <button
                onClick={() => setActiveTab('loot_rng')}
                className={`px-3 py-1.5 rounded-lg text-xs font-cyber font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                  activeTab === 'loot_rng'
                    ? 'bg-amber-400 text-slate-950 shadow-[0_0_10px_rgba(251,191,36,0.4)]'
                    : 'bg-slate-900 text-slate-400 hover:text-white'
                }`}
              >
                <Dices className="w-3.5 h-3.5" />
                <span>🎲 ROLL VAULT LOOT (RNG)</span>
              </button>

              <button
                onClick={() => setActiveTab('artifacts')}
                className={`px-3 py-1.5 rounded-lg text-xs font-cyber font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                  activeTab === 'artifacts'
                    ? 'bg-amber-400 text-slate-950 shadow-[0_0_10px_rgba(251,191,36,0.4)]'
                    : 'bg-slate-900 text-slate-400 hover:text-white'
                }`}
              >
                <Award className="w-3.5 h-3.5" />
                <span>MYTHIC ARTIFACTS</span>
              </button>

              <button
                onClick={() => setActiveTab('binds')}
                className={`px-3 py-1.5 rounded-lg text-xs font-cyber font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                  activeTab === 'binds'
                    ? 'bg-amber-400 text-slate-950 shadow-[0_0_10px_rgba(251,191,36,0.4)]'
                    : 'bg-slate-900 text-slate-400 hover:text-white'
                }`}
              >
                <Zap className="w-3.5 h-3.5" />
                <span>SECRET PRO BINDS</span>
              </button>

              <button
                onClick={() => setActiveTab('shame')}
                className={`px-3 py-1.5 rounded-lg text-xs font-cyber font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                  activeTab === 'shame'
                    ? 'bg-amber-400 text-slate-950 shadow-[0_0_10px_rgba(251,191,36,0.4)]'
                    : 'bg-slate-900 text-slate-400 hover:text-white'
                }`}
              >
                <Skull className="w-3.5 h-3.5" />
                <span>ZE HALL OF SHAME</span>
              </button>

              <button
                onClick={() => setActiveTab('soundboard')}
                className={`px-3 py-1.5 rounded-lg text-xs font-cyber font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                  activeTab === 'soundboard'
                    ? 'bg-amber-400 text-slate-950 shadow-[0_0_10px_rgba(251,191,36,0.4)]'
                    : 'bg-slate-900 text-slate-400 hover:text-white'
                }`}
              >
                <Volume2 className="w-3.5 h-3.5" />
                <span>MEME SOUNDBOARD</span>
              </button>
            </div>

            {/* TAB: RNG LOOT BOX */}
            {activeTab === 'loot_rng' && (
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-gradient-to-r from-purple-950/60 to-slate-900 border border-purple-500/50 flex flex-col sm:flex-row items-center justify-between gap-4">
                  <div>
                    <h4 className="text-base font-cyber font-bold text-yellow-300 flex items-center gap-2">
                      <Gift className="w-4 h-4 text-purple-400" />
                      MYTHIC QUANTUM LOOT ROLLER // 25+ ITEMS
                    </h4>
                    <p className="text-xs text-slate-300 font-tech mt-0.5">
                      Roll for mythic CS2 artifacts, golden banana phones, and quantum cloud RAM relics!
                    </p>
                  </div>

                  <button
                    onClick={handleRollLoot}
                    disabled={isRollingLoot}
                    className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-yellow-400 hover:from-amber-600 hover:to-yellow-500 text-slate-950 font-cyber font-bold text-xs shadow-[0_0_20px_rgba(251,191,36,0.4)] transition-all cursor-pointer transform hover:scale-105 active:scale-95 flex items-center gap-2"
                  >
                    <Dices className={`w-4 h-4 ${isRollingLoot ? 'animate-spin' : ''}`} />
                    <span>{isRollingLoot ? 'ROLLING RNG CASING...' : '🎲 ROLL VAULT LOOT!'}</span>
                  </button>
                </div>

                {/* CURRENT DROP RESULT */}
                {currentLootDrop && (
                  <div className={`p-4 rounded-xl bg-slate-900/90 border-2 ${currentLootDrop.borderColor} shadow-lg space-y-2 animate-fadeIn`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-3xl">{currentLootDrop.icon}</span>
                        <div>
                          <div className={`font-cyber font-black text-sm sm:text-base ${currentLootDrop.textColor}`}>
                            {currentLootDrop.name}
                          </div>
                          <span className={`text-[9px] font-code px-2 py-0.5 rounded font-bold uppercase ${currentLootDrop.badgeBg}`}>
                            TIER: {currentLootDrop.tier} (ODDS: {currentLootDrop.odds})
                          </span>
                        </div>
                      </div>
                      <span className="text-xs font-mono text-slate-400">
                        Roll #{rollCount}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 font-tech">
                      {currentLootDrop.desc}
                    </p>
                  </div>
                )}

                {/* RECENT LOOT HISTORY */}
                {lootHistory.length > 0 && (
                  <div className="space-y-2">
                    <h5 className="text-[11px] font-cyber text-slate-400 uppercase tracking-wider">
                      RECENT LOOT INVENTORY (LAST 10 ROLLS)
                    </h5>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {lootHistory.map((item, idx) => (
                        <div key={idx} className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 flex items-center gap-2.5">
                          <span className="text-xl">{item.icon}</span>
                          <div className="flex-1 min-w-0">
                            <div className="text-xs font-cyber font-bold text-white truncate">
                              {item.name}
                            </div>
                            <span className="text-[9px] font-code text-slate-400">
                              {item.tier}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* TAB: MYTHIC ARTIFACTS */}
            {activeTab === 'artifacts' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-gradient-to-br from-amber-950/70 to-slate-950 border border-yellow-400/60 shadow-[0_0_20px_rgba(250,204,21,0.2)] space-y-2.5">
                  <div className="flex items-center justify-between">
                    <span className="text-2xl animate-bounce">🍌</span>
                    <span className="text-[9px] font-code px-2 py-0.5 rounded bg-yellow-400/20 text-yellow-300 font-bold border border-yellow-400/40">
                      TIER 100 // LEGENDARY
                    </span>
                  </div>
                  <h4 className="font-cyber font-bold text-sm text-yellow-300">
                    GOLDEN BANANA PHONE RELIC
                  </h4>
                  <p className="text-xs text-slate-300 font-tech">
                    Direct hotline to the Geronimo mothership. Rumored to decrease weapon spread by 0.0001% when equipped in primary weapon slot.
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-gradient-to-br from-emerald-950/70 to-slate-950 border border-emerald-500/60 shadow-[0_0_20px_rgba(16,185,129,0.2)] space-y-2.5">
                  <div className="flex items-center justify-between">
                    <span className="text-2xl">🐸</span>
                    <span className="text-[9px] font-code px-2 py-0.5 rounded bg-emerald-400/20 text-emerald-300 font-bold border border-emerald-400/40">
                      HOLOGRAM 07 // MYTHIC
                    </span>
                  </div>
                  <h4 className="font-cyber font-bold text-sm text-emerald-300">
                    SAD PEPE QUANTUM CORE
                  </h4>
                  <p className="text-xs text-slate-300 font-tech">
                    The emotional frequency resonator behind our retro synth engine. Sustains harmonic minor arpeggios at 128 BPM indefinitely.
                  </p>
                </div>
              </div>
            )}

            {/* TAB: SECRET PRO BINDS */}
            {activeTab === 'binds' && (
              <div className="space-y-3">
                {[
                  {
                    id: 'bhop-jump',
                    title: 'CLEAN DESUBTICK JUMP BIND',
                    cmd: 'alias "+myjump" "+jump"; alias "-myjump" "-jump"; bind "mwheeldown" "+myjump"',
                    desc: 'Crisp, responsive mousewheel jump for smooth bunnyhopping.'
                  },
                  {
                    id: 'clear-decals',
                    title: 'COMPACT RADAR ZOOM TOGGLE',
                    cmd: 'bind "v" "toggle cl_radar_scale 0.35 0.7"',
                    desc: 'Instantly toggles full-map radar view to track distant teammate pings.'
                  },
                  {
                    id: 'quick-drop',
                    title: 'FAST BOMB DROP BIND',
                    cmd: 'bind "c" "slot5; drop"',
                    desc: 'Instantly throws C4 to teammates without fumbling weapon slots.'
                  }
                ].map((b) => (
                  <div key={b.id} className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <h5 className="font-cyber text-xs font-bold text-amber-300">{b.title}</h5>
                      <button
                        onClick={() => handleCopyBind(b.cmd, b.id)}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white font-code text-[10px] flex items-center gap-1 cursor-pointer transition-colors"
                      >
                        {copiedBind === b.id ? (
                          <>
                            <Check className="w-3 h-3 text-emerald-400" />
                            <span className="text-emerald-400">COPIED</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3" />
                            <span>COPY BIND</span>
                          </>
                        )}
                      </button>
                    </div>
                    <code className="block p-2 rounded bg-black/80 text-[11px] font-code text-cyan-300 overflow-x-auto">
                      {b.cmd}
                    </code>
                    <p className="text-[11px] text-slate-400 font-tech">{b.desc}</p>
                  </div>
                ))}
              </div>
            )}

            {/* TAB: HALL OF SHAME */}
            {activeTab === 'shame' && (
              <div className="space-y-3">
                <div className="p-3.5 rounded-xl bg-red-950/40 border border-red-500/40 space-y-1">
                  <div className="flex items-center gap-2 text-xs font-cyber font-bold text-red-300">
                    <Skull className="w-4 h-4 text-red-400" />
                    <span>THE ZE_ATOS ELEVATOR INCIDENT (2025)</span>
                  </div>
                  <p className="text-xs text-slate-300 font-tech">
                    An unnamed VIP player pressed the elevator button with 59 teammates still running across the bridge. Immediate infected victory.
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-red-950/40 border border-red-500/40 space-y-1">
                  <div className="flex items-center gap-2 text-xs font-cyber font-bold text-red-300">
                    <Skull className="w-4 h-4 text-red-400" />
                    <span>THE MAKO REACTOR LASER OVER-JUMP</span>
                  </div>
                  <p className="text-xs text-slate-300 font-tech">
                    Jumped 3 centimeters too high over Sephiroth's middle laser, grazed forehead on the ceiling geometry, and turned into mother zombie.
                  </p>
                </div>
              </div>
            )}

            {/* TAB: MEME SOUNDBOARD */}
            {activeTab === 'soundboard' && (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {[
                  { name: '🍌 BANANA RING', fn: () => playVaultSynth('banana') },
                  { name: '🚨 RED ALERT', fn: () => playVaultSynth('alarm') },
                  { name: '🔔 QUANTUM CHIME', fn: () => playVaultSynth('grant') },
                  { name: '💨 SUB-BASS BONG', fn: () => playVaultSynth('bong') },
                  { name: '🤖 ACCESS KEY', fn: () => playVaultSynth('beep') }
                ].map((s, idx) => (
                  <button
                    key={idx}
                    onClick={s.fn}
                    className="p-3 rounded-xl bg-slate-900 border border-slate-700 hover:border-amber-400 text-white font-cyber text-xs flex flex-col items-center justify-center gap-2 cursor-pointer transition-all hover:scale-105 active:scale-95"
                  >
                    <Volume2 className="w-5 h-5 text-amber-400" />
                    <span>{s.name}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
