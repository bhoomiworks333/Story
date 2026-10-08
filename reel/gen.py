#!/usr/bin/env python3
"""Generate reel/public/index.html (HyperFrames composition).

    python3 reel/gen.py            # full reel
    python3 reel/gen.py --until 11 # short test render of the opening
"""
import argparse, json, os, html

ap = argparse.ArgumentParser()
ap.add_argument("--until", type=float, default=None)
args = ap.parse_args()

HERE = os.path.dirname(os.path.abspath(__file__))
FPS, W, H = 30, 1080, 1920
VIDEO_END = 34.98            # end of the speaker cut
END_CARD = 2.3               # follow card after the last line
TOTAL = VIDEO_END + END_CARD
DUR = min(TOTAL, args.until) if args.until else TOTAL

ACCENT = "#2F6BFF"
INK = "#0E0E10"
PAPER = "#F3F2EE"
PIP = dict(left=40, top=96, width=1000, height=720)   # takeover: speaker window on top
FULL = dict(left=0, top=0, width=W, height=H)

def q(t):  # quantize to frame
    return round(t * FPS) / FPS

# ---------------------------------------------------------------- captions
# (start, end, text) on the output timeline; **word** = accent colour
CAPS = [
    (0.00, 2.00, "Only **1%**"),
    (2.00, 3.00, "of the organizations"),
    (3.00, 4.05, "use an **ERP** system"),
    (4.08, 5.45, "India has more than"),
    (5.45, 7.25, "**70–80 lakh**"),
    (7.25, 8.56, "SMEs right now"),
    (8.56, 10.73, "And **Zoho** is betting big on it"),
    (10.73, 12.50, "When **ERP** is implemented"),
    (12.50, 14.05, "at any organization"),
    (14.09, 15.69, "it becomes a **data foundation**"),
    (15.69, 16.55, "they can actually"),
    (16.55, 18.21, "implement any **AI** solution"),
    (18.21, 19.11, "based on their data"),
    (19.11, 20.65, "**ERP** is the foundation"),
    (20.65, 22.89, "**Zoho ERP** is proprietary"),
    (22.89, 24.62, "It's subscription-based"),
    (24.62, 25.24, "But the future"),
    (25.24, 26.25, "from what I see"),
    (26.25, 27.31, "is **open source**"),
    (27.31, 29.00, "Now that **AI** is so powerful"),
    (29.00, 30.20, "you can take it"),
    (30.20, 31.51, "to **any level** you want"),
]

def rich(text):
    out, on = [], False
    for i, part in enumerate(text.split("**")):
        out.append(f'<b class="hl">{html.escape(part)}</b>' if i % 2 else html.escape(part))
    return "".join(out)

# ---------------------------------------------------------------- sfx
# (start, file, volume) — start = event time minus the sound's peak offset
SFX = [
    (0.00, "pop", 0.40),
    (0.38, "hit_main", 0.55),        # the one blue dot lands on "one percent"
    (3.78, "whoosh_short", 0.28),
    (4.15, "tick", 0.30),
    (5.01, "data_whoosh", 0.40),     # counter rolls on "seventy"
    (6.22, "tick", 0.35),
    (7.30, "pop", 0.28),
    (7.34, "whoosh_mid", 0.40),      # billboard enters
    (9.88, "hit_short", 0.45),       # BETTING BIG tag
    (10.45, "whoosh_short", 0.32),   # takeover
    (12.50, "hit_short", 0.50),      # ERP block lands
    (15.12, "tick", 0.35),
    (16.88, "pop", 0.32), (17.28, "pop", 0.32), (17.68, "pop", 0.32),
    (17.84, "data_whoosh", 0.28),
    (19.73, "hit_main", 0.50),       # "ERP is the foundation"
    (19.52, "whoosh_deep", 0.30),    # back to full-bleed at 20.6
    (22.01, "pop", 0.40),
    (23.54, "tick", 0.35),
    (24.29, "whoosh_short", 0.30),
    (24.95, "riser", 0.32),
    (26.47, "hit_main", 0.55),       # "open source"
    (28.40, "tick", 0.22), (28.58, "tick", 0.24), (28.76, "tick", 0.26),
    (28.94, "tick", 0.28), (29.12, "tick", 0.30),
    (30.68, "pop", 0.36),
    (30.43, "whoosh_deep2", 0.32),   # back to full-bleed at 31.4
    (31.56, "tick", 0.28), (32.76, "tick", 0.28),
    (33.57, "hit_short", 0.45),
    (33.69, "hit_main", 0.50),
    (34.59, "whoosh_short", 0.30),
    (35.15, "pop", 0.40), (35.85, "tick", 0.35),
]
SFX_LEN = {"pop": .09, "tick": .03, "hit_main": 1.95, "hit_short": .81, "riser": 1.88,
           "data_whoosh": 1.06, "whoosh_deep": 2.63, "whoosh_deep2": 2.33,
           "whoosh_short": 1.36, "whoosh_mid": 1.12}

