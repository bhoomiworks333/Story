"""Spectral repair: suppress a child's sustained 'aah' under the speaker's voice.

Tracks the child's pitch (F0 600-780 Hz) frame by frame inside one window and
notches only narrow bands around its harmonics, fading the repair in and out.
usage: python3 kidfix.py in.wav out.wav
"""
import sys, wave
import numpy as np

T0, T1, RAMP = 20.30, 21.65, 0.08   # repair window (s) and fade length
F0_LO, F0_HI = 550, 790
HARMONICS = range(1, 9)
HALF_BW = 35.0       # Hz either side of each harmonic
ATTEN_DB = 24.0

w = wave.open(sys.argv[1]); sr = w.getframerate(); ch = w.getnchannels()
x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64).reshape(-1, ch) / 32768
N, hop = 4096, 512
win = np.hanning(N)
freqs = np.fft.rfftfreq(N, 1 / sr)
mono = x.mean(axis=1)


def track_f0(frame_spec_db):
    best, bf = -1e9, None
    for f0 in np.arange(F0_LO, F0_HI, 2.5):
        s = 0.0
        for k in range(2, 7):
            j = int(round(f0 * k / sr * N))
            lo, hi = int(round((f0 * k - 90) / sr * N)), int(round((f0 * k + 90) / sr * N))
            s += frame_spec_db[j - 1:j + 2].max() - np.median(frame_spec_db[lo:hi])
        if s > best:
            best, bf = s, f0
    return bf


out = x.copy()
a = int((T0 - 0.3) * sr); b = int((T1 + 0.3) * sr)   # process a padded region, overlap-add it back
seg = x[a:b]
acc = np.zeros_like(seg); norm = np.zeros(len(seg))
for i in range(0, len(seg) - N, hop):
    t = (a + i + N / 2) / sr
    g = min(1.0, max(0.0, (t - T0) / RAMP), max(0.0, (T1 - t) / RAMP))
    gain = np.ones(len(freqs))
    if g > 0:
        mdb = 20 * np.log10(np.abs(np.fft.rfft(mono[a + i:a + i + N] * win)) + 1e-9)
        f0 = track_f0(mdb)
        for k in HARMONICS:
            band = np.abs(freqs - f0 * k) < HALF_BW
            gain[band] = 10 ** (-ATTEN_DB * g / 20)
    for c in range(ch):
        X = np.fft.rfft(seg[i:i + N, c] * win)
        acc[i:i + N, c] += np.fft.irfft(X * gain, N) * win
    norm[i:i + N] += win ** 2
valid = norm > 1e-3
rep = seg.copy()
rep[valid] = acc[valid] / norm[valid][:, None]
# only replace the inner part where overlap-add is fully supported
inner = slice(N, len(seg) - N)
out[a + inner.start:a + inner.stop] = rep[inner]

o = wave.open(sys.argv[2], "wb"); o.setnchannels(ch); o.setsampwidth(2); o.setframerate(sr)
o.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes()); o.close()
