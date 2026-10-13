#!/usr/bin/env python3
"""Garba outsiders reel (Reel 2): cut list, base video, audio, HyperFrames composition and SRT.

    NODE_PATH=$(npm root -g) node snap_assets.js       # pop-ups -> hf/assets/*.png
    python3 gen.py <take.mp4>                          # hf/assets/base.mp4, build/audio.wav, hf/index.html, srt
    cd hf && HYPERFRAMES_BROWSER_PATH=... hyperframes render -o ../build/silent.mp4 --fps 30
    python3 gen.py <take.mp4> --mux                    # -> output/garba_outsiders_reel.mp4

Same look as Reel 1: full frame, no zoom, white-box captions (2-4 words), Reel 1 style pop-ups.
Dead air between lines is cut (jump cuts). All times below are seconds in the original take.
"""
import html, os, subprocess, sys, wave
import numpy as np

SRC = sys.argv[1]
MUX = '--mux' in sys.argv
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
BUILD = os.path.join(HERE, 'build')
os.makedirs(BUILD, exist_ok=True)
FPS = 30

# Kept ranges of the take. Speech was located from pauses in the audio and mouth movement; gaps
# shorter than ~0.45 s stay in, longer ones are cut.
KEEP = [
    (2.40, 4.60),    # typing, phone buzzes, he picks it up and reads
    (7.20, 8.62),    # "Kal raat white car kiski thi?"
    (9.17, 11.05),   # "...achha." + eye-roll (kept whole: that's the deadpan)
    (13.46, 16.72),  # Garba ka teesra din hai aur group mein yahi chal raha hai
    (16.98, 22.69),  # Dekho na, gate pe ek guard hai ... jaa rahe hain
    (22.92, 27.80),  # Register mein likha hai 'Rahul, guest'. Ab kaunsa Rahul? Kiske ghar?
    (28.41, 36.90),  # Guard ko bhi kya bolein yaar, DJ itna loud hai ... detective ban jaata hai
    (37.25, 42.15),  # Aapki society mein garba pe bahar wale aate hain? + 1.5 s hold
]
KEEP = [(round(a * FPS) / FPS, round(b * FPS) / FPS) for a, b in KEEP]


def out_t(t):
    """Map a take time to the output timeline."""
    acc = 0.0
    for a, b in KEEP:
        if t < a:
            return acc
        if t <= b:
            return acc + t - a
        acc += b - a
    return acc


DUR = round(sum(b - a for a, b in KEEP), 4)

CAPS = [
    (7.37, 7.95, "Kal raat white car"),
    (7.95, 8.62, "kiski thi?"),
    (9.29, 10.90, "...achha."),
    (13.54, 14.85, "Garba ka teesra din hai"),
    (14.85, 15.75, "aur group mein yahi"),
    (15.75, 16.72, "chal raha hai."),
    (17.10, 17.75, "Dekho na,"),
    (17.96, 18.90, "gate pe ek guard hai,"),
    (18.90, 20.00, "ek register hai,"),
    (20.28, 21.10, "aur raat bhar log"),
    (21.10, 21.80, "aa rahe hain,"),
    (21.80, 22.69, "jaa rahe hain."),
    (23.04, 24.10, "Register mein likha hai"),
    (24.10, 25.20, "'Rahul, guest'."),
    (25.42, 26.55, "Ab kaunsa Rahul?"),
    (26.55, 27.80, "Kiske ghar?"),
    (28.53, 29.10, "Guard ko bhi"),
    (29.10, 30.00, "kya bolein yaar,"),
    (30.12, 31.40, "DJ itna loud hai,"),
    (31.40, 33.10, "wo kya poochega."),
    (33.46, 34.40, "Aur agle din poora"),
    (34.40, 35.30, "WhatsApp group hi"),
    (35.30, 36.90, "deactivate ban jaata hai."),
    (37.37, 38.40, "Aapki society mein"),
    (38.40, 39.00, "garba pe"),
    (39.00, 40.65, "bahar wale aate hain?"),
]

