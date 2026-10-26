"""Build harvey subtitles: 2-5 word chunks, yellow highlights, position by layout mode."""
import sys
from timeline import words, TOTAL, mode_at
CHUNKS = ["Brooo.", "Someone just built an", "AI agent whose", "only job is", "*finding you customers.", "It's called", "*Harvey.",
 "And it's", "*open source.", "You tell it", "two things.", "What you sell,", "and who you want", "to sell to.", "That's it.",
 "Then it goes off", "on its own,", "finds those companies,", "reads their websites,", "and digs out", "the right people",
 "and their emails.", "Then it writes", "each of them", "a personal cold email.", "Sends it.", "Replies when they reply.",
 "And books the meeting.", "Every 15 minutes", "it wakes up,", "does its work,", "and goes back to sleep.",
 "Basically a salesperson who", "*never takes leave.", "The code's free.", "It runs on your", "Claude Max subscription.",
 "Want the setup guide?", "Comment", "*'HARVEY'.", "I'll DM it to you."]
MARGIN = {"full": 330, "split": 970}   # split: strip just above the divider, clear of his mouth
i = 0; ev = []
for c in CHUNKS:
    hl = c.startswith("*"); c = c.lstrip("*"); n = 1
    while " ".join(x["w"] for x in words[i:i + n]) != c:
        n += 1; assert n <= 8, (c, [x["w"] for x in words[i:i + 6]])
    ws = words[i:i + n]
    ev.append([ws[0]["s"], ws[-1]["e"], c.rstrip(",.").strip("'").replace("'.", "").replace("HARVEY'", "HARVEY"), hl]); i += n
assert i == len(words), (i, len(words))
for k in range(len(ev)):
    nxt = ev[k + 1][0] if k + 1 < len(ev) else TOTAL
    ev[k][1] = nxt if nxt - ev[k][1] < 0.35 else ev[k][1] + 0.15
ev[-1][1] = TOTAL
# a chunk must not straddle a layout switch: end it at the switch
from timeline import SEGMENTS
switches = [s for s, e, m, c in SEGMENTS[1:] if mode_at(s - 0.001)[0] != m]
for e in ev:
    for sw in switches:
        if e[0] < sw < e[1]: e[1] = sw
def ts(x): return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"
hdr = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Montserrat,60,&H00000000,&H00000000,&H00FFFFFF,&H00FFFFFF,-1,0,0,0,100,100,0,0,3,13,0,2,60,60,330,1
Style: Highlight,Montserrat,60,&H00000000,&H00000000,&H0000D6FF,&H0000D6FF,-1,0,0,0,100,100,0,0,3,13,0,2,60,60,330,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
with open(sys.argv[1], "w") as fo:
    fo.write(hdr)
    for s, e, t, hl in ev:
        mv = MARGIN[mode_at(s + 0.001)[0]]
        fo.write(f"Dialogue: 0,{ts(s)},{ts(e)},{'Highlight' if hl else 'Main'},,0,0,{mv},,{t}\n")
for s, e, t, hl in ev: print(f"{s:6.2f}-{e:6.2f} {mode_at(s + 0.001)[0]:5s} {'[HL] ' if hl else ''}{t}")
