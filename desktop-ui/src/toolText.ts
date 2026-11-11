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

export function resultModal(r: ToolResult): ModalSpec {
  const lines: string[] = [];
  if (r.detail) lines.push(r.detail);
  if (r.next) lines.push(`What to do next: ${r.next}`);
  if (r.status === 'failed' || r.status === 'unfixable' || r.status === 'unverified') lines.push(r.headline);
  if (r.evidence.length) lines.push(`How the app knows:\n${r.evidence.map((e) => `• ${e}`).join('\n')}`);
  if (r.log_file) lines.push(`Windows' own log: ${r.log_file}`);
  return { kind: r.ok && r.status !== 'unverified' ? 'ok' : 'warn', label: r.title, title: STATUS_LABEL[r.status] ?? r.headline, body: lines.join('\n\n') };
}
