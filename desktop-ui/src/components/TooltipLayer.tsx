import { useEffect, useState } from 'react';

/** Plain-language tooltips for actions that carry no explicit title (keyed by the button text, lower case). */
const TIPS: Record<string, string> = {
  connect: 'Joins this server in CS2. If CS2 is not running, it is started through Steam first.',
  sniper: 'Arms the Slot Sniper: it watches this server and joins the moment a slot opens at your chosen priority. Click again to disarm.',
  'sniper armed': 'The Slot Sniper is armed for this server. Click to disarm it.',
  players: 'Shows the live player list of this server.',
  'copy ip': 'Copies the server address (host:port) to your clipboard.',
  global: 'Show the main global community servers.',
  'planet china': 'Show the Chinese community servers (EXG, FyS, UB, ZL, 93X).',
  country: 'Show the estimate by individual countries.',
  region: 'Show the estimate by world region (North America, Europe, Asia...).',
  'add server': 'Add your own server to the list.',
  'save server': 'Saves this server to your list.',
  'save settings': 'Saves the settings on this screen.',
  cancel: 'Closes this window without saving.',
  close: 'Closes this window.',
  ok: 'Closes this message.',
  later: 'Hides this notice until the next start.',
  'skip this version': 'Stops announcing this version. A newer one is still announced.',
  'update now': 'Downloads the update, checks its size, SHA-256 and signature, then restarts into it.',
  'check now': 'Checks geronimohq.com once for a newer signed version. Nothing is installed without your click.',
  apply: 'Applies the choice next to it.',
  'apply custom dns': 'Sets the two DNS addresses you typed on your active network adapter (needs Administrator). Undo: Restore ISP default.',
  'use this dns': 'Sets this provider\'s DNS on your active network adapter (needs Administrator). Undo: Restore ISP default.',
  'engine tweaks': 'Opens the Engine Tweaks screen.',
  'open pc maintenance': 'Opens the PC Maintenance screen.',
  'launch ze browser': 'Opens the Zombie Escape server browser.',
  'open app data folder': 'Opens the folder where the app keeps its settings.',
  'reset app settings': 'Restores every option in this window to its default. Your presence key and timestamps are kept.',
  reload: 'Reads the file again from disk.',
  'refresh live status': 'Reads the live registry state again.',
  refresh: 'Reads the drive list and free space again.',
  'refresh now': 'Asks Discord for an immediate presence update.',
  'turn off presence': 'Clears the game activity from your Discord profile and closes the Discord link.',
  'save changes': 'Saves your manual edits to autoexec.cfg (a backup is made first).',
  'edit config': 'Unlocks the text box so you can write your own binds, aliases and commands.',
  'cancel edit': 'Leaves edit mode without saving.',
  set: 'Saves the FPS limit into autoexec.cfg.',
  'select all': 'Ticks every map that can safely be selected in the current list.',
  'deselect all': 'Clears the selection.',
  'select maps > 1 gb': 'Selects the maps that are bigger than 1 GB.',
  'select all temp downloads (safe)': 'Selects only temporary server downloads. Subscribed packs and official maps are never selected.',
  'select temp dupes only (safe)': 'Selects only duplicate copies of temporary downloads.',
  'delete selected maps': 'Permanently removes the ticked maps from your drive. This cannot be undone.',
  'backup custom vpk': 'Copies your custom server asset VPK files to a backup folder.',
  'restore custom vpk': 'Copies the backed-up custom server asset VPK files back.',
  'run benchmark': 'Measures latency and jitter of the gaming DNS servers.',
  'benchmark all dns servers': 'Pings all gaming DNS servers in parallel (3 samples each) to find the lowest latency and jitter for your location.',
  'restore isp default (dhcp)': 'Switches the adapter back to automatic ISP DNS (DHCP) and flushes the cache.',
  'copy options': 'Copies the text in the box so you can paste it into Steam: CS2, Properties, Launch Options.',
  'load baseline preset': 'Fills the editor with the clean competitive baseline preset.',
  'keep / reset to current': 'Puts back whatever launch options Steam has right now.',
  'relaunch as administrator': 'Restarts the app with Administrator rights (Windows asks first) and opens on this same tab.',
  'inspect & clean custom maps': 'Opens the custom map cleaner to inspect and delete unused workshop maps.',
  'verify workshop vpk health': 'Scans steamapps/workshop/content/730 and checks every .vpk header for corrupted or incomplete downloads.',
  'repair corrupted vpks': 'Removes only damaged or incomplete Workshop folders so Steam downloads them again.',
  'apply selected tweaks': 'Runs the engine tweaks that are switched on. Same as ONE-CLICK OPTIMIZE.',
  settings: 'Opens the settings window.',
  'sfx on': 'Interface sounds are on. Click to turn them off.',
  'sfx off': 'Interface sounds are off. Click to turn them on.',
};
const NAV_TIPS: Record<string, string> = {
  dashboard: 'Overview of your CS2 install, storage, servers and maintenance.',
  'engine tweaks': 'Performance tweaks for CS2 and Windows, each with an undo.',
  'gpu mpo diagnostics': 'Reads your GPU Multi-Plane Overlay state and explains the options.',
  'autoexec & binds': 'View and edit autoexec.cfg and add the ZE visual and audio binds.',
  'launch options': 'Inspect and edit your Steam launch options for CS2.',
  'live booster & dns': 'Raise CS2 CPU priority and choose the fastest gaming DNS.',
  'ze game servers': 'Live Zombie Escape server browser.',
  'pc maintenance': 'Clean-up, drive health and Windows repair tools.',
  'discord presence': 'Automatic Discord Rich Presence for CS2.',
  'help & faq': 'Searchable help for every feature.',
};
const norm = (t: string | null) => (t ?? '').replace(/\s+/g, ' ').trim().toLowerCase();

