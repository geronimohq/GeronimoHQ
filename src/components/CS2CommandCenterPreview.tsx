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
declare const __APP_EXE_SIZE_MB__: number;

export const CS2CommandCenterPreview: React.FC = () => {
  const downloadUrl = '/CS2_Command_Center.exe?v=2.0.3';
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
      summary: 'Central hub with 1-click optimize, hardware detection, a persistent status bar and quick links to every tab, including the live server list.',
      details: [
        '1-Click Optimize: applies the engine tweaks you selected (shader cache purge, low-latency autoexec block, crash-dump cleanup, Game DVR off, fullscreen optimizations off) and your chosen Windows power plan. Restore Defaults reverts them.',
        'Hardware detection: reads your CPU and GPU, recognises AMD 3D V-Cache (X3D) and laptop CPUs, and recommends a matching Windows power plan.',
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
        'NEW: In-App Manual CFG Editor — read-only preview by default; Edit config unlocks the text box and Save writes autoexec.cfg after making a backup.',
        'Block 1 — Engine Tweaks: Appends [CS2 FPS OPTIMIZER - PERFORMANCE TWEAKS] (fps_max 0, rate 1000000, low-latency sleep) without touching personal binds.',
        'Block 2 — ZE Visual & Audio Binds: Appends [CS2 COMMAND CENTER - ZE VISUAL & AUDIO CUSTOMIZER] independently.',
        'Real-Time Live Preview: Automatically refreshes and scrolls to the bottom of autoexec.cfg with timestamp banner & confirmation.',
        'ZE Low Viewmodel preset (FOV 68, X:+2, Y:+2, Z:-2) that keeps the screen centre clear for crouch lasers, plus HUD colour and the frame-time / ping / packet-loss HUD graphs.',
        '1-key Boss/Laser audio ducking toggle (F7 switches game volume between 22% and 100%) and a voice mute toggle on F8. Both keys can be changed.'
      ],
      parameters: [
        { name: 'viewmodel_offset_z', value: '-2.0 (FOV 68)', desc: 'Clears center screen for crouch/ankle lasers' },
        { name: 'bind "F7" "ze_focus_Key"', value: 'volume 0.22 <-> 1.00', desc: 'Instant Boss/Laser audio ducking keybind' },
        { name: 'bind "F8" "voice_modenable_toggle"', value: 'Voice on / off', desc: 'Quick voice mute toggle' }
      ],
      proTip: 'Engine Tweaks and ZE Visual/Audio Binds are stored as two separate tagged sections inside autoexec.cfg—updating one never overwrites the other, and the live preview scrolls directly to your newly injected block!',
      noMemoryAccess: true
    },
    {
      id: 'engine',
      name: 'Engine Tweaks & Live Booster',
      shortTag: 'SOURCE 2 OPTIMIZER',
      badge: 'FRAME-TIME STABILITY',
      icon: <Cpu className="w-5 h-5 text-cyan-400" />,
      summary: 'Five selectable engine and Windows tweaks, a power plan chosen for your CPU, and a Live Booster that raises cs2.exe to High priority while it runs.',
      details: [
        'Shader pre-caching: purges fragmented DirectX/GPU shader caches, useful after game or driver updates.',
        'Low-latency autoexec block: fps_max 0, rate 1000000, low-latency sleep, snd_mixahead 0.025 and the frame-time / ping HUD graphs, in one marked block with a backup.',
        'Windows settings: Game DVR background capture off, fullscreen optimizations off for cs2.exe, and old crash dumps and temp files cleaned.',
        'Power plan: Balanced for Ryzen X3D and laptop CPUs, High Performance otherwise (you can change it).',
        'Live Booster: raises cs2.exe to High process priority while it runs. Nothing is saved, it resets when CS2 closes, and it never touches game memory.'
      ],
      parameters: [
        { name: 'Selectable tweaks', value: '5 + power plan', desc: 'Each can be switched off before you press One-click optimize' },
        { name: 'Process Priority', value: 'HIGH_PRIORITY_CLASS', desc: 'Live Booster only; resets when CS2 closes' },
        { name: 'Undo', value: 'Restore Defaults', desc: 'Reverts Game DVR, fullscreen optimizations, power plan and the autoexec block' }
      ],
      proTip: 'These tweaks aim at steadier frame times (1% lows) and fewer stutters, not a higher maximum FPS.',
      noMemoryAccess: true
    },
    {
      id: 'mpo',
      name: 'GPU MPO Diagnostics',
      shortTag: 'DISPLAY ENGINE',
      badge: 'READ-ONLY + COPY-READY COMMANDS',
      icon: <Zap className="w-5 h-5 text-amber-400" />,
      summary: 'Read-only diagnostics for Windows Multi-Plane Overlay (MPO) problems such as Alt-Tab black screens, driver timeouts and checkerboard glitches, with commands you copy and run yourself.',
      details: [
        'Shows your GPU and whether MPO is currently disabled, by reading the DisableOverlays and DWM OverlayTestMode registry values.',
        'Never edits the registry or your driver: it copies the disable and restore commands to your clipboard so you can run them yourself in an administrator terminal.',
        'Recommends a clean DDU (Display Driver Uninstaller) reinstall in Safe Mode first, with a link to the official DDU site.',
        'Explains in plain language when disabling MPO helps, what it costs (slightly higher idle GPU power) and that it does not add game latency.'
      ],
      parameters: [
        { name: 'Registry read', value: 'DisableOverlays / OverlayTestMode', desc: 'Read-only check of the current MPO state' },
        { name: 'DDU Recommendation', value: 'Clean Safe Mode Wipe', desc: 'Rule out driver corruption first' },
        { name: 'Changes made by the app', value: 'None', desc: 'You run the copied command yourself' }
      ],
      proTip: 'Before toggling MPO, try a DDU clean driver reinstall first. Only if Alt-Tab freezing or driver timeouts persist, disable MPO.',
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
      summary: 'Scans your CS2 workshop maps to free SSD space, protects subscribed server packs, and checks every workshop pack for damaged or unfinished downloads.',
      details: [
        'Protected packs: subscribed server map packs and server asset packs (GFL, Possession, RSS, Mapeadores / cOLa) are detected and cannot be ticked. An option also protects maps played in the last 14 days.',
        '1-click "Select all temp downloads (safe)" ticks only maps you are not subscribed to. Deleting asks for confirmation and cannot be undone.',
        'Verify Workshop VPK health: reads each pack\'s index and confirms that every data part is on disk and complete, so a download that stopped half way is found, not just a bad file header.',
        'Repair corrupted VPKs removes only the damaged workshop folders. It never follows links and skips anything changed in the last 15 minutes. Steam can download the map again afterwards.',
        'Filter tabs (All, Temp downloads, Subscribed packs, Server assets, Duplicates), search, and sort by size or date.'
      ],
      parameters: [
        { name: 'VPK check', value: 'Index + data parts', desc: 'Finds truncated files and missing or short archive parts' },
        { name: 'Target Directory', value: 'workshop/content/730', desc: 'Your Steam library workshop folder for CS2' },
        { name: 'Space freed', value: 'Depends on your maps', desc: 'Often several GB to tens of GB' }
      ],
      proTip: 'If a server kicks you with a missing-file error, run Verify Workshop VPK health. It cannot see changed bytes inside a complete file, but it finds incomplete downloads.',
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
      name: 'Steam Launch Options Editor',
      shortTag: 'ENGINE LAUNCHER',
      badge: 'COPY OR APPLY TO STEAM',
      icon: <Terminal className="w-5 h-5 text-blue-400" />,
      summary: 'Reads your current Steam launch options for CS2, keeps your own flags, and offers one competitive reference preset that you can copy or apply to Steam.',
      details: [
        '-novid skips the Valve intro video for a faster start.',
        '-nojoy turns off joystick polling.',
        '+fps_max 0 uncaps the frame rate (you can cap it to your refresh rate instead).',
        'Your own flags, for example -allow_third_party_software or -condebug, are kept. Apply writes Steam\'s localconfig.vdf (Steam must be closed) and keeps a backup; Copy lets you paste them into Steam yourself.'
      ],
      parameters: [
        { name: 'Reference preset', value: '-novid -nojoy +fps_max 0', desc: 'One click loads it into the editor' },
        { name: 'Apply to Steam', value: 'localconfig.vdf', desc: 'Close Steam first; a backup is kept' },
        { name: 'Log flag', value: '-condebug', desc: 'Type it here so the Log Analyzer and Discord card can read the CS2 log' }
      ],
      proTip: 'Add -condebug to your launch options so the Log Analyzer and the Discord card can read the CS2 log.',
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
        'Finds your server from the connection line CS2 writes to console.log (needs -condebug in your launch options, which you can type in the Launch Options tab), then falls back to matching the map and your Steam name.',
        'Cleared when CS2 closes. One switch turns it on or off, and Refresh now forces an update. It only talks to the Discord app on your PC through a local pipe.'
      ],
      parameters: [
        { name: 'Discord Client ID', value: 'CS2 Command Center RPC', desc: 'Official Rich Presence application' },
        { name: 'Detection', value: 'console.log + map + name', desc: 'Finds the server you are connected to' },
        { name: 'Buttons', value: 'Server IP + community Discord', desc: 'Visible to friends on your profile' }
      ],
      proTip: 'Add -condebug to your launch options so the app can read the server straight from the CS2 log.',
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
              v2.0.3
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
            Portable &bull; ~{typeof __APP_EXE_SIZE_MB__ !== 'undefined' ? __APP_EXE_SIZE_MB__ : 26} MB &bull; No installation required
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
