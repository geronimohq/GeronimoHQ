import { useState } from 'react';
import { api } from '../api';
import { sfx } from '../sound';
import type { StateCheck as Result } from '../types';

const MARK: Record<string, { sym: string; color: string; word: string }> = {
  ok: { sym: '\u2713', color: 'var(--ok)', word: 'in place' },
  off: { sym: '\u2022', color: 'var(--amber)', word: 'not applied / can be cleaned' },
  info: { sym: 'i', color: 'var(--cyan)', word: 'information' },
  na: { sym: '\u2013', color: 'var(--tx3)', word: 'cannot be checked here' },
};

/** "Check" panel: reads the real state of this PC (read-only) so the user can see, before and after, what the tweaks or clean-ups changed. */
export default function StateCheck({ page, intro }: { page: 'engine' | 'maintenance'; intro: string }) {
  const [res, setRes] = useState<Result | null>(null);
  const [busy, setBusy] = useState(false);
  const run = async () => {
    sfx.click();
    setBusy(true);
    try { setRes(await api.stateCheck(page)); } finally { setBusy(false); }
  };
  return (
    <div className="glass card">
      <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap', justifyContent: 'space-between' }}>
        <div style={{ flex: 1, minWidth: 240 }}>
          <div className="sect">Check what is applied</div>
          <div className="d" style={{ color: 'var(--tx2)', marginTop: 4 }}>{intro}</div>
        </div>
        <button className="btn cut ghost sm" disabled={busy} onClick={() => void run()}>{busy ? 'Checking\u2026' : res ? 'Check again' : 'Check now'}</button>
      </div>
      {res && !res.ok && <div className="d" style={{ color: 'var(--bad)', marginTop: 8 }}>{res.error}</div>}
      {res?.ok && res.rows && (
        <div style={{ marginTop: 10 }}>
          <div className="decal" style={{ textTransform: 'none', letterSpacing: 0, marginBottom: 6 }}>
            {res.summary} Checked {res.at ? new Date(res.at).toLocaleTimeString() : ''}. Nothing was changed by this check.
          </div>
          {res.rows.map((r) => {
            const m = MARK[r.state] ?? MARK.info;
            return (
              <div className="row" key={r.key} style={{ alignItems: 'flex-start' }}>
                <span className="mono" aria-label={m.word} title={m.word} style={{ color: m.color, width: 18, fontWeight: 700, textAlign: 'center' }}>{m.sym}</span>
                <div className="grow">
                  <div className="t">{r.label}: <span style={{ color: m.color }}>{r.value}</span></div>
                  {r.how && <div className="d" style={{ color: 'var(--tx2)' }}>Check it yourself: {r.how}</div>}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
