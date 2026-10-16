"""Crop the article screenshots into top cards: drop the nav bar, keep masthead + headline + byline (+ photo)."""
import os
from PIL import Image
H = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(H, '..', 'hf', 'assets')

def stack(src, boxes, bg, dst):
    im = Image.open(os.path.join(H, src)).convert('RGB')
    parts = [im.crop(b) for b in boxes]
    w = max(p.width for p in parts)
    card = Image.new('RGB', (w, sum(p.height for p in parts)), bg)
    y = 0
    for p in parts:
        card.paste(p, ((w - p.width) // 2, y)); y += p.height
    card = card.resize((960, round(card.height * 960 / w)), Image.LANCZOS)
    card.save(os.path.join(OUT, dst)); print(dst, card.size)

# Hagerty: masthead row, then section + headline + byline/date (nav bar removed)
stack('hagerty.png', [(0, 0, 1092, 78), (0, 222, 1092, 512)], (255, 255, 255), 'art_hagerty.png')
# Electrek: headline + byline, then the photo (site's cyan frame line trimmed off) down to the parked cars
stack('electrek.png', [(0, 0, 1033, 182), (50, 205, 1010, 690)], (0, 0, 0), 'art_electrek.png')
