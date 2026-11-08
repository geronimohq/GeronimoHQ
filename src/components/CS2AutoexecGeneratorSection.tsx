import React, { useState, useMemo } from 'react';
import { Sliders, Download, Copy, Check, Terminal, ShieldCheck, Volume2, Eye, Sparkles } from 'lucide-react';

export const CS2AutoexecGeneratorSection: React.FC = () => {
  const [zeLowViewmodel, setZeLowViewmodel] = useState(true);
  const [disableTracers, setDisableTracers] = useState(true);
  const [bossDuckBind, setBossDuckBind] = useState(true);
  const [duckKey, setDuckKey] = useState('F7');
  const [voiceMuteBind, setVoiceMuteBind] = useState(true);
  const [muteKey, setMuteKey] = useState('F8');
  const [radarHudScaling, setRadarHudScaling] = useState(true);
  const [radarZoomBind, setRadarZoomBind] = useState(true);
  const [radarZoomKey, setRadarZoomKey] = useState('v');
  const [maxSubtickRates, setMaxSubtickRates] = useState(true);
  const [crispAudioEq, setCrispAudioEq] = useState(true);
  const [smartTelemetryHud, setSmartTelemetryHud] = useState(true);
  const [performanceTweaks, setPerformanceTweaks] = useState(true);
  const [hudColor, setHudColor] = useState('none');
  const [fpsMax, setFpsMax] = useState('0');
  const [copiedCfg, setCopiedCfg] = useState(false);
  const [copiedLaunch, setCopiedLaunch] = useState(false);
  const [copiedPath, setCopiedPath] = useState(false);

  const generatedCfg = useMemo(() => {
    const sanitizedFps = Math.max(0, Math.min(999, parseInt(fpsMax || '0', 10) || 0));
    const lines: string[] = [
      '// ============================================================================',
      '// GERONIMOHQ.COM // CS2 & ZOMBIE ESCAPE PRO AUTOEXEC.CFG',
      '// Engine CVars & Settings • Place in: steamapps/common/Counter-Strike Global Offensive/game/csgo/cfg/',
      '// ============================================================================',
      '',
      `fps_max "${sanitizedFps}"`,
      '',
    ];

    if (performanceTweaks) {
      lines.push(
        '// ============================================================',
        '// [CS2 FPS OPTIMIZER - PERFORMANCE TWEAKS]',
        '// ============================================================',
        `fps_max "${sanitizedFps}"`,
        'engine_low_latency_sleep_after_client_tick true  // Synchronizes engine ticks to reduce frame stutter',
        'snd_mixahead "0.025"                        // Low audio buffer (0.025s) reduces sound delay & spikes',
        'snd_headphone_eq "0"                        // Disables headphone EQ DSP for lowest CPU overhead',
        'snd_spatialize_lerp "1"',
        'rate "1000000"                              // 1 Mbps max bandwidth',
        'cl_net_buffer_ticks "0"                     // Minimum interpolation delay (fastest packet processing)',
        'cl_allow_animated_avatars "0"               // Disables animated Steam avatars (fixes scoreboard FPS drop)',
        'r_player_visibility_mode "1"                // Enhances enemy contrast',
        'cl_hud_telemetry_frametime_show "2"         // Shows frametime graph if a micro-stutter occurs',
        'cl_hud_telemetry_ping_show "2"              // Real-time ping display',
        'cl_hud_telemetry_net_misdelivery_show "2"   // Real-time packet loss / choke notification',
        'cl_ragdoll_workaround_threshold "0"',
        ''
      );
    }

    if (hudColor && hudColor !== 'none') {
      lines.push(
        '// --- CUSTOM HUD COLOR THEME ---',
        `cl_hud_color "${hudColor}"`,
        ''
      );
    }

    if (maxSubtickRates) {
      lines.push(
        '// --- NETWORK RATES & BUFFER TICKS ---',
        'rate "786432" // (CS2 engine default - typical, check yours)',
        'cl_net_buffer_ticks "0"',
        ''
      );
    }

    if (zeLowViewmodel) {
      lines.push(
        '// --- ZE LASER-JUMP LOW VIEWMODEL (IMPROVED BOTTOM-SCREEN VISIBILITY) ---',
        'viewmodel_fov "68"',
        'viewmodel_offset_x "2.0"',
        'viewmodel_offset_y "2.0"',
        'viewmodel_offset_z "-2.0"',
        ''
      );
    }

    if (disableTracers) {
      lines.push(
        '// --- REDUCE 64-PLAYER NEGEV / BULLET TRACER VISUAL CLUTTER ---',
        'r_drawtracers_firstperson "0"',
        ''
      );
    }

    if (crispAudioEq) {
      lines.push(
        '// --- SPATIAL AUDIO CLARITY & FOOTSTEP EQ ---',
        'snd_headphone_eq "1"',
        'snd_spatialize_lerp "0.5"',
        'snd_steamaudio_enable_perspective_correction "1"',
        'snd_mute_losefocus "0"',
        ''
      );
    }

    if (bossDuckBind) {
      const k = (duckKey || 'F7').trim();
      lines.push(
        '// --- ZE BOSS / ENDING LASER AUDIO DUCKING TOGGLE (22% vs 85% VOLUME) ---',
        'alias "ze_duck_on" "volume 0.22; alias ze_duck_toggle ze_duck_off; echo [ZE] Boss/Laser Audio Ducked (22%)"',
        'alias "ze_duck_off" "volume 0.85; alias ze_duck_toggle ze_duck_on; echo [ZE] Normal Audio Restored (85%)"',
        'alias "ze_duck_toggle" "ze_duck_on"',
        `bind "${k}" "ze_duck_toggle"`,
        ''
      );
    }

    if (voiceMuteBind) {
      const m = (muteKey || 'F8').trim();
      lines.push(
        '// --- PANIC VOICE CHAT MUTE TOGGLE ---',
        'alias "ze_voice_off" "voice_modenable 0; alias ze_voice_toggle ze_voice_on; echo [ZE] Voice Chat Muted (0)"',
        'alias "ze_voice_on" "voice_modenable 1; alias ze_voice_toggle ze_voice_off; echo [ZE] Voice Chat Restored (1)"',
        'alias "ze_voice_toggle" "ze_voice_off"',
        `bind "${m}" "ze_voice_toggle"`,
        ''
      );
    }

    if (radarZoomBind) {
      const rk = (radarZoomKey || 'v').trim();
      lines.push(
        '// --- RADAR ZOOM TOGGLE (0.40 WIDE vs 0.80 CLOSE-UP) ---',
        'alias "ze_radar_toggle" "ze_radar_zoom_in"',
        'alias "ze_radar_zoom_in" "cl_radar_scale 0.80; alias ze_radar_toggle ze_radar_zoom_out; echo [ZE] Radar Zoom: Close-Up (0.80)"',
        'alias "ze_radar_zoom_out" "cl_radar_scale 0.40; alias ze_radar_toggle ze_radar_zoom_in; echo [ZE] Radar Zoom: Overview (0.40)"',
        `bind "${rk}" "ze_radar_toggle"`,
        ''
      );
    }

    if (radarHudScaling) {
      lines.push(
        '// --- RADAR & HUD SCALING DEFAULTS ---',
        'hud_scaling "0.90"',
        'cl_radar_always_centered "0"',
        'cl_radar_scale "0.40"',
        ''
      );
    }



    if (smartTelemetryHud) {
      lines.push(
        '// --- SMART FRAME-TIME & NETWORK JITTER TELEMETRY HUD ---',
        'cl_hud_telemetry_frametime_show "2"',
        'cl_hud_telemetry_ping_show "2"',
        'cl_hud_telemetry_net_misdelivery_show "2"',
        ''
      );
    }

    const duckK = (duckKey || 'F7').trim();
    const muteK = (muteKey || 'F8').trim();
    const radarK = (radarZoomKey || 'v').trim();

    lines.push(
      '// ============================================================================',
      '// HOW TO REVERT ALL SETTINGS & BINDS TO DEFAULTS (COMPLETE REVERT / UNDO GUIDE):',
      '// Restart CS2 to clear memory-resident aliases (ze_duck_toggle, etc.).',
      '// Note: unverified defaults are labeled (typical, check yours).',
      '//',
      '// --- REVERT CUSTOM BINDS ---',
      `// unbind "${duckK}"`,
      `// unbind "${muteK}"`,
      `// unbind "${radarK}"`,
      '//',
      '// --- REVERT ENGINE CVARS & HUD SETTINGS ---',
      '// fps_max 400 // (CS2 factory default - typical, check yours)',
      '// cl_hud_color 0 // (typical default: 0 - Team Color, check yours)',
      '// rate 786432 // (CS2 engine default, check yours)',
      '// cl_net_buffer_ticks 1 // (CS2 1-packet buffer interpolation default - typical, check yours)',
      '// engine_low_latency_sleep_after_client_tick false // (CS2 default - typical, check yours)',
      '// snd_mixahead 0.025 // (CS2 default: 0.025, check yours)',
      '// cl_allow_animated_avatars 1 // (CS2 default: 1, check yours)',
      '// r_player_visibility_mode 1 // (CS2 default: 1, check yours)',
      '// cl_ragdoll_workaround_threshold 1 // (CS2 default: 1, check yours)',
      '// viewmodel_presetpos 1 // (restores CS2 default viewmodel)',
      '// r_drawtracers_firstperson 1 // (typical default: 1, check yours)',
      '// snd_headphone_eq 0 // (typical default: 0 - Natural, check yours)',
      '// snd_spatialize_lerp 0.0 // (typical default: 0.0, check yours)',
      '// snd_steamaudio_enable_perspective_correction 0 // (typical default: 0, check yours)',
      '// snd_mute_losefocus 1 // (typical default: 1, check yours)',
      '// volume 1.0 // (typical default, check yours)',
      '// voice_modenable 1 // (typical default: 1, check yours)',
      '// cl_radar_scale 0.70 // (typical default: 0.70, check yours)',
      '// cl_radar_always_centered 1 // (typical default: 1, check yours)',
      '// hud_scaling 1.0 // (typical default: 1.0, check yours)',
      '// cl_hud_telemetry_frametime_show 0 // (typical default: 0, check yours)',
      '// cl_hud_telemetry_ping_show 0 // (typical default: 0, check yours)',
      '// cl_hud_telemetry_net_misdelivery_show 0 // (typical default: 0, check yours)',
      '// ============================================================================',
      ''
    );
    lines.push('echo "[GeronimoHQ] CS2 & ZE Autoexec Loaded Successfully!"');
    return lines.join('\n');
  }, [
    zeLowViewmodel,
    disableTracers,
    bossDuckBind,
    duckKey,
    voiceMuteBind,
    muteKey,
    radarHudScaling,
    radarZoomBind,
    radarZoomKey,
    maxSubtickRates,
    crispAudioEq,
    smartTelemetryHud,
    hudColor,
    fpsMax,
    performanceTweaks,
  ]);

  const handleDownloadCfg = () => {
    const blob = new Blob([generatedCfg], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'autoexec.cfg';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleCopyCfg = () => {
    navigator.clipboard.writeText(generatedCfg);
    setCopiedCfg(true);
    setTimeout(() => setCopiedCfg(false), 2000);
  };

  const handleCopyLaunch = () => {
    navigator.clipboard.writeText(`-novid -nojoy +fps_max ${fpsMax} +exec autoexec.cfg`);
    setCopiedLaunch(true);
    setTimeout(() => setCopiedLaunch(false), 2000);
  };

  return (
    <section id="cfg-studio" className="relative w-full max-w-6xl mx-auto px-4 py-12 scroll-mt-28">
      <div className="rounded-2xl border border-cyan-500/40 bg-gradient-to-b from-cyan-950/20 via-slate-950/90 to-[#050811] p-6 md:p-8 shadow-[0_0_45px_rgba(0,240,255,0.12)]">
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-6 border-b border-cyan-500/30 pb-4">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-1.5">
              <span className="px-2.5 py-0.5 text-[10px] font-code rounded bg-cyan-950/90 text-cyan-300 border border-cyan-500/50">
                WEB CONFIG STUDIO // ZERO INSTALL NEEDED
              </span>
              <span className="px-2 py-0.5 text-[10px] font-code rounded bg-emerald-950/90 text-emerald-300 border border-emerald-500/50 flex items-center gap-1 font-bold">
                <ShieldCheck className="w-3 h-3 text-emerald-400" />
                100% VAC-SAFE CVARS
              </span>
            </div>
            <h2 className="text-2xl md:text-3xl font-cyber font-black text-white tracking-wider flex items-center gap-2.5">
              <Sliders className="w-7 h-7 text-cyan-400" />
              <span>CS2 AUTOEXEC &amp; ZE LASER BINDS STUDIO</span>
            </h2>
            <p className="text-sm font-tech text-slate-300 mt-1 max-w-3xl">
              Customize your Zombie Escape Laser-Jump Viewmodel, Boss Audio Ducking keybind, First-Person Tracer clutter reducer, and Sub-Tick network rates right in your browser, then download a ready-to-use <code className="text-cyan-300">autoexec.cfg</code> in 1 click.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={handleDownloadCfg}
              title="Download generated autoexec.cfg directly to your computer's Downloads folder"
              className="min-h-[44px] flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-cyber text-xs font-black tracking-wider shadow-[0_0_20px_rgba(0,240,255,0.4)] cursor-pointer transition-all touch-manipulation"
            >
              <Download className="w-4 h-4" />
              <span>DOWNLOAD AUTOEXEC.CFG</span>
            </button>
            <button
              onClick={handleCopyCfg}
              title="Copy complete generated autoexec.cfg script to Windows clipboard"
              className="min-h-[44px] flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-cyan-300 border border-cyan-500/40 font-code text-xs font-bold cursor-pointer transition-all touch-manipulation"
            >
              {copiedCfg ? <Check className="w-4 h-4 text-lime-400" /> : <Copy className="w-4 h-4" />}
              <span>{copiedCfg ? 'COPIED!' : 'COPY CFG'}</span>
            </button>
          </div>
        </div>

        {/* File Installation Location Helper */}
        <div className="mb-6 p-4 rounded-xl bg-slate-950/80 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs font-code text-slate-300">
          <div className="space-y-1.5 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-amber-400 font-bold flex-shrink-0">📁 DEFAULT CFG DIRECTORY:</span>
              <code className="text-lime-300 select-all font-bold">C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg\</code>
            </div>
            <p className="text-[11px] text-slate-400 font-sans leading-relaxed">
              *Note: Your drive letter or Steam library folder may differ (e.g. <code className="text-cyan-300">H:\SteamLibrary\...</code>). To locate your exact folder in Steam: right-click Counter-Strike 2 &rarr; Manage &rarr; Browse local files &rarr; open <code className="text-cyan-300">game/csgo/cfg/</code>.
            </p>
            <p className="text-[11px] text-amber-300/90 font-sans">
              💡 <strong>Console Tip:</strong> If your settings do not apply automatically at game launch (e.g. overridden by Steam Cloud), open the in-game console (`~`) and type <code className="text-lime-300 font-code font-bold">exec autoexec</code>.
            </p>
          </div>
          <button
            onClick={() => {
              navigator.clipboard.writeText("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Counter-Strike Global Offensive\\game\\csgo\\cfg");
              setCopiedPath(true);
              setTimeout(() => setCopiedPath(false), 2000);
            }}
            title="Copy default CS2 cfg folder path to clipboard (adjust drive letter if installed on another drive)"
            className="min-h-[44px] px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-slate-700 text-xs font-bold flex items-center gap-1.5 cursor-pointer flex-shrink-0 transition-colors touch-manipulation"
          >
            {copiedPath ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copiedPath ? 'Copied Folder Path!' : 'Copy Default Folder Path'}</span>
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Interactive Toggles & Keybind Inputs (6 Cols) */}
          <div className="lg:col-span-6 space-y-3 bg-slate-900/70 border border-slate-800 rounded-xl p-4">
            <div className="text-xs font-code text-cyan-300 font-bold uppercase flex items-center gap-1.5 border-b border-slate-800 pb-2">
              <Eye className="w-4 h-4 text-cyan-400" />
              <span>1. ZOMBIE ESCAPE VISUAL &amp; AUDIO PRESETS</span>
            </div>

            {/* In-App Engine & Sub-Tick Performance Tweaks */}
            <div className="p-3 rounded-xl bg-slate-950/80 border border-cyan-500/30">
              <label 
                title="Applies CS2 FPS Optimizer engine & sub-tick tweaks: engine_low_latency_sleep, snd_mixahead 0.025, 1 Mbps bandwidth, and animated avatar fix."
                className="flex items-start gap-2.5 text-xs font-tech text-slate-200 cursor-pointer select-none"
              >
                <input
                  type="checkbox"
                  checked={performanceTweaks}
                  onChange={(e) => setPerformanceTweaks(e.target.checked)}
                  className="mt-0.5 w-4 h-4 accent-cyan-400 rounded cursor-pointer"
                />
                <div>
                  <span className="font-bold text-white flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                    CS2 FPS Optimizer Engine &amp; Sub-Tick Performance Tweaks
                  </span>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    Low-latency tick sleep (<code className="text-cyan-300">engine_low_latency_sleep_after_client_tick true</code>), 0.025s sound buffer, 1 Mbps bandwidth, and animated avatar fix.
                  </p>
                </div>
              </label>
            </div>

            <label 
              title="Sets weapon viewmodel_fov 68 and offsets gun model (X:2.0, Y:2.0, Z:-2.0) down and right for improved bottom-screen visibility. Note: Player camera FOV is locked by CS2 engine at 90."
              className="flex items-start gap-2.5 text-xs font-tech text-slate-200 cursor-pointer select-none"
            >
              <input
                type="checkbox"
                checked={zeLowViewmodel}
                onChange={(e) => setZeLowViewmodel(e.target.checked)}
                className="mt-0.5 w-4 h-4 accent-cyan-400 rounded cursor-pointer"
              />
              <div>
                <span className="font-bold text-white">ZE Laser-Jump Low Viewmodel (viewmodel_fov 68, X:+2, Y:+2, Z:-2)</span>
                <p className="text-[11px] text-slate-400">Lowers and pushes gun model to the corner so you can see crouch &amp; ankle lasers. (Note: Controls weapon model; camera eye FOV is locked at 90 by Valve).</p>
              </div>
            </label>

            <label 
              title="Disable first-person bullet tracers (r_drawtracers_firstperson 0) to eliminate blinding clutter"
              className="flex items-start gap-2.5 text-xs font-tech text-slate-200 cursor-pointer select-none"
            >
              <input
                type="checkbox"
                checked={disableTracers}
                onChange={(e) => setDisableTracers(e.target.checked)}
                className="mt-0.5 w-4 h-4 accent-cyan-400 rounded cursor-pointer"
              />
              <div>
                <span className="font-bold text-white">Hide First-Person Bullet Tracers (r_drawtracers_firstperson 0)</span>
                <p className="text-[11px] text-slate-400">Eliminates blinding muzzle tracer clutter when 45 humans fire Negevs at ZE bosses.</p>
              </div>
            </label>

            <div className="flex flex-wrap items-center justify-between gap-2 bg-slate-950/80 border border-slate-800/90 rounded-lg p-2.5">
              <label 
                title="Toggles between ducked volume (0.22) and standard volume (0.85). Note: overrides active volume setting when key is pressed."
                className="flex items-center gap-2 text-xs font-tech text-slate-200 cursor-pointer select-none"
              >
                <input
                  type="checkbox"
                  checked={bossDuckBind}
                  onChange={(e) => setBossDuckBind(e.target.checked)}
                  className="w-4 h-4 accent-fuchsia-400 rounded cursor-pointer"
                />
                <Volume2 className="w-4 h-4 text-fuchsia-400" />
                <span className="font-bold text-white">Boss / Laser Audio Ducking Toggle (22% vs 85%)</span>
              </label>
              <div className="flex items-center gap-1.5 text-xs font-code">
                <span className="text-slate-400">Key:</span>
                <input
                  type="text"
                  value={duckKey}
                  onChange={(e) => setDuckKey(e.target.value)}
                  title="Keyboard key to toggle boss audio ducking (e.g. F7, Mouse4)"
                  className="w-12 px-2 py-0.5 rounded bg-slate-900 border border-fuchsia-500/50 text-fuchsia-300 text-center font-bold"
                />
              </div>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-2 bg-slate-950/80 border border-slate-800/90 rounded-lg p-2.5">
              <label 
                title="Toggles voice chat between muted (voice_modenable 0) and enabled (voice_modenable 1)"
                className="flex items-center gap-2 text-xs font-tech text-slate-200 cursor-pointer select-none"
              >
                <input
                  type="checkbox"
                  checked={voiceMuteBind}
                  onChange={(e) => setVoiceMuteBind(e.target.checked)}
                  className="w-4 h-4 accent-amber-400 rounded cursor-pointer"
                />
                <span className="font-bold text-white">🔇 Panic Voice Chat Mute Keybind</span>
              </label>
              <div className="flex items-center gap-1.5 text-xs font-code">
                <span className="text-slate-400">Key:</span>
                <input
                  type="text"
                  value={muteKey}
                  onChange={(e) => setMuteKey(e.target.value)}
                  title="Keyboard key to toggle voice mute (e.g. F8)"
                  className="w-12 px-2 py-0.5 rounded bg-slate-900 border border-amber-500/50 text-amber-300 text-center font-bold"
                />
              </div>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-2 bg-slate-950/80 border border-slate-800/90 rounded-lg p-2.5">
              <label 
                title="Single-key toggle to zoom CS2 radar between 0.40 (map overview) and 0.80 (close-up radar) - 100% Valve Safe"
                className="flex items-center gap-2 text-xs font-tech text-slate-200 cursor-pointer select-none"
              >
                <input
                  type="checkbox"
                  checked={radarZoomBind}
                  onChange={(e) => setRadarZoomBind(e.target.checked)}
                  className="w-4 h-4 accent-cyan-400 rounded cursor-pointer"
                />
                <span className="font-bold text-white">🔭 Radar Zoom In/Out Toggle Keybind</span>
              </label>
              <div className="flex items-center gap-1.5 text-xs font-code">
                <span className="text-slate-400">Key:</span>
                <input
                  type="text"
                  value={radarZoomKey}
                  onChange={(e) => setRadarZoomKey(e.target.value)}
                  title="Keyboard key for radar zoom toggle (e.g. v, c, mouse4)"
                  className="w-12 px-2 py-0.5 rounded bg-slate-900 border border-cyan-500/50 text-cyan-300 text-center font-bold"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
              <label 
                title="Sets rate 786432 and cl_net_buffer_ticks 0 for minimal interpolation buffer delay. Note: buffer ticks 0 may cause hitching on unstable connections; increase to 1 or 2 if experiencing stutter."
                className="flex items-center gap-2 text-xs font-tech text-slate-200 cursor-pointer select-none"
              >
                <input
                  type="checkbox"
                  checked={maxSubtickRates}
                  onChange={(e) => setMaxSubtickRates(e.target.checked)}
                  className="w-4 h-4 accent-cyan-400 rounded cursor-pointer"
                />
                <span>🌐 Network Rates & Buffer Ticks</span>
              </label>
              <label 
                title="Sets snd_headphone_eq 1 (unverified in-game preset) with 3D perspective correction and keeps game audio audible when alt-tabbed (snd_mute_losefocus 0). Profiles: 0=Natural, 1=Crisp, 2=Smooth."
                className="flex items-center gap-2 text-xs font-tech text-slate-200 cursor-pointer select-none"
              >
                <input
                  type="checkbox"
                  checked={crispAudioEq}
                  onChange={(e) => setCrispAudioEq(e.target.checked)}
                  className="w-4 h-4 accent-cyan-400 rounded cursor-pointer"
                />
                <span>🎧 Headphone Audio EQ & Background Sound (Preset 1, unverified)</span>
              </label>
              <label 
                title="Show built-in CS2 frametime, ping, and network jitter HUD only when latency spikes occur"
                className="flex items-center gap-2 text-xs font-tech text-slate-200 cursor-pointer select-none"
              >
                <input
                  type="checkbox"
                  checked={smartTelemetryHud}
                  onChange={(e) => setSmartTelemetryHud(e.target.checked)}
                  className="w-4 h-4 accent-cyan-400 rounded cursor-pointer"
                />
                <span>📊 Smart Telemetry HUD</span>
              </label>
              <label 
                title="Applies recommended radar & HUD scale settings (hud_scaling 0.90, uncentered radar, radar scale 0.40)"
                className="flex items-center gap-2 text-xs font-tech text-slate-200 cursor-pointer select-none"
              >
                <input
                  type="checkbox"
                  checked={radarHudScaling}
                  onChange={(e) => setRadarHudScaling(e.target.checked)}
                  className="w-4 h-4 accent-cyan-400 rounded cursor-pointer"
                />
                <span>🗺️ Radar & HUD Scale Defaults (0.40, uncentered)</span>
              </label>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-slate-800">
              <div>
                <label className="block text-[11px] font-code text-slate-400 mb-1">HUD COLOR THEME:</label>
                <div className="relative">
                  <select
                    value={hudColor}
                    onChange={(e) => setHudColor(e.target.value)}
                    title="Choose custom CS2 HUD color theme index (cl_hud_color 0-12)"
                    className="w-full pl-2.5 pr-10 py-2 rounded-lg bg-slate-950 border border-slate-700 text-xs font-mono text-cyan-300 truncate cursor-pointer focus:outline-none focus:border-cyan-500"
                  >
                    <option value="none">Default (No Change)</option>
                    <option value="0">0 (Default / Team)</option>
                    <option value="1">1 (White)</option>
                    <option value="2">2 (Bright White)</option>
                    <option value="3">3 (Light Blue)</option>
                    <option value="4">4 (Dark Blue)</option>
                    <option value="5">5 (Purple)</option>
                    <option value="6">6 (Red)</option>
                    <option value="7">7 (Orange)</option>
                    <option value="8">8 (Yellow)</option>
                    <option value="9">9 (Green)</option>
                    <option value="10">10 (Aqua / Cyan)</option>
                    <option value="11">11 (Pink)</option>
                    <option value="12">12 (Light Yellow)</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-[11px] font-code text-slate-400 mb-1">FPS CAP (fps_max):</label>
                <div className="relative">
                  <select
                    value={fpsMax}
                    onChange={(e) => setFpsMax(e.target.value)}
                    title="Set in-game maximum frame rate limiter (fps_max 0-999)"
                    className="w-full pl-2.5 pr-10 py-2 rounded-lg bg-slate-950 border border-slate-700 text-xs font-mono text-lime-300 truncate cursor-pointer focus:outline-none focus:border-lime-500"
                  >
                    <option value="0">0 — Uncapped (Max FPS)</option>
                    <option value="400">400 — Competitive (400)</option>
                    <option value="360">360 — 360Hz Match</option>
                    <option value="300">300 — Stable Cap (300)</option>
                    <option value="240">240 — 240Hz Match</option>
                    <option value="165">165 — 165Hz Match</option>
                    <option value="144">144 — 144Hz Match</option>
                    <option value="60">60 — Power Saver (60)</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Live Config Preview + Launch Options Helper (6 Cols) */}
          <div className="lg:col-span-6 flex flex-col justify-between bg-slate-950/95 border border-slate-800 rounded-xl p-4">
            <div>
              <div className="text-[11px] font-code text-amber-300/90 bg-amber-950/40 p-2.5 rounded-lg border border-amber-500/30 mb-3">
                ⚠️ <strong>Backup Note:</strong> Back up your CS2 user config folder (<code className="text-white">Steam/userdata/&lt;id&gt;/730/local/cfg</code>) and note your current values first before applying an autoexec. Custom binds ({duckKey}, {muteKey}, {radarZoomKey}) override actions currently assigned to those keys. Restart CS2 to clear memory-resident aliases.
              </div>
              <div className="flex items-center justify-between text-xs font-code text-slate-400 mb-2">
                <span className="flex items-center gap-1.5 text-lime-300 font-bold">
                  <Terminal className="w-4 h-4 text-lime-400" />
                  LIVE PREVIEW: autoexec.cfg
                </span>
                <span>UTF-8 // SOURCE 2 CFG</span>
              </div>

              <pre className="w-full h-72 overflow-y-auto rounded-lg bg-[#050811] border border-slate-800/90 p-3 text-[11px] font-code text-emerald-300 leading-relaxed select-all">
                {generatedCfg}
              </pre>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="text-[11px] font-code text-slate-400">
                <span className="text-cyan-300 font-bold flex items-center gap-1">
                  <Sparkles className="w-3 h-3" /> Recommended Launch Options:
                </span>
                <code className="text-amber-300">-novid -nojoy +fps_max {fpsMax} +exec autoexec.cfg</code>
              </div>
              <button
                onClick={handleCopyLaunch}
                title="Copy recommended Steam launch options flags to Windows clipboard"
                className="min-h-[40px] px-3.5 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-amber-300 border border-amber-500/40 text-xs font-code font-bold flex items-center gap-1.5 cursor-pointer self-start sm:self-auto transition-colors touch-manipulation"
              >
                {copiedLaunch ? <Check className="w-3.5 h-3.5 text-lime-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedLaunch ? 'Copied!' : 'Copy Launch Flags'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
