# Synthesised placeholder score + sound effects, locked to the animation timeline.
# Output: soundtrack.wav (44.1 kHz stereo). Replace the music with a licensed track for the final cut if preferred.
import numpy as np, wave

import json
SR = 44100
WARP = json.load(open('warp.json'))
DUR = WARP['video_duration']
_S = np.array([p[0] for p in WARP['warp']]); _V = np.array([p[1] for p in WARP['warp']])
def V(t): return float(np.interp(t, _S, _V))   # story time -> video time
N = int(SR * DUR)
music = np.zeros((N, 2))
sfx = np.zeros((N, 2))
rng = np.random.default_rng(1)

def add(buf, t, sig, gain=1.0, pan=0.0):
    i = int(V(t) * SR)
    if i >= N: return
    sig = sig[: N - i]
    l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(sig), 0] += sig * gain * l * 1.41
    buf[i:i + len(sig), 1] += sig * gain * r * 1.41

def env(n, a=.005, r=.2):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a) * np.exp(-t / r)
    return e

def note(m): return 440 * 2 ** ((m - 69) / 12)

def pluck(freq, dur=1.2, bright=.5):
    n = int(SR * dur); p = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, p)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = bright * buf[i % p] + (1 - bright) * .5 * (buf[i % p] + buf[(i + 1) % p]) * .996 / 1.0
    return out * .5

_pl = {}
def pl(m, dur=1.2):
    k = (m, dur)
    if k not in _pl: _pl[k] = pluck(note(m), dur, .1)
    return _pl[k]

def pad(ms, dur, gain=.08):
    n = int(SR * dur); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * note(m) * t) + .5 * np.sin(2 * np.pi * note(m) * 1.003 * t) for m in ms)
    e = np.minimum(1, t / .6) * np.minimum(1, (dur - t) / .8)
    return s * e * gain / len(ms)

def bell(freq, dur=2.0):
    n = int(SR * dur); t = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * freq * k * t) * np.exp(-t * d) for k, a, d in [(1, 1, 2), (2.76, .5, 4), (5.4, .25, 7)])
    return s * np.minimum(1, t / .003)

def kick():
    n = int(SR * .35); t = np.arange(n) / SR
    f = 120 * np.exp(-t * 18) + 45
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)

def noise(dur, lp=.2):
    n = int(SR * dur); x = rng.normal(0, 1, n)
    y = np.zeros(n); a = 0
    for i in range(n): a += lp * (x[i] - a); y[i] = a
    return y / (np.abs(y).max() + 1e-9)

def hat():
    n = int(SR * .06); x = rng.normal(0, 1, n); x = np.diff(np.concatenate([[0], x]))
    return x * np.exp(-np.arange(n) / SR * 60) * .5

def sweep(f0, f1, dur, shape='sin'):
    n = int(SR * dur); t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) if shape == 'sin' else 2 * ((ph / (2 * np.pi)) % 1) - 1
    return s * np.minimum(1, t / .005) * np.minimum(1, (dur - t) / .02)

# ---------------- MUSIC ----------------
BEAT = 60 / 84
D, E_, Fs, G_, A_, B_, Cs = 62, 64, 66, 67, 69, 71, 73
motif = [(0, 74), (1, 78), (2, 81), (3, 78), (4, 76), (5, 69), (6, 74)]  # D F# A F# E A D
def play_motif(t0, gain=.35, oct=0):
    for b, m in motif: add(music, t0 + b * BEAT * .5, pl(m + oct, 1.6), gain, pan=-.2 + (m % 5) * .1)

# 0–11: warm, nostalgic
for t0 in np.arange(0.3, 11, BEAT * 4): play_motif(t0, .30)
add(music, 0, pad([50, 57, 62, 66], 6.0), 1); add(music, 5.6, pad([55, 59, 62, 67], 6.0), 1)
# fade music before the question (silence 13.8–18.7)
# 18.7–28: learning, pulse builds
chords = [[50, 57, 62, 66], [47, 54, 59, 62], [43, 55, 59, 62], [45, 52, 57, 61]]
arp = lambda ch: [ch[1] + 12, ch[2] + 12, ch[3] + 12, ch[2] + 12]
t = 18.8; ci = 0
while t < 28.0:
    ch = chords[ci % 4]
    add(music, t, pad(ch, BEAT * 4 + .6, .07), 1)
    for k in range(8):
        add(music, t + k * BEAT / 2, pl(arp(ch)[k % 4], 1.0), .22, pan=(k % 2 - .5) * .6)
    if t > 21: [add(music, t + k * BEAT, kick(), .35) for k in range(4)]
    if t > 24: [add(music, t + k * BEAT / 2 + BEAT / 4, hat(), .25, .3) for k in range(8)]
    t += BEAT * 4; ci += 1
