import React, { useState } from 'react';
import { Dices, Trophy } from 'lucide-react';
import confetti from 'canvas-confetti';

interface Achievement {
  title: string;
  desc: string;
  icon: string;
}

export const ChaosAnomalyEngine: React.FC = () => {
  const [achievementData, setAchievementData] = useState<Achievement | null>(null);
  const [flashbang, setFlashbang] = useState(false);
  const [matrixGlitch, setMatrixGlitch] = useState(false);
  const [barrelRoll, setBarrelRoll] = useState(false);
  const [earthquake, setEarthquake] = useState(false);
  const [rainbowRave, setRainbowRave] = useState(false);
  const [bsodScare, setBsodScare] = useState(false);
  const [invertedDimension, setInvertedDimension] = useState(false);
  const [negevTracers, setNegevTracers] = useState<Array<{ id: number; top: number; delay: number; color: string }>>([]);
  const [fallingItems, setFallingItems] = useState<Array<{ id: number; left: number; emoji: string; duration: number }>>([]);
  const [toastBanner, setToastBanner] = useState<string | null>(null);

  // Play Web Audio synths
  const playChaosSynth = (type: 'gun' | 'achievement' | 'flash' | 'rave' | 'earthquake' | 'airhorn' | 'bsod' | 'coin') => {
    try {
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof window.AudioContext }).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();

      if (type === 'gun') {
        for (let i = 0; i < 10; i++) {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(130 - i * 6, ctx.currentTime + i * 0.07);
          gain.gain.setValueAtTime(0.18, ctx.currentTime + i * 0.07);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.07 + 0.06);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(ctx.currentTime + i * 0.07);
          osc.stop(ctx.currentTime + i * 0.07 + 0.07);
        }
      } else if (type === 'achievement') {
        [440, 554.37, 659.25, 880, 1108.73].forEach((f, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(f, ctx.currentTime + idx * 0.09);
          gain.gain.setValueAtTime(0.18, ctx.currentTime + idx * 0.09);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + idx * 0.09 + 0.35);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(ctx.currentTime + idx * 0.09);
          osc.stop(ctx.currentTime + idx * 0.09 + 0.4);
        });
      } else if (type === 'flash') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(3200, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(700, ctx.currentTime + 1.4);
        gain.gain.setValueAtTime(0.2, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.6);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 1.6);
      } else if (type === 'rave') {
        [220, 330, 440, 660, 550, 880, 1100].forEach((f, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(f, ctx.currentTime + idx * 0.08);
          gain.gain.setValueAtTime(0.14, ctx.currentTime + idx * 0.08);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + idx * 0.08 + 0.1);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(ctx.currentTime + idx * 0.08);
          osc.stop(ctx.currentTime + idx * 0.08 + 0.12);
        });
      } else if (type === 'earthquake') {
        // Low rumble sub-bass
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(55, ctx.currentTime);
        osc.frequency.linearRampToValueAtTime(35, ctx.currentTime + 1.8);
        gain.gain.setValueAtTime(0.28, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 2.0);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 2.0);
      } else if (type === 'airhorn') {
        // Triple MLG Airhorn chords
        const blasts = [0, 0.15, 0.35];
        blasts.forEach((delay) => {
          [466.16, 622.25, 932.33].forEach((f) => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(f, ctx.currentTime + delay);
            gain.gain.setValueAtTime(0.12, ctx.currentTime + delay);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + delay + 0.25);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(ctx.currentTime + delay);
            osc.stop(ctx.currentTime + delay + 0.26);
          });
        });
      } else if (type === 'bsod') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(150, ctx.currentTime);
        gain.gain.setValueAtTime(0.25, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.6);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.6);
      } else if (type === 'coin') {
        [987.77, 1318.51].forEach((f, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(f, ctx.currentTime + idx * 0.08);
          gain.gain.setValueAtTime(0.15, ctx.currentTime + idx * 0.08);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + idx * 0.08 + 0.25);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(ctx.currentTime + idx * 0.08);
          osc.stop(ctx.currentTime + idx * 0.08 + 0.3);
        });
      }
    } catch {
      // AudioContext unavailable
    }
  };

  const ACHIEVEMENTS_POOL: Achievement[] = [
    {
      title: 'Downloaded 512GB of Cloud RAM',
      desc: 'Occupied all memory channels without triggering Windows Task Manager panic.',
      icon: '💾'
    },
    {
      title: 'Cybo Laser Ankle Breaker',
      desc: 'Jumped over the bottom laser, only to hit your forehead on the top laser.',
      icon: '⚡'
    },
    {
      title: 'Banana Hotline 24/7 Operator',
      desc: 'Kept Banana Phone looping on loop for 3 hours straight across global ZE servers.',
      icon: '🍌'
    },
    {
      title: 'Negev 150-Round Suppressor',
      desc: 'Never released mouse1 through the entirety of a 64-player Zombie Escape round.',
      icon: '🔫'
    },
    {
      title: 'Direct-Flip Speedrunner',
      desc: 'Achieved true zero-latency Alt-Tab in CS2 using Command Center tweaks.',
      icon: '🚀'
    },
    {
      title: 'Mako Reactor Reactor Meltdown Survivor',
      desc: 'Reached elevator with 0.4 seconds remaining while zombies clogged the doorway.',
      icon: '☢️'
    },
    {
      title: 'Gaben Blessing Bestowed',
      desc: 'Unboxed a holographic sticker and traded it for a lifetime supply of pizza.',
      icon: '👑'
    },
    {
      title: 'Pepe Synthwave Connoisseur',
      desc: 'Felt the 1.16x master bass reverberate through your motherboard.',
      icon: '🐸'
    },
    {
      title: 'Sub-Tick Quantum Whisperer',
      desc: 'Fired an AWP shot that registered yesterday.',
      icon: '🎯'
    },
    {
      title: 'Secret Vault Breaker',
      desc: 'Discovered the forbidden binds inside the Level-5 Geronimo Vault.',
      icon: '🔓'
    }
  ];

  const triggerRandomChaos = () => {
    const events = [
      'barrel_roll',
      'earthquake',
      'rainbow_rave',
      'bsod_scare',
      'pepe_banana_swarm',
      'confetti_nuke',
      'airhorn',
      'inverted_dimension',
      'negev',
      'achievement',
      'glitch',
      'flashbang'
    ];
    const chosen = events[Math.floor(Math.random() * events.length)];

    if (chosen === 'barrel_roll') {
      playChaosSynth('rave');
      setBarrelRoll(true);
      setToastBanner('🌀 BARREL ROLL ANOMALY ACTIVATED (360° VIEWPORT ROTATION)!');
      setTimeout(() => {
        setBarrelRoll(false);
        setToastBanner(null);
      }, 3000);
    } else if (chosen === 'earthquake') {
      playChaosSynth('earthquake');
      setEarthquake(true);
      setToastBanner('🌋 ZE EARTHQUAKE SIMULATION // SHAKING HOLO-CHAMBER!');
      setTimeout(() => {
        setEarthquake(false);
        setToastBanner(null);
      }, 2500);
    } else if (chosen === 'rainbow_rave') {
      playChaosSynth('rave');
      setRainbowRave(true);
      setToastBanner('🌈 RAINBOW RAVE PROTOCOL // FULL HUE-ROTATE ENGAGED!');
      setTimeout(() => {
        setRainbowRave(false);
        setToastBanner(null);
      }, 3500);
    } else if (chosen === 'bsod_scare') {
      playChaosSynth('bsod');
      setBsodScare(true);
      setTimeout(() => {
        setBsodScare(false);
        playChaosSynth('coin');
      }, 2400);
    } else if (chosen === 'inverted_dimension') {
      playChaosSynth('flash');
      setInvertedDimension(true);
      setToastBanner('⚡ INVERTED DIMENSION // REVERSE PHOSPHOR MATRIX!');
      setTimeout(() => {
        setInvertedDimension(false);
        setToastBanner(null);
      }, 2800);
    } else if (chosen === 'airhorn') {
      playChaosSynth('airhorn');
      setToastBanner('🎺 MLG TRIPLE AIRHORN BLAST // 360 NO SCOPE READY!');
      confetti({
        particleCount: 70,
        spread: 80,
        origin: { y: 0.8 },
        colors: ['#ef4444', '#f59e0b', '#3b82f6']
      });
      setTimeout(() => setToastBanner(null), 3000);
    } else if (chosen === 'confetti_nuke') {
      playChaosSynth('achievement');
      setToastBanner('🎉 MAXIMUM CONFETTI NUKE DETONATED OVER GERONIMOHQ!');
      for (let i = 0; i < 4; i++) {
        setTimeout(() => {
          confetti({
            particleCount: 60,
            angle: 60 + i * 30,
            spread: 70,
            origin: { x: 0.2 + i * 0.2, y: 0.7 },
            colors: ['#ffe600', '#f59e0b', '#00ffcc', '#ff007f']
          });
        }, i * 200);
      }
      setTimeout(() => setToastBanner(null), 3500);
    } else if (chosen === 'negev') {
      playChaosSynth('gun');
      const tracers = Array.from({ length: 40 }, (_, i) => ({
        id: i,
        top: Math.random() * 90 + 5,
        delay: Math.random() * 0.9,
        color: Math.random() < 0.5 ? '#10b981' : '#f43f5e'
      }));
      setNegevTracers(tracers);
      setToastBanner('🔫 NEGEV TRACER OVERLOAD // 150 BULLETS SPRAYED ACROSS SCREEN!');
      setTimeout(() => {
        setNegevTracers([]);
        setToastBanner(null);
      }, 3500);
    } else if (chosen === 'pepe_banana_swarm') {
      playChaosSynth('rave');
      const emojis = ['🍌', '🐸', '🚀', '💾', '💀', '🍔', '⚡', '👑', '🍕', '🎮'];
      const items = Array.from({ length: 50 }, (_, i) => ({
        id: i,
        left: Math.random() * 95,
        emoji: emojis[Math.floor(Math.random() * emojis.length)],
        duration: 1.8 + Math.random() * 2.2
      }));
      setFallingItems(items);
      setToastBanner('🍌🐸 PEPE & BANANA CHAOS SWARM FALLING FROM SKY!');
      setTimeout(() => {
        setFallingItems([]);
        setToastBanner(null);
      }, 4200);
    } else if (chosen === 'achievement') {
      playChaosSynth('achievement');
      const randAch = ACHIEVEMENTS_POOL[Math.floor(Math.random() * ACHIEVEMENTS_POOL.length)];
      setAchievementData(randAch);
      setTimeout(() => {
        setAchievementData(null);
      }, 5500);
    } else if (chosen === 'glitch') {
      playChaosSynth('gun');
      setMatrixGlitch(true);
      setTimeout(() => {
        setMatrixGlitch(false);
      }, 2500);
    } else if (chosen === 'flashbang') {
      playChaosSynth('flash');
      setFlashbang(true);
      setTimeout(() => {
        setFlashbang(false);
      }, 2600);
    }
  };

  return (
    <>
      {/* Floating Chaos Trigger Button (Bottom Right above footer) */}
      <div className="fixed bottom-6 right-6 z-40">
        <button
          onClick={triggerRandomChaos}
          className="group relative px-3.5 py-2.5 rounded-2xl bg-gradient-to-r from-fuchsia-600 via-purple-600 to-indigo-600 text-white font-cyber text-xs font-bold shadow-[0_0_25px_rgba(217,70,239,0.5)] hover:shadow-[0_0_35px_rgba(217,70,239,0.8)] border border-fuchsia-400/60 transition-all duration-300 hover:scale-105 active:scale-95 cursor-pointer flex items-center gap-2"
          title="Trigger a high-RNG chaotic anomaly across the website (Surprise Me!)"
        >
          <Dices className="w-4 h-4 text-yellow-300 group-hover:rotate-180 transition-transform duration-500" />
          <span className="hidden sm:inline tracking-wider">🎲 SURPRISE ME (CHAOS)</span>
          <span className="sm:hidden">🎲</span>
          <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-yellow-400 animate-ping" />
        </button>
      </div>

      {/* TOP TOAST BANNER FOR CURRENT ANOMALY */}
      {toastBanner && (
        <div className="fixed top-20 left-1/2 -translate-x-1/2 z-50 px-5 py-2 rounded-full bg-slate-950/95 border-2 border-fuchsia-400 text-yellow-300 font-cyber text-xs font-bold shadow-[0_0_30px_rgba(217,70,239,0.7)] animate-bounce select-none">
          {toastBanner}
        </div>
      )}

      {/* FULL VIEWPORT BARREL ROLL EFFECT */}
      {barrelRoll && (
        <style dangerouslySetInnerHTML={{ __html: `
          body {
            transition: transform 3s ease-in-out !important;
            transform: rotate(360deg) !important;
          }
        ` }} />
      )}

      {/* FULL VIEWPORT EARTHQUAKE SHAKE EFFECT */}
      {earthquake && (
        <style dangerouslySetInnerHTML={{ __html: `
          body {
            animation: earthquakeShake 0.12s infinite alternate !important;
          }
          @keyframes earthquakeShake {
            0% { transform: translate(3px, 2px) rotate(0.4deg); }
            50% { transform: translate(-3px, -2px) rotate(-0.4deg); }
            100% { transform: translate(2px, -3px) rotate(0.2deg); }
          }
        ` }} />
      )}

      {/* FULL VIEWPORT RAINBOW RAVE EFFECT */}
      {rainbowRave && (
        <style dangerouslySetInnerHTML={{ __html: `
          body {
            animation: rainbowHue 0.6s infinite linear !important;
          }
          @keyframes rainbowHue {
            0% { filter: hue-rotate(0deg); }
            100% { filter: hue-rotate(360deg); }
          }
        ` }} />
      )}

      {/* FULL VIEWPORT INVERTED DIMENSION */}
      {invertedDimension && (
        <style dangerouslySetInnerHTML={{ __html: `
          body {
            filter: invert(100%) hue-rotate(180deg) !important;
            transition: filter 0.3s ease !important;
          }
        ` }} />
      )}

      {/* FAKE BSOD ERROR SCARE */}
      {bsodScare && (
        <div className="fixed inset-0 z-[100] bg-[#0078d7] text-white p-8 sm:p-16 flex flex-col justify-center font-sans select-none animate-fadeIn">
          <div className="text-7xl sm:text-9xl font-light mb-6">:(</div>
          <h2 className="text-2xl sm:text-3xl font-light mb-4">
            Your PC ran into a problem and needs to restart. We're just collecting some error info, and then we'll restart for you.
          </h2>
          <div className="text-lg sm:text-xl font-light mb-8">
            100% complete
          </div>
          <div className="flex items-center gap-6 mt-4">
            <div className="w-24 h-24 bg-white text-black p-2 font-mono text-[9px] flex items-center justify-center text-center font-bold">
              [QR: GERONIMO-CS2]
            </div>
            <div className="text-xs sm:text-sm text-slate-200 font-mono space-y-1">
              <div>Stop code: CRITICAL_PROCESS_DIED_BANANA_OVERFLOW</div>
              <div>What failed: geronimohq_cloud_ram_x64.sys</div>
              <div>Just kidding! You survived the Surprise Me Anomaly! 🍌</div>
            </div>
          </div>
        </div>
      )}

      {/* NEGEV BULLET TRACERS OVERLAY */}
      {negevTracers.length > 0 && (
        <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
          {negevTracers.map((t) => (
            <div
              key={t.id}
              className="absolute h-0.5 rounded-full animate-tracer"
              style={{
                top: `${t.top}%`,
                left: '-10%',
                width: '120px',
                backgroundColor: t.color,
                boxShadow: `0 0 12px ${t.color}`,
                animationDelay: `${t.delay}s`,
                animationDuration: '0.6s'
              }}
            />
          ))}
        </div>
      )}

      {/* BANANA & PEPE GRAVITY RAIN OVERLAY */}
      {fallingItems.length > 0 && (
        <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
          {fallingItems.map((item) => (
            <div
              key={item.id}
              className="absolute text-3xl animate-fall"
              style={{
                top: '-50px',
                left: `${item.left}%`,
                animationDuration: `${item.duration}s`
              }}
            >
              {item.emoji}
            </div>
          ))}
        </div>
      )}

      {/* STEAM IN-GAME ACHIEVEMENT NOTIFICATION */}
      {achievementData && (
        <div className="fixed bottom-20 right-6 z-50 p-3.5 bg-gradient-to-r from-[#1b2838] to-[#171a21] border-2 border-[#66c0f4] rounded-xl shadow-[0_0_30px_rgba(102,192,244,0.4)] flex items-center gap-3 animate-slideInRight max-w-sm">
          <div className="w-12 h-12 rounded-lg bg-slate-900 border border-[#66c0f4]/50 flex items-center justify-center text-2xl flex-shrink-0">
            {achievementData.icon}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-1.5 text-[10px] font-code text-[#66c0f4] font-bold uppercase tracking-wider">
              <Trophy className="w-3 h-3" />
              <span>STEAM ACHIEVEMENT UNLOCKED</span>
            </div>
            <div className="font-cyber font-bold text-xs text-white truncate">
              {achievementData.title}
            </div>
            <div className="text-[10px] font-tech text-slate-300 leading-snug line-clamp-2">
              {achievementData.desc}
            </div>
          </div>
        </div>
      )}

      {/* FULL-SCREEN MATRIX GLITCH */}
      {matrixGlitch && (
        <div className="fixed inset-0 pointer-events-none z-50 bg-emerald-950/20 backdrop-invert-0 flex flex-col items-center justify-center animate-pulse">
          <div className="p-4 rounded-xl bg-slate-950/90 border border-emerald-400 text-emerald-400 font-code text-sm font-bold shadow-[0_0_30px_rgba(16,185,129,0.8)] text-center space-y-1">
            <div>⚡ [SYSTEM OVERRIDE] 1000 FPS OVERCLOCK INJECTED</div>
            <div className="text-xs text-slate-400">CYBERPUNK NEURAL SYNC ESTABLISHED</div>
          </div>
        </div>
      )}

      {/* FLASHBANG MEME */}
      {flashbang && (
        <div className="fixed inset-0 z-50 bg-white/95 transition-opacity duration-1000 flex items-center justify-center animate-fadeOut">
          <div className="text-slate-900 font-cyber font-black text-2xl tracking-widest animate-bounce">
            ⚠️ BLINDED BY TEAMMATE FLASHBANG ⚠️
          </div>
        </div>
      )}
    </>
  );
};
