import { useCallback, useEffect, useState } from 'react';
import { api } from '../api';
import { sfx } from '../sound';
import { Info } from '../components/Info';
import PAGES from '../data/pages.json';
import type { PresenceState } from '../types';

const D = PAGES.discord;

export default function Discord() {
  const [p, setP] = useState<PresenceState | null>(null);
  const [persona, setPersona] = useState('');
  const refresh = useCallback(() => { void api.presence().then(setP); }, []);
  useEffect(() => { refresh(); void api.appInfo().then((i) => setPersona(i.persona ?? '')); const t = setInterval(refresh, 2000); return () => clearInterval(t); }, [refresh]);
  const idle = !p?.details && !p?.state;

  return (
    <section className="view on">
      <div className="vhead"><div><div className="decal">// 09 · social</div><h1>{D.title}</h1><p>{D.sub}</p></div>
        <span className="pill"><i className={`dot ${p?.connected ? '' : 'am'}`} />{p?.status ?? '...'}</span></div>
      <div className="glass card"><div className="decal" style={{ textTransform: 'none', letterSpacing: 0 }}>{D.pipe}</div></div>

      <div className="glass card brk">
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
          <span className="sect">{D.auto_title}</span><span className="tag">{D.auto_badge}</span>
        </div>
        <div className="ptext" style={{ margin: '8px 0 10px' }}>{D.auto_list}</div>
        <div className="row" style={{ padding: '6px 0' }}>
          <div className="grow"><div className="t">Enable Discord Rich Presence (RPC)</div><div className="d" title={D.enable_tip}>Turns the automatic CS2 Discord presence on or off.</div></div>
          <button className="sw" role="switch" aria-checked={!!p?.enabled} aria-label="Enable Discord Rich Presence" onClick={() => { sfx.toggle(); void api.presenceToggle(!p?.enabled).then(setP); }} />
        </div>
        <div className="row"><div className="grow"><div className="t">{D.identity_title}</div><div className="d" style={{ whiteSpace: 'pre-line' }}>{D.identity}</div></div></div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 10, alignItems: 'center' }}>
          <span className="mono" style={{ fontSize: 12, color: p?.connected ? 'var(--ok)' : 'var(--tx3)' }}>Status: {p?.status ?? 'Checking CS2...'}</span>
          <span style={{ flex: 1 }} />
          <button className="btn cut ghost sm" title={D.refresh_tip} onClick={() => { sfx.click(); void api.presenceRefresh().then(setP); }}>Refresh now</button>
          <button className="btn cut ghost sm" title={D.off_tip} onClick={() => { sfx.click(); void api.presenceClear().then(setP); }}>Turn off presence</button>
        </div>
      </div>

      <div className="glass card">
        <div className="sect" style={{ marginBottom: 4 }}>{D.sim_title}</div>
        <div className="decal" style={{ marginBottom: 10, textTransform: 'none', letterSpacing: 0 }}>{D.sim_sub}</div>
        <div className="dpreview">
          <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 12 }}><span className="av">{(persona || 'P')[0].toUpperCase()}</span><div><div className="t">{persona || 'Player'}</div><div className="decal" style={{ textTransform: 'none', letterSpacing: 0 }}>{p?.cs2_running ? 'Online' : 'Standby | CS2 closed (no presence)'}</div></div></div>
          <div className="decal">Playing a game</div>
          <div className="t" style={{ fontSize: 15, marginTop: 6 }}>Counter-Strike 2</div>
          <div style={{ marginTop: 6 }}>{idle ? (p?.cs2_running ? 'Waiting for the next update…' : 'Nothing is shown (CS2 is not running)') : p?.details}</div>
          {!idle && <div style={{ color: 'var(--tx2)', marginTop: 2 }}>{p?.state}</div>}
          {!!p?.buttons.length && <div style={{ display: 'flex', gap: 8, marginTop: 12, flexWrap: 'wrap' }}>{p.buttons.map((b) => <span key={b} className="dbtn">{b}</span>)}</div>}
        </div>
        <div className="decal" style={{ marginTop: 8, textTransform: 'none', letterSpacing: 0 }}>This preview comes from what the Discord desktop app was really sent, not from a guess.</div>
      </div>
      <Info title={D.why_title} text={D.why} open={false} />
    </section>
  );
}
