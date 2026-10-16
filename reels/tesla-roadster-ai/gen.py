#!/usr/bin/env python3
"""Tesla Roadster / physical AI reel: cuts, 1.1x speed, footage clips, HyperFrames composition and SRT.

    python3 gen.py <take.mp4> <hop.mp4> <launch.mp4> <reveal.mp4>      # clips, audio, hf/index.html, srt
    cd hf && HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell \
        npx hyperframes@0.8.164 render -o ../build/silent.mp4 --fps 30
    python3 gen.py <take.mp4> <hop.mp4> <launch.mp4> <reveal.mp4> --mux  # -> output/tesla_roadster_ai_reel.mp4

House look (same as the garba / Argon reels): talking head full frame with no zoom, white-box captions
of 2-4 words as spoken with hard cuts, cards at the top above the eyes. This reel adds the agreed
1.1x speed (pitch kept) and full-screen Tesla cutaways. Footage is reframed so the re-uploader's
watermark and the YouTube player stay outside the frame.

All take times below are seconds in the original take (words timed with Vosk, see vosk.json).
"""
import difflib, html, json, os, re, subprocess, sys, wave
import numpy as np

TAKE, HOP, LAUNCH, REVEAL = sys.argv[1:5]
MUX = '--mux' in sys.argv
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
BUILD = os.path.join(HERE, 'build')
ASSETS = os.path.join(HERE, 'hf', 'assets')
os.makedirs(BUILD, exist_ok=True)
FPS = 30
SPEED = 1.1

# Kept ranges of the take. Script cuts: "breaking the laws of physics", "ground missile",
# "AI runs millions of ... simulations", "in the near future ... real time", "let me know in the comments".
# Pauses over ~0.45 s inside a kept line are cut too (jump cuts).
KEEP = [
    (2.05, 11.98),   # Tesla just revealed ... Did AI build this?
    (14.72, 20.80),  # We are talking active underbody suction fans ... 230 mph
    (23.15, 25.95),  # So, is this AI's doing? Yes and no.
    (26.75, 42.80),  # AI didn't physically build ... draw by hand
    (47.92, 56.50),  # This is where we are heading ... merges directly with
    (57.05, 58.15),  # heavy manufacturing
    (65.20, 69.80),  # The physical world ... Are you ready for it?
]
KEEP = [(round(a * FPS) / FPS, round(b * FPS) / FPS) for a, b in KEEP]
HOLD = 0.6  # last frame held after "ready for it?"


def out_t(t):
    """Map a take time to the output timeline (after cuts and the 1.1x speed-up)."""
    acc = 0.0
    for a, b in KEEP:
        if t < a:
            return acc / SPEED
        if t <= b:
            return (acc + t - a) / SPEED
        acc += b - a
    return acc / SPEED


def q(t):
    return round(t * FPS) / FPS


SPEECH = q(out_t(KEEP[-1][1]))
DUR = q(SPEECH + HOLD)

# Captions exactly as spoken, 2-4 words each. "|" separates captions, lines follow the kept ranges.
SCRIPT = """Tesla just revealed|a car that hits|0 to 60|under 1 second|and literally hops|off the ground|using SpaceX thrusters.|But here's|the real question.|Did AI build this?
|We are talking|active underbody|suction fans,|cold gas|rocket thrusters,|and top speed|over 230 mph.
|So, is this|AI's doing?|Yes and no.|AI didn't physically|build the thrusters.|That's hardcore metallurgy,|fluid dynamics|and rocket science.|But AI is|the ultimate cheat code|that makes it possible.|Engineers use AI|for generative design,|letting algorithms create|lightweight, organic|structural parts|that a human|could never|draw by hand.
|This is where|we are heading.|We're moving past AI|that just writes code|or generates images.|We are entering|the era of|physical AI,|where machine learning|merges directly|with heavy manufacturing.
|The physical world|is about to get|updated like software.|Are you ready|for it?"""
CHUNKS = [c.strip() for c in SCRIPT.replace('\n', '').split('|')]
assert all(2 <= len(c.split()) <= 4 for c in CHUNKS), [c for c in CHUNKS if not 2 <= len(c.split()) <= 4]


