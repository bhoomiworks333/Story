# NestIQ Video #3 compositor.  usage: python3 compose3.py stills 1 12 ... | python3 compose3.py render out.mp4 mix.wav
import sys, json, math, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont

FPS = 30
P = json.load(open("pieces.json")); PID = {p["id"]: p for p in P}
WORDS = json.load(open("transcripts/cut_words.json"))
DUR = sum(p["frames"] for p in P) / FPS
def w(i): return WORDS[i]["s"]
def pstart(pid): return PID[pid]["start"]
def pend(pid): return PID[pid]["start"] + PID[pid]["frames"] / FPS

BG = (24, 24, 26); CARD = (40, 40, 44); SHEET = (0x3A, 0x3A, 0x3A); ORANGE = (0xF9, 0x73, 0x16)
RED = (0xEF, 0x44, 0x44); WHITE = (255, 255, 255); GREY = (160, 160, 166); BLACK = (0, 0, 0)
FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"; FX = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
def font(sz, f=FB): return ImageFont.truetype(f, sz)
SS = 2
def ease_out(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def ease_io(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def back_out(x):
    x = max(0, min(1, x)); c = 1.6; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def clamp(x, a=0, b=1): return max(a, min(b, x))

# ---------------- timing ----------------
SPLIT1 = (w(34) - 0.05, pend("t2"))              # price cards + subtraction (setup + twist)
SPLIT2 = (pstart("p3"), pend("p6"))              # "it adds up" stack
CUE = dict(sheet=w(35), scrap=w(55), minus=w(56), result=w(65),
           sheet_ev=w(83), day_ev=w(85), adds=w(87))
PUNCH = w(65)                                    # subtle punch-in on "lose"
HOOK_TEXT_END = w(6) - 0.05                      # hook text until he says "scrap toh..."
CTA_FROM = pstart("c1")
NESTIQ_FROM = DUR - 2.0

# ---------------- graphics (top half, 1080x960) ----------------
def rr(d, box, r, fill, outline=None, width=0):
    d.rounded_rectangle([v * SS for v in box], radius=r * SS, fill=fill, outline=outline, width=width * SS)

def text(d, xy, s, f, fill, anchor="la"):
    d.text((xy[0] * SS, xy[1] * SS), s, font=ImageFont.truetype(f.path, f.size * SS), fill=fill, anchor=anchor)

def sheet_icon(d, x, y, a):
    rr(d, (x, y, x + 120, y + 84), 6, SHEET)
    for bx, by, bw, bh in ((8, 8, 44, 30), (60, 8, 24, 66), (8, 46, 44, 28), (90, 10, 22, 22)):
        rr(d, (x + bx, y + by, x + bx + bw, y + by + bh), 3, ORANGE)

def scrap_icon(d, x, y):
    for pts in (((0, 60), (34, 40), (52, 70), (18, 84)), ((44, 20), (86, 8), (96, 44), (60, 52)),
                ((70, 58), (118, 50), (110, 84), (78, 80))):
        d.polygon([((x + px) * SS, (y + py) * SS) for px, py in pts], fill=(0x9C, 0x3A, 0x3A))

def price_card(im, y, label, price, icon, p):
    if p <= 0: return
    x = 90 + (1 - ease_out(p)) * 1000           # slides in from the right
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    rr(d, (x, y, x + 900, y + 200), 22, CARD + (255,))
    (sheet_icon if icon == "sheet" else lambda d, a, b, *_: scrap_icon(d, a, b))(d, x + 40, y + 58, 1)
    text(d, (x + 190, y + 100), label, font(46), GREY, "lm")
    text(d, (x + 860, y + 100), price, font(96, FX), WHITE, "rm")
    im.paste(layer, (0, 0), layer)

def equation(im, t):
    pm = ease_out((t - CUE["minus"]) / 0.3)
    if pm <= 0: return
    d = ImageDraw.Draw(im); f = font(80, FX); y = 640
    left = "₹65 − ₹35 ="
    lw = d.textlength(left, font=ImageFont.truetype(FX, 80 * SS)) / SS
    res = "₹30"; resw = d.textlength(res, font=ImageFont.truetype(FX, 80 * SS)) / SS
    total = lw + 24 + resw + 40; x0 = 540 - total / 2
    col = tuple(int(BG[i] + (WHITE[i] - BG[i]) * pm) for i in range(3))
    text(d, (x0, y + 70), left, f, col, "lm")
    pr = (t - CUE["result"]) / 0.35
    if pr > 0:
        sc = back_out(pr); bx = x0 + lw + 24; cx = bx + (resw + 40) / 2; cy = y + 70
        hw, hh = (resw + 40) / 2 * sc, 62 * sc
        rr(d, (cx - hw, cy - hh, cx + hw, cy + hh), 18, ORANGE)
        if sc > 0.3: text(d, (cx, cy), res, font(int(80 * min(1, sc))), BLACK, "mm")
        la = ease_out((t - CUE["result"] - 0.2) / 0.3)
        if la > 0: text(d, (540, y + 185), "lost on every kilo of scrap", font(40),
                        tuple(int(BG[i] + (GREY[i] - BG[i]) * la) for i in range(3)), "mm")

def g_prices(t):
    im = Image.new("RGB", (1080 * SS, 960 * SS), BG)
    price_card(im, 150, "Sheet", "₹65/kg", "sheet", (t - (CUE["sheet"] - 0.3)) / 0.35)
    price_card(im, 390, "Scrap", "₹35/kg", "scrap", (t - (CUE["scrap"] - 0.3)) / 0.35)
    equation(im, t)
    return im.resize((1080, 960), Image.LANCZOS)

CHIP_W, CHIP_H, COLS, ROWS = 180, 74, 5, 7
def g_adds(t):
    im = Image.new("RGB", (1080 * SS, 960 * SS), BG); d = ImageDraw.Draw(im)
    # chips stack from the bottom: a few on "every sheet", more on "every day", the rest on "adds up"
    n_total = COLS * ROWS
    n = 0
    n += 5 * ease_io((t - CUE["sheet_ev"]) / 0.5)
    n += 15 * ease_io((t - CUE["day_ev"]) / 0.6)
    n += (n_total - 20) * ease_io((t - CUE["adds"]) / 0.7)
    n += 2 * ease_io((t - SPLIT2[0]) / 0.3)
    n = min(n_total, n)
    f = ImageFont.truetype(FX, 40 * SS)
    for k in range(int(math.ceil(n))):
        r, c = divmod(k, COLS)
        a = clamp(n - k)
        x = 540 - (COLS * (CHIP_W + 14) - 14) / 2 + c * (CHIP_W + 14) + (r % 2) * 10 - 5
        y = 860 - (r + 1) * (CHIP_H + 12) - (1 - ease_out(a)) * 60
        col = tuple(int(BG[i] + (ORANGE[i] - BG[i]) * a) for i in range(3))
        rr(d, (x, y, x + CHIP_W, y + CHIP_H), 14, col)
        if a > 0.5: d.text(((x + CHIP_W / 2) * SS, (y + CHIP_H / 2) * SS), "−₹30", font=f, fill=BLACK, anchor="mm")
    return im.resize((1080, 960), Image.LANCZOS)

# ---------------- captions ----------------
CAPS_DEF = [
 (0, "Every factory owner tells me,", None), (6, "“Scrap toh bik jaata hai.”", "Scrap toh bik jaata hai."),
 (11, "But where's the loss?", "loss"),
 (16, "Sheet comes in", None), (19, "by the kilo.", None), (22, "Scrap goes out", None), (25, "by the kilo.", None),
 (28, "Let's assume you buy", None), (32, "that sheet around", None), (35, "65 rupees a kilo.", "65 rupees"),
 (39, "You cut your parts,", None), (43, "and the leftover", None), (46, "you sell as scrap.", None),
 (50, "But scrap sells", None), (53, "for around 35.", "35"), (56, "So for every kilo", None),
 (60, "that goes into scrap,", None), (64, "you lose 30 rupees.", "30 rupees"),
 (68, "It doesn't feel", None), (71, "like a loss.", None), (74, "Because some money", None),
 (77, "still comes back.", None), (80, "But for every sheet,", None), (84, "every day,", None),
 (86, "it adds up.", "adds up"),
 (89, "What do you pay", None), (93, "for sheets,", None), (95, "and what do you get", None),
 (100, "for the scraps?", None), (103, "Tell me in the comments.", "comments"),
]
CAPS = []
for k, (i, txt, kw) in enumerate(CAPS_DEF):
    a = w(i) - 0.03
    if k == 0: a = max(a, pstart("h1"))
    b = (w(CAPS_DEF[k + 1][0]) - 0.03) if k + 1 < len(CAPS_DEF) else DUR
    kwt = 0
    if kw:
        first = kw.split()[0].strip("“”.,?").lower()
        j = next(j for j in range(i, len(WORDS)) if WORDS[j]["w"].lower().strip("“”.,?").startswith(first[:3]))
        kwt = w(j) - 0.03
    CAPS.append(dict(a=a, b=b, txt=txt, kw=kw, kwt=kwt))
F_CAP = font(54)
def caption(im, t, cy):
    cap = next((c for c in CAPS if c["a"] <= t < c["b"]), None)
    if not cap: return
    d = ImageDraw.Draw(im); txt = cap["txt"]; padx, pady = 30, 16
    l, tp, r, b = d.textbbox((0, 0), txt, font=F_CAP)
    wd = r - l + 2 * padx; h = 54 + 2 * pady; x = 540 - wd / 2; y = cy - h / 2
    d.rounded_rectangle([x, y, x + wd, y + h], radius=16, fill=WHITE)
    if cap["kw"] and t >= cap["kwt"]:
        i = txt.index(cap["kw"])
        kx0 = d.textlength(txt[:i], font=F_CAP); kx1 = kx0 + d.textlength(cap["kw"], font=F_CAP)
        d.rounded_rectangle([x + padx + kx0 - 9, y + 7, x + padx + kx1 + 7, y + h - 7], radius=12, fill=ORANGE)
    asc = F_CAP.getmetrics()[0]
    d.text((x + padx - l, y + pady + (54 - asc) / 2 + 2), txt, font=F_CAP, fill=BLACK)

EMOJI = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
def top_box(im, s, cy, emoji=None, size=62):
    d = ImageDraw.Draw(im); f = font(size)
    l, tp, r, b = d.textbbox((0, 0), s, font=f); tw = r - l
    ew = 0
    if emoji:
        e = Image.new("RGBA", (140, 140), (0, 0, 0, 0)); ImageDraw.Draw(e).text((0, 0), emoji, font=EMOJI, embedded_color=True)
        e = e.crop(e.getbbox()).resize((int(size * 1.05), int(size * 1.05)), Image.LANCZOS); ew = e.width + 12
    wd = tw + ew + 68; h = size + 44; x = 540 - wd / 2; y = cy - h / 2
    d.rounded_rectangle([x, y, x + wd, y + h], radius=18, fill=WHITE)
    d.text((x + 34 - l, y + 22 + (size - f.getmetrics()[0]) / 2 + 3), s, font=f, fill=BLACK)
    if emoji: im.paste(e, (int(x + 34 + tw + 12), int(cy - e.height / 2)), e)

def frame_at(t, face):
    face_img = Image.fromarray(face)
    if SPLIT1[0] <= t < SPLIT1[1] or SPLIT2[0] <= t < SPLIT2[1]:
        im = Image.new("RGB", (1080, 1920), BG)
        im.paste(g_prices(t) if t < SPLIT1[1] else g_adds(t), (0, 0))
        win = face_img.crop((0, 156, 1080, 1116))
        z = 1 + 0.08 * ease_out((t - PUNCH) / 0.18) if SPLIT1[0] <= t < SPLIT1[1] else 1
        if z > 1:
            W2, H2 = int(1080 * z), int(960 * z)
            win = win.resize((W2, H2), Image.LANCZOS).crop(((W2 - 1080) // 2, int((H2 - 960) * 0.35),
                                                            (W2 - 1080) // 2 + 1080, int((H2 - 960) * 0.35) + 960))
        im.paste(win, (0, 960)); caption(im, t, 958)
    else:
        im = face_img; caption(im, t, 1470)
    if t < HOOK_TEXT_END: top_box(im, "“Scrap toh bik jaata hai.”", 330)
    if t >= CTA_FROM: top_box(im, "Your sheet rate vs scrap rate?", 410, emoji="👇", size=52)
    if t >= NESTIQ_FROM: ImageDraw.Draw(im).text((64, 236), "NestIQ", font=font(44), fill=WHITE)
    return im

def face_frames():
    for p in P:
        pr = subprocess.Popen(["ffmpeg", "-v", "error", "-i", f"segs/{p['id']}.mp4", "-f", "rawvideo", "-pix_fmt", "rgb24",
                               "-"], stdout=subprocess.PIPE); last = None
        for _ in range(p["frames"]):
            buf = pr.stdout.read(1080 * 1920 * 3)
            if len(buf) == 1080 * 1920 * 3: last = np.frombuffer(buf, np.uint8).reshape(1920, 1080, 3)
            yield last
        pr.stdout.close(); pr.wait()

def piece_at(t):
    return next((p for p in P if p["start"] <= t < p["start"] + p["frames"] / FPS), P[-1])

if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for t in map(float, sys.argv[2:]):
            p = piece_at(t)
            raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t - p['start']:.3f}", "-i", f"segs/{p['id']}.mp4",
                                  "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
            frame_at(t, np.frombuffer(raw, np.uint8).reshape(1920, 1080, 3)).save(f"qa/still_{t:05.2f}.png")
        print("duration %.2f" % DUR, {k: round(v, 2) for k, v in CUE.items()}, "split1", SPLIT1, "split2", SPLIT2)
    else:
        out, audio = sys.argv[2], sys.argv[3]
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920",
              "-r", str(FPS), "-i", "-", "-i", audio, "-c:v", "libx264", "-crf", "18", "-preset", "slow",
              "-pix_fmt", "yuv420p", "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709",
              "-color_trc", "bt709", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
              stdin=subprocess.PIPE)
        for k, fr in enumerate(face_frames()):
            ff.stdin.write(frame_at(k / FPS, fr).tobytes())
        ff.stdin.close(); ff.wait(); print("done", out, "%.2f s" % DUR)
