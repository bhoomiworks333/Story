# Steps 5-6: composite Version A (split screen) and Version B (bear clip first, face in a PiP box)
import sys, json, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter
import gfx, subs
VER = sys.argv[1]                     # "A" or "B"
W, H, FPS = 1080, 1920, 30
W_ = {w["w"]: w for w in []}
words = json.load(open("work/words_out.json"))
def at(word, after=0.0):              # start time of the first matching word after `after`
    return next(w["s"] for w in words if w["w"].lower().startswith(word.lower()) and w["s"] >= after)
T2 = 3.35
T_LOOK = at("Look") - 0.06
T_CLAUDE = at("Claude's", T_LOOK) - 0.06
T_GEM = at("Gemini's", T_CLAUDE) - 0.06
T_STIFF = at("Stiff") - 0.06
T_PASS = at("pass") - 0.06
T_WORST = at("In", T_PASS) - 0.06
T_7, T_22 = at("$7"), at("$22")
T_THREE = at("Three") - 0.06
T_ITS = at("It's", T_THREE) - 0.06
T_WHICH = at("Which") - 0.06
END = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "work/face.mp4"],
                           capture_output=True, text=True).stdout)
NF = int(END * FPS)
print(dict(T_LOOK=T_LOOK, T_CLAUDE=T_CLAUDE, T_GEM=T_GEM, T_STIFF=T_STIFF, T_PASS=T_PASS, T_WORST=T_WORST,
           T_7=T_7, T_22=T_22, T_THREE=T_THREE, T_ITS=T_ITS, T_WHICH=T_WHICH, END=END))

# ---- bear clip: 60fps interpolated, held in memory ----
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", "work/bears60.mp4", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
BW, BH = 858, 1078
BEARS = np.frombuffer(raw, np.uint8).reshape(-1, BH, BW, 3)
def bear(src_t, panel):
    i = min(max(int(round(src_t * 60)), 0), len(BEARS) - 1)
    f = BEARS[i]
    if panel == "opus": f = f[18:538]
    elif panel == "argon": f = f[558:1078]
    return Image.fromarray(f)

BEAR_H = round(BH * W / BW)                            # full clip at full width: 1080 x 1357
def closeup(im, width=W, scale=1.4):              # panel 858x520 -> zoomed, centre-cropped to `width`
    big = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    x = (big.width - width) // 2
    return big.crop((x, 0, x + width, big.height))

def blurred_fill(im):
    s = max(W / im.width, H / im.height)
    small = im.resize((max(1, round(im.width * s / 12)), max(1, round(im.height * s / 12))), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(3)).resize((round(im.width * s), round(im.height * s)), Image.BILINEAR)
    x, y = (small.width - W) // 2, (small.height - H) // 2
    bg = small.crop((x, y, x + W, y + H))
    return Image.eval(bg, lambda v: int(v * 0.42))

# ---- bear source schedule (shared by both versions after the hook) ----
def bear_state(t):
    """-> (panel, src_t) or None when no bear footage is on screen."""
    if t < T2: return ("full", 6.2 + t) if VER == "B" else None
    if t < T_LOOK:
        if VER == "A": return None if t < T2 + 1.5 else ("full", 1.5 + (t - T2 - 1.5))
        return ("full", 0.3 + (t - T2))
    if t < T_CLAUDE: return ("full", 6.9 + (t - T_LOOK))
    if t < T_GEM:
        dt = t - T_CLAUDE
        return ("opus", 10.55 + 0.5 * dt) if dt < 3.1 else ("opus", 0.5 * (dt - 3.1))
    if t < T_STIFF: return ("argon", 10.95 + 0.5 * (t - T_GEM))
    if t < T_PASS: return ("argon", 5.1 + 0.5 * (t - T_STIFF))
    if t < T_WORST: return ("argon", 2.85 + 0.5 * (t - T_PASS))
    if t < T_ITS: return None
    return ("full", min(3.77 + (t - T_ITS), 12.1)) if VER == "B" else None

