import sys, json, wave
import numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("/tmp/claude-0/-home-user-Story/ee3be9ec-d393-59ed-8f1d-0bf795805f7a/scratchpad/npmmodel/whisper-small", device="cpu", compute_type="int8")
for path in sys.argv[1:]:
    a = np.frombuffer(wave.open(path).readframes(10**9), np.int16).astype(np.float32) / 32768
    segs, _ = m.transcribe(a, language="en", word_timestamps=True, vad_filter=False)
    words = []
    for s in segs:
        for w in s.words:
            words.append({"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)})
    out = path.rsplit(".", 1)[0] + ".words.json"
    json.dump(words, open(out, "w"), indent=0)
    print("==", path)
    line = []
    for i, w in enumerate(words):
        if i and w["s"] - words[i-1]["e"] > 0.35:
            print(f"   {' '.join(line)}   [gap {w['s']-words[i-1]['e']:.2f}s @ {words[i-1]['e']:.2f}]")
            line = []
        if not line: line.append(f"{w['s']:6.2f}:")
        line.append(w["w"])
    print("  ", " ".join(line))
