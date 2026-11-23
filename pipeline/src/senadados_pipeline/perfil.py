"""Perfil do senador: a foto oficial e o mandato, provados por duas listas do Senado (D045).

A lista de senadores em exercício da API administrativa (a que a coleta grava) e a da API
legislativa devem concordar sobre quem é cada senador. Para cada um, a verificação confere:

- **identidade:** o mesmo código nas duas listas e o mesmo nome (igual, ou um inteiro dentro do
  outro, palavra por palavra), UF e partido. Sem isso, nem a foto nem o mandato aparecem;
- **mandato:** o ano em que começa e o ano em que termina são iguais nas duas listas;
- **foto:** o endereço da lista legislativa, já com os redirecionamentos resolvidos, termina no
  código do senador, está em `https://legis.senado.leg.br` e responde com uma imagem JPEG de
  tamanho razoável. Só os primeiros 1.024 bytes de cada foto são baixados.

Cada campo tem o resultado `identico` ou `sem_explicacao` (não há diferença conhecida entre as
listas que se possa explicar).

Exibição (D037): foto e mandato são dados descritivos. Cada um aparece para quem foi provado e
tem o próprio freio de segurança (mais de 5% de falhas esconde o campo de todos). Só o valor
provado vai para a tabela `perfil`; o que não foi provado fica vazio. Um senador que só está na
lista administrativa fica sem explicação; um que só está na legislativa é apenas avisado na saída.

Prova consistência entre listas do Senado: não prova que a foto é mesmo da pessoa, e não é
auditoria (D027, D045).
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from dataclasses import dataclass, replace
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit

import httpx

from senadados_pipeline.coleta import (
    ColetaError,
    get_json,
    now_local,
    read_manifest,
    write_json,
)
from senadados_pipeline.config import CLEAN_DB, LEGIS_URL, MAX_FAILURE_RATE, RAW_DIR, USER_AGENT
from senadados_pipeline.contato import load_api
from senadados_pipeline.equipe import _word_prefix, normalize
from senadados_pipeline.verificacao import (
    IDENTICAL,
    UNEXPLAINED,
    VerificacaoError,
    check_snapshot,
    ensure_verificacoes_table,
)

MANIFEST_KEY = "perfil"
FIELDS = ("foto", "mandato")
CREDITO = "Foto oficial publicada pelo Senado Federal"

PHOTO_HOST = "legis.senado.leg.br"
PHOTO_PEEK = 1024  # bytes pedidos de cada foto
# Tamanho mínimo aceito para a foto: um julgamento, e não um número pesquisado. A menor das 81
# fotos medidas em 19/11/2026 tem 78 KB; um arquivo bem menor é provavelmente uma imagem substituta.
MIN_PHOTO_BYTES = 10_000
JPEG_START = b"\xff\xd8\xff"

API_MANDATO = re.compile(r"^(\d{4}) / (\d{4})$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ---------------------------------------------------------------------------
# Leitura da lista legislativa
# ---------------------------------------------------------------------------
def parse_legis(payload) -> dict[int, dict]:
    """Código -> nome, UF, partido, endereço da foto e as duas datas do mandato.

    Para o mandato, o início é o da primeira legislatura e o fim, o da última que a lista traz.
    Estrutura inesperada para tudo, em vez de devolver dado errado (falhar fechado).
    """
    try:
        lista = payload["ListaParlamentarEmExercicio"]["Parlamentares"]["Parlamentar"]
        if not isinstance(lista, list) or not lista:
            raise ColetaError("a lista legislativa veio vazia")
        out: dict[int, dict] = {}
        for item in lista:
            ident = item["IdentificacaoParlamentar"]
            mandato = item["Mandato"]
            primeira = mandato["PrimeiraLegislaturaDoMandato"]
            ultima = mandato.get("SegundaLegislaturaDoMandato") or primeira
            code = int(ident["CodigoParlamentar"])
            if code in out:
                raise ColetaError(f"senador {code} repetido na lista legislativa")
            record = {
                "nome": str(ident["NomeParlamentar"]),
                "uf": str(ident["UfParlamentar"]),
                "partido": str(ident["SiglaPartidoParlamentar"]),
                "foto_url": str(ident["UrlFotoParlamentar"]),
                "inicio": str(primeira["DataInicio"]),
                "fim": str(ultima["DataFim"]),
            }
            for chave in ("inicio", "fim"):
                if not ISO_DATE.match(record[chave]):
                    raise ColetaError(f"data de mandato em formato inesperado: {record[chave]!r}")
            out[code] = record
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        raise ColetaError(f"a lista legislativa veio em formato inesperado: {error!r}") from error
    return out


# ---------------------------------------------------------------------------
# Conferência da foto (só o começo de cada arquivo)
# ---------------------------------------------------------------------------
def _total_bytes(response: httpx.Response) -> int | None:
    """O tamanho total do arquivo, pelo `Content-Range` (resposta parcial) ou `Content-Length`."""
    faixa = response.headers.get("content-range", "")
    achou = re.match(r"^bytes \d+-\d+/(\d+)$", faixa)
    if achou:
        return int(achou.group(1))
    if response.status_code == 200 and response.headers.get("content-length", "").isdigit():
        return int(response.headers["content-length"])
    return None


def check_foto(client: httpx.Client, code: int, url: str, *, attempts: int = 2) -> dict:
    """Confere a foto de um senador. Devolve `{"url": endereço final, "ok": bool, "motivo": ...}`.

    Baixa só os primeiros bytes. A falha de um senador vira motivo, e não derruba os outros.
    """
    headers = {"Range": f"bytes=0-{PHOTO_PEEK - 1}", "Accept": "image/jpeg,*/*;q=0.5"}
    ultimo: str = "falha de rede"
    for tentativa in range(1, attempts + 1):
        try:
            with client.stream("GET", url, headers=headers, follow_redirects=True) as resposta:
                final = str(resposta.url)
                if resposta.status_code >= 500 and tentativa < attempts:
                    ultimo = f"o servidor respondeu {resposta.status_code}"
                    continue
                if resposta.status_code not in (200, 206):
                    return {"url": final, "ok": False, "motivo": f"resposta {resposta.status_code}"}
                inicio = next(resposta.iter_bytes(PHOTO_PEEK), b"")
                total = _total_bytes(resposta)
                tipo = resposta.headers.get("content-type", "")
        except httpx.HTTPError as erro:
            ultimo = f"falha de rede ({type(erro).__name__})"
            continue
        partes = urlsplit(final)
        if partes.scheme != "https" or partes.hostname != PHOTO_HOST:
            return {"url": final, "ok": False, "motivo": "o endereço final não é o do Senado"}
        if partes.path.rstrip("/").rsplit("/", 1)[-1] != str(code):
            return {"url": final, "ok": False, "motivo": "o endereço não termina no código"}
        if not tipo.lower().startswith("image/jpeg"):
            return {"url": final, "ok": False, "motivo": f"tipo {tipo or 'ausente'}, não JPEG"}
        if not inicio.startswith(JPEG_START):
            return {"url": final, "ok": False, "motivo": "o arquivo não começa como um JPEG"}
        if total is None:
            return {"url": final, "ok": False, "motivo": "o tamanho da imagem não é informado"}
        if total < MIN_PHOTO_BYTES:
            return {"url": final, "ok": False, "motivo": "a imagem é pequena demais"}
        return {"url": final, "ok": True, "motivo": None}
    return {"url": url, "ok": False, "motivo": ultimo}


def check_fotos(client: httpx.Client, legis: dict[int, dict], codes, *, workers: int = 8) -> dict:
    """Código -> resultado de `check_foto`, só para quem está nas duas listas."""
    alvo = [code for code in sorted(codes) if code in legis]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        feitos = list(pool.map(lambda c: check_foto(client, c, legis[c]["foto_url"]), alvo))
    return dict(zip(alvo, feitos, strict=True))


# ---------------------------------------------------------------------------
# Coleta
# ---------------------------------------------------------------------------
def collect_legis(client: httpx.Client, raw_dir: Path, clock=now_local) -> dict[int, dict]:
    """Baixa a lista legislativa, grava como o Senado publica e registra a hora."""
    payload = get_json(client, f"{LEGIS_URL}/senador/lista/atual")
    legis = parse_legis(payload)
    write_json(raw_dir / "perfil" / "legis_lista_atual.json", payload)
    manifest = read_manifest(raw_dir)
    manifest[MANIFEST_KEY] = clock().isoformat(timespec="seconds")
    write_json(raw_dir / "coleta.json", manifest)
    return legis


# ---------------------------------------------------------------------------
# Comparação
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Field:
    cod_senador: int
    campo: str
    resultado: str
    valor: str | None = None  # o valor que pode aparecer (só se não houver freio)
    detalhe: str | None = None
    exibir: bool = False


def same_name(a: str, b: str) -> bool:
    """Nome igual, ou um inteiro dentro do outro em palavras ("Nelsinho Trad" e "... Filho")."""
    x, y = normalize(a), normalize(b)
    return _word_prefix(x, y) or _word_prefix(y, x)


def identity_problems(api: dict, legis: dict) -> list[str]:
    problems = []
    if not same_name(api.get("nomeParlamentar", ""), legis["nome"]):
        problems.append("o nome difere")
    if api.get("uf") != legis["uf"]:
        problems.append("a UF difere")
    if api.get("partido") != legis["partido"]:
        problems.append("o partido difere")
    return problems


def compare_perfil(code: int, api: dict | None, legis: dict | None, foto: dict | None):
    """Os dois campos de um senador."""
    if api is None or legis is None:
        why = "o senador não está na lista legislativa" if legis is None else "senador sem dados"
        return [Field(code, name, UNEXPLAINED, detalhe=why) for name in FIELDS]
    problems = identity_problems(api, legis)
    if problems:
        why = "as listas do Senado não concordam: " + ", ".join(problems)
        return [Field(code, name, UNEXPLAINED, detalhe=why) for name in FIELDS]

    achou = API_MANDATO.match(str(api.get("mandato", "")))
    if not achou:
        mandato = Field(
            code, "mandato", UNEXPLAINED, detalhe="o mandato da API está fora do formato"
        )
    elif (achou.group(1), achou.group(2)) != (legis["inicio"][:4], legis["fim"][:4]):
        mandato = Field(code, "mandato", UNEXPLAINED, detalhe="os anos do mandato diferem")
    else:
        mandato = Field(code, "mandato", IDENTICAL, valor=f"{legis['inicio']}/{legis['fim']}")

    if foto is None:
        foto_campo = Field(code, "foto", UNEXPLAINED, detalhe="a foto não foi conferida")
    elif not foto["ok"]:
        foto_campo = Field(code, "foto", UNEXPLAINED, detalhe=foto["motivo"])
    else:
        foto_campo = Field(code, "foto", IDENTICAL, valor=foto["url"])
    return [foto_campo, mandato]


def apply_release_rule(fields: list[Field]) -> list[Field]:
    """Define o que aparece, campo a campo, com o freio de segurança de cada campo (D037)."""
    out: list[Field] = []
    for name in FIELDS:
        group = [f for f in fields if f.campo == name]
        failures = sum(f.resultado == UNEXPLAINED for f in group)
        braked = not group or failures / len(group) > MAX_FAILURE_RATE
        for f in group:
            ok = f.resultado == IDENTICAL and f.valor is not None and not braked
            out.append(replace(f, exibir=ok, valor=f.valor if ok else None))
    return out


def verify_perfil(
    senators: dict[int, str], api: dict, legis: dict, fotos: dict
) -> list[Field]:
    fields: list[Field] = []
    for code in sorted(senators):
        fields += compare_perfil(code, api.get(code), legis.get(code), fotos.get(code))
    return apply_release_rule(fields)


# ---------------------------------------------------------------------------
# Banco local
# ---------------------------------------------------------------------------
def write_results(
    connection: sqlite3.Connection, fields: list[Field], year: int, when: datetime
) -> None:
    connection.execute("DROP TABLE IF EXISTS verificacao_perfil")
    connection.execute("DROP TABLE IF EXISTS perfil")
    connection.execute(
        "CREATE TABLE verificacao_perfil (cod_senador INTEGER, campo TEXT, resultado TEXT, "
        "detalhe TEXT, exibir INTEGER, PRIMARY KEY (cod_senador, campo))"
    )
    connection.execute(
        "CREATE TABLE perfil (cod_senador INTEGER PRIMARY KEY, foto_url TEXT, "
        "mandato_inicio TEXT, mandato_fim TEXT)"
    )
    connection.executemany(
        "INSERT INTO verificacao_perfil VALUES (?, ?, ?, ?, ?)",
        [(f.cod_senador, f.campo, f.resultado, f.detalhe, int(f.exibir)) for f in fields],
    )
    by_senator: dict[int, dict[str, str | None]] = {}
    for f in fields:
        by_senator.setdefault(f.cod_senador, {})[f.campo] = f.valor
    rows = []
    for code, values in by_senator.items():
        inicio, fim = (values.get("mandato") or "/").split("/")
        if values.get("foto") or values.get("mandato"):
            rows.append((code, values.get("foto"), inicio or None, fim or None))
    connection.executemany("INSERT INTO perfil VALUES (?, ?, ?, ?)", rows)
    ensure_verificacoes_table(connection)
    connection.execute("DELETE FROM verificacoes WHERE nome LIKE 'perfil_%'")
    stamp = when.isoformat(timespec="seconds")
    for name in FIELDS:
        kinds = Counter(f.resultado for f in fields if f.campo == name)
        connection.execute(
            "INSERT INTO verificacoes VALUES (?, ?, ?, ?, ?, ?)",
            (f"perfil_{name}", year, kinds[IDENTICAL], 0, kinds[UNEXPLAINED], stamp),
        )


def run(
    raw_dir: Path, database: Path, client: httpx.Client, today: date, clock=now_local
) -> tuple[list[Field], list[int]]:
    """Baixa a lista legislativa agora, confere as fotos e compara com a lista da coleta.

    Devolve os resultados e os códigos que só a lista legislativa traz (só para avisar).
    """
    if not database.exists():
        raise VerificacaoError(f"falta {database}; rode a limpeza antes")
    with closing(sqlite3.connect(database)) as connection:
        check_snapshot(connection, raw_dir, [], today)
        senators = dict(connection.execute("SELECT cod_senador, nome FROM senadores"))
        api = load_api(raw_dir)

        legis = collect_legis(client, raw_dir, clock)
        fotos = check_fotos(client, legis, senators)
        fields = verify_perfil(senators, api, legis, fotos)
        with connection:
            write_results(connection, fields, clock().year, clock())
    return fields, sorted(set(legis) - set(senators))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Confere a foto e o mandato de cada senador.")
    parser.add_argument("--raw", type=Path, default=RAW_DIR, help="pasta dos dados coletados")
    parser.add_argument("--banco", type=Path, default=CLEAN_DB, help="banco SQLite limpo")
    args = parser.parse_args(argv)

    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    try:
        with httpx.Client(timeout=60.0, headers=headers) as client:
            fields, extras = run(args.raw, args.banco, client, date.today())
    except (VerificacaoError, ColetaError) as error:
        print(f"erro: {error}", file=sys.stderr)
        return 1

    for name in FIELDS:
        group = [f for f in fields if f.campo == name]
        kinds = Counter(f.resultado for f in group)
        shown = sum(f.exibir for f in group)
        print(f"{name}: {kinds[IDENTICAL]} idênticos, {kinds[UNEXPLAINED]} sem explicação; "
              f"aparece para {shown}")
    for f in fields:
        if f.resultado == UNEXPLAINED:
            print(f"  senador {f.cod_senador} ({f.campo}): {f.detalhe}")
    if extras:
        print(f"aviso: só a lista legislativa traz os códigos {extras}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
