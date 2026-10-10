#!/usr/bin/env python3
"""Writes hf/index.html, the HyperFrames composition for the garba chanda reel.

    python3 gen_hf.py
    cd hf && hyperframes render -o ../../../output/garba_chanda_reel_hf_silent.mp4

No zoom and no hands crop: the take plays as shot. Times are seconds in the take.
Captions follow the approved spec: black Inter SemiBold on a white rounded box, 2-4 words, hard cuts.
"""
import html, os

HERE = os.path.dirname(os.path.abspath(__file__))
DUR = 31.95
FPS = 30

# Caption timing comes from pauses and sibilant anchors in the audio (cash 6.5, GPay 7.8,
# paanch sau 12.6, Notes 17.6, paisa 22.3, bas kiska 24.1); there is no transcript.
CAPS = [
    (0.90, 1.85, "...ek second."),
    (1.85, 3.10, "Ye kisne diya tha?"),
    (3.20, 4.40, "Nahi, seriously."),
    (4.50, 5.30, "Garba ka chanda"),
    (5.30, 6.00, "aata hai na,"),
    (6.00, 7.15, "koi cash deta hai,"),
    (7.15, 8.45, "koi GPay karta hai,"),
    (8.45, 9.55, "koi bolta hai..."),
    (9.55, 11.05, "\"haan haan, baad mein\""),
    (11.25, 11.95, "Aur mujhe sach mein"),
    (11.95, 12.50, "nahi pata"),
    (12.50, 13.35, "ye paanch sau"),
    (13.35, 14.30, "kiska hai."),
    (14.55, 14.90, "List?"),
    (14.90, 15.75, "Wo kisi uncle ke"),
    (15.75, 16.85, "phone mein hai."),
    (16.85, 18.15, "Notes mein."),
    (18.15, 19.15, "Jo khud bhool"),
    (19.15, 20.50, "gaye honge"),
    (20.50, 21.90, "kahan save kiya."),
    (22.05, 23.90, "Matlab paisa aa gaya..."),
    (23.95, 24.75, "bas kiska aaya,"),
    (24.75, 25.60, "ye nahi pata."),
    (25.85, 26.95, "Aapke yahan ye kaun"),
    (26.95, 28.15, "collect karta hai?"),
    (28.25, 28.95, "Tag karo,"),
    (28.95, 29.60, "dekhte hain"),
    (29.60, 30.90, "unka kya haal hai."),
]

# (id, png, start, end, centre x, centre y, scale, rotation)
POPS = [
    ("p-cash", "cash.png", 6.30, 7.60, 540, 270, 1.0, 0),
    ("p-gpay", "gpay.png", 7.60, 9.10, 540, 250, 1.0, 0),
    ("p-chat", "chat.png", 9.55, 11.05, 520, 260, 1.0, 0),
    ("p-q500", "q500.png", 12.55, 14.35, 540, 270, 1.0, 0),
    ("p-notes", "notes.png", 17.25, 21.80, 540, 1060, 0.95, -3),
    ("p-tag", "tag.png", 25.95, DUR, 540, 270, 1.0, 0),
]


def q(t):
    return round(t * FPS) / FPS


caps = "\n".join(
    f'      <div id="cap{i}" class="clip cap" data-start="{q(a):.4f}" data-duration="{q(b) - q(a):.4f}" '
    f'data-track-index="10"><span class="box">{html.escape(t)}</span></div>'
    for i, (a, b, t) in enumerate(CAPS))

pops, anims = [], []
for pid, png, a, b, cx, cy, sc, rot in POPS:
    pops.append(
        f'      <div id="w-{pid}" class="clip pop" data-start="{q(a):.4f}" data-duration="{q(b) - q(a):.4f}" data-track-index="5">'
        f'<img id="{pid}" src="assets/{png}" style="left:{cx}px;top:{cy}px;'
        f'transform:translate(-50%,-50%) rotate({rot}deg) scale({sc})" alt="" /></div>')
    # pop-in, and a quick shrink-fade out unless it holds to the end
    anims.append(f'pop("#{pid}", {q(a):.4f}, {sc}, {rot});')
    if b < DUR:
        anims.append(f'out("#{pid}", {q(b) - 0.12:.4f}, {sc}, {rot});')

page = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Garba chanda reel</title>
    <script src="assets/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "InterHF"; src: url("assets/Inter-SemiBold.otf"); font-weight: 600; }}
      html, body {{ margin: 0; background: #000; }}
      body {{ font-family: "InterHF", system-ui, sans-serif; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #take {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      .pop {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 5; }}
      .pop img {{ position: absolute; display: block; }}
      .cap {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 10; }}
      .cap .box {{ position: absolute; left: 50%; top: 1500px; transform: translate(-50%, -50%); background: #fff; color: #000;
                  font-size: 50px; font-weight: 600; line-height: 1.15; letter-spacing: -0.01em;
                  padding: 14px 26px 16px; border-radius: 14px; white-space: nowrap; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{DUR}">
      <video id="take" class="clip" src="assets/take.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="0"></video>
{chr(10).join(pops)}
{caps}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      const tf = (s, r) => ({{ xPercent: -50, yPercent: -50, rotation: r, scale: s }});
      const pop = (sel, t, s, r) => tl.fromTo(sel, {{ ...tf(s * 0.5, r), opacity: 0 }},
        {{ ...tf(s, r), opacity: 1, duration: 0.22, ease: "back.out(1.8)", immediateRender: false }}, t);
      const out = (sel, t, s, r) => tl.to(sel, {{ scale: s * 0.85, opacity: 0, duration: 0.12, ease: "power2.in" }}, t);
      {chr(10).join('      ' + x for x in anims).lstrip()}
      tl.set({{}}, {{}}, {DUR});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open(os.path.join(HERE, "hf", "index.html"), "w").write(page)
print("wrote hf/index.html:", len(CAPS), "captions,", len(POPS), "pop-ups")


def ts(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


srt = os.path.join(HERE, "..", "..", "output", "garba_chanda_reel.srt")
with open(srt, "w") as f:
    f.write("".join(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n" for i, (a, b, t) in enumerate(CAPS, 1)))
