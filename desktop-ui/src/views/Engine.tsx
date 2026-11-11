import { useEffect, useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { api } from '../api';
import { sfx } from '../sound';
import { Info, WeeklyBanner } from '../components/Info';
import PAGES from '../data/pages.json';
import type { EngineState } from '../types';

export const TWEAKS = [
  { key: 'shaders', group: 'engine', title: 'Optimize shader pre-caching & purge caches', desc: 'Removes fragmented GPU/DirectX shaders. Recommended after game patches to eliminate micro-stutters.' },
  { key: 'autoexec', group: 'engine', title: 'Append low-latency engine autoexec config', desc: 'Appends safe Source 2 rate, telemetry and audio latency tweaks (snd_mixahead 0.025) while preserving custom binds.' },
  { key: 'dumps', group: 'win', title: 'Clean CS2 crash dumps & temp files', desc: 'Removes old crash dumps (.dmp) and crash reports from the CS2 folders. It never deletes console.log.' },
  { key: 'gamedvr', group: 'win', title: 'Disable Windows Game DVR background capture', desc: 'Stops Windows Xbox background frame capture, cutting DWM latency and background GPU load.' },
  { key: 'fullscreen', group: 'win', title: 'Disable fullscreen optimizations (Direct-Flip)', desc: 'Forces exclusive display presentation for cs2.exe, bypassing Windows desktop compositor lag.' },
] as const;

export type Opts = Record<(typeof TWEAKS)[number]['key'], boolean>;
export const ALL_ON: Opts = { shaders: true, autoexec: true, dumps: true, gamedvr: true, fullscreen: true };

function Switch({ on, label, onChange }: { on: boolean; label: string; onChange: (v: boolean) => void }) {
  return <button className="sw" role="switch" aria-checked={on} aria-label={label} onClick={() => { sfx.toggle(); onChange(!on); }} />;
}

function Group({ id, title, children, count }: { id: string; title: string; children: React.ReactNode; count: number }) {
  const [shut, setShut] = useState(false);
  return (
    <div className={`glass card acc${shut ? ' shut' : ''}`} id={id}>
      <button onClick={() => { sfx.click(); setShut(!shut); }} aria-expanded={!shut}>
        <span className="sect">{title}</span><span className="count">{count} tweaks</span><span className="chev"><ChevronDown size={16} /></span>
      </button>
      <div className="accbody">{children}</div>
    </div>
  );
}

export default function Engine({ opts, setOpts, onApplied, log, power, setPower, daysOpt, daysMaint, go }: {
  opts: Opts; setOpts: (o: Opts) => void; onApplied: () => void; log: (tag: string, msg: string) => void;
  power: { on: boolean; plan: 'balanced' | 'high' }; setPower: (p: { on: boolean; plan: 'balanced' | 'high' }) => void;
  daysOpt: number | null | undefined; daysMaint: number | null | undefined; go: (id: 'engine' | 'maintenance') => void;
}) {
  const [state, setState] = useState<EngineState | null>(null);
  const plan = power.plan;
  const setPlan = (p: 'balanced' | 'high') => setPower({ ...power, plan: p });
  const [ddOpen, setDdOpen] = useState(false);
  const [applied, setApplied] = useState(false);
  useEffect(() => { void api.engineState().then((s) => { setState(s); }); }, []);
  useEffect(() => { if (!ddOpen) return; const c = () => setDdOpen(false); window.addEventListener('click', c); return () => window.removeEventListener('click', c); }, [ddOpen]);
  const enabled = Object.values(opts).filter(Boolean).length;
  const planName = plan === 'balanced' ? 'Balanced' : 'High performance';

  return (
    <section className="view on">
      <div className="vhead">
        <div><div className="decal">// 02 · system tuning</div><h1>Engine performance tweaks</h1><p>Each change has an undo: Restore Defaults, the autoexec backup, or the Restore ISP Default (DHCP) button.</p></div>
        <span className="pill"><i className="dot" /><span>{enabled} of {TWEAKS.length} selected</span></span>
      </div>
      <WeeklyBanner daysOpt={daysOpt} daysMaint={daysMaint} go={go} actions={daysOpt == null || daysOpt > 7 ? [{ label: '1-Click Optimize', run: onApplied }] : []} />
      <Info title={PAGES.engine.note_title.replace(/^[^A-Za-z]*/, '')} text={PAGES.engine.note} open={false} tone="var(--cyan)" />
      {state && !state.cs2_found && <div className="glass card" role="alert" style={{ borderColor: 'rgba(239,68,68,.45)' }}>CS2 was not found, so the autoexec, fullscreen and dump tweaks are skipped. Shader cleaning and Game DVR still work.</div>}
      {state?.autoexec && <div className="decal" style={{ padding: '0 4px' }}>{state.autoexec.text}</div>}
      {(['engine', 'win'] as const).map((g) => (
        <Group key={g} id={`acc-${g}`} title={g === 'engine' ? 'CS2 engine' : 'Windows'} count={TWEAKS.filter((t) => t.group === g).length}>
          {TWEAKS.filter((t) => t.group === g).map((t) => (
            <div className="row" key={t.key}>
              <div className="grow"><div className="t">{t.title}</div><div className="d">{t.desc}</div></div>
              <span className="mono" style={{ fontSize: 11, color: opts[t.key] ? 'var(--ok)' : 'var(--tx3)' }}>{opts[t.key] ? 'SELECTED' : 'OFF'}</span>
              <Switch on={opts[t.key]} label={t.title} onChange={(v) => setOpts({ ...opts, [t.key]: v })} />
            </div>
          ))}
        </Group>
      ))}
      <div className="glass card brk">
        <div className="row" style={{ border: 0, padding: '4px 6px' }}>
          <div className="grow"><div className="t">Windows CPU power scheme</div><div className="d">Recommended for your CPU: {power.plan === 'balanced' ? 'Balanced' : 'High performance'} | Active: {state?.power_plan ?? '…'}. {PAGES.engine.power_tip}</div></div>
          <label className="chk" title={PAGES.engine.power_check_tip}><input type="checkbox" checked={power.on} onChange={() => { sfx.toggle(); setPower({ ...power, on: !power.on }); }} />Include in one-click</label>
          <span className={`applied${applied ? ' on' : ''}`}>&#10003; Applied</span>
          <div className={`dd${ddOpen ? ' open' : ''}`}>
            <button aria-haspopup="listbox" aria-expanded={ddOpen} onClick={(e) => { e.stopPropagation(); sfx.click(); setDdOpen(!ddOpen); }}><span>{planName}</span><ChevronDown size={14} /></button>
            <ul role="listbox">
              {([['balanced', 'Balanced'], ['high', 'High performance']] as const).map(([k, l]) => (
                <li key={k} role="option" aria-selected={plan === k} onClick={() => { sfx.click(); setPlan(k); setApplied(false); setDdOpen(false); }}>{l}</li>
              ))}
            </ul>
          </div>
          <button className="btn cut sm ghost" onClick={async () => { const r = await api.powerSet(plan); if (r.ok) { setApplied(true); sfx.toggle(); log('ENGINE', `CPU power scheme set to ${planName}`); void api.engineState().then(setState); } }}>Apply</button>
        </div>
      </div>
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
        <button className="btn cut ghost" onClick={() => { sfx.click(); onApplied(); }}>&#9889; Apply selected tweaks</button>
      </div>
    </section>
  );
}
