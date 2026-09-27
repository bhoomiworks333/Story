# Synthesised score, sound design and voiceover mix, locked to the edit in js/shots.js.
# Output: soundtrack.wav (48 kHz stereo). Every sound is generated here; no samples or licensed music are used.
import json, re, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly

SR = 48000
src = open('js/shots.js').read()
DUR = float(re.search(r'export const DUR = ([\d.]+)', src).group(1))
VO_AT = [float(x) for x in re.search(r'export const VO_AT = \[([^\]]+)\]', src).group(1).split(',')]
N = int(DUR * SR)
rng = np.random.default_rng(7)
music = np.zeros((N, 2)); amb = np.zeros((N, 2)); sfx = np.zeros((N, 2)); vo = np.zeros(N)

def T(n): return np.arange(n) / SR
def bp(x, lo, hi, order=2): return sosfilt(butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, f, order=2): return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, order=2): return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)
def env(n, a=0.005, r=0.3): t = T(n); return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)
def add(buf, t, sig, g=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or i + len(sig) <= 0: return
    if i < 0: sig = sig[-i:]; i = 0
    sig = sig[:N - i]
    l, r = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
    buf[i:i + len(sig), 0] += sig * g * l; buf[i:i + len(sig), 1] += sig * g * r
def span(a, b): return slice(int(a * SR), min(N, int(b * SR)))
def ramp(a, b, fi=0.3, fo=0.3):
    t = np.arange(N) / SR
    return np.clip(np.minimum((t - a) / max(fi, 1e-3), (b - t) / max(fo, 1e-3)), 0, 1)
def note(m): return 440 * 2 ** ((m - 69) / 12)

# ============ ANCIENT (0 – 15.2) ============
t_all = np.arange(N) / SR
A_END = 15.2
# wind: filtered noise with slow gusts
w = lp(rng.standard_normal(N), 500) * 0.9
gust = 0.55 + 0.45 * np.sin(2 * np.pi * 0.09 * t_all + 1) * np.sin(2 * np.pi * 0.23 * t_all)
wind = w * gust * ramp(0, A_END, 1.2, 0.02)
amb[:, 0] += wind * 0.10; amb[:, 1] += np.roll(wind, 900) * 0.10
# tanpura: Sa (D2/D3) and Pa (A2), buzzing harmonics, plucked cycle
def tanpura_pluck(f, dur=2.6):
    n = int(dur * SR); t = T(n)
    s = sum((1 / k ** 0.9) * np.sin(2 * np.pi * f * k * t * (1 + 0.0007 * k)) * (1 + 0.35 * np.sin(2 * np.pi * (0.8 + k * 0.13) * t)) for k in range(1, 14))
    return s * env(n, 0.02, 1.6) * 0.06
cyc = [note(45), note(50), note(50), note(38)]  # Pa Sa Sa Sa(low)
tp = 0.4; k = 0
while tp < A_END - 0.5:
    add(music, tp, tanpura_pluck(cyc[k % 4]), 1.0 * min(1, tp / 3 + 0.3), pan=-0.3 + 0.2 * (k % 2)); tp += 0.62; k += 1
# bansuri phrases (D major pentatonic + a touch of Kafi colour), breathy sine with vibrato
def flute(m, dur, vib=5.2):
    n = int(dur * SR); t = T(n); f = note(m)
    ph = 2 * np.pi * np.cumsum(f * (1 + 0.006 * np.sin(2 * np.pi * vib * t) * np.minimum(1, t / 0.4))) / SR
    s = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    breath = bp(rng.standard_normal(n), f * 0.8, f * 3) * 0.12
    e = np.minimum(1, t / 0.09) * np.minimum(1, (dur - t) / 0.25).clip(0)
    return (s + breath) * e * 0.07
phr = [(1.2, 74, 1.0), (2.2, 76, 0.5), (2.7, 78, 1.4), (4.3, 81, 0.6), (4.9, 78, 0.5), (5.4, 76, 1.8),
       (8.1, 74, 0.6), (8.7, 76, 0.4), (9.1, 78, 1.0), (10.3, 81, 0.5), (10.8, 83, 0.9), (11.9, 81, 0.5), (12.4, 78, 0.5), (12.9, 76, 1.2)]
for st, m, d in phr: add(music, st, flute(m, d), 1.0, pan=0.25)
# hand drums: low thump + slap, pattern from the drain shot, accelerating into the cut
def thump(f0=95, g=1.0):
    n = int(0.45 * SR); t = T(n); f = f0 * np.exp(-t * 9) + f0 * 0.55
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * g
def slap(g=1.0):
    n = int(0.12 * SR); return bp(rng.standard_normal(n), 700, 3500) * env(n, 0.001, 0.03) * g
beat = 60 / 88
for i in range(64):
    tb = 7.6 + i * beat / 2
    if tb >= 14.2: break
    if i % 4 == 0: add(music, tb, thump(), 0.32)
    if i % 4 == 3: add(music, tb, thump(120), 0.16)
    if i % 2 == 1: add(music, tb, slap(), 0.10, pan=0.3)
# drum roll + rising air into the cut
tb, gap = 14.2, beat / 2
while tb < A_END - 0.03:
    add(music, tb, thump(110, 0.7), 0.22 + 0.2 * (tb - 14.2)); add(music, tb + gap / 2, slap(), 0.1 + 0.1 * (tb - 14.2)); gap *= 0.84; tb += max(gap, 0.035)
n = int((A_END - 13.9) * SR); riser = hp(rng.standard_normal(n), 800) * np.linspace(0, 1, n) ** 2 * 0.08
add(music, 13.9, riser, 1.0)
# water: trickle in the drain shot, lapping at the reservoir
n = int(2.4 * SR); trick = bp(rng.standard_normal(n), 1200, 5000) * (0.4 + 0.6 * np.abs(lp(rng.standard_normal(n), 12)) * 6).clip(0, 1.4)
add(amb, 7.6, trick * ramp(0, 2.4, 0.2, 0.3)[:n] * 0.08, 1.0)
n = int(2.5 * SR); lap = lp(rng.standard_normal(n), 900) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.7 * T(n)))
add(amb, 11.8, lap * np.minimum(1, T(n) / 0.3) * 0.12, 1.0, pan=-0.2)
# cut everything ancient at 15.2 exactly
for b in (music, amb): b[int(A_END * SR):] = 0

