import sys,json,os,html,csv,datetime
d=json.load(open(sys.argv[1]))
pid=d['pid']
R='/workspace/ai-visibility/runs/2026-11-04_delta_w02_uk/raw/gemini/'
f=R+f'gemini__{pid}__r1__t1/'
os.makedirs(f,exist_ok=True)
import re
raw=d['answer'].split('\n')
lines=[]
for i,l in enumerate(raw):
    if re.fullmatch(r'\+ \d+',l) or (i>0 and raw[i-1].endswith('   ') and l in d.get('chips',[])): continue
    lines.append(l.rstrip())
d['answer']=re.sub(r'\n{3,}','\n\n','\n'.join(lines))
open(f+'answer.txt','w').write(d['answer'].strip()+'\n')
paras=[p for p in d['answer'].strip().split('\n\n')]
open(f+'answer.html','w').write('<div class="markdown">'+''.join('<p>'+html.escape(p).replace('\n','<br>')+'</p>' for p in paras)+'</div>\n')
rows=d['rows']
open(f+'sources_panel.html','w').write('<div class="sources-panel">'+''.join('<a href="%s"><span class="name">%s</span><span class="domain">%s</span><span class="title">%s</span><span class="snippet">%s</span></a>'%(html.escape(r['url']),html.escape(r['name']),html.escape(r['domain']),html.escape(r['title']),html.escape(r['snip'])) for r in rows)+'</div>\n')
with open(f+'citations.csv','w',newline='') as c:
    w=csv.writer(c);w.writerow('prompt_id,app,source_name,domain,url,source_file'.split(','))
    for r in rows:w.writerow([pid,'gemini',r['name'],r['domain'],r['url'],'html_sources_panel'])
m=dict(run_id='2026-11-04_delta_w02_uk',run_key=f'gemini|{pid}|r1|t1',app='gemini',prompt_id=pid,repeat='r1',turn=1,date='2026-11-04',prompt_sent=d['prompt'],source='grok_bot_ui',captured_by='check · collector',captured_at_utc=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),signed_in=False,session='signed_out_shared_profile',ip='49.249.146.90',egress_ip='49.249.146.90',egress_city='Gurugram',egress_country='IN',web_search=True,model_ui='Flash-Lite',chat_url=d['url'],capture_quality='text_reconstructed_html',notes=f'cites={len(rows)}; answer.html/sources_panel.html reconstructed from DOM text; egress IN not GB; Incognito unavailable; urls stored without #:~:text fragments; chip labels stripped from answer.txt'+d.get('extra',''))
json.dump(m,open(f+'meta.json','w'),indent=2,ensure_ascii=False)
