import confetti from 'canvas-confetti';

export const triggerMonochromeConfetti = () => {
  const count = 200;
  const defaults = {
    origin: { y: 1 },
    colors: ['#000000', '#ffffff', '#e2e2df', '#5f5f5c', '#191918'],
    disableForReducedMotion: true
  };

  function fire(particleRatio: number, opts: confetti.Options) {
    void confetti({
      ...defaults,
      ...opts,
      particleCount: Math.floor(count * particleRatio)
    });
  }

  fire(0.25, { spread: 26, startVelocity: 55 });
  fire(0.2, { spread: 60 });
  fire(0.35, { spread: 100, decay: 0.91, scalar: 0.8 });
  fire(0.1, { spread: 120, startVelocity: 25, decay: 0.92, scalar: 1.2 });
  fire(0.1, { spread: 120, startVelocity: 45 });
};