def align():
    """Time each caption word from Vosk's words (difflib on normalised tokens, gaps interpolated)."""
    V = [w for w in json.load(open(os.path.join(HERE, 'vosk.json'))) if any(a <= w['start'] < b for a, b in KEEP)]
    toks = [(ci, w) for ci, c in enumerate(CHUNKS) for w in c.split()]
    norm = lambda s: re.sub(r"[^a-z0-9']", "", s.lower())
    A, B = [norm(w) for _, w in toks], [norm(v['word']) for v in V]
    st, en = [None] * len(A), [None] * len(A)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
        if tag == 'equal' or (tag == 'replace' and i2 - i1 == j2 - j1):
            for k in range(i2 - i1):
                st[i1 + k], en[i1 + k] = V[j1 + k]['start'], V[j1 + k]['end']
        elif tag == 'replace':
            s0, e0, n = V[j1]['start'], V[j2 - 1]['end'], i2 - i1
            for k in range(n):
                st[i1 + k], en[i1 + k] = s0 + (e0 - s0) * k / n, s0 + (e0 - s0) * (k + 1) / n
    for i in range(len(A)):
        if st[i] is None:
            p = max([j for j in range(i) if en[j] is not None], default=None)
            nx = min([j for j in range(i, len(A)) if st[j] is not None], default=None)
            a = en[p] if p is not None else KEEP[0][0]
            b = st[nx] if nx is not None else a + 0.3
            gap = [j for j in range(i, nx if nx is not None else len(A)) if st[j] is None]
            for k, j in enumerate(gap):
                st[j], en[j] = a + (b - a) * k / len(gap), a + (b - a) * (k + 1) / len(gap)
    caps = []
    for ci, c in enumerate(CHUNKS):
        idx = [i for i, (c2, _) in enumerate(toks) if c2 == ci]
        caps.append([q(out_t(st[idx[0]])), q(out_t(en[idx[-1]])), c])
    # show from the first word to the next caption (or last word + 0.25 s); last one holds to the end
    for i, c in enumerate(caps):
        nxt = caps[i + 1][0] if i + 1 < len(caps) else DUR
        c[1] = nxt if i + 1 == len(caps) else min(nxt, q(c[1] + 0.25))
    return caps


def T(t):
    """Output time of a take time, frame-quantised."""
    return q(out_t(t))


def run(cmd):
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------- footage
# Full-screen cutaways: 9:16 crops of the 1918x1078 recordings, centre x as a fraction of the width.
# Cards: 16:9 crops (x0, y0, w, h in source px) scaled to 960x540. Source times play at 1x.
FULL = {  # name: (src, src_start, cx)
    'hop':   (HOP, 1.20, 0.68),     # leaps over the parked Teslas
    'hover': (HOP, 14.30, 0.44),    # hovers on the cold-gas jets
    'burst': (HOP, 4.30, 0.50),     # lands in the smoke burst
}
CARD = {  # name: (src, src_start, x0, y0, w, h)
    'launch': (LAUNCH, 2.85, 0, 140, 1630, 917),     # 0-60 timer ticking past 0.79
    'fans':   (REVEAL, 18.00, 64, 30, 960, 540),     # underbody, upside down on the loop
    'jets':   (REVEAL, 56.20, 160, 150, 640, 360),   # thrusters firing on the ramp
    'speed':  (REVEAL, 49.40, 64, 30, 960, 540),     # flat-out down the lit straight
}

# Timeline (take times): (kind, name, take start, take end)
SHOTS = [
    ('full', 'hop', KEEP[0][0], 4.95),       # "Tesla just revealed a car that hits 0 to 60"
    ('card', 'launch', 4.95, 5.83),          # "under 1 second"
    ('full', 'hover', 5.83, 8.95),           # "and literally hops off the ground using SpaceX thrusters"
    ('card', 'fans', 15.40, 17.05),          # "active underbody suction fans"
    ('card', 'jets', 17.05, 18.40),          # "cold gas rocket thrusters"
    ('card', 'speed', 18.40, 20.80),         # "and top speed over 230 mph"
    ('full', 'burst', 65.20, 68.75),         # "The physical world is about to get updated like software"
]
CARD_LABEL = {'launch': '0–60 in under 1 s*', 'fans': 'Suction fans', 'jets': 'Cold-gas thrusters', 'speed': '230+ mph'}


def cut_footage():
    for kind, name, a, b in SHOTS:
        dur = T(b) - T(a) + 0.2
        if kind == 'full':
            src, ss, cx = FULL[name]
            vf = f"crop=606:1078:{round(cx * 1918 - 303)}:0,scale=1080:1920:flags=lanczos"
        else:
            src, ss, x0, y0, w, h = CARD[name]
            vf = f"crop={w}:{h}:{x0}:{y0},scale=960:540:flags=lanczos"
        run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{ss}', '-i', src, '-t', f'{dur:.3f}', '-an', '-vf', vf + f',fps={FPS}',
             '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-g', '30', '-keyint_min', '30', '-pix_fmt', 'yuv420p',
             os.path.join(ASSETS, f'{kind}_{name}.mp4')])


