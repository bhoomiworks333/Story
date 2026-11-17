import json,subprocess,numpy as np,sys
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from rembg import remove,new_session
SRC='/root/.claude/uploads/aa978c22-6611-55c0-ae69-050c7dc7122e/1e516321-1117.mp4'
IMG='/tmp/claude-0/-home-user-Story/aa978c22-6611-55c0-ae69-050c7dc7122e/images/'
OUT=sys.argv[1]; LIMIT=float(sys.argv[2]) if len(sys.argv)>2 else 99; START=float(sys.argv[3]) if len(sys.argv)>3 else 0
W,H,FPS=1080,1920,30; SW,SH=1920,1440
F='/usr/share/fonts/opentype/inter/'
fnt=ImageFont.truetype(F+'Inter-Black.otf',92); small=ImageFont.truetype(F+'Inter-Bold.otf',30)
YEL=(255,221,0)
# ---------- captions: 2-3 word chunks
raw=json.load(open('words.json')); words=[]
i=0
while i<len(raw):
    a,b,t=raw[i]
    if t.lower()=='ear' and i+1<len(raw) and raw[i+1][2].lower().startswith('buds'):
        t='earbuds'+raw[i+1][2][4:]; b=raw[i+1][1]; i+=1
    t=t.replace('chargeability','ChatGPT')
    words.append([a,b,t]); i+=1
chunks=[];cur=[]
for w in words:
    cur.append(w)
    if len(cur)==3 or w[2][-1] in ',.?!' : chunks.append(cur);cur=[]
if cur: chunks.append(cur)
def clean(t): return t.upper().strip(',.')
def cap_at(t):
    for ci,c in enumerate(chunks):
        end=chunks[ci+1][0][0] if ci+1<len(chunks) else 99
        end=min(end,c[-1][1]+0.6)
        if c[0][0]<=t<end:
            act=max(k for k,w in enumerate(c) if w[0]<=t)
            return [(clean(w[2]),k==act) for k,w in enumerate(c)]
    return None
def draw_caption(img,t,cx,cy):
    c=cap_at(t)
    if not c: return
    d=ImageDraw.Draw(img); sp=d.textlength(' ',font=fnt)
    ws=[d.textlength(w,font=fnt) for w,_ in c]; tot=sum(ws)+sp*(len(c)-1)
    s=1.0
    if tot>W-80: s=(W-80)/tot
    f=fnt if s==1 else ImageFont.truetype(F+'Inter-Black.otf',int(92*s))
    ws=[d.textlength(w,font=f) for w,_ in c]; sp=d.textlength(' ',font=f); tot=sum(ws)+sp*(len(c)-1)
    x0=max(40,min(cx-tot/2,W-40-tot))
    sl=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sl); x=x0
    for (w,_),wd in zip(c,ws): sd.text((x+4,cy+6),w,font=f,anchor='lm',fill=(0,0,0,200),stroke_width=10,stroke_fill=(0,0,0,200)); x+=wd+sp
    img.alpha_composite(sl.filter(ImageFilter.GaussianBlur(6)))
    x=x0
    for (w,a),wd in zip(c,ws): d.text((x,cy),w,font=f,anchor='lm',fill=YEL if a else 'white',stroke_width=5,stroke_fill='black'); x+=wd+sp
# ---------- assets
def fitw(p): im=Image.open(IMG+p).convert('RGB'); return im.resize((W,int(im.height*W/im.width)),Image.LANCZOS)
s1=fitw('2.webp'); s1=s1.crop((0,0,W,H)); ImageDraw.Draw(s1).rectangle((0,int(890*W/920),W,H),fill='black')  # hide the failed reply
s2=fitw('4.webp')                               # closer photos + Found it (1080x2348)
p3=fitw('3.webp'); p5=fitw('5.webp')
def pop(t,t0,dur=0.2,amt=0.06):
    k=min(1,max(0,(t-t0)/dur)); k=1-(1-k)**3; return 1+amt*(1-k)
def scaled(im,s,cx=W/2,cy=H/2):
    if abs(s-1)<1e-3: return im
    nw,nh=int(im.width*s),int(im.height*s); r=im.resize((nw,nh),Image.BILINEAR)
    x=int(cx*s-cx); y=int(cy*s-cy); return r.crop((x,y,x+im.width,y+im.height))
def ease(k): k=min(1,max(0,k)); return k*k*(3-2*k)
def background(t):
    bg=Image.new('RGB',(W,H),'black')
    if t<8.0:
        z=1+0.04*t/8; bg=scaled(s1,z*pop(t,0),W/2,700)
    elif t<16.36:
        off=int(428*ease((t-12.26)/0.45))
        src=s2
        if t<12.26: src=s2.copy(); ImageDraw.Draw(src).rectangle((0,650,W,src.height),fill='black')
        bg=scaled(src.crop((0,off,W,off+H)),pop(t,8.0)*(pop(t,12.26,0.25,0.03)),W/2,700)
    elif t<17.70:
        k=(t-16.36)/1.34; s=1+0.25*k
        im=scaled(p3,s*pop(t,16.36,0.2,0.08),130,345)
        bg.paste(im,(0,300))
    else:
        s=1+0.12*(t-17.7)/1.4
        im=scaled(p5,s*pop(t,17.70,0.25,0.15),220,380); bg.paste(im,(0,420))
    return bg.convert('RGBA')
# ---------- main loop
sess=new_session('u2net_human_seg')
dec=subprocess.Popen(['ffmpeg','-v','error','-i',SRC,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
  '-map','0:v','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-color_range','tv',
  '-movflags','+faststart',OUT],stdin=subprocess.PIPE)
CUT_END=19.08; n=0; credit=None
while True:
    buf=dec.stdout.read(SW*SH*3)
    if len(buf)<SW*SH*3: break
    t=n/FPS; n+=1
    if t>LIMIT: break
    if t<START: continue
    fr=Image.frombuffer('RGB',(SW,SH),buf)
    if t<CUT_END:
        m=remove(fr.resize((960,720)),session=sess,only_mask=True).resize((SW,SH),Image.BILINEAR)
        cut=fr.convert('RGBA'); cut.putalpha(m)
        bb=(200,150,1640,1440); cut=cut.crop(bb)
        sw=820; cut=cut.resize((sw,int(cut.height*sw/cut.width)),Image.BILINEAR)
        x=W-sw+110; y=H-cut.height
        img=background(t)
        sh=Image.new('RGBA',cut.size,(0,0,0,0)); sh.putalpha(cut.split()[3].point(lambda a:int(a*0.6))); sh=sh.filter(ImageFilter.GaussianBlur(20))
        img.alpha_composite(sh,(x-15,y+10)); img.alpha_composite(cut,(x,y))
        # credit pill
        d=ImageDraw.Draw(img); txt='via u/Just_a_fungi893 on Reddit'
        tw=d.textlength(txt,font=small); d.rounded_rectangle((W/2-tw/2-28,22,W/2+tw/2+28,88),33,fill=(32,32,32,255))
        d.text((W/2,54),txt,font=small,anchor='mm',fill=(220,220,220))
        draw_caption(img,t,560,1640)
    else:
        img=fr.crop((515,0,1325,1440)).resize((W,H),Image.LANCZOS).convert('RGBA')
        k=pop(t,CUT_END,0.25,0.06); img=scaled(img,k,W/2,700)
        draw_caption(img,t,W/2,1380)
    enc.stdin.write(img.convert('RGB').tobytes())
    if n%60==0: print(f'{t:.1f}s',flush=True)
enc.stdin.close(); enc.wait(); dec.kill(); print('done',n)
