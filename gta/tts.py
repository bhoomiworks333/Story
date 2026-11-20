# Generates one wav per line with Kokoro; writes vo/lines.json with timings.
import json, sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
M = '/tmp/claude-0/kokoro/'
k = Kokoro(M + 'kokoro-v1.0.onnx', M + 'voices-v1.0.bin')
VOICE = {'P': ('hm_psi', 1.0, 'en-us'), 'S': ('am_puck', 0.95, 'en-us')}
lines = json.load(open('script.json'))
t = 0.35; out = []
for i, L in enumerate(lines):
    v, sp, lang = VOICE[L['who']]
    say = L.get('say', L['text'])
    a, sr = k.create(say, voice=v, speed=sp, lang=lang)
    # trim silence
    nz = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, nz[0]-400): nz[-1]+1200]
    sf.write(f'vo/l{i:02d}.wav', a, sr)
    t += L.get('pre', 0)
    d = len(a) / sr
    # amplitude envelope at 30 fps for mouth animation
    hop = sr // 30
    env = [float(np.sqrt(np.mean(a[j:j+hop]**2))) for j in range(0, len(a), hop)]
    mx = max(env) or 1
    out.append({**L, 'i': i, 'start': round(t, 3), 'dur': round(d, 3), 'env': [round(e/mx, 2) for e in env]})
    t += d + 0.28 + L.get('pause', 0) + L.get('post', 0)
json.dump({'lines': out, 'total': round(t + 0.2, 3)}, open('vo/lines.json', 'w'))
print('total', t)
for o in out: print(o['start'], o['dur'], o['who'], o['text'])
