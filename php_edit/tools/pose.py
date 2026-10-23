import sys, subprocess, numpy as np, math, json
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
src, model, out = sys.argv[1:4]
W,H=576,1024
opt=vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=model),
  output_face_blendshapes=True, output_facial_transformation_matrixes=True, num_faces=1)
lm=vision.FaceLandmarker.create_from_options(opt)
p=subprocess.Popen(['ffmpeg','-v','error','-i',src,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
rows=[];i=0
while True:
    b=p.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    img=np.frombuffer(b,np.uint8).reshape(H,W,3)
    r=lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB,data=np.ascontiguousarray(img)))
    d={'f':i,'t':round(i/30,3)}
    if r.face_landmarks:
        M=np.array(r.facial_transformation_matrixes[0])[:3,:3]
        d['yaw']=round(math.degrees(math.atan2(-M[2,0],math.hypot(M[0,0],M[1,0]))),1)
        d['pitch']=round(math.degrees(math.atan2(M[2,1],M[2,2])),1)
        d['roll']=round(math.degrees(math.atan2(M[1,0],M[0,0])),1)
        bs={c.category_name:c.score for c in r.face_blendshapes[0]}
        for k in ['jawOpen','mouthFunnel','mouthPucker','browInnerUp','mouthSmileLeft','mouthSmileRight','mouthPressLeft','mouthRollLower']:
            d[k]=round(bs[k],2)
        pts=np.array([[q.x*W,q.y*H] for q in r.face_landmarks[0]])
        d['box']=[float(pts[:,0].min()),float(pts[:,1].min()),float(pts[:,0].max()),float(pts[:,1].max())]
    rows.append(d);i+=1
json.dump(rows,open(out,'w'))
print(i,'frames', sum('yaw' in r for r in rows),'with face')
