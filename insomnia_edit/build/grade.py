"""Step 3: measure each shot, derive per-shot match + shared look. Writes grade.json and before/after stills."""
import json, subprocess, numpy as np
from PIL import Image
E="/home/user/Story/insomnia_edit"; tl=json.load(open(f"{E}/build/timeline.json"))
shots=[(s["clip"],s["src"],s["b"]-s["a"]) for s in tl["sections"] if s["type"]=="walk"]
shots.append(("clipD_c3",20.0,10.0))
def frame(clip,t,vf="scale=540:-2"):
    raw=subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i",f"{E}/source/{clip}.mp4","-frames:v","1","-vf",vf+",format=rgb24","-f","rawvideo","-"],capture_output=True).stdout
    w=540; h=len(raw)//(w*3); return np.frombuffer(raw,np.uint8).reshape(h,w,3)/255.0
stats=[]
for clip,src,dur in shots:
    fs=[frame(clip,src+dur*k/4) for k in range(4)]
    m=np.mean([f[f.shape[0]//4:3*f.shape[0]//4, f.shape[1]//6:5*f.shape[1]//6].reshape(-1,3).mean(0) for f in fs],0)
    stats.append(m)
stats=np.array(stats)
lin=lambda c: c**2.2
L=lambda m: 0.2126*m[0]+0.7152*m[1]+0.0722*m[2]
walk=stats[:-1]; tgt_rgb=walk.mean(0); tgt_ratio=tgt_rgb/L(tgt_rgb)
TARGET_L=0.50
out={}
for (clip,src,dur),m in zip(shots,stats):
    ratio=m/L(m)
    gains=(tgt_ratio/ratio)**0.6          # 60% white-balance match toward the group
    gains/=L(gains*m)/L(m)                 # keep luma
    gamma=(np.log(L(m))/np.log(TARGET_L))**0.5 if clip!="clipD_c3" else (np.log(L(m))/np.log(0.42))**0.5
    out[f"{clip}@{src}"]=dict(rr=round(gains[0],3),gg=round(gains[1],3),bb=round(gains[2],3),gamma=round(float(1/gamma),3),mean=[round(x,3) for x in m])
    print(f"{clip}@{src:5}: mean RGB {np.round(m,3)} L={L(m):.3f} -> gains {np.round(gains,3)} gamma {1/gamma:.3f}")
json.dump(out,open(f"{E}/build/grade.json","w"),indent=1)
