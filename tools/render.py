#!/usr/bin/env python3
"""Tareas con navegador (Playwright + Chromium):
  python3 tools/render.py og      -> static/img/og-es.png, og-pt.png, og-cv.png (correr ANTES de build.py)
  python3 tools/render.py pdf     -> PDFs del CV dentro de dist/cv.hanemann.ar/ (correr DESPUÉS de build.py)
  python3 tools/render.py shots DIR -> capturas 390 px y 1440 px de cada página en DIR
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
ST = ROOT / "static"
DIST = ROOT / "dist"
LAUNCH = {"executable_path": "/opt/pw-browsers/chromium"} if Path("/opt/pw-browsers/chromium").exists() else {}

TURBINA_JS = """
const c=document.getElementById('t'),x=c.getContext('2d'),S=c.width,R=S*0.43,N=13,L=0.14,K=0.37;
x.translate(S/2,S/2);x.rotate(20*Math.PI/180+0.6);x.beginPath();
for(let i=0;i<N;i++){x.save();x.rotate(Math.PI*2*i/N);x.moveTo(0,0);
x.bezierCurveTo(-R*0.06,-R*0.28,-R*(0.06+L*0.5),-R*0.62,-R*L,-R);
x.bezierCurveTo(R*K,-R*0.72,R*(K-0.04),-R*0.22,0,0);x.closePath();x.restore();}
const g=x.createRadialGradient(0,0,R*0.08,0,0,R*1.05);g.addColorStop(0,'#FF2A3E');g.addColorStop(0.45,'#C8141E');g.addColorStop(1,'#6C000A');
x.shadowColor='rgba(100,0,0,0.42)';x.shadowBlur=24;x.fillStyle=g;x.fill();
"""


def og_html(eyebrow, lines, accent_idx, foot):
    h1 = "".join(f'<span class="{"a" if i in accent_idx else ""}">{l}</span>' for i, l in enumerate(lines))
    fonts = (ST / "fonts").as_uri()
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:SG;font-weight:700;src:url({fonts}/space-grotesk-latin-700.woff2)}}
@font-face{{font-family:SG;font-weight:500;src:url({fonts}/space-grotesk-latin-500.woff2)}}
@font-face{{font-family:IN;font-weight:100 900;src:url({fonts}/inter-latin-var.woff2)}}
html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:#08080a;color:#f5f5f7}}
body{{position:relative;font-family:IN,sans-serif;
background:radial-gradient(60% 70% at 85% 30%,rgba(236,31,51,.30),transparent 60%),radial-gradient(50% 50% at 0% 0%,rgba(236,31,51,.10),transparent 60%),#08080a}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.03) 1px,transparent 1px);background-size:58px 58px}}
.wrap{{position:absolute;left:72px;top:64px;right:420px;bottom:60px;display:flex;flex-direction:column}}
.eb{{font-family:SG;font-weight:500;font-size:20px;letter-spacing:.18em;text-transform:uppercase;color:#c8c8cf;display:flex;align-items:center;gap:14px}}
.eb i{{width:10px;height:10px;border-radius:50%;background:#ff5063;box-shadow:0 0 14px #ff5063}}
h1{{font-family:SG;font-weight:700;font-size:88px;line-height:.95;letter-spacing:-.045em;margin:44px 0 0}}
h1 span{{display:block}} h1 .a{{color:#ec1f33}}
.ft{{margin-top:auto;display:flex;align-items:center;gap:16px;font-family:SG;font-weight:500;font-size:24px;color:#c8c8cf}}
.m{{width:44px;height:44px;border-radius:11px;display:grid;place-items:center;background:linear-gradient(150deg,#ff5063,#8e0d18);color:#fff;font-weight:700;font-size:24px}}
canvas{{position:absolute;right:40px;top:115px;width:400px;height:400px;filter:drop-shadow(0 18px 60px rgba(236,31,51,.5))}}
</style></head><body><div class="grid"></div>
<div class="wrap"><div class="eb"><i></i>{eyebrow}</div><h1>{h1}</h1><div class="ft"><span class="m">H</span>{foot}</div></div>
<canvas id="t" width="800" height="800"></canvas><script>{TURBINA_JS}</script></body></html>"""


def do_og():
    jobs = [
        ("og-es.png", "n8n · IA · WhatsApp", ["Tu WhatsApp", "atiende solo.", "Tu equipo", "vende."], [1], "Franco E. Hanemann · n8n.hanemann.ar"),
        ("og-pt.png", "n8n · IA · WhatsApp", ["Seu WhatsApp", "atende sozinho.", "Seu time", "vende."], [1], "Franco E. Hanemann · n8n.hanemann.ar/pt"),
        ("og-cv.png", "Currículum · Currículo", ["Franco E.", "Hanemann", "n8n + IA"], [2], "cv.hanemann.ar"),
    ]
    tmp = ROOT / "tools" / "_og.html"
    with sync_playwright() as p:
        b = p.chromium.launch(**LAUNCH)
        pg = b.new_page(viewport={"width": 1200, "height": 630})
        for name, eb, lines, acc, foot in jobs:
            tmp.write_text(og_html(eb, lines, acc, foot), encoding="utf-8")
            pg.goto(tmp.as_uri())
            pg.wait_for_timeout(400)
            pg.screenshot(path=str(ST / "img" / name), type="png")
            print("og", name)
        b.close()
    tmp.unlink()


def do_pdf():
    cv = DIST / "cv.hanemann.ar"
    jobs = [(cv / "index.html", cv / "franco-hanemann-cv.pdf"), (cv / "pt" / "index.html", cv / "franco-hanemann-curriculo.pdf")]
    with sync_playwright() as p:
        b = p.chromium.launch(**LAUNCH)
        pg = b.new_page()
        for src, dst in jobs:
            pg.goto(src.as_uri())
            pg.wait_for_timeout(300)
            pg.emulate_media(media="print")
            pg.pdf(path=str(dst), format="A4", print_background=True, prefer_css_page_size=True)
            print("pdf", dst.name, dst.stat().st_size)
        b.close()


def do_shots(outdir, site="http://localhost:8775", cv="http://localhost:8776"):
    """Requiere los sitios servidos por HTTP (file:// bloquea las fuentes):
    python3 -m http.server 8775 --directory dist/n8n.hanemann.ar
    python3 -m http.server 8776 --directory dist/cv.hanemann.ar"""
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    pages = {"home-es-AR": site + "/", "home-es": site + "/es/", "home-pt": site + "/pt/", "privacidad": site + "/privacidad/", "cv-es": cv + "/"}
    with sync_playwright() as p:
        b = p.chromium.launch(**LAUNCH)
        for w, h in ((390, 844), (1440, 900)):
            ctx = b.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce")
            pg = ctx.new_page()
            for name, url in pages.items():
                pg.goto(url)
                pg.wait_for_timeout(500)
                pg.screenshot(path=str(out / f"{name}-{w}.png"), full_page=True)
                print("shot", name, w)
            ctx.close()
        b.close()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "og":
        do_og()
    elif cmd == "pdf":
        do_pdf()
    elif cmd == "shots":
        do_shots(sys.argv[2])
    else:
        print(__doc__)
