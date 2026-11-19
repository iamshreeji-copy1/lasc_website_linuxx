# SATs website – how it is built and how to change it

The site is plain static HTML/CSS/JS (hosted on GitHub Pages). The product pages, the home page, the 404 page,
`sitemap.xml` and `assets/data/products.json` are **generated** from a few data files, so one edit updates every page.

## Everyday tasks

| I want to… | Do this |
|---|---|
| Change a product name, short text, category, icon or photos | Edit `_tools/registry.py` (the `PRODUCTS` list), then rebuild |
| Change phone, e-mail, address, brochure/video links | Edit `SITE` at the top of `_tools/registry.py`, then rebuild |
| Change a product's specification wording | Edit `_tools/product_content.json` (or send the new text), then rebuild |
| Change the "At a glance" numbers or the temperature explorer | Edit `GLANCE` / `RANGE` in `_tools/registry.py`, then rebuild |
| Add or remove a **LinkedIn post** | `python3 _tools/linkedin.py add '<embed code>'` – no rebuild needed (see below) |
| Rebuild everything | `python3 _tools/build.py` |
| Re-make web-sized images after adding a photo | `python3 _tools/optimise_images.py` then rebuild |
| Preview locally | `python3 -m http.server 8000` in this folder, open http://127.0.0.1:8000 |

## LinkedIn posts
1. On LinkedIn open the post → **⋯** → **Embed this post** → copy the code.
2. `python3 _tools/linkedin.py add '<paste the whole code here>' --title "Short label"`
3. Commit and push `assets/data/linkedin-posts.json`. The post shows straight away (set `"autoload": false` to ask visitors first,
   because LinkedIn's embeds set cookies). With no posts, only the "Follow on LinkedIn" card shows.
   `python3 _tools/linkedin.py list` / `remove N` manage the list.

### Live, automatic LinkedIn feed
LinkedIn offers no free automatic feed, so a live feed needs a widget service (e.g. Elfsight or SociableKIT):
create an account, connect the LinkedIn page/profile there, copy the widget ID, then run
`python3 _tools/linkedin.py widget elfsight <ID>` (or `sociablekit <ID>`). New LinkedIn posts then appear on the site by themselves.
Posts show immediately (no click). To ask visitors for consent first, set `"autoload": false` in `assets/data/linkedin-posts.json`.

## What each file does
- `_tools/build.py` – page templates (header, footer, hero, product pages, 404, sitemap, robots).
- `_tools/registry.py` – the single source of truth for products, contact details, glance numbers, explorers.
- `_tools/product_content.json` – the original specification text extracted from the old pages.
- `_tools/optimise_images.py`, `_tools/brand.py` – image optimisation and logo variants (official logo in `assets/img/brand/`).
- `assets/css/main.css` (template base) → `sats.css` (v1 refinements) → `sats-v2.css` (brand, animation, dark theme, accessibility).
- `assets/js/main.js` (template base) · `sats-fx.js` (canvases, effects, theme) · `sats-product.js` (product tabs, search, explorer) ·
  `sats-app.js` (quick search, enquiry list) · `sats-a11y.js` (accessibility panel) · `sats-linkedin.js` (LinkedIn corner).
- `_archive/` – old template/demo pages kept for reference. Not deployed (see `.github/workflows/static.yml`).

## Good to know
- Do not edit the generated `*.html` files by hand – the next rebuild overwrites them. Edit the data/templates above.
- Colours come from the official logo: teal `#008374`, coral `#F85A40` (CSS variables at the top of `sats.css` / `sats-v2.css`).
- Visitors' choices (theme, accessibility, enquiry list, LinkedIn opt-in) are stored only in their own browser (localStorage).
- The original, untouched site is backed up in `../lasc_website_BACKUP_2026-11-19`.
