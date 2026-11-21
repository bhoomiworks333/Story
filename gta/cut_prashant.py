# Denoised Prashant recording (vo/prashant/clean.wav) -> vo/real/lNN.wav for his lines.
import numpy as np, soundfile as sf, subprocess, os
a, sr = sf.read('vo/prashant/clean.wav')
WIN = {0: (0.9, 4.95), 2: (6.6, 8.12), 3: (8.12, 10.0), 5: (10.3, 12.5), 7: (13.35, 15.65), 9: (16.25, 18.65),
       11: (19.3, 20.35), 13: (20.5, 21.55), 15: (22.45, 23.3), 17: (23.85, 27.35), 19: (27.25, 30.65)}
for i, (s, e) in WIN.items():
    x = a[int(s * sr):int(e * sr)]
    hop = sr // 100; en = np.array([np.sqrt(np.mean(x[j:j + hop] ** 2)) for j in range(0, len(x) - hop, hop)])
    on = np.where(en > en.max() * .1)[0]
    i0 = max(0, on[0] * hop - int(.05 * sr)); i1 = min(len(x), (on[-1] + 1) * hop + int(.12 * sr))
    y = x[i0:i1].copy(); f = int(.01 * sr); y[:f] *= np.linspace(0, 1, f); y[-f * 3:] *= np.linspace(1, 0, f * 3)
    sf.write('vo/real/tmp.wav', y, sr)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'vo/real/tmp.wav', '-af',
                    'highpass=f=90,acompressor=threshold=-22dB:ratio=3:attack=5:release=80,loudnorm=I=-16:TP=-1.5',
                    '-ar', '48000', f'vo/real/l{i:02d}.wav'], check=True)
    print(i, f'{s + i0 / sr:.2f}-{s + i1 / sr:.2f}')
os.remove('vo/real/tmp.wav')
