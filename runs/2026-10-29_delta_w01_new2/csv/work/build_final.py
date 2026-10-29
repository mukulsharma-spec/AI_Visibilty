import json,csv,re,collections,sys,datetime,os
RUN='2026-10-29_delta_w01_new2'
d=json.load(open('measured.json'))
A,M,C=d['A'],d['M'],d['C']
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
akeys=set(r['run_key'] for r in outA)
TKs=[t['run_key'] for t in d['T']]
if len(TKs)!=len(set(TKs)) or set(TKs)!=akeys: err.append('answer_text keys mismatch')
for nm,rows in [('brand_mentions',outM),('citations',outC)]:
    for r in rows:
        if r['run_key'] not in akeys: err.append(f'orphan {nm} {r["run_key"]}')
for r in outA:
    for x in ['ai_answer_format','ai_n_recommended','ai_angara_role']:
        if r[x]=='' : err.append(f'blank {x} {r["run_key"]}')
    if int(r['n_links'])!=len(cits[r['run_key']]): err.append('n_links '+r['run_key'])
    if bool(r['ai_angara_rank'])!=bool(r['ai_angara_rank_n']): err.append('rank pair '+r['run_key'])
# citation coverage: visible chip/source names but 0 rows
RAWD='/workspace/ai-visibility/runs/'+RUN+'/raw/'
for r in outA:
    if r['n_links'] not in (0,'0'): continue
    fd=RAWD+r['app']+'/%s__%s__%s__t%s/'%(r['app'],r['prompt_id'],r['repeat'],r['turn'])
    txt=open(fd+'answer.txt').read(); h=open(fd+'answer.html').read()
    cn=open(fd+'capture_notes.txt').read() if os.path.exists(fd+'capture_notes.txt') else ''
    vis=re.findall(r'\[[^\[\]]+\]|^\S.{0,40} \+\d+$',txt,re.M)
    vis=[v for v in vis if not v.lower().startswith(('[shop','[compare','[find','[browse','[view'))]
    if vis or 'source-title' in h or re.search(r'^citation_chips:[ \t]*(?![ \t]|none)\S',cn,re.M): err.append('coverage: visible chips but 0 citations '+r['run_key']+' '+str(vis[:3]))
if err: print('\n'.join(err));sys.exit(1)
TK=['run_id','run_key','answer_text','followup_answer_text']
outT=[{x:t[x] for x in TK} for t in d['T']]
for fn,K,rows in [('answers.csv',AK,outA),('brand_mentions.csv',MK,outM),('citations.csv',CK,outC),('answer_text.csv',TK,outT)]:
    with open('../'+fn,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,K,extrasaction='raise');w.writeheader();w.writerows(rows)
live=set(r['brand'] for r in csv.DictReader(open('/tmp/live233/brand_mentions.csv')))
new=sorted(set(r['brand'] for r in outM if r['fact_row']==0)-live)
bya=collections.defaultdict(lambda: collections.Counter())
for c in outC: bya[c['app']][c['source_file']]+=1
W=list(d['W'])+[
 'all citations are html_chip (url blank): no outbound hrefs in any answer.html (chatgpt/claude text_wrapped_html pre-wrap; gemini chips are buttons without hrefs). Chip rows deduped by domain within an answer (keep first); "+N" hidden sources not counted',
 'chatgpt chips parsed from answer.txt: [Name +N], bare "Name +N" lines (BR06) and [chip: Name] (CM05); button labels like [Shop Angara]/[Compare rings...] ignored. Shop links with utm_source=chatgpt.com noted in meta but not in HTML, so not counted',
 'chatgpt BR05: only Angara chips visible ([Angara +1], [Angara +4]) -> 1 citation row; meta notes a brilliantearth.com shop link that is not in HTML',
 'claude chips parsed from answer.txt bracket stems ([angara], [brilliantearth], [comparemaniac], [ajluxe], [goodmorningamerica]); domains mapped as <stem>.com',
 'claude BR08, CM05: meta says inline citation chip labels were removed from answer.txt at capture; CM04 web search used but no chips in text -> 0 citation rows (undercount vs UI). claude BR07: no web search',
 'gemini chips from answer.html .source-title + capture_notes citation_chips; BR07 Reddit chip had +2 hidden (Angara) per notes, counted once as Angara; CM05 duplicate Aurate deduped. Aurate mapped to auratenewyork.com, The Diamond Pro to diamondpro.com',
 'gemini BR08, CM04 meta web_search=false; BR06 web_search=true but no chips rendered',
 'chatgpt meta.source=friday_ui (not in SCHEMA vocab) written as grok_bot_ui; captured_by Friday',
 'chatgpt/gemini answer.txt includes inline source-chip labels, inflating measured mention_count (e.g. Angara)',
 'chatgpt BR08 meta mentions product cards in capture report but none visible in answer.txt; in_product_card=0 throughout',
 'chatgpt CM05 Target and chatgpt BR06 Rare Carat match aliases only via chip labels -> role cited_only',
 'all apps: egress IN (Faridabad 49.249.146.90), human-approved',
 'chatgpt BR05__discarded_1 skipped (contaminated first attempt)',
 'no turn 2 captured; followup_answer_text blank',
]
info=dict(run_id=RUN,builder='Grok Bot',script_version='build_csv v2.3.3',built_at_utc=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),apps=sorted(set(a['app'] for a in outA)),raw_folders_read=len(d['read']),folders_skipped_discarded=len(d['skipped']),skipped_folders=d['skipped'],run_info_mismatches=[],rows=dict(answers=len(outA),brand_mentions=len(outM),citations=len(outC),answer_text=len(outT)),citations_by_app={k:dict(v) for k,v in bya.items()},new_brand_names=new,warnings=W,loaded_to_live=False)
json.dump(info,open('../build_info.json','w'),indent=2,ensure_ascii=False)
print(info['rows'],collections.Counter(r['app'] for r in outA));print('fact0',sum(r['fact_row']==0 for r in outM));print('NEW',new)
print(info['citations_by_app'])
print(collections.Counter(r['ai_angara_role'] for r in outA))
for r in outA: print(r['run_key'],r['signed_in'],r['n_links'],r['ai_answer_format'],r['ai_n_recommended'],r['ai_n_rank_slots'],r['ai_angara_role'],r['ai_angara_rank'],r['ai_angara_rank_n'],r['ai_top1_brand'])