# (id, png, take start, take end, centre x, centre y, scale)
POPS = [
    ("p-wa1", "wa1.png", 3.55, 8.62, 540, 230, 1.0),            # as he reads, until he says it
    ("p-nb0", "nb0.png", 15.05, 17.75, 540, 100, 0.95),  # the flood: banners drop in one after another
    ("p-nb1", "nb1.png", 15.33, 17.75, 540, 188, 0.95),
    ("p-nb2", "nb2.png", 15.61, 17.75, 540, 276, 0.95),
    ("p-nb3", "nb3.png", 15.89, 17.75, 540, 364, 0.95),
    ("p-nb4", "nb4.png", 16.17, 17.75, 540, 452, 0.95),
    ("p-reg", "register.png", 23.95, 27.80, 540, 1185, 0.90),   # on "Rahul, guest"
    ("p-kaun", "kaunsa.png", 25.45, 27.80, 540, 250, 1.0),      # on "kaunsa Rahul"
    ("p-det", "detect.png", 35.30, 36.90, 540, 210, 1.0),       # on "deactivate", small, top
    ("p-aap", "aapki.png", 37.40, 99, 540, 250, 1.0),           # holds to the end
]


def q(t):
    return round(t * FPS) / FPS


def run(cmd):
    subprocess.run(cmd, check=True)


