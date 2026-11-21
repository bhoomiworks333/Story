# Prashant's clean recording (vo/prashant/raw2.wav) -> vo/real/lNN.wav for his lines. Windows from an energy map.
import numpy as np, soundfile as sf, subprocess, os
a, sr = sf.read('vo/prashant/raw2.wav')
WIN = {0: (1.29, 4.60), 2: (5.65, 6.39), 3: (7.06, 8.43), 5: (9.53, 11.39), 7: (12.47, 14.23), 9: (15.28, 17.29),
       11: (18.67, 19.40), 13: (20.51, 21.13), 15: (22.41, 22.89), 17: (24.01, 26.80), 19: (27.99, 30.60)}
for i, (s, e) in WIN.items():
    y = a[int((s - .06) * sr):int((e + .15) * sr)].copy()
    f = int(.01 * sr); y[:f] *= np.linspace(0, 1, f); y[-f * 4:] *= np.linspace(1, 0, f * 4)
    sf.write('vo/real/tmp.wav', y, sr)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'vo/real/tmp.wav', '-af',
                    'highpass=f=80,acompressor=threshold=-22dB:ratio=3:attack=5:release=80,loudnorm=I=-16:TP=-1.5',
                    '-ar', '48000', f'vo/real/l{i:02d}.wav'], check=True)
    print(i, round(len(y) / sr, 2))
os.remove('vo/real/tmp.wav')
