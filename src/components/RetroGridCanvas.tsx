import React, { useEffect, useRef } from 'react';

interface RetroGridCanvasProps {
  glowColor?: string;
  gridColor?: string;
}

export const RetroGridCanvas: React.FC<RetroGridCanvasProps> = ({
  glowColor = '#ff007f',
  gridColor = '#00f0ff',
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);

    // Mouse parallax
    let targetMouseX = width / 2;
    let targetMouseY = height / 2;
    let mouseX = width / 2;
    let mouseY = height / 2;

    const handleMouseMove = (e: MouseEvent) => {
      targetMouseX = e.clientX;
      targetMouseY = e.clientY;
    };

    window.addEventListener('mousemove', handleMouseMove);

    // Floating digital dust particles
    interface Particle {
      x: number;
      y: number;
      size: number;
      speedY: number;
      speedX: number;
      opacity: number;
      hue: number;
    }

    const particles: Particle[] = Array.from({ length: 65 }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      size: Math.random() * 2 + 0.8,
      speedY: -(Math.random() * 0.7 + 0.2),
      speedX: (Math.random() - 0.5) * 0.4,
      opacity: Math.random() * 0.7 + 0.3,
      hue: Math.random() > 0.5 ? 185 : 320, // Cyan or Magenta
    }));

    let gridOffset = 0;

    const render = () => {
      // Smooth mouse lerp
      mouseX += (targetMouseX - mouseX) * 0.05;
      mouseY += (targetMouseY - mouseY) * 0.05;

      const tiltX = (mouseX / width - 0.5) * 40;
      const tiltY = (mouseY / height - 0.5) * 20;

      ctx.clearRect(0, 0, width, height);

      // Deep Cyberpunk Vignette & Horizon Gradient
      const bgGrad = ctx.createRadialGradient(
        width / 2 + tiltX,
        height * 0.45 + tiltY,
        10,
        width / 2,
        height / 2,
        Math.max(width, height) * 0.8
      );
      bgGrad.addColorStop(0, '#0c1020');
      bgGrad.addColorStop(0.5, '#060810');
      bgGrad.addColorStop(1, '#020306');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, width, height);

      // Horizon Glow / Synth Sunset Arc
      const horizonY = height * 0.58 + tiltY * 0.4;
      const horizonGlow = ctx.createRadialGradient(
        width / 2 + tiltX * 0.5,
        horizonY,
        5,
        width / 2 + tiltX * 0.5,
        horizonY,
        width * 0.5
      );
      horizonGlow.addColorStop(0, 'rgba(255, 0, 127, 0.28)');
      horizonGlow.addColorStop(0.3, 'rgba(0, 240, 255, 0.16)');
      horizonGlow.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = horizonGlow;
      ctx.fillRect(0, 0, width, height);

      // Perspective 3D Grid Floor
      const gridLines = 28;
      const vanishingX = width / 2 + tiltX * 0.8;
      const vanishingY = horizonY;

      // Draw Perspective Lines (Fan radiating from horizon)
      ctx.save();
      ctx.lineWidth = 1;
      for (let i = -gridLines; i <= gridLines; i++) {
        const xBottom = width / 2 + i * (width / (gridLines * 0.8)) + tiltX * 1.5;
        const lineGrad = ctx.createLinearGradient(vanishingX, vanishingY, xBottom, height);
        lineGrad.addColorStop(0, 'rgba(0, 240, 255, 0.05)');
        lineGrad.addColorStop(0.5, 'rgba(0, 240, 255, 0.25)');
        lineGrad.addColorStop(1, 'rgba(255, 0, 127, 0.6)');
        
        ctx.strokeStyle = lineGrad;
        ctx.beginPath();
        ctx.moveTo(vanishingX, vanishingY);
        ctx.lineTo(xBottom, height);
        ctx.stroke();
      }

      // Draw Horizontal Moving Lines
      gridOffset = (gridOffset + 0.8) % 40;
      const numHorizLines = 22;
      for (let j = 1; j < numHorizLines; j++) {
        // Perspective distance exponential mapping
        const progress = Math.pow(j / numHorizLines, 2.2);
        const y = vanishingY + progress * (height - vanishingY);
        const alpha = Math.min(progress * 0.9, 0.65);

        ctx.strokeStyle = `rgba(0, 240, 255, ${alpha})`;
        ctx.lineWidth = 1 + progress * 1.2;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Digital Horizon Neon Line
      ctx.strokeStyle = 'rgba(0, 240, 255, 0.7)';
      ctx.lineWidth = 2;
      ctx.shadowColor = '#00f0ff';
      ctx.shadowBlur = 10;
      ctx.beginPath();
      ctx.moveTo(0, vanishingY);
      ctx.lineTo(width, vanishingY);
      ctx.stroke();
      ctx.shadowBlur = 0;
      ctx.restore();

      // Floating Cyber Dust / Spark Particles
      particles.forEach((p) => {
        p.y += p.speedY;
        p.x += p.speedX;

        if (p.y < 0) {
          p.y = height + 10;
          p.x = Math.random() * width;
        }

        ctx.fillStyle = `hsla(${p.hue}, 100%, 70%, ${p.opacity})`;
        ctx.shadowColor = p.hue === 185 ? '#00f0ff' : '#ff007f';
        ctx.shadowBlur = 6;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
      });
      ctx.shadowBlur = 0;

      animationFrameId = requestAnimationFrame(render);
    };

    const prefersReducedMotion = typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) {
      // Draw static cyber grid once without starting animation frame loop
      render();
      return () => {
        window.removeEventListener('resize', handleResize);
        window.removeEventListener('mousemove', handleMouseMove);
      };
    }

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, [glowColor, gridColor]);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0 opacity-80"
      style={{ filter: 'contrast(1.1) brightness(0.95)' }}
    />
  );
};
