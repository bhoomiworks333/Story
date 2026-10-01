"""Voice cleanup, synthesized ambient bed, soft pop, ducking and final mix (48 kHz)."""
import numpy as np, subprocess, os, wave
from scipy.signal import butter, sosfilt, fftconvolve
from timeline import POPS, SRC_DUR

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, "build")
SR = 48000
rng = np.random.default_rng(7)


def sh(cmd): subprocess.run(cmd, shell=True, check=True)


def read_wav(p):
    with wave.open(p) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return a.reshape(-1, w.getnchannels())


def write_wav(p, a):
    a = np.clip(a, -1, 1)
    with wave.open(p, "wb") as w:
        w.setnchannels(a.shape[1]); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((a * 32767).astype(np.int16).tobytes())


# ---------- 1. voice: light cleanup only (source floor is already ~-62 dB) ----------
def voice():
    sh(f"ffmpeg -y -v error -i {B}/src.mp4 -vn -ac 1 -ar {SR} "
       "-af \"highpass=f=75,afftdn=nr=6:nf=-58:tn=1,"
       "equalizer=f=250:t=q:w=1.2:g=-1.5,"            # slight de-mud
       "deesser=i=0.25,"
       "acompressor=threshold=-21dB:ratio=2.2:attack=12:release=140:makeup=1\" "
       f"{B}/voice_raw.wav")
    return read_wav(f"{B}/voice_raw.wav")[:, 0]   # untouched timing: no trims (keeps picture as shot)


# ---------- 2. music: soft lo-fi piano, steady, no build (Fmaj7 - Em7 - Dm7 - Cmaj7, 76 bpm) ----------
def note(m): return 440 * 2 ** ((m - 69) / 12)


def epiano(f, L):
    """mellow electric-piano tone: sine + soft bell partial, quick attack, long decay"""
    t = np.arange(L) / SR
    env = np.minimum(1, t / 0.006) * np.exp(-t * 1.6)
    tone = np.sin(2 * np.pi * f * t) + 0.22 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 4) \
        + 0.06 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t * 9)
    trem = 1 + 0.08 * np.sin(2 * np.pi * 4.2 * t)
    return tone * env * trem


