"""Renders all overlays (subtitles, hook, paper, chart, 6/10) as RGBA frames.

Usage:
  python3 overlays.py still <t> <graded.mp4> <out.png>   # preview one time
  python3 overlays.py stream                              # raw RGBA frames to stdout
"""
import json, os, sys, subprocess
from PIL import Image, ImageChops, ImageDraw, ImageFont

W, H, FPS = 720, 1280, 30
DUR = 45.833
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONT_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONT_SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
WHITE, BLACK, YELLOW = (255, 255, 255, 255), (0, 0, 0, 255), (255, 214, 10, 255)
PAPER = os.path.join(HERE, "paper_psycnet.png")  # APA PsycNet listing (mobile), supplied by user
PAPER_KEEP = [(0, 240), (600, 776)]  # header+title, authors+citation; middle clutter cut
PAPER_HL = (10, 110, 397, 143)  # "Unskilled and unaware of it:" in source pixels

# (start_s, [(text, highlighted), ...]). Starts come from Vosk word timings.
SUBS = [
    (7.80, [("Quickly, in your head", 0)]),
    (9.15, [("rate how well", 0)]),
    (10.08, [("you understand AI.", 0)]),
    (11.58, [("1 to 10.", 1)]),
    (12.54, [("Got a number?", 0)]),
    (13.68, [("If you said", 0)]),
    (14.31, [("eight", 1), ("or above,", 0)]),
    (15.24, [("this is for you.", 0)]),
    (16.50, [("There's a famous", 0)]),
    (17.27, [("psychology study.", 0)]),
    (18.45, [("The people who", 0)]),
    (19.23, [("scored", 0), ("lowest", 1)]),
    (20.28, [("on a test", 0)]),
    (21.39, [("thought they were", 0)]),
    (21.99, [("above average.", 0)]),
    (22.86, [("The people who", 0)]),
    (23.76, [("actually knew the most", 0)]),
    (25.38, [("underrated themselves.", 0)]),
    (28.26, [("It's called the", 0)]),
    (28.80, [("Dunning-Kruger effect.", 0)]),
    (30.00, [("I build AI", 0)]),
    (31.08, [("into factories", 0)]),
    (31.62, [("every day,", 0)]),
    (32.55, [("and honestly,", 0)]),
    (33.54, [("I'd give myself", 0)]),
    (34.62, [("a", 0), ("six.", 1)]),
    (35.58, [("Every month", 0)]),
    (36.36, [("I found out", 0)]),
    (37.20, [("how much I", 0)]),
    (37.86, [("still don't know.", 0)]),
    (38.94, [("So if your", 0)]),
    (39.84, [("number was high,", 0)]),
    (41.04, [("maybe hold", 0)]),
    (41.62, [("that thought.", 0)]),
    (42.54, [("Comment your number.", 0)]),
    (43.59, [("Be", 0), ("honest.", 1)]),
]
# Kept ranges of the source, in frames (30fps): start just before the camera lift, cut the "under-" fumble
KEEP = [(189, 759), (789, 1375)]
HOOK = (6.0, 12.54)  # first output frame already shows it fully; ends when "Got a number?" appears
PAPER_T = (16.6, 18.6)
CHART_T = (19.2, 25.4)
SIX_T = (34.75, 36.2)

SUB_Y = 1005  # vertical centre: below the face, above Instagram's caption UI
_font_cache = {}


def font(path, size):
    k = (path, size)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(path, size)
    return _font_cache[k]


def sub_timeline():
    words = json.load(open(os.path.join(HERE, "vosk_words.json")))
    out = []
    for i, (s, segs) in enumerate(SUBS):
        if i + 1 < len(SUBS):
            nxt = SUBS[i + 1][0]
            # last spoken word before the next chunk; close the gap if there is a pause
            ends = [w["end"] for w in words if s <= w["start"] < nxt]
            e = min(nxt, (max(ends) if ends else nxt) + 0.5)
        else:
            e = DUR  # hold the CTA to the end so the loop lands on it
        out.append((s, e, segs))
    return out


