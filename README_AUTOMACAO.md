# THE ARCHIVE — automação automática

Esta pasta foi preparada para que a automação **primeiro corrija o site e preserve as matérias existentes** e só depois tente publicar uma nova matéria.

## O que ela corrige automaticamente
- preserva matérias antigas, incluindo Bacabal;
- impede que uma nova matéria substitua outra;
- reconstrói os cards da home a partir do catálogo;
- reconstrói a página Notícias;
- corrige a logo nas páginas das matérias;
- mantém o catálogo `articles/catalog.json` sincronizado;
- tenta publicar uma nova matéria a cada 6 horas;
- bloqueia duplicatas;
- exige imagem verificável;
- exige apuração com busca na web;
- faz commit e envia a atualização para o GitHub; o Vercel conectado ao `main` publica a nova versão.

## O que você precisa fazer uma única vez
1. Coloque estes arquivos no repositório, mantendo as pastas:
   - `scripts/repair_site.py`
   - `scripts/auto_publish.py`
   - `.github/workflows/auto-news.yml`
2. No GitHub, abra **Settings → Secrets and variables → Actions → New repository secret**.
3. Nome: `OPENAI_API_KEY`
4. Valor: sua chave da API da OpenAI.
5. Salve.
6. Abra **Actions → THE ARCHIVE — corrigir e publicar automaticamente → Run workflow** para testar imediatamente.

Depois disso, o workflow roda sozinho a cada 6 horas.

## Importante
A chave da API deve ficar somente no GitHub Secret; nunca coloque a chave dentro dos arquivos. O GitHub mascara secrets nos logs e permite que workflows os recebam pelo contexto `secrets`.
