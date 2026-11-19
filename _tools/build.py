#!/usr/bin/env python3
"""
Regenerates the SATs static site from one set of shared fragments.

    python3 _tools/optimise_images.py   # once (or when images change)
    python3 _tools/build.py             # rebuild index + product pages + 404 + sitemap + robots

Content for the product pages comes from _tools/product_content.json (extracted once from the legacy pages),
product facts / images from _tools/registry.py. Re-running is idempotent.
"""
import os, sys, re, json, html, urllib.parse, shutil, datetime
sys.path.insert(0, os.path.dirname(__file__))
from registry import *

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(ROOT)
MAN = json.load(open('_tools/image_manifest.json'))
CONTENT = json.load(open('_tools/product_content.json'))
TODAY = datetime.date.today().isoformat()
LI_PROFILE = json.load(open('assets/data/linkedin-posts.json', encoding='utf-8'))['profile']
THEME_JS = ("(function(){var d=document.documentElement;d.classList.add('js');try{var t=localStorage.getItem('sats-theme');"
            "if(!t)t='dark';d.setAttribute('data-theme',t);d.setAttribute('data-bs-theme',t);"
            "var m=localStorage.getItem('sats-motion'),r=matchMedia('(prefers-reduced-motion: reduce)').matches;"
            "d.setAttribute('data-motion',(m==='off'||(r&&m!=='on'))?'reduced':'full');"
            "var a=JSON.parse(localStorage.getItem('sats-a11y')||'{}');"
            "if(a.zoom)d.setAttribute('data-a11y-zoom',a.zoom);if(a.contrast)d.setAttribute('data-contrast','high');if(a.font)d.setAttribute('data-a11y-font','readable');"
            "if(a.spacing)d.setAttribute('data-a11y-spacing','on');if(a.links)d.setAttribute('data-a11y-links','on');if(a.cursor)d.setAttribute('data-a11y-cursor','big');"
            "}catch(e){d.setAttribute('data-theme','dark');d.setAttribute('data-bs-theme','dark');d.setAttribute('data-motion','full');}})();")
YEAR = datetime.date.today().year
esc = html.escape
by_key = {p['key']: p for p in PRODUCTS}
S = SITE


def href(file):            # URL-safe link to a page in this folder
    return urllib.parse.quote(file)


def abs_url(path=''):
    return S['domain'] + '/' + path.lstrip('/')


def wa(msg):
    return f"https://wa.me/{S['wa_number']}?text=" + urllib.parse.quote(msg)


def mailto(subject, body=''):
    return f"mailto:{S['email']}?subject=" + urllib.parse.quote(subject) + (("&body=" + urllib.parse.quote(body)) if body else '')


def css_rel(path):   # url() inside a CSS variable resolves against assets/css/
    return path.replace('assets/', '../', 1)


def web_img(src, tag):
    dst, w, h = MAN[f"{src}|{tag}"]
    return dst, w, h


# ------------------------------------------------------------------ shared fragments
def head(title, desc, path, *, jsonld=None, canonical=None, noindex=False, og_image='assets/img/og-sats.jpg'):
    canon = abs_url(canonical if canonical is not None else path)
    ld = ''.join(f'\n  <script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in (jsonld or []))
    robots = '\n  <meta name="robots" content="noindex, follow">' if noindex else ''
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script>{THEME_JS}</script>

  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={S['gtag']}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{S['gtag']}');
  </script>
  <!-- Google Tag Manager -->
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
  new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
  'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
  }})(window,document,'script','dataLayer','{S['gtm']}');</script>

  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc, quote=True)}">
  <meta name="keywords" content="semiconductor testing, semiconductor analysis, probe station, cryogenic probe station, potentiostat, hydrothermal autoclave, PEC setup, sample holder, muffle furnace, lab equipment India, SATs, Gandhinagar">{robots}
  <meta name="theme-color" content="#008374">
  <link rel="canonical" href="{canon}">

  <!-- Open Graph / Twitter -->
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="SATs – {S['long_name']}">
  <meta property="og:url" content="{canon}">
  <meta property="og:title" content="{esc(title, quote=True)}">
  <meta property="og:description" content="{esc(desc, quote=True)}">
  <meta property="og:image" content="{abs_url(og_image)}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title, quote=True)}">
  <meta name="twitter:description" content="{esc(desc, quote=True)}">
  <meta name="twitter:image" content="{abs_url(og_image)}">

  <!-- Icons -->
  <link rel="icon" type="image/png" sizes="32x32" href="assets/img/favicon-32.png">
  <link rel="icon" type="image/png" sizes="192x192" href="assets/img/icon-192.png">
  <link rel="apple-touch-icon" href="assets/img/apple-touch-icon-180.png">

  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Open+Sans:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">

  <!-- Vendor CSS -->
  <link href="assets/vendor/bootstrap/css/bootstrap.min.css" rel="stylesheet">
  <link href="assets/vendor/bootstrap-icons/bootstrap-icons.min.css" rel="stylesheet">
  <link href="assets/vendor/aos/aos.css" rel="stylesheet">
  <link href="assets/vendor/glightbox/css/glightbox.min.css" rel="stylesheet">
  <link href="assets/vendor/swiper/swiper-bundle.min.css" rel="stylesheet">

  <!-- Site CSS -->
  <link href="assets/css/main.css" rel="stylesheet">
  <link href="assets/css/sats.css" rel="stylesheet">
  <link href="assets/css/sats-v2.css" rel="stylesheet">
  <noscript><style>#preloader{{display:none}}[data-aos]{{opacity:1!important;transform:none!important}}.hero .hero-copy>*{{opacity:1}}</style></noscript>{ld}
</head>
"""


def social_links(cls='social-links d-flex'):
    out = ''.join(
        f'<a href="{u}" class="{k}" target="_blank" rel="noopener noreferrer" aria-label="{esc(n)}"><i class="bi bi-{k}"></i></a>'
        for k, n, u in S['social'])
    return f'<div class="{cls}">{out}</div>'


def header(on_index, active=None):
    base = '' if on_index else 'index.html'
    home = '#hero' if on_index else 'index.html'
    items = [('Home', home, 'home'), ('About', base + '#about', 'about'), ('Services', base + '#services', 'services'),
             ('Products', base + '#portfolio', 'products'), ('Pricing', base + '#pricing', 'pricing'), ('FAQ', base + '#faq', 'faq')]
    lis = ''.join(f'<li><a href="{h}"{" class=\"active\" aria-current=\"page\"" if active == k else ""}>{n}</a></li>' for n, h, k in items)
    lis += f'<li><a class="getstarted" href="{base}#contact">Contact</a></li>'
    soc = ''.join(f'<a href="{u}" class="{k}" target="_blank" rel="noopener noreferrer" aria-label="{esc(n)}"><i class="bi bi-{k}"></i></a>' for k, n, u in S['social'])
    return f"""<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <!-- Google Tag Manager (noscript) -->
  <noscript><iframe src="https://www.googletagmanager.com/ns.html?id={S['gtm']}" height="0" width="0" style="display:none;visibility:hidden" title="Google Tag Manager"></iframe></noscript>

  <!-- ======= Top bar ======= -->
  <section id="topbar" class="topbar d-flex align-items-center">
    <div class="container d-flex justify-content-center justify-content-md-between">
      <div class="contact-info d-flex align-items-center">
        <i class="bi bi-envelope d-flex align-items-center"><a href="mailto:{S['email']}">{S['email']}</a></i>
        <i class="bi bi-phone d-flex align-items-center ms-4"><a href="tel:{S['phone_tel']}">{S['phone_display']}</a></i>
      </div>
      <div class="social-links d-none d-md-flex align-items-center">{soc}</div>
    </div>
  </section>

  <!-- ======= Header ======= -->
  <header id="header" class="header d-flex align-items-center">
    <div class="container-fluid container-xl d-flex align-items-center justify-content-between">
      <a href="{home if on_index else 'index.html'}" class="logo d-flex align-items-center" aria-label="SATs home">
        <span class="logo-sats" aria-hidden="true">SATS</span><span class="visually-hidden">SATs – Semiconductor Analysis and Testing Solutions</span>
      </a>
      <nav id="navbar" class="navbar" aria-label="Main">
        <ul>{lis}</ul>
      </nav>
      <button type="button" class="theme-toggle search-toggle" data-open-search aria-label="Search products (press /)" aria-haspopup="dialog"><i class="bi bi-search" aria-hidden="true"></i></button>
      <button type="button" id="theme-toggle" class="theme-toggle" aria-label="Switch to dark theme" aria-pressed="false"><i class="bi bi-moon-stars-fill" aria-hidden="true"></i><i class="bi bi-sun-fill" aria-hidden="true"></i></button>
      <i class="mobile-nav-toggle mobile-nav-show bi bi-list" role="button" tabindex="0" aria-label="Open menu" aria-expanded="false"></i>
      <i class="mobile-nav-toggle mobile-nav-hide d-none bi bi-x" role="button" tabindex="0" aria-label="Close menu"></i>
    </div>
  </header>