# ---------------------------------------------------------------- markup
css = f"""
@font-face {{ font-family: "Inter"; src: url("fonts/Inter-SemiBold.otf") format("opentype"); font-weight: 600; font-display: block; }}
@font-face {{ font-family: "Inter"; src: url("fonts/Inter-Bold.otf") format("opentype"); font-weight: 700; font-display: block; }}
@font-face {{ font-family: "Inter"; src: url("fonts/Inter-ExtraBold.otf") format("opentype"); font-weight: 800; font-display: block; }}
@font-face {{ font-family: "Inter"; src: url("fonts/Inter-Black.otf") format("opentype"); font-weight: 900; font-display: block; }}
:root {{ --accent: {ACCENT}; --ink: {INK}; --paper: {PAPER}; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden;
  background: {PAPER}; font-family: "Inter", ui-sans-serif, system-ui, sans-serif; color: {INK}; }}
#stage {{ position: relative; width: {W}px; height: {H}px; overflow: hidden;
  background-color: {PAPER};
  background-image: radial-gradient(rgba(14,14,16,.10) 1.6px, transparent 1.6px);
  background-size: 36px 36px; }}
.video-wrapper {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; overflow: hidden; border-radius: 0; }}
.video-wrapper video {{ width: 100%; height: 100%; object-fit: cover; object-position: 50% 32%; }}
.video-wrapper.pip {{ box-shadow: 0 24px 60px rgba(14,14,16,.28); }}
.layer {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; pointer-events: none; overflow: hidden; }}
.panel {{ position: absolute; background: #fff; border-radius: 36px;
  box-shadow: 0 18px 50px rgba(14,14,16,.22); }}
.kicker {{ font-weight: 800; font-size: 26px; letter-spacing: .16em; color: var(--accent); text-transform: uppercase; }}
/* captions */
.cap {{ position: absolute; left: 0; top: 1440px; width: {W}px; display: flex; justify-content: center; }}
.cap span.box {{ display: inline-block; background: #fff; color: {INK}; font-weight: 800; font-size: 66px;
  line-height: 1.12; padding: 14px 30px 18px; border-radius: 22px; box-shadow: 0 10px 28px rgba(0,0,0,.18);
  white-space: nowrap; }}
.cap .hl, .hl {{ color: var(--accent); }}
/* hook */
.grid {{ position: absolute; left: 56px; top: 56px; width: 380px; height: 380px; display: grid;
  grid-template-columns: repeat(10, 1fr); gap: 10px; }}
.dot {{ width: 29px; height: 29px; border-radius: 50%; background: #D5D5DB; }}
.big {{ font-weight: 900; letter-spacing: -.04em; line-height: .9; }}
/* blocks */
.block {{ position: absolute; border-radius: 26px; display: flex; flex-direction: column; align-items: center;
  justify-content: center; color: #fff; }}
.erp {{ background: linear-gradient(135deg, #2F6BFF, #1C47C9); box-shadow: 0 20px 44px rgba(47,107,255,.40); }}
.ai {{ background: {INK}; box-shadow: 0 14px 30px rgba(14,14,16,.28); }}
.chip {{ position: absolute; display: inline-flex; align-items: center; gap: 16px; border-radius: 999px;
  font-weight: 900; white-space: nowrap; }}
.col {{ position: absolute; top: 0; width: 470px; height: 470px; border-radius: 32px; padding: 40px 36px;
  display: flex; flex-direction: column; justify-content: space-between; }}
.bar {{ position: absolute; bottom: 0; width: 120px; border-radius: 18px 18px 8px 8px; background: {INK}; }}
.kin {{ position: absolute; left: 64px; display: inline-block; white-space: nowrap; font-weight: 900;
  border-radius: 18px; }}
"""

