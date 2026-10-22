"""Shared timeline for the Claude Duet reel. All times in seconds on the final timeline."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "..", "work")
WAKE_LEN = 5.4333333          # graded wake-up section length
TALK_IN = 1.20                # talking clip source in-point
OFF = WAKE_LEN - TALK_IN      # talking source time -> final time
TALK_END = 39.10 + OFF        # last real frame of talking clip
TOTAL = TALK_END + 1.5        # 1.5s freeze hold

words = json.load(open(os.path.join(WORK, "words.json")))
def w(text, n=1):
    """Final-timeline (start, end) of the n-th occurrence of a word."""
    k = 0
    for x in words:
        if x["w"].strip(",.?").lower() == text.lower():
            k += 1
            if k == n: return x["s"] + OFF, x["e"] + OFF
    raise KeyError(text)

# Full-screen inserts: (name, start, end, source, label)
INSERTS = [
    ("header", w("Claude")[0], w("Every")[0], "ins_header.png", "label_demo"),
    ("brief",  w("Every")[0],  w("unpaid")[1], "ins_brief.mp4", "label_video"),
    ("chat",   w("message")[0], w("meeting", 2)[1], "ins_chat.mp4", "label_video"),
    ("appr",   w("email")[0], w("first")[1], "ins_appr.mp4", "label_video"),
]
ACCESS = (w("Right")[0], w("waitlist")[1])
NOTIF_IN = 2.22               # start of the scrolling shot
MUSIC_IN = w("That's")[0]
MUSIC_DIP = w("So")[0]
TAP_AT = w("asks")[0]
HIDE = [(s, e) for _, s, e, _, _ in INSERTS] + [ACCESS]
