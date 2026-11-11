import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { motion } from 'framer-motion';
import { Search } from 'lucide-react';
import { api, on } from '../api';
import { sfx } from '../sound';
import { useModal } from './Modal';
import type { MapRow, MapsNews } from '../types';

type Filter = 'all' | 'temp' | 'sub' | 'assets';
const COMMS: [string, string][] = [['gfl', 'GFL']];     // only GFL re-uploads the maps it runs, so only GFL's collection protects maps; 'Active' covers the rest
const RECENT_DAYS = 30;                                  // keep in step with RECENT_DAYS in custom_map_cleaner.py
const GB = 1024 ** 3;
const isTemp = (m: MapRow) => !m.sub && !m.asset && m.workshop;
const selectable = (m: MapRow) => !m.protected && !m.asset;          // bulk buttons never pick asset packs
const canTick = (m: MapRow, allowAssets: boolean) => selectable(m) || (m.asset && allowAssets);
const fmt = (b: number) => (b >= GB ? `${(b / GB).toFixed(2)} GB` : `${(b / 1048576).toFixed(0)} MB`);

export default function MapCleaner({ onClose }: { onClose: () => void }) {
  const [rows, setRows] = useState<MapRow[]>([]);
  const [comms, setComms] = useState<string[]>(['gfl']);
  const [recent, setRecent] = useState(true);
  const [allowAssets, setAllowAssets] = useState(false);     // advanced, never remembered: asset packs can only be ticked one by one
  const [filter, setFilter] = useState<Filter>('all');
  const [q, setQ] = useState('');
  const [sel, setSel] = useState<Set<string>>(new Set());
  const [sort, setSort] = useState<{ k: 'name' | 'size' | 'mtime'; dir: 1 | -1 }>({ k: 'size', dir: 1 });
  const [busy, setBusy] = useState(true);
  const openModal = useModal();
  const first = useRef(true);
  const [news, setNews] = useState<MapsNews | null>(null);
  useEffect(() => { void api.mapsNews().then(setNews); }, [rows.length]);       // after each scan, so a map subscribed in the meantime stops being "new"

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
  const toggleAssets = () => { sfx.toggle(); if (allowAssets) setSel(new Set([...sel].filter((id) => !rows.find((m) => m.id === id)?.asset))); setAllowAssets(!allowAssets); };
  const toggleRecent = () => { setRecent(!recent); sfx.toggle(); scan(comms, !recent); };

  const unusedLabel = recent ? `Not played in ${RECENT_DAYS}+ days` : 'Not protected';       // what the old 'Temp downloads' tab really is: everything that nothing protects
  const counts = useMemo(() => ({ all: rows.length, temp: rows.filter(isTemp).length, sub: rows.filter((m) => m.sub && !m.asset).length, assets: rows.filter((m) => m.asset).length }), [rows]);
  const shown = useMemo(() => {
    const t = q.trim().toLowerCase();
    const f = rows.filter((m) => (filter === 'all' || (filter === 'temp' && isTemp(m)) || (filter === 'sub' && m.sub && !m.asset) || (filter === 'assets' && m.asset)) && (!t || `${m.name} ${m.id} ${m.status}`.toLowerCase().includes(t)));
    return f.sort((a, b) => (a[sort.k] < b[sort.k] ? -1 : a[sort.k] > b[sort.k] ? 1 : 0) * sort.dir);
  }, [rows, filter, q, sort]);
  const selBytes = rows.filter((m) => sel.has(m.id)).reduce((n, m) => n + m.size, 0);
  const total = rows.reduce((n, m) => n + m.size, 0);

  const pick = (ids: string[]) => { sfx.click(); setSel(new Set(ids)); };
  const del = () => {
    const ids = [...sel];
    if (!ids.length) { openModal({ kind: 'warn', label: 'Nothing selected', title: 'Tick the maps to delete first' }); return; }
    const assets = rows.filter((m) => sel.has(m.id) && m.asset);
    openModal({
      kind: 'q', label: 'Confirm', title: `Delete ${ids.length} ${assets.length ? 'items' : 'maps'}?`,
      body: `This permanently removes ${ids.length} item(s) (${fmt(selBytes)}). It cannot be undone.\n\nSubscribed server packs and official maps are protected. If you visit a server that plays one of these maps, CS2 downloads it again.${assets.length ? `\n\nIncluded: ${assets.length} SERVER ASSET PACK(S) (${assets.map((m) => m.name).join(', ')}). Servers need their asset packs to join and show correctly. If you are still subscribed on Steam, Steam may download them again; unsubscribe on Steam to keep them gone. Use Backup custom VPK first if unsure.` : ''}`,
      confirm: { text: assets.length ? 'Delete including asset packs' : 'Delete maps', run: async () => { setBusy(true); const r = await api.mapsDelete(ids, comms, recent, allowAssets); if (!r.ok) { setBusy(false); openModal({ kind: 'warn', label: 'Problem', title: 'Not started', body: r.error }); } } },
    });
  };
  const backup = async () => { sfx.click(); const r = await api.mapsBackup(); openModal({ kind: r.count ? 'ok' : 'warn', label: 'Backup', title: r.count ? `Backed up ${r.count} VPK files` : 'No server asset VPKs found', body: r.count ? r.dir : undefined }); };
  const restore = async () => { sfx.click(); const r = await api.mapsRestore(); openModal({ kind: r.count ? 'ok' : 'warn', label: 'Restore', title: r.count ? `Restored ${r.count} VPK files` : 'No matching backups to restore' }); };
  const th = (k: 'name' | 'size' | 'mtime', label: string) => <th onClick={() => { sfx.click(); setSort({ k, dir: sort.k === k ? (-sort.dir as 1 | -1) : 1 }); }} className="srt">{label}{sort.k === k ? (sort.dir === 1 ? ' \u25B2' : ' \u25BC') : ''}</th>;

  return createPortal(
    <motion.div className="scrim on" role="dialog" aria-modal="true" aria-labelledby="mcTitle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <motion.div className="cut modal brk mc" initial={{ scale: 0.97, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.97, opacity: 0 }}>
        <div className="decal">// maintenance</div><h3 id="mcTitle">CS2 &amp; Zombie Escape custom map cleaner <span className="mono" style={{ fontSize: 11, color: 'var(--amber)', border: '1px solid var(--amber)', padding: '1px 7px', marginLeft: 8, verticalAlign: 'middle' }}>BETA</span></h3>
        <div style={{ color: 'var(--amber)', marginTop: 4, fontWeight: 600 }}>Beta: check carefully before deleting anything. Deleted files cannot be restored by this app.</div>
        <div style={{ color: 'var(--tx2)', marginTop: 4 }}>Free up space by removing unneeded custom workshop maps. Official Valve maps, server asset packs, GFL&apos;s maps and maps you played in the last {RECENT_DAYS} days are protected. GFL maps are recognised by GFL&apos;s own Steam collection (GFL uploads its own copy of every map it runs).</div>
        {news && news.new > 0 && (
          <div role="status" style={{ border: '1px solid var(--cyan)', background: 'var(--cyan-dim)', borderRadius: 8, padding: '8px 12px', marginTop: 8 }}>
            <b>GFL added {news.new} new map{news.new === 1 ? '' : 's'} to its collection that you do not have.</b>{' '}
            To get {news.new === 1 ? 'it' : 'them'}: close this window, open <b>ZE Game Servers</b>, and click <b>Map pack</b> on the GFL server. Press Subscribe on GFL&apos;s collection page and Steam downloads what is missing.
          </div>
        )}
        <div className="mcprot"><span className="sect">Protected Maps</span>
          {COMMS.map(([id, label]) => <label key={id} className="chk"><input type="checkbox" checked={comms.includes(id)} onChange={() => toggleComm(id)} />{label}</label>)}
          <label className="chk"><input type="checkbox" checked={recent} onChange={toggleRecent} />Active (last {RECENT_DAYS} days)</label>
          <label className="chk" title="Advanced. Lets you tick server asset packs (models, sounds) to delete them. Servers need these to join."><input type="checkbox" checked={allowAssets} onChange={toggleAssets} />Allow deleting server asset packs (advanced)</label></div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center', margin: '10px 0' }}>
          <div className="seg" role="group" aria-label="Filter">
            {([['all', 'All maps'], ['temp', unusedLabel], ['sub', 'Subscribed packs'], ['assets', 'Server assets']] as [Filter, string][]).map(([k, l]) => (
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
                <tr key={m.id} className={isTemp(m) ? 'tmp' : ''}>
                  <td><input type="checkbox" aria-label={`Select ${m.name}`} disabled={!canTick(m, allowAssets)} checked={sel.has(m.id)} onChange={() => { const n = new Set(sel); if (n.has(m.id)) n.delete(m.id); else n.add(m.id); setSel(n); }} /></td>
                  <td>{m.name}</td><td className="mono">{m.id}</td><td>{m.status}</td><td className="mono">{m.size_str}</td><td className="mono">{m.mtime}</td>
                </tr>))}
            </tbody></table>
        </div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 10 }}>
          <button className="btn cut ghost sm" onClick={() => pick(rows.filter((m) => isTemp(m) && selectable(m)).map((m) => m.id))}>Select all {unusedLabel.toLowerCase()} (safe)</button>
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
