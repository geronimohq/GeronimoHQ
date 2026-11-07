import React, { useState, useEffect, useRef } from 'react';
import confetti from 'canvas-confetti';
import { Cpu, Download, CheckCircle2, Sparkles, Terminal, RotateCcw, Copy, Check } from 'lucide-react';

interface RamTier {
  gb: number;
  title: string;
  speed: string;
  badge: string;
  desc: string;
  color: string;
}

const RAM_TIERS: RamTier[] = [
  {
    gb: 16,
    title: '16 GB DDR5',
    speed: '6000 MT/s CL30',
    badge: 'STARTER PACK',
    desc: 'Enough to open 3 Chrome tabs and Counter-Strike 2 simultaneously.',
    color: 'cyan',
  },
  {
    gb: 32,
    title: '32 GB DDR5',
    speed: '7200 MT/s CL28',
    badge: 'GAMER SWEETSPOT',
    desc: 'Zero stutter when 60 players throw HE grenades on GFL Zombie Escape.',
    color: 'lime',
  },
  {
    gb: 64,
    title: '64 GB DDR5',
    speed: '8000 MT/s CL26',
    badge: 'WORKSTATION CHAD',
    desc: 'Download enough dedotated WAM to host your own Minecraft + CS2 cluster.',
    color: 'fuchsia',
  },
  {
    gb: 128,
    title: '128 GB DDR6-X',
    speed: '12,800 MT/s CL14',
    badge: 'NASA QUANTUM OVERKILL',
    desc: 'Directly links your motherboard to the Pentagon satellite array.',
    color: 'amber',
  },
];