L = []   # layers (html strings)
T = []   # timeline js statements
def js(s): T.append(s)

def layer(lid, start, end, inner, track=3, extra_style=""):
    start, end = q(start), q(min(end, DUR))
    if start >= DUR:
        return False
    L.append(f'<div class="layer clip" id="{lid}" data-start="{start:.4f}" data-duration="{end-start:.4f}" '
             f'data-track-index="{track}" style="{extra_style}">{inner}</div>')
    return True

def enter(sel, t, frm, to=None, dur=.45, ease="power3.out"):
    to = to or {k: (1 if k in ("opacity", "scale") else 0) for k in frm}
    to = dict(to, duration=dur, ease=ease)
    js(f"tl.fromTo({json.dumps(sel)}, {json.dumps(frm)}, {json.dumps(to)}, {q(t):.4f});")

def to(sel, t, props, dur=.35, ease="power2.in"):
    js(f"tl.to({json.dumps(sel)}, {json.dumps(dict(props, duration=dur, ease=ease))}, {q(t):.4f});")

def inset(box):
    t, l = box["top"], box["left"]
    r, b = W - l - box["width"], H - t - box["height"]
    rad = 40 if box is not FULL else 0
    return f"inset({t}px {r}px {b}px {l}px round {rad}px)"

def video_to(t, box, dur=.6, pip=True):
    # a clip-path window instead of moving/resizing the wrapper: sub-pixel smooth, face stays put
    js(f"tl.to('#video-wrap', {json.dumps(dict(clipPath=inset(box), duration=dur, ease='power3.inOut'))}, {q(t):.4f});")
    js(f"tl.to('#pip-shadow', {json.dumps(dict(opacity=1 if pip else 0, duration=dur, ease='power2.inOut'))}, {q(t):.4f});")

# ---- 1. HOOK  (0 – 4.05): 100 dots, one lights up --------------------------------
dots = "".join(f'<div class="dot{" one" if i == 45 else ""}" id="d{i}"></div>' for i in range(100))
layer("hook", 0, 4.05, f"""
<div class="panel" id="hook-panel" style="left:60px;top:880px;width:960px;height:492px;">
  <div class="grid">{dots}</div>
  <div style="position:absolute;left:480px;top:44px;width:440px;">
    <div class="kicker">Indian SMEs on ERP</div>
    <div class="big" id="hook-num" style="font-size:250px;margin-top:6px;color:{INK};">1<span style="color:{ACCENT}">%</span></div>
    <div id="hook-sub" style="font-weight:700;font-size:38px;line-height:1.25;color:#55555C;margin-top:12px;">
      use a real ERP —<br>not just Tally or Busy</div>
  </div>
</div>""")
enter("#hook-panel", 0.0, {"opacity": 0, "y": 80, "scale": .94}, dur=.45, ease="back.out(1.4)")
js("tl.from('#hook .dot', {opacity:0, scale:.2, duration:.28, ease:'power2.out', stagger:{each:.0045, from:'center', grid:[10,10]}}, 0.10);")
js(f"tl.to('#hook .dot:not(.one)', {{backgroundColor:'#E7E7EB', duration:.25}}, {q(.60)});")
js(f"tl.to('#d45', {{backgroundColor:'{ACCENT}', duration:.12}}, {q(.60)});")
js(f"tl.fromTo('#d45', {{scale:1}}, {{immediateRender:false, scale:1.75, duration:.18, ease:'power2.out', yoyo:true, repeat:1}}, {q(.60)});")
enter("#hook-num", 0.60, {"opacity": 0, "scale": .5}, dur=.42, ease="back.out(2)")
enter("#hook-sub", 1.05, {"opacity": 0, "y": 20}, dur=.4)
to("#hook-panel", 3.80, {"opacity": 0, "y": 60}, dur=.25)

