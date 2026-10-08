"""Generate the HyperFrames composition for the fake-GitHub-stars short."""
import json, sys

words = json.load(open(sys.argv[1]))
out = sys.argv[2]
DUR = 34.0

fix = {2: "favourite", 65: "hit.", 66: "They", 98: '"STARS"'}
for i, t in fix.items():
    words[i]["text"] = t

# phrase sizes, breaking at natural boundaries (<=4 words)
sizes = [3, 3, 2, 4, 3, 3, 2, 2, 2, 2, 2, 3, 3, 2, 3, 1, 2, 4,
         3, 3, 2, 2, 2, 4, 4, 3, 3, 2, 4,
         3, 2, 3, 3, 3, 2, 3, 2, 3, 3]
assert sum(sizes) == len(words), (sum(sizes), len(words))
groups, i = [], 0
for n in sizes:
    groups.append((i, i + n - 1)); i += n

FULL = [(0, 4.88), (18.16, 21.84)]          # full-frame windows (zoom moves end on these edges)
def is_full(t):
    return any(a <= t < b for a, b in FULL)

caps = []
for gi, (a, b) in enumerate(groups):
    text = " ".join(w["text"] for w in words[a:b + 1])
    start, last_end = words[a]["start"], words[b]["end"]
    nxt = words[groups[gi + 1][0]]["start"] if gi + 1 < len(groups) else DUR
    end = min(nxt, last_end + 0.25) if gi + 1 < len(groups) else last_end + 0.5
    caps.append((round(start, 3), round(end - start, 3), text, is_full(start)))

cap_html = "\n".join(
    f'      <div id="cap{i}" class="clip cap {"cap-full" if full else ""}" data-start="{s}" data-duration="{d}" '
    f'data-track-index="10"><span class="box">{t}</span></div>' for i, (s, d, t, full) in enumerate(caps))

def hdr(i, start, dur, text):
    return (f'      <div id="{i}" class="clip hdr" data-start="{start}" data-duration="{dur}" data-track-index="2">'
            f'<div class="t">{text}</div><div class="dot"></div><div class="rule"></div></div>')

STAR = ('<svg width="64" height="64" viewBox="0 0 16 16" fill="none" stroke="#c9d1d9" stroke-width="1.2" stroke-linejoin="round">'
        '<path d="M8 1.6l1.95 3.95 4.36.63-3.16 3.08.75 4.34L8 11.55l-3.9 2.05.75-4.34L1.69 6.18l4.36-.63z"/></svg>')

