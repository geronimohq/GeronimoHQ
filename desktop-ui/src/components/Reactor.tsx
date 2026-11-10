import { memo } from 'react';

/** Reactor-core backdrop (vector): rotating rings, armor plating, rivets, blinking LEDs. Pure SVG + CSS, no layout cost on resize. */
const CX = 800, CY = 410;
const TICKS = (
  <g stroke="#ff9e1b" strokeOpacity=".55">
    {Array.from({ length: 96 }, (_, i) => {
      const a = (i * Math.PI * 2) / 96, r1 = 366, r2 = i % 8 === 0 ? 392 : 378;
      return <line key={i} x1={CX + Math.cos(a) * r1} y1={CY + Math.sin(a) * r1} x2={CX + Math.cos(a) * r2} y2={CY + Math.sin(a) * r2} strokeWidth={i % 8 === 0 ? 2 : 1} />;
    })}
  </g>
);
const RIVETS = (
  <g fill="#5b6978">
    {[[20, 24], [200, 24], [20, 876], [200, 876], [60, 170], [280, 170], [60, 430], [280, 430], [60, 510], [280, 510], [60, 730], [280, 730], [372, 300], [372, 600]].map(([x, y]) => <circle key={`${x}-${y}`} cx={x} cy={y} r={3.2} />)}
  </g>
);
const LEDS = (
  <g>
    {[[88, 203, '#ff9e1b', 'led'], [108, 203, '#00f0ff', 'led b'], [128, 203, '#ff9e1b', 'led c'], [84, 533, '#ff9e1b', 'led b'], [104, 533, '#10b981', 'led'], [124, 533, '#ff9e1b', 'led c'],
      [150, 533, '#00f0ff', 'led'], [88, 630, '#ff9e1b', 'led c'], [188, 203, '#10b981', 'led b']].map(([x, y, f, c]) => <rect key={`${x}-${y}`} x={Number(x) - 5} y={Number(y) - 3} width={10} height={6} rx={1.5} fill={String(f)} className={String(c)} />)}
  </g>
);

