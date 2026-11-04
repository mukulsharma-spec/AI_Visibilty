import json,re,sys
d=json.load(open('measured.json'))
app=sys.argv[1]; a0=int(sys.argv[2]); a1=int(sys.argv[3])
A=[a for a in d['A'] if a['app']==app][a0:a1]
T={t['run_key']:t['answer_text'] for t in d['T']}
M={}
for m in d['M']: M.setdefault(m['run_key'],[]).append(m)
HEAD=re.compile(r"^(\d+[.)]\s*|[-•*]\s*)?([A-Z0-9][\w&'’.+/\- ]{1,45}?)\s*(:|–|—| - |\(|,)")
for a in A:
    k=a['run_key'];t=T[k]
    print(f"@{k} [{a['answer_chars']}c] M=",'; '.join(f"{m['brand']}~{t[max(0,m['first_char_pos']-25):m['first_char_pos']+30]!r}" for m in M.get(k,[])))
    out=[]
    for ln in t.split('\n'):
        ln=ln.strip()
        if re.match(r'^(Searched \d+ websites|Worked for|ChatGPT is AI)',ln): break
        if not ln or re.match(r'^(Shop|Visit|View|Browse) ',ln) or re.fullmatch(r'\+\d+|[\w.-]+\.(com|co\.uk|org|net|uk|co|io)(/\S*)?|(Under |Over )?[£$][\d,]+.*|Yes|No|Sources:',ln): continue
        if len(ln)<=int(sys.argv[4] if len(sys.argv)>4 else 60): out.append(ln)
        else:
            m=HEAD.match(ln)
            if m: out.append(m.group(0)[:55]+'…')
    s=' ¦ '.join(out)
    print(s)
