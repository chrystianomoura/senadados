"""Cópias reduzidas das fotos oficiais dos senadores, para o site carregar mais rápido (D047).

As fotos do Senado têm 480 por 600 pontos, 287 KB em média e até 1,4 MB, e o site mostra a maioria
delas com uns 170 pontos de largura. Este passo baixa a foto de cada senador cuja foto foi
provada
pela verificação do perfil (D045) e grava duas cópias em WebP, sem nenhum metadado:

- `{código}-p.webp`: 240 por 300, para a lista e o mosaico da home;
- `{código}-g.webp`: 480 por 600, para o cartão do perfil.

As imagens são do Senado e continuam com o crédito "Foto oficial publicada pelo Senado Federal". O
site usa a cópia e, se ela faltar, cai no endereço oficial (D045). As cópias ficam em
`web/public/fotos/` (fora do git, como os dados) e **a pasta inteira é refeita a cada execução**,
então a foto de quem saiu da lista não fica para trás (D026).

Só roda se a verificação do perfil for de hoje. Uma foto que não baixa ou não abre como JPEG é
pulada e avisada; o site continua mostrando o endereço oficial dela.
"""

from __future__ import annotations

import argparse
import io
import shutil
import sqlite3
import sys
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import date
from pathlib import Path

import httpx
from PIL import Image, ImageOps, UnidentifiedImageError

from senadados_pipeline.coleta import ColetaError
from senadados_pipeline.config import CLEAN_DB, ROOT, USER_AGENT
from senadados_pipeline.perfil import JPEG_START, MIN_PHOTO_BYTES
from senadados_pipeline.verificacao import VerificacaoError, local_date

SIZES = {"p": (240, 300), "g": (480, 600)}
QUALITY = 78  # um julgamento: abaixo disso o rosto começa a ficar com blocos
OUT_DEFAULT = ROOT / "web" / "public" / "fotos"
OUT_NAME = "fotos"  # o único nome de pasta que este passo aceita apagar e refazer


def proven_photos(connection: sqlite3.Connection, today: date) -> dict[int, str]:
    """Código -> endereço da foto, só de quem teve a foto provada hoje."""
    row = connection.execute(
        "SELECT verificado_em FROM verificacoes WHERE nome = 'perfil_foto'"
    ).fetchone()
    if row is None:
        raise VerificacaoError("falta a verificação do perfil; rode `perfil` antes")
    if local_date(row[0]) != today:
        raise VerificacaoError(
            f"a verificação do perfil é de {local_date(row[0])}, e hoje é {today}; "
            "rode `perfil` de novo"
        )
    return dict(
        connection.execute(
            "SELECT cod_senador, foto_url FROM perfil WHERE foto_url IS NOT NULL ORDER BY 1"
        )
    )


def fetch_photo(client: httpx.Client, url: str) -> bytes:
    """Baixa a foto inteira. Recusa o que não parece uma foto JPEG de tamanho razoável."""
    try:
        response = client.get(url, follow_redirects=True)
    except httpx.HTTPError as error:
        raise ColetaError(f"falha de rede ({type(error).__name__})") from error
    if response.status_code != 200:
        raise ColetaError(f"resposta {response.status_code}")
    data = response.content
    if not data.startswith(JPEG_START):
        raise ColetaError("o arquivo não começa como um JPEG")
    if len(data) < MIN_PHOTO_BYTES:
        raise ColetaError("a imagem é pequena demais")
    return data


def make_copies(data: bytes) -> dict[str, bytes]:
    """As cópias em WebP, cortadas na proporção 4 por 5 e sem metadado nenhum."""
    try:
        with Image.open(io.BytesIO(data)) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
    except (UnidentifiedImageError, OSError) as error:
        raise ColetaError("não foi possível abrir a imagem") from error
    copies: dict[str, bytes] = {}
    for name, size in SIZES.items():
        out = io.BytesIO()
        ImageOps.fit(image, size, Image.Resampling.LANCZOS).save(
            out, "WEBP", quality=QUALITY, method=6
        )
        copies[name] = out.getvalue()
    return copies


def build(
    client: httpx.Client, proven: dict[int, str], *, workers: int = 8
) -> tuple[dict[int, dict[str, bytes]], dict[int, str]]:
    """Cópias de cada foto, e o motivo de cada uma que ficou de fora."""

    def one(item: tuple[int, str]):
        code, url = item
        try:
            return code, make_copies(fetch_photo(client, url)), None
        except ColetaError as error:
            return code, None, str(error)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(one, sorted(proven.items())))
    copies = {code: made for code, made, _ in results if made is not None}
    failed = {code: why for code, made, why in results if made is None}
    return copies, failed


def write_folder(out: Path, copies: dict[int, dict[str, bytes]]) -> int:
    """Grava numa pasta temporária e a troca pela de saída. Devolve quantos arquivos gerou."""
    if out.name != OUT_NAME:
        raise VerificacaoError(
            f"por segurança, só refaço uma pasta chamada '{OUT_NAME}' (recebi '{out.name}')"
        )
    temp = out.with_name(out.name + ".tmp")
    if temp.exists():
        shutil.rmtree(temp)
    try:
        temp.mkdir(parents=True)
        for code, by_size in copies.items():
            for name, data in by_size.items():
                (temp / f"{code}-{name}.webp").write_bytes(data)
        if out.exists():
            shutil.rmtree(out)
        temp.replace(out)
    finally:
        if temp.exists():
            shutil.rmtree(temp)
    return sum(len(by_size) for by_size in copies.values())


def run(database: Path, out: Path, client: httpx.Client, today: date):
    if not database.exists():
        raise VerificacaoError(f"falta {database}; rode a limpeza antes")
    with closing(sqlite3.connect(database)) as connection:
        proven = proven_photos(connection, today)
    copies, failed = build(client, proven)
    files = write_folder(out, copies)
    return files, failed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gera as cópias reduzidas das fotos oficiais.")
    parser.add_argument("--banco", type=Path, default=CLEAN_DB, help="banco SQLite limpo")
    parser.add_argument("--saida", type=Path, default=OUT_DEFAULT, help="pasta de saída")
    args = parser.parse_args(argv)
    try:
        with httpx.Client(timeout=120.0, headers={"User-Agent": USER_AGENT}) as client:
            files, failed = run(args.banco, args.saida, client, date.today())
    except VerificacaoError as error:
        print(f"erro: {error}", file=sys.stderr)
        return 1
    megabytes = sum(f.stat().st_size for f in args.saida.iterdir()) / 1e6
    print(f"{files} arquivos gravados em {args.saida} ({megabytes:.1f} MB)")
    for code, why in sorted(failed.items()):
        print(f"  senador {code}: ficou sem cópia ({why})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
