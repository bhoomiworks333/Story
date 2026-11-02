"""Step 2 + structure: seated trim (cut list) and output timeline. Writes timeline.json."""
import json, wave, numpy as np
E = "/home/user/Story/insomnia_edit"
FPS = 30
words = json.load(open(f"{E}/review/seated_words_from_2.8s.json"))
for w in words:
    w["w"] = w["w"].split("(")[0]; w["s"] += 2.8; w["e"] += 2.8
# Re-aligned tail (energy + second alignment pass): "comment" ~38.60-39.20, "awake" ~39.30-40.40
words[-2].update(s=38.60, e=39.20); words[-1].update(s=39.30, e=40.40)
SPEECH_END = 40.45; CLIP_END = 40.98; HOLD = 1.5; PAD = 0.12; MAXGAP = 0.35
SPEED = 1.12          # whole reel sped up (user request); hold after AWAKE stays 1.5s real time
FIRST_WORD = "if"      # full script; user adds their own hook text overlay on the opening

w_ = wave.open(f"{E}/review/audio_D_c3.wav"); sr = w_.getframerate()
a = np.frombuffer(w_.readframes(w_.getnframes()), np.int16).astype(float) / 32768
hop = sr // 100
db = np.array([20*np.log10(np.sqrt(np.mean(a[i:i+hop]**2)) + 1e-9) for i in range(0, len(a)-hop, hop)])
QUIET = -45.0
def quiet_runs(t0, t1):
    i0, i1 = int(t0*100), int(t1*100); runs=[]; st=None
    for i in range(i0, i1):
        q = db[i] < QUIET
        if q and st is None: st = i
        if (not q or i == i1-1) and st is not None:
            en = i if not q else i+1; runs.append((st/100, en/100)); st=None
    return runs

def idx(word, nth=1):
    n=0
    for i,w in enumerate(words):
        if w["w"]==word:
            n+=1
            if n==nth: return i
    raise KeyError(word)
# figure out which "it's" is "it's still"
its = [i for i,w in enumerate(words) if w["w"]=="it's"]
still_i = [i for i in its if words[i+1]["w"]=="still"][0]
protected = {idx("there's"), still_i}

cuts = []  # (start, end, reason)
first_i = [i for i,w in enumerate(words) if w['w']==FIRST_WORD][0]
for i in range(first_i + 1, len(words)):
    gap0, gap1 = words[i-1]["e"], words[i]["s"]
    if i in protected: continue
    # search quiet runs in a slightly widened window, but never past neighbouring word centres
    lo = max(gap0 - 0.10, (words[i-1]["s"]+words[i-1]["e"])/2)
    hi = min(gap1 + 0.10, (words[i]["s"]+words[i]["e"])/2)
    for qs, qe in quiet_runs(lo, hi):
        if qe - qs > MAXGAP:
            cs, ce = round(qs + PAD, 2), round(qe - PAD, 2)
            cuts.append((cs, ce, f'{words[i-1]["w"]} | {words[i]["w"]}'))
start = round(words[first_i]["s"] - PAD, 2)
keep = []; t = start
for cs, ce, _ in cuts:
    keep.append((t, cs)); t = ce
keep.append((t, CLIP_END))
def out(tsrc):
    o = 0.0
    for k0, k1 in keep:
        if tsrc < k0: return o / SPEED  # inside a cut -> snaps to next kept point
        if tsrc <= k1: return (o + (tsrc - k0)) / SPEED
        o += k1 - k0
    return o / SPEED
