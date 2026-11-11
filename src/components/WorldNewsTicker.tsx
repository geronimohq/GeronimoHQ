import React, { useMemo } from 'react';
import { Newspaper } from 'lucide-react';
import { scrollToSectionById } from './CyberNavbar';
import { tickerContent, timeAgo, useWorldNews, type NewsCat } from '../utils/worldNews';

const CAT_LABEL: Record<NewsCat, string> = { disaster: 'DISASTER', war: 'WAR', science: 'SCIENCE', aliens: 'ALIENS' };

interface Props {
  theme: 'pepe' | 'banana';
}

/**
 * Slim news strip under the navbar. Shows the breaking stories when there are any; otherwise the newest headlines, labelled LATEST, so it is never
 * mistaken for an alarm. Hidden when the data is missing or more than a day old. Pauses on hover and focus; static (scrollable) under reduced motion.
 */
export const WorldNewsTicker: React.FC<Props> = ({ theme }) => {
  const { data, items, nowS } = useWorldNews();
  const isBanana = theme === 'banana';
  const accent = isBanana ? 'text-[#FFE135]' : 'text-[#2ECC71]';
  const updated = data?.updated ?? nowS;
  const content = useMemo(() => tickerContent(items, nowS, updated), [items, nowS, updated]);
  if (!content) return null;

  const breaking = content.mode === 'breaking';
  const duration = Math.max(40, content.items.length * 14);
  const list = (hidden: boolean) => (
    <span className="news-ticker-copy" aria-hidden={hidden || undefined}>
      {content.items.map((it) => (
        <a
          key={it.id}
          href={it.url}
          target="_blank"
          rel="noopener noreferrer nofollow"
          tabIndex={hidden ? -1 : undefined}
          className="inline-flex items-center gap-2 text-xs font-tech text-slate-200 hover:text-white hover:underline"
        >
          <span className={`font-code text-[10px] font-bold ${accent}`}>{CAT_LABEL[it.cat]}</span>
          {it.signal && <span className="font-code text-[10px] text-rose-300 border border-rose-500/40 rounded px-1">{it.signal}</span>}
          <span>{it.title}</span>
          <span className="font-code text-[10px] text-slate-500">{it.source} &middot; {timeAgo(it.t, nowS)}</span>
        </a>
      ))}
    </span>
  );

  return (
    <div className="w-full max-w-6xl mx-auto px-4 pt-3" role="region" aria-label="World news headlines">
      <div className={`news-ticker flex items-stretch rounded-lg border bg-[#0E1512]/95 overflow-hidden ${isBanana ? 'border-[#FFE135]/30' : 'border-[#2ECC71]/30'}`}>
        <button
          type="button"
          onClick={() => scrollToSectionById('world-news')}
          className={`flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 font-code text-[11px] font-bold tracking-wider cursor-pointer ${breaking ? 'bg-rose-600 text-white' : isBanana ? 'bg-[#FFE135]/15 text-[#FFE135]' : 'bg-[#2ECC71]/15 text-[#2ECC71]'}`}
          title="Open the World News Channel"
        >
          <Newspaper className="w-3.5 h-3.5" />
          {breaking ? <><span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />BREAKING</> : 'LATEST'}
        </button>
        <div className="news-ticker-viewport flex-1 min-w-0 py-1.5 px-3 overflow-hidden">
          <div className="news-ticker-track" style={{ ['--news-dur' as string]: `${duration}s` }}>
            {list(false)}
            {list(true)}
          </div>
        </div>
      </div>
    </div>
  );
};
