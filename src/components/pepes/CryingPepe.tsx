import React, { useState } from 'react';

interface CryingPepeProps {
  className?: string;
  isInspected?: boolean;
}

export const CryingPepe: React.FC<CryingPepeProps> = ({ className = '', isInspected = false }) => {
  const [comfortCount, setComfortCount] = useState(0);
  const [showMessage, setShowMessage] = useState(false);

  const handleComfort = () => {
    setComfortCount((prev) => prev + 1);
    setShowMessage(true);
    setTimeout(() => setShowMessage(false), 2200);
  };

  return (
    <div
      onClick={handleComfort}
      className={`relative group cursor-pointer transition-transform duration-300 ${isInspected ? 'scale-105' : ''} ${className}`}
      title="Click to comfort Sad Pepe"
    >
      {/* Floating Mood Bubble on Interaction */}
      {showMessage && (
        <div className="absolute -top-12 left-1/2 -translate-x-1/2 z-30 whitespace-nowrap px-3 py-1 bg-cyan-950/95 border border-cyan-400 rounded text-cyan-300 text-xs font-code shadow-[0_0_15px_rgba(0,240,255,0.6)] animate-bounce">
          💔 FEELS BAD MAN... ({comfortCount} hugs sent)
        </div>
      )}

      {/* Authentic Full-Body Crying Pepe SVG */}
      <div className="relative animate-pepe-cry">
        <svg
          viewBox="0 0 240 270"
          className="w-full h-auto drop-shadow-[0_0_20px_rgba(0,240,255,0.35)] transition-all group-hover:drop-shadow-[0_0_32px_rgba(0,240,255,0.7)]"
        >
          <defs>
            <linearGradient id="authPepeSadSkin" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#619e34" />
              <stop offset="55%" stopColor="#4f8828" />
              <stop offset="100%" stopColor="#3c6b1c" />
            </linearGradient>

            <linearGradient id="authPepeSadLips" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#c44d2d" />
              <stop offset="100%" stopColor="#96351b" />
            </linearGradient>

            <linearGradient id="tearGlowStream" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.95" />
              <stop offset="60%" stopColor="#00f0ff" stopOpacity="1" />
              <stop offset="100%" stopColor="#bae6fd" stopOpacity="0.7" />
            </linearGradient>
          </defs>

          {/* Tear Puddle at Pepe's Feet */}
          <ellipse cx="120" cy="256" rx="58" ry="8" fill="#00f0ff" opacity="0.28" className="animate-pulse" />
          <ellipse cx="120" cy="256" rx="36" ry="4.5" fill="#38bdf8" opacity="0.45" />

          {/* Full Standing Frog Legs (Matching Authentic Pepe Reference) */}
          <path
            d="M92 222 L90 252 C90 258 104 258 105 252 L107 224 Z"
            fill="url(#authPepeSadSkin)"
            stroke="#142409"
            strokeWidth="3.5"
            strokeLinejoin="round"
          />
          <path
            d="M134 222 L136 254 C136 260 150 260 151 254 L149 222 Z"
            fill="url(#authPepeSadSkin)"
            stroke="#142409"
            strokeWidth="3.5"
            strokeLinejoin="round"
          />

          {/* Full Standing Frog Torso / Belly */}
          <path
            d="M84 140 C76 168 76 205 85 224 C96 232 145 232 156 224 C165 202 164 162 152 136 Z"
            fill="url(#authPepeSadSkin)"
            stroke="#142409"
            strokeWidth="3.8"
            strokeLinejoin="round"
          />

          {/* Authentic Two-Dome Pepe Head & Cheeks */}
          <path
            d="M54 112 C42 98 48 76 64 70 C66 48 84 36 106 42 C116 30 144 30 156 48 C174 56 184 78 180 104 C178 126 162 142 138 144 C102 148 64 138 54 112 Z"
            fill="url(#authPepeSadSkin)"
            stroke="#142409"
            strokeWidth="3.8"
            strokeLinejoin="round"
          />

          {/* Brow & Eyelid Crease Lines (Authentic Pepe Wrinkles) */}
          <path d="M62 68 Q84 56 106 66" fill="none" stroke="#182b0b" strokeWidth="2.5" strokeLinecap="round" />
          <path d="M106 66 Q134 54 160 68" fill="none" stroke="#182b0b" strokeWidth="2.5" strokeLinecap="round" />
          <path d="M60 74 Q84 64 106 72" fill="none" stroke="#182b0b" strokeWidth="2" strokeLinecap="round" />
          <path d="M108 72 Q134 62 162 74" fill="none" stroke="#182b0b" strokeWidth="2" strokeLinecap="round" />

          {/* Left Bulging Pepe Eye */}
          <g>
            <path
              d="M54 84 C58 72 94 70 104 82 C104 94 88 100 72 99 C58 98 52 91 54 84 Z"
              fill="#ffffff"
              stroke="#142409"
              strokeWidth="3"
            />
            {/* Watery Pupil */}
            <ellipse cx="78" cy="88" rx="9.5" ry="9" fill="#090d16" />
            <circle cx="75" cy="85" r="3" fill="#ffffff" />
            <circle cx="81" cy="91" r="1.8" fill="#ffffff" />
            {/* Heavy Droopy Sad Upper Eyelid */}
            <path
              d="M53 82 C68 74 90 74 104 82 C92 78 68 78 53 82 Z"
              fill="#4f8828"
              stroke="#142409"
              strokeWidth="2.5"
            />
            {/* Lower Eye Bag Wrinkle */}
            <path d="M58 101 Q80 106 98 98" fill="none" stroke="#182b0b" strokeWidth="2" strokeLinecap="round" />
          </g>

          {/* Right Bulging Pepe Eye */}
          <g>
            <path
              d="M106 83 C112 71 148 71 158 84 C156 96 140 101 124 100 C110 99 104 91 106 83 Z"
              fill="#ffffff"
              stroke="#142409"
              strokeWidth="3"
            />
            {/* Watery Pupil */}
            <ellipse cx="128" cy="88" rx="9.5" ry="9" fill="#090d16" />
            <circle cx="125" cy="85" r="3" fill="#ffffff" />
            <circle cx="131" cy="91" r="1.8" fill="#ffffff" />
            {/* Heavy Upper Eyelid */}
            <path
              d="M106 82 C120 74 144 74 158 84 C144 79 120 79 106 82 Z"
              fill="#4f8828"
              stroke="#142409"
              strokeWidth="2.5"
            />
            {/* Lower Eye Bag Wrinkle */}
            <path d="M110 102 Q132 107 152 99" fill="none" stroke="#182b0b" strokeWidth="2" strokeLinecap="round" />
          </g>

          {/* Cascading Waterfall Tears (Animated) */}
          <path
            d="M72 98 Q66 145 74 248"
            fill="none"
            stroke="url(#tearGlowStream)"
            strokeWidth="6"
            strokeLinecap="round"
            className="animate-tear-left"
          />
          <path
            d="M132 99 Q138 145 130 248"
            fill="none"
            stroke="url(#tearGlowStream)"
            strokeWidth="6"
            strokeLinecap="round"
            className="animate-tear-right"
          />

          {/* Authentic Thick Reddish-Brown Pepe Lips (Downturned Sad Frown) */}
          <g>
            <path
              d="M52 122 C74 114 118 114 146 124 C150 132 144 138 134 136 C112 130 76 130 56 135 C48 136 48 126 52 122 Z"
              fill="url(#authPepeSadLips)"
              stroke="#142409"
              strokeWidth="3"
              strokeLinejoin="round"
            />
            {/* Center Lip Line */}
            <path
              d="M54 128 Q98 120 144 130"
              fill="none"
              stroke="#142409"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
          </g>

          {/* Left Arm Hanging Down Sad / Wiping Tear */}
          <path
            d="M84 152 C72 164 68 184 72 196 C75 202 84 200 84 192 C83 182 86 170 90 162"
            fill="url(#authPepeSadSkin)"
            stroke="#142409"
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Right Arm Raised Gently Wiping Eye (PepeHands / Reference Pose) */}
          <path
            d="M148 156 C162 148 168 122 158 106 C153 98 144 102 146 112 C148 124 144 138 138 146"
            fill="url(#authPepeSadSkin)"
            stroke="#142409"
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>

      {/* Cyber Tag */}
      <div className="mt-1 text-center">
        <span className="inline-block px-2 py-0.5 text-[10px] font-code tracking-wider uppercase bg-cyan-950/70 text-cyan-400 border border-cyan-500/40 rounded">
          SUB-01 // CRYING_PEPE
        </span>
      </div>
    </div>
  );
};
