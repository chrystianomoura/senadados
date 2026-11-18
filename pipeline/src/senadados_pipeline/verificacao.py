"""Verificação da cota: despesas detalhadas contra o resumo oficial de cada senador.

É a "prova real" da D025. Para cada senador e ano, soma as despesas por categoria e
compara com o resumo que o próprio Senado publica (`recursos-utilizados`):

- `identico`: todas as categorias batem no centavo.
- `explicado`: batem, e a única coisa que o resumo não traz são as linhas sem categoria
  (o resumo não as conta; a API de despesas sim).
- `sem_explicacao`: qualquer outra diferença. O número fica oculto e o motivo é registrado.

A comparação só vale se as bases forem da **mesma foto dos dados**: coleta, limpeza e
resumo do mesmo dia (AGENTS.md). Caso contrário, a verificação se recusa a rodar.

Prova consistência entre bases do Senado, não é auditoria (D025, D027).
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections import defaultdict
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import httpx

from senadados_pipeline.coleta import ColetaError, get_json, parse_years, read_manifest
from senadados_pipeline.config import BASE_URL, CLEAN_DB, RAW_DIR
from senadados_pipeline.limpeza import NO_CATEGORY

# Nome da categoria no resumo -> nome oficial da categoria nas despesas.
# O resumo usa nomes encurtados; um nome que não esteja aqui impede a verificação.
CATEGORY_MAP = {
    "Aluguel de imóveis para escritório político": (
        "Aluguel de imóveis para escritório político, compreendendo despesas concernentes a eles."
    ),
    "Aquisição de material de consumo": (
        "Aquisição de material de consumo para uso no escritório político, inclusive "
        "aquisição ou locação de software, despesas postais, aquisição de publicações, "
        "locação de móveis e de equipamentos."
    ),
    "Locomoção, hospedagem, alimentação e combustíveis": (
        "Locomoção, hospedagem, alimentação, combustíveis e lubrificantes"
    ),
    "Contratação de serviços de apoio ao parlamentar": (
        "Contratação de consultorias, assessorias, pesquisas, trabalhos técnicos e outros "
        "serviços de apoio ao exercício do mandato parlamentar"
    ),
    "Divulgação da atividade parlamentar": "Divulgação da atividade parlamentar",
    "Passagens aéreas, aquáticas e terrestres nacionais": (
        "Passagens aéreas, aquáticas e terrestres nacionais"
    ),
    "Serviços de Segurança Privada": "Serviços de Segurança Privada",
}

IDENTICAL = "identico"
EXPLAINED = "explicado"
UNEXPLAINED = "sem_explicacao"


class VerificacaoError(Exception):
    """A verificação não pôde ser feita (não é o mesmo que um número não bater)."""


@dataclass(frozen=True)
class Result:
    cod_senador: int
    ano: int
    despesas_centavos: int
    resumo_centavos: int
    sem_categoria_centavos: int
    resultado: str
    detalhe: str | None = None


# ---------------------------------------------------------------------------
# Resumo oficial
# ---------------------------------------------------------------------------
def to_cents(value) -> int:
    return round(float(value) * 100)


def parse_resumo(payload) -> tuple[dict[str, int], int]:
    """Do JSON do resumo, devolve (valor por categoria em centavos, total em centavos).

    Senador sem dados no ano devolve ({}, 0).
    """
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise VerificacaoError("o resumo veio em formato inesperado")
    if not payload["data"]:
        return {}, 0
    try:
        cotas = payload["data"][0]["cotas"]
        categories = {item["recurso"]: to_cents(item["valor"]) for item in cotas["despesas"]}
        total = to_cents(cotas["totalValor"])
    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise VerificacaoError(f"o resumo veio em formato inesperado: {error!r}") from error
    return categories, total


def fetch_resumos(
    client: httpx.Client, codes: Iterable[int], years: Iterable[int], *, workers: int = 8
) -> dict[tuple[int, int], tuple[dict[str, int], int]]:
    """Baixa o resumo de cada senador em cada ano (todos de uma vez, na mesma foto)."""
    codes, years = list(codes), list(years)
    pairs = [(code, year) for year in years for code in codes]

    def one(pair):
        code, year = pair
        path = f"/senadores/{code}/recursos-utilizados?ano={year}"
        try:
            return pair, parse_resumo(get_json(client, path))
        except ColetaError as error:
            raise VerificacaoError(str(error)) from error

    with ThreadPoolExecutor(max_workers=workers) as pool:
        return dict(pool.map(one, pairs))


# ---------------------------------------------------------------------------
# Comparação
# ---------------------------------------------------------------------------
def compare_cota(
    cod_senador: int,
    year: int,
    spent: dict[str, int],
    resumo: tuple[dict[str, int], int],
) -> Result:
    """Compara as despesas por categoria (centavos) com o resumo do Senado."""
    categories, resumo_total = resumo
    no_category = spent.get(NO_CATEGORY, 0)
    spent_total = sum(spent.values())

    def result(kind: str, detail: str | None = None) -> Result:
        return Result(cod_senador, year, spent_total, resumo_total, no_category, kind, detail)

    unknown = sorted(name for name in categories if name not in CATEGORY_MAP)
    if unknown:
        return result(UNEXPLAINED, f"categoria desconhecida no resumo: {unknown}")
    if sum(categories.values()) != resumo_total:
        return result(UNEXPLAINED, "as categorias do resumo não somam o total do próprio resumo")

    expected = {CATEGORY_MAP[name]: value for name, value in categories.items()}
    names = set(expected) | {name for name in spent if name != NO_CATEGORY}
    differences = [
        f"{name}: despesas {spent.get(name, 0)} contra resumo {expected.get(name, 0)}"
        for name in sorted(names)
        if spent.get(name, 0) != expected.get(name, 0)
    ]
    if differences:
        return result(UNEXPLAINED, "; ".join(differences))
    return result(EXPLAINED if no_category else IDENTICAL)


def verify_cota(
    spent: dict[tuple[int, int], dict[str, int]],
    resumos: dict[tuple[int, int], tuple[dict[str, int], int]],
) -> list[Result]:
    """Compara todos os pares senador-ano. Pares sem nenhum valor dos dois lados ficam de fora."""
    results = []
    for pair in sorted(set(spent) | set(resumos)):
        row = spent.get(pair, {})
        resumo = resumos.get(pair, ({}, 0))
        if not any(row.values()) and not any(resumo[0].values()) and resumo[1] == 0:
            continue
        results.append(compare_cota(pair[0], pair[1], row, resumo))
    return results


# ---------------------------------------------------------------------------
# A mesma foto dos dados
# ---------------------------------------------------------------------------
def local_date(stamp: str) -> date:
    return datetime.fromisoformat(stamp).astimezone().date()


def check_same_snapshot(
    manifest: dict, years: Iterable[int], cleaned_reference: date, today: date
) -> None:
    """Recusa a verificação se coleta, limpeza e resumo não forem do mesmo dia."""
    problems = []
    if not manifest.get("senadores"):
        problems.append("a lista de senadores não tem data de coleta")
    elif local_date(manifest["senadores"]) != today:
        problems.append(f"a lista de senadores é de {local_date(manifest['senadores'])}")
    for year in years:
        stamp = manifest.get("despesas", {}).get(str(year))
        if not stamp:
            problems.append(f"as despesas de {year} não têm data de coleta")
        elif local_date(stamp) != today:
            problems.append(f"as despesas de {year} são de {local_date(stamp)}")
    if cleaned_reference != today:
        problems.append(f"o banco limpo é de {cleaned_reference}")
    if problems:
        raise VerificacaoError(
            f"as bases não são da mesma foto dos dados (hoje é {today}): "
            + "; ".join(problems)
            + ". Rode a coleta (com --sobrescrever) e a limpeza de novo, e então a verificação."
        )


# ---------------------------------------------------------------------------
# Banco local
# ---------------------------------------------------------------------------
def read_spent(connection: sqlite3.Connection, years: list[int]) -> dict:
    marks = ",".join("?" * len(years))
    rows = connection.execute(
        "SELECT cod_senador, ano, categoria, SUM(valor_centavos) FROM despesas "
        f"WHERE ano IN ({marks}) GROUP BY 1, 2, 3",
        years,
    )
    spent: dict[tuple[int, int], dict[str, int]] = defaultdict(dict)
    for code, year, category, cents in rows:
        spent[(code, year)][category] = cents
    return dict(spent)


def ensure_verificacoes_table(connection: sqlite3.Connection) -> None:
    """Resumo de todas as verificações (uma linha por verificação e ano)."""
    connection.execute(
        "CREATE TABLE IF NOT EXISTS verificacoes (nome TEXT, ano INTEGER, identicos INTEGER, "
        "explicados INTEGER, sem_explicacao INTEGER, verificado_em TEXT, "
        "PRIMARY KEY (nome, ano))"
    )


def write_results(
    connection: sqlite3.Connection, results: list[Result], years: list[int], when: datetime
) -> None:
    connection.execute("DROP TABLE IF EXISTS verificacao_cota")
    ensure_verificacoes_table(connection)
    connection.execute("DELETE FROM verificacoes WHERE nome = 'cota'")
    connection.execute(
        "CREATE TABLE verificacao_cota (cod_senador INTEGER, ano INTEGER, "
        "despesas_centavos INTEGER, resumo_centavos INTEGER, sem_categoria_centavos INTEGER, "
        "resultado TEXT, detalhe TEXT, PRIMARY KEY (cod_senador, ano))"
    )
    connection.executemany(
        "INSERT INTO verificacao_cota VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            (
                r.cod_senador,
                r.ano,
                r.despesas_centavos,
                r.resumo_centavos,
                r.sem_categoria_centavos,
                r.resultado,
                r.detalhe,
            )
            for r in results
        ],
    )
    stamp = when.isoformat(timespec="seconds")
    for year in years:
        of_year = [r.resultado for r in results if r.ano == year]
        connection.execute(
            "INSERT INTO verificacoes VALUES ('cota', ?, ?, ?, ?, ?)",
            (
                year,
                of_year.count(IDENTICAL),
                of_year.count(EXPLAINED),
                of_year.count(UNEXPLAINED),
                stamp,
            ),
        )


def run(raw_dir: Path, database: Path, years: list[int] | None, client: httpx.Client, today: date):
    """Roda a verificação da cota e grava o resultado no banco limpo."""
    if not database.exists():
        raise VerificacaoError(f"falta {database}; rode a limpeza antes")

    with closing(sqlite3.connect(database)) as connection:
        stored = [row[0] for row in connection.execute("SELECT DISTINCT ano FROM despesas")]
        years = sorted(years) if years else sorted(stored)
        missing = [year for year in years if year not in stored]
        if missing:
            raise VerificacaoError(f"o banco limpo não tem despesas de {missing}")
        reference = connection.execute(
            "SELECT valor FROM metadados WHERE chave = 'data_referencia'"
        ).fetchone()
        if reference is None:
            raise VerificacaoError("o banco limpo não registra a data de referência")
        check_same_snapshot(read_manifest(raw_dir), years, date.fromisoformat(reference[0]), today)

        codes = [row[0] for row in connection.execute("SELECT cod_senador FROM senadores")]
        resumos = fetch_resumos(client, codes, years)
        results = verify_cota(read_spent(connection, years), resumos)

        with connection:
            write_results(connection, results, years, datetime.now().astimezone())
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verifica a cota contra o resumo do Senado.")
    parser.add_argument("--raw", type=Path, default=RAW_DIR, help="pasta com os dados coletados")
    parser.add_argument("--banco", type=Path, default=CLEAN_DB, help="banco SQLite limpo")
    parser.add_argument("--anos", default=None, help="anos a verificar, por exemplo 2023-2026")
    args = parser.parse_args(argv)

    try:
        years = parse_years(args.anos) if args.anos else None
        with httpx.Client(base_url=BASE_URL, timeout=60.0) as client:
            results = run(args.raw, args.banco, years, client, date.today())
    except (VerificacaoError, ValueError) as error:
        print(f"erro: {error}", file=sys.stderr)
        return 1

    by_year: dict[int, list[str]] = defaultdict(list)
    for result in results:
        by_year[result.ano].append(result.resultado)
    print("ano  idênticos  explicados  sem explicação")
    for year in sorted(by_year):
        kinds = by_year[year]
        print(
            f"{year}  {kinds.count(IDENTICAL):>9}  {kinds.count(EXPLAINED):>10}  "
            f"{kinds.count(UNEXPLAINED):>14}"
        )
    unexplained = [r for r in results if r.resultado == UNEXPLAINED]
    if unexplained:
        print(f"\n{len(unexplained)} senador(es)-ano sem explicação ficam ocultos (veja o banco).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
