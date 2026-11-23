import json
import sqlite3
from contextlib import closing
from datetime import date, datetime

import httpx
import pytest

from senadados_pipeline import moradia as m
from senadados_pipeline import verificacao as v
from senadados_pipeline.coleta import ColetaError

TODAY = date(2026, 11, 18)
NOW = datetime.fromisoformat("2026-11-18T13:00:00-03:00")


# --- páginas do portal (HTML de teste, no mesmo formato do site) -------------
def portal_html(aux="Não utilizou", imo="Utilizou (em 2 meses)", number="123"):
    link = (
        f'<a href="beneficios/?numeroFuncional={number}&amp;ano=2026">{imo}</a>' if number else imo
    )
    return (
        "<div>Uso de Benefícios</div><table><tr><th>Benefício</th><th>Utilização</th></tr>"
        f"<tr><td>Auxílio-Moradia</td><td>{aux}</td></tr>"
        f"<tr><td>Imóvel Funcional</td><td>{link}</td></tr></table>"
        "<div>× Uso de Benefícios Fechar</div>"
    )


def mensal_html(rows):
    body = "".join(
        f"<tr><td>{month}</td><td>{'Utilizou' if aux else 'Não utilizou'}</td>"
        f"<td>{'Utilizou' if imo else 'Não utilizou'}</td></tr>"
        for month, aux, imo in rows
    )
    return (
        "<h4>Benefícios no ano</h4><table><tr><th>Mês</th><th>Auxílio-moradia</th>"
        f"<th>Imóvel funcional</th></tr>{body}</table>"
    )


def test_parse_portal_le_os_estados_e_o_numero_do_link():
    parsed, number = m.parse_portal(portal_html("Não utilizou", "Utilizou (em 10 meses)"))
    assert parsed == {
        "auxilio": {"estado": m.NOT_USED, "meses": 0},
        "imovel": {"estado": m.USED, "meses": 10},
    }
    assert number == "123"


def test_parse_portal_aceita_um_mes_no_singular():
    parsed, _ = m.parse_portal(portal_html("Utilizou (em 1 mês)", "Não utilizou", number="9"))
    assert parsed["auxilio"] == {"estado": m.USED, "meses": 1}


def test_parse_portal_reconhece_renuncia_e_nao_exige_link():
    parsed, number = m.parse_portal(
        portal_html("Renúncia ao benefício", "Renúncia ao benefício.", number=None)
    )
    assert parsed["auxilio"]["estado"] == m.RENOUNCED
    assert parsed["imovel"]["estado"] == m.RENOUNCED
    assert number is None


def test_parse_portal_utilizou_sem_numero_de_meses():
    parsed, _ = m.parse_portal(portal_html("Utilizou", "Não utilizou"))
    assert parsed["auxilio"] == {"estado": m.USED, "meses": None}


def test_parse_portal_recusa_pagina_sem_o_bloco():
    with pytest.raises(ColetaError, match="bloco"):
        m.parse_portal("<html>nada</html>")


def test_parse_portal_recusa_texto_que_nao_entende():
    with pytest.raises(ColetaError, match="não entendi"):
        m.parse_portal(portal_html("Talvez", "Não utilizou"))


def test_parse_mensal_le_os_meses():
    rows = [("01/2026", False, True), ("02/2026", True, False)]
    assert m.parse_mensal(mensal_html(rows)) == [["01/2026", False, True], ["02/2026", True, False]]


def test_parse_mensal_sem_registro_e_lista_vazia():
    assert m.parse_mensal("<p>Nenhum registro encontrado.</p>") == []


@pytest.mark.parametrize(
    "bad", ["<p>outra coisa</p>", "<th>Auxílio-moradia</th><th>Imóvel funcional</th>"]
)
def test_parse_mensal_recusa_formato_inesperado(bad):
    with pytest.raises(ColetaError):
        m.parse_mensal(bad)


