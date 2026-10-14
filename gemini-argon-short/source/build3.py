"""Generate the HyperFrames composition for the Gemini 4 Argon short (vertical source)."""
import json, os, sys

words = json.load(open(sys.argv[1]))
out = sys.argv[2]
assets_dir = os.path.join(os.path.dirname(out), "assets")
DUR = 34.3333

fix = {28: "Antigravity", 36: "Tasks", 67: "OpenTable,", 68: "", 73: "though.", 74: "Pro", 85: "side"}
for i, t in fix.items():
    words[i]["text"] = t

sizes = [4, 2, 4, 3, 3, 2, 2, 3, 3, 3, 3, 4, 2, 3, 3, 5, 7, 3, 4, 2, 2, 2, 1, 1, 3, 2, 2, 3, 3, 2, 2, 3, 3, 3, 8]
assert sum(sizes) == len(words), (sum(sizes), len(words))
groups, i = [], 0
for n in sizes:
    groups.append((i, i + n - 1)); i += n

# Full-frame windows (native vertical footage, no scaling) and on-screen text that repeats the spoken words.
FULL = [(0, 1.68), (4.08, 6.48), (23.44, 24.58), (28.88, DUR)]
SAY = {29: (9.76, 10.72, "Right inside it."), 44: (14.08, 15.44, "It runs in the background."),
       49: (15.44, 16.96, "You carry on with your day."), 97: (30.8, DUR, "What&rsquo;s the first thing you&rsquo;d use it for?")}

def is_full(t):
    return any(a <= t < b for a, b in FULL)

caps = []
for gi, (a, b) in enumerate(groups):
    if a in SAY:            # the text punch already shows these exact words; no duplicate caption
        continue
    text = " ".join(w["text"] for w in words[a:b + 1] if w["text"])
    start, last_end = words[a]["start"], words[b]["end"]
    nxt = words[groups[gi + 1][0]]["start"] if gi + 1 < len(groups) else DUR
    end = min(nxt, last_end + 0.25)
    caps.append((round(start, 3), round(end - start, 3), text, is_full(start)))

CUTS = sorted({x for w in FULL for x in w if 0 < x < DUR})
split_caps = []
for s0, d, t, full in caps:              # split a caption where the layout switches, so it never sits in the wrong place
    e0 = s0 + d
    for c in CUTS:
        if s0 < c < e0:
            split_caps.append((s0, round(c - s0, 3), t, full)); s0, full = c, is_full(c)
    split_caps.append((s0, round(e0 - s0, 3), t, full))
caps = split_caps

cap_html = "\n".join(
    f'      <div id="cap{i}" class="clip cap {"cap-full" if full else ""}" data-start="{s}" data-duration="{d}" '
    f'data-track-index="10"><span class="box">{t}</span></div>' for i, (s, d, t, full) in enumerate(caps))

def asset(i, start, end, file, label, w=1000, top=None):
    """Real image if it has arrived, otherwise a clearly marked placeholder slot."""
    dur = round(end - start, 3)
    if os.path.exists(os.path.join(assets_dir, file)):
        body = f'<div id="{i}-img" class="shot" style="left: {(1080 - w) // 2}px; top: {top or 170}px; width: {w}px;"><img src="assets/{file}" alt="" /></div>'
    else:
        body = f'<div class="ph"><div>ASSET PENDING</div><div class="ph-l">{label}</div></div>'
    return f'      <div id="{i}" class="clip asset" data-start="{start}" data-duration="{dur}" data-track-index="1">{body}</div>'

def say(i, start, end, text, full=False):
    cls = "say-full" if full else "say"
    return (f'      <div id="{i}" class="clip {cls}" data-start="{start}" data-duration="{round(end - start, 3)}" '
            f'data-track-index="4"><div class="t">{text}</div></div>')

def hdr(i, start, end, text):
    return (f'      <div id="{i}" class="clip hdr" data-start="{start}" data-duration="{round(end - start, 3)}" data-track-index="2">'
            f'<div class="t">{text}</div><div class="dot"></div><div class="rule"></div></div>')

