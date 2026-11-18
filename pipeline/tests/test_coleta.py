import json
from datetime import UTC, datetime

import httpx
import pytest

from senadados_pipeline import coleta

SENADORES = {
    "statusCode": 200,
    "msg": "ok",
    "data": [
        {"codigoParlamentar": 1, "nomeParlamentar": "FULANA"},
        {"codigoParlamentar": 2, "nomeParlamentar": "BELTRANO"},
    ],
}

# 1 e 2 estão em exercício; 99 saiu do mandato e não pode ser guardado (D026).
DESPESAS = [
    {"id": 10, "codSenador": 1, "valorReembolsado": 10.0},
    {"id": 11, "codSenador": 99, "valorReembolsado": 20.0},
    {"id": 12, "codSenador": 2, "valorReembolsado": 30.0},
]


def make_client(routes: dict, calls: list | None = None) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        if calls is not None:
            calls.append(request.url.path)
        body = routes.get(request.url.path)
        if body is None:
            return httpx.Response(404)
        return httpx.Response(200, json=body)

    return httpx.Client(
        base_url="https://example.test/api/v1", transport=httpx.MockTransport(handler)
    )


ROUTES = {
    "/api/v1/senadores": SENADORES,
    "/api/v1/senadores/despesas_ceaps/2024": DESPESAS,
}


def test_grava_so_despesas_de_quem_esta_em_exercicio(tmp_path):
    client = make_client(ROUTES)
    coleta.collect(client, tmp_path, [2024], log=lambda _: None)

    saved = json.loads((tmp_path / "api" / "ceaps_2024.json").read_text(encoding="utf-8"))
    assert [row["id"] for row in saved] == [10, 12]


def test_grava_a_lista_como_o_senado_publica(tmp_path):
    client = make_client(ROUTES)
    coleta.collect(client, tmp_path, [2024], log=lambda _: None)

    saved = json.loads((tmp_path / "senadores_atuais.json").read_text(encoding="utf-8"))
    assert saved == SENADORES


def test_registra_quando_cada_arquivo_foi_baixado(tmp_path):
    moment = datetime(2026, 11, 18, 12, 30, tzinfo=UTC)
    coleta.collect(make_client(ROUTES), tmp_path, [2024], log=lambda _: None, clock=lambda: moment)

    manifest = coleta.read_manifest(tmp_path)
    assert manifest == {
        "senadores": "2026-11-18T12:30:00+00:00",
        "despesas": {"2024": "2026-11-18T12:30:00+00:00"},
    }


def test_manifesto_nao_muda_para_arquivo_pulado(tmp_path):
    first = datetime(2026, 11, 18, 12, 0, tzinfo=UTC)
    later = datetime(2026, 11, 19, 12, 0, tzinfo=UTC)
    coleta.collect(make_client(ROUTES), tmp_path, [2024], log=lambda _: None, clock=lambda: first)
    coleta.collect(make_client(ROUTES), tmp_path, [2024], log=lambda _: None, clock=lambda: later)

    assert coleta.read_manifest(tmp_path)["despesas"] == {"2024": "2026-11-18T12:00:00+00:00"}


def test_manifesto_vazio_quando_nao_houve_coleta(tmp_path):
    assert coleta.read_manifest(tmp_path) == {"senadores": None, "despesas": {}}


def test_nao_sobrescreve_arquivo_existente(tmp_path):
    existing = tmp_path / "api" / "ceaps_2024.json"
    existing.parent.mkdir(parents=True)
    existing.write_text("[]", encoding="utf-8")

    result = coleta.collect(make_client(ROUTES), tmp_path, [2024], log=lambda _: None)

    assert existing.read_text(encoding="utf-8") == "[]"
    assert existing in result["skipped"]


def test_sobrescreve_quando_pedido(tmp_path):
    existing = tmp_path / "api" / "ceaps_2024.json"
    existing.parent.mkdir(parents=True)
    existing.write_text("[]", encoding="utf-8")

    coleta.collect(make_client(ROUTES), tmp_path, [2024], overwrite=True, log=lambda _: None)

    assert len(json.loads(existing.read_text(encoding="utf-8"))) == 2


