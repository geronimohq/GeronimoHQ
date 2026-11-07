import React, { useState } from 'react';
import { Lock, Unlock, ShieldAlert, Sparkles, X, Terminal, Copy, Check, Volume2, Award, Zap, Skull, Cpu } from 'lucide-react';

interface SecretGeronimoVaultProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SecretGeronimoVault: React.FC<SecretGeronimoVaultProps> = ({ isOpen, onClose }) => {
  const [unlocked, setUnlocked] = useState(false);
  const [isHacking, setIsHacking] = useState(false);
  const [hackProgress, setHackProgress] = useState(0);
  const [passcode, setPasscode] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [copiedBind, setCopiedBind] = useState<string | null>(null);
  const [ramDownloaded, setRamDownloaded] = useState(false);
  const [activeTab, setActiveTab] = useState<'binds' | 'artifacts' | 'shame' | 'soundboard'>('artifacts');

  // Play synthetic Web Audio tones
  const playVaultSynth = (type: 'beep' | 'grant' | 'alarm' | 'bong' | 'banana') => {
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
      } else if (type === 'bong') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(140, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(60, ctx.currentTime + 0.8);
        gain.gain.setValueAtTime(0.3, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.2);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 1.2);
      } else if (type === 'banana') {
        [587.33, 659.25, 587.33, 440, 587.33].forEach((f, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(f, ctx.currentTime + idx * 0.12);
          gain.gain.setValueAtTime(0.12, ctx.currentTime + idx * 0.12);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + idx * 0.12 + 0.2);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(ctx.currentTime + idx * 0.12);
          osc.stop(ctx.currentTime + idx * 0.12 + 0.22);
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
    }, 140);
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
                  ? 'Welcome operative. All forbidden binds, memes, and golden artifacts decrypted.'
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
              <ShieldAlert className="w-12 h-12 text-red-400 animate-pulse" />
              <div className="absolute inset-0 rounded-full border-2 border-red-400 border-t-transparent animate-spin" />
            </div>

            <div className="max-w-md space-y-2">
              <h4 className="text-xl font-cyber font-bold text-red-300 tracking-wide">
                BIOMETRIC LASER SCANNER ACTIVE
              </h4>
              <p className="text-xs font-tech text-slate-300 leading-relaxed">
                You have stumbled into Geronimo's private sub-level quarantine chamber. Inside lies the forbidden
                Golden Banana, high-voltage CS2 bind aliases, and 512GB of illegal quantum RAM.
              </p>
            </div>

            {/* Error Message */}
            {errorMsg && (
              <div className="px-4 py-2 rounded-lg bg-red-950/80 border border-red-500/60 text-red-300 text-xs font-code font-bold animate-bounce">
                {errorMsg}
              </div>
            )}

            {/* Hacking Progress Bar */}
            {isHacking && (
              <div className="w-full max-w-sm space-y-1.5">
                <div className="flex justify-between text-[10px] font-code text-amber-300">
                  <span>OVERRIDING GFL MAIN-FIREWALL...</span>
                  <span>{hackProgress}%</span>
                </div>
                <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden border border-amber-500/40">
                  <div
                    className="h-full bg-gradient-to-r from-red-500 to-amber-400 transition-all duration-150"
                    style={{ width: `${hackProgress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Unlock Input / Buttons */}
            <div className="w-full max-w-md space-y-3 pt-2">
              <form onSubmit={handlePasscodeSubmit} className="flex gap-2">
                <input
                  type="text"
                  value={passcode}
                  onChange={(e) => setPasscode(e.target.value)}
                  placeholder="Enter Clearance Code (e.g. BANANA or 42069)..."
                  disabled={isHacking}
                  className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2 text-xs font-code text-white focus:outline-none focus:border-amber-400"
                />
                <button
                  type="submit"
                  disabled={isHacking}
                  className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-cyber font-bold text-xs rounded-xl shadow-[0_0_15px_rgba(251,191,36,0.4)] transition-all cursor-pointer disabled:opacity-50"
                >
                  AUTHENTICATE
                </button>
              </form>

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
                  <span>BRUTE-FORCE HACK</span>
                </button>

                <button
                  onClick={() => {
                    setPasscode('BANANA');
                    setUnlocked(true);
                    playVaultSynth('banana');
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

            {/* TAB 1: MYTHIC ARTIFACTS */}
            {activeTab === 'artifacts' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Artifact 1: Golden Banana */}
                <div className="p-4 rounded-xl bg-gradient-to-br from-amber-950/70 to-slate-950 border border-yellow-400/60 shadow-[0_0_20px_rgba(250,204,21,0.2)] space-y-2.5">
                  <div className="flex items-center justify-between">
                    <span className="text-2xl animate-bounce">🍌</span>
                    <span className="text-[9px] font-code px-2 py-0.5 rounded bg-yellow-400/20 text-yellow-300 font-bold border border-yellow-400/40">
                      TIER 100 // LEGENDARY
                    </span>
                  </div>
                  <h5 className="font-cyber font-black text-amber-300 text-sm">
                    THE GOLDEN BANANA OF CYBO LASER MASTERY
                  </h5>
                  <p className="text-xs font-tech text-slate-300 leading-relaxed">
                    Forged in the heart of Mako Reactor Core #7. Legend says holding this gives +3000 Bhop velocity
                    and guarantees you will never trip on laser floor hazards.
                  </p>
                  <button
                    onClick={() => playVaultSynth('banana')}
                    className="w-full py-1.5 bg-yellow-400 hover:bg-yellow-300 text-slate-950 font-code font-bold text-xs rounded-lg transition-colors cursor-pointer"
                  >
                    PLAY BANANA PHONIC CHIME 🍌
                  </button>
                </div>

                {/* Artifact 2: 512GB Quantum RAM Download */}
                <div className="p-4 rounded-xl bg-gradient-to-br from-fuchsia-950/70 to-slate-950 border border-fuchsia-500/60 shadow-[0_0_20px_rgba(255,0,127,0.2)] space-y-2.5">
                  <div className="flex items-center justify-between">
                    <Cpu className="w-6 h-6 text-fuchsia-400 animate-spin" />
                    <span className="text-[9px] font-code px-2 py-0.5 rounded bg-fuchsia-400/20 text-fuchsia-300 font-bold border border-fuchsia-400/40">
                      FORBIDDEN MEMORY
                    </span>
                  </div>
                  <h5 className="font-cyber font-black text-fuchsia-300 text-sm">
                    512GB QUANTUM CLOUD RAM (9000MHz OC)
                  </h5>
                  <p className="text-xs font-tech text-slate-300 leading-relaxed">
                    Overclocked by Geronimo's personal cooling reactor. Download directly into your browser's neural
                    buffer to experience zero micro-stutters forever.
                  </p>
                  <button
                    onClick={() => {
                      setRamDownloaded(true);
                      playVaultSynth('grant');
                      setTimeout(() => setRamDownloaded(false), 4000);
                    }}
                    className="w-full py-1.5 bg-fuchsia-600 hover:bg-fuchsia-500 text-white font-code font-bold text-xs rounded-lg transition-colors cursor-pointer"
                  >
                    {ramDownloaded ? '⚡ 512GB INJECTED TO CHROME BUFFER!' : '💾 DOWNLOAD 512GB QUANTUM RAM'}
                  </button>
                </div>
              </div>
            )}

            {/* TAB 2: SECRET PRO BINDS */}
            {activeTab === 'binds' && (
              <div className="space-y-3">
                <p className="text-xs text-slate-400 font-code">
                  Exclusive config binds used by veteran Zombie Escape runners. Click any command to copy instantly:
                </p>

                {[
                  {
                    id: 'b1',
                    title: 'Boss Laser Audio Duck + Panic Voice Mute (F7 & F8)',
                    desc: 'Instantly drops master sound to 20% so you can hear boss telegraph sounds over 64 shouting players.',
                    cmd: 'alias "duck_boss" "volume 0.20; voice_modenable 0; echo [BOSS] Audio Ducked!"; alias "unduck_boss" "volume 1.0; voice_modenable 1; echo [NORMAL] Audio Restored!"; bind "f7" "duck_boss"; bind "f8" "unduck_boss"'
                  },
                  {
                    id: 'b2',
                    title: 'Low-Viewmodel Laser Jump Crouch (FOV 68, Z -2)',
                    desc: 'Minimizes your first-person gun model down into the bottom corner so the entire floor laser field is visible.',
                    cmd: 'viewmodel_fov 68; viewmodel_offset_x 2.5; viewmodel_offset_y 2; viewmodel_offset_z -2; r_drawtracers_firstperson 0'
                  },
                  {
                    id: 'b3',
                    title: 'Banana Phone Hotline Broadcast Bind',
                    desc: 'Plays a radio UI chirp and broadcasts moral support to your entire team.',
                    cmd: 'bind "mouse4" "say 🍌 RING RING RING RING RING RING RING BANANA PHONE! (geronimohq.com); play sounds/ui/beep22"'
                  },
                  {
                    id: 'b4',
                    title: 'Emergency 180° Zombie Turn & Knife Dash',
                    desc: 'Instant 180 turn macro for dodging Mother Zombie knife attacks.',
                    cmd: 'alias "+quick180" "yaw 36000 1 0"; alias "-quick180" "yaw 0 1 0"; bind "mouse5" "+quick180"'
                  }
                ].map((b) => (
                  <div key={b.id} className="p-3 bg-slate-900/90 border border-slate-800 rounded-xl space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-cyber font-bold text-xs text-cyan-300">{b.title}</span>
                      <button
                        onClick={() => handleCopyBind(b.cmd, b.id)}
                        className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded text-[10px] font-code flex items-center gap-1 transition-colors cursor-pointer"
                      >
                        {copiedBind === b.id ? (
                          <>
                            <Check className="w-3 h-3 text-emerald-400" />
                            <span className="text-emerald-400">COPIED!</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3" />
                            <span>COPY BIND</span>
                          </>
                        )}
                      </button>
                    </div>
                    <p className="text-[11px] font-tech text-slate-400">{b.desc}</p>
                    <code className="block p-2 bg-slate-950 text-slate-300 text-[10px] font-code rounded border border-slate-800/80 break-all select-all">
                      {b.cmd}
                    </code>
                  </div>
                ))}
              </div>
            )}

            {/* TAB 3: ZE HALL OF SHAME */}
            {activeTab === 'shame' && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {[
                  {
                    name: 'The Door Hugger',
                    crime: 'Stood in the blast door and blocked 45 teammates from evacuating.',
                    rank: 'Rank: 💀 Certified Grief',
                    badge: 'DOOR BLOCKED'
                  },
                  {
                    name: 'The Floor Inspector',
                    crime: 'Jumped early on the low laser and ducked under the high laser.',
                    rank: 'Rank: 🩸 First Blood',
                    badge: 'LASER DIVE'
                  },
                  {
                    name: 'The AFK Mother Zombie',
                    crime: 'Spawned as first infected zombie, immediately alt-tabbed to order Uber Eats.',
                    rank: 'Rank: 🍔 0 Infections',
                    badge: 'FREE ESCAPE'
                  }
                ].map((s, i) => (
                  <div key={i} className="p-3 bg-slate-900/80 border border-red-500/30 rounded-xl space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-cyber font-bold text-red-300">{s.name}</span>
                      <span className="text-[8px] font-code px-1.5 py-0.5 rounded bg-red-950 text-red-400 border border-red-500/40 font-bold">
                        {s.badge}
                      </span>
                    </div>
                    <p className="text-[11px] font-tech text-slate-400 leading-snug">{s.crime}</p>
                    <div className="text-[10px] font-code text-amber-400 font-bold">{s.rank}</div>
                  </div>
                ))}
              </div>
            )}

            {/* TAB 4: MEME SOUNDBOARD */}
            {activeTab === 'soundboard' && (
              <div className="space-y-3">
                <p className="text-xs text-slate-400 font-code">
                  Zero external files — generated live via Web Audio oscillator chips:
                </p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                  <button
                    onClick={() => playVaultSynth('banana')}
                    className="p-3 rounded-xl bg-amber-950/60 hover:bg-amber-900/80 border border-yellow-400/40 text-yellow-300 font-cyber text-xs font-bold transition-all cursor-pointer flex flex-col items-center gap-1.5"
                  >
                    <span className="text-xl">🍌</span>
                    <span>BANANA TONES</span>
                  </button>

                  <button
                    onClick={() => playVaultSynth('grant')}
                    className="p-3 rounded-xl bg-emerald-950/60 hover:bg-emerald-900/80 border border-emerald-400/40 text-emerald-300 font-cyber text-xs font-bold transition-all cursor-pointer flex flex-col items-center gap-1.5"
                  >
                    <Sparkles className="w-5 h-5 text-emerald-400" />
                    <span>SYNTH TRIUMPH</span>
                  </button>

                  <button
                    onClick={() => playVaultSynth('bong')}
                    className="p-3 rounded-xl bg-purple-950/60 hover:bg-purple-900/80 border border-purple-400/40 text-purple-300 font-cyber text-xs font-bold transition-all cursor-pointer flex flex-col items-center gap-1.5"
                  >
                    <span className="text-xl">🔔</span>
                    <span>TACO BELL BONG</span>
                  </button>

                  <button
                    onClick={() => playVaultSynth('alarm')}
                    className="p-3 rounded-xl bg-red-950/60 hover:bg-red-900/80 border border-red-400/40 text-red-300 font-cyber text-xs font-bold transition-all cursor-pointer flex flex-col items-center gap-1.5"
                  >
                    <ShieldAlert className="w-5 h-5 text-red-400 animate-spin" />
                    <span>BOSS LASER SIREN</span>
                  </button>
                </div>
              </div>
            )}

            {/* Relock Button */}
            <div className="pt-3 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => {
                  setUnlocked(false);
                  playVaultSynth('alarm');
                }}
                className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-red-950 text-slate-400 hover:text-red-300 text-xs font-code border border-slate-800 hover:border-red-500/50 transition-colors cursor-pointer"
              >
                🔒 RELOCK SECURITY VAULT
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
