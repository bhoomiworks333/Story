"""Gemini 4 Argon short, single view: full-frame speaker, compact cards floating above his head."""
import json, sys

words = json.load(open(sys.argv[1]))
out = sys.argv[2]
DUR = 34.3333
fix = {28: "Antigravity", 36: "Tasks", 67: "OpenTable,", 68: "", 73: "though.", 74: "Pro", 85: "side"}
for i, t in fix.items():
    words[i]["text"] = t
sizes = [4, 2, 4, 3, 3, 2, 2, 3, 3, 3, 3, 4, 2, 3, 3, 5, 7, 3, 4, 2, 2, 2, 1, 1, 3, 2, 2, 3, 3, 2, 2, 3, 3, 3, 8]
assert sum(sizes) == len(words)
groups, i = [], 0
for n in sizes:
    groups.append((i, i + n - 1)); i += n

# on-screen text that repeats the spoken words exactly; its caption is hidden so the line is never read twice
SAY = {29: (9.76, 10.72, "Right inside it."), 44: (14.08, 15.44, "It runs in the background."),
       49: (15.44, 16.96, "You carry on with your day."), 97: (30.8, DUR, "What&rsquo;s the first thing you&rsquo;d use it for?")}
caps = []
for gi, (a, b) in enumerate(groups):
    if a in SAY:
        continue
    text = " ".join(w["text"] for w in words[a:b + 1] if w["text"])
    nxt = words[groups[gi + 1][0]]["start"] if gi + 1 < len(groups) else DUR
    s = words[a]["start"]
    caps.append((round(s, 3), round(min(nxt, words[b]["end"] + 0.25) - s, 3), text))
cap_html = "\n".join(f'      <div id="cap{i}" class="clip cap" data-start="{s}" data-duration="{d}" data-track-index="10">'
                     f'<span class="box">{t}</span></div>' for i, (s, d, t) in enumerate(caps))

K = 1000 / 817   # crop px -> display px for the post-paragraph crops
def hl(i, x0, y0, x1, y1):
    return (f'<div id="{i}" class="hl" style="left: {K*x0-4:.0f}px; top: {K*y0-3:.0f}px; '
            f'width: {K*(x1-x0)+8:.0f}px; height: {K*(y1-y0)+6:.0f}px;"></div>')

def card(i, start, end, img, hls=""):
    return (f'      <div id="{i}" class="clip" data-start="{start}" data-duration="{round(end - start, 3)}" data-track-index="1">'
            f'<div id="{i}-c" class="card"><img src="assets/{img}" alt="" />{hls}</div></div>')

def say(i, start, end, text):
    return (f'      <div id="{i}" class="clip say" data-start="{start}" data-duration="{round(end - start, 3)}" data-track-index="4">'
            f'<div class="t">{text}</div></div>')

CHECK = '<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
CROSS = '<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>'
def ic(ok): return f'<span class="ic" style="background: {"#1f9d55" if ok else "#c0392b"};">{CHECK if ok else CROSS}</span>'

