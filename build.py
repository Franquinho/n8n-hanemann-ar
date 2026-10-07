#!/usr/bin/env python3
"""Genera n8n.hanemann.ar y cv.hanemann.ar como sitios estáticos en dist/.

Uso:  python3 build.py
Solo usa la biblioteca estándar. Fuentes de verdad:
  content/precios.json   precios (una sola vez para todo: portadas, JSON-LD, prompt del bot)
  content/sitio.json     contacto y URLs
  content/<locale>.json  textos de cada portada
  content/cv.json        textos del CV
  static/                CSS, JS, tipografías e imágenes
Salida:
  dist/n8n.hanemann.ar/  subir tal cual a la carpeta del dominio
  dist/cv.hanemann.ar/   subir tal cual a la carpeta del subdominio
  dist/bot/              prompt del bot con los precios actualizados
"""
import hashlib
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
C = ROOT / "content"
ST = ROOT / "static"
DIST = ROOT / "dist"
OUT = DIST / "n8n.hanemann.ar"
OUTCV = DIST / "cv.hanemann.ar"

LOCALES = ["es-AR", "es", "pt-BR"]
MESES = {
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
    "pt": ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"],
}


def load(name):
    return json.loads((C / name).read_text(encoding="utf-8"))


S = load("sitio.json")
P = load("precios.json")


# ---------------------------------------------------------------- utilidades
def esc(s):
    return html.escape(s, quote=True)


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def miles(n):
    return f"{n:,}".replace(",", ".")


def money(n, moneda):
    return f"USD {miles(n)}" if moneda == "usd" else f"R$ {miles(n)}"


def fecha_larga(iso, lang):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} de {MESES['pt' if lang.startswith('pt') else 'es'][m - 1]} de {y}"


def file_hash(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:10]


def vars_for(L):
    """Valores para los {marcadores} del contenido."""
    m = L["moneda"]
    v = {}
    for k, it in P["items"].items():
        s = money(it[m], m)
        if it.get("mensual"):
            s += L["fmt"]["mes"]
        v[k] = s
        if f"{m}_lista" in it:
            v[k + "_lista"] = money(it[f"{m}_lista"], m)
    v["validez"] = P["validez_propuesta_dias"]
    v["lanzamiento"] = fecha_larga(P["lanzamiento_hasta"], L["html_lang"])
    v.update({k: S[k] for k in ("whatsapp_display", "email", "cv", "linkedin")})
    return v


def fill(s, v):
    return s.format_map(v)


def price_html(key, L, show_from=None, show_was=True):
    it = P["items"][key]
    m = L["moneda"]
    f = L["fmt"]
    if it[m] == 0:
        return f'<p class="price"><b class="amount">{f["gratis"]}</b></p>'
    parts = []
    if show_from if show_from is not None else it.get("desde"):
        parts.append(f'<span class="from">{f["desde"]}</span>')
    per = f'<span class="per">{f["mes"]}</span>' if it.get("mensual") else ""
    parts.append(f'<b class="amount">{money(it[m], m)}</b>{per}')
    if show_was and it.get(f"{m}_lista"):
        parts.append(f'<span class="was">{f["antes"]} {money(it[m + "_lista"], m)}{f["mes"] if it.get("mensual") else ""}</span>')
    return '<p class="price">' + " ".join(parts) + "</p>"


# ---------------------------------------------------------------- iconos
ICO = {
    "cal": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4.5" width="18" height="16" rx="2.5"/><path d="M3 9h18M8 2.5v4M16 2.5v4"/><path d="M8.5 14.5l2.2 2.2 4-4.4"/></svg>',
    "wa": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2.4c-5.3 0-9.6 4.3-9.6 9.6 0 1.7.45 3.34 1.3 4.8L2.4 21.6l4.94-1.3a9.55 9.55 0 0 0 4.7 1.2h.01c5.3 0 9.6-4.3 9.6-9.6 0-2.57-1-4.98-2.81-6.8a9.54 9.54 0 0 0-6.8-2.7Zm0 1.6c2.13 0 4.13.83 5.64 2.34a7.95 7.95 0 0 1 2.33 5.66c0 4.41-3.59 8-8 8a7.94 7.94 0 0 1-4.04-1.1l-.29-.17-2.93.77.78-2.86-.19-.3a7.93 7.93 0 0 1-1.22-4.24c0-4.41 3.59-8 8-8Zm-2.6 3.96c-.16 0-.42.06-.64.3-.22.24-.84.82-.84 2s.86 2.32.98 2.48c.12.16 1.7 2.6 4.13 3.64.58.25 1.02.4 1.37.51.58.18 1.1.16 1.52.1.46-.07 1.43-.58 1.63-1.15.2-.56.2-1.04.14-1.14-.06-.1-.22-.16-.46-.28-.24-.12-1.43-.7-1.65-.78-.22-.08-.38-.12-.54.12-.16.24-.62.78-.76.94-.14.16-.28.18-.52.06-.24-.12-1.02-.38-1.94-1.2-.72-.64-1.2-1.43-1.34-1.67-.14-.24-.02-.37.1-.49.11-.11.24-.28.36-.42.12-.14.16-.24.24-.4.08-.16.04-.3-.02-.42-.06-.12-.54-1.3-.74-1.78-.2-.47-.39-.4-.54-.41h-.46Z"/></svg>',
    "bot": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.5 8.5 0 0 1-12.4 7.55L3 20.5l1.45-5.05A8.5 8.5 0 1 1 21 11.5Z"/><path d="M8.5 11.5h.01M12 11.5h.01M15.5 11.5h.01"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-5.5-7-11a7 7 0 0 1 14 0c0 5.5-7 11-7 11Z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    "x": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>',
    "send": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12 19 5l-5 14-3-6-6-1Z"/></svg>',
}

FAVICON_180 = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 180 180'%3E%3Crect width='180' height='180' rx='40' fill='%23ec1f33'/%3E%3Ctext x='90' y='126' font-family='Arial,sans-serif' font-weight='700' font-size='112' fill='white' text-anchor='middle'%3EH%3C/text%3E%3C/svg%3E"
FAVICON_32 = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%23ec1f33'/%3E%3Ctext x='16' y='23' font-family='Arial,sans-serif' font-weight='700' font-size='20' fill='white' text-anchor='middle'%3EH%3C/text%3E%3C/svg%3E"


