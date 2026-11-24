"""Pesquisa de 23/11/2026: dá para trazer dados de 2025? (D049)

Cada modo, passado como argumento, é uma sondagem de leitura (não grava nada no projeto):
  api           o resumo da API muda de ano para ano? (pessoal e benefícios, 2025 contra 2026)
  moradia       a moradia de 2025 passa nas três fontes?
  equipe        a tela de 2025 muda em relação à de 2026?
  equipe2       resumo da API contra o bloco "Pessoal" da tela, em 2025 e em 2026
  salario       a folha de dezembro de 2025 passa nas cinco provas da D041?
  salario_m11   o mesmo, para o mês escolhido (salario_mNN, com NN de 1 a 11)
  salario_meses cada folha de janeiro a novembro de 2025
Os resultados estão na D049 (docs/decisoes.md). Precisa do banco limpo local (data/limpo/).

Uso, a partir da raiz:  uv run --project pipeline python ferramentas/pesquisa/anos_anteriores.py moradia
"""

import collections
import json
import re
import sqlite3
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

import httpx
from senadados_pipeline import equipe, moradia, salario
from senadados_pipeline.coleta import get_json, get_text
from senadados_pipeline.config import BASE_URL, CLEAN_DB, PORTAL_URL, USER_AGENT

db = sqlite3.connect(CLEAN_DB)
senators = {c: (n, uf) for c, n, uf in db.execute("SELECT cod_senador, nome, uf FROM senadores")}
codes = sorted(senators)
cli = httpx.Client(base_url=BASE_URL, timeout=120, headers={"User-Agent": USER_AGENT})
which = sys.argv[1]


def resumo(code, ano):
    try:
        d = get_json(cli, f"/senadores/{code}/recursos-utilizados?ano={ano}")["data"]
        return d[0] if d else None
    except Exception as e:
        return {"erro": repr(e)[:80]}


if which == "api":
    with ThreadPoolExecutor(8) as p:
        a25 = dict(zip(codes, p.map(lambda c: resumo(c, 2025), codes), strict=False))
        a26 = dict(zip(codes, p.map(lambda c: resumo(c, 2026), codes), strict=False))
    vazio = [c for c in codes if not a25[c] or "erro" in a25[c]]
    print("2025 sem resposta:", len(vazio), [senators[c][0] for c in vazio][:8])
    for campo in ("pessoal", "beneficios", "cota" if "cota" in (a26[codes[0]] or {}) else None):
        if not campo:
            continue
        iguais = sum(
            1 for c in codes if a25[c] and a26[c] and a25[c].get(campo) == a26[c].get(campo)
        )
        print(f"campo {campo}: igual entre 2025 e 2026 em {iguais} de {len(codes)}")
    print("chaves do resumo 2026:", list(a26[codes[0]].keys()))
    c = 5672
    print("Alan pessoal 2025:", json.dumps(a25[c].get("pessoal"), ensure_ascii=False)[:230])
    print("Alan pessoal 2026:", json.dumps(a26[c].get("pessoal"), ensure_ascii=False)[:230])
    print("Alan benef 2025:", a25[c].get("beneficios"), "| 2026:", a26[c].get("beneficios"))

if which == "moradia":
    with ThreadPoolExecutor(8) as p:
        recs = dict(
            zip(codes, p.map(lambda c: moradia.fetch_senator(cli, c, 2025), codes), strict=False)
        )
    cnt = collections.Counter()
    motivos = collections.Counter()
    usados = 0
    for c in codes:
        r = recs[c]
        if "erro" in r:
            cnt["erro"] += 1
            motivos[r["erro"][:90]] += 1
            continue
        months = r["mensal"]
        listed = {}
        for key in moradia.BENEFITS.values():
            idx = 1 if key == "auxilio" else 2
            last = bool(months[-1][idx]) if months else False
            listed[moradia.LIST_FIELDS[key]] = "S" if last else "N"
        res = moradia.compare_moradia(c, 2025, r, listed)
        cnt[res.resultado] += 1
        if res.detalhe:
            motivos[res.detalhe[:110]] += 1
        usados += any(m[1] or m[2] for m in months)
    print("moradia 2025 (3 fontes):", dict(cnt))
    print("com algum uso em 2025:", usados)
    for m, n in motivos.most_common(6):
        print("  ", n, m)

if which == "equipe":

    def tela(code, ano):
        t = moradia.page_text(get_text(cli, f"{PORTAL_URL}/sen/{code}/?ano={ano}"))
        i = t.find("Pessoal")
        j = t.find("Subsídios", i)
        blk = t[i:j]
        return {
            k: int(n)
            for k, n in re.findall(
                r"(Comissionados?|Efetivos?|Requisitados?|Estagiários?|Terceirizados?)\s*(\d+)\s*pessoa",
                blk,
            )
        }

    with ThreadPoolExecutor(8) as p:
        t25 = dict(zip(codes, p.map(lambda c: tela(c, 2025), codes), strict=False))
        t26 = dict(zip(codes, p.map(lambda c: tela(c, 2026), codes), strict=False))
    print(
        "tela Pessoal 2025 igual à de 2026 em",
        sum(t25[c] == t26[c] for c in codes),
        "de",
        len(codes),
    )
    print("Alan tela 2025:", t25[5672], "| 2026:", t26[5672])
    print("Camilo tela 2025:", t25[6336], "| 2026:", t26[6336])

