import { useEffect, useState } from 'react';
import { FolderOpen } from 'lucide-react';
import { api } from '../api';
import { sfx } from '../sound';
import PAGES from '../data/pages.json';
import type { DashboardData } from '../types';

const D = PAGES.dashboard;
function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return <div className="glass card brk dcard"><div className="sect" style={{ marginBottom: 10 }}>{title}</div>{children}</div>;
}
const ago = (d: number | null | undefined) => (d == null || d >= 999 ? 'Never' : d === 0 ? 'Today' : `${d}d ago`);

export default function Dashboard({ go }: { go: (id: 'servers' | 'maintenance' | 'engine') => void }) {
  const [d, setD] = useState<DashboardData | null>(null);
  const [tot, setTot] = useState<{ humans?: number; online?: number; total?: number; bots?: number }>({});
  useEffect(() => { void api.dashboard().then(setD); void api.totals().then(setTot); }, []);
  const dr = d?.drive;
  const free = dr ? (dr.free_gb / dr.total_gb) * 100 : 0;
  const low = !!dr && (free < 10 || dr.is_critical);
  const tone = !dr ? 'var(--tx3)' : low ? 'var(--bad)' : free < 25 ? 'var(--amber)' : 'var(--ok)';

  return (
    <section className="view on">
      <div className="vhead"><div><div className="decal">// 01 · overview</div><h1>System readiness &amp; cyberdeck dashboard</h1><p>CS2 install, autoexec status, drive space and live ZE server counts.</p></div></div>

      <div className="glass card brk">
        <div className="sect" style={{ color: 'var(--cyan)' }}>{D.hero_title}</div>
        <div style={{ margin: '4px 0 10px', color: 'var(--tx)' }}>{D.hero_desc}</div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {['CONFIG FILES + WINDOWS SETTINGS', 'NO GAME MEMORY ACCESS', 'NOT AFFILIATED WITH VALVE'].map((p) => <span className="pill" key={p}><i className="dot" />{p}</span>)}
        </div>
      </div>

      <div className="dgrid">
        <Card title="CS2 environment">
          <div className="t" style={{ fontSize: 14 }}>{d?.cs2_dir ? 'CS2 found' : d ? 'CS2 not found' : '…'}</div>
          {d?.cs2_dir ? <div className="decal" style={{ margin: '4px 0 8px', wordBreak: 'break-all' }}>Counter-Strike 2 installation: {d.cs2_dir}</div> : d && <div className="decal" style={{ margin: '4px 0 8px' }}>{D.cs2_missing}</div>}
          <div style={{ color: 'var(--cyan)', marginBottom: 6 }}>{d?.autoexec?.text ?? ''}</div>
          <div className="decal" style={{ marginBottom: 12, textTransform: 'none', letterSpacing: 0, lineHeight: 1.5 }}>{D.autoexec_note}{d?.autoexec ? '' : ''}</div>
          <button className="btn cut ghost sm" disabled={!d?.cfg_dir} title={D.open_cfg} onClick={() => { sfx.click(); void api.openPath('cfg'); }}><FolderOpen size={13} /> Open cfg folder</button>
        </Card>
        <Card title="Storage: CS2 / Steam library drive">
          {dr ? <>
            <div className="t" style={{ fontSize: 14 }}>Drive {dr.drive} · {dr.free_gb.toFixed(1)} GB free of {dr.total_gb.toFixed(1)} GB ({free.toFixed(0)}% free)</div>
            <div className="bar" style={{ margin: '10px 0 6px' }}><i style={{ width: `${dr.used_pct}%`, background: tone }} /></div>
            <div className="mono" style={{ color: tone, fontSize: 12 }}>{low ? 'Low space (under 10% free)' : 'Space: OK'}</div>
            <div className="decal" style={{ marginTop: 8, textTransform: 'none', letterSpacing: 0, lineHeight: 1.5 }}>This is the drive that holds your CS2 install ({d?.cs2_dir?.slice(0, 2)}). Only free space is measured (not drive hardware health).</div>
          </> : <><div className="t" style={{ fontSize: 14 }}>CS2 not found</div><div className="mono" style={{ color: 'var(--tx3)', fontSize: 12, margin: '6px 0' }}>Space: unmonitored</div><div className="decal" style={{ textTransform: 'none', letterSpacing: 0 }}>{D.storage_missing}</div></>}
        </Card>
        <Card title="ZE game servers">
          <div className="t" style={{ fontSize: 14 }}>{tot.humans ?? '…'} players in-game</div>
          <div style={{ color: 'var(--cyan)', margin: '4px 0 12px' }}>{tot.online ?? '…'} / {tot.total ?? '…'} servers online</div>
          <div className="decal" style={{ marginBottom: 10, textTransform: 'none', letterSpacing: 0, lineHeight: 1.5 }}>{D.servers_note}</div>
          <button className="btn cut ghost sm" title={D.nav_servers} onClick={() => { sfx.click(); go('servers'); }}>Launch ZE browser</button>
        </Card>
        <Card title="Maintenance">
          <div>CS2 engine tweaks: optimized <b>{ago(d?.days_opt)}</b></div>
          <div>PC maintenance: clean <b>{ago(d?.days_maint)}</b></div>
          <div className="decal" style={{ margin: '6px 0 12px' }}>Recommended every 7 days.</div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <button className="btn cut ghost sm" onClick={() => { sfx.click(); go('engine'); }}>Engine tweaks</button>
            <button className="btn cut ghost sm" title={D.nav_maint} onClick={() => { sfx.click(); go('maintenance'); }}>Open PC maintenance</button>
          </div>
        </Card>
      </div>
    </section>
  );
}
