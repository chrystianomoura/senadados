import sqlite3
from datetime import UTC, datetime

import pytest

from senadados_pipeline import carga

AGORA = datetime(2026, 11, 19, 12, 0, tzinfo=UTC)

DDL = """
CREATE TABLE senadores (cod_senador INTEGER, nome TEXT, tipo TEXT, uf TEXT, partido TEXT);
CREATE TABLE despesas (id INTEGER, ano INTEGER, mes INTEGER, cod_senador INTEGER, categoria TEXT,
  tipo_documento TEXT, fornecedor_tipo TEXT, fornecedor_doc TEXT, fornecedor_nome TEXT,
  data TEXT, data_fora_do_esperado INTEGER, valor_centavos INTEGER);
CREATE TABLE contato (cod_senador INTEGER, endereco TEXT, telefones TEXT, email TEXT);
CREATE TABLE moradia_meses (cod_senador INTEGER, ano INTEGER, mes TEXT,
  auxilio_moradia INTEGER, imovel_funcional INTEGER);
CREATE TABLE salario (cod_senador INTEGER, ano INTEGER, mes INTEGER,
  remuneracao_basica_centavos INTEGER, remuneracao_liquida_centavos INTEGER);
CREATE TABLE verificacao_cota (cod_senador INTEGER, ano INTEGER, despesas_centavos INTEGER,
  resumo_centavos INTEGER, sem_categoria_centavos INTEGER, resultado TEXT, detalhe TEXT);
CREATE TABLE verificacao_equipe (cod_senador INTEGER, ano INTEGER, equipe_resumo INTEGER,
  equipe_lista INTEGER, resultado TEXT, detalhe TEXT, exibir INTEGER);
CREATE TABLE verificacao_moradia (cod_senador INTEGER, ano INTEGER, resultado TEXT,
  detalhe TEXT, exibir INTEGER);
CREATE TABLE verificacao_salario (cod_senador INTEGER, ano INTEGER, mes INTEGER,
  resultado TEXT, detalhe TEXT, exibir INTEGER);
CREATE TABLE verificacao_contato (cod_senador INTEGER, campo TEXT, resultado TEXT,
  detalhe TEXT, exibir INTEGER);
CREATE TABLE verificacoes (nome TEXT, ano INTEGER, identicos INTEGER, explicados INTEGER,
  sem_explicacao INTEGER, verificado_em TEXT);
CREATE TABLE metadados (chave TEXT PRIMARY KEY, valor TEXT);
"""

DIA = "2026-11-18T10:00:00-03:00"
CNPJ_A = "11.111.111/0001-11"


