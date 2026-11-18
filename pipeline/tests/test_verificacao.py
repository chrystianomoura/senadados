import json
import sqlite3
from contextlib import closing
from datetime import date

import httpx
import pytest

from senadados_pipeline import verificacao as v

TODAY = date(2026, 11, 18)
SHORT = "Divulgação da atividade parlamentar"
OFFICIAL = v.CATEGORY_MAP[SHORT]
OTHER_SHORT = "Serviços de Segurança Privada"
OTHER_OFFICIAL = v.CATEGORY_MAP[OTHER_SHORT]


def resumo(**values) -> tuple[dict[str, int], int]:
    """Resumo com todas as categorias (zeradas) e os valores pedidos, em centavos."""
    categories = dict.fromkeys(v.CATEGORY_MAP, 0)
    categories.update(values)
    return categories, sum(categories.values())


def payload(categories: dict[str, float]) -> dict:
    return {
        "data": [
            {
                "cotas": {
                    "despesas": [{"recurso": k, "valor": val} for k, val in categories.items()],
                    "totalValor": sum(categories.values()),
                }
            }
        ]
    }


# --- parse ------------------------------------------------------------------
def test_parse_resumo_converte_para_centavos():
    categories, total = v.parse_resumo(payload({SHORT: 583.58, OTHER_SHORT: 0.1}))
    assert categories == {SHORT: 58358, OTHER_SHORT: 10}
    assert total == 58368


def test_parse_resumo_sem_dados_no_ano_e_zero():
    assert v.parse_resumo({"data": []}) == ({}, 0)


@pytest.mark.parametrize("bad", [[], {"data": "x"}, {"data": [{}]}, {"data": [{"cotas": {}}]}])
def test_parse_resumo_recusa_formato_inesperado(bad):
    with pytest.raises(v.VerificacaoError):
        v.parse_resumo(bad)


# --- comparação -------------------------------------------------------------
def test_identico_quando_todas_as_categorias_batem():
    result = v.compare_cota(1, 2026, {OFFICIAL: 1000}, resumo(**{SHORT: 1000}))
    assert result.resultado == v.IDENTICAL
    assert (result.despesas_centavos, result.resumo_centavos) == (1000, 1000)


def test_explicado_quando_so_faltam_as_linhas_sem_categoria():
    spent = {OFFICIAL: 1000, "Sem categoria": 748}
    result = v.compare_cota(1, 2026, spent, resumo(**{SHORT: 1000}))
    assert result.resultado == v.EXPLAINED
    assert result.sem_categoria_centavos == 748
    assert result.despesas_centavos == 1748
    assert result.resumo_centavos == 1000


def test_sem_explicacao_quando_uma_categoria_difere():
    result = v.compare_cota(1, 2026, {OFFICIAL: 1000}, resumo(**{SHORT: 900}))
    assert result.resultado == v.UNEXPLAINED
    assert "1000 contra resumo 900" in result.detalhe


def test_sem_explicacao_mesmo_se_o_total_bater_com_categorias_trocadas():
    spent = {OFFICIAL: 500, OTHER_OFFICIAL: 500}
    result = v.compare_cota(1, 2026, spent, resumo(**{SHORT: 1000}))
    assert result.resultado == v.UNEXPLAINED


def test_sem_explicacao_quando_o_resumo_zera_e_ha_despesa():
    result = v.compare_cota(1, 2008, {OFFICIAL: 1000}, ({}, 0))
    assert result.resultado == v.UNEXPLAINED


def test_sem_explicacao_quando_ha_resumo_e_nao_ha_despesa():
    result = v.compare_cota(1, 2026, {}, resumo(**{SHORT: 1000}))
    assert result.resultado == v.UNEXPLAINED


def test_sem_explicacao_com_categoria_desconhecida_no_resumo():
    categories = {"Categoria nova do Senado": 1000}
    result = v.compare_cota(1, 2026, {OFFICIAL: 1000}, (categories, 1000))
    assert result.resultado == v.UNEXPLAINED
    assert "desconhecida" in result.detalhe


def test_sem_explicacao_quando_o_resumo_nao_soma_o_proprio_total():
    categories = {SHORT: 1000}
    result = v.compare_cota(1, 2026, {OFFICIAL: 1000}, (categories, 1200))
    assert result.resultado == v.UNEXPLAINED
    assert "somam" in result.detalhe