# ---- name tag (4.1 – 7.2) ------------------------------------------------------
layer("name", 4.1, 7.25, f"""
<div class="chip" id="name-chip" style="left:48px;top:120px;background:rgba(14,14,16,.82);color:#fff;
  padding:16px 28px 16px 18px;font-size:30px;font-weight:800;">
  <span style="width:18px;height:18px;border-radius:50%;background:{ACCENT};display:inline-block"></span>
  Prashant Agrawal <span style="font-weight:600;color:#C9C9CF">· Your factory ERP guy</span></div>""", track=4)
enter("#name-chip", 4.12, {"opacity": 0, "x": -60}, dur=.45)
to("#name-chip", 6.95, {"opacity": 0, "x": -40}, dur=.25)

# ---- 2. SMEs counter (4.1 – 7.85) ----------------------------------------------
layer("smes", 4.1, 7.88, f"""
<div class="panel" id="sme-panel" style="left:60px;top:930px;width:960px;height:430px;padding:46px 56px;">
  <div class="kicker">Small & medium businesses · India</div>
  <div class="big" style="font-size:180px;margin-top:10px;">
    <span id="sme-a" style="display:inline-block">0</span><span style="font-size:84px;letter-spacing:-.02em"> lakh</span></div>
  <div style="position:absolute;left:56px;right:56px;bottom:52px;">
    <div style="display:flex;justify-content:space-between;font-weight:800;font-size:28px;color:#55555C;">
      <span>Using an ERP</span><span id="sme-pct" style="color:{ACCENT}">~1%</span></div>
    <div style="margin-top:14px;height:22px;border-radius:11px;background:#E7E7EB;overflow:hidden;">
      <div id="sme-fill" style="width:0;height:100%;background:{ACCENT};border-radius:11px;"></div></div>
  </div>
</div>""")
enter("#sme-panel", 4.1, {"opacity": 0, "y": 80, "scale": .95}, dur=.45, ease="back.out(1.3)")
js(f"(function(){{const o={{v:0}};tl.to(o,{{v:1,duration:{q(6.40)-q(4.10):.4f},ease:'none',onUpdate:function(){{const e=document.querySelector('#sme-a');if(!e)return;const t=tl.time();"
   f"if(t<{q(6.22)}){{const p=Math.min(1,Math.max(0,(t-{q(5.45)})/.7));e.innerHTML=String(Math.round(70*(1-Math.pow(1-p,3))));}}"
   f"else{{e.innerHTML='70<span style=\\'color:{ACCENT}\\'>–80</span>';}}}}}},{q(4.10)});}})();")
js(f"tl.fromTo('#sme-a', {{scale:1}}, {{immediateRender:false, scale:1.06, duration:.12, yoyo:true, repeat:1, transformOrigin:'0% 70%'}}, {q(6.22)});")
js(f"tl.fromTo('#sme-pct', {{opacity:0}}, {{opacity:1, duration:.2}}, {q(7.30)});")
js(f"tl.fromTo('#sme-fill', {{width:'0%'}}, {{width:'1.5%', duration:.35, ease:'power2.out'}}, {q(7.30)});")
to("#sme-panel", 7.62, {"opacity": 0, "y": 60}, dur=.25)

