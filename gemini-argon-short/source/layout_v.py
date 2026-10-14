"""Base track for VERTICAL (1080x1920) footage: full frame <-> bottom-half split, no scaling.

usage: layout_v.py SRC OUT DURATION CROP_Y "t0:t1:from:to,..."
  p=0 full frame; p=1 split: source rows CROP_Y..CROP_Y+960 shown in the bottom half.
  Between states the frame slides down while the top edge wipes in, so nothing is ever upscaled.
"""
import subprocess, sys
from PIL import Image

src, out, dur, crop_y, spec = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
moves = [tuple(float(v) for v in m.split(":")) for m in spec.split(",")]
W, H, FPS = 1080, 1920, 30


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
n, fb = 0, W * H * 3
while n < round(dur * FPS):
    buf = dec.stdout.read(fb)
    if len(buf) < fb:
        break
    p = p_at(n / FPS)
    frame = Image.frombuffer("RGB", (W, H), buf)
    if p <= 0:
        canvas = frame
    else:
        top = round(960 * p)                      # top edge of the speaker window
        off = round((960 - crop_y) * p)           # how far the frame has slid down
        canvas = Image.new("RGB", (W, H), (17, 17, 17))
        src_top = top - off                       # first source row visible at the window's top edge
        canvas.paste(frame.crop((0, src_top, W, src_top + (H - top))), (0, top))
    enc.stdin.write(canvas.tobytes())
    n += 1
enc.stdin.close(); enc.wait(); dec.kill()
print("frames", n)
