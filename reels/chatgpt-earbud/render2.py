import json,subprocess,numpy as np,sys,os,soundfile as sf
from PIL import Image,ImageDraw,ImageFont,ImageFilter
SRC='/root/.claude/uploads/aa978c22-6611-55c0-ae69-050c7dc7122e/1e516321-1117.mp4'
IMG='/tmp/claude-0/-home-user-Story/aa978c22-6611-55c0-ae69-050c7dc7122e/images/'
OUT=sys.argv[1]; ONLY=[float(x) for x in sys.argv[2].split(',')] if len(sys.argv)>2 else None  # optional list of source times to dump as png
W,H,FPS=1080,1920,30; SW,SH=1920,1440; CUT_END=19.08
F='/usr/share/fonts/opentype/inter/'
fnt=ImageFont.truetype(F+'Inter-Black.otf',92); small=ImageFont.truetype(F+'Inter-Bold.otf',30); YEL=(255,221,0)
# ---------------- 1. pause removal -> list of kept source frame ranges
aud,sr=sf.read('a.wav'); raw=json.load(open('words.json'))
def rms(t0,t1): s=aud[int(t0*sr):int(t1*sr)]; return 20*np.log10(np.sqrt((s**2).mean())+1e-9)
cuts=[]
for x,y in zip(raw,raw[1:]):
    if y[0]-x[1]<0.25: continue
    ts=np.arange(x[1]-0.1,y[0]+0.1,0.01); q=np.array([rms(t,t+0.01)<-34 for t in ts])
    for k in range(1,len(q)-2):
        if not q[k] and q[k-1] and (q[k+1] or q[k+2]): q[k]=True
    best=(0,0);i=0
    while i<len(q):
        if q[i]:
            j=i
            while j<len(q) and q[j]: j+=1
            if j-i>best[1]-best[0]: best=(i,j)
            i=j
        else: i+=1
    a,b=ts[best[0]]+0.05,ts[best[1]-1]+0.01-0.06
    if b-a>=0.12: cuts.append((int(np.ceil(a*FPS)),int(np.floor(b*FPS))))
total=int(round(30.3*FPS)); keep=np.ones(total,bool)
for a,b in cuts: keep[a:b]=False
kept=np.where(keep)[0]
json.dump({'cuts':cuts,'kept':kept.tolist()},open('edl.json','w'))
print('cuts',len(cuts),'removed',(~keep).sum()/FPS,'s -> out',len(kept)/FPS,'s',flush=True)
# ---------------- 2. captions (source time)
words=[];i=0
while i<len(raw):
    a,b,t=raw[i]
    if t.lower()=='ear' and i+1<len(raw) and raw[i+1][2].lower().startswith('buds'): t='earbuds'+raw[i+1][2][4:]; b=raw[i+1][1]; i+=1
    words.append([a,b,t.replace('chargeability','ChatGPT')]); i+=1
chunks=[];cur=[]
for w in words:
    cur.append(w)
    if len(cur)==3 or w[2][-1] in ',.?!': chunks.append(cur);cur=[]
if cur: chunks.append(cur)
def cap_at(t):
    for ci,c in enumerate(chunks):
        end=min(chunks[ci+1][0][0] if ci+1<len(chunks) else 99, c[-1][1]+0.6)
        if c[0][0]<=t<end:
            act=max(k for k,w in enumerate(c) if w[0]<=t); return [(w[2].upper().strip(',.'),k==act) for k,w in enumerate(c)]
