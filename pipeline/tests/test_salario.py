import json
import sqlite3
from contextlib import closing
from datetime import date, datetime

import httpx
import pytest

from senadados_pipeline import salario as s
from senadados_pipeline import verificacao as v
from senadados_pipeline.coleta import ColetaError

TODAY = date(2026, 11, 18)
NOW = datetime.fromisoformat("2026-11-18T13:00:00-03:00")


def payroll_row(
    name="FULANA DE TAL",
    seq=1,
    kind="Normal",
    basic="46.366,19",
    net="29.048,49",
    pension="-7.552,74",
    tax="-9.764,96",
    indemnity="0,00",
):
    row = {"sequencial": seq, "nome": name, "mes": 10, "ano": 2026, "tipo_folha": kind}
    for field in s.MONEY_FIELDS:
        row[field] = "0,00"
    row.update(
        remuneracao_basica=basic,
        remuneracao_liquida=net,
        previdencia=pension,
        imposto_renda=tax,
        vantagens_indenizatorias=indemnity,
    )
    return row


IDENTITY = {"nome": "FULANA DE TAL", "vinculo": "PARLAMENTAR", "situacao": "ATIVO", "uf": "AC"}


def check(rows=None, identity=None, uf="AC", ambiguous=0):
    rows = [payroll_row()] if rows is None else rows
    return s.check_salary(1, uf, 2026, 10, identity or IDENTITY, rows, ambiguous)


# --- leitura ----------------------------------------------------------------
@pytest.mark.parametrize(
    ("text", "cents"),
    [
        ("46.366,19", 4636619),
        ("0,00", 0),
        ("-4.819,10", -481910),
        ("7,05", 705),
        ("1.234.567,89", 123456789),
    ],
)
def test_parse_money(text, cents):
    assert s.parse_money(text) == cents


@pytest.mark.parametrize("bad", ["46366.19", "abc", "", None, "46.366,1", 46366.19])
def test_parse_money_recusa_formato_inesperado(bad):
    with pytest.raises(ColetaError):
        s.parse_money(bad)


def test_parse_detail_link_le_codigo_e_vinculo():
    page = '<a href="https://x/detalhe.asp?fcodigo=3873056&amp;fvinculo=1">Consulte</a>'
    assert s.parse_detail_link(page) == ("3873056", "1")
    assert s.parse_detail_link("<p>nada</p>") is None


def identification_page(name="ALAN RICK MIRANDA", link="PARLAMENTAR", situation="ATIVO", uf="AC"):
    def row(k, val):
        return (
            f'<tr><td class="coltitulo_identifica">{k}</td>'
            f'<td class="coldados_identifica">{val}</td></tr>'
        )

    return (
        "<table>"
        + row("Nome", name)
        + row("Vínculo", link)
        + row("Situação", situation)
        + row("UF", uf)
        + "</table>"
    )


def test_parse_identification():
    assert s.parse_identification(identification_page()) == {
        "nome": "ALAN RICK MIRANDA",
        "vinculo": "PARLAMENTAR",
        "situacao": "ATIVO",
        "uf": "AC",
    }


def test_parse_identification_recusa_pagina_sem_os_campos():
    with pytest.raises(ColetaError, match="campo"):
        s.parse_identification("<table></table>")


# --- só os senadores ficam ----------------------------------------------------
def test_senator_rows_descarta_os_nomes_que_nao_sao_de_senador():
    rows = [
        payroll_row("FULANA DE TAL", 1),
        payroll_row("SERVIDOR COMUM", 2),
        payroll_row("OUTRO SERVIDOR", 3),
    ]
    unique, ambiguous = s.senator_rows(rows, {"FULANA DE TAL"})
    assert list(unique) == ["FULANA DE TAL"] and ambiguous == {}
    assert "SERVIDOR" not in json.dumps(unique)


def test_senator_rows_ignora_acento_e_caixa():
    unique, _ = s.senator_rows([payroll_row("Antônia de Sousa", 1)], {"ANTONIA DE SOUSA"})
    assert "ANTONIA DE SOUSA" in unique


