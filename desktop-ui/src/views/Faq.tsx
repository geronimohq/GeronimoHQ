import { useMemo, useState } from 'react';
import { ChevronDown, Search } from 'lucide-react';
import { sfx } from '../sound';
import faq from '../data/faq.json';

interface Card { icon: string; title: string; tag: string; qa: { q: string; a: string }[] }
const CARDS = faq as Card[];

export default function Faq() {
  const [q, setQ] = useState('');
  const [open, setOpen] = useState<Record<string, boolean>>({});
  const cards = useMemo(() => {
    const t = q.trim().toLowerCase();
    return CARDS.map((c) => ({ ...c, qa: t ? c.qa.filter((x) => (x.q + ' ' + x.a).toLowerCase().includes(t)) : c.qa })).filter((c) => c.qa.length);
  }, [q]);
  return (
    <section className="view on">
      <div className="vhead"><div><div className="decal">// 10 · knowledge base</div><h1>Help &amp; FAQ</h1><p>What each feature changes, how to undo it, network troubleshooting and feature guides.</p></div></div>
      <div className="glass toolbar"><div className="search"><Search size={15} style={{ color: 'var(--tx3)' }} /><label className="sr" htmlFor="fq">Search the help</label>
        <input id="fq" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search questions and answers" /></div></div>
      {cards.map((c) => (
        <div className="glass card" key={c.title}>
          <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 8 }}>
            <span style={{ fontSize: 16 }}>{c.icon}</span><span className="sect" style={{ color: 'var(--tx)' }}>{c.title}</span><span className="tag" style={{ marginLeft: 'auto' }}>{c.tag}</span>
          </div>
          {c.qa.map((x) => {
            const id = c.title + x.q, on = q.trim() ? true : !!open[id];
            return (
              <div className="faqq" key={id}>
                <button onClick={() => { sfx.click(); setOpen({ ...open, [id]: !open[id] }); }} aria-expanded={on}>
                  <span className="mono" style={{ color: 'var(--amber)' }}>Q</span><span style={{ flex: 1, textAlign: 'left', fontWeight: 600 }}>{x.q}</span><ChevronDown size={15} style={{ transform: on ? 'none' : 'rotate(-90deg)', transition: '.2s', color: 'var(--tx3)' }} />
                </button>
                {on && <div className="faqa">{x.a}</div>}
              </div>
            );
          })}
        </div>
      ))}
      {!cards.length && <div className="glass card ph">No answers match.</div>}
    </section>
  );
}
