"""Salário: a remuneração do senador na folha de pagamento do Senado.

D016 e D025: o site mostra a remuneração de cada senador como a folha a publica, **só
quando a ligação entre o senador e a folha é inequívoca**. A folha não usa o código do
parlamentar, só o nome, e só tem uma fonte. Por isso a prova é de outro tipo:

1. **Identidade pelo código, não pelo nome.** A página do senador no portal tem um link
   ("Subsídios do Senador") que leva à página de identificação dele no portal de
   servidores. Essa página diz o nome civil, o vínculo, a situação e a UF. O nome civil
   é a chave de ligação com a folha, e o vínculo ("parlamentar"), a situação ("ativo") e
   a UF precisam bater com o que sabemos do senador.
2. **Uma única matrícula na folha** com esse nome. Zero ou mais de uma não se resolve e o
   salário fica oculto.
3. **Uma única folha normal no mês.** Folhas suplementares só são aceitas se estiverem
   zeradas.
4. **Conta interna:** a remuneração líquida é a soma dos componentes (11 campos). Todas as
   10.480 linhas normais de outubro de 2026 fecham a conta.
5. **Valores positivos.**

A consulta de remuneração do portal de servidores exige reCAPTCHA, e este módulo **não
tenta contorná-lo**: só lê a identificação, que o portal mostra sem desafio.

Resultados: `identico` (passou em tudo) ou `sem_explicacao`. Exibição (D037): dado descritivo,
aparece para quem passou, com o freio de segurança de 5%.

Só as linhas da folha dos senadores são guardadas: o nome de qualquer outro servidor é
descartado na hora (D007). Prova consistência e identidade, não é auditoria (D027).
"""

from __future__ import annotations

import argparse
import html
import re
import sqlite3
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from dataclasses import dataclass, replace
from datetime import date, datetime
from pathlib import Path

import httpx

from senadados_pipeline.coleta import (
    ColetaError,
    get_json,
    get_text,
    now_local,
    read_manifest,
    write_json,
)
from senadados_pipeline.config import BASE_URL, CLEAN_DB, PORTAL_URL, RAW_DIR
from senadados_pipeline.equipe import normalize
from senadados_pipeline.verificacao import (
    IDENTICAL,
    UNEXPLAINED,
    VerificacaoError,
    check_same_snapshot,
    ensure_verificacoes_table,
)

MANIFEST_KEY = "salario"
MAX_FAILURE_RATE = 0.05
USER_AGENT = "senadados-pipeline/0.1"
MONTHS_BACK = 3
DETAIL_URL = "https://www.senado.leg.br/transparencia/rh/servidores/detalhe.asp"

# Componentes cuja soma é a remuneração líquida (conferido em todas as linhas normais).
COMPONENTS = (
    "remuneracao_basica",
    "vantagens_pessoais",
    "funcao_comissionada",
    "gratificacao_natalina",
    "horas_extras",
    "outras_eventuais",
    "abono_permanencia",
    "reversao_teto_constitucional",
    "previdencia",
    "imposto_renda",
    "faltas",
)
MONEY_FIELDS = (
    *COMPONENTS,
    "remuneracao_liquida",
    "diarias",
    "auxilios",
    "vantagens_indenizatorias",
)


# ---------------------------------------------------------------------------
# Leitura
# ---------------------------------------------------------------------------
def parse_money(text) -> int:
    """'46.366,19' -> 4636619 centavos. Aceita sinal negativo."""
    if not isinstance(text, str) or not re.fullmatch(r"-?\d{1,3}(?:\.\d{3})*,\d{2}", text):
        raise ColetaError(f"valor em formato inesperado: {text!r}")
    return int(text.replace(".", "").replace(",", ""))


def parse_detail_link(page: str) -> tuple[str, str] | None:
    """(fcodigo, fvinculo) do link 'Subsídios do Senador' da página do senador."""
    match = re.search(r"detalhe\.asp\?fcodigo=(\d+)&(?:amp;)?fvinculo=(\d+)", page)
    return (match.group(1), match.group(2)) if match else None


