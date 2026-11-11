import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { motion } from 'framer-motion';
import { api } from '../api';
import { sfx } from '../sound';
import type { MapHelp, PackSize } from '../types';

const fmtGb = (b: number) => (b >= 1e9 ? `${(b / 1e9).toFixed(b >= 1e10 ? 0 : 1)} GB` : `${Math.max(1, Math.round(b / 1e6))} MB`);
const KIND: Record<string, string> = { maps: 'Map list', default: 'Default map', assets: 'Server assets (collection)', item: 'Server asset pack' };

/** What to do about a map you do not have, or how to get a server's whole map pack: the one map (small), or the server's Steam collections. */
export default function MapHelpDialog({ sid, name, map, wid, mode, onClose, log }: { sid: string; name: string; map: string; wid: string; mode: 'maps' | 'assets'; onClose: () => void; log: (tag: string, msg: string) => void }) {
  const [help, setHelp] = useState<MapHelp | null>(null);
  const [sizes, setSizes] = useState<Record<string, PackSize>>({});
  const closeRef = useRef(onClose);
  closeRef.current = onClose;
  useEffect(() => {
    let alive = true;
    void api.mapHelp(sid, map, wid, mode).then((h) => {
      if (!alive) return;
      setHelp(h);
      h.collections.forEach((c) => {
        void api.collectionSize(c.id).then((s) => { if (alive && s.ok) setSizes((p) => ({ ...p, [c.id]: s })); });
      });
    });
    const k = (e: KeyboardEvent) => { if (e.key === 'Escape') closeRef.current(); };
    window.addEventListener('keydown', k);
    return () => { alive = false; window.removeEventListener('keydown', k); };
  }, [sid, map, wid, mode]);

  const openMap = () => { sfx.click(); void api.mapGet(map, wid).then((r) => { if (!r.ok) log('SERVERS', 'Could not open Steam or the browser for this map.'); }); };
  const openCol = (id: string) => { sfx.click(); void api.collectionOpen(id).then((r) => { if (!r.ok) log('SERVERS', 'Could not open Steam for this collection.'); }); };
  const m = help ? help.map : (map ? { name: map, wid } : null);      // loaded: the server decides (GFL has no single-map page)

  return createPortal(
    <motion.div className="scrim on" role="dialog" aria-modal="true" aria-labelledby="mhTitle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <motion.div className="cut modal brk mc" style={{ width: 'min(680px,100%)' }} initial={{ scale: 0.96, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.96, opacity: 0 }}>
        <div className="decal">{map ? 'Map not installed' : mode === 'assets' ? 'Server assets' : 'Map pack'}</div>
        <h3 id="mhTitle">{map ? map : name}</h3>
        {map && <div className="decal" style={{ margin: '4px 0 10px', textTransform: 'none', letterSpacing: 0, lineHeight: 1.5 }}>
          {name} is playing <b>{map}</b> and it is not on this PC. You can still join: CS2 then asks to download just this map. Or get it first, in one of these ways.
        </div>}
        {map && help?.reupload && (
          <div className="glass card" style={{ margin: '8px 0', padding: 12 }}>
            <div className="sect">GFL uploads its own copy of every map</div>
            <div className="decal" style={{ textTransform: 'none', letterSpacing: 0, marginTop: 4, lineHeight: 1.5 }}>
              {help.pending
                ? <>GFL&apos;s collection has <b>{help.pending}</b> map{help.pending === 1 ? '' : 's'} you do not have, and <b>{map}</b> is most likely among {help.pending === 1 ? 'it' : 'them'}. Open the collection below, press Subscribe, and Steam downloads what is missing.</>
                : <>You have every map that is in GFL&apos;s collection right now, so <b>{map}</b> is not in it yet. GFL adds new maps shortly after putting them in rotation. Until then, join anyway: CS2 asks &quot;Confirm Workshop Download&quot; and fetches that one map. Check this window again later.</>}
              {' '}The mapper&apos;s own page is not what GFL runs, so it is not offered here.
            </div>
          </div>
        )}
        {m && (
          <div className="glass card" style={{ margin: '8px 0', padding: 12 }}>
            <div className="sect">This map only (small download)</div>
            <div className="decal" style={{ textTransform: 'none', letterSpacing: 0, margin: '4px 0 8px' }}>
              {m.wid ? 'Opens the map\'s Steam page. Press Subscribe and Steam downloads it in the background.' : 'The map\'s page is not known, so this opens a workshop search for it.'}
            </div>
            <button className="btn cut amber sm" onClick={openMap}>{m.wid ? 'Open the map page' : 'Search the workshop'}</button>
          </div>
        )}
        {mode === 'assets' && <div className="decal" style={{ margin: '4px 0 10px', textTransform: 'none', letterSpacing: 0, lineHeight: 1.5 }}>{name} uses these Steam workshop items for its models, sounds and skins. Subscribe so the server looks and sounds right; they are small next to a map collection.</div>}
        <div className="sect" style={{ margin: '12px 0 4px' }}>{mode === 'assets' ? 'Server asset packs' : m ? 'Or the whole server collection' : help?.reupload ? 'GFL map collection' : 'Steam collections of this server'}</div>
        {!help && <div className="decal" style={{ padding: 10 }}>Checking the collections...</div>}
        {help && help.collections.length === 0 && <div className="decal" style={{ padding: 10 }}>No collection is known for this server yet.</div>}
        {help?.collections.map((c) => {
          const sz = sizes[c.id];
          return (
            <div key={c.id} className="glass card" style={{ margin: '6px 0', padding: 12, display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap', borderColor: c.match ? 'var(--amber)' : undefined }}>
              <div style={{ flex: 1, minWidth: 220 }}>
                <b>{c.label}</b> <span className="decal">{KIND[c.kind] ?? c.kind}{c.match ? ' · matches this map' : ''}</span>
                <div className="decal" style={{ textTransform: 'none', letterSpacing: 0, marginTop: 4, lineHeight: 1.5 }}>
                  {c.kind === 'item' ? (c.installed ? 'You have this pack.' : 'You do not have this pack yet.') : c.known ? `You have ${c.installed} of ${c.total} items.` : 'Item list not available right now.'}
                  {sz
                    ? sz.missing === 0 ? ' Nothing left to download.'
                      : sz.bytes ? ` Subscribing downloads about ${fmtGb(sz.bytes)}${sz.unknown ? ` (plus ${sz.unknown} items whose size Steam does not show)` : ''}.`
                      : ` Steam does not show the size of the ${sz.unknown} items you are missing.`
                    : c.known ? ' Working out the download size...' : ''}
                </div>
              </div>
              <button className="btn cut ghost sm" onClick={() => openCol(c.id)}>{c.kind === 'item' ? 'Open pack page' : 'Open collection page'}</button>
            </div>
          );
        })}
        {mode === 'maps' && !help?.reupload && <div className="decal" style={{ margin: '10px 0 0', textTransform: 'none', letterSpacing: 0, lineHeight: 1.5 }}>
          A whole collection can be tens of GB, so only subscribe to what you play. Some current maps are not in the collection yet; for those use the single map above.
        </div>}
        <div className="btns" style={{ justifyContent: 'flex-end' }}>
          <button className="btn cut ghost" onClick={() => { sfx.click(); onClose(); }}>Close</button>
        </div>
      </motion.div>
    </motion.div>,
    document.body,
  );
}