def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def pill_row(segs, size, pad_x, pad_y, radius, fnt_path=FONT_XB, inner=None):
    """Text segments on contiguous boxes: white box/black text, yellow box for highlights."""
    f = font(fnt_path, size)
    asc, desc = f.getmetrics()
    h = asc + desc + 2 * pad_y
    widths = []
    inner = pad_x if inner is None else inner
    lefts = []
    for i, (txt, _) in enumerate(segs):
        l = pad_x if i == 0 else inner
        r = pad_x if i == len(segs) - 1 else inner
        lefts.append(l)
        widths.append(int(f.getlength(txt) + l + r))
    total = sum(widths)
    img = Image.new("RGBA", (total, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # outer white pill, then yellow segments clipped to it
    d.rounded_rectangle((0, 0, total - 1, h - 1), radius, fill=WHITE)
    x = 0
    for (txt, hl), w in zip(segs, widths):
        if hl:
            seg = Image.new("RGBA", (total, h), (0, 0, 0, 0))
            ImageDraw.Draw(seg).rectangle((x, 0, x + w, h), fill=YELLOW)
            mask = Image.new("L", (total, h), 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, total - 1, h - 1), radius, fill=255)
            img.paste(seg, (0, 0), Image.composite(seg.getchannel("A"), Image.new("L", (total, h), 0), mask))
        x += w
    x = 0
    for (txt, _), w, l in zip(segs, widths, lefts):
        d.text((x + l, pad_y), txt, font=f, fill=BLACK)
        x += w
    return img


def paste_scaled(canvas, img, cx, cy, scale=1.0, alpha=1.0):
    if scale != 1.0:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.LANCZOS)
    if alpha < 1.0:
        a = img.getchannel("A").point(lambda v: int(v * alpha))
        img = img.copy(); img.putalpha(a)
    canvas.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))


def emoji(ch, size):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * size / im.height), size), Image.LANCZOS)


