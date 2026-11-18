import json
import sqlite3
from contextlib import closing
from datetime import date, datetime

import httpx
import pytest

from senadados_pipeline import contato as c
from senadados_pipeline import verificacao as v
from senadados_pipeline.coleta import ColetaError

TODAY = date(2026, 11, 18)
NOW = datetime.fromisoformat("2026-11-18T13:00:00-03:00")


def portal_page(
    gabinete="Senado Federal Anexo 2   Ala X Gabinete 05",
    telefones="(61) 3303-6333",
    email="sen.fulano@senado.leg.br",
):
    parts = [
        "<h2>Dados Pessoais</h2><dl><dt>Nome civil:</dt><dd>NOME PRIVADO</dd>",
        "<dt>Data de Nascimento:</dt><dd>01/01/1970</dd>",
    ]
    if gabinete:
        parts.append(f"<dt>Gabinete:</dt>\n<dd>{gabinete}</dd>")
    if telefones:
        parts.append(f"<dt>Telefones:</dt><dd>{telefones}</dd>")
    if email:
        parts.append(f'<dt>E-mail:</dt><dd>\n<a href="mailto:{email}">{email}</a>\n</dd>')
    parts.append("</dl>")
    return "".join(parts)


# --- leitura da página ------------------------------------------------------
def test_parse_portal_le_so_os_tres_campos():
    parsed = c.parse_portal(portal_page())
    assert parsed == {
        "endereco": "Senado Federal Anexo 2 Ala X Gabinete 05",
        "telefones": "(61) 3303-6333",
        "email": "sen.fulano@senado.leg.br",
    }
    assert "NOME PRIVADO" not in json.dumps(parsed)


def test_parse_portal_campo_ausente_vira_none():
    assert c.parse_portal(portal_page(email=None))["email"] is None


def test_parse_portal_recusa_pagina_sem_dados_pessoais():
    with pytest.raises(ColetaError):
        c.parse_portal("<html>mudou</html>")


# --- telefones --------------------------------------------------------------
def test_expande_numeros_abreviados():
    assert c.expand_phones("(61) 3303-6187 / 6188 / 6183") == [
        "(61) 3303-6187",
        "(61) 3303-6188",
        "(61) 3303-6183",
    ]


def test_numero_unico_fica_como_esta():
    assert c.expand_phones("(61) 3303-6333") == ["(61) 3303-6333"]


def test_numero_completo_depois_da_barra_e_mantido():
    assert c.expand_phones("(61) 3303-6187 / (61) 3304-1000") == [
        "(61) 3303-6187",
        "(61) 3304-1000",
    ]


@pytest.mark.parametrize("bad", ["", "3303-6187", "(61) 3303-6187 / 618", "(61) 3303-6187 / abc"])
def test_telefone_em_formato_inesperado_e_recusado(bad):
    with pytest.raises(ColetaError):
        c.expand_phones(bad)


# --- comparação por campo ---------------------------------------------------
def test_endereco_igual_ignora_caixa_e_espacos():
    result = c.compare_address(1, "SENADO FEDERAL ANEXO 2   ALA X", "Senado Federal Anexo 2 Ala X")
    assert result.resultado == v.IDENTICAL and result.valor == "Senado Federal Anexo 2 Ala X"


def test_endereco_diferente_ou_ausente_no_portal_e_sem_explicacao():
    assert c.compare_address(1, "A", "B").resultado == v.UNEXPLAINED
    assert c.compare_address(1, "A", None).resultado == v.UNEXPLAINED


def test_telefones_identicos_mesmo_com_formatacao_e_ordem_diferentes():
    result = c.compare_phones(1, "(61)3303-6177; (61)3303-6178", "(61) 3303-6178 / 6177")
    assert result.resultado == v.IDENTICAL


def test_telefones_explicado_quando_o_portal_traz_numeros_a_mais():
    result = c.compare_phones(1, "(61)3303-6677; (61)3303-6678", "(61) 3303-6677 / 6678 / 6679")
    assert result.resultado == v.EXPLAINED
    assert result.valor == "(61) 3303-6677\n(61) 3303-6678\n(61) 3303-6679"
    assert "1 número" in result.detalhe


def test_telefone_da_api_que_o_portal_nao_tem_e_sem_explicacao():
    result = c.compare_phones(1, "(61)3303-6677; (61)3303-9999", "(61) 3303-6677 / 6678")
    assert result.resultado == v.UNEXPLAINED


