#!/usr/bin/env python3
"""Cut list -> 1080x1920 short. Run: python3 -I build.py <scratch> <src> <billboard_img> <outdir>"""
import sys, os, subprocess, json
from PIL import Image, ImageDraw, ImageFont

S, SRC, BB, OUT = sys.argv[1:5]
W, H, FPS = 1080, 1920, 30
P = os.path.join(S, 'pieces'); os.makedirs(P, exist_ok=True); os.makedirs(OUT, exist_ok=True)
GRADE = "eq=contrast=1.06:saturation=1.07:gamma=0.98"

# (src_in, src_out, zoom, face_x, face_y)  zoom='push' = slow push-in
CUTS = [
    (38.48, 38.86, 1.12, .73, .30),   # A  "only"
    (39.28, 42.98, 1.12, .73, .30),   # A  "one percent ... ERP system"
    (16.60, 18.60, 1.00, .80, .30),   # B  "India has more than seventy"
    (19.20, 20.37, 1.00, .80, .30),   # B  "to eighty lakhs"
    (20.84, 22.15, 1.00, .80, .37),   # B  "SMEs right now"  (billboard enters on "right now")
    (105.28, 107.45, 1.00, .62, .38), # C  "And Zoho is betting big on it" (under billboard)
    (56.28, 59.64, 1.00, .63, .36),   # D  "when ERP is implemented at any organization"
    (60.76, 62.36, 1.15, .62, .35),   # D  "it becomes a data foundation"
    (64.88, 65.74, 1.00, .65, .36),   # E  "they can actually"
    (66.40, 68.06, 1.15, .65, .36),   # E  "implement any AI solution"
    (68.50, 69.40, 1.15, .65, .36),   # E  "based on their data"
    (101.58, 102.17, 1.00, .62, .40), # F  "ERP"
    (102.79, 103.74, 1.20, .62, .40), # F  "is the foundation"
    (133.38, 135.62, 1.00, .66, .33), # G  "Zoho ERP is a proprietary solution" (under billboard)
    (135.95, 137.68, 1.00, .66, .33), # G  "it's a subscription-based system"
    (138.40, 139.02, 1.00, .62, .35), # H  "But the future"
    (139.55, 141.62, 1.12, .62, .35), # H  "from what I see is for open source"
    (158.44, 162.64, 1.00, .62, .36), # I  "now that AI is so powerful ... any level that you want"
    (187.28, 190.75, 'push', .62, .37),# J "SMEs of India need to digitally transform themselves"
]

# output-timeline mapping
starts, t = [], 0.0
for c in CUTS:
    starts.append(t); t += c[1] - c[0]
TOTAL = t
def otime(src):
    for (a, b, *_), st in zip(CUTS, starts):
        if a - 0.05 <= src <= b + 0.05:
            return st + min(max(src - a, 0), b - a)
    raise ValueError(src)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(r.stderr[-2000:]); sys.exit(1)

# ---------- pieces ----------
lst = []
for i, (a, b, z, fx, fy) in enumerate(CUTS):
    d = b - a
    if z == 'push':
        n = round(d * FPS)
        zw, zh = W * 2, H * 2
        vf = (f"scale={zw}:{zh}:flags=lanczos,"
              f"zoompan=z='1+0.08*on/{n}':x='max(0,min(iw-iw/zoom,{fx}*iw-iw/zoom/2))':"
              f"y='max(0,min(ih-ih/zoom,{fy}*ih-ih/zoom/2))':d=1:s={W}x{H}:fps={FPS},{GRADE}")
    else:
        sw, sh = round(W * z / 2) * 2, round(H * z / 2) * 2
        x = max(0, min(sw - W, round(fx * sw - W / 2)))
        y = max(0, min(sh - H, round(fy * sh - H / 2)))
        vf = f"scale={sw}:{sh}:flags=lanczos,crop={W}:{H}:{x}:{y},{GRADE},fps={FPS}"
    af = f"afade=t=in:d=0.012,afade=t=out:st={d-0.015:.3f}:d=0.015"
    f = os.path.join(P, f"p{i:02d}.mkv")
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-i", SRC, "-t", f"{d:.3f}",
         "-vf", vf, "-af", af, "-c:v", "libx264", "-crf", "12", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", f])
    lst.append(f"file '{f}'")
open(os.path.join(P, 'list.txt'), 'w').write('\n'.join(lst) + '\n')

# ---------- billboard b-roll ----------
img = Image.open(BB).convert('RGB'); iw, ih = img.size
img.save(os.path.join(P, 'bb.png'))
# 1) pan left->right across the hoarding: from "right now" to end of C
b1_in = otime(21.45); b1_out = starts[6]
d1 = b1_out - b1_in
cw = round(ih * W / H)              # 9:16 window inside the photo
span = iw - cw
x_end = 60
pan = (f"crop={cw}:{ih}:'{span}-({span}-{x_end})*(0.5-0.5*cos(PI*min(t/{d1:.3f},1)))':0,"
       f"scale={W}:{H}:flags=lanczos,{GRADE},format=yuv420p")
run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", os.path.join(P, 'bb.png'),
     "-t", f"{d1:.3f}", "-vf", pan, "-c:v", "libx264", "-crf", "12", os.path.join(P, 'bb1.mp4')])
