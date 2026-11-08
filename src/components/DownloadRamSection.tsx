import React, { useState, useEffect, useRef } from 'react';
import confetti from 'canvas-confetti';
import { Cpu, Download, CheckCircle2, Sparkles, Terminal, RotateCcw, Copy, Check, Gamepad2, Trophy } from 'lucide-react';

interface HardwareTier {
  id: string;
  shortActionLabel: string;
  certLabel: string;
  title: string;
  speed: string;
  badge: string;
  desc: string;
}

type MemePackageMode = 'ram' | 'gpu' | 'fps';

const TIERS_BY_MODE: Record<MemePackageMode, HardwareTier[]> = {
  ram: [
    {
      id: 'ram-16',
      shortActionLabel: '16 GB RAM',
      certLabel: '16 GB DDR5 RAM (6000 MT/s CL30)',
      title: '16 GB DDR5',
      speed: '6000 MT/s CL30',
      badge: 'STARTER PACK',
      desc: 'Enough to open 3 Chrome tabs and Counter-Strike 2 simultaneously.',
    },
    {
      id: 'ram-32',
      shortActionLabel: '32 GB RAM',
      certLabel: '32 GB DDR5 RAM (7200 MT/s CL28)',
      title: '32 GB DDR5',
      speed: '7200 MT/s CL28',
      badge: 'GAMER SWEETSPOT',
      desc: 'Zero stutter when 60 players throw HE grenades on GFL Zombie Escape.',
    },
    {
      id: 'ram-64',
      shortActionLabel: '64 GB RAM',
      certLabel: '64 GB DDR5 RAM (8000 MT/s CL26)',
      title: '64 GB DDR5',
      speed: '8000 MT/s CL26',
      badge: 'WORKSTATION CHAD',
      desc: 'Download enough dedotated WAM to host your own Minecraft + CS2 cluster.',
    },
    {
      id: 'ram-128',
      shortActionLabel: '128 GB RAM',
      certLabel: '128 GB DDR6-X RAM (12,800 MT/s CL14)',
      title: '128 GB DDR6-X',
      speed: '12,800 MT/s CL14',
      badge: 'NASA QUANTUM OVERKILL',
      desc: 'Directly links your motherboard to the Pentagon satellite array.',
    },
  ],
  gpu: [
    {
      id: 'gpu-6090-fe',
      shortActionLabel: 'RTX 6090 FE (32GB)',
      certLabel: 'NVIDIA RTX 6090 Founders Edition (32GB GDDR7)',
      title: 'RTX 6090 FE',
      speed: '32 GB GDDR7 • 3,450 MHz',
      badge: 'FOUNDERS EDITION',
      desc: 'Renders 64-player Molotov + HE grenade smoke at 8K without warming up your room.',
    },
    {
      id: 'gpu-6090-ti',
      shortActionLabel: 'RTX 6090 Ti (64GB)',
      certLabel: 'NVIDIA RTX 6090 Ti OC (64GB GDDR7X • 32,768 CUDA Cores)',
      title: 'RTX 6090 Ti',
      speed: '64 GB GDDR7X • 4,200 MHz',
      badge: 'GERONIMO FLAGSHIP',
      desc: '32,768 CUDA Cores + DLSS 5.0 Future-Frame Prediction (shoots zombies 2 ticks before they spawn).',
    },
    {
      id: 'gpu-6090-matrix',
      shortActionLabel: 'RTX 6090 Ti MATRIX (96GB)',
      certLabel: 'ROG MATRIX RTX 6090 Ti LN2 (96GB HBM3e • -196°C)',
      title: '6090 Ti MATRIX',
      speed: '96 GB HBM3e • LN2 COOLED',
      badge: 'LIQUID NITROGEN EDITION',
      desc: 'Built-in virtual liquid nitrogen loop (-196°C) + Quad-Slot ARGB Halo Matrix telemetry display.',
    },
    {
      id: 'gpu-quad-sli',
      shortActionLabel: 'QUAD-SLI RTX 6090 Ti (256GB)',
      certLabel: 'QUAD-SLI NVIDIA RTX 6090 Ti TITAN-Z (256GB GDDR8)',
      title: 'QUAD-SLI 6090 Ti',
      speed: '256 GB GDDR8 • 4.8 TB/s',
      badge: 'PENTAGON SUPERCOMPUTER',
      desc: 'Requires a virtual nuclear reactor. Ray-traces every individual Mako Reactor laser beam in 16K.',
    },
  ],
  fps: [
    {
      id: 'fps-250',
      shortActionLabel: '+250 FPS BOOST PACK',
      certLabel: '+250 FPS Competitive Sub-Tick Stabilizer Pack',
      title: '+250 FPS BOOST',
      speed: '360 Hz LOCKED • 1.2ms',
      badge: 'COMPETITIVE PACK',
      desc: 'Stabilizes 1% lows during heavy smoke utility and 64-player spawn rushes.',
    },
    {
      id: 'fps-500',
      shortActionLabel: '+500 FPS ZE PRO PACK',
      certLabel: '+500 FPS Zombie Escape Boss & Laser Pack',
      title: '+500 FPS ZE PRO',
      speed: '540 Hz LOCKED • 0.4ms',
      badge: 'ZOMBIE ESCAPE PRO',
      desc: 'Deletes particle lag on ze_ffvii_mako_reactor & ze_dark_souls boss fights.',
    },
    {
      id: 'fps-1000',
      shortActionLabel: '+1,000 FPS OVERDRIVE PACK',
      certLabel: '+1,000 FPS Source 3 Quantum Engine Overdrive Pack',
      title: '+1,000 FPS PACK',
      speed: '1,000 Hz SUB-TICK • 0.05ms',
      badge: 'SOURCE 3 ENGINE LEAK',
      desc: "Unlocks Gaben's private Source 3 multi-threaded quantum renderer for 1,000+ FPS.",
    },
    {
      id: 'fps-9999',
      shortActionLabel: '+9,999 FPS QUANTUM PACK',
      certLabel: '+9,999 FPS NASA Time-Travel Tickrate Pack',
      title: '+9,999 FPS NASA',
      speed: '∞ Hz • NEGATIVE LATENCY',
      badge: 'TIME-TRAVEL TICKRATE',
      desc: 'Frames arrive on your monitor 15ms before the CS2 server even calculates them.',
    },
  ],
};

