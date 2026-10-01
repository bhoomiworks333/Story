"""Edit decision list for the fine-tuning reel (v3). All times are source seconds.

v3 rules from the client: the talking head stays exactly as shot (no trim, no zoom,
no reframe); every image sits at the top of the frame over the video.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
SRC_DUR = 59.0

# Speech onsets/offsets after pauses (from silencedetect). Captions snap to these.
ONSETS = [14.42, 17.67, 23.91, 25.73, 28.81, 36.12, 38.32, 41.14, 45.55, 48.76]
OFFSETS = [14.17, 17.35, 23.53, 25.35, 28.42, 35.80, 36.82, 40.64, 45.22, 48.43, 58.54]

# Viewer comments stack in one by one on "a lot of you asked", then leave together.
COMMENTS = dict(keys=["01_comment_1_rahul", "01_comment_2_avik", "01_comment_3_rajat", "01_comment_4_dharmik"],
                starts=[1.62, 2.10, 2.58, 3.06], e=4.86, tilt=[-2.5, 2.0, -1.5, 2.5])

# Top images: shown from s to e (pop in, quick out).
CARDS = [
    dict(key="02_hf_model",     s=15.78, e=22.86),  # "a model that already exists" -> off on "fine-tuning"
    dict(key="03_dataset",      s=24.81, e=28.19),  # "a dataset"
    dict(key="04_unsloth_gh",   s=28.19, e=31.30),  # exactly on "Unsloth"
    dict(key="06_rtx4090",      s=31.30, e=34.65),  # "an RTX 4090"
    dict(key="05_colab",        s=34.65, e=37.02),  # "Google Colab", through "then you train it"
    dict(key="07_before_after", s=39.63, e=42.87),  # "you test it", held through "GPU towers" so it can be read
]

# Pops: every image entrance (each comment included).
POPS = COMMENTS["starts"] + [c["s"] for c in CARDS]


def captions():
    raw = json.load(open(os.path.join(HERE, "chunks_raw.json")))
    out = [dict(text=c["text"], s=c["s"], e=c["e"]) for c in raw]
    # each measured onset/offset snaps only the single nearest caption edge
    for o in ONSETS:
        c = min(out, key=lambda c: abs(c["s"] - o))
        if abs(c["s"] - o) < 0.45: c["s"] = o
    for o in OFFSETS:
        c = min(out, key=lambda c: abs(c["e"] - o))
        if abs(c["e"] - o) < 0.45: c["e"] = o
    # display: hold until next caption if the gap is short, else word end + 0.2 s
    for i, c in enumerate(out):
        nxt = out[i + 1]["s"] if i + 1 < len(out) else SRC_DUR
        c["show_e"] = nxt if nxt - c["e"] < 0.45 else min(c["e"] + 0.2, nxt)
    return out


if __name__ == "__main__":
    for c in captions():
        print(f"{c['s']:6.2f} {c['show_e']:6.2f}  {c['text']}")
