import json
import sqlite3
from contextlib import closing
from datetime import date

import pandas as pd
import pytest
from pandera.errors import SchemaError, SchemaErrors

from senadados_pipeline import limpeza

TODAY = date(2026, 11, 18)
CNPJ = "11.222.333/0001-81"  # dígitos verificadores válidos


def row(**changes) -> dict:
    base = {
        "id": 1,
        "ano": 2024,
        "mes": 3,
        "codSenador": 10,
        "nomeSenador": "FULANA",
        "tipoDespesa": "Divulgação da atividade parlamentar",
        "tipoDocumento": "Nota Fiscal Eletrônica",
        "cpfCnpj": CNPJ,
        "fornecedor": "EMPRESA A LTDA",
        "documento": "123",
        "data": "2024-03-10",
        "detalhamento": None,
        "valorReembolsado": 100.5,
    }
    base.update(changes)
    return base


def clean(*rows: dict, codes=frozenset({10, 11}), reference=TODAY) -> pd.DataFrame:
    return limpeza.clean_despesas(pd.DataFrame(list(rows)), set(codes), reference)


# --- fornecedor -------------------------------------------------------------
def test_cnpj_com_digitos_validos_e_empresa():
    assert limpeza.classify_supplier(CNPJ) == "empresa"


def test_cnpj_com_digito_verificador_errado_e_outro():
    assert limpeza.classify_supplier("11.222.333/0001-82") == "outro"


@pytest.mark.parametrize("document", ["123.***.***-09", "12345678909", "123.456.789-09"])
def test_cpf_mascarado_ou_completo_e_pessoa_fisica(document):
    assert limpeza.classify_supplier(document) == "pessoa_fisica"


@pytest.mark.parametrize("document", ["1234567890123", "123456789012", "000123", "7654321"])
def test_documento_fora_do_padrao_fica_como_outro_sem_correcao(document):
    assert limpeza.classify_supplier(document) == "outro"


def test_sem_documento():
    assert limpeza.classify_supplier(None) == "sem_documento"


def test_pessoa_fisica_nao_leva_nome_nem_documento():
    result = clean(row(cpfCnpj="123.***.***-09", fornecedor="JOAO DA SILVA"))
    assert result.loc[0, "fornecedor_tipo"] == "pessoa_fisica"
    assert pd.isna(result.loc[0, "fornecedor_doc"])
    assert pd.isna(result.loc[0, "fornecedor_nome"])


def test_cpf_completo_tambem_e_descartado():
    result = clean(row(cpfCnpj="123.456.789-09", fornecedor="MARIA"))
    assert result.loc[0, "fornecedor_tipo"] == "pessoa_fisica"
    assert pd.isna(result.loc[0, "fornecedor_doc"])


def test_empresa_mantem_nome_e_documento():
    result = clean(row())
    assert result.loc[0, "fornecedor_nome"] == "EMPRESA A LTDA"
    assert result.loc[0, "fornecedor_doc"] == CNPJ


def test_documento_fora_do_padrao_e_mantido_sem_inferencia():
    result = clean(row(cpfCnpj="1234567890123"))
    assert result.loc[0, "fornecedor_tipo"] == "outro"
    assert result.loc[0, "fornecedor_doc"] == "1234567890123"


def test_2008_sem_fornecedor_nem_data():
    result = clean(row(ano=2008, cpfCnpj=None, fornecedor=None, tipoDocumento=None, data=None))
    assert result.loc[0, "fornecedor_tipo"] == "sem_documento"
    assert pd.isna(result.loc[0, "data"])
    assert not result.loc[0, "data_fora_do_esperado"]


# --- datas ------------------------------------------------------------------
@pytest.mark.parametrize(
    "value", ["0204-05-29", "0023-10-07", "1201-11-22", "2007-12-31", "2026-11-19", "2026-12-28"]
)
def test_data_impossivel_ou_futura_some_e_a_linha_e_marcada(value):
    result = clean(row(data=value))
    assert pd.isna(result.loc[0, "data"])
    assert result.loc[0, "data_fora_do_esperado"]


@pytest.mark.parametrize("value", ["2008-01-01", "2024-03-10", "2026-11-18"])
def test_data_dentro_do_intervalo_e_mantida(value):
    result = clean(row(data=value))
    assert result.loc[0, "data"] == value
    assert not result.loc[0, "data_fora_do_esperado"]


@pytest.mark.parametrize("value", ["2024-02-30", "10/03/2024", "20240310", "texto"])
def test_data_malformada_e_marcada(value):
    assert limpeza.normalize_date(value, TODAY) == (None, True)


def test_a_linha_com_data_ruim_continua_na_soma():
    result = clean(row(data="0204-05-29", valorReembolsado=50.0), row(id=2, valorReembolsado=25.0))
    assert result["valor_centavos"].sum() == 7500


# --- categoria e valor ------------------------------------------------------
def test_sem_categoria_ganha_o_nome_padrao():
    result = clean(row(tipoDespesa=None), row(id=2, tipoDespesa="  "))
    assert list(result["categoria"]) == ["Sem categoria", "Sem categoria"]


def test_categoria_nova_do_senado_passa_sem_erro():
    result = clean(row(tipoDespesa="Categoria criada amanhã"))
    assert result.loc[0, "categoria"] == "Categoria criada amanhã"