def parse_identification(page: str) -> dict[str, str]:
    """Nome, vínculo, situação e UF da página de identificação."""
    pairs = re.findall(
        r'<td class="coltitulo_identifica">(.*?)</td>\s*<td class="coldados_identifica">(.*?)</td>',
        page,
        flags=re.S,
    )
    data = {
        re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", k))).strip(): re.sub(
            r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", v))
        ).strip()
        for k, v in pairs
    }
    try:
        return {
            "nome": data["Nome"],
            "vinculo": data["Vínculo"],
            "situacao": data["Situação"],
            "uf": data["UF"],
        }
    except KeyError as error:
        raise ColetaError(f"a identificação não traz o campo {error}") from error


# ---------------------------------------------------------------------------
# Coleta
# ---------------------------------------------------------------------------
def fetch_identity(client: httpx.Client, code: int, year: int) -> dict:
    """A identificação do senador pelo código dele. A falha de um só vira `erro`."""
    try:
        link = parse_detail_link(get_text(client, f"{PORTAL_URL}/sen/{code}/?ano={year}"))
        if link is None:
            raise ColetaError("a página do senador não tem o link de subsídios")
        url = f"{DETAIL_URL}?fcodigo={link[0]}&fvinculo={link[1]}"
        return parse_identification(get_text(client, url))
    except ColetaError as error:
        return {"erro": f"ColetaError: {error}"}


def fetch_folha(client: httpx.Client, today: date) -> tuple[int, int, list[dict]]:
    """A folha do mês mais recente que já tem dados (até 3 meses para trás)."""
    year, month = today.year, today.month
    for _ in range(MONTHS_BACK + 1):
        rows = get_json(client, f"/servidores/remuneracoes/{year}/{month}")
        if not isinstance(rows, list):
            raise ColetaError("a folha veio em formato inesperado")
        if rows:
            return year, month, rows
        year, month = (year, month - 1) if month > 1 else (year - 1, 12)
    raise ColetaError("a folha está vazia nos últimos meses")


def senator_rows(rows: list[dict], names: set[str]) -> tuple[dict[str, list[dict]], dict[str, int]]:
    """Só as linhas da folha cujo nome é o de um senador. Os demais nomes são descartados.

    Quando o mesmo nome aparece em mais de uma matrícula, não dá para saber qual é o
    senador, e as linhas de **todas** ficam de fora (podem ser de outra pessoa): só se
    guarda quantas matrículas há.
    """
    found: dict[str, list[dict]] = {}
    for row in rows:
        try:
            key = normalize(row["nome"])
        except (KeyError, TypeError, AttributeError) as error:
            raise ColetaError(f"linha da folha sem nome: {error!r}") from error
        if key in names:
            found.setdefault(key, []).append(row)
    unique: dict[str, list[dict]] = {}
    ambiguous: dict[str, int] = {}
    for key, found_rows in found.items():
        registrations = {row.get("sequencial") for row in found_rows}
        if len(registrations) == 1:
            unique[key] = found_rows
        else:
            ambiguous[key] = len(registrations)
    return unique, ambiguous


def collect_salario(
    client: httpx.Client,
    raw_dir: Path,
    senators: dict[int, str],
    today: date,
    clock=now_local,
    *,
    workers: int = 8,
):
    """Identidade de cada senador e a folha, guardando só as linhas dos senadores."""
    codes = sorted(senators)
    year = today.year
    with ThreadPoolExecutor(max_workers=workers) as pool:
        identities = dict(
            zip(codes, pool.map(lambda c: fetch_identity(client, c, year), codes), strict=True)
        )
    folha_year, folha_month, rows = fetch_folha(client, today)

    names = {normalize(i["nome"]) for i in identities.values() if "nome" in i}
    matched, ambiguous = senator_rows(rows, names)
    write_json(
        raw_dir / "salario" / "folha_senadores.json",
        {
            "ano": folha_year,
            "mes": folha_month,
            "identidades": {str(c): i for c, i in identities.items()},
            "linhas": matched,
            "ambiguos": ambiguous,
        },
    )
    manifest = read_manifest(raw_dir)
    manifest[MANIFEST_KEY] = clock().isoformat(timespec="seconds")
    write_json(raw_dir / "coleta.json", manifest)
    return folha_year, folha_month, identities, matched, ambiguous


