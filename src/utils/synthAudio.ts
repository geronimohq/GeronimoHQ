// Web Audio API Retro-Futuristic Synthwave Engine
// Zero external file dependencies - pure real-time browser audio synthesis!

class CyberSynthEngine {
  private ctx: AudioContext | null = null;
  private isPlaying = false;
  private timer: number | null = null;
  private step = 0;
  private masterGain: GainNode | null = null;

  // Cyberpunk synthwave minor arpeggio notes (Frequencies in Hz)
  // Progression: Am -> F -> C -> G
  private bassNotes = [110, 110, 110, 110, 87.31, 87.31, 87.31, 87.31, 130.81, 130.81, 130.81, 130.81, 98.00, 98.00, 98.00, 98.00];
  private leadNotes = [440, 523.25, 659.25, 523.25, 349.23, 440, 523.25, 440, 261.63, 329.63, 392, 329.63, 392, 493.88, 587.33, 493.88];

  public init() {
    if (!this.ctx) {
      const AudioContextClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      this.ctx = new AudioContextClass();
      this.masterGain = this.ctx.createGain();
      this.masterGain.gain.setValueAtTime(0.12, this.ctx.currentTime);
      this.masterGain.connect(this.ctx.destination);
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  public toggle(): boolean {
    this.init();
    if (this.isPlaying) {
      this.stop();
      return false;
    } else {
      this.start();
      return true;
    }
  }

  public getIsPlaying(): boolean {
    return this.isPlaying;
  }

  private start() {
    if (!this.ctx || !this.masterGain) return;
    this.isPlaying = true;
    const intervalMs = 125; // 120 BPM 16th notes

    this.timer = window.setInterval(() => {
      if (!this.ctx || !this.masterGain) return;

      const now = this.ctx.currentTime;
      const bassFreq = this.bassNotes[this.step % this.bassNotes.length];
      const leadFreq = this.leadNotes[this.step % this.leadNotes.length];

      // Bass synth (sawtooth + lowpass filter)
      const bassOsc = this.ctx.createOscillator();
      const bassGain = this.ctx.createGain();
      const filter = this.ctx.createBiquadFilter();

      bassOsc.type = 'sawtooth';
      bassOsc.frequency.setValueAtTime(bassFreq / 2, now);

      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(450, now);
      filter.Q.setValueAtTime(4, now);

      bassGain.gain.setValueAtTime(0.3, now);
      bassGain.gain.exponentialRampToValueAtTime(0.01, now + 0.12);

      bassOsc.connect(filter);
      filter.connect(bassGain);
      bassGain.connect(this.masterGain);

      bassOsc.start(now);
      bassOsc.stop(now + 0.13);

      // Lead arpeggio synth (bright square wave with delay feel)
      if (this.step % 2 === 0) {
        const leadOsc = this.ctx.createOscillator();
        const leadGain = this.ctx.createGain();

        leadOsc.type = 'sine';
        leadOsc.frequency.setValueAtTime(leadFreq, now);

        leadGain.gain.setValueAtTime(0.18, now);
        leadGain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);

        leadOsc.connect(leadGain);
        leadGain.connect(this.masterGain);

        leadOsc.start(now);
        leadOsc.stop(now + 0.23);
      }

      this.step++;
    }, intervalMs);
  }

  public stop() {
    this.isPlaying = false;
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }
}

export const cyberSynth = new CyberSynthEngine();
