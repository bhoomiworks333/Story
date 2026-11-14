# Renders the Nvidia reel: python3 build.py [--stills t1,t2,...]
# Inputs: work/cut.mov (from build_cut.py), cut-audio.wav, cut-words.json, assets/, raw/v02_press_scroll.mp4
import json, os, subprocess, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
words = json.load(open("cut-words.json"))
DUR = 34.0; NF = 1020
GRADE = "eq=contrast=1.07:brightness=-0.012:saturation=1.0:gamma=0.98"
F_BOLD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
F_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

def wt(word, after=0.0):
    for w in words:
        if w["s"] >= after - 1e-6 and w["w"].strip(",.?").lower() == word.lower(): return w["s"]
    raise KeyError(word)

# ---------- frames ----------
def extract():
    os.makedirs("face", exist_ok=True)
    if not os.path.exists(f"face/{NF:06d}.jpg"):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "work/cut.mov", "-vf", GRADE, "-q:v", "2", "face/%06d.jpg"], check=True)
    os.makedirs("work/stage", exist_ok=True)
    if not os.path.exists("work/stage/0001.jpg"):
        # drop the 14px browser strip, fill the 1080 width
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "raw/v02_press_scroll.mp4", "-vf",
                        "fps=30,crop=792:704:0:14,scale=1080:960:flags=lanczos", "-q:v", "2", "work/stage/%04d.jpg"], check=True)

def face_full(i):   # static 1.15x crop: less ceiling, head at y~560
    im = Image.open(f"face/{min(i+1, NF):06d}.jpg")
    return im.resize((1242, 2208), Image.LANCZOS).crop((81, 288, 81 + W, 288 + H))

def face_card(i):   # bottom half of split: raw scale, head top ~y1110
    im = Image.open(f"face/{min(i+1, NF):06d}.jpg")
    return im.crop((0, 590, W, 590 + 960))

# ---------- highlight measuring (word-highlight skill) ----------
def ink_words(img, band, xr=None, thr=120, gap=9):
    """Word boxes (x0,y0,x1,y1) of dark ink inside a horizontal band of the image."""
    a = np.asarray(img.convert("L")).astype(int)
    y0, y1 = band; x0, x1 = xr or (0, a.shape[1])
    ink = a[y0:y1, x0:x1] < thr
    cols = ink.any(0); out = []; x = 0
    while x < len(cols):
        if cols[x]:
            s = x; e = x; blank = 0
            while x < len(cols) and blank <= gap:
                if cols[x]: e = x; blank = 0
                else: blank += 1
                x += 1
            rows = np.where(ink[:, s:e + 1].any(1))[0]
            out.append((x0 + s, y0 + rows[0], x0 + e + 1, y0 + rows[-1] + 1))
        else: x += 1
    return out

def span(boxes, i, j):
    b = boxes[i:j]
    return (min(q[0] for q in b) - 3, min(q[1] for q in b) - 5, max(q[2] for q in b) + 3, max(q[3] for q in b) + 5)

# ---------- assets ----------
press = Image.open("assets/01_press_release.png").convert("RGB")
bbc = Image.open("assets/02_bbc_affairs_headline.png").convert("RGB")
chart = Image.open("assets/04_chart_nov13.png").convert("RGB")

PR_RESIGN = span(ink_words(press, (428, 458), (140, 1130)), 0, 3)      # "Jensen Huang Resigns"
PR_KRESS = span(ink_words(press, (459, 490), (140, 1130)), 0, 99)      # Kress bullet, whole line
BBC_L2 = ink_words(bbc, (158, 215), (480, 1400), gap=8)               # "Huang resigns over affair allegations"
BBC_AFF = span(BBC_L2, len(BBC_L2) - 2, len(BBC_L2))

def place(img, crop, width, box):
    """Crop, scale to width; return image, scale, offset of the crop and a mapper for a box in source px."""
    c = img.crop(crop); s = width / c.width
    c = c.resize((width, round(c.height * s)), Image.LANCZOS)
    return c, (lambda b: (round((b[0] - crop[0]) * s), round((b[1] - crop[1]) * s), round((b[2] - crop[0]) * s), round((b[3] - crop[1]) * s)))

