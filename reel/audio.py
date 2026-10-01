"""Voice cleanup, synthesized ambient bed, soft pop, ducking and final mix (48 kHz)."""
import numpy as np, subprocess, os, wave
from scipy.signal import butter, sosfilt, fftconvolve
from timeline import CUT, POPS, src_to_out, SRC_DUR

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
    v = read_wav(f"{B}/voice_raw.wav")[:, 0]
    # dead-air trim with a 20 ms equal-power crossfade
    a, b = int(CUT[0] * SR), int(CUT[1] * SR); x = int(0.02 * SR)
    t = np.linspace(0, np.pi / 2, x)
    seam = v[a:a + x] * np.cos(t) + v[b:b + x] * np.sin(t)
    return np.concatenate([v[:a], seam, v[b + x:]])


# ---------- 2. music: minimal cinematic pad, D minor, i-VI-III-VII ----------
def note(m): return 440 * 2 ** ((m - 69) / 12)


def pad(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    chords = [[50, 57, 62, 65, 69], [46, 53, 58, 62, 65], [41, 53, 57, 60, 64], [48, 55, 60, 62, 67]]
    bar = 4 * 60 / 72 * 2  # two bars of 4/4 at 72 bpm per chord (~6.67 s)
    out = np.zeros(n)
    for k in range(int(dur / bar) + 2):
        ch = chords[k % 4]; s0 = int(k * bar * SR); L = int(bar * 1.35 * SR)
        if s0 >= n: break
        L = min(L, n - s0); tt = np.arange(L) / SR
        env = np.minimum(1, tt / 1.8) * np.minimum(1, (L / SR - tt) / 2.2)
        seg = np.zeros(L)
        for m in ch:
            for det in (-0.06, 0.06):  # gently detuned triangle-ish voices
                f = note(m) * 2 ** (det / 12)
                ph = 2 * np.pi * f * tt + rng.uniform(0, 6.28)
                seg += (np.sin(ph) + 0.18 * np.sin(3 * ph) / 3) * (0.55 if m < 52 else 0.35)
        out[s0:s0 + L] += seg * env
    out = sosfilt(butter(2, 1400, "low", fs=SR, output="sos"), out)
    # slow filter-like breathing
    out *= 0.85 + 0.15 * np.sin(2 * np.pi * t / 9.0)
    # soft felt pluck pulse on 8ths, very quiet, only after the hook
    beat = 60 / 72 / 2
    arp = [74, 69, 77, 72]
    pl = np.zeros(n)
    for i in range(int(dur / beat)):
        s0 = int(i * beat * SR)
        if s0 / SR < 6.5: continue
        L = int(0.5 * SR); L = min(L, n - s0); tt = np.arange(L) / SR
        m = arp[i % 4] - (0 if (i // 16) % 2 == 0 else 2)
        pl[s0:s0 + L] += np.sin(2 * np.pi * note(m) * tt) * np.exp(-tt * 9) * (1 if i % 2 == 0 else 0.6)
    pl = sosfilt(butter(2, 2500, "low", fs=SR, output="sos"), pl)
    out = out / np.abs(out).max() + 0.22 * pl / max(1e-9, np.abs(pl).max())
    # sub swell under the chord root
    out += 0.25 * np.sin(2 * np.pi * note(38) * t) * (0.5 + 0.5 * np.sin(2 * np.pi * t / (bar * 4)))
    # simple stereo reverb
    ir_len = int(2.4 * SR); it = np.arange(ir_len) / SR
    st = []
    for ch in range(2):
        ir = rng.standard_normal(ir_len) * np.exp(-it * 2.6); ir[0] = 0
        ir = sosfilt(butter(1, 3000, "low", fs=SR, output="sos"), ir)
        st.append(0.7 * out + 0.3 * fftconvolve(out, ir)[:n] / np.abs(ir).sum() * 40)
    m = np.stack(st, 1)
    fade_in, fade_out = int(1.5 * SR), int(2.5 * SR)
    m[:fade_in] *= np.linspace(0, 1, fade_in)[:, None]
    m[-fade_out:] *= np.linspace(1, 0, fade_out)[:, None] ** 2
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
        i = int(src_to_out(t) * SR) - int(0.01 * SR)
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