function ReactorImpl() {
  return (
    <div className="bgfx" aria-hidden="true">
      <svg className="bgsvg" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice">
<defs>
 <radialGradient id="core" cx="50%" cy="50%" r="50%"><stop offset="0" stopColor="#fff6dc"/><stop offset=".16" stopColor="#ffd27a"/><stop offset=".42" stopColor="#ff9420"/><stop offset=".78" stopColor="#9a4208" stopOpacity=".75"/><stop offset="1" stopColor="#3a1604" stopOpacity="0"/></radialGradient>
 <radialGradient id="halo" cx="50%" cy="50%" r="50%"><stop offset="0" stopColor="#ff9e1b" stopOpacity=".55"/><stop offset=".5" stopColor="#ff7a10" stopOpacity=".16"/><stop offset="1" stopColor="#ff7a10" stopOpacity="0"/></radialGradient>
 <linearGradient id="plate" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#34414f"/><stop offset=".45" stopColor="#1d2630"/><stop offset="1" stopColor="#10151c"/></linearGradient>
 <linearGradient id="plate2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#28323e"/><stop offset="1" stopColor="#151b23"/></linearGradient>
 <linearGradient id="rim" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stopColor="#ffffff" stopOpacity=".28"/><stop offset=".5" stopColor="#ffffff" stopOpacity="0"/><stop offset="1" stopColor="#ff9e1b" stopOpacity=".35"/></linearGradient>
 <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="16"/></filter>
 <g id="side">
  <polygon points="0,0 430,0 392,96 352,150 352,750 392,804 430,900 0,900" fill="url(#plate)" stroke="rgba(255,255,255,.10)"/>
  <polygon points="0,0 250,0 226,70 0,70" fill="url(#plate2)" stroke="rgba(255,255,255,.08)"/>
  <polygon points="0,830 226,830 250,900 0,900" fill="url(#plate2)" stroke="rgba(255,255,255,.08)"/>
  <polygon points="40,150 300,150 330,190 330,380 300,410 40,410" fill="#141a22" stroke="rgba(255,255,255,.10)"/>
  <polygon points="40,490 300,490 330,520 330,710 300,750 40,750" fill="#141a22" stroke="rgba(255,255,255,.10)"/>
  <path d="M40 150H300L330 190" fill="none" stroke="url(#rim)" strokeWidth="1.5"/>
  <path d="M40 490H300L330 520" fill="none" stroke="url(#rim)" strokeWidth="1.5"/>
  <g stroke="rgba(255,255,255,.06)"><path d="M0 120H250M0 450H330M0 790H250M120 150V410M120 490V750M200 150V410M200 490V750"/></g>
  <path d="M352 200C300 230 330 300 270 330S250 440 330 450M352 560C300 590 320 650 262 680" fill="none" stroke="#ff9e1b" strokeOpacity=".5" strokeWidth="1.4"/>
  <path d="M352 214C310 240 340 310 280 340S264 436 336 456" fill="none" stroke="#00f0ff" strokeOpacity=".28" strokeWidth="1"/>
  <g fill="#0b0f14" stroke="rgba(255,255,255,.14)"><rect x="70" y="190" width="70" height="26" rx="3"/><rect x="160" y="190" width="40" height="26" rx="3"/><rect x="70" y="520" width="110" height="26" rx="3"/><rect x="70" y="600" width="60" height="60" rx="3"/></g>
  {LEDS}{RIVETS}
 </g>
</defs>
<rect width="1600" height="900" fill="#0a0e13"/>
<circle cx="800" cy="410" r="520" fill="url(#halo)"/>
<g opacity=".95"><use href="#side"/><use href="#side" transform="translate(1600 0) scale(-1 1)"/></g>
<polygon points="430,0 1170,0 1110,50 490,50" fill="url(#plate2)" stroke="rgba(255,255,255,.10)"/>
<polygon points="430,900 1170,900 1110,850 490,850" fill="url(#plate2)" stroke="rgba(255,255,255,.10)"/>
{TICKS}
<g className="spin r"><circle cx="800" cy="410" r="335" fill="none" stroke="#18212b" strokeWidth="30"/><circle cx="800" cy="410" r="335" fill="none" stroke="rgba(255,255,255,.12)" strokeWidth="1"/><circle cx="800" cy="410" r="352" fill="none" stroke="#ff9e1b" strokeOpacity=".55" strokeWidth="2" strokeDasharray="140 38 12 38"/></g>
<g className="spin"><circle cx="800" cy="410" r="272" fill="none" stroke="#263240" strokeWidth="24" strokeDasharray="210 22"/><circle cx="800" cy="410" r="272" fill="none" stroke="rgba(255,255,255,.14)" strokeWidth="1" strokeDasharray="210 22"/></g>
<g className="spin f"><circle cx="800" cy="410" r="214" fill="none" stroke="#ff9e1b" strokeOpacity=".8" strokeWidth="3" strokeDasharray="2 9"/><circle cx="800" cy="410" r="190" fill="none" stroke="#33404f" strokeWidth="16"/><circle cx="800" cy="410" r="190" fill="none" stroke="#ffae33" strokeWidth="3" strokeDasharray="120 70"/></g>
<circle cx="800" cy="410" r="146" fill="#0a0d12" stroke="rgba(255,255,255,.18)" strokeWidth="2"/>
<circle className="core" cx="800" cy="410" r="136" fill="url(#core)"/>
<circle cx="800" cy="410" r="136" fill="none" stroke="rgba(255,235,190,.35)" strokeWidth="1.5"/>
<circle cx="800" cy="410" r="60" fill="#fff4d6" fillOpacity=".55" filter="url(#soft)"/>
</svg>
    </div>
  );
}
export const Reactor = memo(ReactorImpl);
