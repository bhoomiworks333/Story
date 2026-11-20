# Builds vo/lines.json from per-line audio: vo/real/lNN.wav (real recording) if present, else vo/lNN.wav (TTS).
import json, os, numpy as np, soundfile as sf
lines = json.load(open('script.json')); t = 0.35; out = []
for i, L in enumerate(lines):
    f = f'vo/real/l{i:02d}.wav' if os.path.exists(f'vo/real/l{i:02d}.wav') else f'vo/l{i:02d}.wav'
    a, sr = sf.read(f)
    if a.ndim > 1: a = a.mean(1)
    t += L.get('pre', 0); d = len(a) / sr; hop = sr // 30
    env = [float(np.sqrt(np.mean(a[j:j + hop] ** 2))) for j in range(0, len(a), hop)]; mx = max(env) or 1
    out.append({**L, 'i': i, 'file': f, 'start': round(t, 3), 'dur': round(d, 3), 'env': [round(e / mx, 2) for e in env]})
    t += d + 0.28 + L.get('pause', 0) + L.get('post', 0)
json.dump({'lines': out, 'total': round(t + 0.2, 3)}, open('vo/lines.json', 'w'))
print('total', round(t + .2, 2)); [print(o['start'], o['dur'], o['file']) for o in out]
