import json,re,sys
d=json.load(open('measured.json'))
app=sys.argv[1]; a0=int(sys.argv[2]); a1=int(sys.argv[3]); W=int(sys.argv[4]) if len(sys.argv)>4 else 100
A=[a for a in d['A'] if a['app']==app][a0:a1]
T={t['run_key']:t['answer_text'] for t in d['T']}
M={}
for m in d['M']: M.setdefault(m['run_key'],[]).append(m['brand'])
SKIP=re.compile(r"^(Claude responded|Searched the web|24/7 Customer Support|just now|Comparing|Thinking|Planning|Diamond Rocks UK Logo|My Shopping Bag)|^\+\d+$|^[a-z0-9-]+$|^[\w.-]+\.(com|co\.uk|org|net|uk|co|io)(/\S*)?$|^(Under |Over )?[£$][\d,]+[^a-z]*$|^(Yes|No|Sources:)$")
for a in A:
    k=a['run_key'];t=T[k]
    print(f"\n@{k} M={','.join(M.get(k,[]))}")
    for ln in t.split('\n'):
        ln=ln.strip().replace('\ue015','')
        if re.match(r'^(Searched \d+ websites|Worked for|ChatGPT is AI|Let me narrow it down)',ln): break
        if not ln or SKIP.search(ln): continue
        print(ln[:W]+('…' if len(ln)>W else ''))