def draw_caption(img,t,cx,cy):
    c=cap_at(t)
    if not c: return
    d=ImageDraw.Draw(img); f=fnt
    ws=[d.textlength(w,font=f) for w,_ in c]; sp=d.textlength(' ',font=f); tot=sum(ws)+sp*(len(c)-1)
    if tot>W-80:
        f=ImageFont.truetype(F+'Inter-Black.otf',int(92*(W-80)/tot)); ws=[d.textlength(w,font=f) for w,_ in c]; sp=d.textlength(' ',font=f); tot=sum(ws)+sp*(len(c)-1)
    x0=max(40,min(cx-tot/2,W-40-tot))
    sl=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sl); x=x0
    for (w,_),wd in zip(c,ws): sd.text((x+4,cy+6),w,font=f,anchor='lm',fill=(0,0,0,200),stroke_width=10,stroke_fill=(0,0,0,200)); x+=wd+sp
    img.alpha_composite(sl.filter(ImageFilter.GaussianBlur(6))); x=x0
    for (w,a),wd in zip(c,ws): d.text((x,cy),w,font=f,anchor='lm',fill=YEL if a else 'white',stroke_width=5,stroke_fill='black'); x+=wd+sp
# ---------------- 3. assets
def fitw(im,w=W): return im.resize((w,int(im.height*w/im.width)),Image.LANCZOS)
def cover(im):
    s=max(W/im.width,H/im.height); r=im.resize((int(im.width*s)+1,int(im.height*s)+1)); x=(r.width-W)//2; y=(r.height-H)//2
    r=r.crop((x,y,x+W,y+H)).filter(ImageFilter.GaussianBlur(40)); return Image.blend(r,Image.new('RGB',(W,H)),0.55)
s1=fitw(Image.open(IMG+'2.webp').convert('RGB')).crop((0,0,W,H)); ImageDraw.Draw(s1).rectangle((0,int(890*W/920),W,H),fill='black')
s2=fitw(Image.open(IMG+'4.webp').convert('RGB')); s2_hidden=s2.copy(); ImageDraw.Draw(s2_hidden).rectangle((0,650,W,s2.height),fill='black')
p3=Image.open(IMG+'3.webp').convert('RGB'); p3c=Image.open('p3_clean.png').convert('RGB'); p5=Image.open(IMG+'5.webp').convert('RGB')
BG_HOOK=cover(p3c); BG3=cover(p3); BG5=cover(p5)
HOOK=fitw(p3c,1500); P3=fitw(p3,1500); P5=fitw(p5,1000)
def ease(k): k=min(1,max(0,k)); return k*k*(3-2*k)
def outc(k): k=min(1,max(0,k)); return 1-(1-k)**3
def pop(t,t0,dur=0.2,amt=0.06): return 1+amt*(1-outc((t-t0)/dur))
def punch(t,t0,amt=0.10):          # quick zoom in on a keyword, settles back over ~1.2s
    if t<t0: return 1
    k=(t-t0); return 1+amt*(outc(k/0.12) if k<0.12 else 1-ease((k-0.5)/0.9))
def zoom(im,s,cx,cy):
    if abs(s-1)<1e-3: return im
    nw,nh=int(im.width*s),int(im.height*s); r=im.resize((nw,nh),Image.BILINEAR)
    x=int(cx*s-cx); y=int(cy*s-cy); return r.crop((x,y,x+im.width,y+im.height))
def card(bg,fg,x,y):
    out=bg.copy(); m=Image.new('L',fg.size,0); ImageDraw.Draw(m).rounded_rectangle((0,0,*fg.size),28,fill=255)
    sh=Image.new('RGBA',(fg.width+80,fg.height+80),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((40,50,fg.width+40,fg.height+50),28,fill=(0,0,0,170))
    o=out.convert('RGBA'); o.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)),(x-40,y-40)); o=o.convert('RGB'); o.paste(fg,(x,y),m); return o
def flash(img,t,t0,dur=0.12):
    k=(t-t0)/dur
    if 0<=k<1: img=Image.blend(img,Image.new('RGB',img.size,'white'),0.55*(1-k))
    return img
