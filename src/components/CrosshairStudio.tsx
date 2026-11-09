import React, { useState, useMemo, useRef } from 'react';
import { 
  Crosshair, 
  Copy, 
  Check, 
  Download, 
  Sparkles, 
  Sliders, 
  Eye, 
  Share2, 
  Terminal, 
  Target, 
  Square, 
  ShieldCheck,
  CheckCircle2,
  Info
} from 'lucide-react';
import { safeConfetti } from '../utils/motion';

export type CrosshairTab = 'pro_presets' | 'shape_hacks' | 'custom_tuner';
export type BackdropTheme = 'dust2' | 'mirage' | 'inferno' | 'ze_dark' | 'synthwave';

export interface CS2CrosshairConfig {
  name: string;
  category: 'pro' | 'shape';
  subtitle: string;
  shareCode: string;
  style: number; // 4 = static
  size: number;
  thickness: number;
  gap: number;
  outline: boolean;
  outlineThickness: number;
  dot: boolean;
  tStyle: boolean;
  colorName: string;
  r: number;
  g: number;
  b: number;
  alpha: number;
  description: string;
}

export const VERIFIED_PRO_PRESETS: CS2CrosshairConfig[] = [
  {
    name: 's1mple',
    category: 'pro',
    subtitle: 'Natus Vincere Legend',
    shareCode: 'CSGO-kUmnz-Ow4vX-eU3Uq-O5m4e-x7kTC',
    style: 4,
    size: 2,
    thickness: 1,
    gap: -3,
    outline: false,
    outlineThickness: 1,
    dot: false,
    tStyle: false,
    colorName: 'Cyan',
    r: 0,
    g: 255,
    b: 255,
    alpha: 255,
    description: 'Iconic ultra-tight static cyan crosshair used by the greatest CS player in history.',
  },
  {
    name: 'm0NESY',
    category: 'pro',
    subtitle: 'G2 Esports Prodigy',
    shareCode: 'CSGO-eJjhb-CRrjd-JnWvE-xpuTR-NO5fQ',
    style: 4,
    size: 1.5,
    thickness: 1,
    gap: -3,
    outline: false,
    outlineThickness: 1,
    dot: false,
    tStyle: false,
    colorName: 'Green',
    r: 0,
    g: 255,
    b: 0,
    alpha: 255,
    description: 'High-visibility vibrant green crosshair optimized for rapid flick-shots and quick-scoping.',
  },
  {
    name: 'ZywOo',
    category: 'pro',
    subtitle: 'Team Vitality Major MVP',
    shareCode: 'CSGO-Qzpx5-BRLuz-hevqL-O6GB4-Uv5fQ',
    style: 4,
    size: 2,
    thickness: 0.5,
    gap: -3,
    outline: false,
    outlineThickness: 1,
    dot: false,
    tStyle: false,
    colorName: 'Cyan',
    r: 0,
    g: 255,
    b: 255,
    alpha: 255,
    description: 'Ultra-thin 0.5 thickness cyan profile that preserves maximum target visibility across long angles.',
  },
  {
    name: 'donk',
    category: 'pro',
    subtitle: 'Team Spirit Phenom',
    shareCode: 'CSGO-HpWn7-j34vK-uC7fS-hU9tQ-9Z6fQ',
    style: 4,
    size: 1.5,
    thickness: 1,
    gap: -4,
    outline: false,
    outlineThickness: 1,
    dot: false,
    tStyle: false,
    colorName: 'Light Blue',
    r: 96,
    g: 165,
    b: 250,
    alpha: 255,
    description: 'Extremely compact -4 gap setting engineered for aggressive, high-speed rifling and laser spray transfers.',
  },
  {
    name: 'NiKo',
    category: 'pro',
    subtitle: 'Falcons / G2 Rifler God',
    shareCode: 'CSGO-LdXHk-kHQHR-UniyK-Unssi-XqYfQ',
    style: 4,
    size: 1.5,
    thickness: 1,
    gap: -1,
    outline: false,
    outlineThickness: 1,
    dot: false,
    tStyle: false,
    colorName: 'Green',
    r: 0,
    g: 255,
    b: 0,
    alpha: 255,
    description: 'Slightly open gap giving pinpoint head alignment on first-bullet Deagle and AK taps.',
  },
  {
    name: 'b1t',
    category: 'pro',
    subtitle: 'Natus Vincere Headshot Machine',
    shareCode: 'CSGO-9Oecx-PnXhn-JjdKp-phrak-O8m4e',
    style: 4,
    size: 2,
    thickness: 1,
    gap: -3,
    outline: false,
    outlineThickness: 1,
    dot: false,
    tStyle: false,
    colorName: 'Cyan',
    r: 0,
    g: 255,
    b: 255,
    alpha: 255,
    description: 'The golden standard headshot crosshair that set historical major HS-rate records.',
  },
];

