import React, { useState } from 'react';

interface LaughingPepeProps {
  className?: string;
  isInspected?: boolean;
}

export const LaughingPepe: React.FC<LaughingPepeProps> = ({ className = '', isInspected = false }) => {
  const [floatingLols, setFloatingLols] = useState<{ id: number; text: string; x: number }[]>([]);

  const handleLaughClick = () => {
    const phrases = ['KEKW', 'OMEGALUL', "HE DOESN'T KNOW!", 'PEPELAUGH', 'LOOK AT HIM! 😂'];
    const newLol = {
      id: Date.now() + Math.random(),
      text: phrases[Math.floor(Math.random() * phrases.length)],
      x: (Math.random() - 0.5) * 60,
    };

    setFloatingLols((prev) => [...prev.slice(-4), newLol]);
    setTimeout(() => {
      setFloatingLols((prev) => prev.filter((item) => item.id !== newLol.id));
    }, 1800);
  };

  return (
    <div
      onClick={handleLaughClick}
      className={`relative group cursor-pointer transition-transform duration-300 ${isInspected ? 'scale-105' : ''} ${className}`}
      title="Click to laugh with Pepe"
    >
      {/* Floating KEKW Text Popups */}
      {floatingLols.map((lol) => (
        <div
          key={lol.id}
          style={{ transform: `translateX(${lol.x}px)` }}
          className="absolute -top-10 left-1/2 -translate-x-1/2 z-30 pointer-events-none whitespace-nowrap px-2.5 py-1 bg-fuchsia-950/95 border border-fuchsia-400 rounded text-fuchsia-300 font-cyber font-bold text-xs shadow-[0_0_20px_rgba(255,0,127,0.8)] animate-bounce"
        >
          {lol.text}
        </div>
      ))}

      {/* Authentic Full-Body Laughing Pepe SVG */}
      <div className="relative animate-pepe-laugh">
        <svg
          viewBox="0 0 240 270"
          className="w-full h-auto drop-shadow-[0_0_20px_rgba(255,0,127,0.35)] transition-all group-hover:drop-shadow-[0_0_35px_rgba(255,0,127,0.7)]"
        >
          <defs>
            <linearGradient id="authPepeLaughSkin" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#66a638" />
              <stop offset="55%" stopColor="#528c29" />
              <stop offset="100%" stopColor="#3e6d1c" />
            </linearGradient>

            <linearGradient id="authPepeLaughLips" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#c95232" />
              <stop offset="100%" stopColor="#9c381c" />
            </linearGradient>
          </defs>

          {/* Full Standing Frog Legs (Bouncing with laughter) */}
          <path
            d="M92 222 L88 252 C88 258 102 258 104 252 L107 224 Z"
            fill="url(#authPepeLaughSkin)"
            stroke="#142409"
            strokeWidth="3.5"
            strokeLinejoin="round"
          />
          <path
            d="M135 222 L139 254 C139 260 153 260 154 254 L150 222 Z"
            fill="url(#authPepeLaughSkin)"
            stroke="#142409"
            strokeWidth="3.5"
            strokeLinejoin="round"
          />

          {/* Full Standing Frog Torso / Belly */}
          <path
            d="M82 140 C73 168 74 205 84 224 C96 233 146 233 158 224 C167 202 166 162 154 136 Z"
            fill="url(#authPepeLaughSkin)"
            stroke="#142409"
            strokeWidth="3.8"
            strokeLinejoin="round"
          />

          {/* Authentic Two-Dome Pepe Head Tilted Back Laughing */}
          <path
            d="M52 110 C40 94 46 72 64 66 C66 44 86 32 108 38 C118 26 146 28 158 46 C176 54 186 78 182 104 C178 128 160 144 136 146 C98 148 62 136 52 110 Z"
            fill="url(#authPepeLaughSkin)"
            stroke="#142409"
            strokeWidth="3.8"
            strokeLinejoin="round"
          />

          {/* Expressive Pepe Brow Wrinkles */}
          <path d="M62 62 Q84 50 106 60" fill="none" stroke="#182b0b" strokeWidth="2.5" strokeLinecap="round" />
          <path d="M108 60 Q136 48 162 62" fill="none" stroke="#182b0b" strokeWidth="2.5" strokeLinecap="round" />

          {/* Left Bulging Pepe Eye (Squinted with Joy + Laugh Tear) */}
          <g>
            <path
              d="M54 80 C58 66 94 66 104 78 C104 90 88 94 72 93 C58 92 52 86 54 80 Z"
              fill="#ffffff"
              stroke="#142409"
              strokeWidth="3"
            />
            <ellipse cx="78" cy="81" rx="8.5" ry="7.5" fill="#090d16" />
            <circle cx="75" cy="78" r="2.8" fill="#ffffff" />
            {/* Happy Squinting Upper & Lower Eyelid Folds */}
            <path
              d="M53 76 C68 66 90 66 104 76"
              fill="none"
              stroke="#142409"
              strokeWidth="3.5"
              strokeLinecap="round"
            />
            <path
              d="M56 91 Q80 84 102 90"
              fill="none"
              stroke="#142409"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
            {/* Joy Tear Droplet */}
            <path d="M52 86 C45 90 45 98 52 98 C56 98 56 90 52 86 Z" fill="#38bdf8" stroke="#142409" strokeWidth="1.5" />
          </g>

          {/* Right Bulging Pepe Eye (Squinted with Joy + Laugh Tear) */}
          <g>
            <path
              d="M106 80 C112 66 148 66 158 79 C156 91 140 95 124 94 C110 93 104 86 106 80 Z"
              fill="#ffffff"
              stroke="#142409"
              strokeWidth="3"
            />
            <ellipse cx="128" cy="81" rx="8.5" ry="7.5" fill="#090d16" />
            <circle cx="125" cy="78" r="2.8" fill="#ffffff" />
            <path
              d="M106 76 C120 66 144 66 158 77"
              fill="none"
              stroke="#142409"
              strokeWidth="3.5"
              strokeLinecap="round"
            />
            <path
              d="M108 91 Q132 84 156 91"
              fill="none"
              stroke="#142409"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
            {/* Joy Tear Droplet */}
            <path d="M160 86 C167 90 167 98 160 98 C156 98 156 90 160 86 Z" fill="#38bdf8" stroke="#142409" strokeWidth="1.5" />
          </g>

          {/* Authentic Thick Reddish-Brown Pepe Lips Stretched in Huge Laugh */}
          <g>
            {/* Outer Reddish-Brown Lips */}
            <path
              d="M48 106 C76 100 124 100 156 108 C162 128 140 144 102 144 C64 144 44 126 48 106 Z"
              fill="url(#authPepeLaughLips)"
              stroke="#142409"
              strokeWidth="3.2"
              strokeLinejoin="round"
            />
            {/* Open Laughing Mouth Cavity */}
            <path
              d="M58 112 C82 108 122 108 146 114 C146 128 128 136 102 136 C74 136 58 126 58 112 Z"
              fill="#3b0d11"
              stroke="#142409"
              strokeWidth="2.2"
            />
            {/* Tongue */}
            <path
              d="M78 128 C88 120 116 120 126 128 C118 135 86 135 78 128 Z"
              fill="#ff5c77"
            />
          </g>

          {/* Left Arm Pointing & Mocking */}
          <g>
            <path
              d="M82 154 C64 152 44 156 32 162 C26 165 28 174 36 172 C48 170 66 168 82 170"
              fill="url(#authPepeLaughSkin)"
              stroke="#142409"
              strokeWidth="3.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </g>

          {/* Right Arm Holding Belly / Raised in Glee */}
          <path
            d="M150 152 C166 144 174 120 162 104 C156 96 146 102 148 112 C150 124 146 138 140 146"
            fill="url(#authPepeLaughSkin)"
            stroke="#142409"
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>

      {/* Cyber Tag */}
      <div className="mt-1 text-center">
        <span className="inline-block px-2 py-0.5 text-[10px] font-code tracking-wider uppercase bg-fuchsia-950/70 text-fuchsia-400 border border-fuchsia-500/40 rounded">
          SUB-02 // LAUGHING_PEPE
        </span>
      </div>
    </div>
  );
};