def banco(*, dia_das_verificacoes=DIA, sem=()):
    """Um banco limpo pequeno: senador 1 tudo provado; 2 com cota e equipe sem explicação."""
    db = sqlite3.connect(":memory:")
    db.executescript(DDL)
    db.executemany(
        "INSERT INTO senadores VALUES (?,?,?,?,?)",
        [(1, "ALFA", "Titular", "AC", "P1"), (2, "BETA", "Titular", "BA", "P2"),
         (3, "GAMA", "1º Suplente", "CE", "P3")],
    )
    d = "(?,?,?,?,?,?,?,?,?,?,?,?)"
    db.executemany(
        f"INSERT INTO despesas VALUES {d}",
        [
            # senador 1, 2020: duas grafias do mesmo CNPJ (a mais frequente vence)
            (1, 2020, 1, 1, "Cat A", None, "empresa", CNPJ_A, "Alfa", None, 0, 1000),
            (2, 2020, 1, 1, "Cat A", None, "empresa", CNPJ_A, "Alfa Ltda", None, 0, 500),
            (3, 2020, 2, 1, "Cat B", None, "empresa", CNPJ_A, "Alfa Ltda", None, 0, 200),
            # pessoa física e documento fora do padrão: sem nome e sem documento
            (4, 2020, 1, 1, "Cat A", None, "pessoa_fisica", None, None, None, 0, 300),
            (5, 2020, 1, 1, "Cat A", None, "pessoa_fisica", None, None, None, 0, 100),
            (6, 2020, 1, 1, "Cat A", None, "outro", "123456789012", "Fulano", None, 0, 50),
            # senador 2, 2009: cota sem explicação, não pode ir
            (7, 2009, 1, 2, "Cat A", None, "empresa", "22.222.222/0001-22", "Beta", None, 0, 999),
            (8, 2009, 1, 2, "Cat A", None, "sem_documento", None, None, None, 0, 10),
        ],
    )
    db.executemany(
        "INSERT INTO contato VALUES (?,?,?,?)",
        [(1, "Anexo 1", "(61) 1", "a@x.br"), (2, "Anexo 2", "(61) 2", None), (3, None, None, None)],
    )
    db.executemany(
        "INSERT INTO moradia_meses VALUES (?,?,?,?,?)",
        [(1, 2026, "2026-01", 1, 0), (1, 2026, "2026-02", 0, 1), (2, 2026, "2026-01", 1, 0)],
    )
    db.executemany(
        "INSERT INTO salario VALUES (?,?,?,?,?)",
        [(1, 2026, 10, 4636619, 2904849), (2, 2026, 10, 4636619, 2910062)],
    )
    db.executemany(
        "INSERT INTO verificacao_cota VALUES (?,?,?,?,?,?,?)",
        [(1, 2020, 2150, 2150, 0, "identico", None),
         (2, 2009, 1009, 0, 0, "sem_explicacao", "Cat A: despesas 999 contra resumo 0")],
    )
    db.executemany(
        "INSERT INTO verificacao_equipe VALUES (?,?,?,?,?,?,?)",
        [(1, 2026, 15, 15, "identico", None, 1), (2, 2026, 5, 4, "sem_explicacao", "x", 0)],
    )
    db.executemany(
        "INSERT INTO verificacao_moradia VALUES (?,?,?,?,?)",
        [(1, 2026, "identico", None, 1), (2, 2026, "pendente", "p", 0),
         (3, 2026, "identico", None, 1)],  # o 3 foi provado e não usou nenhum benefício
    )
    db.executemany(
        "INSERT INTO verificacao_salario VALUES (?,?,?,?,?,?)",
        [(1, 2026, 10, "identico", None, 1), (2, 2026, 10, "sem_explicacao", "s", 0)],
    )
    db.executemany(
        "INSERT INTO verificacao_contato VALUES (?,?,?,?,?)",
        [(1, "endereco", "identico", None, 1), (1, "telefones", "identico", None, 1),
         (1, "email", "identico", None, 1),
         (2, "endereco", "identico", None, 1), (2, "telefones", "sem_explicacao", "t", 0),
         (2, "email", "identico", None, 0),
         (3, "endereco", "identico", None, 0)],
    )
    resumo = [
        ("cota", 2009, 0, 0, 1), ("cota", 2020, 1, 0, 0),
        ("equipe", 2026, 1, 0, 1), ("moradia", 2026, 1, 0, 0),
        ("salario", 2026, 1, 0, 1), ("contato_endereco", 2026, 2, 0, 0),
        ("contato_telefones", 2026, 1, 0, 1), ("contato_email", 2026, 2, 0, 0),
    ]
    db.executemany(
        "INSERT INTO verificacoes VALUES (?,?,?,?,?,?)",
        [(n, a, i, e, s, dia_das_verificacoes) for n, a, i, e, s in resumo if n not in sem],
    )
    db.executemany(
        "INSERT INTO metadados VALUES (?,?)",
        [("data_referencia", "2026-11-18"), ("anos", "2008-2026"), ("senadores", "3"),
         ("soma_centavos", "999999")],
    )
    db.commit()  # sem isto o backup para um arquivo fica esperando a transação aberta
    return db


@pytest.fixture
def dados():
    return carga.selecionar(banco(), AGORA)


def test_cota_so_dos_pares_senador_ano_provados(dados):
    chaves = {(c, a) for c, a, *_ in dados["publico.despesas_mensais"]}
    assert chaves == {(1, 2020)}  # o senador 2 em 2009 (sem explicação) não vai