def pad(dur):
    n = int(dur * SR); out = np.zeros(n)
    beat = 60 / 76; bar = 4 * beat
    chords = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]
    bass = [41, 40, 38, 36]
    k = 0
    while k * bar < dur:
        ch = chords[k % 4]; s0 = int(k * bar * SR)
        for j, m in enumerate(ch):        # gently rolled chord on beat 1, soft re-hit on beat 3
            for hit, vel in ((0, 0.9), (2, 0.45)):
                st = s0 + int((hit * beat + j * 0.018) * SR); L = min(int(bar * SR), n - st)
                if L > 0: out[st:st + L] += epiano(note(m), L) * vel * 0.25
        st = s0; L = min(int(bar * SR), n - st)
        if L > 0: out[st:st + L] += np.sin(2 * np.pi * note(bass[k % 4]) * np.arange(L) / SR) * \
            np.exp(-np.arange(L) / SR * 0.9) * 0.35
        k += 1
    # very soft lo-fi kick + brushed hat, steady from the top
    drums = np.zeros(n); i = 0
    while i * beat < dur:
        st = int(i * beat * SR)
        if i % 2 == 0:
            L = min(int(0.25 * SR), n - st); t = np.arange(L) / SR
            drums[st:st + L] += np.sin(2 * np.pi * (48 + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 14) * 0.5
        for off in (0, 0.5):
            st2 = int((i + off) * beat * SR); L = min(int(0.05 * SR), n - st2)
            if L > 0:
                t = np.arange(L) / SR
                drums[st2:st2 + L] += rng.standard_normal(L) * np.exp(-t * 90) * (0.10 if off else 0.06)
        i += 1
    drums = sosfilt(butter(2, 6000, "low", fs=SR, output="sos"), drums)
    x = sosfilt(butter(2, 3200, "low", fs=SR, output="sos"), out) + 0.5 * drums
    x += rng.standard_normal(n) * 0.004   # faint vinyl-ish air
    ir_len = int(1.6 * SR); it = np.arange(ir_len) / SR
    st = []
    for ch in range(2):
        ir = rng.standard_normal(ir_len) * np.exp(-it * 3.5); ir[0] = 0
        ir = sosfilt(butter(1, 2500, "low", fs=SR, output="sos"), ir)
        st.append(0.8 * x + 0.2 * fftconvolve(x, ir)[:n] / np.abs(ir).sum() * 40)
    m = np.stack(st, 1)
    fi, fo = int(0.8 * SR), int(2.0 * SR)
    m[:fi] *= np.linspace(0, 1, fi)[:, None]
    m[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
    return m / np.abs(m).max()


# ---------- 3. pop: soft, short, premium (no cartoon pitch sweep) ----------
def pop():
    L = int(0.16 * SR); t = np.arange(L) / SR
    f = 280 + 900 * np.exp(-t * 90)                     # quick, small pitch drop
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 38) * np.minimum(1, t / 0.0015)
    click = sosfilt(butter(2, [2500, 7000], "band", fs=SR, output="sos"),
                    rng.standard_normal(L)) * np.exp(-t * 400) * 0.35
    p = body + click
    p = sosfilt(butter(2, 5000, "low", fs=SR, output="sos"), p)
    return p / np.abs(p).max()


def env_follow(x, win=0.05):
    k = int(win * SR); e = np.sqrt(np.convolve(x ** 2, np.ones(k) / k, "same"))
    return e


def lufs_gain(x, target):
    """crude integrated loudness via ffmpeg ebur128 on a temp file"""
    write_wav(f"{B}/_tmp.wav", x if x.ndim == 2 else x[:, None])
    r = subprocess.run(f"ffmpeg -nostats -i {B}/_tmp.wav -af ebur128 -f null -", shell=True,
                       capture_output=True, text=True).stderr
    I = float(r.split("I:")[-1].split("LUFS")[0])
    return 10 ** ((target - I) / 20), I


def main():
    v = voice()
    n = len(v); dur = n / SR
    g, I = lufs_gain(v, -15.0); v = v * g
    print(f"voice in {I:.1f} LUFS -> -15")

    music = pad(dur + 0.1)[:n]
    # ducking: speech envelope -> gain. -9 dB under speech, slow release between phrases
    e = env_follow(v, 0.03)
    speech = (e > 10 ** (-38 / 20)).astype(float)
    a_up, a_dn = np.exp(-1 / (0.45 * SR)), np.exp(-1 / (0.06 * SR))
    s = 0.0
    # asymmetric smoother (fast attack, slow release) via simple loop on decimated signal
    dec = 240; sp = speech[::dec]; out = np.zeros_like(sp)
    for i, x in enumerate(sp):
        c = a_dn ** dec if x > s else a_up ** dec
        s = c * s + (1 - c) * x; out[i] = s
    sm = np.interp(np.arange(n), np.arange(len(out)) * dec, out)
    duck = 10 ** (-9 * sm / 20)
    gm, Im = lufs_gain(music, -24.0)   # low bed: ~18 LU under the voice while ducked
    music = music * gm * duck[:, None]
    print(f"music in {Im:.1f} LUFS -> -24 (pre-duck)")

    p = pop(); sfx = np.zeros(n)
    for t in POPS:
        i = int(t * SR) - int(0.01 * SR)
        sfx[i:i + len(p)] += p[:max(0, min(len(p), n - i))]
    sfx *= 10 ** (-21 / 20)            # peaks ~-21 dBFS: audible but well under the voice

    mix = np.stack([v, v], 1) + music + sfx[:, None]
    g2, I2 = lufs_gain(mix, -14.0); mix *= g2
    # headroom-safe write (-6 dB), then a transparent look-ahead limiter in ffmpeg's float path
    write_wav(f"{B}/_pre.wav", mix * 0.5)
    sh(f"ffmpeg -y -v error -i {B}/_pre.wav -af \"volume=2.0,alimiter=limit=0.84:attack=3:release=60:level=disabled\" "
       f"-ar {SR} -c:a pcm_s16le {B}/mix.wav")
    write_wav(f"{B}/stem_music.wav", music); write_wav(f"{B}/stem_voice.wav", v[:, None])
    print("mix written", mix.shape[0] / SR, "s")


if __name__ == "__main__":
    main()
