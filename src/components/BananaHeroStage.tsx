import React, { useState, useEffect, useRef } from 'react';
import { safeConfetti } from '../utils/motion';
import { PhoneCall, Volume2, VolumeX, ExternalLink, Activity, Sparkles } from 'lucide-react';

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

    safeConfetti({
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
  targetLoops?: number;
  onAllLoopsCompleted: () => void;
  masterVolume?: number;
  isMasterMuted?: boolean;
  onToggleMasterMute?: () => void;
  onMasterVolumeChange?: (vol: number) => void;
}

export type BananaTab = 'all' | 'commander' | 'pompom' | 'video';

export const BananaHeroStage: React.FC<BananaHeroStageProps> = ({
  /* targetLoops */
  onAllLoopsCompleted,
  masterVolume = 15,
  isMasterMuted = false,
  onToggleMasterMute,
  onMasterVolumeChange,
}) => {
  const [activeTab, setActiveTab] = useState<BananaTab>('all');
  const [isMusicOn, setIsMusicOn] = useState<boolean>(true);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const onCompleteRef = useRef<() => void>(onAllLoopsCompleted);

  const isMasterMutedRef = useRef<boolean>(isMasterMuted);
  const masterVolumeRef = useRef<number>(masterVolume);

  useEffect(() => {
    isMasterMutedRef.current = isMasterMuted;
    masterVolumeRef.current = masterVolume;
  }, [isMasterMuted, masterVolume]);

  useEffect(() => {
    onCompleteRef.current = onAllLoopsCompleted;
  }, [onAllLoopsCompleted]);

  // Volume & Mute Parity
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.muted = isMasterMuted || masterVolume === 0;
      videoRef.current.volume = Math.max(0, Math.min(1, masterVolume / 100));
    }
  }, [masterVolume, isMasterMuted]);

  // Autoplay / Pause Controller
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    if (isMusicOn) {
      video.muted = isMasterMutedRef.current || masterVolumeRef.current === 0;
      video.volume = Math.max(0, Math.min(1, masterVolumeRef.current / 100));
      const playPromise = video.play();
      if (playPromise !== undefined) {
        playPromise.catch(() => {
          const resumeOnGesture = () => {
            if (videoRef.current && isMusicOn) {
              videoRef.current.play().catch(() => {});
            }
            window.removeEventListener('click', resumeOnGesture);
            window.removeEventListener('keydown', resumeOnGesture);
          };
          window.addEventListener('click', resumeOnGesture, { once: true });
          window.addEventListener('keydown', resumeOnGesture, { once: true });
        });
      }
    } else {
      video.pause();
    }
  }, [isMusicOn]);

  // Focus & Visibility Auto-Resume
  useEffect(() => {
    const handleResumeOnFocus = () => {
      if (videoRef.current && isMusicOn && !isMasterMutedRef.current) {
        if (videoRef.current.paused) {
          videoRef.current.play().catch(() => {});
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

  const handleVideoEnded = () => {
    onCompleteRef.current();
  };

  const bananaYoutubeUrl = 'https://www.youtube.com/watch?v=j5C6X9vOEkU&list=RDj5C6X9vOEkU&start_radio=1';

  return (
    <section className="relative w-full max-w-6xl mx-auto px-4 py-8 flex flex-col items-center overflow-hidden">
      {/* HUD Header for Banana Phone Stage (Matching Pepe Hero Stage Architecture) */}
      <div className="w-full flex flex-wrap items-center justify-between gap-4 mb-6 border-b border-yellow-500/40 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-yellow-400 animate-ping" />
          <span className="font-cyber text-sm tracking-widest text-yellow-300 font-bold uppercase flex items-center gap-2">
            🍌 BANANA PHONE HOLO-CHAMBER // SECTOR-BANANA
          </span>
          <span className="text-[10px] font-code px-2 py-0.5 rounded bg-amber-950/90 text-yellow-300 border border-yellow-400/50">
            POTASSIUM: 9,999%
          </span>
        </div>

        {/* Music Controls + Tabs Header */}
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

          {/* Symmetrical Specimen Filter Tabs */}
          <div className="flex items-center gap-1 bg-black/80 border border-yellow-500/40 p-1 rounded-xl">
            <button
              onClick={() => setActiveTab('all')}
              className={`px-3 py-1.5 text-xs font-code rounded-lg transition-all cursor-pointer ${
                activeTab === 'all'
                  ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-400/60 shadow-[0_0_10px_rgba(250,204,21,0.4)] font-bold'
                  : 'text-slate-400 hover:text-yellow-300'
              }`}
            >
              [01] ALL BANANAS
            </button>
            <button
              onClick={() => setActiveTab('commander')}
              className={`px-3 py-1.5 text-xs font-code rounded-lg transition-all cursor-pointer ${
                activeTab === 'commander'
                  ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-400/60 shadow-[0_0_10px_rgba(250,204,21,0.4)] font-bold'
                  : 'text-slate-400 hover:text-yellow-300'
              }`}
            >
              [02] COMMANDER PEEL
            </button>
            <button
              onClick={() => setActiveTab('pompom')}
              className={`px-3 py-1.5 text-xs font-code rounded-lg transition-all cursor-pointer ${
                activeTab === 'pompom'
                  ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-400/60 shadow-[0_0_10px_rgba(250,204,21,0.4)] font-bold'
                  : 'text-slate-400 hover:text-yellow-300'
              }`}
            >
              [03] POM-POM SQUAD
            </button>
            <button
              onClick={() => setActiveTab('video')}
              className={`px-3 py-1.5 text-xs font-code rounded-lg transition-all cursor-pointer flex items-center gap-1 ${
                activeTab === 'video'
                  ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-400/60 shadow-[0_0_10px_rgba(250,204,21,0.4)] font-bold'
                  : 'text-slate-400 hover:text-yellow-300'
              }`}
            >
              <PhoneCall className="w-3 h-3 text-yellow-400" />
              [04] MUSIC VIDEO
            </button>
          </div>
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

        {/* TAB 1: ALL BANANAS (3D Rotating Stage) */}
        {activeTab === 'all' && (
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
        )}

        {/* TAB 2: COMMANDER PEEL (Inspect Lore & Stats Card) */}
        {activeTab === 'commander' && (
          <div className="relative z-10 flex flex-col md:flex-row items-center justify-center gap-8 max-w-2xl text-left my-4">
            <div className="w-56 md:w-64 flex justify-center">
              <DancingBananaCharacter
                label="COMMANDER PEEL // #002"
                subLabel="Live Operator"
                scaleClass="w-48 md:w-56"
              />
            </div>
            <div className="space-y-3 bg-slate-900/90 border border-yellow-500/40 p-5 rounded-xl backdrop-blur-md">
              <div className="flex items-center justify-between">
                <span className="font-cyber text-yellow-400 text-sm font-bold">COMMANDER_PEEL // OPERATOR</span>
                <span className="text-[10px] font-code bg-amber-950 text-yellow-300 px-2 py-0.5 rounded border border-yellow-500/50">CLASS: VIP</span>
              </div>
              <p className="text-xs text-amber-100/90 leading-relaxed font-tech">
                The supreme hotline operator of GeronimoHQ. Equipped with dual wireless pom-pom antennas capable of intercepting CS2 server traffic and transmitting instant Potassium signals.
              </p>
              <div className="grid grid-cols-2 gap-2 text-[11px] font-code text-slate-300 border-t border-slate-800 pt-2">
                <div>POTASSIUM: <span className="text-yellow-400 font-bold">9,999%</span></div>
                <div>RING FREQUENCY: <span className="text-yellow-400 font-bold">128 BPM</span></div>
                <div>TYPE: <span className="text-yellow-400 font-bold">Cellular / Modular</span></div>
                <div>HOTLINE: <span className="text-yellow-400 font-bold">Ring Ring Ring</span></div>
              </div>
              <p className="text-[11px] text-yellow-400 italic">💡 Click Commander Peel to send confetti rings into the stratosphere!</p>
            </div>
          </div>
        )}

        {/* TAB 3: POM-POM SQUAD (Cheerleader Solo) */}
        {activeTab === 'pompom' && (
          <div className="relative z-10 flex flex-col items-center justify-center gap-4 my-4 max-w-md text-center">
            <div className="w-56 md:w-64 flex justify-center">
              <DancingBananaCharacter
                label="POM-POM CHEERLEADER"
                subLabel="Party Mode Active"
                speedClass="animate-bounce"
                scaleClass="w-52 md:w-60"
              />
            </div>
            <p className="text-xs font-tech text-yellow-200/90 max-w-sm">
              High-frequency cheerleader pom-poms synchronized to sub-tick tickrates. Click to ring!
            </p>
          </div>
        )}

        {/* TAB 4: BANANA PHONE OFFICIAL MEDIA VIDEO */}
        {activeTab === 'video' && (
          <div className="relative z-20 w-full max-w-xl my-4 rounded-xl border border-yellow-400/50 bg-black/90 p-3 shadow-[0_0_30px_rgba(250,204,21,0.3)]">
            <div className="flex items-center justify-between text-[11px] font-code text-yellow-300 mb-2 px-1">
              <span className="flex items-center gap-1.5 font-bold">
                <PhoneCall className="w-3.5 h-3.5 text-yellow-400" />
                RAFFI — BANANA PHONE (OFFICIAL VIDEO)
              </span>
              <a
                href={bananaYoutubeUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[10px] text-amber-300/80 hover:text-white flex items-center gap-1"
              >
                <span>YOUTUBE LINK</span>
                <ExternalLink className="w-2.5 h-2.5" />
              </a>
            </div>
            <div className="relative w-full aspect-video rounded-lg overflow-hidden border border-yellow-500/30 bg-black flex items-center justify-center">
              <video
                src="/media/banana_phone.mp4"
                playsInline
                controls
                className="w-full h-full object-contain"
              />
            </div>
          </div>
        )}

        {/* Dedicated Background Video Player (Never displaces the stage layout) */}
        <video
          ref={videoRef}
          src="/media/banana_phone.mp4"
          playsInline
          autoPlay
          className="hidden"
          onEnded={handleVideoEnded}
        />

        {/* Golden Pedestal Floor Rings */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 w-72 sm:w-80 md:w-[620px] h-36 pointer-events-none flex items-center justify-center [perspective:800px] overflow-hidden">
          <div className="relative w-full h-full [transform:rotateX(72deg)] flex items-center justify-center">
            <div className="absolute w-[280px] sm:w-[360px] md:w-[580px] h-[280px] sm:h-[360px] md:h-[580px] rounded-full border border-yellow-400/40 animate-spin-slow shadow-[0_0_30px_rgba(250,204,21,0.3)]" />
            <div className="absolute w-[220px] sm:w-[260px] md:w-[420px] h-[220px] sm:h-[260px] md:h-[420px] rounded-full border border-dashed border-amber-500/50 animate-spin-reverse-slow" />
          </div>
        </div>

        {/* Bottom Telemetry Bar */}
        <div className="relative z-10 w-full flex items-center justify-between text-[10px] font-code text-amber-300/70 border-t border-yellow-500/20 pt-2 mt-4">
          <span className="flex items-center gap-1">
            <Activity className="w-3 h-3 text-yellow-400" /> STATUS: BANANA PHONE HOTLINE ACTIVE
          </span>
          <span>CLICK ANY BANANA TO RING THE BANANA PHONE!</span>
        </div>
      </div>
    </section>
  );
};
