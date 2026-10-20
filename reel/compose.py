"""Full Dussehra reel edit: B-roll, cards, push-in, end hold, subtitles.

All times are on the ORIGINAL footage timeline (see words_asr.json); with
--cuts they are remapped onto the trimmed footage made by trim.py.
--speed speeds up everything except the end hold (pitch preserved).
usage: python3 compose.py TALKING_HEAD.mp4 DAHAN_CLIP.mp4 OUT.mp4 [--cuts cut_plan.json] [--speed 1.15]
"""
import argparse, json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import subtitles as sub

W, H, FPS = 720, 1280, 30
HOLD = 1.5                                   # freeze at the end for the CTA
BOLD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
PAINTING = "assets/ravana_jatayu_ravi_varma.webp"

PAINT = (0.0, 3.20)                          # full screen (~1.9 s at 1.15x), cut to Prashant on "Dussehra"
PUSH = (22.72, 26.80)                        # "So he lost because ... say stop."
TASKS = (31.28, 34.80)                       # "It can do 10 things at once ... 10 heads."
STOP = (37.20, 40.48)                        # "a human can still check it and say stop."
STOP_PRESS = 39.76                           # the word "stop."
DAHAN = (40.48, 43.84)                       # "Happy Dussehra. Would you let AI make big decisions"
DAHAN_SRC = 3.0                              # where in the clip to start (flames -> collapse)
DAHAN_CROP = (31, 90, 532, 946)              # x, y, w, h: removes the player controls
TASK_LABELS = ["Code", "Email", "Research", "Reports", "Design",
               "Data", "Meetings", "Support", "Sales", "Planning"]


def ease(x):
    x = min(1, max(0, x)); return x * x * (3 - 2 * x)


_emoji_cache = {}
def emoji_img(ch, size):
    key = (ch, size)
    if key not in _emoji_cache:
        f = ImageFont.truetype(EMOJI, 109)
        im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
        im = im.crop(im.getbbox())
        _emoji_cache[key] = im.resize((int(im.width * size / im.height), size), Image.LANCZOS)
    return _emoji_cache[key]


def runs(text):
    out, cur = [], ""
    for c in text:
        if ord(c) > 0x2600 and c != "₹":
            if cur: out.append(("t", cur)); cur = ""
            out.append(("e", c))
        elif ord(c) == 0xFE0F:
            continue
        else:
            cur += c
    if cur: out.append(("t", cur))
    return out


def draw_rich(img, xy, text, font, fill, anchor_center=True):
    """Text with colour emoji, vertically centred on xy[1]; horizontally centred on xy[0]."""
    size = font.size
    parts = []
    for kind, s in runs(text):
        if kind == "t":
            parts.append((kind, s, font.getlength(s)))
        else:
            e = emoji_img(s, int(size * 0.95)); parts.append((kind, e, e.width))
    total = sum(p[2] for p in parts)
    x = xy[0] - total / 2 if anchor_center else xy[0]
    d = ImageDraw.Draw(img)
    for kind, s, w in parts:
        if kind == "t":
            d.text((x, xy[1]), s, font=font, fill=fill, anchor="lm")
        else:
            img.alpha_composite(s, (int(x), int(xy[1] - s.height / 2)))
        x += w
    return total


def pop(img, k):
    sc = 0.85 + 0.15 * ease(k) + 0.04 * math.sin(math.pi * min(1, k))   # slight overshoot
    return img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.LANCZOS)


def place(frame, img, yc):
    frame.alpha_composite(img, (int((W - img.width) / 2), int(H * yc - img.height / 2)))


