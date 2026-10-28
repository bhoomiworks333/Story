# Step 8: sound design - only the squeaky-toy file, on the Opus jelly moments (Gemini's "plastic" stays dry)
import subprocess
HITS = [(0.12, 0.66, 12.21, 0.55),   # long squeak on "stretches"
        (2.38, 2.68, 13.99, 0.55)]   # short squeak on "wobbles"
parts, labels = [], []
for i, (a, b, at, vol) in enumerate(HITS):
    parts.append(f"[1:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b-a-0.06:.2f}:d=0.06,"
                 f"volume={vol},aresample=48000,aformat=channel_layouts=stereo,adelay={int(at*1000)}|{int(at*1000)}[s{i}]")
    labels.append(f"[s{i}]")
fc = ";".join(parts) + f";[0:a]aformat=channel_layouts=stereo,volume=1.12[v];[v]{''.join(labels)}amix=inputs={len(HITS)+1}:normalize=0:duration=first,alimiter=limit=0.8:level=0[out]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "work/voice.wav", "-i", "src/squeak.mp3", "-filter_complex", fc,
                "-map", "[out]", "-c:a", "pcm_s16le", "work/mix.wav"], check=True)
for v in ("A_main", "B_trial"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"bears_{v}.mp4", "-i", "work/mix.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", f"work/tmp_{v}.mp4"], check=True)
    subprocess.run(["mv", f"work/tmp_{v}.mp4", f"bears_{v}.mp4"], check=True)
