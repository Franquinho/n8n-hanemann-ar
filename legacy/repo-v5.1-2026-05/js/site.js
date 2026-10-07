/**
 * Sitio — interacciones generales + animaciones premium con GSAP
 * - Reveal con ScrollTrigger (si GSAP cargó) o IntersectionObserver (fallback)
 * - Parallax sutil en hero
 * - Microinteracciones magnéticas en CTAs
 * - Cursor follower sutil para tarjetas
 * - Smooth scroll nativo
 */
(function () {
  'use strict';

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const hasGSAP = typeof window.gsap !== 'undefined';
  const hasScrollTrigger = hasGSAP && typeof window.ScrollTrigger !== 'undefined';

  /* ================================================================
     FALLBACK — IntersectionObserver para reveal si GSAP no cargó
     ================================================================ */
  function setupFallbackReveals() {
    const revealEls = document.querySelectorAll('.reveal, .reveal-stagger');
    if ('IntersectionObserver' in window && revealEls.length) {
      const io = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            io.unobserve(entry.target);
          }
        });
      }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });
      revealEls.forEach((el) => io.observe(el));
    } else {
      revealEls.forEach((el) => el.classList.add('is-visible'));
    }
  }

  /* ================================================================
     GSAP — Animaciones premium si está disponible
     ================================================================ */
  function setupGSAPAnimations() {
    if (!hasScrollTrigger) {
      setupFallbackReveals();
      return;
    }

    gsap.registerPlugin(ScrollTrigger);

    // --- LENIS — Smooth scroll premium (si está disponible)
    if (typeof window.Lenis !== 'undefined' && !reduceMotion) {
      const lenis = new window.Lenis({
        duration: 1.1,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
        smoothWheel: true,
        smoothTouch: false, // En mobile mejor el scroll nativo
        touchMultiplier: 1.5,
      });

      // Sincronizar Lenis con ScrollTrigger
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add((time) => { lenis.raf(time * 1000); });
      gsap.ticker.lagSmoothing(0);

      // Exponer globalmente para nav links
      window.__lenis = lenis;
    }

    // --- 1. Reveal estándar (.reveal) — fade up sutil
    gsap.utils.toArray('.reveal').forEach((el) => {
      gsap.fromTo(el,
        { opacity: 0, y: 28 },
        {
          opacity: 1,
          y: 0,
          duration: 0.9,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: el,
            start: 'top 88%',
            toggleActions: 'play none none none'
          }
        }
      );
    });

    // --- 2. Reveal-stagger — hijos en cascada
    gsap.utils.toArray('.reveal-stagger').forEach((parent) => {
      const children = parent.children;
      if (!children.length) return;
      gsap.fromTo(children,
        { opacity: 0, y: 32 },
        {
          opacity: 1,
          y: 0,
          duration: 0.75,
          stagger: 0.08,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: parent,
            start: 'top 85%',
            toggleActions: 'play none none none'
          }
        }
      );
    });

    // --- 3. Hero parallax muy sutil (turbina + texto en planos distintos)
    const heroStage = document.querySelector('.hero .stage');
    const heroCopy = document.querySelector('.hero .hero-copy');
    if (heroStage && heroCopy && !reduceMotion) {
      gsap.to(heroStage, {
        yPercent: 8,
        ease: 'none',
        scrollTrigger: {
          trigger: '.hero',
          start: 'top top',
          end: 'bottom top',
          scrub: 1
        }
      });
      gsap.to(heroCopy, {
        yPercent: -3,
        opacity: 0.85,
        ease: 'none',
        scrollTrigger: {
          trigger: '.hero',
          start: 'top top',
          end: 'bottom top',
          scrub: 1
        }
      });
    }

    // --- 4. H1 word reveal con stagger sofisticado
    const heroH1Words = document.querySelectorAll('.hero h1 .word');
    if (heroH1Words.length && !reduceMotion) {
      // cancelar la animación CSS original
      heroH1Words.forEach((w) => {
        w.style.animation = 'none';
        w.style.opacity = '0';
      });
      gsap.to(heroH1Words, {
        opacity: 1,
        y: 0,
        duration: 1.0,
        stagger: 0.09,
        ease: 'power4.out',
        delay: 0.15
      });
      gsap.fromTo(heroH1Words,
        { y: 36, filter: 'blur(8px)' },
        {
          y: 0,
          filter: 'blur(0px)',
          duration: 1.0,
          stagger: 0.09,
          ease: 'power4.out',
          delay: 0.15
        }
      );
    }

    // --- 5. Principio numérico — efecto al entrar
    const principles = document.querySelectorAll('.principle');
    principles.forEach((p, i) => {
      const num = p.querySelector('.principle-num');
      if (num) {
        gsap.fromTo(num,
          { scale: 0.7, opacity: 0 },
          {
            scale: 1,
            opacity: 1,
            duration: 0.6,
            ease: 'back.out(1.8)',
            scrollTrigger: {
              trigger: p,
              start: 'top 90%',
              toggleActions: 'play none none none'
            }
          }
        );
      }
    });

    // --- 6. Timeline items con slide-in alternado
    gsap.utils.toArray('.timeline-item').forEach((item, i) => {
      gsap.fromTo(item,
        { opacity: 0, x: -24 },
        {
          opacity: 1,
          x: 0,
          duration: 0.85,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: item,
            start: 'top 88%',
            toggleActions: 'play none none none'
          }
        }
      );
    });

    // --- 7. Phase cards — entrada con escala
    gsap.utils.toArray('.phase').forEach((phase, i) => {
      gsap.fromTo(phase,
        { opacity: 0, y: 40, scale: 0.96 },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.8,
          delay: i * 0.06,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: phase.parentElement,
            start: 'top 82%',
            toggleActions: 'play none none none'
          }
        }
      );
    });

    // --- 8. Guarantee cards — fade up con icono que pulsa al entrar
    gsap.utils.toArray('.guarantee').forEach((g, i) => {
      gsap.fromTo(g,
        { opacity: 0, y: 32 },
        {
          opacity: 1,
          y: 0,
          duration: 0.85,
          delay: i * 0.1,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: g.parentElement,
            start: 'top 82%',
            toggleActions: 'play none none none'
          }
        }
      );
      const icon = g.querySelector('.guarantee-icon');
      if (icon) {
        gsap.fromTo(icon,
          { scale: 0.6, rotate: -10 },
          {
            scale: 1,
            rotate: 0,
            duration: 0.7,
            delay: i * 0.1 + 0.2,
            ease: 'back.out(1.6)',
            scrollTrigger: {
              trigger: g.parentElement,
              start: 'top 82%',
              toggleActions: 'play none none none'
            }
          }
        );
      }
    });

    // --- 9. Bridge quote — efecto cinematográfico
    const bridge = document.querySelector('.bridge-quote');
    if (bridge) {
      const ps = bridge.querySelectorAll('p');
      gsap.fromTo(ps,
        { opacity: 0, y: 20 },
        {
          opacity: 1,
          y: 0,
          duration: 0.95,
          stagger: 0.18,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: bridge,
            start: 'top 78%',
            toggleActions: 'play none none none'
          }
        }
      );
    }

    // --- 10. Cierre (closer) — entrada dramática
    const closer = document.querySelector('.closer');
    if (closer) {
      gsap.fromTo(closer,
        { opacity: 0, y: 50, scale: 0.97 },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 1.0,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: closer,
            start: 'top 80%',
            toggleActions: 'play none none none'
          }
        }
      );
    }

    // --- 11. Workflow Showcase — Nodos y líneas se dibujan al scrollear
    const workflow = document.querySelector('.workflow-canvas');
    if (workflow) {
      const nodes = workflow.querySelectorAll('.wf-node');
      const lines = workflow.querySelectorAll('.wf-line');
      const caps = workflow.querySelectorAll('.wf-cap');

      // Timeline pinneada al scroll del showcase
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: '.section--showcase',
          start: 'top 70%',
          end: 'bottom 30%',
          toggleActions: 'play none none none'
        }
      });

      // IMPORTANTE: Solo animamos opacity en los nodos.
      // El transform del SVG <g> ya tiene translate(X, Y) — no lo tocamos.
      // Aparece nodo 1
      tl.to(nodes[0], { opacity: 1, duration: 0.5, ease: 'power3.out' });
      // Línea 1 se dibuja
      tl.to(lines[0], { strokeDashoffset: 0, duration: 0.6, ease: 'power2.inOut' }, '-=0.1');
      // Nodo 2
      tl.to(nodes[1], { opacity: 1, duration: 0.5, ease: 'power3.out' }, '-=0.2');
      // Línea 2
      tl.to(lines[1], { strokeDashoffset: 0, duration: 0.6, ease: 'power2.inOut' }, '-=0.1');
      // Nodo 3
      tl.to(nodes[2], { opacity: 1, duration: 0.5, ease: 'power3.out' }, '-=0.2');
      // Línea 3 (baja al sistema legacy)
      tl.to(lines[2], { strokeDashoffset: 0, duration: 0.7, ease: 'power2.inOut' }, '-=0.1');
      // Nodo 4 (sistema)
      tl.to(nodes[3], { opacity: 1, duration: 0.5, ease: 'power3.out' }, '-=0.3');
      // Línea 4 (sistema a logging)
      tl.to(lines[3], { strokeDashoffset: 0, duration: 0.6, ease: 'power2.inOut' }, '-=0.1');
      // Nodo 5 (observabilidad)
      tl.to(nodes[4], { opacity: 1, duration: 0.5, ease: 'power3.out' }, '-=0.2');
      // Línea 5 (notificación)
      tl.to(lines[4], { strokeDashoffset: 0, duration: 0.6, ease: 'power2.inOut' }, '-=0.1');
      // Nodo 6 (notificación)
      tl.to(nodes[5], { opacity: 1, duration: 0.5, ease: 'power3.out' }, '-=0.2');

      // Captions aparecen escalonadas (estas son divs HTML, sí podemos animar y)
      caps.forEach((cap, i) => {
        gsap.to(cap, {
          opacity: 1,
          y: 0,
          duration: 0.6,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: '.workflow-captions',
            start: 'top 85%',
            toggleActions: 'play none none none'
          },
          delay: i * 0.12
        });
      });
    }
  }

  /* ================================================================
     MICROINTERACCIONES — efecto magnético en CTAs principales
     ================================================================ */
  function setupMagneticButtons() {
    if (reduceMotion) return;
    const buttons = document.querySelectorAll('.btn-main, .btn-xl');
    buttons.forEach((btn) => {
      let raf = null;
      btn.addEventListener('mousemove', (e) => {
        const rect = btn.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const dx = (e.clientX - cx) * 0.18;
        const dy = (e.clientY - cy) * 0.18;
        if (raf) cancelAnimationFrame(raf);
        raf = requestAnimationFrame(() => {
          if (hasGSAP) {
            gsap.to(btn, { x: dx, y: dy, duration: 0.4, ease: 'power3.out' });
          } else {
            btn.style.transform = `translate(${dx}px, ${dy}px)`;
          }
        });
      });
      btn.addEventListener('mouseleave', () => {
        if (raf) cancelAnimationFrame(raf);
        if (hasGSAP) {
          gsap.to(btn, { x: 0, y: 0, duration: 0.6, ease: 'elastic.out(1, 0.4)' });
        } else {
          btn.style.transform = '';
        }
      });
    });
  }

  /* ================================================================
     CARD HOVER — spotlight que sigue el cursor
     ================================================================ */
  function setupCardSpotlight() {
    if (reduceMotion) return;
    const cards = document.querySelectorAll('.principle, .phase, .guarantee, .stack-group, .not-card');
    cards.forEach((card) => {
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        card.style.setProperty('--spot-x', x + '%');
        card.style.setProperty('--spot-y', y + '%');
      });
      card.addEventListener('mouseleave', () => {
        card.style.removeProperty('--spot-x');
        card.style.removeProperty('--spot-y');
      });
    });
  }

  /* ================================================================
     CURSOR CUSTOM — solo desktop, sigue el mouse con lerp
     ================================================================ */
  function setupCustomCursor() {
    if (reduceMotion) return;

    // Solo desktop con mouse fino
    const isTouchOrCoarse = window.matchMedia('(hover: none), (pointer: coarse)').matches;
    const isSmallScreen = window.innerWidth < 901;
    if (isTouchOrCoarse || isSmallScreen) return;

    const dot = document.querySelector('.cursor-dot');
    const ring = document.querySelector('.cursor-ring');
    if (!dot || !ring) return;

    let mx = window.innerWidth / 2;
    let my = window.innerHeight / 2;
    let rx = mx;
    let ry = my;

    // Activar cursor al primer movimiento
    let initialized = false;
    const onMove = (e) => {
      mx = e.clientX;
      my = e.clientY;
      if (!initialized) {
        document.body.classList.add('cursor-ready');
        initialized = true;
        rx = mx;
        ry = my;
      }
    };
    window.addEventListener('mousemove', onMove, { passive: true });

    // Loop con lerp para el ring (sigue suave); dot sigue exacto
    function loop() {
      // Dot: posición exacta
      dot.style.transform = `translate(${mx}px, ${my}px) translate(-50%, -50%)`;

      // Ring: lerp suave
      rx += (mx - rx) * 0.18;
      ry += (my - ry) * 0.18;
      ring.style.transform = `translate(${rx}px, ${ry}px) translate(-50%, -50%)`;

      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);

    // Hover states sobre interactivos
    const hoverSelectors = 'a, button, [role="button"], .si-dot, [data-open-chat], summary, input, textarea, select, label';
    document.querySelectorAll(hoverSelectors).forEach((el) => {
      el.addEventListener('mouseenter', () => document.body.classList.add('cursor-hover'));
      el.addEventListener('mouseleave', () => document.body.classList.remove('cursor-hover'));
    });

    // Esconder cursor cuando sale del viewport
    document.addEventListener('mouseleave', () => {
      dot.style.opacity = '0';
      ring.style.opacity = '0';
    });
    document.addEventListener('mouseenter', () => {
      dot.style.opacity = '';
      ring.style.opacity = '';
    });
  }

  /* ================================================================
     SECTION INDICATOR — sidebar con dots activos según scroll
     ================================================================ */
  function setupSectionIndicator() {
    const indicator = document.querySelector('.section-indicator');
    if (!indicator) return;

    // En móvil/tablet/medium-desktop no se usa
    if (window.innerWidth < 1321) return;

    const dots = indicator.querySelectorAll('.si-dot');
    const sections = [];

    dots.forEach((dot) => {
      const id = dot.dataset.section;
      const section = document.getElementById(id);
      if (section) sections.push({ dot, section });
    });

    if (!sections.length) return;

    // Mostrar el indicator
    setTimeout(() => indicator.classList.add('is-ready'), 800);

    // ScrollTrigger por cada sección — toggle is-active
    if (hasScrollTrigger) {
      sections.forEach(({ dot, section }) => {
        ScrollTrigger.create({
          trigger: section,
          start: 'top 40%',
          end: 'bottom 40%',
          onEnter: () => {
            dots.forEach((d) => d.classList.remove('is-active'));
            dot.classList.add('is-active');
          },
          onEnterBack: () => {
            dots.forEach((d) => d.classList.remove('is-active'));
            dot.classList.add('is-active');
          }
        });
      });
    } else {
      // Fallback: IntersectionObserver
      const io = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const id = entry.target.id;
            const match = sections.find((s) => s.section.id === id);
            if (match) {
              dots.forEach((d) => d.classList.remove('is-active'));
              match.dot.classList.add('is-active');
            }
          }
        });
      }, { rootMargin: '-40% 0px -40% 0px' });
      sections.forEach(({ section }) => io.observe(section));
    }
  }

  /* ================================================================
     NAV SCROLL — opaco al hacer scroll
     ================================================================ */
  function setupNavScroll() {
    const nav = document.querySelector('.top');
    if (!nav) return;
    const onScroll = () => {
      if (window.scrollY > 24) {
        nav.classList.add('is-scrolled');
      } else {
        nav.classList.remove('is-scrolled');
      }
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ================================================================
     SMOOTH NAV — scroll suave a anchors internos
     ================================================================ */
  function setupSmoothNav() {
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach((link) => {
      link.addEventListener('click', (e) => {
        const id = link.getAttribute('href');
        if (id && id.startsWith('#') && id.length > 1) {
          const target = document.querySelector(id);
          if (target) {
            e.preventDefault();
            const navH = document.querySelector('.top')?.offsetHeight || 0;
            const top = target.getBoundingClientRect().top + window.scrollY - navH - 20;
            if (window.__lenis) {
              window.__lenis.scrollTo(top, { duration: 1.2 });
            } else {
              window.scrollTo({ top, behavior: 'smooth' });
            }
            history.pushState(null, '', id);
          }
        }
      });
    });
  }

  /* ================================================================
     FOOTER YEAR
     ================================================================ */
  function setupFooter() {
    const yr = document.getElementById('foot-year');
    if (yr) yr.textContent = new Date().getFullYear();
  }

  /* ================================================================
     INIT
     ================================================================ */
  function init() {
    setupFooter();
    setupSmoothNav();
    setupNavScroll();
    if (reduceMotion) {
      // Sin animaciones: mostrar todo de una
      document.querySelectorAll('.reveal, .reveal-stagger').forEach((el) => {
        el.classList.add('is-visible');
      });
      return;
    }
    setupGSAPAnimations();
    setupMagneticButtons();
    setupCardSpotlight();
    setupCustomCursor();
    // Section indicator necesita esperar a que ScrollTrigger esté listo
    setTimeout(setupSectionIndicator, 300);
  }

  // Safety net — si GSAP tarda más de 2.5s, hacer fallback
  setTimeout(() => {
    if (!hasScrollTrigger && typeof window.ScrollTrigger === 'undefined') {
      console.warn('[site] GSAP no disponible, usando fallback');
      setupFallbackReveals();
    }
  }, 2500);

  // Backup ultimate — si nada de lo anterior funciona, en 4s mostrar todo
  setTimeout(() => {
    document.querySelectorAll('.reveal, .reveal-stagger').forEach((el) => {
      if (!el.classList.contains('is-visible') && getComputedStyle(el).opacity === '0') {
        el.classList.add('is-visible');
      }
    });
  }, 4000);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
