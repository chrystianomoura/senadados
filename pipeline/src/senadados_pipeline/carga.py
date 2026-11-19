"""Carga dos dados agregados e provados para o PostgreSQL na nuvem (D042).

Lê o banco limpo local (SQLite, D034), escolhe só o que passou nas verificações (D025),
agrega e grava no esquema `publico` do Neon, junto com o detalhe das verificações no
esquema `interno`. Tudo numa só transação que apaga e recarrega as tabelas, então quem
saiu da lista de senadores some sozinho (D026).

Por padrão é um ENSAIO: a transação é desfeita no fim. Só com `--apply` ela é confirmada.
A conexão usa o papel `sd_carga` (`DATABASE_URL_CARGA`), que escreve mas não cria tabelas.

Falha fechado: se faltar alguma verificação, ou ela não for do mesmo dia da coleta, nada
é carregado. As despesas linha a linha **não** vão para a nuvem (só agregados).
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

from senadados_pipeline.banco import BancoError, conectar, host_de, url_do_ambiente
from senadados_pipeline.config import CLEAN_DB

# Verificações que precisam existir, todas, para a carga acontecer.
VERIFICACOES = (
    "cota",
    "equipe",
    "moradia",
    "salario",
    "contato_endereco",
    "contato_telefones",
    "contato_email",
)

# Motivos de uma lista fechada, em palavras simples e sem culpar ninguém. Só descrevem o fato
# (D010). Nunca texto livre do banco: o `detalhe` fica no esquema interno.
MOTIVOS = {
    ("cota", "oculto"): "o resumo do Senado e as despesas detalhadas diferem",
    ("equipe", "oculto"): "o resumo do Senado e a lista de servidores diferem no número de pessoas",
    ("moradia", "pendente"): "a lista do mês e a página mensal do Senado diferem no último mês",
    ("moradia", "oculto"): "as fontes do Senado sobre moradia diferem",
    ("salario", "oculto"): "a folha do mês não permite ligar o valor ao senador com segurança",
    ("contato_endereco", "oculto"): "a API e a página do Senado trazem endereços diferentes",
    ("contato_telefones", "oculto"): "a API e a página do Senado trazem telefones diferentes",
    ("contato_email", "oculto"): "a API e a página do Senado trazem e-mails diferentes",
}

# Tabelas, na ordem em que são gravadas: nome no banco e colunas.
TABELAS = {
    "publico.senadores": ("cod_senador", "nome", "tipo", "uf", "partido"),
    "publico.despesas_mensais": (
        "cod_senador", "ano", "mes", "categoria", "valor_centavos", "qtd_despesas",
    ),
    "publico.fornecedores_anuais": (
        "cod_senador", "ano", "cnpj", "nome", "valor_centavos", "qtd_despesas",
    ),
    "publico.fornecedores_agrupados_anuais": (
        "cod_senador", "ano", "tipo", "qtd_despesas", "total_centavos", "maior_centavos",
    ),
    "publico.contato": ("cod_senador", "endereco", "telefones", "email"),
    "publico.equipe": ("cod_senador", "ano", "pessoas"),
    "publico.moradia_meses": (
        "cod_senador", "ano", "mes", "auxilio_moradia", "imovel_funcional",
    ),
    "publico.salario": (
        "cod_senador", "ano", "mes", "remuneracao_basica_centavos",
        "remuneracao_liquida_centavos",
    ),
    "publico.verificacoes_resumo": (
        "verificacao", "ano", "identicos", "explicados", "pendentes", "ocultos", "verificado_em",
    ),
    "publico.verificacoes_motivos": ("verificacao", "ano", "situacao", "motivo", "qtd"),
    "publico.metadados": ("chave", "valor"),
    "interno.verificacao_cota": (
        "cod_senador", "ano", "despesas_centavos", "resumo_centavos", "sem_categoria_centavos",
        "resultado", "detalhe",
    ),
    "interno.verificacao_equipe": (
        "cod_senador", "ano", "equipe_resumo", "equipe_lista", "resultado", "detalhe", "exibir",
    ),
    "interno.verificacao_moradia": ("cod_senador", "ano", "resultado", "detalhe", "exibir"),
    "interno.verificacao_salario": (
        "cod_senador", "ano", "mes", "resultado", "detalhe", "exibir",
    ),
    "interno.verificacao_contato": ("cod_senador", "campo", "resultado", "detalhe", "exibir"),
    "interno.verificacoes": (
        "nome", "ano", "identicos", "explicados", "sem_explicacao", "verificado_em",
    ),
}

# A cota de um senador num ano só aparece se passou na verificação (D035). Fornecedores saem
# das mesmas despesas, então seguem a mesma regra.
COTA_PROVADA = (
    "(cod_senador, ano) IN "
    "(SELECT cod_senador, ano FROM verificacao_cota WHERE resultado IN ('identico', 'explicado'))"
)


class CargaError(Exception):
    """Os dados locais não estão em condições de ir para a nuvem."""


def _tudo(db: sqlite3.Connection, sql: str) -> list[tuple]:
    return [tuple(linha) for linha in db.execute(sql)]


def _como_bool(linhas: list[tuple], posicoes: tuple[int, ...]) -> list[tuple]:
    return [
        tuple(bool(v) if i in posicoes else v for i, v in enumerate(linha)) for linha in linhas
    ]


def _quando(texto: str) -> datetime:
    return datetime.fromisoformat(texto)


def conferir_foto(db: sqlite3.Connection) -> str:
    """Recusa carregar se faltar verificação ou se ela não for do dia da coleta (D035)."""
    try:
        ref = db.execute("SELECT valor FROM metadados WHERE chave = 'data_referencia'").fetchone()
        linhas = db.execute("SELECT nome, verificado_em FROM verificacoes").fetchall()
    except sqlite3.OperationalError as erro:
        raise CargaError(
            f"o banco limpo está incompleto ({erro}); rode a limpeza e as verificações"
        ) from erro
    if not ref:
        raise CargaError("o banco limpo não tem a data de referência; rode a limpeza de novo")
    faltam = [nome for nome in VERIFICACOES if nome not in {linha[0] for linha in linhas}]
    if faltam:
        raise CargaError(
            "faltam verificações: " + ", ".join(faltam) + ". Rode todas, depois da limpeza."
        )
    fora = sorted({nome for nome, quando in linhas if quando[:10] != ref[0]})
    if fora:
        raise CargaError(
            f"verificações que não são do dia da coleta ({ref[0]}): "
            + ", ".join(fora)
            + ". Refaça a coleta, a limpeza e as verificações no mesmo dia."
        )
    return ref[0]


def selecionar(db: sqlite3.Connection, agora: datetime) -> dict[str, list[tuple]]:
    """O que vai para a nuvem, tabela por tabela. Não escreve nada em lugar nenhum."""
    dados: dict[str, list[tuple]] = {}

    dados["publico.senadores"] = _tudo(
        db, "SELECT cod_senador, nome, tipo, uf, partido FROM senadores ORDER BY cod_senador"
    )
    dados["publico.despesas_mensais"] = _tudo(
        db,
        f"""SELECT cod_senador, ano, mes, categoria, SUM(valor_centavos), COUNT(*)
              FROM despesas WHERE {COTA_PROVADA}
             GROUP BY cod_senador, ano, mes, categoria ORDER BY 1, 2, 3, 4""",
    )
    # O mesmo CNPJ aparece com grafias diferentes: vale a mais frequente (e, no empate, a primeira
    # em ordem alfabética), para o resultado ser sempre o mesmo.
    dados["publico.fornecedores_anuais"] = _tudo(
        db,
        """WITH nomes AS (
                SELECT fornecedor_doc AS doc, fornecedor_nome AS nome, COUNT(*) AS c
                  FROM despesas WHERE fornecedor_tipo = 'empresa' GROUP BY 1, 2),
            melhor AS (
                SELECT doc, nome FROM (
                    SELECT doc, nome,
                           ROW_NUMBER() OVER (PARTITION BY doc ORDER BY c DESC, nome ASC) AS rn
                      FROM nomes) WHERE rn = 1)
            SELECT d.cod_senador, d.ano, d.fornecedor_doc, m.nome, SUM(d.valor_centavos), COUNT(*)
              FROM despesas d JOIN melhor m ON m.doc = d.fornecedor_doc
             WHERE d.fornecedor_tipo = 'empresa'
               AND (d.cod_senador, d.ano) IN
                   (SELECT cod_senador, ano FROM verificacao_cota
                     WHERE resultado IN ('identico', 'explicado'))
             GROUP BY d.cod_senador, d.ano, d.fornecedor_doc, m.nome ORDER BY 1, 2, 3""",
    )
    dados["publico.fornecedores_agrupados_anuais"] = _tudo(
        db,
        f"""SELECT cod_senador, ano, fornecedor_tipo, COUNT(*), SUM(valor_centavos),
                   MAX(valor_centavos)
              FROM despesas
             WHERE fornecedor_tipo IN ('pessoa_fisica', 'outro', 'sem_documento')
               AND {COTA_PROVADA}
             GROUP BY cod_senador, ano, fornecedor_tipo ORDER BY 1, 2, 3""",
    )

    # Contato: cada campo só vai se foi provado (exibir = 1); o que não foi fica vazio (D040).
    contato = _tudo(
        db,
        """SELECT c.cod_senador,
                  CASE WHEN COALESCE(a.exibir, 0) = 1 THEN c.endereco END,
                  CASE WHEN COALESCE(t.exibir, 0) = 1 THEN c.telefones END,
                  CASE WHEN COALESCE(e.exibir, 0) = 1 THEN c.email END
             FROM contato c
             LEFT JOIN verificacao_contato a
                    ON a.cod_senador = c.cod_senador AND a.campo = 'endereco'
             LEFT JOIN verificacao_contato t
                    ON t.cod_senador = c.cod_senador AND t.campo = 'telefones'
             LEFT JOIN verificacao_contato e
                    ON e.cod_senador = c.cod_senador AND e.campo = 'email'
            ORDER BY c.cod_senador""",
    )
    dados["publico.contato"] = [
        linha for linha in contato if any(v is not None for v in linha[1:])
    ]

    dados["publico.equipe"] = _tudo(
        db,
        """SELECT cod_senador, ano, equipe_resumo FROM verificacao_equipe
            WHERE exibir = 1 AND equipe_resumo IS NOT NULL ORDER BY 1, 2""",
    )
    dados["publico.moradia_meses"] = _como_bool(
        _tudo(
            db,
            """SELECT m.cod_senador, m.ano, m.mes, m.auxilio_moradia, m.imovel_funcional
                 FROM moradia_meses m
                 JOIN verificacao_moradia v
                   ON v.cod_senador = m.cod_senador AND v.ano = m.ano AND v.exibir = 1
                ORDER BY m.cod_senador, m.mes""",
        ),
        (3, 4),
    )
    dados["publico.salario"] = _tudo(
        db,
        """SELECT s.cod_senador, s.ano, s.mes, s.remuneracao_basica_centavos,
                  s.remuneracao_liquida_centavos
             FROM salario s
             JOIN verificacao_salario v
               ON v.cod_senador = s.cod_senador AND v.ano = s.ano
              AND v.mes = s.mes AND v.exibir = 1
            ORDER BY s.cod_senador, s.ano, s.mes""",
    )

    pendentes_moradia = dict(
        _tudo(
            db,
            "SELECT ano, COUNT(*) FROM verificacao_moradia "
            "WHERE resultado = 'pendente' GROUP BY ano",
        )
    )
    dados["publico.verificacoes_resumo"] = [
        (
            nome, ano, identicos, explicados,
            pendentes_moradia.get(ano, 0) if nome == "moradia" else 0,
            sem_explicacao, _quando(quando),
        )
        for nome, ano, identicos, explicados, sem_explicacao, quando in _tudo(
            db,
            """SELECT nome, ano, identicos, explicados, sem_explicacao, verificado_em
                 FROM verificacoes ORDER BY nome, ano""",
        )
    ]
    dados["publico.verificacoes_motivos"] = _motivos(db)

    meta = dict(_tudo(db, "SELECT chave, valor FROM metadados"))
    dados["publico.metadados"] = [
        ("data_referencia", meta["data_referencia"]),
        ("anos", meta["anos"]),
        ("senadores", meta["senadores"]),
        ("carregado_em", agora.isoformat(timespec="seconds")),
    ]

    # O detalhe das verificações vai inteiro para o esquema interno.
    for nome, sql, bools in (
        ("verificacao_cota", "SELECT {c} FROM verificacao_cota ORDER BY 1, 2", ()),
        ("verificacao_equipe", "SELECT {c} FROM verificacao_equipe ORDER BY 1, 2", (6,)),
        ("verificacao_moradia", "SELECT {c} FROM verificacao_moradia ORDER BY 1, 2", (4,)),
        ("verificacao_salario", "SELECT {c} FROM verificacao_salario ORDER BY 1, 2", (5,)),
        ("verificacao_contato", "SELECT {c} FROM verificacao_contato ORDER BY 1, 2", (4,)),
    ):
        colunas = ", ".join(TABELAS[f"interno.{nome}"])
        dados[f"interno.{nome}"] = _como_bool(_tudo(db, sql.format(c=colunas)), bools)
    dados["interno.verificacoes"] = [
        (*linha[:5], _quando(linha[5]))
        for linha in _tudo(
            db,
            "SELECT nome, ano, identicos, explicados, sem_explicacao, verificado_em "
            "FROM verificacoes ORDER BY 1, 2",
        )
    ]
    return dados


def _motivos(db: sqlite3.Connection) -> list[tuple]:
    """Quantos ficaram ocultos ou pendentes em cada verificação, com o motivo da lista fechada."""
    consultas = {
        "cota": "SELECT ano, resultado, COUNT(*) FROM verificacao_cota "
        "WHERE resultado = 'sem_explicacao' GROUP BY ano, resultado",
        "equipe": "SELECT ano, resultado, COUNT(*) FROM verificacao_equipe "
        "WHERE resultado = 'sem_explicacao' GROUP BY ano, resultado",
        "moradia": "SELECT ano, resultado, COUNT(*) FROM verificacao_moradia "
        "WHERE resultado IN ('pendente', 'sem_explicacao') GROUP BY ano, resultado",
        "salario": "SELECT ano, resultado, COUNT(*) FROM verificacao_salario "
        "WHERE resultado = 'sem_explicacao' GROUP BY ano, resultado",
    }
    for campo in ("endereco", "telefones", "email"):
        consultas[f"contato_{campo}"] = (
            f"SELECT (SELECT ano FROM verificacoes WHERE nome = 'contato_{campo}'), resultado, "
            f"COUNT(*) FROM verificacao_contato WHERE campo = '{campo}' "
            "AND resultado = 'sem_explicacao' GROUP BY resultado"
        )
    linhas = []
    for nome, sql in consultas.items():
        for ano, resultado, qtd in _tudo(db, sql):
            situacao = "pendente" if resultado == "pendente" else "oculto"
            linhas.append((nome, ano, situacao, MOTIVOS[(nome, situacao)], qtd))
    return sorted(linhas)


def conferir_coerencia(dados: dict[str, list[tuple]]) -> None:
    """Uma checagem interna: o resumo e os motivos contam a mesma coisa."""
    por_chave: dict[tuple, int] = {}
    for verificacao, ano, situacao, _motivo, qtd in dados["publico.verificacoes_motivos"]:
        chave = (verificacao, ano, situacao)
        por_chave[chave] = por_chave.get(chave, 0) + qtd
    for verificacao, ano, _i, _e, pendentes, ocultos, _q in dados["publico.verificacoes_resumo"]:
        if por_chave.get((verificacao, ano, "oculto"), 0) != ocultos:
            raise CargaError(f"{verificacao} {ano}: o resumo e os motivos não contam o mesmo")
        if por_chave.get((verificacao, ano, "pendente"), 0) != pendentes:
            raise CargaError(f"{verificacao} {ano}: os pendentes do resumo e dos motivos diferem")


def carregar(conn, dados: dict[str, list[tuple]], *, apply: bool, log=print) -> dict[str, int]:
    """Apaga e recarrega tudo numa transação. Confere as contagens antes de confirmar."""
    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE " + ", ".join(TABELAS))
            for tabela, colunas in TABELAS.items():
                linhas = dados[tabela]
                if linhas:
                    marcas = ", ".join(["%s"] * len(colunas))
                    cur.executemany(
                        f"INSERT INTO {tabela} ({', '.join(colunas)}) VALUES ({marcas})", linhas
                    )
            for tabela in TABELAS:
                gravadas = cur.execute(f"SELECT count(*) FROM {tabela}").fetchone()[0]
                if gravadas != len(dados[tabela]):
                    raise CargaError(
                        f"{tabela}: {gravadas} linha(s) no banco contra "
                        f"{len(dados[tabela])} enviadas"
                    )
        if apply:
            conn.commit()
        else:
            conn.rollback()
    except Exception:
        conn.rollback()
        raise
    for tabela in TABELAS:
        log(f"  {tabela}: {len(dados[tabela])} linha(s)")
    return {tabela: len(dados[tabela]) for tabela in TABELAS}


def run(sqlite_path: Path, url: str, *, apply: bool, agora: datetime | None = None, log=print):
    if not sqlite_path.exists():
        raise CargaError(f"não achei o banco limpo em {sqlite_path}; rode a limpeza antes")
    with closing(sqlite3.connect(f"file:{sqlite_path}?mode=ro", uri=True)) as db:
        referencia = conferir_foto(db)
        dados = selecionar(db, agora or datetime.now(UTC))
    conferir_coerencia(dados)
    log(f"Banco alvo: {host_de(url)} | dados de {referencia}")
    log("Modo: GRAVAR" if apply else "Modo: ensaio (tudo é desfeito no fim)")
    conn = conectar(url)
    try:
        resumo = carregar(conn, dados, apply=apply, log=log)
    finally:
        conn.close()
    log(
        "Gravado."
        if apply
        else "Ensaio concluído: nada foi gravado. Para gravar, rode com --apply."
    )
    return resumo


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Carrega os dados provados no banco (ensaio por padrão)."
    )
    parser.add_argument("--banco", type=Path, default=CLEAN_DB, help="banco limpo local (SQLite)")
    parser.add_argument(
        "--apply", action="store_true", help="grava de verdade (sem isto, só ensaia)"
    )
    args = parser.parse_args(argv)
    try:
        run(args.banco, url_do_ambiente("DATABASE_URL_CARGA"), apply=args.apply)
    except (CargaError, BancoError) as error:
        print(f"erro: {error}", file=sys.stderr)
        return 1
    except Exception as error:  # erro do banco: a transação foi desfeita
        print(f"erro, tudo desfeito: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