def highlighted(img, box, k):
    """Grey everything but box (55% white), 3px blue outline; k = 0..1 fade."""
    if k <= 0: return img
    out = img.copy(); veil = Image.new("RGB", img.size, (255, 255, 255))
    grey = Image.blend(img, veil, 0.55 * k)
    m = Image.new("L", img.size, 255); ImageDraw.Draw(m).rounded_rectangle(box, 6, fill=0)
    out.paste(grey, (0, 0), m)
    d = ImageDraw.Draw(out, "RGBA"); d.rounded_rectangle(box, 6, outline=(0, 113, 227, round(255 * k)), width=3)
    return out

# press release: logo + title + bullets
PR_FULL, PR_MAP = place(press, (100, 0, 780, 882), W, None)
PR_K, PR_KMAP = place(press, (105, 270, 930, 740), W, None)
BBC_IMG, BBC_MAP = place(bbc, (480, 0, 1325, 907), W, None)
CH_IMG, _ = place(chart, (425, 100, 1300, 690), W, None)

# ---------- text ----------
def font(p, s): return ImageFont.truetype(p, s)

def box_text(d, cx, cy, lines, size, pad=(28, 14), gap=8, maxw=None):
    f = font(F_BOLD, size)
    ws = [d.textlength(l, font=f) for l in lines]
    while maxw and max(ws) + 2 * pad[0] > maxw:
        size -= 2; f = font(F_BOLD, size); ws = [d.textlength(l, font=f) for l in lines]
    asc, desc = f.getmetrics(); lh = size * 1.12
    bw = max(ws) + 2 * pad[0]; bh = lh * len(lines) + 2 * pad[1] + gap * (len(lines) - 1)
    x0, y0 = cx - bw / 2, cy - bh / 2
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), 14, fill=(255, 255, 255))
    for k, l in enumerate(lines):
        d.text((cx, y0 + pad[1] + k * (lh + gap) + lh / 2), l, font=f, fill=(0, 0, 0), anchor="mm")
    return (x0, y0, x0 + bw, y0 + bh)

def emoji(ch, h):
    f = ImageFont.truetype(EMOJI, 109); im = Image.new("RGBA", (140, 140)); ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox()); return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)

def label(d, x, y, text, size=34, dark=False):
    f = font(F_SEMI, size); w = d.textlength(text, font=f)
    d.rounded_rectangle((x, y, x + w + 28, y + size + 18), 10, fill=(0, 0, 0, 170) if not dark else (255, 255, 255, 230))
    d.text((x + 14, y + 9 + size / 2), text, font=f, fill=(255, 255, 255) if not dark else (0, 0, 0), anchor="lm")

