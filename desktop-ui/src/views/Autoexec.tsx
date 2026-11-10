import { useEffect, useMemo, useState } from 'react';
import { api } from '../api';
import { sfx } from '../sound';
import { useModal } from '../components/Modal';
import type { AutoexecState } from '../types';

/** Colours one autoexec line: commands cyan, strings amber, numbers violet, comments grey. */
function Line({ t }: { t: string }) {
  if (/^\s*\/\//.test(t)) return <div className="cl c">{t || ' '}</div>;
  const parts = t.split(/(\"[^\"]*\"|\b-?\d+(?:\.\d+)?\b)/g);
  return <div className="cl">{parts.map((p, i) => {
    if (i === 0) { const m = p.match(/^(\s*)(\S+)(.*)$/); return m ? <span key={i}>{m[1]}<span className="k">{m[2]}</span>{m[3]}</span> : <span key={i}>{p}</span>; }
    if (p.startsWith('"')) return <span key={i} className="s">{p}</span>;
    if (/^-?\d/.test(p)) return <span key={i} className="n">{p}</span>;
    return <span key={i}>{p}</span>;
  })}</div>;
}

export default function Autoexec() {
  const [st, setSt] = useState<AutoexecState | null>(null);
  const [fps, setFps] = useState('0');
  const openModal = useModal();
  const load = () => { void api.autoexecState().then(setSt); };
  useEffect(load, []);
  const lines = useMemo(() => (st?.text ?? '').split(/\r?\n/), [st]);

  const run = (title: string, fn: () => Promise<{ ok: boolean; error?: string }>) => async () => {
    const r = await fn();
    openModal(r.ok ? { kind: 'ok', label: 'Notification', title } : { kind: 'warn', label: 'Problem', title: 'Not done', body: r.error ?? 'See the log for details.' });
    load();
  };
  const confirm = (title: string, body: string, text: string, fn: () => Promise<void>) => { sfx.click(); openModal({ kind: 'q', label: 'Confirm', title, body, confirm: { text, run: fn } }); };

  return (
    <section className="view on">
      <div className="vhead"><div><div className="decal">// 04 · config</div><h1>Autoexec &amp; binds</h1><p>{st?.status ?? '...'}</p></div></div>
      <div className="glass card">
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
          <button className="btn cut amber pri" disabled={!st?.cfg} onClick={() => confirm('Apply the low-latency autoexec block?', 'Adds the app\'s performance block to autoexec.cfg. Your own binds and settings are kept, and a backup is made first.', 'Apply', run('Autoexec updated', api.autoexecInstall))}>Apply engine autoexec tweaks</button>
          <button className="btn cut ghost" disabled={!st?.cfg} onClick={() => confirm('Restore the autoexec backup?', 'Puts back autoexec_backup.cfg (your file from before the app\'s first change). Later edits are lost.', 'Restore', run('Autoexec restored', api.autoexecRestore))}>Revert backup</button>
          <button className="btn cut ghost" onClick={() => { sfx.click(); load(); }}>Reload</button>
          <span style={{ flex: 1 }} />
          <div className="field" style={{ margin: 0, flexDirection: 'row', alignItems: 'center', gap: 8 }}><label htmlFor="fps" style={{ margin: 0 }}>FPS limit</label><input id="fps" style={{ width: 80 }} value={fps} onChange={(e) => setFps(e.target.value.replace(/\D/g, ''))} /></div>
          <button className="btn cut ghost" disabled={!st?.cfg} onClick={() => void run('FPS limit saved', () => api.autoexecFps(Number(fps) || 0))()}>Set</button>
        </div>
      </div>
      <div className="glass card">
        <div className="sect" style={{ marginBottom: 8 }}>Live autoexec.cfg preview</div>
        <div className="editor">{st?.text ? lines.map((l, i) => <div key={i} className="ln"><span className="no">{i + 1}</span><Line t={l} /></div>) : <div className="decal">{st ? 'No autoexec.cfg to show.' : '...'}</div>}</div>
      </div>
    </section>
  );
}