const MODE_META: Record<
  MemePackageMode,
  {
    topPill: string;
    rangeBadge: string;
    heading: string;
    subtitle: string;
    step1Title: string;
    step1Right: string;
    step2Title: string;
    opt1Label: string;
    opt2Label: string;
    idleStatus: string;
    initialLogs: string[];
  }
> = {
  ram: {
    topPill: 'OFFICIAL GERONIMOHQ.COM CLOUD MEMORY GENERATOR',
    rangeBadge: '16GB — 128GB DDR5 / DDR6-X',
    heading: 'DOWNLOAD MORE RAM',
    subtitle:
      "Came here from Geronimo's Discord bio? Why pay $300 for physical RAM sticks when you can download high-frequency DDR5/DDR6 memory directly into your browser!",
    step1Title: 'STEP 1 // SELECT HOW MUCH RAM YOU WANT TO DOWNLOAD (16 GB – 128 GB):',
    step1Right: 'INSTANT CLOUD DIMM TRANSFER',
    step2Title: 'STEP 2 // CONFIGURE MEMORY ENHANCEMENTS:',
    opt1Label: '🌈 Enable ARGB Rainbow Heatsink Overclock (+420% Aura)',
    opt2Label: '🧟 Pre-Load CS2 Zombie Escape Laser-Dodge Memory Timings',
    idleStatus: 'Ready to inject virtual DIMM modules into motherboard...',
    initialLogs: [
      '[SYS.BIOS] GeronimoHQ Cloud-to-DIMM Neural Interface v4.20 initialized.',
      '[MOTHERBOARD] 4x Virtual PCIe 6.0 / DDR6 Memory Slots detected and unlocked.',
    ],
  },
  gpu: {
    topPill: 'OFFICIAL GERONIMOHQ.COM CLOUD GPU ARCHITECT',
    rangeBadge: '32GB — 256GB GDDR7X / HBM3e VRAM',
    heading: 'DOWNLOAD RTX 6090 Ti GPU',
    subtitle:
      'Out of VRAM during 64-player Zombie Escape particle spam? Download an unreleased flagship NVIDIA RTX 6090 Ti architecture straight into your PCIe 6.0 slot!',
    step1Title: 'STEP 1 // SELECT YOUR VIRTUAL RTX 6090 Ti GRAPHICS CARD TIER:',
    step1Right: 'PCIe 6.0 x16 CLOUD BUS READY',
    step2Title: 'STEP 2 // CONFIGURE GPU OVERCLOCK & COOLING:',
    opt1Label: '🔮 Enable DLSS 5.0 "Future-Frame" Time-Travel Prediction (+690% Clarity)',
    opt2Label: '❄️ Inject Virtual Liquid Nitrogen Loop (-196°C Core Temp & Zero Coil Whine)',
    idleStatus: 'Ready to materialize virtual RTX 6090 Ti silicon into PCIe x16 slot...',
    initialLogs: [
      '[NV.CLOUD] GeronimoHQ Blackwell-Ultra Silicon Synthesizer v6.90 initialized.',
      '[PCIE_BUS] Virtual 16-Pin 1,600W Melt-Proof Power Connector locked and ready.',
    ],
  },
  fps: {
    topPill: 'OFFICIAL GERONIMOHQ.COM SOURCE 2 FRAME INJECTOR',
    rangeBadge: '+250 TO +9,999 FPS SUB-TICK BOOST',
    heading: 'DOWNLOAD +1,000 FPS PACK',
    subtitle:
      'Tired of frame drops when 40 humans spam Negevs at the boss? Inject pure cloud-rendered frames and 0.05ms sub-tick registration directly into your monitor!',
    step1Title: 'STEP 1 // SELECT YOUR CLOUD FPS & SUB-TICK BOOSTER TIER:',
    step1Right: '100% PURE CLOUD FRAMES',
    step2Title: 'STEP 2 // CONFIGURE ENGINE & SUB-TICK OVERDRIVE:',
    opt1Label: '⚡ Bypass 64-Tick Limits with 1,024-Tick Quantum Sub-Tick Desubticker',
    opt2Label: '🛡️ Enable Zero-Smoke-Lag & Auto-Laser-Jump Frame Interpolation',
    idleStatus: 'Ready to inject cloud-rendered frames into cs2.exe pipeline...',
    initialLogs: [
      '[SOURCE3.API] GeronimoHQ Quantum Frame-Gen & Sub-Tick Pipeline online.',
      '[MONITOR] Virtual 1,000Hz DisplayPort 3.0 Overdrive link established.',
    ],
  },
};

