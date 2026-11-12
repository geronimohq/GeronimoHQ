import type { ModalSpec } from './components/Modal';
import type { ToolResult } from './types';

/** Short wording for how a long Windows tool ended; shown under the buttons and as the result window's title. */
export const STATUS_LABEL: Record<string, string> = {
  clean: 'No problems found', repaired: 'Problems found and repaired', unfixable: 'Problems found, not all fixed', done: 'Completed',
  failed: 'Did not complete', timeout: 'Timed out', reboot: 'Restart needed first', unverified: 'Finished, result unclear', admin: 'Needed Administrator',
};

/** What each tool does and how long it takes, shown in the confirmation before it starts. */
export const TOOL_INFO: Record<string, { name: string; time: string; what: string }> = {
  sfc: { name: 'System File Checker (SFC)', time: '5 to 30 minutes', what: 'checks every protected Windows system file and replaces damaged ones with good copies' },
  dism: { name: 'DISM health restore', time: '10 to 40 minutes', what: 'checks the Windows component store (the source SFC repairs from) and repairs it with Windows Update files, which needs an internet connection if repairs are needed' },
  winsxs: { name: 'DISM WinSxS clean-up', time: '5 to 30 minutes', what: 'removes older, superseded copies of Windows update files. Nothing Windows is using is removed' },
  trim: { name: 'SSD TRIM', time: '1 to 10 minutes', what: 'tells your SSDs which blocks are free so they stay fast (any hard disk is defragmented instead)' },
};
export const LONG_TOOLS = ['sfc', 'dism', 'winsxs', 'trim'];

/** Typical run time in seconds, used for the estimated progress until Windows reports a percentage (or when it never does).
 * Replaced by how long the tool took the last time on this PC. */
export const TYPICAL_S: Record<string, number> = { sfc: 600, dism: 1200, winsxs: 600, trim: 90 };

/** Where each tool's own record lives, in one line, for the note under the results. */
export const RECORD_HINT: Record<string, string> = {
  sfc: "SFC's [SR] lines from CBS.log",
  dism: 'dism.log in Windows\\Logs\\DISM',
  winsxs: 'dism.log in Windows\\Logs\\DISM',
  trim: "Optimize Drives' Last run column",
};

/** Progress to draw: Windows' own percentage when it reports one, otherwise an estimate from the elapsed time that slows down and never
 * reaches 100% on its own (only the real end of the tool closes the bar). */
export function progressOf(pct: number | null, elapsed: number, typical: number): { value: number; real: boolean } {
  if (pct != null) return { value: Math.max(0, Math.min(100, pct)), real: true };
  const t = Math.max(1, typical);
  return { value: Math.min(95, 95 * (1 - Math.exp(-1.7 * Math.max(0, elapsed) / t))), real: false };
}

export function resultModal(r: ToolResult): ModalSpec {
  const lines: string[] = [];
  if (r.detail) lines.push(r.detail);
  if (r.next) lines.push(`What to do next: ${r.next}`);
  if (r.status === 'failed' || r.status === 'unfixable' || r.status === 'unverified') lines.push(r.headline);
  if (r.evidence.length) lines.push(`How the app knows:\n${r.evidence.map((e) => `• ${e}`).join('\n')}`);
  if (r.log_file) lines.push(`Windows' own log: ${r.log_file}`);
  if (r.report) lines.push(`A text copy of this result (to keep, print or share): ${r.report}\nOpen it any time with 'Report' under the tool buttons.`);
  return { kind: r.ok && r.status !== 'unverified' ? 'ok' : 'warn', label: r.title, title: STATUS_LABEL[r.status] ?? r.headline, body: lines.join('\n\n') };
}

/** How Verify Workshop VPK health decides, shown in its result window. */
export const VPK_HOW = [
  'What was checked in each workshop pack (steamapps/workshop/content/730, every Steam library that holds CS2):',
  '1. The folder holds a .vpk and no leftover download files (.tmp, .download, .patch).',
  '2. The pack index starts with the VPK signature and every entry in it can be read.',
  '3. Every data part the index points to (_000.vpk, _001.vpk, ...) is on disk and at least as long as the index needs. A download that stopped half way keeps a valid header, so this is the check that finds it.',
  'What it cannot see: a changed byte inside a complete file of the right size (finding that would mean reading every file in full). If a map still crashes, remove it with Repair or the Map Cleaner and let Steam download it again.',
].join('\n');

export const VPK_REPAIR_HOW = 'Repair re-runs the same check and then deletes only the folders it flags, so Steam downloads them again. It never touches healthy packs, links or junctions, anything outside the workshop folder, or a pack that changed in the last 15 minutes (Steam may still be downloading it).';
