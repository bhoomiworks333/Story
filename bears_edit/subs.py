# Step 7: subtitle chunks (spoken wording, script spelling) aligned to word timestamps
import json, re, difflib
CHUNKS = ["Google,", "I *expected*", "*a lot more*", "from you.", "Same prompt to", "Claude Opus 5.5", "and Gemini 4 Argon.",
          "Make gummy bears", "you can play with.", "Look at this.", "Claude's bears behave", "like *real jelly.*",
          "Pull a paw, it stretches,", "snaps back and wobbles.", "Gemini's? Basically", "*plastic.*", "Stiff arms",
          "and they pass right through", "each other.", "And the worst part?", "Claude's version cost", "about $7",
          "and Gemini's?", "*$22.*", "Three times the money", "for the worst bears.", "It's one test,",
          "so I'm not calling it yet.", "But always check", "what it cost.", "Which one would you", "have *bet on?*"]
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
def chunks():
    W = json.load(open("work/words_out.json"))
    toks = [(ci, w) for ci, c in enumerate(CHUNKS) for w in c.replace("*", "").split()]
    A = [norm(w) for _, w in toks]; B = [norm(w["w"]) for w in W]
    st, en = [None] * len(A), [None] * len(A)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
        if tag in ("equal", "replace") and j2 > j1:
            s0, e0, n = W[j1]["s"], W[j2 - 1]["e"], i2 - i1
            for k in range(n): st[i1 + k] = s0 + (e0 - s0) * k / n; en[i1 + k] = s0 + (e0 - s0) * (k + 1) / n
            if tag == "equal":
                for k in range(n): st[i1 + k], en[i1 + k] = W[j1 + k]["s"], W[j1 + k]["e"]
    for i in range(len(A)):                      # words with no match: borrow the neighbour's time
        if st[i] is None:
            p = next(j for j in range(i - 1, -1, -1) if en[j] is not None); st[i] = en[i] = en[p]
    out = []
    for ci, c in enumerate(CHUNKS):
        idx = [i for i, (k, _) in enumerate(toks) if k == ci]
        out.append({"text": c, "s": st[idx[0]], "e": en[idx[-1]]})
    for a, b in zip(out, out[1:]): a["e"] = min(max(a["e"] + 0.25, a["e"]), b["s"])   # hold briefly, never overlap
    out[-1]["e"] += 0.6
    return out
if __name__ == "__main__":
    for c in chunks(): print(f"{c['s']:6.2f} {c['e']:6.2f}  {c['text']}")
