# Voice track + PLACEHOLDER synthesized lo-fi bed and soft SFX, then loudness to -14 LUFS / -1.5 dBTP.
import numpy as np, soundfile as sf, subprocess, json, re
import compose2 as C
SR = 48000; N = int(round(C.DUR * SR)); rng = np.random.default_rng(7)

# ---- voice: lines laid end to end on the frame grid ----
voice = np.zeros(N)
for l in C.ORDER:
    a, _ = sf.read(f"work/{l}_v.wav"); i = int(round(C.START[l] * SR)); a = a[:N - i]; voice[i:i + len(a)] += a
# ---- music (placeholder): warm electric piano chords, soft bass, brushed drums, ~76 bpm ----
bpm = 76; beat = 60 / bpm; bar = 4 * beat
def midi(m): return 440 * 2 ** ((m - 69) / 12)
def lp(x, a):                      # one-pole low-pass
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y
music = np.zeros(N + SR * 4)
def add(t, sig):
    i = int(t * SR); j = min(len(music), i + len(sig))
    if j > i: music[i:j] += sig[:j - i]
def ep(m, dur, vel=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; f = midi(m)
    env = (1 - np.exp(-t / 0.012)) * np.exp(-t / 1.6)
    trem = 1 + 0.06 * np.sin(2 * np.pi * 4.2 * t)
    sig = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.4)
           + 0.12 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / 0.15))
    return sig * env * trem * vel
chords = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]   # Fmaj7 Em7 Dm7 Cmaj7
roots = [41, 40, 38, 36]
t = 0.0; k = 0
while t < C.DUR + 2:
    ch = chords[k % 4]
    for j, m in enumerate(ch): add(t + 0.018 * j, ep(m, bar * 1.1, 0.22))
    add(t + 2.5 * beat, sum(ep(m + 12, beat * 1.4, 0.06) for m in ch[1:3]))
    n = int(bar * SR); tt = np.arange(n) / SR
    add(t, 0.32 * np.sin(2 * np.pi * midi(roots[k % 4]) * tt) * np.exp(-tt / 1.4) * (1 - np.exp(-tt / 0.01)))
    for b in range(4):                                   # drums
        bt = t + b * beat
        if b in (0,) or (b == 2):
            n = int(0.25 * SR); tt = np.arange(n) / SR
            add(bt + (0.5 * beat if b == 2 else 0), 0.35 * np.sin(2 * np.pi * (48 + 70 * np.exp(-tt / 0.03)) * tt) * np.exp(-tt / 0.09))
        if b in (1, 3):
            n = int(0.18 * SR); tt = np.arange(n) / SR
            add(bt, 0.06 * rng.standard_normal(n) * np.exp(-tt / 0.06))
        for h in (0, 0.5):
            n = int(0.05 * SR); tt = np.arange(n) / SR
            add(bt + h * beat + 0.012 * (h > 0), 0.018 * rng.standard_normal(n) * np.exp(-tt / 0.012))
    t += bar; k += 1
music = lp(music, 0.18)                                  # warm, rolled-off top
music += 0.0025 * lp(rng.standard_normal(len(music)), 0.3) # faint vinyl hiss
music = music[:N]

# ---- SFX (placeholder) ----
def tap(f=420, dur=0.12, bright=0.25):
    n = int(dur * SR); tt = np.arange(n) / SR
    body = np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.03)
    click = lp(rng.standard_normal(n), bright) * np.exp(-tt / 0.006)
    return body * 0.7 + click * 0.6
def tick():
    n = int(0.03 * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2600 * tt) + 0.5 * rng.standard_normal(n)) * np.exp(-tt / 0.004)
sfx = np.zeros(N)
def put(t, sig, g):
    i = int(t * SR); j = min(N, i + len(sig)); sfx[i:j] += g * sig[:j - i] / np.abs(sig).max()
for i, tt_ in enumerate(C.CUE["tray"]): put(tt_, tap(700 + 30 * i, 0.08, 0.3), 0.45)      # parts appear
for d in C.CUE["drops"]: put(d + 0.32, tap(380 + rng.uniform(-40, 40)), 1.0)               # parts land
for sq in C.CUE["squares"]: put(sq + 0.75, tap(520, 0.14, 0.2), 1.0)                       # squares into the hole
def rms_db(x): return 20 * np.log10(np.sqrt(np.mean(x[np.abs(x) > 1e-6] ** 2)) + 1e-12)
v_db = rms_db(voice)
# music bed ~12 dB under the voice
music *= 10 ** ((v_db - 12 - rms_db(music)) / 20)
tt = np.arange(N) / SR
# fade out over the last 1.5 s
music *= np.clip((C.DUR - tt) / 1.5, 0, 1)
# SFX ~10 dB under the voice at their peaks' RMS (quiet, supportive)
ev = sfx[np.abs(sfx) > 1e-3]
sfx *= 10 ** ((v_db - 10 - rms_db(ev)) / 20) if len(ev) else 1
mix = voice + music + sfx
sf.write("work/mix_pre.wav", np.stack([mix, mix], 1).astype(np.float32), SR, subtype="FLOAT")
sf.write("work/music_only.wav", music.astype(np.float32), SR, subtype="FLOAT")
# two-pass loudnorm to -14 LUFS, -1.5 dBTP
m = subprocess.run(["ffmpeg", "-hide_banner", "-i", "work/mix_pre.wav", "-af",
                    "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "work/mix_pre.wav", "-af",
    f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
    f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,alimiter=limit=0.82:level=false",
    "-ar", "48000", "-c:a", "pcm_s24le", "work/mix.wav"], check=True)
print("voice rms %.1f dB, mixed; first pass", j["input_i"], j["input_tp"])