# ---- 3. billboard tag (8.6 – 10.7) ---------------------------------------------
layer("bb-tag", 8.6, 10.70, f"""
<div class="chip" id="bb-chip" style="left:300px;top:760px;background:{INK};color:#fff;padding:22px 40px;
  font-size:60px;transform-origin:50% 50%;">BETTING BIG <span style="color:{ACCENT};font-size:64px">↗</span></div>""")
enter("#bb-chip", 9.90, {"opacity": 0, "scale": 1.8, "rotation": -10}, {"opacity": 1, "scale": 1, "rotation": -4},
      dur=.32, ease="back.out(2.2)")
to("#bb-chip", 10.45, {"opacity": 0, "y": -30}, dur=.2)

# ---- 4. FOUNDATION takeover (10.73 – 20.6) ------------------------------------
video_to(10.55, PIP)
ai = ["Analytics", "Predictions", "GenAI"]
ai_blocks = "".join(
    f'<div class="block ai" id="ai{i}" style="left:{90 + i*310}px;top:1080px;width:280px;height:130px;">'
    f'<div style="font-weight:800;font-size:38px">{n}</div></div>' for i, n in enumerate(ai))
particles = "".join(
    f'<div class="pt" id="pt{i}" style="position:absolute;left:{170 + (i*97)%760}px;top:1250px;width:14px;height:14px;'
    f'border-radius:50%;background:#9DB8FF;"></div>' for i in range(14))
layer("found", 10.73, 20.62, f"""
<div id="f-kick" class="kicker" style="position:absolute;left:90px;top:880px;font-size:30px;color:{INK}">What AI actually needs</div>
<div id="f-ai-kick" class="kicker" style="position:absolute;left:90px;top:1022px;">AI on top</div>
{ai_blocks}
{particles}
<div class="block erp" id="erp" style="left:90px;top:1232px;width:900px;height:150px;">
  <div style="font-weight:900;font-size:76px;letter-spacing:-.02em;line-height:1">ERP</div>
  <div id="erp-sub" style="font-weight:700;font-size:28px;letter-spacing:.14em;opacity:.9;margin-top:6px">ALL YOUR BUSINESS DATA</div>
</div>
<div id="f-found" class="kicker" style="position:absolute;left:0;width:{W}px;text-align:center;top:1396px;color:{INK};font-size:28px">▲ the data foundation</div>
""")
enter("#f-kick", 10.85, {"opacity": 0, "y": 20}, dur=.35)
enter("#erp", 12.50, {"opacity": 0, "y": -420}, dur=.5, ease="bounce.out")
js(f"tl.fromTo('#erp-sub', {{opacity:0}}, {{opacity:.9, duration:.3}}, {q(12.95)});")
enter("#f-found", 15.12, {"opacity": 0, "y": 16}, dur=.3)
js(f"tl.fromTo('#erp', {{boxShadow:'0 20px 44px rgba(47,107,255,.40)'}}, {{immediateRender:false, boxShadow:'0 0 0 18px rgba(47,107,255,.22)', duration:.35, yoyo:true, repeat:1}}, {q(15.12)});")
enter("#f-ai-kick", 16.80, {"opacity": 0, "x": -30}, dur=.3)
for i, t in enumerate((16.90, 17.30, 17.70)):
    enter(f"#ai{i}", t, {"opacity": 0, "y": -260}, dur=.42, ease="back.out(1.6)")