def denoise(src, dst, sr=48000):
    """Light room-noise reduction, profile from the 1.0-2.0 s of room tone before he speaks."""
    import noisereduce as nr
    def pcm(args):
        raw = subprocess.run(['ffmpeg', '-v', 'error', *args, '-ac', '1', '-ar', str(sr), '-f', 's16le', '-'],
                             capture_output=True, check=True).stdout
        return np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    y = nr.reduce_noise(y=pcm(['-i', src]), sr=sr, y_noise=pcm(['-ss', '1.0', '-t', '1.0', '-i', TAKE]),
                        stationary=True, prop_decrease=0.85, n_std_thresh_stationary=1.5)
    with wave.open(dst, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


def base_and_audio():
    parts, labels = [], []
    for i, (a, b) in enumerate(KEEP):
        parts.append(f"[0:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{SPEED}[v{i}];"
                     f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,"
                     f"afade=t=out:st={b - a - 0.012:.3f}:d=0.012,atempo={SPEED}[a{i}];")
        labels.append(f"[v{i}][a{i}]")
    fc = ("".join(parts) + "".join(labels) + f"concat=n={len(KEEP)}:v=1:a=1[vc][a];"
          f"[vc]fps={FPS},scale=1080:1920:flags=lanczos,tpad=stop_mode=clone:stop_duration={HOLD}[v]")
    run(['ffmpeg', '-v', 'error', '-y', '-i', TAKE, '-filter_complex', fc, '-map', '[v]', '-c:v', 'libx264', '-crf', '16',
         '-preset', 'medium', '-g', '30', '-keyint_min', '30', '-pix_fmt', 'yuv420p', os.path.join(ASSETS, 'base.mp4'),
         '-map', '[a]', '-ar', '48000', os.path.join(BUILD, 'speech.wav')])
    denoise(os.path.join(BUILD, 'speech.wav'), os.path.join(BUILD, 'speech_dn.wav'))
    run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(BUILD, 'speech_dn.wav'), '-af',
         f"apad=pad_dur={HOLD},loudnorm=I=-16:TP=-1.5:LRA=11", '-ar', '48000', os.path.join(BUILD, 'audio.wav')])


# ---------------------------------------------------------------- overlays (take times)
CHIPS = [  # small white pills dropping in at the top, garba-banner style: (id, text, take start, take end, cy)
    ('c-met', '⚙️ Metallurgy', 30.03, 32.40, 110),
    ('c-flu', '🌊 Fluid dynamics', 30.81, 32.40, 200),
    ('c-roc', '🚀 Rocket science', 31.74, 32.40, 290),
    ('c-code', '💻 Writes code', 50.68, 52.74, 110),
    ('c-img', '🖼️ Makes images', 51.84, 52.74, 200),
]
PUNCH = [  # outlined punch text at the top: (id, html, take start, take end)
    ('k-ai', 'Did <b>AI</b> build this? 🤔', 10.62, 14.72),
    ('k-ready', 'Are you <b>ready?</b> 👇', 68.88, 99),
]
ARTICLES = [  # news screenshots as top cards (articles/make_cards.py): (id, png, take start, take end)
    ('art1', 'art_hagerty.png', 32.40, 35.50),   # "But AI is the ultimate cheat code that makes it possible."
    ('art2', 'art_electrek.png', 52.74, 58.15),  # "We are entering the era of physical AI ... heavy manufacturing."
]
GEN = (35.55, 42.80)  # generative design card: "Engineers use AI ... draw by hand"


