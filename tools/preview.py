#!/usr/bin/env python3
"""Arma una copia navegable de dist/ para la vista previa privada (artifact).
Uso: python3 tools/preview.py SALIDA
Copia los dos sitios a SALIDA/n8n y SALIDA/cv, cambia los enlaces a carpetas ("es/") por
"es/index.html" (el visor no resuelve índices de carpeta) y une los enlaces cruzados entre
sitio y CV. No toca SALIDA/index.html (la página de revisión)."""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
out = Path(sys.argv[1])
for name, src in (("n8n", "n8n.hanemann.ar"), ("cv", "cv.hanemann.ar")):
    dst = out / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(ROOT / "dist" / src, dst, ignore=shutil.ignore_patterns(".htaccess", "404.html", "LICENSE-*", "og-*.png", "profile.png", "linkedin-qr.png", "robots.txt", "sitemap.xml", "cv.css" if name == "n8n" else "__none__"))


def fix(m):
    url = m.group(1)
    if re.match(r"^(https?:|mailto:|tel:|data:|#|/)", url) or not url:
        return m.group(0)
    path, _, frag = url.partition("#")
    if path.endswith("/"):
        path = ("" if path == "./" else path) + "index.html"
    return 'href="' + path + ("#" + frag if frag else "") + '"'


for f in out.rglob("*.html"):
    if f.parent == out:
        continue
    up = "../" * (len(f.relative_to(out).parts) - 1)
    s = re.sub(r'href="([^"]*)"', fix, f.read_text(encoding="utf-8"))
    s = s.replace('href="https://cv.hanemann.ar"', f'href="{up}cv/index.html"')
    s = s.replace('href="https://n8n.hanemann.ar/pt/"', f'href="{up}n8n/pt/index.html"')
    s = s.replace('href="https://n8n.hanemann.ar/"', f'href="{up}n8n/index.html"')
    f.write_text(s, encoding="utf-8")
files = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file() and p.name != "index.html" or (p.is_file() and p.parent != out))
print("\n".join(files))