if which == "salario":
    tmp = Path(tempfile.mkdtemp())
    yr, mo, ids, matched, amb = salario.collect_salario(
        cli, tmp, {c: n for c, (n, _) in senators.items()}, date(2025, 12, 31)
    )
    res = salario.verify_salario(senators, yr, mo, ids, matched, amb)
    print(
        "folha usada:", yr, mo, "| resultados:", dict(collections.Counter(r.resultado for r in res))
    )
    for m, n in collections.Counter(r.detalhe for r in res if r.detalhe).most_common(5):
        print("  ", n, m[:110])
    ok = [r for r in res if r.exibir]
    print("com salário provado:", len(ok))

if which == "equipe2":

    def tela_blocos(code, ano):
        t = moradia.page_text(get_text(cli, f"{PORTAL_URL}/sen/{code}/?ano={ano}"))
        i = t.find("Local / Vínculo")
        j = t.find("Subsídios", i)
        blk = t[i:j] if i >= 0 else ""
        local, out = None, {"Gabinete": {}, "Escritório": {}}
        for m in re.finditer(
            r"(Gabinete|Escritório\(s\) de Apoio)\s*(\d+)\s*pessoa|(Comissionados?|Efetivos?|Requisitados?|Estagiários?|Terceirizados?)\s*(\d+)\s*pessoa",
            blk,
        ):
            if m.group(1):
                local = "Gabinete" if m.group(1) == "Gabinete" else "Escritório"
                out[local]["total"] = int(m.group(2))
            elif local:
                out[local][m.group(3).rstrip("s").upper().replace("Á", "A")] = int(m.group(4))
        return out["Gabinete"]

    for ano in (2025, 2026):
        with ThreadPoolExecutor(8) as p:
            api = dict(zip(codes, p.map(lambda c, ano=ano: resumo(c, ano), codes), strict=False))
            tel = dict(
                zip(codes, p.map(lambda c, ano=ano: tela_blocos(c, ano), codes), strict=False)
            )
        ig = dif = semdado = 0
        ex = []
        for c in codes:
            pes = (api[c] or {}).get("pessoal") or []
            g = next((x for x in pes if x["local"] == "Gabinete"), None)
            if not g or not tel[c]:
                semdado += 1
                continue
            a = {v["vinculo"].upper(): v["quantidade"] for v in g["vinculos"]}
            t = {k: v for k, v in tel[c].items() if k in ("COMISSIONADO", "EFETIVO", "REQUISITADO")}
            if a == t:
                ig += 1
            else:
                dif += 1
                ex.append((senators[c][0], a, t))
        print(
            f"{ano}: API x tela, só comissionado/efetivo/requisitado: iguais {ig}, diferentes {dif}, sem dado num dos lados {semdado}"
        )
        for e in ex[:3]:
            print("   ", e)

if which.startswith("salario_m") and which != "salario_meses":
    mes = int(which.split("m")[-1])
    tmp = Path(tempfile.mkdtemp())
    ultimo = date(2025, mes, 28)
    yr, mo, ids, matched, amb = salario.collect_salario(
        cli, tmp, {c: n for c, (n, _) in senators.items()}, ultimo
    )
    res = salario.verify_salario(senators, yr, mo, ids, matched, amb)
    print(
        "folha",
        yr,
        mo,
        dict(collections.Counter(r.resultado for r in res)),
        "| salário provado:",
        sum(r.exibir for r in res),
    )
    for m, n in collections.Counter(r.detalhe for r in res if r.detalhe).most_common(4):
        print("  ", n, m[:100])

if which == "salario_meses":
    with ThreadPoolExecutor(8) as p:
        ids = dict(
            zip(codes, p.map(lambda c: salario.fetch_identity(cli, c, 2025), codes), strict=False)
        )
    nomes = {equipe.normalize(i["nome"]) for i in ids.values() if "nome" in i}
    print("identidades com nome civil:", len(nomes), "de", len(codes))
    for mes in range(1, 12):
        rows = get_json(cli, f"/servidores/remuneracoes/2025/{mes}")
        matched, amb = salario.senator_rows(rows, nomes)
        res = salario.verify_salario(senators, 2025, mes, ids, matched, amb)
        brutos = collections.Counter(r.resultado for r in res)
        motivos = collections.Counter(
            (r.detalhe or "")[:40] for r in res if r.resultado != "identico"
        )
        print(
            mes,
            "provas ok:",
            brutos.get("identico", 0),
            "| falhas:",
            sum(v for k, v in brutos.items() if k != "identico"),
            "| exibidos:",
            sum(r.exibir for r in res),
            dict(motivos.most_common(3)),
        )
