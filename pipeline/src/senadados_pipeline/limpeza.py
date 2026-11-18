"""Limpeza das despesas da cota (CEAPS) e dos senadores em exercício.

Lê o que a coleta gravou em `data/raw/`, valida com Pandera, aplica as regras de limpeza
e grava um banco SQLite local (D034). Cada regra existe por um motivo registrado em
`docs/`; nada é inferido sem prova (D025).

Se qualquer validação falhar, nada é gravado (falhar fechado).
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from contextlib import closing
from datetime import date
from pathlib import Path

import pandas as pd
from pandera.errors import SchemaError, SchemaErrors

from senadados_pipeline.esquemas import (
    CLEAN_SENADORES,
    FIRST_YEAR,
    RAW_DESPESAS,
    RAW_SENADORES,
    clean_despesas_schema,
)

DEFAULT_RAW = Path(__file__).resolve().parents[3] / "data" / "raw"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[3] / "data" / "limpo" / "senadados.sqlite"
NO_CATEGORY = "Sem categoria"

CNPJ_FORMAT = re.compile(r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class LimpezaError(Exception):
    """Os dados não passaram na validação ou na limpeza."""


# ---------------------------------------------------------------------------
# Regras de limpeza
# ---------------------------------------------------------------------------
def is_valid_cnpj(digits: str) -> bool:
    """Confere os dois dígitos verificadores de um CNPJ (14 dígitos)."""
    if len(digits) != 14 or not digits.isdigit() or len(set(digits)) == 1:
        return False

    def check_digit(base: str, weights: list[int]) -> str:
        remainder = sum(int(d) * w for d, w in zip(base, weights, strict=True)) % 11
        return "0" if remainder < 2 else str(11 - remainder)

    first_weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    first = check_digit(digits[:12], first_weights)
    second = check_digit(digits[:12] + first, [6, *first_weights])
    return digits[12:] == first + second


def classify_supplier(document) -> str:
    """Classifica o fornecedor pelo documento.

    - `sem_documento`: o Senado não informou (acontece só em 2008 e 2009).
    - `pessoa_fisica`: CPF mascarado ou com 11 dígitos. Não se tenta "adivinhar" nada.
    - `empresa`: CNPJ no formato certo e com dígitos verificadores válidos.
    - `outro`: qualquer outro formato; fica como veio, sem correção por suposição.
    """
    if document is None or pd.isna(document):
        return "sem_documento"
    if "*" in document:
        return "pessoa_fisica"
    digits = re.sub(r"\D", "", document)
    if len(digits) == 11:
        return "pessoa_fisica"
    if CNPJ_FORMAT.match(document) and is_valid_cnpj(digits):
        return "empresa"
    return "outro"


def normalize_date(value, reference_date: date) -> tuple[str | None, bool]:
    """Devolve (data em texto ISO ou nada, se ficou fora do esperado).

    Aceita datas de 1º/1/2008 (início dos dados) até o dia da coleta. Fora disso, o Senado
    publicou algo que não pode ser uma data de nota (por exemplo ano 0204 ou data
    futura): a data some e a linha é marcada, sem tentar adivinhar a correta.
    """
    if value is None or pd.isna(value):
        return None, False
    if not ISO_DATE.match(value):
        return None, True
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None, True
    if parsed < date(FIRST_YEAR, 1, 1) or parsed > reference_date:
        return None, True
    return value, False


def clean_senadores(raw: pd.DataFrame) -> pd.DataFrame:
    RAW_SENADORES.validate(raw)
    clean = pd.DataFrame(
        {
            "cod_senador": raw["codigoParlamentar"],
            "nome": raw["nomeParlamentar"].str.strip(),
            "tipo": raw["titularSuplente"].str.strip(),
            "uf": raw["uf"],
            "partido": raw["partido"],
        }
    )
    return CLEAN_SENADORES.validate(clean)


def clean_despesas(raw: pd.DataFrame, codes: set[int], reference_date: date) -> pd.DataFrame:
    """Valida e limpa as despesas. Só aceita senadores da lista (D026)."""
    raw = RAW_DESPESAS.validate(raw)

    outside = set(raw["codSenador"]) - codes
    if outside:
        raise LimpezaError(
            f"{len(outside)} código(s) de senador fora da lista de quem está em exercício: "
            f"{sorted(outside)[:5]}"
        )

    kinds = raw["cpfCnpj"].map(classify_supplier)
    is_person = kinds == "pessoa_fisica"
    dates = raw["data"].map(lambda value: normalize_date(value, reference_date))

    category = raw["tipoDespesa"].str.strip().replace("", pd.NA).fillna(NO_CATEGORY)

    clean = pd.DataFrame(
        {
            "id": raw["id"],
            "ano": raw["ano"],
            "mes": raw["mes"],
            "cod_senador": raw["codSenador"],
            "categoria": category,
            "tipo_documento": raw["tipoDocumento"],
            "fornecedor_tipo": kinds,
            # Pessoa física: nem nome nem documento seguem adiante (D008).
            "fornecedor_doc": raw["cpfCnpj"].mask(is_person),
            "fornecedor_nome": raw["fornecedor"].mask(is_person),
            "data": dates.map(lambda pair: pair[0]),
            "data_fora_do_esperado": dates.map(lambda pair: pair[1]).astype(bool),
            # Em centavos inteiros, para a soma bater no centavo sem erro de arredondamento.
            "valor_centavos": (raw["valorReembolsado"] * 100).round().astype("int64"),
        }
    )
    return clean_despesas_schema(reference_date).validate(clean)


# ---------------------------------------------------------------------------
# Leitura, montagem e gravação
# ---------------------------------------------------------------------------
def load_raw(raw_dir: Path) -> tuple[list[dict], list[dict], list[int]]:
    """Lê a lista de senadores e as despesas de todos os anos coletados."""
    list_path = raw_dir / "senadores_atuais.json"
    if not list_path.exists():
        raise LimpezaError(f"falta {list_path}; rode a coleta antes")
    payload = json.loads(list_path.read_text(encoding="utf-8"))
    senadores = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(senadores, list) or not senadores:
        raise LimpezaError("a lista de senadores está vazia ou em formato inesperado")

    files = sorted((raw_dir / "api").glob("ceaps_*.json"))
    if not files:
        raise LimpezaError(f"nenhum arquivo de despesas em {raw_dir / 'api'}; rode a coleta antes")

    rows: list[dict] = []
    years: list[int] = []
    for path in files:
        year = int(path.stem.removeprefix("ceaps_"))
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise LimpezaError(f"{path.name} não é uma lista de despesas")
        wrong = [row for row in data if row.get("ano") != year]
        if wrong:
            raise LimpezaError(f"{path.name} tem {len(wrong)} linha(s) de outro ano")
        rows.extend(data)
        years.append(year)
    return senadores, rows, years


def build(raw_dir: Path, output: Path, reference_date: date) -> dict:
    """Valida, limpa e grava o banco local. Devolve um resumo do que foi gravado."""
    senadores_raw, rows, years = load_raw(raw_dir)

    senadores = clean_senadores(pd.DataFrame(senadores_raw))
    despesas = clean_despesas(pd.DataFrame(rows), set(senadores["cod_senador"]), reference_date)

    summary = {
        "data_referencia": reference_date.isoformat(),
        "anos": f"{min(years)}-{max(years)}",
        "senadores": len(senadores),
        "despesas": len(despesas),
        "soma_centavos": int(despesas["valor_centavos"].sum()),
        "datas_fora_do_esperado": int(despesas["data_fora_do_esperado"].sum()),
        "sem_categoria": int((despesas["categoria"] == NO_CATEGORY).sum()),
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(output.suffix + ".tmp")
    temp.unlink(missing_ok=True)
    try:
        with closing(sqlite3.connect(temp)) as connection, connection:
            senadores.to_sql("senadores", connection, index=False)
            despesas.to_sql("despesas", connection, index=False)
            connection.execute("CREATE UNIQUE INDEX ix_despesas_id ON despesas (id)")
            connection.execute(
                "CREATE INDEX ix_despesas_senador_ano ON despesas (cod_senador, ano)"
            )
            connection.execute("CREATE TABLE metadados (chave TEXT PRIMARY KEY, valor TEXT)")
            connection.executemany(
                "INSERT INTO metadados VALUES (?, ?)",
                [(key, str(value)) for key, value in summary.items()],
            )
        temp.replace(output)
    finally:
        temp.unlink(missing_ok=True)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valida e limpa as despesas coletadas.")
    parser.add_argument(
        "--raw", type=Path, default=DEFAULT_RAW, help="pasta com os dados coletados"
    )
    parser.add_argument(
        "--saida", type=Path, default=DEFAULT_OUTPUT, help="arquivo SQLite de saída"
    )
    parser.add_argument(
        "--data-referencia",
        type=date.fromisoformat,
        default=None,
        help="dia da coleta, AAAA-MM-DD (padrão: hoje); datas depois dele ficam marcadas",
    )
    args = parser.parse_args(argv)

    try:
        summary = build(args.raw, args.saida, args.data_referencia or date.today())
    except (LimpezaError, SchemaError, SchemaErrors) as error:
        print(f"erro: {error}", file=sys.stderr)
        return 1
    for key, value in summary.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
