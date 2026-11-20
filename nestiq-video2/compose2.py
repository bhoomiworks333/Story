# NestIQ Video #2 ("Nesting") compositor.
# usage: python3 compose2.py stills 1.0 9.5 ...  |  python3 compose2.py render out.mp4 mix.wav
import sys, json, math, subprocess, numpy as np
sys.path.insert(0, "../nestiq-video1")
import graphics as G
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FPS = 30
LINES = json.load(open("lines.json"))
WORDS = json.load(open("transcripts/cut_words.json"))
ORDER = ["L1", "L2", "L3", "L4", "L5"]
START = {}; t = 0.0
for l in ORDER:
    START[l] = t; t += round(LINES[l]["dur"] * FPS) / FPS
DUR = t
def T(l, x): return START[l] + x
def line_at(t):
    for l in ORDER:
        if START[l] <= t < START[l] + LINES[l]["dur"]: return l
    return ORDER[-1]

# ---------------- part layouts (sheet units) ----------------
SIZE = {n: (max(p[0] for p in G.PARTS[n][0]), max(p[1] for p in G.PARTS[n][0])) for n in G.PARTS}
TRAY_ORDER = ["frame", "rA", "rB", "L1", "L2", "sq1", "sq2", "sq3"]
TS = 0.62                                       # parts wait beside the sheet at 62 % size, two rows
def tray_layout():
    out = {}; gap = 0.8
    for row, cy in ((["frame", "rA", "rB"], -11.4), (["L1", "L2", "sq1", "sq2", "sq3"], -4.9)):
        widths = [SIZE[n][0] * TS for n in row]
        x = (G.SW - (sum(widths) + gap * (len(row) - 1))) / 2
        for n, w in zip(row, widths):
            out[n] = (x + w / 2 - SIZE[n][0] / 2, cy - SIZE[n][1] / 2); x += w + gap
    return out
TRAY = tray_layout()
ROWS = {"frame": (0.5, 0.5), "rA": (11.6, 0.7), "sq1": (18.6, 1.0), "sq2": (18.6, 3.6), "rB": (21.6, 0.6),
        "L1": (0.5, 6.75), "L2": (9.9, 6.75), "sq3": (20.1, 11.0)}
ROWS_ROT = {"frame": -1.5, "rA": 2, "sq1": 4, "sq2": -3, "rB": -1.5, "L1": 1, "L2": 181.5, "sq3": 5}
PACK = G.PACKED
DROP_ORDER = ["frame", "rA", "sq1", "sq2", "rB", "L1", "L2", "sq3"]

