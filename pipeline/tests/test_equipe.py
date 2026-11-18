import json
import sqlite3
from contextlib import closing
from datetime import date, datetime

import httpx
import pytest

from senadados_pipeline import equipe as e
from senadados_pipeline import verificacao as v
from senadados_pipeline.coleta import ColetaError

TODAY = date(2026, 11, 18)
NOW = datetime.fromisoformat("2026-11-18T13:00:00-03:00")


def server(lotacao_nome, sigla, vinculo="COMISSIONADO", situacao="ATIVO", name="FULANO DE TAL"):
    return {
        "nome": name,
        "vinculo": vinculo,
        "situacao": situacao,
        "lotacao": {"sigla": sigla, "nome": lotacao_nome},
    }


def pessoal(commissioned=0, effective=0, requisitioned=0):
    links = [
        {"vinculo": "Comissionado", "quantidade": commissioned},
        {"vinculo": "Efetivo", "quantidade": effective},
        {"vinculo": "Requisitado", "quantidade": requisitioned},
    ]
    links = [x for x in links if x["quantidade"]]
    return [
        {"local": "Gabinete", "quantidade": sum(x["quantidade"] for x in links), "vinculos": links}
    ]


# --- coleta sem nomes de pessoas --------------------------------------------
def test_conta_por_gabinete_e_vinculo_e_descarta_os_nomes():
    servers = [
        server("Gabinete do Senador Alan Rick", "GSARICK", "PARLAMENTAR", name="ALAN RICK MIRANDA"),
        server("Gabinete do Senador Alan Rick", "GSARICK", name="ASSESSOR UM"),
        server("Gabinete do Senador Alan Rick", "GSARICK", name="ASSESSOR DOIS"),
        server("Gabinete do Senador Alan Rick", "GSARICK", "EFETIVO", name="ASSESSOR TRES"),
        server("Gabinete da Senadora Leany Lemos", "GSLLEMOS"),
        server("Escritório de Apoio nº 1 do Senador Alan Rick", "E1ARICK"),
        server("Gabinete da Liderança do PT", "GLDPT"),
    ]
    result = e.aggregate_gabinetes(servers)

    assert {(x["sigla"], x["vinculo"]): x["quantidade"] for x in result} == {
        ("GSARICK", "COMISSIONADO"): 2,
        ("GSARICK", "EFETIVO"): 1,
        ("GSARICK", "PARLAMENTAR"): 1,
        ("GSLLEMOS", "COMISSIONADO"): 1,
    }
    dumped = json.dumps(result)
    assert "ASSESSOR" not in dumped
    assert "ALAN RICK MIRANDA" not in dumped


def test_recusa_servidor_que_nao_esta_ativo():
    with pytest.raises(ColetaError, match="situação"):
        e.aggregate_gabinetes([server("Gabinete do Senador X", "GSX", situacao="APOSENTADO")])


@pytest.mark.parametrize("bad", [{"data": []}, [{"nome": "sem lotação"}], [None]])
def test_recusa_lista_de_servidores_em_formato_inesperado(bad):
    with pytest.raises(ColetaError):
        e.aggregate_gabinetes(bad)


def make_client(routes: dict) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        body = routes.get(request.url.path)
        return httpx.Response(200, json=body) if body is not None else httpx.Response(404)

    return httpx.Client(base_url="https://example.test", transport=httpx.MockTransport(handler))


def routes_for(codes, extra=None):
    routes = {
        f"/senadores/{code}/recursos-utilizados": {"data": [{"pessoal": pessoal(2)}]}
        for code in codes
    }
    routes["/servidores/servidores/ativos"] = [
        server("Gabinete do Senador Fulano", "GSFULANO", name="NOME SECRETO"),
        server("Gabinete do Senador Fulano", "GSFULANO", name="OUTRO NOME SECRETO"),
    ]
    routes.update(extra or {})
    return routes


def test_collect_grava_so_contagens_e_registra_a_hora(tmp_path):
    client = make_client(routes_for([1]))
    year, pessoal_by_code, gabinetes = e.collect_equipe(client, tmp_path, [1], clock=lambda: NOW)

    assert year == 2026
    assert pessoal_by_code == {"1": pessoal(2)}
    saved = (tmp_path / "equipe" / "gabinetes_ativos.json").read_text(encoding="utf-8")
    assert "SECRETO" not in saved
    assert json.loads(saved) == gabinetes
    manifest = json.loads((tmp_path / "coleta.json").read_text(encoding="utf-8"))
    assert manifest["equipe"] == "2026-11-18T13:00:00-03:00"


