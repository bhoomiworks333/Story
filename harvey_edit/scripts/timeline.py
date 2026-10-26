"""Shared timeline for the Harvey reel. Word times come from the source clip; final = src (minus the DM-stutter cut)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "..", "work")
CUT_AT, CUT_LEN = 40.01, 0.39          # removed the first "DM"
TALK_END = 41.378 - CUT_LEN            # last real frame
TOTAL = 42.4667                        # base_src.mp4 length incl. 1.5s hold
def f(t): return t if t < CUT_AT else t - CUT_LEN
words = [dict(x, s=f(x["s"]), e=f(x["e"])) for x in json.load(open(os.path.join(WORK, "words.json")))]
def w(text, n=1):
    k = 0
    for x in words:
        if x["w"].strip(",.?'") == text:
            k += 1
            if k == n: return x["s"], x["e"]
    raise KeyError(text)
S = lambda t, n=1: w(t, n)[0]
# (start, end, mode, card)   card None = no top graphic
SEGMENTS = [
    (0.0,           S("AI"),        "full",  None),
    (S("AI"),       S("You"),       "split", "repo"),
    (S("You"),      S("That's"),    "split", "inputs"),
    (S("That's"),   S("Then"),      "full",  None),
    (S("Then"),     S("Then", 2),   "split", "readme"),
    (S("Then", 2),  S("Sends"),     "split", "email"),
    (S("Sends"),    S("Replies"),   "split", "outbox"),
    (S("Replies"),  S("And", 2),    "split", "reply"),
    (S("And", 2),   S("Every"),     "split", "booking"),
    (S("Every"),    S("Basically"), "split", "heartbeat"),
    (S("Basically"),S("The"),       "full",  None),
    (S("The"),      S("Want"),      "split", "cost"),
    (S("Want"),     TOTAL,          "full",  "cta"),
]
REPO_ZOOM = (S("It's"), S("You"))
PILL_AT = S("open")
INPUT1_AT, INPUT2_AT = S("What"), S("who")
CTA_AT = S("Comment")
WHOOSH_AT, CHIME_AT = S("Sends"), S("books")
DIP = (S("Basically"), S("The"))
MUSIC_IN = w("Brooo")[1]
def mode_at(t):
    for s, e, m, c in SEGMENTS:
        if s <= t < e: return m, c, s
    return SEGMENTS[-1][2], SEGMENTS[-1][3], SEGMENTS[-1][0]
