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

    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const x = (rect.left + rect.width / 2) / window.innerWidth;
    const y = (rect.top + rect.height / 2) / window.innerHeight;

    confetti({
      particleCount: 45,
      spread: 70,
      origin: { x, y },
      colors: ['#39ff14', '#00f0ff', '#ff007f', '#ffe600'],
      disableForReducedMotion: true,
    });
  };

  return (
    <div
      onClick={handlePartyBurst}
      className={`relative group cursor-pointer transition-transform duration-300 ${isInspected ? 'scale-105' : ''} ${className}`}
      title="Click for PepePls Dance Overdrive & Confetti!"
    >
      {/* Floating Rave Status on Interaction */}
      {raveMode && (
        <div className="absolute -top-12 left-1/2 -translate-x-1/2 z-30 whitespace-nowrap px-3 py-1 bg-lime-950/95 border border-lime-400 rounded text-lime-300 text-xs font-cyber shadow-[0_0_20px_rgba(57,255,20,0.8)] animate-pulse">
          🐸 PEPEPLS DANCE: {128 + vibeCount * 2} BPM!
        </div>
      )}

      {/* Authentic Full-Body Dancing Pepe SVG (Exact match to Geronimo's Reference Image) */}
      <div className={`relative ${raveMode ? 'animate-bounce' : 'animate-pepe-dance'}`}>
        <svg
          viewBox="0 0 240 270"
          className="w-full h-auto drop-shadow-[0_0_22px_rgba(57,255,20,0.4)] transition-all group-hover:drop-shadow-[0_0_36px_rgba(57,255,20,0.75)]"
        >
          <defs>
            <linearGradient id="authPepeDanceSkin" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#65a437" />
              <stop offset="55%" stopColor="#528b29" />
              <stop offset="100%" stopColor="#3d6c1b" />
            </linearGradient>

            <linearGradient id="authPepeDanceLips" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#c64e2e" />
              <stop offset="100%" stopColor="#99361b" />
            </linearGradient>
          </defs>

          {/* Neon Dance Floor Pulse Under Pepe's Feet */}
          <ellipse cx="120" cy="256" rx="54" ry="7" fill="#39ff14" opacity="0.25" className="animate-pulse" />

          {/* Full Standing Frog Legs (Exact Reference Proportions) */}
          <path
            d="M92 222 L91 252 C91 258 105 258 106 252 L108 224 Z"
            fill="url(#authPepeDanceSkin)"
            stroke="#142409"
            strokeWidth="3.5"
            strokeLinejoin="round"
          />
          <path
            d="M135 222 L137 255 C137 261 151 261 152 255 L149 222 Z"
            fill="url(#authPepeDanceSkin)"
            stroke="#142409"
            strokeWidth="3.5"
            strokeLinejoin="round"
          />

          {/* Full Standing Frog Torso / Belly (Exact Reference Silhouette) */}
          <path
            d="M84 140 C76 168 75 204 85 224 C96 232 145 232 156 224 C165 202 164 162 152 136 Z"
            fill="url(#authPepeDanceSkin)"
            stroke="#142409"
            strokeWidth="3.8"
            strokeLinejoin="round"
          />

          {/* Authentic Two-Dome Pepe Head & Cheeks */}
          <path
            d="M54 112 C42 98 48 76 64 70 C66 48 84 36 106 42 C116 30 144 30 156 48 C174 56 184 78 180 104 C178 126 162 142 138 144 C102 148 64 138 54 112 Z"
            fill="url(#authPepeDanceSkin)"
            stroke="#142409"
            strokeWidth="3.8"
            strokeLinejoin="round"
          />

          {/* Brow & Upper Eyelid Wrinkle Lines (From Reference Image) */}
          <path d="M62 66 Q84 54 106 64" fill="none" stroke="#182b0b" strokeWidth="2.5" strokeLinecap="round" />
          <path d="M106 64 Q134 52 160 66" fill="none" stroke="#182b0b" strokeWidth="2.5" strokeLinecap="round" />
          <path d="M60 72 Q84 62 106 70" fill="none" stroke="#182b0b" strokeWidth="2.2" strokeLinecap="round" />
          <path d="M108 70 Q134 60 162 72" fill="none" stroke="#182b0b" strokeWidth="2.2" strokeLinecap="round" />

          {/* Left Bulging Pepe Eye (White Sclera + Double-Highlight Black Pupil) */}
          <g>
            <path
              d="M52 83 C56 71 94 70 104 82 C104 94 88 99 72 98 C56 97 50 90 52 83 Z"
              fill="#ffffff"
              stroke="#142409"
              strokeWidth="3"
            />
            <ellipse cx="76" cy="87" rx="10" ry="9.5" fill="#090d16" />
            <circle cx="72" cy="84" r="3.2" fill="#ffffff" />
            <circle cx="79" cy="90" r="1.8" fill="#ffffff" />
            {/* Heavy Green Upper Eyelid */}
            <path
              d="M52 80 C68 72 90 72 104 80"
              fill="none"
              stroke="#142409"
              strokeWidth="3"
              strokeLinecap="round"
            />
            <path d="M58 100 Q80 105 98 97" fill="none" stroke="#182b0b" strokeWidth="2" strokeLinecap="round" />
          </g>

          {/* Right Bulging Pepe Eye */}
          <g>
            <path
              d="M106 82 C112 70 148 70 158 83 C156 95 140 100 124 99 C110 98 104 90 106 82 Z"
              fill="#ffffff"
              stroke="#142409"
              strokeWidth="3"
            />
            <ellipse cx="127" cy="87" rx="10" ry="9.5" fill="#090d16" />
            <circle cx="123" cy="84" r="3.2" fill="#ffffff" />
            <circle cx="130" cy="90" r="1.8" fill="#ffffff" />
            {/* Heavy Green Upper Eyelid */}
            <path
              d="M106 80 C120 72 144 72 158 82"
              fill="none"
              stroke="#142409"
              strokeWidth="3"
              strokeLinecap="round"
            />
            <path d="M110 101 Q132 106 152 98" fill="none" stroke="#182b0b" strokeWidth="2" strokeLinecap="round" />
          </g>

          {/* Authentic Thick Reddish-Brown Pepe Lips (Exact Reference Shape & Color) */}
          <g>
            <path
              d="M50 116 C72 118 116 116 144 112 C150 118 148 128 138 129 C112 132 74 134 54 129 C46 127 46 119 50 116 Z"
              fill="url(#authPepeDanceLips)"
              stroke="#142409"
              strokeWidth="3"
              strokeLinejoin="round"
            />
            {/* Center Lip Line */}
            <path
              d="M52 122 C78 125 114 123 144 119"
              fill="none"
              stroke="#142409"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
            {/* Cheek Corner Smile Dimple */}
            <path d="M145 110 Q151 116 147 124" fill="none" stroke="#142409" strokeWidth="2.2" strokeLinecap="round" />
          </g>

          {/* Left Arm Hanging & Swaying to the Beat (Exact Reference Pose) */}
          <path
            d="M84 150 C74 162 70 182 74 194 C77 200 86 198 86 190 C85 180 87 168 91 160"
            fill="url(#authPepeDanceSkin)"
            stroke="#142409"
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Right Arm Raised & Waving Upward (Exact Reference Pose!) */}
          <path
            d="M146 156 C162 150 168 120 158 102 C152 94 142 98 144 110 C146 122 143 138 137 146"
            fill="url(#authPepeDanceSkin)"
            stroke="#142409"
            strokeWidth="3.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>

      {/* Cyber Tag */}
      <div className="mt-1 text-center">
        <span className="inline-block px-2 py-0.5 text-[10px] font-code tracking-wider uppercase bg-lime-950/70 text-lime-400 border border-lime-500/40 rounded">
          SUB-03 // DANCING_PEPE
        </span>
      </div>
    </div>
  );
};
