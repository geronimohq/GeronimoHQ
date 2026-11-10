import { useEffect, useState } from 'react';
import { api } from '../api';
import { sfx } from '../sound';
import { useModal } from '../components/Modal';
import PAGES from '../data/pages.json';
import type { LaunchState } from '../types';

const L = PAGES.launch;
const BASELINE = '-novid -nojoy +fps_max 0';

export default function Launch() {
  const [st, setSt] = useState<LaunchState | null>(null);
  const [val, setVal] = useState('');
  const [err, setErr] = useState('');
  const openModal = useModal();
  useEffect(() => {
    void api.launchState().then((s) => { setSt(s); setVal(s.current || ''); }).catch((e) => setErr(String(e)));
  }, []);

  const copy = () => {
    sfx.toggle();
    try { void navigator.clipboard.writeText(val); } catch { /* ignore */ }
    openModal({ kind: 'ok', label: 'Copied', title: 'Launch options copied', body: 'Paste them in Steam: Library, right-click CS2, Properties, Launch Options.' });
  };
  const apply = () => {
    const v = val.trim();
    if (st && v === st.current.trim()) { openModal({ kind: 'ok', label: 'Already active', title: 'Matches your Steam configuration', body: v || '(empty)' }); return; }
    openModal({
      kind: 'q', label: 'Confirm', title: 'Update Steam launch options?',
      body: 'Make sure Steam is completely closed first, otherwise Steam may overwrite the change when it closes.\n\nThe original is kept as localconfig.vdf.backup.',
      confirm: { text: 'Apply to Steam', run: async () => {
        const r = await api.launchSave(v);
        openModal(r.ok ? { kind: 'ok', label: 'Saved', title: 'Steam launch options updated' } : { kind: 'warn', label: 'Problem', title: 'Not saved', body: r.error ?? 'See the log for details.' });
        void api.launchState().then(setSt);
      } },
    });
  };
  const bad = (st?.warnings.length ?? 0) > 0;

  return (
    <section className="view on">
      <div className="vhead"><div><div className="decal">// 05 · steam</div><h1>Steam launch options helper</h1><p>{L.sub}</p></div></div>
      {err && <div className="glass card" role="alert" style={{ borderColor: 'rgba(239,68,68,.5)' }}>Could not read your Steam launch options: {err}</div>}
      <div className="glass card">
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, flexWrap: 'wrap' }}>
          <span className="sect">Your current active launch options in Steam</span>
          <span className="pill"><i className={`dot ${bad ? 'am' : ''}`} />{!st ? '...' : !st.vdf_found ? 'Steam config not found' : bad ? 'Obsolete flags detected' : 'Clean configuration'}</span>
        </div>
        <pre className="code">{st ? (st.current || '(None currently set)') : '...'}</pre>
        {st?.warnings.map((w) => <div key={w} className="warnline">&#9888; {w}</div>)}
      </div>
      <div className="glass card">
        <div className="sect" style={{ marginBottom: 6, color: 'var(--cyan)' }}>Recommended competitive baseline preset (reference)</div>
        <pre className="code">{BASELINE}</pre>
        <div className="ptext">{L.baseline_help}</div>
      </div>
      <div className="glass card">
        <div className="sect" style={{ marginBottom: 8 }}>Edit / apply launch options to Steam</div>
        <div className="field"><label htmlFor="lo">Launch options</label><input id="lo" value={val} onChange={(e) => setVal(e.target.value)} spellCheck={false} /></div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 14 }}>
          <button className="btn cut amber pri" title={L.copy_tip} onClick={copy}>Copy options</button>
          <button className="btn cut ghost" title={L.apply_tip} onClick={() => { sfx.click(); apply(); }}>Apply directly to Steam</button>
          <button className="btn cut ghost" title={L.load_tip} onClick={() => { sfx.click(); setVal(BASELINE); }}>Load baseline preset</button>
          <button className="btn cut ghost" title={L.reset_tip} onClick={() => { sfx.click(); setVal(st?.current ?? ''); }}>Keep / reset to current</button>
        </div>
      </div>
    </section>
  );
}