aroll_len = sum(k1-k0 for k0,k1 in keep) / SPEED
total = out(SPEECH_END) + HOLD
fr = lambda x: round(round(x*FPS)/FPS, 4)
for w in words: w["os"], w["oe"] = round(out(w["s"]),3), round(out(w["e"]),3)
W = lambda word, nth=1: words[idx(word, nth)]
# ---- structure (output times, frame-snapped) ----
c_carried = fr(W("carried")["os"] - 0.08)
c_half    = fr(W("half")["os"] - 0.06)
the_m = [i for i,w in enumerate(words) if w["w"]=="the" and words[i+1]["w"]=="moment"][0]
c_moment  = fr(words[the_m]["os"] - 0.06)
your_mac = [i for i,w in enumerate(words) if w["w"]=="your" and words[i+1]["w"]=="mac"][0]
c_mac     = fr(words[your_mac]["os"] - 0.06)
stops = W("stops"); blk_end = fr(stops["oe"]); blk_start = fr(blk_end - 0.4)
called_i = [i for i in its if words[i+1]["w"]=="called"][0]
t_called = fr(words[called_i]["os"] - 0.05)
t_small = fr(W("small")["os"] - 0.05)
t_youset = fr(words[[i for i,w in enumerate(words) if w["w"]=="you" and words[i+1]["w"]=="set"][0]]["os"] - 0.05)
close_lid = [i for i,w in enumerate(words) if w["w"]=="close" and words[i+1]["w"]=="the"][0]
t_close = fr(words[close_lid]["os"] - 0.05)
t_when = fr(W("when")["os"] - 0.05)
t_still = fr(words[still_i]["os"] - 0.05)
on_desk = [i for i,w in enumerate(words) if w["w"]=="on" and words[i+1]["w"]=="a"][0]
t_paper = fr(words[on_desk]["os"] - 0.05)
t_paper_end = fr(W("bag")["oe"] + 0.15)
t_want = fr(W("want")["os"] - 0.05)
total = fr(total)
walk = [  # (clip, src_in, out_start, out_end)
    ("clipA_1102", 5.85, 0.0, c_carried),
    ("clipB_c1",   6.50, c_carried, c_half),
    ("clipC_c2",   0.15, c_half, c_moment),
    ("clipC_c2",   7.00, c_moment, c_mac),
    ("clipB_c1",   8.78, c_mac, blk_start),
]
sections = [{"type":"walk","clip":c,"src":s,"a":a_,"b":b} for c,s,a_,b in walk]
sections += [{"type":"black","a":blk_start,"b":blk_end},
             {"type":"full","a":blk_end,"b":t_called},
             {"type":"split","a":t_called,"b":t_still,"assets":[
                 ["header",t_called,t_small],["eye",t_small,t_youset],["duration",t_youset,t_close],
                 ["lid",t_close,t_when],["countdown",t_when,t_still]]},
             {"type":"full","a":t_still,"b":t_paper},
             {"type":"paper","a":t_paper,"b":t_paper_end},
             {"type":"full","a":t_paper_end,"b":total,"cta_from":t_want}]
tl = dict(fps=FPS, keep=keep, cuts=cuts, words=words, aroll_len=round(aroll_len,3), total=total,
          freeze=round(total-aroll_len,3), sections=sections, speed=SPEED, first_word=FIRST_WORD, hook_window=c_carried, cta_start=t_want)
json.dump(tl, open(f"{E}/build/timeline.json","w"), indent=1)
print(f"start trim at {start}s (camera setup before)")
print("CUTS (source seconds):")
for cs,ce,r in cuts: print(f"  {cs:6.2f}-{ce:6.2f}  ({ce-cs:.2f}s)  between '{r}'")
ti=idx("there's"); print(f"protected pauses kept: before There's {words[ti]['s']-words[ti-1]['e']:.2f}s, before It's still {words[still_i]['s']-words[still_i-1]['e']:.2f}s")
print(f"A-roll {aroll_len:.2f}s + freeze {total-aroll_len:.2f}s = total {total:.2f}s")
for s in sections: print(f"  {s['type']:6s} {s['a']:6.2f}-{s['b']:6.2f} ({s['b']-s['a']:.2f}s) {s.get('clip','')} {s.get('src','')}")
for a_ in next(x for x in sections if x["type"]=="split")["assets"]: print(f"     asset {a_[0]:10s} {a_[1]:6.2f}-{a_[2]:6.2f} ({a_[2]-a_[1]:.2f}s)")
