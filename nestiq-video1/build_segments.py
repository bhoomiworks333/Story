import json, subprocess
U="/root/.claude/uploads/dfd639e9-d70c-5cdd-be9f-a90aec2f93bd/"
S=json.load(open("segments.json"))
W,E=640,900
TARGET=(176,124,100)   # natural, slightly warm skin
def solve(s,sc0=None,cx_t=None,eye_t=E):
    x,y,w,h=s["face"]; eye=y+.4*h; cx=x+w/2
    sc=sc0 or max(W/w,1.0)
    for _ in range(40):
        ty=min(0,max(1920-1920*sc,eye_t-eye*sc)); ey=eye*sc+ty
        if sc0 or abs(ey-eye_t)<=40 or sc>=1.12*max(W/w,1): break
        sc+=0.01
    tx=min(0,max(1080-1080*sc,(cx_t or 540)-cx*sc))
    return sc,tx,ty,ey,cx*sc+tx,w*sc
P={}
for s in S: P[s["id"]]=solve(s)
# keep line 6's two halves identical in framing so the join reads as one take
b=P["L6b"]; a=[s for s in S if s["id"]=="L6a"][0]
P["L6a"]=solve(a,sc0=b[0],cx_t=b[4],eye_t=b[3])
ONLY=__import__("sys").argv[1:]
for s in S:
    if ONLY and s["id"] not in ONLY: continue
    sc,tx,ty,ey,cx,fw=P[s["id"]]
    r,g,bb=s["skin"]; k=.75
    gr,gg,gb=[min(1.25,max(.8,1+k*(t/v-1))) for t,v in zip(TARGET,(r,g,bb))]
    s.update(scale=sc,tx=tx,ty=ty,eye=ey,cx=cx,facew=fw,gains=[gr,gg,gb])
    Wp=int(round(1080*sc/2))*2; Hp=int(round(1920*sc/2))*2
    vf=(f"setpts=(PTS-STARTPTS)/{s.get('speed',1.0)},fps=30,scale={Wp}:{Hp}:flags=lanczos,crop=1080:1920:{int(-tx)}:{int(-ty)},"
        f"colorchannelmixer=rr={gr:.3f}:gg={gg:.3f}:bb={gb:.3f},"
        "curves=all='0/0 0.5/0.5 0.82/0.80 1/0.93',eq=saturation=1.04,format=yuv420p")
    subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{s['in']:.4f}","-i",U+s["src"],"-t",f"{s['out']-s['in']:.4f}",
       "-vf",vf,"-an","-c:v","libx264","-crf","14","-preset","fast",f"segs/{s['id']}_full.mp4"],check=True)
    print("%-4s scale %.2f face %.0f eye %.0f cx %.0f gains %.2f %.2f %.2f"%(s["id"],sc,fw,ey,cx,gr,gg,gb))
json.dump(S,open("segments.json","w"))
