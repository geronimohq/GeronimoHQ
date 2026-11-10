import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { motion } from 'framer-motion';
import { RefreshCw, Search } from 'lucide-react';
import { api } from '../api';
import { sfx } from '../sound';
import type { PlayerRow, Srv } from '../types';

type SortKey = 'rank' | 'name' | 'score' | 'time';

/** Live player roster of one server: filter, sort, refresh and connect (same data as the classic Active Players window). */
export default function PlayersDialog({ srv, onClose, onConnect }: { srv: Srv; onClose: () => void; onConnect: () => void }) {
  const [rows, setRows] = useState<PlayerRow[]>([]);
  const [status, setStatus] = useState('Fetching player roster from server...');
  const [q, setQ] = useState('');
  const [sort, setSort] = useState<{ k: SortKey; dir: 1 | -1 }>({ k: 'score', dir: -1 });
  const loaded = useRef(false);
  // silent = the automatic refresh: it swaps the rows in place (no "Fetching" flash) and keeps the old list if one query fails
  const load = useCallback((silent = false) => {
    if (!silent) setStatus('Fetching player roster from server...');
    void api.players(srv.id).then((r) => {
      if (!r.success) { if (!silent || !loaded.current) { setRows([]); setStatus(r.error || 'The server did not answer the player list request.'); } return; }
      loaded.current = true;
      setRows(r.players); setStatus(r.players.length ? '' : 'No active players currently connected');
    });
  }, [srv.id]);
  const closeRef = useRef(onClose);
  closeRef.current = onClose;          // the parent passes a new function on every repaint; it must not restart the load
  useEffect(() => { load(); const t = setInterval(() => load(true), 5000); return () => clearInterval(t); }, [load]);
  useEffect(() => { const k = (e: KeyboardEvent) => { if (e.key === 'Escape') closeRef.current(); }; window.addEventListener('keydown', k); return () => window.removeEventListener('keydown', k); }, []);

  const shown = useMemo(() => {
    const t = q.trim().toLowerCase();
    const ranked = [...rows].sort((a, b) => b.score - a.score).map((r, i) => ({ ...r, rank: i + 1 }));
    const f = ranked.filter((r) => !t || r.name.toLowerCase().includes(t));
    return f.sort((a, b) => {
      const A = sort.k === 'time' ? (a.seconds ?? 0) : a[sort.k], B = sort.k === 'time' ? (b.seconds ?? 0) : b[sort.k];
      return (A < B ? -1 : A > B ? 1 : 0) * sort.dir;
    });
  }, [rows, q, sort]);
  const th = (k: SortKey, label: string) => <th className="srt" onClick={() => { sfx.click(); setSort({ k, dir: sort.k === k ? (-sort.dir as 1 | -1) : (k === 'name' || k === 'rank' ? 1 : -1) }); }}>{label}{sort.k === k ? (sort.dir === 1 ? ' \u25B2' : ' \u25BC') : ''}</th>;

  return createPortal(
    <motion.div className="scrim on" role="dialog" aria-modal="true" aria-labelledby="plTitle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <motion.div className="cut modal brk mc" style={{ width: 'min(760px,100%)' }} initial={{ scale: 0.96, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.96, opacity: 0 }}>
        <div className="decal">Active players</div><h3 id="plTitle">{srv.name}</h3>
        <div className="decal" style={{ margin: '6px 0 10px', textTransform: 'none', letterSpacing: 0, lineHeight: 1.5 }}>Protocol notice: player names, scores and connection times are queried live (A2S_PLAYER). Human and zombie round scores are shielded from public UDP queries by Valve.</div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center', marginBottom: 8 }}>
          <div className="search"><Search size={14} style={{ color: 'var(--tx3)' }} /><label className="sr" htmlFor="pq">Filter players</label><input id="pq" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filter by name" /></div>
          <span className="mono" style={{ fontSize: 12 }}>{shown.length} players</span>
          <button className="btn cut ghost sm" onClick={() => { sfx.click(); load(); }}><RefreshCw size={13} /> Refresh roster</button>
        </div>
        <div className="mctable" style={{ maxHeight: '46vh' }}>
          <table><thead><tr>{th('rank', '#')}{th('name', 'Player name')}{th('score', 'Score / points')}{th('time', 'Session time')}</tr></thead>
            <tbody>{status ? <tr><td colSpan={4} className="decal" style={{ padding: 18 }}>{status}</td></tr> : shown.map((r, i) => <tr key={i}><td className="mono">{r.rank}</td><td title={r.name === '[Connecting...]' ? 'The server lists this player without a name until they finish loading into the game. This list refreshes every 5 seconds.' : undefined}>{r.name}</td><td className="mono">{r.score}</td><td className="mono">{r.time}</td></tr>)}</tbody></table>
        </div>
        <div className="btns" style={{ justifyContent: 'space-between' }}>
          <button className="btn cut amber pri" onClick={() => { sfx.click(); onConnect(); onClose(); }}>Connect to server</button>
          <button className="btn cut ghost" onClick={() => { sfx.click(); onClose(); }}>Close</button>
        </div>
      </motion.div>
    </motion.div>,
    document.body,
  );
}