def vibration(path, dur, bursts, sr=48000):
    """Phone-on-table buzz: ~175 Hz motor tone with rattle harmonics, in bursts."""
    t = np.arange(int(dur * sr)) / sr
    motor = np.sign(np.sin(2 * np.pi * 175 * t)) * 0.5 + np.sin(2 * np.pi * 350 * t) * 0.3
    rattle = np.random.default_rng(3).normal(0, 1, t.size) * (np.sin(2 * np.pi * 175 * t) > 0.6) * 0.35
    env = np.zeros_like(t)
    for a, b in bursts:
        m = (t >= a) & (t < b)
        env[m] = np.minimum(1, np.minimum((t[m] - a) / 0.02, (b - t[m]) / 0.03))
    y = (motor + rattle) * env * 0.5
    with wave.open(path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


def denoise(src, dst, sr=48000):
    """Room-noise reduction using the 2.5 s of silence at the end of the take as the noise profile
    (about -16 dB on the noise floor, voice level within 1 dB)."""
    import noisereduce as nr
    def pcm(args):
        raw = subprocess.run(['ffmpeg', '-v', 'error', *args, '-ac', '1', '-ar', str(sr), '-f', 's16le', '-'],
                             capture_output=True, check=True).stdout
        return np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    y = nr.reduce_noise(y=pcm(['-i', src]), sr=sr, y_noise=pcm(['-ss', '40.9', '-t', '2.5', '-i', SRC]),
                        stationary=True, prop_decrease=0.85, n_std_thresh_stationary=1.5)
    with wave.open(dst, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())


if not MUX:
    # base video + audio: trim each kept range, 12 ms audio fades at every cut so the jumps don't click
    parts, labels = [], []
    for i, (a, b) in enumerate(KEEP):
        parts.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];"
                     f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,"
                     f"afade=t=out:st={b - a - 0.012:.3f}:d=0.012[a{i}];")
        labels.append(f"[v{i}][a{i}]")
    fc = "".join(parts) + "".join(labels) + f"concat=n={len(KEEP)}:v=1:a=1[v][a]"
    run(['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-filter_complex', fc, '-map', '[v]', '-c:v', 'libx264', '-crf', '16',
         '-preset', 'medium', '-g', '30', '-keyint_min', '30', '-pix_fmt', 'yuv420p', os.path.join(HERE, 'hf', 'assets', 'base.mp4'),
         '-map', '[a]', '-ar', '48000', os.path.join(BUILD, 'speech.wav')])
    # buzz while the phone sits on the stand; stops as he lifts it (take 3.4 s -> output 1.0 s)
    denoise(os.path.join(BUILD, 'speech.wav'), os.path.join(BUILD, 'speech_dn.wav'))
    vib = os.path.join(BUILD, 'vibration.wav')
    vibration(vib, 1.2, [(0.0, 0.42), (0.62, 1.0)])
    run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(BUILD, 'speech_dn.wav'), '-i', vib, '-filter_complex',
         "[1:a]aresample=48000,volume=-6dB[b];[0:a][b]amix=inputs=2:normalize=0:duration=first,"
         "loudnorm=I=-16:TP=-1.5:LRA=11[a]", '-map', '[a]', '-ar', '48000', os.path.join(BUILD, 'audio.wav')])

    caps = "\n".join(
        f'      <div id="cap{i}" class="clip cap" data-start="{q(out_t(a)):.4f}" '
        f'data-duration="{q(out_t(b)) - q(out_t(a)):.4f}" data-track-index="10"><span class="box">{html.escape(t)}</span></div>'
        for i, (a, b, t) in enumerate(CAPS))
    pops, anims = [], []
    for pid, png, a, b, cx, cy, sc in POPS:
        s, e = q(out_t(a)), q(min(out_t(b), DUR))
        pops.append(f'      <div id="w-{pid}" class="clip pop" data-start="{s:.4f}" data-duration="{e - s:.4f}" data-track-index="5">'
                    f'<img id="{pid}" src="assets/{png}" style="left:{cx}px;top:{cy}px;'
                    f'transform:translate(-50%,-50%) scale({sc})" alt="" /></div>')
        anims.append(f'pop("#{pid}", {s:.4f}, {sc});')
        if e < DUR:
            anims.append(f'out("#{pid}", {e - 0.12:.4f}, {sc});')
    page = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Garba outsiders reel</title>
    <script src="assets/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "InterHF"; src: url("assets/Inter-SemiBold.otf"); font-weight: 600; }}
      html, body {{ margin: 0; background: #000; }}
      body {{ font-family: "InterHF", system-ui, sans-serif; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #base {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
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
      <video id="base" class="clip" src="assets/base.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="0"></video>
{chr(10).join(pops)}
{caps}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      const tf = (s) => ({{ xPercent: -50, yPercent: -50, scale: s }});
      const pop = (sel, t, s) => tl.fromTo(sel, {{ ...tf(s * 0.5), opacity: 0 }},
        {{ ...tf(s), opacity: 1, duration: 0.22, ease: "back.out(1.8)", immediateRender: false }}, t);
      const out = (sel, t, s) => tl.to(sel, {{ scale: s * 0.85, opacity: 0, duration: 0.12, ease: "power2.in" }}, t);
      {(chr(10) + '      ').join(anims)}
      tl.set({{}}, {{}}, {DUR});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    open(os.path.join(HERE, 'hf', 'index.html'), 'w').write(page)

    def ts(t):
        ms = round(t * 1000)
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    with open(os.path.join(ROOT, 'output', 'garba_outsiders_reel.srt'), 'w') as f:
        f.write("".join(f"{i}\n{ts(out_t(a))} --> {ts(out_t(b))}\n{t}\n\n" for i, (a, b, t) in enumerate(CAPS, 1)))
    print(f"duration {DUR:.2f} s; DJ line 'DJ itna loud hai' at output {out_t(30.12):.2f}-{out_t(31.40):.2f} s")
else:
    final = os.path.join(ROOT, 'output', 'garba_outsiders_reel.mp4')
    run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(BUILD, 'silent.mp4'), '-i', os.path.join(BUILD, 'audio.wav'),
         '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final])
    run(['ffmpeg', '-v', 'error', '-y', '-i', final, '-c:v', 'libx264', '-crf', '23', '-preset', 'medium', '-c:a', 'copy',
         '-movflags', '+faststart', os.path.join(ROOT, 'output', 'garba_outsiders_reel_preview.mp4')])
    print('wrote', final)
