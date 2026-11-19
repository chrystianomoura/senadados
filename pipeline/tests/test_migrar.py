import pytest

from senadados_pipeline import migrar
from senadados_pipeline.config import MIGRACOES_DIR


class Cursor:
    def __init__(self, resposta):
        self.resposta = resposta

    def fetchone(self):
        return self.resposta

    def __iter__(self):
        return iter(self.resposta or [])


class ConexaoFalsa:
    """Guarda o que foi pedido, para conferir ensaio, gravação e desfazer."""

    def __init__(self, ja_aplicadas=None, existe_controle=True, falha_em=None):
        self.ja_aplicadas = ja_aplicadas or []
        self.existe_controle = existe_controle
        self.falha_em = falha_em
        self.pedidos = []
        self.eventos = []

    def execute(self, sql, params=None):
        self.pedidos.append((sql, params))
        if "to_regclass" in sql:
            return Cursor((self.existe_controle,))
        if sql.startswith("SELECT versao"):
            return Cursor([(v,) for v in self.ja_aplicadas])
        if self.falha_em and self.falha_em in sql:
            raise RuntimeError("erro do banco")
        return Cursor(None)

    def commit(self):
        self.eventos.append("commit")

    def rollback(self):
        self.eventos.append("rollback")

    def close(self):
        self.eventos.append("close")


def escrever(pasta, nomes):
    for nome in nomes:
        (pasta / nome).write_text(f"-- {nome}\nSELECT 1;\n", encoding="utf-8")


def test_as_migracoes_do_repositorio_estao_em_ordem_e_sem_buracos():
    arquivos = migrar.listar(MIGRACOES_DIR)
    assert [a.name for a in arquivos[:2]] == ["001_esquemas.sql", "002_papeis.sql"]


def test_listar_ordena_pelo_numero(tmp_path):
    escrever(tmp_path, ["002_b.sql", "001_a.sql", "003_c.sql"])
    assert [a.name for a in migrar.listar(tmp_path)] == ["001_a.sql", "002_b.sql", "003_c.sql"]


def test_nome_fora_do_padrao_e_erro(tmp_path):
    escrever(tmp_path, ["001_a.sql", "criar_tabela.sql"])
    with pytest.raises(migrar.MigracaoError, match="fora do padrão"):
        migrar.listar(tmp_path)


def test_buraco_na_numeracao_e_erro(tmp_path):
    escrever(tmp_path, ["001_a.sql", "003_c.sql"])
    with pytest.raises(migrar.MigracaoError, match="buraco"):
        migrar.listar(tmp_path)


def test_sem_tabela_de_controle_nenhuma_foi_aplicada():
    assert migrar.aplicadas(ConexaoFalsa(existe_controle=False)) == set()


def test_aplicadas_le_a_tabela_de_controle():
    conn = ConexaoFalsa(ja_aplicadas=["001_a.sql"])
    assert migrar.aplicadas(conn) == {"001_a.sql"}


def rodar(monkeypatch, tmp_path, conn, apply):
    escrever(tmp_path, ["001_a.sql", "002_b.sql"])
    monkeypatch.setattr(migrar, "conectar", lambda url: conn)
    url = "postgresql://u:segredo@host.exemplo/db"
    return migrar.run(url, apply=apply, diretorio=tmp_path, log=lambda _: None)


def test_ensaio_desfaz_tudo_e_nao_confirma(monkeypatch, tmp_path):
    conn = ConexaoFalsa(existe_controle=False)
    rodou = rodar(monkeypatch, tmp_path, conn, apply=False)
    assert rodou == ["001_a.sql", "002_b.sql"]
    assert "commit" not in conn.eventos
    assert conn.eventos == ["rollback", "close"]


def test_apply_confirma_e_registra_cada_migracao(monkeypatch, tmp_path):
    conn = ConexaoFalsa(existe_controle=False)
    rodar(monkeypatch, tmp_path, conn, apply=True)
    assert conn.eventos == ["commit", "close"]
    registradas = [p for sql, p in conn.pedidos if sql.startswith("INSERT INTO interno.migracoes")]
    assert registradas == [("001_a.sql",), ("002_b.sql",)]


def test_so_aplica_o_que_ainda_nao_foi_aplicado(monkeypatch, tmp_path):
    conn = ConexaoFalsa(ja_aplicadas=["001_a.sql"])
    assert rodar(monkeypatch, tmp_path, conn, apply=True) == ["002_b.sql"]


def test_erro_numa_migracao_desfaz_e_nao_confirma(monkeypatch, tmp_path):
    conn = ConexaoFalsa(existe_controle=False, falha_em="002_b.sql")
    with pytest.raises(RuntimeError):
        rodar(monkeypatch, tmp_path, conn, apply=True)
    assert "commit" not in conn.eventos
    assert conn.eventos[0] == "rollback"


def test_o_log_mostra_o_servidor_e_nunca_a_senha(monkeypatch, tmp_path):
    escrever(tmp_path, ["001_a.sql"])
    conn = ConexaoFalsa(existe_controle=False)
    monkeypatch.setattr(migrar, "conectar", lambda url: conn)
    linhas = []
    url = "postgresql://dono:segredo@ep-exemplo.neon.tech/db"
    migrar.run(url, apply=False, diretorio=tmp_path, log=linhas.append)
    texto = "\n".join(linhas)
    assert "ep-exemplo.neon.tech" in texto
    assert "segredo" not in texto
