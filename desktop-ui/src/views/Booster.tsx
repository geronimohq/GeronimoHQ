import { useEffect, useState } from 'react';
import { api, on } from '../api';
import { sfx } from '../sound';
import { useModal } from '../components/Modal';
import type { DnsResult, DnsState } from '../types';

export default function Booster() {
  const [running, setRunning] = useState<boolean | null>(null);
  const [dns, setDns] = useState<DnsState | null>(null);
  const [res, setRes] = useState<DnsResult[]>([]);
  const [bench, setBench] = useState(false);
  const openModal = useModal();
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
    openModal({ kind: r.ok ? 'ok' : 'warn', label: 'Live CPU priority boost', title: r.ok ? 'Boost applied' : 'Not applied', body: r.msg });
    void api.cs2Running().then(setRunning);
  };
  const runBench = async () => {
    sfx.click(); setBench(true); setRes([]);
    const r = await api.dnsBenchmark();
    if (!r.ok) { setBench(false); openModal({ kind: 'warn', label: 'Problem', title: 'Not started', body: r.error }); }
  };
  const apply = (r: DnsResult) => openModal({
    kind: 'q', label: 'Confirm', title: `Use ${r.name}?`, body: `Sets DNS ${r.primary} / ${r.secondary} on your active network adapter. Undo any time with Restore ISP default.`,
    confirm: { text: 'Apply DNS', run: async () => {
      const x = await api.dnsApply(r.primary, r.secondary, r.name);
      openModal(x.ok ? { kind: 'ok', label: 'Notification', title: 'DNS updated' } : { kind: 'warn', label: 'Problem', title: 'DNS not changed', body: x.error ?? 'See the log.' });
      loadDns();
    } },
  });
  const restore = () => openModal({
    kind: 'q', label: 'Confirm', title: 'Restore ISP default DNS?', body: 'Switches the adapter back to automatic (DHCP).',
    confirm: { text: 'Restore', run: async () => {
      const x = await api.dnsRestore();
      openModal(x.ok ? { kind: 'ok', label: 'Notification', title: 'DNS restored to automatic' } : { kind: 'warn', label: 'Problem', title: 'DNS not changed', body: x.error ?? 'See the log.' });
      loadDns();
    } },
  });

  return (
    <section className="view on">
      <div className="vhead"><div><div className="decal">// 06 · network &amp; priority</div><h1>Live booster &amp; DNS</h1><p>Raise CS2's CPU priority while you play and pick the fastest gaming DNS.</p></div></div>
      <div className="glass card brk" style={{ display: 'flex', gap: 14, alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 240 }}><div className="sect">Live CPU priority boost</div>
          <div className="d" style={{ color: 'var(--tx2)', marginTop: 4 }}>Sets cs2.exe to High priority. It resets when CS2 closes. Status: <b style={{ color: running ? 'var(--ok)' : 'var(--tx3)' }}>{running === null ? '...' : running ? 'CS2 is running' : 'CS2 is not running'}</b></div></div>
        <button className="btn cut amber pri" onClick={() => void boost()}>Apply safe CS2 CPU priority boost</button>
      </div>
      <div className="glass card">
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap', marginBottom: 6 }}>
          <div style={{ flex: 1, minWidth: 220 }}><div className="sect">Gaming DNS benchmark</div><div className="d" style={{ color: 'var(--tx2)' }}>Adapter: {dns?.interface ?? '...'} · now: {dns?.current ?? '...'}</div></div>
          <button className="btn cut ghost sm" disabled={bench} onClick={() => void runBench()}>{bench ? 'Benchmarking\u2026' : 'Run benchmark'}</button>
          <button className="btn cut ghost sm" onClick={() => { sfx.click(); restore(); }}>Restore ISP default</button>
        </div>
        {dns && !dns.admin && <div className="decal" style={{ marginBottom: 6 }}>Benchmarks work as a standard user. Applying a DNS needs Administrator.</div>}
        {(res.length ? res : (dns?.providers ?? []).map((p, i) => ({ name: p.name, primary: p.primary, secondary: p.secondary, avg_ms: 0, jitter_ms: 0, reachable: true, fastest: false, rank: i + 1, idle: true }))).map((r) => (
          <div className="row" key={r.name}>
            <div className="grow"><div className="t">{r.name}{r.fastest && <span className="tag" style={{ marginLeft: 8 }}>FASTEST</span>}</div><div className="d mono" style={{ fontSize: 12 }}>{r.primary} / {r.secondary}</div></div>
            {'idle' in r ? <span className="decal">not measured</span> : <><span className="cell cy">{r.reachable ? `${r.avg_ms} ms` : 'unreachable'}</span><span className="cell">jitter {r.jitter_ms} ms</span></>}
            <button className="btn cut ghost sm" onClick={() => { sfx.click(); apply(r as DnsResult); }}>Use this DNS</button>
          </div>
        ))}
      </div>
    </section>
  );
}
