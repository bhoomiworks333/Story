"""Step 3: remove the planned silences, frame-accurate, with 10 ms fades at every cut.

usage: python3 trim.py IN.mp4 OUT.mp4 [cut_plan.json]
"""
import json, subprocess, sys

FADE = 0.01


def main(inp, out, plan="cut_plan.json"):
    keep = json.load(open(plan))["keep"]
    v, a, labels = [], [], []
    for i, (s, e) in enumerate(keep):
        fades = []
        if i > 0: fades.append(f"afade=t=in:st=0:d={FADE}")
        if i < len(keep) - 1: fades.append(f"afade=t=out:st={e - s - FADE:.3f}:d={FADE}")
        v.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS[v{i}]")
        a.append(f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS" + "".join("," + f for f in fades) + f"[a{i}]")
        labels.append(f"[v{i}][a{i}]")
    fc = ";".join(v + a) + ";" + "".join(labels) + f"concat=n={len(keep)}:v=1:a=1[v][a]"
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", inp, "-filter_complex", fc,
        "-map", "[v]", "-map", "[a]", "-r", "30", "-c:v", "libx264", "-crf", "18", "-preset", "slow",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])


if __name__ == "__main__":
    main(*sys.argv[1:])