export const DownloadRamSection: React.FC = () => {
  const [selectedGb, setSelectedGb] = useState<number>(64);
  const [isDownloading, setIsDownloading] = useState<boolean>(false);
  const [isCompleted, setIsCompleted] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [statusLine, setStatusLine] = useState<string>('Ready to inject virtual DIMM modules into motherboard...');
  const [logs, setLogs] = useState<string[]>([
    '[SYS.BIOS] GeronimoHQ Cloud-to-DIMM Neural Interface v4.20 initialized.',
    '[MOTHERBOARD] 4x Virtual PCIe 6.0 Memory Slots detected and unlocked.',
  ]);
  const [optRgb, setOptRgb] = useState<boolean>(true);
  const [optBhop, setOptBhop] = useState<boolean>(true);
  const [copiedFlex, setCopiedFlex] = useState<boolean>(false);
  const timerRef = useRef<number | null>(null);

  const selectedTier = RAM_TIERS.find((t) => t.gb === selectedGb) || RAM_TIERS[2];

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  const startRamDownload = () => {
    if (isDownloading) return;
    setIsDownloading(true);
    setIsCompleted(false);
    setProgress(0);
    setLogs([
      `[START] Requesting ${selectedTier.gb} GB (${selectedTier.speed}) from GeronimoHQ Quantum Cloud...`,
    ]);

    const stages: { pct: number; msg: string }[] = [
      { pct: 12, msg: `[SLOTS] Bypassing physical motherboard limits... Allocating ${selectedTier.gb} GB Virtual DIMMs...` },
      { pct: 28, msg: `[TIMINGS] Soldering cloud capacitors & tightening CAS Latency to ${selectedTier.speed}...` },
      { pct: 46, msg: optRgb ? `[RGB] Injecting 16.8 Million ARGB Rainbow Wave photons into RAM heatsinks...` : `[COOLING] Flushing liquid nitrogen through virtual heatspreaders...` },
      { pct: 65, msg: optBhop ? `[CS2_ENGINE] Calibrating sub-tick bhop & Zombie Escape laser-dodge memory registers...` : `[XMP_EXPO] Enabling AMD EXPO / Intel XMP 4.0 Overdrive profile...` },
      { pct: 84, msg: `[VERIFY] Running MemTest69-Pro (0 errors found across ${selectedTier.gb * 1024} MB)...` },
      { pct: 96, msg: `[FINALIZE] Sealing DIMM latches *CLICK* *CLICK*...` },
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
        const finalMsg = `[SUCCESS] ✅ ${selectedTier.gb} GB RAM DOWNLOADED & INSTALLED SUCCESSFULLY!`;
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
    setStatusLine('Ready to inject virtual DIMM modules into motherboard...');
  };

  const copyDiscordFlex = () => {
    const text = `✅ I just downloaded ${selectedTier.gb} GB of ${selectedTier.speed} RAM for free at https://geronimohq.com/#download-ram 💾🚀`;
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

        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-6 border-b border-lime-500/30 pb-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="px-2.5 py-0.5 text-[10px] font-code rounded bg-lime-950/90 text-lime-300 border border-lime-500/50">
                OFFICIAL GERONIMOHQ.COM CLOUD MEMORY GENERATOR
              </span>
              <span className="text-xs font-code text-cyan-400">
                100% FREE DEDOTATED WAM
              </span>
            </div>
            <h2 className="text-2xl md:text-3xl font-cyber font-black text-white tracking-wider flex items-center gap-3">
              <Cpu className="w-7 h-7 text-lime-400 animate-pulse" />
              <span>DOWNLOAD MORE RAM</span>
              <span className="text-xs font-code px-2 py-0.5 bg-lime-950 text-lime-300 border border-lime-400/60 rounded">
                16GB — 128GB
              </span>
            </h2>
            <p className="text-sm font-tech text-slate-300 mt-1 max-w-2xl">
              Came here from Geronimo&apos;s Discord bio? Why pay $300 for physical RAM sticks when you can download high-frequency DDR5/DDR6 memory directly into your browser!
            </p>
          </div>

          <div className="text-left md:text-right font-code text-xs text-slate-400 bg-slate-900/90 px-3.5 py-2 rounded-xl border border-slate-800">
            <div>SELECTED CAPACITY: <span className="text-lime-400 font-bold">{selectedTier.gb} GB</span></div>
            <div>SPEED PROFILE: <span className="text-cyan-300">{selectedTier.speed}</span></div>
          </div>
        </div>

        {/* Step 1: Select RAM Capacity (16 GB to 128 GB) */}
        <div className="mb-6">
          <div className="text-xs font-code text-slate-400 uppercase tracking-wider mb-3 flex items-center justify-between">
            <span>STEP 1 // SELECT HOW MUCH RAM YOU WANT TO DOWNLOAD (16 GB – 128 GB):</span>
            <span className="text-lime-400">INSTANT CLOUD TRANSFER</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
            {RAM_TIERS.map((tier) => {
              const isSelected = selectedGb === tier.gb;
              return (
                <button
                  key={tier.gb}
                  disabled={isDownloading}
                  onClick={() => {
                    setSelectedGb(tier.gb);
                    if (isCompleted) setIsCompleted(false);
                  }}
                  className={`text-left p-4 rounded-xl border transition-all cursor-pointer flex flex-col justify-between ${
                    isSelected
                      ? 'bg-gradient-to-br from-lime-950/80 via-slate-900 to-cyan-950/60 border-lime-400 shadow-[0_0_25px_rgba(57,255,20,0.3)] scale-[1.02]'
                      : 'bg-slate-900/60 border-slate-800 hover:border-slate-600 text-slate-300'
                  } ${isDownloading ? 'opacity-60 cursor-not-allowed' : ''}`}
                >
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <span className="text-[10px] font-code px-2 py-0.5 rounded bg-slate-950 text-lime-300 border border-lime-500/40">
                        {tier.badge}
                      </span>
                      {isSelected && (
                        <span className="w-2.5 h-2.5 rounded-full bg-lime-400 animate-ping" />
                      )}
                    </div>
                    <div className="text-2xl font-cyber font-black text-white">
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
              STEP 2 // CONFIGURE MEMORY ENHANCEMENTS:
            </div>

            <label className="flex items-center gap-2.5 text-xs font-tech text-slate-300 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={optRgb}
                disabled={isDownloading}
                onChange={(e) => setOptRgb(e.target.checked)}
                className="w-4 h-4 accent-lime-400 rounded cursor-pointer"
              />
              <span>🌈 Enable ARGB Rainbow Heatsink Overclock (+420% Aura)</span>
            </label>

            <label className="flex items-center gap-2.5 text-xs font-tech text-slate-300 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={optBhop}
                disabled={isDownloading}
                onChange={(e) => setOptBhop(e.target.checked)}
                className="w-4 h-4 accent-cyan-400 rounded cursor-pointer"
              />
              <span>🧟 Pre-Load CS2 Zombie Escape Laser-Dodge Timings</span>
            </label>

            <div className="pt-2 flex flex-wrap items-center gap-3">
              {!isCompleted ? (
                <button
                  onClick={startRamDownload}
                  disabled={isDownloading}
                  className={`w-full sm:w-auto flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-xl font-cyber text-xs md:text-sm font-black tracking-wider transition-all cursor-pointer ${
                    isDownloading
                      ? 'bg-amber-600/80 text-white border border-amber-400 animate-pulse cursor-wait'
                      : 'bg-gradient-to-r from-lime-500 via-emerald-500 to-cyan-500 hover:from-lime-400 hover:to-cyan-400 text-slate-950 shadow-[0_0_25px_rgba(57,255,20,0.5)] transform hover:-translate-y-0.5'
                  }`}
                >
                  <Download className={`w-4 h-4 ${isDownloading ? 'animate-bounce' : ''}`} />
                  <span>
                    {isDownloading
                      ? `DOWNLOADING ${selectedTier.gb} GB RAM (${progress}%)...`
                      : `DOWNLOAD ${selectedTier.gb} GB RAM NOW`}
                  </span>
                </button>
              ) : (
                <div className="flex flex-wrap items-center gap-2.5 w-full">
                  <button
                    onClick={copyDiscordFlex}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-lime-500 hover:bg-lime-400 text-slate-950 font-cyber text-xs font-black tracking-wider shadow-[0_0_20px_rgba(57,255,20,0.5)] cursor-pointer transition-all"
                  >
                    {copiedFlex ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    <span>{copiedFlex ? 'COPIED DISCORD FLEX!' : 'COPY CERTIFICATE FOR DISCORD'}</span>
                  </button>
                  <button
                    onClick={resetDownload}
                    className="px-3.5 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-code text-xs flex items-center gap-1.5 cursor-pointer transition-all"
                    title="Download even more RAM"
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
                  ? 'STATUS: RAM DOWNLOADED SUCCESSFULLY!'
                  : isDownloading
                  ? 'STATUS: INJECTING CLOUD RAM INTO DIMM SLOTS...'
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
                    🎉 RAM DOWNLOADED SUCCESSFULLY! (+{selectedTier.gb} GB INSTALLED)
                  </div>
                  <div>
                    Your PC now has <strong className="text-white">+{selectedTier.gb} GB ({selectedTier.speed})</strong> of pure virtual meme power. Zero actual files were downloaded to your disk!
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

        {/* Bottom Meme Disclaimer */}
        <div className="mt-3 flex items-center justify-between text-[10px] font-code text-slate-500">
          <span className="flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-lime-400" />
            MEME MODULE // PURELY INTERACTIVE BROWSER UI (NO ACTUAL FILE DOWNLOAD)
          </span>
          <span>DISCORD BIO VERIFIED: GERONIMOHQ.COM</span>
        </div>
      </div>
    </section>
  );
};
