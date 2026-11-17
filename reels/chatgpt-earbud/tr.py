import json,sys
from faster_whisper import WhisperModel
m=WhisperModel("small",compute_type="int8")
import numpy as np,soundfile as sf
aud=sf.read(sys.argv[1],dtype="float32")[0]
segs,info=m.transcribe(aud,word_timestamps=True)
print(info.language)
out=[]
for s in segs:
    print(f"[{s.start:.2f}-{s.end:.2f}] {s.text}")
    for w in s.words: out.append([w.start,w.end,w.word.strip()])
json.dump(out,open("words.json","w"))
