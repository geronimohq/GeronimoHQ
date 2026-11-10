import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { motion } from 'framer-motion';
import { api } from '../api';
import { sfx } from '../sound';
import type { Track } from '../types';

/** Songs registered for the current map in the ZE Graph database, with one-click YouTube links. */
export default function SoundtrackDialog({ map, onClose, log }: { map: string; onClose: () => void; log: (tag: string, msg: string) => void }) {
  const [tracks, setTracks] = useState<Track[] | null>(null);
  const [sel, setSel] = useState<number | null>(null);
  useEffect(() => {
    void api.soundtrack(map).then((r) => setTracks(r.tracks));
    const k = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', k);
    return () => window.removeEventListener('keydown', k);
  }, [map, onClose]);
  const listen = (t: Track) => { sfx.click(); void (t.url ? api.openUrl(t.url) : api.openYoutube(t.name)); };
  const copy = (t: Track) => { sfx.toggle(); try { void navigator.clipboard.writeText(t.name); } catch { /* ignore */ } log('SYSTEM', `Copied track title: ${t.name}`); };
  const cur = sel != null && tracks ? tracks[sel] : null;
  return createPortal(
    <motion.div className="scrim on" role="dialog" aria-modal="true" aria-labelledby="stTitle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <motion.div className="cut modal brk mc" style={{ width: 'min(720px,100%)' }} initial={{ scale: 0.96, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.96, opacity: 0 }}>
        <div className="decal">Map soundtrack intel</div><h3 id="stTitle">Soundtrack: {map || 'unknown map'}</h3>
        <div className="decal" style={{ margin: '6px 0 10px', textTransform: 'none', letterSpacing: 0 }}>Live soundtrack intel registered in the ZE Graph database. Double-click a track or use Listen on YouTube.</div>
        <div className="mctable" style={{ maxHeight: '46vh' }}>
          <table><thead><tr><th>Track / song title</th><th>Duration</th><th>Stage / trigger tags</th></tr></thead>
            <tbody>
              {tracks === null && <tr><td colSpan={3} className="decal" style={{ padding: 18 }}>Fetching soundtrack intel from ZE Graph...</td></tr>}
              {tracks?.length === 0 && <tr><td colSpan={3} className="decal" style={{ padding: 18 }}>No soundtrack configuration registered for '{map}'.</td></tr>}
              {tracks?.map((t, i) => <tr key={i} onClick={() => { sfx.click(); setSel(i); }} onDoubleClick={() => listen(t)} style={{ cursor: 'pointer', background: sel === i ? 'rgba(255,158,27,.14)' : undefined }}><td>{t.name}</td><td className="mono">{t.duration}</td><td className="mono" style={{ color: 'var(--tx2)' }}>{t.tags.join(', ')}</td></tr>)}
            </tbody></table>
        </div>
        <div className="btns" style={{ justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn cut ghost" disabled={!cur} onClick={() => cur && listen(cur)}>Listen on YouTube</button>
            <button className="btn cut ghost" disabled={!cur} onClick={() => cur && copy(cur)}>Copy title</button>
          </div>
          <button className="btn cut ghost" onClick={() => { sfx.click(); onClose(); }}>Close</button>
        </div>
      </motion.div>
    </motion.div>,
    document.body,
  );
}
