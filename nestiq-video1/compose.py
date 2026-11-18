# NestIQ Video #1 compositor: faces, split-screen graphics, captions, text overlays.
# usage: python3 compose.py stills 1.0 9.5 ...   |   python3 compose.py render out.mp4 audio.wav [--preview]
import json, sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont
import graphics as G

FPS = 30
S = json.load(open("segments.json"))
EYES = {"L1": 900, "L2": 919, "L3": 898, "L4": 957, "L5": 863, "L6a": 946, "L6b": 946, "L7": 872}
t0 = 0.0
for s in S:
    s["n"] = round((s["out"] - s["in"]) * FPS); s["start"] = t0; t0 += s["n"] / FPS
DUR = t0
SEG = {s["id"]: s for s in S}
def T(seg, src): s = SEG[seg]; return s["start"] + src - s["in"]

# ---- captions: (segment, text, source start, keyword or None, keyword source time) ----
C = [
 ("L1", "This is our first video.", 1.557, "first video", 2.16),
 ("L1", "I'm Aman.", 3.156, None, 0),
 ("L2", "And I'm Alvish.", 0.30, None, 0),
 ("L2", "We work on software", 1.26, None, 0),
 ("L2", "for factories.", 2.16, None, 0),
 ("L3", "In a lot of factories,", 0.643, None, 0),
 ("L3", "parts are cut", 2.10, None, 0),
 ("L3", "from big metal sheets.", 3.06, None, 0),
 ("L3", "And before cutting,", 4.865, None, 0),
 ("L3", "someone arranges those parts", 6.10, None, 0),
 ("L3", "on the sheets,", 7.72, None, 0),
 ("L3", "by hand", 9.282, "by hand", 9.282),
 ("L3", "or by manual work.", 9.98, None, 0),
 ("L3", "And it takes hours.", 11.58, "hours", 13.0),
 ("L4", "Even after all the time,", 0.196, None, 0),
 ("L4", "a big part of the sheet", 1.54, None, 0),
 ("L4", "ends up as scrap", 2.44, "scrap", 3.06),
 ("L4", "in all the factories", 3.723, None, 0),
 ("L4", "every single day.", 4.90, None, 0),
 ("L5", "And most owners", 19.435, None, 0),
 ("L5", "don't even notice it,", 20.80, None, 0),
 ("L5", "it becomes normal.", 22.58, "normal", 23.28),
 ("L5", "But that bothers us.", 24.085, None, 0),
 ("L6a", "So on this page,", 0.155, None, 0),
 ("L6a", "we'll break down", 1.025, None, 0),
 ("L6a", "these factory problems", 1.976, None, 0),
 ("L6a", "one by one.", 3.09, None, 0),
 ("L6b", "What causes them,", 0.23, None, 0),
 ("L6b", "what they really cost,", 1.42, None, 0),
 ("L6b", "and how we are", 2.773, None, 0),
 ("L6b", "solving them", 3.45, None, 0),
 ("L6b", "with NestIQ.", 4.091, "NestIQ", 4.25),
 ("L7", "If you run", 26.787, None, 0),
 ("L7", "or work in a factory,", 27.512, None, 0),
 ("L7", "follow along.", 28.955, "follow along", 28.955),
]
CAPS = []
for i, (seg, txt, src, kw, kws) in enumerate(C):
    a = T(seg, src) - 0.03
    s = SEG[seg]; seg_end = s["start"] + s["n"] / FPS
    b = T(C[i + 1][0], C[i + 1][2]) - 0.03 if i + 1 < len(C) and C[i + 1][0] == seg else seg_end
    if i + 1 < len(C) and C[i + 1][0] != seg: b = min(b, T(C[i + 1][0], C[i + 1][2]) - 0.03)
    CAPS.append(dict(a=a, b=b, txt=txt, kw=kw, kwt=T(seg, kws) - 0.03 if kw else 0, seg=seg))

# ---- graphic windows ----
G1 = (T("L3", 4.865) - 0.03, SEG["L3"]["start"] + SEG["L3"]["n"] / FPS)
G1C = {"drops": [T("L3", x) - G1[0] for x in (6.10, 6.66, 7.16, 7.46, 8.04, 9.40, 10.42, 10.96)],
       "hours": T("L3", 13.0) - G1[0]}
G2 = (T("L4", 2.44) - 0.03, SEG["L4"]["start"] + SEG["L4"]["n"] / FPS)
G2C = {"fade": 0.12, "glow": 0.45, "text": T("L4", 3.06) - G2[0]}
G3 = (T("L6b", 2.773) - 0.03, DUR)
G3C = {"slide": 0.0, "squares": [1.0, 1.75, 2.5], "strip": 3.4}
VIDEO1_END = T("L2", 0.30)
NESTIQ_FROM = DUR - 2.0

FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
F_CAP = ImageFont.truetype(FB, 54)
F_V1 = ImageFont.truetype(FB, 72)
F_BRAND = ImageFont.truetype(FB, 44)
WHITE, BLACK, ORANGE = (255, 255, 255), (0, 0, 0), (0xF9, 0x73, 0x16)

def graphic_at(t):
    if G1[0] <= t < G1[1]: return G.draw_g1(t - G1[0], G1C)
    if G2[0] <= t < G2[1]: return G.draw_g2(t - G2[0], G2C)
    if G3[0] <= t < G3[1] + 1: return G.draw_g3(t - G3[0], G3C)
    return None

def caption(im, t, cy):
    cap = next((c for c in CAPS if c["a"] <= t < c["b"]), None)
    if not cap: return
    d = ImageDraw.Draw(im)
    txt = cap["txt"]; padx, pady = 30, 16
    l, tp, r, b = d.textbbox((0, 0), txt, font=F_CAP)
    w = r - l + 2 * padx; h = 54 + 2 * pady
    x = 540 - w / 2; y = cy - h / 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=16, fill=WHITE)
    if cap["kw"] and t >= cap["kwt"]:
        i = txt.index(cap["kw"])
        kx0 = d.textlength(txt[:i], font=F_CAP); kx1 = kx0 + d.textlength(cap["kw"], font=F_CAP)
        d.rounded_rectangle([x + padx + kx0 - 9, y + 7, x + padx + kx1 + 7, y + h - 7], radius=12, fill=ORANGE)
    asc = F_CAP.getmetrics()[0]
    d.text((x + padx - l, y + pady + (54 - asc) / 2 + 2), txt, font=F_CAP, fill=BLACK)

def boxed(im, txt, font, cx, cy, padx=34, pady=20):
    d = ImageDraw.Draw(im)
    l, tp, r, b = d.textbbox((0, 0), txt, font=font)
    w, h = r - l + 2 * padx, b - tp + 2 * pady
    x, y = cx - w / 2, cy - h / 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=18, fill=WHITE)
    d.text((x + padx - l, y + pady - tp), txt, font=font, fill=BLACK)

def frame_at(t, face_rgb, seg):
    g = graphic_at(t)
    if g is None:
        im = Image.fromarray(face_rgb)
        cap_y = 1470
    else:
        im = Image.new("RGB", (1080, 1920), G.BG)
        im.paste(g, (0, 0))
        top = int(EYES[seg] - 400); top = max(0, min(960, top))
        im.paste(Image.fromarray(face_rgb[top:top + 960]), (0, 960))
        cap_y = 958
    caption(im, t, cap_y)
    if t < VIDEO1_END: boxed(im, "Video #1", F_V1, 540, 360)
    if t >= NESTIQ_FROM:
        d = ImageDraw.Draw(im)
        d.text((64, 236), "NestIQ", font=F_BRAND, fill=WHITE, stroke_width=0)
    return im

def face_frames():
    for s in S:
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", f"segs/{s['id']}_full.mp4", "-f", "rawvideo",
                              "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        last = None
        for k in range(s["n"]):
            buf = p.stdout.read(1080 * 1920 * 3)
            if len(buf) == 1080 * 1920 * 3: last = np.frombuffer(buf, np.uint8).reshape(1920, 1080, 3)
            yield s["id"], last
        p.stdout.close(); p.wait()

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        ts = [float(x) for x in sys.argv[2:]]
        for t in ts:
            s = next(s for s in S if s["start"] <= t < s["start"] + s["n"] / FPS)
            out = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t - s['start']:.3f}", "-i",
                f"segs/{s['id']}_full.mp4", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                capture_output=True).stdout
            fr = np.frombuffer(out, np.uint8).reshape(1920, 1080, 3)
            frame_at(t, fr, s["id"]).save(f"qa/still_{t:05.2f}.png")
        print("duration %.2f" % DUR)
    elif mode == "render":
        out, audio = sys.argv[2], sys.argv[3]; prev = "--preview" in sys.argv
        vf = ["-vf", "scale=540:960"] if prev else []
        enc = ["-c:v", "libx264", "-crf", "26" if prev else "18", "-preset", "veryfast" if prev else "slow",
               "-pix_fmt", "yuv420p", "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709",
               "-color_trc", "bt709"]
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920",
              "-r", str(FPS), "-i", "-", "-i", audio] + vf + enc +
              ["-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
        for k, (seg, fr) in enumerate(face_frames()):
            ff.stdin.write(frame_at(k / FPS, fr, seg).tobytes())
            if k % 150 == 0: print(f"frame {k}", flush=True)
        ff.stdin.close(); ff.wait()
        print("done", out, "%.2f s" % DUR)
