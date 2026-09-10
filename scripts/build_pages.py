from pathlib import Path
import json, html, re
ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/'articles/catalog.json'
items=json.loads(CAT.read_text(encoding='utf-8'))
def datekey(x):
 import datetime
 m=re.match(r'(\d{1,2}) de ([a-zç]+) de (\d{4})',x.get('date','').lower())
 months={'janeiro':1,'fevereiro':2,'março':3,'abril':4,'maio':5,'junho':6,'julho':7,'agosto':8,'setembro':9,'outubro':10,'novembro':11,'dezembro':12}
 return datetime.date(int(m.group(3)),months.get(m.group(2),1),int(m.group(1))) if m else datetime.date.min
items=sorted(items,key=datekey,reverse=True)
def card(x): return f'''<a class="card" href="articles/{html.escape(x['file'])}"><div class="card-img" style="background-image:url('{html.escape(x['image'],quote=True)}')"></div><div class="card-body"><span class="tag">{html.escape(x['category'])}</span><h3>{html.escape(x['title'])}</h3><div class="meta">{html.escape(x['date'])}</div></div></a>'''
def listitem(x): return f'''<a class="list-item" href="articles/{html.escape(x['file'])}"><div class="card-img" style="background-image:url('{html.escape(x['image'],quote=True)}')"></div><div><span class="tag">{html.escape(x['category'])}</span><h3>{html.escape(x['title'])}</h3><div class="meta">{html.escape(x['date'])}</div><p>{html.escape(x.get('lead',''))}</p></div></a>'''
for name, marker, fn in [('index.html','AUTO:NEWS',card),('noticias.html','AUTO:NEWS',listitem)]:
 p=ROOT/name; s=p.read_text(encoding='utf-8'); start='<!-- '+marker+' START -->'; end='<!-- '+marker+' END -->'; body='\n'.join(fn(x) for x in items)
 s=re.sub(re.escape(start)+r'.*?'+re.escape(end),start+body+end,s,flags=re.S)
 p.write_text(s,encoding='utf-8')
print('Updated pages with',len(items),'articles')
