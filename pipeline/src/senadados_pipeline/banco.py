"""Conexão com o PostgreSQL na nuvem (Neon, D042).

A URL de conexão vem de uma variável de ambiente, nunca do código nem do repositório
(AGENTS.md, seção 6). O driver só é importado na hora de conectar, para os testes das
regras não dependerem dele.
"""

from __future__ import annotations

import os
from urllib.parse import urlsplit


class BancoError(Exception):
    """A conexão com o banco não está configurada ou falhou."""


def url_do_ambiente(variavel: str) -> str:
    url = os.environ.get(variavel, "").strip()
    if not url:
        raise BancoError(
            f"{variavel} não está definida. Ela fica num arquivo .env (que o git ignora) "
            "ou no ambiente, nunca no repositório."
        )
    return url


def host_de(url: str) -> str:
    """Só o endereço do servidor, para mostrar em qual banco o comando vai agir (sem a senha)."""
    return urlsplit(url).hostname or "?"


def conectar(url: str):
    import psycopg

    try:
        return psycopg.connect(url, connect_timeout=15)
    except psycopg.Error as error:
        raise BancoError(f"não foi possível conectar ao banco: {error}") from error
