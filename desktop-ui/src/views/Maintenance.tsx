import { useEffect, useState } from 'react';
import { RefreshCw, ShieldAlert } from 'lucide-react';
import { api } from '../api';
import { sfx } from '../sound';
import { useModal } from '../components/Modal';
import type { MaintState } from '../types';

const CLEAN = [
  { key: 'temp', title: 'Purge Windows temp files', desc: '%TEMP% and Windows\\Temp.' },
  { key: 'win_update', title: 'Purge Windows Update cache', desc: 'SoftwareDistribution download cache.' },
  { key: 'discord_steam', title: 'Purge Discord & Steam web cache', desc: 'Never logs you out.' },
  { key: 'thumb', title: 'Purge Explorer thumbnail cache', desc: 'thumbcache_*.db files.' },
  { key: 'recycle', title: 'Empty the Recycle Bin', desc: 'Permanently removes deleted files.' },
  { key: 'dns', title: 'Flush Windows DNS cache', desc: 'Refreshes server lookups.' },
] as const;
const TOOLS = [
  { key: 'cleanmgr', label: 'Disk Cleanup', admin: false },
  { key: 'startup', label: 'Startup apps manager', admin: false },
  { key: 'trim', label: 'SSD TRIM (defrag /O)', admin: true },
  { key: 'sfc', label: 'System File Checker (SFC)', admin: true },
  { key: 'dism', label: 'DISM health restore', admin: true },
  { key: 'winsxs', label: 'DISM WinSxS cleanup', admin: true },
] as const;

export default function Maintenance({ busy, setBusy }: { busy: boolean; setBusy: (b: boolean) => void }) {
  const [st, setSt] = useState<MaintState | null>(null);
  const [sel, setSel] = useState<Record<string, boolean>>({ temp: true, win_update: true, discord_steam: true, thumb: true, recycle: false, dns: true });
  const openModal = useModal();
  const load = () => { void api.maintState().then(setSt); };
  useEffect(load, []);

  const run = () => {
    const chosen = CLEAN.filter((c) => sel[c.key]);
    if (!chosen.length) { openModal({ kind: 'warn', label: 'Nothing selected', title: 'Pick at least one clean-up' }); return; }
    openModal({
      kind: 'q', label: 'Confirm', title: 'Run the selected clean-up?',
      body: `This will:\n${chosen.map((c) => `- ${c.title}`).join('\n')}\n\nDeleted files cannot be restored.`,
      confirm: { text: 'Run clean-up', run: async () => { setBusy(true); const r = await api.maintRun(sel); if (!r.ok) { setBusy(false); openModal({ kind: 'warn', label: 'Problem', title: 'Not started', body: r.error }); } } },
    });
  };
  const tool = async (key: string, label: string, admin: boolean) => {
    if (admin && st && !st.admin) { openModal({ kind: 'warn', label: 'Administrator needed', title: label, body: 'This repair tool needs Administrator. Use Relaunch as Administrator above.' }); return; }
    sfx.click();
    const r = await api.maintTool(key);
    if (!r.ok) openModal({ kind: 'warn', label: 'Problem', title: label, body: r.error });
  };

  return (
    <section className="view on">
      <div className="vhead"><div><div className="decal">// 08 · housekeeping</div><h1>Safe system &amp; storage maintenance</h1><p>Free up storage, clear cache bloat, inspect drive health and flush DNS.</p></div>
        <button className="btn cut ghost sm" onClick={() => { sfx.click(); load(); }}><RefreshCw size={13} /> Refresh</button></div>

      {st && !st.admin && (
        <div className="glass card" style={{ display: 'flex', gap: 14, alignItems: 'center', flexWrap: 'wrap' }}>
          <ShieldAlert size={20} color="var(--cyan)" />
          <div style={{ flex: 1, minWidth: 220 }}><div className="t">Standard user mode</div><div className="d" style={{ color: 'var(--tx2)' }}>Disk clean-ups work without Administrator. Deep repairs (SSD TRIM, SFC, DISM) need it.</div></div>
          <button className="btn cut ghost sm" onClick={() => { sfx.click(); void api.relaunchAdmin(); }}>Relaunch as Administrator</button>
        </div>
      )}

      <div className="glass card">
        <div className="sect" style={{ marginBottom: 8 }}>Storage capacity &amp; health</div>
        {st?.drives.map((d) => {
          const free = (d.free_gb / d.total_gb) * 100, tone = d.is_critical ? 'var(--bad)' : free < 25 ? 'var(--amber)' : 'var(--ok)';
          return (
            <div className="row" key={d.drive}>
              <div className="mono" style={{ width: 36, fontWeight: 700 }}>{d.drive}</div>
              <div className="grow"><div className="bar" style={{ margin: 0 }}><i style={{ width: `${d.used_pct}%`, background: tone }} /></div></div>
              <div className="mono" style={{ fontSize: 12, color: tone, minWidth: 190, textAlign: 'right' }}>{d.free_gb.toFixed(1)} GB free of {d.total_gb.toFixed(0)} GB</div>
            </div>
          );
        })}
        {st?.drives.some((d) => d.is_critical) && <div className="decal" style={{ color: 'var(--bad)', marginTop: 8 }}>Drives above 85% full can cause stutter: SSD write cache performance drops.</div>}
      </div>

      <div className="glass card">
        <div className="sect" style={{ marginBottom: 4 }}>Safe disk &amp; cache clean-up</div>
        {CLEAN.map((c) => (
          <div className="row" key={c.key}>
            <div className="grow"><div className="t">{c.title}</div><div className="d">{c.desc}</div></div>
            <button className="sw" role="switch" aria-checked={sel[c.key]} aria-label={c.title} onClick={() => { sfx.toggle(); setSel({ ...sel, [c.key]: !sel[c.key] }); }} />
          </div>
        ))}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 10 }}>
          <button className="btn cut amber pri" disabled={busy} onClick={run}>{busy ? 'Working…' : 'Run selected PC clean-up'}</button>
        </div>
      </div>

      <div className="glass card">
        <div className="sect" style={{ marginBottom: 10 }}>Windows system tools &amp; diagnostics</div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {TOOLS.map((t) => <button key={t.key} className="btn cut ghost sm" onClick={() => void tool(t.key, t.label, t.admin)}>{t.label}{t.admin ? ' · admin' : ''}</button>)}
        </div>
      </div>
    </section>
  );
}