def test_telefones_ausentes_ou_em_formato_estranho_sao_sem_explicacao():
    assert c.compare_phones(1, "(61)3303-6677", None).resultado == v.UNEXPLAINED
    assert c.compare_phones(1, "", "(61) 3303-6677").resultado == v.UNEXPLAINED
    assert c.compare_phones(1, "(61)3303-6677", "ligue").resultado == v.UNEXPLAINED


def test_email_igual_ignora_caixa():
    result = c.compare_email(1, "Sen.Fulano@senado.leg.br", "sen.fulano@senado.leg.br")
    assert result.resultado == v.IDENTICAL and result.valor == "sen.fulano@senado.leg.br"


def test_email_ausente_nos_dois_lados_e_identico_e_sem_valor():
    result = c.compare_email(1, "-", None)
    assert result.resultado == v.IDENTICAL and result.valor is None


def test_email_que_difere_ou_em_formato_estranho_e_sem_explicacao():
    assert c.compare_email(1, "a@senado.leg.br", "b@senado.leg.br").resultado == v.UNEXPLAINED
    assert c.compare_email(1, "a@senado.leg.br", None).resultado == v.UNEXPLAINED
    assert c.compare_email(1, "sem arroba", "sem arroba").resultado == v.UNEXPLAINED


def test_falha_de_coleta_derruba_os_tres_campos_do_senador():
    fields = c.compare_contato(1, {"endereco": "A"}, {"erro": "ColetaError: fora do ar"})
    assert [f.resultado for f in fields] == [v.UNEXPLAINED] * 3
    assert all("fora do ar" in f.detalhe for f in fields)
    assert [f.resultado for f in c.compare_contato(1, None, None)] == [v.UNEXPLAINED] * 3


# --- quem aparece -----------------------------------------------------------
def fields_of(field, unexplained, total=81, value="x"):
    out = []
    for code in range(1, total + 1):
        kind = v.UNEXPLAINED if code <= unexplained else v.IDENTICAL
        out.append(c.Field(code, field, kind, None if kind == v.UNEXPLAINED else value))
    return out


def shown(fields, name):
    return sum(f.exibir for f in c.apply_release_rule(fields) if f.campo == name)


def test_falha_isolada_esconde_so_aquele_senador():
    assert shown(fields_of("endereco", 1), "endereco") == 80


def test_freio_de_um_campo_nao_derruba_os_outros():
    fields = fields_of("endereco", 5) + fields_of("email", 0)
    assert shown(fields, "endereco") == 0
    assert shown(fields, "email") == 81


def test_quem_nao_tem_o_campo_nao_aparece_e_nao_conta_como_falha():
    fields = fields_of("email", 0)
    fields[0] = c.Field(1, "email", v.IDENTICAL, None)
    assert shown(fields, "email") == 80


def test_valor_oculto_nao_vaza_para_a_tabela():
    out = c.apply_release_rule(fields_of("endereco", 5))
    assert all(f.valor is None for f in out)


def test_campo_explicado_aparece():
    fields = [
        c.Field(i, "telefones", v.EXPLAINED if i == 1 else v.IDENTICAL, "t") for i in range(1, 82)
    ]
    assert shown(fields, "telefones") == 81


# --- coleta e ponta a ponta --------------------------------------------------
def make_client(pages: dict) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        code = int(request.url.path.split("/sen/")[1].strip("/"))
        assert request.url.params.get("ano") == "2026"
        page = pages[code]
        return httpx.Response(page) if isinstance(page, int) else httpx.Response(200, text=page)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_fetch_portal_pede_a_pagina_do_ano_e_transforma_falha_em_erro(monkeypatch):
    monkeypatch.setattr("senadados_pipeline.coleta.time.sleep", lambda _: None)
    assert c.fetch_portal(make_client({1: portal_page()}), 1, 2026)["telefones"] == "(61) 3303-6333"
    assert "erro" in c.fetch_portal(make_client({1: 503}), 1, 2026)
    assert "erro" in c.fetch_portal(make_client({1: "<html>mudou</html>"}), 1, 2026)


def test_collect_grava_so_o_contato_e_registra_a_hora(tmp_path):
    c.collect_contato(make_client({1: portal_page()}), tmp_path, [1], clock=lambda: NOW)
    saved = (tmp_path / "contato" / "portal.json").read_text(encoding="utf-8")
    assert "NOME PRIVADO" not in saved and "1970" not in saved
    assert (
        json.loads((tmp_path / "coleta.json").read_text(encoding="utf-8"))["contato"]
        == "2026-11-18T13:00:00-03:00"
    )


API = {
    "codigoParlamentar": 1,
    "nomeParlamentar": "FULANO",
    "endereco": "SENADO FEDERAL ANEXO 2   ALA X GABINETE 05",
    "telefones": "(61)3303-6333",
    "email": "sen.fulano@senado.leg.br",
}


