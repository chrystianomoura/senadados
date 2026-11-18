"""Contato do gabinete: endereço, telefones e e-mail, da API contra a página do portal.

D031 e D025: o site mostra o endereço do gabinete, os telefones (copiados da página do
portal, que traz os números completos) e o e-mail. O escritório de apoio fica fora.

Compara, para cada senador, a API de dados abertos com a seção "Dados pessoais" da página
dele no portal. Cada campo tem o seu resultado:

- `identico`: os dois dizem a mesma coisa (ou nenhum dos dois traz o campo).
- `explicado`: só nos telefones. A página traz números a mais do que a API, e todos os
  números da API estão na página. A API nunca lista mais de dois números e a página
  lista até cinco; o motivo **não foi confirmado** pelo Senado.
- `sem_explicacao`: qualquer outra diferença, ou página fora do formato.

Exibição (D037): contato é dado descritivo. Cada campo aparece para quem foi provado e
tem o próprio freio de segurança (mais de 5% de falhas esconde o campo de todos). Quem não
tem o campo simplesmente não o mostra (D025, exceção do contato). Só o valor provado vai
para a tabela `contato`; o que não foi provado fica vazio.

Prova consistência entre bases do Senado, não é auditoria (D027).
"""

from __future__ import annotations

import argparse
import html
import json
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
    get_text,
    now_local,
    read_manifest,
    write_json,
)
from senadados_pipeline.config import CLEAN_DB, MAX_FAILURE_RATE, PORTAL_URL, RAW_DIR, USER_AGENT
from senadados_pipeline.verificacao import (
    EXPLAINED,
    IDENTICAL,
    UNEXPLAINED,
    VerificacaoError,
    check_snapshot,
    ensure_verificacoes_table,
)

MANIFEST_KEY = "contato"
FIELDS = ("endereco", "telefones", "email")
PORTAL_LABELS = {"endereco": "Gabinete", "telefones": "Telefones", "email": "E-mail"}

FULL_PHONE = re.compile(r"^\(\d{2}\) \d{4,5}-\d{4}$")
SHORT_SUFFIX = re.compile(r"^\d{4}$")
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------------------------------------------------------------------------
# Leitura da página do portal
# ---------------------------------------------------------------------------
def collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_portal(page: str) -> dict[str, str | None]:
    """Gabinete, telefones e e-mail da seção "Dados pessoais". Campo ausente vira None."""
    if "Dados Pessoais" not in page:
        raise ColetaError("a página não traz a seção de dados pessoais")
    found: dict[str, str | None] = {}
    for field, label in PORTAL_LABELS.items():
        match = re.search(rf"<dt>{re.escape(label)}:</dt>\s*<dd>(.*?)</dd>", page, flags=re.S)
        if not match:
            found[field] = None
            continue
        text = collapse(html.unescape(re.sub(r"<[^>]+>", "", match.group(1))))
        found[field] = text or None
    return found


def expand_phones(text: str) -> list[str]:
    """Telefones completos, um por número.

    O Senado abrevia vários números ("(61) 3303-6187 / 6188 / 6183"). A regra é mecânica:
    o início do primeiro número vale para os seguintes que trouxerem só os 4 últimos dígitos.
    """
    parts = [collapse(part) for part in text.split("/") if collapse(part)]
    if not parts or not FULL_PHONE.match(parts[0]):
        raise ColetaError(f"telefone em formato inesperado: {text!r}")
    prefix = parts[0][:-4]
    phones = [parts[0]]
    for part in parts[1:]:
        phone = prefix + part if SHORT_SUFFIX.match(part) else part
        if not FULL_PHONE.match(phone):
            raise ColetaError(f"telefone em formato inesperado: {text!r}")
        phones.append(phone)
    return phones


def digits(text: str) -> str:
    return re.sub(r"\D", "", text)


# ---------------------------------------------------------------------------
# Coleta
# ---------------------------------------------------------------------------
def fetch_portal(client: httpx.Client, code: int, year: int) -> dict:
    """O contato de um senador no portal. A falha de um só vira `erro`."""
    try:
        return parse_portal(get_text(client, f"{PORTAL_URL}/sen/{code}/?ano={year}"))
    except ColetaError as error:
        return {"erro": f"ColetaError: {error}"}