def gen_design_svg():
    """Animated illustration: a solid bracket gets carved into an organic, bone-like lattice."""
    holes = [(150, 120), (810, 120), (150, 420), (810, 420)]
    load = (480, 270)
    struts = []
    for i, (hx, hy) in enumerate(holes):  # main load paths, curved and thick
        mx, my = (hx + load[0]) / 2, (hy + load[1]) / 2
        bend = 70 if i % 2 else -70
        struts.append((f"M{hx},{hy} Q{mx + bend * 0.4},{my + bend} {load[0]},{load[1]}", 30))
        struts.append((f"M{hx},{hy} Q{mx - bend},{my - bend * 0.3} {load[0]},{load[1]}", 16))
    for (ax, ay), (bx, by) in [(holes[0], holes[1]), (holes[2], holes[3]), (holes[0], holes[2]), (holes[1], holes[3])]:
        mx, my = (ax + bx) / 2, (ay + by) / 2
        dx, dy = (0, 60) if ay == by else (60, 0)
        dx, dy = (dx, dy) if (mx < 480 or my > 270) else (-dx, -dy)
        sx, sy = (1, 1) if (ay == by and ay < 270) or (ax == bx and ax < 480) else (-1, -1)
        struts.append((f"M{ax},{ay} C{mx - 120},{my + sy * 70} {mx + 120},{my + sy * 70} {bx},{by}", 14))
    for k in range(10):  # thin secondary webs
        ang = k / 10 * 2 * np.pi
        r1, r2 = 70, 170 + 30 * np.sin(k * 1.7)
        x1, y1 = load[0] + r1 * np.cos(ang), load[1] + r1 * 0.8 * np.sin(ang)
        x2, y2 = load[0] + r2 * np.cos(ang + 0.5), load[1] + r2 * 0.8 * np.sin(ang + 0.5)
        cx, cy = load[0] + (r1 + r2) / 2 * np.cos(ang + 0.05), load[1] + (r1 + r2) / 2 * 0.8 * np.sin(ang + 0.05)
        struts.append((f"M{x1:.0f},{y1:.0f} Q{cx:.0f},{cy:.0f} {x2:.0f},{y2:.0f}", 7))
    paths = "\n".join(f'<path class="strut" d="{d}" stroke-width="{w}" />' for d, w in struts)
    bosses = "\n".join(f'<circle class="boss" cx="{x}" cy="{y}" r="42" /><circle class="hole" cx="{x}" cy="{y}" r="17" />'
                       for x, y in holes + [load])
    return f"""<svg viewBox="0 0 960 540" width="960" height="540">
  <defs><linearGradient id="metal" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#f3f5f8" /><stop offset="1" stop-color="#9aa4b2" /></linearGradient></defs>
  <rect id="g-block" x="95" y="70" width="770" height="400" rx="30" fill="url(#metal)" opacity="0.9" />
  <g id="g-lattice" fill="none" stroke="url(#metal)" stroke-linecap="round">{paths}</g>
  <g id="g-bosses" fill="url(#metal)">{bosses}</g>
</svg>"""


