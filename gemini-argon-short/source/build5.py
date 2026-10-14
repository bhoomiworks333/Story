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

def hl(i, k, x0, y0, x1, y1):
    return (f'<div id="{i}" class="hl" style="left: {k*x0-5:.0f}px; top: {k*y0-3:.0f}px; '
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

POST_K, POST_TOP, SC = 1080 / 857, 300, 1.06
def cam_to(sel, px, py, t, sc=SC, k=POST_K, top=POST_TOP, dur=0.5):
    sx, sy = k * px, top + k * py
    x = max(1080 - sc * 1080, min(0, 540 - sc * sx))
    return f'      tl.to("{sel}", {{ x: {x:.0f}, y: {760 - sc * sy:.0f}, scale: {sc}, duration: {dur}, ease: "power2.inOut" }}, {t});'
def cam_set(sel, px, py, t, **kw):
    return cam_to(sel, px, py, t, dur=0.001, **kw)

CHECK = '<svg width="50" height="50" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
CROSS = '<svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>'
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
      .plans { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; background: #111111; z-index: 2; }
      .pl { position: absolute; top: 470px; width: 470px; height: 720px; border-radius: 28px; border: 4px solid #2e2e2e; box-sizing: border-box; background: #191919; }
      .pl .nm { position: absolute; top: 46px; left: 0; right: 0; text-align: center; font-size: 84px; font-weight: 700; }
      .pl .rw { position: absolute; left: 0; right: 0; text-align: center; }
      .pl .rw .lb { font-size: 40px; font-weight: 600; color: #dcdcdc; line-height: 1.2; margin-bottom: 22px; }
      .ic { display: inline-flex; width: 92px; height: 92px; border-radius: 46px; align-items: center; justify-content: center; }
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
      <div id="k-plans" class="clip plans" data-start="24.58" data-duration="4.3" data-track-index="1">
        <div id="pl-pro" class="pl" style="left: 50px;"><div class="nm">Pro</div>
          <div id="r1p" class="rw" style="top: 220px;"><div class="lb">Argon in the app</div>__OK__</div>
          <div id="r2p" class="rw" style="top: 450px;"><div class="lb">Full coding side</div>__NO__</div></div>
        <div id="pl-ultra" class="pl" style="left: 560px;"><div class="nm">Ultra</div>
          <div id="r1u" class="rw" style="top: 220px;"><div class="lb">Argon in the app</div>__OK__</div>
          <div id="r2u" class="rw" style="top: 450px;"><div class="lb">Full coding side</div>__OK__</div></div>
      </div>
__CAPS__
    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
      const mark = (sel, t) => tl.fromTo(sel, { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: "power2.out" }, t);
      const show = (sel, t) => tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: 0.2 }, t);
      // headers: slow push in, highlight on the word
      tl.fromTo("#p-argon-cam", { scale: 1 }, { scale: 1.12, x: -40, y: -60, duration: 2.4, ease: "none" }, 1.68); mark("#hl-argon", 1.8);
      tl.fromTo("#p-mac-cam", { scale: 1 }, { scale: 1.12, x: -110, y: -50, duration: 2.24, ease: "none" }, 6.48); mark("#hl-mac", 6.6);
      // availability post: camera travels to each sentence as it is said
__POSTCAM__
      mark("#hl-ag1", 8.95); mark("#hl-ag2", 9.25);
      mark("#hl-tg", 11.52);
      mark("#hl-wk1", 14.24); mark("#hl-wk2", 14.55);
      mark("#hl-40", 17.76); mark("#hl-ic", 20.24); mark("#hl-ot", 21.12); mark("#hl-ad", 21.84); mark("#hl-sh", 22.4);
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
pages = "\n".join([
    page("p-argon", "argon", 1.68, 4.08, [("hl-argon", 45, 135, 540, 200)]),
    page("p-mac", "mac", 6.48, 8.72, [("hl-mac", 615, 118, 1055, 182)]),
    page("p-post1", "post", 8.72, 15.44, post_hls1),
    page("p-post2", "post", 16.96, 23.44, post_hls2),
])
postcam = "\n".join([
    cam_set("#p-post1-cam", 428, 455, 8.72),
    cam_to("#p-post1-cam", 428, 575, 10.72),
    cam_to("#p-post1-cam", 428, 595, 14.0, dur=0.3),
    cam_set("#p-post2-cam", 428, 718, 16.96),
])
html = (HTML.replace("__DUR__", str(DUR)).replace("__PAGES__", pages).replace("__POSTCAM__", postcam)
        .replace("__CAPS__", cap_html).replace("__OK__", ic(True)).replace("__NO__", ic(False)))
open(out, "w").write(html)
print(len(caps), "captions")