# ---- graphics ----
G = {n: Image.open(f"gfx/{n}.png") for n in ("punch", "credit", "xpost", "hook_A", "hook_B", "cta")}
CARD, PC, PG, PPOS = gfx.price_card()
def pop(im, t, t0, dur=0.22):
    """scale-in pop: 0.6 -> 1.1 -> 1.0"""
    dt = t - t0
    if dt < 0: return None
    if dt >= dur: return im
    k = dt / dur; s = 0.6 + 0.5 * (k / 0.55) if k < 0.55 else 1.1 - 0.1 * ((k - 0.55) / 0.45)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
def put(canvas, im, cx, cy):
    if im is not None: canvas.alpha_composite(im, (round(cx - im.width / 2), round(cy - im.height / 2)))

def price_layer(t):
    c = CARD.copy()
    for im, k, t0 in ((PC, "claude", T_7), (PG, "gemini", T_22)):
        p = pop(im, t, t0 - 0.03, 0.25)
        if p is not None: c.alpha_composite(p, (PPOS[k][0] - p.width // 2, PPOS[k][1] - p.height // 2))
    return pop(c, t, T_WORST, 0.2)

# ---- subtitles ----
SUBS = subs.chunks()
SUB_CACHE = {}
def sub_img(text):
    if text in SUB_CACHE: return SUB_CACHE[text]
    f = gfx.font(58); plain = text.replace("*", "")
    padx, pady = 24, 12; asc, desc = f.getmetrics(); tw = int(f.getlength(plain))
    im = Image.new("RGBA", (tw + 2 * padx, asc + desc + 2 * pady), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), 12, fill=(255, 255, 255, 255))
    if "*" in text:
        pre, hl = text.split("*")[0], text.split("*")[1]
        x0 = padx + f.getlength(pre) - 10; x1 = padx + f.getlength(pre + hl) + 10
        d.rounded_rectangle((x0, 5, x1, im.height - 6), 10, fill=(255, 214, 0, 255))
    d.text((padx, pady), plain, font=f, fill=(0, 0, 0))
    SUB_CACHE[text] = gfx.shadowed(im, blur=10, offset=4, alpha=90); return SUB_CACHE[text]
def sub_at(t):
    for c in SUBS:
        if c["s"] - 0.04 <= t < c["e"]: return c["text"]

# ---- face helpers ----
DARK = (17, 17, 17, 255)
def face_full(face, t):
    if t < T2 and VER == "A":                          # slow push-in on the hook, 100 -> 103 %
        s = 1 + 0.03 * t / T2; w, h = round(W / s), round(H / s)
        face = face.crop(((W - w) // 2, (H - h) // 2 - 40, (W - w) // 2 + w, (H - h) // 2 - 40 + h)).resize((W, H), Image.LANCZOS)
    return face

FACE_TOP, FACE_BOT = 240, 1330
def face_bottom(face):                                 # Version A split: hair-to-chin rows of the face into y 1150-1920
    reg = face.crop((0, FACE_TOP, W, FACE_BOT)); s = 770 / (FACE_BOT - FACE_TOP)
    fg = reg.resize((round(W * s), 770), Image.LANCZOS)
    bg = reg.crop((0, 160, W, 930)).filter(ImageFilter.GaussianBlur(25))
    bg.paste(fg, ((W - fg.width) // 2, 0)); return bg

PIP_W, PIP_H, PIP_X, PIP_Y = 380, 480, 36, 1380
PIP_MASK = gfx.rounded_mask(PIP_W, PIP_H, 36)
def pip(face):                                         # Version B: head-and-shoulders box (rows 240-1290 of the face)
    reg = face.crop((70, 240, 1010, 240 + round(940 * PIP_H / PIP_W))).resize((PIP_W, PIP_H), Image.LANCZOS)
    box = Image.new("RGBA", (PIP_W + 8, PIP_H + 8), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle((0, 0, PIP_W + 7, PIP_H + 7), 40, fill=(255, 255, 255, 255))
    box.paste(reg, (4, 4), PIP_MASK); return gfx.shadowed(box, blur=16, offset=6, alpha=140)

# ---- full-screen bear section (both versions, "Same prompt" -> "each other"): no face, no subtitles ----
def bear_fullscreen(t):
    st = bear_state(t)
    if st is None:                                     # Version A opens the section on the X post
        c = Image.new("RGBA", (W, H), DARK); put(c, pop(G["xpost"], t, T2, 0.2), W / 2, H / 2); return c
    panel, src = st; im = bear(src, panel)
    c = blurred_fill(bear(src, "full")).convert("RGBA")
    if panel == "full": c.paste(im.resize((W, BEAR_H), Image.LANCZOS), (0, (H - BEAR_H) // 2))
    else:
        im = closeup(im); c.paste(im, (0, (H - im.height) // 2))
    c.alpha_composite(G["credit"], (28, 150)); return c

# ---- per-frame composition ----
def frame_A(t, face):
    if T2 + 1.5 <= t < T_CLAUDE: return bear_fullscreen(t)
    full = t < T2 or t >= T_THREE
    if full:
        c = face_full(face, t).convert("RGBA")
        if t < T2: put(c, pop(G["hook_A"], t, 0.0), W / 2, 260)
        if T_THREE <= t < T_ITS: put(c, pop(G["punch"], t, T_THREE), W / 2, 300)
        if t >= T_WHICH: put(c, pop(G["cta"], t, T_WHICH), W / 2, 260)
        sy = 1430
    else:
        c = Image.new("RGBA", (W, H), DARK); c.paste(face_bottom(face), (0, 1150))
        st = bear_state(t)
        if t < T2 + 1.5: put(c, pop(G["xpost"], t, T2, 0.2), W / 2, 575)
        elif t >= T_WORST: put(c, price_layer(t), W / 2, 575)
        elif st:
            panel, src = st; im = bear(src, panel)
            if panel == "full":
                s = 1150 / BH; im = im.resize((round(BW * s), 1150), Image.LANCZOS); c.paste(im, ((W - im.width) // 2, 0))
            else:
                im = closeup(im); c.paste(im, (0, (1150 - im.height) // 2))
            c.alpha_composite(G["credit"], (28, 150))
        sy = 1150
    s = sub_at(t)
    if s: put(c, sub_img(s), W / 2, sy)
    return c

B_CLIP_H = 1500                                        # full clip zoomed to 1194x1500, centre-cropped to 1080 wide
B_CLIP_W = round(BW * B_CLIP_H / BH)
def frame_B(t, face):
    st = bear_state(t) if t < T_WORST or t >= T_ITS else None
    c = blurred_fill(bear(st[1] if st else 9.0, "full")).convert("RGBA")
    if T_WORST <= t < T_ITS:                           # price card stays up through "three times the money"
        put(c, price_layer(t), W / 2, 640)
        if t >= T_THREE: put(c, pop(G["punch"], t, T_THREE), W / 2, 1110)
    elif st:
        panel, src = st; im = bear(src, panel)
        if panel == "full":
            im = im.resize((B_CLIP_W, B_CLIP_H), Image.LANCZOS); x = (B_CLIP_W - W) // 2
            c.paste(im.crop((x, 0, x + W, B_CLIP_H)), (0, 0))
        else:
            im = closeup(im); c.paste(im, (0, 260))
        c.alpha_composite(G["credit"], (28, 150))
    c.alpha_composite(pip(face), (PIP_X - 32, PIP_Y - 32))
    if t < T2: put(c, pop(G["hook_B"], t, 0.0), W / 2, 690)
    if t >= T_WHICH: put(c, pop(G["cta"], t, T_WHICH), W / 2, 690)
    s = sub_at(t)
    if s: put(c, sub_img(s), W / 2, 1318)
    return c

if __name__ == "__main__":
    only = [float(x) for x in sys.argv[2:]]            # optional: still frames at given times
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", "work/face.mp4", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    out = f"bears_{VER}_{'main' if VER == 'A' else 'trial'}.mp4"
    enc = None if only else subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-i", "work/voice.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "18", "-preset", "slow",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    fn = frame_A if VER == "A" else frame_B
    for n in range(NF):
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: break
        t = n / FPS
        if only and not any(abs(t - o) < 0.5 / FPS for o in only): continue
        img = fn(t, Image.frombuffer("RGB", (W, H), buf)).convert("RGB")
        if only: img.save(f"work/frames/{VER}_{t:05.2f}.png")
        else: enc.stdin.write(img.tobytes())
        if n % 150 == 0: print(VER, n, "/", NF, flush=True)
    if enc: enc.stdin.close(); enc.wait(); print("wrote", out)