def test_despesas_mensais_somam_por_mes_e_categoria(dados):
    mensais = dados["publico.despesas_mensais"]
    linhas = {(m, cat): (valor, qtd) for _, _, m, cat, valor, qtd in mensais}
    assert linhas[(1, "Cat A")] == (1950, 5)
    assert linhas[(2, "Cat B")] == (200, 1)


def test_fornecedor_usa_a_grafia_mais_frequente_do_cnpj(dados):
    assert dados["publico.fornecedores_anuais"] == [(1, 2020, CNPJ_A, "Alfa Ltda", 1700, 3)]


def test_quem_nao_e_empresa_fica_agrupado_sem_nome_nem_documento(dados):
    grupos = {linha[2]: linha for linha in dados["publico.fornecedores_agrupados_anuais"]}
    assert grupos["pessoa_fisica"] == (1, 2020, "pessoa_fisica", 2, 400, 300)
    assert grupos["outro"] == (1, 2020, "outro", 1, 50, 50)
    assert all(len(linha) == 6 for linha in dados["publico.fornecedores_agrupados_anuais"])


def test_contato_so_leva_o_campo_provado(dados):
    contato = {linha[0]: linha[1:] for linha in dados["publico.contato"]}
    assert contato[1] == ("Anexo 1", "(61) 1", "a@x.br")
    # senador 2: telefone sem explicação e e-mail com exibir = 0 ficam vazios
    assert contato[2] == ("Anexo 2", None, None)
    assert 3 not in contato  # nada provado: nem linha existe


def test_equipe_moradia_e_salario_so_de_quem_foi_provado(dados):
    assert dados["publico.equipe"] == [(1, 2026, 15)]
    assert {linha[0] for linha in dados["publico.moradia_meses"]} == {1}
    assert dados["publico.moradia_meses"][0][3:] == (True, False)
    assert [linha[0] for linha in dados["publico.salario"]] == [1]


def test_moradia_verificada_inclui_quem_nao_usou_e_exclui_os_nao_provados(dados):
    assert dados["publico.moradia_verificada"] == [(1, 2026), (3, 2026)]
    assert 3 not in {linha[0] for linha in dados["publico.moradia_meses"]}


def test_recusa_meses_de_moradia_sem_prova(dados):
    dados["publico.moradia_meses"].append((2, 2026, "2026-01", True, False))  # o 2 está pendente
    with pytest.raises(carga.CargaError, match="não foi provada"):
        carga.conferir_coerencia(dados)


def test_resumo_conta_pendentes_da_moradia_e_ocultos(dados):
    resumo = {(v, a): (i, e, p, o) for v, a, i, e, p, o, _ in dados["publico.verificacoes_resumo"]}
    assert resumo[("cota", 2009)] == (0, 0, 0, 1)
    assert resumo[("moradia", 2026)] == (1, 0, 1, 0)


def test_motivos_vem_de_uma_lista_fechada_e_fecham_com_o_resumo(dados):
    carga.conferir_coerencia(dados)
    motivos = {linha[3] for linha in dados["publico.verificacoes_motivos"]}
    assert motivos <= set(carga.MOTIVOS.values())
    assert ("moradia", 2026, "pendente", carga.MOTIVOS[("moradia", "pendente")], 1) in dados[
        "publico.verificacoes_motivos"
    ]


def test_publico_nao_tem_nenhum_texto_livre_de_verificacao(dados):
    textos = [str(v) for linha in dados["publico.verificacoes_motivos"] for v in linha]
    assert not any("despesas 999" in t or t == "x" for t in textos)


def test_detalhe_vai_so_para_o_esquema_interno(dados):
    interno = dados["interno.verificacao_cota"]
    assert any(linha[-1] == "Cat A: despesas 999 contra resumo 0" for linha in interno)
    for tabela, linhas in dados.items():
        if tabela.startswith("publico."):
            assert not any("contra resumo" in str(v) for linha in linhas for v in linha)


def test_metadados_publicos_nao_levam_o_total_geral(dados):
    chaves = {linha[0] for linha in dados["publico.metadados"]}
    assert chaves == {"data_referencia", "anos", "senadores", "carregado_em"}


