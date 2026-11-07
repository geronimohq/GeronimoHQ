import React, { useState, useEffect, useRef } from 'react';
import confetti from 'canvas-confetti';
import { PhoneCall, Volume2, VolumeX, ExternalLink, Activity, Sparkles } from 'lucide-react';

declare global {
  interface Window {
    YT?: {
      Player: new (
        element: HTMLElement | string,
        options: {
          videoId: string;
          playerVars?: Record<string, number | string>;
          events?: {
            onReady?: (event: { target: YTPlayerInstance }) => void;
            onStateChange?: (event: { data: number; target: YTPlayerInstance }) => void;
          };
        }
      ) => YTPlayerInstance;
      PlayerState?: {
        ENDED: number;
        PLAYING: number;
        PAUSED: number;
      };
    };
    onYouTubeIframeAPIReady?: () => void;
  }
}

interface YTPlayerInstance {
  playVideo: () => void;
  pauseVideo: () => void;
  stopVideo: () => void;
  seekTo: (seconds: number, allowSeekAhead: boolean) => void;
  mute: () => void;
  unMute: () => void;
  setVolume: (volume: number) => void;
  getPlayerState: () => number;
  destroy: () => void;
}

interface DancingBananaCharacterProps {
  label: string;
  subLabel: string;
  speedClass?: string;
  scaleClass?: string;
  flip?: boolean;
}

