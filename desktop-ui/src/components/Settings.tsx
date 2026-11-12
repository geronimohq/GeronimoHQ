import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { api } from '../api';
import { sfx } from '../sound';
import { useModal } from './Modal';
import type { SettingsValues } from '../types';
import { BG_ANIM_EVENT } from './Reactor';

const DEFAULTS = { start_with_windows: false, start_minimized: false, minimize_to_tray_on_close: true, open_on_page: 'Dashboard', sniper_sound_enabled: true,
  server_refresh_speed: 'Normal (5s)', discord_rpc_enabled: true, check_updates_on_startup: true, animated_background: true };

function Opt({ on, set, title, desc }: { on: boolean; set: (v: boolean) => void; title: string; desc: string }) {
  return (
    <div className="row">
      <div className="grow"><div className="t" style={{ fontSize: 13 }}>{title}</div><div className="d" style={{ fontSize: 12 }}>{desc}</div></div>
      <button className="sw" role="switch" aria-checked={on} aria-label={title} onClick={() => { sfx.toggle(); set(!on); }} />
    </div>
  );
}
const Sec = ({ t }: { t: string }) => <div className="sect" style={{ margin: '16px 0 2px' }}>{t}</div>;

export default function Settings({ onClose, onSaved, openDiscord, log }: { onClose: () => void; onSaved: (refresh: number) => void; openDiscord: () => void; log: (tag: string, msg: string) => void }) {
  const [v, setV] = useState<SettingsValues | null>(null);
  const [upd, setUpd] = useState('Up to date');
  const [last, setLast] = useState('Never');
  const [about, setAbout] = useState({ version: '', build_date: '' });
  const [note, setNote] = useState('');
  const openModal = useModal();
  useEffect(() => {
    void api.settingsGet().then(setV);
    void api.about().then((a) => { setAbout(a); setLast(a.last_update_check); });
  }, []);
  useEffect(() => { const k = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); }; window.addEventListener('keydown', k); return () => window.removeEventListener('keydown', k); }, [onClose]);
  if (!v) return null;
  const set = <K extends keyof SettingsValues>(k: K, val: SettingsValues[K]) => setV({ ...v, [k]: val });
  const save = async () => {
    const r = await api.settingsSave(v); sfx.toggle(); onSaved(r.refresh_seconds); onClose();
    window.dispatchEvent(new CustomEvent(BG_ANIM_EVENT, { detail: v.animated_background !== false }));
    if (r.startup_ok === false) openModal({ kind: 'warn', label: 'Start with Windows', title: 'Could not change Start with Windows', body: 'Windows refused the startup entry. The other settings were saved. See the activity log.' });
  };
  // like 1.6.0: Reset only fills the dialog with the defaults; nothing changes until Save is clicked
  const reset = () => openModal({ kind: 'q', label: 'Confirm', title: 'Reset app settings?', body: 'Are you sure you want to restore default configuration settings? Your presence key and timestamps are kept.',
    confirm: { text: 'Reset', run: () => { setV({ ...v, ...DEFAULTS }); setNote('Defaults restored in the dialog. Click Save to keep them.'); log('SYSTEM', '[SETTINGS] Defaults restored in the dialog. Click Save to keep them.'); } } });
  const copyText = async (get: () => Promise<string>, what: string) => {
    const text = await get();
    try { await navigator.clipboard.writeText(text); } catch { /* ignore */ }
    sfx.toggle(); log('SYSTEM', `[SETTINGS] ${what} copied to the clipboard.`);
    openModal({ kind: 'ok', label: 'Copied', title: `${what} copied`, body: text.length > 200 ? `${text.slice(0, 80)}...` : text });
  };
  return (
    <motion.div className="scrim on" role="dialog" aria-modal="true" aria-labelledby="setTitle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <motion.div className="cut modal brk" style={{ width: 'min(660px,100%)', maxHeight: '90vh', overflow: 'auto' }} initial={{ scale: 0.94, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.96, opacity: 0 }}>
        <div className="decal">Preferences</div><h3 id="setTitle">Settings &amp; background options</h3>
        <div style={{ color: 'var(--tx2)', marginTop: 4 }}>Configure system tray behavior, Windows startup, and Discord integration.</div>

        <Sec t="General" />
        <Opt on={v.start_with_windows} set={(x) => set('start_with_windows', x)} title="Start CS2 Command Center with Windows" desc="Starts the app as a normal user when you log in. Untick to remove it." />
        <Opt on={v.start_minimized} set={(x) => set('start_minimized', x)} title="Start minimized to the system tray (hidden near the Windows clock)" desc="When unchecked, the app window opens on your desktop at startup." />
        <Opt on={v.minimize_to_tray_on_close} set={(x) => set('minimize_to_tray_on_close', x)} title="Minimize to the system tray when [-] is clicked" desc="Clicking [-] hides the window to the tray; clicking [X] closes the application completely." />
        <div className="row"><div className="grow"><div className="t" style={{ fontSize: 13 }}>Open on startup</div><div className="d" style={{ fontSize: 12 }}>Choose whether the app opens to the Dashboard or remembers your last active tab.</div></div>
          <div className="seg">{v.pages.map((s) => <button key={s} aria-pressed={v.open_on_page === s} onClick={() => { sfx.click(); set('open_on_page', s); }}>{s}</button>)}</div></div>

        <Sec t="Performance" />
        <Opt on={v.animated_background !== false} set={(x) => set('animated_background', x)} title="Animated reactor background"
          desc="The rings turn slowly while this window is in front and stop by themselves when it is in the background or minimized (for example while you play). Turn off for the lowest CPU use; the background stays, just still." />

        <Sec t="Server & sniper" />
        <Opt on={v.sniper_sound_enabled} set={(x) => set('sniper_sound_enabled', x)} title="Slot Sniper audio notifications" desc="Plays an audio chime when a monitored server slot becomes available." />
        <div className="row"><div className="grow"><div className="t" style={{ fontSize: 13 }}>Server query speed</div><div className="d" style={{ fontSize: 12 }}>Interval between automatic background server queries.</div></div>
          <div className="seg cy">{v.speeds.map((s) => <button key={s} aria-pressed={v.server_refresh_speed === s} onClick={() => { sfx.click(); set('server_refresh_speed', s); }}>{s}</button>)}</div></div>

        <Sec t="Privacy" />
        <Opt on={v.discord_rpc_enabled} set={(x) => set('discord_rpc_enabled', x)} title="Share game telemetry with Discord Rich Presence" desc="Shares active CS2 server and map details with your local Discord client. Discord Presence features automatic CS2 detection and a real-time profile preview. No setup needed: the app ships with its own Discord Application ID." />

        <Sec t="Discord" />
        <div className="row"><div className="grow"><div className="d" style={{ fontSize: 12 }}>Navigate directly to the Discord Presence tab to see the live preview.</div></div>
          <button className="btn cut ghost sm" onClick={() => { sfx.click(); openDiscord(); }}>Open Discord Presence tab</button></div>

        <Sec t="Data & storage" />
        <div className="row" style={{ flexWrap: 'wrap' }}>
          <div className="grow"><div className="d" style={{ fontSize: 12 }}>Opens the local configuration directory in Explorer, or restores the default values in this dialog.</div></div>
          <button className="btn cut ghost sm" onClick={() => { sfx.click(); void api.openPath('appdata'); }}>Open app data folder</button>
          <button className="btn cut ghost sm dng" onClick={() => { sfx.click(); reset(); }}>Reset app settings</button>
        </div>
        {note && <div className="decal" style={{ color: 'var(--amber)', textTransform: 'none', letterSpacing: 0 }}>{note}</div>}

        <Sec t="Updates" />
        <Opt on={v.check_updates_on_startup} set={(x) => set('check_updates_on_startup', x)} title="Check for updates when the app starts" desc="Connects to geronimohq.com/update/latest.json over HTTPS. Only your app version is sent in the User-Agent header; no telemetry, identity or settings are transmitted." />
        <div className="row"><div className="grow"><div className="d" style={{ fontSize: 12 }}>Last checked: {last} · {upd}</div></div>
          <button className="btn cut ghost sm" onClick={() => { sfx.click(); setUpd('Checking\u2026'); void api.updateCheck().then((r) => { setUpd(r.available ? `Update available: v${r.version}` : (r.message ?? 'Up to date')); if (r.last) setLast(r.last); }); }}>Check now</button></div>

        <Sec t="About" />
        <div className="row" style={{ flexWrap: 'wrap' }}>
          <div className="grow"><div className="t" style={{ fontSize: 13 }}>CS2 Command Center v{about.version}</div><div className="d" style={{ fontSize: 12 }}>Source 2 Engine Optimizer &amp; Zombie Escape Direct Connector by Geronimo</div></div>
          <button className="btn cut ghost sm" onClick={() => { sfx.click(); void copyText(api.diagnostics, 'Diagnostics'); }}>Copy diagnostics</button>
          <button className="btn cut ghost sm" onClick={() => { sfx.click(); void copyText(api.exeSha, 'SHA-256 checksum'); }}>Copy SHA-256</button>
        </div>
        <div className="btns"><button className="btn cut ghost" onClick={() => { sfx.click(); onClose(); }}>Cancel</button><button className="btn cut amber pri" onClick={() => void save()}>Save settings</button></div>
      </motion.div>
    </motion.div>
  );
}
