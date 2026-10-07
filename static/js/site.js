/* n8n.hanemann.ar — comportamiento compartido por las tres portadas.
   Config por página en <script id="site-config" type="application/json">. */
(function () {
  'use strict';

  var cfg = {};
  try { cfg = JSON.parse(document.getElementById('site-config').textContent); } catch (_) {}

  // ---- Año en el footer ----
  var yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // ---- Nav con fondo al scrollear ----
  var navTop = document.getElementById('top');
  if (navTop) {
    var onScroll = function () { navTop.classList.toggle('is-scrolled', window.scrollY > 16); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // ---- Aparición al scrollear (contenido visible por defecto) ----
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduceMotion && 'IntersectionObserver' in window) {
    document.documentElement.classList.add('anim');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    document.querySelectorAll('.reveal, .reveal-stagger').forEach(function (el) { io.observe(el); });
  }

  // ---- Chat (bot real en n8n) ----
  var chat = document.getElementById('chat');
  if (chat) {
    var scrim = document.getElementById('chat-scrim');
    var body = document.getElementById('chat-body');
    var chips = document.getElementById('chat-chips');
    var input = document.getElementById('chat-text');
    var lastFocus = null;

    var open = function () {
      lastFocus = document.activeElement;
      chat.hidden = false; scrim.hidden = false;
      requestAnimationFrame(function () { chat.classList.add('open'); scrim.classList.add('open'); });
      input.focus();
    };
    var close = function () {
      chat.classList.remove('open'); scrim.classList.remove('open');
      setTimeout(function () { chat.hidden = true; scrim.hidden = true; }, 260);
      if (lastFocus) lastFocus.focus();
    };
    document.querySelectorAll('[data-cta="bot"], #bot-fab').forEach(function (b) { b.addEventListener('click', open); });
    document.getElementById('chat-x').addEventListener('click', close);
    scrim.addEventListener('click', close);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !chat.hidden) close(); });

    var sessionId;
    try {
      sessionId = localStorage.getItem('hane_bot_session');
      if (!sessionId) {
        sessionId = (window.crypto && crypto.randomUUID) ? crypto.randomUUID() : 'sess-' + Date.now() + '-' + Math.random().toString(36).slice(2);
        localStorage.setItem('hane_bot_session', sessionId);
      }
    } catch (_) {
      sessionId = 'sess-' + Date.now() + '-' + Math.random().toString(36).slice(2);
    }

    var push = function (text, who) {
      var el = document.createElement('div');
      el.className = 'msg msg--' + who;
      var p = document.createElement('p');
      p.textContent = text;
      el.appendChild(p);
      body.insertBefore(el, chips);
      body.scrollTop = body.scrollHeight;
      return el;
    };
    var showTyping = function () {
      var el = document.createElement('div');
      el.className = 'msg msg--bot msg--typing';
      el.innerHTML = '<p><span class="typing-dots"><i></i><i></i><i></i></span></p>';
      body.insertBefore(el, chips);
      body.scrollTop = body.scrollHeight;
      return el;
    };
    var extractReply = function (data) {
      if (data == null) return '';
      if (typeof data === 'string') return data.trim();
      if (Array.isArray(data)) {
        for (var i = 0; i < data.length; i++) { var r = extractReply(data[i]); if (r) return r; }
        return '';
      }
      if (typeof data === 'object') {
        var keys = ['reply', 'output', 'response', 'text', 'message', 'answer', 'result', 'content'];
        for (var k = 0; k < keys.length; k++) {
          if (typeof data[keys[k]] === 'string' && data[keys[k]].trim()) return data[keys[k]].trim();
        }
        if (data.data) { var d = extractReply(data.data); if (d) return d; }
        if (data.json) { var j = extractReply(data.json); if (j) return j; }
      }
      return '';
    };

    var busy = false;
    var ask = function (q) {
      if (busy || !q) return;
      push(q, 'me');
      busy = true;
      var typingEl = showTyping();
      var done = function (reply) {
        typingEl.remove();
        push(reply || cfg.error || '…', 'bot');
        busy = false;
      };
      fetch(cfg.webhook, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: q, chatInput: q, sessionId: sessionId,
          token: cfg.token, lang: cfg.lang, page: location.pathname
        })
      }).then(function (res) {
        if (!res.ok) return '';
        var ct = res.headers.get('content-type') || '';
        return ct.indexOf('application/json') > -1 ? res.json().then(extractReply) : res.text().then(function (t) { return t.trim(); });
      }).then(done, function () { done(''); });
    };

    chips.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      ask(b.dataset.q);
    });
    document.getElementById('chat-form').addEventListener('submit', function (e) {
      e.preventDefault();
      var v = input.value.trim(); if (!v) return;
      ask(v); input.value = '';
    });
  }

  // ---- Turbina del hero: 13 aspas (diseño de Franco) ----
  var canvas = document.getElementById('hero-turbina');
  if (canvas && canvas.getContext) {
    var ctx = canvas.getContext('2d');
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var TWO_PI = Math.PI * 2, N = 13, TILT = 20 * Math.PI / 180;
    var SPEED = 1.2, CURVE = 0.37, LEAN = 0.14, CORE = 0.06;
    var size = 0, cx = 0, cy = 0, R = 0, t = 0, raf = null;

    var resize = function () {
      var rect = canvas.getBoundingClientRect();
      size = Math.max(60, Math.round(rect.width || 200));
      canvas.width = Math.floor(size * dpr); canvas.height = Math.floor(size * dpr);
      ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.scale(dpr, dpr);
      cx = size / 2; cy = size / 2; R = size * 0.43;
    };
    var blade = function (c) {
      c.moveTo(0, 0);
      c.bezierCurveTo(-R * 0.06, -R * 0.28, -R * (0.06 + LEAN * 0.5), -R * 0.62, -R * LEAN, -R);
      c.bezierCurveTo(R * CURVE, -R * 0.72, R * (CURVE - 0.04), -R * 0.22, 0, 0);
      c.closePath();
    };
    var draw = function () {
      ctx.clearRect(0, 0, size, size);
      t += reduceMotion ? 0 : 0.020 * SPEED + Math.sin(t * 0.45) * 0.002;
      ctx.save(); ctx.translate(cx, cy); ctx.rotate(TILT); ctx.rotate(t);
      ctx.beginPath();
      for (var i = 0; i < N; i++) { ctx.save(); ctx.rotate((TWO_PI * i) / N); blade(ctx); ctx.restore(); }
      ctx.shadowColor = 'rgba(100, 0, 0, 0.42)'; ctx.shadowBlur = 12; ctx.shadowOffsetX = 2; ctx.shadowOffsetY = 3;
      var g = ctx.createRadialGradient(0, 0, R * 0.08, 0, 0, R * 1.05);
      g.addColorStop(0, '#FF2A3E'); g.addColorStop(0.45, '#C8141E'); g.addColorStop(1, '#6C000A');
      ctx.fillStyle = g; ctx.fill(); ctx.restore();
      ctx.save(); ctx.translate(cx, cy);
      var cg = ctx.createRadialGradient(0, 0, 0, 0, 0, R * 0.16);
      cg.addColorStop(0, 'rgba(255, 225, 225, ' + CORE + ')');
      cg.addColorStop(0.45, 'rgba(217, 33, 50, ' + (CORE * 0.5) + ')');
      cg.addColorStop(1, 'rgba(120, 0, 0, 0)');
      ctx.fillStyle = cg; ctx.beginPath(); ctx.arc(0, 0, R * 0.16, 0, TWO_PI); ctx.fill(); ctx.restore();
      raf = reduceMotion ? null : requestAnimationFrame(draw);
    };
    resize(); draw();
    var rt;
    window.addEventListener('resize', function () {
      clearTimeout(rt);
      rt = setTimeout(function () { if (raf) cancelAnimationFrame(raf); raf = null; resize(); draw(); }, 150);
    });
    if ('IntersectionObserver' in window && !reduceMotion) {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { if (!raf) draw(); }
          else if (raf) { cancelAnimationFrame(raf); raf = null; }
        });
      }, { threshold: 0.05 }).observe(canvas);
    }
  }
})();