# ---------- captions: 2-5 words, break on punctuation ----------
def chunks():
    # phrases end on punctuation; a phrase over 5 words splits into even pieces of <=4
    phrases, cur = [], []
    for w in words:
        cur.append(w)
        if w["w"][-1] in ",.?": phrases.append(cur); cur = []
    if cur: phrases.append(cur)
    out = []
    for p in phrases:
        if len(p) <= 5: out.append(p); continue
        n = -(-len(p) // 4); k = len(p) / n
        out += [p[round(i * k):round((i + 1) * k)] for i in range(n)]
    # a lone word joins the next phrase when that stays <=5 words
    merged = []
    for c in out:
        if merged and len(merged[-1]) == 1 and len(merged[-1]) + len(c) <= 5: merged[-1] += c
        else: merged.append(c)
    res = []
    for i, c in enumerate(merged):
        end = merged[i + 1][0]["s"] if i + 1 < len(merged) else DUR
        txt = " ".join(w["w"].strip(",.") for w in c); res.append((c[0]["s"], end, txt[0].upper() + txt[1:]))
    return res
CAPS = chunks()

# ---------- timeline ----------
T_THE = wt("the") - 0.03
T_GONE = wt("gone") - 0.03
T_ITS = wt("It's") - 0.03
T_BBC = wt("Jobs") + 0.50          # end of "Jobs", into the silent beat
T_ONE = wt("One") - 0.03
T_CFO = wt("The", 23) - 0.03
T_AND = wt("and", 26) - 0.03
T_WITHOUT = wt("without") - 0.03
T_SO = wt("So") - 0.03
HOOK_END = T_THE

BEATS = [  # (start, end, layout, visual)
    (0, T_THE, "face", None),
    (T_THE, T_GONE, "split", "stage1"),
    (T_GONE, T_ITS, "full", "press"),
    (T_ITS, T_BBC, "face", None),
    (T_BBC, T_ONE, "full", "bbc"),
    (T_ONE, T_CFO, "face", None),
    (T_CFO, T_AND, "split", "kress"),
    (T_AND, T_WITHOUT, "split", "chart"),
    (T_WITHOUT, T_SO, "split", "stage2"),
    (T_SO, DUR + 1, "face", "cta"),
]
STAGE1_IN, STAGE2_IN = 30, 150     # clip frame where each run starts (one continuous run each, in source order)

def visual(v, t, t0):
    if v in ("stage1", "stage2"):
        n = (STAGE1_IN if v == "stage1" else STAGE2_IN) + round((t - t0) * FPS)
        n = min(n, len(os.listdir("work/stage")))
        return Image.open(f"work/stage/{n:04d}.jpg").convert("RGB"), (0, 0, 0)
    if v == "kress":
        k = min(1, max(0, (t - (wt("CFO") - 0.0)) / 0.15))
        return highlighted(PR_K, PR_KMAP(PR_KRESS), k), (255, 255, 255)
    if v == "chart":
        return CH_IMG, (23, 24, 31)

def frame(i):
    t = i / FPS
    b = next(x for x in BEATS if x[0] <= t < x[1])
    lay, v = b[2], b[3]
    if lay == "face":
        im = face_full(i)
    elif lay == "split":
        im = Image.new("RGB", (W, H)); vis, bg = visual(v, t, b[0])
        panel = Image.new("RGB", (W, 960), bg); panel.paste(vis, (0, (960 - vis.height) // 2)); im.paste(panel, (0, 0))
        im.paste(face_card(i), (0, 960))
    else:
        im = Image.new("RGB", (W, H), (255, 255, 255))
        if v == "press":
            k = min(1, max(0, (t - wt("gone")) / 0.15)); img = highlighted(PR_FULL, PR_MAP(PR_RESIGN), k); y = 240
        else:
            k = min(1, max(0, (t - wt("reason")) / 0.15)); img = highlighted(BBC_IMG, BBC_MAP(BBC_AFF), k); y = 300
        im.paste(img, (0, y))
    d = ImageDraw.Draw(im, "RGBA")
    if v == "kress": label(d, 40, 840, "Interim CEO: Colette Kress", 40, dark=True)
    if v == "chart":
        label(d, 660, 845, "Source: Google Finance", 26)
        label(d, 40, 840, "Q3 results: Tue, Nov 17", 40, dark=True)
    if t < HOOK_END:
        box_text(d, 540, 360, ["Jensen Huang", "is out at Nvidia"], 86, maxw=900)
    if v == "cta":
        bx = box_text(d, 540 - 50, 380, ["Who replaces him?"], 76, maxw=820)
        e = emoji("👇", 84); im.paste(e, (round(bx[2]) + 16, 380 - 42), e)
    elif lay != "full" and t >= HOOK_END:
        c = next((c for c in CAPS if c[0] <= t < c[1]), None)
        if c: box_text(d, 540, 1330 if lay == "face" else 1015, [c[2]], 58, pad=(24, 10), maxw=820)
    return im

def audio():
    if os.path.exists("work/voice.wav"): return
    pre = "highpass=f=80,afftdn=nr=6:nf=-50,volume=5dB,alimiter=limit=0.5:attack=3:release=60:level=false"
    m = subprocess.run(["ffmpeg", "-hide_banner", "-i", "cut-audio.wav", "-af", pre + ",loudnorm=I=-14:TP=-2.0:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-2.0:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
          f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "cut-audio.wav", "-af", pre + "," + ln, "-ar", "48000", "work/voice.wav"], check=True)

if __name__ == "__main__":
    extract()
    if len(sys.argv) > 2 and sys.argv[1] == "--stills":
        os.makedirs("review/stills", exist_ok=True)
        for s in sys.argv[2].split(","):
            frame(round(float(s) * FPS)).save(f"review/stills/t{float(s):05.2f}.jpg", quality=88)
        sys.exit()
    audio()
    os.makedirs("out", exist_ok=True)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", "work/voice.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-profile:v", "high", "-crf", "18", "-preset", "medium",
                          "-vf", "scale=out_range=tv,format=yuv420p", "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                          "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", "out/nvidia-reel.mp4"], stdin=subprocess.PIPE)
    for i in range(NF):
        p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()
