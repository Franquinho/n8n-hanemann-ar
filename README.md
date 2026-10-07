# n8n.hanemann.ar + cv.hanemann.ar

Sitio de Franco E. Hanemann (agentes de WhatsApp con IA y automatización con n8n) y su CV.
Sitio estático generado con un script de Python sin dependencias. **Este repo es la fuente de verdad:** lo que está en `dist/` es exactamente lo que se sube al hosting.

## Dónde vive cada cosa

| Qué | Dónde |
|---|---|
| Precios (una sola vez para todo: portadas, JSON-LD y prompt del bot) | `content/precios.json` |
| Contacto, URLs, webhook del bot | `content/sitio.json` |
| Textos de la portada | `content/es-AR.json` (raíz, voseo), `content/es.json` (/es/, tuteo), `content/pt-BR.json` (/pt/) |
| Privacidad | `content/privacidad.es.html`, `content/privacidade.pt.html` |
| CV | `content/cv.json` |
| Prompt del bot del sitio | `content/bot-prompt.md` → sale con precios en `dist/bot/system-prompt.md` |
| Estilos, JS, tipografías, fotos | `static/` |
| Configuración de Apache | `server/htaccess-n8n`, `server/htaccess-cv` |
| Lo que estaba publicado antes de este cambio | `legacy/` (respaldo, no se sube) |

## Cómo cambiar algo y regenerar

```bash
python3 tools/render.py og     # solo si cambian los titulares: regenera las imágenes para compartir
python3 build.py               # genera dist/
python3 tools/render.py pdf    # genera los PDF del CV (siempre después de build.py)
```

Para revisar antes de subir:

```bash
python3 -m http.server 8775 --directory dist/n8n.hanemann.ar &
python3 -m http.server 8776 --directory dist/cv.hanemann.ar &
python3 tools/check.py         # estado HTTP, scroll horizontal en 5 anchos, errores de consola, enlaces rotos
```

`tools/render.py` y `tools/check.py` usan Playwright con Chromium.

## Publicar en DonWeb (Apache)

El sitio **no** está en Netlify: lo sirve DonWeb (servidor `c284.dattaweb.com`). Se sube por el Administrador de archivos o por FTP.

1. **Respaldo:** descargá todo lo que hay hoy en la carpeta de `n8n.hanemann.ar` y en la de `cv.hanemann.ar`, incluido el `.htaccess` (es un archivo oculto).
2. **n8n.hanemann.ar:** subí el contenido de `dist/n8n.hanemann.ar/` a la carpeta del dominio, respetando subcarpetas (`es/`, `pt/`, `privacidad/`, `css/`, `js/`, `fonts/`, `img/`) y el `.htaccess`.
3. **cv.hanemann.ar:** borrá la carpeta `_next/` del CV viejo y subí el contenido de `dist/cv.hanemann.ar/`. `profile.png` y `linkedin-qr.png` quedan en la raíz a propósito: el sitio viejo y otros enlaces los usan.
4. **Probá:** abrí `/`, `/es/`, `/pt/`, `/privacidad/`, una ruta inexistente (tiene que mostrar la 404 propia) y el CV con su PDF. Si aparece "demasiadas redirecciones", borrá el bloque 1 del `.htaccess`.
5. **Bot:** recién después de subir el sitio, pegá `dist/bot/system-prompt.md` como mensaje de sistema del agente del workflow "Asistente IA - Sitio Branding" y publicalo desde la interfaz de n8n. El sitio nuevo ya manda el token que exige el borrador de ese workflow; el sitio viejo no lo mandaba.
6. **Buscadores:** en Google Search Console, enviá `https://n8n.hanemann.ar/sitemap.xml`.

## Reglas para no romper nada

- Cambios de precio: solo en `content/precios.json`. Nunca a mano en el HTML.
- Después de cambiar precios, regenerá y volvé a pegar el prompt del bot: si no, el bot y el sitio dicen cosas distintas.
- Los "precios de lanzamiento" vencen el 31/12/2026. El 1/1/2027 hay que aplicar los valores `*_lista` o sacar la línea "En 2027" del sitio: publicar un aumento y no hacerlo es publicidad engañosa.
- Ningún caso con nombre de cliente ni cifras del cliente sin su permiso por escrito.
