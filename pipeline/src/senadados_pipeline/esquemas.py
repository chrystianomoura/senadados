"""Esquemas de validação (Pandera) das despesas e dos senadores.

Dois momentos: o que o Senado entrega (`RAW_DESPESAS`) e o que o pipeline produz
(`clean_despesas_schema`). Se o Senado mudar um campo ou entregar dado impossível, a
validação quebra e nada é gravado (falhar fechado, D025).
"""

from __future__ import annotations

import re
from datetime import date

from pandera.pandas import Check, Column, DataFrameSchema

FIRST_YEAR = 2008
FIRST_DATE = f"{FIRST_YEAR}-01-01"
SUPPLIER_TYPES = ["empresa", "pessoa_fisica", "outro", "sem_documento"]


def _at_most_two_decimals(values) -> bool:
    cents = values * 100
    return bool(((cents - cents.round()).abs() < 1e-6).all())


# ---------------------------------------------------------------------------
# O que o Senado entrega (API de despesas, uma linha por nota)
# ---------------------------------------------------------------------------
# strict=True: coluna nova ou faltando é um aviso de que o Senado mudou algo.
RAW_DESPESAS = DataFrameSchema(
    {
        "id": Column(int, unique=True),
        "ano": Column(int, Check.in_range(FIRST_YEAR, 2100)),
        "mes": Column(int, Check.in_range(1, 12)),
        "codSenador": Column(int),
        "nomeSenador": Column(str),
        "tipoDespesa": Column(str, nullable=True),
        "tipoDocumento": Column(str, nullable=True),
        "cpfCnpj": Column(str, nullable=True),
        "fornecedor": Column(str, nullable=True),
        "documento": Column(str, nullable=True),
        "data": Column(str, nullable=True),
        "detalhamento": Column(str, nullable=True),
        "valorReembolsado": Column(float, Check(_at_most_two_decimals), coerce=True),
    },
    strict=True,
    name="despesas do Senado (API)",
)


# ---------------------------------------------------------------------------
# Lista dos senadores em exercício
# ---------------------------------------------------------------------------
RAW_SENADORES = DataFrameSchema(
    {
        "codigoParlamentar": Column(int, unique=True),
        "nomeParlamentar": Column(str),
        "titularSuplente": Column(str),
        "uf": Column(str, Check.str_length(2, 2)),
        "partido": Column(str),
    },
    strict=False,  # a lista traz outros campos (contato etc.) que ainda não usamos
    name="senadores em exercício (API)",
)

CLEAN_SENADORES = DataFrameSchema(
    {
        "cod_senador": Column(int, unique=True),
        "nome": Column(str),
        "tipo": Column(str),
        "uf": Column(str, Check.str_length(2, 2)),
        "partido": Column(str),
    },
    strict=True,
    name="senadores limpos",
)


# ---------------------------------------------------------------------------
# O que o pipeline produz
# ---------------------------------------------------------------------------
def _no_personal_document(values) -> bool:
    """Nenhum CPF (mascarado ou completo) no documento do fornecedor."""
    for value in values.dropna():
        if "*" in value or len(re.sub(r"\D", "", value)) == 11:
            return False
    return True


def clean_despesas_schema(reference_date: date) -> DataFrameSchema:
    """Esquema das despesas limpas. `reference_date` é o dia da coleta."""
    last_date = reference_date.isoformat()
    return DataFrameSchema(
        {
            "id": Column(int, unique=True),
            "ano": Column(int, Check.in_range(FIRST_YEAR, 2100)),
            "mes": Column(int, Check.in_range(1, 12)),
            "cod_senador": Column(int),
            "categoria": Column(str),
            "tipo_documento": Column(str, nullable=True),
            "fornecedor_tipo": Column(str, Check.isin(SUPPLIER_TYPES)),
            "fornecedor_doc": Column(str, Check(_no_personal_document), nullable=True),
            "fornecedor_nome": Column(str, nullable=True),
            "data": Column(
                str,
                [
                    Check.str_matches(r"^\d{4}-\d{2}-\d{2}$"),
                    Check(lambda s: s.dropna().ge(FIRST_DATE).all()),
                    Check(lambda s: s.dropna().le(last_date).all()),
                ],
                nullable=True,
            ),
            "data_fora_do_esperado": Column(bool),
            "valor_centavos": Column(int),
        },
        checks=[
            # Pessoa física nunca leva nome nem documento adiante (D008).
            Check(
                lambda df: bool(
                    (
                        (df["fornecedor_tipo"] != "pessoa_fisica")
                        | (df["fornecedor_doc"].isna() & df["fornecedor_nome"].isna())
                    ).all()
                ),
                error="pessoa física com nome ou documento",
            ),
            # Sem data só é aceito quando o Senado não informou o fornecedor, ou quando a
            # data veio inválida e foi marcada.
            Check(
                lambda df: bool(
                    (
                        df["data"].notna()
                        | df["data_fora_do_esperado"]
                        | (df["fornecedor_tipo"] == "sem_documento")
                    ).all()
                ),
                error="despesa sem data e sem marcação",
            ),
        ],
        strict=True,
        name="despesas limpas",
    )


__all__ = [
    "CLEAN_SENADORES",
    "RAW_DESPESAS",
    "RAW_SENADORES",
    "SUPPLIER_TYPES",
    "clean_despesas_schema",
]
