import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { sfx } from '../sound';
import { api } from '../api';

type Kind = 'ok' | 'q' | 'warn';
export interface ModalSpec {
  kind: Kind; label: string; title: string; body?: ReactNode;
  confirm?: { text: string; run: () => void | Promise<void> }; cancel?: boolean; okText?: string;
}
const Ctx = createContext<(m: ModalSpec) => void>(() => undefined);
export const useModal = () => useContext(Ctx);

const ICON: Record<Kind, string> = { ok: '✓', q: '?', warn: '!' };

export function ModalHost({ children }: { children: ReactNode }) {
  const [m, setM] = useState<ModalSpec | null>(null);
  const open = useCallback((spec: ModalSpec) => { setM(spec); sfx.alert(); }, []);
  const close = useCallback(() => setM(null), []);
  useEffect(() => {
    const k = (e: KeyboardEvent) => { if (e.key === 'Escape') close(); };
    window.addEventListener('keydown', k);
    return () => window.removeEventListener('keydown', k);
  }, [close]);
  return (
    <Ctx.Provider value={open}>
      {children}
      <AnimatePresence>
        {m && (
          <motion.div className="scrim on top" role="dialog" aria-modal="true" aria-labelledby="mTitle"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onMouseDown={(e) => { if (e.target === e.currentTarget) close(); }}>
            <motion.div className="cut modal brk" initial={{ scale: 0.94, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.96, opacity: 0 }} transition={{ type: 'spring', stiffness: 420, damping: 30 }}>
              <div style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
                <div className={`ic ${m.kind === 'ok' ? 'ok' : 'q'}`}>{ICON[m.kind]}</div>
                <div><div className="decal">{m.label}</div><h3 id="mTitle">{m.title}</h3></div>
              </div>
              {m.body && <div style={{ color: 'var(--tx2)', margin: '14px 0 0', whiteSpace: 'pre-line' }}>{m.body}</div>}
              <div className="btns">
                {(m.cancel || m.confirm) && <button className="btn cut ghost" onClick={() => { sfx.click(); close(); }}>Cancel</button>}
                {m.confirm
                  ? <button className="btn cut amber pri" autoFocus onClick={async () => { sfx.click(); close(); await m.confirm!.run(); }}>{m.confirm.text}</button>
                  : <button className="btn cut amber pri" autoFocus onClick={() => { sfx.click(); close(); }}>{m.okText ?? 'OK'}</button>}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </Ctx.Provider>
  );
}

/** "This needs Administrator": offers a relaunch that comes back to the same tab (page = the tab id). */
export function useAdminPrompt() {
  const open = useModal();
  return (title: string, page: string) => open({
    kind: 'q', label: 'Administrator needed', title,
    body: 'This action needs Administrator rights. The app can restart as Administrator and open on this same tab.\n\nRelaunch as Administrator now?',
    confirm: { text: 'Relaunch as Administrator', run: async () => {
      const r = await api.relaunchAdmin(page);
      if (!r.ok) open({ kind: 'warn', label: 'Cancelled', title: 'Still running as a standard user', body: 'The Windows permission request was cancelled or declined.' });
    } },
  });
}