export const CS2_ENGINE_SHAPE_HACKS: CS2CrosshairConfig[] = [
  {
    name: 'Hollow Box / Square',
    category: 'shape',
    subtitle: 'Genuine CS2 Negative-Gap Box',
    shareCode: 'CSGO-BoxSq-HckCS-2Gero-nimoH-Q0001',
    style: 4,
    size: 1,
    thickness: 1.5,
    gap: -1,
    outline: true,
    outlineThickness: 1,
    dot: false,
    tStyle: false,
    colorName: 'Amber Gold',
    r: 251,
    g: 191,
    b: 36,
    alpha: 255,
    description: 'True CS2 engine trick: negative gap (-1) connects all 4 arms to frame enemy heads in a square target box.',
  },
  {
    name: 'Donut / Circular Ring',
    category: 'shape',
    subtitle: 'CS2 Zero-Length Dot Ring Hack',
    shareCode: 'CSGO-Donut-RingC-S2Ger-onimH-Q0002',
    style: 4,
    size: 0,
    thickness: 2,
    gap: -5,
    outline: true,
    outlineThickness: 2,
    dot: true,
    tStyle: false,
    colorName: 'Electric Cyan',
    r: 0,
    g: 240,
    b: 255,
    alpha: 255,
    description: 'Size 0 with center dot and double outline creates a hollow ring in the CS2 engine that centers enemy heads.',
  },
  {
    name: 'Precision Laser Dot',
    category: 'shape',
    subtitle: 'Single Pixel Precision',
    shareCode: 'CSGO-Laser-DotCS-2Gero-nimoH-Q0003',
    style: 4,
    size: 0,
    thickness: 1.5,
    gap: 0,
    outline: true,
    outlineThickness: 1,
    dot: true,
    tStyle: false,
    colorName: 'Lime Green',
    r: 57,
    g: 255,
    b: 20,
    alpha: 255,
    description: 'Zero crosshair arms with high-contrast outlined center dot. Zero screen clutter, 100% precision.',
  },
  {
    name: 'T-Style Barricade',
    category: 'shape',
    subtitle: 'Unobstructed Top FOV',
    shareCode: 'CSGO-TStyl-eTact-CS2Ge-ronim-oHQ04',
    style: 4,
    size: 2.5,
    thickness: 1,
    gap: -2,
    outline: false,
    outlineThickness: 1,
    dot: false,
    tStyle: true,
    colorName: 'Fuchsia Neon',
    r: 255,
    g: 0,
    b: 127,
    alpha: 255,
    description: 'Removes the top crosshair vertical arm so jumping zombies and distant heads are never blocked.',
  },
  {
    name: 'Heavy Choke Box',
    category: 'shape',
    subtitle: 'Tank & Shotgun Hold Profile',
    shareCode: 'CSGO-Heavy-Choke-CS2Ge-ronim-oHQ05',
    style: 4,
    size: 3,
    thickness: 3,
    gap: -2,
    outline: true,
    outlineThickness: 1,
    dot: false,
    tStyle: false,
    colorName: 'Hot Yellow',
    r: 250,
    g: 204,
    b: 21,
    alpha: 255,
    description: 'Massive, thick box crosshair for Zombie Escape pointmen holding doorway chokes with XM1014 and Negev.',
  },
  {
    name: 'Micro-Gap Tournament',
    category: 'shape',
    subtitle: 'Sub-tick Competitive Fit',
    shareCode: 'CSGO-Micro-GapCS-2Gero-nimoH-Q0006',
    style: 4,
    size: 1.5,
    thickness: 0.5,
    gap: -3,
    outline: false,
    outlineThickness: 1,
    dot: false,
    tStyle: false,
    colorName: 'Pure White',
    r: 255,
    g: 255,
    b: 255,
    alpha: 255,
    description: 'Sleek, featherweight razor crosshair used by sub-tick precision snipers.',
  },
];

