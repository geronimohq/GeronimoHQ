import React, { useState } from 'react';
import { 
  Download, 
  Sliders, 
  Cpu, 
  ShieldCheck, 
  Target, 
  Zap, 
  HardDrive, 
  Radio, 
  Terminal, 
  Copy, 
  Check, 
  Sparkles,
  ChevronRight,
  Info
} from 'lucide-react';

interface AppFeatureModule {
  id: string;
  name: string;
  shortTag: string;
  badge: string;
  icon: React.ReactNode;
  summary: string;
  details: string[];
  parameters: { name: string; value: string; desc: string }[];
  proTip: string;
  noMemoryAccess: boolean;
}

declare const __APP_EXE_SHA256__: string;

export const CS2CommandCenterPreview: React.FC = () => {
  const downloadUrl = '/CS2_Command_Center.exe?v=2.0.2';
  const exeSha256 = typeof __APP_EXE_SHA256__ !== 'undefined' ? __APP_EXE_SHA256__ : '66B78485C7C1F5622C12B702D07C83B7CEC781E344DC7AFE35B0272B494E7A01';
  const [activeTab, setActiveTab] = useState<string>('autoexec');
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [copiedHash, setCopiedHash] = useState<boolean>(false);

  const modules: AppFeatureModule[] = [
    {
      id: 'dashboard',
      name: 'CyberDeck Executive Dashboard & Telemetry',
      shortTag: 'TACTICAL COMMAND OS',
      badge: 'NEW TACTICAL CONSOLE',
      icon: <Terminal className="w-5 h-5 text-amber-400" />,
      summary: 'Centralized executive command hub featuring 1-click total optimization, balanced CPU/GPU hardware diagnostics, persistent bottom telemetry, and instant server jumping.',
      details: [
        '1-Click Total Optimization: Automatically verifies and applies recommended Source 2 CVARs, power plans, and autoexec binds in a single click.',
        'Hardware Architecture Telemetry: Real-time detection of AMD 3D V-Cache, Intel P/E-Core topologies, and discrete GPU drivers.',
        'Persistent CyberDeck Status Bar: Live slot sniper state and the DNS your adapter really uses. The Dashboard shows whether CS2 was found and where it is installed.',
        'New dark-glass interface with a reactor-core backdrop on every tab, left-rail navigation, and mouse back/forward buttons for moving between tabs.'
      ],
      parameters: [
        { name: 'Architecture', value: 'CyberDeck Command Rail', desc: 'Tactical left-rail navigation with instant view switching' },
        { name: 'Telemetry Bar', value: 'Real-time Win32 & UDP', desc: 'Reads game state (Valve GSI) and server info over UDP' },
        { name: 'Game process', value: 'No memory access', desc: 'Does not read or modify CS2 memory; no DLL injection' }
      ],
      proTip: 'The new CyberDeck Command Console is designed for quick alt-tab use; most features work offline.',
      noMemoryAccess: true
    },
    {
      id: 'servers',
      name: 'ZE Game Servers: Live Browser',
      shortTag: 'LIVE TELEMETRY',
      badge: 'GLOBAL + PLANET CHINA',
      icon: <Radio className="w-5 h-5 text-cyan-400" />,
      summary: 'Live Zombie Escape server list with humans-only player counts, ping, map pictures, time on the current map, a country/region estimate of who is playing, and a warning when you do not have the map yet.',
      details: [
        'Humans only: bots are subtracted from the player count, with a MOSTLY BOTS badge and a bots-excluded note on bot-heavy servers.',
        'Time on map per server: exact for GFL (from ZE Graph) and measured from player connection times elsewhere; a leading ">=" marks a minimum.',
        'Geo radar (estimate): Country or Region view per server, filling the card width up to two lines. It is an estimate from name signals and time of day; no player is identified.',
        'Missing-map warning: when a server plays a map that is not on your PC, an amber "Map not installed. Get it" link opens that map\'s Steam workshop page so you can subscribe before joining.',
        'Planet China: pick a community cluster (EXG, FyS, MoeUB, ZL, 93X). Those servers block the live player list, so the Players dialog is not offered there.',
        'Connect, Copy IP, Players list, 3D map, soundtrack, community Discord and portal links on every row, plus the GFL slot priority and a Refresh all button.'
      ],
      parameters: [
        { name: 'Queries', value: 'Steam A2S over UDP', desc: 'Read-only server info; no game memory access' },
        { name: 'Missing map', value: 'steam://url/CommunityFilePage', desc: 'Opens the map workshop page in Steam; you press Subscribe' },
        { name: 'Window', value: 'Edge WebView2', desc: 'Memory is trimmed while minimized or in the tray' }
      ],
      proTip: 'If a row shows the amber map warning, click it before you press Connect. CS2 only uses workshop maps that Steam downloaded itself.',
      noMemoryAccess: true
    },
    {
      id: 'autoexec',
      name: 'Autoexec & In-App Manual CFG Editor',
      shortTag: 'CONFIG & HUD ENGINE',
      badge: 'MANUAL EDIT + REAL-TIME PREVIEW',
      icon: <Sliders className="w-5 h-5 text-fuchsia-400" />,
      summary: 'Comprehensive autoexec studio: (1) Core Engine Tweaks, (2) ZE Visual & Audio Binds, and (3) Manual In-App CFG Editor with direct save capabilities.',
      details: [
        'NEW: In-App Manual CFG Editor — Safe read-only mode by default; toggling manual edit unlocks full in-app editing with a direct "Save CFG" button.',
        'Block 1 — Engine Tweaks: Appends [CS2 FPS OPTIMIZER - PERFORMANCE TWEAKS] (fps_max 0, rate 1000000, low-latency sleep) without touching personal binds.',
        'Block 2 — ZE Visual & Audio Binds: Appends [CS2 COMMAND CENTER - ZE VISUAL & AUDIO CUSTOMIZER] independently.',
        'Real-Time Live Preview: Automatically refreshes and scrolls to the bottom of autoexec.cfg with timestamp banner & confirmation.',
        'ZE Laser-Jump Low Viewmodel (FOV 68, X:+2, Y:+2, Z:-2) & First-Person Bullet Tracer Clutter Reducer (r_drawtracers_firstperson 0).',
        '1-Key Boss/Laser Audio Ducking Toggle (F7 switches game volume between 22% and 100%) & Panic Voice Mute key (F8).'
      ],
      parameters: [
        { name: 'viewmodel_offset_z', value: '-2.0 (FOV 68)', desc: 'Clears center screen for crouch/ankle lasers' },
        { name: 'bind "F7" "ze_duck_toggle"', value: 'volume 0.22 <-> 1.00', desc: 'Instant Boss/Laser audio ducking keybind' },
        { name: 'r_drawtracers_firstperson', value: '0 (Disabled)', desc: 'Eliminates 64-player Negev tracer clutter' }
      ],
      proTip: 'Engine Tweaks and ZE Visual/Audio Binds are stored as two separate tagged sections inside autoexec.cfg—updating one never overwrites the other, and the live preview scrolls directly to your newly injected block!',
      noMemoryAccess: true
    },
    {
      id: 'engine',
      name: 'Engine & CPU Affinity Tuning',
      shortTag: 'SOURCE 2 OPTIMIZER',
      badge: 'FPS STABILIZER',
      icon: <Cpu className="w-5 h-5 text-cyan-400" />,
      summary: 'Raises cs2.exe to High process priority while it runs, so background apps get CPU time after the game.',
      details: [
        'Elevates cs2.exe OS scheduling priority above background Discord/Chrome processes.',
        'Changes nothing inside the game process: only its Windows priority (reverts when CS2 closes).'
      ],
      parameters: [
        { name: 'Process Priority', value: 'HIGH_PRIORITY_CLASS', desc: 'Direct Windows thread scheduling elevation' },
        { name: 'Undo', value: 'Close CS2', desc: 'Priority is not saved; it resets on the next launch' }
      ],
      proTip: 'Particularly effective on 64-player Zombie Escape servers where heavy grenade smoke, particle effects, and laser barricades drop 1% low FPS.',
      noMemoryAccess: true
    },
    {
      id: 'mpo',
      name: 'GPU MPO & DWM Latency Fixer',
      shortTag: 'DISPLAY ENGINE',
      badge: 'ALT-TAB FIX',
      icon: <Zap className="w-5 h-5 text-amber-400" />,
      summary: 'Detects and resolves Windows Multi-Plane Overlay (MPO) driver conflicts that cause Alt-Tab black screens, display freezing, and desktop stutter.',
      details: [
        'Important: Before altering MPO, perform a clean DDU (Display Driver Uninstaller) wipe in Safe Mode + fresh GPU driver reinstall.',
        'Automatic scan of Windows Registry for active MPO overlays on NVIDIA & AMD drivers.',
        '1-Click automated MPO disable/enable patch with instant backup and restore.',
        'DWM (Desktop Window Manager) composition latency tuning for borderless & fullscreen modes.',
        'Hardware Accelerated GPU Scheduling (HAGS) compatibility diagnostics.'
      ],
      parameters: [
        { name: 'DDU Recommendation', value: 'Clean Safe Mode Wipe', desc: 'Rule out driver/shader corruption first' },
        { name: 'OverlayTestMode', value: '0x00000005 (Disabled)', desc: 'NVIDIA/AMD MPO registry bypass' },
        { name: 'DWM Composition', value: 'Low Latency Mode', desc: 'Eliminates DWM frame queue buffer delay' },
        { name: 'Alt-Tab Freeze', value: 'RESOLVED', desc: 'Seamless instant desktop switching' }
      ],
      proTip: 'Before toggling MPO, try running DDU + clean GPU driver reinstall first to verify if that solves your issue! If Alt-Tab freezing persists, disable MPO.',
      noMemoryAccess: true
    },
    {
      id: 'sniper',
      name: 'Silent Slot Watcher & Sniper',
      shortTag: 'DIRECT NETWORK',
      badge: 'SILENT UDP + 10S COOLDOWN',
      icon: <Target className="w-5 h-5 text-lime-400" />,
      summary: 'Monitors server player counts via low-overhead UDP A2S queries about four times a second while full. When a slot opens, it uses the console when CS2 is in front and otherwise opens a Steam connect link, with a 10-second cooldown.',
      details: [
        'True Silent Sniping: Watches server player count via lightweight UDP packets outside the game engine—preventing CS2 memory heap & SDR session leaks.',
        'Responsive Detection: Checks player counts about four times a second for rapid slot detection.',
        'Zero Console & Clipboard Spam while waiting (avoids Windows Clipboard History buildup).',
        'Uses console when CS2 is in front, otherwise opens Steam connect link, with 10s cooldown.',
        'GFL Priority Slot Tiers (Normal up to 61, Mapper/Supporter up to 62, VIP/Admin up to 63) and a separate target for all other servers. Only runs while CS2 is open.'
      ],
      parameters: [
        { name: 'Waiting Mode', value: 'Silent UDP A2S (0.25s)', desc: 'Zero CS2 RAM & Zero SDR leaks' },
        { name: 'Slot Detection Trigger', value: 'Console Connect', desc: 'Sends console connect when slot opens' },
        { name: 'Auto-Stop Cooldown', value: '10s Timer on Button', desc: 'Prevents duplicate spam & allows clean retry' }
      ],
      proTip: 'Set your slot priority (Normal ≤ 61, Supporter ≤ 62, VIP ≤ 63) and activate Slot Sniper—it queries server telemetry via background UDP about four times a second, using the console when CS2 is in front and otherwise opening a Steam connect link.',
      noMemoryAccess: true
    },
    {
      id: 'cleaner',
      name: 'ZE Map Cleaner & VPK Health Verifier',
      shortTag: 'STORAGE & VPK DOCTOR',
      badge: 'PROTECTED PACKS & SAFE CLEAN',
      icon: <HardDrive className="w-5 h-5 text-emerald-400" />,
      summary: 'Scans your CS2 Workshop and community maps directory to reclaim 10–50GB of SSD space, protects subscribed server packs, and verifies .vpk binary headers (0x55aa1234) to repair corrupted/incomplete downloads.',
      details: [
        'NEW: Protected Server Packs System - Automatically detects and safeguards subscribed packs (GFL 355+ ZE, Possession PSE, RSS Revenant, Mapeadores & cOLa) and maps played in the last 14 days.',
        'NEW: 1-Click "Select All Temp Downloads (Safe)" - Safely purges non-subscribed temporary server downloads with zero risk to subscribed collections.',
        'NEW: Steam Workshop VPK Binary Header Verifier (checks 0x55aa1234 signature across steamapps/workshop/content/730/).',
        'Filter tabs (All, Temp downloads, Subscribed packs, Server assets, Duplicates), search, sort by size or date, and a confirmation before anything is deleted. Subscribed packs and server assets cannot be ticked.'
      ],
      parameters: [
        { name: 'VPK Magic Signature', value: '0x55AA1234 (v1/v2)', desc: 'Detects truncated or corrupted Workshop packs' },
        { name: 'Target Directory', value: 'workshop/content/730', desc: 'CS2 Steam Workshop & custom maps folders' },
        { name: 'Space Reclaimed', value: '10 GB - 50 GB avg', desc: 'Instant SSD space recovery' }
      ],
      proTip: 'If you ever get kicked from a ZE server with a "Missing VPK" or "Pure Server File Mismatch" error, run the Workshop VPK Health Verifier in 1 click!',
      noMemoryAccess: true
    },
    {
      id: 'dns',
      name: 'Gaming DNS (Any / Custom) & Log Analyzer',
      shortTag: 'NETWORK & TELEMETRY',
      badge: 'ANY DNS + LOG PARSER',
      icon: <Sparkles className="w-5 h-5 text-violet-400" />,
      summary: 'Choose ANY DNS provider you want (not just the fastest!) with 1-click "Use This DNS" buttons on every row, Custom DNS IPv4 support, parallel UDP latency benchmarking, AND passive CS2 console.log session analysis.',
      details: [
        'NEW: Full DNS Freedom — Click any row or click "Use This DNS" on Cloudflare, Google, Quad9, OpenDNS, Level3, or AdGuard to apply your preferred resolver regardless of benchmark rank.',
        'NEW: Custom DNS IPv4 Input — Enter any custom Primary & Secondary IPv4 DNS servers and apply in 1 click.',
        'Post-Session CS2 Frame-Time & Network Jitter Log Analyzer (reads console.log only; no game hooks).',
        'Parallel real-time UDP port 53 latency & jitter benchmark + 1-Click Restore to ISP Default (Automatic DHCP).'
      ],
      parameters: [
        { name: 'Any / Custom DNS', value: 'Preset or Custom IPv4', desc: 'Pick any provider or enter custom Primary/Secondary IPs' },
        { name: 'Passive Log Analyzer', value: 'game/csgo/console.log', desc: 'Counts frame hitches, shader stalls & net jitter' },
        { name: 'Undo', value: 'Back to automatic DNS', desc: 'Windows netsh • 1-click restore (needs Administrator)' }
      ],
      proTip: 'You do not have to use the #1 fastest DNS—click any provider row (e.g. Quad9 for security or AdGuard for ad-blocking) or enter custom IPv4 addresses and apply immediately!',
      noMemoryAccess: true
    },
    {
      id: 'launch',
      name: 'Steam Launch Options Preset Builder',
      shortTag: 'ENGINE LAUNCHER',
      badge: 'PRESET GENERATOR',
      icon: <Terminal className="w-5 h-5 text-blue-400" />,
      summary: 'Launch option presets for Counter-Strike 2 that you can review and copy into Steam.',
      details: [
        'Skips the Valve splash video intro (-novid) for faster game launches.',
        'Disables controller joystick polling (-nojoy) to free input thread cycles.',
        'Adds launch options you can copy into Steam (review each one before use).',
        'High execution priority (-high) and physical thread affinity (-threads N).'
      ],
      parameters: [
        { name: 'Competitive Baseline', value: '-novid -nojoy -high', desc: 'Universal stutter-free baseline' },
        { name: 'CPU Thread Lock', value: '-threads 8 (Custom)', desc: 'Allocates exact physical core count' },
        { name: 'Third-Party Interop', value: '-allow_third_party_software', desc: 'For Discord / OBS / NVIDIA overlay' }
      ],
      proTip: 'Click any preset in the app to immediately copy the exact command line ready to paste into Steam CS2 Properties.',
      noMemoryAccess: true
    },
    {
      id: 'discord',
      name: 'Discord Rich Presence Integration',
      shortTag: 'SOCIAL RPC',
      badge: 'LIVE PROFILE SYNC',
      icon: <Radio className="w-5 h-5 text-indigo-400" />,
      summary: 'Shows the Zombie Escape server you are on, its map, player count and a session timer on your Discord profile, with buttons for the server IP and its community Discord.',
      details: [
        'Shows the server name, the current map and the live player count, with a session timer that starts when you join.',
        'Two buttons for friends: Server IP (connect link) and the server\'s own community Discord (GFL, Possession, Mapeadores, cOLa, RSS). Discord hides the buttons on your own profile.',
        'Finds your server from the connection line CS2 writes to console.log (needs -condebug, which the Launch Options tab can add), then falls back to matching the map and your Steam name.',
        'Cleared when CS2 closes. One switch turns it on or off, and Refresh now forces an update. It only talks to the Discord app on your PC through a local pipe.'
      ],
      parameters: [
        { name: 'Discord Client ID', value: 'CS2 Command Center RPC', desc: 'Official Rich Presence application' },
        { name: 'Detection', value: 'console.log + map + name', desc: 'Finds the server you are connected to' },
        { name: 'Buttons', value: 'Server IP + community Discord', desc: 'Visible to friends on your profile' }
      ],
      proTip: 'Add -condebug in the Launch Options tab so the app can read the server straight from the CS2 log.',
      noMemoryAccess: true
    }
  ];

  const currentModule = modules.find((m) => m.id === activeTab) || modules[0];

  const handleCopy = (key: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  return (
    <section id="cs2-command" className="relative w-full max-w-6xl mx-auto px-4 pt-2 pb-12 scroll-mt-4">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8 border-b border-[#1E2E26] pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="px-2.5 py-0.5 text-[10px] font-code rounded bg-fuchsia-950/80 text-fuchsia-300 border border-fuchsia-500/50">
              MODULE 01 // DESKTOP SUITE CONSOLE
            </span>
            <span className="text-xs font-code text-slate-400">
              WINDOWS 10 / 11 64-BIT // PORTABLE EXE
            </span>
          </div>
          <h2 className="text-2xl md:text-3xl font-cyber font-black text-white tracking-wider flex items-center gap-3">
            CS2 COMMAND CENTER
            <span className="text-xs font-code px-2 py-0.5 bg-fuchsia-950 text-fuchsia-300 border border-fuchsia-500/50 rounded uppercase">
              v2.0.2
            </span>
          </h2>
          <p className="text-sm font-tech text-slate-300 mt-1 max-w-2xl">
            Want seamless PC integration without manual file editing? Explore the full capabilities of the standalone desktop companion below.
          </p>
        </div>

        {/* Primary Download CTA */}
        <div className="flex flex-col items-start md:items-end gap-1.5">
          <a
            href={downloadUrl}
            download="CS2_Command_Center.exe"
            title="Download portable CS2 Command Center standalone executable for Windows 10/11"
            aria-label="Download CS2 Command Center executable"
            className="flex items-center gap-2.5 px-6 py-3 min-h-[44px] bg-gradient-to-r from-fuchsia-600 via-pink-600 to-cyan-600 hover:from-fuchsia-500 hover:to-cyan-500 text-white font-cyber text-xs tracking-wider font-bold rounded-xl shadow-[0_0_25px_rgba(255,0,127,0.4)] transition-all transform hover:-translate-y-0.5 cursor-pointer touch-manipulation"
          >
            <Download className="w-4 h-4 animate-bounce" />
            <span>DOWNLOAD APP (.EXE)</span>
          </a>
          <span className="text-[11px] font-code text-slate-400">
            Portable &bull; ~33 MB &bull; No installation required
          </span>

          <div id="exe-sha256-badge" className="flex items-center gap-1.5 text-[10px] font-code text-slate-400 mt-0.5 scroll-mt-28">
            <span className="text-slate-400">SHA-256:</span>
            <code className="text-cyan-300 select-all font-mono">{exeSha256.slice(0, 8).toLowerCase()}...{exeSha256.slice(-8).toLowerCase()}</code>
            <button
              onClick={() => {
                navigator.clipboard.writeText(exeSha256);
                setCopiedHash(true);
                setTimeout(() => setCopiedHash(false), 2000);
              }}
              title="Copy the SHA-256 hash to clipboard"
              className="px-1.5 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-cyan-300 border border-slate-700 cursor-pointer flex items-center gap-1 transition-colors touch-manipulation"
            >
              {copiedHash ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3 text-slate-400" />}
              <span className="font-bold">{copiedHash ? 'COPIED' : 'COPY'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Transparency Note: Stability & Consistency vs. Raw FPS */}
      <div className="mb-6 p-4 rounded-xl bg-cyan-950/30 border border-cyan-500/40 flex items-start gap-3">
        <Info className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
        <div className="text-xs font-tech text-slate-200 leading-relaxed">
          <strong className="font-cyber text-cyan-300 tracking-wide uppercase block mb-0.5">
            WHAT THIS OPTIMIZER & PC MAINTENANCE ACTUALLY DO (STABILITY vs. RAW FPS):
          </strong>
          These tools are <strong className="text-white">not</strong> meant to magically inflate maximum FPS beyond your physical CPU/GPU hardware limits. Instead, they are engineered to improve <strong className="text-cyan-300">Frame-Time Consistency (1% Lows)</strong>, eliminate micro-stutters during 64-player Zombie Escape &amp; heavy smoke utility, resolve <strong className="text-cyan-300">Display / Alt-Tab freezes (MPO)</strong>, optimize <strong className="text-cyan-300">Sub-Tick &amp; Gaming DNS network responsiveness</strong>, and maintain peak SSD/OS storage health with <strong className="text-lime-300">an undo for each change</strong> (zero risky RAM cleaners).
        </div>
      </div>

      {/* Interactive Feature Console Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-8">
        
        {/* Left Module Navigation Tabs (4 Cols) */}
        <div className="lg:col-span-4 flex flex-col gap-2 bg-slate-950/80 p-3 rounded-2xl border border-slate-800 backdrop-blur-md">
          <div className="px-3 py-2 text-[11px] font-code text-slate-400 font-bold border-b border-slate-800/80 flex items-center justify-between">
            <span>APP MODULES ({modules.length})</span>
            <span className="text-fuchsia-400">CLICK TO EXPLORE</span>
          </div>

          <div className="flex flex-col gap-2">
            {modules.map((mod) => {
              const isActive = activeTab === mod.id;
              return (
                <button
                  key={mod.id}
                  onClick={() => setActiveTab(mod.id)}
                  title={`View details for ${mod.name}`}
                  aria-label={`Select ${mod.name} module`}
                  className={`w-full text-left p-3 min-h-[44px] rounded-xl border transition-all flex items-center justify-between cursor-pointer group touch-manipulation ${
                    isActive
                      ? 'bg-gradient-to-r from-fuchsia-950/80 to-slate-900 border-fuchsia-500/60 shadow-[0_0_15px_rgba(255,0,127,0.25)] text-white'
                      : 'bg-slate-900/40 border-slate-800/80 hover:bg-slate-900 hover:border-slate-700 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className={`p-2 rounded-lg border transition-colors ${
                      isActive ? 'bg-fuchsia-950 border-fuchsia-500/50' : 'bg-slate-950 border-slate-800 group-hover:border-slate-700'
                    }`}>
                      {mod.icon}
                    </div>
                    <div className="min-w-0">
                      <div className="text-xs font-cyber font-bold truncate">
                        {mod.name}
                      </div>
                      <div className="text-[10px] font-code text-slate-400 truncate">
                        {mod.shortTag}
                      </div>
                    </div>
                  </div>

                  <ChevronRight className={`w-4 h-4 transition-transform flex-shrink-0 ${
                    isActive ? 'text-fuchsia-400 translate-x-1' : 'text-slate-400'
                  }`} />
                </button>
              );
            })}
          </div>
        </div>

        {/* Right Feature Detail Display (8 Cols) */}
        <div className="lg:col-span-8 bg-slate-950/90 rounded-2xl border border-fuchsia-500/40 p-6 backdrop-blur-md shadow-[0_0_30px_rgba(255,0,127,0.1)] flex flex-col justify-between">
          <div>
            {/* Top Badge Row */}
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4 mb-4">
              <div className="flex items-center gap-2">
                <span className="p-2 rounded-lg bg-fuchsia-950/80 border border-fuchsia-500/40">
                  {currentModule.icon}
                </span>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-code bg-fuchsia-950 text-fuchsia-300 border border-fuchsia-500/50 font-bold">
                      {currentModule.badge}
                    </span>
                    <span className="text-[10px] font-code text-emerald-400 flex items-center gap-1 font-bold">
                      <ShieldCheck className="w-3 h-3" /> NO GAME MEMORY ACCESS
                    </span>
                  </div>
                  <h3 className="text-lg md:text-xl font-cyber font-bold text-white mt-1">
                    {currentModule.name}
                  </h3>
                </div>
              </div>
            </div>

            {/* Summary */}
            <p className="text-sm font-tech text-slate-300 leading-relaxed mb-5">
              {currentModule.summary}
            </p>

            {/* Feature Bullet Points */}
            <div className="mb-6">
              <h4 className="text-xs font-code font-bold text-fuchsia-300 uppercase tracking-wider mb-2.5">
                Included Capabilities & Logic:
              </h4>
              <ul className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                {currentModule.details.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-xs font-tech text-slate-300 bg-slate-900/50 p-2.5 rounded-lg border border-slate-800/80">
                    <span className="text-fuchsia-400 font-bold mt-0.5">&bull;</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Parameters & Variables Preview Table */}
            <div className="mb-6">
              <h4 className="text-xs font-code font-bold text-cyan-300 uppercase tracking-wider mb-2.5">
                Engine Commands & Registry Configuration:
              </h4>
              <div className="overflow-x-auto border border-slate-800 rounded-xl bg-slate-900/60">
                <table className="w-full text-left text-xs font-code">
                  <thead className="bg-slate-900 border-b border-slate-800 text-slate-400">
                    <tr>
                      <th className="py-2 px-3">Setting / Command</th>
                      <th className="py-2 px-3">Configured Value</th>
                      <th className="py-2 px-3">Impact</th>
                      <th className="py-2 px-3 text-right">Copy</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {currentModule.parameters.map((param, idx) => (
                      <tr key={idx} className="hover:bg-slate-900/80 transition-colors">
                        <td className="py-2 px-3 font-semibold text-cyan-300">{param.name}</td>
                        <td className="py-2 px-3 text-fuchsia-300">{param.value}</td>
                        <td className="py-2 px-3 text-slate-400 text-[11px]">{param.desc}</td>
                        <td className="py-2 px-3 text-right">
                          <button
                            onClick={() => handleCopy(`${currentModule.id}-${idx}`, `${param.name} ${param.value}`)}
                            className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors cursor-pointer"
                            title="Copy command"
                          >
                            {copiedKey === `${currentModule.id}-${idx}` ? (
                              <Check className="w-3.5 h-3.5 text-emerald-400" />
                            ) : (
                              <Copy className="w-3.5 h-3.5" />
                            )}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Pro Tip Callout Footer */}
          <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs font-tech text-slate-300 flex items-start gap-2.5">
            <Sparkles className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
            <div>
              <strong className="text-amber-300">Pro-Tip:</strong> {currentModule.proTip}
            </div>
          </div>
        </div>

      </div>

      {/* Unified Security & First-Launch Guidance Banner */}
      <div className="mt-6 p-4 rounded-xl bg-slate-950/90 border border-slate-800 shadow-lg">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 divide-y md:divide-y-0 md:divide-x divide-slate-800/80">
          {/* What the app changes (plain facts) */}
          <div className="flex items-start gap-3 text-xs font-tech text-slate-300 pr-0 md:pr-4">
            <ShieldCheck className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-cyber font-bold text-white text-xs mb-1 flex items-center gap-1.5">
                <span>WHAT IT CHANGES</span>
                <span className="text-[10px] font-code px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-500/40">PLAIN FACTS</span>
              </div>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                Modifies standard CS2 text config files (<code className="text-cyan-300">.cfg</code>) and uses Valve&apos;s official Steam game server protocols and Windows registry entries. It does <strong className="text-white">not</strong> read or modify CS2 memory, inject DLLs or patch game files. It can raise CS2&apos;s process priority and type a <code className="text-cyan-300">connect</code> command into the CS2 console. Hobby project, not affiliated with Valve. Use at your own risk.
              </p>
            </div>
          </div>

          {/* Windows Defender SmartScreen Notice */}
          <div className="flex items-start gap-3 text-xs font-tech text-slate-300 pt-3 md:pt-0 pl-0 md:pl-4">
            <Info className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <div className="w-full">
              <div className="font-cyber font-bold text-amber-300 text-xs mb-1 flex items-center gap-1.5">
                <span>FIRST-TIME LAUNCH // WINDOWS SMARTSCREEN</span>
                <span className="text-[10px] font-code px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-500/40">COMMUNITY EXE</span>
              </div>
              <p className="text-slate-400 leading-relaxed text-[11px] mb-2">
                If Windows displays <span className="text-white font-medium">&ldquo;Windows protected your PC&rdquo;</span>, this is normal Microsoft Defender SmartScreen reputation filtering for newly compiled unsigned tools.
              </p>
              <div className="flex flex-wrap items-center gap-1.5 text-[10px] font-code text-slate-300 bg-slate-900/90 p-1.5 rounded-lg border border-slate-800">
                <span className="text-amber-400 font-bold">To Run:</span>
                <span>1. Click <strong className="text-cyan-300">&ldquo;More info&rdquo;</strong></span>
                <span>&rarr;</span>
                <span>2. Click <strong className="text-emerald-400">&ldquo;Run anyway&rdquo;</strong></span>
                <span className="text-slate-400 hidden lg:inline">|</span>
                <span className="text-[9px] text-slate-400 hidden lg:inline">(or right-click .exe &rarr; Properties &rarr; &ldquo;Unblock&rdquo;)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
