import { memo } from 'react';
import { sfx } from '../sound';
import type { GeoRow } from '../types';

const COLS = ['--c1', '--c2', '--c3', '--c4', '--c5', '--c6'];

/** Geo radar line: an estimate, chosen per server (Country or Region). */
function GeoImpl({ countries, regions, mode, onMode, humans, max = 4 }: {
  countries: GeoRow[]; regions: GeoRow[]; mode: 'country' | 'region'; onMode: (m: 'country' | 'region') => void; humans: number; max?: number;
}) {
  if (!humans || !countries.length) {
    return <div className="geo"><div className="top"><span className="decal">&#9678; Geo radar</span><span className="decal">idle · {humans || 0} players</span></div></div>;
  }
  const rows = mode === 'region' ? regions : countries;
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
      <div className="pl">
        {rows.slice(0, max).map((r, i) => <span key={r.code}><i style={{ background: `var(${COLS[Math.min(i, 5)]})` }} />{r.code} {r.pct}%</span>)}
        {rows.length > max && <span className="decal" title={rows.slice(max).map((r) => `${r.name} ${r.pct}%`).join('\n')}>+{rows.length - max} more</span>}
      </div>
    </div>
  );
}
export const Geo = memo(GeoImpl);
