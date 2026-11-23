import json
import sqlite3
from contextlib import closing
from datetime import date, datetime

import httpx
import pytest

from senadados_pipeline import perfil as p
from senadados_pipeline import verificacao as v
from senadados_pipeline.coleta import ColetaError

TODAY = date(2026, 11, 23)
NOW = datetime.fromisoformat("2026-11-23T10:00:00-03:00")
FOTO = "https://legis.senado.leg.br/senadores/fotos-oficiais/{}"
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 1020


def item(code=1, nome="Fulano", uf="AC", partido="P1", inicio="2023-02-01", fim="2031-01-31",
         segunda=True):
    mandato = {"PrimeiraLegislaturaDoMandato": {"DataInicio": inicio, "DataFim": "2027-01-31"}}
    if segunda:
        mandato["SegundaLegislaturaDoMandato"] = {"DataInicio": "2027-02-01", "DataFim": fim}
    return {
        "IdentificacaoParlamentar": {
            "CodigoParlamentar": str(code), "NomeParlamentar": nome, "UfParlamentar": uf,
            "SiglaPartidoParlamentar": partido,
            "UrlFotoParlamentar": f"http://www.senado.leg.br/senadores/img/fotos-oficiais/senador{code}.jpg",
            "EmailParlamentar": "privado@senado.leg.br",
        },
        "Mandato": mandato,
    }


def payload(*items):
    return {"ListaParlamentarEmExercicio": {"Parlamentares": {"Parlamentar": list(items)}}}


API1 = {"codigoParlamentar": 1, "nomeParlamentar": "FULANO", "uf": "AC", "partido": "P1",
        "mandato": "2023 / 2031"}
LEGIS1 = {"nome": "Fulano", "uf": "AC", "partido": "P1", "foto_url": "x",
          "inicio": "2023-02-01", "fim": "2031-01-31"}
FOTO_OK = {"url": FOTO.format(1), "ok": True, "motivo": None}


# --- lista legislativa ------------------------------------------------------
def test_parse_legis_pega_inicio_da_primeira_e_fim_da_ultima_legislatura():
    legis = p.parse_legis(payload(item(1), item(2, segunda=False)))
    assert legis[1]["inicio"] == "2023-02-01" and legis[1]["fim"] == "2031-01-31"
    assert legis[2]["fim"] == "2027-01-31"  # só uma legislatura: vale o fim dela
    assert legis[1]["foto_url"].startswith("http://www.senado.leg.br/")


@pytest.mark.parametrize(
    "ruim", [{}, {"ListaParlamentarEmExercicio": {}}, payload(), payload({"x": 1}),
             payload(item(1), item(1)), payload(item(1, inicio="01/02/2023"))]
)
def test_parse_legis_recusa_formato_inesperado(ruim):
    with pytest.raises(ColetaError):
        p.parse_legis(ruim)