# 2) slow push on the "Zoho ERP" logo for G
b2_in = starts[13]; d2 = CUTS[13][1] - CUTS[13][0]
n2 = round(d2 * FPS)
tw2 = 330; th2 = round(tw2 * H / W)   # tight 9:16 window on the logo
push = (f"crop={tw2}:{th2}:110:0,scale={W*2}:{H*2}:flags=lanczos,"
        f"zoompan=z='1+0.06*on/{n2}':x='iw/2-iw/zoom/2':y='ih*0.41-ih/zoom*0.41':d=1:s={W}x{H}:fps={FPS},"
        f"{GRADE},format=yuv420p")
run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", os.path.join(P, 'bb.png'),
     "-frames:v", str(n2), "-vf", push, "-c:v", "libx264", "-crf", "12", os.path.join(P, 'bb2.mp4')])

# ---------- captions ----------
# (src_start, src_end, text, size)
CAPS = [
    (38.48, 40.05, "Only 1%", 92),
    (40.06, 41.91, "of the organizations", 60),
    (41.92, 42.98, "use an ERP system", 60),
    (16.60, 17.77, "India has more than", 60),
    (17.98, 20.37, "70–80 lakh", 60),
    (20.84, 22.15, "SMEs right now", 60),
    (105.28, 107.45, "And Zoho is betting big on it", 56),
    (56.28, 58.66, "When ERP is implemented", 60),
    (58.67, 59.64, "at any organization", 60),
    (60.76, 62.36, "it becomes a data foundation", 58),
    (64.88, 65.74, "they can actually", 60),
    (66.40, 68.06, "implement any AI solution", 60),
    (68.50, 69.40, "based on their data", 60),
    (101.58, 103.74, "ERP is the foundation", 64),
    (133.38, 135.62, "Zoho ERP is proprietary", 60),
    (135.95, 137.68, "subscription-based", 60),
    (138.40, 139.02, "But the future", 60),
    (139.55, 140.40, "from what I see", 60),
    (140.50, 141.62, "is open source", 64),
    (158.44, 160.15, "Now that AI is so powerful", 58),
    (160.16, 161.40, "you can take it", 60),
    (161.41, 162.64, "to any level you want", 60),
    (187.28, 188.54, "SMEs of India", 62),
    (188.55, 189.69, "need to digitally", 58),
    (189.70, 190.75, "transform themselves", 58),
]
CY = int(H * 0.66)
cap_inputs, cap_filters = [], []
srt = []
def ts(x):
    ms = int(round(x * 1000)); return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
for k, (a, b, text, size) in enumerate(CAPS):
    size = round(size * 1.2)
    font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", size)
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    l, tp, r, bt = dr.textbbox((0, 0), text, font=font)
    tw, th = r - l, bt - tp
    px, py = int(size * 0.42), int(size * 0.30)
    x0 = (W - tw) // 2 - px; y0 = CY - th // 2 - py
    dr.rounded_rectangle([x0, y0, x0 + tw + 2 * px, y0 + th + 2 * py], radius=int(size * 0.32), fill=(255, 255, 255, 245))
    dr.text(((W - tw) // 2 - l, CY - th // 2 - tp), text, font=font, fill=(17, 17, 17, 255))
    fp = os.path.join(P, f"c{k:02d}.png"); im.save(fp)
    oa, ob = otime(a), otime(b)
    if k + 1 < len(CAPS):  # never overlap the next caption
        ob = min(ob, otime(CAPS[k + 1][0]) - 0.001)
    cap_inputs += ["-i", fp]
    cap_filters.append((oa, ob))
    srt.append(f"{k+1}\n{ts(oa)} --> {ts(ob)}\n{text}\n")
open(os.path.join(OUT, 'short.srt'), 'w').write('\n'.join(srt))

# ---------- assemble ----------
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(P, 'list.txt'),
     "-c", "copy", os.path.join(P, 'base.mkv')])

AUD = "highpass=f=70,afftdn=nr=6:nf=-35,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=1"
# loudness pass 1
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", os.path.join(P, 'base.mkv'), "-af",
                    AUD + ",loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True)
j = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
LN = (f"loudnorm=I=-14:TP=-1.5:LRA=7:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
      f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")

fc = [f"[1:v]setpts=PTS-STARTPTS+{b1_in:.3f}/TB[b1]",
      f"[2:v]setpts=PTS-STARTPTS+{b2_in:.3f}/TB[b2]",
      "[0:v][b1]overlay=eof_action=pass[v1]",
      "[v1][b2]overlay=eof_action=pass[v2]"]
last = "v2"
for k, (oa, ob) in enumerate(cap_filters):
    fc.append(f"[{last}][{k+3}:v]overlay=0:0:enable='between(t,{oa:.3f},{ob:.3f})'[c{k}]")
    last = f"c{k}"
fc.append(f"[0:a]{AUD},{LN},aresample=48000,afade=t=out:st={TOTAL-0.12:.3f}:d=0.12[a]")
final = os.path.join(OUT, 'short_final.mp4')
run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(P, 'base.mkv'),
     "-i", os.path.join(P, 'bb1.mp4'), "-i", os.path.join(P, 'bb2.mp4')] + cap_inputs +
    ["-filter_complex", ';'.join(fc), "-map", f"[{last}]", "-map", "[a]",
     "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
     "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", final])
print(json.dumps({"total": round(TOTAL, 2), "bb1": [round(b1_in, 2), round(d1, 2)],
                  "bb2": [round(b2_in, 2), round(d2, 2)], "starts": [round(s, 2) for s in starts]}))