# --- comparação -------------------------------------------------------------
def record(
    aux="Não utilizou",
    imo="Utilizou",
    portal_aux=(m.NOT_USED, 0),
    portal_imo=(m.USED, 2),
    months=None,
):
    months = months if months is not None else [["01/2026", False, True], ["02/2026", False, True]]
    return {
        "api": {"Auxílio-Moradia": aux, "Imóvel Funcional": imo},
        "portal": {
            "auxilio": {"estado": portal_aux[0], "meses": portal_aux[1]},
            "imovel": {"estado": portal_imo[0], "meses": portal_imo[1]},
        },
        "mensal": months,
    }


LISTED_NOW = {"auxilioMoradia": "N", "imovelFuncional": "S"}


def test_identico_quando_as_quatro_fontes_concordam():
    result = m.compare_moradia(1, 2026, record(), LISTED_NOW)
    assert result.resultado == v.IDENTICAL


def test_explicado_quando_a_tela_informa_renuncia():
    rec = record("Não utilizou", "Não utilizou", (m.RENOUNCED, 0), (m.RENOUNCED, 0), months=[])
    result = m.compare_moradia(1, 2026, rec, {"auxilioMoradia": "N", "imovelFuncional": "N"})
    assert result.resultado == v.EXPLAINED


def test_utilizou_sem_numero_de_meses_vale_pelo_que_a_pagina_mensal_mostra():
    rec = record(
        "Utilizou",
        "Não utilizou",
        (m.USED, None),
        (m.NOT_USED, 0),
        months=[["10/2026", True, False]],
    )
    result = m.compare_moradia(1, 2026, rec, {"auxilioMoradia": "S", "imovelFuncional": "N"})
    assert result.resultado == v.IDENTICAL


def test_pendente_quando_a_lista_de_hoje_difere_do_ultimo_mes():
    rec = record(
        "Utilizou",
        "Não utilizou",
        (m.USED, 2),
        (m.NOT_USED, 0),
        months=[["09/2026", True, False], ["10/2026", True, False]],
    )
    result = m.compare_moradia(1, 2026, rec, {"auxilioMoradia": "N", "imovelFuncional": "N"})
    assert result.resultado == m.PENDING
    assert "10/2026" in result.detalhe


def test_pendente_quando_a_lista_diz_que_usa_e_a_pagina_nao_tem_meses():
    rec = record("Não utilizou", "Não utilizou", (m.NOT_USED, 0), (m.NOT_USED, 0), months=[])
    result = m.compare_moradia(1, 2026, rec, {"auxilioMoradia": "S", "imovelFuncional": "N"})
    assert result.resultado == m.PENDING


def test_sem_explicacao_quando_a_tela_diz_que_usou_e_a_api_diz_que_nao():
    rec = record(imo="Não utilizou")
    assert m.compare_moradia(1, 2026, rec, LISTED_NOW).resultado == v.UNEXPLAINED


def test_sem_explicacao_quando_a_api_diz_que_usou_e_a_tela_diz_que_nao():
    rec = record(aux="Utilizou")
    assert m.compare_moradia(1, 2026, rec, LISTED_NOW).resultado == v.UNEXPLAINED


def test_sem_explicacao_quando_o_numero_de_meses_da_tela_difere_da_pagina_mensal():
    rec = record(portal_imo=(m.USED, 5))
    result = m.compare_moradia(1, 2026, rec, LISTED_NOW)
    assert result.resultado == v.UNEXPLAINED
    assert "5 mês" in result.detalhe


def test_sem_explicacao_quando_a_tela_diz_que_nao_usou_mas_ha_meses_de_uso():
    rec = record(imo="Não utilizou", portal_imo=(m.NOT_USED, 0))
    assert m.compare_moradia(1, 2026, rec, LISTED_NOW).resultado == v.UNEXPLAINED


