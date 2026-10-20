"""Burn word-synced subtitles (white rounded box, black text) onto the reel.

Timing comes from words_asr.json (Parakeet word starts on the ORIGINAL
footage). Spelling is corrected to the script; wording follows the audio.
Pass --cuts cut_plan.json to remap times onto the trimmed footage.

usage: python3 subtitles.py IN.mp4 OUT.mp4 [--cuts cut_plan.json] [--srt OUT.srt]
"""
import argparse, json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
SIZE, PAD_X, PAD_Y, RADIUS = 46, 22, 12, 14
Y_CENTER = 0.70            # fraction of height; clear of IG caption/UI area
MAX_WORDS, MAX_CHARS = 4, 20
GLUE = {"a", "the", "in", "his", "to", "at", "of", "on", "he", "so", "and", "but", "it", "can", "10", "i", "those", "you", "is"}
LEAD = 0.05                # show a chunk slightly before its first word
POP = 0.08                 # pop-in duration (s)

# ASR spelling -> script spelling (audio wording is kept)
FIX = {"Vibeshan": "Vibhishan", "Dashara.": "Dussehra."}


def load_words(path):
    w = json.load(open(path))
    out = []
    i = 0
    while i < len(w):
        s, e, t = w[i]
        if t == "the" and i + 1 < len(w) and w[i + 1][2].startswith("Shara"):
            out.append([s, w[i + 1][1], "Dussehra,"])   # "on the Shara," = "on Dussehra,"
            i += 2
            continue
        out.append([s, e, FIX.get(t, t)])
        i += 1
    return out


def chunk(words):
    chunks, cur = [], []
    for w in words:
        text = " ".join(x[2] for x in cur + [w])
        if cur and (len(cur) >= MAX_WORDS or len(text) > MAX_CHARS):
            carry = []
            while len(cur) > 1 and cur[-1][2].lower() in GLUE:   # don't end a box on "the"
                carry.insert(0, cur.pop())
            chunks.append(cur); cur = carry
        cur.append(w)
        if w[2][-1] in ".,?!":
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    return [[c[0][0], " ".join(x[2] for x in c)] for c in chunks]


def remap(t, cuts):
    shift = 0.0
    for a, b in cuts:
        if t >= b: shift += b - a
        elif t > a: return a - shift
    return t - shift


def render_box(text, font):
    l, t, r, b = font.getbbox(text)
    w, h = r - l + 2 * PAD_X, SIZE + 2 * PAD_Y
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], RADIUS, fill=(255, 255, 255, 255))
    d.text((PAD_X - l, h / 2), text, font=font, fill=(0, 0, 0, 255), anchor="lm")
    return img


def probe(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate:format=duration", "-of", "json", path])
    j = json.loads(out); s = j["streams"][0]
    n, d = map(int, s["r_frame_rate"].split("/"))
    return s["width"], s["height"], n / d, float(j["format"]["duration"])


def srt_time(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--words", default="words_asr.json")
    ap.add_argument("--cuts"); ap.add_argument("--srt")
    a = ap.parse_args()
    W, H, fps, dur = probe(a.inp)
    cuts = json.load(open(a.cuts))["cuts"] if a.cuts else []
    ch = [[remap(s, cuts), t] for s, t in chunk(load_words(a.words))]
    cues = []
    for i, (s, t) in enumerate(ch):
        end = ch[i + 1][0] - LEAD if i + 1 < len(ch) else dur
        cues.append((max(0, s - LEAD), end, t))
    if a.srt:
        with open(a.srt, "w") as f:
            for i, (s, e, t) in enumerate(cues, 1):
                f.write(f"{i}\n{srt_time(s)} --> {srt_time(e)}\n{t}\n\n")
    font = ImageFont.truetype(FONT, SIZE)
    boxes = [render_box(t, font) for _, _, t in cues]
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-i", a.inp,
        "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
        "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
        "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "18", "-preset", "slow",
        "-c:a", "copy", "-r", str(fps), a.out], stdin=subprocess.PIPE)
    blank = Image.new("RGBA", (W, H), (0, 0, 0, 0)).tobytes()
    nframes, ci = int(round(dur * fps)), 0
    for f in range(nframes):
        t = f / fps
        while ci < len(cues) and t >= cues[ci][1]: ci += 1
        if ci < len(cues) and t >= cues[ci][0]:
            box = boxes[ci]
            k = min(1.0, (t - cues[ci][0]) / POP)
            sc = 0.88 + 0.12 * k
            b = box.resize((max(1, int(box.width * sc)), max(1, int(box.height * sc))), Image.LANCZOS) if sc < 1 else box
            fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            fr.alpha_composite(b, (int((W - b.width) / 2), int(H * Y_CENTER - b.height / 2)))
            ff.stdin.write(fr.tobytes())
        else:
            ff.stdin.write(blank)
    ff.stdin.close(); sys.exit(ff.wait())


if __name__ == "__main__":
    main()