"""


def footer(on_index):
    base = '' if on_index else 'index.html'
    quick = [('Home', '#hero' if on_index else 'index.html'), ('About us', base + '#about'), ('Services', base + '#services'),
             ('Products', base + '#portfolio'), ('Pricing', base + '#pricing'), ('FAQ', base + '#faq'), ('Contact', base + '#contact')]
    quick_li = ''.join(f'<li><a href="{h}">{n}</a></li>' for n, h in quick)
    prods = [p for p in PRODUCTS if not p.get('canonical_of')]
    prod_li = ''.join(f'<li><a href="{href(p["file"])}">{esc(p["name"])}</a></li>' for p in prods)
    addr = '<br>'.join(S['address_lines'])
    return f"""
  <!-- ======= Footer ======= -->
  <footer id="footer" class="footer">
    <div class="container">
      <div class="row gy-4">
        <div class="col-lg-3 col-md-12 footer-info">
          <a href="{'#hero' if on_index else 'index.html'}" class="logo d-flex align-items-center" aria-label="SATs home"><img src="assets/img/brand/sats-logo-white.png" width="734" height="527" loading="lazy" alt="SATs – Semiconductor Analysis and Testing Solutions"></a>
          <p>SATs specializes in semiconductor testing equipment: Low Temp Probe Stations, Hydrothermal Systems, Autoclaves, Sample Holders, Automated PEC Setups, Industrial-Grade Water Chillers, and Custom Software Solutions.</p>
          {social_links('social-links d-flex mt-4')}
        </div>
        <div class="col-lg-2 col-6 footer-links">
          <h2 class="fh">Quick links</h2>
          <ul>{quick_li}</ul>
        </div>
        <div class="col-lg-4 col-12 footer-links two-col">
          <h2 class="fh">Our products</h2>
          <ul>{prod_li}</ul>
        </div>
        <div class="col-lg-3 col-6 footer-contact">
          <h2 class="fh">Contact us</h2>
          <ul>
            <li><i class="bi bi-geo-alt-fill"></i><span>{addr}</span></li>
            <li><i class="bi bi-telephone-fill"></i><a href="tel:{S['phone_tel']}">{S['phone_display']}</a></li>
            <li><i class="bi bi-envelope-fill"></i><a href="mailto:{S['email']}">{S['email']}</a></li>
            <li><i class="bi bi-whatsapp"></i><a href="{wa('Hello SATs, I would like to know more about your products. Contacted from the SATs website.')}" target="_blank" rel="noopener noreferrer">Chat on WhatsApp</a></li>
          </ul>
        </div>
      </div>
      {'' if on_index else '<div class="made-with">Crafted with <span class="heart" aria-hidden="true">❤</span> love in Gandhinagar, India<small>SATs – Instruments made by researchers, for researchers.</small></div>'}
      <div class="footer-bottom">
        <div class="copyright">&copy; {YEAR} <strong><span>SATs</span></strong>. All Rights Reserved</div>
        <div class="credits">Designed by <a href="{S['credit_url']}" target="_blank" rel="noopener noreferrer"><b>Team SATs</b> with ❤️</a></div>
      </div>
    </div>
  </footer>

  <a href="#" class="scroll-top d-flex align-items-center justify-content-center" aria-label="Back to top"><i class="bi bi-arrow-up-short"></i></a>
  <div id="preloader" aria-hidden="true"></div>
"""


def scripts(index=False, product=False):
    li_js = '\n  <script src="assets/js/sats-linkedin.js"></script>' if index else ''
    extra = ('\n  <script src="assets/vendor/purecounter/purecounter_vanilla.js"></script>'
             '\n  <script src="assets/vendor/isotope-layout/isotope.pkgd.min.js"></script>') if index else ''
    prod_js = '\n  <script src="assets/js/sats-product.js"></script>' if product else ''
    return f"""
  <!-- Vendor JS -->
  <script src="assets/vendor/bootstrap/js/bootstrap.bundle.min.js"></script>
  <script src="assets/vendor/aos/aos.js"></script>
  <script src="assets/vendor/glightbox/js/glightbox.min.js"></script>
  <script src="assets/vendor/swiper/swiper-bundle.min.js"></script>{extra}

  <!-- Site JS -->
  <script src="assets/js/main.js"></script>
  <script src="assets/js/sats-fx.js"></script>
  <script src="assets/js/sats-app.js"></script>
  <script src="assets/js/sats-a11y.js"></script>{prod_js}{li_js}
