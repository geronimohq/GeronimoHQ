import { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Play, Plus, Search } from 'lucide-react';
import { api } from '../api';
import { sfx } from '../sound';
import { Geo } from '../components/Geo';
import { useModal } from '../components/Modal';
import type { AppInfo, Match, SniperStatus, Srv, Status } from '../types';

type GeoMode = 'country' | 'region';
const botsMostly = (s?: Status) => !!s && (s.bots ?? 0) >= 3 && (s.bots ?? 0) * 2 >= (s.players ?? 0);

/** Highlights a value for a moment when it changes. */
function useFlash(v: unknown): string {
  const prev = useRef(v);
  const [on, setOn] = useState(false);
  useEffect(() => {
    if (prev.current === v) return;
    prev.current = v;
    setOn(true);
    const t = setTimeout(() => setOn(false), 700);
    return () => clearTimeout(t);
  }, [v]);
  return on ? 'flash' : '';
}

function MapTimer({ since, exact }: { since: number; exact: boolean }) {
  const [now, setNow] = useState(() => Date.now() / 1000);
  useEffect(() => { const t = setInterval(() => setNow(Date.now() / 1000), 1000); return () => clearInterval(t); }, []);
  const sec = Math.max(0, Math.floor(now - since));
  const m = Math.floor(sec / 60), s = sec % 60;
  return <span className="cell">&#9201; {exact ? '' : '≥ '}{m}:{String(s).padStart(2, '0')} on map</span>;
}

