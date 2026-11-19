"""Aplica as migrações SQL de `pipeline/migracoes/`, em ordem, as que ainda não foram aplicadas.

Cada execução roda numa só transação. Por padrão é um ENSAIO: tudo é desfeito no fim e nada
é gravado. Só com `--apply` a transação é confirmada. O que já foi aplicado fica registrado
em `interno.migracoes`.

A conexão usa o dono do banco (`DATABASE_URL`): as migrações criam esquemas e tabelas, coisa
que os papéis de menor privilégio não fazem (D042).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from senadados_pipeline.banco import BancoError, conectar, host_de, url_do_ambiente
from senadados_pipeline.config import MIGRACOES_DIR

NOME_VALIDO = re.compile(r"^\d{3}_[a-z0-9_]+\.sql$")


class MigracaoError(Exception):
    """Alguma migração está fora do padrão ou falhou."""


def listar(diretorio: Path) -> list[Path]:
    """As migrações, em ordem. Nome fora do padrão `NNN_nome.sql` é erro, não é ignorado."""
    arquivos = sorted(p for p in diretorio.glob("*.sql"))
    for arquivo in arquivos:
        if not NOME_VALIDO.match(arquivo.name):
            raise MigracaoError(f"nome de migração fora do padrão NNN_nome.sql: {arquivo.name}")
    numeros = [int(a.name[:3]) for a in arquivos]
    if numeros != list(range(1, len(numeros) + 1)):
        raise MigracaoError(f"a numeração das migrações tem buraco ou repetição: {numeros}")
    return arquivos


def aplicadas(conn) -> set[str]:
    """Versões já aplicadas. Se a tabela de controle ainda não existe, nenhuma foi."""
    existe = conn.execute("SELECT to_regclass('interno.migracoes') IS NOT NULL").fetchone()[0]
    if not existe:
        return set()
    return {linha[0] for linha in conn.execute("SELECT versao FROM interno.migracoes")}


def aplicar(conn, arquivos: list[Path], log=print) -> None:
    for arquivo in arquivos:
        log(f"→ {arquivo.name}")
        conn.execute(arquivo.read_text(encoding="utf-8"))
        conn.execute("INSERT INTO interno.migracoes (versao) VALUES (%s)", (arquivo.name,))
        log("  executada sem erro")


def run(url: str, *, apply: bool, diretorio: Path = MIGRACOES_DIR, log=print) -> list[str]:
    """Devolve os nomes das migrações que rodaram (ou rodariam, no ensaio)."""
    arquivos = listar(diretorio)
    log(f"Banco alvo: {host_de(url)}")
    log("Modo: GRAVAR" if apply else "Modo: ensaio (tudo é desfeito no fim)")
    conn = conectar(url)
    try:
        ja = aplicadas(conn)
        pendentes = [a for a in arquivos if a.name not in ja]
        log(
            f"Migrações: {len(arquivos)} no total, {len(ja)} já aplicadas, "
            f"{len(pendentes)} pendentes."
        )
        aplicar(conn, pendentes, log)
        if apply:
            conn.commit()
            log("Gravado." if pendentes else "Nada a fazer.")
        else:
            conn.rollback()
            log("Ensaio concluído: nada foi gravado. Para gravar, rode com --apply.")
        return [a.name for a in pendentes]
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Aplica as migrações do banco (ensaio por padrão)."
    )
    parser.add_argument(
        "--apply", action="store_true", help="grava de verdade (sem isto, só ensaia)"
    )
    args = parser.parse_args(argv)
    try:
        run(url_do_ambiente("DATABASE_URL"), apply=args.apply)
    except (BancoError, MigracaoError) as error:
        print(f"erro: {error}", file=sys.stderr)
        return 1
    except Exception as error:  # erro do banco: tudo foi desfeito
        print(f"erro, tudo desfeito: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
