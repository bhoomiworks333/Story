# Step 2: concatenate the cut, clean the voice, grade the face
import json, subprocess
edl = json.load(open("work/edl.json"))
GRADE = ("eq=contrast=1.06:saturation=1.04:gamma=1.02,"
         "curves=all='0/0.025 0.25/0.26 0.6/0.61 0.85/0.83 1/0.94',"   # lift shadows, compress highlights (face shine)
         "colortemperature=temperature=6000:mix=0.5")                    # slight warmth
inputs = {"0304PM": 0, "0306PM": 1}
parts, labels = [], []
for i, (take, a, b) in enumerate(edl["segments"]):
    n = inputs[take]
    parts.append(f"[{n}:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[{n}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,"
                 f"afade=t=in:d=0.01,afade=t=out:st={b-a-0.01:.3f}:d=0.01[a{i}]")
    labels.append(f"[v{i}][a{i}]")
fc = ";".join(parts) + f";{''.join(labels)}concat=n={len(labels)}:v=1:a=1[vc][ac];" \
     f"[vc]{GRADE},format=yuv420p[vout];" \
     f"[ac]highpass=f=80,afftdn=nf=-25,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]"
cmd = ["ffmpeg", "-v", "error", "-y", "-i", "src/take_0304PM.mov", "-i", "src/take_0306PM.mov",
       "-filter_complex", fc, "-map", "[vout]", "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-r", "30",
       "work/face.mp4", "-map", "[aout]", "-c:a", "pcm_s16le", "work/voice.wav"]
subprocess.run(cmd, check=True)
