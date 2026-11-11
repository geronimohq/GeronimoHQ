import { useState, type ReactNode } from 'react';
import { ChevronDown } from 'lucide-react';
import { sfx } from '../sound';

/** Glass help card with a title, an optional badge and long text (kept as the classic app wrote it). Collapsible. */
export function Info({ title, badge, text, children, open = true, tone = 'var(--amber)' }: { title: string; badge?: string; text?: string; children?: ReactNode; open?: boolean; tone?: string }) {
  const [on, setOn] = useState(open);
  return (
    <div className="glass card info">
      <button className="infohead" onClick={() => { sfx.click(); setOn(!on); }} aria-expanded={on}>
        <span className="sect" style={{ color: tone, flex: 1, textAlign: 'left' }}>{title}</span>
        {badge && <span className="tag">{badge}</span>}
        <ChevronDown size={15} style={{ transform: on ? 'none' : 'rotate(-90deg)', transition: '.2s', color: 'var(--tx3)' }} />
      </button>
      {on && <div className="infobody">{text && <div className="ptext">{text}</div>}{children}</div>}
    </div>
  );
}

/** Reminder banner shown on Engine Tweaks and PC Maintenance (same rules as the classic app: 7 days). */
export function WeeklyBanner({ daysOpt, daysMaint, go, actions }: { daysOpt: number | null | undefined; daysMaint: number | null | undefined; go: (id: 'engine' | 'maintenance') => void; actions?: { label: string; run: () => void }[] }) {
  const age = (d: number | null | undefined) => (d == null || d >= 999 ? 'not yet run' : d === 0 ? 'today' : `${d}d ago`);
  const optOld = daysOpt == null || daysOpt > 7, mOld = daysMaint == null || daysMaint > 7;
  const both = optOld && mOld;
  const bad = optOld || mOld;
  const title = !bad ? 'System & CS2 health up-to-date' : both ? 'Weekly PC & CS2 hygiene overdue: both tasks need attention' : mOld ? 'PC maintenance overdue' : 'CS2 engine optimization due';
  const body = !bad
    ? `CS2 engine tweaks: optimized ${age(daysOpt)} \u2022 PC maintenance: clean ${age(daysMaint)} (recommended: every 7 days)`
    : both ? `CS2 engine tweaks (${age(daysOpt)}) and PC maintenance (${age(daysMaint)}) have not been run recently. Stale shader caches and accumulated temporary files degrade frame pacing.`
    : mOld ? `CS2 engine tweaks are up-to-date (${age(daysOpt)}), but PC maintenance is overdue (${age(daysMaint)}). Running SSD TRIM and cache cleanups prevents micro-stutters and frees disk space.`
    : `PC maintenance is clean (${age(daysMaint)}), but CS2 engine tweaks are overdue (${age(daysOpt)}). Purging DirectX/GPU shaders and refreshing autoexec ensures smooth 1% lows.`;
  return (
    <div className="glass card" role="status" style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap', borderColor: bad ? 'rgba(255,158,27,.45)' : 'rgba(16,185,129,.4)' }}>
      <span style={{ color: bad ? 'var(--amber)' : 'var(--ok)', fontSize: 18 }}>{bad ? '\u26A0' : '\u2713'}</span>
      <div style={{ flex: 1, minWidth: 240 }}><div className="t">{title}</div><div className="d" style={{ color: 'var(--tx2)' }}>{body}</div></div>
      <button className="btn cut ghost sm" onClick={() => { sfx.click(); go(optOld ? 'engine' : 'maintenance'); }}>{optOld ? 'Open engine tweaks' : 'Open PC maintenance'}</button>
      {(actions ?? []).map((a) => <button key={a.label} className="btn cut ghost sm" onClick={() => { sfx.click(); a.run(); }}>{a.label}</button>)}
      {!optOld && !mOld ? null : (optOld && mOld) ? <button className="btn cut ghost sm" onClick={() => { sfx.click(); go('maintenance'); }}>Open PC maintenance</button> : null}
    </div>
  );
}
