# Renders the graphics layer (hook, subtitles, QR card, end card) as raw RGBA frames to stdout.
import json, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode

S = sys.argv[1]
W, H, FPS, DUR = 1080, 1920, 30, 58.0
FB = "/usr/share/fonts/truetype/inter/Inter-ExtraBold.ttf"
import glob
def font(style, size):
    c = glob.glob(f"/usr/share/fonts/**/Inter*{style}*.[to]tf", recursive=True) + glob.glob(f"/usr/**/Inter*{style}*.[to]tf", recursive=True)
    return ImageFont.truetype(sorted(c, key=len)[0], size)
F_SUB = font("ExtraBold", 66); F_HOOK = font("Black", 76); F_SMALL = font("SemiBold", 34)
F_ROW_K = font("Medium", 34); F_ROW_V = font("Bold", 38); F_CARD_T = font("Bold", 40)
F_WORD = font("Bold", 92); F_TAG = font("SemiBold", 44)
YELLOW = (255, 216, 77, 255); WHITE = (255, 255, 255, 255); PURPLE = (153, 110, 255, 255)

def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def back(x):
    x = min(max(x, 0), 1); c = 1.70158; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# ---------- subtitles ----------
words = json.load(open(f"{S}/vo_words.json"))
for w in words: w["w"] = w["w"].strip()
for w in words:
    if w["w"] == "question": w["w"] = "questions"     # VO says "question"; subtitle corrected
KEY = {"prove", "300", "brown", "doors", "slightly", "different.", "every", "batch.", "QR", "code",
       "proof", "nothing", "recorded", "WPC"}
chunks, cur = [], []
for i, w in enumerate(words):
    if w["w"].startswith("Thank"): break
    cur.append(w)
    gap = words[i + 1]["s"] - w["e"] if i + 1 < len(words) else 9
    if len(cur) >= 3 or w["w"][-1] in ".,?" or gap > 0.3:
        chunks.append(cur); cur = []
if cur: chunks.append(cur)
for j, c in enumerate(chunks):
    c0, c1 = c[0]["s"], c[-1]["e"]
    nxt = chunks[j + 1][0]["s"] if j + 1 < len(chunks) else 54.3
    chunks[j] = (c0, min(max(c1 + 0.25, c0 + 0.7), nxt), c)

def draw_sub(img, t):
    d = ImageDraw.Draw(img)
    for s, e, c in chunks:
        if s <= t < e:
            p = ease((t - s) / 0.12)
            parts = [(w["w"], YELLOW if w["w"].lower().strip("?,.") in {k.lower().strip("?,.") for k in KEY} else WHITE) for w in c]
            sizes = [d.textlength(x + " ", font=F_SUB) for x, _ in parts]
            x = (W - sum(sizes) + d.textlength(" ", font=F_SUB)) / 2
            y = 1330 + (1 - p) * 20
            for (txt, col), sw in zip(parts, sizes):
                col = col[:3] + (int(255 * p),)
                d.text((x, y), txt, font=F_SUB, fill=col, stroke_width=7, stroke_fill=(0, 0, 0, int(230 * p)))
                x += sw
            return

# ---------- hook ----------
def draw_hook(img, t):
    return  # hook text removed at user request
    if t >= 4.4: return
    a = 1.0 if t < 4.1 else 1 - (t - 4.1) / 0.3
    d = ImageDraw.Draw(img)
    lines = ["“This is not", "what I ordered.”"]
    y = 300
    for ln in lines:
        tw = d.textlength(ln, font=F_HOOK)
        d.rounded_rectangle((W / 2 - tw / 2 - 30, y - 12, W / 2 + tw / 2 + 30, y + 98), 22, fill=(255, 255, 255, int(240 * a)))
        d.text((W / 2 - tw / 2, y), ln, font=F_HOOK, fill=(20, 18, 40, int(255 * a)))
        y += 122

# ---------- QR card ----------
qr = qrcode.QRCode(border=1, box_size=10); qr.add_data("ALFASTACK|DOOR|BATCH-B0417|DEMO"); qr.make()
QR = qr.make_image(fill_color=(20, 18, 46), back_color="white").convert("RGBA").resize((330, 330), Image.NEAREST)
ROWS = [("Batch", "B-0417", 47.50), ("Materials", "PVC resin · wood flour · additives", 48.44),
        ("Date", "14 Sep 2026", 49.26), ("Machine", "Extrusion line 2", 49.88)]
