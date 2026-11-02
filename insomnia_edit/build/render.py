"""Builds the Insomnia reel from timeline.json + grade.json.
Usage: python3 -I render.py [draft|final]
Never writes into source/. All intermediates go to build/tmp/."""
import json, os, subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

MODE = sys.argv[1] if len(sys.argv) > 1 else "draft"
E = "/home/user/Story/insomnia_edit"; SRC = f"{E}/source"; T = f"{E}/build/tmp"; os.makedirs(T, exist_ok=True)
tl = json.load(open(f"{E}/build/timeline.json")); gr = json.load(open(f"{E}/build/grade.json"))
FPS = tl["fps"]; W, H = 1080, 1920; TOTAL = tl["total"]; SPEED = tl.get("speed", 1.0)
SLATE = 0.0   # no reminder card: full script, user adds their own hook text
FONT = f"{E}/fonts/Montserrat-Bold.ttf"
ASSETS = f"{E}/assets"
INT = ["-c:v", "libx264", "-crf", "12", "-preset", "fast", "-pix_fmt", "yuv420p", "-r", str(FPS)]

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(r.stderr[-3000:]); raise SystemExit(f"failed: {' '.join(cmd[:6])}")
    return r

# ---------- colour ----------
LOOK = ("curves=master='0/0.035 0.25/0.265 0.5/0.51 0.75/0.735 1/0.95',"   # lift shadows, pull highlights, light contrast
        "colorbalance=rm=0.015:bm=-0.02:rh=-0.01:bh=0.0,"                   # slight warmth in mids, no hot highlights
        "eq=saturation=1.03")
# Walking shots: v1 brightened + lifted blacks -> milky and clipped. v2 keeps their exposure, adds gentle
# S-contrast with only a hint of lift, protects highlights, light sharpen. Only white balance is matched.
LOOK_WALK = ("curves=master='0/0.012 0.25/0.235 0.5/0.5 0.75/0.765 1/0.955',"
             "colorbalance=rm=0.012:bm=-0.015,eq=saturation=1.07,unsharp=5:5:0.45:5:5:0")
def grade(key, denoise=False):
    g = gr[key]
    if not key.startswith("clipD"):
        gam = min(1.04, max(0.97, 1 / g["gamma"]))          # tiny exposure nudge only, no big brightening
        return f"colorchannelmixer=rr={g['rr']}:gg={g['gg']}:bb={g['bb']},eq=gamma={gam:.3f},{LOOK_WALK}"
    f = f"colorchannelmixer=rr={g['rr']}:gg={g['gg']}:bb={g['bb']},eq=gamma={1/g['gamma']:.3f},{LOOK}"
    if denoise: f = "hqdn3d=1.5:1.5:4:4," + f
    return f

# ---------- A-roll (seated, trimmed) ----------
def build_aroll():
    keep = tl["keep"]; n = len(keep); fc = []
    for i, (a, b) in enumerate(keep):
        fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}]")
        fade = f"afade=t=in:d=0.008,afade=t=out:st={b-a-0.008:.3f}:d=0.008"
        fc.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,{fade}[a{i}]")
    fc.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[cv0][ca0]")
    fc.append(f"[cv0]setpts=PTS/{SPEED}[cv]"); fc.append(f"[ca0]atempo={SPEED}[ca]")
    g = grade("clipD_c3@20.0", denoise=True)
    fr = tl["freeze"]
    fc.append(f"[cv]fps={FPS},{g},tpad=stop_mode=clone:stop_duration={fr},split[f0][b0]")
    fc.append(f"[f0]crop=608:1080:416:0,scale={W}:{H}:flags=lanczos,setsar=1[full]")
    fc.append(f"[b0]crop=1080:960:217:60,setsar=1[bot]")
    fc.append(f"[ca]apad=whole_dur={TOTAL},atrim=0:{TOTAL}[aout]")
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{SRC}/clipD_c3.mp4", "-filter_complex", ";".join(fc),
         "-map", "[full]", *INT, "-t", str(TOTAL), f"{T}/aroll_full.mp4",
         "-map", "[bot]", *INT, "-t", str(TOTAL), f"{T}/aroll_bot.mp4",
         "-map", "[aout]", "-c:a", "pcm_s16le", "-ar", "48000", f"{T}/voice_raw.wav"])