HTML = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Fake stars short</title>
    <script src="assets/gsap.min.js"></script>
    <style>
      @font-face { font-family: "InterHF"; src: url("assets/Inter-Regular.otf"); font-weight: 400; }
      @font-face { font-family: "InterHF"; src: url("assets/Inter-Medium.otf"); font-weight: 500; }
      @font-face { font-family: "InterHF"; src: url("assets/Inter-SemiBold.otf"); font-weight: 600; }
      @font-face { font-family: "InterHF"; src: url("assets/Inter-Bold.otf"); font-weight: 700; }
      html, body { margin: 0; background: #111111; }
      body { font-family: "InterHF", system-ui, sans-serif; color: #fff; }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; background: #111111; }
      #base { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 1; }
      .asset { position: absolute; left: 0; top: 0; width: 1080px; height: 960px; overflow: hidden; background: #111111; z-index: 2; }
      .hdr { position: absolute; left: 0; top: 0; width: 1080px; height: 120px; background: #111111; z-index: 5; }
      .hdr .t { position: absolute; left: 60px; top: 50px; font-size: 28px; font-weight: 600; letter-spacing: .14em; color: #9a9a9a; }
      .hdr .dot { position: absolute; left: 1004px; top: 58px; width: 14px; height: 14px; border-radius: 7px; background: #e5e5e5; }
      .hdr .rule { position: absolute; left: 60px; right: 60px; top: 112px; height: 2px; background: #262626; }
      .alabel { position: absolute; left: 0; right: 0; text-align: center; font-size: 40px; font-weight: 600; color: #fff; }
      .page { position: absolute; background: #fff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,.45); }
      .page img { display: block; width: 100%; height: auto; }
      .shot { position: absolute; border-radius: 16px; overflow: hidden; border: 2px solid #2c2c2c; }
      .shot img { display: block; width: 100%; height: auto; }
      #rec { position: absolute; left: 90px; top: 150px; width: 900px; height: 770px; z-index: 2; border-radius: 16px; border: 2px solid #2c2c2c; object-fit: cover; }

      /* star button */
      .ghbtn { position: absolute; left: 160px; top: 330px; width: 760px; height: 190px; border-radius: 28px; background: #21262d;
               border: 3px solid #3d444d; display: flex; align-items: center; }
      .ghbtn .l { display: flex; align-items: center; gap: 26px; padding: 0 44px; font-size: 76px; font-weight: 600; color: #e6edf3; }
      .ghbtn .sep { width: 3px; height: 190px; background: #3d444d; }
      .ghbtn .n { padding: 0 48px; font-size: 76px; font-weight: 700; color: #e6edf3; }
      #strike { position: absolute; left: 130px; top: 418px; width: 820px; height: 14px; border-radius: 7px; background: #e5484d;
                transform-origin: 0 50%; rotate: -8deg; }

      /* numbers */
      .numcol { position: absolute; left: 0; right: 0; text-align: center; }
      .numcol .num { font-size: 190px; font-weight: 700; letter-spacing: -0.04em; line-height: 1; }
      .numcol .lbl { font-size: 40px; font-weight: 600; color: #9b9b9b; letter-spacing: .12em; margin-top: 10px; }

      /* ranking */
      .rk-title { position: absolute; left: 0; right: 0; top: 160px; text-align: center; font-size: 46px; font-weight: 700; }
      .rk { position: absolute; left: 190px; width: 700px; height: 96px; border-radius: 16px; display: flex; align-items: center;
            padding: 0 34px; box-sizing: border-box; font-size: 46px; font-weight: 600; }
      .rk .tag { margin-left: auto; font-size: 26px; font-weight: 600; letter-spacing: .1em; color: #8a8a8a; border: 2px solid #444;
                 border-radius: 10px; padding: 6px 14px; }

      /* two-month line */
      #line-path { stroke-dasharray: 1400; stroke-dashoffset: 1400; }

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

__HDRS__

      <div id="a-star" class="clip asset" data-start="4.88" data-duration="1.12" data-track-index="1">
        <div id="star-btn" class="ghbtn"><div class="l">__STAR__<span>Star</span></div><div class="sep"></div><div class="n">48.2k</div></div>
        <div id="strike"></div>
        <div class="alabel" style="top: 640px; color: #9a9a9a;">Not the signal</div>
      </div>

      <div id="a-issues" class="clip asset" data-start="6.0" data-duration="2.56" data-track-index="1">
        <div id="iss" class="shot" style="left: 115px; top: 150px; width: 850px;"><img src="assets/issues.png" alt="" /></div>
      </div>

      <div id="a-title" class="clip asset" data-start="8.56" data-duration="2.48" data-track-index="1">
        <div id="title-card" class="page" style="left: 40px; top: 300px; width: 1000px;"><img src="assets/title.png" alt="" /></div>
        <div class="alabel" style="top: 740px;">Carnegie Mellon University</div>
      </div>

      <div id="a-nums" class="clip asset" data-start="11.04" data-duration="4.4" data-track-index="1">
        <div id="n1" class="numcol" style="top: 200px;"><div class="num">6M</div><div class="lbl">SUSPECTED FAKE STARS</div></div>
        <div id="n2" class="numcol" style="top: 540px;"><div class="num">18,000+</div><div class="lbl">REPOS</div></div>
      </div>

      <div id="a-rank" class="clip asset" data-start="15.44" data-duration="2.42" data-track-index="1">
        <div class="rk-title">Who gets fake stars</div>
        <div id="rk-mal" class="rk" style="top: 270px; background: #1c1c1c; color: #6f6f6f;"><span>Malware</span><span class="tag">EXCLUDED</span></div>
        <div id="rk-ai" class="rk" style="top: 386px; background: #ffd60a; color: #111; font-size: 54px; font-weight: 700;">AI / LLM</div>
        <div id="rk-rest">
          <div class="rk" style="top: 502px; background: #1c1c1c; color: #cfcfcf;">Blockchain</div>
          <div class="rk" style="top: 610px; background: #1c1c1c; color: #cfcfcf;">Tools / apps</div>
          <div class="rk" style="top: 718px; background: #1c1c1c; color: #cfcfcf;">Tutorials</div>
        </div>
      </div>

      <div id="a-line" class="clip asset" data-start="22.2" data-duration="4.28" data-track-index="1">
        <svg width="1080" height="960" viewBox="0 0 1080 960" style="position: absolute; left: 0; top: 0;">
          <line x1="140" y1="760" x2="960" y2="760" stroke="#444" stroke-width="3" />
          <line x1="140" y1="200" x2="140" y2="760" stroke="#444" stroke-width="3" />
          <path id="line-path" d="M140 740 C 260 700, 330 330, 470 300 S 640 290, 700 330 S 860 430, 950 470" fill="none" stroke="#ffd60a" stroke-width="10" stroke-linecap="round" />
          <g id="marker">
            <line x1="520" y1="210" x2="520" y2="760" stroke="#e6e6e6" stroke-width="3" stroke-dasharray="14 12" />
            <text x="540" y="240" fill="#fff" font-family="InterHF" font-size="44" font-weight="700">~2 months</text>
          </g>
          <text x="140" y="810" fill="#8a8a8a" font-family="InterHF" font-size="30" font-weight="600">time</text>
          <text x="160" y="190" fill="#8a8a8a" font-family="InterHF" font-size="30" font-weight="600">effect of fake stars</text>
        </svg>
        <div id="line-foot" class="alabel" style="top: 840px; font-size: 32px; color: #9a9a9a;">Short boost, long-term liability</div>
      </div>

      <video id="rec" class="clip" src="assets/rec.mp4" muted playsinline data-start="26.48" data-duration="5.12" data-track-index="1"></video>

      <div id="a-cta" class="clip asset" data-start="31.6" data-duration="__CTADUR__" data-track-index="1">
        <div class="page" style="left: 40px; top: 300px; width: 1000px;"><img src="assets/title.png" alt="" /></div>
      </div>

__CAPS__
    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
      const pop = (sel, t) => tl.fromTo(sel, { opacity: 0, scale: 0.94 }, { opacity: 1, scale: 1, duration: 0.28, ease: "power3.out" }, t);
      const rise = (sel, t) => tl.fromTo(sel, { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }, t);

      pop("#star-btn", 4.88);
      tl.fromTo("#strike", { scaleX: 0 }, { scaleX: 1, duration: 0.25, ease: "power2.out" }, 5.6);
      tl.to("#star-btn", { opacity: 0.45, duration: 0.25 }, 5.6);
      rise("#iss", 6.0);
      rise("#title-card", 8.56);
      pop("#n1", 11.28); pop("#n2", 14.16);
      tl.fromTo("#rk-mal", { opacity: 0 }, { opacity: 1, duration: 0.25 }, 15.92);
      pop("#rk-ai", 16.56);
      tl.fromTo("#rk-rest", { opacity: 0 }, { opacity: 1, duration: 0.3 }, 16.9);
      tl.to("#line-path", { strokeDashoffset: 0, duration: 3.0, ease: "none" }, 22.3);
      tl.fromTo("#marker", { opacity: 0 }, { opacity: 1, duration: 0.25 }, 25.44);
      tl.fromTo("#line-foot", { opacity: 0 }, { opacity: 1, duration: 0.3 }, 25.7);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""

hdrs = "\n".join([
    hdr("h-star", 4.88, 1.12, "THE USUAL SIGNAL"),
    hdr("h-iss", 6.0, 2.56, "GITHUB · UNSLOTHAI/UNSLOTH"),
    hdr("h-paper", 8.56, 9.3, "ICSE 2026 · CARNEGIE MELLON"),
    hdr("h-paper2", 22.2, 4.28, "ICSE 2026 · CARNEGIE MELLON"),
    hdr("h-rec", 26.48, 5.12, "CHECK THE ISSUES"),
    hdr("h-cta", 31.6, round(DUR - 31.6, 3), "ICSE 2026 · CARNEGIE MELLON"),
])
html = (HTML.replace("__DUR__", str(DUR)).replace("__CTADUR__", str(round(DUR - 31.6, 3)))
        .replace("__HDRS__", hdrs).replace("__STAR__", STAR).replace("__CAPS__", cap_html))
open(out, "w").write(html)
for s, d, t, full in caps:
    print(f"{s:6.2f} +{d:4.2f} {'F' if full else 'S'} {t}")
