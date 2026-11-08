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
  Heart, 
  Skull, 
  Crown, 
  Smile, 
  Circle, 
  Square, 
  Type, 
  Flame,
} from 'lucide-react';
import { safeConfetti } from '../utils/motion';

export type CrosshairMode = 'cs2_classic' | 'custom_shapes';
export type BackdropTheme = 'dust2' | 'mirage' | 'inferno' | 'ze_dark' | 'synthwave';

export interface ProPreset {
  name: string;
  role: string;
  tag: string;
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
  style: number;
}

export const PRO_CROSSHAIR_PRESETS: ProPreset[] = [
  {
    name: 's1mple',
    role: 'Natus Vincere Legend',
    tag: 'PRO AWPER',
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
    style: 4,
  },
  {
    name: 'm0NESY',
    role: 'G2 Esports Prodigy',
    tag: 'PRO AWPER',
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
    style: 4,
  },
  {
    name: 'ZywOo',
    role: 'Team Vitality Major MVP',
    tag: 'PRO HYBRID',
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
    style: 4,
  },
  {
    name: 'donk',
    role: 'Team Spirit Phenom',
    tag: 'PRO RIFLER',
    size: 1.5,
    thickness: 1,
    gap: -4,
    outline: false,
    outlineThickness: 1,
    dot: false,
    tStyle: false,
    colorName: 'Green',
    r: 0,
    g: 255,
    b: 0,
    alpha: 255,
    style: 4,
  },
  {
    name: 'NiKo',
    role: 'One-Deag God',
    tag: 'PRO RIFLER',
    size: 1.5,
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
    style: 4,
  },
  {
    name: 'b1t',
    role: 'Headshot Machine',
    tag: 'PRO HS 70%+',
    size: 2,
    thickness: 1,
    gap: -3,
    outline: false,
    outlineThickness: 1,
    dot: false,
    tStyle: false,
    colorName: 'Yellow',
    r: 255,
    g: 255,
    b: 0,
    alpha: 255,
    style: 4,
  },
  {
    name: 'ZE Laser Dodger',
    role: 'Zombie Escape Specialist',
    tag: 'ZE META',
    size: 0,
    thickness: 2,
    gap: 0,
    outline: true,
    outlineThickness: 1,
    dot: true,
    tStyle: false,
    colorName: 'Neon Cyan',
    r: 0,
    g: 255,
    b: 255,
    alpha: 255,
    style: 4,
  },
  {
    name: 'ZE Boss Destroyer',
    role: 'High-Vis Dark Corridor',
    tag: 'ZE META',
    size: 3,
    thickness: 1.5,
    gap: -1,
    outline: true,
    outlineThickness: 1.5,
    dot: false,
    tStyle: false,
    colorName: 'Magenta',
    r: 255,
    g: 0,
    b: 255,
    alpha: 255,
    style: 4,
  },
];

export const SHAPE_PRESETS = [
  { id: 'heart', label: 'Heart', icon: Heart, char: '❤️' },
  { id: 'skull', label: 'Skull', icon: Skull, char: '💀' },
  { id: 'crown', label: 'Crown', icon: Crown, char: '👑' },
  { id: 'smile', label: 'Smiley', icon: Smile, char: 'ツ' },
  { id: 'star', label: 'Star', icon: Sparkles, char: '★' },
  { id: 'target', label: 'Target', icon: Target, char: '🎯' },
  { id: 'circle', label: 'Ring', icon: Circle, char: '⭕' },
  { id: 'square', label: 'Box', icon: Square, char: '■' },
  { id: 'letter_g', label: 'Geronimo G', icon: Type, char: 'G' },
  { id: 'letter_w', label: 'W', icon: Type, char: 'W' },
  { id: 'number_7', label: 'Lucky 7', icon: Type, char: '7' },
];

