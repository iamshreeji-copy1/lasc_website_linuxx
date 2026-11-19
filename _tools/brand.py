#!/usr/bin/env python3
"""Builds transparent white / teal variants of the official SATs logo (source: SCADA project brand_source)."""
import os
from PIL import Image
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); os.chdir(ROOT)
src = Image.open('assets/img/brand/sats-official-logo.png').convert('RGB')
bg = src.getpixel((3, 3)); print('logo background colour:', '#%02x%02x%02x' % bg)
r = src.split()[0]                       # R channel: 0 on the teal field, 255 on white lettering
alpha = r.point(lambda v: min(255, int(v * 255 / max(1, 255))))
def variant(rgb, name, crop=None, scale=1.0):
    im = Image.new('RGBA', src.size, rgb + (0,)); im.putalpha(alpha)
    if crop: im = im.crop(crop)
    if scale != 1.0: im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    im.save(f'assets/img/brand/{name}.png', optimize=True); print(name, im.size)
variant((255, 255, 255), 'sats-logo-white')
variant(bg, 'sats-logo-teal')
# vertical "SATS" mark + rule (left part of the logo) for the compact header
mark = (14, 8, 140, 519)
variant((255, 255, 255), 'sats-mark-white', mark)
variant(bg, 'sats-mark-teal', mark)
