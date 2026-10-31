"""Halloween clip: jump-cut edit of the five poses in halloween/prashant_poses.webp (a 2x3 collage).

Beats: neutral -> BOOM shocked -> reading in horror -> defeated -> checks phone, "Usage limit reached" pops up.
Usage: python3 halloween/render.py   -> output/prashant_halloween.mp4
"""
import math, os, subprocess, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'output', 'prashant_halloween.mp4')
W, H, FPS = 1080, 1920, 30
CAPTION = ["the only Halloween costume", "that actually scares me:"]
BOLD = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
REG = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'
ORANGE = (217, 119, 87)

# (crop box in the collage, start time, push-in direction dx, dy, sound)
SHOTS = [
    ((2, 2, 504, 506),       0.0, (0.00, -0.01), 'tick'),
    ((516, 2, 1022, 506),    1.4, (0.00, 0.00),  'boom'),
    ((1033, 2, 1534, 506),   3.0, (0.00, -0.02), 'hit'),
    ((110, 516, 620, 1024),  4.3, (0.00, 0.02),  'hit'),
    ((731, 516, 1199, 1024), 5.6, (0.00, 0.0),   'hit'),
]
PHONE_T = 6.2
DUR = 8.8
PANEL_CY = 1010   # vertical centre of the photo on the 9:16 canvas

collage = Image.open(os.path.join(HERE, 'prashant_poses.webp')).convert('RGB')
# paint out the tail of the collage's own arrow that pointed at its phone inset (we draw a sharper phone)
_patch = collage.crop((1150, 696, 1186, 736)).transpose(Image.FLIP_LEFT_RIGHT).resize((26, 42))
collage.paste(_patch, (1185, 694))


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def back(x):  # ease-out with overshoot
    x = min(max(x, 0.0), 1.0)
    c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def prep(box):
    im = collage.crop(box)
    w, h = im.size
    s = 2 * W / w  # 2x supersampled panel at full canvas width
    im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=3, percent=60, threshold=2))
    bg = collage.crop(box).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new('RGB', (W, H), (18, 18, 18)), 0.45)
    return im, bg


PANELS = [prep(s[0]) for s in SHOTS]


def caption_layer():
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    font = ImageFont.truetype(BOLD, 60)
    d = ImageDraw.Draw(layer)
    lines, y = [], 175
    for line in CAPTION:
        lines.append(((W - d.textlength(line, font=font)) / 2, y, line))
        y += 76
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for x, y, line in lines:
        sd.text((x, y + 3), line, font=font, fill=(0, 0, 0, 200))
    shadow = shadow.filter(ImageFilter.GaussianBlur(7))
    for x, y, line in lines:
        d.text((x, y), line, font=font, fill='white')
    return Image.alpha_composite(shadow, layer)


def burst(d, cx, cy, r, width, color):
    for k in range(12):
        a = k * math.pi / 6 + 0.13
        x1, y1 = cx + math.cos(a) * r * 0.22, cy + math.sin(a) * r * 0.22
        x2, y2 = cx + math.cos(a) * r, cy + math.sin(a) * r
        d.line((x1, y1, x2, y2), fill=color, width=width)
        for x, y in ((x2, y2), (x1, y1)):
            d.ellipse((x - width / 2, y - width / 2, x + width / 2, y + width / 2), fill=color)


def phone_layer():
    pw, ph = 470, 820
    im = Image.new('RGBA', (pw + 80, ph + 80), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, 52, 40 + pw, 52 + ph), 70, fill=(0, 0, 0, 150))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((40, 40, 40 + pw, 40 + ph), 70, fill=(22, 22, 24))
    d.rounded_rectangle((56, 56, 24 + pw, 24 + ph), 56, fill=(250, 249, 245))
    d.rounded_rectangle((40 + pw / 2 - 60, 74, 40 + pw / 2 + 60, 108), 17, fill=(22, 22, 24))
    small = ImageFont.truetype(BOLD, 26)
    d.text((100, 76), '9:41', font=small, fill=(30, 30, 30))
    cx = 40 + pw / 2
    burst(d, cx, 330, 78, 20, ORANGE)
    big = ImageFont.truetype(BOLD, 50)
    for i, line in enumerate(['Usage limit', 'reached']):
        d.text((cx - d.textlength(line, font=big) / 2, 450 + i * 62), line, font=big, fill=(25, 25, 25))
    body = ImageFont.truetype(REG, 32)
    for i, line in enumerate(['Please try again', 'in 5 hours.']):
        d.text((cx - d.textlength(line, font=body) / 2, 610 + i * 44), line, font=body, fill=(90, 90, 90))
    return im


CAP = caption_layer()
PHONE = phone_layer()


def shot_at(t):
    i = max(k for k, s in enumerate(SHOTS) if s[1] <= t)
    return i, t - SHOTS[i][1]


