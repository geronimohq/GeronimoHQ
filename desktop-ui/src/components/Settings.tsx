import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { api } from '../api';
import { sfx } from '../sound';
import { useModal } from './Modal';
import type { SettingsValues } from '../types';

const BOOLS: [keyof SettingsValues, string, string][] = [
  ['start_with_windows', 'Start CS2 Command Center with Windows', 'Starts the app as a normal user when you log in. Untick to remove it.'],
  ['start_minimized', 'Start minimized to the system tray', 'When starting with Windows, start hidden in the tray.'],
  ['minimize_to_tray_on_close', 'Closing the window hides it to the tray', 'Clicking minimize hides to the taskbar; clicking close hides to the tray instead of quitting. Untick to quit on close.'],
  ['check_updates_on_startup', 'Check for updates at startup', 'Checks geronimohq.com once. Nothing is installed without your click.'],
  ['sniper_sound_enabled', 'Slot Sniper audio notifications', 'Plays a sound when the sniper fires.'],
  ['discord_rpc_enabled', 'Share game status with Discord Rich Presence', 'Shows your CS2 map and server on your Discord profile.'],
];

export default function Settings({ onClose, onSaved }: { onClose: () => void; onSaved: (refresh: number) => void }) {
  const [v, setV] = useState<SettingsValues | null>(null);
  const openModal = useModal();
  useEffect(() => { void api.settingsGet().then(setV); }, []);
  useEffect(() => { const k = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); }; window.addEventListener('keydown', k); return () => window.removeEventListener('keydown', k); }, [onClose]);
  if (!v) return null;
  const set = <K extends keyof SettingsValues>(k: K, val: SettingsValues[K]) => setV({ ...v, [k]: val });
  const save = async () => { const r = await api.settingsSave(v); sfx.toggle(); onSaved(r.refresh_seconds); onClose(); };
  const reset = () => openModal({ kind: 'q', label: 'Confirm', title: 'Reset app settings?', body: 'Restores every option on this screen to its default. Your presence key and timestamps are kept.',
    confirm: { text: 'Reset', run: async () => { await api.settingsReset(); void api.settingsGet().then(setV); } } });
  return (
    <motion.div className="scrim on" role="dialog" aria-modal="true" aria-labelledby="setTitle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <motion.div className="cut modal brk" style={{ width: 'min(620px,100%)', maxHeight: '88vh', overflow: 'auto' }} initial={{ scale: 0.94, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.96, opacity: 0 }}>
        <div className="decal">Preferences</div><h3 id="setTitle">Settings &amp; background options</h3>
        {BOOLS.map(([k, t, d]) => (
          <div className="row" key={k}>
            <div className="grow"><div className="t" style={{ fontSize: 13 }}>{t}</div><div className="d" style={{ fontSize: 12 }}>{d}</div></div>
            <button className="sw" role="switch" aria-checked={!!v[k]} aria-label={t} onClick={() => { sfx.toggle(); set(k, !v[k] as never); }} />
          </div>
        ))}
        <div className="row"><div className="grow"><div className="t" style={{ fontSize: 13 }}>Server query speed</div><div className="d" style={{ fontSize: 12 }}>How often the server list refreshes.</div></div>
          <div className="seg cy">{v.speeds.map((s) => <button key={s} aria-pressed={v.server_refresh_speed === s} onClick={() => { sfx.click(); set('server_refresh_speed', s); }}>{s}</button>)}</div></div>
        <div className="row"><div className="grow"><div className="t" style={{ fontSize: 13 }}>Open on</div></div>
          <div className="seg">{v.pages.map((s) => <button key={s} aria-pressed={v.open_on_page === s} onClick={() => { sfx.click(); set('open_on_page', s); }}>{s}</button>)}</div></div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 14 }}>
          <button className="btn cut ghost sm" onClick={() => { sfx.click(); void api.openPath('appdata'); }}>Open app data folder</button>
          <button className="btn cut ghost sm dng" onClick={() => { sfx.click(); reset(); }}>Reset app settings</button>
        </div>
        <div className="btns"><button className="btn cut ghost" onClick={() => { sfx.click(); onClose(); }}>Cancel</button><button className="btn cut amber pri" onClick={() => void save()}>Save settings</button></div>
      </motion.div>
    </motion.div>
  );
}
