# Step 6.1: person matte for the Version B cut-out (U2Net human-seg, temporally smoothed)
import subprocess, numpy as np, cv2, onnxruntime as ort, sys
W, H = 1080, 1920
sess = ort.InferenceSession("models/u2net_human_seg.onnx", providers=["CPUExecutionProvider"])
MEAN, STD = np.array([0.485, 0.456, 0.406]), np.array([0.229, 0.224, 0.225])
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", "work/face.mp4", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                        "-c:v", "ffv1", "work/matte.mkv"], stdin=subprocess.PIPE)
prev, n = None, 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    x = cv2.resize(img, (320, 320), interpolation=cv2.INTER_AREA) / 255.0
    x = ((x - MEAN) / STD).transpose(2, 0, 1)[None].astype(np.float32)
    m = sess.run(None, {"input.1": x})[0][0, 0]
    m = (m - m.min()) / (m.max() - m.min() + 1e-6)
    m = cv2.resize(m, (W, H), interpolation=cv2.INTER_CUBIC)
    prev = m if prev is None else 0.65 * m + 0.35 * prev       # damp frame-to-frame flicker
    a = np.clip((prev - 0.15) / 0.7, 0, 1)                         # tighten the soft edge band
    enc.stdin.write((a * 255).astype(np.uint8).tobytes()); n += 1
    if n % 200 == 0: print(n, flush=True)
enc.stdin.close(); enc.wait(); print("frames", n)
