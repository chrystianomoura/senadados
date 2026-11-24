"""Varre o HTML que o site gerou (web/out/) atrás de erros que o código não mostra.

Procura "NaN", "undefined" e "null" no texto, palavras de culpa (D010), formato de CPF (D008), links e imagens
quebrados, páginas de senador sem nenhum dado e confere que cada botão de trocar de ano leva à página certa e volta.

Uso, depois de `npm run build` em web/:  python3 ferramentas/conferencia/site.py
Termina com a contagem de ERROS; zero é o esperado.
"""

import collections
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "web" / "out"
D = ROOT / "web" / "dados"


class P(HTMLParser):
    def __init__(s):
        super().__init__()
        s.t = []
        s.links = []
        s.imgs = []
        s.skip = 0

    def handle_starttag(s, tag, a):
        a = dict(a)
        if tag in ("script", "style"):
            s.skip += 1
        if tag == "a" and a.get("href"):
            s.links.append(a["href"])
        if tag == "img" and a.get("src"):
            s.imgs.append(a["src"])

    def handle_endtag(s, tag):
        if tag in ("script", "style") and s.skip:
            s.skip -= 1

    def handle_data(s, d):
        if not s.skip:
            s.t.append(d)


def ler(path):
    p = P()
    p.feed(path.read_text(encoding="utf-8"))
    return re.sub(r"\s+", " ", "".join(p.t)), p


erros = []
PROIBIDAS = re.compile(
    r"\b(suspeit\w*|irregular\w*|fraud\w*|desvio de dinheiro|ilegal\w*|corrup\w*)\b", re.I
)
RUIM = re.compile(r"\b(NaN|undefined|Infinity)\b|\[object|\bnull\b")
CPF = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\*{3}\.\d{3}\.\*{3}")


def existe(href):
    h = href.split("#")[0].split("?")[0]
    if not h.startswith("/"):
        return True
    p = OUT / h.lstrip("/")
    return p.exists() if p.suffix else (p / "index.html").exists()


paginas = list(OUT.rglob("index.html"))
print("páginas html:", len(paginas))
lista = json.load(open(D / "senadores.json"))
sem_dado = []
abre = collections.Counter()
ano_pages = 0
for p in paginas:
    txt, pr = ler(p)
    rel = str(p.relative_to(OUT))
    for m in RUIM.findall(txt):
        erros.append(f"{rel}: texto ruim {m!r}")
    for m in PROIBIDAS.findall(txt):
        erros.append(f"{rel}: palavra proibida {m!r}")
    if CPF.search(txt):
        erros.append(f"{rel}: formato de CPF")
    for link in pr.links + pr.imgs:
        if not existe(link):
            erros.append(f"{rel}: link quebrado {link}")
    if rel.startswith("senador/"):
        if "Ainda não há dados comprovados" in txt:
            sem_dado.append(rel)
        h2 = re.search(r"Resumo de (\d{4})", txt)
        if len(rel.split("/")) == 4:
            ano_pages += 1
        if h2:
            abre[(len(rel.split("/")), h2.group(1))] += 1
print("páginas de senador (padrão x outro ano) por ano do resumo:", dict(abre))
print("páginas de outro ano:", ano_pages)
print("sem nenhum dado comprovado:", sem_dado)
# cada botão de troca de ano leva a uma página que existe e que mostra o ano prometido
trocas = 0
for it in lista:
    f = OUT / "senador" / it["slug"] / "index.html"
    txt, pr = ler(f)
    for link in pr.links:
        m = re.match(r"/senador/[^/]+/(\d{4})/$", link)
        if m:
            trocas += 1
            alvo, _ = ler(OUT / link.lstrip("/") / "index.html")
            if f"Resumo de {m.group(1)}" not in alvo:
                erros.append(f"{it['slug']}: {link} não mostra {m.group(1)}")
print("botões de trocar de ano conferidos (ida):", trocas)
volta = 0
for f in OUT.glob("senador/*/20*/index.html"):
    txt, pr = ler(f)
    slug = f.parts[-3]
    ok = f"/senador/{slug}/" in pr.links
    volta += ok
    if not ok:
        erros.append(f"{slug}: a página de outro ano não tem o botão de volta")
print("botões de volta:", volta, "de", ano_pages)
print("ERROS:", len(erros))
[print(" ", e) for e in erros[:15]]
