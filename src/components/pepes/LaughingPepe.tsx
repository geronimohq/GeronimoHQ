import React, { useState } from 'react';

interface LaughingPepeProps {
  className?: string;
  isInspected?: boolean;
}

export const LaughingPepe: React.FC<LaughingPepeProps> = ({ className = '', isInspected = false }) => {
  const [floatingLols, setFloatingLols] = useState<{ id: number; text: string; x: number }[]>([]);

  const handleLaughClick = () => {
    const phrases = ['KEKW', 'OMEGALUL', 'HE DOESN\'T KNOW!', 'LMAOOOO', 'LOOK AT HIM!'];
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

      {/* Laughing Animated Container */}
      <div className="relative animate-pepe-laugh">
        <svg
          viewBox="0 0 240 240"
          className="w-full h-auto drop-shadow-[0_0_20px_rgba(255,0,127,0.35)] transition-all group-hover:drop-shadow-[0_0_35px_rgba(255,0,127,0.7)]"
        >
          <defs>
            <linearGradient id="pepeLaughSkin" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#80cc38" />
              <stop offset="50%" stop-color="#64a827" />
              <stop offset="100%" stop-color="#467e16" />
            </linearGradient>

            <linearGradient id="pepeMouthDark" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#2a0d17" />
              <stop offset="100%" stop-color="#6e102e" />
            </linearGradient>

            <linearGradient id="pepeTongue" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#ff4d88" />
              <stop offset="100%" stop-color="#cc2055" />
            </linearGradient>

            <filter id="neonLaughGlow">
              <feGaussianBlur stdDeviation="3" result="glow" />
              <feMerge>
                <feMergeNode in="glow" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Cyberpunk Neon Collared Jacket */}
          <path
            d="M30 200 C50 178 80 170 120 170 C160 170 190 178 210 200 L228 240 L12 240 Z"
            fill="#120c1e"
            stroke="#ff007f"
            stroke-width="2"
            stroke-opacity="0.6"
          />
          {/* Cyberpunk glowing lapel */}
          <path d="M85 174 L120 215 L155 174" fill="none" stroke="#ff007f" stroke-width="2" stroke-opacity="0.8" />

          {/* Pepe Laughing Head Outline (Tilted with hysterical glee) */}
          <path
            d="M50 125 C38 105 38 75 48 56 C60 35 95 30 135 32 C172 34 200 48 206 72 C214 98 206 122 188 138 C176 150 158 158 130 160 C90 162 62 148 50 125 Z"
            fill="url(#pepeLaughSkin)"
            stroke="#1b3809"
            stroke-width="4.5"
            stroke-linejoin="round"
          />

          {/* Joyful laughter wrinkles on forehead and brow */}
          <path d="M88 48 Q125 42 165 52" fill="none" stroke="#366314" stroke-width="3" stroke-linecap="round" />
          <path d="M96 58 Q125 54 158 62" fill="none" stroke="#366314" stroke-width="2.5" stroke-linecap="round" />

          {/* Left Eye: Squinted into joyful crescent shape with crow's feet wrinkles */}
          <g transform="translate(0, 0)">
            {/* Eye socket hollow */}
            <ellipse cx="86" cy="80" rx="26" ry="18" fill="#325a15" />
            {/* Squinted Happy Eyelid Arcs (iconic laughing squint) */}
            <path
              d="M62 82 Q86 68 110 80"
              fill="none"
              stroke="#1b3809"
              stroke-width="5"
              stroke-linecap="round"
            />
            {/* Sclera sliver */}
            <path d="M66 82 Q86 74 106 82 Q86 86 66 82 Z" fill="#ffffff" />
            <ellipse cx="86" cy="80" rx="5" ry="4" fill="#0f172a" />
            {/* Laugh wrinkle crow's feet */}
            <path d="M56 80 L64 82" stroke="#1b3809" stroke-width="2.5" stroke-linecap="round" />
            <path d="M57 74 L65 79" stroke="#1b3809" stroke-width="2.5" stroke-linecap="round" />
            <path d="M58 88 L65 85" stroke="#1b3809" stroke-width="2.5" stroke-linecap="round" />
          </g>

          {/* Right Eye: Squinted mocking crescent */}
          <g transform="translate(0, 0)">
            <ellipse cx="152" cy="84" rx="26" ry="18" fill="#325a15" />
            <path
              d="M128 86 Q152 72 176 84"
              fill="none"
              stroke="#1b3809"
              stroke-width="5"
              stroke-linecap="round"
            />
            <path d="M132 86 Q152 78 172 86 Q152 90 132 86 Z" fill="#ffffff" />
            <ellipse cx="152" cy="84" rx="5" ry="4" fill="#0f172a" />
            {/* Crow's feet wrinkles */}
            <path d="M174 84 L182 82" stroke="#1b3809" stroke-width="2.5" stroke-linecap="round" />
            <path d="M173 78 L181 74" stroke="#1b3809" stroke-width="2.5" stroke-linecap="round" />
            <path d="M173 89 L180 92" stroke="#1b3809" stroke-width="2.5" stroke-linecap="round" />
          </g>

          {/* Cheerful Cheek Bulges */}
          <path d="M54 100 Q65 118 78 114" fill="none" stroke="#2a4c10" stroke-width="3" stroke-linecap="round" />
          <path d="M184 102 Q172 120 160 116" fill="none" stroke="#2a4c10" stroke-width="3" stroke-linecap="round" />

          {/* Snickering Nostrils */}
          <ellipse cx="108" cy="102" rx="4" ry="5" fill="#1b3809" />
          <ellipse cx="128" cy="103" rx="4" ry="5" fill="#1b3809" />

          {/* HUGE MOCKING LAUGHING MOUTH */}
          <g>
            {/* Giant open mouth cavity */}
            <path
              d="M58 118 C85 110 152 110 182 122 C184 156 160 178 120 178 C78 178 56 154 58 118 Z"
              fill="url(#pepeMouthDark)"
              stroke="#1b3809"
              stroke-width="4.5"
            />
            {/* Pink bouncy tongue inside mouth */}
            <path
              d="M84 158 C96 140 144 140 156 158 C144 172 96 172 84 158 Z"
              fill="url(#pepeTongue)"
            />
            {/* Upper lip outline */}
            <path
              d="M52 118 Q120 106 186 122"
              fill="none"
              stroke="#1b3809"
              stroke-width="5"
              stroke-linecap="round"
            />
            {/* Big smiling lower lip ridge */}
            <path
              d="M62 176 Q120 188 178 176"
              fill="none"
              stroke="#325a15"
              stroke-width="4"
              stroke-linecap="round"
            />
          </g>

          {/* POINTING HAND (Mocking right at Crying Pepe!) */}
          <g transform="translate(10, 0)">
            {/* Wrist / Arm coming forward */}
            <path
              d="M0 180 C20 175 40 175 55 185 L50 205 C35 198 15 198 0 205 Z"
              fill="#558f27"
              stroke="#1b3809"
              stroke-width="3"
            />
            {/* Pointing Index Finger aiming left towards Crying Pepe */}
            <path
              d="M55 185 C40 185 20 185 8 186 C2 186 -2 192 4 196 C14 198 32 196 52 198 Z"
              fill="#74be42"
              stroke="#1b3809"
              stroke-width="3.5"
            />
            {/* Clenched other knuckles */}
            <circle cx="58" cy="192" r="8" fill="#5c9a29" stroke="#1b3809" stroke-width="2.5" />
            <circle cx="68" cy="195" r="7.5" fill="#528a24" stroke="#1b3809" stroke-width="2.5" />
            <circle cx="76" cy="200" r="7" fill="#46771e" stroke="#1b3809" stroke-width="2.5" />
            {/* Thumb resting on fist */}
            <path d="M52 183 C58 174 68 176 68 186 Z" fill="#64a827" stroke="#1b3809" stroke-width="2" />
          </g>

          {/* Neon Hologram Cyber Aura */}
          <circle
            cx="120"
            cy="110"
            r="88"
            fill="none"
            stroke="#ff007f"
            stroke-width="1.2"
            stroke-dasharray="12 8"
            className="opacity-0 group-hover:opacity-60 transition-opacity"
          />
        </svg>
      </div>

      {/* Cyber Tag */}
      <div className="mt-2 text-center">
        <span className="inline-block px-2 py-0.5 text-[10px] font-code tracking-wider uppercase bg-fuchsia-950/70 text-fuchsia-400 border border-fuchsia-500/40 rounded">
          SUB-02 // LAUGHING_PEPE
        </span>
      </div>
    </div>
  );
};