# ---------------------------------------------------------------- piezas
def head(*, lang, title, description, canonical, prefix, alternates=(), og=None, jsonld=None, robots="index, follow, max-image-preview:large", css_v="", noindex=False):
    canon = f'\n  <link rel="canonical" href="{canonical}" />' if canonical else ""
    alt = "\n".join(f'  <link rel="alternate" hreflang="{h}" href="{u}" />' for h, u in alternates)
    ogtags = ""
    if og:
        site_name = esc(og.get("site_name", "Franco Hanemann · Automatización con n8n e IA"))
        og_alts = "".join('\n  <meta property="og:locale:alternate" content="%s" />' % x for x in og.get("alternates", []))
        ogtags = f"""
  <meta property="og:type" content="website" />
  <meta property="og:locale" content="{og['locale']}" />
  <meta property="og:site_name" content="{site_name}" />{og_alts}
  <meta property="og:title" content="{esc(og['title'])}" />
  <meta property="og:description" content="{esc(og['description'])}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:image" content="{og['image']}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="{esc(og['title'])}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(og['title'])}" />
  <meta name="twitter:description" content="{esc(og['description'])}" />
  <meta name="twitter:image" content="{og['image']}" />"""
    ld = ""
    if jsonld:
        ld = '\n  <script type="application/ld+json">\n' + json.dumps(jsonld, ensure_ascii=False, indent=2) + "\n  </script>"
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}" />
  <meta name="author" content="Franco E. Hanemann" />
  <meta name="robots" content="{'noindex, follow' if noindex else robots}" />
  <meta name="theme-color" content="#08080a" />{canon}
{alt}{ogtags}
  <link rel="icon" type="image/svg+xml" href="{FAVICON_32}" />
  <link rel="apple-touch-icon" href="{FAVICON_180}" />
  <link rel="preload" href="{prefix}fonts/space-grotesk-latin-700.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="{prefix}fonts/inter-latin-var.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="stylesheet" href="{prefix}css/site.css?v={css_v}" />{ld}
