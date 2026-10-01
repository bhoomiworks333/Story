"""Edit decision list for the fine-tuning reel. All times are SOURCE seconds."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
SRC_DUR = 59.0

# Dead-air trim: "...train it." [1.5 s pause + breath] "and after training"
# Cut points sit inside measured silence (36.82-37.45, 37.68-38.32), leaving ~0.4 s pause.
CUT = (37.00, 38.10)

# Speech onsets after pauses (from silencedetect). Captions snap to these.
ONSETS = [14.42, 17.67, 23.91, 25.73, 28.81, 36.12, 38.32, 41.14, 45.55, 48.76]
OFFSETS = [14.17, 17.35, 23.53, 25.35, 28.42, 35.80, 36.82, 40.64, 45.22, 48.43, 58.54]

# Asset cards (top of frame, reference layout). Each shows from `s` until the next card/full-screen starts.
CARDS = [
    dict(key="02_hf_model",     s=15.78, label="Hugging Face model page"),  # "a model that already exists"
    dict(key="04_unsloth_gh",   s=27.36, label="unsloth on GitHub"),        # "a tool like Unsloth"
    dict(key="06_rtx4090",      s=31.30, label="GeForce RTX 4090"),         # "an RTX 4090"
    dict(key="07_before_after", s=38.32, label="Before / after"),           # "and after training you test it"
]
# Full-screen assets: hide the speaker and captions entirely (voice continues).
FULLS = [
    dict(key="03_dataset_full", s=23.91, e=27.36, bg=(11, 15, 25)),  # "You need a dataset. Once that's ready, you can use"
    dict(key="05_colab_full",   s=34.65, e=CUT[0], bg=(19, 19, 20)), # "Google Colab GPUs. Then you train it" -> cut hides the jump
]
CARDS_END = 43.00          # cards leave as "no cinematic" starts
REFRAME_IN = (15.30, 15.70)  # speaker slides down to make room for the card
REFRAME_OUT = (43.05, 43.50)

# Subtle punch-ins (scale, anchor y as fraction of frame). Hard cuts on speech beats.
PUNCH = [
    dict(s=6.69, e=9.12, z=1.07),    # "You don't train a foundation model from zero"
    dict(s=CUT[1], e=REFRAME_OUT[1], z=1.05),  # hides the jump cut at the dead-air trim
    dict(s=57.24, e=SRC_DUR, z=1.07),  # CTA "Comment TRAIN"
]

# Pops: every asset entrance + the CTA keyword.
POPS = sorted([c["s"] for c in CARDS] + [f["s"] for f in FULLS]) + [57.24 + 0.33]  # entrances + "TRAIN"


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


def src_to_out(t):
    if t <= CUT[0]: return t
    if t >= CUT[1]: return t - (CUT[1] - CUT[0])
    return CUT[0]


if __name__ == "__main__":
    for c in captions():
        print(f"{c['s']:6.2f} {c['show_e']:6.2f}  {c['text']}")
