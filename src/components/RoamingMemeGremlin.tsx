import React, { useState, useEffect, useRef } from 'react';
import { safeConfetti } from '../utils/motion';

interface RoamingMemeGremlinProps {
  theme: 'pepe' | 'banana';
  enabled: boolean;
}

export const RoamingMemeGremlin: React.FC<RoamingMemeGremlinProps> = ({ theme, enabled }) => {
  const [pos, setPos] = useState<{ x: number; y: number }>({ x: 180, y: 260 });
  const [isInterrupting, setIsInterrupting] = useState<boolean>(false);
  const [speech, setSpeech] = useState<string>('🕺 Vibe checking your browser...');
  const [facingLeft, setFacingLeft] = useState<boolean>(false);
  const [countdown, setCountdown] = useState<number>(0);

  const lastInterruptRef = useRef<number>(0);
  const interruptTimerRef = useRef<number | null>(null);
  const countdownTimerRef = useRef<number | null>(null);

  const pepeIdleQuips = [
    '🐸 Just gooning around geronimohq.com...',
    '💾 Did you download 128GB of RAM yet?',
    '🧟 GFL is 64/64... arm the Slot Sniper!',
    '🕺 PepePls vibing in your viewport!',
    '👀 Whiffed a point-blank Zeus? FeelsBadMan',
  ];

  const bananaIdleQuips = [
    '🍌 RING RING RING! BANANA PHONE!',
    '📞 Boop-boo-ba-doo-ba-doop!',
    '🕺 Peanut Butter Jelly & Banana Time!',
    '🍌 Potassium levels at maximum capacity!',
    '😂 Watching you browse geronimohq.com!',
  ];

  const pepeInterruptQuips = [
    '🛑 HOLD UP! Mandatory 3s Pepe Dance Vibe Check before you press that!',
    '🐸 NOPE! Let me hit this PepePls dance on your button first!',
    '😂 INTERCEPTED! Wait 3 seconds while I goon right here!',
  ];

  const bananaInterruptQuips = [
    '🍌 BANANA PHONE INTERCEPTION! Answer the call for 3 seconds first!',
    '📞 RING RING! Blocking this button for a quick Banana Dance!',
    '🕺 HOLD UP! Pom-Pom Banana Inspection in progress (3s)!',
  ];

  // Autonomous roaming loop when not interrupting
  useEffect(() => {
    if (!enabled) return;

    const roamInterval = window.setInterval(() => {
      if (isInterrupting) return;
      const vw = Math.max(360, window.innerWidth - 150);
      const vh = Math.max(360, window.innerHeight - 160);
      const nextX = Math.floor(60 + Math.random() * (vw - 100));
      const nextY = Math.floor(90 + Math.random() * (vh - 140));

      setFacingLeft(nextX < pos.x);
      setPos({ x: nextX, y: nextY });

      const list = theme === 'banana' ? bananaIdleQuips : pepeIdleQuips;
      setSpeech(list[Math.floor(Math.random() * list.length)]);
    }, 4500);

    return () => clearInterval(roamInterval);
  }, [enabled, isInterrupting, theme, pos.x]);

  // Listen for user hovering interactive buttons to playfully interrupt them for ~3 seconds
  useEffect(() => {
    if (!enabled) return;

    const handleMouseOver = (e: MouseEvent) => {
      if (isInterrupting) return;
      const now = Date.now();
      // Cooldown of 14 seconds between playful button interruptions so the site stays fun & usable
      if (now - lastInterruptRef.current < 14000) return;

      const target = (e.target as HTMLElement | null)?.closest('button, a');
      if (!target) return;

      // Ignore the Gremlin toggle button itself in navbar
      if (target.getAttribute('data-gremlin-ignore') === 'true') return;

      const rect = target.getBoundingClientRect();
      if (rect.width < 30 || rect.height < 20) return;

      lastInterruptRef.current = now;
      const targetX = Math.min(window.innerWidth - 120, Math.max(20, rect.left + rect.width / 2 - 48));
      const targetY = Math.min(window.innerHeight - 130, Math.max(60, rect.top + rect.height / 2 - 55));

      setFacingLeft(targetX < pos.x);
      setPos({ x: targetX, y: targetY });
      setIsInterrupting(true);
      setCountdown(3);

      const list = theme === 'banana' ? bananaInterruptQuips : pepeInterruptQuips;
      setSpeech(list[Math.floor(Math.random() * list.length)]);

      if (countdownTimerRef.current) clearInterval(countdownTimerRef.current);
      countdownTimerRef.current = window.setInterval(() => {
        setCountdown((c) => Math.max(0, c - 1));
      }, 1000);

      if (interruptTimerRef.current) clearTimeout(interruptTimerRef.current);
      interruptTimerRef.current = window.setTimeout(() => {
        if (countdownTimerRef.current) clearInterval(countdownTimerRef.current);
        setIsInterrupting(false);
        setSpeech(theme === 'banana' ? '😂 Hehe ok go ahead! Ring ring! 🍌' : '😂 Hehe ok you can click it now! KEKW');
        // Scurry away to the side so the button is 100% clear
        const escapeX = targetX > window.innerWidth / 2 ? Math.max(40, targetX - 240) : Math.min(window.innerWidth - 140, targetX + 240);
        const escapeY = Math.max(90, Math.min(window.innerHeight - 160, targetY - 110));
        setPos({ x: escapeX, y: escapeY });
      }, 3000);
    };

    window.addEventListener('mouseover', handleMouseOver, { passive: true });
    return () => {
      window.removeEventListener('mouseover', handleMouseOver);
    };
  }, [enabled, isInterrupting, theme, pos.x]);

  if (!enabled) return null;

  const dismissImmediately = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (interruptTimerRef.current) clearTimeout(interruptTimerRef.current);
    if (countdownTimerRef.current) clearInterval(countdownTimerRef.current);
    setIsInterrupting(false);
    lastInterruptRef.current = Date.now();

    safeConfetti({
      particleCount: 25,
      spread: 60,
      origin: {
        x: (pos.x + 48) / window.innerWidth,
        y: (pos.y + 48) / window.innerHeight,
      },
      colors: theme === 'banana' ? ['#ffe600', '#ffffff', '#ef4444'] : ['#39ff14', '#00f0ff', '#ff007f'],
      disableForReducedMotion: true,
    });

    setSpeech(theme === 'banana' ? '🍌 WOAH! Slipping away!' : '🐸 OOF! Running away!');
    const nextX = Math.floor(60 + Math.random() * (window.innerWidth - 180));
    const nextY = Math.floor(100 + Math.random() * (window.innerHeight - 200));
    setPos({ x: nextX, y: nextY });
  };

  return (
    <div
      style={{
        transform: `translate3d(${pos.x}px, ${pos.y}px, 0)`,
        transition: isInterrupting
          ? 'transform 0.32s cubic-bezier(0.22, 1, 0.36, 1)'
          : 'transform 2.4s ease-in-out',
      }}
      onClick={dismissImmediately}
      className={`fixed top-0 left-0 z-[70] select-none cursor-pointer ${
        isInterrupting ? 'pointer-events-auto' : 'pointer-events-auto'
      }`}
      title="Click me to shoo me away!"
    >
      {/* Speech Bubble */}
      <div
        className={`mb-1 px-2.5 py-1 rounded-lg border text-[11px] font-code max-w-[230px] text-center shadow-lg transition-all ${
          isInterrupting
            ? 'bg-red-950/95 border-yellow-400 text-yellow-200 shadow-[0_0_20px_rgba(250,204,21,0.7)] animate-bounce'
            : theme === 'banana'
            ? 'bg-amber-950/90 border-yellow-400/60 text-yellow-300'
            : 'bg-slate-950/90 border-lime-400/60 text-lime-300'
        }`}
      >
        <div>{speech}</div>
        {isInterrupting && (
          <div className="text-[10px] text-white font-bold mt-0.5">
            [Dancing in front of your cursor: {countdown}s — Click me to skip!]
          </div>
        )}
      </div>

      {/* Character Sprite (Authentic Full-Body Pepe or Dancing Pom-Pom Banana) */}
      <div
        className={`w-24 h-24 mx-auto ${isInterrupting ? 'animate-bounce scale-110' : 'animate-pepe-dance'}`}
        style={{ transform: facingLeft ? 'scaleX(-1)' : undefined }}
      >
        {theme === 'banana' ? (
          /* Roaming Dancing Pom-Pom Banana */
          <svg viewBox="0 0 260 270" className="w-full h-full drop-shadow-[0_0_16px_rgba(250,204,21,0.7)]">
            <line x1="96" y1="115" x2="38" y2="76" stroke="#111111" strokeWidth="8" strokeLinecap="round" />
            <line x1="150" y1="115" x2="216" y2="74" stroke="#111111" strokeWidth="8" strokeLinecap="round" />
            <polygon
              points="35,44 43,54 55,48 52,61 64,66 54,75 60,87 47,86 42,98 33,88 21,94 24,81 12,76 22,67 16,55 29,56"
              fill="#ffffff"
              stroke="#1f2937"
              strokeWidth="4.5"
            />
            <polygon
              points="218,42 226,52 238,46 235,59 247,64 237,73 243,85 230,84 225,96 216,86 204,92 207,79 195,74 205,65 199,53 212,54"
              fill="#ffffff"
              stroke="#1f2937"
              strokeWidth="4.5"
            />
            <line x1="122" y1="194" x2="100" y2="238" stroke="#111111" strokeWidth="8" strokeLinecap="round" />
            <line x1="142" y1="192" x2="164" y2="238" stroke="#111111" strokeWidth="8" strokeLinecap="round" />
            <ellipse cx="90" cy="244" rx="24" ry="11" fill="#ffffff" stroke="#111111" strokeWidth="5" />
            <ellipse cx="174" cy="244" rx="24" ry="11" fill="#ffffff" stroke="#111111" strokeWidth="5" />
            <path
              d="M114 18 L134 18 C148 56 156 126 152 192 L124 198 C100 156 92 92 114 18 Z"
              fill="#facc15"
              stroke="#111111"
              strokeWidth="6.5"
              strokeLinejoin="round"
            />
            <circle cx="111" cy="74" r="15" fill="#ffffff" stroke="#111111" strokeWidth="4.5" />
            <circle cx="111" cy="74" r="4.5" fill="#111111" />
            <circle cx="139" cy="74" r="15" fill="#ffffff" stroke="#111111" strokeWidth="4.5" />
            <circle cx="139" cy="74" r="4.5" fill="#111111" />
            <path
              d="M98 102 Q125 106 148 102 C146 128 104 128 98 102 Z"
              fill="#ef4444"
              stroke="#111111"
              strokeWidth="4.5"
            />
          </svg>
        ) : (
          /* Roaming Authentic Full-Body Dancing Pepe */
          <svg viewBox="0 0 240 270" className="w-full h-full drop-shadow-[0_0_16px_rgba(57,255,20,0.7)]">
            <path
              d="M92 222 L91 252 C91 258 105 258 106 252 L108 224 Z"
              fill="#528b29"
              stroke="#142409"
              strokeWidth="4"
            />
            <path
              d="M135 222 L137 255 C137 261 151 261 152 255 L149 222 Z"
              fill="#528b29"
              stroke="#142409"
              strokeWidth="4"
            />
            <path
              d="M84 140 C76 168 75 204 85 224 C96 232 145 232 156 224 C165 202 164 162 152 136 Z"
              fill="#528b29"
              stroke="#142409"
              strokeWidth="4"
            />
            <path
              d="M54 112 C42 98 48 76 64 70 C66 48 84 36 106 42 C116 30 144 30 156 48 C174 56 184 78 180 104 C178 126 162 142 138 144 C102 148 64 138 54 112 Z"
              fill="#528b29"
              stroke="#142409"
              strokeWidth="4"
            />
            <path
              d="M52 83 C56 71 94 70 104 82 C104 94 88 99 72 98 C56 97 50 90 52 83 Z"
              fill="#ffffff"
              stroke="#142409"
              strokeWidth="3.2"
            />
            <ellipse cx="76" cy="87" rx="10" ry="9.5" fill="#090d16" />
            <circle cx="72" cy="84" r="3.2" fill="#ffffff" />
            <path
              d="M106 82 C112 70 148 70 158 83 C156 95 140 100 124 99 C110 98 104 90 106 82 Z"
              fill="#ffffff"
              stroke="#142409"
              strokeWidth="3.2"
            />
            <ellipse cx="127" cy="87" rx="10" ry="9.5" fill="#090d16" />
            <circle cx="123" cy="84" r="3.2" fill="#ffffff" />
            <path
              d="M50 116 C72 118 116 116 144 112 C150 118 148 128 138 129 C112 132 74 134 54 129 C46 127 46 119 50 116 Z"
              fill="#c64e2e"
              stroke="#142409"
              strokeWidth="3.2"
            />
            <path
              d="M84 150 C74 162 70 182 74 194 C77 200 86 198 86 190 C85 180 87 168 91 160"
              fill="#528b29"
              stroke="#142409"
              strokeWidth="4"
            />
            <path
              d="M146 156 C162 150 168 120 158 102 C152 94 142 98 144 110 C146 122 143 138 137 146"
              fill="#528b29"
              stroke="#142409"
              strokeWidth="4"
            />
          </svg>
        )}
      </div>
    </div>
  );
};
