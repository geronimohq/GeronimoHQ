import { useCallback, useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { AppWindow, Binary, ChevronDown, Gauge, Globe2, LayoutDashboard, MessageSquare, Minus, Monitor, Rocket, Square, Wifi, Wrench, X, Zap, HelpCircle } from 'lucide-react';
import { api, IN_APP, isNative, on } from './api';
import { sfx } from './sound';
import { ModalHost, useModal, type ModalSpec } from './components/Modal';
import Servers from './views/Servers';
import Engine, { ALL_ON, type Opts } from './views/Engine';
import Dashboard from './views/Dashboard';
import PAGES from './data/pages.json';
import Maintenance from './views/Maintenance';
import Launch from './views/Launch';
import Booster from './views/Booster';
import Autoexec from './views/Autoexec';
import Faq from './views/Faq';
import Mpo from './views/Mpo';
import Discord from './views/Discord';
import Settings from './components/Settings';
import { Reactor } from './components/Reactor';
import { TooltipLayer } from './components/TooltipLayer';
import type { HwInfo } from './types';
import type { AppInfo, LogLine, SniperStatus, ToolResult, UpdateInfo } from './types';
import { resultModal } from './toolText';

const NAV = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'engine', label: 'Engine Tweaks', icon: Zap },
  { id: 'mpo', label: 'GPU MPO Diagnostics', icon: Monitor },
  { id: 'autoexec', label: 'Autoexec & Binds', icon: Binary },
  { id: 'launch', label: 'Launch Options', icon: Rocket },
  { id: 'booster', label: 'Live Booster & DNS', icon: Wifi },
  { id: 'servers', label: 'ZE Game Servers', icon: Globe2 },
  { id: 'maintenance', label: 'PC Maintenance', icon: Wrench },
  { id: 'discord', label: 'Discord Presence', icon: MessageSquare },
  { id: 'faq', label: 'Help & FAQ', icon: HelpCircle },
] as const;
type NavId = (typeof NAV)[number]['id'];
const TAGCLS: Record<string, string> = { SYSTEM: 's', SERVERS: 'm', ENGINE: 'o' };

const EDGES = ['n', 's', 'e', 'w', 'ne', 'nw', 'se', 'sw'] as const;
/** True once the Python bridge is attached (it appears a moment after the page loads). */
function useNative(): boolean {
  const [n, setN] = useState(isNative());
  useEffect(() => {
    // pause the background animation while the window is hidden or minimized
    const set = () => { document.documentElement.classList.toggle('idle', document.hidden); void api.memTrim(document.hidden); };
    set();
    const back = () => { void api.memTrim(false); };      // restored from the taskbar: leave low-memory mode
    document.addEventListener('visibilitychange', set);
    window.addEventListener('focus', back);
    return () => { document.removeEventListener('visibilitychange', set); window.removeEventListener('focus', back); };
  }, []);
  useEffect(() => {
    if (n) return;
    const f = () => setN(isNative());
    window.addEventListener('pywebviewready', f);
    const t = setTimeout(f, IN_APP ? 90000 : 1500);
    return () => { window.removeEventListener('pywebviewready', f); clearTimeout(t); };
  }, [n]);
  return n;
}

function ResizeEdges({ disabled }: { disabled: boolean }) {
  const native = useNative();
  if (!native || disabled) return null;
  return <>{EDGES.map((e) => <div key={e} className={`edge e-${e}`} onMouseDown={(ev) => { if (ev.button === 0) void api.winResize(e); }} />)}</>;
}