def test_nome_em_duas_matriculas_nao_guarda_as_linhas_so_a_contagem():
    rows = [payroll_row("FULANA DE TAL", 1), payroll_row("FULANA DE TAL", 2, basic="6.686,29")]
    unique, ambiguous = s.senator_rows(rows, {"FULANA DE TAL"})
    assert unique == {} and ambiguous == {"FULANA DE TAL": 2}


def test_normal_e_suplementar_da_mesma_matricula_ficam_juntos():
    rows = [
        payroll_row(seq=1),
        payroll_row(
            seq=1, kind="Suplementar", basic="0,00", net="0,00", pension="0,00", tax="0,00"
        ),
    ]
    unique, ambiguous = s.senator_rows(rows, {"FULANA DE TAL"})
    assert len(unique["FULANA DE TAL"]) == 2 and ambiguous == {}


# --- a prova ------------------------------------------------------------------
def test_passa_quando_tudo_fecha():
    result = check()
    assert result.resultado == v.IDENTICAL
    assert (result.basica_centavos, result.liquida_centavos) == (4636619, 2904849)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"vinculo": "COMISSIONADO"}, "vínculo"),
        ({"situacao": "APOSENTADO"}, "situação"),
        ({"uf": "SP"}, "UF"),
    ],
)
def test_identidade_diferente_do_esperado_e_sem_explicacao(change, message):
    result = check(identity={**IDENTITY, **change})
    assert result.resultado == v.UNEXPLAINED and message in result.detalhe


def test_falha_na_identificacao_e_sem_explicacao():
    assert check(identity={"erro": "ColetaError: fora do ar"}).resultado == v.UNEXPLAINED


def test_nome_fora_da_folha_e_sem_explicacao():
    assert "não está na folha" in check(rows=[]).detalhe


def test_duas_matriculas_com_o_mesmo_nome_e_ambiguo():
    rows = [payroll_row(seq=1), payroll_row(seq=2)]
    assert "ambígua" in check(rows=rows).detalhe
    assert "ambígua" in check(rows=[], ambiguous=2).detalhe


def test_sem_folha_normal_ou_com_duas():
    assert "0 folhas normais" in check(rows=[payroll_row(kind="Suplementar")]).detalhe
    assert "2 folhas normais" in check(rows=[payroll_row(), payroll_row()]).detalhe


def test_suplementar_zerada_e_aceita_e_com_valores_nao():
    zero = payroll_row(kind="Suplementar", basic="0,00", net="0,00", pension="0,00", tax="0,00")
    assert check(rows=[payroll_row(), zero]).resultado == v.IDENTICAL
    with_value = payroll_row(
        kind="Suplementar",
        basic="0,00",
        net="0,00",
        pension="0,00",
        tax="0,00",
        indemnity="46.366,19",
    )
    result = check(rows=[payroll_row(), with_value])
    assert result.resultado == v.UNEXPLAINED and "suplementar" in result.detalhe


def test_conta_interna_que_nao_fecha_e_sem_explicacao():
    result = check(rows=[payroll_row(net="29.048,50")])
    assert result.resultado == v.UNEXPLAINED and "soma" in result.detalhe


def test_valor_nao_positivo_e_sem_explicacao():
    row = payroll_row(basic="0,00", net="-17.317,70")
    assert check(rows=[row]).resultado == v.UNEXPLAINED


def test_valor_em_formato_inesperado_e_sem_explicacao():
    assert "formato" in check(rows=[payroll_row(basic="46366.19")]).detalhe


# --- quem aparece ------------------------------------------------------------
def results_of(failures, total=81):
    out = []
    for code in range(1, total + 1):
        ok = code > failures
        out.append(
            s.Result(
                code,
                2026,
                10,
                v.IDENTICAL if ok else v.UNEXPLAINED,
                None if ok else "x",
                4636619 if ok else None,
                2904849 if ok else None,
            )
        )
    return out