# ============ HARD CUT / MODERN ROOM (15.2 – 29.6) ============
M_END = 29.6
room = lp(rng.standard_normal(N), 300) * 0.02 + 0.006 * np.sin(2 * np.pi * 100 * t_all)          # tube-light hum
fan = lp(rng.standard_normal(N), 700) * (0.6 + 0.4 * np.sin(2 * np.pi * 3.1 * t_all)) * 0.02       # ceiling fan
roomtone = (room + fan) * ramp(15.5, M_END, 0.6, 0.4)
amb[:, 0] += roomtone; amb[:, 1] += np.roll(roomtone, 400)
def vibrate(dur=0.5):
    n = int(dur * SR); t = T(n); s = np.sign(np.sin(2 * np.pi * 172 * t)) * 0.5 + np.sin(2 * np.pi * 172 * t)
    return lp(s, 1500) * (np.sin(2 * np.pi * 2.0 / dur * t) > -0.2) * np.minimum(1, t / 0.01) * 0.12
def ping(f1=1318, f2=1760):
    n = int(0.28 * SR); t = T(n); a = np.sin(2 * np.pi * f1 * t) * env(n, 0.002, 0.05); b = np.roll(np.sin(2 * np.pi * f2 * t) * env(n, 0.002, 0.08), int(0.07 * SR))
    return (a + b) * 0.09