def collect_contato(client: httpx.Client, raw_dir: Path, codes, clock=now_local, *, workers=8):
    codes = list(codes)
    year = clock().year
    with ThreadPoolExecutor(max_workers=workers) as pool:
        fetched = list(pool.map(lambda code: fetch_portal(client, code, year), codes))
    records = {str(code): record for code, record in zip(codes, fetched, strict=True)}
    write_json(raw_dir / "contato" / "portal.json", records)
    manifest = read_manifest(raw_dir)
    manifest[MANIFEST_KEY] = clock().isoformat(timespec="seconds")
    write_json(raw_dir / "coleta.json", manifest)
    return records


def load_api(raw_dir: Path) -> dict[int, dict]:
    """O contato como a API publica, da lista de senadores que a coleta gravou."""
    path = raw_dir / "senadores_atuais.json"
    if not path.exists():
        raise VerificacaoError(f"falta {path}; rode a coleta antes")
    data = json.loads(path.read_text(encoding="utf-8")).get("data")
    if not isinstance(data, list):
        raise VerificacaoError("a lista de senadores está em formato inesperado")
    try:
        return {int(item["codigoParlamentar"]): item for item in data}
    except (KeyError, TypeError, ValueError) as error:
        raise VerificacaoError(
            f"a lista de senadores está em formato inesperado: {error!r}"
        ) from error


# ---------------------------------------------------------------------------
# Comparação
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Field:
    cod_senador: int
    campo: str
    resultado: str
    valor: str | None = None  # o valor que pode aparecer (só se não houver freio)
    detalhe: str | None = None
    exibir: bool = False


def clean_email(value) -> str | None:
    text = collapse(value or "").lower()
    if text in ("", "-"):
        return None
    return text


def compare_address(code: int, api_value, portal_value) -> Field:
    api, portal = collapse(api_value or ""), collapse(portal_value or "")
    if not portal:
        return Field(code, "endereco", UNEXPLAINED, detalhe="o portal não traz o gabinete")
    if api.casefold() != portal.casefold():
        return Field(
            code, "endereco", UNEXPLAINED, detalhe="o endereço da API e o do portal diferem"
        )
    return Field(code, "endereco", IDENTICAL, valor=portal)


def compare_phones(code: int, api_value, portal_value) -> Field:
    if not portal_value:
        return Field(code, "telefones", UNEXPLAINED, detalhe="o portal não traz telefones")
    try:
        portal = expand_phones(portal_value)
    except ColetaError as error:
        return Field(code, "telefones", UNEXPLAINED, detalhe=str(error))
    api = [digits(p) for p in (api_value or "").split(";") if digits(p)]
    portal_digits = [digits(p) for p in portal]
    if not api:
        return Field(code, "telefones", UNEXPLAINED, detalhe="a API não traz telefones")
    value = "\n".join(portal)
    if set(api) == set(portal_digits):
        return Field(code, "telefones", IDENTICAL, valor=value)
    if set(api) < set(portal_digits):
        extra = len(set(portal_digits) - set(api))
        return Field(
            code,
            "telefones",
            EXPLAINED,
            valor=value,
            detalhe=f"o portal traz {extra} número(s) a mais que a API",
        )
    return Field(code, "telefones", UNEXPLAINED, detalhe="a API tem número que o portal não tem")


def compare_email(code: int, api_value, portal_value) -> Field:
    api, portal = clean_email(api_value), clean_email(portal_value)
    for value in (api, portal):
        if value is not None and not EMAIL.match(value):
            return Field(code, "email", UNEXPLAINED, detalhe="e-mail em formato inesperado")
    if api != portal:
        return Field(code, "email", UNEXPLAINED, detalhe="o e-mail da API e o do portal diferem")
    return Field(code, "email", IDENTICAL, valor=portal)


def compare_contato(code: int, api: dict | None, portal: dict | None) -> list[Field]:
    """Os três campos de um senador."""
    if api is None or portal is None or "erro" in portal:
        reason = (portal or {}).get("erro", "senador sem dados")
        return [Field(code, field, UNEXPLAINED, detalhe=reason) for field in FIELDS]
    return [
        compare_address(code, api.get("endereco"), portal.get("endereco")),
        compare_phones(code, api.get("telefones"), portal.get("telefones")),
        compare_email(code, api.get("email"), portal.get("email")),
    ]