def page(caps):
    vids, anims = [], []
    for i, (kind, name, a, b) in enumerate(SHOTS):
        s, e = T(a), T(b)
        if kind == 'full':
            vids.append(f'      <video id="{kind}_{name}" class="clip full" src="assets/{kind}_{name}.mp4" muted playsinline '
                        f'data-start="{s:.4f}" data-duration="{e - s:.4f}" data-track-index="2"></video>')
            vids.append(f'      <div class="clip credit" data-start="{s:.4f}" data-duration="{e - s:.4f}" data-track-index="3">'
                        f'Footage: Tesla</div>')
        else:
            note = ('<div class="note">*Thrust &amp; Rocket trims. Base model: under 1.6 s</div>' if name == 'launch' else '')
            vids.append(f'      <video id="v_{name}" class="clip cardv g_{name}" src="assets/{kind}_{name}.mp4" muted playsinline '
                        f'data-start="{s:.4f}" data-duration="{e - s:.4f}" data-track-index="4"></video>')
            vids.append(f'      <div id="o_{name}" class="clip cardo g_{name}" data-start="{s:.4f}" data-duration="{e - s:.4f}" '
                        f'data-track-index="5"><span class="lab">{CARD_LABEL[name]}</span><span class="tag">Footage: Tesla</span>{note}</div>')
            # pop only when the card comes in over the talking head, not when it swaps for the next card
            prev = SHOTS[i - 1] if i else None
            if not (prev and prev[0] == 'card' and abs(T(prev[3]) - s) < 0.01):
                anims.append(f'pop(".g_{name}", {s:.4f}, 1, 0.6, 0.35);')
    pops = []
    for cid, text, a, b, cy in CHIPS:
        s, e = T(a), T(b)
        pops.append(f'      <div class="clip pop" data-start="{s:.4f}" data-duration="{e - s:.4f}" data-track-index="5">'
                    f'<span id="{cid}" class="chip" style="top:{cy}px">{html.escape(text)}</span></div>')
        anims.append(f'pop("#{cid}", {s:.4f}, 1);')
        anims.append(f'out("#{cid}", {e - 0.12:.4f}, 1);')
    anims.append(f'strike(["#c-code", "#c-img"], {T(52.74) - 0.3:.4f});')
    for kid, h, a, b in PUNCH:
        s, e = T(a), (DUR if b >= 99 else min(T(b), DUR))
        pops.append(f'      <div class="clip pop" data-start="{s:.4f}" data-duration="{e - s:.4f}" data-track-index="6">'
                    f'<div id="{kid}" class="punch" data-t="{html.escape(re.sub("<.*?>", "", h))}">{h}</div></div>')
        anims.append(f'pop("#{kid}", {s:.4f}, 1);')
        if e < DUR:
            anims.append(f'out("#{kid}", {e - 0.12:.4f}, 1);')
    for aid, png, a, b in ARTICLES:
        s, e = T(a), T(b)
        pops.append(f'      <div class="clip cardw" data-start="{s:.4f}" data-duration="{e - s:.4f}" data-track-index="4">'
                    f'<img id="card_{aid}" class="card art" src="assets/{png}" alt="" /></div>')
        anims.append(f'pop("#card_{aid}", {s:.4f}, 1, 0.6, 0.35);')
        anims.append(f'out("#card_{aid}", {e - 0.12:.4f}, 1);')
    gs, ge = T(GEN[0]), T(GEN[1])
    pops.append(f'      <div class="clip cardw" data-start="{gs:.4f}" data-duration="{ge - gs:.4f}" data-track-index="4">'
                f'<div id="card_gen" class="card gen">{gen_design_svg()}<span class="lab">Generative design</span>'
                f'<span class="tag">Illustration</span></div></div>')
    anims.append(f'pop("#card_gen", {gs:.4f}, 1, 0.6, 0.35);')
    anims.append(f'genDesign({gs:.4f});')
    capdiv = "\n".join(
        f'      <div class="clip cap" data-start="{a:.4f}" data-duration="{b - a:.4f}" data-track-index="10">'
        f'<span class="box">{html.escape(t)}</span></div>' for a, b, t in caps)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Tesla Roadster AI reel</title>
    <script src="assets/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "InterHF"; src: url("assets/Inter-SemiBold.otf"); font-weight: 600; }}
      @font-face {{ font-family: "InterHF"; src: url("assets/Inter-Black.otf"); font-weight: 900; }}
      @font-face {{ font-family: "Noto Color Emoji"; src: local("Noto Color Emoji"); }}
      html, body {{ margin: 0; background: #000; }}
      body {{ font-family: "InterHF", "Noto Color Emoji", system-ui, sans-serif; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #base {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      .full {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 2; }}
      .credit {{ position: absolute; left: 40px; top: 48px; z-index: 3; color: rgba(255,255,255,.85); font-size: 26px;
                font-weight: 600; text-shadow: 0 2px 6px rgba(0,0,0,.8); }}
      .cardw {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 4; }}
      .card {{ position: absolute; left: 60px; top: 70px; width: 960px; height: 540px; border-radius: 24px; overflow: hidden;
              box-shadow: 0 20px 60px rgba(0,0,0,.6); background: #000; }}
      .cardv {{ position: absolute; left: 60px; top: 70px; width: 960px; height: 540px; border-radius: 24px; z-index: 4;
               box-shadow: 0 20px 60px rgba(0,0,0,.6); object-fit: cover; background: #000; }}
      .cardo {{ position: absolute; left: 60px; top: 70px; width: 960px; height: 540px; z-index: 5; }}
      .card.art {{ height: auto; }}
      #card_art2 {{ width: 860px; left: 110px; }}
      .card.gen {{ background: radial-gradient(ellipse at 50% 45%, #1f2a3a 0%, #0b0f16 75%); }}
      .card .lab, .cardo .lab {{ position: absolute; left: 24px; bottom: 22px; background: #fff; color: #000; font-size: 40px; font-weight: 600;
                   padding: 10px 20px 12px; border-radius: 12px; letter-spacing: -0.01em; }}
      .card .tag, .cardo .tag {{ position: absolute; right: 22px; top: 18px; color: rgba(255,255,255,.8); font-size: 22px; font-weight: 600;
                   text-shadow: 0 2px 6px rgba(0,0,0,.8); }}
      .note {{ position: absolute; left: 0; top: 556px; width: 960px; text-align: center; color: #fff; font-size: 28px;
              font-weight: 600; text-shadow: 0 2px 8px rgba(0,0,0,.9); }}
      .pop {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 6; }}
      .chip {{ position: absolute; left: 540px; background: #fff; color: #000; font-size: 44px; font-weight: 600; white-space: nowrap;
              padding: 12px 26px 14px; border-radius: 40px; box-shadow: 0 10px 28px rgba(0,0,0,.30); }}
      .chip .line {{ position: absolute; left: 18px; right: 18px; top: 50%; height: 6px; background: #e0242b; border-radius: 3px;
                    transform-origin: left center; transform: scaleX(0); }}
      .punch {{ position: absolute; left: 540px; top: 230px; font-size: 84px; font-weight: 900; color: #fff; white-space: nowrap;
               letter-spacing: -0.02em; line-height: 1.05; isolation: isolate; }}
      .punch::before {{ content: attr(data-t); position: absolute; left: 0; top: 0; z-index: -1; color: transparent;
                       -webkit-text-stroke: 16px #000; }}
      .punch b {{ color: #ffd400; font-weight: 900; }}
      .cap {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 10; }}
      .cap .box {{ position: absolute; left: 50%; top: 1500px; transform: translate(-50%, -50%); background: #fff; color: #000;
                  font-size: 50px; font-weight: 600; line-height: 1.15; letter-spacing: -0.01em;
                  padding: 14px 26px 16px; border-radius: 14px; white-space: nowrap; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{DUR}">
      <video id="base" class="clip" src="assets/base.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="0"></video>
{chr(10).join(vids)}
{chr(10).join(pops)}
{capdiv}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      const tf = (s) => ({{ xPercent: -50, yPercent: -50, scale: s }});
      const pop = (sel, t, s, from = 0.5, d = 0.22) => {{
        const centred = !(sel.startsWith("#card") || sel.startsWith(".g_"));
        const a = centred ? {{ ...tf(s * from) }} : {{ scale: s * from }};
        const b = centred ? {{ ...tf(s) }} : {{ scale: s }};
        tl.fromTo(sel, {{ ...a, opacity: 0 }}, {{ ...b, opacity: 1, duration: d, ease: "back.out(1.8)", immediateRender: false }}, t);
      }};
      const out = (sel, t, s) => tl.to(sel, {{ scale: s * 0.85, opacity: 0, duration: 0.12, ease: "power2.in" }}, t);
      document.querySelectorAll(".chip").forEach((c) => c.insertAdjacentHTML("beforeend", '<span class="line"></span>'));
      gsap.set(".chip, .punch", {{ xPercent: -50, yPercent: -50 }});
      const strike = (sels, t) => sels.forEach((s, i) =>
        tl.to(s + " .line", {{ scaleX: 1, duration: 0.18, ease: "power2.out" }}, t + i * 0.08));
      const genDesign = (t) => {{
        const struts = document.querySelectorAll("#g-lattice .strut");
        struts.forEach((p) => {{ const L = p.getTotalLength(); gsap.set(p, {{ strokeDasharray: L, strokeDashoffset: L }}); }});
        tl.fromTo("#g-block", {{ opacity: 0.9 }}, {{ opacity: 0.12, duration: 1.2, ease: "power1.inOut", immediateRender: false }}, t + 0.5);
        tl.to(struts, {{ strokeDashoffset: 0, duration: 1.1, ease: "power2.out", stagger: 0.07 }}, t + 0.6);
        tl.to("#g-block", {{ opacity: 0, duration: 0.6 }}, t + 2.6);
      }};
      {(chr(10) + '      ').join(anims)}
      tl.set({{}}, {{}}, {DUR});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""


def ts(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


if not MUX:
    caps = align()
    base_and_audio()
    cut_footage()
    open(os.path.join(HERE, 'hf', 'index.html'), 'w').write(page(caps))
    with open(os.path.join(ROOT, 'output', 'tesla_roadster_ai_reel.srt'), 'w') as f:
        f.write("".join(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n" for i, (a, b, t) in enumerate(caps, 1)))
    for a, b, t in caps:
        print(f"{a:6.2f} {b:6.2f}  {t}")
    print(f"duration {DUR:.2f} s")
else:
    final = os.path.join(ROOT, 'output', 'tesla_roadster_ai_reel.mp4')
    run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(BUILD, 'silent.mp4'), '-i', os.path.join(BUILD, 'audio.wav'),
         '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final])
    run(['ffmpeg', '-v', 'error', '-y', '-i', final, '-c:v', 'libx264', '-crf', '23', '-preset', 'medium', '-c:a', 'copy',
         '-movflags', '+faststart', os.path.join(ROOT, 'output', 'tesla_roadster_ai_reel_preview.mp4')])
    print('wrote', final)