def build_static():
    st = {}
    # hook: two lines, top third
    l1 = pill_row([("Rate your AI knowledge:", 0)], 46, 20, 12, 14)
    l2 = pill_row([("1–10", 1)], 64, 26, 10, 16)
    e = emoji("🤔", l2.height - 6)
    row2 = Image.new("RGBA", (l2.width + 14 + e.width, l2.height), (0, 0, 0, 0))
    row2.alpha_composite(l2, (0, 0)); row2.alpha_composite(e, (l2.width + 14, 3))
    hook = Image.new("RGBA", (max(l1.width, row2.width), l1.height + 12 + row2.height), (0, 0, 0, 0))
    hook.alpha_composite(l1, ((hook.width - l1.width) // 2, 0))
    hook.alpha_composite(row2, ((hook.width - row2.width) // 2, l1.height + 12))
    st["hook"] = hook
    # 6/10 punch
    st["six"] = pill_row([("6", 1), ("/10", 0)], 150, 30, 6, 34, inner=12)
    st["subs"] = [(s, e, pill_row(segs, 40, 16, 9, 12)) for s, e, segs in sub_timeline()]
    src = Image.open(PAPER).convert("RGB")
    # paint out the site's hamburger menu icon with the header's own background colour
    bgc = src.getpixel((500, 46))
    ImageDraw.Draw(src).rectangle((520, 20, src.width, 72), fill=bgc)
    parts = [src.crop((0, a, src.width, b)) for a, b in PAPER_KEEP]
    gap = 36
    comp = Image.new("RGB", (src.width, sum(p.height for p in parts) + gap), (255, 255, 255))
    comp.paste(parts[0], (0, 0)); comp.paste(parts[1], (0, parts[0].height + gap))
    st["paper"] = comp
    return st


def chart(t):
    """'What they thought vs reality' card. Bars grow in with the voice-over."""
    cw, ch = 620, 318
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, cw - 1, ch - 1), 28, fill=WHITE)
    d.text((28, 20), "What they thought vs. reality", font=font(FONT_XB, 32), fill=BLACK)
    d.text((28, 62), "Lowest-scoring 25% · percentile rank", font=font(FONT_SB, 21), fill=(90, 90, 90, 255))
    track_x0, track_x1 = 160, cw - 28
    rows = [
        # label, value, colour, appears at (s) -- 12th/62nd from Kruger & Dunning (1999) abstract
        ("Thought", 62, (30, 30, 30, 255), 21.39),
        ("Reality", 12, YELLOW, 19.23),
    ]
    y = 104
    for label, val, col, t0 in rows:
        p = ease_out((t - t0) / 0.6)
        d.text((28, y + 6), label, font=font(FONT_B, 27), fill=BLACK)
        d.rounded_rectangle((track_x0, y, track_x1, y + 44), 10, fill=(236, 236, 236, 255))
        bw = (track_x1 - track_x0) * val / 100 * p
        if bw > 4:
            d.rounded_rectangle((track_x0, y, track_x0 + bw, y + 44), 10, fill=col)
        if p > 0.05:
            d.text((track_x0 + bw + 10, y + 7), {12: "12th", 62: "62nd"}[val], font=font(FONT_XB, 27), fill=BLACK)
        y += 58
    # top scorers line appears with "the people who actually knew the most"
    a = ease_out((t - 22.86) / 0.4)
    if a > 0:
        d.line((28, y + 4, cw - 28, y + 4), fill=(220, 220, 220, 255), width=2)
        txt = Image.new("RGBA", (cw, 70), (0, 0, 0, 0))
        ImageDraw.Draw(txt).text((28, 0), "Top 25%: rated themselves", font=font(FONT_B, 26), fill=BLACK)
        ImageDraw.Draw(txt).text((28, 33), "LOWER than they really were", font=font(FONT_XB, 26), fill=BLACK)
        txt.putalpha(txt.getchannel("A").point(lambda v: int(v * a)))
        card.alpha_composite(txt, (0, y + 16))
    return card


def frame(t, st):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # paper: full screen, white background, 100 -> 115% push-in
    if "paper" in st and PAPER_T[0] <= t < PAPER_T[1]:
        p = (t - PAPER_T[0]) / (PAPER_T[1] - PAPER_T[0])
        fade = min(1.0, (t - PAPER_T[0]) / 0.15, (PAPER_T[1] - t) / 0.15)
        bg = Image.new("RGBA", (W, H), WHITE)
        pi = st["paper"].copy()
        # yellow marker wipes across the title phrase; multiply keeps the blue text on top
        hp = ease_out((t - PAPER_T[0] - 0.25) / 0.5)
        if hp > 0:
            x0, y0, x1, y1 = PAPER_HL
            hl = Image.new("RGB", pi.size, (255, 255, 255))
            ImageDraw.Draw(hl).rectangle((x0, y0, x0 + (x1 - x0) * hp, y1), fill=(255, 225, 60))
            pi = ImageChops.multiply(pi, hl)
        # push-in 100 -> 115%, anchored on the title's left edge so "Unskilled" never crops
        s0 = W / pi.width
        sc = s0 * (1.0 + 0.15 * ease_out(p))
        img = pi.resize((int(pi.width * sc), int(pi.height * sc)), Image.LANCZOS).convert("RGBA")
        ax, ay = PAPER_HL[0], (PAPER_HL[1] + PAPER_HL[3]) / 2
        sx = ax * s0 + (14 - ax * s0) * ease_out(p)  # anchor drifts to a 14px margin
        bg.alpha_composite(img, (int(sx - ax * sc), int(470 - ay * sc)))
        bg.putalpha(int(255 * fade))
        c.alpha_composite(bg)
    if HOOK[0] <= t < HOOK[1]:
        a = min(1.0, (HOOK[1] - t) / 0.2)
        s = 0.9 + 0.1 * ease_out((t - HOOK[0]) / 0.25)
        paste_scaled(c, st["hook"], W / 2, 250, s, a)
    if CHART_T[0] <= t < CHART_T[1]:
        a = min(1.0, (t - CHART_T[0]) / 0.2, (CHART_T[1] - t) / 0.2)
        s = 0.94 + 0.06 * ease_out((t - CHART_T[0]) / 0.25)
        paste_scaled(c, chart(t), W / 2, 255, s, a)
    if SIX_T[0] <= t < SIX_T[1]:
        a = min(1.0, (SIX_T[1] - t) / 0.2)
        s = 1.0 + 0.25 * (1 - ease_out((t - SIX_T[0]) / 0.2))
        paste_scaled(c, st["six"], W / 2, 300, s, a)
    for s0, e0, img in st["subs"]:
        if s0 <= t < e0:
            sc = 0.92 + 0.08 * ease_out((t - s0) / 0.1)
            paste_scaled(c, img, W / 2, SUB_Y, sc)
            break
    return c


if __name__ == "__main__":
    st = build_static()
    if sys.argv[1] == "still":
        t = float(sys.argv[2])
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", sys.argv[3], "-frames:v", "1",
                              "-f", "rawvideo", "-pix_fmt", "rgba", "-"], capture_output=True).stdout
        bg = Image.frombytes("RGBA", (W, H), raw)
        bg.alpha_composite(frame(t, st))
        bg.convert("RGB").save(sys.argv[4])
    else:
        out = sys.stdout.buffer
        for a, b in KEEP:
            for n in range(a, b):
                out.write(frame(n / FPS, st).tobytes())
