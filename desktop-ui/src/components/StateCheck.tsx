import { useCallback, useEffect, useState } from 'react';
import { api, on } from '../api';
import { sfx } from '../sound';
import type { CheckRow } from '../types';

const COLOR: Record<string, string> = { ok: 'var(--ok)', off: 'var(--amber)', info: 'var(--cyan)', na: 'var(--tx3)' };

/**
 * Live status of the Engine Tweaks / PC Maintenance items, read from this PC (read-only: registry values, autoexec.cfg, folder sizes,
 * Recycle Bin, power plan). Loaded when the page opens and again after every apply or clean-up finishes, so the line under each item
 * always shows what is really there now.
 */
export function useLiveStatus(page: 'engine' | 'maintenance') {
  const [rows, setRows] = useState<Record<string, CheckRow>>({});
  const [at, setAt] = useState<string>('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const refresh = useCallback(async () => {
    setBusy(true);
    try {
      const r = await api.stateCheck(page);
      if (r.ok && r.rows) {
        setRows(Object.fromEntries(r.rows.map((x) => [x.key, x])));
        setAt(r.at ?? '');
        setError('');
      } else setError(r.error ?? 'The status could not be read.');
    } finally { setBusy(false); }
  }, [page]);
  useEffect(() => {
    void refresh();
    const off = on('job', () => { void refresh(); });          // after one-click optimize, apply, clean-up or restore
    return () => off();
  }, [refresh]);
  return { rows, at, busy, error, refresh };
}

/** "Now: ..." line under an item, with a Details toggle (what is in there, and how to check it in Windows without this app). */
export function StatusLine({ row }: { row?: CheckRow }) {
  const [open, setOpen] = useState(false);
  if (!row) return null;
  return (
    <div style={{ marginTop: 4 }}>
      <div className="mono" style={{ fontSize: 11.5, color: COLOR[row.state] ?? 'var(--tx2)', display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
        <span>Now: {row.value}</span>
        {(row.detail || row.how) && (
          <button className="lnk" style={{ fontSize: 11 }} aria-expanded={open} onClick={(e) => { e.stopPropagation(); sfx.click(); setOpen(!open); }}>{open ? 'Hide details' : 'Details'}</button>
        )}
      </div>
      {open && (
        <div className="d" style={{ color: 'var(--tx2)', fontSize: 12, lineHeight: 1.5, marginTop: 3 }}>
          {row.detail && <div>{row.detail}</div>}
          {row.how && <div>Check it yourself: {row.how}</div>}
        </div>
      )}
    </div>
  );
}

/** One line at the top of a list: when the status was read, and a refresh button. */
export function StatusBar({ at, busy, error, onRefresh, note }: { at: string; busy: boolean; error: string; onRefresh: () => void; note: string }) {
  return (
    <div className="decal" style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap', textTransform: 'none', letterSpacing: 0, margin: '0 0 6px' }}>
      <span style={{ flex: 1, minWidth: 220 }}>
        {error ? <span style={{ color: 'var(--bad)' }}>{error}</span> : busy && !at ? 'Reading the current status from this PC…' : `${note} Read from this PC at ${at ? new Date(at).toLocaleTimeString() : '…'}; it refreshes by itself after every run.`}
      </span>
      <button className="lnk" disabled={busy} onClick={() => { sfx.click(); onRefresh(); }}>{busy ? 'Reading…' : 'Refresh status'}</button>
    </div>
  );
}