def test_falha_se_a_lista_vier_em_formato_inesperado(tmp_path):
    client = make_client({"/api/v1/senadores": [{"codigoParlamentar": 1}]})
    with pytest.raises(coleta.ColetaError):
        coleta.collect(client, tmp_path, [2024], log=lambda _: None)


def test_falha_se_a_lista_vier_vazia(tmp_path):
    client = make_client({"/api/v1/senadores": {"data": []}})
    with pytest.raises(coleta.ColetaError):
        coleta.collect(client, tmp_path, [2024], log=lambda _: None)


def test_falha_se_as_despesas_vierem_em_formato_inesperado(tmp_path):
    routes = {**ROUTES, "/api/v1/senadores/despesas_ceaps/2024": {"data": DESPESAS}}
    with pytest.raises(coleta.ColetaError):
        coleta.collect(make_client(routes), tmp_path, [2024], log=lambda _: None)


def test_falha_se_a_despesa_nao_tiver_codigo_do_senador(tmp_path):
    routes = {**ROUTES, "/api/v1/senadores/despesas_ceaps/2024": [{"id": 1}]}
    with pytest.raises(coleta.ColetaError):
        coleta.collect(make_client(routes), tmp_path, [2024], log=lambda _: None)


def test_nao_deixa_arquivo_pela_metade_se_a_coleta_falhar(tmp_path):
    routes = {**ROUTES, "/api/v1/senadores/despesas_ceaps/2024": {"erro": True}}
    with pytest.raises(coleta.ColetaError):
        coleta.collect(make_client(routes), tmp_path, [2024], log=lambda _: None)

    assert not (tmp_path / "api" / "ceaps_2024.json").exists()
    assert not list(tmp_path.rglob("*.tmp"))


def test_tenta_de_novo_quando_a_rede_falha(monkeypatch):
    monkeypatch.setattr(coleta.time, "sleep", lambda _: None)
    attempts = []

    def handler(_request: httpx.Request) -> httpx.Response:
        attempts.append(1)
        if len(attempts) < 3:
            return httpx.Response(503)
        return httpx.Response(200, json=[1])

    client = httpx.Client(base_url="https://example.test", transport=httpx.MockTransport(handler))
    assert coleta.get_json(client, "/x") == [1]
    assert len(attempts) == 3


def test_desiste_depois_de_varias_falhas(monkeypatch):
    monkeypatch.setattr(coleta.time, "sleep", lambda _: None)
    client = httpx.Client(
        base_url="https://example.test",
        transport=httpx.MockTransport(lambda _request: httpx.Response(503)),
    )
    with pytest.raises(coleta.ColetaError):
        coleta.get_json(client, "/x")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("2026", [2026]),
        ("2023-2025", [2023, 2024, 2025]),
        ("2010-2011,2008", [2008, 2010, 2011]),
    ],
)
def test_parse_years(text, expected):
    assert coleta.parse_years(text) == expected


@pytest.mark.parametrize("text", ["2007", "2030-2031", "2026-2024", "abc"])
def test_parse_years_recusa_valores_invalidos(text):
    with pytest.raises(ValueError):
        coleta.parse_years(text)


def test_nao_tenta_de_novo_quando_o_erro_nao_passa_sozinho(monkeypatch):
    monkeypatch.setattr(coleta.time, "sleep", lambda _: None)
    attempts = []

    def handler(_request: httpx.Request) -> httpx.Response:
        attempts.append(1)
        return httpx.Response(404)

    client = httpx.Client(base_url="https://example.test", transport=httpx.MockTransport(handler))
    with pytest.raises(coleta.ColetaError):
        coleta.get_json(client, "/x")
    assert len(attempts) == 1


def test_falha_se_um_senador_da_lista_nao_tiver_codigo(tmp_path):
    routes = {"/api/v1/senadores": {"data": [{"nomeParlamentar": "SEM CODIGO"}]}}
    with pytest.raises(coleta.ColetaError):
        coleta.collect(make_client(routes), tmp_path, [2024], log=lambda _: None)


def test_linha_de_comando_recusa_ano_invalido(capsys):
    assert coleta.main(["--anos", "2007"]) == 1
    assert "erro:" in capsys.readouterr().err