def frame(t):
    i, lt = shot_at(t)
    panel, bg = PANELS[i]
    nxt = SHOTS[i + 1][1] if i + 1 < len(SHOTS) else DUR
    p = lt / (nxt - SHOTS[i][1])
    dx, dy = SHOTS[i][2]
    zoom = 1.0 + 0.06 * p + 0.10 * (1 - ease(lt / 0.2))   # slow push + punch on the cut
    ox, oy = dx * p * W, dy * p * H * 0.5
    if SHOTS[i][3] == 'boom':                               # decaying shake on the shocked pose
        s = math.exp(-lt * 6)
        ox += 22 * s * math.sin(lt * 80)
        oy += 16 * s * math.cos(lt * 67)
    img = bg.copy().convert('RGBA')
    pw, ph = panel.size[0] / 2 * zoom, panel.size[1] / 2 * zoom
    # panel fills the width; crop the zoomed overflow so it stays a clean full-width band
    scaled = panel.resize((int(pw), int(ph)), Image.LANCZOS)
    x = int((W - pw) / 2 + ox)
    y = int(PANEL_CY - ph / 2 + oy)
    band_h = int(panel.size[1] / 2)
    band_y = PANEL_CY - band_h // 2
    band = Image.new('RGB', (W, band_h))
    band.paste(scaled, (x, y - band_y))
    img.paste(band, (0, band_y))
    if SHOTS[i][3] == 'boom' and lt < 0.12:
        img = Image.alpha_composite(img, Image.new('RGBA', (W, H), (255, 255, 255, int(130 * (1 - lt / 0.12)))))
    if t >= PHONE_T:
        k = back((t - PHONE_T) / 0.35)
        ph_im = PHONE.rotate(-6 + 3 * (1 - k), Image.BICUBIC, expand=True)
        sc = 0.3 + 0.7 * k
        ph_im = ph_im.resize((max(1, int(ph_im.width * sc)), max(1, int(ph_im.height * sc))), Image.LANCZOS)
        cx, cy = 800, 1470 + (1 - min(k, 1)) * 300
        img.alpha_composite(ph_im, (int(cx - ph_im.width / 2), int(cy - ph_im.height / 2)))
    cap = CAP
    if t < 0.2:
        cap = CAP.copy()
        cap.putalpha(cap.getchannel('A').point(lambda v: int(v * t / 0.2)))
    return Image.alpha_composite(img, cap).convert('RGB')


def audio(path):
    sr = 44100
    n = int(DUR * sr)
    rng = np.random.default_rng(1)
    out = np.zeros(n)

    def add(t0, sig):
        i = int(t0 * sr)
        out[i:i + len(sig)] += sig[: n - i]

    def tone(f0, f1, dur, decay, amp):
        tt = np.arange(int(dur * sr)) / sr
        f = f1 + (f0 - f1) * np.exp(-tt * 8)
        return amp * np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt * decay)

    def noise(dur, decay, amp, smooth=1):
        x = rng.standard_normal(int(dur * sr))
        if smooth > 1:
            x = np.convolve(x, np.ones(smooth) / smooth, 'same')
        return amp * x * np.exp(-np.arange(len(x)) / sr * decay)

    for _, t0, _, kind in SHOTS:
        if kind == 'boom':
            add(t0, tone(120, 42, 2.2, 2.6, 1.0)); add(t0, noise(0.4, 18, 0.5, 6))
        elif kind == 'hit':
            add(t0 - 0.12, noise(0.16, 6, 0.10, 12) * np.linspace(0, 1, int(0.16 * sr)))  # whoosh in
            add(t0, tone(180, 70, 0.5, 9, 0.6)); add(t0, noise(0.12, 40, 0.3, 3))
        else:
            add(t0 + 0.05, tone(1400, 1400, 0.08, 60, 0.25))
    # phone notification: two soft bells
    for k, f in enumerate((1318.5, 1760.0)):
        add(PHONE_T + 0.03 + k * 0.13, tone(f, f, 0.9, 5, 0.32)); add(PHONE_T + 0.03 + k * 0.13, tone(2 * f, 2 * f, 0.5, 9, 0.08))
    # sad falling note under the defeated pose
    add(SHOTS[3][1] + 0.15, tone(220, 165, 1.1, 2.5, 0.2))
    out += 0.004 * rng.standard_normal(n)
    out = np.tanh(out * 1.2) / np.tanh(1.2)
    fade = int(0.25 * sr)
    out[-fade:] *= np.linspace(1, 0, fade)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((out * 30000).astype(np.int16).tobytes())


if __name__ == '__main__':
    tmp = tempfile.mkdtemp()
    wav = os.path.join(tmp, 'a.wav')
    audio(wav)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                           '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                           '-crf', '18', '-preset', 'slow', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                           '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
    for k in range(int(DUR * FPS)):
        ff.stdin.write(frame(k / FPS).tobytes())
    ff.stdin.close()
    ff.wait()
    print('wrote', os.path.abspath(OUT))