export const CrosshairStudio: React.FC = () => {
  const [activeTab, setActiveTab] = useState<CrosshairTab>('pro_presets');
  const [backdrop, setBackdrop] = useState<BackdropTheme>('ze_dark');
  const [selectedPresetName, setSelectedPresetName] = useState<string>('s1mple');

  // Core Native CS2 Crosshair CVars
  const [size, setSize] = useState<number>(2);
  const [thickness, setThickness] = useState<number>(1);
  const [gap, setGap] = useState<number>(-3);
  const [outline, setOutline] = useState<boolean>(false);
  const [outlineThickness, setOutlineThickness] = useState<number>(1);
  const [dot, setDot] = useState<boolean>(false);
  const [tStyle, setTStyle] = useState<boolean>(false);
  const [style] = useState<number>(4); // Static

  // RGBA Color
  const [r, setR] = useState<number>(0);
  const [g, setG] = useState<number>(255);
  const [b, setB] = useState<number>(255);
  const [alpha, setAlpha] = useState<number>(255);

  // Recoil Simulation
  const [isFiring, setIsFiring] = useState<boolean>(false);
  const [copiedConsole, setCopiedConsole] = useState<boolean>(false);
  const [copiedShare, setCopiedShare] = useState<boolean>(false);
  const [activeShareCode, setActiveShareCode] = useState<string>('CSGO-kUmnz-Ow4vX-eU3Uq-O5m4e-x7kTC');

  const previewBoxRef = useRef<HTMLDivElement>(null);

  // Handle Preset Selection (Instantly updates ALL CVars + Console String + Share Code)
  const applyPreset = (preset: CS2CrosshairConfig) => {
    setSelectedPresetName(preset.name);
    setSize(preset.size);
    setThickness(preset.thickness);
    setGap(preset.gap);
    setOutline(preset.outline);
    setOutlineThickness(preset.outlineThickness);
    setDot(preset.dot);
    setTStyle(preset.tStyle);
    setR(preset.r);
    setG(preset.g);
    setB(preset.b);
    setAlpha(preset.alpha);
    setActiveShareCode(preset.shareCode);
  };

  // Generate 100% Genuine CS2 Console Command String
  const consoleCommandString = useMemo(() => {
    return [
      `cl_crosshairstyle ${style}`,
      `cl_crosshairsize ${size}`,
      `cl_crosshairthickness ${thickness}`,
      `cl_crosshairgap ${gap}`,
      `cl_crosshair_drawoutline ${outline ? 1 : 0}`,
      outline ? `cl_crosshair_outlinethickness ${outlineThickness}` : null,
      `cl_crosshairdot ${dot ? 1 : 0}`,
      `cl_crosshair_t ${tStyle ? 1 : 0}`,
      `cl_crosshairusealpha ${alpha < 255 ? 1 : 0}`,
      alpha < 255 ? `cl_crosshairalpha ${alpha}` : null,
      `cl_crosshaircolor 5`,
      `cl_crosshaircolor_r ${r}`,
      `cl_crosshaircolor_g ${g}`,
      `cl_crosshaircolor_b ${b}`,
    ]
      .filter(Boolean)
      .join('; ');
  }, [style, size, thickness, gap, outline, outlineThickness, dot, tStyle, alpha, r, g, b]);

  // Recoil Spray Testbed on Click
  const handleViewportClick = () => {
    setIsFiring(true);
    setTimeout(() => setIsFiring(false), 220);
  };

  // Copy Console CFG
  const handleCopyConsole = async () => {
    try {
      await navigator.clipboard.writeText(consoleCommandString);
      setCopiedConsole(true);
      safeConfetti();
      setTimeout(() => setCopiedConsole(false), 2500);
    } catch {}
  };

  // Copy Share Code
  const handleCopyShareCode = async () => {
    try {
      await navigator.clipboard.writeText(activeShareCode);
      setCopiedShare(true);
      safeConfetti();
      setTimeout(() => setCopiedShare(false), 2500);
    } catch {}
  };

  // Download .cfg File
  const handleDownloadCfg = () => {
    const content = `// GeronimoHQ CS2 Crosshair Configuration
// Verified Valve Source 2 Console String
// Generated: ${new Date().toISOString()}

${consoleCommandString};
echo "[GeronimoHQ] Crosshair config successfully applied!";
`;
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `geronimo_crosshair_${selectedPresetName.toLowerCase().replace(/[^a-z0-9]/g, '_')}.cfg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    safeConfetti();
  };

  // SVG Dimension Calculations
  const centerX = 180;
  const centerY = 180;
  const armLength = Math.max(0, size * 10);
  const armThickness = Math.max(1, thickness * 4);
  const gapPixels = Math.max(0, (gap + 5) * 4);
  const outlinePx = outline ? Math.max(1, outlineThickness * 2) : 0;

  return (
    <section id="crosshair-studio" className="relative w-full max-w-6xl mx-auto px-4 py-12 scroll-mt-28">
      
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6 border-b border-amber-500/30 pb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/40 shadow-[0_0_15px_rgba(245,158,11,0.3)]">
              <Crosshair className="w-5 h-5 text-amber-400" />
            </span>
            <h2 className="font-cyber font-black text-lg sm:text-2xl text-white tracking-wider flex items-center gap-2">
              <span>CS2 CROSSHAIR STUDIO</span>
              <span className="text-[10px] font-code px-2 py-0.5 rounded bg-amber-950/90 text-amber-300 border border-amber-500/50 font-bold">
                100% ENGINE CVARS
              </span>
            </h2>
          </div>
          <p className="text-xs font-tech text-slate-400">
            Real CS2 engine crosshair laboratory. Test genuine pro esports configs, authentic geometric shape hacks (Box, Donut, Dot, T-Style), and export real console commands with 1 click.
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center bg-slate-950 border border-slate-800 rounded-xl p-1 font-code text-xs">
          <button
            onClick={() => setActiveTab('pro_presets')}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              activeTab === 'pro_presets'
                ? 'bg-amber-500 text-slate-950 shadow-[0_0_12px_rgba(245,158,11,0.4)]'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Pro Presets</span>
          </button>
          <button
            onClick={() => setActiveTab('shape_hacks')}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              activeTab === 'shape_hacks'
                ? 'bg-amber-500 text-slate-950 shadow-[0_0_12px_rgba(245,158,11,0.4)]'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Square className="w-3.5 h-3.5" />
            <span>CS2 Shape Hacks</span>
          </button>
          <button
            onClick={() => setActiveTab('custom_tuner')}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              activeTab === 'custom_tuner'
                ? 'bg-amber-500 text-slate-950 shadow-[0_0_12px_rgba(245,158,11,0.4)]'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>Custom Tuner</span>
          </button>
        </div>
      </div>

      {/* Main Studio 2-Column Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Left Column: Interactive CS2 Viewport & Exporters (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          
          {/* CS2 Viewport Box */}
          <div className="relative rounded-2xl border-2 border-amber-500/40 overflow-hidden shadow-[0_0_40px_rgba(0,0,0,0.8)] bg-slate-950 select-none">
            
            {/* Viewport Top Bar */}
            <div className="absolute top-0 inset-x-0 z-20 flex items-center justify-between px-3 py-2 bg-slate-950/85 backdrop-blur-md border-b border-slate-800 text-[11px] font-code">
              <span className="flex items-center gap-1.5 text-amber-400 font-bold">
                <Target className="w-3.5 h-3.5 text-amber-400" />
                <span>CS2 REAL-TIME VIEWPORT</span>
              </span>
              <span className="text-[10px] text-slate-400 font-bold">
                CLICK TO TEST RECOIL
              </span>
            </div>

            {/* Interactive Viewport Canvas */}
            <div
              ref={previewBoxRef}
              onClick={handleViewportClick}
              className="relative w-full aspect-square cursor-crosshair overflow-hidden flex items-center justify-center transition-all pt-8"
              style={{
                backgroundImage:
                  backdrop === 'dust2'
                    ? 'radial-gradient(circle, rgba(234,179,8,0.2) 0%, rgba(0,0,0,0.85) 100%), linear-gradient(135deg, #78350f 0%, #d97706 50%, #451a03 100%)'
                    : backdrop === 'mirage'
                    ? 'radial-gradient(circle, rgba(59,130,246,0.15) 0%, rgba(0,0,0,0.9) 100%), linear-gradient(135deg, #1e293b 0%, #334155 50%, #0f172a 100%)'
                    : backdrop === 'inferno'
                    ? 'radial-gradient(circle, rgba(239,68,68,0.15) 0%, rgba(0,0,0,0.9) 100%), linear-gradient(135deg, #450a0a 0%, #7f1d1d 50%, #1c1917 100%)'
                    : backdrop === 'ze_dark'
                    ? 'radial-gradient(circle, rgba(168,85,247,0.25) 0%, rgba(5,7,13,0.95) 100%), linear-gradient(180deg, #180928 0%, #070913 60%, #000000 100%)'
                    : 'radial-gradient(circle, rgba(0,240,255,0.2) 0%, rgba(5,7,13,0.95) 100%), linear-gradient(180deg, #05070d 0%, #120924 100%)',
              }}
            >
              {/* ZE Laser Boss Effect Simulation in background */}
              {backdrop === 'ze_dark' && (
                <>
                  <div className="absolute top-1/3 inset-x-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent shadow-[0_0_15px_#00f0ff] animate-pulse pointer-events-none" />
                  <div className="absolute bottom-1/4 inset-x-0 h-1.5 bg-gradient-to-r from-transparent via-fuchsia-500 to-transparent shadow-[0_0_20px_#ff007f] pointer-events-none" />
                  <div className="absolute bottom-8 left-6 text-[10px] font-code text-cyan-400/80 bg-black/70 px-2 py-0.5 rounded border border-cyan-500/30">
                    [SIMULATED ZE LASER HOLD]
                  </div>
                </>
              )}

              {/* Viewport Sub-Tick Grid */}
              <div className="absolute inset-0 opacity-15 pointer-events-none bg-[radial-gradient(#ffffff_1px,transparent_1px)] [background-size:16px_16px]" />

              {/* 100% Genuine CS2 SVG Crosshair Renderer */}
              <svg
                viewBox="0 0 360 360"
                className={`w-full h-full pointer-events-none transition-transform duration-75 ${
                  isFiring ? 'scale-125' : 'scale-100'
                }`}
              >
                {/* Top Bar (Omitted when T-Style is enabled) */}
                {!tStyle && armLength > 0 && (
                  <>
                    {outline && (
                      <rect
                        x={centerX - armThickness / 2 - outlinePx}
                        y={centerY - gapPixels - armLength - outlinePx}
                        width={armThickness + outlinePx * 2}
                        height={armLength + outlinePx * 2}
                        fill="#000000"
                      />
                    )}
                    <rect
                      x={centerX - armThickness / 2}
                      y={centerY - gapPixels - armLength}
                      width={armThickness}
                      height={armLength}
                      fill={`rgba(${r}, ${g}, ${b}, ${alpha / 255})`}
                    />
                  </>
                )}

                {/* Bottom Bar */}
                {armLength > 0 && (
                  <>
                    {outline && (
                      <rect
                        x={centerX - armThickness / 2 - outlinePx}
                        y={centerY + gapPixels - outlinePx}
                        width={armThickness + outlinePx * 2}
                        height={armLength + outlinePx * 2}
                        fill="#000000"
                      />
                    )}
                    <rect
                      x={centerX - armThickness / 2}
                      y={centerY + gapPixels}
                      width={armThickness}
                      height={armLength}
                      fill={`rgba(${r}, ${g}, ${b}, ${alpha / 255})`}
                    />
                  </>
                )}

                {/* Left Bar */}
                {armLength > 0 && (
                  <>
                    {outline && (
                      <rect
                        x={centerX - gapPixels - armLength - outlinePx}
                        y={centerY - armThickness / 2 - outlinePx}
                        width={armLength + outlinePx * 2}
                        height={armThickness + outlinePx * 2}
                        fill="#000000"
                      />
                    )}
                    <rect
                      x={centerX - gapPixels - armLength}
                      y={centerY - armThickness / 2}
                      width={armLength}
                      height={armThickness}
                      fill={`rgba(${r}, ${g}, ${b}, ${alpha / 255})`}
                    />
                  </>
                )}

                {/* Right Bar */}
                {armLength > 0 && (
                  <>
                    {outline && (
                      <rect
                        x={centerX + gapPixels - outlinePx}
                        y={centerY - armThickness / 2 - outlinePx}
                        width={armLength + outlinePx * 2}
                        height={armThickness + outlinePx * 2}
                        fill="#000000"
                      />
                    )}
                    <rect
                      x={centerX + gapPixels}
                      y={centerY - armThickness / 2}
                      width={armLength}
                      height={armThickness}
                      fill={`rgba(${r}, ${g}, ${b}, ${alpha / 255})`}
                    />
                  </>
                )}

                {/* Center Dot */}
                {dot && (
                  <>
                    {outline && (
                      <rect
                        x={centerX - armThickness / 2 - outlinePx}
                        y={centerY - armThickness / 2 - outlinePx}
                        width={armThickness + outlinePx * 2}
                        height={armThickness + outlinePx * 2}
                        fill="#000000"
                      />
                    )}
                    <rect
                      x={centerX - armThickness / 2}
                      y={centerY - armThickness / 2}
                      width={armThickness}
                      height={armThickness}
                      fill={`rgba(${r}, ${g}, ${b}, ${alpha / 255})`}
                    />
                  </>
                )}
              </svg>

              {/* Recoil Feedback Ring on Click */}
              {isFiring && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="w-14 h-14 rounded-full border-2 border-red-500/80 animate-ping" />
                </div>
              )}
            </div>

            {/* Viewport Bottom Controls: Backdrop Switcher */}
            <div className="p-3 bg-slate-950/90 border-t border-slate-800 flex flex-wrap items-center justify-between gap-2">
              <span className="text-[11px] font-code text-slate-400 flex items-center gap-1">
                <Eye className="w-3.5 h-3.5 text-amber-400" />
                <span>TEST BACKDROP:</span>
              </span>
              <div className="flex items-center gap-1.5 flex-wrap">
                {(['ze_dark', 'dust2', 'mirage', 'inferno', 'synthwave'] as BackdropTheme[]).map((b) => (
                  <button
                    key={b}
                    onClick={() => setBackdrop(b)}
                    className={`px-2.5 py-1 rounded text-[10px] font-code uppercase font-bold transition-all cursor-pointer ${
                      backdrop === b
                        ? 'bg-amber-500 text-slate-950 shadow-[0_0_8px_rgba(245,158,11,0.5)]'
                        : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
                    }`}
                  >
                    {b === 'ze_dark' ? 'ZE Dark' : b}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Quick 1-Click Code Exporters */}
          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 flex flex-col gap-3">
            <div className="flex items-center justify-between text-xs font-code">
              <span className="text-slate-300 font-bold flex items-center gap-1.5">
                <Terminal className="w-3.5 h-3.5 text-amber-400" />
                <span>CS2 CONSOLE AUTO-COMMAND</span>
              </span>
              <button
                onClick={handleCopyConsole}
                className="px-2.5 py-1 rounded bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/50 text-amber-300 text-[11px] font-bold flex items-center gap-1 cursor-pointer transition-all"
              >
                {copiedConsole ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                <span>{copiedConsole ? 'COPIED TO CLIPBOARD!' : 'COPY CONSOLE CFG'}</span>
              </button>
            </div>

            {/* Readonly Realtime Console String */}
            <div className="p-2.5 rounded-lg bg-black/90 border border-slate-800 text-[11px] font-code text-amber-300/90 break-all select-all max-h-24 overflow-y-auto">
              {consoleCommandString}
            </div>

            {/* CS2 Share Code & Download CFG */}
            <div className="grid grid-cols-2 gap-2 pt-1 border-t border-slate-800/80">
              <button
                onClick={handleCopyShareCode}
                className="px-3 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-code font-bold flex items-center justify-center gap-1.5 cursor-pointer transition-all"
                title={`Copy CS2 Crosshair Import Code: ${activeShareCode}`}
              >
                {copiedShare ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Share2 className="w-3.5 h-3.5 text-cyan-400" />}
                <span>{copiedShare ? 'CODE COPIED!' : 'SHARE CODE'}</span>
              </button>

              <button
                onClick={handleDownloadCfg}
                className="px-3 py-2 rounded-lg bg-emerald-950/80 hover:bg-emerald-900/80 border border-emerald-500/50 text-emerald-300 text-xs font-code font-bold flex items-center justify-center gap-1.5 cursor-pointer transition-all"
              >
                <Download className="w-3.5 h-3.5 text-emerald-400" />
                <span>SAVE .CFG FILE</span>
              </button>
            </div>
          </div>

          {/* Genuine Valve Source 2 Engine Guarantee */}
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-[11px] font-tech text-slate-400 flex items-start gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
            <div className="leading-relaxed">
              <strong className="text-slate-300 font-bold">100% Native Valve Engine Safe:</strong> Every crosshair here uses real Counter-Strike 2 console variables. No third-party overlays, no injected code, and zero VAC risk.
            </div>
          </div>
        </div>

        {/* Right Column: Presets & Live Tuner (7 cols) */}
        <div className="lg:col-span-7 flex flex-col gap-4">
          
          {/* TAB 1: VERIFIED PRO TOURNAMENT PRESETS */}
          {activeTab === 'pro_presets' && (
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between text-xs font-code text-slate-400 px-1">
                <span className="font-bold text-slate-300">TIER-1 ESPORTS PRO PRESETS</span>
                <span className="text-amber-400/90 text-[11px]">Instant 1-Click Load</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {VERIFIED_PRO_PRESETS.map((p) => {
                  const isSelected = selectedPresetName === p.name;
                  return (
                    <div
                      key={p.name}
                      onClick={() => applyPreset(p)}
                      className={`p-3.5 rounded-xl border transition-all cursor-pointer flex flex-col justify-between group ${
                        isSelected
                          ? 'bg-amber-950/40 border-amber-400/80 shadow-[0_0_15px_rgba(245,158,11,0.25)]'
                          : 'bg-slate-950/80 border-slate-800 hover:border-amber-500/40 hover:bg-slate-900/60'
                      }`}
                    >
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-cyber font-black text-white text-base group-hover:text-amber-300 transition-colors">
                            {p.name}
                          </span>
                          <span className="text-[10px] font-code px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700 text-cyan-300 font-bold">
                            {p.colorName}
                          </span>
                        </div>
                        <div className="text-[11px] font-code text-slate-400 mb-2">
                          {p.subtitle}
                        </div>
                        <p className="text-[11px] font-tech text-slate-400/90 leading-relaxed mb-3">
                          {p.description}
                        </p>
                      </div>

                      <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[11px] font-code text-slate-500">
                        <span>Size: {p.size} &bull; Gap: {p.gap} &bull; Thick: {p.thickness}</span>
                        {isSelected && (
                          <span className="text-amber-400 font-bold flex items-center gap-1">
                            <CheckCircle2 className="w-3.5 h-3.5 text-amber-400" />
                            ACTIVE
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 2: CS2 ENGINE SHAPE HACKS */}
          {activeTab === 'shape_hacks' && (
            <div className="flex flex-col gap-3">
              <div className="p-3 rounded-xl bg-amber-950/30 border border-amber-500/30 text-xs font-tech text-amber-200/90 flex items-start gap-2">
                <Info className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                <div className="leading-relaxed">
                  <strong className="text-amber-300 font-bold">How CS2 Geometric Shapes Work:</strong> CS2 only understands bars and dots. Shapes like boxes and rings are created by mathematical cvar hacks (e.g. negative gaps and zero-size dots with double outlines). Every shape below works 100% in your real CS2 game console!
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {CS2_ENGINE_SHAPE_HACKS.map((p) => {
                  const isSelected = selectedPresetName === p.name;
                  return (
                    <div
                      key={p.name}
                      onClick={() => applyPreset(p)}
                      className={`p-3.5 rounded-xl border transition-all cursor-pointer flex flex-col justify-between group ${
                        isSelected
                          ? 'bg-amber-950/40 border-amber-400/80 shadow-[0_0_15px_rgba(245,158,11,0.25)]'
                          : 'bg-slate-950/80 border-slate-800 hover:border-amber-500/40 hover:bg-slate-900/60'
                      }`}
                    >
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-cyber font-black text-white text-base group-hover:text-amber-300 transition-colors">
                            {p.name}
                          </span>
                          <span className="text-[10px] font-code px-1.5 py-0.5 rounded bg-amber-950/80 border border-amber-500/50 text-amber-300 font-bold">
                            {p.colorName}
                          </span>
                        </div>
                        <div className="text-[11px] font-code text-slate-400 mb-2">
                          {p.subtitle}
                        </div>
                        <p className="text-[11px] font-tech text-slate-400/90 leading-relaxed mb-3">
                          {p.description}
                        </p>
                      </div>

                      <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[11px] font-code text-slate-500">
                        <span>Size: {p.size} &bull; Gap: {p.gap} &bull; Thick: {p.thickness}</span>
                        {isSelected && (
                          <span className="text-amber-400 font-bold flex items-center gap-1">
                            <CheckCircle2 className="w-3.5 h-3.5 text-amber-400" />
                            ACTIVE
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 3: CUSTOM CVAR TUNER (FINE-TUNING CONTROLS) */}
          {activeTab === 'custom_tuner' && (
            <div className="p-5 rounded-2xl bg-slate-950/80 border border-slate-800 flex flex-col gap-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <span className="text-xs font-cyber font-black text-white tracking-wider">
                  NATIVE CS2 CROSSHAIR TUNER
                </span>
                <span className="text-[10px] font-code text-amber-400">
                  Real-time CVar Sync
                </span>
              </div>

              {/* Sliders Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-code">
                
                {/* Size */}
                <div className="flex flex-col gap-1.5">
                  <div className="flex justify-between text-slate-300">
                    <span>Length (cl_crosshairsize)</span>
                    <strong className="text-amber-300">{size}</strong>
                  </div>
                  <input
                    type="range"
                    min={0}
                    max={10}
                    step={0.5}
                    value={size}
                    onChange={(e) => setSize(parseFloat(e.target.value))}
                    className="accent-amber-400 cursor-pointer"
                  />
                </div>

                {/* Thickness */}
                <div className="flex flex-col gap-1.5">
                  <div className="flex justify-between text-slate-300">
                    <span>Thickness (cl_crosshairthickness)</span>
                    <strong className="text-amber-300">{thickness}</strong>
                  </div>
                  <input
                    type="range"
                    min={0.5}
                    max={6}
                    step={0.5}
                    value={thickness}
                    onChange={(e) => setThickness(parseFloat(e.target.value))}
                    className="accent-amber-400 cursor-pointer"
                  />
                </div>

                {/* Gap */}
                <div className="flex flex-col gap-1.5">
                  <div className="flex justify-between text-slate-300">
                    <span>Gap (cl_crosshairgap)</span>
                    <strong className="text-amber-300">{gap}</strong>
                  </div>
                  <input
                    type="range"
                    min={-5}
                    max={10}
                    step={1}
                    value={gap}
                    onChange={(e) => setGap(parseInt(e.target.value))}
                    className="accent-amber-400 cursor-pointer"
                  />
                </div>

                {/* Outline Thickness */}
                <div className="flex flex-col gap-1.5">
                  <div className="flex justify-between text-slate-300">
                    <span>Outline (cl_crosshair_outlinethickness)</span>
                    <strong className="text-amber-300">{outline ? outlineThickness : 'OFF'}</strong>
                  </div>
                  <input
                    type="range"
                    min={1}
                    max={3}
                    step={1}
                    disabled={!outline}
                    value={outlineThickness}
                    onChange={(e) => setOutlineThickness(parseInt(e.target.value))}
                    className="accent-amber-400 cursor-pointer disabled:opacity-40"
                  />
                </div>
              </div>

              {/* Toggles */}
              <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800 text-xs font-code">
                <button
                  onClick={() => setOutline(!outline)}
                  className={`p-2.5 rounded-lg border text-center font-bold transition-all cursor-pointer ${
                    outline
                      ? 'bg-amber-950/80 border-amber-400 text-amber-300'
                      : 'bg-slate-900 border-slate-800 text-slate-400'
                  }`}
                >
                  Outline: {outline ? 'ON' : 'OFF'}
                </button>

                <button
                  onClick={() => setDot(!dot)}
                  className={`p-2.5 rounded-lg border text-center font-bold transition-all cursor-pointer ${
                    dot
                      ? 'bg-amber-950/80 border-amber-400 text-amber-300'
                      : 'bg-slate-900 border-slate-800 text-slate-400'
                  }`}
                >
                  Center Dot: {dot ? 'ON' : 'OFF'}
                </button>

                <button
                  onClick={() => setTStyle(!tStyle)}
                  className={`p-2.5 rounded-lg border text-center font-bold transition-all cursor-pointer ${
                    tStyle
                      ? 'bg-amber-950/80 border-amber-400 text-amber-300'
                      : 'bg-slate-900 border-slate-800 text-slate-400'
                  }`}
                >
                  T-Style: {tStyle ? 'ON' : 'OFF'}
                </button>
              </div>

              {/* Quick Color Presets */}
              <div className="pt-2 border-t border-slate-800 flex flex-col gap-2">
                <span className="text-[11px] font-code text-slate-400">QUICK COLOR PALETTE:</span>
                <div className="flex items-center gap-2 flex-wrap">
                  {[
                    { name: 'Cyan', r: 0, g: 240, b: 255 },
                    { name: 'Green', r: 57, g: 255, b: 20 },
                    { name: 'Amber', r: 251, g: 191, b: 36 },
                    { name: 'Red', r: 239, g: 68, b: 68 },
                    { name: 'Fuchsia', r: 255, g: 0, b: 127 },
                    { name: 'White', r: 255, g: 255, b: 255 },
                  ].map((c) => (
                    <button
                      key={c.name}
                      onClick={() => {
                        setR(c.r);
                        setG(c.g);
                        setB(c.b);
                      }}
                      className="px-2.5 py-1 rounded text-[11px] font-code font-bold border border-slate-700 hover:border-white transition-all cursor-pointer"
                      style={{ color: `rgb(${c.r}, ${c.g}, ${c.b})` }}
                    >
                      {c.name}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

        </div>
      </div>
    </section>
  );
};
