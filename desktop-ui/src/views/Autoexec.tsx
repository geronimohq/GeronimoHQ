import { useEffect, useMemo, useRef, useState } from 'react';
import { api } from '../api';
import { sfx } from '../sound';
import { useModal } from '../components/Modal';
import PAGES from '../data/pages.json';
import type { AutoexecState } from '../types';

const A = PAGES.autoexec;
const HUD = ['0 (Default / Team)', '1 (White)', '2 (Bright White)', '3 (Light Blue)', '4 (Dark Blue)', '5 (Purple)', '6 (Red)', '7 (Orange)', '8 (Yellow)', '9 (Green)', '10 (Aqua / Cyan)', '11 (Pink)', '12 (Light Yellow)'];

/** Colours one autoexec line: commands cyan, strings amber, numbers violet, comments grey. */
function Line({ t }: { t: string }) {
  if (/^\s*\/\//.test(t)) return <div className="cl c">{t || ' '}</div>;
  const parts = t.split(/("[^"]*"|\b-?\d+(?:\.\d+)?\b)/g);
  return <div className="cl">{parts.map((p, i) => {
    if (i === 0) { const m = p.match(/^(\s*)(\S+)(.*)$/); return m ? <span key={i}>{m[1]}<span className="k">{m[2]}</span>{m[3]}</span> : <span key={i}>{p}</span>; }
    if (p.startsWith('"')) return <span key={i} className="s">{p}</span>;
    if (/^-?\d/.test(p)) return <span key={i} className="n">{p}</span>;
    return <span key={i}>{p}</span>;
  })}</div>;
}

function Check({ on, set, title, desc }: { on: boolean; set: (v: boolean) => void; title: string; desc: string }) {
  return (
    <div className="row" style={{ padding: '8px 0' }}>
      <div className="grow"><div className="t" style={{ fontSize: 13 }}>{title}</div><div className="d" style={{ fontSize: 12 }}>{desc}</div></div>
      <button className="sw" role="switch" aria-checked={on} aria-label={title} onClick={() => { sfx.toggle(); set(!on); }} />
    </div>
  );
}

export default function Autoexec() {
  const [st, setSt] = useState<AutoexecState | null>(null);
  const [fps, setFps] = useState('0');
  const [vm, setVm] = useState(true), [tel, setTel] = useState(true), [hud, setHud] = useState(HUD[0]);
  const [duck, setDuck] = useState('F7'), [mute, setMute] = useState('F8');
  const [editing, setEditing] = useState(false), [draft, setDraft] = useState('');
  const [flash, setFlash] = useState('Read-only preview (click Edit config to modify)');
  const openModal = useModal();
  const edRef = useRef<HTMLDivElement>(null);
  const load = () => { void api.autoexecState().then((s) => { setSt(s); if (s.personal_vm) setVm(false); }); };
  useEffect(load, []);
  const lines = useMemo(() => (st?.text ?? '').split(/\r?\n/), [st]);

  const run = (title: string, fn: () => Promise<{ ok: boolean; error?: string }>) => async () => {
    const r = await fn();
    openModal(r.ok ? { kind: 'ok', label: 'Notification', title } : { kind: 'warn', label: 'Problem', title: 'Not done', body: r.error ?? 'See the log for details.' });
    load();
  };
  const confirm = (title: string, body: string, text: string, fn: () => Promise<void>) => { sfx.click(); openModal({ kind: 'q', label: 'Confirm', title, body, confirm: { text, run: fn } }); };

  const inject = async () => {
    const r = await api.zeCustomizer({ ze_laser_viewmodel: vm, clean_telemetry_hud: tel, hud_color: hud, duck_key: duck, voice_mute_key: mute });
    setFlash(`Updated at ${new Date().toLocaleTimeString()}: live preview shows the injected block at the bottom.`);
    load();
    setTimeout(() => { if (edRef.current) edRef.current.scrollTop = edRef.current.scrollHeight; }, 500);
    openModal(r.ok
      ? { kind: 'ok', label: 'Notification', title: 'ZE visual & audio binds added to autoexec.cfg',
          body: `Successfully injected into autoexec.cfg!\n\n${r.message}\n\n• Viewmodel low laser preset: ${vm ? 'ON (FOV 68, X:+2, Y:+2, Z:-2)' : 'OFF (your own viewmodel settings are kept)'}\n• HUD color: ${hud}\n• Boss audio ducking key: [${duck}] (22% <-> 100%)  |  Panic voice mute key: [${mute}]\n\nThe live autoexec.cfg preview below has updated and shows your new ZE block.` }
      : { kind: 'warn', label: 'ZE customizer notice', title: 'Not added', body: r.message });
  };
  const save = async () => {
    const r = await api.autoexecSave(draft);
    if (r.ok) { setEditing(false); setFlash(`Saved manually at ${new Date().toLocaleTimeString()} (backup created)`); load(); openModal({ kind: 'ok', label: 'Autoexec saved', title: 'Your edits were saved', body: `File: ${r.path}\n\nA safety backup was created as autoexec.cfg.manual_bak.` }); }
    else openModal({ kind: 'warn', label: 'Save error', title: 'Not saved', body: r.error });
  };

  return (
    <section className="view on">
      <div className="vhead"><div><div className="decal">// 04 · config</div><h1>CS2 in-game autoexec configuration</h1><p>Config directory: {st?.cfg_dir ?? (st ? 'Not found' : '...')}</p></div></div>

      {st && !st.cfg && <div className="glass card" role="alert" style={{ borderColor: 'rgba(255,158,27,.5)' }}><b>CS2 cfg folder not found.</b> The app works without it, but the autoexec tools are off. Install CS2 through Steam, or check that your Steam library is detected.</div>}
      {st?.cfg && st.state === 'missing' && <div className="glass card" style={{ borderColor: 'rgba(0,240,255,.4)' }}><b>No autoexec.cfg yet.</b> Apply engine autoexec tweaks creates one for you and keeps a backup of anything it replaces. {PAGES.autoexec.sub}</div>}
      <div className="glass card">
        <div className="sect" style={{ marginBottom: 6 }}>1. Engine autoexec tweaks</div>
        <div className="ptext" style={{ marginBottom: 6 }}>{A.sub}</div>
        <div className="mono" style={{ fontSize: 12, color: 'var(--cyan)', marginBottom: 10 }}>{st?.status ?? ''}</div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
          <button className="btn cut amber pri" disabled={!st?.cfg} title={A.apply_tip} onClick={() => confirm('Apply the low-latency autoexec block?', 'Adds or replaces the app\'s marked performance block in autoexec.cfg. Your other lines are kept, and a backup is made the first time.', 'Apply', run('Autoexec updated', api.autoexecInstall))}>Apply engine autoexec tweaks</button>
          <button className="btn cut ghost" disabled={!st?.cfg} title={A.revert_tip} onClick={() => confirm('Revert autoexec to the original?', 'Puts back autoexec_backup.cfg (your file from before the app\'s first change). Later edits are lost.', 'Revert', run('Autoexec restored', api.autoexecRestore))}>Revert autoexec to original</button>
          <span style={{ flex: 1 }} />
          <div className="field" style={{ margin: 0, flexDirection: 'row', alignItems: 'center', gap: 8 }}><label htmlFor="fps" style={{ margin: 0 }}>FPS limit</label><input id="fps" style={{ width: 80 }} value={fps} onChange={(e) => setFps(e.target.value.replace(/\D/g, ''))} /></div>
          <button className="btn cut ghost" disabled={!st?.cfg} onClick={() => void run('FPS limit saved', () => api.autoexecFps(Number(fps) || 0))()}>Set</button>
        </div>
        <div className="decal" style={{ marginTop: 10, textTransform: 'none', letterSpacing: 0 }}>{A.hint}</div>
      </div>

      <div className="glass card brk">
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}><span className="sect" style={{ color: 'var(--cyan)' }}>{A.ze_title}</span><span className="tag">CONSOLE SETTINGS ONLY</span></div>
        <div className="ptext" style={{ margin: '6px 0 8px' }}>{A.ze_desc}</div>
        {st?.personal_vm && <div className="glass card" style={{ borderColor: 'rgba(0,240,255,.4)', margin: '8px 0', padding: '10px 14px' }}><b>Personal config detected.</b> {A.personal.replace(/^[^A-Za-z]*PERSONAL CONFIG DETECTED:\s*/i, '')}</div>}
        <Check on={vm} set={setVm} title={st?.personal_vm ? 'Override with ZE laser viewmodel (FOV 68, Y:+2, Z:-2)' : 'ZE laser-jump low viewmodel (FOV 68, Y:+2, Z:-2)'} desc={A.vm_tip} />
        <Check on={tel} set={setTel} title="Smart frame-time & network jitter telemetry HUD" desc={A.telemetry_tip} />
        <div className="row" style={{ padding: '8px 0' }}><div className="grow"><div className="t" style={{ fontSize: 13 }}>HUD color</div><div className="d" style={{ fontSize: 12 }}>{A.hud_tip}</div></div>
          <select className="sel" style={{ minWidth: 190 }} value={hud} onChange={(e) => setHud(e.target.value)} aria-label="HUD color">{HUD.map((h) => <option key={h}>{h}</option>)}</select></div>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', margin: '8px 0' }}>
          <div className="field" style={{ margin: 0 }}><label htmlFor="dk">Boss / laser audio duck key (22% vs 100%)</label><input id="dk" value={duck} onChange={(e) => setDuck(e.target.value)} style={{ width: 150 }} /></div>
          <div className="field" style={{ margin: 0 }}><label htmlFor="mk">Panic voice mute key</label><input id="mk" value={mute} onChange={(e) => setMute(e.target.value)} style={{ width: 150 }} /></div>
        </div>
        <button className="btn cut amber pri" disabled={!st?.cfg} title={A.inject_tip} onClick={() => void inject()}>Inject ZE visual &amp; audio binds</button>
      </div>

      <div className="glass card">
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center', marginBottom: 8 }}>
          <span className="sect">autoexec.cfg</span><span className="decal" style={{ textTransform: 'none', letterSpacing: 0 }}>{editing ? 'Editing active: modify your cfg and click Save changes' : flash}</span>
          <span style={{ flex: 1 }} />
          <button className="btn cut ghost sm" title={A.edit_tip} onClick={() => { sfx.click(); if (!editing) setDraft(st?.text ?? ''); setEditing(!editing); }}>{editing ? 'Cancel edit' : 'Edit config'}</button>
          {editing && <button className="btn cut ghost sm" title={A.save_tip} onClick={() => void save()}>Save changes</button>}
          <button className="btn cut ghost sm" onClick={() => { sfx.click(); load(); }}>Reload</button>
        </div>
        {editing
          ? <textarea className="editor edit" value={draft} onChange={(e) => setDraft(e.target.value)} spellCheck={false} aria-label="autoexec.cfg editor" />
          : <div className="editor" ref={edRef}>{st?.text ? lines.map((l, i) => <div key={i} className="ln"><span className="no">{i + 1}</span><Line t={l} /></div>) : <div className="decal" style={{ padding: 10 }}>{st ? 'No autoexec.cfg to show.' : '...'}</div>}</div>}
      </div>
    </section>
  );
}
