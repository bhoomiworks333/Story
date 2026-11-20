# Mixes voice lines + a soft synthesised lo-fi bed + sfx -> mix.wav (48 kHz stereo)
import json, numpy as np, soundfile as sf
SR = 48000
D = json.load(open('vo/lines.json')); LINES = D['lines']; TOT = D['total']
N = int(TOT * SR); rng = np.random.default_rng(3)
vo = np.zeros(N); mus = np.zeros(N); fx = np.zeros(N)
def put(buf, t, sig, g=1.0):
    i = int(t * SR); sig = sig[:max(0, N - i)]; buf[i:i + len(sig)] += sig * g
def resample(a, sr):
    if sr == SR: return a
    x = np.linspace(0, len(a) - 1, int(len(a) * SR / sr)); return np.interp(x, np.arange(len(a)), a)
for L in LINES:
    a, sr = sf.read(L['file']); a = a.mean(1) if a.ndim > 1 else a; a = resample(a, sr)
    a = a / (np.max(np.abs(a)) + 1e-9) * .8
    put(vo, L['start'], a)
tt = lambda d: np.arange(int(d * SR)) / SR
def note(m): return 440 * 2 ** ((m - 69) / 12)
def epiano(m, d=1.6, g=.18):
    t = tt(d); f = note(m)
    s = np.sin(2*np.pi*f*t + .6*np.sin(2*np.pi*f*2*t) * np.exp(-t*4)) * np.exp(-t*2.2)
    return s * np.minimum(1, t / .004) * g
def kick():
    t = tt(.3); f = 110 * np.exp(-t * 20) + 42
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*10)
def hat():
    t = tt(.05); return rng.uniform(-1, 1, len(t)) * np.exp(-t*90) * .25
def bass(m, d):
    t = tt(d); return np.sin(2*np.pi*note(m)*t) * np.minimum(1, t/.01) * np.exp(-t*1.2) * .35
BPM = 84; beat = 60 / BPM
chords = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 65]]  # Am7 Fmaj7 Cmaj7 G7
bars = int(TOT / (4 * beat)) + 1
for b in range(bars):
    t0 = b * 4 * beat; ch = chords[b % 4]
    for k, m in enumerate(ch): put(mus, t0 + k * .03, epiano(m, 4 * beat), .55)
    put(mus, t0 + 2.5 * beat, epiano(ch[-1] + 12, 1.0, .1))
    put(mus, t0, bass(ch[0] - 24, 2 * beat)); put(mus, t0 + 2 * beat, bass(ch[0] - 24, 2 * beat))
    for q in range(4):
        if q in (0, 2): put(mus, t0 + q * beat, kick(), .5)
        for e in (0, .5): put(mus, t0 + (q + e) * beat + (.03 if e else 0), hat(), .35 if e else .2)
# vinyl crackle
mus += (rng.uniform(-1, 1, N) * (rng.uniform(0, 1, N) > .9993)) * .08
# lowpass the music a touch (one-pole)
y = np.zeros(N); a = .35
for i in range(1, N): y[i] = y[i-1] + a * (mus[i] - y[i-1])
mus = y
# sfx
def boing():
    t = tt(.45); f = 300 + 250 * np.sin(2*np.pi*7*t) * np.exp(-t*5); return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*6) * .35
def honk():
    t = tt(.22); f = 520
    s = np.sign(np.sin(2*np.pi*f*t)) * .5 + np.sign(np.sin(2*np.pi*f*1.26*t)) * .5
    return s * np.minimum(1, t/.01) * np.minimum(1, (.22 - t)/.02) * .16
def pop():
    t = tt(.25); f = 900 * np.exp(-t*14) + 200; return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*16) * .5 + rng.uniform(-1,1,len(t))*np.exp(-t*40)*.15
def click():
    t = tt(.06); return (rng.uniform(-1, 1, len(t)) * .6 + np.sin(2*np.pi*1800*t)) * np.exp(-t*120) * .5
def blip(m):
    t = tt(.09); return np.sin(2*np.pi*note(m)*t) * np.exp(-t*40) * .25
put(fx, LINES[4]['start'] - .1, boing())
s16 = LINES[16]['start']
put(fx, s16 - .02, pop())
for k in range(5): put(fx, s16 + .5 + k * .62, honk(), 1 if k < 2 else .7)
put(fx, LINES[20]['start'] + LINES[20]['dur'] + .25, click())
for i in (10, 12): put(fx, LINES[i]['start'] - .05, blip(84 if i == 10 else 79))
# duck music under voice
env = np.abs(vo); k = int(.12 * SR)
sm = np.convolve(env, np.ones(k) / k, mode='same'); duck = 1 - .45 * np.clip(sm / .05, 0, 1)
mix = vo * 1.0 + mus * .22 * duck + fx
# music stops with the lights
off = int((LINES[20]['start'] + LINES[20]['dur'] + .25) * SR); mix[off:] -= (mus * .22 * duck)[off:]
mix = mix / np.max(np.abs(mix)) * .89
st = np.stack([mix, mix], 1)
sf.write('mix.wav', st, SR)
print('ok', len(mix) / SR)
