"""Coleta dos dados abertos do Senado.

Baixa a lista dos senadores em exercício e as despesas da cota (CEAPS) de cada ano.
Só grava no disco as despesas de quem está na lista (decisão D026): a API devolve
também ex-senadores, e esses dados não devem ser guardados.

A API é a fonte principal (D005). O que a API devolve é gravado sem alteração; a
limpeza e a validação vêm em etapas seguintes.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Iterable
from datetime import date, datetime
from pathlib import Path

import httpx

from senadados_pipeline.config import BASE_URL, FIRST_YEAR, RAW_DIR

MANIFEST = "coleta.json"

# Erros que costumam passar sozinhos: vale tentar de novo. Os outros (404, 400...) não.
TRANSIENT_STATUS = {429, 500, 502, 503, 504}


class ColetaError(Exception):
    """A coleta falhou ou o Senado devolveu algo diferente do esperado."""


def get_json(client: httpx.Client, path: str, *, attempts: int = 3, wait: float = 2.0):
    """Faz um GET e devolve o JSON. Tenta de novo em erro de rede ou de servidor."""
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            response = client.get(path)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as error:
            last_error = error
            if error.response.status_code not in TRANSIENT_STATUS:
                break
        except (httpx.TransportError, ValueError) as error:
            last_error = error
        if attempt < attempts:
            time.sleep(wait * attempt)
    raise ColetaError(f"falha ao ler {path}: {last_error}") from last_error


def fetch_senadores(client: httpx.Client) -> dict:
    """Lista oficial dos senadores em exercício, como o Senado publica."""
    payload = get_json(client, "/senadores")
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise ColetaError("a lista de senadores veio em formato inesperado")
    if not payload["data"]:
        raise ColetaError("a lista de senadores veio vazia")
    for item in payload["data"]:
        if "codigoParlamentar" not in item:
            raise ColetaError("senador sem 'codigoParlamentar' na lista")
    return payload


def senator_codes(senadores: dict) -> set[int]:
    return {int(item["codigoParlamentar"]) for item in senadores["data"]}


def fetch_despesas(client: httpx.Client, year: int, codes: set[int]) -> list[dict]:
    """Despesas de um ano, só dos senadores em exercício (D026)."""
    payload = get_json(client, f"/senadores/despesas_ceaps/{year}")
    if not isinstance(payload, list):
        raise ColetaError(f"as despesas de {year} vieram em formato inesperado")
    for row in payload:
        if "codSenador" not in row:
            raise ColetaError(f"despesa de {year} sem 'codSenador'")
    return [row for row in payload if int(row["codSenador"]) in codes]


def write_json(path: Path, data) -> None:
    """Grava o JSON de forma atômica, para não deixar arquivo pela metade."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    temp.replace(path)


def read_manifest(output: Path) -> dict:
    """Quando cada arquivo foi baixado. Serve para conferir que bases são da mesma foto."""
    path = output / MANIFEST
    if not path.exists():
        return {"senadores": None, "despesas": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def update_manifest(output: Path, when: datetime, *, year: int | None = None) -> None:
    """Registra a hora do download da lista de senadores (`year` vazio) ou de um ano."""
    manifest = read_manifest(output)
    stamp = when.isoformat(timespec="seconds")
    if year is None:
        manifest["senadores"] = stamp
    else:
        manifest["despesas"][str(year)] = stamp
    write_json(output / MANIFEST, manifest)


def now_local() -> datetime:
    return datetime.now().astimezone()


def collect(
    client: httpx.Client,
    output: Path,
    years: Iterable[int],
    *,
    overwrite: bool = False,
    log=print,
    clock=now_local,
) -> dict[str, list[Path]]:
    """Baixa a lista de senadores e as despesas dos anos pedidos.

    Não sobrescreve arquivo existente, a menos que `overwrite` seja verdadeiro. Cada
    download é registrado em `coleta.json`, com a data e a hora.
    """
    written: list[Path] = []
    skipped: list[Path] = []

    senadores = fetch_senadores(client)
    codes = senator_codes(senadores)

    list_path = output / "senadores_atuais.json"
    if list_path.exists() and not overwrite:
        skipped.append(list_path)
    else:
        write_json(list_path, senadores)
        update_manifest(output, clock())
        written.append(list_path)
    log(f"{len(codes)} senadores em exercício")

    for year in years:
        path = output / "api" / f"ceaps_{year}.json"
        if path.exists() and not overwrite:
            skipped.append(path)
            log(f"{year}: já existe, pulado")
            continue
        rows = fetch_despesas(client, year, codes)
        write_json(path, rows)
        update_manifest(output, clock(), year=year)
        written.append(path)
        log(f"{year}: {len(rows)} despesas")

    return {"written": written, "skipped": skipped}


def parse_years(text: str) -> list[int]:
    """Aceita '2026', '2023-2026' ou '2008,2010-2012'."""
    years: list[int] = []
    for part in text.split(","):
        part = part.strip()
        if "-" in part:
            start, end = (int(x) for x in part.split("-", 1))
            if start > end:
                raise ValueError(f"intervalo invertido: {part}")
            years.extend(range(start, end + 1))
        else:
            years.append(int(part))
    for year in years:
        if year < FIRST_YEAR or year > date.today().year:
            raise ValueError(f"ano fora do intervalo {FIRST_YEAR}-{date.today().year}: {year}")
    return sorted(set(years))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coleta os dados abertos do Senado.")
    parser.add_argument(
        "--anos",
        default=f"{FIRST_YEAR}-{date.today().year}",
        help="anos das despesas, por exemplo 2026, 2023-2026 ou 2008,2010-2012",
    )
    parser.add_argument("--saida", type=Path, default=RAW_DIR, help="pasta de saída")
    parser.add_argument(
        "--sobrescrever",
        action="store_true",
        help="substitui arquivos que já existem (por padrão, eles são pulados)",
    )
    args = parser.parse_args(argv)

    try:
        years = parse_years(args.anos)
        with httpx.Client(base_url=BASE_URL, timeout=60.0) as client:
            collect(client, args.saida, years, overwrite=args.sobrescrever)
    except (ColetaError, ValueError) as error:
        print(f"erro: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
