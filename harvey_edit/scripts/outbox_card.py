"""Build the Outbox card from a frame of the repo's dashboard GIF (2x canvas)."""
from PIL import Image, ImageDraw
G = 'graphics/'
def rr(im, r):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=255)
    im = im.convert('RGBA'); im.putalpha(m); return im
ob = Image.open('work/outbox_10.png').convert('RGB').crop((478, 112, 1168, 655))
s = min(2000 / ob.width, 1340 / ob.height); ob = ob.resize((round(ob.width * s), round(ob.height * s)), Image.LANCZOS)
c = Image.open(G + 'card_blank.png').convert('RGBA'); c.alpha_composite(rr(ob, 24), ((2160 - ob.width) // 2, 130))
lab = Image.open(G + 'label_approve.png'); c.alpha_composite(lab, ((2160 - lab.width) // 2, 130 + ob.height + 24))
print('outbox card content bottom (1x):', (130 + ob.height + 24 + lab.height) / 2)
c.save(G + 'card_outbox.png')
