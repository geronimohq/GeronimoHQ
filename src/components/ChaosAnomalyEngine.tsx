import React, { useState } from 'react';
import { Dices, Trophy, AlertTriangle, ShieldAlert, Radio, Sparkles } from 'lucide-react';
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
  const [vaporwaveCRT, setVaporwaveCRT] = useState(false);
  const [nightVision, setNightVision] = useState(false);
  const [deepFried, setDeepFried] = useState(false);
  const [pixelMode, setPixelMode] = useState(false);
  const [widePepe, setWidePepe] = useState(false);
  const [stretched43, setStretched43] = useState(false);
  const [smokeScreen, setSmokeScreen] = useState(false);
  const [molotovScreen, setMolotovScreen] = useState(false);
  const [zeroGrav, setZeroGrav] = useState(false);
  const [speedLines, setSpeedLines] = useState(false);
  const [warpSpeed, setWarpSpeed] = useState(false);
  const [laserDance, setLaserDance] = useState(false);
  const [matrixRain, setMatrixRain] = useState(false);
  const [terminalModal, setTerminalModal] = useState(false);
  const [caseModal, setCaseModal] = useState(false);
  const [rankUpModal, setRankUpModal] = useState(false);
  const [dvdBounce, setDvdBounce] = useState(false);
  const [clutchModal, setClutchModal] = useState(false);
  const [nukeModal, setNukeModal] = useState(false);
  const [c4Modal, setC4Modal] = useState(false);
  const [speedrunModal, setSpeedrunModal] = useState(false);
  const [gabenModal, setGabenModal] = useState(false);
  const [lagSpike, setLagSpike] = useState(false);
  const [subtickJitter, setSubtickJitter] = useState(false);
  const [godmodeHalo, setGodmodeHalo] = useState(false);

  const [negevTracers, setNegevTracers] = useState<Array<{ id: number; top: number; delay: number; color: string }>>([]);
  const [fallingItems, setFallingItems] = useState<Array<{ id: number; left: number; emoji: string; duration: number }>>([]);
  const [hitmarkers, setHitmarkers] = useState<Array<{ id: number; x: number; y: number }>>([]);
  const [toastBanner, setToastBanner] = useState<string | null>(null);

  // High-fidelity Web Audio Synth Generator
  const playChaosSynth = (type: 
    | 'gun' | 'achievement' | 'flash' | 'rave' | 'earthquake' | 'airhorn' | 'bsod' | 'coin' 
    | 'laser' | 'siren' | 'heartbeat' | 'vaporwave' | 'nvg' | 'dialup' | 'subbass' | 'cheer' | 'ding'
  ) => {
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
      } else if (type === 'laser') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(1200, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(180, ctx.currentTime + 0.35);
        gain.gain.setValueAtTime(0.2, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.38);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.4);
      } else if (type === 'siren') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(600, ctx.currentTime);
        osc.frequency.linearRampToValueAtTime(950, ctx.currentTime + 0.4);
        osc.frequency.linearRampToValueAtTime(600, ctx.currentTime + 0.8);
        osc.frequency.linearRampToValueAtTime(950, ctx.currentTime + 1.2);
        gain.gain.setValueAtTime(0.15, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.5);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 1.5);
      } else if (type === 'heartbeat') {
        [0, 0.2, 0.7, 0.9, 1.4, 1.6].forEach((delay) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(65, ctx.currentTime + delay);
          gain.gain.setValueAtTime(0.25, ctx.currentTime + delay);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + delay + 0.15);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(ctx.currentTime + delay);
          osc.stop(ctx.currentTime + delay + 0.16);
        });
      } else if (type === 'vaporwave') {
        [261.63, 329.63, 392.00, 523.25].forEach((f) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(f, ctx.currentTime);
          gain.gain.setValueAtTime(0.08, ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.8);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start();
          osc.stop(ctx.currentTime + 1.8);
        });
      } else if (type === 'nvg') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(1400, ctx.currentTime);
        gain.gain.setValueAtTime(0.05, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.5);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 1.5);
      } else if (type === 'dialup') {
        [700, 950, 1200, 850, 1400, 1800].forEach((f, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(f, ctx.currentTime + idx * 0.12);
          gain.gain.setValueAtTime(0.06, ctx.currentTime + idx * 0.12);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + idx * 0.12 + 0.11);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(ctx.currentTime + idx * 0.12);
          osc.stop(ctx.currentTime + idx * 0.12 + 0.12);
        });
      } else if (type === 'subbass') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(110, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(35, ctx.currentTime + 1.2);
        gain.gain.setValueAtTime(0.35, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.4);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 1.4);
      } else if (type === 'cheer') {
        for (let i = 0; i < 5; i++) {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(300 + Math.random() * 400, ctx.currentTime + i * 0.1);
          gain.gain.setValueAtTime(0.12, ctx.currentTime + i * 0.1);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.1 + 0.5);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(ctx.currentTime + i * 0.1);
          osc.stop(ctx.currentTime + i * 0.1 + 0.6);
        }
      } else if (type === 'ding') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(2400, ctx.currentTime);
        gain.gain.setValueAtTime(0.2, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.12);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.13);
      }
    } catch {}
  };

  const ACHIEVEMENTS_POOL: Achievement[] = [
    { title: 'Downloaded 1,024 GB of Cloud RAM', desc: 'Saturated your motherboard with zero page file errors.', icon: '💾' },
    { title: 'Cybo Laser Ankle Breaker', desc: 'Jumped over the bottom laser, but stubbed your toe on the middle laser.', icon: '⚡' },
    { title: 'Banana Hotline 24/7 Operator', desc: 'Looped Banana Phone for 4 consecutive hours on ZE servers.', icon: '🍌' },
    { title: 'Negev 150-Round Suppressor', desc: 'Held Mouse1 until your barrel melted into liquid steel.', icon: '🔫' },
    { title: 'Direct-Flip Speedrunner', desc: 'Switched tabs in true 0.0ms hardware composition latency.', icon: '🚀' },
    { title: 'Mako Reactor Meltdown Survivor', desc: 'Boarded the elevator with 0.1s left before core breach.', icon: '☢️' },
    { title: 'Gaben Blessing Bestowed', desc: 'Unboxed a holographic sticker and bought an entire pizza place.', icon: '👑' },
    { title: 'Sub-Tick Quantum Whisperer', desc: 'Your AWP shot registered in a parallel timeline.', icon: '🎯' },
    { title: 'Phoon Too Much For ZBlock', desc: 'Hit 12 consecutive bunnyhops out of elevator into sewer.', icon: '🐇' },
    { title: 'Kerrigan Boss Beater', desc: 'Defeated the Queen of Blades without taking toxic storm damage.', icon: '👾' },
    { title: 'Predator Laser Dodger', desc: 'Survived the vertical slicing laser array on 1 HP.', icon: '🛸' },
    { title: '1-Click Optimization Purist', desc: 'Never manually touched regedit again after CS2 Command Center.', icon: '🛡️' },
    { title: 'Pepe Bass Connoisseur', desc: 'Tested your subwoofer with the 1.16x master bass curve.', icon: '🐸' },
    { title: 'CS2 Smokes Sniffer', desc: 'Walked into a grey cloud and came out with a knife kill.', icon: '💨' },
    { title: 'MPO Slayer Champion', desc: 'Banished multiplane overlay stutter from Windows forever.', icon: '⚔️' },
  ];

  // 50 Distinct RNG Anomaly Keys
  const CHAOS_POOL = [
    'barrel_roll', 'earthquake', 'rainbow_rave', 'bsod_scare', 'pepe_banana_swarm',
    'confetti_nuke', 'airhorn', 'inverted_dimension', 'negev', 'glitch',
    'flashbang', 'vaporwave_crt', 'matrix_code_rain', 'zero_gravity', 'deep_fried_meme',
    'night_vision_goggles', 'speedrun_split', 'ze_high_laser', 'ze_low_laser', 'chicken_rain',
    'diamond_hands', 'pixel_retro_8bit', 'disco_fever', 'mario_coin_shower', 'tactical_nuke',
    'clutch_or_kick', 'hitmarker_storm', 'cs2_rank_up', 'smoke_grenade', 'molotov_fire',
    'c4_countdown', 'case_unboxing', 'banana_overdrive', 'stretched_res', 'wide_pepe_walk',
    'fake_lag_spike', 'dialup_handshake', 'hacker_terminal', 'dvd_screensaver', 'dubstep_bass_drop',
    'crowd_cheer', 'sv_cheats_god', 'phoon_bhop', 'achievement_jackpot', 'ram_injection',
    'subtick_rewind', 'airdrop_crate', 'gaben_summer_sale', 'laser_dance_party', 'super_nova_warp'
  ];

  const triggerRandomChaos = () => {
    const chosen = CHAOS_POOL[Math.floor(Math.random() * CHAOS_POOL.length)];

    if (chosen === 'barrel_roll') {
      playChaosSynth('rave');
      setBarrelRoll(true);
      setToastBanner('🌀 BARREL ROLL // 360° VIEWPORT ROTATION ACTIVATED!');
      setTimeout(() => { setBarrelRoll(false); setToastBanner(null); }, 3000);
    } else if (chosen === 'earthquake') {
      playChaosSynth('earthquake');
      setEarthquake(true);
      setToastBanner('🌋 ZE EARTHQUAKE // HOLO-CHAMBER SEISMIC SHAKE!');
      setTimeout(() => { setEarthquake(false); setToastBanner(null); }, 2500);
    } else if (chosen === 'rainbow_rave') {
      playChaosSynth('rave');
      setRainbowRave(true);
      setToastBanner('🌈 RAINBOW RAVE // FULL HUE-ROTATE DISCO STROBE!');
      setTimeout(() => { setRainbowRave(false); setToastBanner(null); }, 3500);
    } else if (chosen === 'bsod_scare') {
      playChaosSynth('bsod');
      setBsodScare(true);
      setTimeout(() => { setBsodScare(false); playChaosSynth('coin'); }, 2400);
    } else if (chosen === 'inverted_dimension') {
      playChaosSynth('flash');
      setInvertedDimension(true);
      setToastBanner('⚡ INVERTED DIMENSION // REVERSE PHOSPHOR MATRIX!');
      setTimeout(() => { setInvertedDimension(false); setToastBanner(null); }, 2800);
    } else if (chosen === 'airhorn') {
      playChaosSynth('airhorn');
      setToastBanner('🎺 MLG TRIPLE AIRHORN BLAST // 360 NO-SCOPE READY!');
      confetti({ particleCount: 75, spread: 80, origin: { y: 0.8 }, colors: ['#ef4444', '#f59e0b', '#3b82f6'] });
      setTimeout(() => setToastBanner(null), 3000);
    } else if (chosen === 'confetti_nuke') {
      playChaosSynth('achievement');
      setToastBanner('🎉 MAXIMUM CONFETTI NUKE DETONATED OVER GERONIMOHQ!');
      for (let i = 0; i < 4; i++) {
        setTimeout(() => {
          confetti({
            particleCount: 65,
            angle: 60 + i * 30,
            spread: 75,
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
      setToastBanner('🔫 NEGEV TRACER OVERLOAD // 150 BULLETS FIRED!');
      setTimeout(() => { setNegevTracers([]); setToastBanner(null); }, 3200);
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
      setTimeout(() => { setFallingItems([]); setToastBanner(null); }, 4000);
    } else if (chosen === 'achievement_jackpot') {
      playChaosSynth('achievement');
      const randAch = ACHIEVEMENTS_POOL[Math.floor(Math.random() * ACHIEVEMENTS_POOL.length)];
      setAchievementData(randAch);
      setTimeout(() => setAchievementData(null), 5000);
    } else if (chosen === 'glitch') {
      playChaosSynth('gun');
      setMatrixGlitch(true);
      setTimeout(() => setMatrixGlitch(false), 2500);
    } else if (chosen === 'flashbang') {
      playChaosSynth('flash');
      setFlashbang(true);
      setTimeout(() => setFlashbang(false), 2600);
    } else if (chosen === 'vaporwave_crt') {
      playChaosSynth('vaporwave');
      setVaporwaveCRT(true);
      setToastBanner('🌆 VAPORWAVE RETRO 1984 // CRT SCANLINES ACTIVE!');
      setTimeout(() => { setVaporwaveCRT(false); setToastBanner(null); }, 3500);
    } else if (chosen === 'night_vision_goggles') {
      playChaosSynth('nvg');
      setNightVision(true);
      setToastBanner('🥽 NVG NIGHT VISION // GREEN PHOSPHOR LENS ACTIVATED!');
      setTimeout(() => { setNightVision(false); setToastBanner(null); }, 3500);
    } else if (chosen === 'deep_fried_meme') {
      playChaosSynth('laser');
      setDeepFried(true);
      setToastBanner('🍟 DEEP FRIED MEME MODE // 300% SATURATION OVERDRIVE!');
      setTimeout(() => { setDeepFried(false); setToastBanner(null); }, 3200);
    } else if (chosen === 'pixel_retro_8bit') {
      playChaosSynth('coin');
      setPixelMode(true);
      setToastBanner('👾 RETRO 8-BIT ARCADE // PIXEL MATRIX APPLIED!');
      setTimeout(() => { setPixelMode(false); setToastBanner(null); }, 3200);
    } else if (chosen === 'wide_pepe_walk') {
      playChaosSynth('rave');
      setWidePepe(true);
      setToastBanner('🚶 WIDE PEPE 21:9 STRETCH // HE COMING!');
      setTimeout(() => { setWidePepe(false); setToastBanner(null); }, 3500);
    } else if (chosen === 'stretched_res') {
      playChaosSynth('gun');
      setStretched43(true);
      setToastBanner('📺 CS2 PRO 4:3 STRETCHED RESOLUTION // BIG HEADS ENGAGED!');
      setTimeout(() => { setStretched43(false); setToastBanner(null); }, 3500);
    } else if (chosen === 'smoke_grenade') {
      playChaosSynth('flash');
      setSmokeScreen(true);
      setToastBanner('💨 CS2 SMOKE GRENADE POPPED // VOLUMETRIC CLOUD!');
      setTimeout(() => { setSmokeScreen(false); setToastBanner(null); }, 3200);
    } else if (chosen === 'molotov_fire') {
      playChaosSynth('gun');
      setMolotovScreen(true);
      setToastBanner('🔥 MOLOTOV COCKTAIL // BURNING THE SITE!');
      setTimeout(() => { setMolotovScreen(false); setToastBanner(null); }, 3200);
    } else if (chosen === 'zero_gravity') {
      playChaosSynth('laser');
      setZeroGrav(true);
      setToastBanner('🌌 ZERO GRAVITY // SV_GRAVITY 100 INJECTED!');
      setTimeout(() => { setZeroGrav(false); setToastBanner(null); }, 3200);
    } else if (chosen === 'phoon_bhop') {
      playChaosSynth('rave');
      setSpeedLines(true);
      setToastBanner('🐇 BHOP SPEED: 480 UPS // PHOON IS HOPPING OVER US!');
      setTimeout(() => { setSpeedLines(false); setToastBanner(null); }, 3500);
    } else if (chosen === 'super_nova_warp') {
      playChaosSynth('laser');
      setWarpSpeed(true);
      setToastBanner('🚀 WARP DRIVE OVERCLOCK // HYPERSPACE JUMP!');
      setTimeout(() => { setWarpSpeed(false); setToastBanner(null); }, 3200);
    } else if (chosen === 'laser_dance_party') {
      playChaosSynth('laser');
      setLaserDance(true);
      setToastBanner('⚡ ZE CYBO LASER GRID DANCE PARTY // JUMP & CROUCH!');
      setTimeout(() => { setLaserDance(false); setToastBanner(null); }, 3500);
    } else if (chosen === 'matrix_code_rain') {
      playChaosSynth('rave');
      setMatrixRain(true);
      setToastBanner('💻 THE MATRIX DIGITAL RAIN // TERMINAL DECRYPTING!');
      setTimeout(() => { setMatrixRain(false); setToastBanner(null); }, 3500);
    } else if (chosen === 'hacker_terminal') {
      playChaosSynth('gun');
      setTerminalModal(true);
      setTimeout(() => setTerminalModal(false), 3500);
    } else if (chosen === 'case_unboxing') {
      playChaosSynth('achievement');
      setCaseModal(true);
      confetti({ particleCount: 80, spread: 70, origin: { y: 0.6 } });
      setTimeout(() => setCaseModal(false), 4000);
    } else if (chosen === 'cs2_rank_up') {
      playChaosSynth('achievement');
      setRankUpModal(true);
      confetti({ particleCount: 90, spread: 85, origin: { y: 0.6 }, colors: ['#ffd700', '#f59e0b'] });
      setTimeout(() => setRankUpModal(false), 4000);
    } else if (chosen === 'dvd_screensaver') {
      playChaosSynth('coin');
      setDvdBounce(true);
      setToastBanner('📀 RETRO DVD LOGO BOUNCE // WILL IT HIT THE CORNER?!');
      setTimeout(() => { setDvdBounce(false); setToastBanner(null); }, 4500);
    } else if (chosen === 'clutch_or_kick') {
      playChaosSynth('heartbeat');
      setClutchModal(true);
      setTimeout(() => setClutchModal(false), 3800);
    } else if (chosen === 'tactical_nuke') {
      playChaosSynth('siren');
      setNukeModal(true);
      setTimeout(() => setNukeModal(false), 3800);
    } else if (chosen === 'c4_countdown') {
      playChaosSynth('heartbeat');
      setC4Modal(true);
      setTimeout(() => setC4Modal(false), 3800);
    } else if (chosen === 'speedrun_split') {
      playChaosSynth('coin');
      setSpeedrunModal(true);
      setTimeout(() => setSpeedrunModal(false), 3500);
    } else if (chosen === 'gaben_summer_sale') {
      playChaosSynth('coin');
      setGabenModal(true);
      setTimeout(() => setGabenModal(false), 3500);
    } else if (chosen === 'fake_lag_spike') {
      playChaosSynth('bsod');
      setLagSpike(true);
      setToastBanner('📶 PING: 999ms // PACKET LOSS 85% // CHOKE 60%!');
      setTimeout(() => { setLagSpike(false); setToastBanner(null); }, 2500);
    } else if (chosen === 'subtick_rewind') {
      playChaosSynth('laser');
      setSubtickJitter(true);
      setToastBanner('⏱️ SUB-TICK QUANTUM REWIND // VALVE TICK ROLLBACK!');
      setTimeout(() => { setSubtickJitter(false); setToastBanner(null); }, 2500);
    } else if (chosen === 'sv_cheats_god') {
      playChaosSynth('achievement');
      setGodmodeHalo(true);
      setToastBanner('🛡️ CONSOLE: sv_cheats 1; god; noclip // INVINCIBILITY ENGAGED!');
      setTimeout(() => { setGodmodeHalo(false); setToastBanner(null); }, 3200);
    } else if (chosen === 'chicken_rain') {
      playChaosSynth('rave');
      const chickens = Array.from({ length: 45 }, (_, i) => ({
        id: i,
        left: Math.random() * 95,
        emoji: '🐔',
        duration: 1.5 + Math.random() * 2.0
      }));
      setFallingItems(chickens);
      setToastBanner('🐔 CS2 INFERNO CHICKEN APOCALYPSE!');
      setTimeout(() => { setFallingItems([]); setToastBanner(null); }, 3800);
    } else if (chosen === 'diamond_hands') {
      playChaosSynth('coin');
      const items = Array.from({ length: 45 }, (_, i) => ({
        id: i,
        left: Math.random() * 95,
        emoji: ['💎', '🚀', '🌕', '📈'][Math.floor(Math.random() * 4)],
        duration: 1.6 + Math.random() * 2.0
      }));
      setFallingItems(items);
      setToastBanner('💎🚀 TO THE MOON // DIAMOND HANDS ANOMALY!');
      setTimeout(() => { setFallingItems([]); setToastBanner(null); }, 3800);
    } else if (chosen === 'mario_coin_shower') {
      playChaosSynth('coin');
      const coins = Array.from({ length: 50 }, (_, i) => ({
        id: i,
        left: Math.random() * 95,
        emoji: '🪙',
        duration: 1.4 + Math.random() * 1.8
      }));
      setFallingItems(coins);
      setToastBanner('🪙 GOLDEN COIN SHOWER // EXTRA LIFE BONUS!');
      setTimeout(() => { setFallingItems([]); setToastBanner(null); }, 3500);
    } else if (chosen === 'hitmarker_storm') {
      playChaosSynth('ding');
      const marks = Array.from({ length: 15 }, (_, i) => ({
        id: i,
        x: Math.random() * 80 + 10,
        y: Math.random() * 80 + 10
      }));
      setHitmarkers(marks);
      setToastBanner('🎯 100% ACCURACY HITMARKER OVERDRIVE!');
      setTimeout(() => { setHitmarkers([]); setToastBanner(null); }, 3000);
    } else if (chosen === 'ze_high_laser') {
      playChaosSynth('laser');
      setToastBanner('⚠️ RED LASER WARNING // DUCK IMMEDIATELY!');
      setTimeout(() => setToastBanner(null), 3200);
    } else if (chosen === 'ze_low_laser') {
      playChaosSynth('laser');
      setToastBanner('⚡ BLUE LASER WARNING // JUMP IMMEDIATELY!');
      setTimeout(() => setToastBanner(null), 3200);
    } else if (chosen === 'banana_overdrive') {
      playChaosSynth('rave');
      setToastBanner('🍌 BANANA OVERDRIVE 9000 // VITAMIN B POTASSIUM MAXIMUM!');
      confetti({ particleCount: 70, spread: 80, colors: ['#facc15', '#fef08a'] });
      setTimeout(() => setToastBanner(null), 3200);
    } else if (chosen === 'dialup_handshake') {
      playChaosSynth('dialup');
      setToastBanner('📠 1999 56K DIAL-UP HANDSHAKE // CONNECTING TO AOL...');
      setTimeout(() => setToastBanner(null), 3500);
    } else if (chosen === 'dubstep_bass_drop') {
      playChaosSynth('subbass');
      setEarthquake(true);
      setToastBanner('🔊 MASSIVE SUB-BASS DROP // FEEL THE 30HZ SHAKE!');
      setTimeout(() => { setEarthquake(false); setToastBanner(null); }, 2500);
    } else if (chosen === 'crowd_cheer') {
      playChaosSynth('cheer');
      setToastBanner('🏆 STADIUM STANDING OVATION // MVP ROUND GERONIMO!');
      confetti({ particleCount: 85, spread: 90, origin: { y: 0.7 } });
      setTimeout(() => setToastBanner(null), 3200);
    } else if (chosen === 'ram_injection') {
      playChaosSynth('coin');
      setToastBanner('💾 +1,024 GB DDR5 CLOUD RAM INJECTED INTO BROWSER VRAM!');
      setTimeout(() => setToastBanner(null), 3200);
    } else if (chosen === 'airdrop_crate') {
      playChaosSynth('achievement');
      const crate = [{ id: 1, left: 50, emoji: '📦', duration: 3.0 }];
      setFallingItems(crate);
      setToastBanner('🪂 WEAPON SUPPLY CRATE AIRDROPPED AT YOUR FEET!');
      setTimeout(() => { setFallingItems([]); setToastBanner(null); }, 3800);
    } else if (chosen === 'disco_fever') {
      playChaosSynth('rave');
      setRainbowRave(true);
      setToastBanner('🪩 DISCO FEVER // STAYIN ALIVE IN ZOMBIE ESCAPE!');
      setTimeout(() => { setRainbowRave(false); setToastBanner(null); }, 3200);
    }
  };

  return (
    <>
      {/* Floating Chaos Trigger Button */}
      <div className="fixed bottom-6 right-6 z-40">
        <button
          onClick={triggerRandomChaos}
          className="group relative px-4 py-2.5 min-h-[44px] rounded-2xl bg-gradient-to-r from-fuchsia-600 via-purple-600 to-indigo-600 text-white font-cyber text-xs font-bold shadow-[0_0_25px_rgba(217,70,239,0.5)] hover:shadow-[0_0_35px_rgba(217,70,239,0.8)] border border-fuchsia-400/60 transition-all duration-300 hover:scale-105 active:scale-95 cursor-pointer flex items-center gap-2 touch-manipulation"
          title="Trigger 50+ high-RNG chaotic anomalies across the website (Surprise Me!)"
          aria-label="Trigger chaotic surprise anomaly"
        >
          <Dices className="w-4 h-4 text-yellow-300 group-hover:rotate-180 transition-transform duration-500" />
          <span className="hidden sm:inline tracking-wider">🎲 SURPRISE ME (CHAOS)</span>
          <span className="sm:hidden">🎲</span>
          <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-yellow-400 animate-ping" />
        </button>
      </div>

      {/* Top Banner Toast */}
      {toastBanner && (
        <div className="fixed top-20 left-1/2 -translate-x-1/2 z-50 px-5 py-2 rounded-full bg-slate-950/95 border-2 border-fuchsia-400 text-yellow-300 font-cyber text-xs font-bold shadow-[0_0_30px_rgba(217,70,239,0.7)] animate-bounce select-none">
          {toastBanner}
        </div>
      )}

      {/* 1. BARREL ROLL */}
      {barrelRoll && (
        <style dangerouslySetInnerHTML={{ __html: `
          body { transition: transform 3s ease-in-out !important; transform: rotate(360deg) !important; }
        ` }} />
      )}

      {/* 2. EARTHQUAKE */}
      {earthquake && (
        <style dangerouslySetInnerHTML={{ __html: `
          body { animation: earthquakeShake 0.12s infinite alternate !important; }
          @keyframes earthquakeShake {
            0% { transform: translate(3px, 2px) rotate(0.4deg); }
            50% { transform: translate(-3px, -2px) rotate(-0.4deg); }
            100% { transform: translate(2px, -3px) rotate(0.2deg); }
          }
        ` }} />
      )}

      {/* 3. RAINBOW RAVE */}
      {rainbowRave && (
        <style dangerouslySetInnerHTML={{ __html: `
          body { animation: rainbowHue 0.6s infinite linear !important; }
          @keyframes rainbowHue { 0% { filter: hue-rotate(0deg); } 100% { filter: hue-rotate(360deg); } }
        ` }} />
      )}

      {/* 4. INVERTED DIMENSION */}
      {invertedDimension && (
        <style dangerouslySetInnerHTML={{ __html: `
          body { filter: invert(100%) hue-rotate(180deg) !important; transition: filter 0.3s ease !important; }
        ` }} />
      )}

      {/* 5. VAPORWAVE CRT */}
      {vaporwaveCRT && (
        <div className="fixed inset-0 pointer-events-none z-50 bg-gradient-to-b from-purple-500/20 to-pink-500/20 mix-blend-color-dodge">
          <div className="w-full h-full bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.4)_50%)] bg-[length:100%_4px]" />
        </div>
      )}

      {/* 6. NIGHT VISION */}
      {nightVision && (
        <div className="fixed inset-0 pointer-events-none z-50 bg-emerald-500/30 mix-blend-color-burn">
          <div className="w-full h-full rounded-full border-[100px] border-black/80" />
        </div>
      )}

      {/* 7. DEEP FRIED */}
      {deepFried && (
        <style dangerouslySetInnerHTML={{ __html: `
          body { filter: saturate(400%) contrast(200%) !important; }
        ` }} />
      )}

      {/* 8. RETRO PIXEL */}
      {pixelMode && (
        <style dangerouslySetInnerHTML={{ __html: `
          body { filter: contrast(160%) brightness(110%) !important; image-rendering: pixelated !important; }
        ` }} />
      )}

      {/* 9. WIDE PEPE 21:9 */}
      {widePepe && (
        <style dangerouslySetInnerHTML={{ __html: `
          body { transform: scaleX(1.35) !important; transition: transform 0.5s ease !important; }
        ` }} />
      )}

      {/* 10. 4:3 STRETCHED */}
      {stretched43 && (
        <style dangerouslySetInnerHTML={{ __html: `
          body { transform: scaleX(1.25) !important; }
        ` }} />
      )}

      {/* 11. SMOKE GRENADE */}
      {smokeScreen && (
        <div className="fixed inset-0 pointer-events-none z-50 bg-slate-300/80 backdrop-blur-md animate-pulse" />
      )}

      {/* 12. MOLOTOV FIRE */}
      {molotovScreen && (
        <div className="fixed bottom-0 left-0 right-0 h-48 pointer-events-none z-50 bg-gradient-to-t from-orange-600/70 via-red-500/40 to-transparent animate-pulse" />
      )}

      {/* 13. ZERO GRAVITY */}
      {zeroGrav && (
        <style dangerouslySetInnerHTML={{ __html: `
          body { animation: zeroGravFloat 2s infinite ease-in-out alternate !important; }
          @keyframes zeroGravFloat { 0% { transform: translateY(0px); } 100% { transform: translateY(-20px); } }
        ` }} />
      )}

      {/* 14. PHOON BHOP SPEED LINES */}
      {speedLines && (
        <div className="fixed inset-0 pointer-events-none z-50 border-[20px] border-cyan-400/40 animate-ping" />
      )}

      {/* 15. WARP SPEED */}
      {warpSpeed && (
        <style dangerouslySetInnerHTML={{ __html: `
          body { transform: scale(1.08) !important; filter: blur(1px) !important; transition: all 0.3s ease !important; }
        ` }} />
      )}

      {/* 16. LASER DANCE */}
      {laserDance && (
        <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
          <div className="absolute top-1/4 left-0 right-0 h-1 bg-cyan-400 shadow-[0_0_20px_#00f0ff] animate-pulse" />
          <div className="absolute top-2/4 left-0 right-0 h-1 bg-fuchsia-500 shadow-[0_0_20px_#ff007f] animate-pulse" />
          <div className="absolute top-3/4 left-0 right-0 h-1 bg-lime-400 shadow-[0_0_20px_#84cc16] animate-pulse" />
        </div>
      )}

      {/* 17. MATRIX RAIN */}
      {matrixRain && (
        <div className="fixed inset-0 pointer-events-none z-50 bg-emerald-950/25 flex items-center justify-around font-mono text-emerald-400 text-xs overflow-hidden">
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="animate-fall space-y-2 opacity-80" style={{ animationDuration: `${1.5 + (i % 3)}s` }}>
              <div>01000111</div><div>01000101</div><div>01010010</div><div>01001111</div>
            </div>
          ))}
        </div>
      )}

      {/* 18. FAKE BSOD */}
      {bsodScare && (
        <div className="fixed inset-0 z-[100] bg-[#0078d7] text-white p-8 sm:p-16 flex flex-col justify-center font-sans select-none animate-fadeIn">
          <div className="text-7xl sm:text-9xl font-light mb-6">:(</div>
          <h2 className="text-2xl sm:text-3xl font-light mb-4">
            Your PC ran into a problem and needs to restart. We're just collecting some error info...
          </h2>
          <div className="text-lg sm:text-xl font-light mb-8">100% complete</div>
          <div className="flex items-center gap-6 mt-4">
            <div className="w-24 h-24 bg-white text-black p-2 font-mono text-[9px] flex items-center justify-center text-center font-bold">
              [QR: GERONIMO]
            </div>
            <div className="text-xs sm:text-sm text-slate-200 font-mono space-y-1">
              <div>Stop code: CRITICAL_PROCESS_DIED_BANANA_OVERFLOW</div>
              <div>What failed: geronimohq_cloud_ram_x64.sys</div>
              <div>Just kidding! You survived the Surprise Me Anomaly! 🍌</div>
            </div>
          </div>
        </div>
      )}

      {/* 19. NEGEV TRACERS */}
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

      {/* 20. FALLING EMOJIS */}
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

      {/* 21. HITMARKERS */}
      {hitmarkers.length > 0 && (
        <div className="fixed inset-0 pointer-events-none z-50">
          {hitmarkers.map((h) => (
            <div
              key={h.id}
              className="absolute text-red-500 font-bold text-2xl animate-ping"
              style={{ left: `${h.x}%`, top: `${h.y}%` }}
            >
              ╳
            </div>
          ))}
        </div>
      )}

      {/* 22. HACKER TERMINAL MODAL */}
      {terminalModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 pointer-events-none">
          <div className="w-full max-w-lg bg-black/90 border-2 border-emerald-500 p-4 rounded-xl font-mono text-emerald-400 text-xs shadow-[0_0_30px_#10b981]">
            <div className="flex items-center justify-between border-b border-emerald-500/50 pb-2 mb-2 font-bold">
              <span>root@geronimohq:~#</span>
              <span className="text-red-400">ACCESS GRANTED</span>
            </div>
            <div>[+] Injecting Direct-Flip 0.0ms display pipeline... [OK]</div>
            <div>[+] Disabling Multiplane Overlay (MPO)... [OK]</div>
            <div>[+] Connecting to Japan Possession & GFL ZE... [OK]</div>
            <div className="text-yellow-400 mt-2">&gt; OVERCLOCK 1000 FPS STABLE</div>
          </div>
        </div>
      )}

      {/* 23. CS2 KNIFE CASE UNBOXING */}
      {caseModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 pointer-events-none animate-fadeIn">
          <div className="p-6 rounded-2xl bg-gradient-to-b from-yellow-950 via-slate-900 to-black border-2 border-yellow-400 text-center shadow-[0_0_40px_rgba(250,204,21,0.6)]">
            <Sparkles className="w-12 h-12 text-yellow-400 mx-auto animate-spin mb-2" />
            <div className="text-yellow-400 font-cyber font-black text-xs uppercase tracking-widest">★ SPECIAL RARE ITEM ★</div>
            <div className="text-2xl font-cyber font-black text-white mt-1">Butterfly Knife | Doppler</div>
            <div className="text-xs text-fuchsia-400 font-code mt-1">Exterior: Factory New (0.007 Float)</div>
          </div>
        </div>
      )}

      {/* 24. CS2 RANK UP MODAL */}
      {rankUpModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 pointer-events-none animate-fadeIn">
          <div className="p-6 rounded-2xl bg-gradient-to-b from-blue-950 via-slate-900 to-black border-2 border-blue-400 text-center shadow-[0_0_40px_rgba(96,165,250,0.6)]">
            <Trophy className="w-12 h-12 text-blue-400 mx-auto animate-bounce mb-2" />
            <div className="text-blue-400 font-cyber font-bold text-xs uppercase tracking-widest">SKILL GROUP PROMOTION</div>
            <div className="text-2xl font-cyber font-black text-white mt-1">THE GLOBAL ELITE</div>
            <div className="text-xs text-slate-300 font-code mt-1">Top 0.5% Worldwide Competitive Matchmaking</div>
          </div>
        </div>
      )}

      {/* 25. DVD BOUNCE LOGO */}
      {dvdBounce && (
        <div className="fixed top-1/3 left-1/3 z-50 pointer-events-none animate-bounce">
          <div className="px-5 py-2.5 rounded-xl bg-fuchsia-600 border border-white text-white font-cyber font-black text-lg shadow-[0_0_25px_#d946ef]">
            GERONIMO DVD
          </div>
        </div>
      )}

      {/* 26. CLUTCH OR KICK */}
      {clutchModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
          <div className="px-6 py-4 rounded-xl bg-red-950/90 border-2 border-red-500 text-center shadow-[0_0_35px_#ef4444] animate-pulse">
            <ShieldAlert className="w-10 h-10 text-red-500 mx-auto mb-1 animate-ping" />
            <div className="text-red-400 font-cyber font-black text-xl">1v5 CLUTCH SITUATION</div>
            <div className="text-white text-xs font-code mt-1">1 HP REMAINING &bull; CLUTCH OR KICK!</div>
          </div>
        </div>
      )}

      {/* 27. TACTICAL NUKE */}
      {nukeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
          <div className="px-6 py-4 rounded-xl bg-amber-950/90 border-2 border-amber-400 text-center shadow-[0_0_40px_#f59e0b] animate-bounce">
            <AlertTriangle className="w-10 h-10 text-amber-400 mx-auto mb-1" />
            <div className="text-amber-300 font-cyber font-black text-2xl">⚠️ TACTICAL NUKE INCOMING!</div>
            <div className="text-white text-xs font-code mt-1">EMP DETONATING IN 3... 2... 1...</div>
          </div>
        </div>
      )}

      {/* 28. C4 COUNTDOWN */}
      {c4Modal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
          <div className="px-6 py-4 rounded-xl bg-red-950/90 border-2 border-red-500 text-center shadow-[0_0_35px_#ef4444]">
            <Radio className="w-10 h-10 text-red-400 mx-auto mb-1 animate-pulse" />
            <div className="text-red-400 font-cyber font-black text-xl">THE BOMB HAS BEEN PLANTED</div>
            <div className="text-white text-xs font-code mt-1">40 SECONDS UNTIL DETONATION</div>
          </div>
        </div>
      )}

      {/* 29. SPEEDRUN SPLIT */}
      {speedrunModal && (
        <div className="fixed top-24 right-8 z-50 p-4 rounded-xl bg-slate-950/95 border border-cyan-400 text-cyan-300 font-mono text-xs shadow-[0_0_25px_#00f0ff] pointer-events-none">
          <div className="font-bold text-white mb-1">ANY% ZE MAKO ELEVATOR</div>
          <div className="text-emerald-400 font-bold text-lg">-00:00.42 (PB)</div>
          <div className="text-[10px] text-slate-400">Current Pace: Gold Split</div>
        </div>
      )}

      {/* 30. GABEN SUMMER SALE */}
      {gabenModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
          <div className="px-8 py-5 rounded-2xl bg-gradient-to-r from-emerald-950 via-slate-900 to-emerald-950 border-2 border-emerald-400 text-center shadow-[0_0_35px_#10b981]">
            <div className="text-emerald-400 font-cyber font-black text-3xl">-90% STEAM SUMMER SALE</div>
            <div className="text-white text-xs font-code mt-1">Lord Gaben has discounted all CS2 skins!</div>
          </div>
        </div>
      )}

      {/* 31. FAKE LAG SPIKE */}
      {lagSpike && (
        <div className="fixed inset-0 pointer-events-none z-50 border-[15px] border-red-600/70 flex items-center justify-center">
          <div className="bg-red-950 border border-red-500 px-4 py-2 rounded-lg text-red-400 font-mono text-xs">
            CONNECTION PROBLEM (AUTO-DISCONNECT IN 25.0 SECONDS)
          </div>
        </div>
      )}

      {/* 32. SUB-TICK JITTER */}
      {subtickJitter && (
        <style dangerouslySetInnerHTML={{ __html: `
          body { animation: subtickShake 0.08s 4 ease-in-out !important; }
          @keyframes subtickShake { 0% { transform: translateX(4px); } 100% { transform: translateX(-4px); } }
        ` }} />
      )}

      {/* 33. GODMODE HALO */}
      {godmodeHalo && (
        <div className="fixed inset-0 pointer-events-none z-50 border-[8px] border-cyan-400 shadow-[inset_0_0_40px_#00f0ff] animate-pulse" />
      )}

      {/* 34. FLASHBANG */}
      {flashbang && (
        <div className="fixed inset-0 z-50 bg-white/95 transition-opacity duration-1000 flex items-center justify-center animate-fadeOut">
          <div className="text-slate-900 font-cyber font-black text-2xl tracking-widest animate-bounce">
            ⚠️ BLINDED BY TEAMMATE FLASHBANG ⚠️
          </div>
        </div>
      )}

      {/* 35. MATRIX GLITCH */}
      {matrixGlitch && (
        <div className="fixed inset-0 pointer-events-none z-50 bg-emerald-950/20 backdrop-invert-0 flex flex-col items-center justify-center animate-pulse">
          <div className="p-4 rounded-xl bg-slate-950/90 border border-emerald-400 text-emerald-400 font-code text-sm font-bold shadow-[0_0_30px_rgba(16,185,129,0.8)] text-center space-y-1">
            <div>⚡ [SYSTEM OVERRIDE] 1000 FPS OVERCLOCK INJECTED</div>
            <div className="text-xs text-slate-400">CYBERPUNK NEURAL SYNC ESTABLISHED</div>
          </div>
        </div>
      )}

      {/* 36. STEAM ACHIEVEMENT NOTIFICATION */}
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
    </>
  );
};