def setup(tmp_path, reference="2026-11-18", listed_at="2026-11-18T10:00:00-03:00", api=API):
    database = tmp_path / "db.sqlite"
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.execute("CREATE TABLE senadores (cod_senador INTEGER, nome TEXT)")
        connection.execute("INSERT INTO senadores VALUES (1, 'FULANO')")
        connection.execute("CREATE TABLE metadados (chave TEXT PRIMARY KEY, valor TEXT)")
        connection.execute("INSERT INTO metadados VALUES ('data_referencia', ?)", (reference,))
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "senadores_atuais.json").write_text(json.dumps({"data": [api]}), encoding="utf-8")
    (raw / "coleta.json").write_text(
        json.dumps({"senadores": listed_at, "despesas": {}}), encoding="utf-8"
    )
    return raw, database


def test_run_verifica_e_grava_so_o_que_foi_provado(tmp_path):
    raw, database = setup(tmp_path)
    fields = c.run(raw, database, make_client({1: portal_page()}), TODAY, clock=lambda: NOW)

    assert {f.campo: f.resultado for f in fields} == {
        "endereco": v.IDENTICAL,
        "telefones": v.IDENTICAL,
        "email": v.IDENTICAL,
    }
    with closing(sqlite3.connect(database)) as connection:
        # 1 senador com 3 campos: o freio de 5% se aplica a cada campo (0 falhas)
        assert connection.execute("SELECT endereco, telefones, email FROM contato").fetchone() == (
            "Senado Federal Anexo 2 Ala X Gabinete 05",
            "(61) 3303-6333",
            "sen.fulano@senado.leg.br",
        )
        assert connection.execute(
            "SELECT nome, identicos FROM verificacoes ORDER BY nome"
        ).fetchall() == [("contato_email", 1), ("contato_endereco", 1), ("contato_telefones", 1)]


def test_run_deixa_vazio_o_campo_que_falhou_e_nao_apaga_outras_verificacoes(tmp_path):
    raw, database = setup(tmp_path)
    with closing(sqlite3.connect(database)) as connection, connection:
        v.ensure_verificacoes_table(connection)
        connection.execute("INSERT INTO verificacoes VALUES ('cota', 2026, 1, 0, 0, 'x')")
    page = portal_page(email="outro@senado.leg.br")
    c.run(raw, database, make_client({1: page}), TODAY, clock=lambda: NOW)
    c.run(raw, database, make_client({1: page}), TODAY, clock=lambda: NOW)
    with closing(sqlite3.connect(database)) as connection:
        assert connection.execute("SELECT telefones, email FROM contato").fetchone() == (
            "(61) 3303-6333",
            None,
        )
        names = [r[0] for r in connection.execute("SELECT nome FROM verificacoes ORDER BY nome")]
        assert names == ["contato_email", "contato_endereco", "contato_telefones", "cota"]


def test_run_recusa_dados_de_outro_dia_e_nao_baixa_nada(tmp_path):
    raw, database = setup(tmp_path, listed_at="2026-11-10T10:00:00-03:00")
    with pytest.raises(v.VerificacaoError, match="mesma foto"):
        c.run(raw, database, make_client({}), TODAY, clock=lambda: NOW)
    assert not (raw / "contato").exists()


def test_run_pede_a_coleta_quando_falta_a_lista_de_senadores(tmp_path):
    raw, database = setup(tmp_path)
    (raw / "senadores_atuais.json").unlink()
    with pytest.raises(v.VerificacaoError, match="coleta"):
        c.run(raw, database, make_client({}), TODAY, clock=lambda: NOW)


def test_run_recusa_lista_de_senadores_em_formato_inesperado(tmp_path):
    raw, database = setup(tmp_path)
    (raw / "senadores_atuais.json").write_text(
        json.dumps({"data": [{"sem": "codigo"}]}), encoding="utf-8"
    )
    with pytest.raises(v.VerificacaoError, match="formato"):
        c.run(raw, database, make_client({}), TODAY, clock=lambda: NOW)


def test_run_pede_a_limpeza_quando_nao_ha_banco(tmp_path):
    with pytest.raises(v.VerificacaoError, match="limpeza"):
        c.run(tmp_path, tmp_path / "nao-existe.sqlite", make_client({}), TODAY)


def test_linha_de_comando_avisa_quando_falta_o_banco(tmp_path, capsys):
    assert c.main(["--raw", str(tmp_path), "--banco", str(tmp_path / "nao-existe.sqlite")]) == 1
    assert "limpeza" in capsys.readouterr().err
