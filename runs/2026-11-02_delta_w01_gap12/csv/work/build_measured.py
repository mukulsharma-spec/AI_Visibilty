# build_csv v2.3.3 (measured) for 2026-11-02_delta_w01_gap12 — reads raw/ (read-only), writes csv/work/measured.json
import csv,re,os,json,glob,html as H,datetime
from urllib.parse import urlparse
BASE='/workspace/ai-visibility/'
RUN_ID='2026-11-02_delta_w01_gap12'
RUN=BASE+'runs/'+RUN_ID+'/'
OUT=RUN+'csv/work/'
SUFFIX=" I'm shopping in the USA."
PROMPTS={r['prompt_id']:r['prompt_text'] for r in csv.DictReader(open(BASE+'inputs/run_lists/prompts_delta_2026-11-02_w01_gap12.csv',encoding='utf-8'))}
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
def normurl(u):
    u=H.unescape(u).strip()
    return re.sub(r'#:~:text=.*$','',u)   # strip Chrome text fragments (Gemini panel) -> dedupe
def ts(s):
    s=(s or '').strip()
    return re.sub(r'\s*(UTC|Z)$','',s.replace('Z','')).replace('T',' ').split('.')[0]
A=[];M=[];C=[];T=[];W=[];read=[];skipped=[];ORIG={}
for app in ('chatgpt','claude','gemini'):
  for d in sorted(glob.glob(f'{RUN}raw/{app}/*/')):
    name=os.path.basename(d.rstrip('/'))
    if '__discarded' in name: skipped.append(name); continue
    read.append(name)
    meta=json.load(open(d+'meta.json',encoding='utf-8'))
    _,pid,rep,t=name.split('__'); turn=int(t[1:])
    rk=f'{app}|{pid}|{rep}|t{turn}'
    if meta.get('run_key') and meta['run_key']!=rk: W.append(f'{name}: meta.run_key {meta.get("run_key")} != folder')
    body=open(d+'answer.txt',encoding='utf-8').read()
    html=open(d+'answer.html',encoding='utf-8').read() if os.path.exists(d+'answer.html') else ''
    tsrc='answer'
    if not body.strip():
        body=H.unescape(re.sub(r'<[^>]+>',' ',html)); tsrc='page_copy'; W.append(f'{name}: answer.txt empty, used page_copy')
    key=dict(run_id=RUN_ID,run_key=rk,app=app,prompt_id=pid,repeat=rep,turn=turn)
    # citations: folder citations.csv first
    cits=[];seen=set();orig=[];dups=0
    for r in csv.DictReader(open(d+'citations.csv',encoding='utf-8')):
        u=normurl(r.get('url',''))
        if u and (not re.match(r'https?://',u,re.I) or dropped(u)): continue
        k=u or ('chip:'+(r.get('domain') or r.get('source_name','')).lower())
        if k in seen: dups+=1; continue
        seen.add(k)
        dom=regdom(urlparse(u).netloc) if u else regdom(r.get('domain',''))
        cits.append(dict(url=u,domain=dom,source_file='html' if u else 'html_chip'))
        orig.append(r.get('source_file',''))
    if dups: W.append(f'{name}: {dups} duplicate citation rows dropped (dedupe by URL{" after stripping #:~:text fragments" if app=="gemini" else ""})')
    if not cits:  # fallback: hrefs in answer.html
        for u in re.findall(r'href\s*=\s*"([^"]*)"',html,re.I):
            u=normurl(u)
            if not re.match(r'https?://',u,re.I) or dropped(u) or u in seen: continue
            seen.add(u); cits.append(dict(url=u,domain=regdom(urlparse(u).netloc),source_file='html')); orig.append('answer_html_href')
        if cits: W.append(f'{name}: folder citations.csv empty; {len(cits)} rows from answer.html hrefs')
    ORIG[rk]=orig
    for i,c in enumerate(cits,1):
        C.append({**key,'link_order':i,'url':c['url'],'domain':c['domain'],'is_angara':int(c['domain']=='angara.com'),'source_file':c['source_file']})
    hits=[]
    for b,p in ALIASES:
        ms=list(p.finditer(body))
        if ms: hits.append((ms[0].start(),b,len(ms)))
    hits.sort()
    for o,(pos,b,n) in enumerate(hits,1):
        M.append({**key,'brand':b,'fact_row':1,'mention_count':n,'first_char_pos':pos,'order_of_first_appearance':o,'text_source':tsrc})
    am=[x.start() for x in re.finditer('angara',body,re.I)]
    si=meta.get('signed_in')
    if si is None:
        si = 'true' if app=='claude' else 'false'
        W.append(f'{name}: meta.signed_in missing; set {si} (Claude captured signed-in Incognito per BRIEF)')
    else: si=str(si).lower()
    cap=meta.get('captured_at_utc')
    if not cap or len(str(cap))<=10:
        cap=datetime.datetime.utcfromtimestamp(os.path.getmtime(d+'answer.txt')).strftime('%Y-%m-%d %H:%M:%S')
        W.append(f'{name}: meta has date only; captured_at_utc approximated from answer.txt mtime ({cap})')
    sess=meta.get('session') or ''
    if sess=='claude_incognito': sess='claude_incognito_chat'
    ws=meta.get('web_search')
    A.append({**key,'prompt':meta.get('prompt_sent') or PROMPTS[pid]+SUFFIX,'captured_at_utc':ts(cap),'signed_in':si,
      'session':sess,'egress_country':'IN','source':'grok_bot_ui',
      'text_source':tsrc,'has_raw_folder':1,'answer_chars':len(body),'web_search_marker':int(ws is True or str(ws).lower()=='true'),
      'angara_in_text':int(bool(am)),'angara_mention_count':len(am),'angara_first_char_pos':am[0] if am else '',
      'n_brands_found':len(hits),'n_links':len(cits),'angara_link_present':int(any(c['domain']=='angara.com' for c in cits))})
    T.append(dict(run_id=RUN_ID,run_key=rk,answer_text=body,followup_answer_text=''))
json.dump(dict(A=A,M=M,C=C,T=T,W=W,read=read,skipped=skipped,ORIG=ORIG),open(OUT+'measured.json','w'),indent=1,ensure_ascii=False)
print(len(A),len(M),len(C),len(T),len(read),len(skipped))
for w in W: print('W',w)
for a in A: print(a['run_key'],a['answer_chars'],a['captured_at_utc'],a['signed_in'],'ws',a['web_search_marker'],'ang',a['angara_mention_count'],'nl',a['n_links'],'al',a['angara_link_present'],'|',' '.join(m['brand'] for m in M if m['run_key']==a['run_key']))