def test_falha_isolada_esconde_so_o_proprio_senador():
    shown = s.apply_release_rule(results_of(2))
    assert sum(r.exibir for r in shown) == 79
    assert all(r.basica_centavos is None for r in shown if not r.exibir)


def test_acima_de_5_por_cento_esconde_o_salario_de_todos_e_zera_os_valores():
    shown = s.apply_release_rule(results_of(5))
    assert not any(r.exibir for r in shown)
    assert all(r.basica_centavos is None and r.liquida_centavos is None for r in shown)


def test_ate_5_por_cento_ainda_aparece():
    assert sum(r.exibir for r in s.apply_release_rule(results_of(4))) == 77


def test_sem_resultado_nada_aparece():
    assert s.apply_release_rule([]) == []


# --- folha do mês mais recente ------------------------------------------------
def make_client(routes: dict) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        key = request.url.path
        if "detalhe.asp" in key:
            return httpx.Response(200, text=routes["detalhe"][request.url.params["fcodigo"]])
        if "/sen/" in key:
            code = int(key.split("/sen/")[1].strip("/"))
            return httpx.Response(200, text=routes["portal"][code])
        body = routes.get(key)
        return httpx.Response(200, json=body) if body is not None else httpx.Response(404)

    return httpx.Client(
        base_url="https://example.test/api/v1", transport=httpx.MockTransport(handler)
    )


def test_fetch_folha_volta_ao_mes_anterior_se_o_atual_esta_vazio():
    client = make_client(
        {
            "/api/v1/servidores/remuneracoes/2026/11": [],
            "/api/v1/servidores/remuneracoes/2026/10": [{"x": 1}],
        }
    )
    assert s.fetch_folha(client, TODAY) == (2026, 10, [{"x": 1}])


def test_fetch_folha_atravessa_a_virada_do_ano():
    client = make_client(
        {
            "/api/v1/servidores/remuneracoes/2026/1": [],
            "/api/v1/servidores/remuneracoes/2025/12": [{"x": 1}],
        }
    )
    assert s.fetch_folha(client, date(2026, 1, 15))[:2] == (2025, 12)


def test_fetch_folha_recusa_vazia_ou_em_formato_inesperado():
    empty = make_client({f"/api/v1/servidores/remuneracoes/2026/{m}": [] for m in (11, 10, 9, 8)})
    with pytest.raises(ColetaError, match="vazia"):
        s.fetch_folha(empty, TODAY)
    bad = make_client({"/api/v1/servidores/remuneracoes/2026/11": {"data": []}})
    with pytest.raises(ColetaError, match="formato"):
        s.fetch_folha(bad, TODAY)


# --- ponta a ponta -----------------------------------------------------------
PORTAL = '<a href="https://x/detalhe.asp?fcodigo=900&amp;fvinculo=1">Consulte</a>'
ROUTES = {
    "portal": {1: PORTAL},
    "detalhe": {"900": identification_page("FULANA DE TAL", uf="AC")},
    "/api/v1/servidores/remuneracoes/2026/11": [payroll_row(), payroll_row("SERVIDOR COMUM", 7)],
}


def test_collect_grava_so_as_linhas_dos_senadores(tmp_path):
    year, month, identities, matched, ambiguous = s.collect_salario(
        make_client(ROUTES), tmp_path, {1: "FULANA"}, TODAY, clock=lambda: NOW
    )
    saved = (tmp_path / "salario" / "folha_senadores.json").read_text(encoding="utf-8")
    assert (year, month) == (2026, 11) and ambiguous == {}
    assert "SERVIDOR COMUM" not in saved
    assert (
        json.loads((tmp_path / "coleta.json").read_text(encoding="utf-8"))["salario"]
        == "2026-11-18T13:00:00-03:00"
    )


def test_fetch_identity_sem_link_vira_erro_do_proprio_senador():
    client = make_client({**ROUTES, "portal": {1: "<html>sem link</html>"}})
    assert "link" in s.fetch_identity(client, 1, 2026)["erro"]


