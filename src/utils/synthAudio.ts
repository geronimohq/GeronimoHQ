// Web Audio API Retro-Futuristic Cyberpunk Darksynth Engine
// Pure browser audio synthesis - Zero external files!
// Strictly plays for the Pepe Retro-Futuristic theme (never overlaps with Banana Phone music)

class CyberSynthEngine {
  private ctx: AudioContext | null = null;
  private isPlaying = false;
  private timer: number | null = null;
  private step = 0;
  private masterGain: GainNode | null = null;
  private unlockBound = false;
  private volumeMultiplier = 0.20; // default 20%

  public setVolume(percent: number) {
    this.volumeMultiplier = Math.max(0, Math.min(100, percent)) / 100;
    if (this.ctx && this.masterGain) {
      const baseGain = 0.45;
      this.masterGain.gain.setValueAtTime(baseGain * this.volumeMultiplier, this.ctx.currentTime);
    }
  }

  public getVolume(): number {
    return Math.round(this.volumeMultiplier * 100);
  }

  // D-Minor Bassline (D1, D1, D2, D1, F1, F1, C1, Bb1)
  private bassNotes = [
    73.42, 73.42, 146.83, 73.42, 87.31, 87.31, 146.83, 87.31,
    65.41, 65.41, 130.81, 65.41, 58.27, 58.27, 116.54, 58.27
  ];

  // Neon Arpeggio Lead (D minor / F maj / C maj / Bb maj arpeggios in Hz)
  private leadNotes = [
    587.33, 698.46, 880.00, 1046.50, 698.46, 880.00, 1046.50, 1174.66,
    523.25, 659.25, 783.99, 1046.50, 466.16, 587.33, 698.46, 880.00
  ];

  private ensureUnlockListeners() {
    if (this.unlockBound || typeof window === 'undefined') return;
    this.unlockBound = true;

    const tryResume = () => {
      if (!this.isPlaying) return;
      if (!this.ctx) {
        this.initContext();
      }
      if (this.ctx && this.ctx.state !== 'running') {
        this.ctx.resume().catch(() => {});
      }
    };

    // Capture-phase listeners ensure the very first user gesture anywhere in the tab
    // immediately unlocks and starts the synth without needing to toggle the button twice.
    const events = ['pointerdown', 'mousedown', 'keydown', 'touchstart', 'wheel', 'click'];
    events.forEach((evt) => {
      window.addEventListener(evt, tryResume, { capture: true, passive: true });
    });
  }

