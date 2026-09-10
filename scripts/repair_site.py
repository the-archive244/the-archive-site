from pathlib import Path
import json,re,html,datetime
ROOT=Path(__file__).resolve().parents[1]; ART=ROOT/'articles'; CAT=ART/'catalog.json'
MONTHS={'janeiro':1,'fevereiro':2,'março':3,'abril':4,'maio':5,'junho':6,'julho':7,'agosto':8,'setembro':9,'outubro':10,'novembro':11,'dezembro':12}

def strip_tags(s): return re.sub(r'<[^>]+>',' ',s or '').replace('&nbsp;',' ').strip()
def datekey(x):
    m=re.search(r'(\d{1,2}) de ([a-zç]+) de (\d{4})',x.get('date','').lower())
    return datetime.date(int(m.group(3)),MONTHS.get(m.group(2),1),int(m.group(1))) if m else datetime.date.min

def extract(path):
    s=path.read_text(encoding='utf-8',errors='ignore')
    title=re.search(r'<title>(.*?)</title>',s,re.I|re.S)
    title=strip_tags(title.group(1)) if title else path.stem.replace('-',' ').title()
    title=re.sub(r'\s*\|\s*THE ARCHIVE.*$','',title,flags=re.I)
    img=re.search(r'<(?:img|source)[^>]+(?:src|data-src)=["\']([^"\']+)',s,re.I)
    image=img.group(1) if img else ''
    if not image:
        m=re.search(r'background-image\s*:\s*url\(["\']?([^\)"\']+)',s,re.I); image=m.group(1) if m else ''
    meta=re.search(r'<div[^>]*class=["\'][^"\']*eyebrow[^"\']*["\'][^>]*>(.*?)</div>',s,re.I|re.S)
    raw=strip_tags(meta.group(1)) if meta else 'Notícias'
    bits=[b.strip() for b in raw.split('•')]
    category=bits[0].title() if bits else 'Notícias'; date=bits[1] if len(bits)>1 else ''
    if not date:
        m=re.search(r'(\d{1,2} de [a-zç]+ de \d{4})',s,re.I); date=m.group(1) if m else ''
    lead=re.search(r'<p[^>]*class=["\'][^"\']*article-lead[^"\']*["\'][^>]*>(.*?)</p>',s,re.I|re.S)
    lead=strip_tags(lead.group(1)) if lead else ''
    return {'file':path.name,'title':title,'category':category,'date':date,'image':image,'lead':lead}

def load_catalog():
    old=[]
    if CAT.exists():
        try: old=json.loads(CAT.read_text(encoding='utf-8'))
        except Exception: old=[]
    byfile={x.get('file'):x for x in old if x.get('file')}
    for p in sorted(ART.glob('*.html')):
        if p.name in ('catalog.html',): continue
        x=extract(p); prev=byfile.get(p.name,{})
        for k,v in x.items():
            if v: prev[k]=v
        byfile[p.name]=prev
    items=list(byfile.values())
    items.sort(key=datekey,reverse=True)
    CAT.write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
    return items

def card(x):
    image=x.get('image','')
    bg=f" style=\"background-image:url('{html.escape(image,quote=True)}')\"" if image else ''
    return f'''<a class="card" href="articles/{html.escape(x['file'])}"><div class="thumb"{bg}><span>{html.escape(x.get('category','NOTÍCIAS').upper())}</span></div><div class="card-body"><h3>{html.escape(x['title'])}</h3><div class="meta">{html.escape(x.get('date',''))}</div></div></a>'''

def listitem(x):
    image=x.get('image',''); bg=f" style=\"background-image:url('{html.escape(image,quote=True)}')\"" if image else ''
    return f'''<a class="list-item" href="articles/{html.escape(x['file'])}"><div class="thumb"{bg}></div><div><span class="tag">{html.escape(x.get('category','NOTÍCIAS'))}</span><h3>{html.escape(x['title'])}</h3><div class="meta">{html.escape(x.get('date',''))}</div><p>{html.escape(x.get('lead',''))}</p></div></a>'''

def replace_or_insert(path, body, mode):
    s=path.read_text(encoding='utf-8',errors='ignore')
    start='<!-- AUTO:NEWS START -->'; end='<!-- AUTO:NEWS END -->'
    block=start+'\n'+body+'\n'+end
    if start in s and end in s:
        s=re.sub(re.escape(start)+r'.*?'+re.escape(end),block,s,flags=re.S)
    elif mode=='index':
        # Replace only the cards container inside the Últimas notícias section.
        pat=r'(<section[^>]+id=["\']noticias["\'][\s\S]*?<div[^>]+class=["\']cards["\'])>[\s\S]*?(</div>\s*<div[^>]+class=["\']side["\'])'
        m=re.search(pat,s,re.I)
        if m:
            s=s[:m.start()]+m.group(1)+'>'+block+m.group(2)+s[m.end():]
        else:
            raise SystemExit('Não encontrei a área de notícias da home. Nada foi apagado.')
    elif mode=='noticias':
        m=re.search(r'(<main[\s\S]*?)(</main>)',s,re.I)
        if m:
            s=s[:m.start(1)]+m.group(1)+block+s[m.end(1):]
    path.write_text(s,encoding='utf-8')

items=load_catalog()
replace_or_insert(ROOT/'index.html','\n'.join(card(x) for x in items[:8]),'index')
if (ROOT/'noticias.html').exists(): replace_or_insert(ROOT/'noticias.html','\n'.join(listitem(x) for x in items),'noticias')
# Fix every article logo/favicon path without changing article content.
for p in ART.glob('*.html'):
    s=p.read_text(encoding='utf-8',errors='ignore')
    s=re.sub(r'(href=["\'])\.\./(?:icon|logo)\.svg(["\'])',r'\1../assets/logo.png\2',s,flags=re.I)
    s=re.sub(r'(src=["\'])\.\./(?:icon|logo)\.svg(["\'])',r'\1../assets/logo.png\2',s,flags=re.I)
    if 'assets/logo.png' not in s and '<body' in s:
        s=s.replace('<body>','<body><a href="../index.html" aria-label="THE ARCHIVE"><img src="../assets/logo.png" alt="THE ARCHIVE" style="height:52px;width:auto;margin:18px 24px"></a>',1)
    p.write_text(s,encoding='utf-8')
print(f'REPAIR OK: {len(items)} matérias preservadas e páginas regeneradas.')
