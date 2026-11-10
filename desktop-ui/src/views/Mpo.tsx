import { useEffect, useState } from 'react';
import { RefreshCw } from 'lucide-react';
import { api } from '../api';
import { sfx } from '../sound';
import { Info } from '../components/Info';
import { useModal } from '../components/Modal';
import PAGES from '../data/pages.json';
import type { MpoState } from '../types';

const M = PAGES.mpo;
const REG = 'HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers';
const COPIES: [string, string, string][] = [
  ['Copy registry path', REG, 'GraphicsDrivers registry path'],
  ['Copy disable MPO command', 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" /v "DisableOverlays" /t REG_DWORD /d 1 /f', 'Disable MPO registry command'],
  ['Copy restore MPO default command', 'reg delete "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" /v "DisableOverlays" /f', 'Restore MPO default registry command'],
  ['Copy DDU website link', 'https://www.wagnardsoft.com/', 'Official DDU website link'],
];

export default function Mpo() {
  const [m, setM] = useState<MpoState | null>(null);
  const openModal = useModal();
  const load = () => { void api.mpo().then(setM); };
  useEffect(load, []);
  const copy = (text: string, what: string) => {
    sfx.toggle();
    try { void navigator.clipboard.writeText(text); } catch { /* ignore */ }
    openModal({ kind: 'ok', label: 'Copied', title: `${what} copied`, body: text });
  };
  return (
    <section className="view on">
      <div className="vhead"><div><div className="decal">// 03 · display</div><h1>GPU multi-plane overlay (MPO) diagnostics &amp; troubleshooter</h1>
        <p>Dedicated MPO troubleshooter covering AMD Radeon, NVIDIA GeForce and Intel graphics. Inspects your active GPU and the live registry state.</p></div>
        <button className="btn cut ghost sm" onClick={() => { sfx.click(); load(); }}><RefreshCw size={13} /> Refresh live status</button></div>

      <Info title={M.why_title} badge={M.why_badge} text={M.why} open={false} tone="var(--cyan)" />

      <div className="glass card brk">
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: 240 }}><div className="sect">Windows multi-plane overlay (MPO) diagnostic</div><div className="decal" style={{ marginTop: 4 }}>Detected GPU</div><div className="t" style={{ fontSize: 18 }}>{m?.gpu ?? '...'}</div></div>
          {m && <span className="pill" style={{ color: m.disabled ? 'var(--cyan)' : 'var(--ok)' }}><i className={`dot ${m.disabled ? 'cy' : ''}`} />{m.badge}</span>}
        </div>
        <div className="decal" style={{ marginTop: 12 }}>Current PC configuration</div>
        <div className="t">{m ? (m.disabled ? 'MODIFIED / CUSTOM: MPO is DISABLED (registry override active: DisableOverlays = 1)' : 'WINDOWS DEFAULT: MPO is ENABLED (standard Windows hardware multi-plane composition)') : '...'}</div>
        <div className="decal" style={{ marginTop: 10 }}>Live system / registry inspection (read only)</div>
        <pre className="code">{m ? `Registry Key: ${m.detail}` : '...'}</pre>
      </div>

      <Info title="System behavior & optional considerations" text={M.considerations} tone="var(--cyan)" />
      <Info title="Technical details & impact" text={M.technical} tone="var(--cyan)" open={false} />
      <Info title="Trade-offs & stability considerations" text={M.tradeoffs} tone="var(--cyan)" open={false} />
      <Info title="Summary & options (optional)" text={M.summary} tone="var(--ok)" />
      <Info title="How to do it yourself (manual steps)" text={M.diy}>
        <div className="decal" style={{ margin: '12px 0 8px' }}>The app only reads this setting. These buttons copy text to your clipboard; nothing is changed for you.</div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {COPIES.map(([label, text, what]) => <button key={label} className="btn cut ghost sm" title={`Copies ${what} to the Windows clipboard.`} onClick={() => copy(text, what)}>{label}</button>)}
        </div>
      </Info>
    </section>
  );
}
