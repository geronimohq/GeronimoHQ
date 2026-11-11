import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { motion } from 'framer-motion';
import { Search } from 'lucide-react';
import { api, on } from '../api';
import { sfx } from '../sound';
import { useModal } from './Modal';
import type { MapRow } from '../types';

type Filter = 'all' | 'temp' | 'sub' | 'assets' | 'dupes';
const COMMS: [string, string][] = [['gfl', 'GFL'], ['possession', 'Possession (PSE)'], ['rss', 'RSS Revenant'], ['mapeadores_cola', 'Mapeadores / cOLa']];
const GB = 1024 ** 3;
const isTemp = (m: MapRow) => !m.sub && !m.asset && m.workshop;
const selectable = (m: MapRow) => !m.protected && !m.asset;
const fmt = (b: number) => (b >= GB ? `${(b / GB).toFixed(2)} GB` : `${(b / 1048576).toFixed(0)} MB`);

export default function MapCleaner({ onClose }: { onClose: () => void }) {
  const [rows, setRows] = useState<MapRow[]>([]);
  const [comms, setComms] = useState<string[]>(['gfl', 'possession', 'rss', 'mapeadores_cola']);
  const [recent, setRecent] = useState(true);
  const [filter, setFilter] = useState<Filter>('all');
  const [q, setQ] = useState('');
  const [sel, setSel] = useState<Set<string>>(new Set());
  const [sort, setSort] = useState<{ k: 'name' | 'size' | 'mtime'; dir: 1 | -1 }>({ k: 'size', dir: 1 });
  const [busy, setBusy] = useState(true);
  const openModal = useModal();
  const first = useRef(true);

  const scan = useCallback((c: string[], r: boolean) => { setBusy(true); void api.mapsScan(c, r).then((x) => { if (!x.ok) setBusy(false); }); }, []);
  useEffect(() => {
    const o1 = on<MapRow[]>('maps', (r) => { setRows(r); setSel(new Set()); });
    const o2 = on<{ name: string }>('job', (j) => { if (j.name === 'maps_scan') setBusy(false); });
    const o3 = on<{ count: number; freed: number; skipped?: number }>('maps_deleted', (d) => {
      openModal({ kind: 'ok', label: 'Clean complete', title: `Deleted ${d.count} maps`, body: `Reclaimed ${(d.freed / GB).toFixed(2)} GB of storage.${d.skipped ? `\n\n${d.skipped} selected item(s) were skipped because they are now protected or no longer on disk.` : ''}` });
      scan(comms, recent);
    });
    void api.mapsSettings().then((s) => { setComms(s.communities); setRecent(s.protect_recent); scan(s.communities, s.protect_recent); first.current = false; });
    const k = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', k);
    return () => { o1(); o2(); o3(); window.removeEventListener('keydown', k); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const toggleComm = (id: string) => { const n = comms.includes(id) ? comms.filter((c) => c !== id) : [...comms, id]; setComms(n); sfx.toggle(); scan(n, recent); };
  const toggleRecent = () => { setRecent(!recent); sfx.toggle(); scan(comms, !recent); };

  const counts = useMemo(() => ({ all: rows.length, temp: rows.filter(isTemp).length, sub: rows.filter((m) => m.sub && !m.asset).length, assets: rows.filter((m) => m.asset).length, dupes: rows.filter((m) => m.dupe).length }), [rows]);
  const shown = useMemo(() => {
    const t = q.trim().toLowerCase();
    const f = rows.filter((m) => (filter === 'all' || (filter === 'temp' && isTemp(m)) || (filter === 'sub' && m.sub && !m.asset) || (filter === 'assets' && m.asset) || (filter === 'dupes' && m.dupe)) && (!t || `${m.name} ${m.id} ${m.status}`.toLowerCase().includes(t)));
    return f.sort((a, b) => (a[sort.k] < b[sort.k] ? -1 : a[sort.k] > b[sort.k] ? 1 : 0) * sort.dir);
  }, [rows, filter, q, sort]);
  const selBytes = rows.filter((m) => sel.has(m.id)).reduce((n, m) => n + m.size, 0);
  const total = rows.reduce((n, m) => n + m.size, 0);

  const pick = (ids: string[]) => { sfx.click(); setSel(new Set(ids)); };
  const del = () => {
    const ids = [...sel];
    if (!ids.length) { openModal({ kind: 'warn', label: 'Nothing selected', title: 'Tick the maps to delete first' }); return; }
    openModal({
      kind: 'q', label: 'Confirm', title: `Delete ${ids.length} maps?`,
      body: `This permanently removes ${ids.length} maps (${fmt(selBytes)}). It cannot be undone.\n\nSubscribed server packs and official maps are protected. If you visit a server that plays one of these maps, CS2 downloads it again.`,
      confirm: { text: 'Delete maps', run: async () => { setBusy(true); const r = await api.mapsDelete(ids, comms, recent); if (!r.ok) { setBusy(false); openModal({ kind: 'warn', label: 'Problem', title: 'Not started', body: r.error }); } } },
    });
  };
  const backup = async () => { sfx.click(); const r = await api.mapsBackup(); openModal({ kind: r.count ? 'ok' : 'warn', label: 'Backup', title: r.count ? `Backed up ${r.count} VPK files` : 'No server asset VPKs found', body: r.count ? r.dir : undefined }); };
  const restore = async () => { sfx.click(); const r = await api.mapsRestore(); openModal({ kind: r.count ? 'ok' : 'warn', label: 'Restore', title: r.count ? `Restored ${r.count} VPK files` : 'No matching backups to restore' }); };
  const th = (k: 'name' | 'size' | 'mtime', label: string) => <th onClick={() => { sfx.click(); setSort({ k, dir: sort.k === k ? (-sort.dir as 1 | -1) : 1 }); }} className="srt">{label}{sort.k === k ? (sort.dir === 1 ? ' \u25B2' : ' \u25BC') : ''}</th>;

  return createPortal(
    <motion.div className="scrim on" role="dialog" aria-modal="true" aria-labelledby="mcTitle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <motion.div className="cut modal brk mc" initial={{ scale: 0.97, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.97, opacity: 0 }}>
        <div className="decal">// maintenance</div><h3 id="mcTitle">CS2 &amp; Zombie Escape custom map cleaner</h3>
        <div style={{ color: 'var(--tx2)', marginTop: 4 }}>Free up space by removing unneeded custom workshop maps. Subscribed server map packs and official Valve maps are detected and protected.</div>
        <div className="mcprot"><span className="sect">Protect packs</span>
          {COMMS.map(([id, label]) => <label key={id} className="chk"><input type="checkbox" checked={comms.includes(id)} onChange={() => toggleComm(id)} />{label}</label>)}
          <label className="chk"><input type="checkbox" checked={recent} onChange={toggleRecent} />Active (last 14 days)</label></div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center', margin: '10px 0' }}>
          <div className="seg" role="group" aria-label="Filter">
            {([['all', 'All maps'], ['temp', 'Temp downloads'], ['sub', 'Subscribed packs'], ['assets', 'Server assets'], ['dupes', 'Duplicates']] as [Filter, string][]).map(([k, l]) => (
              <button key={k} aria-pressed={filter === k} onClick={() => { sfx.click(); setFilter(k); }}>{l} ({counts[k]})</button>))}
          </div>
          <div className="search"><Search size={14} style={{ color: 'var(--tx3)' }} /><label className="sr" htmlFor="mq">Search maps</label><input id="mq" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search maps" /></div>
          <span className="mono" style={{ fontSize: 12, color: 'var(--tx)' }}>Total: {rows.length} maps ({fmt(total)}) | Selected: {sel.size} ({fmt(selBytes)})</span>
        </div>
        <div className="mctable">
          <table><thead><tr><th style={{ width: 34 }} />{th('name', 'Map / asset package')}<th>Workshop ID</th><th>Status</th>{th('size', 'Size')}{th('mtime', 'Last played / modified')}</tr></thead>
            <tbody>
              {busy && !rows.length && <tr><td colSpan={6} className="decal" style={{ padding: 20 }}>Scanning maps\u2026</td></tr>}
              {shown.map((m) => (
                <tr key={m.id} className={m.dupe ? 'dup' : isTemp(m) ? 'tmp' : ''}>
                  <td><input type="checkbox" aria-label={`Select ${m.name}`} disabled={!selectable(m)} checked={sel.has(m.id)} onChange={() => { const n = new Set(sel); if (n.has(m.id)) n.delete(m.id); else n.add(m.id); setSel(n); }} /></td>
                  <td>{m.name}</td><td className="mono">{m.id}</td><td>{m.status}</td><td className="mono">{m.size_str}</td><td className="mono">{m.mtime}</td>
                </tr>))}
            </tbody></table>
        </div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 10 }}>
          <button className="btn cut ghost sm" onClick={() => pick(rows.filter((m) => isTemp(m) && selectable(m)).map((m) => m.id))}>Select all temp downloads (safe)</button>
          <button className="btn cut ghost sm" onClick={() => pick(rows.filter((m) => isTemp(m) && m.dupe && selectable(m)).map((m) => m.id))}>Select temp dupes only (safe)</button>
          <button className="btn cut ghost sm" onClick={() => pick(shown.filter(selectable).map((m) => m.id))}>Select all</button>
          <button className="btn cut ghost sm" onClick={() => pick([])}>Deselect all</button>
          <button className="btn cut ghost sm" onClick={() => pick(rows.filter((m) => selectable(m) && m.size > GB).map((m) => m.id))}>Select maps &gt; 1 GB</button>
        </div>
        <div className="btns" style={{ justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <button className="btn cut danger" disabled={busy} onClick={del}>Delete selected maps</button>
            <button className="btn cut ghost" onClick={() => void backup()}>Backup custom VPK</button>
            <button className="btn cut ghost" onClick={() => void restore()}>Restore custom VPK</button>
          </div>
          <button className="btn cut ghost" onClick={() => { sfx.click(); onClose(); }}>Close</button>
        </div>
      </motion.div>
    </motion.div>,
    document.body,
  );
}
