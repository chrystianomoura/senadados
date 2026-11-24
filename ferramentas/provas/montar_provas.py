"""Monta as imagens de prova da página "Verificações" (docs/evidencias/).

Junta os recortes que fotografar.mjs gravou em ferramentas/saida/prints/ (telas e exportações do Senado) e refaz as
tabelas "montagem do Senadados" a partir dos arquivos oficiais de despesas, que baixa na hora. Nenhum valor é
alterado. Escreve por cima das 11 imagens de docs/evidencias/; o git guarda as versões anteriores.

Uso, a partir da raiz do repositório (Pillow vem do ambiente do pipeline):
  node ferramentas/provas/fotografar.mjs
  uv run --project pipeline python ferramentas/provas/montar_provas.py
Os números dos textos dos casos (docs e web/src/lib/divergencias.ts) precisam ser conferidos à mão depois.
"""

import csv
import html
import json
import os
import re
import subprocess
import unicodedata
import urllib.request
from datetime import datetime
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "ferramentas" / "saida" / "prints"
CSV = ROOT / "ferramentas" / "saida" / "csv"
OUT = ROOT / "docs" / "evidencias"
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
AGORA = datetime.now()
DIA = AGORA.strftime("%d/%m/%Y")
HORA = AGORA.strftime("%H:%M")


def empilhar(imgs, saida, espaco=12, fundo="white"):
    ims = [Image.open(i).convert("RGB") for i in imgs]
    w = max(i.width for i in ims)
    h = sum(i.height for i in ims) + espaco * (len(ims) - 1)
    tela = Image.new("RGB", (w, h), fundo)
    y = 0
    for i in ims:
        tela.paste(i, (0, y))
        y += i.height + espaco
    tela.save(saida, optimize=True)


# ---- telas e exportações --------------------------------------------------------------------
for nome, cod in (("02-exportacao-camilo-pessoal", 6336), ("04-exportacao-alan-pessoal", 5672)):
    empilhar([P / f"x-{cod}-topo.png", P / f"x-{cod}-pessoal.png"], OUT / f"{nome}.png", espaco=14)
for nome in ("01-portal-camilo-pessoal", "03-portal-alan-pessoal", "09-portal-mourao-2026"):
    Image.open(P / f"{nome}.png").convert("RGB").save(OUT / f"{nome}.png", optimize=True)
cinco = ["renan", "arns", "magno", "paim", "jayme"]
for ano, nome in ((2008, "05-portal-cinco-2008"), (2009, "07-portal-cinco-2009")):
    empilhar(
        [P / f"t-{ano}-h1.png"] + [P / f"p-{ano}-{n}.png" for n in cinco],
        OUT / f"{nome}.png",
        espaco=14,
    )


# ---- arquivos oficiais ----------------------------------------------------------------------
def baixar_arquivos() -> None:
    """Baixa de novo os arquivos de despesas usados nas tabelas, para a hora de "baixado em" ser verdadeira."""
    CSV.mkdir(parents=True, exist_ok=True)
    for ano in (2008, 2009, 2024, 2026):
        url = f"https://www.senado.leg.br/transparencia/LAI/verba/despesa_ceaps_{ano}.csv"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        (CSV / f"{ano}.csv").write_bytes(urllib.request.urlopen(req, timeout=180).read())


baixar_arquivos()


def sem_acento(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    ).upper()


def carregar(ano):
    with open(CSV / f"{ano}.csv", encoding="latin1", newline="") as f:
        r = csv.reader(f, delimiter=";")
        atualizacao = next(r)[1]
        cab = next(r)
        linhas = [dict(zip(cab, x, strict=False)) for x in r if len(x) == len(cab)]
    return atualizacao, linhas


def centavos(s):
    return round(float(s.replace(".", "").replace(",", ".")) * 100)


def brl(c, simbolo=False):
    t = f"{abs(c) / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("R$ " if simbolo else "") + ("-" if c < 0 else "") + t


