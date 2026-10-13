"""Animated overlays for the Java 25 reaction reel (2160x3840, 30 fps).

Writes raw RGBA overlay frames to stdout; render.sh pipes them into ffmpeg.
Beats are synced to the reaction: hand leaves forehead ~3.0 s, hand over
mouth ~3.4 s, fist to cheek ~5.8 s.
"""
import math
import re
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 2160, 3840, 30
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 9.9
INTER_XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
INTER_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

# timeline (seconds)
OLD_IN, STRIKE, OLD_OUT, OLD_GONE = 0.25, 2.25, 2.8, 3.1
NEW_IN, NEW_OUT, NEW_GONE = 3.2, 5.55, 5.75
MEM_IN = 5.85


def emoji(ch, size):
    f = ImageFont.truetype(EMOJI, 109)  # Noto Color Emoji only renders at 109
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((round(im.width * size / im.height), size), Image.LANCZOS)


def ease_out_back(t, s=2.2):
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def clamp(t):
    return max(0.0, min(1.0, t))


# ---------- hook (static, whole clip) ----------
def make_hook():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(INTER_XB, 112)
    asc = font.getmetrics()[0]
    rose = emoji("🥀", 112)
    lines = [[("Breaking:", "hl"), (" Java ended the", None)],
             [("public static void main era ", None), (rose, None)]]

    def width(l):
        return sum(font.getlength(t) if isinstance(t, str) else t.width for t, _ in l)

    lh, px, py, top = 150, 64, 52, 210
    bw = max(width(l) for l in lines) + 2 * px
    d.rectangle([(W - bw) / 2, top, (W + bw) / 2, top + 2 * lh + 2 * py - 20], fill="white")
    for i, l in enumerate(lines):
        x, y = (W - width(l)) / 2, top + py + i * lh
        for t, st in l:
            if isinstance(t, Image.Image):
                img.alpha_composite(t, (int(x), int(y + asc - t.height + 10)))
                continue
            w = font.getlength(t)
            if st == "hl":
                d.rounded_rectangle([x - 14, y - 4, x + w + 14, y + asc + 34], 26, fill=(255, 214, 10))
            d.text((x, y), t, font=font, fill="black")
            x += w
    return img


# ---------- code cards (white, GitHub-light syntax) ----------
KW = {"public", "class", "static", "void", "String"}
COL = {"kw": (207, 34, 46), "str": (10, 48, 105), "fn": (130, 80, 223), "txt": (31, 35, 40)}
PAD = 72


def tokens(line):
    for m in re.finditer(r'"[^"]*"|\w+|\s+|.', line):
        t = m.group()
        k = "str" if t.startswith('"') else "kw" if t in KW else "fn" if t in {"main", "println"} else "txt"
        yield t, k


def make_card(lines, tag, tag_col, mark, glow=None, size=66):
    """Returns (card image, list of (x0, x1, y_mid) per code line in card coords)."""
    CODE_FONT = ImageFont.truetype(MONO_B, size)
    LH = round(size * 1.4)
    tw = max(CODE_FONT.getlength(l) for l in lines)
    cw, ch = int(tw + 2 * PAD), int(len(lines) * LH + 2 * PAD - 10)
    tag_font = ImageFont.truetype(INTER_XB, 72)
    m = emoji(mark, 66)
    tag_w = int(tag_font.getlength(tag) + m.width + 110)
    tag_h = 124
    margin = 90  # room for shadow / glow
    out = Image.new("RGBA", (cw + 2 * margin, ch + tag_h - 30 + 2 * margin), (0, 0, 0, 0))
    cx, cy = margin, margin + tag_h - 30

    # soft drop shadow (or coloured glow) so the white card separates from the white shirt
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    col = glow or (0, 0, 0)
    ImageDraw.Draw(sh).rounded_rectangle([cx, cy + (0 if glow else 18), cx + cw, cy + ch + (0 if glow else 18)],
                                         44, fill=col + (200 if glow else 110,))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(38 if glow else 30)))

    d = ImageDraw.Draw(out)
    d.rounded_rectangle([cx, cy, cx + cw, cy + ch], 44, fill="white",
                        outline=glow or (225, 228, 232), width=10 if glow else 3)
    spans = []
    y = cy + PAD - 8
    for ln in lines:
        x = cx + PAD
        for t, k in tokens(ln):
            d.text((x, y), t, font=CODE_FONT, fill=COL[k])
            x += CODE_FONT.getlength(t)
        lead = CODE_FONT.getlength(ln) - CODE_FONT.getlength(ln.lstrip())
        if ln.strip():
            spans.append((cx + PAD + lead - 10, x + 10, y + size * 0.62))
        y += LH

    # tag pill sitting on the card's top-left edge
    tx, ty = cx + 40, margin
    d.rounded_rectangle([tx, ty, tx + tag_w, ty + tag_h - 10], 60, fill=tag_col)
    d.text((tx + 44, ty + 17), tag, font=tag_font, fill="white")
    out.alpha_composite(m, (int(tx + 44 + tag_font.getlength(tag) + 22), ty + 25))
    return out, spans


