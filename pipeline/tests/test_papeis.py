import pytest

from senadados_pipeline import papeis

URL_DONO = "postgresql://dono:senha-do-dono@ep-x.c-9.us-east-2.aws.neon.tech/neondb?sslmode=require"


class Cursor:
    def __init__(self, resposta):
        self.resposta = resposta

    def fetchone(self):
        return self.resposta


class Conexao:
    def __init__(self, existentes=()):
        self.existentes = set(existentes)
        self.criados, self.eventos = [], []

    def execute(self, consulta, params=None):
        if isinstance(consulta, str) and consulta.startswith("SELECT 1 FROM pg_roles"):
            return Cursor((1,) if params[0] in self.existentes else None)
        self.criados.append(consulta)
        return Cursor(None)

    def commit(self):
        self.eventos.append("commit")

    def rollback(self):
        self.eventos.append("rollback")

    def close(self):
        self.eventos.append("close")


@pytest.fixture(autouse=True)
def sem_driver(monkeypatch):
    # o SQL do CREATE ROLE é montado pelo psycopg; aqui só importa que foi pedido
    monkeypatch.setattr(
        papeis, "criar_papel", lambda conn, papel, senha: conn.criados.append(papel)
    )


def rodar(monkeypatch, tmp_path, conn, env=None):
    monkeypatch.setattr(papeis, "conectar", lambda url: conn)
    linhas = []
    senhas = iter(["Senha/Um+1", "Senha/Dois+2"])
    criados = papeis.run(
        URL_DONO, env or tmp_path / ".env", log=linhas.append, gerar_senha=lambda: next(senhas)
    )
    return criados, linhas


def test_montar_url_troca_so_usuario_e_senha():
    url = papeis.montar_url(URL_DONO, "sd_carga", "a/b+c")
    assert url.startswith("postgresql://sd_carga:a%2Fb%2Bc@ep-x.c-9.us-east-2.aws.neon.tech/neondb")
    assert url.endswith("?sslmode=require")


def test_cria_os_dois_papeis_e_grava_as_urls_no_env(monkeypatch, tmp_path):
    conn = Conexao()
    criados, _ = rodar(monkeypatch, tmp_path, conn)
    assert criados == ["sd_carga", "sd_leitura"]
    texto = (tmp_path / ".env").read_text(encoding="utf-8")
    assert "DATABASE_URL_CARGA=postgresql://sd_carga:" in texto
    assert "DATABASE_URL_LEITURA=postgresql://sd_leitura:" in texto
    assert conn.eventos == ["commit", "close"]


def test_o_env_fica_so_para_o_dono_e_nao_perde_o_que_ja_tinha(monkeypatch, tmp_path):
    env = tmp_path / ".env"
    env.write_text("DATABASE_URL=algo", encoding="utf-8")  # sem quebra de linha no fim
    rodar(monkeypatch, tmp_path, Conexao(), env)
    assert env.read_text(encoding="utf-8").startswith("DATABASE_URL=algo\nDATABASE_URL_CARGA=")
    assert oct(env.stat().st_mode & 0o777) == "0o600"


def test_a_senha_nunca_aparece_no_registro(monkeypatch, tmp_path):
    _, linhas = rodar(monkeypatch, tmp_path, Conexao())
    texto = "\n".join(linhas)
    assert "ep-x.c-9.us-east-2.aws.neon.tech" in texto
    assert "Senha" not in texto and "senha-do-dono" not in texto


def test_idempotente_nao_troca_senha_de_papel_ja_pronto(monkeypatch, tmp_path):
    env = tmp_path / ".env"
    env.write_text("DATABASE_URL_CARGA=x\nDATABASE_URL_LEITURA=y\n", encoding="utf-8")
    conn = Conexao(existentes={"sd_carga", "sd_leitura"})
    criados, _ = rodar(monkeypatch, tmp_path, conn, env)
    assert criados == []
    assert env.read_text(encoding="utf-8") == "DATABASE_URL_CARGA=x\nDATABASE_URL_LEITURA=y\n"


def test_papel_existe_sem_url_no_env_e_erro_claro(monkeypatch, tmp_path):
    conn = Conexao(existentes={"sd_carga"})
    with pytest.raises(papeis.PapelError, match="redefina a senha"):
        rodar(monkeypatch, tmp_path, conn)
    assert "commit" not in conn.eventos


def test_url_no_env_de_outro_banco_e_erro_claro(monkeypatch, tmp_path):
    env = tmp_path / ".env"
    env.write_text("DATABASE_URL_CARGA=x\n", encoding="utf-8")
    with pytest.raises(papeis.PapelError, match="de outro banco"):
        rodar(monkeypatch, tmp_path, Conexao(), env)