def total_portal(cod, ano):
    req = urllib.request.Request(
        f"https://www6g.senado.leg.br/transparencia/sen/{cod}/?ano={ano}",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    t = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
    m = re.search(
        r"collapse-ceaps.*?Total\s*</t[dh]>\s*<t[dh][^>]*>\s*([\d\.]+,\d\d)", t, flags=re.S
    )
    return centavos(m.group(1))


CSS = """
body{margin:0;padding:24px 28px 28px;width:1144px;font:15px/1.4 -apple-system,'Helvetica Neue',Arial,sans-serif;color:#1a1a1a;background:#fff}
.sel{display:inline-block;background:#111;color:#fff;font-weight:800;font-size:11px;letter-spacing:.04em;text-transform:uppercase;padding:5px 11px;border-radius:999px}
h2{font-size:19px;margin:18px 0 8px}
.meta{color:#555;font-size:14px;margin:0 0 14px}
code{background:#f1ece2;padding:1px 6px;border-radius:4px;font-size:13px}
table{border-collapse:collapse;width:100%;margin-bottom:14px}
th{background:#f3eee6;text-align:left;font-weight:700}
th,td{border:1px solid #ddd5c5;padding:8px 10px;font-size:15px}
td.n,th.n{text-align:right}
tr.dif td{background:#eef7c4;font-weight:700}
.nota{border-left:4px solid #111;padding:2px 0 2px 12px;color:#444;font-size:13.5px;margin-top:6px}
em{color:#444}
"""


def pagina(arquivo, titulo, meta, corpo, nota):
    doc = (
        f"<!doctype html><meta charset=utf-8><style>{CSS}</style><span class=sel>Trecho do arquivo oficial · montagem do Senadados</span>"
        f"<h2>{titulo}</h2><p class=meta>{meta}</p>{corpo}<div class=nota>{nota}</div>"
    )
    html_path = P / f"{arquivo}.html"
    html_path.write_text(doc, encoding="utf-8")
    png = P / f"m-{arquivo}.png"
    subprocess.run(
        [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--window-size=1200,1500",
            f"--screenshot={png}",
            f"file://{html_path}",
        ],
        capture_output=True,
        timeout=90,
    )
    im = Image.open(png).convert("RGB")
    px = im.load()
    ultimo = 0
    for y in range(im.height - 1, -1, -1):
        if any(px[x, y] != (255, 255, 255) for x in range(0, im.width, 3)):
            ultimo = y
            break
    im.crop((0, 0, 1200, min(im.height, ultimo + 26))).save(OUT / f"{arquivo}.png", optimize=True)


def meta_arquivo(ano, atualizacao, extra=""):
    return (
        f"Arquivo: <code>senado.leg.br/transparencia/LAI/verba/despesa_ceaps_{ano}.csv</code> · baixado em {DIA} às {HORA}"
        f" · última atualização do arquivo: {atualizacao}{extra}"
    )


numeros = {"baixado": f"{DIA} {HORA}"}
alvos = ["RENAN CALHEIROS", "FLAVIO ARNS", "MAGNO MALTA", "PAULO PAIM", "JAYME CAMPOS"]
codigos = {
    "RENAN CALHEIROS": 70,
    "FLAVIO ARNS": 345,
    "MAGNO MALTA": 631,
    "PAULO PAIM": 825,
    "JAYME CAMPOS": 4531,
}
for ano, arq in ((2008, "06-arquivo-cinco-2008"), (2009, "08-arquivo-cinco-2009")):
    atual, linhas = carregar(ano)
    corpo = "<table><tr><th>SENADOR</th><th class=n>Linhas</th><th class=n>Soma de VALOR_REEMBOLSADO (R$)</th></tr>"
    numeros[ano] = {}
    for alvo in alvos:
        rs = [x for x in linhas if sem_acento(x["SENADOR"]) == alvo]
        soma = sum(centavos(x["VALOR_REEMBOLSADO"]) for x in rs)
        nome = rs[0]["SENADOR"] if rs else alvo
        numeros[ano][alvo] = {
            "linhas": len(rs),
            "soma": brl(soma),
            "tela": brl(total_portal(codigos[alvo], ano)),
        }
        corpo += f"<tr><td>{html.escape(nome)}</td><td class=n>{len(rs)}</td><td class=n>{brl(soma)}</td></tr>"
    corpo += "</table>"
    pagina(
        arq,
        f"Soma das despesas de {ano} no arquivo oficial, para os cinco senadores",
        meta_arquivo(ano, atual),
        corpo,
        "Como conferir: baixe o arquivo, filtre a coluna SENADOR pelo nome e some VALOR_REEMBOLSADO.",
    )

atual, linhas = carregar(2026)
m = [x for x in linhas if sem_acento(x["SENADOR"]) == "HAMILTON MOURAO"]
branco = [x for x in m if not x["TIPO_DESPESA"].strip()]
soma = sum(centavos(x["VALOR_REEMBOLSADO"]) for x in m)
soma_b = sum(centavos(x["VALOR_REEMBOLSADO"]) for x in branco)
tela = total_portal(6341, 2026)
numeros["mourao"] = {
    "linhas": len(m),
    "soma": brl(soma),
    "tela": brl(tela),
    "dif": brl(soma - tela),
    "branco": len(branco),
    "soma_branco": brl(soma_b),
}
corpo = "<table><tr><th>ANO</th><th>MES</th><th>SENADOR</th><th>TIPO_DESPESA</th><th>DATA</th><th class=n>VALOR_REEMBOLSADO</th></tr>"
for x in branco:
    corpo += (
        f"<tr><td>{x['ANO']}</td><td>{x['MES']}</td><td>{html.escape(x['SENADOR'])}</td><td><em>(em branco)</em></td>"
        f"<td>{x['DATA']}</td><td class=n>{x['VALOR_REEMBOLSADO']}</td></tr>"
    )
corpo += "</table><table><tr><th>Conta</th><th class=n>R$</th></tr>"
corpo += f"<tr><td>Soma de todas as {len(m)} linhas do senador em 2026 (arquivo oficial)</td><td class=n>{brl(soma)}</td></tr>"
corpo += f"<tr><td>Total mostrado na página do senador no portal (print acima)</td><td class=n>{brl(tela)}</td></tr>"
corpo += f"<tr class=dif><td>Diferença</td><td class=n>{brl(soma - tela)}</td></tr>"
corpo += f"<tr><td>Soma das {len(branco)} linha(s) com TIPO_DESPESA em branco</td><td class=n>{brl(soma_b)}</td></tr></table>"
pagina(
    "10-arquivo-mourao-2026",
    "Despesas de 2026 do senador Hamilton Mourão no arquivo oficial: linhas sem categoria",
    meta_arquivo(2026, atual, " · linhas copiadas sem alteração (documento e fornecedor omitidos)"),
    corpo,
    "Como conferir: baixe o arquivo, filtre SENADOR por “HAMILTON MOURAO” e some VALOR_REEMBOLSADO; depois some só as linhas em que TIPO_DESPESA está em branco.",
)

atual, linhas = carregar(2024)
ruins = [x for x in linhas if re.search(r"/0\d{3}$", x["DATA"])]
numeros["datas"] = len(ruins)
corpo = "<table><tr><th>ANO</th><th>MES</th><th>SENADOR</th><th>TIPO_DESPESA</th><th>DATA</th><th class=n>VALOR_REEMBOLSADO</th></tr>"
for x in ruins:
    t = x["TIPO_DESPESA"]
    t = t[:60] + "…" if len(t) > 60 else t
    corpo += (
        f"<tr><td>{x['ANO']}</td><td>{x['MES']}</td><td>{html.escape(x['SENADOR'])}</td><td>{html.escape(t)}</td>"
        f"<td><b>{x['DATA']}</b></td><td class=n>{x['VALOR_REEMBOLSADO']}</td></tr>"
    )
corpo += "</table>"
pagina(
    "11-arquivo-datas-impossiveis",
    "Notas com data de ano “0204” e “0202” no arquivo oficial de 2024",
    meta_arquivo(2024, atual, " · linhas copiadas sem alteração (documento e fornecedor omitidos)"),
    corpo,
    "Como conferir: baixe o arquivo no endereço acima e procure, na coluna DATA, valores terminados em /0204 e /0202.",
)
print(json.dumps(numeros, ensure_ascii=False, indent=1))
