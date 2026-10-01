"""Frame compositor (v3): untouched talking head + top images + comment stack + captions.

usage: python3 render.py [--preview]   (preview = fast low-quality encode)
"""
import numpy as np, subprocess, os, sys, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import timeline as T

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, "build")
W, H = 1080, 1920
CARD_BOX = (65, 70, 1015, 510)          # top area images are fitted into
CAP_CY = int(0.865 * H)                 # caption box centre, measured from reference
FONT = ImageFont.truetype(os.path.join(HERE, "fonts", "Figtree-Medium.ttf"), 78)
POP_IN, POP_OUT = 0.23, 0.13            # seconds


def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)


def ease_out_back(x, k=1.4):
    x = min(1, max(0, x)) - 1
    return 1 + (k + 1) * x ** 3 + k * x ** 2


def asset(key):
    return Image.open(glob.glob(os.path.join(HERE, "assets", key + ".*"))[0]).convert("RGBA")


def with_shadow(im, blur=18, off=8, op=0.55, pad=40):
    """soft drop shadow so screenshots separate from the video behind them"""
    w, h = im.width + 2 * pad, im.height + 2 * pad
    sh = Image.new("L", (w, h), 0); sh.paste(int(255 * op), (pad, pad + off, pad + im.width, pad + off + im.height))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); out.putalpha(sh)
    out.alpha_composite(im, (pad, pad))
    return out


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
    bx0, by0, bx1, by1 = CARD_BOX
    cards = []
    for c in T.CARDS:
        im = asset(c["key"])
        s = min((bx1 - bx0) / im.width, (by1 - by0) / im.height)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        cards.append(dict(c, img=with_shadow(im)))
    return cards


def load_comments():
    C = T.COMMENTS; out = []
    for i, (k, s, tilt) in enumerate(zip(C["keys"], C["starts"], C["tilt"])):
        im = asset(k); sc = 900 / im.width
        im = im.resize((900, round(im.height * sc)), Image.LANCZOS)
        im = with_shadow(im, blur=14, off=6, op=0.6).rotate(tilt, Image.BICUBIC, expand=True)
        cy = 150 + i * 112                      # overlapping stack, like the reference
        out.append(dict(img=im, s=s, e=C["e"], cx=W // 2 + (-14 if i % 2 else 14), cy=cy))
    return out


def paste(dst, im, x, y, alpha=1.0):
    """alpha-composite RGBA PIL image onto float HxWx3 array"""
    a = np.asarray(im, np.float32) / 255
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(W, x + im.width), min(H, y + im.height)
    if x1 <= x0 or y1 <= y0: return
    sub = a[y0 - y:y1 - y, x0 - x:x1 - x]
    al = sub[..., 3:4] * alpha
    dst[y0:y1, x0:x1] = dst[y0:y1, x0:x1] * (1 - al) + sub[..., :3] * 255 * al


def pop(dst, im, cx, cy, t, s, e):
    """pop in (slight overshoot), quick fade/shrink out; (cx, cy) is the centre"""
    if not (s <= t < e + POP_OUT): return
    k_in = (t - s) / POP_IN
    a = min(1, k_in * 2.5)
    sc = 0.88 + 0.12 * ease_out_back(k_in)
    if t >= e:
        k = ease((t - e) / POP_OUT); a *= 1 - k; sc *= 1 - 0.04 * k
    if a <= 0: return
    if abs(sc - 1) > 0.002:
        im = im.resize((max(1, round(im.width * sc)), max(1, round(im.height * sc))), Image.BILINEAR)
    paste(dst, im, int(cx - im.width / 2), int(cy - im.height / 2), a)


def main():
    preview = "--preview" in sys.argv
    caps = T.captions(); cap_imgs = [caption_img(c["text"]) for c in caps]
    cards = load_cards(); comments = load_comments()
    bx0, by0, bx1, by1 = CARD_BOX

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
        canvas = np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32)

        for c in comments:
            pop(canvas, c["img"], c["cx"], c["cy"], t, c["s"], c["e"])
        for c in cards:  # vertically centred in the top area
            pop(canvas, c["img"], W // 2, (by0 + by1) // 2, t, c["s"], c["e"])

        # caption (2-frame fade-in, cut out)
        for c, im in zip(caps, cap_imgs):
            if c["s"] <= t < c["show_e"]:
                a = min(1, (t - c["s"]) * T.FPS / 2 + 0.5)
                paste(canvas, im, (W - im.width) // 2, CAP_CY - im.height // 2, a)
                break

        enc.stdin.write(np.clip(canvas, 0, 255).astype(np.uint8).tobytes())
        if i % 300 == 0: print(f"  {t:5.1f}s", flush=True)
    enc.stdin.close(); enc.wait(); dec.wait()
    print("wrote", out)


if __name__ == "__main__":
    main()
