# NestIQ Video #1 graphics: flat, top-down, dark grey sheet, orange parts.
# Each draw_gN(t, dur, cues) returns a 1080x960 RGB PIL image for local time t.
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

W, H = 1080, 960
SS = 2                                  # supersample for smooth edges
BG = (24, 24, 26)
SHEET = (0x3A, 0x3A, 0x3A)
ORANGE = (0xF9, 0x73, 0x16)
ORANGE_EDGE = (0xC2, 0x55, 0x0C)
RED = (0xEF, 0x44, 0x44)
GREEN = (0x22, 0xC5, 0x5E)
U = 35                                  # px per sheet unit
SX, SY = 85, 300                        # sheet top-left
SW, SH = 26, 14                         # sheet size in units
FONT = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"

def ease_out(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def ease_io(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def clamp(x, a=0, b=1): return max(a, min(b, x))

# ---- the 8 parts (shapes in units, relative to their own top-left) ----
def rect(w, h): return [[(0, 0), (w, 0), (w, h), (0, h)]]
def L(w, h, t): return [[(0, 0), (t, 0), (t, h - t), (w, h - t), (w, h), (0, h)]]
def L180(w, h, t): return [[(0, 0), (w, 0), (w, h), (w - t, h), (w - t, t), (0, t)]]
FRAME_HOLE = (1.8, 1.8, 6.4, 2.4)       # x, y, w, h of the hole inside the frame
PARTS = {
    "frame": rect(10, 6),
    "sq1": rect(1.9, 1.9), "sq2": rect(1.9, 1.9), "sq3": rect(1.9, 1.9),
    "L1": L(8.5, 7.2, 3.4), "L2": L180(8.5, 7.2, 3.4),
    "rA": rect(5.9, 4.5), "rB": rect(3.8, 8.7),
}
MESSY = {"frame": (0.6, 0.4), "rA": (12.0, 0.6), "rB": (21.7, 0.5), "L1": (13.0, 6.4),
         "L2": (2.6, 6.8), "sq1": (18.6, 1.5), "sq2": (23.0, 10.6), "sq3": (0.4, 8.0)}
MESSY_ROT = {"frame": -2, "rA": 4, "rB": -3, "L1": 2, "L2": -3, "sq1": 9, "sq2": -7, "sq3": 6}
hx, hy, hw, hh = FRAME_HOLE
PACKED = {"frame": (0.3, 0.3), "rA": (10.5, 0.3), "rB": (12.6, 5.0), "L1": (0.3, 6.5),
          "L2": (3.9, 6.5),
          "sq1": (0.3 + hx + 0.2, 0.3 + hy + 0.25), "sq2": (0.3 + hx + 2.25, 0.3 + hy + 0.25),
          "sq3": (0.3 + hx + 4.3, 0.3 + hy + 0.25)}
PACKED_RIGHT = 16.6                     # the saved strip starts here (units)
DROP_ORDER = ["frame", "rA", "L1", "sq1", "rB", "sq2", "L2", "sq3"]

def u2p(x, y): return ((SX + x * U) * SS, (SY + y * U) * SS)

def poly_px(name, pos, rot=0, scale=1.0):
    px, py = pos
    out = []
    for ring in PARTS[name]:
        xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        a = math.radians(rot); ca, sa = math.cos(a), math.sin(a)
        pts = []
        for x, y in ring:
            dx, dy = (x - cx) * scale, (y - cy) * scale
            rx, ry = dx * ca - dy * sa, dx * sa + dy * ca
            pts.append(u2p(px + cx + rx, py + cy + ry))
        out.append(pts)
    return out

def draw_part(d, name, pos, rot=0, scale=1.0, alpha=1.0, base=None, fill=ORANGE, hole=None):
    if alpha <= 0: return
    col = tuple(int(b + (c - b) * alpha) for c, b in zip(fill, base or SHEET))
    edge = tuple(int(b + (c - b) * alpha) for c, b in zip(ORANGE_EDGE, base or SHEET))
    for pts in poly_px(name, pos, rot, scale):
        d.polygon(pts, fill=col, outline=edge, width=2 * SS)
    if name == "frame":                  # punch the hole, transformed like the part itself
        w, h = 10, 6; a = math.radians(rot); ca, sa = math.cos(a), math.sin(a)
        pts = []
        for x, y in [(hx, hy), (hx + hw, hy), (hx + hw, hy + hh), (hx, hy + hh)]:
            dx, dy = (x - w / 2) * scale, (y - h / 2) * scale
            pts.append(u2p(pos[0] + w / 2 + dx * ca - dy * sa, pos[1] + h / 2 + dx * sa + dy * ca))
        d.polygon(pts, fill=hole or SHEET, outline=edge, width=2 * SS)

def canvas():
    im = Image.new("RGB", (W * SS, H * SS), BG)
    return im, ImageDraw.Draw(im)

def draw_sheet(d, alpha=1.0, k=1.0):
    col = tuple(int(BG[i] + (SHEET[i] - BG[i]) * alpha) for i in range(3))
    x0, y0 = u2p(0, 0); x1, y1 = u2p(SW, SH)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    x0, x1 = cx + (x0 - cx) * k, cx + (x1 - cx) * k; y0, y1 = cy + (y0 - cy) * k, cy + (y1 - cy) * k
    d.rounded_rectangle([x0, y0, x1, y1], radius=6 * SS, fill=col)

def finish(im): return im.resize((W, H), Image.LANCZOS)

def label(im, text, cx, cy, size=64, box=(255, 255, 255), fg=(0, 0, 0), alpha=1.0):
    f = ImageFont.truetype(FONT, size * SS)
    d = ImageDraw.Draw(im)
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    pw, ph = 30 * SS, 18 * SS
    w, h = r - l + 2 * pw, b - t + 2 * ph
    x, y = cx * SS - w / 2, cy * SS - h / 2
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    a = int(255 * alpha)
    ld.rounded_rectangle([x, y, x + w, y + h], radius=14 * SS, fill=box + (a,))
    ld.text((x + pw - l, y + ph - t), text, font=f, fill=fg + (a,))
    im.paste(layer, (0, 0), layer)

def clock(im, cx, cy, r, turn, alpha):
    if alpha <= 0: return
    d = ImageDraw.Draw(im)
    cx, cy, r = cx * SS, cy * SS, r * SS
    w = tuple(int(BG[i] + (235 - BG[i]) * alpha) for i in range(3))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=w, width=5 * SS)
    for k in range(12):
        a = k * math.pi / 6; d.line([cx + .78 * r * math.sin(a), cy - .78 * r * math.cos(a),
                                     cx + .9 * r * math.sin(a), cy - .9 * r * math.cos(a)], fill=w, width=2 * SS)
    a = turn * 2 * math.pi                      # minute hand spins once
    d.line([cx, cy, cx + .72 * r * math.sin(a), cy - .72 * r * math.cos(a)], fill=w, width=5 * SS)
    a2 = turn * 2 * math.pi / 12 + math.radians(90)
    oc = tuple(int(BG[i] + (ORANGE[i] - BG[i]) * alpha) for i in range(3))
    d.line([cx, cy, cx + .48 * r * math.sin(a2), cy - .48 * r * math.cos(a2)], fill=oc, width=6 * SS)
    d.ellipse([cx - 6 * SS, cy - 6 * SS, cx + 6 * SS, cy + 6 * SS], fill=w)

# ---------------- GRAPHIC 1: messy ----------------
def draw_g1(t, cues):
    """cues: drops = list of 8 local times a part lands; hours = local time of 'hours'."""
    im, d = canvas()
    a = ease_out(t / 0.35); draw_sheet(d, a, 0.96 + 0.04 * a)
    for name, tl in zip(DROP_ORDER, cues["drops"]):
        p = clamp((t - (tl - 0.28)) / 0.28)          # 0.28 s fall, lands at tl
        if p <= 0: continue
        e = 1 - (1 - p) ** 2
        sc = 1.18 - 0.18 * e
        if p >= 1:                                   # tiny settle after landing
            q = clamp((t - tl) / 0.18); sc = 1 + 0.025 * math.sin(q * math.pi) * (1 - q)
        draw_part(d, name, MESSY[name], MESSY_ROT[name], sc, alpha=clamp(p * 1.6))
    th = cues["hours"]
    ca = clamp((t - (th - 0.6)) / 0.3)
    clock(im, 980, 250, 38, ease_io((t - th) / 0.9), ca)
    return finish(im)

# ---------------- GRAPHIC 2: waste ----------------
def draw_g2(t, cues):
    """cues: fade = when parts start fading, glow = red glow start, text = 'This is scrap.' time."""
    im, d = canvas(); draw_sheet(d)
    fa = 1 - ease_io((t - cues["fade"]) / 0.5)
    glow = ease_io((t - cues["glow"]) / 0.5)
    if glow > 0:   # gaps = sheet minus parts, glowing red
        mask = Image.new("L", im.size, 0); md = ImageDraw.Draw(mask)
        x0, y0 = u2p(0, 0); x1, y1 = u2p(SW, SH); md.rounded_rectangle([x0, y0, x1, y1], radius=6 * SS, fill=255)
        for n in PARTS:
            for pts in poly_px(n, MESSY[n], MESSY_ROT[n]): md.polygon(pts, fill=0)
            if n == "frame":
                x, y = MESSY[n]; a, b = u2p(x + hx, y + hy); c, e = u2p(x + hx + hw, y + hy + hh)
                md.rectangle([a, b, c, e], fill=255)
        pulse = 0.85 + 0.15 * math.sin(max(0, t - cues["glow"]) * 4.0)
        red = Image.new("RGB", im.size, RED)
        soft = mask.filter(ImageFilter.GaussianBlur(10 * SS)).point(lambda v: int(v * 0.45 * glow))
        im.paste(red, (0, 0), soft)
        im.paste(red, (0, 0), mask.point(lambda v: int(v * 0.55 * glow * pulse)))
        d = ImageDraw.Draw(im)
    for n in PARTS:   # parts fade out to an outline ghost
        draw_part(d, n, MESSY[n], MESSY_ROT[n], alpha=fa)
        if fa < 1:
            for pts in poly_px(n, MESSY[n], MESSY_ROT[n]):
                d.line(pts + [pts[0]], fill=(90, 90, 90), width=2 * SS)
    ta = ease_out((t - cues["text"]) / 0.25)
    if ta > 0: label(im, "This is scrap.", W / 2, SY + SH * U / 2, size=66, alpha=ta)
    return finish(im)

# ---------------- GRAPHIC 3: packed ----------------
def draw_g3(t, cues):
    """cues: slide (parts slide in), squares = 3 drop times (slow-mo), strip = green highlight."""
    im, d = canvas(); draw_sheet(d)
    big = [n for n in DROP_ORDER if not n.startswith("sq")]
    for i, n in enumerate(big):                      # big parts slide in tight, staggered
        p = ease_out((t - cues["slide"] - i * 0.08) / 0.45)
        if p <= 0: continue
        mx, my = MESSY[n]; px, py = PACKED[n]
        pos = (mx + (px - mx) * p, my + (py - my) * p)
        draw_part(d, n, pos, MESSY_ROT[n] * (1 - p), alpha=clamp(p * 3))
    for n, ts in zip(["sq1", "sq2", "sq3"], cues["squares"]):
        dur = 0.75                                    # slow-motion drop into the hole
        p = (t - ts) / dur
        if p < -0.6: continue
        px, py = PACKED[n]
        if p < 0:   # hovering above the hole, waiting
            draw_part(d, n, (px, py - 3.2), 0, 1.25, alpha=clamp((p + 0.6) / 0.3))
            continue
        e = ease_io(p)
        sc = 1.25 - 0.25 * e
        if p >= 1: q = clamp((t - ts - dur) / 0.2); sc = 1 - 0.04 * math.sin(q * math.pi)
        draw_part(d, n, (px, py - 3.2 * (1 - e)), 0, sc)
    g = ease_io((t - cues["strip"]) / 0.5)
    if g > 0:
        x0, y0 = u2p(PACKED_RIGHT, 0); x1, y1 = u2p(SW, SH)
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
        ld.rounded_rectangle([x0 + 6 * SS, y0 + 6 * SS, x1 - 6 * SS, y1 - 6 * SS], radius=8 * SS,
                             fill=GREEN + (int(110 * g),), outline=GREEN + (int(255 * g),), width=4 * SS)
        im.paste(layer, (0, 0), layer)
        f = ImageFont.truetype(FONT, 40 * SS); d = ImageDraw.Draw(im)
        cx = (x0 + x1) / 2; cy = (y0 + y1) / 2
        for k, line in enumerate(["saved", "material"]):
            l, tt, r, b = d.textbbox((0, 0), line, font=f)
            d.text((cx - (r - l) / 2 - l, cy - 50 * SS + k * 56 * SS - tt), line, font=f,
                   fill=tuple(int(255 * g + 30 * (1 - g)) for _ in range(3)))
    return finish(im)
