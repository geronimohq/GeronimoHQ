import React, { useState, useMemo } from 'react';
import { Sliders, Download, Copy, Check, Terminal, ShieldCheck, Volume2, Eye, Sparkles } from 'lucide-react';

export const CS2AutoexecGeneratorSection: React.FC = () => {
  const [zeLowViewmodel, setZeLowViewmodel] = useState(true);
  const [disableTracers, setDisableTracers] = useState(true);
  const [bossDuckBind, setBossDuckBind] = useState(true);
  const [duckKey, setDuckKey] = useState('F7');
  const [voiceMuteBind, setVoiceMuteBind] = useState(true);
  const [muteKey, setMuteKey] = useState('F8');
  const [jumpthrowBind, setJumpthrowBind] = useState(true);
  const [jumpthrowKey, setJumpthrowKey] = useState('v');
  const [nullMovement, setNullMovement] = useState(false);
  const [maxSubtickRates, setMaxSubtickRates] = useState(true);
  const [crispAudioEq, setCrispAudioEq] = useState(true);
  const [smartTelemetryHud, setSmartTelemetryHud] = useState(true);
  const [hudColor, setHudColor] = useState('11');
  const [fpsMax, setFpsMax] = useState('0');
  const [copiedCfg, setCopiedCfg] = useState(false);
  const [copiedLaunch, setCopiedLaunch] = useState(false);
  const [copiedPath, setCopiedPath] = useState(false);

  const generatedCfg = useMemo(() => {
    const sanitizedFps = Math.max(0, Math.min(999, parseInt(fpsMax || '0', 10) || 0));
    const lines: string[] = [
      '// ============================================================================',
      '// GERONIMOHQ.COM // CS2 & ZOMBIE ESCAPE PRO AUTOEXEC.CFG',
      '// 100% VAC-Safe Engine CVars • Place in: steamapps/common/Counter-Strike Global Offensive/game/csgo/cfg/',
      '// ============================================================================',
      '',
      `fps_max "${sanitizedFps}"`,
      `cl_hud_color "${hudColor}"`,
      'hud_scaling "0.90"',
      'cl_radar_always_centered "0"',
      'cl_radar_scale "0.40"',
      '',
    ];

    if (maxSubtickRates) {
      lines.push(
        '// --- CS2 SUB-TICK & 64-PLAYER ZE NETWORK RATES (CS2 ENGINE VERIFIED) ---',
        'rate "786432"',
        'cl_net_buffer_ticks "0"',
        ''
      );
    }

    if (zeLowViewmodel) {
      lines.push(
        '// --- ZE LASER-JUMP LOW VIEWMODEL (MAXIMUM BOTTOM-SCREEN VISIBILITY) ---',
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
        `bind "${m}" "voice_modenable_toggle"`,
        ''
      );
    }

    if (jumpthrowBind) {
      const jk = (jumpthrowKey || 'v').trim();
      lines.push(
        '// --- SUB-TICK CONSISTENT JUMPTHROW ALIAS ---',
        'alias "+ze_jt" "+jump"',
        'alias "+ze_ta" "-attack; -attack2"',
        'alias "-ze_jt" "-jump"',
        `bind "${jk}" "+ze_jt; +ze_ta"`,
        ''
      );
    }

    if (nullMovement) {
      lines.push(
        '// --- NULL-CANCELLING STRAFE MOVEMENT BINDS (A / D) ---',
        'alias "+ze_left" "+left; -right"',
        'alias "-ze_left" "-left"',
        'alias "+ze_right" "+right; -left"',
        'alias "-ze_right" "-right"',
        'bind "a" "+ze_left"',
        'bind "d" "+ze_right"',
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

    lines.push('host_writeconfig', 'echo "[GeronimoHQ] CS2 & ZE Autoexec Loaded Successfully!"');
    return lines.join('\n');
  }, [
    zeLowViewmodel,
    disableTracers,
    bossDuckBind,
    duckKey,
    voiceMuteBind,
    muteKey,
    jumpthrowBind,
    jumpthrowKey,
    nullMovement,
    maxSubtickRates,
    crispAudioEq,
    smartTelemetryHud,
    hudColor,
    fpsMax,
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
                title="Toggle boss audio ducking between 22% (ducked) and 85% (normal) during loud ZE boss lasers"
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
                title="Panic voice chat mute keybind (voice_modenable_toggle)"
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
                title="Sub-tick jumpthrow alias bind ensuring 100% consistent grenade trajectory"
                className="flex items-center gap-2 text-xs font-tech text-slate-200 cursor-pointer select-none"
              >
                <input
                  type="checkbox"
                  checked={jumpthrowBind}
                  onChange={(e) => setJumpthrowBind(e.target.checked)}
                  className="w-4 h-4 accent-lime-400 rounded cursor-pointer"
                />
                <span className="font-bold text-white">🎯 Sub-Tick Jumpthrow Alias Keybind</span>
              </label>
              <div className="flex items-center gap-1.5 text-xs font-code">
                <span className="text-slate-400">Key:</span>
                <input
                  type="text"
                  value={jumpthrowKey}
                  onChange={(e) => setJumpthrowKey(e.target.value)}
                  title="Keyboard key for jumpthrow bind (e.g. v, mouse5)"
                  className="w-12 px-2 py-0.5 rounded bg-slate-900 border border-lime-500/50 text-lime-300 text-center font-bold"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
              <label 
                title="Null-cancelling strafe binds (A/D) ensuring opposite strafe key immediately cancels prior input (Allowed on community servers)"
                className="flex items-center gap-2 text-xs font-tech text-slate-200 cursor-pointer select-none"
              >
                <input
                  type="checkbox"
                  checked={nullMovement}
                  onChange={(e) => setNullMovement(e.target.checked)}
                  className="w-4 h-4 accent-cyan-400 rounded cursor-pointer"
                />
                <span>⚡ Null-Movement Binds (A/D)</span>
              </label>
              <label 
                title="Maximize CS2 network packet rates (rate 786432, cl_net_buffer_ticks 0) for zero input delay"
                className="flex items-center gap-2 text-xs font-tech text-slate-200 cursor-pointer select-none"
              >
                <input
                  type="checkbox"
                  checked={maxSubtickRates}
                  onChange={(e) => setMaxSubtickRates(e.target.checked)}
                  className="w-4 h-4 accent-cyan-400 rounded cursor-pointer"
                />
                <span>🌐 Max Sub-Tick Network Rates</span>
              </label>
              <label 
                title="Spatial headphone audio EQ (snd_headphone_eq 1) and perspective correction for precise footstep sound"
                className="flex items-center gap-2 text-xs font-tech text-slate-200 cursor-pointer select-none"
              >
                <input
                  type="checkbox"
                  checked={crispAudioEq}
                  onChange={(e) => setCrispAudioEq(e.target.checked)}
                  className="w-4 h-4 accent-cyan-400 rounded cursor-pointer"
                />
                <span>🎧 Crisp Footstep Audio EQ</span>
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
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-slate-800">
              <div>
                <label className="block text-[11px] font-code text-slate-400 mb-1">HUD COLOR THEME:</label>
                <select
                  value={hudColor}
                  onChange={(e) => setHudColor(e.target.value)}
                  title="Choose custom CS2 HUD color theme index (cl_hud_color 0-12)"
                  className="w-full px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs font-code text-cyan-300"
                >
                  <option value="11">11 — Light Blue (Pro Default)</option>
                  <option value="9">9 — Aqua Cyan</option>
                  <option value="5">5 — Neon Purple</option>
                  <option value="8">8 — Safe Emerald Green</option>
                  <option value="6">6 — Crimson Red</option>
                  <option value="4">4 — Bright Banana Yellow</option>
                </select>
              </div>
              <div>
                <label className="block text-[11px] font-code text-slate-400 mb-1">FPS CAP (fps_max):</label>
                <select
                  value={fpsMax}
                  onChange={(e) => setFpsMax(e.target.value)}
                  title="Set in-game maximum frame rate limiter (fps_max 0-999)"
                  className="w-full px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs font-code text-lime-300"
                >
                  <option value="0">0 — Uncapped (Max Framerate)</option>
                  <option value="240">240 FPS (240Hz Monitor)</option>
                  <option value="360">360 FPS (360Hz Monitor)</option>
                  <option value="400">400 FPS (Consistent Frame Pacing)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Right Column: Live Config Preview + Launch Options Helper (6 Cols) */}
          <div className="lg:col-span-6 flex flex-col justify-between bg-slate-950/95 border border-slate-800 rounded-xl p-4">
            <div>
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