# ---------- walking shots ----------
def build_walk(i, s):
    d = s["b"] - s["a"]; key = f"{s['clip']}@{s['src']}"
    if key not in gr:  # in-point moved after grade.py ran -> nearest entry for that clip
        key = min((k for k in gr if k.startswith(s["clip"])), key=lambda k: abs(float(k.split("@")[1]) - s["src"]))
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(s["src"]), "-i", f"{SRC}/{s['clip']}.mp4", "-t", f"{d:.4f}",
         "-vf", f"fps={FPS},scale={W}:{H}:flags=lanczos,{grade(key)},setsar=1", "-an", *INT, f"{T}/walk{i}.mp4"])

# ---------- image helpers ----------
def rounded(im, r=24):
    im = im.convert("RGBA"); m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.size[0]-1, im.size[1]-1], r, fill=255)
    a = np.minimum(np.array(im.getchannel("A")), np.array(m)); im.putalpha(Image.fromarray(a)); return im
def with_shadow(card, blur=26, off=12, alpha=95):
    pad = blur * 3; c = Image.new("RGBA", (card.width + pad*2, card.height + pad*2), (0, 0, 0, 0))
    sh = Image.new("RGBA", c.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad+off, pad+card.width, pad+off+card.height], 24, fill=(40, 30, 20, alpha))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur))); c.alpha_composite(card, (pad, pad)); return c, pad
def fit(im, mw, mh):
    s = min(mw / im.width, mh / im.height); return im.resize((round(im.width*s), round(im.height*s)), Image.LANCZOS)
def text_card(lines, size=40, fg=(90, 80, 70), bg=(255, 255, 255, 255), padx=36, pady=22):
    f = ImageFont.truetype(FONT, size); d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    w = max(d.textlength(l, font=f) for l in lines); h = len(lines) * size * 1.3
    im = Image.new("RGBA", (int(w + padx*2), int(h + pady*2)), bg); dd = ImageDraw.Draw(im)
    for k, l in enumerate(lines): dd.text((padx, pady + k*size*1.3), l, font=f, fill=fg)
    return rounded(im, 18)

PANEL_BG = (236, 232, 225, 255)
PANEL_H = 960; ASSET_BOX = (960, 740); ASSET_CY = 430      # asset bottom stays above ~800; subtitles sit at the seam