function Shell() {
  const [view, setView] = useState<NavId>(() => (NAV.find((n) => n.id === location.hash.slice(1))?.id ?? 'servers'));
  const [info, setInfo] = useState<AppInfo | null>(null);
  const [logs, setLogs] = useState<LogLine[]>([]);
  const [drawer, setDrawer] = useState(false);
  const [opts, setOpts] = useState<Opts>(ALL_ON);
  const [sound, setSound] = useState(sfx.on);
  const [busy, setBusy] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [update, setUpdate] = useState<UpdateInfo | null>(null);
  const [hw, setHw] = useState<HwInfo | null>(null);
  const [power, setPower] = useState<{ on: boolean; plan: 'balanced' | 'high' }>({ on: false, plan: 'balanced' });
  const [days, setDays] = useState<{ opt: number | null; maint: number | null }>({ opt: null, maint: null });
  const [sniper, setSniper] = useState<SniperStatus | null>(null);
  const [maxed, setMaxed] = useState(false);
  const [dnsInfo, setDnsInfo] = useState<{ text: string; state: string } | null>(null);
  const hist = useRef<NavId[]>([]);
  const pos = useRef(-1);
  const openModal = useModal();
  const native = useNative();
  const logEnd = useRef<HTMLDivElement>(null);

  const addLog = useCallback((tag: string, msg: string) => {
    const t = new Date(), p = (n: number) => String(n).padStart(2, '0');
    setLogs((l) => [...l.slice(-399), { t: `${p(t.getHours())}:${p(t.getMinutes())}:${p(t.getSeconds())}`, tag, msg }]);
  }, []);

  useEffect(() => {
    if (!NAV.some((n) => n.id === location.hash.slice(1))) void api.startPage().then((p) => { if (NAV.some((n) => n.id === p)) setView(p as NavId); });
    void api.hw().then((h) => { setHw(h); setPower((p) => ({ ...p, plan: h.recommended_plan })); });
    void api.dashboard().then((d) => setDays({ opt: d.days_opt, maint: d.days_maint }));
    void api.appInfo().then(setInfo);
    void api.logHistory().then((h) => setLogs(h));
    const pollDns = () => { void api.dnsStatus().then(setDnsInfo); };
    pollDns();
    const dnsTimer = setInterval(pollDns, 30000);
    const pollSniper = () => { void api.sniperStatus().then(setSniper); };
    pollSniper();
    const sniperTimer = setInterval(pollSniper, 1500);
    const offS = on<SniperStatus>('sniper', setSniper);
    const offU = on<UpdateInfo>('update', setUpdate);
    const offM = on<boolean>('maximized', setMaxed);
    const off1 = on<LogLine>('log', (l) => setLogs((p) => [...p.slice(-399), l]));
    const off2 = on<{ name: string; ok: boolean; problems?: number; already?: number; changed?: number }>('job', (j) => {
      setBusy(false);
      void api.appInfo().then(setInfo);
      const n = j.problems ?? 0;
      const same = (j.already ?? 0) > 0 && (j.changed ?? 0) === 0;                // every step found nothing to change
      const some = (j.already ?? 0) > 0 && (j.changed ?? 0) > 0 ? ` ${j.already} step${j.already === 1 ? ' was' : 's were'} already set and left as ${j.already === 1 ? 'it was' : 'they were'}.` : '';
      const nothing = (what: string): ModalSpec => ({ kind: 'ok', label: 'No changes', title: 'Nothing to change', body: `${what}\n\nThe log lists each step.` });
      const partial = (title: string, what: string): ModalSpec => ({ kind: 'warn', label: 'Finished with problems', title, body: `${n} step${n === 1 ? '' : 's'} reported an error while ${what}. The activity log marks each one with [ERROR]; the other steps were done.` });
      const TOOLS: Record<string, string> = { maint_trim: 'SSD TRIM', maint_sfc: 'System File Checker', maint_dism: 'DISM repair', maint_winsxs: 'WinSxS clean-up' };
      if (j.name === 'engine_apply') {
        openModal(!j.ok
          ? { kind: 'warn', label: 'Problem', title: 'Optimization stopped', body: 'Something failed. The log lists each step.' }
          : n > 0 ? partial('Optimization finished with problems', 'applying the tweaks')
          : same ? nothing('Everything you selected was already set on this PC, so nothing was changed.')
          : { kind: 'ok', label: 'Notification', title: 'Optimization applied', body: `The selected tweaks are done.${some} Every change has an undo: Restore Defaults brings back your previous settings. The log lists each step.` });
      } else if (j.name === 'maint_run') {
        openModal(!j.ok || n > 0 ? partial('Clean-up finished with problems', 'cleaning')
          : same ? nothing('No files were found in the places you selected, so nothing was cleaned.')
          : { kind: 'ok', label: 'Notification', title: 'Clean-up finished', body: `Each step is listed in the log, with the space it freed.${some}` });
      } else if (j.name === 'engine_restore') {
        openModal(!j.ok || n > 0 ? partial('Restore finished with problems', 'restoring')
          : same ? nothing('Everything was already at its original setting, so nothing was changed. DNS and Steam launch options are never touched by Restore.')
          : { kind: 'ok', label: 'Notification', title: 'Restore finished', body: `Each step is listed in the log. DNS and Steam launch options were not changed.${some}` });
      } else if (TOOLS[j.name] && !j.ok) {                                  // a normal ending shows the tool's own result window (tool_result); this is only the crash case
        openModal({ kind: 'warn', label: 'Problem', title: `${TOOLS[j.name]} did not complete`, body: 'The app hit an unexpected error while running it. The activity log has the details.' });
      }
    });
    const off3 = on<ToolResult>('tool_result', (r) => openModal(resultModal(r)));
    return () => { off1(); off2(); off3(); offS(); offU(); offM(); clearInterval(sniperTimer); clearInterval(dnsTimer); };
  }, [openModal]);

  useEffect(() => { logEnd.current?.scrollIntoView({ block: 'end' }); }, [logs, drawer]);
  useEffect(() => { void api.setLastPage(view); }, [view]);
  useEffect(() => {
    const h = (e: PromiseRejectionEvent) => { addLog('SYSTEM', `[ERROR] ${String(e.reason?.message ?? e.reason)}`); setDrawer(true); };
    window.addEventListener('unhandledrejection', h);
    return () => window.removeEventListener('unhandledrejection', h);
  }, [addLog]);
  useEffect(() => { const h = () => { const n = NAV.find((x) => x.id === location.hash.slice(1)); if (n) setView(n.id); }; window.addEventListener('hashchange', h); return () => window.removeEventListener('hashchange', h); }, []);

  const show = useCallback((id: NavId) => { setView(id); try { history.replaceState(null, '', `#${id}`); } catch { location.hash = id; } }, []);
  const go = (id: NavId) => {
    sfx.click();
    if (hist.current[pos.current] !== id) { hist.current = [...hist.current.slice(0, pos.current + 1), id]; pos.current = hist.current.length - 1; }
    show(id);
  };
  // Mouse 4 = back, Mouse 5 = forward (also Alt+Left / Alt+Right), through the tabs you visited
  const step = useCallback((d: -1 | 1) => {
    const n = pos.current + d;
    if (n < 0 || n >= hist.current.length) return;
    pos.current = n; sfx.click(); show(hist.current[n]);
  }, [show]);
  useEffect(() => { if (pos.current < 0) { hist.current = [view]; pos.current = 0; } }, [view]);
  useEffect(() => {
    const block = (e: MouseEvent) => { if (e.button === 3 || e.button === 4) { e.preventDefault(); e.stopPropagation(); } };
    const up = (e: MouseEvent) => { if (e.button === 3) { block(e); step(-1); } else if (e.button === 4) { block(e); step(1); } };
    const key = (e: KeyboardEvent) => { if (e.altKey && e.key === 'ArrowLeft') { e.preventDefault(); step(-1); } else if (e.altKey && e.key === 'ArrowRight') { e.preventDefault(); step(1); } };
    window.addEventListener('mousedown', block, true); window.addEventListener('auxclick', block, true); window.addEventListener('mouseup', up, true); window.addEventListener('keydown', key);
    return () => { window.removeEventListener('mousedown', block, true); window.removeEventListener('auxclick', block, true); window.removeEventListener('mouseup', up, true); window.removeEventListener('keydown', key); };
  }, [step]);
  useEffect(() => { document.documentElement.classList.toggle('max', maxed); }, [maxed]);

  const runApply = () => {
    openModal({
      kind: 'q', label: 'Confirm', title: 'Apply the selected tweaks?',
      body: 'Runs the tweaks that are switched on in Engine Tweaks. You can undo them at any time.',
      confirm: { text: 'Apply', run: async () => { setBusy(true); const r = await api.engineApply({ ...opts, power: power.on ? power.plan : null }); if (!r.ok) { setBusy(false); openModal({ kind: 'warn', label: 'Problem', title: 'Not started', body: r.error }); } } },
    });
  };
  const runRestore = async () => {
    const summary = await api.restoreSummary();
    openModal({
      kind: 'q', label: 'Confirm', title: 'Restore defaults?', body: summary,
      confirm: { text: 'Restore', run: async () => { setBusy(true); const r = await api.engineRestore(); if (!r.ok) { setBusy(false); openModal({ kind: 'warn', label: 'Problem', title: 'Not started', body: r.error }); } } },
    });
  };

  const engineAge = info?.days_since_optimization;
  const last = logs[logs.length - 1];

  return (
    <div className="app">
      <header className="glass titlebar">
        <div className="cut badge pywebview-drag-region" onDoubleClick={() => void api.winMax().then(setMaxed)} style={{ ['--fill' as string]: 'rgba(10,14,19,.95)' }}><span className="in">CS2 // COMMAND CENTER</span></div>
        <span className="decal pywebview-drag-region">v{info?.version ?? '...'} {native ? '' : '· browser preview'}</span>
        <div className="drag pywebview-drag-region" onDoubleClick={() => void api.winMax().then(setMaxed)} />
        <div className="ind">
          <span className="pill"><i className="dot" />PERM: {info ? (info.admin ? 'ADMIN' : 'STANDARD') : '...'}</span>
          <button className="sfx" onClick={() => { sfx.click(); setSettingsOpen(true); }} title="Settings">SETTINGS</button>
          <button className="sfx" aria-pressed={sound} onClick={() => { const v = !sound; sfx.set(v); setSound(v); if (v) sfx.click(); }} title="Interface sounds on or off">{sound ? 'SFX ON' : 'SFX OFF'}</button>
        </div>
        <div className="winctl">
          <button aria-label="Minimize" onClick={() => void api.winMin()}><Minus size={14} /></button>
          <button aria-label="Maximize" onClick={() => void api.winMax().then(setMaxed)}><Square size={11} /></button>
          <button aria-label="Close" className="x" onClick={() => void api.winClose()}><X size={14} /></button>
        </div>
      </header>

      <section className="glass hud2 brk" aria-label="Quick actions">
        <div className="hwb">
          <div className="l1">PROCESSOR:&nbsp; {hw?.cpu ?? '...'}</div>
          <div className="l2">GRAPHICS:&nbsp; {hw?.gpu ?? '...'}</div>
          <div className="l3">&#9889; Profile: {hw?.profile ?? ''}</div>
        </div>
        <div className="acts">
          <button className="btn cut amber pri" disabled={busy} onClick={runApply} title={PAGES.header.oneclick}><Zap size={14} /> {busy ? 'Working…' : 'One-click optimize'}</button>
          <button className="btn cut ghost" disabled={busy} onClick={() => void runRestore()} title={PAGES.header.restore}>Restore defaults</button>
        </div>
      </section>

      {update?.available && (
        <section className="glass card" role="status" style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap', borderColor: 'rgba(0,240,255,.4)', flex: 'none' }}>
          <div style={{ flex: 1, minWidth: 220 }}><div className="t">Update available: v{update.version}</div><div className="d" style={{ color: 'var(--tx2)' }}>{update.notes}</div></div>
          <button className="btn cut amber pri sm" onClick={() => { sfx.click(); void api.updateInstall().then((r) => { if (!r.ok) openModal({ kind: 'warn', label: 'Update', title: 'Not installed', body: r.error }); else setBusy(true); }); }}>Update now</button>
          <button className="btn cut ghost sm" onClick={() => { sfx.click(); setUpdate(null); }}>Later</button>
          <button className="btn cut ghost sm" onClick={() => { sfx.click(); void api.updateSkip(update.version ?? ''); setUpdate(null); }}>Skip this version</button>
        </section>
      )}
      <div className="main">
        <nav className="glass rail" aria-label="Sections">
          <div className="cap decal">// Navigation</div>
          {NAV.map(({ id, label, icon: Icon }) => (
            <button key={id} className="nav" aria-current={view === id ? 'page' : undefined} onMouseEnter={sfx.hover} onClick={() => go(id)}><Icon size={17} strokeWidth={1.7} />{label}</button>
          ))}
        </nav>
        <main className="content" style={{ minWidth: 0, display: 'flex', flexDirection: 'column', gap: 12 }}>
          <AnimatePresence mode="wait">
            <motion.div key={view} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.18 }} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {view === 'dashboard' && <Dashboard go={go} />}
              {view === 'maintenance' && <Maintenance busy={busy} setBusy={setBusy} go={go} />}
              {view === 'launch' && <Launch />}
              {view === 'booster' && <Booster />}
              {view === 'autoexec' && <Autoexec />}
              {view === 'faq' && <Faq />}
              {view === 'mpo' && <Mpo />}
              {view === 'discord' && <Discord />}
              {view === 'servers' && <Servers info={info} log={addLog} sniper={sniper} />}
              {view === 'engine' && <Engine opts={opts} setOpts={setOpts} onApplied={runApply} log={addLog} power={power} setPower={setPower} daysOpt={days.opt} daysMaint={days.maint} go={go} />}
              {!['servers', 'engine', 'dashboard', 'maintenance', 'launch', 'booster', 'autoexec', 'faq', 'mpo', 'discord'].includes(view) && (
                <div className="glass card ph brk"><div className="big">{NAV.find((n) => n.id === view)?.label.toUpperCase()}</div><div>This screen is not in the new app yet. It is still in the classic app.</div><div className="decal" style={{ marginTop: 8 }}>Still to come: Discord Presence</div></div>
              )}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      <section className={`glass log${drawer ? '' : ' shut'}`}>
        <button className="btn cut ghost sm logclear" onClick={() => { sfx.click(); void api.logClear(); setLogs([]); }}>Clear</button>
        <button className="loghead" onClick={() => { sfx.click(); setDrawer(!drawer); }} aria-expanded={drawer}>
          <span className="sect">System activity log</span>{last && <span className="decal">// {last.msg.slice(0, 70)}</span>}<span style={{ marginLeft: 'auto', color: 'var(--tx3)' }}><ChevronDown size={14} /></span>
        </button>
        <div className="body">
          {logs.map((l, i) => <div key={i}><span style={{ color: 'var(--tx3)' }}>[{l.t}] </span><span className={`lt ${TAGCLS[l.tag] ?? 's'}`}>[{l.tag}]</span> {l.msg}</div>)}
          <div ref={logEnd} />
        </div>
      </section>
      <AnimatePresence>{settingsOpen && <Settings onClose={() => setSettingsOpen(false)} onSaved={() => { addLog('SYSTEM', 'Settings saved'); void api.appInfo().then(setInfo); }} openDiscord={() => { setSettingsOpen(false); go('discord'); }} log={addLog} />}</AnimatePresence>
      <footer className="statusbar">
        <span className={`sn ${sniper?.state ?? 'idle'}`}>{sniper?.text ?? '\u25CF SLOT SNIPER: IDLE'}</span>
        {dnsInfo && <span className="sn dns">{dnsInfo.text}</span>}
        <span className="decal">Hobby project · not affiliated with Valve</span>
      </footer>
    </div>
  );
}

export default function App() {
  return <ModalHost><Reactor /><Shell /><ResizeEdges disabled={false} /><TooltipLayer /></ModalHost>;
}
