import numpy as np, wave
SR=48000; N=int(SR*58.0); buf=np.zeros((N,2)); rng=np.random.default_rng(3)
def env(n,a=.005,r=.2):
    e=np.ones(n); na=int(SR*a); nr=int(SR*r); e[:na]=np.linspace(0,1,na); e[-nr:]*=np.linspace(1,0,nr); return e
def add(t,sig,g=1.,pan=0.):
    i=int(t*SR); s=sig[:N-i]*g; buf[i:i+len(s),0]+=s*(1-pan)/1.0*0.7; buf[i:i+len(s),1]+=s*(1+pan)*0.7
def noise(d,lp=.2):
    x=rng.standard_normal(int(SR*d)); y=np.zeros_like(x); a=0
    for k in range(len(x)): a+=lp*(x[k]-a); y[k]=a
    return y/ (np.abs(y).max()+1e-9)
def sweep(f0,f1,d):
    t=np.arange(int(SR*d))/SR; f=np.geomspace(f0,f1,len(t)); return np.sin(2*np.pi*np.cumsum(f)/SR)
def bell(f,d=1.5):
    t=np.arange(int(SR*d))/SR; return (np.sin(2*np.pi*f*t)+.4*np.sin(2*np.pi*f*2.76*t))*np.exp(-t*4)
def ring(d):
    t=np.arange(int(SR*d))/SR
    tone=np.sin(2*np.pi*1180*t)+.7*np.sin(2*np.pi*1530*t); trem=(np.sin(2*np.pi*22*t)>0)*.8+.2
    return tone*trem*((t%.6)<.42)*.35*env(len(t),.01,.1)
def whoosh(d):
    n=noise(d,.12); x=np.linspace(0,1,len(n)); return n*np.sin(np.pi*x)**2
pop=lambda f: sweep(f,f*2.2,.08)*env(int(SR*.08),.002,.04)
add(0.0,ring(1.25),.18,.3)
for t in [13.75,41.35]: add(t-.25,whoosh(.55),.35)

for t,f in [(46.1,500),(47.5,700),(48.44,780),(49.26,860),(49.88,940)]: add(t,pop(f),.45)
add(53.26,bell(1320,1.2),.22); add(53.26,bell(1980,1.0),.12)

buf=np.clip(buf,-1,1); w=wave.open('sfx.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((buf*32767).astype('<i2').tobytes()); w.close()
