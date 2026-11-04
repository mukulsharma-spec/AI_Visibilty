# shorthand: "@rk fmt" ; "Names(;)|rank|role|sent|claim[|conf][|price]" -> gap12 labels.txt format
import csv,glob,sys
AL=set(r['brand'] for r in csv.DictReader(open('/workspace/ai-visibility/inputs/brand_aliases_v3.csv')))
out=["# brand|rank|tie|role(R/C/M/O/F)|card|price|claim|sent(+/0/-)|conf(h/m/l) ; '+' prefix = fact_row=0"]
for f in sorted(glob.glob('lab/*.txt')):
  for ln in open(f,encoding='utf-8'):
    ln=ln.strip()
    if not ln or ln.startswith('#'): continue
    if ln.startswith('@'):
        k,fmt=ln[1:].split(' ',1); out.append(f'@{k} fmt={fmt.strip()}'); continue
    p=ln.split('|')
    names,rank,role,sent,claim=p[:5]; conf=p[5] if len(p)>5 and p[5] else 'h'; price=p[6] if len(p)>6 else ''
    ns=[n.strip() for n in names.split(';') if n.strip()]
    tie='1' if len(ns)>1 and rank else ''
    for n in ns:
        card='0'
        if n.startswith('*'): n=n[1:]; card='1'
        pre='' if n in AL else '+'
        out.append(f'{pre}{n}|{rank}|{tie}|{role}|{card}|{price}|{claim.strip()}|{sent}|{conf}')
open('labels.txt','w',encoding='utf-8').write('\n'.join(out)+'\n')
print(len(out))
