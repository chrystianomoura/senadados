"""Testa as permissões dos papéis do banco conectando como cada um (D042, menor privilégio).

Exemplo com publico.perfil e interno.verificacao_perfil: sd_leitura lê o publico, mas não lê o interno nem escreve;
sd_carga lê o interno, mas não faz UPDATE nem cria tabela. Tudo o que roda é desfeito no fim (rollback).

Uso, a partir da raiz:  uv run --project pipeline --env-file .env python ferramentas/conferencia/permissoes.py
"""

import os

import psycopg


def tent(url, sql):
    try:
        with psycopg.connect(url, connect_timeout=15) as c, c.cursor() as cur:
            cur.execute(sql)
            r = cur.fetchone() if cur.description else "ok"
            c.rollback()
            return f"permitido {r}"
    except psycopg.errors.InsufficientPrivilege:
        return "NEGADO"
    except Exception as e:
        return f"erro {type(e).__name__}"


L, C = os.environ["DATABASE_URL_LEITURA"], os.environ["DATABASE_URL_CARGA"]
for papel, url, sql in [
    ("sd_leitura", L, "SELECT count(*), count(foto_url) FROM publico.perfil"),
    ("sd_leitura", L, "SELECT count(*) FROM interno.verificacao_perfil"),
    ("sd_leitura", L, "INSERT INTO publico.perfil (cod_senador) VALUES (1)"),
    ("sd_leitura", L, "DELETE FROM publico.perfil"),
    ("sd_carga", C, "SELECT count(*) FROM interno.verificacao_perfil"),
    ("sd_carga", C, "UPDATE publico.perfil SET foto_url = NULL"),
    ("sd_carga", C, "CREATE TABLE publico.x (a int)"),
]:
    print(f"{papel:11} {sql[:58]:58} -> {tent(url, sql)}")