const Row = memo(function Row({ srv, st, mode, onMode, since, armed, onConnect, onPlayers, onSniper }: { srv: Srv; st?: Status; mode: GeoMode; onMode: (m: GeoMode) => void; since?: number; armed: boolean; onConnect: () => void; onPlayers: () => void; onSniper: () => void }) {
  const humans = st?.humans ?? 0;
  const fp = useFlash(humans), fg = useFlash(st?.ping);
  return (
    <article className="glass srv">
      <div style={{ minWidth: 0 }}>
        <div className="nm"><span className="cc">{srv.flag.replace(/[^A-Za-z]/g, '').slice(0, 2).toUpperCase() || '--'}</span>{srv.name}</div>
        <div className="cells">
          {st?.online
            ? <>
                <span className={`cell ${fp}`}>&#9679; <b>{humans}</b>/{st.max} humans</span>
                {botsMostly(st) && <span className="cell bots" title={`${st.bots} of the ${st.players} players are bots (about ${humans} real). Totals exclude them.`}>&#129302; MOSTLY BOTS ({st.bots}/{st.players})</span>}
                <span className={`cell cy ${fg}`}>{st.ping ?? '-'} ms</span>
                {since ? <MapTimer since={since} exact={false} /> : null}
              </>
            : <span className="cell">{st ? '● Offline / not answering' : 'Querying…'}</span>}
        </div>
        <div className="decal" style={{ marginTop: 7 }}>{srv.region || srv.cluster || 'Custom'}{st?.map ? ` · ${st.map}` : ''}</div>
      </div>
      <Geo countries={st?.geo?.countries ?? []} regions={st?.geo?.regions ?? []} mode={mode} onMode={onMode} humans={humans} />
      <div className="dock">
        <button className={`btn cut amber pri sm${st?.online ? '' : ' dim'}`} onClick={onConnect}>Connect</button>
        <button className={`btn cut ${armed ? 'armed' : 'ghost'} sm`} aria-pressed={armed} onClick={onSniper}>{armed ? 'Sniper armed' : 'Sniper'}</button>
        <button className="btn cut ghost sm" onClick={onPlayers}>Players</button>
      </div>
    </article>
  );
});

function AddServer({ onClose, onSaved }: { onClose: () => void; onSaved: () => void }) {
  const [name, setName] = useState(''), [addr, setAddr] = useState(''), [err, setErr] = useState('');
  const save = async () => {
    const m = addr.trim().match(/^(.+):(\d{2,5})$/);
    if (!m) { setErr('Enter the address as host:port, for example 74.91.124.21:27015.'); return; }
    const r = await api.addServer(name, m[1], Number(m[2]));
    if (r.ok) { sfx.toggle(); onSaved(); onClose(); } else setErr(r.error ?? 'Could not save the server.');
  };
  return (
    <motion.div className="scrim on" role="dialog" aria-modal="true" aria-labelledby="addTitle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <motion.div className="cut modal brk" initial={{ scale: 0.94, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.96, opacity: 0 }}>
        <div style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
          <div className="ic q">+</div><div><div className="decal">Server list</div><h3 id="addTitle">Add server</h3></div>
        </div>
        <div className="field"><label htmlFor="fName">Server name</label><input id="fName" value={name} onChange={(e) => setName(e.target.value)} placeholder="My ZE server" autoFocus /></div>
        <div className="field"><label htmlFor="fHost">Host : port</label><input id="fHost" value={addr} onChange={(e) => setAddr(e.target.value)} placeholder="74.91.124.21:27015" onKeyDown={(e) => { if (e.key === 'Enter') void save(); }} /></div>
        {err && <div style={{ color: 'var(--bad)', marginTop: 10 }} role="alert">{err}</div>}
        <div className="btns"><button className="btn cut ghost" onClick={() => { sfx.click(); onClose(); }}>Cancel</button><button className="btn cut amber pri" onClick={() => void save()}>Save server</button></div>
      </motion.div>
    </motion.div>
  );
}

export default function Servers({ info, log, sniper, tier, setTier }: { info: AppInfo | null; log: (tag: string, msg: string) => void; sniper: SniperStatus | null; tier: number; setTier: (n: number) => void }) {
  const openModal = useModal();
  const [catalog, setCatalog] = useState<Srv[]>([]);
  const [st, setSt] = useState<Record<string, Status>>({});
  const [rate, setRateState] = useState(info?.refresh_seconds ?? 5);
  const [q, setQ] = useState('');
  const [group, setGroup] = useState<'global' | 'china'>('global');
  const [modes, setModes] = useState<Record<string, GeoMode>>({});
  const [match, setMatch] = useState<Match>({});
  const [totals, setTotals] = useState<{ humans?: number; online?: number; total?: number }>({});
  const [adding, setAdding] = useState(false);
  const seen = useRef<Record<string, { map: string; since: number }>>({});
  const busy = useRef({ list: false, feat: false });

  const loadCatalog = useCallback(() => { void api.catalog().then(setCatalog); }, []);
  useEffect(loadCatalog, [loadCatalog]);

  const merge = useCallback((rows: Status[]) => {
    const now = Date.now() / 1000;
    for (const r of rows) {
      if (r.online && r.map && seen.current[r.id]?.map !== r.map) seen.current[r.id] = { map: r.map, since: now };
    }
    setSt((p) => { const n = { ...p }; for (const r of rows) n[r.id] = r; return n; });
  }, []);

  const featured = catalog.find((s) => s.featured);
  const listAll = useMemo(() => catalog.filter((s) => !s.featured && s.group === group), [catalog, group]);
  const list = useMemo(() => {
    const t = q.trim().toLowerCase();
    return t ? listAll.filter((s) => `${s.name} ${s.region} ${s.cluster} ${st[s.id]?.map ?? ''}`.toLowerCase().includes(t)) : listAll;
  }, [listAll, q, st]);

  // list refresh at the chosen rate (the server queries run in Python threads; the page only repaints changed cells)
  useEffect(() => {
    const ids = listAll.map((s) => s.id);
    if (!ids.length) return;
    const run = async () => {
      if (busy.current.list) return;
      busy.current.list = true;
      try { merge(await api.statusMany(ids)); } finally { busy.current.list = false; }
    };
    void run();
    const t = setInterval(run, rate * 1000);
    return () => clearInterval(t);
  }, [listAll, rate, merge]);

  // featured server: every second
  useEffect(() => {
    if (!featured) return;
    const run = async () => {
      if (busy.current.feat) return;
      busy.current.feat = true;
      try { merge(await api.statusMany([featured.id])); } finally { busy.current.feat = false; }
    };
    void run();
    const t = setInterval(run, 1000);
    const m = setInterval(() => { void api.gflMatch().then(setMatch); }, 2500);
    void api.gflMatch().then(setMatch);
    return () => { clearInterval(t); clearInterval(m); };
  }, [featured, merge]);

  useEffect(() => {
    const go = () => { void api.totals().then(setTotals); };
    go();
    const t = setInterval(go, 60000);
    return () => clearInterval(t);
  }, []);

  const connect = (s: Srv) => {
    sfx.click();
    void api.connect(s.id).then((r) => {
      if (!r.ok) openModal({ kind: 'warn', label: 'Problem', title: 'Could not connect', body: r.error });
      else log('SERVERS', `Connecting to ${s.name}`);
    });
  };
  const players = async (s: Srv) => {
    sfx.click();
    const r = await api.players(s.id);
    openModal({
      kind: r.success ? 'ok' : 'warn', label: 'Active players', title: s.name,
      body: r.success
        ? (r.players.length ? <div className="roster">{r.players.map((p, i) => <div key={i} className="rrow"><span>{p.name}</span><span className="mono">{p.score}</span><span className="mono">{p.time}</span></div>)}</div> : 'No players on the server right now.')
        : (r.error || 'The server did not answer the player list request.'),
    });
  };
  const toggleSniper = (s: Srv) => {
    sfx.click();
    if (sniper?.active && sniper.target === s.name) { void api.sniperStop(); return; }
    void api.sniperStart(s.id, tier);
  };
  const isArmed = (s: Srv) => !!sniper?.active && sniper.target === s.name;
  const f = featured ? st[featured.id] : undefined;
  const fHumans = f?.humans ?? 0;
  const ringDash = f?.online && f.max ? Math.min(1, (f.players ?? 0) / f.max) : 0;
  const featSince = match.started_sec && match.started_sec > 0 ? match.started_sec : seen.current[featured?.id ?? '']?.since;
  const setMode = (id: string) => (m: GeoMode) => setModes((p) => ({ ...p, [id]: m }));
  const pickRate = (s: number) => { sfx.click(); setRateState(s); void api.setRefresh(s); log('SYSTEM', `List refresh set to ${s} s`); };
  const fp = useFlash(fHumans), fg = useFlash(f?.ping);

  return (
    <section className="view on">
      <div className="vhead">
        <div><div className="decal">// 07 · live telemetry</div><h1>ZE game servers</h1><p>Direct Steam server queries. Player counts are humans only, bots are not counted.</p></div>
        <div className="seg cy" role="group" aria-label="List refresh rate">
          {[1, 5, 15].map((s) => <button key={s} aria-pressed={rate === s} onClick={() => pickRate(s)}>{s}s</button>)}
        </div>
      </div>

      {featured && (
        <div className="featwrap">
          <article className="glass feat cut" style={{ ['--c' as string]: '18px', ['--fill' as string]: 'rgba(12,17,23,.9)' }}>
            <div className="hero">
              <div className="map">
                <div className="meta"><span className="tag">PREMIER FEATURED</span><span className="pill" style={{ fontSize: 10 }}>{featured.region.toUpperCase()}</span></div>
                <div className="mname">{f?.map ?? '…'}</div>
              </div>
              <div className="fbody">
                <h2>{featured.name.replace(/ 24\/7$/, '')} <em>24/7</em></h2>
                <div style={{ display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
                  <div className="ring">
                    <svg viewBox="0 0 100 100">
                      <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,.08)" strokeWidth="9" />
                      <circle cx="50" cy="50" r="42" fill="none" stroke="url(#g)" strokeWidth="9" strokeLinecap="round" strokeDasharray="264" strokeDashoffset={264 * (1 - ringDash)} style={{ transition: 'stroke-dashoffset .6s' }} />
                      <defs><linearGradient id="g"><stop offset="0" stopColor="#00F0FF" /><stop offset="1" stopColor="#FF9E1B" /></linearGradient></defs>
                    </svg>
                    <div className="v"><div>{f?.players ?? '--'}/{f?.max ?? '--'}<small>PLAYERS</small></div></div>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6, minWidth: 0 }}>
                    <span className={`cell ${fp}`}>&#9679; <b>{fHumans}</b> humans</span>
                    <span className={`cell cy ${fg}`}>{f?.ping ?? '-'} ms</span>
                    {featSince ? <MapTimer since={featSince} exact={!!match.started_sec} /> : null}
                  </div>
                </div>
                <div className="stat"><span>Humans <b style={{ color: 'var(--cyan)' }}>{match.human_score ?? '-'}</b></span><span>Zombies <b style={{ color: 'var(--bad)' }}>{match.zombie_score ?? '-'}</b></span><span>Extends <b>{match.extend_count ?? '-'}/3</b></span></div>
                <Geo countries={f?.geo?.countries ?? []} regions={f?.geo?.regions ?? []} mode={modes[featured.id] ?? 'country'} onMode={setMode(featured.id)} humans={fHumans} />
                <div className="dock">
                  <button className="btn cut amber pri sm" onClick={() => connect(featured)}><Play size={13} /> Connect</button>
                  <button className={`btn cut ${isArmed(featured) ? 'armed' : 'ghost'} sm`} aria-pressed={isArmed(featured)} onClick={() => toggleSniper(featured)}>{isArmed(featured) ? 'Sniper armed' : 'Sniper'}</button>
                  <button className="btn cut ghost sm" onClick={() => void players(featured)}>Players</button>
                  <button className="btn cut ghost sm" onClick={() => { sfx.toggle(); try { void navigator.clipboard.writeText(`${featured.host}:${featured.port}`); } catch { /* ignore */ } }}>Copy IP</button>
                </div>
              </div>
            </div>
          </article>
        </div>
      )}

      <div className="glass toolbar">
        <div className="seg" role="group" aria-label="Community">
          <button aria-pressed={group === 'global'} onClick={() => { sfx.click(); setGroup('global'); }}>Global</button>
          <button aria-pressed={group === 'china'} onClick={() => { sfx.click(); setGroup('china'); }}>Planet China</button>
        </div>
        <div className="search"><Search size={15} style={{ color: 'var(--tx3)' }} /><label className="sr" htmlFor="q">Filter servers</label>
          <input id="q" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filter by name, map or region" /></div>
        <div className="seg" role="group" aria-label="Sniper target" title="The Slot Sniper joins when the player count falls to this number or lower">
          {[61, 62, 63].map((n) => <button key={n} aria-pressed={tier === n} onClick={() => { sfx.click(); setTier(n); }}>{'\u2264'}{n}</button>)}
        </div>
        {totals.humans !== undefined && <span className="pill" title="Human players on the catalog servers that answered recently"><i className="dot cy" />{totals.humans} PLAYERS IN-GAME</span>}
        {totals.online !== undefined && <span className="pill">{totals.online} / {totals.total} SERVERS ONLINE</span>}
        <button className="btn cut sm ghost" onClick={() => { sfx.click(); setAdding(true); }}><Plus size={13} /> Add server</button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {list.map((s) => <Row key={s.id} srv={s} st={st[s.id]} mode={modes[s.id] ?? 'country'} onMode={setMode(s.id)} since={seen.current[s.id]?.since} armed={isArmed(s)} onConnect={() => connect(s)} onPlayers={() => void players(s)} onSniper={() => toggleSniper(s)} />)}
        {!list.length && <div className="glass card ph">No servers match.</div>}
      </div>
      <AnimatePresence>{adding && <AddServer onClose={() => setAdding(false)} onSaved={() => { log('SERVERS', 'Server saved'); loadCatalog(); }} />}</AnimatePresence>
    </section>
  );
}