  private initContext() {
    if (!this.ctx && typeof window !== 'undefined') {
      const AudioContextClass =
        window.AudioContext ||
        (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      if (AudioContextClass) {
        try {
          this.ctx = new AudioContextClass();
          this.masterGain = this.ctx.createGain();
          this.masterGain.gain.setValueAtTime(0.45 * this.volumeMultiplier, this.ctx.currentTime);
          this.masterGain.connect(this.ctx.destination);
        } catch {
          // ignore
        }
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume().catch(() => {});
    }
  }

  public startSynth() {
    this.ensureUnlockListeners();
    this.initContext();
    this.isPlaying = true;

    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume().catch(() => {});
    }

    if (this.timer !== null) {
      return;
    }

    const stepIntervalMs = 125; // 120 BPM 16th-note clock
    this.timer = window.setInterval(() => {
      if (!this.isPlaying) return;
      if (!this.ctx || !this.masterGain) {
        this.initContext();
        return;
      }
      if (this.ctx.state === 'suspended') {
        this.ctx.resume().catch(() => {});
        return;
      }

      const now = this.ctx.currentTime;
      const stepInMeasure = this.step % 16;

      // 1. Four-on-the-floor Punchy Kick Drum (Beats 1, 2, 3, 4)
      if (stepInMeasure % 4 === 0) {
        this.triggerKick(now);
      }

      // 2. Snappy Electro Snare on Beats 2 and 4 (Steps 4 and 12)
      if (stepInMeasure === 4 || stepInMeasure === 12) {
        this.triggerSnare(now);
      }

      // 3. Off-beat Hi-Hats
      if (stepInMeasure % 2 === 1) {
        this.triggerHiHat(now);
      }

      // 4. Rolling 16th-note Analog Bassline
      const bassFreq = this.bassNotes[this.step % this.bassNotes.length];
      const bassOsc = this.ctx.createOscillator();
      const bassGain = this.ctx.createGain();
      const bassFilter = this.ctx.createBiquadFilter();

      bassOsc.type = 'sawtooth';
      bassOsc.frequency.setValueAtTime(bassFreq, now);

      bassFilter.type = 'lowpass';
      const sweepCutoff = 350 + (stepInMeasure % 4) * 80;
      bassFilter.frequency.setValueAtTime(sweepCutoff, now);
      bassFilter.Q.setValueAtTime(5, now);

      bassGain.gain.setValueAtTime(0.24, now);
      bassGain.gain.exponentialRampToValueAtTime(0.02, now + 0.11);

      bassOsc.connect(bassFilter);
      bassFilter.connect(bassGain);
      bassGain.connect(this.masterGain);

      bassOsc.start(now);
      bassOsc.stop(now + 0.12);

      // 5. Shimmering Neon Arpeggio Lead
      if (stepInMeasure % 2 === 0) {
        const idx = (this.step / 2) % this.leadNotes.length;
        const leadFreq = this.leadNotes[idx];
        const leadOsc = this.ctx.createOscillator();
        const leadGain = this.ctx.createGain();
        const leadFilter = this.ctx.createBiquadFilter();

        leadOsc.type = 'square';
        leadOsc.frequency.setValueAtTime(leadFreq, now);

        leadFilter.type = 'bandpass';
        leadFilter.frequency.setValueAtTime(leadFreq, now);
        leadFilter.Q.setValueAtTime(2, now);

        leadGain.gain.setValueAtTime(0.12, now);
        leadGain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);

        leadOsc.connect(leadFilter);
        leadFilter.connect(leadGain);
        leadGain.connect(this.masterGain);

        leadOsc.start(now);
        leadOsc.stop(now + 0.23);
      }

      this.step++;
    }, stepIntervalMs);
  }

  public stopSynth() {
    this.isPlaying = false;
    if (this.timer !== null) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }

  public getIsPlaying(): boolean {
    return this.isPlaying;
  }

  private triggerKick(now: number) {
    if (!this.ctx || !this.masterGain) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(140, now);
    osc.frequency.exponentialRampToValueAtTime(36, now + 0.08);

    gain.gain.setValueAtTime(0.5, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.16);

    osc.connect(gain);
    gain.connect(this.masterGain);

    osc.start(now);
    osc.stop(now + 0.17);
  }

  private triggerSnare(now: number) {
    if (!this.ctx || !this.masterGain) return;
    const bufferSize = this.ctx.sampleRate * 0.1;
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const output = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      output[i] = Math.random() * 2 - 1;
    }

    const whiteNoise = this.ctx.createBufferSource();
    whiteNoise.buffer = buffer;

    const filter = this.ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.setValueAtTime(1200, now);
    filter.Q.setValueAtTime(1.5, now);

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0.28, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.14);

    whiteNoise.connect(filter);
    filter.connect(gain);
    gain.connect(this.masterGain);

    whiteNoise.start(now);
    whiteNoise.stop(now + 0.15);
  }

  private triggerHiHat(now: number) {
    if (!this.ctx || !this.masterGain) return;
    const bufferSize = this.ctx.sampleRate * 0.04;
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const output = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      output[i] = Math.random() * 2 - 1;
    }

    const whiteNoise = this.ctx.createBufferSource();
    whiteNoise.buffer = buffer;

    const filter = this.ctx.createBiquadFilter();
    filter.type = 'highpass';
    filter.frequency.setValueAtTime(6500, now);

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0.07, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.04);

    whiteNoise.connect(filter);
    filter.connect(gain);
    gain.connect(this.masterGain);

    whiteNoise.start(now);
    whiteNoise.stop(now + 0.05);
  }
}

export const cyberSynth = new CyberSynthEngine();
