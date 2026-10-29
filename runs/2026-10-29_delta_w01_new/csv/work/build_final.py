import json,csv,re,collections,sys,datetime
RUN='2026-10-29_delta_w01_new'
d=json.load(open('measured.json'))
A,M,C=d['A'],d['M'],d['C']
EXTRA_W=[]
# Gemini folders whose answer.html is empty: recover name-only chips from capture_notes.txt (labels also visible in answer.txt)
import os
RAW='/workspace/ai-visibility/runs/'+RUN+'/raw/gemini/'
livedoms=set(r['domain'] for r in csv.DictReader(open('/tmp/aiv/live_csv/citations.csv')) if r['domain'])|set(c['domain'] for c in C if c['domain'])
for a in A:
    if a['app']!='gemini' or a['n_links']: continue
    fd=RAW+'gemini__%s__%s__t%s/'%(a['prompt_id'],a['repeat'],a['turn'])
    if os.path.getsize(fd+'answer.html')>0 or not os.path.exists(fd+'capture_notes.txt'): continue
    ln=[l for l in open(fd+'capture_notes.txt') if l.startswith('citation_chips:')]
    if not ln: continue
    labs=[re.sub(r'\s*\+\s*\d+$','',x).strip() for x in ln[0].split(':',1)[1].split(';') if x.strip()]
    for i,lab in enumerate(labs,1):
        stem=re.sub(r'[^a-z0-9]','',lab.lower()); dom=next((x for x in sorted(livedoms) if x.split('.')[0].replace('-','')==stem),'')
        if not dom: EXTRA_W.append(f'{os.path.basename(fd[:-1])}: chip label "{lab}" domain not resolvable, left blank')
        C.append(dict(run_id=RUN,run_key=a['run_key'],app='gemini',prompt_id=a['prompt_id'],repeat=a['repeat'],turn=a['turn'],link_order=i,url='',domain=dom,is_angara=int(dom=='angara.com'),source_file='html_chip'))
    a['n_links']=len(labs); a['angara_link_present']=int(any(c['domain']=='angara.com' for c in C if c['run_key']==a['run_key']))
    EXTRA_W.append(f'{os.path.basename(fd[:-1])}: answer.html is 0 bytes; {len(labs)} html_chip rows recovered from capture_notes.txt citation_chips (labels also in answer.txt), not from HTML')
FMT=set("bullets bullets_by_category bullets_by_price_tier checklist clarifying_question comparison comparison_table headings local_map_list mixed numbered_headings numbered_list paragraphs paragraphs_bullets paragraphs_by_category paragraphs_by_price_tier product_cards product_cards_text_missing prose_bullets prose_by_category prose_paragraphs table".split())
ROLE=dict(R='recommended',C='compared_against',M='mentioned',O='cited_only',F='false_match')
SENT={'+':'positive','0':'neutral','-':'negative'};CONF=dict(h='high',m='medium',l='low')
labels={};fmt={};cur=None;err=[]
for ln in open('labels.txt',encoding='utf-8'):
    ln=ln.rstrip('\n')
    if not ln.strip() or ln.startswith('#'):continue
    if ln.startswith('@'):
        k,f=ln[1:].split(' fmt=');cur=k;fmt[k]=f;labels[k]=[];continue
    p=ln.split('|');assert len(p)==9,ln
    b,rk,tie,ro,card,price,claim,s,c=p
    fr=0 if b.startswith('+') else 1;b=b.lstrip('+')
    labels[cur].append(dict(brand=b,fact_row=fr,published_rank=rk,tie=tie or '0',role=ROLE[ro],in_product_card=card,price_shown_usd=price,claim=claim,sentiment=SENT[s],confidence=CONF[c]))
AK=['run_id','run_key','app','prompt_id','repeat','turn','prompt','captured_at_utc','signed_in','session','egress_country','source','text_source','has_raw_folder','answer_chars','web_search_marker','angara_in_text','angara_mention_count','angara_first_char_pos','n_brands_found','n_links','angara_link_present','ai_answer_format','ai_n_recommended','ai_n_rank_slots','ai_angara_role','ai_angara_published_rank','ai_angara_rank','ai_angara_rank_n','ai_top1_brand']
MK=['run_id','run_key','app','prompt_id','repeat','turn','brand','fact_row','mention_count','first_char_pos','order_of_first_appearance','text_source','published_rank','tie','role','in_product_card','price_shown_usd','claim','sentiment','confidence']
CK=['run_id','run_key','app','prompt_id','repeat','turn','link_order','url','domain','is_angara','source_file']
bl=lambda v:'' if v is None else v
mby=collections.defaultdict(dict)
for m in M: mby[m['run_key']][m['brand']]=m
cits=collections.defaultdict(list)
for c in C: cits[c['run_key']].append(c)
outA=[];outM=[]
keys=set(a['run_key'] for a in A)
for k in labels:
    if k not in keys: err.append('label for unknown answer '+k)
