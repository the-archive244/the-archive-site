#!/usr/bin/env python3
import os,re,json,html,urllib.request,urllib.parse,datetime
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]; ART=ROOT/'articles'; CAT=ART/'catalog.json'
API=os.getenv('OPENAI_API_KEY'); MODEL=os.getenv('OPENAI_MODEL','gpt-4.1-mini')
FEEDS=[
 'Brasil investigação desaparecimento polícia crime quando:7d',
 'Brasil feminicídio investigação polícia quando:7d',
 'Brasil mistério fenômeno estranho quando:7d',
 'Brasil descoberta curiosidade ciência história quando:7d']

def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'THE-ARCHIVE-AUTO/2.0'}),timeout=30).read()
def feed(q):
 u='https://news.google.com/rss/search?q='+urllib.parse.quote(q)+'&hl=pt-BR&gl=BR&ceid=BR:pt-419'
 out=[]
 try:
  r=ET.fromstring(get(u))
  for i in r.findall('.//item')[:12]:
   t=(i.findtext('title') or '').strip(); l=(i.findtext('link') or '').strip(); d=re.sub('<[^>]+>',' ',i.findtext('description') or '').strip()
   if t and l: out.append({'title':t,'url':l,'description':d[:900]})
 except Exception as e: print('RSS:',e)
 return out

def ask(prompt):
 body={'model':MODEL,'tools':[{'type':'web_search_preview'}],'input':prompt}
 req=urllib.request.Request('https://api.openai.com/v1/responses',data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+API,'Content-Type':'application/json'})
 r=json.loads(urllib.request.urlopen(req,timeout=240).read())
 return r.get('output_text','')
def slug(s):
 import unicodedata
 s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower(); return re.sub(r'[^a-z0-9]+','-',s).strip('-')[:72]
def valid_image(u):
 if not u or not u.startswith(('http://','https://')): return False
 try:
  r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'THE-ARCHIVE-AUTO/2.0'}),timeout=20)
  return ('image' in (r.headers.get('Content-Type') or '').lower()) or u.lower().split('?')[0].endswith(('.jpg','.jpeg','.png','.webp'))
 except: return False

def main():
 if not API: print('OPENAI_API_KEY ausente: reparo continua funcionando, publicação automática aguardará a chave.'); return
 catalog=json.loads(CAT.read_text(encoding='utf-8')) if CAT.exists() else []
 existing='\n'.join(x.get('title','')+' | '+x.get('file','') for x in catalog)
 candidates=[]
 for q in FEEDS: candidates += feed(q)
 prompt=f'''Você é editor-chefe do THE ARCHIVE, portal brasileiro independente. Escolha UMA pauta nova entre os candidatos, publicada/atualizada nos últimos 7 dias. Priorize fatos verificáveis, interesse público e temas de Notícias, Investigações, Mistérios, Curiosidades ou Histórias. NÃO repita nenhuma matéria já publicada abaixo. Em crime, jamais trate suspeito/acusado como condenado. Exija pelo menos duas fontes independentes quando possível e uma fonte oficial quando existir. Só publique se houver uma imagem pública verificável; se não houver, use publish=false. Não invente URLs, nomes, datas, números ou imagens. Gere texto original, sem copiar fontes. Responda SOMENTE JSON válido com title,slug,category,date,lead,image,credit,sections (array com heading e paragraphs),sources (array com name e url),publish,reason. Data em português brasileiro.

JÁ PUBLICADAS:\n{existing}\n\nCANDIDATOS:\n{json.dumps(candidates[:40],ensure_ascii=False)}'''
 raw=ask(prompt).strip(); raw=re.sub(r'^```(?:json)?\s*|\s*```$','',raw,flags=re.S)
 try: data=json.loads(raw)
 except Exception as e: print('JSON inválido:',e); return
 if not data.get('publish'): print('Nenhuma publicação:',data.get('reason','')); return
 fname=slug(data.get('slug') or data.get('title'))+'.html'
 if any(x.get('file')==fname or x.get('title','').strip().lower()==data.get('title','').strip().lower() for x in catalog): print('Duplicata bloqueada.'); return
 if not valid_image(data.get('image','')): print('Imagem não validada. Publicação bloqueada.'); return
 esc=lambda x:html.escape(str(x),quote=True)
 sections=''.join('<h2>'+esc(s.get('heading',''))+'</h2>'+''.join('<p>'+esc(p)+'</p>' for p in s.get('paragraphs',[])) for s in data.get('sections',[]))
 sources=''.join('<li><a href="'+esc(s.get('url',''))+'" target="_blank" rel="noopener">'+esc(s.get('name','Fonte'))+'</a></li>' for s in data.get('sources',[]))
 doc=f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{esc(data.get('lead',''))}"><title>{esc(data['title'])} | THE ARCHIVE</title><link rel="icon" href="../assets/icon.png"><link rel="stylesheet" href="../style.css"></head><body><header class="topbar"><div class="container nav"><a class="brand" href="../index.html"><img src="../assets/logo.png" alt="THE ARCHIVE"></a><nav class="menu"><a href="../index.html">INÍCIO</a><a class="active" href="../noticias.html">NOTÍCIAS</a><a href="../misterios.html">MISTÉRIOS</a><a href="../curiosidades.html">CURIOSIDADES</a><a href="../historias.html">HISTÓRIAS</a><a href="../parceiros.html">CANAIS PARCEIROS</a></nav></div></header><main class="section"><div class="container article"><div class="eyebrow">{esc(str(data.get('category','Notícias')).upper())} • {esc(data.get('date',''))}</div><h1>{esc(data['title'])}</h1><p class="article-lead">{esc(data.get('lead',''))}</p><div class="meta">THE ARCHIVE • Atualizado em {esc(data.get('date',''))}</div><img class="article-cover" src="{esc(data['image'])}" alt="{esc(data['title'])}"><p>{esc(data.get('credit','Imagem: fonte consultada.'))}</p><div class="article-body">{sections}</div><div class="sources"><h3>Fontes consultadas</h3><ul>{sources}</ul></div></div></main><footer class="footer"><div class="container copyright">© 2026 THE ARCHIVE. Conteúdo editorial independente.</div></footer><script src="../app.js"></script></body></html>'''
 (ART/fname).write_text(doc,encoding='utf-8')
 catalog.append({'file':fname,'title':data['title'],'category':data.get('category','Notícias'),'date':data.get('date',''),'image':data['image'],'lead':data.get('lead','')})
 CAT.write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
 print('NOVA MATÉRIA PUBLICADA:',data['title'])
if __name__=='__main__': main()