def test_sem_explicacao_quando_a_tela_diz_que_usou_mas_nao_ha_meses():
    rec = record(months=[])
    assert m.compare_moradia(1, 2026, rec, LISTED_NOW).resultado == v.UNEXPLAINED


def test_sem_explicacao_com_mes_de_outro_ano_ou_repetido():
    other_year = record(months=[["01/2025", False, True], ["02/2025", False, True]])
    repeated = record(months=[["01/2026", False, True], ["01/2026", False, True]])
    assert m.compare_moradia(1, 2026, other_year, LISTED_NOW).resultado == v.UNEXPLAINED
    assert m.compare_moradia(1, 2026, repeated, LISTED_NOW).resultado == v.UNEXPLAINED


def test_sem_explicacao_quando_o_resumo_da_api_tem_valor_inesperado():
    assert m.compare_moradia(1, 2026, record(aux="Talvez"), LISTED_NOW).resultado == v.UNEXPLAINED


def test_sem_explicacao_quando_a_coleta_do_senador_falhou():
    result = m.compare_moradia(1, 2026, {"erro": "ColetaError: página fora do ar"}, LISTED_NOW)
    assert result.resultado == v.UNEXPLAINED
    assert "fora do ar" in result.detalhe


def test_sem_explicacao_quando_o_senador_nao_esta_na_lista_do_mes():
    assert m.compare_moradia(1, 2026, record(), None).resultado == v.UNEXPLAINED


# --- quem aparece -----------------------------------------------------------
def results_of(unexplained=0, pending=0, total=81):
    kinds = [v.UNEXPLAINED] * unexplained + [m.PENDING] * pending
    kinds += [v.IDENTICAL] * (total - len(kinds))
    return [m.Result(code, 2026, kind) for code, kind in enumerate(kinds, start=1)]


def test_so_identico_e_explicado_aparecem():
    special = [v.EXPLAINED, m.PENDING, v.UNEXPLAINED]
    results = [
        m.Result(code, 2026, kind) for code, kind in enumerate([v.IDENTICAL] * 78 + special, 1)
    ]
    shown = m.apply_release_rule(results)
    assert [r.exibir for r in shown[:78]] == [True] * 78
    assert [r.exibir for r in shown[78:]] == [True, False, False]


def test_pendente_nao_conta_para_o_freio_de_seguranca():
    # 10 pendentes de 81 (12%) não derrubam a moradia dos demais
    shown = [r.exibir for r in m.apply_release_rule(results_of(pending=10))]
    assert sum(shown) == 71


def test_sem_explicacao_acima_de_5_por_cento_esconde_para_todos():
    assert not any(r.exibir for r in m.apply_release_rule(results_of(unexplained=5)))


def test_sem_explicacao_ate_5_por_cento_esconde_so_os_proprios():
    assert sum(r.exibir for r in m.apply_release_rule(results_of(unexplained=4))) == 77


def test_sem_resultado_nada_aparece():
    assert m.apply_release_rule([]) == []


def test_lista_de_moradia_recusa_nome_repetido_e_ignora_sem_nome():
    with pytest.raises(v.VerificacaoError, match="repete"):
        m.build_listed([{"nomeParlamentar": "ALAN RICK"}, {"nomeParlamentar": "Alan Rick"}])
    assert m.build_listed([{"nomeParlamentar": None}, {"nomeParlamentar": "Ana"}]).keys() == {"ANA"}


