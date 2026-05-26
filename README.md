# n8n.hanemann.ar

Landing personal de Franco E. Hanemann — Consultor n8n + IA aplicada + desarrollo a medida.

## Stack

Sitio estático sin build:

- HTML5 semántico
- CSS3 vanilla (custom properties + clamp + grid)
- JavaScript vanilla
- GSAP 3.12.5 + ScrollTrigger (CDN)
- Lenis 1.1.20 (smooth scroll, CDN)

## Deploy

Conectado a Netlify. Cada push a `main` deploya automáticamente.

URL producción: https://n8n.hanemann.ar

## Estructura

```
.
├── index.html          # Página principal
├── css/
│   ├── main.css        # Estilos generales (~2.8k líneas)
│   └── chat.css        # Drawer del chat
├── js/
│   ├── site.js         # GSAP, Lenis, cursor custom, section indicator
│   ├── turbina-hero.js # Canvas turbina 13 aspas
│   └── chat.js         # Drawer del chat
└── assets/
    └── logo-mark.svg
```