def apply_release_rule(fields: list[Field]) -> list[Field]:
    """Define o que aparece, campo a campo, com o freio de segurança de cada campo (D037)."""
    out: list[Field] = []
    for name in FIELDS:
        group = [f for f in fields if f.campo == name]
        failures = sum(f.resultado == UNEXPLAINED for f in group)
        braked = not group or failures / len(group) > MAX_FAILURE_RATE
        for f in group:
            ok = f.resultado in (IDENTICAL, EXPLAINED) and f.valor is not None and not braked
            out.append(replace(f, exibir=ok, valor=f.valor if ok else None))
    return out


def verify_contato(senators: dict[int, str], api: dict, portal: dict) -> list[Field]:
    fields: list[Field] = []
    for code in sorted(senators):
        fields += compare_contato(code, api.get(code), portal.get(str(code)))
    return apply_release_rule(fields)


# ---------------------------------------------------------------------------
# Banco local
# ---------------------------------------------------------------------------
def write_results(
    connection: sqlite3.Connection, fields: list[Field], year: int, when: datetime
) -> None:
    connection.execute("DROP TABLE IF EXISTS verificacao_contato")
    connection.execute("DROP TABLE IF EXISTS contato")
    connection.execute(
        "CREATE TABLE verificacao_contato (cod_senador INTEGER, campo TEXT, resultado TEXT, "
        "detalhe TEXT, exibir INTEGER, PRIMARY KEY (cod_senador, campo))"
    )
    connection.execute(
        "CREATE TABLE contato (cod_senador INTEGER PRIMARY KEY, endereco TEXT, telefones TEXT, "
        "email TEXT)"
    )
    connection.executemany(
        "INSERT INTO verificacao_contato VALUES (?, ?, ?, ?, ?)",
        [(f.cod_senador, f.campo, f.resultado, f.detalhe, int(f.exibir)) for f in fields],
    )
    by_senator: dict[int, dict[str, str | None]] = {}
    for f in fields:
        by_senator.setdefault(f.cod_senador, {})[f.campo] = f.valor
    connection.executemany(
        "INSERT INTO contato VALUES (?, ?, ?, ?)",
        [(c, v.get("endereco"), v.get("telefones"), v.get("email")) for c, v in by_senator.items()],
    )
    ensure_verificacoes_table(connection)
    connection.execute("DELETE FROM verificacoes WHERE nome LIKE 'contato_%'")
    stamp = when.isoformat(timespec="seconds")
    for name in FIELDS:
        kinds = Counter(f.resultado for f in fields if f.campo == name)
        connection.execute(
            "INSERT INTO verificacoes VALUES (?, ?, ?, ?, ?, ?)",
            (
                f"contato_{name}",
                year,
                kinds[IDENTICAL],
                kinds[EXPLAINED],
                kinds[UNEXPLAINED],
                stamp,
            ),
        )


def run(
    raw_dir: Path, database: Path, client: httpx.Client, today: date, clock=now_local
) -> list[Field]:
    """Coleta o contato do portal agora e compara com a API da lista de senadores."""
    if not database.exists():
        raise VerificacaoError(f"falta {database}; rode a limpeza antes")
    with closing(sqlite3.connect(database)) as connection:
        check_snapshot(connection, raw_dir, [], today)
        senators = dict(connection.execute("SELECT cod_senador, nome FROM senadores"))
        api = load_api(raw_dir)

        records = collect_contato(client, raw_dir, senators, clock)
        fields = verify_contato(senators, api, records)
        with connection:
            write_results(connection, fields, clock().year, clock())
    return fields


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coleta e verifica o contato dos gabinetes.")
    parser.add_argument("--raw", type=Path, default=RAW_DIR, help="pasta dos dados coletados")
    parser.add_argument("--banco", type=Path, default=CLEAN_DB, help="banco SQLite limpo")
    args = parser.parse_args(argv)

    try:
        with httpx.Client(timeout=120.0, headers={"User-Agent": USER_AGENT}) as client:
            fields = run(args.raw, args.banco, client, date.today())
    except (VerificacaoError, ColetaError) as error:
        print(f"erro: {error}", file=sys.stderr)
        return 1

    for name in FIELDS:
        group = [f for f in fields if f.campo == name]
        kinds = Counter(f.resultado for f in group)
        shown = sum(f.exibir for f in group)
        print(
            f"{name}: {kinds[IDENTICAL]} idênticos, {kinds[EXPLAINED]} explicados, "
            f"{kinds[UNEXPLAINED]} sem explicação; aparece para {shown}"
        )
    for f in fields:
        if f.resultado == UNEXPLAINED:
            print(f"  senador {f.cod_senador} ({f.campo}): {f.detalhe}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