def test_collect_preserva_o_que_ja_estava_no_manifesto(tmp_path):
    (tmp_path / "coleta.json").write_text(
        json.dumps({"senadores": "2026-11-18T10:00:00-03:00", "despesas": {"2026": "x"}}),
        encoding="utf-8",
    )
    e.collect_equipe(make_client(routes_for([1])), tmp_path, [1], clock=lambda: NOW)
    manifest = json.loads((tmp_path / "coleta.json").read_text(encoding="utf-8"))
    assert manifest["senadores"] == "2026-11-18T10:00:00-03:00"
    assert manifest["despesas"] == {"2026": "x"}


def test_collect_falha_se_o_resumo_nao_trouxer_pessoal(tmp_path):
    routes = routes_for([1], {"/senadores/1/recursos-utilizados": {"data": [{}]}})
    with pytest.raises(ColetaError):
        e.collect_equipe(make_client(routes), tmp_path, [1], clock=lambda: NOW)
    assert not (tmp_path / "equipe").exists()


# --- ligação entre senador e gabinete ---------------------------------------
def gab(sigla, nome):
    return {
        "sigla": sigla,
        "nome": f"Gabinete do Senador {nome}",
        "vinculo": "COMISSIONADO",
        "quantidade": 1,
    }


def test_liga_por_nome_igual_ignorando_acento_e_caixa():
    links = e.link_gabinetes(
        {1: "ALAN RICK", 2: "ÂNGELO CORONEL"}, [gab("A", "Alan Rick"), gab("B", "Angelo Coronel")]
    )
    assert links == {1: "A", 2: "B"}


def test_liga_quando_um_nome_contem_o_outro_em_palavras_inteiras():
    senators = {1: "NELSINHO TRAD FILHO", 2: "WEVERTON"}
    gabinetes = [gab("T", "Nelsinho Trad"), gab("W", "Weverton Rocha")]
    assert e.link_gabinetes(senators, gabinetes) == {1: "T", 2: "W"}


def test_nao_liga_quando_ha_mais_de_uma_possibilidade():
    senators = {1: "ANA"}
    gabinetes = [gab("A", "Ana Paula"), gab("B", "Ana Maria")]
    assert e.link_gabinetes(senators, gabinetes) == {}


def test_nao_confunde_nome_que_so_comeca_igual_sem_ser_palavra_inteira():
    assert e.link_gabinetes({1: "ANA"}, [gab("A", "Anastacio")]) == {}


def test_nome_exato_tem_prioridade_sobre_o_parcial():
    senators = {1: "ANA", 2: "ANA PAULA"}
    gabinetes = [gab("A", "Ana"), gab("B", "Ana Paula")]
    assert e.link_gabinetes(senators, gabinetes) == {1: "A", 2: "B"}


# --- comparação -------------------------------------------------------------
def test_resumo_gabinete_le_total_e_vinculos_normalizados():
    assert e.resumo_gabinete(pessoal(14, 3)) == (17, {"COMISSIONADO": 14, "EFETIVO": 3})


def test_resumo_sem_entrada_de_gabinete_e_zero():
    assert e.resumo_gabinete(
        [{"local": "Escritório(s) de Apoio", "quantidade": 1, "vinculos": []}]
    ) == (0, {})


def test_resumo_que_nao_soma_o_proprio_total_e_recusado():
    bad = [
        {
            "local": "Gabinete",
            "quantidade": 5,
            "vinculos": [{"vinculo": "Efetivo", "quantidade": 3}],
        }
    ]
    with pytest.raises(v.VerificacaoError, match="não soma"):
        e.resumo_gabinete(bad)


@pytest.mark.parametrize("bad", [{"x": 1}, [{"local": "Gabinete"}]])
def test_resumo_em_formato_inesperado_e_recusado(bad):
    with pytest.raises(v.VerificacaoError):
        e.resumo_gabinete(bad)


def test_identico_quando_total_e_vinculos_batem_sem_contar_o_senador():
    listed = {"COMISSIONADO": 14, "EFETIVO": 3, "PARLAMENTAR": 1}
    result = e.compare_equipe(1, 2026, pessoal(14, 3), listed)
    assert result.resultado == v.IDENTICAL
    assert (result.equipe_resumo, result.equipe_lista) == (17, 17)


