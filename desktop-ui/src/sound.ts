/** Interface sounds, synthesised with Web Audio (no audio files). Start only after the first click. */
let ac: AudioContext | null = null;
let enabled = true;
try { enabled = localStorage.getItem('sfx') !== 'off'; } catch { /* storage unavailable */ }

function ctx(): AudioContext | null {
  if (!ac) {
    try { ac = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)(); } catch { /* no audio */ }
  }
  return ac;
}
function tone(f: number, d: number, type: OscillatorType, g: number, to?: number) {
  const c = ctx();
  if (!c || !enabled) return;
  if (c.state === 'suspended') void c.resume();
  const o = c.createOscillator(), a = c.createGain(), t = c.currentTime;
  o.type = type;
  o.frequency.setValueAtTime(f, t);
  if (to) o.frequency.exponentialRampToValueAtTime(to, t + d);
  a.gain.setValueAtTime(g, t);
  a.gain.exponentialRampToValueAtTime(0.0001, t + d);
  o.connect(a); a.connect(c.destination);
  o.start(t); o.stop(t + d + 0.02);
}

export const sfx = {
  click: () => tone(1900, 0.05, 'square', 0.03, 900),
  hover: () => tone(110, 0.03, 'sine', 0.02),
  toggle: () => { tone(520, 0.05, 'triangle', 0.05, 780); setTimeout(() => tone(1040, 0.06, 'triangle', 0.04), 45); },
  alert: () => tone(660, 0.18, 'sine', 0.05, 990),
  get on() { return enabled; },
  set(v: boolean) { enabled = v; try { localStorage.setItem('sfx', v ? 'on' : 'off'); } catch { /* ignore */ } },
};
