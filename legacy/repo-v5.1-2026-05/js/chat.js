/**
 * Chatbot — UI completa, lista para enchufar n8n
 *
 * CONFIGURACIÓN DEL BACKEND
 * -------------------------
 * Cuando el flujo de n8n esté listo, definí la URL del webhook en una de estas formas:
 *
 *   1) Global JS:
 *      window.AGENT_CHAT_CONFIG = { endpoint: 'https://n8n.tu-dominio.com/webhook/agent-chat' };
 *
 *   2) Meta tag en el HTML:
 *      <meta name="agent-chat-endpoint" content="https://...">
 *
 * Si no hay endpoint configurado, el chatbot responde en modo DEMO (respuestas locales).
 *
 * CONTRATO con el webhook
 * -----------------------
 * Request (POST JSON):
 *   {
 *     "sessionId": "uuid-string",
 *     "message": "texto del usuario",
 *     "history": [ { "role": "user|assistant", "content": "..." }, ... ]
 *   }
 *
 * Response esperada (JSON):
 *   { "reply": "respuesta del agente" }
 *   // o también acepta:  { "output": "..." }   { "message": "..." }   { "text": "..." }
 */
(function () {
  const trigger = document.getElementById('chat-trigger');
  const drawer = document.getElementById('chat-drawer');
  const overlay = document.getElementById('chat-overlay');
  const closeBtn = document.getElementById('chat-close');
  const body = document.getElementById('chat-body');
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input');
  const sendBtn = document.getElementById('chat-send');
  const suggestions = document.querySelectorAll('[data-suggestion]');

  if (!trigger || !drawer) return;

  /* ---------- Config ---------- */
  function getEndpoint() {
    if (window.AGENT_CHAT_CONFIG && window.AGENT_CHAT_CONFIG.endpoint) {
      return window.AGENT_CHAT_CONFIG.endpoint;
    }
    const meta = document.querySelector('meta[name="agent-chat-endpoint"]');
    if (meta && meta.content) return meta.content;
    return null;
  }

  /* ---------- Estado ---------- */
  const SESSION_KEY = 'agent-chat-session-id';
  const HISTORY_KEY = 'agent-chat-history';

  function getSessionId() {
    let id = sessionStorage.getItem(SESSION_KEY);
    if (!id) {
      id = 'sess_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 8);
      sessionStorage.setItem(SESSION_KEY, id);
    }
    return id;
  }

  let history = [];
  try {
    const stored = sessionStorage.getItem(HISTORY_KEY);
    if (stored) history = JSON.parse(stored);
  } catch (e) { history = []; }

  function persistHistory() {
    try {
      sessionStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(-30)));
    } catch (e) {}
  }

  /* ---------- Apertura / cierre ---------- */
  let lastFocus = null;

  function openChat() {
    lastFocus = document.activeElement;
    drawer.classList.add('--open');
    overlay.classList.add('--open');
    trigger.classList.add('--hidden');
    trigger.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
    setTimeout(() => input && input.focus(), 350);
  }

  function closeChat() {
    drawer.classList.remove('--open');
    overlay.classList.remove('--open');
    trigger.classList.remove('--hidden');
    trigger.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  trigger.addEventListener('click', openChat);
  closeBtn.addEventListener('click', closeChat);
  overlay.addEventListener('click', closeChat);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && drawer.classList.contains('--open')) closeChat();
  });

  // Conectar todos los botones con data-open-chat (botón del hero, etc.)
  document.querySelectorAll('[data-open-chat]').forEach((btn) => {
    btn.addEventListener('click', openChat);
  });

  /* ---------- Render de mensajes ---------- */
  function formatTime(ts) {
    const d = new Date(ts);
    return d.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' });
  }

  function escapeHTML(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // Markdown muy básico: **bold**, líneas en blanco como párrafos, links http(s)
  function lightMarkdown(text) {
    const safe = escapeHTML(text);
    return safe
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>')
      .replace(/\n/g, '<br>');
  }

  function clearWelcome() {
    const welcome = body.querySelector('.chat-welcome');
    if (welcome) welcome.remove();
  }

  function appendMessage(role, content, ts) {
    clearWelcome();
    const wrap = document.createElement('div');
    wrap.className = 'msg --' + (role === 'user' ? 'user' : 'bot');

    if (role === 'bot') {
      const avatar = document.createElement('div');
      avatar.className = 'msg-avatar';
      avatar.innerHTML = '<img src="assets/logo-mark.svg" alt="">';
      wrap.appendChild(avatar);
    }

    const col = document.createElement('div');
    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.innerHTML = lightMarkdown(content);
    const time = document.createElement('div');
    time.className = 'msg-time';
    time.textContent = formatTime(ts || Date.now());

    col.appendChild(bubble);
    col.appendChild(time);
    wrap.appendChild(col);
    body.appendChild(wrap);

    body.scrollTo({ top: body.scrollHeight, behavior: 'smooth' });
  }

  function appendTyping() {
    clearWelcome();
    const wrap = document.createElement('div');
    wrap.className = 'msg --bot';
    wrap.id = 'chat-typing';

    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar';
    avatar.innerHTML = '<img src="assets/logo-mark.svg" alt="">';

    const col = document.createElement('div');
    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble msg-typing';
    bubble.innerHTML = '<span></span><span></span><span></span>';
    col.appendChild(bubble);

    wrap.appendChild(avatar);
    wrap.appendChild(col);
    body.appendChild(wrap);
    body.scrollTo({ top: body.scrollHeight, behavior: 'smooth' });
  }

  function removeTyping() {
    const typing = document.getElementById('chat-typing');
    if (typing) typing.remove();
  }

  /* ---------- Restaurar historial ---------- */
  if (history.length) {
    history.forEach((m) => appendMessage(m.role === 'user' ? 'user' : 'bot', m.content, m.ts));
  }

  /* ---------- Envío de mensaje ---------- */
  function autoGrow() {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
  }

  input.addEventListener('input', autoGrow);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      form.requestSubmit();
    }
  });

  function setSending(sending) {
    sendBtn.disabled = sending;
    input.disabled = sending;
  }

  async function sendToBackend(message) {
    const endpoint = getEndpoint();

    if (!endpoint) {
      // Modo DEMO local
      await new Promise((r) => setTimeout(r, 900 + Math.random() * 700));
      return demoReply(message);
    }

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: getSessionId(),
          message: message,
          history: history.slice(-12)
        })
      });
      if (!res.ok) throw new Error('Status ' + res.status);
      const data = await res.json();
      return data.reply || data.output || data.message || data.text || 'Recibí tu mensaje, pero no pude generar respuesta.';
    } catch (err) {
      console.warn('[agent-chat] error:', err);
      return 'Ahora mismo el agente no está disponible. Probá de nuevo en un minuto o escribime por LinkedIn.';
    }
  }

  function demoReply(msg) {
    const m = msg.toLowerCase();
    if (/precio|costo|cu[aá]nto|tarifa/.test(m)) {
      return 'Cada proyecto se cotiza según alcance y complejidad. Lo más concreto es agendar un **diagnóstico** de 30 min — sin costo — para entender tu caso. ¿Te paso el link?';
    }
    if (/tiempo|cu[aá]ndo|plazo|demora/.test(m)) {
      return 'Un primer flujo en producción suele estar listo en **2 a 4 semanas**. Implementaciones más amplias se entregan por fases para que veas valor desde el principio.';
    }
    if (/zapier|make|por qu[eé] n8n/.test(m)) {
      return 'n8n es **self-hosted, open-core y AI-first**. Te da control técnico real, mejor manejo de errores, observabilidad y costos contenidos. Zapier/Make son perfectos para casos chicos; n8n brilla cuando hay arquitectura.';
    }
    if (/diagn[oó]stico|agendar|reuni[oó]n|cita/.test(m)) {
      return 'Genial. Pongo el botón **Agenda diagnóstico** arriba — o escribime por LinkedIn y coordinamos directo.';
    }
    if (/hola|buenas|qu[eé] tal/.test(m)) {
      return '¡Hola! Soy el asistente de Franco. Puedo contarte sobre **servicios, tiempos, precios o agendar un diagnóstico**. ¿En qué te ayudo?';
    }
    return 'Buena pregunta. Para darte una respuesta concreta, lo ideal es un **diagnóstico corto** donde veamos tu caso real. ¿Querés que coordinemos uno?';
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;

    appendMessage('user', text, Date.now());
    history.push({ role: 'user', content: text, ts: Date.now() });
    persistHistory();

    input.value = '';
    autoGrow();
    setSending(true);
    appendTyping();

    const reply = await sendToBackend(text);

    removeTyping();
    appendMessage('bot', reply, Date.now());
    history.push({ role: 'assistant', content: reply, ts: Date.now() });
    persistHistory();
    setSending(false);
    input.focus();
  });

  /* ---------- Sugerencias ---------- */
  suggestions.forEach((btn) => {
    btn.addEventListener('click', () => {
      const text = btn.getAttribute('data-suggestion');
      if (!text) return;
      input.value = text;
      form.requestSubmit();
    });
  });
})();