js(f"tl.fromTo('#found .pt', {{opacity:0, y:0}}, {{opacity:1, y:-150, duration:.55, ease:'power1.in', stagger:.05}}, {q(18.25)});")
js(f"tl.to('#found .pt', {{opacity:0, duration:.15, stagger:.05}}, {q(18.70)});")
js(f"tl.fromTo('#erp', {{scale:1}}, {{immediateRender:false, scale:1.05, duration:.14, yoyo:true, repeat:1, ease:'power2.out'}}, {q(19.97)});")
js(f"tl.to('#found .ai', {{y:-26, duration:.14, yoyo:true, repeat:1, ease:'power2.out', stagger:.05}}, {q(19.97)});")
to("#found", 20.40, {"opacity": 0}, dur=.2)
video_to(20.45, FULL, dur=.5, pip=False)

# ---- 5. proprietary chip on billboard / speaker (20.65 – 24.6) ----------------
layer("prop", 20.65, 24.58, f"""
<div class="panel" id="prop-panel" style="left:150px;top:980px;width:780px;padding:34px 40px;">
  <div style="display:flex;align-items:center;gap:22px;">
    <div style="font-size:64px;line-height:1">🔒</div>
    <div><div class="kicker" style="color:#8A8A92">Zoho ERP</div>
      <div style="font-weight:900;font-size:58px;letter-spacing:-.02em">Proprietary</div></div>
  </div>
  <div id="prop-sub" style="margin-top:20px;display:flex;gap:14px;">
    <span style="background:#F0F0F3;border-radius:999px;padding:10px 22px;font-weight:800;font-size:30px">₹ Subscription</span>
    <span style="background:#F0F0F3;border-radius:999px;padding:10px 22px;font-weight:800;font-size:30px">Closed code</span>
  </div>
</div>""")
enter("#prop-panel", 22.03, {"opacity": 0, "y": 60, "scale": .92}, dur=.4, ease="back.out(1.5)")
js(f"tl.fromTo('#prop-sub', {{opacity:0, y:14}}, {{opacity:1, y:0, duration:.3}}, {q(23.56)});")
to("#prop-panel", 24.40, {"opacity": 0, "y": 40}, dur=.2)

# ---- 6. proprietary vs open takeover (24.6 – 27.3) -----------------------------
video_to(24.55, PIP)
layer("vs", 24.62, 27.40, f"""
<div id="vs" style="position:absolute;left:55px;top:880px;width:970px;height:470px;">
  <div class="col" id="vs-l" style="left:0;background:#fff;box-shadow:0 14px 34px rgba(14,14,16,.14)">
    <div style="font-size:70px">🔒</div>
    <div><div class="kicker" style="color:#8A8A92">Zoho ERP</div>
      <div style="font-weight:900;font-size:50px;line-height:1.05;margin-top:6px">Proprietary</div>
      <div style="font-weight:700;font-size:28px;color:#6A6A72;margin-top:12px">Rent it. Their roadmap.</div></div>
  </div>
  <div class="col" id="vs-r" style="left:500px;background:{ACCENT};color:#fff;box-shadow:0 20px 44px rgba(47,107,255,.45)">
    <div style="font-size:70px">🔓</div>
    <div><div class="kicker" style="color:#CFDCFF">The future</div>
      <div style="font-weight:900;font-size:50px;line-height:1.05;margin-top:6px">Open source</div>
      <div style="font-weight:700;font-size:28px;color:#E4EBFF;margin-top:12px">Own it. Extend it with AI.</div></div>
  </div>
  <div id="vs-x" style="position:absolute;left:452px;top:200px;width:66px;height:66px;border-radius:50%;background:{INK};color:#fff;
    font-weight:900;font-size:26px;display:flex;align-items:center;justify-content:center">VS</div>
</div>""")
enter("#vs-l", 24.70, {"opacity": 0, "x": -80}, dur=.4)
enter("#vs-x", 25.30, {"opacity": 0, "scale": .3}, dur=.3, ease="back.out(2)")
enter("#vs-r", 26.71, {"opacity": 0, "scale": .7, "x": 60}, dur=.42, ease="back.out(1.7)")
js(f"tl.to('#vs-l', {{opacity:.45, scale:.94, duration:.35}}, {q(26.71)});")
to("#vs", 27.15, {"opacity": 0, "y": 30}, dur=.2)