for a in A:
    k=a['run_key']
    if k not in labels: err.append('no label block '+k);continue
    if fmt[k] not in FMT: err.append('bad fmt '+k)
    L=labels[k];seen=set()
    for l in L:
        if l['brand'] in seen: err.append(f'dup brand {k} {l["brand"]}')
        seen.add(l['brand'])
        if l['fact_row']==1 and l['brand'] not in mby[k]: err.append(f'fact_row=1 label not measured {k} {l["brand"]}')
        if l['fact_row']==0 and l['brand'] in mby[k]: err.append(f'fact_row=0 but alias matched {k} {l["brand"]}')
        if (l['role']=='recommended')!=(l['published_rank']!=''): err.append(f'rank/role mismatch {k} {l["brand"]}')
        if len(l['claim'].split())>15: err.append(f'claim>15 {k} {l["brand"]}')
    for b in mby[k]:
        if b not in seen: err.append(f'measured brand unlabeled {k} {b}')
    for l in L:
        m=mby[k].get(l['brand'],{})
        r={x:a[x] for x in MK[:6]}
        r.update(brand=l['brand'],fact_row=l['fact_row'])
        for x in ['mention_count','first_char_pos','order_of_first_appearance','text_source']: r[x]=bl(m.get(x)) if l['fact_row']==1 else ''
        for x in MK[12:]: r[x]=l[x]
        outM.append(r)
    rec=[l for l in L if l['role']=='recommended']
    ranks=[int(l['published_rank']) for l in rec]
    ang=[l for l in L if l['brand']=='Angara']
    r={x:bl(a.get(x)) for x in AK[:22]}
    r['ai_answer_format']=fmt[k];r['ai_n_recommended']=len(rec);r['ai_n_rank_slots']=max(ranks) if ranks else ''
    if ang: role=ang[0]['role']
    elif str(a.get('angara_link_present'))=='1': role='cited_only'
    else: role='absent'
    r['ai_angara_role']=role
    arank=ang[0]['published_rank'] if ang and ang[0]['role']=='recommended' else ''
    r['ai_angara_published_rank']=arank
    r['ai_angara_rank']=arank
    r['ai_angara_rank_n']=r['ai_n_rank_slots'] if arank else ''
    if arank and not (1<=int(arank)<=int(r['ai_angara_rank_n'])): err.append('rank range '+k)
    r['ai_top1_brand']=';'.join(l['brand'] for l in rec if l['published_rank']=='1')
    outA.append(r)
outC=[{x:bl(c.get(x)) for x in CK} for c in C]
# checks
for name,rows,uk in [('answers',outA,['run_key']),('brand_mentions',outM,['run_key','brand']),('citations',outC,['run_key','link_order'])]:
    ks=[tuple(r[x] for x in uk) for r in rows]
    if len(ks)!=len(set(ks)): err.append('dup keys '+name)
    for r in rows:
        if r['run_id']!=RUN: err.append('run_id '+name)
for r in outA:
    if r['signed_in'] not in ('true','false'): err.append('signed_in '+r['run_key']+' '+str(r['signed_in']))
if err: print('\n'.join(err));sys.exit(1)
for fn,K,rows in [('answers.csv',AK,outA),('brand_mentions.csv',MK,outM),('citations.csv',CK,outC)]:
    with open('../'+fn,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,K,extrasaction='raise');w.writeheader();w.writerows(rows)
live=set(r['brand'] for r in csv.DictReader(open('/tmp/aiv/live_csv/brand_mentions.csv')))
new=sorted(set(r['brand'] for r in outM if r['fact_row']==0)-live)
W=list(d['W'])+EXTRA_W+[
 'gemini: meta.json files were synthesized by check · collector after the stop ("verify before scoring"); captured_at_utc is a placeholder 2026-10-29 07:38:00 for all 3 (not real per-prompt times); meta model_ui says "not shown" while capture_notes say Flash-Lite',
 'gemini: no run_info_gemini.json/SUMMARY_gemini.md were written at capture; written at build time from metas + capture_notes',
 'gemini citations are name-only source chips (url blank, source_file=html_chip)',
 'chatgpt: 0 citations - answer.html is a text-wrapped <pre> with no hrefs (capture_quality=text_wrapped_html). answer.txt shows source chips not counted as citations: OC21 [Angara],[USA Jewels],[Earth\'s Treasury +1]; SG14 [Brilliant Earth],[Setting - Montana Sapphire Ring Co.],[Aquamarise],[Cape Cod Jewelers]; ST23 [Aquamarise +1]. So chatgpt angara_link_present=0 understates OC21 (Angara chip visible)',
 'chatgpt: all 3 chats landed on /uc/ URLs (not /c/); answers were fully on screen and saved per human instruction',
 'chatgpt/gemini answer.txt includes inline source-chip labels, inflating measured mention_count (e.g. Angara)',
 'all apps: egress IN (Faridabad 49.249.146.90), human said location does not matter for this run; claude signed_in=true (Incognito chat), chatgpt/gemini signed out',
 'claude SG14: "A Nueva Jewelry" labeled with live spelling "Anueva Jewelry"; "Fay Wolf Cross Jewelry (fwcj.com)" labeled with live spelling "Shop FWCJ"',
]
info=dict(run_id=RUN,builder='Grok Bot',script_version='build_csv v2.2',built_at_utc=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),apps=sorted(set(a['app'] for a in outA)),raw_folders_read=len(d['read']),folders_skipped_discarded=len(d['skipped']),skipped_folders=d['skipped'],run_info_mismatches=[],rows=dict(answers=len(outA),brand_mentions=len(outM),citations=len(outC)),new_brand_names=new,warnings=W,loaded_to_live=False)
json.dump(info,open('../build_info.json','w'),indent=2,ensure_ascii=False)
print(info['rows'],collections.Counter(r['app'] for r in outA));print('fact0',sum(r['fact_row']==0 for r in outM));print('NEW',new)
print(collections.Counter(r['ai_angara_role'] for r in outA))