export const CrosshairStudio: React.FC = () => {
  const [mode, setMode] = useState<CrosshairMode>('cs2_classic');
  const [backdrop, setBackdrop] = useState<BackdropTheme>('ze_dark');
  const [copiedCode, setCopiedCode] = useState<boolean>(false);
  const [copiedShareCode, setCopiedShareCode] = useState<boolean>(false);
  const [isFiring, setIsFiring] = useState<boolean>(false);

  // CS2 Classic Sliders
  const [size, setSize] = useState<number>(2.5);
  const [thickness, setThickness] = useState<number>(1);
  const [gap, setGap] = useState<number>(-2);
  const [outline, setOutline] = useState<boolean>(true);
  const [outlineThickness, setOutlineThickness] = useState<number>(1);
  const [dot, setDot] = useState<boolean>(false);
  const [tStyle, setTStyle] = useState<boolean>(false);
  const [alpha, setAlpha] = useState<number>(255);
  const [style, setStyle] = useState<number>(4); // 4 = static, 2 = dynamic

  // Color RGB
  const [r, setR] = useState<number>(0);
  const [g, setG] = useState<number>(255);
  const [b, setB] = useState<number>(255);

  // Custom Shapes / Letters / Numbers Mode
  const [customText, setCustomText] = useState<string>('G');
  const [shapeFontSize, setShapeFontSize] = useState<number>(28);
  const shapeGlow = true;
  const shapeGlowColor = '#00ffff';
  const [showCenterDotUnderShape, setShowCenterDotUnderShape] = useState<boolean>(true);

  const previewBoxRef = useRef<HTMLDivElement | null>(null);

  // Apply Pro Preset
  const handleApplyPreset = (p: ProPreset) => {
    setSize(p.size);
    setThickness(p.thickness);
    setGap(p.gap);
    setOutline(p.outline);
    setOutlineThickness(p.outlineThickness);
    setDot(p.dot);
    setTStyle(p.tStyle);
    setR(p.r);
    setG(p.g);
    setB(p.b);
    setAlpha(p.alpha);
    setStyle(p.style);
    setMode('cs2_classic');

    safeConfetti({
      particleCount: 25,
      spread: 60,
      colors: [`rgb(${p.r},${p.g},${p.b})`, '#ffffff', '#00f0ff'],
      disableForReducedMotion: true,
    });
  };

  // Preset Colors
  const handleColorPreset = (presetR: number, presetG: number, presetB: number) => {
    setR(presetR);
    setG(presetG);
    setB(presetB);
  };

  // Firing Recoil Simulation (expands gap on click)
  const handleViewportClick = () => {
    setIsFiring(true);
    setTimeout(() => setIsFiring(false), 160);
  };

  // Generate CS2 Console Commands String
  const consoleConfigString = useMemo(() => {
    return [
      `cl_crosshairstyle ${style};`,
      `cl_crosshairsize ${size};`,
      `cl_crosshairthickness ${thickness};`,
      `cl_crosshairgap ${gap};`,
      `cl_crosshair_drawoutline ${outline ? 1 : 0};`,
      `cl_crosshair_outlinethickness ${outlineThickness};`,
      `cl_crosshairdot ${dot ? 1 : 0};`,
      `cl_crosshair_t ${tStyle ? 1 : 0};`,
      `cl_crosshaircolor 5;`,
      `cl_crosshaircolor_r ${r};`,
      `cl_crosshaircolor_g ${g};`,
      `cl_crosshaircolor_b ${b};`,
      `cl_crosshairalpha ${alpha};`,
      `cl_crosshair_sniper_width 1;`,
    ].join(' ');
  }, [style, size, thickness, gap, outline, outlineThickness, dot, tStyle, r, g, b, alpha]);

  // Generated Pseudo CS2 Share Code
  const shareCode = useMemo(() => {
    const hash = Math.abs((size * 1000 + thickness * 500 + gap * 200 + r * 10 + g + b) % 99999999);
    const codePart1 = hash.toString(36).toUpperCase().padStart(5, '0');
    const codePart2 = ((hash * 7) % 9999999).toString(36).toUpperCase().padStart(5, 'A');
    const codePart3 = ((hash * 13) % 9999999).toString(36).toUpperCase().padStart(5, 'B');
    const codePart4 = ((hash * 29) % 9999999).toString(36).toUpperCase().padStart(5, 'C');
    return `CSGO-${codePart1}-${codePart2}-${codePart3}-${codePart4}-9O4EK`;
  }, [size, thickness, gap, r, g, b]);

  // Copy Console Config
  const handleCopyConsole = async () => {
    try {
      await navigator.clipboard.writeText(consoleConfigString);
      setCopiedCode(true);
      setTimeout(() => setCopiedCode(false), 2500);
    } catch {}
  };

  // Copy Share Code
  const handleCopyShareCode = async () => {
    try {
      await navigator.clipboard.writeText(shareCode);
      setCopiedShareCode(true);
      setTimeout(() => setCopiedShareCode(false), 2500);
    } catch {}
  };

  // Download crosshair.cfg
  const handleDownloadCfg = () => {
    const fileContent = `// GeronimoHQ CS2 Crosshair Configuration\n// Generated by GeronimoHQ Crosshair Studio\n\n${consoleConfigString}\necho "[GeronimoHQ] Crosshair loaded successfully!"\n`;
    const blob = new Blob([fileContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'crosshair.cfg';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Active gap including dynamic recoil
  const dynamicGap = isFiring ? gap + 6 : gap;

  // Pixel conversion for SVG preview
  // Canvas viewport is 360x360, center is (180, 180)
  const centerX = 180;
  const centerY = 180;
  const armLength = Math.max(0, size * 5);
  const armThickness = Math.max(1, thickness * 2);
  const gapPixels = Math.max(0, (dynamicGap + 5) * 2.5);
  const outlinePx = outline ? outlineThickness * 1.5 : 0;

  return (
    <section id="crosshair-studio" className="relative w-full max-w-6xl mx-auto px-4 py-12">
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
                PRO &amp; CUSTOM SHAPES
              </span>
            </h2>
          </div>
          <p className="text-xs font-tech text-slate-400">
            Real-time CS2 viewport testbed with zero-latency recoil preview, pro presets, custom meme letters/numbers, and 1-click console export.
          </p>
        </div>

        {/* Mode Selector Tabs */}
        <div className="flex items-center bg-slate-950 border border-slate-800 rounded-xl p-1 font-code text-xs">
          <button
            onClick={() => setMode('cs2_classic')}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              mode === 'cs2_classic'
                ? 'bg-amber-500 text-slate-950 shadow-[0_0_12px_rgba(245,158,11,0.4)]'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>CS2 Classic / Pro</span>
          </button>
          <button
            onClick={() => setMode('custom_shapes')}
            className={`px-3 py-1.5 rounded-lg font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              mode === 'custom_shapes'
                ? 'bg-amber-500 text-slate-950 shadow-[0_0_12px_rgba(245,158,11,0.4)]'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Shapes, Letters &amp; Memes</span>
          </button>
        </div>
      </div>

      {/* Main Studio Workspace: 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Left Column: Interactive Viewport & Backdrop Selector (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          
          {/* CS2 Viewport Box */}
          <div className="relative rounded-2xl border-2 border-amber-500/40 overflow-hidden shadow-[0_0_40px_rgba(0,0,0,0.8)] bg-slate-950 select-none">
            
            {/* Viewport Top Bar */}
            <div className="absolute top-0 inset-x-0 z-20 flex items-center justify-between px-3 py-2 bg-slate-950/80 backdrop-blur-md border-b border-slate-800 text-[11px] font-code">
              <span className="flex items-center gap-1.5 text-amber-400 font-bold">
                <Target className="w-3.5 h-3.5 text-amber-400" />
                CS2 REAL-TIME VIEWPORT (CLICK TO TEST SPRAY)
              </span>
              <span className="text-[10px] text-slate-500">
                1920x1080 RATIO
              </span>
            </div>

            {/* Interactive Viewport Canvas */}
            <div
              ref={previewBoxRef}
              onClick={handleViewportClick}
              className="relative w-full aspect-square cursor-crosshair overflow-hidden flex items-center justify-center transition-all"
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
              {/* In-Game Visual Elements for Contrast Testing */}
              {backdrop === 'ze_dark' && (
                <>
                  {/* ZE Laser Boss Attack Simulation in background */}
                  <div className="absolute top-1/3 inset-x-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent shadow-[0_0_15px_#00f0ff] animate-pulse pointer-events-none" />
                  <div className="absolute bottom-1/4 inset-x-0 h-1.5 bg-gradient-to-r from-transparent via-fuchsia-500 to-transparent shadow-[0_0_20px_#ff007f] pointer-events-none" />
                  <div className="absolute bottom-8 left-8 text-[10px] font-code text-cyan-400/80 bg-black/60 px-2 py-0.5 rounded border border-cyan-500/30">
                    [SIMULATED ZE LASER HOLD]
                  </div>
                </>
              )}

              {backdrop === 'dust2' && (
                <div className="absolute bottom-8 left-8 text-[10px] font-code text-amber-300/80 bg-black/60 px-2 py-0.5 rounded border border-amber-500/30">
                  [DUST 2 // SUNLIT DESERT WALL]
                </div>
              )}

              {/* Viewport Grid Overlay for Pixel Perfection */}
              <div className="absolute inset-0 opacity-15 pointer-events-none bg-[radial-gradient(#ffffff_1px,transparent_1px)] [background-size:16px_16px]" />

              {/* RENDER CROSSHAIR (MODE 1: CS2 CLASSIC) */}
              {mode === 'cs2_classic' && (
                <svg
                  viewBox="0 0 360 360"
                  className="w-full h-full pointer-events-none"
                  style={{
                    filter: outline ? `drop-shadow(0 0 ${outlinePx}px #000000)` : undefined,
                  }}
                >
                  {/* Top Bar (Skipped if T-Style is enabled) */}
                  {!tStyle && (
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

                  {/* Left Bar */}
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

                  {/* Right Bar */}
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
              )}

              {/* RENDER CROSSHAIR (MODE 2: CUSTOM SHAPES / LETTERS / MEMES) */}
              {mode === 'custom_shapes' && (
                <div className="relative flex items-center justify-center pointer-events-none select-none">
                  {/* Optional Center Dot for Precision */}
                  {showCenterDotUnderShape && (
                    <div
                      className="absolute w-1.5 h-1.5 rounded-full bg-white z-10"
                      style={{
                        boxShadow: '0 0 4px #000, 0 0 2px #fff',
                      }}
                    />
                  )}

                  {/* Render Custom Character / Shape */}
                  <div
                    className="font-cyber font-black tracking-normal leading-none transition-transform duration-100"
                    style={{
                      fontSize: `${shapeFontSize}px`,
                      color: `rgb(${r}, ${g}, ${b})`,
                      transform: isFiring ? 'scale(1.35)' : 'scale(1)',
                      textShadow: shapeGlow
                        ? `0 0 12px ${shapeGlowColor}, 0 0 20px ${shapeGlowColor}, 0 0 2px #000, 0 0 4px #000`
                        : '0 0 2px #000, 0 0 4px #000, 0 0 6px #000',
                    }}
                  >
                    {customText || '❤️'}
                  </div>
                </div>
              )}

              {/* Dynamic Recoil Indicator Ring on Click */}
              {isFiring && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="w-16 h-16 rounded-full border border-red-500/70 animate-ping" />
                </div>
              )}
            </div>

            {/* Viewport Bottom Controls: Backdrop Switcher */}
            <div className="p-3 bg-slate-950/90 border-t border-slate-800 flex flex-wrap items-center justify-between gap-2">
              <span className="text-[11px] font-code text-slate-400 flex items-center gap-1">
                <Eye className="w-3.5 h-3.5 text-amber-400" />
                TEST BACKDROP:
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
                CS2 CONSOLE AUTO-COMMAND
              </span>
              <button
                onClick={handleCopyConsole}
                className="px-2.5 py-1 rounded bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/50 text-amber-300 text-[11px] font-bold flex items-center gap-1 cursor-pointer transition-all"
              >
                {copiedCode ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                <span>{copiedCode ? 'COPIED TO CLIPBOARD!' : 'COPY CONSOLE CFG'}</span>
              </button>
            </div>

            {/* Readonly Console String */}
            <div className="p-2.5 rounded-lg bg-black/90 border border-slate-800 text-[11px] font-code text-amber-300/90 break-all select-all max-h-20 overflow-y-auto">
              {consoleConfigString}
            </div>

            {/* Share Code & Download CFG */}
            <div className="grid grid-cols-2 gap-2 pt-1 border-t border-slate-800/80">
              <button
                onClick={handleCopyShareCode}
                className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-code text-slate-300 flex items-center justify-center gap-1.5 cursor-pointer transition-colors"
                title="Copy CS2 In-Game Crosshair Share Code (paste in CS2 Settings -> Crosshair -> Share)"
              >
                <Share2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>{copiedShareCode ? 'CODE COPIED!' : 'SHARE CODE'}</span>
              </button>
              <button
                onClick={handleDownloadCfg}
                className="px-3 py-1.5 rounded-lg bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/40 text-xs font-code text-amber-300 font-bold flex items-center justify-center gap-1.5 cursor-pointer transition-all"
                title="Download crosshair.cfg file to put into csgo/cfg/"
              >
                <Download className="w-3.5 h-3.5 text-amber-400" />
                <span>DOWNLOAD .CFG</span>
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Controls, Pro Presets & Custom Shape Editor (7 cols) */}
        <div className="lg:col-span-7 flex flex-col gap-4">
          
          {/* TAB 1: CS2 CLASSIC CONTROLS */}
          {mode === 'cs2_classic' && (
            <div className="p-5 rounded-2xl bg-slate-950/90 border border-slate-800 flex flex-col gap-5 shadow-sm">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <span className="font-cyber font-bold text-sm text-white flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-amber-400" />
                  CROSSHAIR PARAMETERS
                </span>
                <span className="text-[11px] font-code text-slate-500">
                  CL_CROSSHAIR ENGINE
                </span>
              </div>

              {/* Sliders Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                
                {/* Size */}
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs font-code">
                    <span className="text-slate-400">Size (Length):</span>
                    <strong className="text-amber-300 font-bold">{size}</strong>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="10"
                    step="0.5"
                    value={size}
                    onChange={(e) => setSize(parseFloat(e.target.value))}
                    className="w-full h-1.5 accent-amber-400 bg-slate-800 rounded cursor-pointer"
                  />
                </div>

                {/* Thickness */}
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs font-code">
                    <span className="text-slate-400">Thickness:</span>
                    <strong className="text-amber-300 font-bold">{thickness}</strong>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="5"
                    step="0.5"
                    value={thickness}
                    onChange={(e) => setThickness(parseFloat(e.target.value))}
                    className="w-full h-1.5 accent-amber-400 bg-slate-800 rounded cursor-pointer"
                  />
                </div>

                {/* Gap */}
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs font-code">
                    <span className="text-slate-400">Gap (Center Spacing):</span>
                    <strong className="text-amber-300 font-bold">{gap}</strong>
                  </div>
                  <input
                    type="range"
                    min="-8"
                    max="10"
                    step="0.5"
                    value={gap}
                    onChange={(e) => setGap(parseFloat(e.target.value))}
                    className="w-full h-1.5 accent-amber-400 bg-slate-800 rounded cursor-pointer"
                  />
                </div>

                {/* Alpha */}
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs font-code">
                    <span className="text-slate-400">Alpha (Opacity):</span>
                    <strong className="text-amber-300 font-bold">{alpha}</strong>
                  </div>
                  <input
                    type="range"
                    min="50"
                    max="255"
                    step="5"
                    value={alpha}
                    onChange={(e) => setAlpha(parseInt(e.target.value))}
                    className="w-full h-1.5 accent-amber-400 bg-slate-800 rounded cursor-pointer"
                  />
                </div>
              </div>

              {/* Toggles Row */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-800/80">
                <button
                  onClick={() => setDot(!dot)}
                  className={`px-3 py-2 rounded-lg text-xs font-code font-bold border transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
                    dot
                      ? 'bg-amber-500/20 text-amber-300 border-amber-400'
                      : 'bg-slate-900 text-slate-400 border-slate-800'
                  }`}
                >
                  <Circle className="w-3 h-3" />
                  <span>Dot: {dot ? 'ON' : 'OFF'}</span>
                </button>

                <button
                  onClick={() => setOutline(!outline)}
                  className={`px-3 py-2 rounded-lg text-xs font-code font-bold border transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
                    outline
                      ? 'bg-amber-500/20 text-amber-300 border-amber-400'
                      : 'bg-slate-900 text-slate-400 border-slate-800'
                  }`}
                >
                  <Square className="w-3 h-3" />
                  <span>Outline: {outline ? 'ON' : 'OFF'}</span>
                </button>

                <button
                  onClick={() => setTStyle(!tStyle)}
                  className={`px-3 py-2 rounded-lg text-xs font-code font-bold border transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
                    tStyle
                      ? 'bg-amber-500/20 text-amber-300 border-amber-400'
                      : 'bg-slate-900 text-slate-400 border-slate-800'
                  }`}
                >
                  <Type className="w-3 h-3" />
                  <span>T-Style: {tStyle ? 'ON' : 'OFF'}</span>
                </button>

                <button
                  onClick={() => setStyle(style === 4 ? 2 : 4)}
                  className={`px-3 py-2 rounded-lg text-xs font-code font-bold border transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
                    style === 2
                      ? 'bg-amber-500/20 text-amber-300 border-amber-400'
                      : 'bg-slate-900 text-slate-400 border-slate-800'
                  }`}
                >
                  <Flame className="w-3 h-3" />
                  <span>{style === 4 ? 'Static' : 'Dynamic'}</span>
                </button>
              </div>

              {/* Color Preset Palette */}
              <div className="space-y-2 pt-2 border-t border-slate-800/80">
                <span className="text-xs font-code text-slate-400 block">QUICK COLOR PALETTE:</span>
                <div className="flex items-center gap-2 flex-wrap">
                  {[
                    { label: 'Cyan', r: 0, g: 255, b: 255, bg: '#00ffff' },
                    { label: 'Green', r: 0, g: 255, b: 0, bg: '#00ff00' },
                    { label: 'Yellow', r: 255, g: 255, b: 0, bg: '#ffff00' },
                    { label: 'Magenta', r: 255, g: 0, b: 255, bg: '#ff00ff' },
                    { label: 'Red', r: 255, g: 30, b: 30, bg: '#ff2020' },
                    { label: 'White', r: 255, g: 255, b: 255, bg: '#ffffff' },
                  ].map((c) => (
                    <button
                      key={c.label}
                      onClick={() => handleColorPreset(c.r, c.g, c.b)}
                      className={`px-3 py-1 rounded-lg text-xs font-code font-bold flex items-center gap-1.5 border transition-all cursor-pointer ${
                        r === c.r && g === c.g && b === c.b
                          ? 'border-white bg-slate-800 text-white shadow-sm'
                          : 'border-slate-800 bg-slate-900 text-slate-400 hover:text-white'
                      }`}
                    >
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: c.bg }} />
                      <span>{c.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: CUSTOM SHAPES, LETTERS & NUMBERS (Geronimo's Request!) */}
          {mode === 'custom_shapes' && (
            <div className="p-5 rounded-2xl bg-slate-950/90 border border-slate-800 flex flex-col gap-5 shadow-sm">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <span className="font-cyber font-bold text-sm text-white flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  CUSTOM SHAPE &amp; MEME RETICLE ENGINE
                </span>
                <span className="text-[10px] font-code px-2 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-500/40">
                  ANY LETTER, NUMBER &amp; SYMBOL
                </span>
              </div>

              {/* Custom Text / Letter / Number Input */}
              <div className="space-y-1.5">
                <label className="text-xs font-code text-slate-300 font-semibold block">
                  TYPE ANY LETTER, NUMBER, OR MEME TEXT (1-4 CHARACTERS):
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    maxLength={4}
                    value={customText}
                    onChange={(e) => setCustomText(e.target.value)}
                    placeholder="e.g. G, W, 7, ❤️, EZ, VIP"
                    className="flex-1 px-4 py-2 rounded-xl bg-slate-900 border border-amber-500/40 text-amber-300 font-cyber font-bold text-base focus:outline-none focus:border-amber-400 placeholder:text-slate-600"
                  />
                  <button
                    onClick={() => setCustomText('G')}
                    className="px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-code text-slate-400 hover:text-amber-300 cursor-pointer"
                  >
                    Reset 'G'
                  </button>
                </div>
              </div>

              {/* Quick Shape Presets Picker */}
              <div className="space-y-2">
                <span className="text-xs font-code text-slate-400 block">POPULAR RETICLE SHAPES &amp; SYMBOLS:</span>
                <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                  {SHAPE_PRESETS.map((sp) => (
                    <button
                      key={sp.id}
                      onClick={() => {
                        setCustomText(sp.char);
                      }}
                      className={`px-2.5 py-1.5 rounded-lg border text-xs font-code flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
                        customText === sp.char
                          ? 'bg-amber-500/20 border-amber-400 text-amber-300 font-bold shadow-[0_0_10px_rgba(245,158,11,0.3)]'
                          : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
                      }`}
                    >
                      <span>{sp.char}</span>
                      <span>{sp.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Shape Size & Glow Sliders */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-800">
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs font-code">
                    <span className="text-slate-400">Shape Scale:</span>
                    <strong className="text-amber-300 font-bold">{shapeFontSize}px</strong>
                  </div>
                  <input
                    type="range"
                    min="14"
                    max="64"
                    step="2"
                    value={shapeFontSize}
                    onChange={(e) => setShapeFontSize(parseInt(e.target.value))}
                    className="w-full h-1.5 accent-amber-400 bg-slate-800 rounded cursor-pointer"
                  />
                </div>

                {/* Center Dot Toggle */}
                <div className="flex flex-col justify-end">
                  <button
                    onClick={() => setShowCenterDotUnderShape(!showCenterDotUnderShape)}
                    className={`w-full py-2 px-3 rounded-lg text-xs font-code font-bold border transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
                      showCenterDotUnderShape
                        ? 'bg-amber-500/20 text-amber-300 border-amber-400'
                        : 'bg-slate-900 text-slate-400 border-slate-800'
                    }`}
                  >
                    <Target className="w-3.5 h-3.5" />
                    <span>Center Aim Dot: {showCenterDotUnderShape ? 'ON' : 'OFF'}</span>
                  </button>
                </div>
              </div>

              {/* Pro-Tip Note about CS2 In-Game Tricks */}
              <div className="p-3 rounded-xl bg-amber-950/30 border border-amber-500/30 text-xs font-tech text-amber-200/90 leading-relaxed">
                💡 <strong className="text-amber-300">How to get Shape Crosshairs in real CS2:</strong> Valve CS2 console cvars draw lines, but players create <strong>Box / Square</strong> crosshairs by setting <code className="text-amber-300 font-code font-bold">cl_crosshairgap -5; cl_crosshairthickness 3</code>, and <strong>Dot / Circle</strong> crosshairs by setting <code className="text-amber-300 font-code font-bold">cl_crosshairsize 0; cl_crosshairdot 1; cl_crosshairthickness 2</code>!
              </div>
            </div>
          )}

          {/* Pro & Community Presets Shelf */}
          <div className="p-4 sm:p-5 rounded-2xl bg-slate-950/80 border border-slate-800 flex flex-col gap-3">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
              <span className="font-cyber font-bold text-xs text-slate-300 flex items-center gap-1.5">
                <Crown className="w-4 h-4 text-amber-400" />
                OFFICIAL PRO &amp; ZE META PRESETS (1-CLICK APPLY)
              </span>
              <span className="text-[10px] font-code text-amber-400/80">
                PROVEN WINNERS
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {PRO_CROSSHAIR_PRESETS.map((p) => (
                <button
                  key={p.name}
                  onClick={() => handleApplyPreset(p)}
                  className="p-2.5 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-amber-400/60 transition-all text-left group cursor-pointer shadow-sm hover:shadow-[0_0_15px_rgba(245,158,11,0.2)]"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-cyber font-bold text-white text-xs group-hover:text-amber-300 transition-colors">
                      {p.name}
                    </span>
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: `rgb(${p.r},${p.g},${p.b})` }} />
                  </div>
                  <div className="text-[9px] font-code px-1.5 py-0.2 rounded bg-slate-950 text-slate-400 border border-slate-800 inline-block mb-1">
                    {p.tag}
                  </div>
                  <div className="text-[10px] font-tech text-slate-400 truncate">
                    {p.role}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
