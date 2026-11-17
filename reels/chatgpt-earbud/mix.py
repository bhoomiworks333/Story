import soundfile as sf,numpy as np,sys
SR=48000; D=30.4
def load(f):
    a,sr=sf.read('sfx/'+f); a=a if a.ndim==1 else a.mean(1); assert sr==SR; return a
def peak(a): e=np.convolve(a**2,np.ones(960),'same'); return e.argmax()
# synth camera shutter: two short filtered clicks
rng=np.random.default_rng(1)
def click(n): x=rng.standard_normal(n)*np.exp(-np.linspace(0,9,n)); return np.convolve(x,np.ones(6)/6,'same')
sh=np.zeros(int(SR*0.12)); c=click(int(SR*0.025)); sh[:len(c)]+=c; sh[int(SR*0.07):int(SR*0.07)+len(c)]+=0.7*c; sh/=abs(sh).max()
S={k:load(v) for k,v in dict(wh='reel_public_sfx_whoosh_short.wav',bell='arena-video_sfx_bell.wav',riser='reel_public_sfx_riser.wav',
   hit='reel_public_sfx_hit_short.wav',pop='reel_public_sfx_pop.wav',pop2='arena-video_sfx_pop.wav').items()}
S['shutter']=sh
cues=[('wh',8.0,-10),('wh',12.26,-12),('wh',16.36,-10),('wh',19.08,-10),('shutter',8.52,-8),('bell',12.40,-13),
      ('riser',17.70,-16),('hit',17.72,-9),('pop',17.95,-8),('pop2',24.92,-12)]
tr=np.zeros(int(SR*D))
for k,t,g in cues:
    a=S[k]*10**(g/20); st=int(t*SR)-peak(S[k]); 
    if st<0: a=a[-st:]; st=0
    tr[st:st+len(a)]+=a[:len(tr)-st]
sf.write('sfx_track.wav',tr,SR)
