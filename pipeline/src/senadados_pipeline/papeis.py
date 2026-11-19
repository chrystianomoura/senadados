"""Cria os papéis de banco `sd_carga` e `sd_leitura` e grava a URL de cada um no `.env`.

Os papéis nascem **sem nenhuma permissão** (quem concede é a migração 002) e por SQL, o que
os deixa de fora do grupo de administração da Neon. A senha é gerada aqui, vai direto para o
`.env` (que o git ignora) e **nunca é impressa**. Idempotente: se o papel já existe, não
troca a senha (ela pode estar em uso).

Usa o dono do banco (`DATABASE_URL`). Para uma branch ou para a produção, é a URL do dono
daquele banco: os papéis são criados no banco ao qual a URL aponta.
"""

from __future__ import annotations

import argparse
import re
import secrets
import sys
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit

from senadados_pipeline.banco import BancoError, conectar, host_de, url_do_ambiente
from senadados_pipeline.config import ROOT

# papel -> variável do .env com a URL dele
PAPEIS = {"sd_carga": "DATABASE_URL_CARGA", "sd_leitura": "DATABASE_URL_LEITURA"}

ENV_PADRAO = ROOT / ".env"


class PapelError(Exception):
    """Não foi possível criar um papel ou gravar a URL dele."""


def montar_url(url_dono: str, papel: str, senha: str) -> str:
    """A URL do dono com o usuário e a senha trocados. O resto (servidor, banco, SSL) fica."""
    partes = urlsplit(url_dono)
    servidor = partes.hostname or ""
    porta = f":{partes.port}" if partes.port else ""
    return urlunsplit(
        (partes.scheme, f"{papel}:{quote(senha, safe='')}@{servidor}{porta}", partes.path,
         partes.query, partes.fragment)
    )


def tem_variavel(env: Path, variavel: str) -> bool:
    if not env.exists():
        return False
    return re.search(rf"^{re.escape(variavel)}=", env.read_text(encoding="utf-8"), re.M) is not None


def acrescentar(env: Path, variavel: str, valor: str) -> None:
    """Acrescenta `VARIAVEL=valor` ao .env, só dono pode ler, sem tocar no que já existe."""
    texto = env.read_text(encoding="utf-8") if env.exists() else ""
    separador = "" if texto == "" or texto.endswith("\n") else "\n"
    env.touch(mode=0o600)
    env.write_text(f"{texto}{separador}{variavel}={valor}\n", encoding="utf-8")
    env.chmod(0o600)


def criar_papel(conn, papel: str, senha: str) -> None:
    from psycopg import sql

    conn.execute(
        sql.SQL(
            "CREATE ROLE {papel} WITH LOGIN PASSWORD {senha} NOSUPERUSER NOCREATEDB "
            "NOCREATEROLE NOREPLICATION NOBYPASSRLS CONNECTION LIMIT 10"
        ).format(papel=sql.Identifier(papel), senha=sql.Literal(senha))
    )


def run(url_dono: str, env: Path = ENV_PADRAO, log=print, gerar_senha=None) -> list[str]:
    """Devolve os papéis que foram criados agora."""
    gerar_senha = gerar_senha or (lambda: secrets.token_urlsafe(24))
    log(f"Banco alvo: {host_de(url_dono)}")
    conn = conectar(url_dono)
    criados: list[str] = []
    try:
        for papel, variavel in PAPEIS.items():
            existe = conn.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (papel,)).fetchone()
            tem_url = tem_variavel(env, variavel)
            if existe and tem_url:
                log(f"  {papel}: já existe e {variavel} já está no .env; nada a fazer")
                continue
            if existe:
                raise PapelError(
                    f"o papel {papel} existe, mas {variavel} não está no .env e a senha não "
                    "pode ser recuperada: redefina a senha dele no console da Neon e grave a URL"
                )
            if tem_url:
                raise PapelError(
                    f"{variavel} já está no .env, mas o papel {papel} não existe neste banco; "
                    "apague a linha antiga do .env (ela é de outro banco) e rode de novo"
                )
            senha = gerar_senha()
            criar_papel(conn, papel, senha)
            acrescentar(env, variavel, montar_url(url_dono, papel, senha))
            criados.append(papel)
            log(f"  {papel}: criado, {variavel} gravada no .env (a senha não é impressa)")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return criados


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(
        description="Cria os papéis sd_carga e sd_leitura e grava as URLs no .env."
    ).parse_args(argv)
    try:
        run(url_do_ambiente("DATABASE_URL"))
    except (BancoError, PapelError) as error:
        print(f"erro: {error}", file=sys.stderr)
        return 1
    except Exception as error:  # erro do banco: nada foi criado
        print(f"erro, nada foi criado: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
