import sys, json, wave, numpy as np, sherpa_onnx
m, wav, out = sys.argv[1], sys.argv[2], sys.argv[3]
rec = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=f"{m}/encoder.int8.onnx", decoder=f"{m}/decoder.int8.onnx",
    joiner=f"{m}/joiner.int8.onnx", tokens=f"{m}/tokens.txt",
    model_type="nemo_transducer", num_threads=4)
with wave.open(wav) as w:
    sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)/32768
s = rec.create_stream(); s.accept_waveform(sr, a); rec.decode_stream(s)
r = s.result
toks, ts = r.tokens, r.timestamps
durs = list(getattr(r, "durations", []) or [])
words=[]; 
for i,(t,st) in enumerate(zip(toks,ts)):
    end = st + (durs[i] if i < len(durs) and durs[i] > 0 else 0.08)
    if t.startswith("▁") or t.startswith(" ") or not words:
        words.append({"text": t.lstrip("▁ "), "start": round(st,3), "end": round(end,3)})
    else:
        words[-1]["text"] += t; words[-1]["end"] = round(end,3)
words=[w for w in words if w["text"]]
json.dump(words, open(out,"w"), indent=0)
print(r.text)
for w in words: print(f'{w["start"]:6.2f}-{w["end"]:6.2f} {w["text"]}')