# ---- 7. any level (27.3 – 31.4) -------------------------------------------------
hs = [110, 170, 240, 320, 410]
bars = "".join(f'<div class="bar" id="bar{i}" style="left:{40 + i*150}px;height:{h}px;'
               f'{"background:" + ACCENT if i == 4 else ""}"></div>' for i, h in enumerate(hs))
layer("level", 27.31, 31.45, f"""
<div id="lvl" style="position:absolute;left:90px;top:870px;width:900px;height:520px;">
  <div class="kicker" style="color:{INK};font-size:30px">Open source + AI</div>
  <div style="position:absolute;left:0;top:60px;width:820px;height:440px;">{bars}
    <div id="lvl-arrow" style="position:absolute;left:640px;top:-36px;font-weight:900;font-size:64px;color:{ACCENT}">↑ ∞</div>
  </div>
  <div id="lvl-lbl" style="position:absolute;left:0;top:150px;font-weight:900;font-size:56px;line-height:1.05;letter-spacing:-.02em">Take it to<br><span style="color:{ACCENT}">any level</span></div>
</div>""")
enter("#lvl", 27.40, {"opacity": 0, "y": 30}, dur=.35)
js(f"tl.fromTo('#level .bar', {{scaleY:0, transformOrigin:'50% 100%'}}, {{scaleY:1, duration:.32, ease:'back.out(1.6)', stagger:.18}}, {q(28.40)});")
js(f"tl.fromTo('#lvl-lbl', {{opacity:0, y:20}}, {{opacity:1, y:0, duration:.35}}, {q(29.10)});")
enter("#lvl-arrow", 30.70, {"opacity": 0, "y": 40}, dur=.4, ease="back.out(2)")
to("#lvl", 31.20, {"opacity": 0}, dur=.2)
video_to(31.25, FULL, dur=.5, pip=False)

# ---- 8. payoff kinetic type (31.5 – 34.98) -------------------------------------
layer("pay", 31.51, VIDEO_END, f"""
<div class="kin" id="k1" style="top:1060px;background:#fff;color:{INK};font-size:56px;padding:12px 26px;">SMEs of India</div>
<div class="kin" id="k2" style="top:1160px;background:#fff;color:{INK};font-size:56px;padding:12px 26px;">need to</div>
<div class="kin" id="k3" style="top:1262px;background:#fff;color:{INK};font-size:132px;padding:6px 30px 14px;letter-spacing:-.03em;">DIGITALLY</div>
<div class="kin" id="k4" style="top:1432px;background:{ACCENT};color:#fff;font-size:132px;padding:6px 30px 14px;letter-spacing:-.03em;">TRANSFORM</div>
<div class="kin" id="k5" style="top:1608px;background:#fff;color:{INK};font-size:56px;padding:12px 26px;">themselves.</div>
""", track=5)
for sel, t in (("#k1", 31.58), ("#k2", 32.78), ("#k5", 34.37)):
    js(f"tl.fromTo('{sel}', {{clipPath:'inset(0 100% 0 0)'}}, {{clipPath:'inset(0 0% 0 0)', duration:.32, ease:'power3.out'}}, {q(t)});")
for sel, t in (("#k3", 33.59), ("#k4", 33.93)):
    enter(sel, t, {"opacity": 0, "scale": 1.35, "y": 20}, dur=.3, ease="power4.out")

