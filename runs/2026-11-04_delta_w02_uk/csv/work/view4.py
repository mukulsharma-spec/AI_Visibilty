import json,re,sys
d=json.load(open('measured.json'))
app=sys.argv[1]; a0=int(sys.argv[2]); a1=int(sys.argv[3]); W=int(sys.argv[4]) if len(sys.argv)>4 else 50
A=[a for a in d['A'] if a['app']==app][a0:a1]
T={t['run_key']:t['answer_text'] for t in d['T']}
M={}
for m in d['M']: M.setdefault(m['run_key'],[]).append(m['brand'])
SKIP=re.compile(r"^(Why|Best for|Pros|Cons|Price|Prices|Note|Tip|Style|Metal|Budget|Durability|Check|Look|Ask|What|How|The Catch|UK Shopping|Clarity|Colou?r|Cut|Carat|Setting|Certification|Pricing|Returns|Delivery|Shipping|Customi[sz]ation|Selection|Quality|Origin|Treatment|Hardness|Care|Warranty|Sizing)\b",re.I)
for a in A:
    k=a['run_key'];t=T[k];ms=M.get(k,[])
    print(f"\n@{k} M={','.join(ms)}")
    lines=[('\t'+l.strip() if l.startswith('\t') else l.strip()) for l in t.split('\n') if l.strip()]
    for i,ln in enumerate(lines):
        if i==0: print(ln[:80]);continue
        c=ln.find(':')
        if 0<c<70 and not SKIP.match(ln):
            print('• '+ln[:c+1+W]); continue
        if re.match(r'^\d+\.',ln) or (len(ln.split())<=8 and not ln.endswith('.')):
            print(ln[:90]); continue
        if ln.startswith('\t'): print('T'+ln[:110]); continue
        if any(b in ln for b in ms) or re.search(r"verdict|recommend|best pick|winner|go with",ln,re.I): print('> '+ln[:140])
