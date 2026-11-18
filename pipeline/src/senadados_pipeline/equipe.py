"""Equipe do gabinete: o número de pessoas do resumo oficial contra a lista de servidores.

D015 e D025: o site mostra só o **número** de pessoas, vindo do resumo oficial, e só se
ele bater com a lista de servidores ativos do Senado, por gabinete e por tipo de vínculo.

Nomes de servidores **nunca** são guardados (D007): a lista é contada por gabinete e
vínculo na hora do download, e só as contagens vão para o disco.

Resultados: `identico` ou `sem_explicacao`. Não existe "explicado" aqui, porque não há
nenhuma diferença conhecida entre as duas fontes.

Exibição (D037): a equipe é um dado **descritivo**, não entra em ranking. Aparece para os
gabinetes `identico` e some para os outros. Há um freio de segurança: se mais de 5% dos
gabinetes falharem, o problema provavelmente é nosso ou da API do Senado, e a equipe some
para todos.

Prova consistência entre bases do Senado, não é auditoria (D027).
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
import unicodedata
from collections import Counter, defaultdict
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
    now_local,
    read_manifest,
    write_json,
)
from senadados_pipeline.config import BASE_URL, CLEAN_DB, RAW_DIR
from senadados_pipeline.verificacao import (
    IDENTICAL,
    UNEXPLAINED,
    VerificacaoError,
    check_same_snapshot,
    ensure_verificacoes_table,
)

MANIFEST_KEY = "equipe"
# Acima disso, falha demais para ser uma discrepância isolada da fonte (D037).
MAX_FAILURE_RATE = 0.05
GABINETE = re.compile(r"(?i)^gabinete d[oa] senador(?:a)? (?P<nome>.+)$")
# O senador também consta na lista de servidores do próprio gabinete; ele não é "equipe".
SENATOR_LINK = "PARLAMENTAR"


# ---------------------------------------------------------------------------
# Coleta (sem nomes de pessoas)
# ---------------------------------------------------------------------------
def aggregate_gabinetes(servers) -> list[dict]:
    """Conta os servidores ativos por gabinete de senador e vínculo.

    Só as contagens saem daqui; o nome de cada servidor é descartado (D007).
    """
    if not isinstance(servers, list):
        raise ColetaError("a lista de servidores veio em formato inesperado")
    counts: Counter = Counter()
    for server in servers:
        try:
            lotacao = server["lotacao"]
            vinculo = server["vinculo"]
            situation = server["situacao"]
        except (KeyError, TypeError) as error:
            raise ColetaError(f"servidor em formato inesperado: {error!r}") from error
        if situation != "ATIVO":
            raise ColetaError(f"a lista de ativos trouxe situação {situation!r}")
        name = ((lotacao or {}).get("nome") or "").strip()
        if GABINETE.match(name):
            counts[(lotacao["sigla"], name, vinculo)] += 1
    return [
        {"sigla": sigla, "nome": name, "vinculo": vinculo, "quantidade": quantity}
        for (sigla, name, vinculo), quantity in sorted(counts.items())
    ]


def fetch_pessoal(
    client: httpx.Client, codes: Iterable[int], year: int, *, workers: int = 8
) -> dict[str, list]:
    """O bloco `pessoal` do resumo de cada senador, como o Senado publica."""
    codes = list(codes)

    def one(code: int):
        payload = get_json(client, f"/senadores/{code}/recursos-utilizados?ano={year}")
        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, list) or not data or "pessoal" not in data[0]:
            raise ColetaError(f"o resumo do senador {code} veio em formato inesperado")
        return str(code), data[0]["pessoal"]

    with ThreadPoolExecutor(max_workers=workers) as pool:
        return dict(pool.map(one, codes))


def collect_equipe(client: httpx.Client, raw_dir: Path, codes: Iterable[int], clock=now_local):
    """Baixa o resumo e a lista de servidores e grava só o que o pipeline usa."""
    year = clock().year
    pessoal = fetch_pessoal(client, codes, year)
    gabinetes = aggregate_gabinetes(get_json(client, "/servidores/servidores/ativos"))
    write_json(raw_dir / "equipe" / "resumo_pessoal.json", {"ano": year, "senadores": pessoal})
    write_json(raw_dir / "equipe" / "gabinetes_ativos.json", gabinetes)
    manifest = read_manifest(raw_dir)
    manifest[MANIFEST_KEY] = clock().isoformat(timespec="seconds")
    write_json(raw_dir / "coleta.json", manifest)
    return year, pessoal, gabinetes


# ---------------------------------------------------------------------------
# Ligação entre senador e gabinete
# ---------------------------------------------------------------------------
def normalize(text: str) -> str:
    plain = "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"\s+", " ", plain.upper().strip())


def _word_prefix(short: str, long: str) -> bool:
    return long == short or long.startswith(short + " ")


def link_gabinetes(senators: dict[int, str], gabinetes: list[dict]) -> dict[int, str]:
    """Liga cada senador à sigla do gabinete, pelo nome. Devolve código -> sigla.

    1. Nome igual. 2. Um nome inteiro dentro do outro, em palavras ("Nelsinho Trad" e
    "Nelsinho Trad Filho"), só se houver uma única possibilidade. Quem não se liga fica
    de fora, e a verificação o marca como sem explicação. A contagem de pessoas, que vem
    de outra fonte, é a segunda barreira contra uma ligação errada.
    """
    names: dict[str, str] = {}
    for item in gabinetes:
        match = GABINETE.match(item["nome"])
        if match:
            names[item["sigla"]] = normalize(match.group("nome"))

    by_name = {normalize(name): code for code, name in senators.items()}
    links: dict[int, str] = {}
    used: set[str] = set()
    for sigla, name in sorted(names.items()):
        if name in by_name and by_name[name] not in links:
            links[by_name[name]] = sigla
            used.add(sigla)
    for code, senator_name in sorted(senators.items()):
        if code in links:
            continue
        key = normalize(senator_name)
        candidates = [
            sigla
            for sigla, name in names.items()
            if sigla not in used and (_word_prefix(name, key) or _word_prefix(key, name))
        ]
        if len(candidates) == 1:
            links[code] = candidates[0]
            used.add(candidates[0])
    return links


# ---------------------------------------------------------------------------
# Comparação
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Result:
    cod_senador: int
    ano: int
    equipe_resumo: int | None
    equipe_lista: int | None
    resultado: str
    detalhe: str | None = None
    exibir: bool = False


def resumo_gabinete(pessoal) -> tuple[int, dict[str, int]]:
    """Total e quebra por vínculo do gabinete, no resumo. Sem entrada, é zero."""
    if not isinstance(pessoal, list):
        raise VerificacaoError("o bloco de pessoal do resumo veio em formato inesperado")
    entries = [item for item in pessoal if item.get("local") == "Gabinete"]
    if not entries:
        return 0, {}
    try:
        entry = entries[0]
        by_link = {normalize(v["vinculo"]): int(v["quantidade"]) for v in entry["vinculos"]}
        total = int(entry["quantidade"])
    except (KeyError, TypeError, ValueError) as error:
        raise VerificacaoError(f"pessoal do resumo em formato inesperado: {error!r}") from error
    if total != sum(by_link.values()):
        raise VerificacaoError("o resumo não soma o total de pessoas por vínculo")
    return total, {k: v for k, v in by_link.items() if v}


def compare_equipe(cod_senador: int, year: int, pessoal, listed: dict[str, int] | None) -> Result:
    """Compara a equipe do resumo com a lista de servidores (`listed`: vínculo -> pessoas)."""
    try:
        total, by_link = resumo_gabinete(pessoal)
    except VerificacaoError as error:
        return Result(cod_senador, year, None, None, UNEXPLAINED, str(error))
    if listed is None:
        return Result(cod_senador, year, total, None, UNEXPLAINED, "gabinete não encontrado")
    staff = {k: v for k, v in listed.items() if k != SENATOR_LINK and v}
    listed_total = sum(staff.values())
    if by_link == staff:
        return Result(cod_senador, year, total, listed_total, IDENTICAL)
    parts = [
        f"{name}: resumo {by_link.get(name, 0)} contra lista {staff.get(name, 0)}"
        for name in sorted(set(by_link) | set(staff))
        if by_link.get(name, 0) != staff.get(name, 0)
    ]
    return Result(cod_senador, year, total, listed_total, UNEXPLAINED, "; ".join(parts))


def verify_equipe(
    senators: dict[int, str], year: int, pessoal: dict[str, list], gabinetes: list[dict]
) -> list[Result]:
    links = link_gabinetes(senators, gabinetes)
    by_sigla: dict[str, dict[str, int]] = defaultdict(dict)
    for item in gabinetes:
        by_sigla[item["sigla"]][normalize(item["vinculo"])] = item["quantidade"]
    results = []
    for code in sorted(senators):
        listed = by_sigla.get(links[code]) if code in links else None
        # `by_sigla` guarda vínculos em maiúsculas; o resumo foi normalizado do mesmo jeito.
        results.append(compare_equipe(code, year, pessoal.get(str(code)), listed))
    return apply_release_rule(results)


def apply_release_rule(results: list[Result]) -> list[Result]:
    """Define quem aparece (`exibir`): os idênticos, salvo se houver falha demais (D037).

    O freio de segurança existe porque uma falha isolada é uma discrepância da fonte,
    mas muitas juntas indicam problema na nossa ligação ou mudança na API do Senado.
    """
    failures = sum(r.resultado != IDENTICAL for r in results)
    if not results or failures / len(results) > MAX_FAILURE_RATE:
        return [replace(r, exibir=False) for r in results]
    return [replace(r, exibir=r.resultado == IDENTICAL) for r in results]


# ---------------------------------------------------------------------------
# Banco local
# ---------------------------------------------------------------------------
def write_results(
    connection: sqlite3.Connection, results: list[Result], year: int, when: datetime
) -> None:
    connection.execute("DROP TABLE IF EXISTS verificacao_equipe")
    connection.execute(
        "CREATE TABLE verificacao_equipe (cod_senador INTEGER, ano INTEGER, "
        "equipe_resumo INTEGER, equipe_lista INTEGER, resultado TEXT, detalhe TEXT, "
        "exibir INTEGER, PRIMARY KEY (cod_senador, ano))"
    )
    connection.executemany(
        "INSERT INTO verificacao_equipe VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            (
                r.cod_senador,
                r.ano,
                r.equipe_resumo,
                r.equipe_lista,
                r.resultado,
                r.detalhe,
                int(r.exibir),
            )
            for r in results
        ],
    )
    ensure_verificacoes_table(connection)
    connection.execute("DELETE FROM verificacoes WHERE nome = 'equipe'")
    kinds = [r.resultado for r in results]
    connection.execute(
        "INSERT INTO verificacoes VALUES ('equipe', ?, ?, 0, ?, ?)",
        (
            year,
            kinds.count(IDENTICAL),
            kinds.count(UNEXPLAINED),
            when.isoformat(timespec="seconds"),
        ),
    )


def run(
    raw_dir: Path, database: Path, client: httpx.Client, today: date, clock=now_local
) -> list[Result]:
    """Coleta a equipe agora e verifica contra a lista de senadores do banco limpo."""
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
            year, pessoal, gabinetes = collect_equipe(client, raw_dir, senators, clock)
        except ColetaError as error:
            raise VerificacaoError(str(error)) from error
        results = verify_equipe(senators, year, pessoal, gabinetes)
        with connection:
            write_results(connection, results, year, clock())
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coleta e verifica a equipe dos gabinetes.")
    parser.add_argument("--raw", type=Path, default=RAW_DIR, help="pasta dos dados coletados")
    parser.add_argument("--banco", type=Path, default=CLEAN_DB, help="banco SQLite limpo")
    args = parser.parse_args(argv)

    try:
        with httpx.Client(base_url=BASE_URL, timeout=120.0) as client:
            results = run(args.raw, args.banco, client, date.today())
    except (VerificacaoError, ColetaError) as error:
        print(f"erro: {error}", file=sys.stderr)
        return 1

    kinds = [r.resultado for r in results]
    shown = sum(r.exibir for r in results)
    print(f"gabinetes: {len(results)}")
    print(f"idênticos: {kinds.count(IDENTICAL)}")
    print(f"sem explicação: {kinds.count(UNEXPLAINED)}")
    print(f"equipe exibida para: {shown}")
    for result in results:
        if result.resultado == UNEXPLAINED:
            print(f"  senador {result.cod_senador}: {result.detalhe}")
    if UNEXPLAINED in kinds and not shown:
        print("\nFalhas demais (freio de segurança, D037): a equipe não aparece para ninguém.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