def test_valor_em_centavos_nao_perde_nada_por_arredondamento():
    result = clean(
        row(valorReembolsado=583.58),
        row(id=2, valorReembolsado=3800),
        row(id=3, valorReembolsado=-33.11),
        row(id=4, valorReembolsado=0.1),
        row(id=5, valorReembolsado=0.2),
    )
    assert list(result["valor_centavos"]) == [58358, 380000, -3311, 10, 20]
    assert result["valor_centavos"].sum() == 58358 + 380000 - 3311 + 30


def test_valor_com_mais_de_duas_casas_e_recusado():
    with pytest.raises((SchemaError, SchemaErrors)):
        clean(row(valorReembolsado=10.123))


# --- validação do que o Senado entrega --------------------------------------
def test_coluna_nova_do_senado_quebra_a_validacao():
    frame = pd.DataFrame([{**row(), "campoNovo": "x"}])
    with pytest.raises((SchemaError, SchemaErrors)):
        limpeza.clean_despesas(frame, {10}, TODAY)


def test_coluna_que_sumiu_quebra_a_validacao():
    frame = pd.DataFrame([row()]).drop(columns=["valorReembolsado"])
    with pytest.raises((SchemaError, SchemaErrors)):
        limpeza.clean_despesas(frame, {10}, TODAY)


def test_id_repetido_quebra_a_validacao():
    with pytest.raises((SchemaError, SchemaErrors)):
        clean(row(), row())


def test_mes_invalido_quebra_a_validacao():
    with pytest.raises((SchemaError, SchemaErrors)):
        clean(row(mes=13))


def test_senador_fora_da_lista_e_recusado():
    with pytest.raises(limpeza.LimpezaError):
        clean(row(codSenador=99))


# --- senadores --------------------------------------------------------------
def test_nome_do_senador_perde_espacos_nas_pontas():
    raw = pd.DataFrame(
        [
            {
                "codigoParlamentar": 1,
                "nomeParlamentar": "RENZO BRAZ ",
                "titularSuplente": "1º Suplente",
                "uf": "MG",
                "partido": "PP",
                "email": "x@y",
            }
        ]
    )
    assert limpeza.clean_senadores(raw).loc[0, "nome"] == "RENZO BRAZ"


# --- do começo ao fim -------------------------------------------------------
def write_raw(tmp_path, rows, year=2024, senadores=None):
    raw = tmp_path / "raw"
    (raw / "api").mkdir(parents=True)
    senadores = senadores or [
        {
            "codigoParlamentar": 10,
            "nomeParlamentar": "FULANA",
            "titularSuplente": "Titular",
            "uf": "AC",
            "partido": "XX",
        }
    ]
    (raw / "senadores_atuais.json").write_text(json.dumps({"data": senadores}), encoding="utf-8")
    (raw / "api" / f"ceaps_{year}.json").write_text(json.dumps(rows), encoding="utf-8")
    return raw


def test_build_grava_o_banco_local(tmp_path):
    raw = write_raw(tmp_path, [row(), row(id=2, data="0204-05-29", tipoDespesa=None)])
    output = tmp_path / "limpo" / "db.sqlite"

    summary = limpeza.build(raw, output, TODAY)

    assert summary["despesas"] == 2
    assert summary["datas_fora_do_esperado"] == 1
    assert summary["sem_categoria"] == 1
    with closing(sqlite3.connect(output)) as connection:
        assert connection.execute("SELECT COUNT(*) FROM despesas").fetchone() == (2,)
        assert connection.execute("SELECT SUM(valor_centavos) FROM despesas").fetchone() == (20100,)
        assert connection.execute("SELECT nome FROM senadores").fetchone() == ("FULANA",)
        assert dict(connection.execute("SELECT chave, valor FROM metadados")) == {
            key: str(value) for key, value in summary.items()
        }


def test_build_nao_grava_nada_se_a_validacao_falha(tmp_path):
    raw = write_raw(tmp_path, [row(), row()])  # id repetido
    output = tmp_path / "limpo" / "db.sqlite"

    with pytest.raises((SchemaError, SchemaErrors)):
        limpeza.build(raw, output, TODAY)

    assert not output.exists()
    assert not list(tmp_path.rglob("*.tmp"))


def test_build_nao_substitui_o_banco_antigo_se_a_validacao_falha(tmp_path):
    output = tmp_path / "limpo" / "db.sqlite"
    output.parent.mkdir()
    output.write_text("banco antigo", encoding="utf-8")
    raw = write_raw(tmp_path, [row(mes=13)])

    with pytest.raises((SchemaError, SchemaErrors)):
        limpeza.build(raw, output, TODAY)

    assert output.read_text(encoding="utf-8") == "banco antigo"


def test_build_recusa_arquivo_com_linha_de_outro_ano(tmp_path):
    raw = write_raw(tmp_path, [row(ano=2023)], year=2024)
    with pytest.raises(limpeza.LimpezaError):
        limpeza.build(raw, tmp_path / "db.sqlite", TODAY)


def test_build_pede_a_coleta_quando_faltam_arquivos(tmp_path):
    with pytest.raises(limpeza.LimpezaError):
        limpeza.build(tmp_path / "vazio", tmp_path / "db.sqlite", TODAY)