add(sfx, 15.8, vibrate(0.55), 1.0, pan=0.3)
# register: page, pen scratches following the writing
n = int(0.35 * SR); add(sfx, 16.62, bp(rng.standard_normal(n), 600, 6000) * env(n, 0.01, 0.08) * 0.25, 1.0)
tt = 16.72
while tt < 18.5:
    d = 0.06 + rng.random() * 0.12; n = int(d * SR)
    add(sfx, tt, bp(rng.standard_normal(n), 2500, 9000) * np.sin(np.pi * T(n) / d) * 0.09, 1.0, pan=0.1); tt += d + rng.random() * 0.05
n = int(0.45 * SR); buzz = lp(np.sign(np.sin(2 * np.pi * 440 * T(n))) + np.sign(np.sin(2 * np.pi * 554 * T(n))), 3000) * 0.04
add(sfx, 17.9, buzz * np.minimum(1, (0.45 - T(n)) / 0.03).clip(0), 1.0, pan=-0.5)                # gate buzzer
# chat: a ping per message, vibrations
for i in range(9): add(sfx, 18.6 + i / 4.2, ping(), 0.9, pan=0.2 + (i % 3) * 0.1)
add(sfx, 19.3, vibrate(0.4), 0.8); add(sfx, 20.1, vibrate(0.4), 0.8)
# ledger: keyboard, a sigh of the fan, a calculator beep
tt = 20.7
while tt < 22.6:
    n = int(0.03 * SR); add(sfx, tt, bp(rng.standard_normal(n), 1500, 6000) * env(n, 0.001, 0.008) * 0.25, 1.0, pan=-0.3); tt += 0.07 + rng.random() * 0.13
n = int(0.12 * SR); add(sfx, 22.2, np.sin(2 * np.pi * 2800 * T(n)) * 0.03, 1.0, pan=-0.4)
# flood: pings and buzzes pile up, then everything stops dead at 23.8
for i in range(13): add(sfx, 22.8 + i / 13, ping(1318 + (i % 4) * 110, 1760 + (i % 3) * 90), 0.9 + i * 0.05, pan=(i % 5 - 2) * 0.3)
add(sfx, 22.8, np.tile(vibrate(0.25), 4), 1.2)
n = int(1.0 * SR); ring = (np.sin(2 * np.pi * 880 * T(n)) + np.sin(2 * np.pi * 1109 * T(n))) * (np.sin(2 * np.pi * 8 * T(n)) > 0) * 0.03
add(sfx, 22.8, ring * np.linspace(0.3, 1, n), 1.0, pan=-0.3)
sfx[int(23.8 * SR):int(26.4 * SR)] = 0
add(sfx, 26.5, ping(988, 1318), 0.6)                                                            # the screen lights up once
# low pulse under the question, dropping out before the answer
n = int(5.0 * SR); pulse = np.sin(2 * np.pi * 55 * T(n)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.5 * T(n))) * np.minimum(1, T(n) / 1.5) * np.minimum(1, (5.0 - T(n)) / 0.8).clip(0) * 0.05
add(music, 23.9, pulse, 1.0)

# ============ RESOLUTION: modern music (29.6 – end) ============
def piano(m, dur=2.5, vel=1.0):
    n = int(dur * SR); t = T(n); f = note(m)
    s = sum((0.6 ** (k - 1)) * np.sin(2 * np.pi * f * k * t * (1 + 0.0004 * k * k)) * np.exp(-t * (0.9 + 0.7 * k)) for k in range(1, 8))
    return s * np.minimum(1, t / 0.004) * 0.11 * vel
def pad(ms, dur, g=0.03):
    n = int(dur * SR); t = T(n)
    s = sum(np.sin(2 * np.pi * note(m) * t) + 0.5 * np.sin(2 * np.pi * note(m) * 1.004 * t) + 0.3 * np.sin(2 * np.pi * note(m + 12) * t) for m in ms)
    return lp(s, 2500) * np.minimum(1, t / 0.8) * np.minimum(1, (dur - t) / 1.0).clip(0) * g / len(ms)
