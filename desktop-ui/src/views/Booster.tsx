import { useEffect, useState } from 'react';
import { api, on } from '../api';
import { sfx } from '../sound';
import { Info } from '../components/Info';
import { useAdminPrompt, useModal } from '../components/Modal';
import PAGES from '../data/pages.json';
import type { AnalyzerResult, DnsResult, DnsState } from '../types';

const B = PAGES.boost;

export default function Booster() {
  const [running, setRunning] = useState<boolean | null>(null);
  const [dns, setDns] = useState<DnsState | null>(null);
  const [res, setRes] = useState<DnsResult[]>([]);
  const [bench, setBench] = useState(false);
  const [sel, setSel] = useState<string | null>(null);
  const [p1, setP1] = useState('1.1.1.1'), [p2, setP2] = useState('1.0.0.1');
  const [an, setAn] = useState<AnalyzerResult | null>(null);
  const [boostMsg, setBoostMsg] = useState('Ready to boost');
  const openModal = useModal();
  const adminPrompt = useAdminPrompt();
  const loadDns = () => { void api.dnsState().then(setDns); };
  useEffect(() => {
    void api.cs2Running().then(setRunning);
    loadDns();
    const off1 = on<DnsResult[]>('dns_results', (r) => setRes(r));
    const off2 = on<{ name: string }>('job', (j) => { if (j.name === 'dns_benchmark') setBench(false); });
    return () => { off1(); off2(); };
  }, []);

  const boost = async () => {
    sfx.click();
    const r = await api.boost();
    setBoostMsg(r.msg);
    openModal({ kind: r.ok ? 'ok' : 'warn', label: 'Live CPU priority boost', title: r.ok ? 'Boost applied' : 'Not applied', body: r.msg });
    void api.cs2Running().then(setRunning);
  };
  const runBench = async () => {
    sfx.click(); setBench(true); setRes([]);
    const r = await api.dnsBenchmark();
    if (!r.ok) { setBench(false); openModal({ kind: 'warn', label: 'Problem', title: 'Not started', body: r.error }); }
  };
  const done = (x: { ok: boolean; error?: string }, title: string) => {
    if (!x.ok && /administrator/i.test(x.error ?? '')) { adminPrompt('Changing DNS', 'booster'); loadDns(); return; }
    openModal(x.ok ? { kind: 'ok', label: 'Notification', title } : { kind: 'warn', label: 'Problem', title: 'DNS not changed', body: x.error ?? 'See the log.' });
    loadDns();
  };
  const applyInner = (name: string, primary: string, secondary: string) => dns && !dns.admin ? adminPrompt(`Use ${name}`, 'booster') : openModal({
    kind: 'q', label: 'Confirm', title: `Use ${name}?`, body: `Sets DNS ${primary} / ${secondary} on your active network adapter. Undo any time with Restore ISP default.`,
    confirm: { text: 'Apply DNS', run: async () => done(await api.dnsApply(primary, secondary, name), 'DNS updated') },
  });
  const alreadyOn = (name: string) => openModal({ kind: 'ok', label: 'Notification', title: `${name} is already active`, body: 'Your network adapter already uses this DNS, so nothing was changed.' });
  const apply = (name: string, primary: string, secondary: string) => (dns?.current ?? '').includes(primary) ? alreadyOn(name) : applyInner(name, primary, secondary);
  const restore = () => dns && !dns.admin ? adminPrompt('Restore ISP default DNS', 'booster') : openModal({
    kind: 'q', label: 'Confirm', title: 'Restore ISP default DNS?', body: 'Switches the adapter back to automatic (DHCP) and flushes the DNS cache.',
    confirm: { text: 'Restore', run: async () => done(await api.dnsRestore(), 'DNS restored to automatic') },
  });
  const customInner = () => dns && !dns.admin ? adminPrompt('Apply custom DNS', 'booster') : openModal({
    kind: 'q', label: 'Confirm', title: 'Apply custom DNS?', body: `Sets DNS ${p1} / ${p2 || '(none)'} on your active network adapter.`,
    confirm: { text: 'Apply custom DNS', run: async () => done(await api.dnsCustom(p1, p2), 'Custom DNS applied') },
  });
  const custom = () => p1.trim() && (dns?.current ?? '').includes(p1.trim()) ? alreadyOn('Custom DNS') : customInner();
  const analyze = async () => {
    sfx.click();
    const r = await api.logAnalyze();
    setAn(r);
    if (!r.found) openModal({ kind: 'warn', label: 'CS2 session log analyzer', title: 'console.log not found', body: r.condebug ? r.message : `${r.message}\n\nTip: add -condebug in the Launch Options tab to enable passive session logging.` });
  };

  const rows = res.length ? res : (dns?.providers ?? []).map((p, i) => ({ name: p.name, primary: p.primary, secondary: p.secondary, avg_ms: 0, jitter_ms: 0, reachable: true, fastest: false, rank: i + 1, idle: true, desc: p.desc }));
  const descOf = (n: string) => dns?.providers.find((p) => p.name === n)?.desc ?? '';

  return (
    <section className="view on">
      <div className="vhead"><div><div className="decal">// 06 · network &amp; priority</div><h1>Live CS2 process priority &amp; gaming DNS optimizer</h1><p>{B.sub}</p></div></div>

      <div className="glass card brk">
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}><span className="sect">{B.title}</span><span className="tag">{B.badge}</span></div>
        <div className="ptext" style={{ margin: '8px 0 12px' }}>{B.desc}</div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <button className="btn cut amber pri" title={B.boost_tip} onClick={() => void boost()}>Apply safe CS2 CPU priority boost</button>
          <span className="mono" style={{ fontSize: 12, color: 'var(--tx2)' }}>Status: {boostMsg} · {running === null ? '...' : running ? 'CS2 is running' : 'CS2 is not running'}</span>
        </div>
      </div>

      <div className="glass card">
        <div className="sect">Gaming DNS optimizer &amp; real-time latency benchmark</div>
        <div className="mono" style={{ fontSize: 12, color: 'var(--cyan)', margin: '6px 0' }}>Adapter: {dns?.interface ?? 'Detecting...'} &nbsp;|&nbsp; Active DNS: {dns?.current ?? 'Checking...'}</div>
        <div className="ptext" style={{ marginBottom: 10 }}>{B.dns_help}</div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 6 }}>
          <button className="btn cut ghost sm" title={B.bench_tip} disabled={bench} onClick={() => void runBench()}>{bench ? 'Benchmarking…' : 'Benchmark all DNS servers'}</button>
          <button className="btn cut ghost sm" title={B.restore_tip} onClick={() => { sfx.click(); restore(); }}>Restore ISP default (DHCP)</button>
        </div>
        {dns && !dns.admin && <div className="decal" style={{ marginBottom: 6, textTransform: 'none', letterSpacing: 0 }}>Benchmarks work as a standard user. Applying a DNS needs Administrator: the app offers to restart as Administrator and come back to this tab.</div>}
        {rows.map((r) => (
          <div className={`row dnsrow${sel === r.name ? ' sel' : ''}`} key={r.name} onClick={() => { sfx.click(); setSel(r.name); }}>
            <div className="grow"><div className="t">{r.name}{r.fastest && <span className="tag" style={{ marginLeft: 8 }}>FASTEST</span>}</div>
              <div className="d mono" style={{ fontSize: 12 }}>{r.primary} / {r.secondary}</div><div className="d" style={{ fontSize: 12 }}>{descOf(r.name)}</div></div>
            {'idle' in r ? <span className="decal">click row to select</span> : <><span className="cell cy">{r.reachable ? `${r.avg_ms} ms` : 'unreachable'}</span><span className="cell">jitter {r.jitter_ms} ms</span></>}
            <button className="btn cut ghost sm" onClick={(e) => { e.stopPropagation(); sfx.click(); apply(r.name, r.primary, r.secondary); }}>Use this DNS</button>
          </div>
        ))}
        <div className="sect" style={{ margin: '14px 0 6px' }}>Custom DNS IPv4 (any provider)</div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div className="field" style={{ margin: 0 }}><label htmlFor="d1">Primary</label><input id="d1" value={p1} onChange={(e) => setP1(e.target.value)} style={{ width: 150 }} /></div>
          <div className="field" style={{ margin: 0 }}><label htmlFor="d2">Secondary</label><input id="d2" value={p2} onChange={(e) => setP2(e.target.value)} style={{ width: 150 }} /></div>
          <button className="btn cut ghost sm" onClick={() => { sfx.click(); custom(); }}>Apply custom DNS</button>
        </div>
      </div>

      <div className="glass card">
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}><span className="sect" style={{ color: 'var(--cyan)' }}>{B.analyzer_title}</span><span className="tag">{B.analyzer_badge}</span></div>
        <div className="ptext" style={{ margin: '8px 0 12px' }}>{B.analyzer_desc}</div>
        <button className="btn cut ghost sm" title={B.analyzer_tip} onClick={() => void analyze()}>Analyze CS2 session telemetry log</button>
        <div className="mono" style={{ fontSize: 12, marginTop: 10, color: 'var(--tx2)' }}>
          {!an ? "Click 'Analyze CS2 session telemetry log' to inspect your latest session." : !an.found ? (an.condebug ? '-condebug is set; restart CS2 once and play a session so console.log is created.' : 'console.log not found. Add -condebug in the Launch Options tab.')
            : `Size: ${an.file_size_mb} MB | Frame hitches: ${an.frame_hitch_events} | Shader stalls: ${an.shader_compile_events} | Net jitter: ${an.net_jitter_events} | VPKs loaded: ${an.vpk_load_events} | Last map: ${an.last_map}`}
        </div>
        {an?.found && <div className="ptext" style={{ marginTop: 8 }}>{an.recommendation}</div>}
      </div>

      <div className="decal" style={{ padding: '2px 4px' }}>Guide: what DNS changes, pros and cons, and how to undo it</div>
      <Info title={B.guide_all_title} text={B.guide_all} open={false} />
      <Info title={B.guide_pros_title} text={B.guide_pros} open={false} tone="var(--ok)" />
      <Info title={B.guide_cons_title} text={B.guide_cons} open={false} tone="var(--cyan)" />
      <Info title={B.guide_ram_title} text={B.guide_ram} open={false} />
    </section>
  );
}