# --- coleta -----------------------------------------------------------------
def make_client(code_pages: dict) -> httpx.Client:
    """`code_pages`: código -> dict com api, portal e mensal (texto HTML ou None)."""

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/auxilio-moradia-imoveis-funcionais"):
            return httpx.Response(200, json={"data": [{"nomeParlamentar": "FULANO", **LISTED_NOW}]})
        code = (
            int(path.split("/sen/")[1].split("/")[0])
            if "/sen/" in path
            else int(path.split("/senadores/")[1].split("/")[0])
        )
        page = code_pages[code]
        if "recursos-utilizados" in path:
            if page.get("api_status"):
                return httpx.Response(page["api_status"])
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "beneficios": [
                                {"beneficio": "Auxílio-Moradia", "utilizacao": "Não utilizou"},
                                {"beneficio": "Imóvel Funcional", "utilizacao": "Utilizou"},
                            ]
                        }
                    ]
                },
            )
        if "/beneficios/" in path:
            return httpx.Response(200, text=page["mensal"])
        return httpx.Response(200, text=page["portal"])

    return httpx.Client(
        base_url="https://example.test/api/v1", transport=httpx.MockTransport(handler)
    )


GOOD = {
    "portal": portal_html(),
    "mensal": mensal_html([("01/2026", False, True), ("02/2026", False, True)]),
}


def test_fetch_senator_junta_as_tres_fontes_sem_guardar_o_numero_funcional():
    rec = m.fetch_senator(make_client({1: GOOD}), 1, 2026)
    assert rec["api"] == {"Auxílio-Moradia": "Não utilizou", "Imóvel Funcional": "Utilizou"}
    assert rec["portal"]["imovel"] == {"estado": m.USED, "meses": 2}
    assert rec["mensal"] == [["01/2026", False, True], ["02/2026", False, True]]
    assert "123" not in json.dumps(rec)


def test_fetch_senator_sem_link_nao_pede_a_pagina_mensal():
    pages = {
        1: {
            "portal": portal_html("Não utilizou", "Não utilizou", number=None),
            "mensal": "NAO DEVE SER LIDA",
        }
    }
    assert m.fetch_senator(make_client(pages), 1, 2026)["mensal"] == []


def test_fetch_senator_transforma_falha_em_erro_do_proprio_senador(monkeypatch):
    monkeypatch.setattr("senadados_pipeline.coleta.time.sleep", lambda _: None)
    rec = m.fetch_senator(make_client({1: {**GOOD, "api_status": 503}}), 1, 2026)
    assert "erro" in rec


def test_fetch_senator_pagina_fora_do_formato_vira_erro():
    rec = m.fetch_senator(make_client({1: {**GOOD, "portal": "<html>mudou</html>"}}), 1, 2026)
    assert "bloco" in rec["erro"]


def test_collect_grava_so_o_necessario_e_registra_a_hora(tmp_path):
    year, records, entries = m.collect_moradia(
        make_client({1: GOOD}), tmp_path, [1], clock=lambda: NOW
    )
    saved = (tmp_path / "moradia" / "uso.json").read_text(encoding="utf-8")
    assert year == 2026 and list(records) == [1] and len(entries) == 1
    assert "numeroFuncional" not in saved and "123" not in saved
    assert (
        json.loads((tmp_path / "coleta.json").read_text(encoding="utf-8"))["moradia"]
        == "2026-11-18T13:00:00-03:00"
    )


def test_collect_falha_se_a_lista_de_moradia_vier_em_formato_inesperado(tmp_path):
    def handler(_request):
        return httpx.Response(200, json=[1, 2])

    client = httpx.Client(
        base_url="https://example.test/api/v1", transport=httpx.MockTransport(handler)
    )
    with pytest.raises(ColetaError):
        m.collect_moradia(client, tmp_path, [1], clock=lambda: NOW)


# --- do começo ao fim --------------------------------------------------------
def make_database(path, reference="2026-11-18"):
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("CREATE TABLE senadores (cod_senador INTEGER, nome TEXT)")
        connection.execute("INSERT INTO senadores VALUES (1, 'FULANO')")
        connection.execute("CREATE TABLE metadados (chave TEXT PRIMARY KEY, valor TEXT)")
        connection.execute("INSERT INTO metadados VALUES ('data_referencia', ?)", (reference,))