# --- foto -------------------------------------------------------------------
def client_foto(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def resposta_ok(request):
    if request.url.host == "www.senado.leg.br":
        return httpx.Response(301, headers={"location": FOTO.format(1)})
    assert request.headers["range"] == "bytes=0-1023"
    return httpx.Response(
        206, content=JPEG,
        headers={"content-type": "image/jpeg", "content-range": "bytes 0-1023/241034"},
    )


def test_foto_ok_segue_o_redirecionamento_e_guarda_o_endereco_final():
    cli = client_foto(resposta_ok)
    assert p.check_foto(cli, 1, "http://www.senado.leg.br/x/senador1.jpg") == FOTO_OK


def test_foto_aceita_resposta_completa_com_content_length():
    def handler(request):
        return httpx.Response(200, content=JPEG * 20, headers={"content-type": "image/jpeg"})

    r = p.check_foto(client_foto(handler), 1, FOTO.format(1))
    assert r["ok"], r


@pytest.mark.parametrize(
    ("resposta", "trecho"),
    [
        (httpx.Response(404), "resposta 404"),
        (httpx.Response(206, content=JPEG, headers={"content-type": "text/html",
                        "content-range": "bytes 0-1023/241034"}), "não JPEG"),
        (httpx.Response(206, content=b"<html>" + b"x" * 1018, headers={
            "content-type": "image/jpeg", "content-range": "bytes 0-1023/241034"}), "começa"),
        (httpx.Response(206, content=JPEG, headers={"content-type": "image/jpeg",
                        "content-range": "bytes 0-1023/2000"}), "pequena"),
        (httpx.Response(206, content=JPEG, headers={"content-type": "image/jpeg"}), "tamanho"),
    ],
)
def test_foto_recusa_o_que_nao_e_uma_foto_jpeg_de_tamanho_razoavel(resposta, trecho):
    r = p.check_foto(client_foto(lambda request: resposta), 1, FOTO.format(1))
    assert not r["ok"] and trecho in r["motivo"]


def test_foto_recusa_endereco_de_outro_codigo_ou_de_fora_do_senado():
    r = p.check_foto(client_foto(resposta_ok), 2, "http://www.senado.leg.br/x.jpg")
    assert not r["ok"] and "código" in r["motivo"]

    def de_fora(request):
        return httpx.Response(206, content=JPEG, headers={
            "content-type": "image/jpeg", "content-range": "bytes 0-1023/241034"})

    r = p.check_foto(client_foto(de_fora), 1, "https://outro.exemplo.com/fotos/1")
    assert not r["ok"] and "não é o do Senado" in r["motivo"]


def test_foto_falha_de_rede_vira_motivo_e_erro_5xx_tenta_de_novo():
    def cai(request):
        raise httpx.ConnectError("sem rede")

    assert "rede" in p.check_foto(client_foto(cai), 1, FOTO.format(1))["motivo"]
    chamadas = []

    def instavel(request):
        chamadas.append(1)
        return httpx.Response(503) if len(chamadas) == 1 else resposta_ok(request)

    assert p.check_foto(client_foto(instavel), 1, FOTO.format(1))["ok"]


# --- comparação -------------------------------------------------------------
def campos(api=API1, legis=LEGIS1, foto=FOTO_OK):
    return {f.campo: f for f in p.compare_perfil(1, api, legis, foto)}


def test_tudo_igual_prova_foto_e_mandato():
    f = campos()
    assert f["foto"].resultado == v.IDENTICAL and f["foto"].valor == FOTO.format(1)
    assert f["mandato"].resultado == v.IDENTICAL and f["mandato"].valor == "2023-02-01/2031-01-31"


def test_nome_inteiro_dentro_do_outro_vale_mas_nome_diferente_nao():
    assert p.same_name("Nelsinho Trad", "NELSINHO TRAD FILHO")
    assert p.same_name("Esperidião Amin", "ESPERIDIAO AMIN")
    assert not p.same_name("Ana", "Anabela")
    assert not p.same_name("Ana Paula", "Paula")


@pytest.mark.parametrize(
    ("mudanca", "trecho"),
    [({"nomeParlamentar": "OUTRO"}, "nome"), ({"uf": "BA"}, "UF"), ({"partido": "P9"}, "partido")],
)
def test_identidade_diferente_esconde_foto_e_mandato(mudanca, trecho):
    f = campos(api={**API1, **mudanca})
    assert {x.resultado for x in f.values()} == {v.UNEXPLAINED}
    assert trecho in f["foto"].detalhe and f["foto"].valor is None


def test_mandato_com_anos_diferentes_ou_fora_do_formato_fica_sem_explicacao():
    assert campos(api={**API1, "mandato": "2023 / 2027"})["mandato"].resultado == v.UNEXPLAINED
    assert campos(api={**API1, "mandato": "-"})["mandato"].resultado == v.UNEXPLAINED
    # a foto não depende do mandato
    assert campos(api={**API1, "mandato": "-"})["foto"].resultado == v.IDENTICAL


def test_foto_com_problema_nao_derruba_o_mandato():
    f = campos(foto={"url": "x", "ok": False, "motivo": "resposta 404"})
    assert f["foto"].resultado == v.UNEXPLAINED and f["foto"].detalhe == "resposta 404"
    assert f["mandato"].resultado == v.IDENTICAL
    assert campos(foto=None)["foto"].resultado == v.UNEXPLAINED


def test_senador_fora_da_lista_legislativa_fica_sem_explicacao():
    r = p.compare_perfil(1, API1, None, None)
    assert {x.resultado for x in r} == {v.UNEXPLAINED}


# --- freio de segurança -----------------------------------------------------
def shown(fields, name):
    return sum(f.exibir for f in fields if f.campo == name)


def test_ate_5_por_cento_de_falhas_ainda_aparece_e_acima_some_para_todos():
    base = [p.Field(i, "foto", v.IDENTICAL, f"u{i}") for i in range(1, 82)]
    com_4 = [p.Field(i, "foto", v.UNEXPLAINED) if i <= 4 else f for i, f in enumerate(base, 1)]
    assert shown(p.apply_release_rule(com_4), "foto") == 77
    com_5 = [p.Field(i, "foto", v.UNEXPLAINED) if i <= 5 else f for i, f in enumerate(base, 1)]
    assert shown(p.apply_release_rule(com_5), "foto") == 0
    assert all(f.valor is None for f in p.apply_release_rule(com_5))


def test_cada_campo_tem_o_seu_freio():
    fields = [p.Field(i, "foto", v.UNEXPLAINED) for i in range(1, 11)]
    fields += [p.Field(i, "mandato", v.IDENTICAL, "a/b") for i in range(1, 11)]
    out = p.apply_release_rule(fields)
    assert shown(out, "foto") == 0 and shown(out, "mandato") == 10


# --- ponta a ponta ----------------------------------------------------------
def setup(tmp_path, *, listed_at="2026-11-23T09:00:00-03:00", reference="2026-11-23"):
    database = tmp_path / "limpo.sqlite"
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.execute("CREATE TABLE senadores (cod_senador INTEGER, nome TEXT)")
        connection.execute("INSERT INTO senadores VALUES (1, 'FULANO')")
        connection.execute("CREATE TABLE metadados (chave TEXT PRIMARY KEY, valor TEXT)")
        connection.execute("INSERT INTO metadados VALUES ('data_referencia', ?)", (reference,))
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "senadores_atuais.json").write_text(json.dumps({"data": [API1]}), encoding="utf-8")
    (raw / "coleta.json").write_text(
        json.dumps({"senadores": listed_at, "despesas": {}}), encoding="utf-8"
    )
    return raw, database