export const DancingBananaCharacter: React.FC<DancingBananaCharacterProps> = ({
  label,
  subLabel,
  speedClass = 'animate-pepe-dance',
  scaleClass = 'w-48 md:w-56',
  flip = false,
}) => {
  const [ringCount, setRingCount] = useState(0);
  const [showPopup, setShowPopup] = useState(false);
  const [popupText, setPopupText] = useState('RING RING RING! 🍌📞');

  const phrases = [
    'RING RING RING! BANANA PHONE! 🍌📞',
    'BOOP-BOO-BA-DOO-BA-DOOP! 🎶',
    'IT GROWS IN BUNCHES! 🍌',
    'PEANUT BUTTER JELLY TIME! 🕺',
    'CELLULAR! MODULAR! INTERACTIVODULAR! 📞',
  ];

  const handleBananaClick = (e: React.MouseEvent) => {
    setRingCount((c) => c + 1);
    setPopupText(phrases[Math.floor(Math.random() * phrases.length)]);
    setShowPopup(true);
    setTimeout(() => setShowPopup(false), 2000);

    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const x = (rect.left + rect.width / 2) / window.innerWidth;
    const y = (rect.top + rect.height / 2) / window.innerHeight;

    confetti({
      particleCount: 40,
      spread: 75,
      origin: { x, y },
      colors: ['#ffe600', '#f59e0b', '#ffffff', '#ef4444'],
      disableForReducedMotion: true,
    });
  };

  return (
    <div
      onClick={handleBananaClick}
      className={`relative group cursor-pointer flex flex-col items-center transition-transform duration-300 hover:scale-105 ${scaleClass}`}
      title="Click the Dancing Banana for Banana Phone Confetti!"
    >
      {showPopup && (
        <div className="absolute -top-12 left-1/2 -translate-x-1/2 z-30 whitespace-nowrap px-3 py-1 bg-amber-950/95 border border-yellow-400 rounded-lg text-yellow-300 text-xs font-cyber font-bold shadow-[0_0_20px_rgba(250,204,21,0.85)] animate-bounce">
          {popupText} (x{ringCount})
        </div>
      )}

      {/* Animated Dancing Banana SVG matching Geronimo's uploaded image */}
      <div className={`relative w-full ${speedClass}`} style={{ transform: flip ? 'scaleX(-1)' : undefined }}>
        <svg
          viewBox="0 0 260 270"
          className="w-full h-auto drop-shadow-[0_0_22px_rgba(250,204,21,0.45)] group-hover:drop-shadow-[0_0_35px_rgba(250,204,21,0.85)] transition-all"
        >
          <defs>
            <linearGradient id="bananaBodyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#fde047" />
              <stop offset="55%" stopColor="#facc15" />
              <stop offset="100%" stopColor="#eab308" />
            </linearGradient>
          </defs>

          {/* Left Stick Arm Reaching Up to Pom-Pom */}
          <line
            x1="96"
            y1="115"
            x2="38"
            y2="76"
            stroke="#111111"
            strokeWidth="7"
            strokeLinecap="round"
          />

          {/* Right Stick Arm Reaching Up to Pom-Pom */}
          <line
            x1="150"
            y1="115"
            x2="216"
            y2="74"
            stroke="#111111"
            strokeWidth="7"
            strokeLinecap="round"
          />

          {/* Left Fluffy White Cheerleader Pom-Pom */}
          <polygon
            points="35,44 43,54 55,48 52,61 64,66 54,75 60,87 47,86 42,98 33,88 21,94 24,81 12,76 22,67 16,55 29,56"
            fill="#ffffff"
            stroke="#1f2937"
            strokeWidth="4"
            strokeLinejoin="round"
          />

          {/* Right Fluffy White Cheerleader Pom-Pom */}
          <polygon
            points="218,42 226,52 238,46 235,59 247,64 237,73 243,85 230,84 225,96 216,86 204,92 207,79 195,74 205,65 199,53 212,54"
            fill="#ffffff"
            stroke="#1f2937"
            strokeWidth="4"
            strokeLinejoin="round"
          />

          {/* Left Stick Leg */}
          <line
            x1="122"
            y1="194"
            x2="100"
            y2="238"
            stroke="#111111"
            strokeWidth="7.5"
            strokeLinecap="round"
          />

          {/* Right Stick Leg */}
          <line
            x1="142"
            y1="192"
            x2="164"
            y2="238"
            stroke="#111111"
            strokeWidth="7.5"
            strokeLinecap="round"
          />

          {/* Left White Oval Shoe */}
          <ellipse
            cx="90"
            cy="244"
            rx="24"
            ry="11"
            fill="#ffffff"
            stroke="#111111"
            strokeWidth="5"
          />

          {/* Right White Oval Shoe */}
          <ellipse
            cx="174"
            cy="244"
            rx="24"
            ry="11"
            fill="#ffffff"
            stroke="#111111"
            strokeWidth="5"
          />

          {/* Iconic Curved Yellow Banana Body with Thick Black Outline */}
          <path
            d="M114 18 L134 18 C148 56 156 126 152 192 L124 198 C100 156 92 92 114 18 Z"
            fill="url(#bananaBodyGrad)"
            stroke="#111111"
            strokeWidth="6"
            strokeLinejoin="round"
          />

          {/* Subtle Banana Highlight Curve */}
          <path
            d="M118 30 C106 85 108 140 126 184"
            fill="none"
            stroke="#fef08a"
            strokeWidth="4"
            strokeLinecap="round"
            opacity="0.7"
          />

          {/* Left Big Googly Eye */}
          <circle
            cx="111"
            cy="74"
            r="15"
            fill="#ffffff"
            stroke="#111111"
            strokeWidth="4.5"
          />
          <circle cx="111" cy="74" r="4.5" fill="#111111" />

          {/* Right Big Googly Eye */}
          <circle
            cx="139"
            cy="74"
            r="15"
            fill="#ffffff"
            stroke="#111111"
            strokeWidth="4.5"
          />
          <circle cx="139" cy="74" r="4.5" fill="#111111" />

          {/* Wide Open Red Smiling Mouth */}
          <path
            d="M98 102 Q125 106 148 102 C146 128 104 128 98 102 Z"
            fill="#ef4444"
            stroke="#111111"
            strokeWidth="4.5"
            strokeLinejoin="round"
          />
        </svg>
      </div>

      <div className="mt-1 text-center">
        <span className="inline-block px-2.5 py-0.5 text-[10px] font-code tracking-wider uppercase bg-amber-950/80 text-yellow-300 border border-yellow-400/50 rounded">
          {label}
        </span>
        <p className="mt-1 text-xs font-tech text-amber-200/80 text-center tracking-wide">
          {subLabel}
        </p>
      </div>
    </div>
  );
};

interface BananaHeroStageProps {
  targetLoops: number;
  onAllLoopsCompleted: () => void;
  masterVolume?: number;
  isMasterMuted?: boolean;
  onToggleMasterMute?: () => void;
  onMasterVolumeChange?: (vol: number) => void;
}

