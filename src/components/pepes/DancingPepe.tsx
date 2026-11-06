import React, { useState } from 'react';
import confetti from 'canvas-confetti';

interface DancingPepeProps {
  className?: string;
  isInspected?: boolean;
}

export const DancingPepe: React.FC<DancingPepeProps> = ({ className = '', isInspected = false }) => {
  const [raveMode, setRaveMode] = useState(false);
  const [vibeCount, setVibeCount] = useState(0);

  const handlePartyBurst = (e: React.MouseEvent) => {
    setVibeCount((v) => v + 1);
    setRaveMode(true);
    setTimeout(() => setRaveMode(false), 2000);

    // Fire cyber confetti with neon colors (cyan, magenta, lime, yellow)
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const x = (rect.left + rect.width / 2) / window.innerWidth;
    const y = (rect.top + rect.height / 2) / window.innerHeight;

    confetti({
      particleCount: 45,
      spread: 70,
      origin: { x, y },
      colors: ['#00f0ff', '#ff007f', '#39ff14', '#ffe600'],
      disableForReducedMotion: true,
    });
  };

  return (
    <div
      onClick={handlePartyBurst}
      className={`relative group cursor-pointer transition-transform duration-300 ${isInspected ? 'scale-105' : ''} ${className}`}
      title="Click for Rave Mode & Cyber Confetti!"
    >
      {/* Floating Rave Status on Interaction */}
      {raveMode && (
        <div className="absolute -top-12 left-1/2 -translate-x-1/2 z-30 whitespace-nowrap px-3 py-1 bg-lime-950/90 border border-lime-400 rounded text-lime-300 text-xs font-cyber shadow-[0_0_20px_rgba(57,255,20,0.8)] animate-pulse">
          ⚡ RAVE OVERDRIVE: {135 + vibeCount * 2} BPM!
        </div>
      )}

      {/* Pepe Dance Animated Frame */}
      <div className={`relative ${raveMode ? 'animate-bounce' : 'animate-pepe-dance'}`}>
        <svg
          viewBox="0 0 240 240"
          className="w-full h-auto drop-shadow-[0_0_20px_rgba(57,255,20,0.35)] transition-all group-hover:drop-shadow-[0_0_35px_rgba(57,255,20,0.7)]"
        >
          <defs>
            <linearGradient id="pepePartySkin" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#8ce03a" />
              <stop offset="60%" stop-color="#6ec228" />
              <stop offset="100%" stop-color="#498a14" />
            </linearGradient>

            <linearGradient id="neonVisor" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#ff007f" />
              <stop offset="50%" stop-color="#ffe600" />
              <stop offset="100%" stop-color="#00f0ff" />
            </linearGradient>

            <linearGradient id="neonHeadphones" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#00f0ff" />
              <stop offset="100%" stop-color="#0284c7" />
            </linearGradient>

            <filter id="neonPartyGlow">
              <feGaussianBlur stdDeviation="3" result="glow" />
              <feMerge>
                <feMergeNode in="glow" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Party Vibe Shirt with Cyber Matrix Pattern */}
          <path
            d="M25 200 C45 175 75 168 120 168 C165 168 195 175 215 200 L230 240 L10 240 Z"
            fill="#091422"
            stroke="#39ff14"
            stroke-width="2"
            stroke-opacity="0.5"
          />
          {/* Cyber Equalizer lines on shirt */}
          <path d="M90 205 L90 190" stroke="#39ff14" stroke-width="3" stroke-linecap="round" />
          <path d="M100 208 L100 182" stroke="#00f0ff" stroke-width="3" stroke-linecap="round" />
          <path d="M110 210 L110 176" stroke="#ff007f" stroke-width="3" stroke-linecap="round" />
          <path d="M120 212 L120 172" stroke="#ffe600" stroke-width="3" stroke-linecap="round" />
          <path d="M130 210 L130 178" stroke="#ff007f" stroke-width="3" stroke-linecap="round" />
          <path d="M140 208 L140 184" stroke="#00f0ff" stroke-width="3" stroke-linecap="round" />
          <path d="M150 205 L150 192" stroke="#39ff14" stroke-width="3" stroke-linecap="round" />

          {/* DJ Headphones Band Over Head */}
          <path
            d="M40 92 C38 30 202 30 200 92"
            fill="none"
            stroke="url(#neonHeadphones)"
            stroke-width="9"
            stroke-linecap="round"
          />
          <path
            d="M50 82 C50 40 190 40 190 82"
            fill="none"
            stroke="#00f0ff"
            stroke-width="2"
            stroke-opacity="0.8"
          />

          {/* Pepe Head Outline */}
          <path
            d="M48 130 C36 110 38 80 46 64 C58 42 90 38 120 38 C158 38 190 46 196 70 C204 94 200 120 184 136 C174 148 158 156 130 158 C92 160 62 148 48 130 Z"
            fill="url(#pepePartySkin)"
            stroke="#1b3809"
            stroke-width="4.5"
            stroke-linejoin="round"
          />

          {/* DJ Headphone Earcups with Pulsing RGB Ring */}
          {/* Left Earcup */}
          <g>
            <rect x="24" y="80" width="22" height="36" rx="8" fill="#0f172a" stroke="#00f0ff" stroke-width="3" />
            <circle cx="35" cy="98" r="6" fill="#39ff14" className="animate-ping" opacity="0.6" />
          </g>
          {/* Right Earcup */}
          <g>
            <rect x="194" y="80" width="22" height="36" rx="8" fill="#0f172a" stroke="#00f0ff" stroke-width="3" />
            <circle cx="205" cy="98" r="6" fill="#39ff14" className="animate-ping" opacity="0.6" />
          </g>

          {/* CYBERPUNK NEON VISOR SUNGLASSES (Sleek Tron wrap-around visor) */}
          <g filter="url(#neonPartyGlow)">
            {/* Dark Visor Base */}
            <path
              d="M45 74 C75 64 165 64 195 74 L190 102 C155 110 85 110 50 102 Z"
              fill="#060913"
              stroke="#00f0ff"
              stroke-width="2.5"
            />
            {/* Glowing Neon Visor Mirror Strip */}
            <path
              d="M50 78 C76 70 164 70 190 78 L186 96 C152 104 88 104 54 96 Z"
              fill="url(#neonVisor)"
              opacity="0.95"
            />
            {/* Cyber Visor HUD Scan Lines */}
            <line x1="58" y1="86" x2="182" y2="86" stroke="#ffffff" stroke-width="1.2" stroke-opacity="0.7" />
            <circle cx="70" cy="86" r="2" fill="#ffffff" />
            <circle cx="170" cy="86" r="2" fill="#ffffff" />
          </g>

          {/* Cheerful Nostrils */}
          <ellipse cx="108" cy="118" rx="3.5" ry="4" fill="#1b3809" />
          <ellipse cx="128" cy="118" rx="3.5" ry="4" fill="#1b3809" />

          {/* Cool Smirking Vibing Mouth */}
          <g>
            <path
              d="M68 136 C88 132 140 130 172 136 C168 152 138 160 114 158 C88 156 72 148 68 136 Z"
              fill="#2e5414"
              stroke="#1b3809"
              stroke-width="4"
            />
            {/* Pouty Cool Smirk Lip */}
            <path
              d="M66 136 Q118 130 174 136"
              fill="none"
              stroke="#1b3809"
              stroke-width="4.5"
              stroke-linecap="round"
            />
          </g>

          {/* VIBING DANCING HANDS (Hands in the air partying) */}
          {/* Left Dancing Hand */}
          <g transform="translate(-10, -5)">
            <path
              d="M38 175 C30 155 24 130 20 110 C25 106 32 110 32 118 L34 138 C38 130 46 132 46 142 L45 158"
              fill="#6ec228"
              stroke="#1b3809"
              stroke-width="3"
            />
            {/* Glowing Neon Green Glowstick in hand */}
            <line
              x1="12"
              y1="95"
              x2="28"
              y2="135"
              stroke="#39ff14"
              stroke-width="5"
              stroke-linecap="round"
              filter="url(#neonPartyGlow)"
            />
          </g>

          {/* Right Dancing Hand */}
          <g transform="translate(10, -5)">
            <path
              d="M202 175 C210 155 216 130 220 110 C215 106 208 110 208 118 L206 138 C202 130 194 132 194 142 L195 158"
              fill="#6ec228"
              stroke="#1b3809"
              stroke-width="3"
            />
            {/* Glowing Neon Magenta Glowstick in hand */}
            <line
              x1="228"
              y1="95"
              x2="212"
              y2="135"
              stroke="#ff007f"
              stroke-width="5"
              stroke-linecap="round"
              filter="url(#neonPartyGlow)"
            />
          </g>

          {/* Cyber Ring Orbit */}
          <ellipse
            cx="120"
            cy="110"
            rx="85"
            ry="75"
            fill="none"
            stroke="#39ff14"
            stroke-width="1.2"
            stroke-dasharray="10 6"
            className="opacity-0 group-hover:opacity-70 transition-opacity"
          />
        </svg>
      </div>

      {/* Cyber Tag */}
      <div className="mt-2 text-center">
        <span className="inline-block px-2 py-0.5 text-[10px] font-code tracking-wider uppercase bg-lime-950/70 text-lime-400 border border-lime-500/40 rounded">
          SUB-03 // DANCING_PEPE
        </span>
      </div>
    </div>
  );
};