def client_completo(lista):
    def handler(request):
        if request.url.path.endswith("/senador/lista/atual"):
            return httpx.Response(200, json=lista)
        return resposta_ok(request)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_run_confere_grava_so_o_provado_e_guarda_a_lista_como_o_senado_publica(tmp_path):
    raw, database = setup(tmp_path)
    fields, extras = p.run(raw, database, client_completo(payload(item(1, "Fulano"))), TODAY,
                           clock=lambda: NOW)
    assert {f.campo: f.resultado for f in fields} == {"foto": v.IDENTICAL, "mandato": v.IDENTICAL}
    assert extras == []
    with closing(sqlite3.connect(database)) as connection:
        assert connection.execute("SELECT * FROM perfil").fetchall() == [
            (1, FOTO.format(1), "2023-02-01", "2031-01-31")
        ]
        assert connection.execute(
            "SELECT nome, identicos, sem_explicacao FROM verificacoes ORDER BY nome"
        ).fetchall() == [("perfil_foto", 1, 0), ("perfil_mandato", 1, 0)]
    assert json.loads((raw / "coleta.json").read_text(encoding="utf-8"))["perfil"].startswith(
        "2026-11-23T10:00:00"
    )
    assert (raw / "perfil" / "legis_lista_atual.json").exists()


def test_run_avisa_de_quem_so_esta_na_lista_legislativa(tmp_path):
    raw, database = setup(tmp_path)
    _fields, extras = p.run(raw, database, client_completo(payload(item(1, "Fulano"), item(9))),
                            TODAY, clock=lambda: NOW)
    assert extras == [9]


def test_run_nao_apaga_outras_verificacoes(tmp_path):
    raw, database = setup(tmp_path)
    with closing(sqlite3.connect(database)) as connection, connection:
        v.ensure_verificacoes_table(connection)
        connection.execute("INSERT INTO verificacoes VALUES ('cota', 2026, 1, 0, 0, 'x')")
    p.run(raw, database, client_completo(payload(item(1, "Fulano"))), TODAY, clock=lambda: NOW)
    with closing(sqlite3.connect(database)) as connection:
        assert connection.execute("SELECT count(*) FROM verificacoes").fetchone() == (3,)


def test_run_recusa_dados_de_outro_dia_e_nao_baixa_nada(tmp_path):
    raw, database = setup(tmp_path, listed_at="2026-11-22T09:00:00-03:00")

    def nao_deve_baixar(request):
        raise AssertionError("não devia baixar nada")

    with pytest.raises(v.VerificacaoError, match="mesma foto"):
        p.run(raw, database, httpx.Client(transport=httpx.MockTransport(nao_deve_baixar)), TODAY)


def test_run_pede_a_limpeza_quando_nao_ha_banco(tmp_path):
    with pytest.raises(v.VerificacaoError, match="limpeza"):
        p.run(tmp_path, tmp_path / "nao-existe.sqlite", client_completo(payload()), TODAY)
