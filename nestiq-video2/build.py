# NestIQ Video #2 ("Nesting"): cut voice lines, tighten VO pauses, render framed face clips.
import json, subprocess, numpy as np, soundfile as sf

U = "/root/.claude/uploads/dfd639e9-d70c-5cdd-be9f-a90aec2f93bd/"
FACE = U + "7e4277e8-ufirst_and_last_line_with_face.mp4"
SR = 48000
FACE_SPEED = 1.1

def load(path):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "0:a:0", "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(out, np.float32).astype(np.float64)

def clean(x, eq=""):
    """highpass + gentle denoise + presence, via ffmpeg, float in/out"""
    sf.write("work/_tmp_in.wav", x, SR, subtype="FLOAT")
    af = "highpass=f=80,afftdn=nr=10:nf=-45:tn=1,equalizer=f=3500:t=q:w=1:g=2.5,highshelf=f=7000:g=1.5"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "work/_tmp_in.wav", "-af", af, "-c:a", "pcm_f32le",
                    "work/_tmp_out.wav"], check=True)
    y, _ = sf.read("work/_tmp_out.wav"); return y

def speech_mask(x, thr_db=-40, win=0.02):
    w = int(SR * win); n = len(x) // w
    e = 20 * np.log10(np.sqrt(np.mean(x[:n * w].reshape(n, w) ** 2, 1)) + 1e-9)
    return e > thr_db, w

def tighten(x, short=0.28, long=0.55, long_from=0.85, lead=0.10, tail=0.18):
    """Keep speech, shrink every pause: >= long_from s -> long, else -> short (never lengthen)."""
    m, w = speech_mask(x)
    idx = np.where(m)[0]
    a, b = idx[0] * w, (idx[-1] + 1) * w
    spans = []; start = idx[0]; prev = idx[0]
    for i in idx[1:]:
        if (i - prev) * w / SR > 0.12:
            spans.append([start * w, (prev + 1) * w]); start = i
        prev = i
    spans.append([start * w, (prev + 1) * w])
    out = [np.zeros(0)]; fade = int(0.015 * SR)
    def piece(s, e):
        p = x[max(0, s):min(len(x), e)].copy()
        r = np.linspace(0, 1, fade); p[:fade] *= r; p[-fade:] *= r[::-1]; return p
    out.append(piece(spans[0][0] - int(lead * SR), spans[0][0]))
    for k, (s, e) in enumerate(spans):
        out.append(piece(s, e))
        if k + 1 < len(spans):
            gap = (spans[k + 1][0] - e) / SR
            tgt = min(gap, long if gap >= long_from else short)
            g = int(tgt * SR); h = g // 2
            out.append(piece(e, e + h)); out.append(piece(spans[k + 1][0] - (g - h), spans[k + 1][0]))
    out.append(piece(spans[-1][1], spans[-1][1] + int(tail * SR)))
    return np.concatenate(out), [(s / SR, e / SR) for s, e in spans]

def level(y, target=-18.0):
    sf.write("work/_lv.wav", y, SR, subtype="FLOAT")
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", "work/_lv.wav", "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    I = float([l for l in o.splitlines() if l.strip().startswith("I:")][-1].split()[1])
    return y * 10 ** ((target - I) / 20)

if __name__ == "__main__":
    info = {}
    # ---- voice-over lines (no picture): tighten pauses ----
    for name, f in [("L2", "37f6b274-Line_2.m4a"), ("L3", "9548f5a1-Line_3.m4a"), ("L4", "90228117-Line_4.m4a")]:
        x = load(U + f)
        y, spans = tighten(x)
        y = level(clean(y))
        sf.write(f"work/{name}_v.wav", y, SR, subtype="FLOAT")
        info[name] = dict(kind="vo", dur=len(y) / SR, raw=len(x) / SR)
        print(f"{name}: {len(x)/SR:.2f}s -> {len(y)/SR:.2f}s")
    # ---- face lines: cut, 1.1x, frame and grade ----
    FACE_CUTS = {"L1": (0.85, 6.95), "L5": (9.50, 13.62)}
    for name, (a, b) in FACE_CUTS.items():
        a = round(a * 60) / 60; b = round(b * 60) / 60
        n = round((b - a) / FACE_SPEED * 30)
        # framing: face ~560 px wide, eyes at y 850, centred (measured face boxes in the source)
        box = {"L1": (337, 589, 454), "L5": (342, 708, 453)}[name]
        x0, y0, w = box; sc = 560 / w; eye = y0 + 0.4 * w; cx = x0 + w / 2
        Wp, Hp = int(round(1080 * sc / 2)) * 2, int(round(1920 * sc / 2)) * 2
        tx = int(min(Wp - 1080, max(0, cx * sc - 540))); ty = int(min(Hp - 1920, max(0, eye * sc - 850)))
        vf = (f"setpts=(PTS-STARTPTS)/{FACE_SPEED},fps=30,scale={Wp}:{Hp}:flags=lanczos,crop=1080:1920:{tx}:{ty},"
              "colorchannelmixer=rr=1.07:gg=1.04:bb=0.96,curves=all='0/0 0.5/0.5 0.82/0.80 1/0.93',"
              "eq=saturation=1.04,format=yuv420p")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.4f}", "-i", FACE, "-t", f"{(b-a)/FACE_SPEED + 0.2:.4f}",
                        "-vf", vf, "-an", "-frames:v", str(n), "-c:v", "libx264", "-crf", "14", "-preset", "fast",
                        f"segs/{name}_full.mp4"], check=True)
        x = load(FACE)[int(a * SR):int(b * SR)]
        sf.write("work/_f.wav", x, SR, subtype="FLOAT")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "work/_f.wav", "-af", f"atempo={FACE_SPEED}",
                        "-c:a", "pcm_f32le", "work/_f2.wav"], check=True)
        y, _ = sf.read("work/_f2.wav"); y = level(clean(y))
        r = np.linspace(0, 1, int(.02 * SR)); y[:len(r)] *= r; y[-len(r):] *= r[::-1]
        y = np.pad(y, (0, max(0, int(n / 30 * SR) - len(y))))[:int(round(n / 30 * SR))]
        sf.write(f"work/{name}_v.wav", y, SR, subtype="FLOAT")
        info[name] = dict(kind="face", dur=n / 30, src=(a, b), frames=n, sc=sc, tx=tx, ty=ty)
        print(f"{name}: face {n} frames, {n/30:.2f}s, scale {sc:.2f}")
    json.dump(info, open("lines.json", "w"), indent=1)
