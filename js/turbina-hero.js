/**
 * Turbina canvas — 13 aspas asimétricas inclinadas
 *
 * Parámetros finales:
 *   tilt   = 20°
 *   speed  = 0.6×
 *   curve  = 37%
 *   lean   = 14%
 *   core   = 6%
 *
 * RENDERIZADO UNIFICADO:
 * Todas las aspas se construyen como un único path continuo y se rinden
 * con UN solo fill() usando un gradiente radial global. Resultado: la
 * silueta se ve como una sola forma sin divisiones internas visibles.
 *
 * Mantiene:
 * - 13 aspas (simbolismo personal)
 * - DPR / nitidez retina
 * - Pausa fuera de viewport
 * - Respeto a prefers-reduced-motion
 */
(function () {
  const canvas = document.getElementById('hero-turbina');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const TWO_PI = Math.PI * 2;
  const N = 13;

  const TILT_DEG = 20;
  const SPEED_FACTOR = 1.2;
  const CURVE = 0.37;
  const LEAN = 0.14;
  const CORE_OPACITY = 0.06;

  const TILT = TILT_DEG * Math.PI / 180;
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  let displaySize = 0;
  let cx = 0;
  let cy = 0;
  let bladeRadius = 0;
  let t = 0;
  let rafId = null;

  function resize() {
    const rect = canvas.getBoundingClientRect();
    displaySize = Math.max(60, Math.round(rect.width || 200));
    canvas.width = Math.floor(displaySize * dpr);
    canvas.height = Math.floor(displaySize * dpr);
    canvas.style.width = displaySize + 'px';
    canvas.style.height = displaySize + 'px';
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(dpr, dpr);
    cx = displaySize / 2;
    cy = displaySize / 2;
    bladeRadius = displaySize * 0.43;
  }

  function addBladeSubpath(c) {
    const r = bladeRadius;
    c.moveTo(0, 0);
    c.bezierCurveTo(
      -r * 0.06, -r * 0.28,
      -r * (0.06 + LEAN * 0.5), -r * 0.62,
      -r * LEAN, -r
    );
    c.bezierCurveTo(
       r * CURVE, -r * 0.72,
       r * (CURVE - 0.04), -r * 0.22,
       0, 0
    );
    c.closePath();
  }

  function draw() {
    ctx.clearRect(0, 0, displaySize, displaySize);

    // La turbina gira siempre como identidad de marca, pero más lento si hay reduced-motion
    const breath = reduceMotion
      ? 0.004
      : 0.020 * SPEED_FACTOR + Math.sin(t * 0.45) * 0.002;
    t += breath;

    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(TILT);
    ctx.rotate(t);

    // Construir TODAS las aspas como un único path continuo
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      ctx.save();
      ctx.rotate((TWO_PI * i) / N);
      addBladeSubpath(ctx);
      ctx.restore();
    }

    // Sombra externa para asentar la figura sobre el fondo oscuro
    ctx.shadowColor = 'rgba(100, 0, 0, 0.42)';
    ctx.shadowBlur = 12;
    ctx.shadowOffsetX = 2;
    ctx.shadowOffsetY = 3;

    // Gradiente radial global aplicado UNA sola vez sobre toda la silueta
    const baseGrad = ctx.createRadialGradient(0, 0, bladeRadius * 0.08, 0, 0, bladeRadius * 1.05);
    baseGrad.addColorStop(0, '#FF2A3E');
    baseGrad.addColorStop(0.45, '#C8141E');
    baseGrad.addColorStop(1, '#6C000A');
    ctx.fillStyle = baseGrad;

    ctx.fill();
    ctx.restore();

    // Núcleo central (muy sutil con core=6%)
    if (CORE_OPACITY > 0) {
      ctx.save();
      ctx.translate(cx, cy);
      const coreGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, bladeRadius * 0.16);
      coreGrad.addColorStop(0, 'rgba(255, 225, 225, ' + CORE_OPACITY + ')');
      coreGrad.addColorStop(0.45, 'rgba(217, 33, 50, ' + (CORE_OPACITY * 0.5) + ')');
      coreGrad.addColorStop(1, 'rgba(120, 0, 0, 0)');
      ctx.fillStyle = coreGrad;
      ctx.beginPath();
      ctx.arc(0, 0, bladeRadius * 0.16, 0, TWO_PI);
      ctx.fill();
      ctx.restore();
    }

    rafId = requestAnimationFrame(draw);
  }

  resize();
  draw();

  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      cancelAnimationFrame(rafId);
      resize();
      draw();
    }, 150);
  });

  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          if (!rafId) draw();
        } else {
          if (rafId) {
            cancelAnimationFrame(rafId);
            rafId = null;
          }
        }
      });
    }, { threshold: 0.05 });
    io.observe(canvas);
  }
})();
