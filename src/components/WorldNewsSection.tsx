import React, { useMemo, useState } from 'react';
import { AlertTriangle, ExternalLink, FlaskConical, Newspaper, Orbit, Shield } from 'lucide-react';
import { isBreaking, timeAgo, useWorldNews, type NewsCat, type NewsItem } from '../utils/worldNews';

type Tab = 'all' | NewsCat;

const TABS: { id: Tab; label: string }[] = [
  { id: 'all', label: 'All' },
  { id: 'disaster', label: 'Disasters' },
  { id: 'war', label: 'War' },
  { id: 'science', label: 'Science' },
  { id: 'aliens', label: 'Aliens' },
];

const ICON: Record<NewsCat, React.ComponentType<{ className?: string }>> = { disaster: AlertTriangle, war: Shield, science: FlaskConical, aliens: Orbit };
const CAT_NAME: Record<NewsCat, string> = { disaster: 'Disaster', war: 'War', science: 'Science', aliens: 'Aliens' };
const PER_TAB = 12;

interface Props {
  theme: 'pepe' | 'banana';
}

export const WorldNewsSection: React.FC<Props> = ({ theme }) => {
  const { loaded, data, items, nowS } = useWorldNews();
  const [tab, setTab] = useState<Tab>('all');
  const isBanana = theme === 'banana';
  const accent = isBanana ? 'text-[#FFE135]' : 'text-[#2ECC71]';
  const accentBorder = isBanana ? 'border-[#FFE135]' : 'border-[#2ECC71]';
  const updated = data?.updated ?? nowS;
  const stale = !!data && nowS - data.updated > 6 * 3600;

  const counts = useMemo(() => {
    const c: Record<Tab, number> = { all: items.length, disaster: 0, war: 0, science: 0, aliens: 0 };
    for (const i of items) c[i.cat] += 1;
    return c;
  }, [items]);

  const shown = useMemo(() => {
    const pool = tab === 'all' ? items : items.filter((i) => i.cat === tab);
    return [...pool]
      .sort((a, b) => Number(isBreaking(b, nowS, updated)) - Number(isBreaking(a, nowS, updated)) || b.t - a.t)
      .slice(0, PER_TAB);
  }, [items, tab, nowS, updated]);

  return (
    <section id="world-news" className="relative w-full max-w-6xl mx-auto px-4 pt-2 pb-10 scroll-mt-4">
      <div className={`bento-card ${isBanana ? 'bento-accent-banana' : 'bento-accent-pepe'}`}>
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-3 mb-4 border-b border-[#1E2E26] pb-4">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className={`px-2.5 py-0.5 text-[10px] font-code rounded border ${isBanana ? 'bg-[#FFE135]/10 text-[#FFE135] border-[#FFE135]/40' : 'bg-[#2ECC71]/10 text-[#2ECC71] border-[#2ECC71]/40'}`}>
                BROADCAST // WORLD NEWS CHANNEL
              </span>
              <span className="text-[10px] font-code px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-300">AUTOMATED &middot; UNVERIFIED</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-cyber font-black text-white tracking-wider flex items-center gap-2">
              <Newspaper className={`w-6 h-6 ${accent}`} />
              WORLD NEWS CHANNEL
            </h2>
            <p className="text-sm font-tech text-slate-300 mt-1 max-w-3xl">
              A scanner that reads public news feeds about disasters, war, science breakthroughs and aliens, and lists the headlines with a link to the source. We only show the headline: the story stays with the outlet that wrote it.
            </p>
          </div>
          <div className="text-[11px] font-code text-slate-400 md:text-right flex-shrink-0">
            {data ? <>Updated {timeAgo(data.updated, nowS)}{stale && <span className="text-amber-300"> &middot; feed is behind</span>}</> : loaded ? 'Feed unavailable right now' : 'Scanning...'}
          </div>
        </div>

        <div role="tablist" aria-label="News categories" className="flex flex-wrap gap-2 mb-4">
          {TABS.map((t) => (
            <button
              key={t.id}
              role="tab"
              aria-selected={tab === t.id}
              onClick={() => setTab(t.id)}
              className={`px-3 py-1.5 rounded-lg border font-code text-xs font-bold transition-colors cursor-pointer ${tab === t.id ? `${accentBorder} ${accent} bg-white/5` : 'border-[#1E2E26] text-slate-400 hover:text-white'}`}
            >
              {t.label} <span className="opacity-60">({counts[t.id]})</span>
            </button>
          ))}
        </div>

        {tab === 'aliens' && (
          <div className="mb-3 rounded-lg border border-fuchsia-500/30 bg-fuchsia-950/20 px-3 py-2 text-xs font-tech text-fuchsia-200">
            <strong className="font-code">SIGNAL CHECK:</strong> space and science headlines that mention alien life, UAPs or the search for it. Nothing here is confirmed contact. If it ever is, it will not be hiding in a feed.
          </div>
        )}

        {shown.length === 0 ? (
          <div className="rounded-lg border border-[#1E2E26] bg-black/20 px-4 py-8 text-center text-sm font-tech text-slate-400">
            {loaded ? 'Nothing in this category right now.' : 'Scanning the wires...'}
          </div>
        ) : (
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {shown.map((it) => <NewsCard key={it.id} item={it} nowS={nowS} breaking={isBreaking(it, nowS, updated)} isBanana={isBanana} />)}
          </ul>
        )}

        <p className="mt-4 text-[11px] font-tech text-slate-500 leading-relaxed">
          Headlines are collected automatically from public feeds (USGS, GDACS, NASA, BBC, Al Jazeera, DW, NPR, France 24, ScienceDaily, SETI Institute) about every 30 minutes, and large earthquakes refresh in your browser. We do not check them, and &quot;breaking&quot; only means recent plus a hard alert or two outlets. In an emergency follow your local authorities, not this page.
        </p>
      </div>
    </section>
  );
};

const NewsCard: React.FC<{ item: NewsItem; nowS: number; breaking: boolean; isBanana: boolean }> = ({ item, nowS, breaking, isBanana }) => {
  const Icon = ICON[item.cat];
  return (
    <li className={`rounded-lg border bg-[#0A100D] px-3 py-2.5 ${breaking ? 'border-rose-500/50' : 'border-[#1E2E26]'}`}>
      <div className="flex flex-wrap items-center gap-1.5 mb-1">
        <span className={`inline-flex items-center gap-1 text-[10px] font-code font-bold ${isBanana ? 'text-[#FFE135]' : 'text-[#2ECC71]'}`}>
          <Icon className="w-3 h-3" />{CAT_NAME[item.cat].toUpperCase()}
        </span>
        {breaking && (
          <span className="inline-flex items-center gap-1 text-[10px] font-code font-bold px-1.5 py-0.5 rounded bg-rose-600 text-white">
            <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />BREAKING
          </span>
        )}
        {item.signal && <span className="text-[10px] font-code text-rose-300 border border-rose-500/40 rounded px-1">{item.signal}</span>}
      </div>
      <a href={item.url} target="_blank" rel="noopener noreferrer nofollow" className="group block text-sm font-tech font-semibold text-white hover:underline leading-snug">
        {item.title} <ExternalLink className="inline w-3 h-3 text-slate-500 group-hover:text-white align-baseline" />
      </a>
      <div className="mt-1 text-[11px] font-code text-slate-500">
        {item.source} &middot; {timeAgo(item.t, nowS)}
        {item.also.length > 0 && <span> &middot; also: {item.also.join(', ')}</span>}
      </div>
    </li>
  );
};

