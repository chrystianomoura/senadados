import io
import os
import sqlite3
from contextlib import closing
from datetime import date

import httpx
import pytest
from PIL import Image

from senadados_pipeline import fotos as f
from senadados_pipeline.coleta import ColetaError
from senadados_pipeline.verificacao import VerificacaoError

TODAY = date(2026, 11, 23)


def jpeg(width=480, height=600) -> bytes:
    """Uma foto de mentira, com ruído para passar do tamanho mínimo."""
    image = Image.frombytes("RGB", (width, height), os.urandom(width * height * 3))
    out = io.BytesIO()
    image.save(out, "JPEG", quality=90)
    return out.getvalue()


FOTO = jpeg()


def client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def ok(request):
    return httpx.Response(200, content=FOTO, headers={"content-type": "image/jpeg"})


# --- baixar -----------------------------------------------------------------
def test_fetch_devolve_a_foto():
    assert f.fetch_photo(client(ok), "https://x/1") == FOTO


@pytest.mark.parametrize(
    ("resposta", "trecho"),
    [
        (httpx.Response(404), "404"),
        (httpx.Response(200, content=b"<html>" + b"x" * 20000), "JPEG"),
        (httpx.Response(200, content=b"\xff\xd8\xff" + b"x" * 100), "pequena"),
    ],
)
def test_fetch_recusa_o_que_nao_e_uma_foto(resposta, trecho):
    with pytest.raises(ColetaError, match=trecho):
        f.fetch_photo(client(lambda request: resposta), "https://x/1")


def test_fetch_falha_de_rede_vira_erro_da_coleta():
    def cai(request):
        raise httpx.ConnectError("sem rede")

    with pytest.raises(ColetaError, match="rede"):
        f.fetch_photo(client(cai), "https://x/1")


# --- cópias -----------------------------------------------------------------
def test_copias_tem_o_tamanho_certo_sao_webp_e_bem_menores():
    copies = f.make_copies(FOTO)
    assert set(copies) == {"p", "g"}
    for name, size in f.SIZES.items():
        image = Image.open(io.BytesIO(copies[name]))
        assert image.format == "WEBP" and image.size == size
    # o ruído é o pior caso para compressão; ainda assim a cópia pequena não passa da original
    assert len(copies["p"]) < len(FOTO)


def test_copia_corta_na_proporcao_4_por_5_em_vez_de_esticar():
    image = Image.open(io.BytesIO(f.make_copies(jpeg(600, 600))["p"]))
    assert image.size == (240, 300)


def test_copia_nao_leva_metadado():
    source = Image.open(io.BytesIO(FOTO))
    exif = Image.Exif()
    exif[0x010E] = "descrição privada"
    out = io.BytesIO()
    source.save(out, "JPEG", exif=exif)
    for data in f.make_copies(out.getvalue()).values():
        image = Image.open(io.BytesIO(data))
        assert not image.getexif() and b"privada" not in data


def test_imagem_corrompida_vira_erro_da_coleta():
    quebrada = b"\xff\xd8\xff" + b"\x00" * 20000
    with pytest.raises(ColetaError, match="abrir"):
        f.make_copies(quebrada)


# --- montagem e gravação ----------------------------------------------------
def test_build_separa_o_que_deu_certo_do_que_falhou():
    def handler(request):
        return ok(request) if request.url.path.endswith("/1") else httpx.Response(404)

    copies, failed = f.build(client(handler), {1: "https://x/1", 2: "https://x/2"})
    assert set(copies) == {1} and failed == {2: "resposta 404"}


def test_write_folder_troca_a_pasta_inteira_e_nao_deixa_foto_de_quem_saiu(tmp_path):
    out = tmp_path / "fotos"
    out.mkdir()
    (out / "999-p.webp").write_bytes(b"velha")
    copies = {1: f.make_copies(FOTO)}
    assert f.write_folder(out, copies) == 2
    assert sorted(p.name for p in out.iterdir()) == ["1-g.webp", "1-p.webp"]
    assert not (tmp_path / "fotos.tmp").exists()


def test_write_folder_so_aceita_uma_pasta_chamada_fotos(tmp_path):
    alvo = tmp_path / "importante"
    alvo.mkdir()
    (alvo / "arquivo.txt").write_text("não apague")
    with pytest.raises(VerificacaoError, match="fotos"):
        f.write_folder(alvo, {})
    assert (alvo / "arquivo.txt").exists()


# --- ponta a ponta ----------------------------------------------------------
def banco(tmp_path, *, quando="2026-11-23T10:00:00-03:00"):
    database = tmp_path / "limpo.sqlite"
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.execute("CREATE TABLE perfil (cod_senador INTEGER, foto_url TEXT)")
        connection.executemany(
            "INSERT INTO perfil VALUES (?, ?)", [(1, "https://x/1"), (2, None)]
        )
        connection.execute(
            "CREATE TABLE verificacoes (nome TEXT, ano INTEGER, identicos INTEGER, "
            "explicados INTEGER, sem_explicacao INTEGER, verificado_em TEXT)"
        )
        connection.execute(
            "INSERT INTO verificacoes VALUES ('perfil_foto', 2026, 1, 0, 1, ?)", (quando,)
        )
    return database


def test_run_so_baixa_quem_teve_a_foto_provada(tmp_path):
    pedidos = []

    def handler(request):
        pedidos.append(str(request.url))
        return ok(request)

    files, failed = f.run(banco(tmp_path), tmp_path / "fotos", client(handler), TODAY)
    assert files == 2 and failed == {} and pedidos == ["https://x/1"]


def test_run_recusa_verificacao_de_outro_dia_e_nao_baixa_nada(tmp_path):
    def nao_deve_baixar(request):
        raise AssertionError("não devia baixar nada")

    database = banco(tmp_path, quando="2026-11-22T10:00:00-03:00")
    with pytest.raises(VerificacaoError, match="de novo"):
        f.run(database, tmp_path / "fotos", client(nao_deve_baixar), TODAY)
    assert not (tmp_path / "fotos").exists()


def test_run_pede_a_limpeza_quando_nao_ha_banco(tmp_path):
    with pytest.raises(VerificacaoError, match="limpeza"):
        f.run(tmp_path / "nao-existe.sqlite", tmp_path / "fotos", client(ok), TODAY)
