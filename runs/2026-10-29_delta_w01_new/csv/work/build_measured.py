# build_csv v2 (measured) for 2026-10-29_delta_w01_new — reads raw/, writes csv/work/*.json only
import csv,re,os,json,glob,base64,html as H
from urllib.parse import urlparse
BASE='/workspace/ai-visibility/'
RUN_ID='2026-10-29_delta_w01_new'
RUN=BASE+'runs/'+RUN_ID+'/'
OUT=RUN+'csv/work/'
ALIASES=[(r['brand'],re.compile(r['pattern'],re.I)) for r in csv.DictReader(open(BASE+'inputs/brand_aliases_v3.csv',encoding='utf-8'))]
DROP_HOSTS=('chatgpt.com','chat.openai.com','openai.com','claude.ai','anthropic.com','gemini.google.com','accounts.google.com','support.google.com','policies.google.com')
TWO=('co.uk','com.au','co.nz','co.in','com.br','co.jp','com.sg','co.za','org.uk','ac.uk','com.mx','com.hk')
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
    s=re.sub(r'\s*(UTC|Z)$','',s).replace('T',' ').split('.')[0]
    return s
A=[];M=[];C=[];W=[];read=[];skipped=[]
def readtxt(path,name):
    b=open(path,'rb').read()
    try: return b.decode('utf-8')
    except UnicodeDecodeError:
        W.append(f'{name}: {os.path.basename(path)} not UTF-8; decoded as cp1252 (Windows-1252 punctuation)'); return b.decode('cp1252')
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
    body=readtxt(d+'answer.txt',name) if os.path.exists(d+'answer.txt') else ''
    hp=d+'answer.html'
    if os.path.exists(hp+'.gz'):
        import gzip; html=gzip.open(hp+'.gz','rb').read().decode('utf-8','replace')
    else: html=readtxt(hp,name) if os.path.exists(hp) else ''
    tsrc='answer'
    if not body.strip():
        body=H.unescape(re.sub(r'<[^>]+>',' ',html)); tsrc='page_copy'; W.append(f'{name}: answer.txt empty, used page_copy')
    key=dict(run_id=RUN_ID,run_key=rk,app=app,prompt_id=pid,repeat=rep,turn=turn)
    # citations
    cits=[];seen=set()
    for m in re.finditer(r'<source-inline-chip\b.*?</source-inline-chip>|href\s*=\s*"([^"]*)"',html,re.S|re.I):
        if m.group(0).lower().startswith('<source-inline-chip'):
            chip=m.group(0)
            lab=re.search(r'class="source-title"[^>]*>([^<]*)<',chip)
            lab=H.unescape(lab.group(1)).strip() if lab else ''
            dom=''
            if re.fullmatch(r'(?:[a-z0-9-]+\.)+[a-z]{2,}',lab.lower()): dom=regdom(lab)
            else:
                # recognizable label: confirm via the chip's own source metadata in the HTML
                stem=re.sub(r'[^a-z0-9]','',lab.lower())
                for b in re.findall(r'BardVeMetadataKey:([A-Za-z0-9+/=]+)',chip):
                    try: dec=base64.b64decode(b+'==').decode('utf-8','ignore')
                    except Exception: continue
                    for u in re.findall(r'https?://[^"\\\]]+',dec):
                        rd=regdom(urlparse(u).netloc)
                        if stem and stem in rd.replace('-','').replace('.',''): dom=rd; break
                    if dom: break
                if not dom and lab: W.append(f'{name}: chip label "{lab}" domain not resolvable, left blank')
            cits.append(dict(url='',domain=dom,source_file='html_chip',label=lab))
        else:
            u=H.unescape(m.group(1)).strip()
            if not re.match(r'https?://',u,re.I): continue
            if dropped(u) or u in seen: continue
            seen.add(u); cits.append(dict(url=u,domain=regdom(urlparse(u).netloc),source_file='html'))
    for i,c in enumerate(cits,1):
        C.append({**key,'link_order':i,'url':c['url'],'domain':c['domain'],'is_angara':int(c['domain']=='angara.com'),'source_file':c['source_file'],'_label':c.get('label','')})
    # brands
    hits=[]
    for b,p in ALIASES:
        ms=list(p.finditer(body))
        if ms: hits.append((ms[0].start(),b,len(ms)))
    hits.sort()
    for o,(pos,b,n) in enumerate(hits,1):
        ctx=body[max(0,pos-80):pos+120].replace('\n',' ')
        M.append({**key,'brand':b,'fact_row':1,'mention_count':n,'first_char_pos':pos,'order_of_first_appearance':o,'text_source':tsrc,'_ctx':ctx})
    am=[x.start() for x in re.finditer('angara',body,re.I)]
    si=meta.get('signed_in'); si=str(si).lower() if isinstance(si,bool) else str(si).strip().lower()
    ws=meta.get('web_search')
    A.append({**key,'prompt':meta.get('prompt_sent',''),'captured_at_utc':ts(meta.get('captured_at_utc')),'signed_in':si,
      'session':meta.get('session') or '','egress_country':meta.get('egress_country') or '','source':meta.get('source') or 'grok_bot_ui',
      'text_source':tsrc,'has_raw_folder':1,'answer_chars':len(body),'web_search_marker':int(ws is True or str(ws).lower()=='true'),
      'angara_in_text':int(bool(am)),'angara_mention_count':len(am),'angara_first_char_pos':am[0] if am else '',
      'n_brands_found':len(hits),'n_links':len(cits),'angara_link_present':int(any(c['domain']=='angara.com' for c in cits)),
      '_quality':meta.get('capture_quality'),'_raw_ts':meta.get('captured_at_utc')})
json.dump(dict(A=A,M=M,C=C,W=W,read=read,skipped=skipped),open(OUT+'measured.json','w'),indent=1,ensure_ascii=False)
print(len(A),len(M),len(C),len(read),len(skipped))
for w in W: print('W',w)
for a in A: print(a['run_key'],a['answer_chars'],a['captured_at_utc'],'ws',a['web_search_marker'],'ang',a['angara_mention_count'],'nb',a['n_brands_found'],'nl',a['n_links'],'al',a['angara_link_present'],a['_quality'])
