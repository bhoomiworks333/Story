# NestIQ Video #3 ("Scrap toh bik jaata hai"): cut list -> framed, graded clips + processed audio pieces.
import json, subprocess, numpy as np, soundfile as sf

U = "/root/.claude/uploads/dfd639e9-d70c-5cdd-be9f-a90aec2f93bd/"
SRC = {"H": "3e215bdf-Hook.mp4", "S": "f51daf0d-1123.mp4", "T": "54a079e8-11231.mp4",
       "P": "7eb4cff7-11232.mp4", "C": "eb5477e4-CTA.mp4"}
# measured face box (x, y, w) in a 1080-wide frame, and median skin RGB
FACE = {"H": (195, 278, 696, (176, 130, 117)), "S": (270, 340, 656, (171, 126, 112)),
        "T": (266, 364, 604, (173, 127, 118)), "P": (284, 294, 583, (171, 127, 114)),
        "C": (232, 316, 651, (168, 124, 113))}
SPEED = 1.15
# (id, source, in, out, speed, section)
PIECES = [
    ("coin", "H", 2.45, 3.95, 1.0, "hook"),          # coins dropping, real clangs
    ("h1",   "H", 8.12, 13.80, SPEED, "hook"),        # Every factory owner ... where's the loss?
    ("s1",   "S", 0.71, 8.55, SPEED, "setup"),        # Sheet comes in ... 65 rupees a kilo.
    ("s2",   "S", 8.97, 12.78, SPEED, "setup"),       # You cut your parts ... sell as scrap.
    ("t1",   "T", 0.30, 3.95, SPEED, "twist"),        # But scrap sells for around 35. So
    ("t2",   "T", 4.20, 9.53, SPEED, "twist"),        # for every kilo ... you lose 30 rupees.
    ("p1",   "P", 1.74, 4.85, SPEED, "payoff"),       # It doesn't feel like a loss. (coin drops)
    ("p2",   "P", 6.20, 8.30, SPEED, "payoff"),       # Because some money still comes back.
    ("p3",   "P", 9.33, 9.80, SPEED, "payoff"),       # But
    ("p4",   "P", 10.98, 12.30, SPEED, "payoff"),     # for every sheet,
    ("p5",   "P", 12.80, 13.75, SPEED, "payoff"),     # every day,
    ("p6",   "P", 14.31, 15.24, SPEED, "payoff"),     # it adds up.
    ("c1",   "C", 2.91, 4.33, SPEED, "cta"),          # What do you pay for sheets
    ("c2",   "C", 4.58, 6.45, SPEED, "cta"),          # and what do you get for the scraps?
    ("c3",   "C", 6.85, 9.20, SPEED, "cta"),          # Tell me in the comments. (+ relaxed hold)
]
EYE, FACEW = 556, 690
TARGET = (176, 124, 100)

def framing(src):
    x, y, w, skin = FACE[src]
    s = max(1.0, FACEW / w); eye = y + 0.4 * w; cx = x + w / 2
    ty = min(0, max(1920 - 1920 * s, EYE - eye * s)); tx = min(0, max(1080 - 1080 * s, 540 - cx * s))
    gains = [min(1.2, max(.85, 1 + .7 * (t / v - 1))) for t, v in zip(TARGET, skin)]
    return s, tx, ty, gains

def fps_of(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                        "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
    a, b = r.split("/"); return float(a) / float(b)

if __name__ == "__main__":
    out = []
    for pid, src, a, b, sp, sec in PIECES:
        f = U + SRC[src]; fr = fps_of(f)
        a = round(a * fr) / fr; b = round(b * fr) / fr
        n = round((b - a) / sp * 30)
        s, tx, ty, g = framing(src)
        Wp, Hp = int(round(1080 * s / 2)) * 2, int(round(1920 * s / 2)) * 2
        vf = (f"setpts=(PTS-STARTPTS)/{sp},fps=30,scale={Wp}:{Hp}:flags=lanczos,crop=1080:1920:{int(-tx)}:{int(-ty)},"
              f"colorchannelmixer=rr={g[0]:.3f}:gg={g[1]:.3f}:bb={g[2]:.3f},curves=all='0/0 0.5/0.5 0.82/0.80 1/0.93',"
              "eq=saturation=1.04,format=yuv420p")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.4f}", "-i", f, "-t", f"{(b - a) + 0.3:.4f}", "-vf", vf,
                        "-an", "-frames:v", str(n), "-c:v", "libx264", "-crf", "14", "-preset", "fast", f"segs/{pid}.mp4"],
                       check=True)
        af = f"atempo={sp}," if sp != 1 else ""
        af += "highpass=f=80,afftdn=nr=10:nf=-45:tn=1"
        if pid != "coin": af += ",equalizer=f=3500:t=q:w=1:g=2,highshelf=f=7000:g=1"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.4f}", "-i", f, "-t", f"{b - a:.4f}", "-map", "0:a:0",
                        "-ac", "1", "-ar", "48000", "-af", af, "-c:a", "pcm_f32le", f"work/{pid}.wav"], check=True)
        y, sr = sf.read(f"work/{pid}.wav"); N = int(round(n / 30 * sr)); y = np.pad(y, (0, max(0, N - len(y))))[:N]
        r = np.linspace(0, 1, int(.02 * sr)); y[:len(r)] *= r; y[-len(r):] *= r[::-1]
        sf.write(f"work/{pid}.wav", y, sr, subtype="FLOAT")
        out.append(dict(id=pid, src=src, a=a, b=b, speed=sp, sec=sec, frames=n))
        print(f"{pid:5s} {src} {a:6.2f}-{b:6.2f} -> {n/30:5.2f}s  scale {s:.2f}")
    t = 0
    for p in out: p["start"] = t; t += p["frames"] / 30
    print("total %.2f s" % t)
    json.dump(out, open("pieces.json", "w"), indent=1)