bpm = 96; b = 60 / bpm; t0 = 29.7
prog = [[50, 57, 62, 66], [47, 54, 59, 62], [43, 50, 55, 59], [45, 52, 57, 61]]  # D  Bm  G  A
bar = 4 * b
for i in range(6):
    ch = prog[i % 4]; tb = t0 + i * bar
    add(music, tb, pad(ch, bar + 0.8), 1.0)
    for k, m in enumerate([ch[0] + 12, ch[2] + 12, ch[3] + 12, ch[2] + 12, ch[1] + 24, ch[2] + 12, ch[3] + 12, ch[2] + 12]):
        add(music, tb + k * b / 2, piano(m, 1.8, 0.8 if k % 2 else 1.0), 1.0, pan=0.15 * (1 if k % 2 else -1))
# soft beat from the app shot
def kick():
    n = int(0.3 * SR); t = T(n); f = 110 * np.exp(-t * 25) + 45; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10)
def hat():
    n = int(0.05 * SR); return hp(rng.standard_normal(n), 7000) * env(n, 0.001, 0.015)
tb = 33.9
while tb < 41.3:
    k = round((tb - 33.9) / (b / 2))
    if k % 4 == 0: add(music, tb, kick(), 0.28)
    add(music, tb, hat(), 0.05 if k % 2 else 0.03, pan=0.3)
    tb += b / 2
# morph whoosh, tile settle, taps in the app, logo swell and final resolution
n = int(1.4 * SR); add(sfx, 31.8, bp(rng.standard_normal(n), 300, 4000) * np.sin(np.pi * T(n) / 1.4) ** 2 * 0.06, 1.0)
for tt in (33.2, 34.6, 35.6, 36.6):
    n = int(0.06 * SR); add(sfx, tt, (np.sin(2 * np.pi * 1800 * T(n)) * env(n, 0.001, 0.012)) * 0.12, 1.0)
add(music, 37.6, pad([62, 66, 69, 74], 3.5, 0.05), 1.0)
for i, m in enumerate([74, 78, 81, 86]): add(music, 37.75 + i * 0.09, piano(m, 3.0, 0.7), 1.0, pan=(i - 1.5) * 0.2)
end = [38, 50, 57, 62, 66, 69, 74]
for i, m in enumerate(end): add(music, 41.4 + i * 0.02, piano(m, 3.0, 0.9), 1.0)
add(music, 41.4, pad([50, 57, 62, 66], DUR - 41.4, 0.05), 1.0)
music *= np.clip((DUR - t_all) / 0.6, 0, 1)[:, None]

# ============ VOICEOVER ============
meta = json.load(open('vo/vo.json'))
for i, at in enumerate(VO_AT):
    s, sr = sf.read(f'vo/vo_{i}.wav')
    if s.ndim > 1: s = s.mean(1)
    s = resample_poly(s, SR, sr)
    s = hp(s, 80); s = s / (np.max(np.abs(s)) + 1e-9) * 0.9
    i0 = int(at * SR); vo[i0:i0 + len(s)] += s[:N - i0]
# duck music and ambience under the voice
voe = lp(np.abs(vo), 6)
duck = 1 - 0.6 * np.clip(voe / 0.05, 0, 1)
duck = lp(duck, 3)
mix = music * duck[:, None] * 0.9 + amb * (0.5 + 0.5 * duck[:, None]) + sfx + np.stack([vo, vo], 1) * 0.55
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix = mix / np.max(np.abs(mix)) * 0.93
sf.write('soundtrack.wav', mix.astype(np.float32), SR, subtype='PCM_16')
print('soundtrack.wav', round(DUR, 2), 's', 'peak', round(float(np.max(np.abs(mix))), 3), 'rms dB', round(20 * np.log10(np.sqrt(np.mean(mix ** 2))), 1))