# ---------------------------------------------------------------------------
# Comparação
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Result:
    cod_senador: int
    ano: int
    mes: int
    resultado: str
    detalhe: str | None = None
    basica_centavos: int | None = None
    liquida_centavos: int | None = None
    exibir: bool = False


def check_salary(
    code: int, uf: str, year: int, month: int, identity: dict, rows: list[dict], ambiguous: int = 0
) -> Result:
    """Aplica as cinco provas a um senador."""

    def fail(reason: str) -> Result:
        return Result(code, year, month, UNEXPLAINED, reason)

    if "erro" in identity:
        return fail(identity["erro"])
    if identity["vinculo"].casefold() != "parlamentar":
        return fail(f"o portal informa vínculo {identity['vinculo']!r}")
    if identity["situacao"].casefold() != "ativo":
        return fail(f"o portal informa situação {identity['situacao']!r}")
    if identity["uf"].strip().upper() != uf.strip().upper():
        return fail(f"a UF do portal ({identity['uf']}) difere da do senador ({uf})")

    if ambiguous > 1:
        return fail(f"{ambiguous} matrículas com esse nome na folha: ligação ambígua")
    registrations = {row["sequencial"] for row in rows}
    if not rows:
        return fail("o nome civil não está na folha do mês")
    if len(registrations) != 1:
        return fail(f"{len(registrations)} matrículas com esse nome na folha: ligação ambígua")

    normal = [row for row in rows if row.get("tipo_folha") == "Normal"]
    other = [row for row in rows if row.get("tipo_folha") != "Normal"]
    if len(normal) != 1:
        return fail(f"{len(normal)} folhas normais no mês")
    try:
        for row in other:
            if any(parse_money(row[field]) for field in MONEY_FIELDS):
                return fail("há folha suplementar com valores no mês")
        values = {field: parse_money(normal[0][field]) for field in MONEY_FIELDS}
    except (ColetaError, KeyError) as error:
        return fail(f"folha em formato inesperado: {error}")

    if sum(values[field] for field in COMPONENTS) != values["remuneracao_liquida"]:
        return fail("a remuneração líquida não é a soma dos componentes")
    if values["remuneracao_basica"] <= 0 or values["remuneracao_liquida"] <= 0:
        return fail("valor não positivo na remuneração")
    return Result(
        code,
        year,
        month,
        IDENTICAL,
        None,
        values["remuneracao_basica"],
        values["remuneracao_liquida"],
    )


def apply_release_rule(results: list[Result]) -> list[Result]:
    failures = sum(r.resultado == UNEXPLAINED for r in results)
    if not results or failures / len(results) > MAX_FAILURE_RATE:
        return [
            replace(r, exibir=False, basica_centavos=None, liquida_centavos=None) for r in results
        ]
    return [
        replace(r, exibir=r.resultado == IDENTICAL)
        if r.resultado == IDENTICAL
        else replace(r, exibir=False, basica_centavos=None, liquida_centavos=None)
        for r in results
    ]


def verify_salario(
    senators: dict[int, tuple[str, str]],
    year: int,
    month: int,
    identities: dict,
    matched: dict,
    ambiguous: dict | None = None,
) -> list[Result]:
    """`senators`: código -> (nome, UF)."""
    results = []
    for code in sorted(senators):
        identity = identities.get(code) or {"erro": "senador sem identificação"}
        key = normalize(identity["nome"]) if "nome" in identity else None
        rows = matched.get(key, []) if key else []
        count = (ambiguous or {}).get(key, 0) if key else 0
        results.append(check_salary(code, senators[code][1], year, month, identity, rows, count))
    return apply_release_rule(results)


