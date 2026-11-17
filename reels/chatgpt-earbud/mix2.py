import json,numpy as np,soundfile as sf
SR=48000;FPS=30
kept=np.array(json.load(open('edl.json'))['kept'])
v,_=sf.read('voice48.wav'); spf=SR//FPS
# contiguous runs
runs=[];s=kept[0];p=kept[0]
for k in kept[1:]:
    if k!=p+1: runs.append((s,p+1)); s=k
    p=k
runs.append((s,p+1))
fade=int(0.006*SR); out=[]
for a,b in runs:
    seg=v[a*spf:b*spf].copy()
    if len(seg)<a*0+1: continue
    seg[:fade]*=np.linspace(0,1,fade); seg[-fade:]*=np.linspace(1,0,fade); out.append(seg)
voice=np.concatenate(out); n_out=len(kept)
voice=np.pad(voice,(0,max(0,n_out*spf-len(voice))))[:n_out*spf]
def remap(t):   # source seconds -> output seconds
    f=t*FPS; i=np.searchsorted(kept,int(np.floor(f))); 
    return (i+(f-np.floor(f)))/FPS if i<len(kept) and kept[i]==int(np.floor(f)) else i/FPS
def load(f):
    a,sr=sf.read('sfx/'+f); return a if a.ndim==1 else a.mean(1)
def peak(a): return np.convolve(a**2,np.ones(960),'same').argmax()
rng=np.random.default_rng(1)
def click(n): x=rng.standard_normal(n)*np.exp(-np.linspace(0,9,n)); return np.convolve(x,np.ones(6)/6,'same')
sh=np.zeros(int(SR*0.12)); c=click(int(SR*0.025)); sh[:len(c)]+=c; sh[int(SR*0.07):int(SR*0.07)+len(c)]+=0.7*c; sh/=abs(sh).max()
S={k:load(v_) for k,v_ in dict(wh='reel_public_sfx_whoosh_short.wav',bell='arena-video_sfx_bell.wav',riser='reel_public_sfx_riser.wav',
   hit='reel_public_sfx_hit_short.wav',pop='reel_public_sfx_pop.wav',pop2='arena-video_sfx_pop.wav').items()}; S['shutter']=sh
cues=[('wh',3.86,-11),('wh',8.0,-10),('wh',12.26,-12),('wh',16.36,-10),('wh',19.08,-10),('shutter',8.52,-8),('bell',12.40,-13),
      ('riser',17.70,-16),('hit',17.72,-9),('pop',17.95,-8),('pop2',24.92,-12)]
tr=np.zeros_like(voice)
for k,t,g in cues:
    a=S[k]*10**(g/20); st=int(remap(t)*SR)-peak(S[k])
    if st<0: a=a[-st:]; st=0
    tr[st:st+len(a)]+=a[:max(0,len(tr)-st)]
sf.write('voice_cut.wav',voice,SR); sf.write('sfx_cut.wav',tr,SR)
print('out dur',len(voice)/SR, 'cues', [(k,round(remap(t),2)) for k,t,_ in cues])
