# Cuts the AI-voice recording (vo/girl/raw.wav) into vo/real/lNN.wav for Stacky's lines.
import numpy as np, soundfile as sf, subprocess
a, sr = sf.read('vo/girl/raw.wav')
WIN = {1: (1.4, 6.0), 4: (6.9, 8.3), 6: (8.6, 10.5), 8: (10.7, 14.6), 10: (14.7, 15.9), 12: (15.95, 17.4),
       14: (17.6, 21.2), 16: (21.9, 24.6), 18: (25.3, 27.95), 20: (29.0, 31.65)}
for i, (s, e) in WIN.items():
    x = a[int(s * sr):int(e * sr)]
    hop = sr // 100; en = np.array([np.sqrt(np.mean(x[j:j + hop] ** 2)) for j in range(0, len(x) - hop, hop)])
    on = np.where(en > en.max() * .06)[0]
    i0 = max(0, on[0] * hop - int(.06 * sr)); i1 = min(len(x), (on[-1] + 1) * hop + int(.16 * sr))
    y = x[i0:i1].copy(); f = int(.01 * sr); y[:f] *= np.linspace(0, 1, f); y[-f * 3:] *= np.linspace(1, 0, f * 3)
    sf.write(f'vo/real/tmp.wav', y, sr)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'vo/real/tmp.wav', '-af',
                    'highpass=f=80,afftdn=nf=-30,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-16:TP=-1.5',
                    '-ar', '48000', f'vo/real/l{i:02d}.wav'], check=True)
    print(i, f'{s + i0 / sr:.2f}-{s + i1 / sr:.2f}', round(len(y) / sr, 2))
import os; os.remove('vo/real/tmp.wav')