# ---------- cards ----------
BG = (14, 15, 19, 255)
def tasks_card(t):
    """10 labelled boxes appearing one by one in an arc around an 'AI' head."""
    im = Image.new("RGBA", (W, H), BG); d = ImageDraw.Draw(im)
    f_t, f_l = ImageFont.truetype(BOLD, 54), ImageFont.truetype(SEMI, 25)
    d.text((W / 2, 170), "10 tasks at once", font=f_t, fill="white", anchor="mm")
    cx, cy, R = W / 2, 600, 262
    k0 = ease(t / 0.35)
    r = int(72 * (0.8 + 0.2 * k0))
    shown = []
    for i, lab in enumerate(TASK_LABELS):
        k = (t - 0.25 - i * 0.12) / 0.18
        if k <= 0: continue
        a = math.radians(225 - i * 30)               # 270° crown open at the bottom, like the ten heads
        shown.append((lab, k, cx + R * math.cos(a), cy - R * math.sin(a)))
    for _, k, x, y in shown:                         # spokes under the boxes
        d.line([cx, cy, x, y], fill=(70, 74, 90, 255), width=2)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 255))
    d.text((cx, cy), "AI", font=ImageFont.truetype(BOLD, 56), fill="black", anchor="mm")
    bw, bh = 128, 54
    for lab, k, x, y in shown:
        box = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
        bd.rounded_rectangle([0, 0, bw - 1, bh - 1], 12, fill=(32, 35, 45, 255), outline=(255, 196, 64, 255), width=2)
        bd.text((bw / 2, bh / 2), lab, font=f_l, fill="white", anchor="mm")
        b = pop(box, k)
        im.alpha_composite(b, (int(x - b.width / 2), int(y - b.height / 2)))
    return im


def stop_card(t, pressed):
    """'AI wants to: send payment ₹5,00,000' with Approve / Stop; Stop highlighted, pressed on 'stop.'"""
    im = Image.new("RGBA", (W, H), BG); d = ImageDraw.Draw(im)
    k = ease(t / 0.3)
    x0, y0, x1, y1 = 70, int(300 + 40 * (1 - k)), W - 70, int(800 + 40 * (1 - k))
    d.rounded_rectangle([x0, y0, x1, y1], 32, fill=(255, 255, 255, int(255 * k)))
    if k < 1: return im
    draw_rich(im, (x0 + 50, y0 + 75), "🤖 AI wants to:", ImageFont.truetype(SEMI, 34), (90, 94, 110), anchor_center=False)
    d.text((x0 + 50, y0 + 160), "Send payment", font=ImageFont.truetype(BOLD, 52), fill="black", anchor="lm")
    d.text((x0 + 50, y0 + 245), "₹5,00,000", font=ImageFont.truetype(BOLD, 76), fill="black", anchor="lm")
    by, bh, bw = y1 - 150, 100, 230
    fb = ImageFont.truetype(BOLD, 36)
    ax = x0 + 40
    d.rounded_rectangle([ax, by, ax + bw, by + bh], 22, fill=(240, 241, 245), outline=(205, 208, 218), width=3)
    draw_rich(im, (ax + bw / 2, by + bh / 2), "✅ Approve", fb, (120, 124, 138))
    sx = x1 - 40 - bw
    pulse = 0.5 + 0.5 * math.sin(t * 2 * math.pi * 1.6)
    glow = 8 + int(10 * pulse) if not pressed else 14
    d.rounded_rectangle([sx - glow, by - glow, sx + bw + glow, by + bh + glow], 22 + glow, fill=(229, 57, 53, 70 if not pressed else 120))
    s = 0.94 if pressed else 1.0
    cxs, cys = sx + bw / 2, by + bh / 2
    d.rounded_rectangle([cxs - bw * s / 2, cys - bh * s / 2, cxs + bw * s / 2, cys + bh * s / 2], 22, fill=(198, 32, 32))
    draw_rich(im, (cxs, cys), "🛑 Stop", fb, "white")
    if pressed:
        d.text((W / 2, y1 + 70), "Human said stop. Nothing sent.", font=ImageFont.truetype(SEMI, 32), fill=(200, 203, 214), anchor="mm")
    return im


# ---------- frames ----------
def cover(img, focus_x=0.5, focus_y=0.5, zoom=1.0):
    sc = max(W / img.width, H / img.height) * zoom
    rw, rh = img.width * sc, img.height * sc
    left = min(max(0, rw * focus_x - W / 2), rw - W); top = min(max(0, rh * focus_y - H / 2), rh - H)
    box = (left / sc, top / sc, (left + W) / sc, (top + H) / sc)
    return img.resize((W, H), Image.LANCZOS, box=box)


