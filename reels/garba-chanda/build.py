"""Builds the garba chanda reel from the single wide take.

Usage: python3 build.py <source.mp4> <counting_sfx.mp3> <out.mp4>
Run `node snap_assets.js` first so build/*.png exists.

Timeline (src = seconds in the take, out = src + HOOK):
  out 0.0-0.9   hands close-up from the end of the take (src 28.95+), muted, counting SFX
  out 0.9-1.8   hands close-up of the real opening (src 0-0.9), SFX stops as he speaks
  out 1.8       hard cut to the face at 110% on "ek second"
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageFilter

SRC, SFX, OUT = sys.argv[1:4]
DIR = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(DIR, 'build')
W, H, FPS = 1080, 1920, 30
HOOK_FRAMES = 27                 # 0.9 s of extra hands footage in front
HOOK = HOOK_FRAMES / FPS
HOOK_SRC = 28.95                 # he is counting notes here, with his face out of the crop
OPEN_END = 0.9                   # first word ("...ek second") starts here in the take
HANDS = (270, 850, 540, 960)     # x, y, w, h crop for the hands close-up
CAP_Y = 1440                     # caption centre: inside the bottom third, above Instagram's UI

tl = json.load(open(os.path.join(DIR, 'timeline.json')))
caps = [(a, b, Image.open(os.path.join(BUILD, f'cap{i}.png')).convert('RGBA'))
        for i, (a, b, _) in enumerate(tl['captions'])]
pops = [dict(p, img=Image.open(os.path.join(BUILD, p['asset'] + '.png')).convert('RGBA')) for p in tl['popups']]


def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def zoom_at(t):
    """(scale, centre_x, centre_y) for source time t."""
    if OPEN_END <= t < 3.2:                       # punch-in on "ek second", back out on "Nahi, seriously"
        return 1.10, 540, 900
    if 11.25 <= t < 14.4:                         # slow push-in under "₹500 = ???"
        return 1.0 + 0.06 * smooth((t - 11.25) / 3.15), 540, 800
    return 1.0, 540, 960


def crop_resize(img, x, y, w, h):
    x = min(max(x, 0), W - w)
    y = min(max(y, 0), H - h)
    return img.resize((W, H), Image.LANCZOS, box=(x, y, x + w, y + h))


def pop_scale_alpha(dt, dur, base=1.0):
    """Pop-in (ease-out-back over 0.2 s) and a quick 0.12 s shrink-fade on exit."""
    if dt < 0.2:
        u = dt / 0.2
        c = 1.70158
        s = 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2
        return base * (0.5 + 0.5 * s), min(1.0, dt / 0.08)
    left = dur - dt
    if left < 0.12:
        u = left / 0.12
        return base * (0.85 + 0.15 * u), u
    return base, 1.0


def paste_center(frame, img, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    if scale != 1.0:
        img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)
    if rot:
        img = img.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1.0:
        a = img.getchannel('A').point(lambda v: int(v * alpha))
        img = img.copy()
        img.putalpha(a)
    frame.alpha_composite(img, (round(cx - img.width / 2), round(cy - img.height / 2)))


def compose(raw, t, hook):
    img = Image.fromarray(raw, 'RGB')
    if hook:
        img = crop_resize(img, *HANDS).filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    else:
        z, cx, cy = zoom_at(t)
        if z != 1.0:
            w, h = round(W / z), round(H / z)
            img = crop_resize(img, round(cx - w / 2), round(cy - h / 2), w, h)
    if hook:
        return img
    frame = img.convert('RGBA')
    for p in pops:
        if p['in'] <= t < p['out']:
            s, a = pop_scale_alpha(t - p['in'], p['out'] - p['in'], p.get('scale', 1.0))
            paste_center(frame, p['img'], p['cx'], p['cy'], s, a, p.get('rot', 0))
    for a, b, im in caps:
        if a <= t < b:
            s = 0.92 + 0.08 * smooth((t - a) / 0.1)
            paste_center(frame, im, W / 2, CAP_Y, s)
    return frame.convert('RGB')


def frames(start=None, count=None):
    cmd = ['ffmpeg', '-v', 'error']
    if start is not None:
        cmd += ['-ss', f'{start}']
    cmd += ['-i', SRC]
    if count is not None:
        cmd += ['-frames:v', str(count)]
    cmd += ['-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        yield np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    p.wait()


tmp_v = os.path.join(BUILD, 'video_only.mp4')
tmp_a = os.path.join(BUILD, 'audio.wav')
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                        '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                        '-pix_fmt', 'yuv420p', tmp_v], stdin=subprocess.PIPE)
n_out = 0
for raw in frames(HOOK_SRC, HOOK_FRAMES):
    enc.stdin.write(compose(raw, 0, True).tobytes()); n_out += 1
for i, raw in enumerate(frames()):
    t = i / FPS
    enc.stdin.write(compose(raw, t, t < OPEN_END).tobytes()); n_out += 1
    if i % 150 == 0:
        print(f'frame {n_out}', flush=True)
enc.stdin.close(); enc.wait()
dur = n_out / FPS

# Audio: take audio delayed by HOOK, counting SFX from 0 until he starts talking, then loudness-normalised.
sfx_len = HOOK + OPEN_END - 0.05
fc = (f"[0:a]aresample=48000,adelay={int(HOOK*1000)}:all=1[d];"
      f"[1:a]aresample=48000,atrim=6.0:{6.0+sfx_len:.3f},asetpts=PTS-STARTPTS,volume=-3dB,"
      f"afade=t=out:st={sfx_len-0.06:.3f}:d=0.06[s];"
      f"[d][s]amix=inputs=2:normalize=0:duration=first,atrim=0:{dur:.3f},"
      f"loudnorm=I=-16:TP=-1.5:LRA=11[a]")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-i', SFX, '-filter_complex', fc, '-map', '[a]',
                '-ar', '48000', tmp_a], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp_v, '-i', tmp_a, '-c:v', 'copy', '-c:a', 'aac',
                '-b:a', '192k', '-shortest', '-movflags', '+faststart', OUT], check=True)
print(f'wrote {OUT} ({dur:.2f} s, {n_out} frames)')