export const DownloadRamSection: React.FC = () => {
  const [memeMode, setMemeMode] = useState<MemePackageMode>('ram');
  const [selectedTierIdByMode, setSelectedTierIdByMode] = useState<Record<MemePackageMode, string>>({
    ram: 'ram-64',
    gpu: 'gpu-6090-ti',
    fps: 'fps-1000',
  });
  const [isDownloading, setIsDownloading] = useState<boolean>(false);
  const [isCompleted, setIsCompleted] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [statusLine, setStatusLine] = useState<string>(MODE_META.ram.idleStatus);
  const [logs, setLogs] = useState<string[]>(MODE_META.ram.initialLogs);
  const [optRgb, setOptRgb] = useState<boolean>(true);
  const [optBhop, setOptBhop] = useState<boolean>(true);
  const [copiedFlex, setCopiedFlex] = useState<boolean>(false);
  const [isTabHidden, setIsTabHidden] = useState<boolean>(false);
  const timerRef = useRef<number | null>(null);

  // Watch for background tab visibility to pause mini-game and prevent background memory/CPU drain
  useEffect(() => {
    const handleVisibilityChange = () => {
      setIsTabHidden(document.hidden);
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  // Interactive "Dodge the ZE Ending Lasers" Mini-Game State
  const [laserGameActive, setLaserGameActive] = useState(false);
  const [laserGameOver, setLaserGameOver] = useState(false);
  const [playerPose, setPlayerPose] = useState<'stand' | 'jump' | 'crouch'>('stand');
  const [laserScore, setLaserScore] = useState(0);
  const [laserHighScore, setLaserHighScore] = useState(12);
  const [laserBeam, setLaserBeam] = useState<{ x: number; heightType: 'low' | 'high'; speed: number }>({
    x: 100,
    heightType: 'low',
    speed: 3.6,
  });
  const poseRef = useRef<'stand' | 'jump' | 'crouch'>('stand');
  const gameContainerRef = useRef<HTMLDivElement>(null);
  const [isGameInViewport, setIsGameInViewport] = useState<boolean>(true);

  // Pause game when mini-game scrolls out of view
  useEffect(() => {
    const el = gameContainerRef.current;
    if (!el || typeof IntersectionObserver === 'undefined') return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsGameInViewport(entry.isIntersecting);
      },
      { threshold: 0.1 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const currentTiers = TIERS_BY_MODE[memeMode];
  const currentMeta = MODE_META[memeMode];
  const selectedTier =
    currentTiers.find((t) => t.id === selectedTierIdByMode[memeMode]) || currentTiers[1];
  const activePackageLabel = selectedTier.certLabel;

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  // ZE Laser Mini-Game Loop (Automatically pauses when tab is hidden or scrolled out of viewport)
  useEffect(() => {
    if (!laserGameActive || isTabHidden || !isGameInViewport) return;

    const tick = window.setInterval(() => {
      setLaserBeam((prev) => {
        const nextX = prev.x - prev.speed;

        // Check collision window around player (x between 12% and 22%)
        if (nextX <= 21 && nextX >= 12) {
          const currentPose = poseRef.current;
          const dodged =
            (prev.heightType === 'low' && currentPose === 'jump') ||
            (prev.heightType === 'high' && currentPose === 'crouch');

          if (!dodged) {
            setLaserGameActive(false);
            setLaserGameOver(true);
            return prev;
          }
        }

        // Laser passed player cleanly! Spawn next laser faster!
        if (nextX <= 0) {
          setLaserScore((s) => {
            const ns = s + 1;
            setLaserHighScore((h) => Math.max(h, ns));
            return ns;
          });
          return {
            x: 100,
            heightType: Math.random() < 0.55 ? 'low' : 'high',
            speed: Math.min(7.2, prev.speed + 0.18),
          };
        }

        return { ...prev, x: nextX };
      });
    }, 30);

    return () => clearInterval(tick);
  }, [laserGameActive, isTabHidden, isGameInViewport]);

  // Keyboard navigation for laser game (Space/Up = Jump, Down/Ctrl = Crouch)
  // Strictly active ONLY while laserGameActive is true AND visible in viewport, and never hijacks text inputs
  useEffect(() => {
    // Space and arrows act strictly while game is actively running in visible viewport
    if (!laserGameActive || laserGameOver || !isGameInViewport || isTabHidden) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Never hijack keystrokes if the user is typing in any text box or input
      const target = e.target as HTMLElement | null;
      if (
        target &&
        (target.tagName === 'INPUT' ||
          target.tagName === 'TEXTAREA' ||
          target.isContentEditable ||
          target.getAttribute('role') === 'textbox')
      ) {
        return;
      }

      // If user presses Space on a focused button, blur the button and execute the jump
      if (target && target.tagName === 'BUTTON') {
        target.blur();
      }

      if (e.code === 'Space' || e.code === 'ArrowUp' || e.code === 'KeyW') {
        e.preventDefault();
        triggerPose('jump');
      } else if (
        e.code === 'ArrowDown' ||
        e.code === 'KeyS' ||
        e.code === 'ControlLeft' ||
        e.code === 'ControlRight'
      ) {
        e.preventDefault();
        triggerPose('crouch');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [laserGameActive, laserGameOver, isGameInViewport, isTabHidden]);

  const triggerPose = (pose: 'jump' | 'crouch') => {
    poseRef.current = pose;
    setPlayerPose(pose);
    window.setTimeout(() => {
      if (poseRef.current === pose) {
        poseRef.current = 'stand';
        setPlayerPose('stand');
      }
    }, 520);
  };

  const startLaserMiniGame = () => {
    if (typeof document !== 'undefined' && document.activeElement instanceof HTMLElement) {
      document.activeElement.blur();
    }
    poseRef.current = 'stand';
    setPlayerPose('stand');
    setLaserScore(0);
    setLaserGameOver(false);
    setLaserBeam({ x: 100, heightType: 'low', speed: 3.6 });
    setLaserGameActive(true);
  };

  const switchMemeMode = (nextMode: MemePackageMode) => {
    if (timerRef.current) clearInterval(timerRef.current);
    setMemeMode(nextMode);
    setIsDownloading(false);
    setIsCompleted(false);
    setProgress(0);
    setStatusLine(MODE_META[nextMode].idleStatus);
    setLogs(MODE_META[nextMode].initialLogs);
  };

  const startRamDownload = () => {
    if (isDownloading) return;
    setIsDownloading(true);
    setIsCompleted(false);
    setProgress(0);
    setLogs([
      `[START] Requesting ${activePackageLabel} from GeronimoHQ Quantum Cloud...`,
    ]);

    const stages: { pct: number; msg: string }[] =
      memeMode === 'gpu'
        ? [
            { pct: 12, msg: `[PCIE_6.0] Unlocking virtual PCIe 6.0 x16 lane & allocating ${activePackageLabel}...` },
            { pct: 28, msg: `[CUDA_CORES] Materializing 32,768 Blackwell-Ultra Shader Cores & GDDR7X VRAM modules...` },
            { pct: 46, msg: optRgb ? `[DLSS_5.0] Training Neural Time-Travel Frame Predictor (shoots zombies 2 ticks early)...` : `[RAYTRACING] Compiling 16K path-traced Mako Reactor laser reflections...` },
            { pct: 65, msg: optBhop ? `[LN2_COOLING] Flooding virtual GPU waterblock with -196°C Liquid Nitrogen (0 dB coil whine)...` : `[VBIOS] Flashing 4,200 MHz Core Clock Overdrive VBIOS...` },
            { pct: 84, msg: `[BENCHMARK] 3DMark Port Royal Score: 420,069 pts (World Record Verified)...` },
            { pct: 96, msg: `[FINALIZE] Locking 16-pin melt-proof titanium power latch *CLICK*...` },
          ]
        : memeMode === 'fps'
        ? [
            { pct: 12, msg: `[SOURCE_2] Attaching Quantum Frame-Generator to cs2.exe render queue...` },
            { pct: 28, msg: `[SHADERS] Pre-deleting 64-player HE grenade, Molotov & Negev tracer lag spikes...` },
            { pct: 46, msg: optRgb ? `[SUB_TICK] Overclocking 64-tick server packets to 1,024-tick Quantum Desubticker...` : `[RENDERER] Unlocking Gaben's secret Source 3 multi-threaded pipeline...` },
            { pct: 65, msg: optBhop ? `[LASER_SYNC] Calibrating 0.00ms crouch/jump frame interpolation for ZE ending lasers...` : `[1%_LOWS] Locking minimum 1% Low FPS above 999.9 FPS...` },
            { pct: 84, msg: `[TELEMETRY] Frame-time variance stabilized at 0.01ms (Zero choke / 0% loss)...` },
            { pct: 96, msg: `[FINALIZE] Injecting ${activePackageLabel} directly into display refresh buffer...` },
          ]
        : [
            { pct: 12, msg: `[SLOTS] Bypassing physical motherboard limits... Allocating ${activePackageLabel}...` },
            { pct: 28, msg: `[TIMINGS] Soldering cloud capacitors & tightening CAS Latency to 0.01ns...` },
            { pct: 46, msg: optRgb ? `[RGB] Injecting 16.8 Million ARGB Rainbow Wave photons into heatsinks...` : `[COOLING] Flushing liquid nitrogen through virtual heatspreaders...` },
            { pct: 65, msg: optBhop ? `[CS2_ENGINE] Calibrating sub-tick bhop & Zombie Escape laser-dodge memory registers...` : `[XMP_EXPO] Enabling AMD EXPO / Intel XMP 4.0 Overdrive profile...` },
            { pct: 84, msg: `[VERIFY] Running MemTest69-Pro (0 errors found)...` },
            { pct: 96, msg: `[FINALIZE] Sealing PCIe / DIMM latches *CLICK* *CLICK*...` },
          ];

    const triggeredStages = new Set<number>();
    let currentPct = 0;

    timerRef.current = window.setInterval(() => {
      currentPct += Math.floor(Math.random() * 4) + 2;
      if (currentPct >= 100) {
        currentPct = 100;
        if (timerRef.current) clearInterval(timerRef.current);
        setProgress(100);
        setIsDownloading(false);
        setIsCompleted(true);
        const finalMsg = `[SUCCESS] ✅ ${activePackageLabel} DOWNLOADED & INSTALLED SUCCESSFULLY!`;
        setStatusLine(finalMsg);
        setLogs((prev) => [...prev, finalMsg]);

        confetti({
          particleCount: 90,
          spread: 100,
          origin: { y: 0.65 },
          colors: ['#00f0ff', '#39ff14', '#ff007f', '#ffe600'],
          disableForReducedMotion: true,
        });
        return;
      }

      setProgress(currentPct);
      for (const st of stages) {
        if (currentPct >= st.pct && !triggeredStages.has(st.pct)) {
          triggeredStages.add(st.pct);
          setStatusLine(st.msg);
          setLogs((prev) => [...prev.slice(-6), st.msg]);
        }
      }
    }, 130);
  };

  const resetDownload = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    setIsDownloading(false);
    setIsCompleted(false);
    setProgress(0);
    setStatusLine(currentMeta.idleStatus);
    setLogs(currentMeta.initialLogs);
  };

  const copyDiscordFlex = () => {
    const text = `✅ I just downloaded ${activePackageLabel} for free at https://geronimohq.com/#download-ram 💾🚀`;
    navigator.clipboard.writeText(text);
    setCopiedFlex(true);
    setTimeout(() => setCopiedFlex(false), 2500);
  };

  return (
    <section id="download-ram" className="relative w-full max-w-6xl mx-auto px-4 py-12 scroll-mt-28">
      {/* Outer Cyberpunk Container */}
      <div className="relative rounded-2xl border border-lime-500/40 bg-gradient-to-b from-emerald-950/25 via-slate-950/90 to-[#05080f] p-6 md:p-8 shadow-[0_0_50px_rgba(16,185,129,0.15)] overflow-hidden">
        
        {/* Corner Accents */}
        <div className="absolute top-3 left-3 w-5 h-5 border-t-2 border-l-2 border-lime-400/80" />
        <div className="absolute top-3 right-3 w-5 h-5 border-t-2 border-r-2 border-lime-400/80" />
        <div className="absolute bottom-3 left-3 w-5 h-5 border-b-2 border-l-2 border-lime-400/80" />
        <div className="absolute bottom-3 right-3 w-5 h-5 border-b-2 border-r-2 border-lime-400/80" />

        {/* Prominent Satirical Meme Disclaimer Banner */}
        <div className="mb-5 flex items-start gap-2.5 p-3.5 rounded-xl bg-amber-950/40 border border-amber-500/50 text-amber-200 text-xs font-tech">
          <span className="text-base flex-shrink-0">⚠️</span>
          <div>
            <strong className="text-amber-300 font-cyber tracking-wider">OFFICIAL DISCLAIMER:</strong> This is an interactive satirical meme generator. It simulates virtual hardware installation directly in your browser. <span className="text-white font-bold underline underline-offset-2">Zero files are downloaded</span> and zero real PC changes occur.
          </div>
        </div>

        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4 mb-5 border-b border-lime-500/30 pb-4">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 text-[10px] font-code rounded bg-lime-950/90 text-lime-300 border border-lime-500/50">
                {currentMeta.topPill}
              </span>
              <span className="px-2.5 py-0.5 text-[10px] font-code font-bold rounded bg-slate-900 text-cyan-300 border border-cyan-500/50">
                {currentMeta.rangeBadge}
              </span>
              <span className="text-[11px] font-code text-lime-400">
                100% FREE DEDOTATED WAM
              </span>
            </div>
            <h2 className="text-2xl md:text-3xl font-cyber font-black text-white tracking-wider flex items-center gap-3">
              <Cpu className="w-7 h-7 text-lime-400 animate-pulse flex-shrink-0" />
              <span>{currentMeta.heading}</span>
            </h2>
            <p className="text-sm font-tech text-slate-300 mt-1 max-w-2xl">
              {currentMeta.subtitle}
            </p>
          </div>

          {/* Bonus Cloud Hardware Mode Switcher */}
          <div className="flex flex-wrap items-center gap-1.5 bg-slate-900/90 p-1.5 rounded-xl border border-slate-800 flex-shrink-0 self-start lg:self-end">
            <button
              onClick={() => switchMemeMode('ram')}
              title="Switch meme generator to virtual DDR5/DDR6 system RAM mode (16 GB - 128 GB)"
              aria-label="Switch to RAM mode"
              className={`px-3 py-2 min-h-[44px] rounded-lg text-xs font-code font-bold cursor-pointer transition-all touch-manipulation ${
                memeMode === 'ram'
                  ? 'bg-lime-500/20 text-lime-300 border border-lime-400/60 shadow-[0_0_12px_rgba(57,255,20,0.25)]'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              💾 FREE RAM (16-128GB)
            </button>
            <button
              onClick={() => switchMemeMode('gpu')}
              title="Switch meme generator to unreleased NVIDIA RTX 6090 Ti GPU mode (32 GB - 256 GB)"
              aria-label="Switch to GPU mode"
              className={`px-3 py-2 min-h-[44px] rounded-lg text-xs font-code font-bold cursor-pointer transition-all touch-manipulation ${
                memeMode === 'gpu'
                  ? 'bg-fuchsia-500/20 text-fuchsia-300 border border-fuchsia-400/60 shadow-[0_0_12px_rgba(255,0,127,0.25)]'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              🎮 RTX 6090 Ti
            </button>
            <button
              onClick={() => switchMemeMode('fps')}
              title="Switch meme generator to Source 2 quantum frame-booster mode (+250 to +9,999 FPS)"
              aria-label="Switch to FPS mode"
              className={`px-3 py-2 min-h-[44px] rounded-lg text-xs font-code font-bold cursor-pointer transition-all touch-manipulation ${
                memeMode === 'fps'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/60 shadow-[0_0_12px_rgba(0,240,255,0.25)]'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              ⚡ +1,000 FPS PACK
            </button>
          </div>
        </div>

        {/* Step 1: Select Hardware Tier (Dynamic per Mode: RAM / RTX 6090 Ti / +1,000 FPS Pack) */}
        <div className="mb-6">
          <div className="text-xs font-code text-slate-400 uppercase tracking-wider mb-3 flex flex-wrap items-center justify-between gap-2">
            <span>{currentMeta.step1Title}</span>
            <span className="text-lime-400">{currentMeta.step1Right}</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
            {currentTiers.map((tier) => {
              const isSelected = selectedTier.id === tier.id;
              const activeCardColors =
                memeMode === 'gpu'
                  ? 'bg-gradient-to-br from-fuchsia-950/80 via-slate-900 to-cyan-950/60 border-fuchsia-400 shadow-[0_0_25px_rgba(255,0,127,0.3)] scale-[1.02]'
                  : memeMode === 'fps'
                  ? 'bg-gradient-to-br from-cyan-950/80 via-slate-900 to-lime-950/60 border-cyan-400 shadow-[0_0_25px_rgba(0,240,255,0.3)] scale-[1.02]'
                  : 'bg-gradient-to-br from-lime-950/80 via-slate-900 to-cyan-950/60 border-lime-400 shadow-[0_0_25px_rgba(57,255,20,0.3)] scale-[1.02]';
              const badgeColors =
                memeMode === 'gpu'
                  ? 'text-fuchsia-300 border-fuchsia-500/40'
                  : memeMode === 'fps'
                  ? 'text-cyan-300 border-cyan-500/40'
                  : 'text-lime-300 border-lime-500/40';
              const dotColor =
                memeMode === 'gpu'
                  ? 'bg-fuchsia-400'
                  : memeMode === 'fps'
                  ? 'bg-cyan-400'
                  : 'bg-lime-400';

              return (
                <button
                  key={tier.id}
                  disabled={isDownloading}
                  onClick={() => {
                    setSelectedTierIdByMode((prev) => ({
                      ...prev,
                      [memeMode]: tier.id,
                    }));
                    if (isCompleted) setIsCompleted(false);
                  }}
                  title={`Select ${tier.title} (${tier.speed}) - ${tier.badge}`}
                  aria-label={`Select ${tier.title}`}
                  className={`text-left p-4 rounded-xl border transition-all cursor-pointer flex flex-col justify-between touch-manipulation min-h-[44px] ${
                    isSelected
                      ? activeCardColors
                      : 'bg-slate-900/60 border-slate-800 hover:border-slate-600 text-slate-300'
                  } ${isDownloading ? 'opacity-60 cursor-not-allowed' : ''}`}
                >
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <span className={`text-[10px] font-code px-2 py-0.5 rounded bg-slate-950 border ${badgeColors}`}>
                        {tier.badge}
                      </span>
                      {isSelected && (
                        <span className={`w-2.5 h-2.5 rounded-full animate-ping ${dotColor}`} />
                      )}
                    </div>
                    <div className="text-xl xl:text-2xl font-cyber font-black text-white">
                      {tier.title}
                    </div>
                    <div className="text-xs font-code text-cyan-300 mt-0.5">
                      {tier.speed}
                    </div>
                  </div>
                  <p className="text-xs font-tech text-slate-400 mt-3 leading-relaxed">
                    {tier.desc}
                  </p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Step 2: Optional Meme Boosters & Download Trigger */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center bg-slate-900/75 border border-slate-800 rounded-xl p-5">
          
          {/* Left: Toggles & Action Button (5 cols) */}
          <div className="lg:col-span-5 flex flex-col gap-3">
            <div className="text-xs font-code text-slate-300 font-bold uppercase">
              {currentMeta.step2Title}
            </div>

            <label
              title="Simulate ARGB rainbow heatsink lighting and visual boost (+420% Aura)"
              className="flex items-center gap-2.5 text-xs font-tech text-slate-300 cursor-pointer select-none min-h-[44px]"
            >
              <input
                type="checkbox"
                checked={optRgb}
                disabled={isDownloading}
                onChange={(e) => setOptRgb(e.target.checked)}
                className="w-4 h-4 accent-lime-400 rounded cursor-pointer flex-shrink-0"
              />
              <span>{currentMeta.opt1Label}</span>
            </label>

            <label
              title="Simulate sub-tick timing calibration for Zombie Escape lasers"
              className="flex items-center gap-2.5 text-xs font-tech text-slate-300 cursor-pointer select-none min-h-[44px]"
            >
              <input
                type="checkbox"
                checked={optBhop}
                disabled={isDownloading}
                onChange={(e) => setOptBhop(e.target.checked)}
                className="w-4 h-4 accent-cyan-400 rounded cursor-pointer flex-shrink-0"
              />
              <span>{currentMeta.opt2Label}</span>
            </label>

            <div className="pt-2 flex flex-wrap items-center gap-3">
              {!isCompleted ? (
                <button
                  onClick={startRamDownload}
                  disabled={isDownloading}
                  title={`Simulate downloading and installing ${selectedTier.shortActionLabel} in your browser`}
                  className={`w-full sm:w-auto flex items-center justify-center gap-2.5 px-6 py-3.5 min-h-[44px] rounded-xl font-cyber text-xs md:text-sm font-black tracking-wider transition-all cursor-pointer touch-manipulation ${
                    isDownloading
                      ? 'bg-amber-600/80 text-white border border-amber-400 animate-pulse cursor-wait'
                      : 'bg-gradient-to-r from-lime-500 via-emerald-500 to-cyan-500 hover:from-lime-400 hover:to-cyan-400 text-slate-950 shadow-[0_0_25px_rgba(57,255,20,0.5)] transform hover:-translate-y-0.5'
                  }`}
                >
                  <Download className={`w-4 h-4 ${isDownloading ? 'animate-bounce' : ''}`} />
                  <span>
                    {isDownloading
                      ? `DOWNLOADING (${progress}%)...`
                      : `DOWNLOAD ${selectedTier.shortActionLabel} NOW`}
                  </span>
                </button>
              ) : (
                <div className="flex flex-wrap items-center gap-2.5 w-full">
                  <button
                    onClick={copyDiscordFlex}
                    title="Copy meme verification text to clipboard for Discord flex"
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-3 min-h-[44px] rounded-xl bg-lime-500 hover:bg-lime-400 text-slate-950 font-cyber text-xs font-black tracking-wider shadow-[0_0_20px_rgba(57,255,20,0.5)] cursor-pointer transition-all touch-manipulation"
                  >
                    {copiedFlex ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    <span>{copiedFlex ? 'COPIED DISCORD FLEX!' : 'COPY CERTIFICATE FOR DISCORD'}</span>
                  </button>
                  <button
                    onClick={resetDownload}
                    title="Reset meme hardware download generator to start over"
                    className="px-3.5 py-3 min-h-[44px] rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-code text-xs flex items-center gap-1.5 cursor-pointer transition-all touch-manipulation"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>MORE</span>
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Right: Interactive Progress Bar & Live Terminal Output (7 cols) */}
          <div className="lg:col-span-7 flex flex-col gap-3 bg-slate-950/95 border border-slate-800 rounded-xl p-4">
            <div className="flex items-center justify-between text-xs font-code">
              <span className="text-cyan-300 flex items-center gap-1.5">
                <Terminal className="w-3.5 h-3.5 text-lime-400" />
                {isCompleted
                  ? 'STATUS: CLOUD HARDWARE INSTALLED SUCCESSFULLY!'
                  : isDownloading
                  ? 'STATUS: INJECTING VIRTUAL HARDWARE INTO MOTHERBOARD...'
                  : 'STATUS: AWAITING USER COMMAND'}
              </span>
              <span className="text-lime-400 font-bold">{progress}%</span>
            </div>

            {/* Progress Bar Track */}
            <div className="w-full h-5 rounded-lg bg-slate-900 border border-slate-800 overflow-hidden p-0.5">
              <div
                className={`h-full rounded transition-all duration-150 ${
                  isCompleted
                    ? 'bg-gradient-to-r from-lime-400 via-emerald-400 to-cyan-400 shadow-[0_0_15px_rgba(57,255,20,0.8)]'
                    : 'bg-gradient-to-r from-cyan-500 via-fuchsia-500 to-lime-400'
                }`}
                style={{ width: `${progress}%` }}
              />
            </div>

            {/* Success Banner when finished */}
            {isCompleted && (
              <div className="flex items-center gap-3 p-3 rounded-lg bg-lime-950/80 border border-lime-400/70 text-lime-200 animate-fadeIn">
                <CheckCircle2 className="w-6 h-6 text-lime-400 flex-shrink-0" />
                <div className="text-xs font-tech">
                  <div className="font-cyber font-bold text-lime-300 text-sm">
                    🎉 {activePackageLabel} DOWNLOADED SUCCESSFULLY!
                  </div>
                  <div>
                    Your PC now has <strong className="text-white">{activePackageLabel}</strong> of pure virtual meme power. Zero actual files were downloaded to your disk!
                  </div>
                </div>
              </div>
            )}

            {/* Terminal Log Lines */}
            <div className="font-code text-[11px] text-slate-400 space-y-1 max-h-28 overflow-y-auto pr-1">
              {logs.map((line, i) => (
                <div
                  key={i}
                  className={
                    line.includes('[SUCCESS]')
                      ? 'text-lime-400 font-bold'
                      : line.includes('[START]')
                      ? 'text-cyan-300'
                      : 'text-slate-400'
                  }
                >
                  &gt; {line}
                </div>
              ))}
              {!isCompleted && (
                <div className="text-cyan-400/80 animate-pulse">&gt; {statusLine}</div>
              )}
            </div>
          </div>

        </div>

        {/* BONUS INTERACTIVE MINI-GAME: DODGE THE ZE ENDING LASERS! */}
        <div ref={gameContainerRef} className="mt-6 rounded-xl border border-fuchsia-500/40 bg-slate-950/90 p-4">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
            <div className="flex items-center gap-2">
              <Gamepad2 className="w-5 h-5 text-fuchsia-400" />
              <span className="font-cyber text-xs md:text-sm font-black text-white tracking-wider">
                MINI-GAME: DODGE THE MAKO REACTOR ENDING LASERS!
              </span>
              <span className="text-[10px] font-code px-2 py-0.5 rounded bg-fuchsia-950 text-fuchsia-300 border border-fuchsia-500/50">
                PEPE &amp; BANANA ARCADE
              </span>
            </div>
            <div className="flex items-center gap-3 text-xs font-code">
              <span className="text-cyan-300">
                LASERS DODGED: <strong className="text-white">{laserScore}</strong>
              </span>
              <span className="text-amber-300 flex items-center gap-1">
                <Trophy className="w-3.5 h-3.5 text-amber-400" /> BEST: <strong>{laserHighScore}</strong>
              </span>
            </div>
          </div>

          {/* Laser Corridor Arena */}
          <div className="relative w-full h-32 rounded-lg bg-[#040711] border border-slate-800 overflow-hidden flex items-center px-4">
            {/* Bridge Floor Line */}
            <div className="absolute bottom-3 inset-x-0 h-0.5 bg-cyan-500/40" />

            {/* Player Character (Pepe/Banana) at X=16% */}
            <div
              className={`absolute left-[15%] transition-all duration-150 select-none text-2xl ${
                playerPose === 'jump'
                  ? 'bottom-14 scale-110'
                  : playerPose === 'crouch'
                  ? 'bottom-2 scale-y-50'
                  : 'bottom-3'
              }`}
            >
              🐸🍌
            </div>

            {/* Incoming Laser Beam */}
            {laserGameActive && (
              <div
                style={{ left: `${laserBeam.x}%` }}
                className={`absolute w-8 h-2.5 rounded-full shadow-[0_0_18px_rgba(0,240,255,0.95)] ${
                  laserBeam.heightType === 'low'
                    ? 'bottom-4 bg-cyan-400 border border-white'
                    : 'bottom-11 bg-fuchsia-500 border border-white'
                }`}
              />
            )}

            {/* Overlay Controls / Start Prompt */}
            {!laserGameActive && (
              <div className="relative z-10 w-full flex flex-col sm:flex-row items-center justify-between gap-2 bg-slate-950/85 px-4 py-2.5 rounded-lg border border-slate-800">
                <div className="text-xs font-tech text-slate-300">
                  {laserGameOver ? (
                    <span className="text-red-400 font-bold">
                      💥 SLICED BY SEPHIROTH LASER! Score: {laserScore} lasers dodged.
                    </span>
                  ) : (
                    <span>
                      Jump over <strong className="text-cyan-300">LOW CYAN LASERS</strong> &amp; Crouch under{' '}
                      <strong className="text-fuchsia-300">HIGH PINK LASERS</strong>!
                    </span>
                  )}
                  <span className="hidden md:inline text-slate-400 text-[11px] ml-2">
                    (Keyboard: <kbd className="px-1 py-0.5 rounded bg-slate-800 border border-slate-700">Space</kbd> / <kbd className="px-1 py-0.5 rounded bg-slate-800 border border-slate-700">↑</kbd> to Jump &bull; <kbd className="px-1 py-0.5 rounded bg-slate-800 border border-slate-700">↓</kbd> / <kbd className="px-1 py-0.5 rounded bg-slate-800 border border-slate-700">Ctrl</kbd> to Crouch)
                  </span>
                </div>
                <button
                  onClick={startLaserMiniGame}
                  title="Start Mako Reactor laser dodging training mini-game"
                  className="px-5 py-2.5 min-h-[44px] rounded-lg bg-fuchsia-600 hover:bg-fuchsia-500 text-white font-cyber text-xs font-bold cursor-pointer shadow-[0_0_15px_rgba(255,0,127,0.4)] touch-manipulation"
                >
                  {laserGameOver ? '🔄 PLAY AGAIN' : '▶ START LASER TRAINING'}
                </button>
              </div>
            )}
          </div>

          {/* On-Screen Mobile Touch & Desktop Interactive Controls */}
          {laserGameActive && (
            <div className="mt-3 flex flex-wrap items-center justify-between gap-2 p-2 rounded-lg bg-slate-900/80 border border-slate-800">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => triggerPose('jump')}
                  title="Jump over low cyan lasers (or press Space / Up Arrow)"
                  className="px-4 py-2.5 min-h-[44px] min-w-[120px] rounded-lg bg-cyan-500 hover:bg-cyan-400 active:bg-cyan-600 text-slate-950 font-cyber text-xs font-black cursor-pointer shadow-[0_0_12px_rgba(0,240,255,0.4)] touch-manipulation"
                >
                  ⬆ JUMP (LOW)
                </button>
                <button
                  onClick={() => triggerPose('crouch')}
                  title="Crouch under high pink lasers (or press Down Arrow / Ctrl)"
                  className="px-4 py-2.5 min-h-[44px] min-w-[120px] rounded-lg bg-fuchsia-500 hover:bg-fuchsia-400 active:bg-fuchsia-600 text-white font-cyber text-xs font-black cursor-pointer shadow-[0_0_12px_rgba(255,0,127,0.4)] touch-manipulation"
                >
                  ⬇ CROUCH (HIGH)
                </button>
              </div>
              <div className="flex items-center gap-2">
                <span className="hidden sm:inline text-[11px] font-code text-slate-400">
                  Tab auto-pauses when backgrounded
                </span>
                <button
                  onClick={startLaserMiniGame}
                  title="Restart laser dodging mini-game from 0"
                  className="px-3.5 py-2.5 min-h-[44px] rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-code text-xs flex items-center gap-1.5 cursor-pointer touch-manipulation"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>🔄 RESTART</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Bottom Meme Disclaimer */}
        <div className="mt-4 p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-2 text-[11px] font-code text-slate-400">
          <span className="flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-lime-400" />
            <span>MEME GENERATOR // BROWSER-ONLY SIMULATION (DOWNLOADS 0 REAL BYTES)</span>
          </span>
          <span className="text-slate-500">GERONIMOHQ.COM // DISCORD BIO VERIFIED</span>
        </div>
      </div>
    </section>
  );
};
