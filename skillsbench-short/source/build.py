"""Generate the HyperFrames composition (index.html) for the SkillsBench short."""
import json, sys

words = json.load(open(sys.argv[1]))
out = sys.argv[2]
DUR = 41.2667

# Script wording where the ASR blurred sounds together (s-before-is, dropped -ed, "There's").
fix = {7: "skills", 14: "There's", 60: "focused", 93: '"SKILLS"', 57: "And"}
for i, t in fix.items():
    words[i]["text"] = t
words[38]["text"] = "skill,"
words[51]["text"] = "skill,"
words[76]["text"] = "well,"

# (first, last, override-text) — breaks at natural phrase boundaries, <=4 words.
groups = [
    (0, 2), (3, 4), (5, 7), (8, 9), (10, 13),
    (14, 15), (16, 17, "a research paper"), (18, 19),
    (20, 22), (23, 24), (25, 26), (27, 28, "different fields,"), (29, 30), (31, 32),
    (33, 35), (36, 38), (39, 41), (42, 44),
    (45, 47), (48, 51), (52, 54), (55, 56, "no difference."),
    (57, 59, "And the short,"), (60, 61), (62, 63), (64, 66, "than the long,"), (67, 68),
    (69, 71), (72, 74), (75, 76), (77, 79), (80, 81), (82, 85),
    (86, 88), (89, 91),
    (92, 93), (94, 96), (97, 99),
]
# "a" is not in the ASR output; it sits in the 8.48-8.96 gap before "research".
words[16]["start"] = 8.50

# Layout states: (start, mode)
FULL_WINDOWS = [(0, 2.20)]
def is_full(t):
    return any(a <= t < b for a, b in FULL_WINDOWS)

caps = []
for gi, g in enumerate(groups):
    a, b = g[0], g[1]
    text = g[2] if len(g) > 2 else " ".join(w["text"] for w in words[a:b + 1])
    start = words[a]["start"]
    last_end = words[b]["end"]
    nxt = words[groups[gi + 1][0]]["start"] if gi + 1 < len(groups) else DUR
    end = min(nxt, last_end + 0.25)
    if gi + 1 == len(groups):
        end = last_end + 0.6
    caps.append((round(start, 3), round(end - start, 3), text, is_full(start)))

# A caption that straddles a layout cut is split there, so it never sits in the wrong position.
CUTS = [2.20]
split_caps = []
for s0, d, t, full in caps:
    e0 = s0 + d
    for c in CUTS:
        if s0 < c < e0:
            split_caps.append((s0, round(c - s0, 3), t, full))
            s0, full = c, is_full(c)
    split_caps.append((s0, round(e0 - s0, 3), t, full))
caps = split_caps

cap_html = "\n".join(
    f'      <div id="cap{i}" class="clip cap {"cap-full" if full else "cap-split"}" '
    f'data-start="{s}" data-duration="{d}" data-track-index="10">'
    f'<span class="box">{t}</span></div>'
    for i, (s, d, t, full) in enumerate(caps)
)