OLD = ['public class Main {',
       '  public static void main(String[] args) {',
       '    System.out.println("Hello");',
       '  }',
       '}']
NEW = ['void main() {',
       '  IO.println("Hello");',
       '}']

CARD_CY = 2680  # vertical centre of the cards: chest, clear of face and IG bottom UI


def place(frame, card, scale, alpha, dx=0, dy=0, rot=0):
    if alpha <= 0 or scale <= 0:
        return
    c = card
    if abs(scale - 1) > 1e-3:
        c = c.resize((max(1, int(c.width * scale)), max(1, int(c.height * scale))), Image.BILINEAR)
    if rot:
        c = c.rotate(rot, resample=Image.BILINEAR, expand=True)
    if alpha < 1:
        a = c.getchannel("A").point(lambda v: int(v * alpha))
        c = c.copy()
        c.putalpha(a)
    frame.alpha_composite(c, (int(W / 2 - c.width / 2 + dx), int(CARD_CY - c.height / 2 + dy)))


def pop(t, t0, dur=0.32):
    p = clamp((t - t0) / dur)
    return ease_out_back(p) if p > 0 else 0, clamp((t - t0) / 0.1)


# ---------- "30 years of muscle memory" (caption style of reference 1) ----------
def make_mem_lines():
    font = ImageFont.truetype(INTER_XB, 150)
    skull = emoji("💀", 150)
    res = []
    for text, mark in [("30 years of", None), ("muscle memory", skull)]:
        w = int(font.getlength(text) + (mark.width + 34 if mark else 0))
        im = Image.new("RGBA", (w + 60, 240), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((30, 20), text, font=font, fill="white", stroke_width=14, stroke_fill="black")
        if mark:
            im.alpha_composite(mark, (int(30 + font.getlength(text) + 34), 48))
        res.append(im)
    return res


def main():
    hook = make_hook()
    old, old_spans = make_card(OLD, "Old way", (207, 34, 46), "❌")
    new, _ = make_card(NEW, "Java 25", (26, 127, 55), "✅", glow=(46, 204, 113), size=104)
    mem = make_mem_lines()
    out = sys.stdout.buffer
    for i in range(round(DUR * FPS)):
        t = i / FPS
        f = hook.copy()

        # OLD: pop in, strike each line, shake, then drop away
        if OLD_IN <= t < OLD_GONE:
            card = old
            if t >= STRIKE:
                card = old.copy()
                d = ImageDraw.Draw(card)
                for k, (x0, x1, ym) in enumerate(old_spans):
                    p = clamp((t - STRIKE - k * 0.07) / 0.18)
                    if p > 0:
                        d.line([x0, ym, x0 + (x1 - x0) * p, ym], fill=(255, 59, 48), width=9)
            s, a = pop(t, OLD_IN)
            dx = dy = rot = 0
            if OLD_OUT <= t:
                q = clamp((t - OLD_OUT) / (OLD_GONE - OLD_OUT))
                dx = math.sin(q * 30) * 28 * (1 - q)
                dy, rot, s, a = 900 * q * q, -14 * q, 1 - 0.25 * q, 1 - q * q
            place(f, card, s, a, dx, dy, rot)

        # NEW: bounce in with green glow, quick gentle pulse, out before the fist pose
        if NEW_IN <= t < NEW_GONE:
            s, a = pop(t, NEW_IN, 0.36)
            if t > NEW_IN + 0.5:
                s = 1 + 0.025 * math.sin((t - NEW_IN - 0.5) * 2 * math.pi / 1.1)
            if t >= NEW_OUT:
                q = clamp((t - NEW_OUT) / (NEW_GONE - NEW_OUT))
                s, a = s * (1 - 0.3 * q), 1 - q
            place(f, new, s, a)

        # MEMORY caption: two lines pop in staggered, then hold
        if t >= MEM_IN:
            y = 2560
            for k, im in enumerate(mem):
                s, a = pop(t, MEM_IN + k * 0.18, 0.3)
                if s > 0:
                    c = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
                    if a < 1:
                        c.putalpha(c.getchannel("A").point(lambda v: int(v * a)))
                    f.alpha_composite(c, (int(W / 2 - c.width / 2), int(y + 110 - c.height / 2)))
                y += 200
        out.write(f.tobytes())


if __name__ == "__main__":
    main()