</head>"""


def topbar(L, prefix, home_prefix, in_home=True):
    n = L["nav"]
    a = "" if in_home else home_prefix
    alt = L["alt_lang"]
    alt_href = prefix + ("pt/" if alt["target"] == "pt" else "es/")
    secs = "".join(
        f'\n        <a class="nav-sec" href="{a}#{k}">{n[k]}</a>' for k in ("casos", "precios", "metodo", "sobre", "preguntas")
    )
    return f"""
  <a class="skip-link" href="#contenido">{n['skip']}</a>
  <header class="top" id="top">
    <div class="wrap nav">
      <a class="brand" href="{home_prefix or './'}" aria-label="Franco E. Hanemann">
        <span class="brand-mark" aria-hidden="true">H</span>
        <span class="brand-word">Franco E. Hanemann.</span>
      </a>
      <nav class="nav-links" aria-label="{n['menu_label']}">{secs}
        <a class="lang-link" href="{alt_href}" hreflang="{'pt-BR' if alt['target'] == 'pt' else 'es'}" lang="{'pt-BR' if alt['target'] == 'pt' else 'es'}" title="{alt['label']}">{alt['short']}</a>
        <a class="nav-cta" href="{S['cal_url']}" target="_blank" rel="noopener"><span class="long">{n['cta']}</span><span class="short" aria-hidden="true">{n['cta_short']}</span></a>
      </nav>
    </div>
  </header>"""


def footer(L, prefix, current):
    f = L["footer"]
    links = [
        ("", "Español (Argentina)", "es-AR"),
        ("es/", "Español", "es"),
        ("pt/", "Português", "pt-BR"),
    ]
    cur = ' aria-current="page"'
    langs = "".join(
        '<li><a href="{}" hreflang="{}" lang="{}"{}>{}</a></li>'.format(prefix + p if p else (prefix or "./"), h, h, cur if current == h else "", label)
        for p, label, h in links
    )
    priv = prefix + L["privacy_path"]
    priv_cur = cur if current == "privacy" else ""
    return f"""
  <footer class="foot">
    <div class="wrap foot-inner">
      <span class="foot-brand"><span class="brand-mark sm" aria-hidden="true">H</span> Franco E. Hanemann</span>
      <p class="foot-meta">{f['line1']}</p>
      <ul class="foot-links" aria-label="{f['langs_label']}">{langs}<li><a href="{priv}"{priv_cur}>{f['privacy']}</a></li></ul>
      <p class="foot-meta">© <span id="year">2026</span> · Franco E. Hanemann · <span class="foot-updated">{f['updated']}</span></p>
    </div>
  </footer>"""


def chat_block(L, prefix, v):
    c = L["chat"]
    chips = "".join(f'\n        <button type="button" data-q="{esc(q)}">{q}</button>' for q in c["chips"])
    note = c["note"].format(privacy=prefix + L["privacy_path"])
    return f"""
  <button class="bot-fab" id="bot-fab" type="button" aria-haspopup="dialog" aria-controls="chat" aria-label="{esc(c['fab_aria'])}">
    <span class="bot-fab-dot" aria-hidden="true"></span>
    {c['fab']}
  </button>
  <div class="chat-scrim" id="chat-scrim" hidden></div>
  <aside class="chat" id="chat" role="dialog" aria-modal="true" aria-labelledby="chat-title" hidden>
    <header class="chat-head">
      <span class="chat-avatar" aria-hidden="true">H</span>
      <div class="chat-id">
        <p id="chat-title">{c['title']}</p>
        <small><span class="chat-live"></span> {c['status']}</small>
      </div>
      <button class="chat-x" id="chat-x" type="button" aria-label="{c['close']}">{ICO['x']}</button>
    </header>
    <div class="chat-body" id="chat-body" aria-live="polite">
      <div class="msg msg--bot"><p>{c['greeting']}</p></div>
      <div class="chat-chips" id="chat-chips">{chips}
        <button type="button" class="chip-action" data-q="{esc(c['chip_action'])}">{c['chip_action']}</button>
      </div>
    </div>
    <form class="chat-input" id="chat-form" autocomplete="off">
      <input id="chat-text" type="text" placeholder="{esc(c['placeholder'])}" aria-label="{esc(c['input_label'])}" maxlength="800" />
      <button type="submit" aria-label="{c['send']}">{ICO['send']}</button>
    </form>
    <small class="chat-note">{note}</small>
  </aside>"""


def scripts(L, prefix, js_v):
    cfg = {
        "webhook": S["bot_webhook"],
        "token": S["bot_token"],
        "lang": L["chat"]["lang"],
        "error": L["chat"]["error"],
    }
    return f"""
  <script id="site-config" type="application/json">{json.dumps(cfg, ensure_ascii=False)}</script>
  <script src="{prefix}js/site.js?v={js_v}" defer></script>"""


def wa_url(text):
    from urllib.parse import quote
    return f"https://wa.me/{S['whatsapp_num']}?text={quote(text)}"


def workflow_svg(L):
    s = L["metodo"]["svg"]
    t = {k: esc(val) for k, val in s.items()}
    return f"""<svg viewBox="0 0 1100 500" preserveAspectRatio="xMidYMid meet" class="workflow-svg" aria-hidden="true">
            <defs>
              <linearGradient id="wfLine" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#8e0d18" stop-opacity="0.5"/><stop offset="55%" stop-color="#ec1f33" stop-opacity="0.9"/><stop offset="100%" stop-color="#ff5063" stop-opacity="1"/></linearGradient>
              <linearGradient id="wfNode" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="rgba(255,255,255,0.06)"/><stop offset="100%" stop-color="rgba(255,255,255,0.015)"/></linearGradient>
            </defs>
            <path id="wfp1" class="wf-line wf-line-1" d="M 205 176 C 252 176, 253 176, 300 176" stroke="url(#wfLine)" stroke-width="2.4" fill="none" stroke-linecap="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="0"/>
            <path id="wfp2" class="wf-line wf-line-2" d="M 485 176 C 532 176, 533 176, 580 176" stroke="url(#wfLine)" stroke-width="2.4" fill="none" stroke-linecap="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="0"/>
            <path id="wfp3" class="wf-line wf-line-3" d="M 765 176 C 818 176, 820 96, 860 96" stroke="url(#wfLine)" stroke-width="2.4" fill="none" stroke-linecap="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="0"/>
            <path id="wfp4" class="wf-line wf-line-4" d="M 765 176 C 818 176, 820 326, 860 326" stroke="url(#wfLine)" stroke-width="2.4" fill="none" stroke-linecap="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="0"/>
            <path id="wfp5" class="wf-line wf-line-5 wf-line-sub" d="M 672 360 C 672 312, 672 300, 672 248" stroke="url(#wfLine)" stroke-width="2" fill="none" stroke-linecap="round" stroke-dasharray="5 5" pathLength="100" stroke-dashoffset="0"/>
            <circle class="wf-packet" r="3.4" fill="#ff5063"><animateMotion dur="2.4s" begin="0.4s" repeatCount="indefinite"><mpath href="#wfp1"/></animateMotion></circle>
            <circle class="wf-packet" r="3.4" fill="#ff5063"><animateMotion dur="2.4s" begin="1.0s" repeatCount="indefinite"><mpath href="#wfp2"/></animateMotion></circle>
            <circle class="wf-packet" r="3.4" fill="#ff5063"><animateMotion dur="2.6s" begin="1.7s" repeatCount="indefinite"><mpath href="#wfp3"/></animateMotion></circle>
            <circle class="wf-packet" r="3.4" fill="#ff5063"><animateMotion dur="2.6s" begin="2.0s" repeatCount="indefinite"><mpath href="#wfp4"/></animateMotion></circle>
            <circle class="wf-packet wf-packet-sub" r="2.8" fill="#ff8a98"><animateMotion dur="2.2s" begin="2.6s" repeatCount="indefinite" keyPoints="1;0" keyTimes="0;1" calcMode="linear"><mpath href="#wfp5"/></animateMotion></circle>
            <g class="wf-node wf-node-1" transform="translate(40, 140)">
              <rect width="165" height="72" rx="13" fill="url(#wfNode)" stroke="rgba(236,31,51,0.40)" stroke-width="1.5"/>
              <rect x="14" y="20" width="32" height="32" rx="8" fill="#ec1f33"/><polygon points="26,29 39,36 26,43" fill="#fff"/>
              <text x="58" y="30" fill="#ff5063" font-family="Space Grotesk, sans-serif" font-weight="500" font-size="10" letter-spacing="1.8">{t['n1_tag']}</text>
              <text x="58" y="48" fill="#f5f5f7" font-family="Inter, sans-serif" font-weight="600" font-size="14">{t['n1_title']}</text>
              <text x="58" y="64" fill="#8a8a93" font-family="Inter, sans-serif" font-size="11">{t['n1_sub']}</text>
              <circle class="wf-port" cx="165" cy="36" r="4" fill="#ec1f33" stroke="#0c0c0f" stroke-width="1.5"/>
            </g>
            <g class="wf-node wf-node-2" transform="translate(300, 140)">
              <rect width="185" height="72" rx="13" fill="url(#wfNode)" stroke="rgba(236,31,51,0.45)" stroke-width="1.5"/>
              <rect x="14" y="20" width="32" height="32" rx="8" fill="#ec1f33"/><polyline points="23,36 28,41 39,29" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <text x="58" y="30" fill="#ff5063" font-family="Space Grotesk, sans-serif" font-weight="500" font-size="10" letter-spacing="1.8">{t['n2_tag']}</text>
              <text x="58" y="48" fill="#f5f5f7" font-family="Inter, sans-serif" font-weight="600" font-size="14">{t['n2_title']}</text>
              <text x="58" y="64" fill="#8a8a93" font-family="Inter, sans-serif" font-size="11">{t['n2_sub']}</text>
              <circle class="wf-port" cx="0" cy="36" r="4" fill="#ec1f33" stroke="#0c0c0f" stroke-width="1.5"/><circle class="wf-port" cx="185" cy="36" r="4" fill="#ec1f33" stroke="#0c0c0f" stroke-width="1.5"/>
            </g>
            <g class="wf-node wf-node-3" transform="translate(580, 140)">
              <rect width="185" height="72" rx="13" fill="url(#wfNode)" stroke="rgba(236,31,51,0.62)" stroke-width="1.5"/>
              <rect x="14" y="20" width="32" height="32" rx="8" fill="#ff5063"/><path d="M30,26 L32.2,33.8 L40,36 L32.2,38.2 L30,46 L27.8,38.2 L20,36 L27.8,33.8 Z" fill="#fff"/>
              <text x="58" y="30" fill="#ff5063" font-family="Space Grotesk, sans-serif" font-weight="500" font-size="10" letter-spacing="1.8">{t['n3_tag']}</text>
              <text x="58" y="48" fill="#f5f5f7" font-family="Inter, sans-serif" font-weight="600" font-size="14">{t['n3_title']}</text>
              <text x="58" y="64" fill="#8a8a93" font-family="Inter, sans-serif" font-size="11">{t['n3_sub']}</text>
              <circle class="wf-port" cx="0" cy="36" r="4" fill="#ff5063" stroke="#0c0c0f" stroke-width="1.5"/><circle class="wf-port" cx="185" cy="36" r="4" fill="#ff5063" stroke="#0c0c0f" stroke-width="1.5"/><circle class="wf-port" cx="92.5" cy="72" r="4" fill="#ff5063" stroke="#0c0c0f" stroke-width="1.5"/>
            </g>
            <g class="wf-node wf-node-4" transform="translate(860, 60)">
              <rect width="185" height="72" rx="13" fill="url(#wfNode)" stroke="rgba(255,255,255,0.16)" stroke-width="1.5"/>
              <rect x="14" y="20" width="32" height="32" rx="8" fill="#5a5a63"/><g fill="none" stroke="#fff" stroke-width="1.7"><ellipse cx="30" cy="30" rx="7" ry="2.6"/><path d="M23,30 v12 c0,1.5 3.1,2.6 7,2.6 s7,-1.1 7,-2.6 v-12"/><path d="M23,36 c0,1.5 3.1,2.6 7,2.6 s7,-1.1 7,-2.6"/></g>
              <text x="58" y="30" fill="#8a8a93" font-family="Space Grotesk, sans-serif" font-weight="500" font-size="10" letter-spacing="1.8">{t['n4_tag']}</text>
              <text x="58" y="48" fill="#f5f5f7" font-family="Inter, sans-serif" font-weight="600" font-size="14">{t['n4_title']}</text>
              <text x="58" y="64" fill="#8a8a93" font-family="Inter, sans-serif" font-size="11">{t['n4_sub']}</text>
              <circle class="wf-port" cx="0" cy="36" r="4" fill="#5a5a63" stroke="#0c0c0f" stroke-width="1.5"/>
            </g>
            <g class="wf-node wf-node-5" transform="translate(860, 290)">
              <rect width="185" height="72" rx="13" fill="url(#wfNode)" stroke="rgba(236,31,51,0.40)" stroke-width="1.5"/>
              <rect x="14" y="20" width="32" height="32" rx="8" fill="#ec1f33"/><path d="M24,32 h12 a2,2 0 0 1 2,2 v5 a2,2 0 0 1 -2,2 h-6 l-4,3 v-3 a2,2 0 0 1 -2,-2 v-5 a2,2 0 0 1 2,-2 Z" fill="none" stroke="#fff" stroke-width="1.7" stroke-linejoin="round"/>
              <text x="58" y="34" fill="#ff5063" font-family="Space Grotesk, sans-serif" font-weight="500" font-size="10" letter-spacing="1.8">{t['n5_tag']}</text>
              <text x="58" y="52" fill="#f5f5f7" font-family="Inter, sans-serif" font-weight="600" font-size="14">{t['n5_title']}</text>
              <circle class="wf-port" cx="0" cy="36" r="4" fill="#ec1f33" stroke="#0c0c0f" stroke-width="1.5"/>
            </g>
            <g class="wf-node wf-node-6" transform="translate(580, 360)">
              <rect width="185" height="72" rx="13" fill="url(#wfNode)" stroke="rgba(236,31,51,0.38)" stroke-width="1.5"/>
              <rect x="14" y="20" width="32" height="32" rx="8" fill="#ec1f33"/><polyline points="23,43 28,36 32,39 39,29" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M23,43 h16" stroke="#fff" stroke-width="1.3" opacity="0.5"/>
              <text x="58" y="30" fill="#ff5063" font-family="Space Grotesk, sans-serif" font-weight="500" font-size="10" letter-spacing="1.8">{t['n6_tag']}</text>
              <text x="58" y="48" fill="#f5f5f7" font-family="Inter, sans-serif" font-weight="600" font-size="14">{t['n6_title']}</text>
              <text x="58" y="64" fill="#8a8a93" font-family="Inter, sans-serif" font-size="11">{t['n6_sub']}</text>
              <circle class="wf-port" cx="92.5" cy="0" r="4" fill="#ec1f33" stroke="#0c0c0f" stroke-width="1.5"/>
            </g>
          </svg>"""


# ---------------------------------------------------------------- portada
def home_jsonld(L, v, url):
    m = L["moneda"]
    cur = "USD" if m == "usd" else "BRL"
    lang = L["html_lang"]
    person = {
        "@type": "Person",
        "@id": f"{S['dominio']}/#franco",
        "name": S["nombre"],
        "givenName": "Franco",
        "familyName": "Hanemann",
        "jobTitle": "Consultor de automatización con n8n e IA" if not lang.startswith("pt") else "Consultor de automação com n8n e IA",
        "url": f"{S['dominio']}/",
        "email": S["email"],
        "telephone": S["telefono_e164"],
        "image": f"{S['dominio']}/img/franco-hanemann.jpg",
        "alumniOf": {"@type": "CollegeOrUniversity", "name": "Universidad Tecnológica Nacional (UTN)"},
        "address": {"@type": "PostalAddress", "addressLocality": S["ciudad"], "addressRegion": S["provincia"], "addressCountry": S["pais"]},
        "knowsAbout": ["n8n", "Agentes de IA", "API oficial de WhatsApp", "Automatización de procesos", "Integración de sistemas", "ERP", "CRM", "Google Ads conversiones offline"] if not lang.startswith("pt") else ["n8n", "Agentes de IA", "API oficial do WhatsApp", "Automação de processos", "Integração de sistemas", "ERP", "CRM", "Conversões offline no Google Ads"],
        "knowsLanguage": ["es", "pt"],
        "hasCredential": [
            {"@type": "EducationalOccupationalCredential", "credentialCategory": "certificate", "name": "n8n Basic Course (2025)"},
            {"@type": "EducationalOccupationalCredential", "credentialCategory": "certificate", "name": "n8n Advanced Course (2025)"},
            {"@type": "EducationalOccupationalCredential", "credentialCategory": "degree", "name": "Técnico Universitario de Programación (UTN, 2019)"},
        ],
        "sameAs": [S["cv"], S["linkedin"]],
    }
    offers = []
    names = {s["price"]: s["name"] for s in L["precios"]["steps"]}
    names.update({e["price"]: e["name"] for e in L["precios"]["extras"]})
    for st in L["precios"]["steps"]:
        for pl in st.get("planes", []):
            names[pl["price"]] = f"{st['name']} · {pl['name']}"
    for key, name in names.items():
        it = P["items"][key]
        o = {"@type": "Offer", "name": name, "priceCurrency": cur, "priceValidUntil": P["lanzamiento_hasta"]}
        if it.get("desde"):
            o["priceSpecification"] = {"@type": "PriceSpecification", "minPrice": it[m], "priceCurrency": cur}
        else:
            o["price"] = it[m]
        offers.append(o)
    service = {
        "@type": "ProfessionalService",
        "@id": f"{S['dominio']}/#service",
        "name": "Franco Hanemann · Automatización con n8n e IA",
        "url": f"{S['dominio']}/",
        "provider": {"@id": f"{S['dominio']}/#franco"},
        "email": S["email"],
        "telephone": S["telefono_e164"],
        "address": person["address"],
        "areaServed": [{"@type": "Country", "name": "Argentina"}, {"@type": "Country", "name": "Brasil"}, {"@type": "Place", "name": "Latinoamérica"}],
        "availableLanguage": ["es", "pt"],
        "serviceType": ["Agentes de WhatsApp con IA", "Automatización con n8n", "Integración con ERP y CRM", "Atribución de ventas a Google Ads y Meta"] if not lang.startswith("pt") else ["Agentes de WhatsApp com IA", "Automação com n8n", "Integração com ERP e CRM", "Atribuição de vendas ao Google Ads e à Meta"],
        "makesOffer": offers,
    }
    faq = {
        "@type": "FAQPage",
        "@id": f"{url}#faq",
        "mainEntity": [
            {"@type": "Question", "name": strip_tags(fill(i["q"], v)), "acceptedAnswer": {"@type": "Answer", "text": strip_tags(fill(i["lead"], v) + " " + fill(i["body"], v))}}
            for i in L["faq"]["items"]
        ],
    }
    page = {
        "@type": "WebPage",
        "@id": f"{url}#webpage",
        "url": url,
        "name": fill(L["meta"]["title"], v),
        "inLanguage": lang,
        "about": {"@id": f"{S['dominio']}/#franco"},
        "datePublished": S["publicado_desde"],
        "dateModified": S["actualizado"],
        "primaryImageOfPage": f"{S['dominio']}/img/{L['meta']['og_image']}",
    }
    website = {"@type": "WebSite", "@id": f"{S['dominio']}/#website", "url": f"{S['dominio']}/", "name": "Franco Hanemann · Automatización con n8n e IA", "inLanguage": ["es-AR", "es", "pt-BR"], "publisher": {"@id": f"{S['dominio']}/#franco"}}
    return {"@context": "https://schema.org", "@graph": [person, service, website, page, faq]}


def render_home(code, css_v, js_v):
    L = load(f"{code}.json")
    v = vars_for(L)
    depth = L["path"].count("/")
    prefix = "../" * depth
    url = f"{S['dominio']}/{L['path']}"
    H = L["hero"]
    alternates = [("es-AR", f"{S['dominio']}/"), ("es", f"{S['dominio']}/es/"), ("pt-BR", f"{S['dominio']}/pt/"), ("x-default", f"{S['dominio']}/es/")]
    out = [head(
        lang=L["html_lang"], title=fill(L["meta"]["title"], v), description=fill(L["meta"]["description"], v),
        canonical=url, prefix=prefix, alternates=alternates, css_v=css_v,
        og={"locale": L["og_locale"], "title": L["meta"]["og_title"], "description": L["meta"]["og_description"], "image": f"{S['dominio']}/img/{L['meta']['og_image']}",
            "site_name": L["meta"]["site_name"], "alternates": [x for x in ("es_AR", "es_LA", "pt_BR") if x != L["og_locale"]]},
        jsonld=home_jsonld(L, v, url),
    )]
    out.append('<body>\n  <div class="atmos" aria-hidden="true"></div>\n  <div class="grid-veil" aria-hidden="true"></div>')
    out.append(topbar(L, prefix, "", in_home=True))
    wa = wa_url(H["wa_text"])

    # HERO
    h1 = "".join(
        '<span class="ln">' + ('<span class="accent">' + line + "</span>" if i in H["h1_accent"] else line) + "</span>"
        for i, line in enumerate(H["h1"])
    )
    proof = "".join(f'<li><span class="proof-name">{p["name"]}</span><span class="proof-tag">{p["tag"]}</span></li>' for p in H["proof"])
    facts = "".join(f'<li><span class="cert-check" aria-hidden="true">{ICO["check"]}</span><span>{f}</span></li>' for f in H["facts"])
    out.append(f"""
  <main id="contenido">
    <section class="hero" id="inicio" aria-labelledby="hero-title">
      <div class="wrap hero-grid">
        <div class="hero-head"><p class="eyebrow"><span class="pulse" aria-hidden="true"></span>{H['eyebrow']}</p></div>
        <div class="hero-title-wrap">
          <h1 class="hero-title" id="hero-title">{h1}</h1>
          <div class="hero-turbine" aria-hidden="true"><canvas id="hero-turbina" width="320" height="320"></canvas></div>
        </div>
        <div class="hero-foot">
          <div class="hero-lead-col">
            <p class="hero-lead">{H['lead']}</p>
            <div class="cta-row">
              <a class="cta cta--solid" href="{S['cal_url']}" target="_blank" rel="noopener">
                <span class="cta-ico" aria-hidden="true">{ICO['cal']}</span>
                <span class="cta-txt"><b>{H['cta_cal']['b']}</b><small>{H['cta_cal']['small']}</small></span>
              </a>
              <a class="cta" href="{wa}" target="_blank" rel="noopener">
                <span class="cta-ico" aria-hidden="true">{ICO['wa']}</span>
                <span class="cta-txt"><b>{H['cta_wa']['b']}</b><small>{fill(H['cta_wa']['small'], v)}</small></span>
              </a>
              <button class="cta" type="button" data-cta="bot" aria-haspopup="dialog" aria-controls="chat">
                <span class="cta-ico" aria-hidden="true">{ICO['bot']}</span>
                <span class="cta-txt"><b>{H['cta_bot']['b']}</b><small>{H['cta_bot']['small']}</small></span>
              </button>
            </div>
            <p class="cta-note">{H['cta_note']}</p>
          </div>
          <aside class="hero-proof" aria-label="{H['proof_label']}">
            <p class="proof-label">{H['proof_label']}</p>
            <ul class="proof-list">{proof}</ul>
            <ul class="proof-facts">{facts}</ul>
          </aside>
        </div>
      </div>
    </section>""")

    # CASOS
    K = L["casos"]
    cases = ""
    for c in K["items"]:
        demo = f'<button class="case-demo" type="button" data-cta="bot" aria-haspopup="dialog" aria-controls="chat">{c["demo"]}</button>' if c.get("demo") else ""
        cases += f'\n          <li class="case case--{c["state"]}"><p class="case-status">{c["status"]}</p><h3>{c["title"]}</h3><p>{c["text"]}</p>{demo}</li>'
    out.append(f"""
    <section class="section" id="casos" aria-labelledby="casos-title">
      <div class="wrap">
        <header class="sec-head reveal">
          <span class="kicker">{K['kicker']}</span>
          <h2 id="casos-title">{K['h2']}</h2>
          <p class="sec-sub">{K['sub']}</p>
        </header>
        <ul class="case-grid reveal-stagger">{cases}
        </ul>
      </div>
    </section>""")

    # PRECIOS
    R = L["precios"]
    steps = ""
    for i, st in enumerate(R["steps"], 1):
        main = " step--main" if st.get("incluye") else ""
        if st.get("planes"):
            price = price_html(st["price"], L, show_from=True, show_was=False)
            planes = "".join(
                f'<li><div class="plan-head"><b>{pl["name"]}</b>{price_html(pl["price"], L)}</div><p>{pl["text"]}</p></li>'
                for pl in st["planes"]
            )
            extra = f'<ul class="planes">{planes}</ul>'
        else:
            price = price_html(st["price"], L)
            extra = f'<p>{fill(st["text"], v)}</p>' if st.get("text") else ""
        if st.get("incluye"):
            lis = "".join(f"<li>{x}</li>" for x in st["incluye"])
            extra += f'<div class="inc"><p class="inc-label">{st["inc_label"]}</p><ul>{lis}</ul><p class="exc"><b>{st["exc_label"]}:</b> {st["no_incluye"]}</p></div>'
        steps += f"""
          <li class="step{main}">
            <div class="step-top"><span class="step-n">{i}</span><span class="step-meta">{st['meta']}</span></div>
            <h3>{st['name']}</h3>
            {price}
            {extra}
          </li>"""
    extras = "".join(
        f'\n          <li class="extra"><div class="extra-head"><h3>{e["name"]}</h3>{price_html(e["price"], L)}</div><p>{e["text"]}</p></li>'
        for e in R["extras"]
    )
    out.append(f"""
    <section class="section" id="precios" aria-labelledby="precios-title">
      <div class="wrap">
        <header class="sec-head reveal">
          <span class="kicker">{R['kicker']}</span>
          <h2 id="precios-title">{R['h2']}</h2>
          <p class="sec-sub">{fill(R['sub'], v)}</p>
          <p class="launch"><span class="pulse" aria-hidden="true"></span>{fill(R['launch'], v)}</p>
        </header>
        <p class="ladder-label">{R['path_label']}</p>
        <ol class="ladder reveal-stagger">{steps}
        </ol>
        <p class="ladder-label">{R['extras_label']}</p>
        <ul class="extras">{extras}
        </ul>
        <div class="pay-notes">
          <p>{fill(R['hora'], v)}</p>
          <p>{fill(R['pago'], v)}</p>
        </div>
      </div>
    </section>""")

    # MÉTODO
    M = L["metodo"]
    caps = "".join(f'\n            <li class="wf-cap"><span class="wf-cap-tag" aria-hidden="true">{ICO["check"]}</span><p>{x}</p></li>' for x in M["entregables"])
    out.append(f"""
    <section class="section section--showcase" id="metodo" aria-labelledby="metodo-title">
      <div class="wrap">
        <header class="sec-head reveal">
          <span class="kicker">{M['kicker']}</span>
          <h2 id="metodo-title">{M['h2']}</h2>
          <p class="sec-sub">{M['sub']}</p>
        </header>
        <figure class="workflow-canvas reveal" role="img" aria-label="{esc(M['svg_aria'])}" style="margin-inline:0">
          {workflow_svg(L)}
        </figure>
        <ul class="workflow-captions">{caps}
        </ul>
      </div>
    </section>""")

    # SERVICIOS
    SV = L["servicios"]
    cards = "".join(f'\n          <li class="auto-card"><span class="auto-tag">{c["tag"]}</span><h3>{c["title"]}</h3><p>{c["text"]}</p></li>' for c in SV["items"])
    out.append(f"""
    <section class="section" id="servicios" aria-labelledby="servicios-title">
      <div class="wrap">
        <header class="sec-head reveal">
          <span class="kicker">{SV['kicker']}</span>
          <h2 id="servicios-title">{SV['h2']}</h2>
        </header>
        <ul class="auto-grid reveal-stagger">{cards}
        </ul>
      </div>
    </section>""")

    # SOBRE
    B = L["sobre"]
    tray = "".join(f'<li><span class="tray-year">{t["years"]}</span><div class="tray-info"><b>{t["title"]}</b><span>{t["text"]}</span></div></li>' for t in B["tray"])
    certs = "".join(f'<span class="cert-pill cert-pill--n8n">{c}</span>' for c in B["certs_n8n"]) + "".join(f'<span class="cert-pill">{c}</span>' for c in B["certs"])
    out.append(f"""
    <section class="section section--sobre" id="sobre" aria-labelledby="sobre-title">
      <div class="wrap">
        <header class="sec-head reveal">
          <span class="kicker">{B['kicker']}</span>
          <h2 id="sobre-title">{B['h2']}</h2>
        </header>
        <div class="sobre-grid">
          <figure class="sobre-photo">
            <picture>
              <source srcset="{prefix}img/franco-hanemann.webp" type="image/webp" />
              <img src="{prefix}img/franco-hanemann.jpg" alt="{esc(B['photo_alt'])}" width="640" height="640" loading="lazy" decoding="async" />
            </picture>
            <figcaption><span class="sobre-loc">{ICO['pin']}{B['loc']}</span></figcaption>
          </figure>
          <div class="sobre-body">
            <p class="sobre-lead">{B['lead']}</p>
            <p>{B['p']}</p>
            <ol class="trayectoria" aria-label="{B['tray_label']}">{tray}</ol>
            <div class="sobre-certs" aria-label="{B['certs_label']}">{certs}</div>
            <p class="sobre-more">{fill(B['more'], v)}</p>
          </div>
        </div>
      </div>
    </section>""")

    # FAQ
    F = L["faq"]
    qs = ""
    for i, it in enumerate(F["items"]):
        qs += f"""
          <details{' open' if i == 0 else ''}>
            <summary><h3>{fill(it['q'], v)}</h3><span class="faq-sign" aria-hidden="true"></span></summary>
            <div class="faq-body"><p class="faq-lead">{fill(it['lead'], v)}</p><p>{fill(it['body'], v)}</p></div>
          </details>"""
    out.append(f"""
    <section class="section section--faq" id="preguntas" aria-labelledby="faq-title">
      <div class="wrap">
        <header class="sec-head reveal">
          <span class="kicker">{F['kicker']}</span>
          <h2 id="faq-title">{F['h2']}</h2>
        </header>
        <div class="faq">{qs}
        </div>
      </div>
    </section>""")

    # CONTACTO
    T = L["contacto"]
    out.append(f"""
    <section class="section section--contacto" id="contacto" aria-labelledby="contacto-title">
      <div class="wrap closer reveal">
        <span class="kicker">{T['kicker']}</span>
        <h2 id="contacto-title">{T['h2']}</h2>
        <p class="closer-lead">{T['lead']}</p>
        <div class="closer-cta">
          <a class="cta cta--solid" href="{S['cal_url']}" target="_blank" rel="noopener"><span class="cta-ico" aria-hidden="true">{ICO['cal']}</span><span class="cta-txt"><b>{T['cta_cal']}</b></span></a>
          <a class="cta" href="{wa}" target="_blank" rel="noopener"><span class="cta-ico" aria-hidden="true">{ICO['wa']}</span><span class="cta-txt"><b>{T['cta_wa']}</b></span></a>
          <button class="cta" type="button" data-cta="bot" aria-haspopup="dialog" aria-controls="chat"><span class="cta-ico" aria-hidden="true">{ICO['bot']}</span><span class="cta-txt"><b>{T['cta_bot']}</b></span></button>
        </div>
        <p class="closer-meta">{fill(T['meta'], v)}</p>
      </div>
    </section>
  </main>""")
    out.append(footer(L, prefix, L["html_lang"]))
    out.append(chat_block(L, prefix, v))
    out.append(scripts(L, prefix, js_v))
    out.append("\n</body>\n</html>\n")
    dest = OUT / L["path"] / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("".join(out), encoding="utf-8")
    return dest


# ---------------------------------------------------------------- páginas de texto
def render_text_page(*, code, rel_path, title, description, fragment, alternates, css_v, current, noindex=False, back_label=None, prefix=None):
    L = load(f"{code}.json")
    if prefix is None:
        prefix = "../" * rel_path.count("/")
    url = f"{S['dominio']}/{rel_path}" if rel_path else None
    home = prefix + L["path"] if L["path"] else (prefix or "./")
    back = f'\n        <a class="prose-back" href="{home}">{back_label}</a>' if back_label else ""
    page = head(lang=L["html_lang"], title=title, description=description, canonical=url, prefix=prefix, alternates=alternates, css_v=css_v, noindex=noindex)
    page += '\n<body>\n  <div class="atmos" aria-hidden="true"></div>'
    page += topbar(L, prefix, home, in_home=False)
    page += f"""
  <main id="contenido">
    <div class="wrap">
      <article class="prose">
{fragment}{back}
      </article>
    </div>
  </main>"""
    page += footer(L, prefix, current)
    page += f'\n  <script>document.getElementById("year").textContent=new Date().getFullYear();</script>\n</body>\n</html>\n'
    dest = OUT / rel_path / "index.html" if rel_path else OUT / "404.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page, encoding="utf-8")
    return dest


# ---------------------------------------------------------------- CV
def render_cv(lang_key, css_v):
    CVD = load("cv.json")[lang_key]
    depth = CVD["path"].count("/")
    prefix = "../" * depth
    url = f"{S['cv']}/{CVD['path']}"
    exp = ""
    for e in CVD["exp"]:
        bl = "".join(f"<li>{b}</li>" for b in e["bullets"])
        exp += f"""
          <li class="cv-job">
            <div class="cv-job-head"><h3>{e['role']}</h3><span class="cv-dates">{e['dates']}</span></div>
            <p class="cv-org">{e['org']}</p>
            <ul>{bl}</ul>
          </li>"""
    skills = "".join(f"<li>{s}</li>" for s in CVD["skills"])
    certs = "".join(f"<li>{s}</li>" for s in CVD["certs"])
    edu = "".join(f'<li><b>{e["title"]}</b><span>{e["org"]} · {e["year"]}</span></li>' for e in CVD["edu"])
    langs = "".join(f"<li>{s}</li>" for s in CVD["langs"])
    site = f"{S['dominio']}/{'pt/' if lang_key == 'pt' else ''}"
    alternates = [("es", f"{S['cv']}/"), ("pt-BR", f"{S['cv']}/pt/"), ("x-default", f"{S['cv']}/")]
    ld = {
        "@context": "https://schema.org",
        "@type": "ProfilePage",
        "url": url,
        "inLanguage": CVD["html_lang"],
        "dateModified": S["actualizado"],
        "mainEntity": {"@type": "Person", "@id": f"{S['dominio']}/#franco", "name": S["nombre"], "jobTitle": CVD["role"], "email": S["email"], "url": f"{S['dominio']}/", "sameAs": [S["linkedin"]]},
    }
    page = head(lang=CVD["html_lang"], title=CVD["title"], description=CVD["description"], canonical=url, prefix=prefix, alternates=alternates, css_v=css_v, jsonld=ld,
                og={"locale": "pt_BR" if lang_key == "pt" else "es_AR", "title": f"{S['nombre']} · {CVD['role']}", "description": CVD["tagline"], "image": f"{S['dominio']}/img/og-cv.png"})
    page = page.replace(f'href="{prefix}css/site.css?v={css_v}" />', f'href="{prefix}css/site.css?v={css_v}" />\n  <link rel="stylesheet" href="{prefix}css/cv.css?v={css_v}" />')
    page += f"""