def make_database(path, reference="2026-11-18"):
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("CREATE TABLE senadores (cod_senador INTEGER, nome TEXT, uf TEXT)")
        connection.execute("INSERT INTO senadores VALUES (1, 'FULANA', 'AC')")
        connection.execute("CREATE TABLE metadados (chave TEXT PRIMARY KEY, valor TEXT)")
        connection.execute("INSERT INTO metadados VALUES ('data_referencia', ?)", (reference,))


def write_manifest(raw, senadores="2026-11-18T10:00:00-03:00"):
    raw.mkdir(exist_ok=True)
    (raw / "coleta.json").write_text(
        json.dumps({"senadores": senadores, "despesas": {}}), encoding="utf-8"
    )


def test_run_verifica_e_grava_so_o_salario_provado(tmp_path):
    database = tmp_path / "db.sqlite"
    make_database(database)
    write_manifest(tmp_path / "raw")
    results = s.run(tmp_path / "raw", database, make_client(ROUTES), TODAY, clock=lambda: NOW)
    assert [r.resultado for r in results] == [v.IDENTICAL]
    with closing(sqlite3.connect(database)) as connection:
        assert connection.execute(
            "SELECT mes, remuneracao_basica_centavos, remuneracao_liquida_centavos FROM salario"
        ).fetchall() == [(11, 4636619, 2904849)]
        assert connection.execute(
            "SELECT nome, identicos, sem_explicacao FROM verificacoes"
        ).fetchall() == [("salario", 1, 0)]


def test_run_nao_grava_salario_de_quem_falhou_nem_apaga_outras_verificacoes(tmp_path):
    database = tmp_path / "db.sqlite"
    make_database(database)
    write_manifest(tmp_path / "raw")
    with closing(sqlite3.connect(database)) as connection, connection:
        v.ensure_verificacoes_table(connection)
        connection.execute("INSERT INTO verificacoes VALUES ('cota', 2026, 1, 0, 0, 'x')")
    routes = {**ROUTES, "detalhe": {"900": identification_page("FULANA DE TAL", uf="SP")}}
    s.run(tmp_path / "raw", database, make_client(routes), TODAY, clock=lambda: NOW)
    with closing(sqlite3.connect(database)) as connection:
        assert connection.execute("SELECT COUNT(*) FROM salario").fetchone() == (0,)
        assert connection.execute(
            "SELECT resultado, exibir FROM verificacao_salario"
        ).fetchall() == [(v.UNEXPLAINED, 0)]
        assert [
            r[0] for r in connection.execute("SELECT nome FROM verificacoes ORDER BY nome")
        ] == ["cota", "salario"]


def test_run_recusa_dados_de_outro_dia_e_nao_baixa_nada(tmp_path):
    database = tmp_path / "db.sqlite"
    make_database(database)
    write_manifest(tmp_path / "raw", senadores="2026-11-10T10:00:00-03:00")
    with pytest.raises(v.VerificacaoError, match="mesma foto"):
        s.run(tmp_path / "raw", database, make_client({}), TODAY, clock=lambda: NOW)
    assert not (tmp_path / "raw" / "salario").exists()


def test_falha_da_folha_vira_erro_de_verificacao(tmp_path):
    database = tmp_path / "db.sqlite"
    make_database(database)
    write_manifest(tmp_path / "raw")
    routes = {**ROUTES, "/api/v1/servidores/remuneracoes/2026/11": {"data": []}}
    with pytest.raises(v.VerificacaoError):
        s.run(tmp_path / "raw", database, make_client(routes), TODAY, clock=lambda: NOW)


def test_run_pede_a_limpeza_quando_nao_ha_banco(tmp_path):
    with pytest.raises(v.VerificacaoError, match="limpeza"):
        s.run(tmp_path, tmp_path / "nao-existe.sqlite", make_client({}), TODAY)


def test_linha_de_comando_avisa_quando_falta_o_banco(tmp_path, capsys):
    assert s.main(["--raw", str(tmp_path), "--banco", str(tmp_path / "nao-existe.sqlite")]) == 1
    assert "limpeza" in capsys.readouterr().err