def test_despesa_com_categoria_nova_do_senado_nao_passa_sem_conferencia():
    result = v.compare_cota(1, 2026, {"Categoria nova": 100}, resumo())
    assert result.resultado == v.UNEXPLAINED


def test_verify_cota_ignora_pares_sem_valor_dos_dois_lados():
    spent = {(1, 2026): {OFFICIAL: 1000}}
    resumos = {(1, 2026): resumo(**{SHORT: 1000}), (2, 2026): resumo(), (3, 2026): ({}, 0)}
    results = v.verify_cota(spent, resumos)
    assert [(r.cod_senador, r.resultado) for r in results] == [(1, v.IDENTICAL)]


# --- mesma foto dos dados ---------------------------------------------------
def manifest(senadores="2026-11-18T10:00:00-03:00", year="2026-11-18T10:01:00-03:00") -> dict:
    return {"senadores": senadores, "despesas": {"2026": year}}


def test_mesma_foto_passa():
    v.check_same_snapshot(manifest(), [2026], TODAY, TODAY)


def test_recusa_despesas_de_outro_dia():
    with pytest.raises(v.VerificacaoError, match="2026 são de 2026-11-17"):
        v.check_same_snapshot(manifest(year="2026-11-17T10:00:00-03:00"), [2026], TODAY, TODAY)


def test_recusa_lista_de_outro_dia():
    with pytest.raises(v.VerificacaoError, match="lista de senadores é de"):
        v.check_same_snapshot(manifest(senadores="2026-11-10T10:00:00-03:00"), [2026], TODAY, TODAY)


def test_recusa_banco_limpo_de_outro_dia():
    with pytest.raises(v.VerificacaoError, match="banco limpo é de 2026-11-17"):
        v.check_same_snapshot(manifest(), [2026], date(2026, 11, 17), TODAY)


def test_recusa_ano_sem_data_de_coleta():
    with pytest.raises(v.VerificacaoError, match="2025 não têm data"):
        v.check_same_snapshot(manifest(), [2025, 2026], TODAY, TODAY)


def test_recusa_quando_nunca_houve_coleta():
    with pytest.raises(v.VerificacaoError, match="não tem data de coleta"):
        v.check_same_snapshot({"senadores": None, "despesas": {}}, [2026], TODAY, TODAY)


# --- do começo ao fim -------------------------------------------------------
def make_database(path, *, reference="2026-11-18", rows=None):
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("CREATE TABLE senadores (cod_senador INTEGER)")
        connection.executemany("INSERT INTO senadores VALUES (?)", [(1,), (2,)])
        connection.execute(
            "CREATE TABLE despesas (cod_senador INTEGER, ano INTEGER, categoria TEXT, "
            "valor_centavos INTEGER)"
        )
        connection.executemany(
            "INSERT INTO despesas VALUES (?, ?, ?, ?)",
            rows
            if rows is not None
            else [
                (1, 2026, OFFICIAL, 600),
                (1, 2026, OFFICIAL, 400),
                (2, 2026, OFFICIAL, 1000),
                (2, 2026, "Sem categoria", 50),
            ],
        )
        connection.execute("CREATE TABLE metadados (chave TEXT PRIMARY KEY, valor TEXT)")
        connection.execute("INSERT INTO metadados VALUES ('data_referencia', ?)", (reference,))


def write_manifest(raw_dir, **kwargs):
    raw_dir.mkdir(exist_ok=True)
    (raw_dir / "coleta.json").write_text(json.dumps(manifest(**kwargs)), encoding="utf-8")


def make_client(by_senator: dict[int, dict[str, float]]) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        code = int(request.url.path.split("/")[-2])
        return httpx.Response(200, json=payload(by_senator[code]))

    return httpx.Client(base_url="https://example.test", transport=httpx.MockTransport(handler))


FULL = dict.fromkeys(v.CATEGORY_MAP, 0.0)