# ---- end card (34.98 – end) ----------------------------------------------------
js(f"tl.to('#video-wrap', {{opacity:0, scale:.92, duration:.35, ease:'power2.in'}}, {q(VIDEO_END - .3)});")
layer("end", VIDEO_END - .05, TOTAL, f"""
<div style="position:absolute;left:0;top:560px;width:{W}px;display:flex;flex-direction:column;align-items:center;">
  <img id="e-face" src="img/headshot.png" style="width:300px;height:300px;border-radius:50%;
       box-shadow:0 0 0 10px #fff, 0 0 0 16px {ACCENT}, 0 24px 50px rgba(14,14,16,.25);" />
  <div id="e-name" style="font-weight:900;font-size:78px;letter-spacing:-.02em;margin-top:56px">Prashant Agrawal</div>
  <div id="e-role" style="font-weight:700;font-size:38px;color:#55555C;margin-top:10px">Your factory ERP guy</div>
  <div id="e-btn" style="margin-top:70px;background:{INK};color:#fff;border-radius:999px;padding:30px 56px;font-weight:800;font-size:42px">
    Follow <span style="color:#9DB8FF">@build.with.prashant</span></div>
  <div id="e-sub" style="margin-top:28px;font-weight:700;font-size:32px;color:#6A6A72">ERP × AI breakdowns that aren't BS</div>
</div>""", track=6)
enter("#e-face", 35.15, {"opacity": 0, "scale": .4}, dur=.5, ease="back.out(1.8)")
enter("#e-name", 35.35, {"opacity": 0, "y": 30}, dur=.4)
enter("#e-role", 35.50, {"opacity": 0, "y": 20}, dur=.4)
enter("#e-btn", 35.85, {"opacity": 0, "scale": .6}, dur=.4, ease="back.out(2)")
enter("#e-sub", 36.10, {"opacity": 0}, dur=.4)

# ---- captions --------------------------------------------------------------------
for k, (a, b, text) in enumerate(CAPS):
    if a >= DUR:
        continue
    if layer(f"cap{k}", a, b, f'<div class="cap"><span class="box" id="capb{k}">{rich(text)}</span></div>', track=7):
        enter(f"#capb{k}", a, {"opacity": 0, "scale": .86, "y": 14}, dur=.16, ease="back.out(2)")

# ---- audio -----------------------------------------------------------------------
audio = []
for k, (t, name, vol) in enumerate(sorted(SFX)):
    if t >= DUR:
        continue
    d = min(SFX_LEN[name], DUR - t)
    audio.append(f'<audio id="sfx{k}" src="sfx/{name}.wav" data-start="{q(t):.4f}" data-duration="{d:.4f}" '
                 f'data-track-index="{20 + k}" data-volume="{vol}"></audio>')

vd = min(VIDEO_END, DUR)
doc = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8" /><style>{css}</style></head>
<body>
<div id="stage" data-composition-id="reel" data-start="0" data-duration="{DUR:.4f}" data-fps="{FPS}" data-width="{W}" data-height="{H}">
  <div id="pip-shadow" style="position:absolute;left:{PIP['left']}px;top:{PIP['top']}px;width:{PIP['width']}px;height:{PIP['height']}px;border-radius:40px;box-shadow:0 26px 60px rgba(14,14,16,.32);opacity:0;"></div>
  <div class="video-wrapper" id="video-wrap" style="clip-path:{inset(FULL)};">
    <video id="bg-video" src="input-video.mp4" playsinline data-has-audio="true" data-start="0" data-duration="{vd:.4f}" data-track-index="1"></video>
  </div>
  {''.join(L)}
  {''.join(audio)}
  <script src="vendor/gsap.min.js"></script>
  <script>
  (function () {{
    const tl = window.gsap.timeline({{ paused: true }});
    {chr(10).join('    ' + s for s in T)}
    tl.set({{}}, {{}}, {DUR:.4f});
    window.__timelines = window.__timelines || {{}};
    window.__timelines["reel"] = tl;
  }})();
  </script>
</div>
</body>
</html>
"""
open(os.path.join(HERE, "public", "index.html"), "w").write(doc)
print(f"wrote index.html  duration={DUR:.2f}s  layers={len(L)}  sfx={len(audio)}")