<body class="cv-body">
  <main class="cv wrap" id="contenido">
    <header class="cv-head">
      <picture class="cv-photo">
        <source srcset="{prefix}img/franco-hanemann.webp" type="image/webp" />
        <img src="{prefix}img/franco-hanemann.jpg" alt="{S['nombre']}" width="640" height="640" />
      </picture>
      <div class="cv-id">
        <h1>{S['nombre']}</h1>
        <p class="cv-role">{CVD['role']}</p>
        <p class="cv-tagline">{CVD['tagline']}</p>
      </div>
      <nav class="cv-actions" aria-label="{CVD['contact_label']}">
        <a class="cv-btn cv-btn--solid" href="{prefix}{CVD['pdf_file']}" download>{CVD['pdf_label']}</a>
        <a class="cv-btn" href="{site}">{CVD['site_label']}</a>
        <a class="cv-btn" href="{prefix}{CVD['alt_lang']['href'] if lang_key == 'es' else ''}" hreflang="{'pt-BR' if lang_key == 'es' else 'es'}">{CVD['alt_lang']['label']}</a>
      </nav>
    </header>
    <ul class="cv-contact" aria-label="{CVD['contact_label']}">
      <li><a href="mailto:{S['email']}">{S['email']}</a></li>
      <li><a href="https://wa.me/{S['whatsapp_num']}">{S['whatsapp_display']}</a></li>
      <li>{CVD['loc']}</li>
      <li><a href="{S['dominio']}/">n8n.hanemann.ar</a></li>
      <li><a href="{S['linkedin']}">LinkedIn</a></li>
    </ul>
    <div class="cv-grid">
      <div class="cv-main">
        <section><h2>{CVD['h_resumen']}</h2><p class="cv-summary">{CVD['resumen']}</p></section>
        <section><h2>{CVD['h_exp']}</h2><ol class="cv-jobs">{exp}
        </ol></section>
      </div>
      <aside class="cv-side">
        <section><h2>{CVD['h_skills']}</h2><ul class="cv-tags">{skills}</ul></section>
        <section><h2>{CVD['h_certs']}</h2><ul class="cv-list">{certs}</ul></section>
        <section><h2>{CVD['h_edu']}</h2><ul class="cv-edu">{edu}</ul></section>
        <section><h2>{CVD['h_lang']}</h2><ul class="cv-list">{langs}</ul></section>
        <section><h2>{CVD['h_more']}</h2><p class="cv-more">{CVD['more']}</p></section>
      </aside>
    </div>
  </main>
