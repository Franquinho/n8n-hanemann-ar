#!/usr/bin/env python3
"""Chequeo de las páginas construidas, servidas por HTTP local.
Uso: python3 tools/check.py [base_sitio] [base_cv]  (por defecto localhost:8775 y :8776)
Revisa: estado HTTP, scroll horizontal en 5 anchos, errores de consola y enlaces internos rotos."""
import sys
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright

SITE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8775"
CV = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8776"
PAGES = [(SITE, p) for p in ("/", "/es/", "/pt/", "/privacidad/", "/pt/privacidade/", "/404.html")] + [(CV, p) for p in ("/", "/pt/")]
WIDTHS = (360, 390, 768, 1024, 1440)
problems = []
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    links = set()
    for base, path in PAGES:
        for w in WIDTHS:
            pg = b.new_page(viewport={"width": w, "height": 844})
            errs = []
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(str(e)))
            r = pg.goto(base + path)
            pg.wait_for_timeout(250)
            sw = pg.evaluate("document.documentElement.scrollWidth")
            if r.status != 200 or sw > w or errs:
                problems.append(f"{base}{path} @{w}: status={r.status} scrollWidth={sw} errors={errs[:2]}")
            if w == 390:
                for h in pg.eval_on_selector_all("a[href], link[rel=stylesheet], img[src], source[srcset], script[src]", "els => els.map(e => e.getAttribute('href') || e.getAttribute('src') || e.getAttribute('srcset'))"):
                    u = urljoin(base + path, h)
                    if urlparse(u).netloc in (urlparse(SITE).netloc, urlparse(CV).netloc):
                        links.add(u.split("#")[0])
            pg.close()
    ctx = b.new_context()
    for u in sorted(links):
        resp = ctx.request.get(u)
        if resp.status != 200:
            problems.append(f"enlace roto {u} -> {resp.status}")
    b.close()
print(f"{len(PAGES)} páginas x {len(WIDTHS)} anchos, {len(links)} enlaces internos")
print("\n".join(problems) if problems else "Sin problemas")
