import sys
from timeline import words, OFF, TOTAL, HIDE
CHUNKS = ["Imagine waking up,", "and your AI has", "*already texted you.", "That's what Anthropic", "just launched.",
 "It's called", "*Claude Duet.", "Every morning it tells you", "what's going on,", "which invoices are", "*unpaid,",
 "which client replied,", "and which meeting", "needs you today.", "Then you just", "message it like you'd",
 "message a teammate.", "Set up this meeting,", "build me a deck,", "chase this payment.", "And it keeps working",
 "while you're away.", "Before it sends", "an email or", "pays anything, it", "*asks you first.", "Right now it's only",
 "for Pro and Max users", "in the US, on a waitlist.", "So, honest question.", "Would you let AI", "handle your inbox?", "*Yes or no?"]
i = 0; ev = []
for c in CHUNKS:
    hl = c.startswith("*"); c = c.lstrip("*"); n = len(c.split())
    ws = words[i:i+n]
    assert " ".join(x["w"] for x in ws) == c, (c, [x["w"] for x in ws])
    ev.append([ws[0]["s"] + OFF, ws[-1]["e"] + OFF, c.rstrip(",."), hl]); i += n
assert i == len(words)
for k in range(len(ev)):              # hold each chunk until the next starts (if gap < 0.35s)
    nxt = ev[k+1][0] if k+1 < len(ev) else TOTAL
    ev[k][1] = nxt if nxt - ev[k][1] < 0.35 else ev[k][1] + 0.15
ev[-1][1] = TOTAL
out = []
for s, e, t, hl in ev:
    if not hl:                         # plain chunks are hidden under inserts / access card
        for hs, he in HIDE:
            if s < he and e > hs:
                if s >= hs: s = max(s, he)
                else: e = min(e, hs)
        if e - s < 0.25: continue
    out.append((s, e, t, hl))
def ts(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
hdr = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Montserrat,74,&H00000000,&H00000000,&H00FFFFFF,&H00FFFFFF,-1,0,0,0,100,100,0,0,3,14,0,2,60,60,500,1
Style: Highlight,Montserrat,74,&H00000000,&H00000000,&H0000D7FF,&H0000D7FF,-1,0,0,0,100,100,0,0,3,14,0,2,60,60,500,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
with open(sys.argv[1], "w") as f:
    f.write(hdr)
    for s, e, t, hl in out:
        f.write(f"Dialogue: 0,{ts(s)},{ts(e)},{'Highlight' if hl else 'Main'},,0,0,0,,{t}\n")
for s, e, t, hl in out: print(f"{s:6.2f}-{e:6.2f} {'[HL] ' if hl else ''}{t}")