export const BananaHeroStage: React.FC<BananaHeroStageProps> = ({
  targetLoops,
  onAllLoopsCompleted,
  masterVolume = 15,
  isMasterMuted = false,
  onToggleMasterMute,
  onMasterVolumeChange,
}) => {
  const [isMusicOn, setIsMusicOn] = useState<boolean>(true);
  const playerContainerRef = useRef<HTMLDivElement | null>(null);
  const playerRef = useRef<YTPlayerInstance | null>(null);
  const completedLoopsRef = useRef<number>(0);
  const ytActivelyPlayingRef = useRef<boolean>(false);
  const targetLoopsRef = useRef<number>(targetLoops);
  const onCompleteRef = useRef<() => void>(onAllLoopsCompleted);

  const isMasterMutedRef = useRef<boolean>(isMasterMuted);
  const masterVolumeRef = useRef<number>(masterVolume);

  useEffect(() => {
    isMasterMutedRef.current = isMasterMuted;
    masterVolumeRef.current = masterVolume;
  }, [isMasterMuted, masterVolume]);

  useEffect(() => {
    targetLoopsRef.current = targetLoops;
  }, [targetLoops]);

  useEffect(() => {
    onCompleteRef.current = onAllLoopsCompleted;
  }, [onAllLoopsCompleted]);

  // Reactive listener to masterVolume and isMasterMuted changes
  useEffect(() => {
    if (playerRef.current) {
      try {
        if (isMasterMuted || masterVolume === 0) {
          playerRef.current.mute();
          playerRef.current.setVolume(0);
        } else {
          playerRef.current.unMute();
          playerRef.current.setVolume(masterVolume);
        }
      } catch {
        // ignore
      }
    }
  }, [masterVolume, isMasterMuted]);

  // Automatically wake up and resume audio if user switches back to the tab from other applications
  useEffect(() => {
    const handleResumeOnFocus = () => {
      if (playerRef.current && isMusicOn && !isMasterMutedRef.current) {
        try {
          const st = playerRef.current.getPlayerState();
          if (st !== 1) { // 1 = PLAYING
            playerRef.current.playVideo();
          }
        } catch {
          // ignore
        }
      }
    };

    window.addEventListener('focus', handleResumeOnFocus);
    const handleVis = () => {
      if (document.visibilityState === 'visible') {
        handleResumeOnFocus();
      }
    };
    document.addEventListener('visibilitychange', handleVis);

    return () => {
      window.removeEventListener('focus', handleResumeOnFocus);
      document.removeEventListener('visibilitychange', handleVis);
    };
  }, [isMusicOn]);

  // Mount & control the YouTube IFrame API player for seamless looping and exact end-of-loop theme transition
  useEffect(() => {
    if (!isMusicOn) {
      if (playerRef.current) {
        try {
          playerRef.current.stopVideo();
          playerRef.current.destroy();
        } catch {
          // ignore
        }
        playerRef.current = null;
      }
      ytActivelyPlayingRef.current = false;
      return;
    }

    let isCancelled = false;

    const createPlayer = () => {
      if (isCancelled || !playerContainerRef.current || !window.YT || !window.YT.Player) return;

      // Clean previous instance if any
      if (playerRef.current) {
        try {
          playerRef.current.destroy();
        } catch {
          // ignore
        }
        playerRef.current = null;
      }

      const iframe = document.createElement('iframe');
      const originParam = encodeURIComponent(window.location.origin);
      const isMutedParam = isMasterMutedRef.current || masterVolumeRef.current === 0 ? '1' : '0';
      iframe.src = `https://www.youtube.com/embed/j5C6X9vOEkU?autoplay=1&mute=${isMutedParam}&rel=0&playsinline=1&enablejsapi=1&origin=${originParam}`;
      iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
      iframe.setAttribute('allowfullscreen', 'true');
      iframe.className = 'w-full h-full border-0';

      playerContainerRef.current.innerHTML = '';
      playerContainerRef.current.appendChild(iframe);

      const unlockEvents = ['pointerdown', 'mousedown', 'keydown', 'touchstart', 'click'];

      const unlockPlay = () => {
        if (isCancelled || !playerRef.current) return;
        try {
          if (isMasterMutedRef.current || masterVolumeRef.current === 0) {
            playerRef.current.mute();
            playerRef.current.setVolume(0);
          } else {
            playerRef.current.unMute();
            playerRef.current.setVolume(masterVolumeRef.current);
          }
          const st = playerRef.current.getPlayerState();
          if (st !== 1) {
            playerRef.current.playVideo();
          }
        } catch {
          // ignore
        }
        // Run once on initial user gesture to unlock browser audio, then remove immediately
        unlockEvents.forEach((evt) => {
          window.removeEventListener(evt, unlockPlay, { capture: true });
        });
      };

      // Only listen for audio unlock if user has NOT muted
      if (!isMasterMutedRef.current) {
        unlockEvents.forEach((evt) => {
          window.addEventListener(evt, unlockPlay, { capture: true, passive: true });
        });
      }

      playerRef.current = new window.YT.Player(iframe, {
        videoId: 'j5C6X9vOEkU',
        events: {
          onReady: (event) => {
            if (isCancelled) return;
            try {
              if (isMasterMutedRef.current || masterVolumeRef.current === 0) {
                event.target.mute();
                event.target.setVolume(0);
              } else {
                event.target.unMute();
                event.target.setVolume(masterVolumeRef.current);
              }
              event.target.playVideo();
            } catch {
              // ignore
            }
          },
          onStateChange: (event) => {
            if (isCancelled) return;
            // 1 = PLAYING
            if (event.data === 1) {
              ytActivelyPlayingRef.current = true;
              try {
                if (isMasterMutedRef.current || masterVolumeRef.current === 0) {
                  event.target.mute();
                  event.target.setVolume(0);
                } else {
                  event.target.unMute();
                  event.target.setVolume(masterVolumeRef.current);
                }
              } catch {
                // ignore
              }
            }
            // 0 = ENDED (Banana Phone song finished 1 complete play of 3m 16s!)
            if (event.data === 0) {
              completedLoopsRef.current += 1;
              // 1 complete song finished -> switch to Pepe theme!
              try {
                event.target.stopVideo();
              } catch {
                // ignore
              }
              onCompleteRef.current();
            }
          },
        },
      });
    };

    if (window.YT && window.YT.Player) {
      createPlayer();
    } else {
      const existingScript = document.getElementById('yt-iframe-api-script');
      if (!existingScript) {
        const tag = document.createElement('script');
        tag.id = 'yt-iframe-api-script';
        tag.src = 'https://www.youtube.com/iframe_api';
        document.head.appendChild(tag);
      }
      const prevCallback = window.onYouTubeIframeAPIReady;
      window.onYouTubeIframeAPIReady = () => {
        if (prevCallback) prevCallback();
        createPlayer();
      };
      // Poll briefly in case script already loaded
      const checkTimer = window.setInterval(() => {
        if (window.YT && window.YT.Player) {
          clearInterval(checkTimer);
          createPlayer();
        }
      }, 250);
      return () => {
        isCancelled = true;
        clearInterval(checkTimer);
        if (playerRef.current) {
          try {
            playerRef.current.stopVideo();
            playerRef.current.destroy();
          } catch {
            // ignore
          }
          playerRef.current = null;
        }
      };
    }

    return () => {
      isCancelled = true;
      if (playerRef.current) {
        try {
          playerRef.current.stopVideo();
          playerRef.current.destroy();
        } catch {
          // ignore
        }
        playerRef.current = null;
      }
    };
  }, [isMusicOn]);

  // Fallback timer ONLY if the user turned off the Banana Phone music or if YT autoplay was blocked by browser
  // (Never interrupts if the YouTube song is actively playing, so the song always finishes its loop first!)
  useEffect(() => {
    const songDurationMs = 147_000; // Raffi Banana Phone (j5C6X9vOEkU) is 2:27 (147s)
    const fallbackTimer = window.setTimeout(() => {
      if (!ytActivelyPlayingRef.current || !isMusicOn) {
        onCompleteRef.current();
      }
    }, targetLoops * songDurationMs + 3000);

    return () => clearTimeout(fallbackTimer);
  }, [targetLoops, isMusicOn]);

  const bananaYoutubeUrl = 'https://www.youtube.com/watch?v=j5C6X9vOEkU&list=RDj5C6X9vOEkU&start_radio=1';

  return (
    <section className="relative w-full max-w-6xl mx-auto px-4 py-8 flex flex-col items-center">
      {/* HUD Header for Banana Phone Stage */}
      <div className="w-full flex flex-wrap items-center justify-between gap-4 mb-6 border-b border-yellow-500/40 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-yellow-400 animate-ping" />
          <span className="font-cyber text-sm tracking-widest text-yellow-300 font-bold uppercase flex items-center gap-2">
            🍌 BANANA PHONE HOLO-CHAMBER // SECTOR-BANANA
          </span>
          <span className="text-[10px] font-code px-2 py-0.5 rounded bg-amber-950/90 text-yellow-300 border border-yellow-400/50">
            RING RING RINGx7
          </span>
        </div>

        {/* Banana Phone Master Music & Volume Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {onToggleMasterMute ? (
            <button
              onClick={onToggleMasterMute}
              data-gremlin-ignore="true"
              className={`px-3 py-1.5 text-xs font-code font-bold rounded-lg border flex items-center justify-center gap-1.5 min-w-[185px] cursor-pointer transition-all ${
                !isMasterMuted
                  ? 'bg-yellow-500/20 text-yellow-300 border-yellow-400 shadow-[0_0_15px_rgba(250,204,21,0.4)]'
                  : 'bg-red-950/90 text-red-400 border-red-500/60'
              }`}
              title="Toggle Master Mute"
            >
              {!isMasterMuted ? (
                <>
                  <Volume2 className="w-4 h-4 text-yellow-400 animate-bounce" />
                  <span>BANANA MUSIC: ON</span>
                </>
              ) : (
                <>
                  <VolumeX className="w-4 h-4 text-red-400" />
                  <span>BANANA MUSIC: MUTED</span>
                </>
              )}
            </button>
          ) : (
            <button
              onClick={() => setIsMusicOn((prev) => !prev)}
              data-gremlin-ignore="true"
              className={`px-3 py-1.5 text-xs font-code font-bold rounded-lg border flex items-center gap-1.5 cursor-pointer transition-all ${
                isMusicOn
                  ? 'bg-yellow-500/20 text-yellow-300 border-yellow-400 shadow-[0_0_15px_rgba(250,204,21,0.4)]'
                  : 'bg-slate-900/90 text-slate-400 border-slate-700 hover:border-yellow-400 hover:text-yellow-300'
              }`}
            >
              {isMusicOn ? <Volume2 className="w-4 h-4 text-yellow-400" /> : <VolumeX className="w-4 h-4" />}
              <span>BANANA MUSIC: {isMusicOn ? 'ON' : 'OFF'}</span>
            </button>
          )}

          {onMasterVolumeChange && (
            <div className="flex items-center gap-1.5 bg-black/85 border border-yellow-500/40 px-2.5 py-1.5 rounded-lg text-yellow-300 text-xs font-code">
              <span className="text-[10px] text-amber-400 font-bold">VOL:</span>
              <input
                type="range"
                min="0"
                max="100"
                value={isMasterMuted ? 0 : masterVolume}
                onChange={(e) => onMasterVolumeChange(Number(e.target.value))}
                className="w-16 h-1.5 accent-yellow-400 cursor-pointer"
                title={`Master Volume: ${isMasterMuted ? 0 : masterVolume}%`}
              />
              <span className="w-7 text-[10px] tabular-nums font-bold">
                {isMasterMuted ? '0%' : `${masterVolume}%`}
              </span>
            </div>
          )}

          <a
            href={bananaYoutubeUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-1.5 text-xs font-code rounded-lg bg-slate-900/90 text-amber-300 border border-amber-500/40 hover:border-yellow-400 flex items-center gap-1.5 transition-all"
          >
            <PhoneCall className="w-3.5 h-3.5 text-yellow-400 animate-bounce" />
            <span>YOUTUBE MIX ↗</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>

      {/* Main Banana Phone Holographic Stage */}
      <div className="relative w-full min-h-[500px] flex flex-col items-center justify-between rounded-2xl border border-yellow-500/40 bg-gradient-to-b from-amber-950/35 via-slate-950/75 to-[#090702]/95 backdrop-blur-xl overflow-hidden shadow-[0_0_60px_rgba(234,179,8,0.2)] p-6">
        {/* Corner Brackets */}
        <div className="absolute top-3 left-3 w-6 h-6 border-t-2 border-l-2 border-yellow-400/90" />
        <div className="absolute top-3 right-3 w-6 h-6 border-t-2 border-r-2 border-yellow-400/90" />
        <div className="absolute bottom-3 left-3 w-6 h-6 border-b-2 border-l-2 border-yellow-400/90" />
        <div className="absolute bottom-3 right-3 w-6 h-6 border-b-2 border-r-2 border-yellow-400/90" />

        {/* Top Ticker Banner */}
        <div className="relative z-10 inline-flex items-center gap-2 px-4 py-1 rounded-full bg-amber-950/80 border border-yellow-400/50 text-yellow-300 text-xs font-code mb-2 shadow-[0_0_20px_rgba(250,204,21,0.3)]">
          <Sparkles className="w-3.5 h-3.5 text-yellow-400" />
          <span>♪ RING RING RING RING RING RING RING... BANANA PHONE! BOOP-BOO-BA-DOO-BA-DOOP! ♪</span>
        </div>

        {/* 3x Dancing Bananas Squad */}
        <div className="relative z-10 grid grid-cols-1 md:grid-cols-3 items-end justify-items-center gap-8 md:gap-4 w-full max-w-4xl my-4">
          <DancingBananaCharacter
            label="BANANA-01 // POM-POM LEFT"
            subLabel="Ring Ring Ring // 100% Potassium"
            scaleClass="w-44 md:w-52"
          />

          <DancingBananaCharacter
            label="BANANA-02 // COMMANDER PEEL"
            subLabel="Banana Phone Operator // VIP Gooner"
            scaleClass="w-52 md:w-60"
          />

          <DancingBananaCharacter
            label="BANANA-03 // POM-POM RIGHT"
            subLabel="Ding Dong Ding // Cellular Modular"
            scaleClass="w-44 md:w-52"
            flip={true}
          />
        </div>

        {/* Embedded Banana Phone YouTube Music Player (Loops automatically via YT API) */}
        {isMusicOn && (
          <div className="relative z-20 w-full max-w-xl mt-2 mb-6 rounded-xl border border-yellow-400/50 bg-black/90 p-2.5 shadow-[0_0_30px_rgba(250,204,21,0.3)]">
            <div className="flex items-center justify-between text-[11px] font-code text-yellow-300 mb-1.5 px-1">
              <span className="flex items-center gap-1.5 font-bold">
                <PhoneCall className="w-3.5 h-3.5 text-yellow-400" />
                NOW PLAYING (AUTO-LOOP): RAFFI — BANANA PHONE
              </span>
              <span className="text-[10px] text-amber-300/80">
                AUTO-LOOPING ACTIVE
              </span>
            </div>
            <div className="relative w-full aspect-video rounded-lg overflow-hidden border border-yellow-500/30 bg-black">
              <div
                ref={playerContainerRef}
                className="w-full h-full pointer-events-none select-none [&>iframe]:w-full [&>iframe]:h-full [&>iframe]:pointer-events-none"
              />
              {/* Invisible non-clickable protective shield: prevents accidental pauses or opening external YouTube links */}
              <div
                className="absolute inset-0 z-10 cursor-default"
                title="Raffi — Banana Phone (Holo-Player)"
                onClick={(e) => {
                  e.stopPropagation();
                  e.preventDefault();
                }}
              />
            </div>
          </div>
        )}

        {/* Golden Pedestal Floor Rings */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 w-80 md:w-[620px] h-36 pointer-events-none flex items-center justify-center [perspective:800px]">
          <div className="relative w-full h-full [transform:rotateX(72deg)] flex items-center justify-center">
            <div className="absolute w-[360px] md:w-[580px] h-[360px] md:h-[580px] rounded-full border border-yellow-400/40 animate-spin-slow shadow-[0_0_30px_rgba(250,204,21,0.3)]" />
            <div className="absolute w-[260px] md:w-[420px] h-[260px] md:h-[420px] rounded-full border border-dashed border-amber-500/50 animate-spin-reverse-slow" />
          </div>
        </div>

        {/* Bottom Telemetry Bar */}
        <div className="relative z-10 w-full flex items-center justify-between text-[10px] font-code text-amber-300/70 border-t border-yellow-500/20 pt-2">
          <span className="flex items-center gap-1">
            <Activity className="w-3 h-3 text-yellow-400" /> POTASSIUM LEVEL: 9,999%
          </span>
          <span>CLICK ANY BANANA TO RING THE BANANA PHONE!</span>
        </div>
      </div>
    </section>
  );
};
