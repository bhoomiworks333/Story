"""Halloween clip: animates halloween/prashant_costume.webp into a 9:16 meme video.

Beats: caption on, handheld drift, punch-in on the "Daily limit reached" card with a boom, hold, ease back out.
Usage: python3 halloween/render.py   -> output/prashant_halloween.mp4
"""
import math, os, subprocess, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'output', 'prashant_halloween.mp4')
W, H, FPS, DUR = 1080, 1920, 30, 6.0
SS = 2  # supersample the source so zooms stay sharp
CAPTION = ["the only Halloween costume", "that actually scares me:"]
FONT = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
PUNCH_T = 2.4                     # moment of the punch-in
CARD = (0.515, 0.50)             # card centre in normalised source coords

src = Image.open(os.path.join(HERE, 'prashant_costume.webp')).convert('RGB')
base = src.resize((W * SS, H * SS), Image.LANCZOS)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def camera(t):
    """Returns zoom, centre (normalised), rotation (deg)."""
    # handheld drift: a few incommensurate sines
    dx = 0.004 * math.sin(t * 1.3) + 0.002 * math.sin(t * 3.1 + 1)
    dy = 0.003 * math.sin(t * 1.1 + 2) + 0.0015 * math.sin(t * 2.7)
    rot = 0.35 * math.sin(t * 0.9) + 0.15 * math.sin(t * 2.3 + 0.5)
    zoom, cx, cy = 1.04 + 0.01 * t / DUR, 0.5, 0.5
    # punch-in: snap in fast, hold, ease back out
    if t >= PUNCH_T:
        k = ease((t - PUNCH_T) / 0.12) * (1 - ease((t - PUNCH_T - 1.6) / 0.6))
        zoom += 0.42 * k
        cx += (CARD[0] - cx) * k
        cy += (CARD[1] - cy) * k
        # impact shake that decays
        s = math.exp(-(t - PUNCH_T) * 7) * k
        dx += 0.010 * s * math.sin(t * 90)
        dy += 0.008 * s * math.cos(t * 77)
        rot += 1.2 * s * math.sin(t * 60)
    return zoom, cx + dx, cy + dy, rot


def caption_layer():
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    font = ImageFont.truetype(FONT, 58)
    d = ImageDraw.Draw(layer)
    y = 150
    lines = []
    for line in CAPTION:
        w = d.textlength(line, font=font)
        lines.append(((W - w) / 2, y, line))
        y += 72
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for x, y, line in lines:
        sd.text((x, y + 3), line, font=font, fill=(0, 0, 0, 170))
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    for x, y, line in lines:
        d.text((x, y), line, font=font, fill='white')
    return Image.alpha_composite(shadow, layer)


CAP = caption_layer()


def frame(t):
    zoom, cx, cy, rot = camera(t)
    # crop window in supersampled source, then rotate + resize
    cw, ch = W * SS / zoom, H * SS / zoom
    x0 = min(max(cx * W * SS - cw / 2, 0), W * SS - cw)
    y0 = min(max(cy * H * SS - ch / 2, 0), H * SS - ch)
    pad = 0.04  # extra margin so rotation never shows edges
    box = (x0 - cw * pad, y0 - ch * pad, x0 + cw * (1 + pad), y0 + ch * (1 + pad))
    crop = base.transform((int(W * (1 + 2 * pad)), int(H * (1 + 2 * pad))), Image.EXTENT, box,
                          Image.BICUBIC, fillcolor=(235, 235, 232))
    crop = crop.rotate(rot, Image.BICUBIC)
    l, tp = int(W * pad), int(H * pad)
    img = crop.crop((l, tp, l + W, tp + H)).convert('RGBA')
    # brief white flash on impact
    if PUNCH_T <= t < PUNCH_T + 0.15:
        a = int(110 * (1 - (t - PUNCH_T) / 0.15))
        img = Image.alpha_composite(img, Image.new('RGBA', (W, H), (255, 255, 255, a)))
    cap = CAP
    if t < 0.25:
        cap = CAP.copy()
        cap.putalpha(cap.getchannel('A').point(lambda v: int(v * t / 0.25)))
    return Image.alpha_composite(img, cap).convert('RGB')


def audio(path):
    sr = 44100
    n = int(DUR * sr)
    t = np.arange(n) / sr
    out = 0.02 * np.random.default_rng(1).standard_normal(n) * 0.15  # faint room tone
    i = int(PUNCH_T * sr)
    tb = t[: n - i]
    env = np.exp(-tb * 3.2)
    f = 55 * np.exp(-tb * 1.5) + 38
    boom = np.sin(2 * np.pi * np.cumsum(f) / sr) * env
    boom += 0.3 * np.random.default_rng(2).standard_normal(len(tb)) * np.exp(-tb * 25)
    out[i:] += 0.9 * boom
    out = np.tanh(out * 1.4) / np.tanh(1.4)
    pcm = (out * 32000).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())


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
