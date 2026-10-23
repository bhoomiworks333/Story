import json,sys,numpy as np
from PIL import Image
P=json.load(open(sys.argv[1])); d=sys.argv[2]; tags=sys.argv[3].split(',')
def src(n): return n if n<120 else n+27
for n in [0,139,278]:
    x0,y0,x1,y1=map(int,P[src(n)]['box'])
    for tag in tags:
        a=np.asarray(Image.open(f'{d}/{tag}_{n}.png').convert('RGB')).astype(float)/255
        f=a[y0:y1,x0:x1]; Y=f@[0.299,0.587,0.114]
        win=a[150:330, 300:576]@[0.299,0.587,0.114]
        r,g,b=f.reshape(-1,3).mean(0)
        print(f"frame {n:3d} {tag:7s} faceY={Y.mean():.3f} p10={np.percentile(Y,10):.3f} p99={np.percentile(Y,99):.3f} hot>0.85={(Y>0.85).mean()*100:4.1f}%  RGB=({r:.2f},{g:.2f},{b:.2f}) R/G={r/g:.2f} G/B={g/b:.2f} window={win.mean():.2f}")