def ease_out(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def ease_io(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def lerp(a, b, p): return a + (b - a) * p
def clamp(x, a=0, b=1): return max(a, min(b, x))

def setup(full):
    if full: G.W, G.H, G.SX, G.SY = 1080, 1920, 85, 700
    else:    G.W, G.H, G.SX, G.SY = 1080, 960, 85, 300

_MASK = {}
def gap_mask():
    key = (G.SX, G.SY, G.H)
    if key not in _MASK:
        mask = Image.new("L", (G.W * G.SS, G.H * G.SS), 0); md = ImageDraw.Draw(mask)
        x0, y0 = G.u2p(0, 0); x1, y1 = G.u2p(G.SW, G.SH)
        md.rounded_rectangle([x0, y0, x1, y1], radius=6 * G.SS, fill=255)
        for n in G.PARTS:
            for pts in G.poly_px(n, ROWS[n], ROWS_ROT[n]): md.polygon(pts, fill=0)
        # the frame's hole is scrap too
        (fx, fy), r = ROWS["frame"], math.radians(ROWS_ROT["frame"]); ca, sa = math.cos(r), math.sin(r)
        md.polygon([G.u2p(fx + 5 + (x - 5) * ca - (y - 3) * sa, fy + 3 + (x - 5) * sa + (y - 3) * ca)
                    for x, y in [(G.hx, G.hy), (G.hx + G.hw, G.hy), (G.hx + G.hw, G.hy + G.hh), (G.hx, G.hy + G.hh)]],
                   fill=255)
        bbox = (int(x0), int(y0), int(x1), int(y1))
        _MASK[key] = (mask, bbox, mask.crop(bbox))
    return _MASK[key]

def gap_glow(im, amount, t, hole=0.0):
    mask, _, _ = gap_mask()
    if amount > 0:
        pulse = 0.85 + 0.15 * math.sin(t * 4.0)
        red = Image.new("RGB", im.size, G.RED)
        im.paste(red, (0, 0), mask.filter(ImageFilter.GaussianBlur(10 * G.SS)).point(lambda v: int(v * 0.45 * amount)))
        im.paste(red, (0, 0), mask.point(lambda v: int(v * 0.55 * amount * pulse)))
    if hole > 0:   # the scrap has left: the gaps are now empty holes in the sheet
        im.paste(Image.new("RGB", im.size, G.BG), (0, 0), mask.point(lambda v: int(v * hole)))
        x0, y0 = G.u2p(0, 0); x1, y1 = G.u2p(G.SW, G.SH)
        c = tuple(int(lerp(G.BG[i], 110, hole)) for i in range(3))
        ImageDraw.Draw(im).rounded_rectangle([x0, y0, x1, y1], radius=6 * G.SS, outline=c, width=3 * G.SS)

BIN = (540, 1325)            # scrap bin, below the sheet (full layout, px)
def draw_bin(im, alpha, lid, wobble):
    if alpha <= 0: return
    S = G.SS; cx, cy = BIN[0] * S, BIN[1] * S
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    a = int(255 * alpha); body = (82, 82, 86, a); line = (150, 150, 156, a)
    w2, h, top = 78 * S, 150 * S, cy - 60 * S
    ox = wobble * 6 * S
    ld.polygon([(cx - w2 + ox, top), (cx + w2 + ox, top), (cx + w2 * 0.8 + ox, top + h), (cx - w2 * 0.8 + ox, top + h)],
               fill=body, outline=line)
    for k in (-1, 0, 1):
        ld.line([(cx + k * 34 * S + ox, top + 24 * S), (cx + k * 28 * S + ox, top + h - 22 * S)], fill=line, width=6 * S)
    ly = top - 14 * S - lid * 34 * S; lx = cx + ox - lid * 26 * S
    ld.rounded_rectangle([lx - w2 - 10 * S, ly, lx + w2 + 10 * S, ly + 16 * S], radius=6 * S, fill=line)
    ld.rounded_rectangle([lx - 26 * S, ly - 14 * S, lx + 26 * S, ly + 2 * S], radius=6 * S, fill=line)
    im.paste(layer, (0, 0), layer)

def flying_scrap(im, p):
    """red gap pieces leave the sheet and fall into the bin, p = 0..1"""
    if p <= 0 or p >= 1: return
    _, (x0, y0, x1, y1), crop = gap_mask()
    e = p * p                                             # accelerate like a fall
    sc = lerp(1.0, 0.10, e)
    w, h = max(2, int(crop.width * sc)), max(2, int(crop.height * sc))
    m = crop.resize((w, h), Image.BILINEAR).rotate(-25 * e, expand=True, resample=Image.BILINEAR)
    m = m.point(lambda v: int(v * (1 - 0.3 * e)))
    sx, sy = (x0 + x1) / 2, (y0 + y1) / 2
    tx, ty = BIN[0] * G.SS, (BIN[1] - 70) * G.SS
    cx = lerp(sx, tx, ease_io(p)); cy = lerp(sy, ty, e) - math.sin(math.pi * p) * 60 * G.SS
    im.paste(Image.new("RGB", m.size, G.RED), (int(cx - m.width / 2), int(cy - m.height / 2)), m)

def green_strip(im, g, text=None, text_alpha=1.0, size=48):
    if g <= 0: return
    x0, y0 = G.u2p(G.PACKED_RIGHT, 0); x1, y1 = G.u2p(G.SW, G.SH)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle([x0 + 6 * G.SS, y0 + 6 * G.SS, x1 - 6 * G.SS, y1 - 6 * G.SS], radius=8 * G.SS,
                         fill=G.GREEN + (int(110 * g),), outline=G.GREEN + (int(255 * g),), width=4 * G.SS)
    im.paste(layer, (0, 0), layer)
    if text and text_alpha > 0:
        f = ImageFont.truetype(G.FONT, size * G.SS); d = ImageDraw.Draw(im)
        l, tt, r, b = d.textbbox((0, 0), text, font=f)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        col = tuple(int(lerp(G.GREEN[i] * 0.5, 255, text_alpha * g)) for i in range(3))
        d.text((cx - (r - l) / 2 - l, cy - (b - tt) / 2 - tt), text, font=f, fill=col)

# ---------------- cue times (absolute) ----------------
def W(l, i): return T(l, WORDS[l][i]["s"])
def Wfind(l, word, k=0):
    hits = [w for w in WORDS[l] if w["w"].lower().strip(".,").startswith(word)]
    return T(l, hits[k]["s"])
CUE = dict(
    sheet_in=START["L2"],
    tray=[START["L2"] + 0.7 + 0.45 * i for i in range(8)],
    nesting_label=Wfind("L2", "nesting"),
    drops=[START["L3"] + 0.12 + 0.28 * i for i in range(8)],
    glow=Wfind("L3", "gaps", 0),
    gaps_label=Wfind("L3", "scrap"),
    bin_in=Wfind("L3", "those"), scrap_go=Wfind("L3", "become") + 0.05,
    slide=Wfind("L4", "smartly"), rotate=Wfind("L4", "rotating"),
    squares=[Wfind("L4", "even") + 0.05, Wfind("L4", "even") + 0.70, Wfind("L4", "even") + 1.35],
    strip=Wfind("L4", "less"),
    nestiq=START["L5"] + Wfind("L5", "nestiq") - START["L5"] - 0.6,
)

def dp_on(n, t):   # part sits at its loose-row spot (bad nesting), not yet sliding
    return CUE["drops"][DROP_ORDER.index(n)] + 0.32 <= t < CUE["slide"]

def scene(t, full=True):
    """The one evolving sheet, drawn for absolute time t."""
    setup(full)
    im, d = G.canvas()
    a = ease_out((t - CUE["sheet_in"]) / 0.35); G.draw_sheet(d, a, 0.96 + 0.04 * a)
    # red gaps during bad nesting (drawn under the parts), gone once parts start sliding
    back = 1 - ease_io((t - CUE["slide"]) / 0.4)          # a fresh sheet for good nesting
    left = clamp((t - CUE["scrap_go"]) / 0.12)            # scrap has lifted off the sheet
    glow = ease_io((t - CUE["glow"]) / 0.4) * back * (1 - left)
    hole = left * back if full else 0
    if (glow > 0 or hole > 0) and full: gap_glow(im, glow, t, hole); d = ImageDraw.Draw(im)
    big = ["frame", "rA", "rB", "L1", "L2"]
    for i, n in enumerate(DROP_ORDER):
        # stage 1: wait in the tray
        tp = clamp((t - CUE["tray"][TRAY_ORDER.index(n)]) / 0.25)
        if tp <= 0: continue
        bob = 0.18 * math.sin(2 * math.pi * (t * 0.7 + TRAY_ORDER.index(n) * 0.13)) * clamp((t - CUE["tray"][-1]) / 0.6)
        pos = (TRAY[n][0], TRAY[n][1] + bob)
        rot, sc, al = (180 if n == "L2" else 0), TS * (0.7 + 0.3 * ease_out(tp)), ease_out(tp)
        # stage 2: drop onto the sheet in rows (bad nesting)
        dp = (t - CUE["drops"][i]) / 0.32
        if dp > 0:
            e = ease_io(dp)
            pos = (lerp(pos[0], ROWS[n][0], e), lerp(pos[1], ROWS[n][1], e))
            rot = lerp(180 if n == "L2" else 0, ROWS_ROT[n], e)
            sc = lerp(TS, 1.0, e)
            if dp >= 1: q = clamp((t - CUE["drops"][i] - 0.32) / 0.16); sc = 1 + 0.025 * math.sin(q * math.pi)
        # stage 3: slide in tight (good nesting)
        if n in big:
            sp = ease_out((t - CUE["slide"] - big.index(n) * 0.22) / 0.6)
            if sp > 0:
                pos = (lerp(ROWS[n][0], PACK[n][0], sp), lerp(ROWS[n][1], PACK[n][1], sp))
                rot = ROWS_ROT[n] * (1 - sp)
                if n == "L2":   # turned into place on "rotating"
                    rp = ease_io((t - CUE["rotate"]) / 0.6)
                    rot = lerp(ROWS_ROT[n], 0, rp)
                    pos = (lerp(ROWS[n][0], PACK[n][0], min(sp, max(rp, 0.35))),
                           lerp(ROWS[n][1], PACK[n][1], min(sp, max(rp, 0.35))))
        else:
            k = ["sq1", "sq2", "sq3"].index(n); ts = CUE["squares"][k]
            lift = ease_io((t - (ts - 0.5)) / 0.45)        # rise above the hole
            if lift > 0:
                hover = (PACK[n][0], PACK[n][1] - 3.2)
                pos = (lerp(ROWS[n][0], hover[0], lift), lerp(ROWS[n][1], hover[1], lift))
                rot = ROWS_ROT[n] * (1 - lift); sc = 1 + 0.25 * lift
                p = (t - ts) / 0.75                          # slow-motion drop
                if p > 0:
                    e = ease_io(p); pos = (hover[0], lerp(hover[1], PACK[n][1], e)); sc = 1.25 - 0.25 * e
                    if p >= 1: q = clamp((t - ts - 0.75) / 0.2); sc = 1 - 0.04 * math.sin(q * math.pi)
        on_sheet = t >= CUE["drops"][i] + 0.16
        gone = full and CUE["scrap_go"] + 0.12 <= t < CUE["slide"] + 0.2
        hole_c = G.BG if (gone or not on_sheet) else (
            tuple(int(lerp(G.SHEET[c], G.RED[c], 0.55 * glow)) for c in range(3)) if (glow > 0 and n == "frame" and
            dp_on(n, t)) else None)
        G.draw_part(d, n, pos, rot, sc, alpha=al, hole=hole_c)
    g = ease_io((t - CUE["strip"]) / 0.5)
    na = ease_io((t - CUE["nestiq"]) / 0.6)
    green_strip(im, g, "Saved", 1 - na, 52)
    if na > 0:
        f = ImageFont.truetype(G.FONT, 46 * G.SS); dd = ImageDraw.Draw(im)
        x0, y0 = G.u2p(G.PACKED_RIGHT, 0); x1, y1 = G.u2p(G.SW, G.SH)
        l, tt, r, b = dd.textbbox((0, 0), "NestIQ", font=f)
        dd.text(((x0 + x1) / 2 - (r - l) / 2 - l, (y0 + y1) / 2 - (b - tt) / 2 - tt), "NestIQ", font=f,
                fill=tuple(int(lerp(G.GREEN[i] * 0.5, 255, na)) for i in range(3)))
    # labels above the sheet
    lab_y = (G.SY + G.SH * G.U + 100) if full else (G.SY - 70)
    la = ease_out((t - CUE["nesting_label"]) / 0.25) * (1 - ease_io((t - CUE["drops"][0]) / 0.25))
    if la > 0: G.label(im, "Nesting", G.W / 2, lab_y, size=60, alpha=la)
    if full:
        fly = (t - CUE["scrap_go"]) / 0.8
        land = clamp((t - CUE["scrap_go"] - 0.8) / 0.35)
        lid = clamp((t - CUE["scrap_go"] - 0.35) / 0.2) * (1 - land)
        wob = math.sin(land * math.pi * 3) * (1 - land) if 0 < land < 1 else 0
        ba = ease_out((t - CUE["bin_in"]) / 0.3) * (1 - ease_io((t - CUE["slide"]) / 0.3))
        draw_bin(im, ba, lid, wob)
        flying_scrap(im, fly)
    ga = ease_out((t - CUE["gaps_label"]) / 0.25) * (1 - ease_io((t - CUE["slide"]) / 0.25))
    if ga > 0: G.label(im, "Gaps = scrap", G.W / 2, (G.SY - 90) if full else lab_y, size=60, alpha=ga)
    return G.finish(im)

# ---------------- captions ----------------
CAPS_DEF = [   # (line, text, first word index in cut transcript, keyword)
 ("L1", "There's one term", 0, None), ("L1", "every cutting factory", 4, None),
 ("L1", "or industry should know,", 7, None), ("L1", "and that is nesting.", 11, "nesting"),
 ("L2", "Before a sheet is cut,", 0, None), ("L2", "someone decides", 5, None),
 ("L2", "where each part goes on it.", 7, None), ("L2", "That arrangement", 12, None),
 ("L2", "is called nesting.", 14, "nesting"),
 ("L3", "Place them carelessly,", 0, None), ("L3", "and you get gaps.", 3, "gaps"),
 ("L3", "Those gaps", 7, None), ("L3", "become scrap.", 9, "scrap"),
 ("L4", "Place them smartly,", 0, None), ("L4", "rotating them,", 3, None),
 ("L4", "fitted together,", 5, None), ("L4", "even inside each other,", 7, None),
 ("L4", "and the same parts", 11, None), ("L4", "need less sheet.", 15, "less sheet"),
 ("L5", "And that's what", 0, None), ("L5", "we are fixing", 3, None), ("L5", "with NestIQ.", 6, "NestIQ"),
]
KW_WORD = {"nesting": "nesting", "gaps": "gaps", "scrap": "scrap", "less sheet": "less", "NestIQ": "nestiq"}
CAPS = []
for i, (l, txt, wi, kw) in enumerate(CAPS_DEF):
    a = T(l, WORDS[l][wi]["s"]) - 0.03
    if i + 1 < len(CAPS_DEF):
        nl, _, nwi, _ = CAPS_DEF[i + 1]; b = T(nl, WORDS[nl][nwi]["s"]) - 0.03
    else: b = DUR
    if i + 1 < len(CAPS_DEF) and CAPS_DEF[i + 1][0] != l: b = min(b, START[l] + LINES[l]["dur"])
    kwt = 0
    if kw:
        idx = [k for k, w in enumerate(WORDS[l]) if k >= wi and w["w"].lower().strip(".,").startswith(KW_WORD[kw])][0]
        kwt = T(l, WORDS[l][idx]["s"]) - 0.03
    CAPS.append(dict(a=a, b=b, txt=txt, kw=kw, kwt=kwt))

FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
F_CAP = ImageFont.truetype(FB, 54); F_V = ImageFont.truetype(FB, 72)
def caption(im, t, cy):
    cap = next((c for c in CAPS if c["a"] <= t < c["b"]), None)
    if not cap: return
    d = ImageDraw.Draw(im); txt = cap["txt"]; padx, pady = 30, 16
    l, tp, r, b = d.textbbox((0, 0), txt, font=F_CAP)
    w = r - l + 2 * padx; h = 54 + 2 * pady; x = 540 - w / 2; y = cy - h / 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=16, fill=(255, 255, 255))
    if cap["kw"] and t >= cap["kwt"]:
        i = txt.index(cap["kw"])
        kx0 = d.textlength(txt[:i], font=F_CAP); kx1 = kx0 + d.textlength(cap["kw"], font=F_CAP)
        d.rounded_rectangle([x + padx + kx0 - 9, y + 7, x + padx + kx1 + 7, y + h - 7], radius=12, fill=G.ORANGE)
    asc = F_CAP.getmetrics()[0]
    d.text((x + padx - l, y + pady + (54 - asc) / 2 + 2), txt, font=F_CAP, fill=(0, 0, 0))

def boxed(im, txt, cx, cy):
    d = ImageDraw.Draw(im); l, tp, r, b = d.textbbox((0, 0), txt, font=F_V)
    w, h = r - l + 68, b - tp + 40; x, y = cx - w / 2, cy - h / 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=18, fill=(255, 255, 255))
    d.text((x + 34 - l, y + 20 - tp), txt, font=F_V, fill=(0, 0, 0))

