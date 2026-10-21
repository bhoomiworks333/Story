import sys, json
cover = json.loads(sys.argv[2]) if len(sys.argv)>2 else {}
H="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Montserrat,60,&H00000000,&H00000000,&H00FFFFFF,&H00FFFFFF,-1,0,0,0,100,100,0,0,3,16,0,2,60,60,420,1
Style: Hook,Montserrat,66,&H00000000,&H00000000,&H00FFFFFF,&H00FFFFFF,-1,0,0,0,100,100,0,0,3,18,0,8,40,40,220,1
Style: Cover,Montserrat,60,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
def t(s): h=int(s//3600); m=int(s%3600//60); return f"{h}:{m:02d}:{s%60:05.2f}"
hook_text = sys.argv[1]
ev=[(0.0,4.0,"Hook",hook_text),
(0.62,3.85,"Sub","Kid: Why do we say\\N'nǐ hǎo' in Chinese?"),
(6.41,10.60,"Sub","AI: 'Nǐ hǎo' is how you\\Nsay hello in Chinese."),
(11.20,12.95,"Sub","AI: Like when you want to\\Nsay hello to someone,"),
(12.95,14.35,"Sub","AI: you say 'nǐ hǎo'."),
(15.27,16.94,"Sub","AI: Say it and show me:\\N'nǐ hǎo'!"),
(16.94,18.40,"Sub","Kid: Meeha!")]
out=H
for i,(a,b,st,tx) in enumerate(ev):
    mv = 438 if st=="Sub" and "\\N" not in tx else 0   # centre single lines in the cover card
    out+=f"Dialogue: 1,{t(a)},{t(b)},{st},,0,0,{mv},,{tx}\n"
    if str(i) in cover:
        x0,y0,x1,y1=cover[str(i)]
        out+=f"Dialogue: 0,{t(a)},{t(b)},Cover,,0,0,0,,{{\\pos(0,0)\\p1}}m {x0} {y0} l {x1} {y0} {x1} {y1} {x0} {y1}{{\\p0}}\n"
sys.stdout.write(out)
