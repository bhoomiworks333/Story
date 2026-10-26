"""Composite the Harvey reel frame by frame (full/split layouts, cards, animations) and burn subtitles."""
import subprocess, sys, os, math
from PIL import Image, ImageDraw
from timeline import *
W, H, FPS, HALF = 1080, 1920, 30, 960
G = os.path.join(HERE, "..", "graphics")
out_path, ass_path = sys.argv[1], sys.argv[2]
N = int(round(TOTAL * FPS))
FACE_X = 895                                   # face centre in the 1920x1080 source
FULL_CW = 860                                      # full mode: 860x1080 of source -> 1080x1356, wall extended above
FULL_S = W / FULL_CW; FULL_H = round(1080 * FULL_S); FULL_TOP = H - FULL_H
FEATHER = Image.linear_gradient("L").resize((W, 220))  # soft seam between real and extended wall
_plate = Image.open(os.path.join(WORK, "wall_plate.png")).convert("RGB")   # median of the top rows: wall without his hair
_plate = _plate.resize((W, 30), Image.LANCZOS, box=(FACE_X - FULL_CW / 2, 0, FACE_X + FULL_CW / 2, 30))
from PIL import ImageFilter
WALL = _plate.resize((W, FULL_TOP + 220), Image.BILINEAR).filter(ImageFilter.GaussianBlur(24))
SPLIT_BOX = (FACE_X - 550, 60, FACE_X + 550, 1038)  # 1100x978 -> 1080x960, head fully in frame

