# build_csv v2.3.3 (measured) for 2026-10-29_delta_w01_new2 — reads raw/, writes csv/work/measured.json only
import csv,re,os,json,glob,html as H
from urllib.parse import urlparse
BASE='/workspace/ai-visibility/'
RUN_ID='2026-10-29_delta_w01_new2'
RUN=BASE+'runs/'+RUN_ID+'/'
OUT=RUN+'csv/work/'
ALIASES=[(r['brand'],re.compile(r['pattern'],re.I)) for r in csv.DictReader(open(BASE+'inputs/brand_aliases_v3.csv',encoding='utf-8'))]
DROP_HOSTS=('chatgpt.com','chat.openai.com','openai.com','claude.ai','anthropic.com','gemini.google.com','accounts.google.com','support.google.com','policies.google.com')
TWO=('co.uk','com.au','co.nz','co.in','com.br','co.jp','com.sg','co.za','org.uk','ac.uk','com.mx','com.hk')
# chip label -> registrable domain (recognizable names only)
CHIPDOM={'angara':'angara.com','brilliant earth':'brilliantearth.com','brilliantearth':'brilliantearth.com','blue nile':'bluenile.com',
 'kay':'kay.com','kay jewelers':'kay.com','rare carat':'rarecarat.com',"macy's":'macys.com','target':'target.com','ruby & oscar':'rubyandoscar.com',
 'the diamond pro':'diamondpro.com','reddit':'reddit.com','aurate':'auratenewyork.com','forbes':'forbes.com','zales':'zales.com','etsy':'etsy.com',
 'comparemaniac':'comparemaniac.com','ajluxe':'ajluxe.com','goodmorningamerica':'goodmorningamerica.com'}
def regdom(host):
    host=host.lower().split(':')[0]
    if host.startswith('www.'): host=host[4:]
    p=host.split('.')
    if len(p)>=3 and '.'.join(p[-2:]) in TWO: return '.'.join(p[-3:])
    return '.'.join(p[-2:]) if len(p)>=2 else host
def dropped(u):
    h=urlparse(u).netloc.lower().split(':')[0]
    return any(h==d or h.endswith('.'+d) for d in DROP_HOSTS)
def ts(s):
    s=(s or '').strip()
    return re.sub(r'\s*(UTC|Z)$','',s).replace('T',' ').split('.')[0]
def clean(l):
    l=l.strip().replace('®','').replace('™','')
    l=re.sub(r'^chip:\s*','',l,flags=re.I)
    l=re.sub(r'\s*\+\s*\d+\s*$','',l).strip()
    l=re.sub(r'\s*\(.*?\)\s*$','',l).strip()
    return l
def chip_labels(app,body,html,folder):
    if app=='chatgpt':
        labs=[]
        for m in re.finditer(r'\[([^\[\]]+)\]|^([A-Z][\w&\' .-]{1,40}?) \+\d+\s*$',body,re.M):
            t=m.group(1) or m.group(2)
            if m.group(1) and not (re.search(r'\+\d+\s*$',t) or t.lower().startswith('chip:')): continue  # skip buttons like [Shop Angara]
            labs.append(t)
        return labs
    if app=='claude':
        return re.findall(r'\[([a-z0-9.-]+)\]',body)
    if app=='gemini':
        labs=[H.unescape(x).strip() for x in re.findall(r'class="source-title"[^>]*>([^<]*)<',html)]
        cn=folder+'capture_notes.txt'
        if os.path.exists(cn):
            m=re.search(r'^citation_chips:\s*(.*)$',open(cn,encoding='utf-8').read(),re.M)
            if m and not m.group(1).lower().startswith('none'):
                notes=[clean(x) for x in m.group(1).split(';') if clean(x)]
                if len(set(map(str.lower,notes)))>len(set(map(str.lower,labs))): labs=notes
        return labs
    return []
