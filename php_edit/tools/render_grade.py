# Grade B: ffmpeg global chain -> face-only shine pass (smoothed boxes) -> encode.
import sys, json, subprocess, numpy as np
sys.path.insert(0, sys.argv[1]); import faceshine
pose, src, out = sys.argv[2:5]
W, H, N, CUT = 576, 1024, 279, 120
P = json.load(open(pose))
raw = np.array([P[i if i < CUT else i + 27]['box'] for i in range(N)], float)
box = np.empty_like(raw)
for a, b in [(0, CUT), (CUT, N)]:            # smooth within each segment only
    seg = raw[a:b]
    for i in range(len(seg)):
        box[a + i] = seg[max(0, i - 6):i + 7].mean(0)
G = ("eq=contrast=1.05:saturation=1.06:brightness=-0.02,hqdn3d=1.5:1.5:3:3,unsharp=5:5:0.35,"
     "colorbalance=rs=0.03:bs=-0.02:rm=0.06:gm=-0.01:bm=-0.04")
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-vf', G, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '30', '-i', '-',
                        '-an', '-c:v', 'libx264', '-crf', '12', '-preset', 'slow', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
n = 0
while True:
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    f = np.frombuffer(b, np.uint8).reshape(H, W, 3)
    o, _ = faceshine.apply(f, box[n], gamma=1.0, shine_keep=0.35)
    enc.stdin.write(o.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print(n, 'frames')