def test_sem_explicacao_quando_o_total_difere():
    result = e.compare_equipe(1, 2026, pessoal(14), {"COMISSIONADO": 13, "PARLAMENTAR": 1})
    assert result.resultado == v.UNEXPLAINED
    assert "COMISSIONADO: resumo 14 contra lista 13" in result.detalhe


def test_sem_explicacao_quando_o_total_bate_mas_os_vinculos_nao():
    result = e.compare_equipe(1, 2026, pessoal(13, 1), {"COMISSIONADO": 14})
    assert result.resultado == v.UNEXPLAINED


def test_caso_da_diferenca_de_um_efetivo_no_resumo():
    # O resumo traz 1 efetivo que a lista de servidores ativos não tem.
    result = e.compare_equipe(1, 2026, pessoal(27, 1), {"COMISSIONADO": 27, "PARLAMENTAR": 1})
    assert result.resultado == v.UNEXPLAINED
    assert result.detalhe == "EFETIVO: resumo 1 contra lista 0"
    assert (result.equipe_resumo, result.equipe_lista) == (28, 27)


def test_sem_explicacao_quando_o_gabinete_nao_foi_encontrado():
    result = e.compare_equipe(1, 2026, pessoal(5), None)
    assert result.resultado == v.UNEXPLAINED
    assert result.detalhe == "gabinete não encontrado"


def test_gabinete_vazio_dos_dois_lados_e_identico():
    result = e.compare_equipe(1, 2026, [{"local": "Gabinete", "quantidade": 0, "vinculos": []}], {})
    assert result.resultado == v.IDENTICAL


def test_verify_equipe_de_ponta_a_ponta():
    senators = {1: "ALAN RICK", 2: "BETO FARO", 3: "SEM GABINETE"}
    gabinetes = [
        {
            "sigla": "A",
            "nome": "Gabinete do Senador Alan Rick",
            "vinculo": "COMISSIONADO",
            "quantidade": 2,
        },
        {
            "sigla": "A",
            "nome": "Gabinete do Senador Alan Rick",
            "vinculo": "PARLAMENTAR",
            "quantidade": 1,
        },
        {
            "sigla": "B",
            "nome": "Gabinete do Senador Beto Faro",
            "vinculo": "COMISSIONADO",
            "quantidade": 3,
        },
    ]
    resumos = {"1": pessoal(2), "2": pessoal(4), "3": pessoal(1)}
    results = {
        r.cod_senador: r.resultado for r in e.verify_equipe(senators, 2026, resumos, gabinetes)
    }
    assert results == {1: v.IDENTICAL, 2: v.UNEXPLAINED, 3: v.UNEXPLAINED}


# --- banco local ------------------------------------------------------------
def make_database(path, reference="2026-11-18"):
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("CREATE TABLE senadores (cod_senador INTEGER, nome TEXT)")
        connection.executemany("INSERT INTO senadores VALUES (?, ?)", [(1, "FULANO")])
        connection.execute("CREATE TABLE metadados (chave TEXT PRIMARY KEY, valor TEXT)")
        connection.execute("INSERT INTO metadados VALUES ('data_referencia', ?)", (reference,))


def write_manifest(raw_dir, senadores="2026-11-18T10:00:00-03:00"):
    raw_dir.mkdir(exist_ok=True)
    (raw_dir / "coleta.json").write_text(
        json.dumps({"senadores": senadores, "despesas": {}}), encoding="utf-8"
    )


def test_run_coleta_verifica_e_grava(tmp_path):
    database = tmp_path / "db.sqlite"
    make_database(database)
    write_manifest(tmp_path / "raw")

    results = e.run(
        tmp_path / "raw", database, make_client(routes_for([1])), TODAY, clock=lambda: NOW
    )

    assert [r.resultado for r in results] == [v.IDENTICAL]
    with closing(sqlite3.connect(database)) as connection:
        assert connection.execute(
            "SELECT nome, ano, identicos, sem_explicacao FROM verificacoes"
        ).fetchall() == [("equipe", 2026, 1, 0)]
        assert connection.execute("SELECT resultado FROM verificacao_equipe").fetchall() == [
            (v.IDENTICAL,)
        ]


