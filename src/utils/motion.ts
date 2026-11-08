import canvasConfetti from 'canvas-confetti';

/**
 * Returns true if the user's OS or browser has requested reduced motion.
 */
export function isReducedMotionPreferred(): boolean {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
    return false;
  }
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/**
 * Centralized, accessibility-safe confetti wrapper.
 * Strictly respects WCAG 2.2 and OS-level prefers-reduced-motion settings.
 */
export function safeConfetti(opts?: any): void {
  if (isReducedMotionPreferred()) {
    return;
  }
  canvasConfetti({
    ...opts,
    disableForReducedMotion: true,
  });
}
