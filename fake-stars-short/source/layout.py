"""Render the speaker base track (1080x1920): full-frame <-> bottom-half split with zoom moves.

usage: layout.py SRC OUT DURATION FACE_X FACE_Y "t0:t1:from:to,..."
  each segment eases the 'split amount' p from `from` to `to` between t0 and t1
  (p=0 whole frame fit to width, p=1 bottom-half split); outside segments p holds.
Frames stream ffmpeg -> python -> ffmpeg as raw RGB.
"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageFilter

src, out, dur, fx, fy, spec = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
moves = [tuple(float(v) for v in m.split(":")) for m in spec.split(",")]
W, H, SW, SH, FPS = 1080, 1920, 1440, 1080, 30
S_FIT, S_SPLIT = W / SW, 960 / SH
FIT_Y = (H - round(SH * W / SW)) // 2


def smooth(a):
    a = min(max(a, 0.0), 1.0)
    return a * a * (3 - 2 * a)


def p_at(t):
    p = moves[0][2]
    for t0, t1, a, b in moves:
        if t >= t1:
            p = b
        elif t >= t0:
            return a + (b - a) * smooth((t - t0) / (t1 - t0))
    return p


dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
n, frame_bytes = 0, SW * SH * 3
while n < round(dur * FPS):
    buf = dec.stdout.read(frame_bytes)
    if len(buf) < frame_bytes:
        break
    t = n / FPS
    p = p_at(t)
    # "full" = the whole landscape frame at its true ratio (1080 wide), centred on the dark base: no crop zoom
    s = S_FIT + (S_SPLIT - S_FIT) * p
    im = Image.frombuffer("RGB", (SW, SH), buf).resize((round(SW * s), round(SH * s)), Image.LANCZOS)
    x_split = min(0, max(W - round(SW * S_SPLIT), round(W / 2 - fx * S_SPLIT)))
    x = round(x_split * p)
    y = round(FIT_Y + (960 - FIT_Y) * p)
    canvas = Image.new("RGB", (W, H), (17, 17, 17))
    canvas.paste(im, (x, y))
    enc.stdin.write(canvas.tobytes())
    n += 1
enc.stdin.close(); enc.wait(); dec.kill()
print("frames", n)
