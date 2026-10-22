"""Composite graded base + inserts + graphics frame by frame, pipe to ffmpeg (burns ASS subtitles)."""
import subprocess, sys, os, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from timeline import *
W, H, FPS = 1080, 1920, 30
G = os.path.join(HERE, "..", "graphics")
out_path, ass_path = sys.argv[1], sys.argv[2]
N = int(round(TOTAL * FPS))

def reader(path, vf=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path] + (["-vf", vf] if vf else []) + ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: return
        yield Image.frombuffer("RGB", (W, H), b)

def base_frames():
    yield from reader(os.path.join(WORK, "base_wake.mp4"))
    last = None
    for f in reader(os.path.join(WORK, "base_talk.mp4")): last = f; yield f
    while True: yield last

def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def rgba(p): return Image.open(os.path.join(G, p)).convert("RGBA")
hook, notif, access = rgba("hook.png"), rgba("notif.png"), rgba("access.png")
labels = {k: rgba(k + ".png") for k in ("label_demo", "label_video")}

# rounded-corner mask and soft shadow for full-screen inserts
mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 1, H - 1], 24, fill=255)
PAD = 60
shadow = Image.new("L", (W + 2 * PAD, H + 2 * PAD), 0)
ImageDraw.Draw(shadow).rounded_rectangle([PAD, PAD + 12, PAD + W, PAD + H + 12], 24, fill=140)
shadow = shadow.filter(ImageFilter.GaussianBlur(28))

def zoom_at(t):
    if t < WAKE_LEN: return 1.0
    u = t - WAKE_LEN
    if u < 0.3: return 1.06 - 0.06 * ease(u / 0.3)          # punch-in on the cut
    end1 = w("you", 2)[1]                                      # "...already texted you."
    if t < end1: return 1.0 + 0.03 * (t - WAKE_LEN - 0.3) / (end1 - WAKE_LEN - 0.3)
    if t < TALK_END: return 1.03
    return 1.03 + 0.03 * (t - TALK_END) / (TOTAL - TALK_END)   # slow push on the end hold
def zoom(img, z, cy=800):
    if z == 1.0: return img
    cw, ch = W / z, H / z
    y0 = min(max(cy - ch / 2, 0), H - ch); x0 = (W - cw) / 2
    return img.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))

def pop_alpha_scale(t, s, e, fin=0.2, fout=0.15):
    a = ease((t - s) / fin) * min(1, max(0, (e - t) / fout))
    return a, 0.9 + 0.1 * ease((t - s) / fin)

def paste_alpha(dst, src, xy, a):
    if a <= 0: return
    if a < 1:
        src = src.copy(); src.putalpha(src.getchannel("A").point(lambda v: int(v * a)))
    dst.alpha_composite(src, (int(xy[0]), int(xy[1])))

ins_gen = {}
def insert_frame(name, src):
    if src.endswith(".png"):
        if name not in ins_gen: ins_gen[name] = Image.open(os.path.join(WORK, src)).convert("RGB")
        return ins_gen[name]
    if name not in ins_gen: ins_gen[name] = [reader(os.path.join(WORK, src)), None]
    g = ins_gen[name]
    try: g[1] = next(g[0])
    except StopIteration: pass
    return g[1]

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-vf", f"ass={ass_path}", "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-r", str(FPS), out_path],
    stdin=subprocess.PIPE)
base = base_frames()
for n in range(N):
    t = n / FPS
    fr = zoom(next(base), zoom_at(t)).convert("RGBA")
    if t < WAKE_LEN:
        paste_alpha(fr, hook, (0, 430), 1)
        if t >= NOTIF_IN:
            y = -270 + (150 + 270) * ease((t - NOTIF_IN) / 0.25)
            paste_alpha(fr, notif, (20, y), 1)
    for name, s, e, src, lab in INSERTS:
        if s <= t < e:
            a, sc = pop_alpha_scale(t, s, e)
            img = insert_frame(name, src)
            sw, sh = int(W * sc), int(H * sc)
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            sh_img = Image.new("RGBA", shadow.size, (0, 0, 0, 255)); sh_img.putalpha(shadow)
            sh_img = sh_img.resize((int(shadow.size[0] * sc), int(shadow.size[1] * sc)))
            layer.alpha_composite(sh_img, ((W - sh_img.width) // 2, (H - sh_img.height) // 2))
            ins = img.resize((sw, sh), Image.LANCZOS).convert("RGBA"); ins.putalpha(mask.resize((sw, sh)))
            layer.alpha_composite(ins, ((W - sw) // 2, (H - sh) // 2))
            lb = labels[lab]; layer.alpha_composite(lb, (int((W - sw) / 2 + 24 * sc), int((H - sh) / 2 + 184 * sc)))
            paste_alpha(fr, layer, (0, 0), a)
    s, e = ACCESS
    if s <= t < e:
        a, sc = pop_alpha_scale(t, s, e)
        c = access.resize((int(access.width * sc), int(access.height * sc)), Image.LANCZOS)
        paste_alpha(fr, c, ((W - c.width) / 2, 1140 + (access.height - c.height) / 2), a)
    enc.stdin.write(fr.convert("RGB").tobytes())
    if n % 150 == 0: print(f"{t:.1f}s", flush=True)
enc.stdin.close(); enc.wait()
