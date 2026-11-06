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
        <div className="absolute -top-12 left-1/2 -translate-x-1/2 z-30 whitespace-nowrap px-3 py-1 bg-cyan-950/90 border border-cyan-400 rounded text-cyan-300 text-xs font-code shadow-[0_0_15px_rgba(0,240,255,0.6)] animate-bounce">
          💔 FEELS BAD MAN... ({comfortCount} hugs sent)
        </div>
      )}

      {/* Pepe SVG Vector */}
      <div className="relative animate-pepe-cry">
        <svg
          viewBox="0 0 240 240"
          className="w-full h-auto drop-shadow-[0_0_20px_rgba(0,240,255,0.3)] transition-all group-hover:drop-shadow-[0_0_30px_rgba(0,240,255,0.6)]"
        >
          <defs>
            <linearGradient id="pepeSadSkin" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#6ea837" />
              <stop offset="60%" stop-color="#558f27" />
              <stop offset="100%" stop-color="#3c6b19" />
            </linearGradient>

            <linearGradient id="pepeSadLip" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#3a5e1a" />
              <stop offset="100%" stop-color="#264110" />
            </linearGradient>

            <linearGradient id="tearGlow" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#00f0ff" stop-opacity="0.9" />
              <stop offset="50%" stop-color="#38bdf8" stop-opacity="1" />
              <stop offset="100%" stop-color="#80e5ff" stop-opacity="0.4" />
            </linearGradient>

            <filter id="neonTearGlow">
              <feGaussianBlur stdDeviation="2.5" result="glow" />
              <feMerge>
                <feMergeNode in="glow" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Blue Cyber Hood / Shirt */}
          <path
            d="M30 195 C45 175 75 165 120 165 C165 165 195 175 210 195 L225 240 L15 240 Z"
            fill="#1e293b"
            stroke="#00f0ff"
            stroke-width="2"
            stroke-opacity="0.4"
          />
          <path d="M90 170 L120 205 L150 170" fill="none" stroke="#00f0ff" stroke-width="1.5" stroke-opacity="0.5" />

          {/* Pepe Head Outline */}
          <path
            d="M48 135 C38 120 36 90 44 70 C54 48 85 40 120 40 C160 40 190 50 198 75 C206 100 200 125 186 142 C178 152 165 162 142 166 C105 172 65 160 48 135 Z"
            fill="url(#pepeSadSkin)"
            stroke="#1b3809"
            stroke-width="4.5"
            stroke-linejoin="round"
          />

          {/* Forehead wrinkles of deep sadness */}
          <path d="M78 58 Q120 50 162 58" fill="none" stroke="#2c5013" stroke-width="3" stroke-linecap="round" />
          <path d="M85 68 Q120 62 155 68" fill="none" stroke="#2c5013" stroke-width="2.5" stroke-linecap="round" />

          {/* Left Eye (Sad, droopy, watery) */}
          <g transform="translate(0, 0)">
            {/* Eye Sockets */}
            <ellipse cx="82" cy="92" rx="28" ry="24" fill="#2d5214" />
            {/* Sclera */}
            <path
              d="M58 96 C62 80 82 76 104 84 C108 98 98 108 80 108 C66 108 58 102 58 96 Z"
              fill="#f1f5f9"
              stroke="#1b3809"
              stroke-width="3"
            />
            {/* Pupil Looking Down and Wet */}
            <ellipse cx="84" cy="98" rx="10" ry="11" fill="#0f172a" />
            <circle cx="81" cy="94" r="3.5" fill="#ffffff" />
            <circle cx="87" cy="101" r="1.5" fill="#00f0ff" />
            {/* Heavy Sad Upper Eyelid droop */}
            <path
              d="M54 84 C70 94 94 92 108 86 C106 74 88 74 68 76 Z"
              fill="#4d8222"
              stroke="#1b3809"
              stroke-width="2.5"
            />
          </g>

          {/* Right Eye (Sad, droopy, watery) */}
          <g transform="translate(0, 0)">
            {/* Eye Sockets */}
            <ellipse cx="152" cy="94" rx="28" ry="24" fill="#2d5214" />
            {/* Sclera */}
            <path
              d="M130 98 C134 82 154 78 174 86 C178 100 168 110 150 110 C136 110 130 104 130 98 Z"
              fill="#f1f5f9"
              stroke="#1b3809"
              stroke-width="3"
            />
            {/* Pupil */}
            <ellipse cx="148" cy="100" rx="10" ry="11" fill="#0f172a" />
            <circle cx="145" cy="96" r="3.5" fill="#ffffff" />
            <circle cx="151" cy="103" r="1.5" fill="#00f0ff" />
            {/* Upper eyelid */}
            <path
              d="M126 86 C142 96 166 94 178 88 C176 76 158 76 138 78 Z"
              fill="#4d8222"
              stroke="#1b3809"
              stroke-width="2.5"
            />
          </g>

          {/* Sad Nostrils */}
          <ellipse cx="106" cy="116" rx="3.5" ry="4.5" fill="#1b3809" />
          <ellipse cx="124" cy="116" rx="3.5" ry="4.5" fill="#1b3809" />

          {/* Iconic Sad Pepe Downturned Mouth */}
          <g>
            {/* Quivering downturned mouth line */}
            <path
              d="M60 148 C80 136 100 134 118 136 C138 134 160 137 175 152"
              fill="none"
              stroke="#1a340a"
              stroke-width="5"
              stroke-linecap="round"
            />
            {/* Big pouty sorrowful bottom lip */}
            <path
              d="M68 147 C92 165 140 166 166 150 C154 163 118 170 82 162 Z"
              fill="url(#pepeSadLip)"
              stroke="#1a340a"
              stroke-width="3"
            />
          </g>

          {/* ANIMATED NEON CYAN TEARS (Cascading Down Cheeks) */}
          <g filter="url(#neonTearGlow)">
            {/* Left Eye Tears */}
            <path
              d="M78 106 Q72 135 68 180"
              fill="none"
              stroke="url(#tearGlow)"
              stroke-width="5"
              stroke-linecap="round"
              className="animate-tear-left"
            />
            <circle cx="68" cy="180" r="4" fill="#00f0ff" className="animate-pulse" />

            {/* Right Eye Tears */}
            <path
              d="M152 108 Q158 138 162 185"
              fill="none"
              stroke="url(#tearGlow)"
              stroke-width="5"
              stroke-linecap="round"
              className="animate-tear-right"
            />
            <circle cx="162" cy="185" r="4" fill="#00f0ff" className="animate-pulse" />

            {/* Droplets pooling near chin */}
            <circle cx="70" cy="155" r="3" fill="#80e5ff" opacity="0.8" />
            <circle cx="160" cy="158" r="3" fill="#80e5ff" opacity="0.8" />
          </g>

          {/* PepeHands Hands Clutched In Sorrow */}
          <g transform="translate(0, 10)">
            {/* Left Hand reaching up */}
            <path
              d="M45 200 C40 185 55 170 65 182 C72 172 82 176 82 186 C88 180 96 186 92 196 C90 205 75 220 55 215 Z"
              fill="#558f27"
              stroke="#1b3809"
              stroke-width="3"
            />
            {/* Right Hand reaching up */}
            <path
              d="M195 200 C200 185 185 170 175 182 C168 172 158 176 158 186 C152 180 144 186 148 196 C150 205 165 220 185 215 Z"
              fill="#558f27"
              stroke="#1b3809"
              stroke-width="3"
            />
          </g>

          {/* Cyber HUD Targeting Reticle overlay on hover */}
          <circle
            cx="120"
            cy="110"
            r="85"
            fill="none"
            stroke="#00f0ff"
            stroke-width="1"
            stroke-dasharray="8 6"
            className="opacity-0 group-hover:opacity-40 transition-opacity"
          />
        </svg>
      </div>

      {/* Cyber Tag */}
      <div className="mt-2 text-center">
        <span className="inline-block px-2 py-0.5 text-[10px] font-code tracking-wider uppercase bg-cyan-950/70 text-cyan-400 border border-cyan-500/40 rounded">
          SUB-01 // CRYING_PEPE
        </span>
      </div>
    </div>
  );
};
