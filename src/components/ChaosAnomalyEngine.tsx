import React, { useState } from 'react';
import { Dices, Trophy } from 'lucide-react';

export const ChaosAnomalyEngine: React.FC = () => {
  const [achievementData, setAchievementData] = useState<{ title: string; desc: string; icon: string } | null>(null);
  const [flashbang, setFlashbang] = useState(false);
  const [matrixGlitch, setMatrixGlitch] = useState(false);
  const [negevTracers, setNegevTracers] = useState<Array<{ id: number; top: number; delay: number; color: string }>>([]);
  const [fallingItems, setFallingItems] = useState<Array<{ id: number; left: number; emoji: string; duration: number }>>([]);

  const playSynth = (type: 'gun' | 'achievement' | 'flash' | 'rave' | 'laser') => {
    try {
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof window.AudioContext }).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();

      if (type === 'gun') {
        for (let i = 0; i < 8; i++) {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(120 - i * 5, ctx.currentTime + i * 0.08);
          gain.gain.setValueAtTime(0.15, ctx.currentTime + i * 0.08);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.08 + 0.07);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(ctx.currentTime + i * 0.08);
          osc.stop(ctx.currentTime + i * 0.08 + 0.08);
        }
      } else if (type === 'achievement') {
        [440, 554.37, 659.25, 880].forEach((f, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(f, ctx.currentTime + idx * 0.1);
          gain.gain.setValueAtTime(0.15, ctx.currentTime + idx * 0.1);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + idx * 0.1 + 0.3);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(ctx.currentTime + idx * 0.1);
          osc.stop(ctx.currentTime + idx * 0.1 + 0.35);
        });
      } else if (type === 'flash') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(3000, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(800, ctx.currentTime + 1.2);
        gain.gain.setValueAtTime(0.18, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.5);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 1.5);
      } else if (type === 'rave') {
        [220, 440, 330, 660, 440, 880].forEach((f, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(f, ctx.currentTime + idx * 0.09);
          gain.gain.setValueAtTime(0.1, ctx.currentTime + idx * 0.09);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + idx * 0.09 + 0.1);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(ctx.currentTime + idx * 0.09);
          osc.stop(ctx.currentTime + idx * 0.09 + 0.12);
        });
      }
    } catch {
      // AudioContext unavailable
    }
  };

  const triggerRandomChaos = () => {
    const events = ['negev', 'rain', 'achievement', 'glitch', 'flashbang', 'rave'];
    const chosen = events[Math.floor(Math.random() * events.length)];

    if (chosen === 'negev') {
      playSynth('gun');
      const tracers = Array.from({ length: 30 }, (_, i) => ({
        id: i,
        top: Math.random() * 90 + 5,
        delay: Math.random() * 0.8,
        color: Math.random() < 0.5 ? '#10b981' : '#f43f5e'
      }));
      setNegevTracers(tracers);
      setTimeout(() => {
        setNegevTracers([]);
      }, 3500);
    } else if (chosen === 'rain') {
      playSynth('rave');
      const emojis = ['🍌', '🐸', '🚀', '💾', '💀', '🍔', '⚡'];
      const items = Array.from({ length: 35 }, (_, i) => ({
        id: i,
        left: Math.random() * 95,
        emoji: emojis[Math.floor(Math.random() * emojis.length)],
        duration: 2 + Math.random() * 2
      }));
      setFallingItems(items);
      setTimeout(() => {
        setFallingItems([]);
      }, 4500);
    } else if (chosen === 'achievement') {
      playSynth('achievement');
      const pool = [
        {
          title: 'Downloaded Too Much RAM',
          desc: 'Achieved 512GB Chrome RAM usage without catching fire.',
          icon: '💾'
        },
        {
          title: 'Cybo Laser Ankle Breaker',
          desc: 'Jumped over the low laser, only to hit your forehead on the high laser.',
          icon: '⚡'
        },
        {
          title: 'Banana Hotline Operator',
          desc: 'Broadcasted Banana Phone 420 times across global ZE servers.',
          icon: '🍌'
        },
        {
          title: 'Negev 150-Round Suppressor',
          desc: 'Never let go of mouse1 the entire 64-player Zombie Escape round.',
          icon: '🔫'
        }
      ];
      setAchievementData(pool[Math.floor(Math.random() * pool.length)]);
      setTimeout(() => {
        setAchievementData(null);
      }, 5500);
    } else if (chosen === 'glitch') {
      playSynth('gun');
      setMatrixGlitch(true);
      setTimeout(() => {
        setMatrixGlitch(false);
      }, 2500);
    } else if (chosen === 'flashbang') {
      playSynth('flash');
      setFlashbang(true);
      setTimeout(() => {
        setFlashbang(false);
      }, 2800);
    } else if (chosen === 'rave') {
      playSynth('rave');
    }
  };

  return (
    <>
      {/* Floating Chaos Trigger Button (Bottom Right above footer) */}
      <div className="fixed bottom-6 right-6 z-40">
        <button
          onClick={triggerRandomChaos}
          className="group relative px-3.5 py-2.5 rounded-2xl bg-gradient-to-r from-fuchsia-600 via-purple-600 to-indigo-600 text-white font-cyber text-xs font-bold shadow-[0_0_25px_rgba(217,70,239,0.5)] hover:shadow-[0_0_35px_rgba(217,70,239,0.8)] border border-fuchsia-400/60 transition-all duration-300 hover:scale-105 active:scale-95 cursor-pointer flex items-center gap-2"
          title="Trigger a random chaotic anomaly across the website (Surprise Me!)"
        >
          <Dices className="w-4 h-4 text-yellow-300 group-hover:rotate-180 transition-transform duration-500" />
          <span className="hidden sm:inline tracking-wider">🎲 SURPRISE ME (CHAOS)</span>
          <span className="sm:hidden">🎲</span>
          <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-yellow-400 animate-ping" />
        </button>
      </div>

      {/* 1. NEGEV BULLET TRACERS OVERLAY */}
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
          <div className="absolute top-8 left-1/2 -translate-x-1/2 px-4 py-1.5 rounded-full bg-slate-950/90 border border-emerald-400 text-emerald-300 font-cyber text-xs font-bold shadow-[0_0_20px_rgba(16,185,129,0.5)]">
            🔫 NEGEV TRACER OVERLOAD // 150 ROUNDS FIRED
          </div>
        </div>
      )}

      {/* 2. BANANA & PEPE GRAVITY RAIN OVERLAY */}
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

      {/* 3. STEAM IN-GAME ACHIEVEMENT NOTIFICATION */}
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

      {/* 4. FULL-SCREEN MATRIX GLITCH */}
      {matrixGlitch && (
        <div className="fixed inset-0 pointer-events-none z-50 bg-emerald-950/20 backdrop-invert-0 flex flex-col items-center justify-center animate-pulse">
          <div className="p-4 rounded-xl bg-slate-950/90 border border-emerald-400 text-emerald-400 font-code text-sm font-bold shadow-[0_0_30px_rgba(16,185,129,0.8)] text-center space-y-1">
            <div>⚡ [SYSTEM OVERRIDE] 1000 FPS OVERCLOCK INJECTED</div>
            <div className="text-xs text-slate-400">CYBERPUNK NEURAL SYNC ESTABLISHED</div>
          </div>
        </div>
      )}

      {/* 5. FLASHBANG MEME */}
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
