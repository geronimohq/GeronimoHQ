import { useEffect, useState } from 'react';
import { RefreshCw } from 'lucide-react';
import { api } from '../api';
import { sfx } from '../sound';
import type { MpoState } from '../types';

export default function Mpo() {
  const [m, setM] = useState<MpoState | null>(null);
  const load = () => { void api.mpo().then(setM); };
  useEffect(load, []);
  return (
    <section className="view on">
      <div className="vhead"><div><div className="decal">// 03 · display</div><h1>GPU MPO diagnostics</h1><p>Multi-Plane Overlay troubleshooter for AMD Radeon, NVIDIA GeForce and Intel graphics.</p></div>
        <button className="btn cut ghost sm" onClick={() => { sfx.click(); load(); }}><RefreshCw size={13} /> Refresh live status</button></div>
      <div className="glass card brk">
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: 220 }}><div className="decal">Detected GPU</div><div className="t" style={{ fontSize: 18 }}>{m?.gpu ?? '...'}</div></div>
          {m && <span className="pill" style={{ color: m.disabled ? 'var(--cyan)' : 'var(--amber)' }}><i className={`dot ${m.disabled ? 'cy' : 'am'}`} />{m.badge}</span>}
        </div>
        <div className="decal" style={{ marginTop: 12 }}>Live registry inspection (read only)</div>
        <pre className="code">{m ? `${m.detail}\n${m.reg_path}` : '...'}</pre>
      </div>
      <div className="glass card">
        <div className="sect" style={{ marginBottom: 8 }}>What this is</div>
        <p className="d" style={{ margin: '0 0 10px', color: 'var(--tx2)' }}>MPO lets Windows composite several screen layers in hardware. On some AMD, NVIDIA and Intel driver combinations it causes black flickers, Alt-Tab freezes or stutter in games. Turning it off (the DisableOverlays value) can remove those symptoms. The trade-off is slightly higher compositor work on some systems.</p>
        <p className="d" style={{ margin: 0, color: 'var(--tx2)' }}>This screen only reads your current state. Changing it is a Windows registry edit that needs Administrator and a restart, so the app does not do it for you. The Help &amp; FAQ entries on MPO explain the manual steps and how to undo them.</p>
      </div>
    </section>
  );
}