# 28–37.5: realisation, fuller
t = 28.0; ci = 0
while t < 37.8:
    ch = chords[ci % 4]
    add(music, t, pad(ch, BEAT * 4 + .6, .1), 1)
    add(music, t, pl(ch[0] - 12, 2.5), .45)
    for k in range(16):
        add(music, t + k * BEAT / 4, pl(arp(ch)[k % 4] + (12 if k % 8 > 5 else 0), .7), .16, pan=(k % 2 - .5) * .7)
    for k in range(4): add(music, t + k * BEAT, kick(), .4)
    for k in range(8): add(music, t + k * BEAT / 2 + BEAT / 4, hat(), .28, .3)
    t += BEAT * 4; ci += 1
# 38.2 resolve on the logo
add(music, 38.2, pad([50, 57, 62, 66, 69, 74], 3.5, .16), 1)
for m, d in [(74, 0), (78, .05), (81, .1), (86, .15)]: add(music, 38.2 + d, bell(note(m), 3.0), .09)
add(music, 38.2, kick(), .6)
# 41–46.5: ecosystem, energetic
t = 41.1; ci = 0
while t < 46.4:
    ch = chords[ci % 4]
    add(music, t, pad(ch, BEAT * 4 + .4, .08), 1)
    add(music, t, pl(ch[0] - 12, 1.2), .5); add(music, t + BEAT * 2, pl(ch[0] - 12, 1.2), .45)
    for k in range(16): add(music, t + k * BEAT / 4, pl(arp(ch)[k % 4] + 12 * (k % 3 == 0), .5), .17, pan=((k * 3) % 5 - 2) * .25)
    for k in range(4): add(music, t + k * BEAT, kick(), .45)
    for k in range(16): add(music, t + k * BEAT / 4, hat(), .18 if k % 2 else .28, .35)
    t += BEAT * 4; ci += 1
# 46.5–53.4: strip back to the opening motif
add(music, 46.5, pad([50, 57, 62, 66], 7.2, .08), 1)
play_motif(46.8, .30); play_motif(46.8 + BEAT * 4, .26)
# 53.8–57: final statement
add(music, 53.7, pad([50, 57, 62, 66, 69], 3.3, .12), 1)
play_motif(53.9, .32)
add(music, 55.6, pl(62, 1.4), .4); add(music, 55.6, bell(note(74), 1.4), .06)

# music gain automation: duck out before the question, silence, back in
tt = np.interp(np.arange(N) / SR, _V, _S)  # story time of each sample
g = np.ones(N)
g *= np.where(tt < 12.6, 1, np.where(tt < 13.8, 1 - (tt - 12.6) / 1.2, 0)) + np.where(tt > 18.7, 1, 0) * np.where(tt < 13.8, 0, 1)
g = np.clip(g, 0, 1)
g *= np.clip((57.0 - tt) / .5, 0, 1)
music *= g[:, None]

# ---------------- SFX ----------------
def ring(dur):
    n = int(SR * dur); t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * 1180 * t) + .7 * np.sin(2 * np.pi * 1530 * t) + .3 * np.sin(2 * np.pi * 2400 * t)
    trem = (np.sin(2 * np.pi * 22 * t) > 0) * .8 + .2
    burst = ((t % .6) < .42).astype(float)
    return tone * trem * burst * .35
add(sfx, 0.0, ring(1.55), .55); add(sfx, 6.9, ring(1.4), .5, .3); add(sfx, 48.9, ring(1.4), .12, .5)
def clack(): return noise(.08, .6) * env(int(SR * .08), .001, .02)
add(sfx, 1.55, clack(), .7); add(sfx, 6.62, clack(), .7); add(sfx, 8.3, clack(), .6)
# paper drops + scribbles
for d in [3.0, 4.2, 5.6, 6.3, 8.9, 9.6, 10.3, 16.2]:
    s = noise(.3, .08) * env(int(SR * .3), .02, .08); add(sfx, d + .2, s, .35, -.5)
def scribble(dur):
    s = noise(dur, .5); t = np.arange(len(s)) / SR
    return s * (.5 + .5 * np.sin(2 * np.pi * 14 * t)) * .5
