import { memo, useLayoutEffect, useRef, useState } from 'react';
import { sfx } from '../sound';
import type { GeoRow } from '../types';

const COLS = ['--c1', '--c2', '--c3', '--c4', '--c5', '--c6'];

/** Geo radar line: an estimate, chosen per server (Country or Region). */
function GeoImpl({ countries, regions, mode, onMode, humans }: {
  countries: GeoRow[]; regions: GeoRow[]; mode: 'country' | 'region'; onMode: (m: 'country' | 'region') => void; humans: number;
}) {
  const rows = mode === 'region' ? regions : countries;
  const box = useRef<HTMLDivElement>(null), mirror = useRef<HTMLDivElement>(null);
  const [shown, setShown] = useState(rows.length);
  // fit as many pills as the width allows in at most two lines, then "+N more"
  useLayoutEffect(() => {
    const calc = () => {
      const b = box.current, m = mirror.current;
      if (!b || !m) return;
      const W = b.clientWidth, gap = 6, MORE = 78;
      const w = [...m.children].map((c) => (c as HTMLElement).offsetWidth);
      const lines = (k: number, extra: number) => { let n = 1, x = 0; for (let i = 0; i < k + (extra ? 1 : 0); i++) { const iw = i < k ? w[i] : extra; if (x && x + gap + iw > W) { n++; x = iw; } else x = x ? x + gap + iw : iw; } return n; };
      let k = w.length;
      if (lines(k, 0) > 2) { k = Math.max(1, k - 1); while (k > 1 && lines(k, MORE) > 2) k--; }
      setShown(k);
    };
    calc();
    const ro = new ResizeObserver(calc);
    if (box.current) ro.observe(box.current);
    return () => ro.disconnect();
  }, [rows]);
  if (!humans || !countries.length) {
    return <div className="geo"><div className="top"><span className="decal">&#9678; Geo radar</span><span className="decal">idle · {humans || 0} players</span></div></div>;
  }
  const tip = `${mode === 'region' ? 'By region' : 'By country'} (estimate)\n` +
    rows.map((r) => `${r.name}: ${r.pct}% (~${r.count} players)`).join('\n') +
    '\nBased on name signals and time-of-day activity. No player is identified.';
  return (
    <div className="geo" title={tip}>
      <div className="top">
        <span className="decal">&#9678; Geo radar · estimate</span>
        <span className="mini">
          {(['country', 'region'] as const).map((m) => (
            <button key={m} aria-pressed={mode === m} onClick={() => { sfx.click(); onMode(m); }}>{m === 'country' ? 'Country' : 'Region'}</button>
          ))}
        </span>
      </div>
      <div className="bar2">{rows.map((r, i) => <i key={r.code} style={{ width: `${r.pct}%`, background: `var(${COLS[Math.min(i, 5)]})` }} />)}</div>
      <div className="pl" ref={box}>
        {rows.slice(0, shown).map((r, i) => <span key={r.code}><i style={{ background: `var(${COLS[Math.min(i, 5)]})` }} />{r.code} {r.pct}%</span>)}
        {rows.length > shown && <span className="decal" title={rows.slice(shown).map((r) => `${r.name} ${r.pct}%`).join('\n')}>+{rows.length - shown} more</span>}
      </div>
      <div className="pl plmirror" ref={mirror} aria-hidden="true">{rows.map((r, i) => <span key={r.code}><i style={{ background: `var(${COLS[Math.min(i, 5)]})` }} />{r.code} {r.pct}%</span>)}</div>
    </div>
  );
}
export const Geo = memo(GeoImpl);
