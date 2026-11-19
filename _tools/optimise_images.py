#!/usr/bin/env python3
"""Create web-sized WebP copies of every image the site uses (originals are never touched)."""
import os, re, sys, json
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from registry import PRODUCTS, CLIENTS, TESTIMONIALS
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); os.chdir(ROOT)
OUT = 'assets/img/web'
os.makedirs(OUT + '/clients', exist_ok=True); os.makedirs(OUT + '/testimonials', exist_ok=True)
manifest = {}

def save_webp(src, dst, max_w, q=82):
    im = Image.open(src)
    im.load()
    has_alpha = im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info)
    im = im.convert('RGBA' if has_alpha else 'RGB')
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    im.save(dst, 'WEBP', quality=q, method=6)
    return im.width, im.height, os.path.getsize(dst)

before = after = 0
for p in PRODUCTS:
    if p.get('canonical_of'):
        key_for = 'low-temp-probe-station'
    else:
        key_for = p['key']
    for i, src in enumerate(p['imgs']):
        slug = f"{key_for}-{i+1}"
        for tag, w in (('lg', 1400), ('md', 800)):
            dst = f"{OUT}/{slug}-{tag}.webp"
            if os.path.exists(dst): 
                im = Image.open(dst); manifest[f"{src}|{tag}"] = (dst, im.width, im.height); continue
            W, H, size = save_webp(src, dst, w)
            manifest[f"{src}|{tag}"] = (dst, W, H); after += size
        before += os.path.getsize(src)

for fn, alt in CLIENTS:
    src = f"assets/img/clients/{fn}"; dst = f"{OUT}/clients/{os.path.splitext(fn)[0]}.webp"
    W, H, size = save_webp(src, dst, 320, 85); manifest[f"client|{fn}"] = (dst, W, H); before += os.path.getsize(src); after += size
for fn, *_ in TESTIMONIALS:
    src = f"assets/img/testimonials/{fn}"; dst = f"{OUT}/testimonials/{os.path.splitext(fn)[0]}.webp"
    W, H, size = save_webp(src, dst, 160, 85); manifest[f"testimonial|{fn}"] = (dst, W, H); before += os.path.getsize(src); after += size

W, H, size = save_webp('assets/img/cta-bg.jpg', f'{OUT}/cta-bg.webp', 1920, 68); before += os.path.getsize('assets/img/cta-bg.jpg'); after += size

# --- social share image (1200x630 JPEG: WhatsApp/Facebook don't reliably read WebP) and square icons
logo = Image.open('assets/img/final_sats_logi.png').convert('RGB')
bg = (0, 131, 116)
og = Image.new('RGB', (1200, 630), bg)
lh = 440; lw = round(logo.width * lh / logo.height)
og.paste(logo.resize((lw, lh), Image.LANCZOS), ((1200 - lw) // 2, (630 - lh) // 2))
og.save('assets/img/og-sats.jpg', 'JPEG', quality=88, optimize=True)
# square mark: crop the vertical "SATS" letters from the logo
mark = logo.crop((20, 55, 125, 470))
def square(size):
    c = Image.new('RGB', (size, size), bg)
    h = int(size * 0.74); w = round(mark.width * h / mark.height)
    c.paste(mark.resize((w, h), Image.LANCZOS), ((size - w) // 2, (size - h) // 2))
    return c
square(180).save('assets/img/apple-touch-icon-180.png', optimize=True)
square(192).save('assets/img/icon-192.png', optimize=True)
square(32).save('assets/img/favicon-32.png', optimize=True)
json.dump(manifest, open('_tools/image_manifest.json', 'w'), indent=1)
print(f"optimised {len(manifest)} variants; source {before/1e6:.1f} MB -> web {after/1e6:.1f} MB")
