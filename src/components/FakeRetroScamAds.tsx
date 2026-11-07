import React, { useState, useEffect } from 'react';
import { 
  Gift, 
  AlertTriangle 
} from 'lucide-react';
import confetti from 'canvas-confetti';

export const FakeRetroScamAds: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [step, setStep] = useState(1);
  const [isSpinning, setIsSpinning] = useState(false);
  const [wheelAngle, setWheelAngle] = useState(0);
  const [countdown, setCountdown] = useState(45);
  const [selectedCaptcha, setSelectedCaptcha] = useState<number[]>([]);
  const [calibratingProgress, setCalibratingProgress] = useState(98.1);
  const [closeAttempts, setCloseAttempts] = useState(0);

  // Fake ticking countdown timer
  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => (prev > 1 ? prev - 1 : 59));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const openModal = () => {
    setIsOpen(true);
    setStep(1);
    setWheelAngle(0);
    setSelectedCaptcha([]);
    setCalibratingProgress(98.1);
  };

  const handleSpin = () => {
    if (isSpinning) return;
    setIsSpinning(true);
    // Rigged spin: always lands just past the jackpot into "SPIN AGAIN / SURVEY REQUIRED"
    const targetAngle = wheelAngle + 1800 + 45;
    setWheelAngle(targetAngle);

    setTimeout(() => {
      setIsSpinning(false);
      setStep(2);
    }, 3200);
  };

  const handleCaptchaSubmit = () => {
    if (selectedCaptcha.length === 0) {
      alert("⚠️ Error: You must select at least one banana hologram to prove you are human!");
      return;
    }
    setStep(3);

    // Slowly calibrate progress
    let cur = 98.1;
    const progTimer = setInterval(() => {
      cur += 0.2;
      if (cur >= 99.8) {
        clearInterval(progTimer);
        setTimeout(() => setStep(4), 1000);
      } else {
        setCalibratingProgress(Number(cur.toFixed(1)));
      }
    }, 350);
  };

  const handleClaimFinalPrize = () => {
    confetti({
      particleCount: 80,
      spread: 90,
      origin: { y: 0.6 },
      colors: ['#ffe600', '#f59e0b', '#00ffcc', '#ff007f']
    });
    setIsOpen(false);
    // Scroll down to the RAM download holo-chamber
    const el = document.getElementById('download-ram');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleTrollClose = () => {
    if (closeAttempts < 2) {
      setCloseAttempts((c) => c + 1);
      alert("🚨 WAIT! Are you sure? If you leave now, your FREE iPhone 18 and 1 Bitcoin will be transferred to another visitor in 5 seconds!");
    } else {
      setIsOpen(false);
      setCloseAttempts(0);
    }
  };

  return (
    <>
      {/* LEFT RETRO FLOATING SCAM BANNER (Desktop Gutters) */}
      <div className="hidden xl:flex fixed left-3 top-1/2 -translate-y-1/2 z-30 flex-col items-center">
        <div 
          onClick={openModal}
          className="w-40 p-2.5 bg-gradient-to-b from-yellow-300 via-amber-400 to-red-500 rounded-lg border-2 border-dashed border-red-600 shadow-[0_0_25px_rgba(250,204,21,0.85)] cursor-pointer hover:scale-105 active:scale-95 transition-all text-center select-none animate-pulse"
          title="Click to claim your guaranteed prize!"
        >
          <div className="bg-red-600 text-white font-black text-[10px] tracking-widest px-1 py-0.5 rounded uppercase mb-1">
            ⭐ 1,000,000th VISITOR! ⭐
          </div>
          <div className="flex justify-center my-1 text-2xl animate-bounce">
            🎁📱💰
          </div>
          <div className="font-extrabold text-black text-xs leading-tight drop-shadow-sm font-sans uppercase">
            YOU WON (1) FREE BITCOIN & IPHONE 18!
          </div>
          <div className="mt-1.5 py-1 px-1 bg-black text-yellow-300 font-mono text-[9px] font-bold rounded border border-yellow-400">
            EXPIRES IN: 00:{countdown < 10 ? `0${countdown}` : countdown}
          </div>
          <button className="mt-2 w-full py-1 bg-blue-600 hover:bg-blue-700 text-white font-bold text-[11px] rounded shadow tracking-wide uppercase cursor-pointer">
            CLAIM NOW &gt;&gt;
          </button>
        </div>
      </div>

      {/* RIGHT RETRO FLOATING SCAM BANNER (Desktop Gutters) */}
      <div className="hidden xl:flex fixed right-3 top-1/2 -translate-y-1/2 z-30 flex-col items-center">
        <div 
          onClick={openModal}
          className="w-40 p-2.5 bg-gradient-to-b from-cyan-300 via-fuchsia-400 to-indigo-600 rounded-lg border-2 border-dashed border-fuchsia-500 shadow-[0_0_25px_rgba(236,72,153,0.85)] cursor-pointer hover:scale-105 active:scale-95 transition-all text-center select-none animate-pulse"
          title="Spin the prize wheel for free rewards!"
        >
          <div className="bg-fuchsia-700 text-white font-black text-[10px] tracking-widest px-1 py-0.5 rounded uppercase mb-1">
            ⚡ LUCKY ROULETTE ⚡
          </div>
          <div className="flex justify-center my-1 text-2xl animate-spin" style={{ animationDuration: '4s' }}>
            🎡
          </div>
          <div className="font-extrabold text-white text-xs leading-tight drop-shadow-md font-sans uppercase">
            SPIN WHEEL FOR CS2 DRAGON LORE & RAM!
          </div>
          <div className="mt-1.5 py-1 px-1 bg-black text-cyan-300 font-mono text-[9px] font-bold rounded border border-cyan-400">
            100% UNBIASED & SAFE
          </div>
          <button className="mt-2 w-full py-1 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-[11px] rounded shadow tracking-wide uppercase cursor-pointer">
            FREE SPIN &gt;&gt;
          </button>
        </div>
      </div>

      {/* THE ENDLESS SCAM SURVEY HOLO-TERMINAL MODAL */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="relative w-full max-w-lg bg-[#000080] border-4 border-[#c0c0c0] shadow-[0_0_50px_rgba(0,0,0,0.9)] font-sans text-black overflow-hidden rounded-none">
            
            {/* Windows 98 / Early 2000s Classic Blue Window Title Bar */}
            <div className="bg-gradient-to-r from-[#000080] via-[#1084d0] to-[#000080] text-white font-bold text-xs px-2 py-1.5 flex items-center justify-between select-none">
              <div className="flex items-center gap-1.5">
                <Gift className="w-4 h-4 text-yellow-300" />
                <span className="tracking-wide">
                  OFFICIAL CLAIM TERMINAL // STEP {step} OF 99
                </span>
              </div>
              <button 
                onClick={handleTrollClose}
                className="w-5 h-5 bg-[#c0c0c0] text-black font-bold text-xs flex items-center justify-center border-t border-l border-white border-b-2 border-r-2 border-black active:border-t-2 active:border-l-2 active:border-b active:border-r"
              >
                ✕
              </button>
            </div>

            {/* Window Content Body */}
            <div className="p-4 bg-[#c0c0c0]">
              
              {/* STEP 1: RIGGED WHEEL */}
              {step === 1 && (
                <div className="flex flex-col items-center text-center">
                  <h3 className="text-base font-black text-red-700 uppercase tracking-tight mb-1">
                    🎉 YOU HAVE (1) COMPLIMENTARY PRIZE SPIN! 🎉
                  </h3>
                  <p className="text-xs text-gray-800 mb-3">
                    Click <strong>SPIN</strong> below to secure your iPhone 18 Pro Max or 1 Bitcoin!
                  </p>

                  {/* Wheel Graphic */}
                  <div className="relative w-44 h-44 my-2 flex items-center justify-center">
                    {/* Fixed Pointer Needle */}
                    <div className="absolute -top-3 z-20 text-red-600 text-xl font-black">
                      ▼
                    </div>
                    {/* Rotating Wheel */}
                    <div 
                      className="w-40 h-40 rounded-full border-4 border-black relative overflow-hidden transition-transform ease-out shadow-lg"
                      style={{ 
                        transform: `rotate(${wheelAngle}deg)`,
                        transitionDuration: isSpinning ? '3.2s' : '0s',
                        background: 'conic-gradient(#facc15 0deg 90deg, #3b82f6 90deg 180deg, #ef4444 180deg 270deg, #10b981 270deg 360deg)'
                      }}
                    >
                      <div className="absolute inset-0 flex items-center justify-center text-[10px] font-black text-white">
                        <span className="absolute top-2 text-black">1 BTC 💰</span>
                        <span className="absolute bottom-2 text-white">IPHONE 📱</span>
                        <span className="absolute left-2 text-white">128GB RAM</span>
                        <span className="absolute right-1 text-black">SPIN AGAIN 🔄</span>
                      </div>
                    </div>
                    {/* Center Peg */}
                    <div className="absolute w-8 h-8 rounded-full bg-white border-2 border-black flex items-center justify-center z-10 font-bold text-[10px]">
                      ⭐
                    </div>
                  </div>

                  <button
                    onClick={handleSpin}
                    disabled={isSpinning}
                    className={`mt-4 px-6 py-2.5 text-sm font-black uppercase text-white rounded border-2 border-black tracking-wider transition-all ${
                      isSpinning 
                        ? 'bg-gray-500 cursor-not-allowed' 
                        : 'bg-red-600 hover:bg-red-700 active:scale-95 cursor-pointer shadow-[0_4px_0_#000]'
                    }`}
                  >
                    {isSpinning ? 'SPINNING RIGGED WHEEL...' : '👉 CLICK TO SPIN NOW! 👈'}
                  </button>
                </div>
              )}

              {/* STEP 2: PARODY CAPTCHA */}
              {step === 2 && (
                <div className="flex flex-col text-left">
                  <div className="p-2 bg-yellow-100 border border-yellow-500 rounded text-xs text-yellow-900 mb-3 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
                    <span><strong>ALMOST WON!</strong> Arrow landed on &quot;Spin Again / Survey Verification Required&quot;!</span>
                  </div>

                  <h4 className="font-bold text-xs text-gray-900 uppercase mb-1">
                    Human Security Check (Question 1 of 47):
                  </h4>
                  <p className="text-[11px] text-gray-700 mb-2">
                    Select all images that contain a <strong>Dancing Banana vibrating at exactly 440 Hz</strong>:
                  </p>

                  <div className="grid grid-cols-3 gap-2 my-2">
                    {[
                      { id: 1, label: 'Banana 1', emoji: '🍌' },
                      { id: 2, label: 'Banana 2', emoji: '🍌' },
                      { id: 3, label: 'Pepe', emoji: '🐸' },
                      { id: 4, label: 'Telephone', emoji: '📞' },
                      { id: 5, label: 'Banana 3', emoji: '🍌' },
                      { id: 6, label: 'Computer RAM', emoji: '💾' },
                    ].map((item) => {
                      const isSel = selectedCaptcha.includes(item.id);
                      return (
                        <div
                          key={item.id}
                          onClick={() => {
                            setSelectedCaptcha((prev) => 
                              isSel ? prev.filter((x) => x !== item.id) : [...prev, item.id]
                            );
                          }}
                          className={`p-3 text-center border-2 rounded cursor-pointer transition-all select-none ${
                            isSel 
                              ? 'bg-blue-200 border-blue-600 font-bold' 
                              : 'bg-white border-gray-400 hover:bg-gray-50'
                          }`}
                        >
                          <div className="text-2xl mb-1">{item.emoji}</div>
                          <div className="text-[10px] text-gray-800">{item.label}</div>
                          <input 
                            type="checkbox" 
                            checked={isSel} 
                            readOnly 
                            className="mt-1 pointer-events-none"
                          />
                        </div>
                      );
                    })}
                  </div>

                  <button
                    onClick={handleCaptchaSubmit}
                    className="mt-3 w-full py-2 bg-blue-700 hover:bg-blue-800 text-white font-bold text-xs uppercase rounded border-2 border-black shadow-[0_3px_0_#000] active:translate-y-0.5 cursor-pointer"
                  >
                    Verify &amp; Continue &gt;&gt;
                  </button>
                </div>
              )}

              {/* STEP 3: FAKE SATELLITE CALIBRATION PROGRESS BAR */}
              {step === 3 && (
                <div className="flex flex-col text-center py-4">
                  <div className="text-3xl mb-2 animate-bounce">
                    🛰️📡
                  </div>
                  <h4 className="font-bold text-sm text-gray-900 uppercase mb-1">
                    Calibrating Quantum Delivery Satellite...
                  </h4>
                  <p className="text-xs text-gray-700 mb-3">
                    Locking GPS coordinates to beam your Free iPhone 18 and 1 Bitcoin to your chair:
                  </p>

                  <div className="w-full bg-gray-300 border-2 border-gray-600 h-6 p-0.5 rounded overflow-hidden">
                    <div 
                      className="bg-blue-600 h-full text-white text-[10px] font-bold flex items-center justify-center transition-all duration-300"
                      style={{ width: `${calibratingProgress}%` }}
                    >
                      {calibratingProgress}%
                    </div>
                  </div>

                  <p className="mt-3 text-[10px] text-gray-600 italic">
                    Please do not close this window or turn off your computer...
                  </p>
                </div>
              )}

              {/* STEP 4: HILARIOUS FINAL REVEAL & CONVERSION */}
              {step === 4 && (
                <div className="flex flex-col items-center text-center py-2">
                  <div className="text-4xl mb-2">
                    🏆🎉
                  </div>
                  <h3 className="text-base font-black text-emerald-800 uppercase tracking-tight mb-1">
                    CONGRATULATIONS, CHAMPION!
                  </h3>
                  <p className="text-xs text-gray-800 mb-3">
                    You have successfully passed the grueling 2000s verification gauntlet!
                  </p>

                  <div className="p-3 bg-white border-2 border-gray-500 rounded text-left text-xs mb-4 w-full">
                    <div className="font-bold text-red-600 mb-1">
                      ⚠️ PRIZE CONVERSION NOTICE:
                    </div>
                    <p className="text-gray-700 text-[11px] leading-relaxed">
                      Due to international holo-shipping restrictions, your <strong>iPhone 18</strong> and <strong>1 Bitcoin</strong> have been automatically converted into <strong>128 Gigabytes of 100% Free Pure Holographic RAM</strong> in the GeronimoHQ Holo-Chamber!
                    </p>
                  </div>

                  <button
                    onClick={handleClaimFinalPrize}
                    className="w-full py-2.5 bg-green-600 hover:bg-green-700 text-white font-black text-sm uppercase rounded border-2 border-black shadow-[0_4px_0_#000] active:translate-y-0.5 cursor-pointer tracking-wider"
                  >
                    🚀 DOWNLOAD MY 128GB RAM NOW!
                  </button>
                </div>
              )}

            </div>
          </div>
        </div>
      )}
    </>
  );
};