EYE = 850
def frame_at(t, face):
    l = line_at(t)
    if l == "L1":
        im = Image.fromarray(face); caption(im, t, 1470)
    elif l == "L5":
        im = Image.new("RGB", (1080, 1920), G.BG); im.paste(scene(t, full=False), (0, 0))
        top = EYE - 400; im.paste(Image.fromarray(face[top:top + 960]), (0, 960)); caption(im, t, 958)
    else:
        im = scene(t, full=True); caption(im, t, 1470)
    return im

def face_frames():
    for l in ORDER:
        n = round(LINES[l]["dur"] * FPS)
        if LINES[l]["kind"] != "face":
            for _ in range(n): yield None
            continue
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", f"segs/{l}_full.mp4", "-f", "rawvideo", "-pix_fmt",
                              "rgb24", "-"], stdout=subprocess.PIPE); last = None
        for _ in range(n):
            buf = p.stdout.read(1080 * 1920 * 3)
            if len(buf) == 1080 * 1920 * 3: last = np.frombuffer(buf, np.uint8).reshape(1920, 1080, 3)
            yield last
        p.stdout.close(); p.wait()

if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for t in map(float, sys.argv[2:]):
            l = line_at(t); fr = None
            if LINES[l]["kind"] == "face":
                raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t - START[l]:.3f}", "-i", f"segs/{l}_full.mp4",
                    "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
                fr = np.frombuffer(raw, np.uint8).reshape(1920, 1080, 3)
            frame_at(t, fr).save(f"qa/still_{t:05.2f}.png")
        print("duration %.2f" % DUR, {k: round(v, 2) if not isinstance(v, list) else [round(x, 2) for x in v] for k, v in CUE.items()})
    else:
        out, audio = sys.argv[2], sys.argv[3]
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920",
              "-r", str(FPS), "-i", "-", "-i", audio, "-c:v", "libx264", "-crf", "18", "-preset", "slow",
              "-pix_fmt", "yuv420p", "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709",
              "-color_trc", "bt709", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
              stdin=subprocess.PIPE)
        for k, fr in enumerate(face_frames()):
            ff.stdin.write(frame_at(k / FPS, fr).tobytes())
        ff.stdin.close(); ff.wait(); print("done", out, "%.2f s" % DUR)
