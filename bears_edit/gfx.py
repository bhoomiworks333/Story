# Step 4: graphics (rendered with PIL at final 1080x1920 scale)
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import re
BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
XBOLD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
EMOJI_RE = re.compile("([\U0001F300-\U0001FAFF])")

def font(size, path=BOLD): return ImageFont.truetype(path, size)

def emoji_img(ch, size):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((round(im.width * size / im.height), size), Image.LANCZOS)

def rich_line(text, size, color, path=BOLD):
    """Text with inline colour emoji -> RGBA strip sized to the text's cap/descender box."""
    f = font(size, path); asc, desc = f.getmetrics()
    parts = [p for p in EMOJI_RE.split(text) if p]
    pieces = []
    for p in parts:
        if EMOJI_RE.fullmatch(p): pieces.append(emoji_img(p, int(size * 0.95)))
        else:
            w = int(f.getlength(p)); im = Image.new("RGBA", (max(w, 1), asc + desc), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((0, 0), p, font=f, fill=color); pieces.append(im)
    W = sum(p.width for p in pieces); H = asc + desc
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0)); x = 0
    for p in pieces:
        out.alpha_composite(p, (x, (H - p.height) // 2 + (0 if p.height < H else 0))); x += p.width
    return out

def boxed(text, size, fg=(0, 0, 0), bg=(255, 255, 255), padx=26, pady=14, radius=14, path=BOLD, outline=None):
    lines = text.split("\n")
    strips = [rich_line(l, size, fg, path) for l in lines]
    W = max(s.width for s in strips) + 2 * padx; lh = int(size * 1.22); H = lh * len(strips) + 2 * pady
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, W - 1, H - 1), radius, fill=bg + (255,), outline=outline, width=3 if outline else 0)
    for i, s in enumerate(strips):
        im.alpha_composite(s, ((W - s.width) // 2, pady + i * lh + (lh - s.height) // 2 + int(size * 0.04)))
    return im

def shadowed(im, blur=18, offset=8, alpha=110):
    pad = blur * 2
    out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0)); a = im.split()[3].point(lambda v: v * alpha // 255)
    sh.paste((0, 0, 0, 255), (pad, pad + offset), a); sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(sh); out.alpha_composite(im, (pad, pad)); return out

def price_card(w=1000, h=700):
    """Returns (card base, claude price layer, gemini price layer, positions)."""
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 32, fill=(30, 30, 30, 255), outline=(60, 60, 60, 255), width=2)
    d.line((w // 2, 90, w // 2, h - 170), fill=(70, 70, 70, 255), width=3)
    f = font(46)
    for cx, name in ((w // 4, "Claude Opus 5.5"), (3 * w // 4, "Gemini 4 Argon")):
        tw = f.getlength(name); d.text((cx - tw / 2, 110), name, font=f, fill=(235, 235, 235))
    f2 = font(48); t = "≈3x cheaper with Claude"; tw = f2.getlength(t)
    d.text(((w - tw) / 2, h - 120), t, font=f2, fill=(34, 197, 94))
    pc = rich_line("$7.2", 170, (34, 197, 94), XBOLD); pg = rich_line("$22", 170, (239, 68, 68), XBOLD)
    pos = {"claude": (w // 4, 340), "gemini": (3 * w // 4, 340)}     # centres
    return card, pc, pg, pos

def credit_pill():
    f = font(30); t = "Video: @semichenkko"; tw = int(f.getlength(t)); asc, desc = f.getmetrics()
    im = Image.new("RGBA", (tw + 44, asc + desc + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), im.height // 2, fill=(0, 0, 0, 150))
    d.text((22, 10), t, font=f, fill=(255, 255, 255)); return im

def xpost_card(path, width=940):
    src = Image.open(path).convert("RGB")
    src = src.crop((2, 4, src.width - 2, 412))                      # header + post text, without the embedded video
    src = src.resize((width, round(src.height * width / src.width)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
    mask = Image.new("L", src.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, src.width - 1, src.height - 1), 28, fill=255)
    im = Image.new("RGBA", src.size, (0, 0, 0, 0)); im.paste(src, (0, 0), mask)
    return shadowed(im, blur=22, offset=10, alpha=160)

def rounded_mask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m

if __name__ == "__main__":
    import os; os.makedirs("gfx", exist_ok=True)
    card, pc, pg, pos = price_card(); full = card.copy()
    for im, k in ((pc, "claude"), (pg, "gemini")):
        full.alpha_composite(im, (pos[k][0] - im.width // 2, pos[k][1] - im.height // 2))
    full.save("gfx/price_card.png"); pc.save("gfx/price_claude.png"); pg.save("gfx/price_gemini.png")
    boxed("3x the money 💸", 72).save("gfx/punch.png")
    credit_pill().save("gfx/credit.png")
    xpost_card("src/xpost.png").save("gfx/xpost.png")
    boxed("Gemini 4 Argon cost\n3x more for this 😬", 60).save("gfx/hook_A.png")
    boxed("Same prompt. Claude: $7.2. Gemini: $22 😬", 46).save("gfx/hook_B.png")
    boxed("Which one would you have bet on? 👇", 50).save("gfx/cta.png")
    # preview sheet on grey
    names = ["price_card", "punch", "credit", "xpost", "hook_A", "hook_B", "cta"]
    sheet = Image.new("RGBA", (1100, 2700), (90, 90, 90, 255)); y = 20
    for n in names:
        im = Image.open(f"gfx/{n}.png"); sheet.alpha_composite(im, (20, y)); y += im.height + 20
    sheet.crop((0, 0, 1100, y)).convert("RGB").save("work/frames/gfx_sheet.png")
