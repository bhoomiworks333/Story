import json,difflib,re
V=json.load(open('vosk.json'))
# caption chunks exactly as spoken (corrected), max 3 words each, natural breaks
CH="""So after|that last video|a lot|of you asked|then what|does it actually|look like|when someone|trains a model|for real|You don't train|a foundation model|from zero|When someone|trains a model|for real|that can require|massive amounts|of compute|and cost crores|Instead|you take|a model|that already exists|something like|Llama or Mistral|from Hugging Face|and adapt it|to your|specific task|that's called|fine-tuning|You need|a dataset|Once that's ready|you can use|a tool like|Unsloth|You can fine-tune|models on|something like|an RTX 4090|and for|some setups|even a free|Google Colab GPUs|Then you|train it|and after training|you test it|properly|No RGB|GPU towers|no cinematic|terminal footages|Obviously|I can't teach|the whole thing|in 60 seconds|so I'm putting|together|a full breakdown|where I'll show|the dataset|the code|the settings|the GPU requirements|the mistakes|everything|Comment TRAIN|if you|want it""".split('|')
bad=[c for c in CH if len(c.split())>3]; assert not bad, bad
toks=[(ci,w) for ci,c in enumerate(CH) for w in c.split()]
norm=lambda s:re.sub(r"[^a-z0-9']","",s.lower())
A=[norm(w) for _,w in toks]; B=[norm(v['word']) for v in V]
sm=difflib.SequenceMatcher(None,A,B,autojunk=False)
st=[None]*len(A); en=[None]*len(A)
for tag,i1,i2,j1,j2 in sm.get_opcodes():
    if tag=='equal' or (tag=='replace' and i2-i1==j2-j1):
        for k in range(i2-i1): st[i1+k]=V[j1+k]['start']; en[i1+k]=V[j1+k]['end']
    elif tag=='replace':  # spread span over vosk span
        s0=V[j1]['start']; e0=V[j2-1]['end']; n=i2-i1
        for k in range(n): st[i1+k]=s0+(e0-s0)*k/n; en[i1+k]=s0+(e0-s0)*(k+1)/n
# fill remaining by interpolation
for i in range(len(A)):
    if st[i] is None:
        p=max([j for j in range(i) if en[j] is not None],default=None); q=min([j for j in range(i,len(A)) if st[j] is not None],default=None)
        a=en[p] if p is not None else 0; b=st[q] if q is not None else a+0.3
        gap=[j for j in range(i,q if q else len(A)) if st[j] is None]; n=len(gap)
        for k,j in enumerate(gap): st[j]=a+(b-a)*k/n; en[j]=a+(b-a)*(k+1)/n
out=[]
for ci,c in enumerate(CH):
    idx=[i for i,(c2,_) in enumerate(toks) if c2==ci]
    out.append(dict(text=c,s=round(st[idx[0]],3),e=round(en[idx[-1]],3),words=[(toks[i][1],round(st[i],3),round(en[i],3)) for i in idx]))
json.dump(out,open('chunks.json','w'),indent=1)
for o in out: print(f"{o['s']:6.2f} {o['e']:6.2f}  {o['text']}")