def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_io(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def load2x(n): return Image.open(os.path.join(G, n + ".png")).convert("RGBA")
def half(im): return im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
cards2x = {k: load2x("card_" + k) for k in ("repo", "inputs_0", "inputs_1", "inputs_2", "email", "outbox", "reply", "booking", "heartbeat", "cost", "blank")}
cards = {k: half(v) for k, v in cards2x.items()}
pill, cta = half(load2x("pill_opensource")), half(load2x("cta"))

# README pan source (frame 0:07.3 of the screen recording; crop excludes the cursor)
readme = Image.open(os.path.join(WORK, "readme_7.3.png")).convert("RGB").crop((20, 0, 548, 892))
RM_W, RM_H, RM_X, RM_Y = 1000, 740, 40, 70
rm_mask = Image.new("L", (RM_W, RM_H), 0); ImageDraw.Draw(rm_mask).rounded_rectangle([0, 0, RM_W - 1, RM_H - 1], 22, fill=255)
def readme_card(p):
    sc = RM_W / readme.width; sh = RM_H / sc
    y0 = 215 + (readme.height - sh - 215) * ease_io(p)
    win = readme.resize((RM_W, RM_H), Image.LANCZOS, box=(0, y0, readme.width, y0 + sh)).convert("RGBA"); win.putalpha(rm_mask)
    c = cards["blank"].copy(); c.alpha_composite(win, (RM_X, RM_Y)); return c

# heartbeat: yellow arc sweeps once around the ring; labels stay on top
HB_C, HB_R, HB_WD = (1080, 890), 550, 22            # 2x coordinates
HB_LABELS = [(860, 300, 1300, 480), (1370, 1130, 1800, 1340), (360, 1130, 840, 1340)]
def heartbeat_card(p):
    c = cards2x["heartbeat"].copy(); d = ImageDraw.Draw(c)
    if p > 0:
        a0, a1 = -90, -90 + 360 * p
        bb = [HB_C[0] - HB_R, HB_C[1] - HB_R, HB_C[0] + HB_R, HB_C[1] + HB_R]
        d.arc(bb, a0, a1, fill="#FFD600", width=HB_WD)
        t = math.radians(a1); hx, hy = HB_C[0] + HB_R * math.cos(t), HB_C[1] + HB_R * math.sin(t)
        tx, ty = -math.sin(t), math.cos(t); nx, ny = math.cos(t), math.sin(t)
        d.polygon([(hx + tx * 46, hy + ty * 46), (hx - tx * 6 + nx * 34, hy - ty * 6 + ny * 34), (hx - tx * 6 - nx * 34, hy - ty * 6 - ny * 34)], fill="#FFD600")
        for box in HB_LABELS: c.alpha_composite(cards2x["heartbeat"].crop(box), box[:2])
    return half(c)

def repo_card(t):
    z = 1 + 0.10 * ease_io((t - REPO_ZOOM[0]) / (REPO_ZOOM[1] - REPO_ZOOM[0]))
    src = cards2x["repo"]; fx, fy = 1080, 725        # focus on the repo name (2x coords)
    bw, bh = src.width / z, src.height / z; x0, y0 = fx - fx / z, fy - fy / z
    c = src.resize((W, HALF), Image.LANCZOS, box=(x0, y0, x0 + bw, y0 + bh))
    if t >= PILL_AT:
        a = ease((t - PILL_AT) / 0.2); s = 0.92 + 0.08 * a
        pl = pill.resize((int(pill.width * s), int(pill.height * s)), Image.LANCZOS)
        if a < 1: pl.putalpha(pl.getchannel("A").point(lambda v: int(v * a)))
        c.alpha_composite(pl, ((W - pl.width) // 2, 698 - pl.height // 2))
    return c

def card_for(name, t, s, e):
    p = (t - s) / max(e - s, 1e-6)
    if name == "repo": return repo_card(t)
    if name == "readme": return readme_card(p)
    if name == "heartbeat": return heartbeat_card(p)
    if name == "inputs":
        base = cards["inputs_0"] if t < INPUT1_AT else cards["inputs_1"] if t < INPUT2_AT else cards["inputs_2"]
        prev = None if t < INPUT1_AT else cards["inputs_0"] if t < INPUT2_AT else cards["inputs_1"]
        k = INPUT1_AT if t < INPUT2_AT else INPUT2_AT
        if prev is not None and t - k < 0.2: return Image.blend(prev, base, ease((t - k) / 0.2))
        return base
    return cards[name]

def pop(img, t0, t, canvas_size):
    a = ease((t - t0) / 0.2); s = 0.92 + 0.08 * a
    layer = Image.new("RGBA", canvas_size, (0, 0, 0, 255))
    im = img if s >= 0.999 else img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)
    if a < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    layer.alpha_composite(im, ((canvas_size[0] - im.width) // 2, (canvas_size[1] - im.height) // 2)); return layer

def full_frame(fr, z):
    """Zoomed-out full layout: the real frame sits at the bottom, the plain grey wall is extended above it."""
    real = fr.resize((W, FULL_H), Image.LANCZOS, box=(FACE_X - FULL_CW / 2, 0, FACE_X + FULL_CW / 2, 1080))
    canvas = Image.new("RGB", (W, H)); canvas.paste(WALL, (0, 0))
    canvas.paste(real.crop((0, 0, W, 220)), (0, FULL_TOP), FEATHER); canvas.paste(real.crop((0, 220, W, FULL_H)), (0, FULL_TOP + 220))
    if z != 1.0:                                       # push-in around his face
        cx, cy = W / 2, FULL_TOP + 460 * FULL_S; bw, bh = W / z, H / z
        canvas = canvas.resize((W, H), Image.LANCZOS, box=(cx - cx / z, cy - cy / z, cx - cx / z + bw, cy - cy / z + bh))
    return canvas.convert("RGBA")

def frames(path):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    last = None
    while True:
        b = p.stdout.read(1920 * 1080 * 3)
        if len(b) < 1920 * 1080 * 3: break
        last = Image.frombuffer("RGB", (1920, 1080), b); yield last
    while True: yield last

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-vf", f"ass={ass_path}", "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-r", str(FPS), out_path], stdin=subprocess.PIPE)
src = frames(os.path.join(WORK, "base_src.mp4"))
for n in range(N):
    t = n / FPS; fr = next(src)
    mode, card, s0 = mode_at(t)
    e0 = next(e for s, e, m, c in SEGMENTS if s == s0)
    if mode == "full":
        z = 1 + 0.04 * ease_io(t / SEGMENTS[0][1]) if s0 == 0 else 1.0       # push-in on "Brooo"
        out = full_frame(fr, z)
        if card == "cta" and t >= CTA_AT:
            a = ease((t - CTA_AT) / 0.2); sc = 0.92 + 0.08 * a
            c = cta.resize((int(cta.width * sc), int(cta.height * sc)), Image.LANCZOS)
            if a < 1: c.putalpha(c.getchannel("A").point(lambda v: int(v * a)))
            out.alpha_composite(c, ((W - c.width) // 2, 212 - c.height // 2))
    else:
        out = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        out.alpha_composite(pop(card_for(card, t, s0, e0), s0, t, (W, HALF)), (0, 0))
        out.paste(fr.resize((W, HALF), Image.LANCZOS, box=SPLIT_BOX), (0, HALF))
        ImageDraw.Draw(out).rectangle([0, HALF - 2, W, HALF + 1], fill=(10, 10, 10, 255))
    enc.stdin.write(out.convert("RGB").tobytes())
    if n % 150 == 0: print(f"{t:.1f}s", flush=True)
enc.stdin.close(); enc.wait()