def test_run_verifica_e_grava_o_resultado(tmp_path):
    database = tmp_path / "db.sqlite"
    make_database(database)
    write_manifest(tmp_path / "raw")
    client = make_client({1: {**FULL, SHORT: 10.0}, 2: {**FULL, SHORT: 10.0}})

    results = v.run(tmp_path / "raw", database, None, client, TODAY)

    assert {r.cod_senador: r.resultado for r in results} == {1: v.IDENTICAL, 2: v.EXPLAINED}
    with closing(sqlite3.connect(database)) as connection:
        assert connection.execute(
            "SELECT nome, ano, identicos, explicados, sem_explicacao FROM verificacoes"
        ).fetchall() == [("cota", 2026, 1, 1, 0)]
        assert connection.execute(
            "SELECT resultado FROM verificacao_cota ORDER BY cod_senador"
        ).fetchall() == [(v.IDENTICAL,), (v.EXPLAINED,)]


def test_run_registra_o_que_nao_bate(tmp_path):
    database = tmp_path / "db.sqlite"
    make_database(database)
    write_manifest(tmp_path / "raw")
    client = make_client({1: {**FULL, SHORT: 9.0}, 2: {**FULL, SHORT: 10.0}})

    results = v.run(tmp_path / "raw", database, None, client, TODAY)

    assert {r.cod_senador: r.resultado for r in results}[1] == v.UNEXPLAINED
    with closing(sqlite3.connect(database)) as connection:
        assert connection.execute("SELECT sem_explicacao FROM verificacoes").fetchone() == (1,)


def test_run_refaz_a_verificacao_sem_acumular(tmp_path):
    database = tmp_path / "db.sqlite"
    make_database(database)
    write_manifest(tmp_path / "raw")
    client = make_client({1: {**FULL, SHORT: 10.0}, 2: {**FULL, SHORT: 10.0}})

    v.run(tmp_path / "raw", database, None, client, TODAY)
    v.run(tmp_path / "raw", database, None, client, TODAY)

    with closing(sqlite3.connect(database)) as connection:
        assert connection.execute("SELECT COUNT(*) FROM verificacao_cota").fetchone() == (2,)
        assert connection.execute("SELECT COUNT(*) FROM verificacoes").fetchone() == (1,)


def test_run_recusa_dados_de_dias_diferentes_e_nao_grava(tmp_path):
    database = tmp_path / "db.sqlite"
    make_database(database)
    write_manifest(tmp_path / "raw", year="2026-11-10T10:00:00-03:00")

    with pytest.raises(v.VerificacaoError, match="mesma foto"):
        v.run(tmp_path / "raw", database, None, make_client({}), TODAY)

    with closing(sqlite3.connect(database)) as connection:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master")}
    assert "verificacao_cota" not in tables


def test_run_pede_a_limpeza_quando_nao_ha_banco(tmp_path):
    with pytest.raises(v.VerificacaoError, match="limpeza"):
        v.run(tmp_path, tmp_path / "nao-existe.sqlite", None, make_client({}), TODAY)


def test_run_recusa_ano_que_o_banco_nao_tem(tmp_path):
    database = tmp_path / "db.sqlite"
    make_database(database)
    write_manifest(tmp_path / "raw")
    with pytest.raises(v.VerificacaoError, match="não tem despesas"):
        v.run(tmp_path / "raw", database, [2020], make_client({}), TODAY)


def test_falha_de_rede_no_resumo_interrompe_sem_gravar(tmp_path, monkeypatch):
    monkeypatch.setattr("senadados_pipeline.coleta.time.sleep", lambda _: None)
    database = tmp_path / "db.sqlite"
    make_database(database)
    write_manifest(tmp_path / "raw")
    client = httpx.Client(
        base_url="https://example.test",
        transport=httpx.MockTransport(lambda _request: httpx.Response(503)),
    )

    with pytest.raises(v.VerificacaoError):
        v.run(tmp_path / "raw", database, None, client, TODAY)

    with closing(sqlite3.connect(database)) as connection:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master")}
    assert "verificacao_cota" not in tables


def test_run_recusa_banco_sem_data_de_referencia(tmp_path):
    database = tmp_path / "db.sqlite"
    make_database(database)
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.execute("DELETE FROM metadados")
    write_manifest(tmp_path / "raw")
    with pytest.raises(v.VerificacaoError, match="data de referência"):
        v.run(tmp_path / "raw", database, None, make_client({}), TODAY)


def test_linha_de_comando_avisa_quando_falta_o_banco(tmp_path, capsys):
    code = v.main(["--raw", str(tmp_path), "--banco", str(tmp_path / "nao-existe.sqlite")])
    assert code == 1
    assert "limpeza" in capsys.readouterr().err