A=[];M=[];C=[];T=[];W=[];read=[];skipped=[]
for app in ('chatgpt','claude','gemini'):
  for d in sorted(glob.glob(f'{RUN}raw/{app}/*/')):
    name=os.path.basename(d.rstrip('/'))
    if '__discarded' in name: skipped.append(name); continue
    read.append(name)
    meta=json.load(open(d+'meta.json',encoding='utf-8'))
    _,pid,rep,t=name.split('__'); turn=int(t[1:])
    rk=f'{app}|{pid}|{rep}|t{turn}'
    if meta.get('run_key')!=rk: W.append(f'{name}: meta.run_key {meta.get("run_key")} != folder')
    if meta.get('run_id')!=RUN_ID: W.append(f'{name}: meta.run_id {meta.get("run_id")}')
    body=open(d+'answer.txt',encoding='utf-8').read() if os.path.exists(d+'answer.txt') else ''
    hp=d+'answer.html'
    if os.path.exists(hp+'.gz'):
        import gzip; html=gzip.open(hp+'.gz','rb').read().decode('utf-8','replace')
    else: html=open(hp,encoding='utf-8').read() if os.path.exists(hp) else ''
    tsrc='answer'
    if not body.strip():
        body=H.unescape(re.sub(r'<[^>]+>',' ',html)); tsrc='page_copy'; W.append(f'{name}: answer.txt empty, used page_copy')
    key=dict(run_id=RUN_ID,run_key=rk,app=app,prompt_id=pid,repeat=rep,turn=turn)
    cits=[];seen=set()
    for u in re.findall(r'href\s*=\s*"([^"]*)"',html,re.I):
        u=H.unescape(u).strip()
        if not re.match(r'https?://',u,re.I) or dropped(u) or u in seen: continue
        seen.add(u); cits.append(dict(url=u,domain=regdom(urlparse(u).netloc),source_file='html',label=''))
    if not cits:  # chip fallback
        sd=set()
        for lab in chip_labels(app,body,html,d):
            n=clean(lab); dom=CHIPDOM.get(n.lower(),'')
            k=dom or n.lower()
            if not n or k in sd: continue
            sd.add(k)
            if not dom: W.append(f'{name}: chip label "{n}" domain not resolvable, left blank')
            cits.append(dict(url='',domain=dom,source_file='html_chip',label=n))
    for i,c in enumerate(cits,1):
        C.append({**key,'link_order':i,'url':c['url'],'domain':c['domain'],'is_angara':int(c['domain']=='angara.com'),'source_file':c['source_file'],'_label':c['label']})
    hits=[]
    for b,p in ALIASES:
        ms=list(p.finditer(body))
        if ms: hits.append((ms[0].start(),b,len(ms)))
    hits.sort()
    for o,(pos,b,n) in enumerate(hits,1):
        M.append({**key,'brand':b,'fact_row':1,'mention_count':n,'first_char_pos':pos,'order_of_first_appearance':o,'text_source':tsrc})
    am=[x.start() for x in re.finditer('angara',body,re.I)]
    si=meta.get('signed_in'); si=str(si).lower() if isinstance(si,bool) else str(si).strip().lower()
    ws=meta.get('web_search'); src=meta.get('source') or 'grok_bot_ui'
    if src not in ('grok_bot_ui','parallel_test','schedule','api'):
        W.append(f'{name}: meta.source "{src}" not in SCHEMA vocab; written as grok_bot_ui (captured_by={meta.get("captured_by")})'); src='grok_bot_ui'
    A.append({**key,'prompt':meta.get('prompt_sent',''),'captured_at_utc':ts(meta.get('captured_at_utc')),'signed_in':si,
      'session':meta.get('session') or '','egress_country':meta.get('egress_country') or '','source':src,
      'text_source':tsrc,'has_raw_folder':1,'answer_chars':len(body),'web_search_marker':int(ws is True or str(ws).lower()=='true'),
      'angara_in_text':int(bool(am)),'angara_mention_count':len(am),'angara_first_char_pos':am[0] if am else '',
      'n_brands_found':len(hits),'n_links':len(cits),'angara_link_present':int(any(c['domain']=='angara.com' for c in cits))})
    T.append(dict(run_id=RUN_ID,run_key=rk,answer_text=body,followup_answer_text=''))
json.dump(dict(A=A,M=M,C=C,T=T,W=W,read=read,skipped=skipped),open(OUT+'measured.json','w'),indent=1,ensure_ascii=False)
print(len(A),len(M),len(C),len(T),len(read),len(skipped))
for w in W: print('W',w)
for a in A: print(a['run_key'],a['answer_chars'],a['captured_at_utc'],'ws',a['web_search_marker'],'ang',a['angara_mention_count'],'nl',a['n_links'],'al',a['angara_link_present'],'|',' '.join(m['brand'] for m in M if m['run_key']==a['run_key']),'|',[c['_label'] for c in C if c['run_key']==a['run_key']])
