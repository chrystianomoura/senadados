"""Moradia: uso de auxílio-moradia e de imóvel funcional, mês a mês, por senador.

D028 e D025: o site mostra o uso de cada benefício **mês a mês**, como o próprio Senado
mostra, e só para quem foi provado. Quatro fontes do Senado, todas baixadas na hora:

1. o **resumo anual** da API de dados abertos (`utilizou` ou `não utilizou`);
2. o **resumo da tela** do portal ("Utilizou (em 10 meses)", "Não utilizou" ou
   "Renúncia ao benefício");
3. a **página mensal** do portal, a única que traz o uso mês a mês;
4. a **lista do mês**, da API, que diz quem usa o benefício **agora**.

Resultados:
- `identico`: as quatro fontes concordam.
- `explicado`: concordam, mas a tela informa "renúncia ao benefício" onde a API diz
  "não utilizou" (quem renuncia não usa).
- `pendente`: as três primeiras concordam, mas a lista do mês mostra um estado diferente
  do último mês da página mensal. São períodos diferentes, e isso **não está provado**
  como a causa; some até a página mensal alcançar o mês da lista (D025).
- `sem_explicacao`: qualquer outra diferença.

Exibição (D037): dado descritivo, aparece para `identico` e `explicado`. Só os
`sem_explicacao` contam para o freio de segurança (mais de 5% esconde para todos); o
`pendente` tem causa provável conhecida e some só para o próprio senador.

Prova consistência entre bases do Senado, não é auditoria (D027).
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from collections import Counter
from collections.abc import Iterable
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
    EXPLAINED,
    IDENTICAL,
    UNEXPLAINED,
    VerificacaoError,
    check_same_snapshot,
    ensure_verificacoes_table,
)

PENDING = "pendente"
MANIFEST_KEY = "moradia"
MAX_FAILURE_RATE = 0.05
USER_AGENT = "senadados-pipeline/0.1"

# nome no resumo da API, e chave usada aqui
BENEFITS = {"Auxílio-Moradia": "auxilio", "Imóvel Funcional": "imovel"}
LIST_FIELDS = {"auxilio": "auxilioMoradia", "imovel": "imovelFuncional"}

USED = "utilizou"
NOT_USED = "nao_utilizou"
RENOUNCED = "renuncia"


# ---------------------------------------------------------------------------
# Leitura das páginas do portal
# ---------------------------------------------------------------------------
def page_text(html: str) -> str:
    """O texto visível da página, em uma linha."""
    html = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S)
    return re.sub(r"[\s|]+", " ", re.sub(r"<[^>]+>", "|", html)).replace("&nbsp;", " ").strip()


def parse_portal(html: str) -> tuple[dict[str, dict], str | None]:
    """O uso de benefícios na tela do senador e o número do link da página mensal.

    Devolve ({"auxilio": {"estado", "meses"}, "imovel": {...}}, número funcional ou None).
    """
    text = page_text(html)
    start = text.find("Uso de Benefícios Benefício Utilização")
    if start < 0:
        raise ColetaError("a página não traz o bloco de uso de benefícios")
    end = text.find("×", start)
    segment = text[start : end if end > 0 else start + 400]

    result: dict[str, dict] = {}
    for name, key in BENEFITS.items():
        match = re.search(
            re.escape(name)
            + r" (Não utilizou|Renúncia ao benefício|Utilizou(?: \(em (\d+) m(?:ê|e)s(?:es)?\))?)",
            segment,
        )
        if not match:
            raise ColetaError(f"não entendi o uso de {name!r} na página")
        label = match.group(1)
        if label == "Não utilizou":
            result[key] = {"estado": NOT_USED, "meses": 0}
        elif label.startswith("Renúncia"):
            result[key] = {"estado": RENOUNCED, "meses": 0}
        else:
            months = int(match.group(2)) if match.group(2) else None
            result[key] = {"estado": USED, "meses": months}

    link = re.search(r"beneficios/\?numeroFuncional=(\d+)&(?:amp;)?ano=\d{4}", html)
    return result, (link.group(1) if link else None)


def parse_mensal(html: str) -> list[list]:
    """A página mensal: [[mês "MM/AAAA", usou auxílio, usou imóvel], ...]."""
    text = page_text(html)
    if "Nenhum registro encontrado" in text:
        return []
    if "Auxílio-moradia Imóvel funcional" not in text:
        raise ColetaError("a página mensal não traz as colunas esperadas")
    rows = re.findall(r"(\d{2}/\d{4}) (Não utilizou|Utilizou) (Não utilizou|Utilizou)", text)
    if not rows:
        raise ColetaError("a página mensal veio sem meses")
    return [[month, a == "Utilizou", i == "Utilizou"] for month, a, i in rows]


# ---------------------------------------------------------------------------
# Coleta
# ---------------------------------------------------------------------------
def fetch_senator(client: httpx.Client, code: int, year: int) -> dict:
    """Os dados de moradia de um senador. Falha de um só vira `erro`, e não derruba os outros."""
    try:
        api = get_json(client, f"/senadores/{code}/recursos-utilizados?ano={year}")
        data = api.get("data") if isinstance(api, dict) else None
        if not isinstance(data, list) or not data or "beneficios" not in data[0]:
            raise ColetaError("o resumo da API veio em formato inesperado")
        benefits = {item["beneficio"]: item["utilizacao"] for item in data[0]["beneficios"]}

        portal, number = parse_portal(get_text(client, f"{PORTAL_URL}/sen/{code}/?ano={year}"))
        monthly: list[list] = []
        if number:
            url = f"{PORTAL_URL}/sen/{code}/beneficios/?numeroFuncional={number}&ano={year}"
            monthly = parse_mensal(get_text(client, url))
        return {"api": benefits, "portal": portal, "mensal": monthly}
    except (ColetaError, KeyError, TypeError) as error:
        return {"erro": f"{type(error).__name__}: {error}"}


def collect_moradia(
    client: httpx.Client, raw_dir: Path, codes: Iterable[int], clock=now_local, *, workers: int = 8
):
    """Baixa as quatro fontes e grava só o que o pipeline usa (sem o número funcional)."""
    codes = list(codes)
    year = clock().year
    listed = get_json(client, "/senadores/auxilio-moradia-imoveis-funcionais")
    if not isinstance(listed, dict) or not isinstance(listed.get("data"), list):
        raise ColetaError("a lista de moradia veio em formato inesperado")

    with ThreadPoolExecutor(max_workers=workers) as pool:
        fetched = list(pool.map(lambda code: fetch_senator(client, code, year), codes))
    records = dict(zip(codes, fetched, strict=True))

    write_json(
        raw_dir / "moradia" / "uso.json",
        {
            "ano": year,
            "senadores": {str(c): r for c, r in records.items()},
            "lista": listed["data"],
        },
    )
    manifest = read_manifest(raw_dir)
    manifest[MANIFEST_KEY] = clock().isoformat(timespec="seconds")
    write_json(raw_dir / "coleta.json", manifest)
    return year, records, listed["data"]


# ---------------------------------------------------------------------------
# Comparação
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Result:
    cod_senador: int
    ano: int
    resultado: str
    detalhe: str | None = None
    exibir: bool = False


def compare_moradia(cod_senador: int, year: int, record: dict, listed: dict | None) -> Result:
    """Compara as quatro fontes para um senador."""

    def result(kind: str, detail: str | None = None) -> Result:
        return Result(cod_senador, year, kind, detail)

    if "erro" in record:
        return result(UNEXPLAINED, record["erro"])

    months = record["mensal"]
    if any(not month[0].endswith(f"/{year}") for month in months):
        return result(UNEXPLAINED, "a página mensal traz meses de outro ano")
    if len({month[0] for month in months}) != len(months):
        return result(UNEXPLAINED, "a página mensal repete um mês")

    renounced = False
    for name, key in BENEFITS.items():
        api_state = record["api"].get(name)
        if api_state not in ("Utilizou", "Não utilizou"):
            return result(UNEXPLAINED, f"{name}: resumo da API com valor inesperado {api_state!r}")
        used_by_api = api_state == "Utilizou"
        portal = record["portal"][key]
        index = 1 if key == "auxilio" else 2
        used_months = sum(1 for month in months if month[index])

        if portal["estado"] == USED:
            if not used_by_api:
                return result(UNEXPLAINED, f"{name}: a tela diz que usou e a API diz que não")
            expected = portal["meses"] if portal["meses"] is not None else used_months
            if used_months == 0 or used_months != expected:
                return result(
                    UNEXPLAINED,
                    f"{name}: a tela diz {expected} mês(es) e a página mensal tem {used_months}",
                )
        else:
            if used_by_api:
                return result(UNEXPLAINED, f"{name}: a API diz que usou e a tela diz que não")
            if used_months:
                return result(
                    UNEXPLAINED, f"{name}: a tela diz que não usou e a página mensal tem uso"
                )
            renounced = renounced or portal["estado"] == RENOUNCED

    if listed is None:
        return result(UNEXPLAINED, "o senador não consta na lista de moradia do mês")

    differences = []
    for name, key in BENEFITS.items():
        index = 1 if key == "auxilio" else 2
        last = bool(months[-1][index]) if months else False
        now = listed.get(LIST_FIELDS[key]) == "S"
        if now != last:
            last_month = months[-1][0] if months else "sem meses"
            differences.append(
                f"{name}: a lista de hoje diz {'usa' if now else 'não usa'} e o último mês "
                f"da página mensal ({last_month}) diz {'usou' if last else 'não usou'}"
            )
    if differences:
        return result(PENDING, "; ".join(differences))
    return result(EXPLAINED if renounced else IDENTICAL)


def apply_release_rule(results: list[Result]) -> list[Result]:
    """Define quem aparece (`exibir`). Só `sem_explicacao` conta para o freio (D037)."""
    failures = sum(r.resultado == UNEXPLAINED for r in results)
    if not results or failures / len(results) > MAX_FAILURE_RATE:
        return [replace(r, exibir=False) for r in results]
    return [replace(r, exibir=r.resultado in (IDENTICAL, EXPLAINED)) for r in results]


def build_listed(entries: list[dict]) -> dict[str, dict]:
    """A lista de moradia por nome normalizado. Recusa nome repetido."""
    by_name: dict[str, dict] = {}
    for entry in entries:
        name = entry.get("nomeParlamentar")
        if not name:
            continue
        key = normalize(name)
        if key in by_name:
            raise VerificacaoError(f"a lista de moradia repete o nome {name!r}")
        by_name[key] = entry
    return by_name


def verify_moradia(
    senators: dict[int, str], year: int, records: dict, entries: list[dict]
) -> list[Result]:
    listed = build_listed(entries)
    results = []
    for code in sorted(senators):
        record = records.get(code) or records.get(str(code)) or {"erro": "senador sem dados"}
        results.append(compare_moradia(code, year, record, listed.get(normalize(senators[code]))))
    return apply_release_rule(results)


# ---------------------------------------------------------------------------
# Banco local
# ---------------------------------------------------------------------------
def write_results(
    connection: sqlite3.Connection,
    results: list[Result],
    records: dict,
    year: int,
    when: datetime,
) -> None:
    connection.execute("DROP TABLE IF EXISTS verificacao_moradia")
    connection.execute("DROP TABLE IF EXISTS moradia_meses")
    connection.execute(
        "CREATE TABLE verificacao_moradia (cod_senador INTEGER, ano INTEGER, resultado TEXT, "
        "detalhe TEXT, exibir INTEGER, PRIMARY KEY (cod_senador, ano))"
    )
    connection.execute(
        "CREATE TABLE moradia_meses (cod_senador INTEGER, ano INTEGER, mes TEXT, "
        "auxilio_moradia INTEGER, imovel_funcional INTEGER, PRIMARY KEY (cod_senador, ano, mes))"
    )
    connection.executemany(
        "INSERT INTO verificacao_moradia VALUES (?, ?, ?, ?, ?)",
        [(r.cod_senador, r.ano, r.resultado, r.detalhe, int(r.exibir)) for r in results],
    )
    rows = []
    for r in results:
        record = records.get(r.cod_senador) or records.get(str(r.cod_senador)) or {}
        for month, aux, imo in record.get("mensal", []):
            mm, yy = month.split("/")
            rows.append((r.cod_senador, year, f"{yy}-{mm}", int(aux), int(imo)))
    connection.executemany("INSERT INTO moradia_meses VALUES (?, ?, ?, ?, ?)", rows)

    ensure_verificacoes_table(connection)
    connection.execute("DELETE FROM verificacoes WHERE nome = 'moradia'")
    kinds = Counter(r.resultado for r in results)
    connection.execute(
        "INSERT INTO verificacoes VALUES ('moradia', ?, ?, ?, ?, ?)",
        (
            year,
            kinds[IDENTICAL],
            kinds[EXPLAINED],
            kinds[UNEXPLAINED],
            when.isoformat(timespec="seconds"),
        ),
    )


def run(
    raw_dir: Path, database: Path, client: httpx.Client, today: date, clock=now_local
) -> list[Result]:
    """Coleta a moradia agora e verifica contra a lista de senadores do banco limpo."""
    if not database.exists():
        raise VerificacaoError(f"falta {database}; rode a limpeza antes")
    with closing(sqlite3.connect(database)) as connection:
        reference = connection.execute(
            "SELECT valor FROM metadados WHERE chave = 'data_referencia'"
        ).fetchone()
        if reference is None:
            raise VerificacaoError("o banco limpo não registra a data de referência")
        check_same_snapshot(read_manifest(raw_dir), [], date.fromisoformat(reference[0]), today)
        senators = dict(connection.execute("SELECT cod_senador, nome FROM senadores"))

        try:
            year, records, entries = collect_moradia(client, raw_dir, senators, clock)
        except ColetaError as error:
            raise VerificacaoError(str(error)) from error
        results = verify_moradia(senators, year, records, entries)
        with connection:
            write_results(connection, results, records, year, clock())
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coleta e verifica o uso de moradia.")
    parser.add_argument("--raw", type=Path, default=RAW_DIR, help="pasta dos dados coletados")
    parser.add_argument("--banco", type=Path, default=CLEAN_DB, help="banco SQLite limpo")
    args = parser.parse_args(argv)

    try:
        headers = {"User-Agent": USER_AGENT}
        with httpx.Client(base_url=BASE_URL, timeout=120.0, headers=headers) as client:
            results = run(args.raw, args.banco, client, date.today())
    except (VerificacaoError, ColetaError) as error:
        print(f"erro: {error}", file=sys.stderr)
        return 1

    kinds = Counter(r.resultado for r in results)
    print(f"senadores: {len(results)}")
    for kind in (IDENTICAL, EXPLAINED, PENDING, UNEXPLAINED):
        print(f"{kind}: {kinds[kind]}")
    print(f"moradia exibida para: {sum(r.exibir for r in results)}")
    for result in results:
        if result.resultado in (PENDING, UNEXPLAINED):
            print(f"  [{result.resultado}] senador {result.cod_senador}: {result.detalhe}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
