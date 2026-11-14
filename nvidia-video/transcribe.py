import json, sys
from faster_whisper import WhisperModel
m = WhisperModel(sys.argv[1], device="cpu", compute_type="int8")
import numpy as np, wave
wf = wave.open(sys.argv[2]); audio = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
segs, _ = m.transcribe(audio, language="en", word_timestamps=True,
    initial_prompt="Jensen Huang, Nvidia, Colette Kress, Steve Jobs, CFO.")
out = []
for s in segs:
    print(f"{s.start:6.2f}-{s.end:6.2f} {s.text}")
    out += [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3), "p": round(w.probability, 3)} for w in s.words]
json.dump(out, open(sys.argv[3], "w"), indent=1)