def test_so_agregados_vao_para_a_nuvem(dados):
    assert "publico.despesas" not in dados
    assert all("id" not in colunas for colunas in carga.TABELAS.values())


def test_colunas_e_linhas_tem_o_mesmo_tamanho(dados):
    for tabela, colunas in carga.TABELAS.items():
        for linha in dados[tabela]:
            assert len(linha) == len(colunas), tabela


def test_foto_ok_devolve_a_data():
    assert carga.conferir_foto(banco()) == "2026-11-18"


def test_recusa_verificacao_de_outro_dia():
    with pytest.raises(carga.CargaError, match="não são do dia da coleta"):
        carga.conferir_foto(banco(dia_das_verificacoes="2026-11-17T10:00:00-03:00"))


def test_recusa_quando_falta_uma_verificacao():
    with pytest.raises(carga.CargaError, match="faltam verificações: salario"):
        carga.conferir_foto(banco(sem=("salario",)))


def test_recusa_banco_limpo_incompleto():
    with pytest.raises(carga.CargaError, match="incompleto"):
        carga.conferir_foto(sqlite3.connect(":memory:"))


class Cursor:
    def __init__(self, conn):
        self.conn = conn
        self.resposta = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, params=None):
        self.conn.pedidos.append(sql)
        if sql.startswith("SELECT count(*) FROM "):
            tabela = sql.removeprefix("SELECT count(*) FROM ")
            self.resposta = (self.conn.contagens.get(tabela, 0) + self.conn.desvio,)
        return self

    def executemany(self, sql, linhas):
        tabela = sql.split()[2]
        self.conn.contagens[tabela] = self.conn.contagens.get(tabela, 0) + len(list(linhas))

    def fetchone(self):
        return self.resposta


class Conexao:
    def __init__(self, desvio=0):
        self.pedidos, self.contagens, self.eventos, self.desvio = [], {}, [], desvio

    def cursor(self):
        return Cursor(self)

    def commit(self):
        self.eventos.append("commit")

    def rollback(self):
        self.eventos.append("rollback")

    def close(self):
        self.eventos.append("close")


def test_ensaio_apaga_e_recarrega_mas_desfaz(dados):
    conn = Conexao()
    resumo = carga.carregar(conn, dados, apply=False, log=lambda _: None)
    assert conn.pedidos[0].startswith("TRUNCATE publico.senadores")
    assert "interno.verificacoes" in conn.pedidos[0]
    assert conn.eventos == ["rollback"]
    assert resumo["publico.senadores"] == 3


def test_apply_confirma(dados):
    conn = Conexao()
    carga.carregar(conn, dados, apply=True, log=lambda _: None)
    assert conn.eventos == ["commit"]


def test_contagem_diferente_desfaz_e_nao_confirma(dados):
    conn = Conexao(desvio=1)
    with pytest.raises(carga.CargaError, match="linha"):
        carga.carregar(conn, dados, apply=True, log=lambda _: None)
    assert "commit" not in conn.eventos
    assert conn.eventos[-1] == "rollback"


def test_run_recusa_antes_de_conectar_se_a_foto_nao_fecha(tmp_path, monkeypatch):
    arquivo = tmp_path / "limpo.sqlite"
    db = sqlite3.connect(arquivo)
    banco(sem=("salario",)).backup(db)
    db.close()
    monkeypatch.setattr(carga, "conectar", lambda url: pytest.fail("não devia conectar"))
    with pytest.raises(carga.CargaError, match="faltam verificações"):
        carga.run(arquivo, "postgresql://u:s@h/d", apply=False, log=lambda _: None)


def test_run_nao_mostra_a_senha(tmp_path, monkeypatch):
    arquivo = tmp_path / "limpo.sqlite"
    db = sqlite3.connect(arquivo)
    banco().backup(db)
    db.close()
    monkeypatch.setattr(carga, "conectar", lambda url: Conexao())
    linhas = []
    url = "postgresql://sd_carga:segredo@ep-x.neon.tech/db"
    carga.run(arquivo, url, apply=False, agora=AGORA, log=linhas.append)
    texto = "\n".join(linhas)
    assert "ep-x.neon.tech" in texto and "segredo" not in texto
