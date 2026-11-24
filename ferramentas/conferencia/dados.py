"""Confere os dados de ponta a ponta: banco da nuvem, banco local, JSON do site e despesas brutas do Senado.

Compara as somas da cota por ano, as verificações, cada bloco dos perfis (cota, moradia, salário, equipe, foto e
mandato) e, de forma independente do pipeline, as despesas brutas em data/raw/ contra o total que o site mostra.

Uso, a partir da raiz (precisa do .env, com DATABASE_URL_LEITURA, e dos dados de web/dados/ e data/):
  uv run --project pipeline --env-file .env python ferramentas/conferencia/dados.py
Termina com a contagem de ERROS; zero é o esperado. Os anos 2025 e 2026 estão fixos na conferência dos brutos.
"""

import collections
import json
import os
import sqlite3
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[2]
db = sqlite3.connect(ROOT / "data/limpo/senadados.sqlite")
conn = psycopg.connect(os.environ["DATABASE_URL_LEITURA"])


def q(sql):
    return conn.execute(sql).fetchall()


erros = []


def ok(cond, msg):
    if not cond:
        erros.append(msg)


# 1) banco na nuvem x banco local
for ano, soma in q(
    "SELECT ano, SUM(valor_centavos) FROM publico.despesas_mensais GROUP BY ano ORDER BY ano"
):
    loc = db.execute(
        "SELECT SUM(valor_centavos) FROM despesas d WHERE ano=? AND (cod_senador, ano) IN (SELECT cod_senador, ano FROM verificacao_cota WHERE resultado IN ('identico','explicado'))",
        (ano,),
    ).fetchone()[0]
    print(f"cota {ano}: nuvem {soma / 100:,.2f} | local {loc / 100:,.2f}")
    ok(soma == loc, f"soma da cota {ano} difere")
nuv = {r[0]: r[1] for r in q("SELECT 'sen', count(*) FROM publico.senadores")}
ok(nuv["sen"] == 81, "senadores != 81")
print(
    "anos no banco:",
    [r[0] for r in q("SELECT DISTINCT ano FROM publico.despesas_mensais ORDER BY 1")],
    "| anos fornecedores:",
    [r[0] for r in q("SELECT DISTINCT ano FROM publico.fornecedores_anuais ORDER BY 1")],
)
res_n = {
    (v, a): (i, e, p, o)
    for v, a, i, e, p, o in q(
        "SELECT verificacao, ano, identicos, explicados, pendentes, ocultos FROM publico.verificacoes_resumo"
    )
}
res_l = {
    (n, a): (i, e, s)
    for n, a, i, e, s in db.execute(
        "SELECT nome, ano, identicos, explicados, sem_explicacao FROM verificacoes"
    )
}
for k, (i, e, _p, o) in res_n.items():
    li, le, ls = res_l[k]
    ok((i, e, o) == (li, le, ls), f"resumo {k} difere nuvem x local")
print(
    "verificações no resumo:",
    len(res_n),
    "| iguais ao local:",
    all((res_n[k][0], res_n[k][1], res_n[k][3]) == res_l[k] for k in res_n),
)

# 2) exportação (JSON) x banco da nuvem
D = ROOT / "web/dados"
lista = json.load(open(D / "senadores.json"))
meta = json.load(open(D / "metadados.json"))
ok(
    len(lista) == 81 and meta["versao_contrato"] == 2 and meta["anos"] == "2025-2026",
    "metadados/lista",
)
cota_db = collections.defaultdict(int)
for c, a, v in q(
    "SELECT cod_senador, ano, SUM(valor_centavos) FROM publico.despesas_mensais GROUP BY 1,2"
):
    cota_db[(c, a)] = v
mor_db = collections.Counter(
    (c, a) for c, a, *_ in q("SELECT cod_senador, ano, mes FROM publico.moradia_meses")
)
mor_ok = {(c, a) for c, a in q("SELECT cod_senador, ano FROM publico.moradia_verificada")}
sal = {
    c: (a, m, b, liq)
    for c, a, m, b, liq in q(
        "SELECT cod_senador, ano, mes, remuneracao_basica_centavos, remuneracao_liquida_centavos FROM publico.salario"
    )
}
eq = {c: (a, n) for c, a, n in q("SELECT cod_senador, ano, pessoas FROM publico.equipe")}
perfil = {
    c: (f, i, j)
    for c, f, i, j in q(
        "SELECT cod_senador, foto_url, mandato_inicio, mandato_fim FROM publico.perfil"
    )
}
n_cota = n_mor = 0
for it in lista:
    p = json.load(open(D / "senadores" / f"{it['slug']}.json"))
    for a in (p["cota"] or {"anos": []})["anos"]:
        n_cota += 1
        ok(a["total_centavos"] == cota_db[(p["codigo"], a["ano"])], f"cota {p['nome']} {a['ano']}")
        ok(
            sum(m["total_centavos"] for m in a["meses"]) == a["total_centavos"],
            f"meses {p['nome']}",
        )
    anos_cota = {a["ano"] for a in (p["cota"] or {"anos": []})["anos"]}
    ok(
        set(cota_db_k[1] for cota_db_k in cota_db if cota_db_k[0] == p["codigo"]) == anos_cota,
        f"anos da cota {p['nome']}",
    )
    for m in (p["moradia"] or {"anos": []})["anos"]:
        n_mor += 1
        ok(
            (p["codigo"], m["ano"]) in mor_ok
            and len(m["meses"]) == mor_db[(p["codigo"], m["ano"])],
            f"moradia {p['nome']} {m['ano']}",
        )
    if p["salario"]:
        ok(sal[p["codigo"]][2] == p["salario"]["basica_centavos"], f"salário {p['nome']}")
    else:
        ok(p["codigo"] not in sal, f"salário ausente {p['nome']}")
    if p["equipe"]:
        ok(eq[p["codigo"]][1] == p["equipe"]["pessoas"], f"equipe {p['nome']}")
    else:
        ok(p["codigo"] not in eq, f"equipe ausente {p['nome']}")
    q_e = p["quem_e"]
    pf = perfil.get(p["codigo"])
    ok((q_e is not None) == (pf is not None), f"quem_e {p['nome']}")
    if q_e and q_e["mandato"]:
        ok(
            q_e["mandato"]["inicio_data"] == str(pf[1])
            and q_e["mandato"]["fim_data"] == str(pf[2]),
            f"mandato {p['nome']}",
        )
print("blocos de cota conferidos contra o banco:", n_cota, "| moradia:", n_mor)

# 3) cadeia inteira: despesas brutas do Senado -> JSON (independente do pipeline)
tot = collections.defaultdict(int)
for ano in (2025, 2026):
    rows = json.load(open(ROOT / f"data/raw/api/ceaps_{ano}.json"))
    for r in rows:
        tot[(int(r["codSenador"]), ano)] += round(float(r["valorReembolsado"]) * 100)
dif = 0
comp = 0
for it in lista:
    p = json.load(open(D / "senadores" / f"{it['slug']}.json"))
    for a in (p["cota"] or {"anos": []})["anos"]:
        comp += 1
        if a["total_centavos"] != tot[(p["codigo"], a["ano"])]:
            dif += 1
            erros.append(
                f"bruto x JSON {p['nome']} {a['ano']}: {a['total_centavos']} x {tot[(p['codigo'], a['ano'])]}"
            )
print(f"despesas brutas (JSON do Senado) x site: {comp} totais, {dif} diferenças")
print("ERROS:", len(erros))
[print(" ", e) for e in erros[:12]]