def background(t):
    if t<3.86:      # hook: clean wide photo (earbud not marked yet), slow push toward it
        z=(1+0.06*t/3.86)*punch(t,0.98,0.08)
        fg=zoom(HOOK,z,180,420).crop((0,0,W,HOOK.height)); bg=card(BG_HOOK,fg,0,330)
    elif t<8.0:
        bg=zoom(s1,pop(t,3.86)*punch(t,5.66,0.12)*(1+0.03*(t-3.86)/4),690,560); bg=flash(bg,t,3.86)
    elif t<16.36:
        off=int(428*ease((t-12.26)/0.3)); src=s2_hidden if t<12.26 else s2
        bg=zoom(src.crop((0,off,W,off+H)),pop(t,8.0)*punch(t,8.52,0.10)*punch(t,14.40,0.10),300 if t>12.26 else 540,420 if t>12.26 else 230)
        bg=flash(bg,t,12.26)
    elif t<17.70:
        k=(t-16.36)/1.34; fg=zoom(P3,(1+0.30*k)*pop(t,16.36,0.2,0.08),180,450).crop((0,0,W,P3.height)); bg=card(BG3,fg,0,330)
    else:
        fg=zoom(P5,(1+0.10*(t-17.7)/1.4)*pop(t,17.70,0.25,0.15),205,330); bg=card(BG5,fg,40,420)
    return bg.convert('RGBA')
# ---------------- 4. render
from rembg import remove,new_session
sess=None
def mask(n,fr):
    global sess
    p=f'masks/{n:04d}.png'
    if os.path.exists(p): return Image.open(p)
    if sess is None: sess=new_session('u2net_human_seg')
    m=remove(fr.resize((960,720)),session=sess,only_mask=True); m.save(p); return m
dec=subprocess.Popen(['ffmpeg','-v','error','-i',SRC,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=None if ONLY else subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
  '-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-color_range','tv',OUT],stdin=subprocess.PIPE)
want=set(int(round(x*FPS)) for x in ONLY) if ONLY else None
n=-1; wrote=0
while True:
    buf=dec.stdout.read(SW*SH*3)
    if len(buf)<SW*SH*3: break
    n+=1
    if n>=total or not keep[n]: continue
    if want is not None and n not in want: continue
    t=n/FPS; fr=Image.frombuffer('RGB',(SW,SH),buf)
    if t<CUT_END:
        cut=fr.convert('RGBA'); cut.putalpha(mask(n,fr).resize((SW,SH),Image.BILINEAR))
        cut=cut.crop((200,150,1640,1440)); sw=820; cut=cut.resize((sw,int(cut.height*sw/cut.width)),Image.BILINEAR)
        x=W-sw+110; y=H-cut.height; img=background(t)
        sh=Image.new('RGBA',cut.size,(0,0,0,0)); sh.putalpha(cut.split()[3].point(lambda a:int(a*0.6))); sh=sh.filter(ImageFilter.GaussianBlur(20))
        img.alpha_composite(sh,(x-15,y+10)); img.alpha_composite(cut,(x,y))
        d=ImageDraw.Draw(img); txt='via u/Just_a_fungi893 on Reddit'; tw=d.textlength(txt,font=small)
        d.rounded_rectangle((W/2-tw/2-28,22,W/2+tw/2+28,88),33,fill=(32,32,32,255)); d.text((W/2,54),txt,font=small,anchor='mm',fill=(220,220,220))
        draw_caption(img,t,560,1640)
    else:
        img=fr.crop((515,0,1325,1440)).resize((W,H),Image.LANCZOS)
        img=zoom(img,pop(t,CUT_END,0.25,0.06)*punch(t,24.92,0.07),W/2,700).convert('RGBA')
        draw_caption(img,t,W/2,1380)
    if want is not None: img.convert('RGB').save(f'v2_{t:.2f}.png'); continue
    enc.stdin.write(img.convert('RGB').tobytes()); wrote+=1
    if wrote%60==0: print(f'out {wrote/FPS:.1f}s',flush=True)
if enc: enc.stdin.close(); enc.wait()
dec.kill(); print('done',wrote)