</body>
</html>
"""


def cta_wa_msg(name):
    return f"Hello SATs, I'm interested in the {name}. Please share the details. Contacted from the SATs website."


# ------------------------------------------------------------------ product page content
def split_title(text):
    m = re.match(r'^(.{3,60}?)\s+[–—-]\s+(.+)$', text)
    if m and len(m.group(1).split()) <= 8:
        return m.group(1), m.group(2)
    m = re.match(r'^([A-Z][A-Za-z&/ -]{2,40}):\s+(.+)$', text)
    if m:
        return m.group(1), m.group(2)
    return None, text


def parse_page(prod):
    blocks = CONTENT[prod['file']]['blocks']
    key = prod['key']
    seq = []
    for k, t in blocks:
        if k == 'text' and t == 'Key Specifications':
            k = 'h3'
        seq.append((k, t))
    intro, sections, cur, term = [], [], None, None
    for k, t in seq[1:]:
        if k == 'h3':
            cur = {'title': t, 'items': []}; sections.append(cur); term = None
        elif cur is None:
            if k == 'text':
                intro.append(t)
        elif k == 'h5':
            fix = TEXT_FIXUPS.get((key, t))
            term = {'term': t, 'descs': [], 'strip': None}
            if fix:
                term['term'], term['strip'] = fix
            cur['items'].append(term)
        elif k == 'text':
            if term is not None and not term['descs']:
                term['descs'].append(t)
            elif term is not None and re.match(r'^[A-Z][A-Za-z -]{3,40}: ', t) and len(term['descs']) >= 1 and term['term'].lower() not in ('widely used in the semiconductor r&d',):
                cur['items'].append({'term': None, 'descs': [t], 'strip': None}); term = None
            elif term is not None:
                term['descs'].append(t)
            else:
                cur['items'].append({'term': None, 'descs': [t], 'strip': None})
    return intro, sections


def tidy_item(it):
    descs = []
    for d in it['descs']:
        if it.get('strip') and d.startswith(it['strip']):
            d = d[len(it['strip']):]
        if it['term'] and d.lower().startswith(it['term'].lower() + ' '):
            d = d[len(it['term']):].lstrip()
        if re.fullmatch(r'X{4,}', d.strip()):      # legacy placeholder text
            continue
        descs.append(d.strip())
    it = dict(it); it['descs'] = descs
    if it['term']:
        it['term'] = it['term'].rstrip(':').strip()
    return it


PROBE_ITEMS = None


def probe_items():
    global PROBE_ITEMS
    if PROBE_ITEMS is None:
        _, secs = parse_page(by_key['low-temp-probe-station'])
        PROBE_ITEMS = {(i['term'], tuple(i['descs'])) for s in secs for i in s['items'] if i['term']}
    return PROBE_ITEMS


DROPPED = {}


def clean_sections(prod, sections):
    out = []
    for s in sections:
        items = []
        for it in s['items']:
            if (it['term'] and prod['key'] not in PROBE_PAGE_KEYS and it['term'] in PROBE_COPY_TERMS
                    and (it['term'], tuple(it['descs'])) in probe_items()):
                DROPPED.setdefault(prod['key'], []).append(it['term'])
                continue
            items.append(tidy_item(it))
        if items:
            out.append({'title': s['title'], 'items': items})
    return out


# ------------------------------------------------------------------ Phase 2 helpers
_ICON_CSS = open('assets/vendor/bootstrap-icons/bootstrap-icons.min.css', encoding='utf-8').read()


def icon(name):
    assert f'.{name}::before' in _ICON_CSS, f'icon {name} missing'
    return name


ICON_RULES = [
    (('accuracy', 'resolution', 'stability', 'uniformity', 'precision'), 'bi-bullseye'),
    (('temperature', 'thermal', 'heating', 'cooling', 'heat', 'stage'), 'bi-thermometer-half'),
    (('vacuum', 'pressure', 'gas'), 'bi-wind'),
    (('electrode', 'probe', 'contact', 'tip'), 'bi-bullseye'),
    (('optical', 'window', 'light', 'illumination', 'intensity', 'colour', 'color', 'quartz', 'wavelength'), 'bi-brightness-high'),
    (('positioning', 'xyz', 'movement', 'mechanism', 'operation'), 'bi-arrows-move'),
    (('compatib', 'integration', 'integrat', 'connect'), 'bi-plug'),
    (('control', 'pid', 'programm', 'software', 'display', 'interface', 'acquisition', 'pulsing', 'user-friendly'), 'bi-sliders2'),
    (('safety', 'alarm', 'protection', 'reduced'), 'bi-shield-check'),
    (('power', 'supply', 'voltage', 'current', 'potential', 'compliance', 'impedance', 'bias'), 'bi-lightning-charge'),
    (('volume', 'size', 'capacity', 'tank', 'chamber', 'compact'), 'bi-box-seam'),
    (('material', 'shell', 'vessel', 'construction', 'worktop', 'frame', 'steel', 'isolation', 'legs', 'design'), 'bi-layers'),
    (('training', 'curriculum', 'instructor', 'learning', 'case studies'), 'bi-mortarboard'),
    (('support', 'maintenance', 'installation', 'guidance', 'quality', 'customization'), 'bi-headset'),
    (('pump', 'flow', 'circulation', 'water'), 'bi-droplet'),
    (('range', 'rate', 'speed', 'methods'), 'bi-speedometer2'),
]


def spec_icon(term):
    low = (term or '').lower()
    for kws, ic in ICON_RULES:
        if any(k in low for k in kws):
            return icon(ic)
    return icon('bi-patch-check')


_UNIT = r'(?:°\s?C|K|V|mA|nA|µA|pA|µV|mV|TΩ|Ω|Torr|Watts?|W|L|mL|liters?|litres?|µm|mm|%|Hz)'
_NUM = r'[±+\-–−]?\d[\d,]*(?:\.\d+)?'
_TOK = rf'{_NUM}\s?(?:×10\s?[⁻−\-]\s?\d+\s?)?{_UNIT}(?:\s?(?:per minute|/\s?min))?'
_RNG = re.compile(rf'({_TOK})(?:\s?(?:to|–|—|-)\s?({_TOK}))?')

# explicit chip text where the first number in the sentence would be misleading (None = no chip)
KEYVAL = {
    ('muffle-furnace', 'Temperature Range'): '800 – 1500 °C', ('muffle-furnace', 'Chamber Volume'): '1 – 20 L',
    ('muffle-furnace', 'Power Supply'): '230 V / 415 V', ('muffle-furnace', 'Heating Element'): None,
    ('hydrothermal-autoclave', 'Versatile internal Volume Options'): '25 – 2500 mL',
    ('low-temp-probe-station', 'Temperature Versatility'): '−40 to 120 °C', ('micro-probe-station-alt', 'Temperature Versatility'): '−40 to 120 °C',
    ('low-temp-probe-station', 'Vacuum Compatibility'): '5×10⁻² Torr', ('micro-probe-station-alt', 'Vacuum Compatibility'): '5×10⁻² Torr',
    ('low-temp-probe-station', 'Electrode Configuration'): '4 × 50 µm', ('micro-probe-station-alt', 'Electrode Configuration'): '4 × 50 µm',
    ('potentiostat', 'Current Ranges'): '10 nA – 250 mA', ('potentiostat', 'Measured Potential Accuracy'): '0.1 % / 1 mV',
    ('potentiostat', 'Applied Potential Accuracy'): '0.1 % / 1 mV', ('potentiostat', 'Measured Current Accuracy'): '0.5 % / 50 pA',
    ('potentiostat', 'Measured Current Resolution'): '1.5 pA', ('potentiostat', 'Applied Potential Resolution'): '152 µV',
    ('potentiostat', 'Measured Potential Resolution'): '156 µV',
    ('cryogenic-probe-station', 'Temperature Range'): '−196 to +300 °C', ('cryogenic-probe-station', 'Temperature Stability / Resolution'): '±0.1 °C',
    ('externally-controlled-cryo-probe-station', 'Wide Temperature Range'): '−196 to +300 °C',
    ('externally-controlled-cryo-probe-station', 'Fast and Stable Thermal Control'): '50 / 20 °C/min',
    ('light-source', '6500K Colour Temperature'): '6500 K',
}


def key_value(page_key, term, desc):
    if (page_key, term) in KEYVAL:
        return KEYVAL[(page_key, term)]
    m = _RNG.search(desc or '')
    if not m or m.start() > 90:
        return None
    a, b = m.group(1), m.group(2)
    return tidy_kv(a if not b else f'{a} to {b}')


def tidy_kv(s):
    s = re.sub(r'\s*(?:per minute|/\s?min)', '/min', s)
    s = re.sub(r'(\d)\s?°\s?C', r'\1 °C', s)
    s = re.sub(r'(\d)\s?(?:liters?|litres?)', r'\1 L', s)
    s = re.sub(r'(\d)\s?Watts?', r'\1 W', s)
    s = re.sub(r'(^|to |\s)[-–](\d)', lambda m: m.group(1) + '−' + m.group(2), s)
    return re.sub(r'\s+', ' ', s).strip()


def explode_labels(items):
    """Split one run-on item such as 'Rapid Cooling: 400 Watt… Wide Temperature Range: …' into separate items."""
    out = []
    for it in items:
        d = it['descs'][0] if len(it['descs']) == 1 else ''
        parts = re.split(r'(?:(?<=\.)\s+|^)(?=[A-Z][A-Za-z\- ]{2,34}:\s)', d) if d else []
        if len(parts) >= 3:
            for part in parts:
                m = re.match(r'^([A-Z][A-Za-z\- ]{2,34}):\s*(.*)$', part.strip())
                if m and m.group(2).strip():
                    out.append({'term': m.group(1).strip(), 'descs': [m.group(2).strip()], 'strip': None})
        else:
            out.append(it)
    return out


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def kind_of(title):
    low = title.lower()
    if 'applic' in low: return 'apps'
    if 'benefit' in low: return 'benefits'
    if 'add-on' in low: return 'addons'
    if 'method' in low: return 'methods'
    if 'equipment we supply' in low: return 'equip'
    return 'spec'


def fmt_stat(pre, num, suf, dec):
    if num is None:
        return f'<span class="pre">{esc(pre)}</span><span class="suf">{esc(suf)}</span>'
    txt = f'{num:,.{dec}f}'.replace('-', '−')
    return (f'<span class="pre">{esc(pre)}</span><span class="num" data-count="{num}" data-dec="{dec}">{txt}</span><span class="suf">{esc(suf)}</span>')


def render_glance(prod):
    items = GLANCE.get(prod['key'])
    if not items:
        return None
    cells = ''.join(
        f'<div class="pd-stat" data-aos="fade-up" data-aos-delay="{i * 80}"><div class="pd-stat-val">{fmt_stat(pre, num, suf, dec)}</div><div class="pd-stat-label">{esc(label)}</div></div>'
        for i, (pre, num, suf, label, dec) in enumerate(items))
    return {'id': 'sec-glance', 'label': 'At a glance', 'html': f'<section class="pd-section pd-glance" id="sec-glance"><h2>At a glance</h2><div class="pd-glance-grid">{cells}</div></section>'}


def render_range(prod):
    cfg = RANGE.get(prod['key'])
    if not cfg:
        return None
    data = {k: cfg[k] for k in ('min', 'max', 'std_max', 'default', 'heat', 'cool', 'zones') if k in cfg}
    marks = ''.join(f'<span style="left:calc(11px + (100% - 22px) * {(v - cfg["min"]) / (cfg["max"] - cfg["min"]):.4f})">{esc(l)}</span>' for v, l in cfg['marks'])
    std = f'calc(11px + (100% - 22px) * {(cfg["std_max"] - cfg["min"]) / (cfg["max"] - cfg["min"]):.4f})'
    eta_note = ('Time estimates assume a 25 °C start and the maximum stated heating/cooling rate; real times depend on load and setup.'
                if cfg.get('heat') else '')
    h = (f'<section class="pd-section" id="sec-explorer"><h2>{esc(cfg["title"])}</h2>'
         f'<div class="pd-range" data-range=\'{json.dumps(data, ensure_ascii=False)}\' style="--std:{std}">'
         f'<div class="pd-range-read"><div class="pd-range-val"><span id="rv-{prod["key"]}">{cfg["default"]}</span><small>°C</small></div>'
         f'<div class="pd-range-info"><div class="pd-range-zone-text" aria-live="polite"></div><div class="pd-range-eta" aria-live="polite"></div></div></div>'
         f'<div class="pd-range-slider"><div class="pd-range-track"><i class="pd-range-fill"></i></div>'
         f'<input type="range" min="{cfg["min"]}" max="{cfg["max"]}" step="1" value="{cfg["default"]}" aria-label="Select a temperature in degrees Celsius" aria-controls="rv-{prod["key"]}"></div>'
         f'<div class="pd-range-marks" aria-hidden="true">{marks}</div>'
         f'<p class="pd-range-note"><i class="bi bi-info-circle"></i> {esc(cfg["note"])} {esc(eta_note)}</p></div></section>')
    return {'id': 'sec-explorer', 'label': 'Explorer', 'html': h}


def render_spec_section(sec, prod, first):
    sid = 'sec-' + slug(sec['title']); items = sec['items']
    cards, rows = '', ''
    for it in items:
        term, descs = it['term'], it['descs']
        if not term and descs:
            term, d0 = split_title(descs[0]); descs = [d0]
        desc = ' '.join(descs)
        kv = key_value(prod['key'], term or '', desc) if term else None
        ic = spec_icon(term)
        search = esc((term or '') + ' ' + desc + ' ' + (kv or ''), quote=True).lower()
        chip = f'<span class="pd-spec-key">{esc(kv)}</span>' if kv else ''
        cards += (f'<article class="pd-spec" data-search="{search}"><div class="pd-spec-top"><span class="pd-spec-ico"><i class="bi {ic}"></i></span>{chip}</div>'
                  f'{f"<h3>{esc(term)}</h3>" if term else ""}<p>{esc(desc)}</p></article>')
        rows += f'<tr data-search="{search}"><th scope="row">{esc(term or "")}</th><td>{esc(kv) if kv else "—"}</td><td>{esc(desc)}</td></tr>'
    tool = ''
    if len(items) >= 5:
        tool = (f'<div class="pd-toolbar"><label class="pd-search"><i class="bi bi-search"></i><input type="search" placeholder="Search specifications…" aria-label="Search specifications"></label>'
                f'<span class="pd-count" aria-live="polite">{len(items)} specifications</span>'
                f'<div class="pd-view" role="group" aria-label="Choose view"><button type="button" data-view="cards" aria-pressed="true"><i class="bi bi-grid-3x3-gap"></i> Cards</button>'
                f'<button type="button" data-view="table" aria-pressed="false"><i class="bi bi-table"></i> Table</button></div></div>')
    html_ = (f'<section class="pd-section pd-specs" id="{sid}" data-total="{len(items)}"><h2>{esc(sec["title"])}</h2>{tool}'
             f'<div class="pd-spec-grid">{cards}</div>'
             f'<div class="pd-table-wrap" hidden><table class="pd-table"><thead><tr><th scope="col">Parameter</th><th scope="col">Key value</th><th scope="col">Details</th></tr></thead><tbody>{rows}</tbody></table></div>'
             f'<p class="pd-empty" hidden>No specification matches your search.</p></section>')
    return {'id': sid, 'label': 'Specifications' if first else sec['title'], 'html': html_}


def render_list_section(sec, prod):
    sid = 'sec-' + slug(sec['title']); k = kind_of(sec['title']); items = sec['items']
    if len(items) == 1 and not items[0]['term'] and items[0]['descs'] and k == 'methods' and items[0]['descs'][0].count(',') >= 3:
        parts = [p.strip(' .') for p in re.split(r',\s*(?:and\s+)?', items[0]['descs'][0]) if p.strip(' .')]
        lis = ''.join(f'<li>{esc(p)}</li>' for p in parts)
        return {'id': sid, 'label': sec['title'], 'html': f'<section class="pd-section" id="{sid}" data-aos="fade-up"><h2>{esc(sec["title"])}</h2><ul class="pd-chips">{lis}</ul></section>'}
    lis = ''
    for n, it in enumerate(items):
        term, descs = it['term'], it['descs']
        if not term and descs:
            term, d0 = split_title(descs[0]); descs = [d0] if term else descs
        body = f'<strong>{esc(term)}</strong>' if term else ''
        if len(descs) == 1 and descs[0]:
            body += f'<span>{esc(descs[0])}</span>'
        elif len(descs) > 1:
            body += '<ul>' + ''.join(f'<li>{esc(d)}</li>' for d in descs) + '</ul>'
        lis += f'<li style="--n:{n}"><i class="bi bi-check2-circle"></i><div>{body}</div></li>'
    return {'id': sid, 'label': 'Applications' if k == 'apps' else sec['title'], 'html': f'<section class="pd-section" id="{sid}" data-aos="fade-up"><h2>{esc(sec["title"])}</h2><ul class="pd-check">{lis}</ul></section>'}


def product_body(prod):
    """returns (intro paragraphs, [section dicts with id/label/html])"""
    k = prod['key']
    if prod.get('spec_on_request'):
        intro = [f"Specifications, configurations and pricing for the SATs {prod['name']} are available on request."]
        note = ('<section class="pd-section" id="sec-details" data-aos="fade-up"><div class="pd-note"><i class="bi bi-info-circle"></i>'
                '<div>Full specifications for this product are available on request. Send us a message and our team will get back to you.</div></div></section>')
        return intro, [{'id': 'sec-details', 'label': 'Details', 'html': note}]
    if prod.get('custom_content') == 'automation':
        intro = ["Our end-to-end automation solutions encompass the complete automation of your testing processes, all designed to enhance efficiency and accuracy in your lab operations.",
                 "We tailor our automation systems to fit your specific needs, ensuring seamless integration and operation."]
        items = [{'term': t, 'descs': []} for t in ('Automated sample handling', 'Data acquisition', 'Analysis', 'Reporting')]
        secs = [render_list_section({'title': 'What is included', 'items': items}, prod),
                {'id': 'sec-ai-ml-predictive-analysis', 'label': 'AI-ML analysis', 'html': '<section class="pd-section" id="sec-ai-ml-predictive-analysis" data-aos="fade-up"><h2>AI-ML predictive analysis</h2><p>Harness the power of Artificial Intelligence and Machine Learning with our predictive analysis services. We help you forecast trends and outcomes, enabling smarter decision-making in semiconductor research and development.</p></section>'}]
        return intro, secs
    intro, sections = parse_page(prod)
    sections = clean_sections(prod, sections)
    extra = []
    if len(intro) == 1 and len(re.findall(r'[A-Z][A-Za-z ]+: ', intro[0])) >= 3:
        parts = [p.strip() for p in re.split(r'(?<=\.)\s+(?=[A-Z][A-Za-z ]+: )', intro[0]) if p.strip()]
        extra.append({'title': 'Equipment we supply', 'items': [{'term': None, 'descs': [p], 'strip': None} for p in parts]})
        intro = [prod['short']]
    if k == 'water-chiller':
        for s in sections:
            if s['title'] == 'Applications':
                s['items'] = [{'term': None, 'descs': [t]} for t in ('Laser Systems', 'Thermal Systems', 'Sputtering Systems', 'Glove Boxes', 'Other lab and industrial equipment')]
            else:
                s['items'] = [i for i in explode_labels(s['items']) if i['descs'] and i['descs'][0]]
    out, first_spec = [], True
    g, r = render_glance(prod), render_range(prod)
    if g: out.append(g)
    if r: out.append(r)
    for s in extra + sections:
        if kind_of(s['title']) == 'spec':
            out.append(render_spec_section(s, prod, first_spec)); first_spec = False
        else:
            out.append(render_list_section(s, prod))
    return intro, out


_KW = {}


def keywords(p):
    """Search terms for a product: its spec parameter names, section titles and at-a-glance labels."""
    k = 'low-temp-probe-station' if p.get('canonical_of') else p['key']
    if k in _KW:
        return _KW[k]
    terms = []
    if not (p.get('spec_on_request') or p.get('custom_content')):
        _, secs = parse_page(by_key[k]); secs = clean_sections(by_key[k], secs)
        for s in secs:
            terms.append(s['title'])
            for it in s['items']:
                if it['term']:
                    terms.append(it['term'])
                elif it['descs']:
                    tt, _d = split_title(it['descs'][0])
                    if tt: terms.append(tt)
    terms += [g[3] for g in GLANCE.get(k, [])]
    out, seen = [], set()
    for x in terms:
        x = x.strip().rstrip(':')
        if x and x.lower() not in seen:
            seen.add(x.lower()); out.append(x)
    _KW[k] = out
    return out


_TXT = {}


def spec_text(p):
    """Full specification wording (names + values) so searches like '1500' or 'PTFE' work."""
    k = 'low-temp-probe-station' if p.get('canonical_of') else p['key']
    if k in _TXT:
        return _TXT[k]
    parts = []
    if p.get('spec_on_request') or p.get('custom_content'):
        parts = [p['short']]
    else:
        intro, secs = parse_page(by_key[k]); secs = clean_sections(by_key[k], secs)
        parts += intro
        for s in secs:
            items = explode_labels(s['items']) if k == 'water-chiller' else s['items']
            for it in items:
                parts.append(' '.join(x for x in [it['term'] or ''] + it['descs'] if x))
    _TXT[k] = re.sub(r'\s+', ' ', ' | '.join(parts))[:4000]
    return _TXT[k]


def search_blob(p):
    return esc(' '.join([p['name'], p.get('card_title') or '', p['short'], CAT_LABEL[p['cat']]] + keywords(p)).lower(), quote=True)


def build_data():
    os.makedirs('assets/data', exist_ok=True)
    rows = []
    for p in PRODUCTS:
        if p.get('canonical_of'):
            continue
        img = None
        if p['imgs']:
            img = web_img(p['imgs'][p.get('card_index', 0)], 'md')[0]
        rows.append({'key': p['key'], 'name': p['name'], 'title': p.get('card_title') or p['name'], 'url': p['file'], 'cat': p['cat'],
                     'catLabel': CAT_LABEL[p['cat']], 'short': p['short'], 'image': img, 'fit': p['fit'], 'keywords': keywords(p), 'text': spec_text(p),
                     'inGrid': bool(p.get('in_grid', True) and p['imgs'])})
    json.dump({'generated': TODAY, 'contact': {'wa': S['wa_number'], 'email': S['email']}, 'products': rows}, open('assets/data/products.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def related(prod, n=3):
    pool = [p for p in PRODUCTS if p.get('in_grid', True) and not p.get('canonical_of') and p['key'] != prod['key']]
    same = [p for p in pool if p['cat'] == prod['cat']]
    rest = [p for p in pool if p['cat'] != prod['cat']]
    return (same + rest)[:n]


def card(p, delay=0, tag=True):
    ci = p.get('card_index', 0)
    dst, w, h = web_img(p['imgs'][ci], 'md')
    contain = ' contain' if p['fit'] == 'contain' else ''
    bgstyle = f' style="--bgimg:url(\'{css_rel(dst)}\')"' if contain else ''
    tg = f'<span class="pc-tag">{CAT_LABEL[p["cat"]]}</span>' if tag else ''
    anchor = (f'<a class="portfolio-card" href="{href(p["file"])}" aria-label="{esc(p["card_title"] or p["name"], quote=True)} – view details">'
              f'<div class="pc-media{contain}"{bgstyle}>{tg}<img src="{dst}" width="{w}" height="{h}" loading="lazy" decoding="async" alt="{esc(p["card_title"] or p["name"], quote=True)}"></div>'
              f'<div class="pc-body"><h3>{esc(p["card_title"] or p["name"])}</h3><i class="bi bi-arrow-right"></i></div></a>')
    btn = (f'<button type="button" class="enq-add" data-enq="{p["key"]}" data-name="{esc(p["name"], quote=True)}" aria-pressed="false" '
           f'aria-label="Add {esc(p["name"], quote=True)} to enquiry list" title="Add to enquiry list"><i class="bi bi-plus-lg"></i></button>')
    return f'<div class="pc-wrap">{anchor}{btn}</div>'


def gallery(prod):
    imgs = prod['imgs']
    if not imgs:
        return f'<div class="pd-gallery"><div class="pd-noimg"><div><i class="bi {prod["icon"]}"></i><span>{esc(prod["name"])}</span></div></div></div>'
    slides = ''
    for i, src in enumerate(imgs):
        md, w, h = web_img(src, 'md'); lg, lw, lh = web_img(src, 'lg')
        alt = f'{prod["name"]} – photo {i + 1} of {len(imgs)}'
        prio = ' fetchpriority="high"' if i == 0 else ' loading="lazy"'
        tag = (f'<a class="glightbox" style="--bgimg:url(\'{css_rel(md)}\')" data-gallery="pd" data-title="{esc(prod["name"], quote=True)}" href="{lg}" aria-label="Enlarge: {esc(alt, quote=True)}">'
               f'<img src="{md}" srcset="{md} {w}w, {lg} {lw}w" sizes="(min-width: 992px) 560px, 92vw" width="{w}" height="{h}" decoding="async"{prio} alt="{esc(alt, quote=True)}"></a>')
        slides += f'<div class="swiper-slide">{tag}</div>'
    if len(imgs) == 1:
        return f'<div class="pd-gallery">{slides.replace("<div class=\"swiper-slide\">", "<div class=\"pd-single-wrap\">", 1)}</div>'
    return (f'<div class="pd-gallery"><div class="slides-1 swiper" aria-label="{esc(prod["name"], quote=True)} photos">'
            f'<div class="swiper-wrapper">{slides}</div><div class="swiper-pagination"></div>'
            f'<div class="swiper-button-prev" aria-label="Previous photo"></div><div class="swiper-button-next" aria-label="Next photo"></div></div></div>')


def build_product(prod):
    intro, secs = product_body(prod)
    name = prod['name']
    title = f"{name} | SATs – Semiconductor Analysis and Testing Solutions"
    desc = prod['short']
    canonical = prod.get('canonical_of') or prod['file']
    ld = [{
        "@context": "https://schema.org", "@type": "Product", "name": name, "description": prod['short'],
        "brand": {"@type": "Brand", "name": "SATs"},
        "image": [abs_url(web_img(i, 'lg')[0]) for i in prod['imgs']] or [abs_url('assets/img/og-sats.jpg')],
        "url": abs_url(canonical),
    }, {
        "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": abs_url('index.html')},
            {"@type": "ListItem", "position": 2, "name": "Products", "item": abs_url('index.html#portfolio')},
            {"@type": "ListItem", "position": 3, "name": name, "item": abs_url(canonical)}]}]
    rel = ''.join(f'<div class="col-lg-4 col-md-6" data-aos="fade-up" data-aos-delay="{i * 100}">{card(p)}</div>' for i, p in enumerate(related(prod)))
    paras = ''.join(f'<p>{esc(t)}</p>' for t in intro)
    tab_items = [(s['id'], s['label']) for s in secs] + [('sec-related', 'Related products')]
    tabs = ('<nav class="pd-tabs" aria-label="Page sections"><ul>' +
            ''.join(f'<li><a href="#{i}"{" class=\"active\"" if n == 0 else ""}>{esc(l)}</a></li>' for n, (i, l) in enumerate(tab_items)) + '</ul></nav>')
    msg = cta_wa_msg(name)
    page = head(title, desc, prod['file'], jsonld=ld, canonical=canonical)
    page += header(False, 'products')
    page += f"""
  <main id="main">
    <section class="breadcrumbs" style="padding:0">
      <div class="page-header d-flex align-items-center">
        <canvas class="fx-circuit" aria-hidden="true"></canvas>
        <div class="container position-relative">
          <div class="row d-flex justify-content-center">
            <div class="col-lg-9 text-center">
              <h1>{esc(name)}</h1>
              <p>{esc(prod['short'])}</p>
            </div>
          </div>
        </div>
      </div>
      <nav aria-label="Breadcrumb">
        <div class="container">
          <ol>
            <li><a href="index.html">Home</a></li>
            <li><a href="index.html#portfolio">Products</a></li>
            <li aria-current="page">{esc(name)}</li>
          </ol>
        </div>
      </nav>
    </section>

    <section class="portfolio-details pd">
      <div class="container">
        <div class="row gy-5 align-items-start">
          <div class="col-lg-7" data-aos="fade-right">{gallery(prod)}</div>
          <div class="col-lg-5" data-aos="fade-left">
            <aside class="pd-summary">
              <span class="pd-badge"><i class="bi {prod['icon']}"></i>{CAT_LABEL[prod['cat']]}</span>
              <h2>Overview</h2>
              {paras}
              <div class="pd-actions">
                <a class="btn-sats btn-sats-wa" href="{wa(msg)}" target="_blank" rel="noopener noreferrer"><i class="bi bi-whatsapp"></i> Enquire on WhatsApp</a>
                <a class="btn-sats btn-sats-primary" href="{mailto('Enquiry: ' + name, msg)}"><i class="bi bi-envelope-fill"></i> Email us</a>
                <button type="button" class="btn-sats btn-sats-outline" data-enq="{prod['key'] if not prod.get('canonical_of') else by_key['low-temp-probe-station']['key']}" data-name="{esc(name, quote=True)}" aria-pressed="false"><i class="bi bi-plus-circle"></i> <span class="enq-label">Add to enquiry list</span></button>
                <a class="btn-sats btn-sats-outline" href="index.html#contact"><i class="bi bi-chat-dots"></i> Open contact form</a>
              </div>
            </aside>
          </div>
        </div>

        {tabs}
        {''.join(s['html'] for s in secs)}

        <section class="pd-section" id="sec-related" data-aos="fade-up">
          <h2>Related products</h2>
          <div class="row gy-4">{rel}</div>
        </section>

        <div class="pd-cta" data-aos="zoom-in">
          <h2>Need this customised for your lab?</h2>
          <p>Tell us about your samples, temperature range and measurement needs – we will recommend the right configuration and share a quote.</p>
          <div class="btn-row">
            <a class="btn-sats btn-sats-primary" href="{wa(msg)}" target="_blank" rel="noopener noreferrer"><i class="bi bi-whatsapp"></i> Talk to us on WhatsApp</a>
            <a class="btn-sats btn-sats-outline" href="{mailto('Enquiry: ' + name, msg)}"><i class="bi bi-envelope-fill"></i> Email us</a>
          </div>
        </div>
      </div>
    </section>
  </main>