CHECK = '<svg width="54" height="54" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
CROSS = '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>'

APPS = [("Instacart", 20.24), ("OpenTable", 21.12), ("Adobe", 21.84), ("Shopify", 22.4)]
def app_tile(k, name):
    x, y = 120 + (k % 2) * 440, 360 + (k // 2) * 250
    logo = f"logo-{name.lower()}.png"
    inner = (f'<img src="assets/{logo}" alt="" style="max-width: 300px; max-height: 120px;" />'
             if os.path.exists(os.path.join(assets_dir, logo)) else f'<span>{name}</span>')
    return f'<div id="app{k}" class="tile" style="left: {x}px; top: {y}px;">{inner}</div>'

HTML = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Gemini 4 Argon short</title>
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
      .shot { position: absolute; border-radius: 16px; overflow: hidden; border: 2px solid #2c2c2c; }
      .shot img { display: block; width: 100%; height: auto; }
      .ph { position: absolute; left: 90px; top: 170px; width: 900px; height: 700px; box-sizing: border-box; border: 4px dashed #555;
            border-radius: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center;
            color: #777; font-size: 34px; font-weight: 700; letter-spacing: .12em; }
      .ph .ph-l { margin-top: 18px; font-size: 44px; color: #bbb; letter-spacing: 0; }
      /* spoken-text punches: static, appear on the word, no animation */
      .say { position: absolute; left: 0; top: 0; width: 1080px; height: 960px; background: #111111; z-index: 4;
             display: flex; align-items: center; justify-content: center; }
      .say .t { width: 900px; text-align: center; font-size: 84px; font-weight: 700; line-height: 1.12; letter-spacing: -0.02em; }
      .say-full { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 4; }
      .say-full .t { position: absolute; left: 80px; right: 80px; top: 200px; text-align: center; background: #fff; color: #000;
                     font-size: 64px; font-weight: 700; line-height: 1.15; padding: 26px 34px; border-radius: 20px; }
      /* apps */
      .apps-n { position: absolute; left: 0; right: 0; top: 160px; text-align: center; font-size: 150px; font-weight: 700; letter-spacing: -0.04em; line-height: 1; }
      .apps-n small { font-size: 60px; font-weight: 600; color: #9b9b9b; letter-spacing: 0; margin-left: 18px; }
      .tile { position: absolute; width: 400px; height: 210px; border-radius: 22px; background: #1c1c1c; border: 2px solid #2e2e2e;
              display: flex; align-items: center; justify-content: center; font-size: 50px; font-weight: 700; }
      /* plans */
      .plan { position: absolute; top: 170px; width: 430px; height: 640px; border-radius: 24px; background: #1a1a1a; border: 3px solid #2e2e2e; }
      .plan .nm { position: absolute; top: 40px; left: 0; right: 0; text-align: center; font-size: 64px; font-weight: 700; }
      .plan .row { position: absolute; left: 34px; right: 34px; font-size: 38px; font-weight: 600; line-height: 1.2; color: #d6d6d6; }
      .plan .ic { position: absolute; left: 0; right: 0; display: flex; justify-content: center; }
      .ic span { width: 84px; height: 84px; border-radius: 42px; display: flex; align-items: center; justify-content: center; }
      .cap { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 10; }
      .cap .box { position: absolute; left: 50%; top: 960px; transform: translate(-50%, -50%); background: #fff; color: #000;
                  font-size: 50px; font-weight: 600; line-height: 1.15; letter-spacing: -0.01em;
                  padding: 14px 26px 16px; border-radius: 14px; white-space: nowrap; }
      .cap-full .box { top: 1560px; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="__DUR__">
      <video id="base" class="clip" src="assets/base.mp4" muted playsinline data-start="0" data-duration="__DUR__" data-track-index="0"></video>
__HDRS__
__ASSETS__
      <div id="a-apps" class="clip asset" data-start="16.96" data-duration="6.33" data-track-index="1">
        <div id="apps-n" class="apps-n">40+<small>apps</small></div>
__TILES__
      </div>
      <div id="a-plans" class="clip asset" data-start="24.58" data-duration="4.15" data-track-index="1">
        <div id="pl-pro" class="plan" style="left: 80px;">
          <div class="nm">Pro</div>
          <div class="row" style="top: 190px;">Argon in the Gemini app</div>
          <div class="ic" style="top: 290px;"><span style="background: #1f9d55;">__CHECK__</span></div>
          <div class="row" style="top: 430px;">Full coding side</div>
          <div class="ic" style="top: 520px;"><span style="background: #c0392b;">__CROSS__</span></div>
        </div>
        <div id="pl-ultra" class="plan" style="left: 570px;">
          <div class="nm">Ultra</div>
          <div class="row" style="top: 190px;">Argon in the Gemini app</div>
          <div class="ic" style="top: 290px;"><span style="background: #1f9d55;">__CHECK__</span></div>
          <div class="row" style="top: 430px;">Full coding side</div>
          <div class="ic" style="top: 520px;"><span style="background: #1f9d55;">__CHECK__</span></div>
        </div>
      </div>
__SAYS__
__CAPS__
    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
      const pop = (sel, t) => tl.fromTo(sel, { opacity: 0, scale: 0.94 }, { opacity: 1, scale: 1, duration: 0.25, ease: "power3.out" }, t);
      const rise = (sel, t) => tl.fromTo(sel, { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }, t);
__ANIMS__
      pop("#apps-n", 18.16);
__TILEANIMS__
      pop("#pl-pro", 24.58);
      tl.fromTo("#pl-ultra", { opacity: 0 }, { opacity: 0.55, duration: 0.25 }, 24.58);
      tl.to("#pl-ultra", { opacity: 1, borderColor: "#ffd60a", scale: 1.03, duration: 0.25, ease: "power2.out" }, 28.24);
      tl.to("#pl-pro", { opacity: 0.5, duration: 0.25 }, 28.24);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""

ASSETS = [("a-key", 1.68, 4.08, "keyart.png", "Argon key art"),
          ("a-mac", 6.48, 8.72, "macapp.png", "Gemini Mac app"),
          ("a-ag", 8.72, 9.76, "antigravity.png", "Antigravity in the Mac app"),
          ("a-tasks", 10.72, 14.08, "tasks.png", "Chat &rarr; Tasks toggle")]
assets_html = "\n".join(asset(*a) for a in ASSETS)
anims = "\n".join(f'      rise("#{a[0]}-img", {a[1]});' for a in ASSETS if os.path.exists(os.path.join(assets_dir, a[3])))
says = "\n".join([say("s-inside", 9.76, 10.72, SAY[29][2]), say("s-bg", 14.08, 15.44, SAY[44][2]),
                  say("s-day", 15.44, 16.96, SAY[49][2]), say("s-q", 30.8, DUR, SAY[97][2], full=True)])
hdrs = "\n".join([hdr("h1", 1.68, 4.08, "GOOGLE · GEMINI 4 ARGON"), hdr("h2", 6.48, 23.29, "GEMINI APP · MAC"),
                  hdr("h3", 24.58, 28.73, "WHO GETS WHAT")])
tiles = "\n".join("        " + app_tile(k, n) for k, (n, _) in enumerate(APPS))
tile_anims = "\n".join(f'      pop("#app{k}", {t});' for k, (_, t) in enumerate(APPS))

html = (HTML.replace("__DUR__", str(DUR)).replace("__HDRS__", hdrs).replace("__ASSETS__", assets_html)
        .replace("__TILES__", tiles).replace("__SAYS__", says).replace("__CAPS__", cap_html)
        .replace("__ANIMS__", anims).replace("__TILEANIMS__", tile_anims)
        .replace("__CHECK__", CHECK).replace("__CROSS__", CROSS))
open(out, "w").write(html)
for s, d, t, full in caps:
    print(f"{s:6.2f} +{d:4.2f} {'F' if full else 'S'} {t}")
