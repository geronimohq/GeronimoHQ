import { useCallback, useEffect, useState } from 'react';
import { api } from '../api';
import { sfx } from '../sound';
import { useModal } from '../components/Modal';
import type { PresenceState, Srv } from '../types';

export default function Discord() {
  const [p, setP] = useState<PresenceState | null>(null);
  const [servers, setServers] = useState<Srv[]>([]);
  const [pick, setPick] = useState('gfl');
  const openModal = useModal();
  const refresh = useCallback(() => { void api.presence().then(setP); }, []);
  useEffect(() => {
    refresh();
    void api.catalog().then((c) => setServers(c.filter((s) => s.group === 'global')));
    const t = setInterval(refresh, 2000);
    return () => clearInterval(t);
  }, [refresh]);

  const idle = !p?.details && !p?.state;
  const broadcast = async () => {
    sfx.click();
    const r = await api.presenceBroadcast(pick);
    openModal(r.ok ? { kind: 'ok', label: 'Discord', title: 'Now broadcasting', body: 'Your Discord profile shows this server while CS2 runs.' } : { kind: 'warn', label: 'Problem', title: 'Not broadcast', body: r.error });
    refresh();
  };
  return (
    <section className="view on">
      <div className="vhead"><div><div className="decal">// 09 · social</div><h1>Discord presence</h1><p>Shows your CS2 map and server on your Discord profile while the game runs. Nothing is shown when CS2 is closed.</p></div>
        <span className="pill"><i className={`dot ${p?.connected ? '' : 'am'}`} />{p?.status ?? '...'}</span></div>
      <div className="glass card brk">
        <div className="row" style={{ border: 0, padding: '4px 6px' }}>
          <div className="grow"><div className="t">Share game status with Discord</div><div className="d">Uses the app's own Discord application ID. No setup needed.</div></div>
          <button className="sw" role="switch" aria-checked={!!p?.enabled} aria-label="Share game status with Discord" onClick={() => { sfx.toggle(); void api.presenceToggle(!p?.enabled).then(setP); }} />
        </div>
      </div>
      <div className="glass card">
        <div className="sect" style={{ marginBottom: 10 }}>What Discord shows right now</div>
        <div className="dpreview">
          <div className="decal">Playing Counter-Strike 2</div>
          <div className="t" style={{ fontSize: 15, marginTop: 6 }}>{idle ? (p?.cs2_running ? 'Waiting for the next update\u2026' : 'Nothing is shown (CS2 is not running)') : p?.details}</div>
          {!idle && <div style={{ color: 'var(--tx2)', marginTop: 2 }}>{p?.state}</div>}
          {!!p?.buttons.length && <div style={{ display: 'flex', gap: 8, marginTop: 12, flexWrap: 'wrap' }}>{p.buttons.map((b) => <span key={b} className="dbtn">{b}</span>)}</div>}
        </div>
        <div className="decal" style={{ marginTop: 8 }}>This preview comes from what the Discord desktop app was really sent, not from a guess.</div>
      </div>
      <div className="glass card">
        <div className="sect" style={{ marginBottom: 8 }}>Manual controls</div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
          <div className="field" style={{ margin: 0 }}><label htmlFor="bs">Broadcast a server</label>
            <select id="bs" className="sel" value={pick} onChange={(e) => setPick(e.target.value)}>{servers.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}</select></div>
          <button className="btn cut ghost" style={{ alignSelf: 'flex-end' }} onClick={() => void broadcast()}>Broadcast</button>
          <span style={{ flex: 1 }} />
          <button className="btn cut ghost" onClick={() => { sfx.click(); void api.presenceStandby().then(setP); }}>Set main-menu standby</button>
          <button className="btn cut ghost" onClick={() => { sfx.click(); void api.presenceClear().then(setP); }}>Clear presence</button>
        </div>
      </div>
    </section>
  );
}