def asset_card(name):
    """Every asset comes from the real repo/README. Missing user screenshots render as a labelled placeholder."""
    if name == "header":
        p = f"{ASSETS}/repo_header.png"
        if os.path.exists(p):   # user's screenshot: two enlarged crops so name + stars read on a phone
            src = Image.open(p).convert("RGBA"); bgc = src.getpixel((5, 110))
            a = src.crop((0, 0, 330, 72)); b = src.crop((596, 138, 926, 196))
            a = a.resize((a.width*2, a.height*2), Image.LANCZOS); b = b.resize((b.width*2, b.height*2), Image.LANCZOS)
            main = Image.new("RGBA", (max(a.width, b.width) + 60, a.height + b.height + 70), bgc)
            main.alpha_composite(a, (30, 20)); main.alpha_composite(b, ((main.width - b.width)//2, a.height + 45))
            main = rounded(fit(main, *ASSET_BOX))
        else:
            ph = Image.new("RGBA", (900, 300), (255, 255, 255, 255)); d = ImageDraw.Draw(ph)
            d.rectangle([4, 4, 895, 295], outline=(200, 60, 60, 255), width=6)
            f = ImageFont.truetype(FONT, 38); d.text((450, 150), "PLACEHOLDER: repo header\nscreenshot from you", font=f, fill=(200, 60, 60), anchor="mm", align="center")
            main = rounded(ph)
        bp = f"{ASSETS}/readme_badges.png"   # real README badges: License MIT · macOS 26+ · Status experimental
        label = rounded(fit(Image.open(bp).convert("RGBA"), 860, 80), 8) if os.path.exists(bp) else text_card(["macOS 26+ · experimental"], size=40)
        c = Image.new("RGBA", (max(main.width, label.width), main.height + 28 + label.height), (0, 0, 0, 0))
        m2, pad = with_shadow(main); c = Image.new("RGBA", (m2.width, m2.height + label.height), (0, 0, 0, 0))
        c.alpha_composite(m2); l2, lp = with_shadow(label, blur=14, off=6, alpha=60)
        c.alpha_composite(l2, ((c.width - l2.width)//2, pad + main.height + 28 - lp)); return c
    if name == "eye":
        eye = Image.open(f"{ASSETS}/readme_eye-open.png").convert("RGBA")
        card = Image.new("RGBA", (560, 560), (255, 255, 255, 255)); e = fit(eye, 380, 380)
        card.alpha_composite(e, ((560-e.width)//2, (560-e.height)//2))
        return with_shadow(rounded(card))[0]
    if name == "duration":
        im = Image.open(f"{ASSETS}/readme_session-flow.png").convert("RGBA").crop((0, 0, 1576, 510))
        return with_shadow(rounded(fit(im, *ASSET_BOX)))[0]
    if name == "countdown":
        im = Image.open(f"{ASSETS}/readme_session-flow.png").convert("RGBA").crop((1610, 0, 2440, 510))
        return with_shadow(rounded(fit(im, 900, 700)))[0]
    if name == "lid":
        src = Image.open(f"{ASSETS}/readme_lid-actions.png").convert("RGBA")
        col = src.crop((2100, 225, 2925, 1150))          # "Lid opens / Try to restore / Session continues" column
        note = src.crop((80, 1240, 1360, 1345))          # "Active sessions only. Timer keeps running."
        card = Image.new("RGBA", (max(col.width, note.width) + 80, col.height + note.height + 90), (243, 241, 237, 255))
        card.alpha_composite(col, ((card.width - col.width)//2, 40)); card.alpha_composite(note, ((card.width - note.width)//2, col.height + 60))
        return with_shadow(rounded(fit(card, *ASSET_BOX)))[0]
    raise KeyError(name)

def pipe_writer(path, w, h):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                             "-r", str(FPS), "-i", "-", *INT, path], stdin=subprocess.PIPE)

def build_top_panel(sec):
    cards = {n: asset_card(n) for n, _, _ in sec["assets"]}
    n_frames = round((sec["b"] - sec["a"]) * FPS); p = pipe_writer(f"{T}/top.mp4", W, PANEL_H)
    for k in range(n_frames):
        t = sec["a"] + k / FPS; frame = Image.new("RGBA", (W, PANEL_H), PANEL_BG)
        for name, a, b in sec["assets"]:
            if a <= t < b:
                c = cards[name]; age = t - a; pr = min(1.0, age / 0.18); e = 1 - (1 - pr) ** 3   # 0.18s ease-out pop
                s = 0.9 + 0.1 * e; ci = c.resize((max(1, round(c.width*s)), max(1, round(c.height*s))), Image.LANCZOS)
                if pr < 1: ci.putalpha(Image.fromarray((np.array(ci.getchannel("A")) * e).astype(np.uint8)))
                frame.alpha_composite(ci, ((W - ci.width)//2, ASSET_CY - ci.height//2))
        p.stdin.write(frame.convert("RGB").tobytes())
    p.stdin.close(); p.wait()

# ---------- paper effect ----------
WARNING = "Use a stable, well-ventilated surface, not a closed bag."
REST = "Insomnia is experimental. Recovery can fail, and a running timer is not a safety guarantee."
def build_paper(sec):
    S = 2; PW, PH = W*S, H*S
    shot = f"{ASSETS}/readme_warning.png"
    rng = np.random.default_rng(7)
    paper = np.full((PH, PW, 3), (247, 243, 234), np.float32) + rng.normal(0, 3.0, (PH, PW, 1))
    base = Image.fromarray(np.clip(paper, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(base); lines_hl = []
    if os.path.exists(shot):  # real README blockquote from the user's screen recording
        im = Image.open(shot).convert("RGBA"); boxes = json.load(open(shot.replace(".png", ".json")))
        sc = (1800 - 56*S) / im.width; im = im.resize((round(im.width*sc), round(im.height*sc)), Image.LANCZOS)
        card = Image.new("RGBA", (im.width + 56*S, im.height + 56*S), (13, 17, 23, 255)); card.alpha_composite(im, (28*S, 28*S))
        card = rounded(card, 24*S); sh, pad = with_shadow(card, blur=30*S, off=14*S, alpha=90)
        x0 = (PW - card.width)//2; y0 = PH//2 - card.height//2
        base.alpha_composite(sh, (x0 - pad, y0 - pad))
        lines_hl = [(x0 + 28*S + round(b[0]*sc), y0 + 28*S + round(b[1]*sc), x0 + 28*S + round(b[2]*sc), y0 + 28*S + round(b[3]*sc)) for b in boxes]
        ys = [b[1] for b in lines_hl] + [b[3] for b in lines_hl]; focus = (PW//2, (min(ys) + max(ys))//2)
        txt_layer = None; base_np = np.array(base).astype(np.float32)
    else:  # stand-in: the README sentence typeset as text (exact wording from the repo)
        f = ImageFont.truetype(f"{E}/fonts/Montserrat-Bold.ttf", 64*S); f2 = ImageFont.truetype(FONT, 50*S)
        def wrap(txt, font, maxw):
            out, cur = [], ""
            for wd in txt.split():
                nxt = (cur + " " + wd).strip()
                if d.textlength(nxt, font=font) <= maxw: cur = nxt
                else: out.append(cur); cur = wd
            return out + [cur]
        L1 = wrap(WARNING, f, PW - 220*S); L2 = wrap(REST, f2, PW - 220*S)
        lh1, lh2 = 92*S, 72*S; y = PH//2 - (len(L1)*lh1 + 50*S + len(L2)*lh2)//2; x = 110*S
        txt_layer = []
        for l in L1:
            w = d.textlength(l, font=f); lines_hl.append((x - 12*S, y + 4*S, x + w + 12*S, y + lh1 - 6*S)); txt_layer.append((x, y, l, f, (25, 25, 25))); y += lh1
        y += 50*S
        for l in L2: txt_layer.append((x, y, l, f2, (110, 104, 96))); y += lh2
        ys = [b[1] for b in lines_hl] + [b[3] for b in lines_hl]; focus = (PW//2, (min(ys) + max(ys))//2)
    n = round((sec["b"] - sec["a"]) * FPS); p = pipe_writer(f"{T}/paper.mp4", W, H)
    swipe_start, swipe_dur = 0.35, 0.5
    total_len = sum(b[2] - b[0] for b in lines_hl)
    for k in range(n):
        t = k / FPS; fr = base.copy(); hl = Image.new("RGBA", fr.size, (0, 0, 0, 0)); hd = ImageDraw.Draw(hl)
        pr = min(1, max(0, (t - swipe_start) / swipe_dur)); remain = pr * total_len
        for (x0, y0, x1, y1) in lines_hl:
            seg = min(remain, x1 - x0); remain -= seg
            if seg <= 0: continue
            if txt_layer is None:   # light text on dark card -> black text on a yellow bar
                pad_ = 6*S; ya, yb, xa, xb = y0 - pad_, y1 + pad_, x0 - pad_, x0 + int(seg)
                reg = base_np[ya:yb, xa:xb, :3]; L = (0.2126*reg[...,0] + 0.7152*reg[...,1] + 0.0722*reg[...,2]) / 255
                tt = np.clip((L - 0.12) / 0.45, 0, 1)[..., None]
                col = np.array([255, 214, 0], np.float32) * (1 - tt) + np.array([18, 18, 18], np.float32) * tt
                arr = np.array(fr); arr[ya:yb, xa:xb, :3] = col.astype(np.uint8); arr[ya:yb, xa:xb, 3] = 255; fr = Image.fromarray(arr)
            else: hd.rectangle([x0, y0, x0 + seg, y1], fill=(255, 214, 0, 200))
        fr.alpha_composite(hl)
        if txt_layer:
            dd = ImageDraw.Draw(fr)
            for (x, y, l, font, col) in txt_layer: dd.text((x, y), l, font=font, fill=col)
        z = 1 + 0.15 * (0.5 - 0.5 * math.cos(math.pi * min(1, t / (n / FPS))))   # 100% -> 115%, eased
        cw, ch = PW / z, PH / z
        cx = PW/2 + (focus[0] - PW/2) * (z - 1) / 0.15 * 0.6; cy = PH/2 + (focus[1] - PH/2) * (z - 1) / 0.15 * 0.6
        box = (cx - cw/2, cy - ch/2, cx + cw/2, cy + ch/2)
        p.stdin.write(fr.convert("RGB").resize((W, H), Image.LANCZOS, box=box).tobytes())
    p.stdin.close(); p.wait()


# ---------- reminder card (user's adverse-case clip goes here) ----------
def build_slate():
    im = Image.new("RGB", (W, H), (20, 20, 20)); d = ImageDraw.Draw(im)
    d.rectangle([40, 40, W-41, H-41], outline=(255, 214, 0), width=10)
    f1 = ImageFont.truetype(FONT, 78); f2 = ImageFont.truetype(FONT, 42)
    d.text((W//2, H//2 - 120), "ADD YOUR\nADVERSE CASE\nCLIP HERE", font=f1, fill=(255, 214, 0), anchor="mm", align="center", spacing=18)
    d.text((W//2, H//2 + 170), "Replace this 2s card.", font=f2, fill=(235, 235, 235), anchor="mm")
    d.text((W//2, H//2 + 240), "Next line: \"Carried your laptop around...\"", font=f2, fill=(170, 170, 170), anchor="mm")
    p = f"{T}/slate.png"; im.save(p); return p

# ---------- warning line on the user's real screen recording ----------
REC = f"{SRC}/screenrec_repo.mp4"
def build_paper_rec(sec):
    """Plays the recording into the warning line (0.5s), then holds that frame: zoom 100->115%, yellow swipe."""
    S = 2; PW, PH = W*S, H*S; rw, rh = 598, 904; sc = PW / rw
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "0.5", "-t", "0.5", "-i", REC, "-vf", f"fps={FPS}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    frames = [Image.frombytes("RGB", (rw, rh), raw[i:i+rw*rh*3]) for i in range(0, len(raw) - rw*rh*3 + 1, rw*rh*3)]
    hold = Image.open(f"{E}/review/rec_1.0.png").convert("RGB")
    bg = tuple(int(x) for x in np.median(np.asarray(hold)[850:900, :, :].reshape(-1, 3), 0))
    def place(im):
        b = Image.new("RGB", (PW, PH), bg); r = im.resize((PW, round(rh*sc)), Image.LANCZOS); y0 = (PH - r.height)//2
        b.paste(r, (0, y0)); return b, y0
    base, y0 = place(hold); base_np = np.asarray(base).astype(np.float32)
    # bold sentence in recording coords: line 1 (x 60-540, y 528-552), line 2 "bag." (x 60-102, y 560-584)
    lines = [(round(60*sc), y0 + round(528*sc), round(540*sc), y0 + round(552*sc)),
             (round(60*sc), y0 + round(560*sc), round(102*sc), y0 + round(584*sc))]
    focus = (PW//2, (lines[0][1] + lines[1][3])//2)
    n = round((sec["b"] - sec["a"]) * FPS); p = pipe_writer(f"{T}/paper.mp4", W, H)
    play = len(frames); total_len = sum(l[2] - l[0] for l in lines); hold_n = n - play
    for k in range(n):
        if k < play:
            p.stdin.write(place(frames[k])[0].resize((W, H), Image.LANCZOS).tobytes()); continue
        t = (k - play) / FPS; arr = np.asarray(base).copy()
        pr = min(1, max(0, (t - 0.25) / 0.5)); remain = pr * total_len
        for (x0, ya, x1, yb) in lines:
            seg = min(remain, x1 - x0); remain -= seg
            if seg <= 0: continue
            pd = 5*S; r0, r1, c0, c1 = ya - pd, yb + pd, x0 - pd, x0 + int(seg)
            reg = base_np[r0:r1, c0:c1]; L = (0.2126*reg[..., 0] + 0.7152*reg[..., 1] + 0.0722*reg[..., 2]) / 255
            tt = np.clip((L - 0.12) / 0.45, 0, 1)[..., None]
            arr[r0:r1, c0:c1] = (np.array([255, 214, 0]) * (1 - tt) + np.array([18, 18, 18]) * tt).astype(np.uint8)
        z = 1 + 0.15 * (0.5 - 0.5 * math.cos(math.pi * min(1, t / max(1e-6, hold_n / FPS))))
        cw, ch = PW / z, PH / z; cx = PW/2; cy = PH/2 + (focus[1] - PH/2) * (z - 1) / 0.15
        cy = min(max(cy, ch/2), PH - ch/2)
        p.stdin.write(Image.fromarray(arr).resize((W, H), Image.LANCZOS, box=(cx - cw/2, cy - ch/2, cx + cw/2, cy + ch/2)).tobytes())
    p.stdin.close(); p.wait()

# ---------- subtitles / text (ASS) ----------
CHUNKS = [  # (words, highlight)
    ("If you use Claude Code,", 0), ("you've done this.", 0), ("Carried your laptop", 0), ("around", 0),
    ("half open,", 1), ("because the moment", 0), ("you close it,", 0), ("your Mac sleeps", 0), ("and the task stops.", 0),
    ("There's a free repo", 0), ("on GitHub", 0), ("that fixes this.", 0), ("It's called", 0), ("Insomnia.", 1),
    ("It sits in your", 0), ("menu bar", 0), ("as a small eye icon.", 0), ("You set how long", 0), ("your Mac should", 0),
    ("stay awake,", 0), ("close the lid,", 1), ("and your agents", 0), ("keep working.", 0), ("When the timer ends,", 0),
    ("it goes back to normal.", 0), ("It's still experimental,", 0), ("so keep it", 0), ("on a desk,", 0), ("not in your bag.", 1),
    ("Want the link?", 0), ("Comment", 0), ("AWAKE.", 1)]
def ass_time(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60; return f"{h}:{m:02d}:{s:05.2f}"
def build_ass():
    words = tl["words"]; norm = lambda x: x.lower().strip(".,?!'\"").replace("’", "'")
    wi = [i for i, w in enumerate(words) if w["w"] == tl.get("first_word", words[0]["w"])][0]; events = []
    for text, hl in CHUNKS:
        n = len(text.split()); ws = words[wi:wi+n]
        assert [norm(w["w"]) for w in ws] == [norm(x) for x in text.split()], (text, [w["w"] for w in ws])
        events.append([ws[0]["os"], ws[-1]["oe"], text, hl]); wi += n
    for k in range(len(events) - 1):           # hold each chunk until the next one (unless a long pause)
        nxt = events[k+1][0]; events[k][1] = nxt if nxt - events[k][1] < 0.6 else events[k][1] + 0.25
    events[-1][1] = TOTAL
    secs = tl["sections"]; split = next(s for s in secs if s["type"] == "split"); paper = next(s for s in secs if s["type"] == "paper")
    lines = []
    for a, b, text, hl in events:
        if a >= paper["a"] - 0.01 and b <= paper["b"] + 0.3: continue          # hidden under the paper effect
        a = max(a, 0); mid = (a + b) / 2
        style = ("HL" if hl else "Sub") + ("Seam" if split["a"] <= mid < split["b"] else "")
        lines.append(f"Dialogue: 1,{ass_time(a+SLATE)},{ass_time(b+SLATE)},{style},,0,0,0,,{text}")
    lines.append(f"Dialogue: 2,{ass_time(tl['cta_start']+SLATE)},{ass_time(TOTAL+SLATE)},Hook,,0,0,0,,Comment AWAKE {{\\fnDejaVu Sans}}↓")
    seam_mv = H - PANEL_H - 40
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Montserrat,58,&H00000000,&H00000000,&H00FFFFFF,&H00FFFFFF,-1,0,0,0,100,100,0,0,3,14,0,2,40,40,420,1
Style: HL,Montserrat,58,&H00000000,&H00000000,&H0000D6FF,&H0000D6FF,-1,0,0,0,100,100,0,0,3,14,0,2,40,40,420,1
Style: SubSeam,Montserrat,58,&H00000000,&H00000000,&H00FFFFFF,&H00FFFFFF,-1,0,0,0,100,100,0,0,3,14,0,2,40,40,{seam_mv},1
Style: HLSeam,Montserrat,58,&H00000000,&H00000000,&H0000D6FF,&H0000D6FF,-1,0,0,0,100,100,0,0,3,14,0,2,40,40,{seam_mv},1
Style: Hook,Montserrat,66,&H00000000,&H00000000,&H00FFFFFF,&H00FFFFFF,-1,0,0,0,100,100,0,0,3,18,0,8,60,60,250,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    open(f"{T}/subs.ass", "w").write(hdr + "\n".join(lines) + "\n")
    return events

# ---------- audio ----------
def build_audio():
    v = f"{T}/voice_raw.wav"; af = "highpass=f=80,afftdn=nf=-25"
    r = run(["ffmpeg", "-hide_banner", "-y", "-i", v, "-af", f"{af},loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"])
    js = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}")+1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
    run(["ffmpeg", "-v", "error", "-y", "-i", v, "-af", f"{af},{ln},aresample=48000", f"{T}/voice_norm.wav"])
    # separate pass: adelay chained after loudnorm silently does nothing in this ffmpeg build (verified)
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{T}/voice_norm.wav", "-af",
         f"adelay={max(1, int(SLATE*1000))}:all=1,apad=whole_dur={TOTAL+SLATE},atrim=0:{TOTAL+SLATE}", f"{T}/voice.wav"])
    d = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{T}/voice.wav"]).stdout)
    assert abs(d - (TOTAL + SLATE)) < 0.05, f"voice length {d} != {TOTAL+SLATE}"
    # music / SFX get mixed here once the files are supplied (Step 6)
    return f"{T}/voice.wav"

# ---------- compose ----------
def compose(audio, out):
    secs = tl["sections"]; inputs = []; fc = []; labels = []; cnt = [0]
    def inp(path, pre=()): inputs.extend([*pre, "-i", path]); cnt[0] += 1; return cnt[0] - 1
    if SLATE > 0:
        i_sl = inp(build_slate(), ("-loop", "1", "-framerate", str(FPS), "-t", str(SLATE)))
        fc.append(f"[{i_sl}:v]format=yuv420p,setsar=1[slate]"); labels.append("[slate]")
    i_full = inp(f"{T}/aroll_full.mp4"); i_bot = inp(f"{T}/aroll_bot.mp4")
    wi = 0
    for k, s in enumerate(secs):
        a, b = s["a"], s["b"]; lab = f"s{k}"
        if s["type"] == "walk": fc.append(f"[{inp(f'{T}/walk{wi}.mp4')}:v]setpts=PTS-STARTPTS[{lab}]"); wi += 1
        elif s["type"] == "black": fc.append(f"color=c=black:s={W}x{H}:r={FPS}:d={b-a:.4f},format=yuv420p[{lab}]")
        elif s["type"] == "full": fc.append(f"[{i_full}:v]trim={a}:{b},setpts=PTS-STARTPTS[{lab}]")
        elif s["type"] == "split":
            fc.append(f"[{i_bot}:v]trim={a}:{b},setpts=PTS-STARTPTS[bt{k}]")
            fc.append(f"[{inp(f'{T}/top.mp4')}:v]setpts=PTS-STARTPTS[tp{k}]")
            fc.append(f"[tp{k}][bt{k}]vstack,setsar=1[{lab}]")
        elif s["type"] == "paper": fc.append(f"[{inp(f'{T}/paper.mp4')}:v]setpts=PTS-STARTPTS[{lab}]")
        labels.append(f"[{lab}]")
    ia = inp(audio)
    fc.append("".join(labels) + f"concat=n={len(labels)}:v=1:a=0,fps={FPS},format=yuv420p,"
              f"ass={T}/subs.ass:fontsdir={E}/fonts[v]")
    enc = ["-c:v", "libx264", "-crf", "18", "-preset", "slow" if MODE == "final" else "medium", "-pix_fmt", "yuv420p",
           "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"]
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", f"{ia}:a",
         *enc, "-t", str(TOTAL + SLATE), out])

if __name__ == "__main__":
    print("A-roll..."); build_aroll()
    for i, s in enumerate([s for s in tl["sections"] if s["type"] == "walk"]): build_walk(i, s)
    print("panels..."); build_top_panel(next(s for s in tl["sections"] if s["type"] == "split"))
    build_paper_rec(next(s for s in tl["sections"] if s["type"] == "paper"))
    build_ass(); print("audio..."); a = build_audio()
    out = f"{E}/insomnia_{'draft' if MODE == 'draft' else 'final'}.mp4"
    print("compose..."); compose(a, out); print("wrote", out)
