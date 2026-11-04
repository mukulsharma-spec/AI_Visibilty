import json,re,sys
d=json.load(open('measured.json'))
app=sys.argv[1]; a0=int(sys.argv[2]); a1=int(sys.argv[3]); W=int(sys.argv[4]) if len(sys.argv)>4 else 60
A=[a for a in d['A'] if a['app']==app][a0:a1]
T={t['run_key']:t['answer_text'] for t in d['T']}
M={}
for m in d['M']: M.setdefault(m['run_key'],[]).append(m['brand'])
STOP=re.compile(r"^(Searched \d+ websites|Worked for|ChatGPT is AI|Let me narrow|Let's narrow|I'd love to (narrow|help)|Get recommendations that fit|Three questions|Let me help)",re.I)
KEEP=re.compile(r"^\d+[.)]|^#|^(Shop|Browse|Explore|See|View|Visit)\b|pick|choice|recommend|verdict|winner|avoid|I'd (start|go|choose|buy|lean)|top |best ",re.I)
COMMON=set("what why how an for best my top tips and of to in on with your is are price prices i you budget style metal colour".split())
for a in A:
    k=a['run_key'];t=T[k];ms=M.get(k,[])
    print(f"\n@{k} M={','.join(ms)}")
    first=True;n=0
    for ln in t.split('\n'):
        ln=ln.strip().replace('\ue015','')
        if not ln: continue
        if STOP.match(ln) and n>3: print('[STOP] '+ln[:40]);break
        n+=1
        w=ln.split()
        short= len(w)<=7 and not ln.endswith(('.',':','?')) and w[0][0].isupper() and w[0].lower() not in COMMON
        if first or KEEP.search(ln) or any(b in ln for b in ms) or short:
            print(ln[:W]+('…' if len(ln)>W else '')); first=False
