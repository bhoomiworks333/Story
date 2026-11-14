# Builds the cut take from raw/take1_original.mp4 using segments.json.
# A segment is [start, end] in raw seconds, or ["hold", seconds] for a silent beat
# (last frame held; only used where a full-screen headline covers the face).
import json, subprocess
SRC = "raw/take1_original.mp4"
snap = lambda x: round(x * 30) / 30
segs = json.load(open("segments.json"))
vf, af, n, last_end = [], [], 0, None
for s in segs:
    if s[0] == "hold":
        d = snap(s[1]); t = last_end - 1/30
        vf.append(f"[0:v]trim={t:.4f}:{last_end:.4f},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={d-1/30:.4f}[v{n}]")
        af.append(f"anullsrc=r=48000:cl=mono,atrim=0:{d:.4f}[a{n}]")
    else:
        a, b = snap(s[0]), snap(s[1]); last_end = b
        vf.append(f"[0:v]trim={a:.4f}:{b:.4f},setpts=PTS-STARTPTS[v{n}]")
        af.append(f"[0:a:0]atrim={a:.4f}:{b:.4f},asetpts=PTS-STARTPTS,aresample=48000,pan=mono|c0=0.5*c0+0.5*c1,"
                  f"afade=t=in:d=0.03,afade=t=out:st={b-a-0.03:.4f}:d=0.03[a{n}]")
    n += 1
fc = ";".join(vf + af) + ";" + "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
    "-r", "30", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "work/cut.mov"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "work/cut.mov", "-map", "0:a", "-c:a", "pcm_s16le", "cut-audio.wav"], check=True)