function tipFor(el: HTMLElement): string {
  const own = el.getAttribute('data-tip');
  if (own) return own;
  const label = el.getAttribute('aria-label');
  const text = norm(el.textContent);
  if (el.classList.contains('nav')) return NAV_TIPS[text] ?? '';
  if (el.getAttribute('role') === 'switch') return `${label ?? text}: click to turn on or off.`;
  if (label === 'Minimize') return 'Minimize (hides to the tray when that setting is on).';
  if (label === 'Maximize') return 'Maximize or restore the window.';
  if (label === 'Close') return 'Close the application completely.';
  if (el.tagName === 'BUTTON') {
    if (TIPS[text]) return TIPS[text];
    const m = text.match(/^\u2264\s*(\d+)$/);
    if (m) return `The Slot Sniper joins when the player count drops to ${m[1]} or lower.`;
    const fm = text.match(/^(.*) \((\d+)\)$/);
    if (fm) return `Show only: ${fm[1]}.`;
  }
  return '';
}

/** One styled tooltip for the whole app. Elements keep their `title`; it is moved to data-tip so the browser's own tooltip never shows. */
export function TooltipLayer() {
  const [tip, setTip] = useState<{ text: string; x: number; y: number } | null>(null);
  useEffect(() => {
    let timer: number | undefined;
    let current: HTMLElement | null = null;
    const hide = () => { window.clearTimeout(timer); current = null; setTip(null); };
    const over = (e: MouseEvent) => {
      const el = (e.target as HTMLElement | null)?.closest?.('[title],[data-tip],button,[role="switch"],.nav') as HTMLElement | null;
      if (!el || el === current) return;
      const t = el.getAttribute('title');
      if (t) { el.setAttribute('data-tip', t); el.removeAttribute('title'); }
      const text = tipFor(el);
      window.clearTimeout(timer);
      current = el;
      if (!text) { setTip(null); return; }
      const x = e.clientX, y = e.clientY;
      timer = window.setTimeout(() => setTip({ text, x, y }), 450);
    };
    const out = (e: MouseEvent) => { if (current && !current.contains(e.relatedTarget as Node | null)) hide(); };
    window.addEventListener('mouseover', over);
    window.addEventListener('mouseout', out);
    window.addEventListener('mousedown', hide, true);
    window.addEventListener('wheel', hide, { passive: true });
    window.addEventListener('keydown', hide);
    return () => {
      window.removeEventListener('mouseover', over); window.removeEventListener('mouseout', out);
      window.removeEventListener('mousedown', hide, true); window.removeEventListener('wheel', hide); window.removeEventListener('keydown', hide);
    };
  }, []);
  if (!tip) return null;
  const left = Math.min(tip.x + 14, window.innerWidth - 340), top = Math.min(tip.y + 18, window.innerHeight - 90);
  return <div className="tip" style={{ left, top }} role="tooltip">{tip.text}</div>;
}
