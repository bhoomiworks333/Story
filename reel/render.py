"""Frame compositor: reframe + asset cards + punch-ins + captions, encoded with the final mix.

usage: python3 render.py [--preview]   (preview = fast low-quality encode)
"""
import numpy as np, subprocess, os, sys, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import timeline as T
from card7 import placeholder

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, "build")
W, H = 1080, 1920
DY = 470                                # top of the speaker layer while cards are up
SCALE = 0.82                            # speaker scale while cards are up (keeps chin clear of captions)
CARD_BOX = (65, 72, 1015, DY - 26)      # area the card is fitted into
CAP_CY = int(0.865 * H)                 # caption box centre, measured from reference
FONT = ImageFont.truetype(os.path.join(HERE, "fonts", "Figtree-Medium.ttf"), 78)


def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)


def ease_out(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3


# ---------- captions: white rounded box, black medium text (reference geometry @1080x1920) ----------
def caption_img(text):
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    font = FONT
    while d.textlength(text, font=font) > W - 2 * 70 - 80:
        font = font.font_variant(size=font.size - 2)
    tw = d.textlength(text, font=font)
    bw, bh, padx, base = int(tw + 2 * 40), 147, 40, 98
    im = Image.new("RGBA", (bw * 2, bh * 2), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
    dd.rounded_rectangle((0, 0, bw * 2 - 1, bh * 2 - 1), 44, fill=(255, 255, 255, 255))
    dd.text((padx * 2, base * 2), text, font=font.font_variant(size=font.size * 2), fill=(17, 17, 17, 255), anchor="ls")
    return im.resize((bw, bh), Image.LANCZOS)


def load_cards():
    cards = []
    for i, c in enumerate(T.CARDS):
        f = sorted(glob.glob(os.path.join(HERE, "assets", c["key"] + ".*")))
        if not f:
            p = os.path.join(B, c["key"] + "_placeholder.png"); placeholder(p, c["label"]); f = [p]
            print("  missing asset ->", c["key"], "(placeholder)")
        im = Image.open(f[0]).convert("RGBA")
        bx0, by0, bx1, by1 = CARD_BOX
        s = min((bx1 - bx0) / im.width, (by1 - by0) / im.height)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        e = T.CARDS[i + 1]["s"] if i + 1 < len(T.CARDS) else T.CARDS_END
        e = min([e] + [f["s"] for f in T.FULLS if f["s"] > c["s"]])  # a full-screen asset ends the card
        cards.append(dict(img=im, s=c["s"], e=e))
    return cards


def load_fulls():
    out = []
    for f in T.FULLS:
        im = Image.open(glob.glob(os.path.join(HERE, "assets", f["key"] + ".*"))[0]).convert("RGBA")
        s = min(1000 / im.width, 1700 / im.height)
        out.append(dict(f, img=im, base=s))
    return out


def paste(dst, im, x, y, alpha=1.0):
    """alpha-composite RGBA PIL image onto float HxWx3 array"""
    a = np.asarray(im, np.float32) / 255
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(W, x + im.width), min(H, y + im.height)
    if x1 <= x0 or y1 <= y0: return
    sub = a[y0 - y:y1 - y, x0 - x:x1 - x]
    al = sub[..., 3:4] * alpha
    dst[y0:y1, x0:x1] = dst[y0:y1, x0:x1] * (1 - al) + sub[..., :3] * 255 * al


def zoom(frame, z, ay=0.36):
    if z == 1: return frame
    cw, ch = W / z, H / z; cx, cy = W / 2, H * ay
    box = (cx - cw / 2, max(0, cy - ch * ay), cx + cw / 2, max(0, cy - ch * ay) + ch)
    return frame.resize((W, H), Image.LANCZOS, box=box)


def edge_mask(w, h, r, f=60):
    """soft alpha on left/right/top edges so the scaled speaker melts into the blurred backdrop"""
    fx = max(1, int(f * r)); m = np.ones((h, w), np.float32)
    ramp = np.linspace(0, 1, fx, dtype=np.float32)
    m[:, :fx] *= ramp; m[:, w - fx:] *= ramp[::-1]; m[:fx, :] *= ramp[:, None]
    return m[..., None]


def main():
    preview = "--preview" in sys.argv
    caps = T.captions(); cap_imgs = [caption_img(c["text"]) for c in caps]
    cards = load_cards(); fulls = load_fulls()

    dec = subprocess.Popen(
        f"ffmpeg -v error -i {B}/src.mp4 -vf scale={W}:{H}:flags=lanczos -f rawvideo -pix_fmt rgb24 -",
        shell=True, stdout=subprocess.PIPE)
    out = os.path.join(B, "preview.mp4" if preview else "final.mp4")
    enc = subprocess.Popen(
        f"ffmpeg -y -v error -f rawvideo -pix_fmt rgb24 -s {W}x{H} -r {T.FPS} -i - -i {B}/mix.wav "
        f"-map 0:v -map 1:a -c:v libx264 -preset {'veryfast' if preview else 'slow'} -crf {23 if preview else 16} "
        "-profile:v high -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 "
        "-c:a aac -b:a 320k -ar 48000 -shortest -movflags +faststart " + out,
        shell=True, stdin=subprocess.PIPE)

    fb = W * H * 3; i = 0
    while True:
        raw = dec.stdout.read(fb)
        if len(raw) < fb: break
        t = i / T.FPS; i += 1
        if T.CUT[0] <= t < T.CUT[1]: continue
        frame = Image.frombuffer("RGB", (W, H), raw)

        # reframe progress
        r = ease((t - T.REFRAME_IN[0]) / (T.REFRAME_IN[1] - T.REFRAME_IN[0])) * \
            (1 - ease((t - T.REFRAME_OUT[0]) / (T.REFRAME_OUT[1] - T.REFRAME_OUT[0])))
        z = 1.0
        for p in T.PUNCH:
            if p["s"] <= t < p["e"]:
                z = p["z"]
                if p["e"] == T.REFRAME_OUT[1]:  # ease this one back out with the reframe
                    z = 1 + (p["z"] - 1) * (1 - ease((t - T.REFRAME_OUT[0]) / (T.REFRAME_OUT[1] - T.REFRAME_OUT[0])))
        zf = zoom(frame, z)
        if r > 0:
            sc = 1 - (1 - SCALE) * r                     # speaker shrinks a little and slides down
            dy = int(round(DY * r)); sw, shh = round(W * sc), round(H * sc)
            layer = np.asarray(zf.resize((sw, shh), Image.BILINEAR if r < 1 else Image.LANCZOS), np.float32)
            x0 = (W - sw) // 2
            bg = np.asarray(frame.resize((54, 96), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3))
                            .resize((W, H), Image.BICUBIC), np.float32)
            dark = (1 - 0.55 * r) * np.ones((H, 1, 1), np.float32)
            dark[dy:] = 1 - 0.25 * r                     # backdrop: darker behind cards, lighter at the sides
            canvas = bg * dark
            m = edge_mask(sw, shh, r)
            h = min(shh, H - dy)
            reg = canvas[dy:dy + h, x0:x0 + sw]
            canvas[dy:dy + h, x0:x0 + sw] = layer[:h] * m[:h] + reg * (1 - m[:h])
        else:
            canvas = np.asarray(zf, np.float32).copy()

        # cards
        bx0, by0, bx1, by1 = CARD_BOX
        for c in cards:
            if c["s"] <= t < c["e"] + 0.17:
                a_in = ease_out((t - c["s"]) / 0.27)
                a_out = 1 - ease((t - c["e"]) / 0.17) if t >= c["e"] else 1
                a = a_in * a_out
                if a <= 0: continue
                im = c["img"]
                sc = 0.965 + 0.035 * a_in
                if sc < 0.999:
                    im = im.resize((round(im.width * sc), round(im.height * sc)), Image.BILINEAR)
                x = (W - im.width) // 2
                y = by0 + ((by1 - by0) - im.height) // 2 + int(16 * (1 - a_in))
                paste(canvas, im, x, y, a)

        # full-screen assets: 4-frame fade in, slow 3.5% push, hard cut out
        full_on = False
        for f in fulls:
            if f["s"] <= t < f["e"]:
                a = ease((t - f["s"]) * T.FPS / 4)
                k = (t - f["s"]) / (f["e"] - f["s"])
                sc = f["base"] * (1 + 0.035 * k)
                im = f["img"].resize((round(f["img"].width * sc), round(f["img"].height * sc)), Image.LANCZOS)
                layer = np.empty_like(canvas); layer[:] = f["bg"]
                paste(layer, im, (W - im.width) // 2, (H - im.height) // 2)
                canvas = canvas * (1 - a) + layer * a
                full_on = a >= 0.5

        # caption (2-frame fade-in, cut out); hidden under full-screen assets
        for c, im in zip(caps if not full_on else [], cap_imgs):
            if c["s"] <= t < c["show_e"]:
                a = min(1, (t - c["s"]) * T.FPS / 2 + 0.5)
                paste(canvas, im, (W - im.width) // 2, CAP_CY - im.height // 2, a)
                break

        enc.stdin.write(np.clip(canvas, 0, 255).astype(np.uint8).tobytes())
        if i % 150 == 0: print(f"  {t:5.1f}s", flush=True)
    enc.stdin.close(); enc.wait(); dec.wait()
    print("wrote", out)


if __name__ == "__main__":
    main()
