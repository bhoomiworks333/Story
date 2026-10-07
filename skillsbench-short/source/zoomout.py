import sys, glob, os
from PIL import Image, ImageFilter
src, dst = sys.argv[1], sys.argv[2]
def smooth(a): a = min(max(a, 0), 1); return a * a * (3 - 2 * a)
for i, f in enumerate(sorted(glob.glob(os.path.join(src, "*.png")))):
    t = i / 30
    s1 = 1.7778 * (1 + 0.04 * min(t, 1.8) / 1.8)        # full frame with slow push-in
    p = smooth((t - 1.8) / 0.4)                          # 1.8 -> 2.2 s zoom-out into the bottom half
    s = s1 + (0.8889 - s1) * p
    y1 = 864 - 486 * s1
    x, y = 540 - 640 * s, y1 + (960 - y1) * p
    im = Image.open(f).convert("RGB")
    im = im.resize((round(1440 * s), round(1080 * s)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 40, 2))
    canvas = Image.new("RGB", (1080, 1920), (17, 17, 17))
    canvas.paste(im, (round(x), round(y)))
    canvas.save(os.path.join(dst, f"{i:03d}.png"))