def write_manifest(raw_dir, senadores="2026-11-18T10:00:00-03:00"):
    raw_dir.mkdir(exist_ok=True)
    (raw_dir / "coleta.json").write_text(
        json.dumps({"senadores": senadores, "despesas": {}}), encoding="utf-8"
    )


def run_atual(raw_dir, database, client):
    """O `run` só com o ano atual (quatro fontes); o ano anterior tem testes próprios."""
    return m.run(raw_dir, database, client, TODAY, clock=lambda: NOW, com_ano_anterior=False)


def test_run_coleta_verifica_e_grava_as_tabelas(tmp_path):
    database = tmp_path / "db.sqlite"
    make_database(database)
    write_manifest(tmp_path / "raw")

    results = run_atual(tmp_path / "raw", database, make_client({1: GOOD}))

    assert [r.resultado for r in results] == [v.IDENTICAL] and results[0].exibir
    with closing(sqlite3.connect(database)) as connection:
        assert connection.execute(
            "SELECT resultado, exibir FROM verificacao_moradia"
        ).fetchall() == [(v.IDENTICAL, 1)]
        assert connection.execute(
            "SELECT mes, auxilio_moradia, imovel_funcional FROM moradia_meses ORDER BY mes"
        ).fetchall() == [("2026-01", 0, 1), ("2026-02", 0, 1)]
        assert connection.execute(
            "SELECT nome, identicos, sem_explicacao FROM verificacoes"
        ).fetchall() == [("moradia", 1, 0)]


def test_run_nao_apaga_o_resumo_das_outras_verificacoes(tmp_path):
    database = tmp_path / "db.sqlite"
    make_database(database)
    write_manifest(tmp_path / "raw")
    with closing(sqlite3.connect(database)) as connection, connection:
        v.ensure_verificacoes_table(connection)
        connection.execute("INSERT INTO verificacoes VALUES ('cota', 2026, 1, 0, 0, 'x')")
    run_atual(tmp_path / "raw", database, make_client({1: GOOD}))
    run_atual(tmp_path / "raw", database, make_client({1: GOOD}))
    with closing(sqlite3.connect(database)) as connection:
        assert [
            r[0] for r in connection.execute("SELECT nome FROM verificacoes ORDER BY nome")
        ] == ["cota", "moradia"]
        assert connection.execute("SELECT COUNT(*) FROM verificacao_moradia").fetchone() == (1,)


def test_run_recusa_dados_de_outro_dia(tmp_path):
    database = tmp_path / "db.sqlite"
    make_database(database)
    write_manifest(tmp_path / "raw", senadores="2026-11-10T10:00:00-03:00")
    with pytest.raises(v.VerificacaoError, match="mesma foto"):
        run_atual(tmp_path / "raw", database, make_client({}))
    assert not (tmp_path / "raw" / "moradia").exists()


def test_run_pede_a_limpeza_quando_nao_ha_banco(tmp_path):
    with pytest.raises(v.VerificacaoError, match="limpeza"):
        m.run(tmp_path, tmp_path / "nao-existe.sqlite", make_client({}), TODAY)


def test_linha_de_comando_avisa_quando_falta_o_banco(tmp_path, capsys):
    code = m.main(["--raw", str(tmp_path), "--banco", str(tmp_path / "nao-existe.sqlite")])
    assert code == 1
    assert "limpeza" in capsys.readouterr().err


# --- o ano anterior, com três fontes (D049) ----------------------------------
GOOD_2025 = {
    "portal": portal_html(),
    "mensal": mensal_html([("01/2025", False, True), ("02/2025", False, True)]),
}


def test_ano_que_passou_vale_com_as_tres_fontes_e_sem_a_lista_do_mes():
    rec = record(months=[["01/2025", False, True], ["02/2025", False, True]])
    result = m.compare_moradia(1, 2025, rec, None, usar_lista=False)
    assert result.resultado == v.IDENTICAL