def test_run_recusa_dados_de_outro_dia_e_nao_baixa_nada(tmp_path):
    database = tmp_path / "db.sqlite"
    make_database(database)
    write_manifest(tmp_path / "raw", senadores="2026-11-10T10:00:00-03:00")

    with pytest.raises(v.VerificacaoError, match="mesma foto"):
        e.run(tmp_path / "raw", database, make_client({}), TODAY, clock=lambda: NOW)
    assert not (tmp_path / "raw" / "equipe").exists()


def test_run_pede_a_limpeza_quando_nao_ha_banco(tmp_path):
    with pytest.raises(v.VerificacaoError, match="limpeza"):
        e.run(tmp_path, tmp_path / "nao-existe.sqlite", make_client({}), TODAY)


def test_falha_de_coleta_vira_erro_de_verificacao_sem_gravar(tmp_path):
    database = tmp_path / "db.sqlite"
    make_database(database)
    write_manifest(tmp_path / "raw")
    routes = routes_for([1], {"/servidores/servidores/ativos": {"data": []}})
    with pytest.raises(v.VerificacaoError):
        e.run(tmp_path / "raw", database, make_client(routes), TODAY, clock=lambda: NOW)
    with closing(sqlite3.connect(database)) as connection:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master")}
    assert "verificacao_equipe" not in tables


def test_equipe_e_cota_convivem_na_tabela_de_resumo(tmp_path):
    database = tmp_path / "db.sqlite"
    with closing(sqlite3.connect(database)) as connection, connection:
        v.write_results(connection, [], [2026], NOW)
        e.write_results(connection, [], 2026, NOW)
        v.write_results(connection, [], [2026], NOW)  # a cota roda de novo
        names = [
            row[0] for row in connection.execute("SELECT nome FROM verificacoes ORDER BY nome")
        ]
    assert names == ["cota", "equipe"]


def test_linha_de_comando_avisa_quando_falta_o_banco(tmp_path, capsys):
    code = e.main(["--raw", str(tmp_path), "--banco", str(tmp_path / "nao-existe.sqlite")])
    assert code == 1
    assert "limpeza" in capsys.readouterr().err


# --- quem aparece: o critério e o freio de segurança (D037) -----------------
def results_with(failures: int, total: int) -> list[e.Result]:
    return [
        e.Result(
            code,
            2026,
            10,
            10 if code > failures else 9,
            v.IDENTICAL if code > failures else v.UNEXPLAINED,
        )
        for code in range(1, total + 1)
    ]


def shown(results: list[e.Result]) -> list[int]:
    return [r.cod_senador for r in e.apply_release_rule(results) if r.exibir]


def test_todos_identicos_todos_aparecem():
    assert shown(results_with(0, 81)) == list(range(1, 82))


def test_uma_falha_isolada_esconde_so_aquele_gabinete():
    assert shown(results_with(1, 81)) == list(range(2, 82))


def test_no_limite_de_5_por_cento_ainda_aparece_para_quem_bate():
    # 4 de 81 = 4,9%
    assert shown(results_with(4, 81)) == list(range(5, 82))


def test_acima_de_5_por_cento_a_equipe_some_para_todos():
    # 5 de 81 = 6,2%
    assert shown(results_with(5, 81)) == []


def test_com_poucos_gabinetes_uma_falha_ja_passa_do_limite():
    # 1 de 10 = 10%
    assert shown(results_with(1, 10)) == []


def test_sem_resultado_nenhum_nada_aparece():
    assert e.apply_release_rule([]) == []


def test_verify_equipe_ja_aplica_a_regra_de_exibicao():
    senators = {1: "ALAN RICK", 2: "BETO FARO"}
    gabinetes = [
        {
            "sigla": "A",
            "nome": "Gabinete do Senador Alan Rick",
            "vinculo": "COMISSIONADO",
            "quantidade": 2,
        },
        {
            "sigla": "B",
            "nome": "Gabinete do Senador Beto Faro",
            "vinculo": "COMISSIONADO",
            "quantidade": 3,
        },
    ]
    results = e.verify_equipe(senators, 2026, {"1": pessoal(2), "2": pessoal(3)}, gabinetes)
    assert [r.exibir for r in results] == [True, True]


def test_run_grava_a_coluna_exibir(tmp_path):
    database = tmp_path / "db.sqlite"
    make_database(database)
    write_manifest(tmp_path / "raw")

    e.run(tmp_path / "raw", database, make_client(routes_for([1])), TODAY, clock=lambda: NOW)

    with closing(sqlite3.connect(database)) as connection:
        assert connection.execute("SELECT exibir FROM verificacao_equipe").fetchall() == [(1,)]