# ---------------------------------------------------------------------------
# Banco local
# ---------------------------------------------------------------------------
def write_results(connection: sqlite3.Connection, results: list[Result], when: datetime) -> None:
    connection.execute("DROP TABLE IF EXISTS verificacao_salario")
    connection.execute("DROP TABLE IF EXISTS salario")
    connection.execute(
        "CREATE TABLE verificacao_salario (cod_senador INTEGER PRIMARY KEY, ano INTEGER, "
        "mes INTEGER, resultado TEXT, detalhe TEXT, exibir INTEGER)"
    )
    connection.execute(
        "CREATE TABLE salario (cod_senador INTEGER PRIMARY KEY, ano INTEGER, mes INTEGER, "
        "remuneracao_basica_centavos INTEGER, remuneracao_liquida_centavos INTEGER)"
    )
    connection.executemany(
        "INSERT INTO verificacao_salario VALUES (?, ?, ?, ?, ?, ?)",
        [(r.cod_senador, r.ano, r.mes, r.resultado, r.detalhe, int(r.exibir)) for r in results],
    )
    connection.executemany(
        "INSERT INTO salario VALUES (?, ?, ?, ?, ?)",
        [
            (r.cod_senador, r.ano, r.mes, r.basica_centavos, r.liquida_centavos)
            for r in results
            if r.exibir
        ],
    )
    ensure_verificacoes_table(connection)
    connection.execute("DELETE FROM verificacoes WHERE nome = 'salario'")
    kinds = Counter(r.resultado for r in results)
    year = results[0].ano if results else 0
    connection.execute(
        "INSERT INTO verificacoes VALUES ('salario', ?, ?, 0, ?, ?)",
        (year, kinds[IDENTICAL], kinds[UNEXPLAINED], when.isoformat(timespec="seconds")),
    )


def run(
    raw_dir: Path, database: Path, client: httpx.Client, today: date, clock=now_local
) -> list[Result]:
    if not database.exists():
        raise VerificacaoError(f"falta {database}; rode a limpeza antes")
    with closing(sqlite3.connect(database)) as connection:
        reference = connection.execute(
            "SELECT valor FROM metadados WHERE chave = 'data_referencia'"
        ).fetchone()
        if reference is None:
            raise VerificacaoError("o banco limpo não registra a data de referência")
        check_same_snapshot(read_manifest(raw_dir), [], date.fromisoformat(reference[0]), today)
        senators = {
            code: (name, uf)
            for code, name, uf in connection.execute("SELECT cod_senador, nome, uf FROM senadores")
        }
        try:
            year, month, identities, matched, ambiguous = collect_salario(
                client, raw_dir, {c: n for c, (n, _) in senators.items()}, today, clock
            )
        except ColetaError as error:
            raise VerificacaoError(str(error)) from error
        results = verify_salario(senators, year, month, identities, matched, ambiguous)
        with connection:
            write_results(connection, results, clock())
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coleta e verifica o salário dos senadores.")
    parser.add_argument("--raw", type=Path, default=RAW_DIR, help="pasta dos dados coletados")
    parser.add_argument("--banco", type=Path, default=CLEAN_DB, help="banco SQLite limpo")
    args = parser.parse_args(argv)
    try:
        headers = {"User-Agent": USER_AGENT}
        with httpx.Client(base_url=BASE_URL, timeout=180.0, headers=headers) as client:
            results = run(args.raw, args.banco, client, date.today())
    except (VerificacaoError, ColetaError) as error:
        print(f"erro: {error}", file=sys.stderr)
        return 1

    kinds = Counter(r.resultado for r in results)
    print(f"senadores: {len(results)}  (folha de {results[0].mes:02d}/{results[0].ano})")
    print(f"idênticos: {kinds[IDENTICAL]}")
    print(f"sem explicação: {kinds[UNEXPLAINED]}")
    print(f"salário exibido para: {sum(r.exibir for r in results)}")
    for r in results:
        if r.resultado == UNEXPLAINED:
            print(f"  senador {r.cod_senador}: {r.detalhe}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