"""
    page += footer(False) + scripts(False, product=True)
    open(prod['file'], 'w', encoding='utf-8').write(page)


# ------------------------------------------------------------------ index
def build_index():
    org = {"@context": "https://schema.org", "@type": "Organization", "name": "Semiconductor Analysis and Testing Solutions (SATs)",
           "alternateName": "SATs", "url": abs_url(), "logo": abs_url('assets/img/icon-192.png'), "image": abs_url('assets/img/og-sats.jpg'),
           "email": S['email'], "telephone": S['phone_tel'],
           "address": {"@type": "PostalAddress", "streetAddress": "IIC, PDPU Hostel Road, Raysan", "addressLocality": "Gandhinagar",
                       "addressRegion": "Gujarat", "postalCode": "382007", "addressCountry": "IN"},
           "sameAs": [u for _, _, u in S['social']]}
    title = "Semiconductor Analysis and Testing Solutions India | SATs"
    desc = ("SATs specializes in semiconductor testing equipment, including Low Temp Probe Stations, Hydrothermal Systems, Autoclaves, "
            "Sample Holders, Automated PEC Setups, Industrial-Grade Water Chillers, and Custom Software Solutions.")
    page = head(title, desc, '', jsonld=[org], canonical='')
    page += header(True)

    def logos(hidden):
        return ''.join(
            f'<img src="{MAN["client|" + fn][0]}" width="{MAN["client|" + fn][1]}" height="{MAN["client|" + fn][2]}" loading="lazy" decoding="async" alt="{"" if hidden else esc(alt, quote=True)}">'
            for fn, alt in CLIENTS)
    clients = f'<div class="marquee"><div class="marquee-track">{logos(False)}<span class="marquee-dup" aria-hidden="true" style="display:contents">{logos(True)}</span></div></div>'

    svc = ''
    for i, (t, txt, icon, key) in enumerate(SERVICES):
        link = href(by_key[key]['file']) if key else '#contact'
        label = 'Read more' if key else 'Enquire'
        svc += (f'<div class="col-lg-4 col-md-6" data-aos="fade-up" data-aos-delay="{(i % 3) * 100}"><div class="service-item position-relative">'
                f'<div class="icon"><i class="bi {icon}"></i></div><h3>{esc(t)}</h3><p>{esc(txt)}</p>'
                f'<a href="{link}" class="readmore stretched-link" aria-label="{esc(label)}: {esc(t, quote=True)}">{label} <i class="bi bi-arrow-right"></i></a></div></div>')

    grid_products = [p for p in PRODUCTS if p.get('in_grid', True) and not p.get('canonical_of') and p['imgs']]
    cards = ''.join(
        f'<div class="col-lg-4 col-md-6 portfolio-item filter-{p["cat"]}" data-key="{p["key"]}" data-search="{search_blob(p)}">{card(p)}</div>' for p in grid_products)
    cats_present = [c for c in ('equipment', 'consult', 'edu') if any(p['cat'] == c for p in grid_products)]
    flt = '<li data-filter="*" class="filter-active" role="button" tabindex="0" aria-pressed="true">All</li>' + ''.join(
        f'<li data-filter=".filter-{c}" role="button" tabindex="0" aria-pressed="false">{CAT_LABEL[c]}</li>' for c in cats_present)

    testi = ''
    for fn, name, role, text in TESTIMONIALS:
        d, w, h = MAN['testimonial|' + fn]
        stars = '<i class="bi bi-star-fill"></i>' * 5
        testi += (f'<div class="swiper-slide"><div class="testimonial-wrap"><div class="testimonial-item"><div class="d-flex align-items-center">'
                  f'<img src="{d}" width="{w}" height="{h}" loading="lazy" class="testimonial-img flex-shrink-0" alt="{esc(name, quote=True)}"><div>'
                  f'<h3>{esc(name)}</h3><h4>{esc(role)}</h4><div class="stars" aria-label="5 out of 5 stars">{stars}</div></div></div>'
                  f'<p><i class="bi bi-quote quote-icon-left"></i>{esc(text)}<i class="bi bi-quote quote-icon-right"></i></p></div></div></div>')

    faqs = [
        ("Do you offer customization for your products?", "Yes, we offer customization to meet the specific needs of our clients. Our team will work closely with you to understand your requirements and provide tailored solutions that best fit your research and testing needs."),
        ("What are PEC setups, and why are they important?", "PEC (Photoelectrochemical) setups are essential for studying the interactions between light and semiconductor materials. They are crucial for research in solar energy and other applications where understanding the photoresponse of materials is vital."),
        ("Do you provide training for using your equipment?", "Yes, we provide training sessions for our clients to ensure they are fully equipped to use our products effectively. Training can be arranged at your facility or remotely, depending on your preference."),
        ("What is included in your end-to-end automation solutions?", "Our end-to-end automation solutions encompass the complete automation of your testing processes. This includes automated sample handling, data acquisition, analysis, and reporting, all designed to enhance efficiency and accuracy in your lab operations."),
        ("Can SATs assist with international shipping and installation?", "Yes, SATs provides international shipping and installation services. Our team will ensure that your equipment is delivered and installed efficiently, no matter where you are located."),
        ("What is your return and refund policy?", "Our return and refund policy varies depending on the product. Please contact our customer service team for detailed information regarding returns and refunds."),
    ]
    faq = ''.join(
        f'<div class="accordion-item"><h3 class="accordion-header"><button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq-content-{i}" aria-expanded="false" aria-controls="faq-content-{i}"><span class="num">{i}.</span>{esc(q)}</button></h3>'
        f'<div id="faq-content-{i}" class="accordion-collapse collapse" data-bs-parent="#faqlist"><div class="accordion-body">{esc(a)}</div></div></div>'
        for i, (q, a) in enumerate(faqs, 1))

    def plan(name, icon, price, per, feats, na, msg, featured=False, cta='Enquire on WhatsApp', delay=0):
        li = ''.join(f'<li><i class="bi bi-check"></i>{f}</li>' for f in feats) + ''.join(f'<li class="na"><i class="bi bi-x"></i> <span>{f}</span></li>' for f in na)
        return (f'<div class="col-lg-4" data-aos="fade-up" data-aos-delay="{delay}"><div class="pricing-item{" featured" if featured else ""}"><h3>{name}</h3>'
                f'<div class="icon"><i class="bi {icon}"></i></div><h4>{price}<span>{per}</span></h4><ul>{li}</ul>'
                f'<div class="text-center"><a href="{wa(msg)}" target="_blank" rel="noopener noreferrer" class="buy-btn"><i class="bi bi-whatsapp"></i> {cta}</a></div></div></div>')
    pricing = (
        plan('Free Plan', 'bi-box', '<sup>₹</sup>0', ' / One time only*',
             ['Free sample characterization', 'Free Sample Analysis', 'Free Consultation'],
             ['Hands-on training for sample testing and analysis', 'High precision and accuracy solutions'],
             "I'm interested in the SATs free plan. Please guide me. Contacted from the SATs website.", cta='Get started', delay=0)
        + plan('Basic Plan', 'bi-airplane', '<sup>₹</sup>1,00,000', '/year',
               ['Hands-on training for sample testing and analysis', 'Basic support to fit your needs (&lt; 24 hours)',
                'In-depth procedure on client requirement use-case', 'Optimised performance, managing risk, and keeping costs under control'],
               ['Programmatic solutions'], "I'm interested in the SATs basic plan. Please guide me. Contacted from the SATs website.", featured=True, delay=100)
        + plan('Business Plan', 'bi-send', '<sup>₹</sup>3,00,000', '/year',
               ['High precision and accuracy solutions', 'In-depth procedure on client requirement use-case', 'Programmatic solutions',
                'Architectural Guidance for R&amp;D', 'Enhanced support to fit your needs – prioritized responses'], [],
               "I'm interested in the SATs business plan. Please guide me. Contacted from the SATs website.", delay=200))

    maps = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(S['address_one_line'])
    addr = '<br>'.join(S['address_lines'])
    page += f"""
  <main id="main">
  <!-- ======= Hero ======= -->
  <section id="hero" class="hero">
    <canvas class="fx-circuit" aria-hidden="true"></canvas>
    <div class="container position-relative">
      <div class="row gy-5 align-items-center">
        <div class="col-lg-6 order-2 order-lg-1 d-flex flex-column justify-content-center text-center text-lg-start hero-copy">
          <span class="hero-logo"><img src="assets/img/brand/sats-logo-white.png" width="734" height="527" alt="SATs – Semiconductor Analysis and Testing Solutions"></span>
          <h1>Welcome to <span>SATs.</span></h1>
          <p class="hero-sub">Semiconductor Analysis and Testing Solutions</p>
          <p class="hero-typed" aria-live="off"><span class="label">We build </span><span data-typed data-words='["Probe Stations","Cryogenic Systems","PEC Setups","Hydrothermal Autoclaves","Potentiostats","Sample Holders","Lab Automation"]'>Probe Stations</span><span class="caret" aria-hidden="true"></span></p>
          <div class="d-flex flex-wrap gap-3 justify-content-center justify-content-lg-start align-items-center">
            <a href="{S['brochure']}" target="_blank" rel="noopener noreferrer" class="btn-get-started"><i class="bi bi-download"></i> Get brochure</a>
            <a href="{S['hero_video']}" class="glightbox btn-watch-video d-flex align-items-center"><i class="bi bi-play-circle"></i><span>Watch Video</span></a>
          </div>
        </div>
        <div class="col-lg-6 order-1 order-lg-2">
          <div class="wafer-wrap">
            <canvas id="wafer" role="img" aria-label="Animated semiconductor wafer map: a scanning beam tests each die, most pass and a few fail"></canvas>
            <div class="wafer-caption"><i class="bi bi-cpu" aria-hidden="true"></i><span id="wafer-label">Live wafer map · hover to probe a die</span></div>
          </div>
        </div>
      </div>
    </div>

    <div class="icon-boxes position-relative">
      <div class="container position-relative">
        <div class="row gy-4 mt-5">
          <div class="col-xl-3 col-md-6" data-aos="fade-up" data-aos-delay="0"><div class="icon-box"><div class="icon"><i class="bi bi-easel"></i></div><p class="title">State-of-the-art approaches</p></div></div>
          <div class="col-xl-3 col-md-6" data-aos="fade-up" data-aos-delay="100"><div class="icon-box"><div class="icon"><i class="bi bi-gem"></i></div><p class="title">Best &amp; Extensible Solutions</p></div></div>
          <div class="col-xl-3 col-md-6" data-aos="fade-up" data-aos-delay="200"><div class="icon-box"><div class="icon"><i class="bi bi-patch-check"></i></div><p class="title">High-quality Products</p></div></div>
          <div class="col-xl-3 col-md-6" data-aos="fade-up" data-aos-delay="300"><div class="icon-box"><div class="icon"><i class="bi bi-headset"></i></div><p class="title">24*7 after-sales Support</p></div></div>
        </div>
      </div>
    </div>
  </section>

  <!-- ======= About ======= -->
  <section id="about" class="about">
    <div class="container" data-aos="fade-up">
      <div class="section-header">
        <h2>About Us</h2>
        <p>Our company is driven by a team of active researchers who have been deeply engaged in state-of-the-art research in the semiconductor domain for over 8 years. We are dedicated to advancing technology and providing cutting-edge solutions for semiconductor analysis and testing.</p>
      </div>
      <div class="row gy-4">
        <div class="col-lg-6" data-aos="fade-up" data-aos-delay="0">
          <div class="about-card">
            <h3><i class="bi bi-eye"></i> Vision</h3>
            <p>Our vision is to promote the "Make in India" initiative by developing and manufacturing automatic precision scientific instruments for semiconductor testing in research and development. We aim to position India as a leader in semiconductor technology through our innovative solutions.</p>
          </div>
        </div>
        <div class="col-lg-6" data-aos="fade-up" data-aos-delay="100">
          <div class="about-card">
            <h3><i class="bi bi-bullseye"></i> Mission</h3>
            <ul>
              <li><i class="bi bi-check-circle-fill"></i> Promote "Make In India"</li>
              <li><i class="bi bi-check-circle-fill"></i> Promote "Green Energy Solutions"</li>
              <li><i class="bi bi-check-circle-fill"></i> Promote "Research &amp; Development through specialized instruments"</li>
            </ul>
            <p>Our mission is to forecast the future of green energy, particularly solar energy, and support its advancement through our specialized instruments and services. We are committed to contributing to a sustainable future by providing the tools necessary for groundbreaking research and development in the semiconductor industry.</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ======= Clients ======= -->
  <section id="clients" class="clients" aria-label="Our clients">
    <div class="container" data-aos="fade-up">
      {clients}
    </div>
  </section>

  <!-- ======= Stats ======= -->
  <section id="stats-counter" class="stats-counter">
    <div class="container" data-aos="fade-up">
      <div class="row gy-4 align-items-center">
        <div class="col-lg-6"><img src="assets/img/stats-img.svg" alt="Illustration of two colleagues presenting a chart" class="img-fluid" width="792" height="399" loading="lazy"></div>
        <div class="col-lg-6">
          <div class="stats-item d-flex align-items-center"><span data-purecounter-start="0" data-purecounter-end="72" data-purecounter-duration="1" class="purecounter">72</span><p><strong>Happy Clients</strong> Delighting customers with our services.</p></div>
          <div class="stats-item d-flex align-items-center"><span data-purecounter-start="0" data-purecounter-end="132" data-purecounter-duration="1" class="purecounter">132</span><p><strong>Projects</strong> Handling and executing projects efficiently.</p></div>
          <div class="stats-item d-flex align-items-center"><span data-purecounter-start="0" data-purecounter-end="280" data-purecounter-duration="1" class="purecounter">280</span><p><strong>Hours Of Support</strong> Providing dedicated support whenever needed.</p></div>
        </div>
      </div>
    </div>
  </section>

  <!-- ======= Call to action ======= -->
  <section id="call-to-action" class="call-to-action">
    <div class="container text-center" data-aos="zoom-out">
      <canvas class="fx-circuit" aria-hidden="true"></canvas>
      <h3>Call to book</h3>
      <p>Don't wait to elevate your research and development capabilities. Contact us today to learn more about our offerings and how we can tailor our solutions to meet your specific needs. Our dedicated team is ready to assist you with any questions and guide you through the booking process.</p>
      <a class="cta-btn" href="tel:{S['phone_tel']}"><i class="bi bi-telephone-fill"></i> Call us now</a>
    </div>
  </section>

  <!-- ======= Services ======= -->
  <section id="services" class="services sections-bg">
    <div class="container" data-aos="fade-up">
      <div class="section-header">
        <h2>Our Services</h2>
        <p>At SATs, we are committed to providing comprehensive and innovative solutions for semiconductor analysis and testing. Our range of services and products is designed to meet the diverse needs of researchers and developers in the semiconductor industry. Here’s what we offer:</p>
      </div>
      <div class="row gy-4">{svc}</div>
    </div>
  </section>

  <!-- ======= Testimonials ======= -->
  <section id="testimonials" class="testimonials">
    <div class="container" data-aos="fade-up">
      <div class="section-header">
        <h2>Testimonials</h2>
        <p>Our commitment to excellence in semiconductor analysis and testing solutions has earned us the trust and satisfaction of numerous esteemed clients. Here’s what some of them have to say about their experience with SATs</p>
      </div>
      <div class="slides-3 swiper"><div class="swiper-wrapper">{testi}</div><div class="swiper-pagination"></div></div>
    </div>
  </section>

  <!-- ======= Products ======= -->
  <section id="portfolio" class="portfolio sections-bg">
    <div class="container container-wide" data-aos="fade-up">
      <div class="section-header">
        <h2>Products</h2>
        <p>Explore our range of semiconductor testing instruments, lab equipment and research services.</p>
      </div>
      <div class="portfolio-isotope" data-portfolio-filter="*" data-portfolio-layout="fitRows" data-portfolio-sort="original-order">
        <div class="product-tools">
          <label class="pd-search product-search"><i class="bi bi-search" aria-hidden="true"></i><input id="product-q" type="search" placeholder="Search products – e.g. cryogenic, vacuum, potentiostat…" aria-label="Search products" autocomplete="off"></label>
          <span class="pd-count" id="product-count" aria-live="polite">{len(grid_products)} products</span>
        </div>
        <ul class="portfolio-flters" aria-label="Filter products">{flt}</ul>
        <p class="pd-empty" id="product-empty" hidden>No product matches your search. <button type="button" id="product-reset" class="btn-link-sats">Show all products</button></p>
        <div class="row gy-4 portfolio-container">{cards}</div>
      </div>
    </div>
  </section>

  <!-- ======= Pricing ======= -->
  <section id="pricing" class="pricing">
    <div class="container" data-aos="fade-up">
      <div class="section-header">
        <h2>Pricing</h2>
        <p>Choose our semiconductor testing for top-notch precision and reliability at the lowest industry rates. 👌</p>
      </div>
      <div class="row g-4 py-lg-4">{pricing}</div>
    </div>
  </section>

  <!-- ======= FAQ ======= -->
  <section id="faq" class="faq sections-bg">
    <div class="container" data-aos="fade-up">
      <div class="row gy-4">
        <div class="col-lg-4">
          <div class="content px-xl-5">
            <h3>Frequently Asked <strong>Questions</strong></h3>
            <p>Here, we address some of the most common questions our clients have about our products, services, and company. Whether you are a new customer looking to learn more about what we offer or a long-time partner seeking additional information, you'll find valuable insights below. If you don't see the answer to your question, please don't hesitate to contact us directly.</p>
          </div>
        </div>
        <div class="col-lg-8"><div class="accordion accordion-flush" id="faqlist">{faq}</div></div>
      </div>
    </div>
  </section>

  <!-- ======= LinkedIn ======= -->
  <section id="linkedin" class="linkedin">
    <div class="container" data-aos="fade-up">
      <div class="section-header">
        <h2>Follow SATs on LinkedIn</h2>
        <p>Updates from the SATs team, straight from our LinkedIn page.</p>
      </div>
      <div class="row gy-4 align-items-stretch li-row no-posts">
        <div class="col-lg-4 li-card-col">
          <div class="li-card">
            <span class="li-badge" aria-hidden="true"><i class="bi bi-linkedin"></i></span>
            <h3>Semiconductor Analysis and Testing Solutions (SATs)</h3>
            <p>Follow our page for the latest from our team of researchers and engineers.</p>
            <a class="btn-sats btn-sats-primary" href="{LI_PROFILE}" target="_blank" rel="noopener noreferrer"><i class="bi bi-linkedin"></i> Follow on LinkedIn</a>
          </div>
        </div>
        <div class="col-lg-8 li-posts" id="linkedin-posts" hidden><div id="linkedin-feed"></div></div>
      </div>
    </div>
  </section>

  <!-- ======= Crafted with love ======= -->
  <section class="crafted" aria-label="About this website">
    <div class="container text-center" data-aos="zoom-in">
      <p class="crafted-line">Crafted with <span class="heart" aria-hidden="true">❤</span> love in Gandhinagar, India</p>
      <p class="crafted-sub">SATs – Instruments made by researchers, for researchers.</p>
    </div>
  </section>

  <!-- ======= Contact ======= -->
  <section id="contact" class="contact">
    <div class="container" data-aos="fade-up">
      <div class="section-header">
        <h2>Contact</h2>
        <p>All the challenges are our hobby, and we're always thrilled to serve our community.</p>
      </div>
      <div class="row gx-lg-0 gy-4">
        <div class="col-lg-4">
          <div class="info-container">
            <div class="info-item d-flex"><i class="bi bi-geo-alt flex-shrink-0"></i><div><h3 class="ih">Location:</h3><p>{addr}<br><a href="{maps}" target="_blank" rel="noopener noreferrer">Open in Google Maps</a></p></div></div>
            <div class="info-item d-flex"><i class="bi bi-envelope flex-shrink-0"></i><div><h3 class="ih">Email:</h3><p><a href="mailto:{S['email']}">{S['email']}</a></p></div></div>
            <div class="info-item d-flex"><i class="bi bi-phone flex-shrink-0"></i><div><h3 class="ih">Call:</h3><p><a href="tel:{S['phone_tel']}">{S['phone_display']}</a></p></div></div>
            <div class="info-item d-flex"><i class="bi bi-clock flex-shrink-0"></i><div><h3 class="ih">Open Hours:</h3><p>{S['hours']}</p></div></div>
          </div>
        </div>
        <div class="col-lg-8">
          <div class="form-frame"><iframe src="{S['contact_form']}" title="SATs enquiry form" loading="lazy" frameborder="0" marginheight="0" marginwidth="0">Loading…</iframe></div>
        </div>
      </div>
    </div>
  </section>
  </main>