</body>
</html>
"""
    dest = OUTCV / CVD["path"] / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page, encoding="utf-8")
    return dest


# ---------------------------------------------------------------- bot
def render_bot_prompt():
    """Bloque de precios para pegar en el prompt del bot (sale de precios.json)."""
    v = vars_for(load("es-AR.json"))
    vb = vars_for(load("pt-BR.json"))
    it = P["items"]
    lines = [
        f"## Precios publicados en el sitio (lanzamiento hasta el {v['lanzamiento']})",
        "Usá exactamente estos valores. Si te preguntan por algo que no está acá, decí que se cotiza en el diagnóstico gratis.",
        f"- Diagnóstico: gratis, 30 minutos por videollamada. Link: {S['cal_url']}",
        f"- Automatización puntual (un flujo, sin WhatsApp ni IA conversacional; entrega habitual en 5 días hábiles desde que Franco tiene los accesos, 30 días de correcciones): desde {v['puntual']} (en 2027: {v['puntual_lista']}) · Brasil: a partir de {vb['puntual']}",
        f"- Piloto en modo sombra (50 a 100 chats exportados, informe de acierto, 100% descontable si contrata en 30 días): {v['piloto']} (en 2027: {v['piloto_lista']}) · Brasil: {vb['piloto']}",
        f"- Agente de WhatsApp con IA + CRM: desde {v['agente']} (en 2027: {v['agente_lista']}) · Brasil: a partir de {vb['agente']}. Incluye hasta 4 tipos de consulta, audios, pase a humano, bandeja compartida, 1 CRM con API, 1 semana en modo sombra, 2 rondas de ajustes y manual. No incluye ERP, campañas salientes, panel a medida ni migración.",
        f"- Integración con ERP (siempre después de un piloto): desde {v['erp']} · Brasil: a partir de {vb['erp']}",
        f"- Operación mensual sin plazo mínimo: Monitoreo {v['monitoreo']} (hasta 3 flujos, respuesta en 48 h) u Operación {v['operacion']} (hasta 10 flujos, 2 h de cambios, respuesta en 24 h) · Brasil: {vb['monitoreo']} / {vb['operacion']}",
        f"- Horas sueltas: {v['hora']} la hora, con presupuesto previo · Brasil: {vb['hora']} por hora.",
        "- Meta (mensajes de WhatsApp) y el proveedor de IA se pagan aparte, directo y a nombre de la empresa del cliente, sin recargo de Franco.",
        "- Pago: 50% al empezar y 50% contra entrega. Argentina: en dólares o en pesos al tipo de cambio vendedor del Banco Nación del día de la factura. Resto de Latinoamérica y Brasil: transferencia internacional en dólares; en Brasil los valores en reales son referencia y los tributos de importación de servicio corren por cuenta del cliente.",
    ]
    tpl = (C / "bot-prompt.md").read_text(encoding="utf-8")
    out = tpl.replace("{{PRECIOS}}", "\n".join(lines)).replace("{{CAL}}", S["cal_url"]).replace("{{WHATSAPP}}", S["whatsapp_display"])
    d = DIST / "bot"
    d.mkdir(parents=True, exist_ok=True)
    (d / "system-prompt.md").write_text(out, encoding="utf-8")


# ---------------------------------------------------------------- archivos de servidor
def server_files():
    today = S["actualizado"]
    D = S["dominio"]
    alts = '\n'.join(
        f'    <xhtml:link rel="alternate" hreflang="{h}" href="{u}"/>' for h, u in [("es-AR", f"{D}/"), ("es", f"{D}/es/"), ("pt-BR", f"{D}/pt/"), ("x-default", f"{D}/es/")]
    )
    urls = ""
    for u, pr in [(f"{D}/", "1.0"), (f"{D}/es/", "0.9"), (f"{D}/pt/", "0.9")]:
        urls += f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n{alts}\n    <priority>{pr}</priority>\n  </url>\n"
    for u in (f"{D}/privacidad/", f"{D}/pt/privacidade/"):
        urls += f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>0.2</priority>\n  </url>\n"
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + "</urlset>\n",
        encoding="utf-8",
    )
    robots = (ROOT / "legacy/publicado-2026-06-17/robots.txt").read_text(encoding="utf-8")
    (OUT / "robots.txt").write_text(robots, encoding="utf-8")
    shutil.copy(ROOT / "server/htaccess-n8n", OUT / ".htaccess")
    shutil.copy(ROOT / "server/htaccess-cv", OUTCV / ".htaccess")
    (OUTCV / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")


# ---------------------------------------------------------------- main
def main():
    if DIST.exists():
        for sub in (OUT, OUTCV, DIST / "bot"):
            if sub.exists():
                shutil.rmtree(sub)
    for target in (OUT, OUTCV):
        target.mkdir(parents=True, exist_ok=True)
        for folder in ("css", "js", "fonts", "img"):
            if (ST / folder).exists():
                shutil.copytree(ST / folder, target / folder, dirs_exist_ok=True)
    shutil.rmtree(OUTCV / "js", ignore_errors=True)
    # rutas viejas del CV (el sitio anterior y LinkedIn apuntan a /profile.png)
    for f in (ST / "cv-legacy").iterdir():
        shutil.copy(f, OUTCV / f.name)
    css_v = file_hash(ST / "css/site.css")[:5] + file_hash(ST / "css/cv.css")[:5]
    js_v = file_hash(ST / "js/site.js")
    for code in LOCALES:
        render_home(code, css_v, js_v)
    es_alt = [("es-AR", f"{S['dominio']}/privacidad/"), ("pt-BR", f"{S['dominio']}/pt/privacidade/"), ("x-default", f"{S['dominio']}/privacidad/")]
    render_text_page(code="es-AR", rel_path="privacidad/", title="Política de privacidad · Franco Hanemann",
                     description="Qué datos recibe el sitio n8n.hanemann.ar, para qué los uso y cómo ejercer tus derechos.",
                     fragment=(C / "privacidad.es.html").read_text(encoding="utf-8"), alternates=es_alt, css_v=css_v, current="privacy")
    render_text_page(code="pt-BR", rel_path="pt/privacidade/", title="Política de privacidade · Franco Hanemann",
                     description="Quais dados o site n8n.hanemann.ar recebe, para que são usados e como exercer seus direitos.",
                     fragment=(C / "privacidade.pt.html").read_text(encoding="utf-8"), alternates=es_alt, css_v=css_v, current="privacy")
    render_text_page(code="es-AR", rel_path="", title="Página no encontrada · Franco Hanemann", description="Esta página no existe.",
                     fragment='<h1>Esta página no existe</h1>\n<p>Puede que el enlace esté mal escrito o que la página se haya movido.</p>',
                     alternates=[], css_v=css_v, current="", noindex=True, back_label="Ir al inicio", prefix="/")  # 404: rutas absolutas
    render_cv("es", css_v)
    render_cv("pt", css_v)
    render_bot_prompt()
    server_files()
    n = sum(1 for _ in DIST.rglob("*") if _.is_file())
    print(f"OK · {n} archivos en {DIST.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
