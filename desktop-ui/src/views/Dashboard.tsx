import { useEffect, useState } from 'react';
import { FolderOpen } from 'lucide-react';
import { api } from '../api';
import { sfx } from '../sound';
import type { DashboardData } from '../types';

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return <div className="glass card brk dcard"><div className="sect" style={{ marginBottom: 10 }}>{title}</div>{children}</div>;
}
const ago = (d: number | null | undefined) => (d == null ? 'Never' : d === 0 ? 'Today' : `${d}d ago`);

export default function Dashboard({ go }: { go: (id: 'servers' | 'maintenance' | 'engine') => void }) {
  const [d, setD] = useState<DashboardData | null>(null);
  const [tot, setTot] = useState<{ humans?: number; online?: number; total?: number; bots?: number }>({});
  useEffect(() => { void api.dashboard().then(setD); void api.totals().then(setTot); }, []);
  const dr = d?.drive;
  const free = dr ? (dr.free_gb / dr.total_gb) * 100 : 0;
  const tone = !dr ? 'var(--tx3)' : free < 10 || dr.is_critical ? 'var(--bad)' : free < 25 ? 'var(--amber)' : 'var(--ok)';

  return (
    <section className="view on">
      <div className="vhead"><div><div className="decal">// 01 · overview</div><h1>System readiness</h1><p>CS2 install, autoexec status, drive space and live ZE server counts.</p></div></div>
      <div className="dgrid">
        <Card title="CS2 environment">
          <div className="t" style={{ fontSize: 14 }}>{d?.cs2_dir ? 'CS2 found' : d ? 'CS2 not found' : '…'}</div>
          {d?.cs2_dir && <div className="decal" style={{ margin: '4px 0 8px', wordBreak: 'break-all' }}>{d.cs2_dir}</div>}
          <div style={{ color: 'var(--cyan)', marginBottom: 12 }}>{d?.autoexec?.text ?? ''}</div>
          <button className="btn cut ghost sm" disabled={!d?.cfg_dir} onClick={() => { sfx.click(); void api.openPath('cfg'); }}><FolderOpen size={13} /> Open cfg folder</button>
        </Card>
        <Card title="Storage: CS2 / Steam library drive">
          {dr ? <>
            <div className="t" style={{ fontSize: 14 }}>Drive {dr.drive} · {dr.free_gb.toFixed(1)} GB free of {dr.total_gb.toFixed(1)} GB</div>
            <div className="bar" style={{ margin: '10px 0 6px' }}><i style={{ width: `${dr.used_pct}%`, background: tone }} /></div>
            <div className="mono" style={{ color: tone, fontSize: 12 }}>{free < 10 || dr.is_critical ? 'Low space: free some storage' : `${free.toFixed(0)}% free`}</div>
          </> : <div className="decal">{d ? 'Space unmonitored (CS2 not found)' : '…'}</div>}
        </Card>
        <Card title="ZE game servers">
          <div className="t" style={{ fontSize: 14 }}>{tot.humans ?? '…'} players in-game</div>
          <div style={{ color: 'var(--cyan)', margin: '4px 0 12px' }}>{tot.online ?? '…'} / {tot.total ?? '…'} servers online</div>
          <div className="decal" style={{ marginBottom: 10 }}>Humans only (bots not counted), same numbers as geronimohq.com.</div>
          <button className="btn cut ghost sm" onClick={() => { sfx.click(); go('servers'); }}>Launch ZE browser</button>
        </Card>
        <Card title="Maintenance">
          <div>CS2 engine tweaks: optimized <b>{ago(d?.days_opt)}</b></div>
          <div>PC maintenance: clean <b>{ago(d?.days_maint)}</b></div>
          <div className="decal" style={{ margin: '6px 0 12px' }}>Recommended every 7 days.</div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <button className="btn cut ghost sm" onClick={() => { sfx.click(); go('engine'); }}>Engine tweaks</button>
            <button className="btn cut ghost sm" onClick={() => { sfx.click(); go('maintenance'); }}>PC maintenance</button>
          </div>
        </Card>
      </div>
    </section>
  );
}
