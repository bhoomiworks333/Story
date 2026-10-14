"""Gemini 4 Argon short v3: full-screen paper cutaways with camera + highlights; captions at the bottom only."""
import json, sys

words = json.load(open(sys.argv[1]))
out = sys.argv[2]
DUR = 34.3333
fix = {28: "Antigravity", 36: "Tasks", 67: "OpenTable,", 68: "", 73: "though.", 74: "Pro", 85: "side"}
for i, t in fix.items():
    words[i]["text"] = t
sizes = [4, 2, 4, 3, 3, 2, 2, 3, 3, 3, 3, 4, 2, 3, 3, 2, 3, 4, 3, 3, 4, 2, 2, 2, 1, 1, 3, 2, 2, 3, 3, 2, 2, 3, 3, 3, 4, 4]
assert sum(sizes) == len(words), (sum(sizes), len(words))
groups, i = [], 0
for n in sizes:
    groups.append((i, i + n - 1)); i += n
caps = []
for gi, (a, b) in enumerate(groups):
    text = " ".join(w["text"] for w in words[a:b + 1] if w["text"])
    nxt = words[groups[gi + 1][0]]["start"] if gi + 1 < len(groups) else DUR
    s = words[a]["start"]
    end = min(nxt, words[b]["end"] + 0.25) if gi + 1 < len(groups) else DUR
    caps.append((round(s, 3), round(end - s, 3), text))
cap_html = "\n".join(f'      <div id="cap{i}" class="clip cap" data-start="{s}" data-duration="{d}" data-track-index="10">'
                     f'<span class="box">{t}</span></div>' for i, (s, d, t) in enumerate(caps))

HUE = {"hl-ag": "rgba(255,214,0,.6)", "hl-tg": "rgba(80,230,140,.55)", "hl-wk": "rgba(255,120,190,.5)",
       "hl-40": "rgba(255,160,40,.6)", "hl-ic": "rgba(80,230,140,.55)", "hl-ot": "rgba(255,120,190,.5)",
       "hl-ad": "rgba(120,190,255,.6)", "hl-sh": "rgba(255,214,0,.6)"}
def hl(i, k, x0, y0, x1, y1):
    bg = next((v for key, v in HUE.items() if i.startswith(key)), "rgba(255,214,0,.55)")
    return (f'<div id="{i}" class="hl" style="background: {bg}; left: {k*x0-5:.0f}px; top: {k*y0-3:.0f}px; '
            f'width: {k*(x1-x0)+10:.0f}px; height: {k*(y1-y0)+6:.0f}px;"></div>')

# pages: (img, source width, top on screen, background)
PG = {"argon": ("argon.png", 1193, 330, "linear-gradient(#e4f3ff, #f7faff)"),
      "mac": ("mac.png", 1180, 380, "#ffffff"),
      "post": ("post.png", 857, 300, "linear-gradient(#e6f4ff, #f8faff)")}
def page(i, key, start, end, hls):
    img, sw, top, bg = PG[key]; k = 1080 / sw
    marks = "".join(hl(h[0], k, *h[1:]) for h in hls)
    return (f'      <div id="{i}" class="clip paper" data-start="{start}" data-duration="{round(end - start, 3)}" data-track-index="1" style="background: {bg};">'
            f'<div id="{i}-cam" class="cam"><div class="pg" style="top: {top}px;"><img src="assets/{img}" alt="" />{marks}</div></div></div>')

def popcard(i, start, end, img, cw, ch, h):
    k = 1000 / cw
    top = 130                               # above his head, as in v1
    mark = hl(h[0], k, *h[1:]).replace('class="hl"', 'class="phl"')
    return (f'      <div id="{i}" class="clip" data-start="{start}" data-duration="{round(end - start, 3)}" data-track-index="1">'
            f'<div id="{i}-c" class="pcard" style="top: {top}px;"><img src="assets/{img}" alt="" />{mark}</div></div>')

POST_K, POST_TOP, SC = 1080 / 857, 300, 1.06
def cam_to(sel, px, py, t, sc=SC, k=POST_K, top=POST_TOP, dur=0.5):
    sx, sy = k * px, top + k * py
    x = max(1080 - sc * 1080, min(0, 540 - sc * sx))
    return f'      tl.to("{sel}", {{ x: {x:.0f}, y: {760 - sc * sy:.0f}, scale: {sc}, duration: {dur}, ease: "power2.inOut" }}, {t});'
def cam_set(sel, px, py, t, **kw):
    return cam_to(sel, px, py, t, dur=0.001, **kw)

CHECK = '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
CROSS = '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>'
def ic(ok): return f'<span class="ic" style="background: {"#1f9d55" if ok else "#c0392b"};">{CHECK if ok else CROSS}</span>'

