# Face-only pass: feathered elliptical mask, mild gamma lift, compress skin shine.
import numpy as np, cv2
def mask_for(box,W,H,feather=45):
    x0,y0,x1,y1=box; cx,cy=(x0+x1)/2,(y0+y1)/2; ax,ay=(x1-x0)*0.62,(y1-y0)*0.66
    m=np.zeros((H,W),np.float32)
    cv2.ellipse(m,(int(cx),int(cy)),(int(ax),int(ay)),0,0,360,1.0,-1)
    return cv2.GaussianBlur(m,(0,0),feather)
def apply(rgb,box,gamma=1.12,shine_keep=0.35):
    H,W=rgb.shape[:2]; a=rgb.astype(np.float32)/255
    m=mask_for(box,W,H)
    b=np.power(a,1/gamma)
    L=b@np.array([0.299,0.587,0.114],np.float32)
    base=cv2.GaussianBlur(L,(0,0),12)            # local skin level
    sel=m>0.5
    thr=np.percentile(L[sel],80) if sel.any() else 0.8
    ex=np.clip(L-np.maximum(base,thr),0,None)    # sheen above local skin + face p80
    Lnew=L-ex*(1-shine_keep)
    b=b*(Lnew/np.maximum(L,1e-4))[...,None]      # scale RGB together: keeps hue/saturation
    out=a*(1-m[...,None])+b*m[...,None]
    return (np.clip(out,0,1)*255+0.5).astype(np.uint8), m