add(sfx, 2.0, scribble(2.5), .10, -.1); add(sfx, 8.3, scribble(3.0), .10, -.1)
def pop(f=500): return sweep(f, f * 2.2, .08) * env(int(SR * .08), .002, .04)
for i, t0 in enumerate([4.55, 4.7, 4.85]): add(sfx, t0, pop(420 + i * 80), .5, [-.6, .6, .3][i])
for k in range(8): add(sfx, 6.6 + k * .14, pop(1400) * .3, .3, -.7)
add(sfx, 7.7, sweep(300, 900, .25) * env(int(SR * .25), .005, .1), .4, -.6)
for i in range(6): add(sfx, 8.6 + i * .18, pop(700 + i * 90), .3)
add(sfx, 13.25, pop(380), .6, .3)
add(sfx, 13.8, scribble(1.0), .12, .3)
for k in range(9): add(sfx, 13.9 + k * .5, clack() * .5, .35, .5)  # clock ticks in the silence
add(sfx, 17.3, noise(.5, .05) * env(int(SR * .5), .1, .2), .3)
add(sfx, 18.0, noise(.12, .7) * env(int(SR * .12), .001, .03), .9)  # notebook clap
whoosh = lambda d, up=True: noise(d, .15) * (np.linspace(0, 1, int(SR * d)) ** 2 if up else np.linspace(1, 0, int(SR * d)) ** 2)
add(sfx, 18.1, whoosh(.65), .5); add(sfx, 19.2, whoosh(.7) * np.hanning(int(SR * .7)), .35)
page = lambda: noise(.18, .25) * env(int(SR * .18), .01, .05)
add(sfx, 19.95, page(), .5)
for b in [22.25, 24.85]:
    for k in range(3): add(sfx, b + k * .12, page(), .45, (k - 1) * .4)
for t0 in [22.55, 25.1, 27.25]: add(sfx, t0, bell(1760, .8), .12, .2)
for k in range(40): add(sfx, 28.3 + k * .055 + rng.uniform(0, .03), clack() * .4, .25, rng.uniform(-.3, .3))
# plings for each connection, rising
for i, t0 in enumerate([31.2, 31.8, 32.3, 32.75, 33.15, 33.5, 33.8, 34.05, 34.25]):
    add(sfx, t0, bell(note(74 + [0, 2, 4, 7, 9, 12, 14, 16, 19][i]), 1.0), .14, (i % 3 - 1) * .5)
add(sfx, 34.5, sweep(220, 110, .35, 'saw') * env(int(SR * .35), .002, .1), .12)  # thread let go
for k in range(6): add(sfx, 34.8 + k * .45, whoosh(.3) * np.hanning(int(SR * .3)), .15, (k % 2 - .5))
# logo
add(sfx, 38.15, sweep(90, 38, .9) * env(int(SR * .9), .01, .5), .55)
add(sfx, 38.2, whoosh(.4, False), .3)
# factory
hum = np.sin(2 * np.pi * 55 * np.arange(int(SR * 5.4)) / SR) * .5 + noise(5.4, .02) * .3
hum *= np.minimum(1, np.arange(len(hum)) / SR / .5) * np.minimum(1, (len(hum) / SR - np.arange(len(hum)) / SR) / .5)
add(sfx, 41.1, hum, .12)
add(sfx, 42.85, bell(1320, .6), .2, .1); add(sfx, 42.95, bell(1320, .6), .15, .1)
add(sfx, 43.0, whoosh(.5) * np.hanning(int(SR * .5)), .25); add(sfx, 44.0, whoosh(.5) * np.hanning(int(SR * .5)), .25, .4)
for k in range(3): add(sfx, 43.6 + k * .12, bell(note(86 + k * 2), .6), .08)
servo = lambda f0, f1, d: sweep(f0, f1, d, 'saw') * .3
add(sfx, 44.5, servo(180, 260, .4), .12, .6); add(sfx, 44.95, servo(260, 200, .3), .12, .6); add(sfx, 45.25, servo(200, 150, .3), .12, .5)
add(sfx, 45.6, noise(.15, .3) * env(int(SR * .15), .001, .05), .6, .2)
add(sfx, 45.7, bell(note(81), 1.0), .1)
add(sfx, 48.3, sum(bell(note(m), 1.5) for m in [86, 90, 93]) * .3, .1)
add(sfx, 54.1, sweep(80, 40, .7) * env(int(SR * .7), .01, .4), .35)

# ---------------- VOICEOVER (Prashant, first person) ----------------
import soundfile as sf
from scipy.signal import resample_poly
vo = np.zeros((N, 2))
duck = np.ones(N)
for i, st in enumerate(WARP['vo_starts']):
    a, sr = sf.read(f'vo/vo_{i}.wav')
    a = resample_poly(a, SR, sr) if sr != SR else a
    a = a / (np.abs(a).max() + 1e-9) * .8
    j = int((st + .12) * SR)
    a = a[: N - j]
    vo[j:j + len(a), 0] += a; vo[j:j + len(a), 1] += a
    # duck music & sfx under the voice
    k0, k1 = max(0, j - int(.25 * SR)), min(N, j + len(a) + int(.3 * SR))
    duck[k0:k1] = np.minimum(duck[k0:k1], .38)
# smooth the ducking envelope
kern = np.hanning(int(.3 * SR)); kern /= kern.sum()
duck = np.convolve(duck, kern, mode='same')
music *= duck[:, None]; sfx *= (.5 + .5 * duck)[:, None]
mix = music * .9 + sfx * .8 + vo * 1.0
mix = np.tanh(mix * 1.05)
mix /= np.abs(mix).max() / .89
data = (mix * 32767).astype(np.int16)
with wave.open('soundtrack.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())
print('ok', data.shape)
