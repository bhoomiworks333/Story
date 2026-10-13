"""Render the transparent PNG overlays for the Java 25 reaction reel (2160x3840)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
W, H = 2160, 3840
INTER_XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"


def emoji(ch, size):
    f = ImageFont.truetype(EMOJI, 109)  # Noto Color Emoji only renders at 109
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((round(im.width * size / im.height), size), Image.LANCZOS)


def run_width(runs, font):
    return sum(font.getlength(t) if isinstance(t, str) else t.width + 12 for t, _ in runs)


def draw_runs(img, d, x, y, runs, font, asc):
    for t, style in runs:
        if isinstance(t, Image.Image):
            img.alpha_composite(t, (int(x + 6), int(y + asc - t.height + 10)))
            x += t.width + 12
            continue
        w = font.getlength(t)
        if style == "hl":
            d.rounded_rectangle([x - 14, y - 4, x + w + 14, y + asc + 34], 26, fill=(255, 214, 10))
        d.text((x, y), t, font=font, fill=(0, 0, 0))
        x += w


def hook():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(INTER_XB, 112)
    asc = font.getmetrics()[0]
    rose = emoji("🥀", 112)
    lines = [
        [("Breaking:", "hl"), (" Java ended the", None)],
        [("public static void main era ", None), (rose, None)],
    ]
    lh, pad_x, pad_y, top = 150, 60, 50, 210
    widths = [run_width(l, font) for l in lines]
    bw = max(widths) + 2 * pad_x
    d.rectangle([(W - bw) / 2, top, (W + bw) / 2, top + len(lines) * lh + 2 * pad_y - 20], fill=(255, 255, 255))
    for i, (l, w) in enumerate(zip(lines, widths)):
        draw_runs(img, d, (W - w) / 2, top + pad_y + i * lh, l, font, asc)
    img.save(OUT / "hook.png")


# minimal Java highlighter: keyword / string / plain
KW = {"public", "class", "static", "void", "String"}
COL = {"kw": (255, 123, 114), "str": (165, 214, 255), "fn": (210, 168, 255), "txt": (230, 237, 243)}


def tokens(line):
    import re
    for m in re.finditer(r'"[^"]*"|\w+|\s+|.', line):
        t = m.group()
        if t.startswith('"'):
            yield t, "str"
        elif t in KW:
            yield t, "kw"
        elif t in {"main", "println"}:
            yield t, "fn"
        else:
            yield t, "txt"


def code_card():
    old = ['public class Main {',
           '    public static void main(String[] args) {',
           '        System.out.println("Hello");',
           '    }',
           '}']
    new = ['void main() {',
           '    IO.println("Hello");',
           '}']
    cw, ch = 1980, 1200
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, cw - 1, ch - 1], 48, fill=(13, 17, 23, 245))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):  # window dots
        d.ellipse([50 + i * 56, 44, 86 + i * 56, 80], fill=c)
    font = ImageFont.truetype(MONO_B, 64)
    label = ImageFont.truetype(INTER_XB, 64)
    lh, x0 = 88, 70

    def block(y, title, mark, lines, struck):
        d.text((x0, y), title, font=label, fill=(139, 148, 158))
        card.alpha_composite(emoji(mark, 64), (int(x0 + label.getlength(title) + 20), y + 6))
        y += 110
        for ln in lines:
            x = x0
            for t, k in tokens(ln):
                d.text((x, y), t, font=font, fill=COL[k] + ((150,) if struck else ()))
                x += font.getlength(t)
            y += lh
        return y

    y = block(120, "Old", "❌", old, struck=True)
    d.line([x0, y + 30, cw - x0, y + 30], fill=(48, 54, 61), width=3)
    y = block(y + 70, "New (Java 25)", "✅", new, struck=False)
    card = card.crop((0, 0, cw, y + 50))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, cw - 1, card.height - 1], 48, outline=(48, 54, 61), width=4)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.alpha_composite(card, ((W - cw) // 2, 2260))
    img.save(OUT / "code.png")


def muscle():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(INTER_XB, 128)
    skull = emoji("💀", 128)
    y = 2560
    for text, mark in [("30 years of", None), ("muscle memory", skull)]:
        w = font.getlength(text) + (mark.width + 30 if mark else 0)
        x = (W - w) / 2
        d.text((x, y), text, font=font, fill="white", stroke_width=12, stroke_fill="black")
        if mark:
            img.alpha_composite(mark, (int(x + font.getlength(text) + 30), y + 20))
        y += 170
    img.save(OUT / "muscle.png")


hook(); code_card(); muscle()
