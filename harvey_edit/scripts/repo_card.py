"""Repo header card: enlarge the key parts of the GitHub screenshot (2x canvas, 2160x1920)."""
from PIL import Image, ImageDraw
src = Image.open('work/repo_header.png').convert('RGB')
c = Image.open('graphics/card_blank.png').convert('RGBA')
def place(box, height, y, x=None):
    im = src.crop(box); s = height / im.height; im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], 18, fill=255)
    im = im.convert('RGBA'); im.putalpha(m)
    c.alpha_composite(im, ((2160 - im.width) // 2 if x is None else x, y)); return im.size
place((70, 16, 340, 62), 150, 300)                 # GitHub logo + "ethanplusai / harvey"
place((14, 144, 212, 190), 230, 610)               # "harvey  Public"
fw = round(114 * 190 / 38); sw = round(117 * 190 / 38); x0 = (2160 - fw - 70 - sw) // 2
place((608, 148, 722, 186), 190, 960, x0)           # Fork 536
place((775, 148, 892, 186), 190, 960, x0 + fw + 70) # Star 2.6k
c.save('graphics/card_repo.png')
