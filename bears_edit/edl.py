# Step 1: build the cut list from both takes and map word timings onto the output timeline
import json
SIL_0306 = [(7.33, 7.75), (18.50, 18.85), (22.84, 23.19), (24.40, 24.75), (26.97, 27.44), (31.23, 31.75), (32.47, 32.87)]
PAD, MIN_GAP = 0.12, 0.35

segs = [("0304PM", 8.00, 11.35)]          # "Google, [pause] I expected a lot more from you." + protected pause
t = 2.06                                   # 0306PM from "Same prompt"
for a, b in SIL_0306:
    if b - a > MIN_GAP:
        segs.append(("0306PM", t, a + PAD)); t = b - PAD
segs.append(("0306PM", t, 34.54))          # ... "Which one would you have bet on?"
segs.append(("0306PM", 35.70, 37.20))      # silent 1.5s hold (skips "Tell me in the comments")

words = {k: json.load(open(f"work/take_{k}.words.json")) for k in ("0304PM", "0306PM")}
# whisper smears word edges into pauses, so a word belongs to the kept segment it overlaps most
starts, out = [], 0.0
for _, a, b in segs:
    starts.append(out); out += b - a
words_out = []
for take in ("0304PM", "0306PM"):
    for w in words[take]:
        ov = [(min(w["e"], b) - max(w["s"], a), i) for i, (k, a, b) in enumerate(segs) if k == take]
        best, i = max(ov)
        if best > 0:
            _, a, b = segs[i]
            words_out.append({"w": w["w"], "s": round(starts[i] + max(w["s"], a) - a, 3), "e": round(starts[i] + min(w["e"], b) - a, 3)})
words_out.sort(key=lambda w: w["s"])
json.dump({"segments": segs, "duration": round(out, 3)}, open("work/edl.json", "w"), indent=1)
json.dump(words_out, open("work/words_out.json", "w"), indent=0)
for s in segs: print(f"{s[0]}  {s[1]:6.2f} -> {s[2]:6.2f}  ({s[2]-s[1]:.2f}s)")
print("duration", round(out, 2))
print(" ".join(f"{w['w']}@{w['s']:.1f}" for w in words_out))