HTML = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Gemini 4 Argon short</title>
    <script src="assets/gsap.min.js"></script>
    <style>
      @font-face { font-family: "InterHF"; src: url("assets/Inter-SemiBold.otf"); font-weight: 600; }
      @font-face { font-family: "InterHF"; src: url("assets/Inter-Bold.otf"); font-weight: 700; }
      html, body { margin: 0; background: #111111; }
      body { font-family: "InterHF", system-ui, sans-serif; color: #fff; }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; background: #111111; }
      #base { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 1; }
      .paper { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: hidden; z-index: 2; }
      .cam { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform-origin: 0 0; }
      .pg { position: absolute; left: 0; width: 1080px; }
      .pg img { display: block; width: 100%; height: auto; }
      .hl { position: absolute; background: rgba(255, 214, 0, 0.55); mix-blend-mode: multiply; border-radius: 4px; transform-origin: 0 50%; }
      .plans { position: absolute; left: 40px; top: 130px; width: 1000px; height: 390px; border-radius: 26px; z-index: 3;
               background: rgba(18,18,18,.95); box-shadow: 0 20px 60px rgba(0,0,0,.6); transform-origin: 50% 0; }
      .pl { position: absolute; top: 24px; width: 470px; height: 342px; border-radius: 18px; border: 3px solid #2e2e2e; box-sizing: border-box; }
      .pl .nm { position: absolute; top: 20px; left: 0; right: 0; text-align: center; font-size: 56px; font-weight: 700; }
      .pl .rw { position: absolute; left: 28px; right: 28px; display: flex; align-items: center; gap: 18px; }
      .pl .rw .lb { font-size: 36px; font-weight: 600; color: #dcdcdc; }
      .ic { flex: none; display: inline-flex; width: 60px; height: 60px; border-radius: 30px; align-items: center; justify-content: center; }
      .pcard { position: absolute; left: 40px; width: 1000px; border-radius: 24px; overflow: hidden; z-index: 3;
               box-shadow: 0 20px 60px rgba(0,0,0,.6); transform-origin: 50% 0; }
      .pcard img { display: block; width: 100%; height: auto; }
      .phl { position: absolute; background: rgba(255, 214, 0, 0.55); mix-blend-mode: multiply; border-radius: 4px; transform-origin: 0 50%; }
      .cap { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 10; }
      .cap .box { position: absolute; left: 50%; top: 1560px; transform: translate(-50%, -50%); background: #fff; color: #000;
                  font-size: 50px; font-weight: 600; line-height: 1.15; letter-spacing: -0.01em;
                  padding: 14px 26px 16px; border-radius: 14px; white-space: nowrap; box-shadow: 0 6px 24px rgba(0,0,0,.28); }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="__DUR__">
      <video id="base" class="clip" src="assets/base.mp4" muted playsinline data-start="0" data-duration="__DUR__" data-track-index="0"></video>
__PAGES__
      <div id="k-plans" class="clip" data-start="24.58" data-duration="4.3" data-track-index="1"><div id="k-plans-c" class="plans">
        <div id="pl-pro" class="pl" style="left: 20px;"><div class="nm">Pro</div>
          <div id="r1p" class="rw" style="top: 130px;">__OK__<div class="lb">Argon in the app</div></div>
          <div id="r2p" class="rw" style="top: 230px;">__NO__<div class="lb">Full coding side</div></div></div>
        <div id="pl-ultra" class="pl" style="left: 510px;"><div class="nm">Ultra</div>
          <div id="r1u" class="rw" style="top: 130px;">__OK__<div class="lb">Argon in the app</div></div>
          <div id="r2u" class="rw" style="top: 230px;">__OK__<div class="lb">Full coding side</div></div></div>
      </div></div>
__CAPS__
    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
      const mark = (sel, t) => tl.fromTo(sel, { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: "power2.out" }, t);
      const show = (sel, t) => tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: 0.2 }, t);
      // headers: slow push in, highlight on the word
      const pop = (sel, t) => tl.fromTo(sel, { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.35, ease: "back.out(1.8)" }, t);
      pop("#p-argon-c", 1.68); mark("#hl-argon", 2.0);
      pop("#p-mac-c", 6.48); mark("#hl-mac", 6.8);
      pop("#k-plans-c", 24.58);
      // availability post: camera travels to each sentence as it is said

      mark("#hl-ag1", 8.95); mark("#hl-ag2", 9.1); mark("#hl-ag3", 9.3);
      mark("#hl-tg1", 11.52); mark("#hl-tg2", 11.75);
      mark("#hl-wk1", 14.24); mark("#hl-wk2", 14.45); mark("#hl-wk3", 14.65);
      mark("#hl-40a", 17.76); mark("#hl-40b", 17.95); mark("#hl-ic", 20.24); mark("#hl-ot", 21.12); mark("#hl-ad", 21.84); mark("#hl-sh", 22.4);
      // plans
      tl.set(["#r1p", "#r1u", "#r2p", "#r2u"], { opacity: 0 }, 24.58);
      show(["#r1p", "#r1u"], 25.36); show(["#r2p", "#r2u"], 26.88);
      tl.to("#pl-ultra", { borderColor: "#ffd60a", scale: 1.03, duration: 0.25 }, 28.24);
      tl.to("#pl-pro", { opacity: 0.45, duration: 0.25 }, 28.24);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
KA, KM = 1080 / 1193, 1080 / 1180
post_hls1 = [("hl-ag1", 348, 433, 797, 456), ("hl-ag2", 37, 465, 423, 488), ("hl-tg", 153, 561, 470, 584),
             ("hl-wk1", 472, 561, 797, 584), ("hl-wk2", 37, 593, 512, 616)]
post_hls2 = [("hl-40", 309, 687, 470, 710), ("hl-ic", 530, 687, 610, 710), ("hl-ot", 620, 687, 715, 710),
             ("hl-ad", 725, 687, 784, 710), ("hl-sh", 37, 721, 105, 744)]
# highlight boxes in screen px on the held frames
REC1 = [("hl-ag1", 816, 637, 984, 697), ("hl-ag2", 40, 710, 987, 770), ("hl-ag3", 40, 783, 1007, 843),
        ("hl-tg1", 344, 1083, 977, 1143), ("hl-tg2", 40, 1157, 163, 1217),
        ("hl-wk1", 173, 1157, 989, 1217), ("hl-wk2", 40, 1230, 987, 1290), ("hl-wk3", 40, 1305, 270, 1365)]
REC2 = [("hl-40a", 688, 450, 997, 510), ("hl-40b", 40, 523, 152, 583), ("hl-ic", 304, 523, 504, 583),
        ("hl-ot", 529, 523, 769, 583), ("hl-ad", 795, 523, 941, 583), ("hl-sh", 136, 597, 307, 657)]
def rec(i, src, start, end, boxes):
    d = round(end - start, 3)
    marks = "".join(hl(b[0], 1, *b[1:]) for b in boxes)
    return (f'      <video id="{i}" class="clip" src="assets/{src}" muted playsinline data-start="{start}" data-duration="{d}" data-track-index="1" '
            f'style="position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 2;"></video>\n'
            f'      <div id="{i}-hl" class="clip" data-start="{start}" data-duration="{d}" data-track-index="2" '
            f'style="position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 3;">{marks}'
            f'<div style="position: absolute; left: 0; top: 1400px; width: 1080px; height: 520px; '
            f'background: linear-gradient(rgba(244,248,255,0), #f4f8ff 90px);"></div></div>')

pages = "\n".join([
    popcard("p-argon", 1.68, 4.08, "keyart.png", 1090, 330, ("hl-argon", 45 - 30, 135 - 110, 540 - 30, 200 - 110)),
    popcard("p-mac", 6.48, 8.72, "macapp.png", 1080, 215, ("hl-mac", 650 - 20, 118 - 95, 1055 - 20, 182 - 95)),
    rec("p-post1", "post1.mp4", 8.72, 15.44, REC1),
    rec("p-post2", "post2.mp4", 16.96, 23.44, REC2),
])
postcam = "\n".join([
    cam_set("#p-post1-cam", 428, 430, 8.72), cam_to("#p-post1-cam", 428, 470, 8.73, dur=1.95).replace("power2.inOut", "none"),
    cam_to("#p-post1-cam", 428, 565, 10.72, dur=0.3), cam_to("#p-post1-cam", 428, 590, 11.03, dur=2.9).replace("power2.inOut", "none"),
    cam_to("#p-post1-cam", 428, 600, 13.95, dur=0.25), cam_to("#p-post1-cam", 428, 620, 14.21, dur=1.2).replace("power2.inOut", "none"),
    cam_set("#p-post2-cam", 428, 690, 16.96), cam_to("#p-post2-cam", 428, 735, 16.97, dur=6.4).replace("power2.inOut", "none"),
])
html = (HTML.replace("__DUR__", str(DUR)).replace("__PAGES__", pages).replace("__POSTCAM__", postcam)
        .replace("__CAPS__", cap_html).replace("__OK__", ic(True)).replace("__NO__", ic(False)))
open(out, "w").write(html)
print(len(caps), "captions")