HTML = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>SkillsBench short</title>
    <script src="assets/gsap.min.js"></script>
    <style>
      @font-face { font-family: "InterHF"; src: url("assets/Inter-Regular.otf"); font-weight: 400; }
      @font-face { font-family: "InterHF"; src: url("assets/Inter-Medium.otf"); font-weight: 500; }
      @font-face { font-family: "InterHF"; src: url("assets/Inter-SemiBold.otf"); font-weight: 600; }
      @font-face { font-family: "InterHF"; src: url("assets/Inter-Bold.otf"); font-weight: 700; }
      html, body { margin: 0; background: #111111; }
      body { font-family: "InterHF", system-ui, sans-serif; color: #fff; }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; background: #111111; }

      /* speaker layout (full / split) is pre-built into base.mp4 */
      #base { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 1; }

      /* top-half assets */
      .asset { position: absolute; left: 0; top: 0; width: 1080px; height: 960px; overflow: hidden;
               background: #111111; z-index: 2; }
      .center { display: flex; align-items: center; justify-content: center; flex-direction: column; }
      #typing { position: absolute; left: 40px; top: 170px; width: 1000px; height: 600px; z-index: 2;
                border-radius: 18px; border: 2px solid #2c2c2c; object-fit: cover; }
      /* header bar + asset label (reference: logo bar on top, label under the asset) */
      .hdr { position: absolute; left: 0; top: 0; width: 1080px; height: 120px; background: #111111; z-index: 5; }
      .hdr .t { position: absolute; left: 60px; top: 50px; font-size: 28px; font-weight: 600; letter-spacing: .14em; color: #9a9a9a; }
      .hdr .dot { position: absolute; left: 1004px; top: 58px; width: 14px; height: 14px; border-radius: 7px; background: #e5e5e5; }
      .hdr .rule { position: absolute; left: 60px; right: 60px; top: 112px; height: 2px; background: #262626; }
      .hl { position: absolute; background: rgba(255, 214, 0, 0.55); mix-blend-mode: multiply; border-radius: 3px; transform-origin: 0 50%; }
      .alabel { position: absolute; left: 0; right: 0; text-align: center; font-size: 40px; font-weight: 600; color: #fff; z-index: 3; }
      .page { background: #fff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,.45); }
      .page img { display: block; width: 100%; height: auto; }
      .foot { position: absolute; left: 0; right: 0; bottom: 78px; text-align: center; font-size: 26px;
              font-weight: 500; color: #7a7a7a; letter-spacing: .01em; }

      /* numbers */
      .num-row { display: flex; align-items: baseline; gap: 30px; width: 980px; margin: 8px 0; }
      .num { font-size: 168px; font-weight: 700; letter-spacing: -0.04em; line-height: 1; width: 600px; text-align: right; flex: none; }
      .lbl { font-size: 44px; font-weight: 600; color: #9b9b9b; letter-spacing: .12em; white-space: nowrap; }

      /* bars */
      .chart-title { position: absolute; top: 150px; left: 0; right: 0; text-align: center; font-size: 40px;
                     font-weight: 600; color: #cfcfcf; }
      .baseline { position: absolute; left: 140px; right: 140px; top: 720px; height: 3px; background: #444; }
      .col { position: absolute; top: 0; width: 300px; height: 960px; }
      .col .bar { position: absolute; left: 50px; width: 200px; bottom: 240px; border-radius: 10px 10px 0 0; transform-origin: 50% 100%; }
      .col .val { position: absolute; left: 0; right: 0; text-align: center; font-size: 72px; font-weight: 700; letter-spacing: -0.02em; }
      .col .cat { position: absolute; left: -20px; right: -20px; top: 748px; text-align: center; font-size: 36px; font-weight: 600; color: #cfcfcf; }

      /* short vs long */
      .doc { position: absolute; background: #1d1d1d; border: 2px solid #333; border-radius: 18px; overflow: hidden; }
      .doc .hd { font-family: "InterHF", monospace; font-size: 26px; font-weight: 600; color: #bdbdbd; padding: 22px 26px 8px; }
      .ln { height: 14px; border-radius: 7px; background: #3a3a3a; margin: 16px 26px; }
      .badge { position: absolute; width: 84px; height: 84px; border-radius: 42px; display: flex; align-items: center; justify-content: center; }
      .tag { position: absolute; text-align: center; font-size: 40px; font-weight: 600; }

      /* CTA */
      .cta-kick { font-size: 44px; font-weight: 500; color: #a8a8a8; margin-top: 44px; }
      .cta-word { font-size: 112px; font-weight: 700; letter-spacing: .04em; line-height: 1.05; }

      /* captions */
      .cap { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 10; }
      .cap .box { position: absolute; left: 50%; top: 960px; transform: translate(-50%, -50%); background: #fff; color: #000;
                  font-size: 50px; font-weight: 600; line-height: 1.15; letter-spacing: -0.01em;
                  padding: 14px 26px 16px; border-radius: 14px; white-space: nowrap; }
      .cap-full .box { top: 1720px; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="__DUR__">
      <video id="base" class="clip" src="assets/base.mp4" muted playsinline data-start="0" data-duration="__DUR__" data-track-index="0"></video>

      <div id="h-typing" class="clip hdr" data-start="2.2" data-duration="5.64" data-track-index="2"><div class="t">WHAT MOST PEOPLE DO</div><div class="dot"></div><div class="rule"></div></div>
      <div id="l-typing" class="clip alabel" data-start="2.2" data-duration="5.64" data-track-index="3" style="top: 800px;">Asking AI to write the skill</div>
      <div id="h-paper1" class="clip hdr" data-start="7.84" data-duration="__HDRDUR__" data-track-index="2"><div class="t">SKILLSBENCH · ARXIV:2602.12670</div><div class="dot"></div><div class="rule"></div></div>
      <video id="typing" class="clip" src="assets/typing.mp4" muted playsinline data-start="2.2" data-duration="5.64" data-track-index="1"></video>

      <div id="a-title" class="clip asset center" data-start="7.84" data-duration="2.72" data-track-index="1">
        <div id="title-card" class="page" style="width: 1000px; margin-top: 40px;"><img src="assets/title.png" alt="" /></div>
        <div class="alabel" style="top: 836px;">The research paper</div>
      </div>

      <div id="a-nums" class="clip asset" data-start="10.56" data-duration="6.16" data-track-index="1">
        <div id="np-cam" style="position: absolute; left: 0; top: 0; width: 1080px; height: 960px; transform-origin: 0 0;">
          <div id="np-page" class="page" style="position: absolute; left: 40px; top: 200px; width: 1000px;">
            <img src="assets/page.png" alt="" />
__HL__
          </div>
        </div>
      </div>

      <div id="a-bars" class="clip asset" data-start="16.72" data-duration="8.64" data-track-index="1">
        <div class="chart-title">Avg. pass-rate change vs. no skills</div>
        <div class="baseline"></div>
        <div id="col-h" class="col" style="left: 170px;">
          <div id="bar-h" class="bar" style="height: 400px; background: #f2f2f2;"></div>
          <div class="val" style="top: 228px;">+16.2</div>
          <div class="cat">Human-written skill</div>
        </div>
        <div id="col-a" class="col" style="left: 610px;">
          <div id="bar-a" class="bar" style="height: 8px; background: #6b6b6b;"></div>
          <div class="val" style="top: 610px; color: #9b9b9b;">≈ 0</div>
          <div class="cat">AI-written skill</div>
        </div>
      </div>

      <div id="a-sl" class="clip asset" data-start="25.36" data-duration="4.72" data-track-index="1">
        <div id="sl-short">
          <div class="doc" style="left: 110px; top: 330px; width: 380px; height: 250px;">
            <div class="hd">SKILL.md</div>
            <div class="ln" style="width: 260px;"></div><div class="ln" style="width: 300px;"></div><div class="ln" style="width: 200px;"></div>
          </div>
          <div class="badge" style="left: 258px; top: 590px; background: #1f9d55;">
            <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5" /></svg>
          </div>
          <div class="tag" style="left: 70px; width: 460px; top: 700px;">Short, focused</div>
        </div>
        <div id="sl-long">
          <div class="doc" style="left: 590px; top: 150px; width: 380px; height: 480px;">
            <div id="long-scroll">
              <div class="hd">SKILL.md</div>
              __LONGLINES__
            </div>
          </div>
          <div class="badge" style="left: 738px; top: 590px; background: #c0392b; box-shadow: 0 0 0 10px #111;">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18" /></svg>
          </div>
          <div class="tag" style="left: 550px; width: 460px; top: 700px;">Long, detailed</div>
        </div>
        <div class="foot">Focused skills (2–3 modules) beat comprehensive docs</div>
      </div>

      <div id="a-abs" class="clip asset" data-start="30.08" data-duration="7.68" data-track-index="1">
        <div id="abs-card" class="page" style="position: absolute; left: 40px; top: -440px; width: 1000px;"><img src="assets/abstract.png" alt="" /></div>
      </div>

      <div id="a-cta" class="clip asset" data-start="37.76" data-duration="__CTADUR__" data-track-index="1">
        <div class="page" style="position: absolute; left: 110px; top: 150px; width: 860px;"><img src="assets/title.png" alt="" /></div>
        <div class="cta-kick" style="position: absolute; left: 0; right: 0; top: 690px; margin: 0; text-align: center;">Comment</div>
        <div class="cta-word" style="position: absolute; left: 0; right: 0; top: 742px; text-align: center;">SKILLS</div>
      </div>

__CAPS__
    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
      const pop = (sel, t) => tl.fromTo(sel, { opacity: 0, scale: 0.94 }, { opacity: 1, scale: 1, duration: 0.28, ease: "power3.out" }, t);
      const rise = (sel, t) => tl.fromTo(sel, { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }, t);

      rise("#title-card", 7.84);
      rise("#np-page", 10.56);
      // focus (page px) -> camera transform; k = display / source width
      const K = 1000 / 937, SC = 1.7;
      const cam = (px, py, t) => tl.to("#np-cam", { x: 540 - SC * (40 + K * px), y: 540 - SC * (200 + K * py), scale: SC, duration: 0.5, ease: "power2.inOut" }, t);
      const mark = (sel, t) => tl.fromTo(sel, { scaleX: 0 }, { scaleX: 1, duration: 0.35, ease: "power2.out" }, t);
      cam(653, 532, 11.28); mark("#hl-84", 11.5);
      cam(213, 183, 13.36); mark("#hl-11", 13.58);
      cam(340, 270, 15.20); mark("#hl-73a", 15.42); mark("#hl-73b", 15.7);
      tl.fromTo("#col-h", { opacity: 0 }, { opacity: 1, duration: 0.2 }, 19.52);
      tl.fromTo("#bar-h", { scaleY: 0 }, { scaleY: 1, duration: 0.45, ease: "power3.out" }, 19.52);
      tl.fromTo("#col-a", { opacity: 0 }, { opacity: 1, duration: 0.2 }, 24.48);
      pop("#sl-short", 25.68);
      pop("#sl-long", 28.48);
      tl.fromTo("#long-scroll", { y: 0 }, { y: -900, duration: 4.0, ease: "none" }, 28.48);
      rise("#abs-card", 30.08);
      tl.fromTo("#abs-card", { scale: 1 }, { scale: 1.1, duration: 7.3, ease: "sine.inOut", transformOrigin: "50% 73%" }, 30.38);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""

K = 1000 / 937
def hl(i, x0, y0, x1, y1):
    return (f'            <div id="{i}" class="hl" style="left: {K*x0-3:.1f}px; top: {K*y0-2:.1f}px; '
            f'width: {K*(x1-x0)+6:.1f}px; height: {K*(y1-y0)+4:.1f}px;"></div>')
hl_html = "\n".join([hl("hl-84", 635, 524, 688, 541), hl("hl-11", 173, 174, 254, 193),
                      hl("hl-73a", 296, 253, 384, 271), hl("hl-73b", 58, 272, 98, 290)])
long_lines = "\n".join(
    f'<div class="ln" style="width: {w}px;"></div>' for w in ([300, 320, 250, 310, 280, 200, 320, 290, 260, 315, 240, 300] * 6)
)
html = (HTML.replace("__DUR__", str(DUR)).replace("__CTADUR__", str(round(DUR - 37.76, 4)))
        .replace("__CAPS__", cap_html).replace("__HL__", hl_html)
        .replace("__HDRDUR__", str(round(DUR - 7.84, 4))).replace("__LONGLINES__", long_lines))
open(out, "w").write(html)
for s, d, t, full in caps:
    print(f"{s:6.2f} +{d:4.2f} {'F' if full else 'S'} {t}")