T_IN, T_OUT = 46.10, 50.45
def draw_qr(img, t):
    if not (T_IN - 0.05 <= t < T_OUT + 0.3): return
    p = back((t - T_IN) / 0.35); out = ease((t - T_OUT) / 0.3) if t > T_OUT else 0
    card = Image.new("RGBA", (860, 900), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, 859, 899), 44, fill=(255, 255, 255, 245))
    d.text((48, 40), "Door #0287", font=F_CARD_T, fill=(20, 18, 46, 255))
    d.rounded_rectangle((612, 40, 812, 92), 26, fill=PURPLE)
    d.text((712, 66), "VERIFIED", font=F_SMALL, fill=WHITE, anchor="mm")
    card.alpha_composite(QR, (265, 120))
    y = 480
    for k, v, ts in ROWS:
        q = ease((t - ts) / 0.25)
        if q <= 0: y += 100; continue
        dx = int((1 - q) * 40)
        d.text((48 + dx, y), k.upper(), font=F_ROW_K, fill=(120, 116, 150, int(255 * q)))
        d.text((48 + dx, y + 40), v, font=F_ROW_V, fill=(20, 18, 46, int(255 * q)))
        y += 100
    sc = max(0.01, p * (1 - 0.15 * out))
    cw, ch = int(860 * sc), int(900 * sc)
    c2 = card.resize((cw, ch), Image.LANCZOS)
    if out: c2.putalpha(c2.getchannel("A").point(lambda a: int(a * (1 - out))))
    sh = Image.new("RGBA", (cw + 80, ch + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, 50, cw + 40, ch + 50), 44, fill=(0, 0, 0, int(110 * (1 - out))))
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    cx, cy = W // 2, 250 + 450
    img.alpha_composite(sh, (cx - cw // 2 - 40, cy - ch // 2 - 40))
    img.alpha_composite(c2, (cx - cw // 2, cy - ch // 2))

# ---------- "PROOF" stamp ----------
def draw_proof(img, t):
    if not (53.26 <= t < 54.4): return
    p = back((t - 53.26) / 0.3); d = ImageDraw.Draw(img)
    txt = "PROOF ✓" ; f = font("Black", int(110 * max(p, .01)))
    tw = d.textlength(txt, font=f)
    d.rounded_rectangle((W / 2 - tw / 2 - 40, 420, W / 2 + tw / 2 + 40, 420 + 150 * max(p, .01)), 30, fill=PURPLE)
    d.text((W / 2, 420 + 75 * p), txt, font=f, fill=WHITE, anchor="mm")

# ---------- end card ----------
LOGO = Image.open(f"{S}/logo.png").convert("RGBA")
def draw_end(img, t):
    t0 = 54.4
    if t < t0: return
    d = ImageDraw.Draw(img)
    p = back((t - t0 - 0.1) / 0.5)
    s = max(0.01, 0.62 * p)
    lg = LOGO.resize((int(560 * s), int(550 * s)), Image.LANCZOS)
    img.alpha_composite(lg, (W // 2 - lg.width // 2, 640 - lg.height // 2))
    q = ease((t - t0 - 0.45) / 0.4)
    d.text((W / 2, 900 + (1 - q) * 20), "Alfastack", font=F_WORD, fill=(192, 192, 192, int(255 * q)), anchor="mm")
    q2 = ease((t - t0 - 0.9) / 0.4)
    d.text((W / 2, 1040), "Every door. Every batch.", font=F_TAG, fill=(255, 255, 255, int(255 * q2)), anchor="mm")
    d.text((W / 2, 1105), "On record.", font=F_TAG, fill=PURPLE[:3] + (int(255 * q2),), anchor="mm")

out = sys.stdout.buffer
only = [float(x) for x in sys.argv[2:]]
for i in range(int(DUR * FPS)) if not only else [int(x * FPS) for x in only]:
    t = i / FPS
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_hook(img, t); draw_qr(img, t); draw_proof(img, t); draw_end(img, t); draw_sub(img, t)
    if only: img.save(f"{S}/ov_{t:05.2f}.png")
    else: out.write(img.tobytes())