def read_frames(path, w, h, ss=None, t=None, crop=None):
    vf = f"crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]}," if crop else ""
    cmd = ["ffmpeg", "-v", "error"] + (["-ss", str(ss)] if ss else []) + ["-i", path] + (["-t", str(t)] if t else []) + \
          ["-vf", vf + f"scale={w}:{h}:flags=lanczos,fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(w * h * 3)
        if len(b) < w * h * 3: break
        yield Image.frombytes("RGB", (w, h), b)


def main(head, dahan, out, cuts=(), speed=1.0):
    global PAINT, PUSH, TASKS, STOP, STOP_PRESS, DAHAN
    R = lambda t: sub.remap(t, cuts)
    PAINT, PUSH, TASKS, STOP, DAHAN = [tuple(map(R, x)) for x in (PAINT, PUSH, TASKS, STOP, DAHAN)]
    STOP_PRESS = R(STOP_PRESS)
    final, out = out, (out + ".1x.mp4" if speed != 1.0 else out)
    _, _, _, dur = sub.probe(head)
    total = dur + HOLD
    cues = sub.build_cues("words_asr.json", dur, cuts)
    cues[-1] = (cues[-1][0], total, cues[-1][2])                         # "Yes or no?" holds through the freeze
    sfont = ImageFont.truetype(sub.FONT, sub.SIZE)
    sboxes = [sub.render_box(t, sfont) for _, _, t in cues]
    painting = Image.open(PAINTING).convert("RGB")
    dahan_frames = [f.crop((0, 0, W, H)) for f in read_frames(dahan, W, H, ss=DAHAN_SRC, t=DAHAN[1] - DAHAN[0] + 0.2, crop=DAHAN_CROP)]

    audio = out + ".audio.wav"
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", head, "-af",
        f"volume=4.2dB,alimiter=limit=0.84:level=false,apad=pad_dur={HOLD}", "-t", f"{total:.3f}", "-ar", "48000", audio])
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "18",
        "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out],
        stdin=subprocess.PIPE)
    src = read_frames(head, W, H)
    last = None
    for f in range(int(round(total * FPS))):
        t = f / FPS
        cur = next(src, None)
        if cur is not None: last = cur
        if PAINT[0] <= t < PAINT[1]:
            k = (t - PAINT[0]) / (PAINT[1] - PAINT[0])
            fr = cover(painting, 0.40, 0.42, 1.0 + 0.10 * ease(k))
        elif TASKS[0] <= t < TASKS[1]:
            fr = tasks_card(t - TASKS[0])
        elif STOP[0] <= t < STOP[1]:
            fr = stop_card(t - STOP[0], t >= STOP_PRESS)
        elif DAHAN[0] <= t < DAHAN[1]:
            fr = dahan_frames[min(len(dahan_frames) - 1, int((t - DAHAN[0]) * FPS))]
        elif PUSH[0] <= t < PUSH[1]:
            k = ease((t - PUSH[0]) / (PUSH[1] - PUSH[0]))
            fr = cover(last, 0.5, 0.36, 1.0 + 0.12 * k)
        else:
            fr = last
        fr = fr.convert("RGBA")
        for i, (s, e, _) in enumerate(cues):
            if s <= t < e:
                place(fr, pop(sboxes[i], (t - s) / sub.POP), sub.Y_CENTER); break
        enc.stdin.write(fr.convert("RGB").tobytes())
    enc.stdin.close(); rc = enc.wait()
    os.remove(audio)
    if rc: sys.exit(rc)
    if speed != 1.0:
        sp = f"{speed}"
        subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", out, "-filter_complex",
            f"[0:v]trim=0:{dur},setpts=(PTS-STARTPTS)/{sp},fps={FPS}[v1];[0:v]trim={dur},setpts=PTS-STARTPTS[v2];"
            f"[0:a]atrim=0:{dur},asetpts=PTS-STARTPTS,atempo={sp}[a1];[0:a]atrim={dur},asetpts=PTS-STARTPTS[a2];"
            "[v1][a1][v2][a2]concat=n=2:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]", "-c:v", "libx264",
            "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", final])
        os.remove(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("head"); ap.add_argument("dahan"); ap.add_argument("out")
    ap.add_argument("--cuts"); ap.add_argument("--speed", type=float, default=1.0)
    a = ap.parse_args()
    main(a.head, a.dahan, a.out, json.load(open(a.cuts))["cuts"] if a.cuts else [], a.speed)