def test_ano_que_passou_com_renuncia_e_explicado():
    rec = record(
        aux="Não utilizou",
        imo="Não utilizou",
        portal_aux=(m.RENOUNCED, 0),
        portal_imo=(m.NOT_USED, 0),
        months=[],
    )
    assert m.compare_moradia(1, 2025, rec, None, usar_lista=False).resultado == v.EXPLAINED


def test_ano_que_passou_continua_exigindo_que_as_tres_fontes_concordem():
    rec = record(aux="Utilizou")  # a API diz que usou auxílio; a tela e a página mensal, que não
    assert m.compare_moradia(1, 2025, rec, None, usar_lista=False).resultado == v.UNEXPLAINED
    other_year = record(months=[["01/2026", False, True], ["02/2026", False, True]])
    assert m.compare_moradia(1, 2025, other_year, None, usar_lista=False).resultado == v.UNEXPLAINED


def make_client_por_ano(pages: dict) -> httpx.Client:
    """`pages`: ano -> dict com portal e mensal. O resumo da API é o mesmo nos dois anos."""

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/auxilio-moradia-imoveis-funcionais"):
            return httpx.Response(200, json={"data": [{"nomeParlamentar": "FULANO", **LISTED_NOW}]})
        year = int(request.url.params["ano"]) if "ano" in request.url.params else 2026
        if "recursos-utilizados" in path:
            benefits = [
                {"beneficio": "Auxílio-Moradia", "utilizacao": "Não utilizou"},
                {"beneficio": "Imóvel Funcional", "utilizacao": "Utilizou"},
            ]
            return httpx.Response(200, json={"data": [{"beneficios": benefits}]})
        key = "mensal" if "/beneficios/" in path else "portal"
        return httpx.Response(200, text=pages[year][key])

    return httpx.Client(
        base_url="https://example.test/api/v1", transport=httpx.MockTransport(handler)
    )


def test_run_confere_tambem_o_ano_anterior_e_grava_os_dois_anos(tmp_path):
    database = tmp_path / "db.sqlite"
    make_database(database)
    write_manifest(tmp_path / "raw")
    client = make_client_por_ano({2026: GOOD, 2025: GOOD_2025})

    results = m.run(tmp_path / "raw", database, client, TODAY, clock=lambda: NOW)

    assert [(r.ano, r.resultado) for r in results] == [(2026, v.IDENTICAL), (2025, v.IDENTICAL)]
    with closing(sqlite3.connect(database)) as connection:
        assert connection.execute(
            "SELECT ano, resultado, exibir FROM verificacao_moradia ORDER BY ano"
        ).fetchall() == [(2025, v.IDENTICAL, 1), (2026, v.IDENTICAL, 1)]
        assert connection.execute(
            "SELECT ano, mes FROM moradia_meses ORDER BY ano, mes"
        ).fetchall() == [(2025, "2025-01"), (2025, "2025-02"), (2026, "2026-01"), (2026, "2026-02")]
        assert connection.execute(
            "SELECT nome, ano, identicos FROM verificacoes ORDER BY ano"
        ).fetchall() == [("moradia", 2025, 1), ("moradia", 2026, 1)]
    raw_2025 = tmp_path / "raw" / "moradia" / "uso_2025.json"
    assert raw_2025.exists() and "lista" not in raw_2025.read_text(encoding="utf-8")


def test_ano_anterior_com_falha_nao_derruba_a_moradia_do_ano_atual(tmp_path):
    database = tmp_path / "db.sqlite"
    make_database(database)
    write_manifest(tmp_path / "raw")
    ruim = {"portal": "<html>mudou</html>", "mensal": ""}
    client = make_client_por_ano({2026: GOOD, 2025: ruim})

    results = m.run(tmp_path / "raw", database, client, TODAY, clock=lambda: NOW)

    assert [(r.ano, r.resultado, r.exibir) for r in results] == [
        (2026, v.IDENTICAL, True),
        (2025, v.UNEXPLAINED, False),
    ]