HTML = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Gemini 4 Argon short</title>
    <script src="assets/gsap.min.js"></script>
    <style>
      @font-face { font-family: "InterHF"; src: url("assets/Inter-Medium.otf"); font-weight: 500; }
      @font-face { font-family: "InterHF"; src: url("assets/Inter-SemiBold.otf"); font-weight: 600; }
      @font-face { font-family: "InterHF"; src: url("assets/Inter-Bold.otf"); font-weight: 700; }
      html, body { margin: 0; background: #111111; }
      body { font-family: "InterHF", system-ui, sans-serif; color: #fff; }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; background: #111111; }
      #base { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 1; }
      /* floating card above his head (free space is roughly y 110-520) */
      .card { position: absolute; left: 40px; top: 130px; width: 1000px; border-radius: 24px; overflow: hidden; z-index: 3;
              box-shadow: 0 18px 50px rgba(0,0,0,.55); }
      .card img { display: block; width: 100%; height: auto; }
      .hl { position: absolute; background: rgba(255, 214, 0, 0.55); mix-blend-mode: multiply; border-radius: 4px; transform-origin: 0 50%; }
      .say { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 4; }
      .say .t { position: absolute; left: 70px; right: 70px; top: 180px; text-align: center; background: #fff; color: #000;
                font-size: 68px; font-weight: 700; line-height: 1.15; padding: 26px 34px; border-radius: 22px;
                box-shadow: 0 18px 50px rgba(0,0,0,.45); }
      .plans { position: absolute; left: 40px; top: 130px; width: 1000px; height: 360px; border-radius: 24px; z-index: 3;
               background: rgba(18,18,18,.94); box-shadow: 0 18px 50px rgba(0,0,0,.55); }
      .pl { position: absolute; top: 24px; width: 470px; height: 312px; border-radius: 18px; border: 3px solid #2e2e2e; box-sizing: border-box; }
      .pl .nm { position: absolute; top: 18px; left: 0; right: 0; text-align: center; font-size: 52px; font-weight: 700; }
      .pl .row { position: absolute; left: 28px; right: 28px; display: flex; align-items: center; gap: 18px; font-size: 34px; font-weight: 600; color: #dcdcdc; }
      .ic { flex: none; width: 54px; height: 54px; border-radius: 27px; display: flex; align-items: center; justify-content: center; }
      .cap { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 10; }
      .cap .box { position: absolute; left: 50%; top: 1560px; transform: translate(-50%, -50%); background: #fff; color: #000;
                  font-size: 50px; font-weight: 600; line-height: 1.15; letter-spacing: -0.01em;
                  padding: 14px 26px 16px; border-radius: 14px; white-space: nowrap; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="__DUR__">
      <video id="base" class="clip" src="assets/base.mp4" muted playsinline data-start="0" data-duration="__DUR__" data-track-index="0"></video>
__CARDS__
      <div id="k-plans" class="clip" data-start="24.58" data-duration="4.3" data-track-index="1">
        <div id="k-plans-c" class="plans">
          <div id="pl-pro" class="pl" style="left: 20px;"><div class="nm">Pro</div>
            <div id="r1p" class="row" style="top: 110px;">__OK__<span>Argon in the app</span></div>
            <div id="r2p" class="row" style="top: 205px;">__NO__<span>Full coding side</span></div></div>
          <div id="pl-ultra" class="pl" style="left: 510px;"><div class="nm">Ultra</div>
            <div id="r1u" class="row" style="top: 110px;">__OK__<span>Argon in the app</span></div>
            <div id="r2u" class="row" style="top: 205px;">__OK__<span>Full coding side</span></div></div>
        </div>
      </div>
__SAYS__
__CAPS__
    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
      const pop = (sel, t) => tl.fromTo(sel, { opacity: 0, y: -16, scale: 0.97 }, { opacity: 1, y: 0, scale: 1, duration: 0.28, ease: "power3.out" }, t);
      const mark = (sel, t) => tl.fromTo(sel, { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: "power2.out" }, t);
      const show = (sel, t) => tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: 0.2 }, t);
      pop("#k-key-c", 1.68); pop("#k-mac-c", 6.48); pop("#k-ag-c", 8.72); mark("#hl-ag1", 8.9); mark("#hl-ag2", 9.2);
      pop("#k-tasks-c", 10.72); mark("#hl-tasks", 11.52);
      pop("#k-apps-c", 16.96); mark("#hl-40", 17.76); mark("#hl-ic", 20.24); mark("#hl-ot", 21.12); mark("#hl-ad", 21.84); mark("#hl-sh", 22.4);
      pop("#k-plans-c", 24.58);
      tl.set(["#r1p", "#r1u", "#r2p", "#r2u"], { opacity: 0 }, 24.58);
      show(["#r1p", "#r1u"], 25.36); show(["#r2p", "#r2u"], 26.88);
      tl.to("#pl-ultra", { borderColor: "#ffd60a", duration: 0.2 }, 28.24);
      tl.to("#pl-pro", { opacity: 0.45, duration: 0.2 }, 28.24);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
cards = "\n".join([
    card("k-key", 1.68, 4.08, "keyart.png"),
    card("k-mac", 6.48, 8.72, "macapp.png"),
    card("k-ag", 8.72, 9.76, "antigravity.png", hl("hl-ag1", 328, 33, 777, 56) + hl("hl-ag2", 17, 65, 403, 88)),
    card("k-tasks", 10.72, 14.08, "tasks.png", hl("hl-tasks", 133, 36, 450, 59)),
    card("k-apps", 16.96, 23.44, "apps.png", hl("hl-40", 289, 9, 450, 32) + hl("hl-ic", 510, 9, 590, 32) + hl("hl-ot", 600, 9, 695, 32)
         + hl("hl-ad", 705, 9, 764, 32) + hl("hl-sh", 17, 43, 85, 66)),
])
says = "\n".join([say("s-in", *SAY[29]), say("s-bg", *SAY[44]), say("s-day", *SAY[49]), say("s-q", *SAY[97])])
html = (HTML.replace("__DUR__", str(DUR)).replace("__CARDS__", cards).replace("__SAYS__", says).replace("__CAPS__", cap_html)
        .replace("__OK__", ic(True)).replace("__NO__", ic(False)))
open(out, "w").write(html)
print(len(caps), "captions")