"""
    page += footer(True) + scripts(True)
    open('index.html', 'w', encoding='utf-8').write(page)


def build_404():
    page = head('Page not found | SATs', 'The page you are looking for could not be found. Return to the SATs home page.', '404.html', noindex=True)
    page += header(False)
    page += """
  <main id="main">
    <section class="error-page">
      <div class="container">
        <div class="code">4<span>0</span>4</div>
        <h1 class="h3 mb-3">We couldn't find that page</h1>
        <p class="text-muted mb-4">The link may be old or mistyped. Try the home page or browse our products.</p>
        <a class="btn-sats btn-sats-primary" href="index.html"><i class="bi bi-house"></i> Back to home</a>
        <a class="btn-sats btn-sats-outline ms-2" href="index.html#portfolio"><i class="bi bi-grid"></i> View products</a>
      </div>
    </section>
  </main>
"""
    page += footer(False) + scripts(False)
    open('404.html', 'w', encoding='utf-8').write(page)


def build_seo_files():
    urls = [('', '1.0')] + [(p['file'], '0.8') for p in PRODUCTS if not p.get('canonical_of')]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u, pr in urls:
        xml += f'  <url><loc>{esc(abs_url(href(u)) if u else abs_url())}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>\n'
    xml += '</urlset>\n'
    open('sitemap.xml', 'w', encoding='utf-8').write(xml)
    open('robots.txt', 'w', encoding='utf-8').write(
        f"User-agent: *\nAllow: /\nDisallow: /_archive/\nDisallow: /_tools/\n\nSitemap: {abs_url('sitemap.xml')}\n")


def archive():
    os.makedirs('_archive', exist_ok=True)
    moved = []
    for f in ARCHIVE:
        if os.path.exists(f):
            shutil.move(f, os.path.join('_archive', f)); moved.append(f)
    open('_archive/README.txt', 'w', encoding='utf-8').write(
        "Pages moved out of the live site on %s.\nThey were unused template demos (lorem ipsum) or old backups; nothing linked to them.\n"
        "Move a file back to the site root to restore it. The _archive folder is excluded from deployment and from search engines.\n" % TODAY)
    return moved


if __name__ == '__main__':
    moved = archive()
    build_index()
    for p in PRODUCTS:
        build_product(p)
    build_data()
    build_404()
    build_seo_files()
    print('archived:', moved)
    print('built index + %d product pages + 404 + sitemap + robots' % len(PRODUCTS))
    for k, v in DROPPED.items():
        print('  removed copy-pasted probe-station specs from', k, '->', v)
