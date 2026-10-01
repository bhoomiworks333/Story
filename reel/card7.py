"""Designs asset #7 (base vs fine-tuned answer) and placeholder cards for missing screenshots."""
from PIL import Image, ImageDraw, ImageFont
import os

HERE = os.path.dirname(os.path.abspath(__file__))
F = lambda w, s: ImageFont.truetype(os.path.join(HERE, "fonts", f"Figtree-{w}.ttf"), s)
K = 2  # supersample


def wrap(d, text, font, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= width: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]


def before_after(path, W=950, H=390):
    im = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, W * K - 1, H * K - 1), 22 * K, fill=(14, 16, 20, 255))
    pad = 30 * K
    # question
    q = "What's the reorder level for MS Sheet 2 mm?"
    d.text((pad, 34 * K), "Q", font=F("Bold", 34 * K), fill=(120, 126, 138))
    d.text((pad + 42 * K, 34 * K), q, font=F("SemiBold", 34 * K), fill=(245, 246, 248))
    top, gap = 108 * K, 18 * K
    bw = (W * K - 2 * pad - gap) // 2; bh = H * K - top - pad
    boxes = [
        dict(x=pad, label="BASE MODEL", lc=(150, 155, 166), bg=(28, 31, 38), border=None,
             main=("It depends on your demand, lead time and safety stock.", "Medium", 32, (200, 204, 212)), sub=None),
        dict(x=pad + bw + gap, label="FINE-TUNED", lc=(74, 222, 128), bg=(20, 38, 28), border=(74, 222, 128),
             main=("Reorder at 450 sheets", "Bold", 40, (255, 255, 255)), sub="6-day lead time × 60/day + 90 safety stock"),
    ]
    for b in boxes:
        x0, y0 = b["x"], top
        d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), 16 * K, fill=b["bg"],
                            outline=b["border"], width=3 * K if b["border"] else 0)
        d.text((x0 + 24 * K, y0 + 22 * K), b["label"], font=F("Bold", 22 * K), fill=b["lc"])
        txt, wgt, sz, col = b["main"]; f = F(wgt, sz * K); y = y0 + 64 * K
        for ln in wrap(d, txt, f, bw - 48 * K):
            d.text((x0 + 24 * K, y), ln, font=f, fill=col); y += int(sz * 1.25 * K)
        if b["sub"]:
            fs = F("Medium", 24 * K); y += 10 * K
            for ln in wrap(d, b["sub"], fs, bw - 48 * K):
                d.text((x0 + 24 * K, y), ln, font=fs, fill=(170, 200, 180)); y += int(24 * 1.3 * K)
    im.resize((W, H), Image.LANCZOS).save(path)


def placeholder(path, label, W=950, H=300):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, W - 1, H - 1), 18, fill=(40, 40, 46, 235), outline=(255, 90, 90), width=4)
    d.text((W // 2, H // 2 - 26), "PLACEHOLDER", font=F("Bold", 40), fill=(255, 110, 110), anchor="mm")
    d.text((W // 2, H // 2 + 30), f"screenshot: {label}", font=F("Medium", 32), fill="white", anchor="mm")
    im.save(path)


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "assets"), exist_ok=True)
    before_after(os.path.join(HERE, "assets", "07_before_after.png"))
