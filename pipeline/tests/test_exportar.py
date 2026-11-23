import json
from datetime import UTC, date, datetime

import pytest

from senadados_pipeline import exportar

FEITO_EM = datetime(2026, 11, 19, 12, 0, tzinfo=UTC)
CNPJ = "11.111.111/0001-11"


def dados_base():
    """Três senadores: 1 com tudo provado, 2 com contato parcial, 3 provado sem uso de moradia."""
    return {
        "senadores": [
            (1, "ALAN RICK", "Titular", "AC", "REPUBLICANOS"),
            (2, "ANA PAULA LOBATO", "Titular", "MA", "PDT"),
            (3, "NELSINHO TRAD FILHO", "1º Suplente", "MS", "PSD"),
        ],
        "despesas_mensais": [
            (1, 2025, 12, "Divulgação da atividade parlamentar", 500, 1),
            (1, 2026, 1, "Divulgação da atividade parlamentar", 1000, 2),
            (1, 2026, 1, "Categoria nova do Senado", 500, 1),
            (1, 2026, 2, "Divulgação da atividade parlamentar", 1500, 3),
            (1, 2026, 3, "Passagens aéreas, aquáticas e terrestres nacionais", 1500, 1),
        ],
        "fornecedores_anuais": [
            (1, 2026, f"22.222.222/{i:04d}-22", f"EMPRESA {i}", 100 * i, 1) for i in range(1, 13)
        ] + [(1, 2026, CNPJ, "ALFA LTDA", 5000, 4)],
        "fornecedores_agrupados_anuais": [
            (1, 2026, "pessoa_fisica", 2, 400, 300),
            (1, 2026, "outro", 1, 50, 50),
        ],
        "contato": [
            (1, "Anexo 1", "(61) 3303-0001\n(61) 3303-0002\n", "sen.alan@senado.leg.br"),
            (2, None, None, "sen.ana@senado.leg.br"),
        ],
        "perfil": [
            (1, "https://legis.senado.leg.br/senadores/fotos-oficiais/1", date(2023, 2, 1),
             date(2031, 1, 31)),
            (2, None, date(2019, 2, 1), date(2027, 1, 31)),
        ],
        "equipe": [(1, 2025, 10), (1, 2026, 15)],
        "moradia_verificada": [(1, 2026), (3, 2026)],
        "moradia_meses": [
            (1, 2026, "2026-02", False, True),
            (1, 2026, "2026-01", False, True),
        ],
        "salario": [(1, 2026, 9, 4500000, 3000000), (1, 2026, 10, 4600000, 3100000)],
        "verificacoes_resumo": [("cota", 2026, 73, 7, 0, 0, FEITO_EM)],
        "verificacoes_motivos": [("cota", 2009, "oculto", "motivo da lista fechada", 5)],
        "metadados": [
            ("anos", "2008-2026"),
            ("carregado_em", "2026-11-19T12:00:00+00:00"),
            ("data_referencia", "2026-11-18"),
            ("senadores", "3"),
        ],
    }


@pytest.fixture
def saida():
    return exportar.montar(dados_base())


def test_slug_tira_acento_e_liga_com_hifen():
    assert exportar.slug("ALAN RICK") == "alan-rick"
    assert exportar.slug("ÂNGELO Coronel") == "angelo-coronel"
    assert exportar.slug("Nelsinho Trad Filho") == "nelsinho-trad-filho"


def test_a_lista_tem_um_item_por_senador_em_ordem_de_codigo(saida):
    assert [s["codigo"] for s in saida["senadores"]] == [1, 2, 3]
    assert saida["senadores"][0] == {
        "codigo": 1, "slug": "alan-rick", "nome": "ALAN RICK", "tipo": "Titular", "uf": "AC",
        "partido": "REPUBLICANOS",
        "foto_url": "https://legis.senado.leg.br/senadores/fotos-oficiais/1",
    }


def test_metadados(saida):
    assert saida["metadados"] == {
        "versao_contrato": 2, "data_referencia": "2026-11-18",
        "carregado_em": "2026-11-19T12:00:00+00:00", "anos": "2008-2026", "senadores": 3,
        "fonte": "Senado Federal, dados abertos",
    }


def test_quem_e_leva_a_foto_com_credito_e_o_mandato_com_anos_e_datas(saida):
    assert saida["perfis"]["alan-rick"]["quem_e"] == {
        "foto": {
            "url": "https://legis.senado.leg.br/senadores/fotos-oficiais/1",
            "credito": "Foto oficial publicada pelo Senado Federal",
        },
        "mandato": {
            "inicio": 2023, "fim": 2031, "inicio_data": "2023-02-01", "fim_data": "2031-01-31",
        },
    }


def test_quem_e_mantem_so_a_parte_provada_e_vira_nulo_sem_nenhuma(saida):
    assert saida["perfis"]["ana-paula-lobato"]["quem_e"]["foto"] is None
    assert saida["perfis"]["ana-paula-lobato"]["quem_e"]["mandato"]["fim"] == 2027
    assert saida["perfis"]["nelsinho-trad-filho"]["quem_e"] is None
    dados = dados_base()
    dados["perfil"] = [(1, None, None, None)]
    assert exportar.montar(dados)["perfis"]["alan-rick"]["quem_e"] is None


def test_a_lista_so_traz_foto_url_de_quem_tem_foto_provada(saida):
    por_codigo = {item["codigo"]: item for item in saida["senadores"]}
    assert por_codigo[1]["foto_url"] == "https://legis.senado.leg.br/senadores/fotos-oficiais/1"
    assert "foto_url" not in por_codigo[2] and "foto_url" not in por_codigo[3]


def test_salario_vale_o_mes_mais_recente(saida):
    assert saida["perfis"]["alan-rick"]["salario"] == {
        "ano": 2026, "mes": 10, "basica_centavos": 4600000, "liquida_centavos": 3100000,
    }
    assert saida["perfis"]["ana-paula-lobato"]["salario"] is None


def test_cota_por_ano_com_meses_categorias_e_maior_mes(saida):
    anos = {a["ano"]: a for a in saida["perfis"]["alan-rick"]["cota"]["anos"]}
    assert list(anos) == [2025, 2026]
    a = anos[2026]
    assert a["parcial"] is True and anos[2025]["parcial"] is False
    assert a["total_centavos"] == 4500
    assert a["meses"] == [
        {"mes": 1, "total_centavos": 1500}, {"mes": 2, "total_centavos": 1500},
        {"mes": 3, "total_centavos": 1500},
    ]
    assert a["maior_mes"] == {"mes": 1, "total_centavos": 1500}  # empate: o mês mais cedo


def test_categoria_tem_nome_curto_e_nome_oficial(saida):
    categorias = saida["perfis"]["alan-rick"]["cota"]["anos"][1]["categorias"]
    nomes = {c["nome_oficial"]: c["nome"] for c in categorias}
    passagens = "Passagens aéreas, aquáticas e terrestres nacionais"
    assert nomes[passagens] == "Passagens dentro do Brasil"
    assert nomes["Categoria nova do Senado"] == "Categoria nova do Senado"  # sem nome curto


def test_categorias_vem_da_maior_para_a_menor(saida):
    categorias = saida["perfis"]["alan-rick"]["cota"]["anos"][1]["categorias"]
    totais = [c["total_centavos"] for c in categorias]
    assert totais == sorted(totais, reverse=True)


def test_senador_sem_cota_provada_tem_cota_nula(saida):
    assert saida["perfis"]["ana-paula-lobato"]["cota"] is None


def test_fornecedores_so_as_10_maiores_empresas_e_conta_o_total(saida):
    f = saida["perfis"]["alan-rick"]["fornecedores"]["anos"][0]
    assert f["total_empresas"] == 13 and len(f["empresas"]) == 10
    assert f["empresas"][0] == {
        "cnpj": CNPJ, "nome": "ALFA LTDA", "qtd_despesas": 4, "total_centavos": 5000,
    }
    valores = [e["total_centavos"] for e in f["empresas"]]
    assert valores == sorted(valores, reverse=True)


def test_agrupados_nao_levam_nome_nem_documento(saida):
    f = saida["perfis"]["alan-rick"]["fornecedores"]["anos"][0]
    assert [g["tipo"] for g in f["agrupados"]] == ["outro", "pessoa_fisica"]  # ordem alfabética
    pessoas = f["agrupados"][1]
    assert pessoas == {
        "tipo": "pessoa_fisica", "qtd_despesas": 2, "total_centavos": 400, "maior_centavos": 300,
    }
    assert set(pessoas) == {"tipo", "qtd_despesas", "total_centavos", "maior_centavos"}


def test_equipe_vale_o_ano_mais_recente(saida):
    assert saida["perfis"]["alan-rick"]["equipe"] == {"ano": 2026, "pessoas": 15}
    assert saida["perfis"]["ana-paula-lobato"]["equipe"] is None


def test_contato_separa_os_telefones_e_ignora_linha_vazia(saida):
    assert saida["perfis"]["alan-rick"]["contato"] == {
        "endereco": "Anexo 1", "telefones": ["(61) 3303-0001", "(61) 3303-0002"],
        "email": "sen.alan@senado.leg.br",
    }


def test_contato_parcial_mantem_so_o_que_foi_provado(saida):
    assert saida["perfis"]["ana-paula-lobato"]["contato"] == {
        "endereco": None, "telefones": [], "email": "sen.ana@senado.leg.br",
    }


def test_contato_todo_vazio_vira_nulo():
    dados = dados_base()
    dados["contato"] = [(1, None, None, None)]
    assert exportar.montar(dados)["perfis"]["alan-rick"]["contato"] is None


def test_moradia_traz_um_bloco_por_ano_provado_do_mais_antigo_ao_mais_recente():
    dados = dados_base()
    dados["moradia_verificada"] = [(1, 2025), (1, 2026)]
    dados["moradia_meses"] = [
        (1, 2026, "2026-01", False, True),
        (1, 2025, "2025-12", True, False),
    ]
    moradia = exportar.montar(dados)["perfis"]["alan-rick"]["moradia"]
    assert [a["ano"] for a in moradia["anos"]] == [2025, 2026]
    assert moradia["anos"][0]["meses"] == [
        {"mes": "2025-12", "auxilio_moradia": True, "imovel_funcional": False}
    ]


def test_moradia_em_ordem_de_mes(saida):
    meses = saida["perfis"]["alan-rick"]["moradia"]["anos"][-1]["meses"]
    assert [m["mes"] for m in meses] == ["2026-01", "2026-02"]


def test_moradia_provada_sem_uso_tem_meses_vazio_e_nao_provada_e_nula(saida):
    assert saida["perfis"]["nelsinho-trad-filho"]["moradia"] == {
        "anos": [{"ano": 2026, "meses": []}]
    }
    assert saida["perfis"]["ana-paula-lobato"]["moradia"] is None


def test_verificacoes_so_tem_contagens_e_motivos_sem_nomes(saida):
    v = saida["verificacoes"]
    assert v["resumo"][0]["verificado_em"] == "2026-11-19T12:00:00+00:00"
    assert v["motivos"] == [{"verificacao": "cota", "ano": 2009, "situacao": "oculto",
                             "motivo": "motivo da lista fechada", "qtd": 5}]


def test_recusa_dois_senadores_com_o_mesmo_endereco():
    dados = dados_base()
    dados["senadores"].append((4, "Alan  Rick", "Titular", "AC", "X"))
    dados["metadados"] = [(k, "4" if k == "senadores" else v) for k, v in dados["metadados"]]
    with pytest.raises(exportar.ExportacaoError, match="endereço repetido"):
        exportar.montar(dados)


def test_recusa_quando_o_numero_de_senadores_nao_fecha_com_os_metadados():
    dados = dados_base()
    dados["metadados"] = [(k, "81" if k == "senadores" else v) for k, v in dados["metadados"]]
    with pytest.raises(exportar.ExportacaoError, match="nos metadados"):
        exportar.montar(dados)


def test_recusa_algo_com_formato_de_cpf():
    dados = dados_base()
    dados["contato"] = [(1, "CPF 123.456.789-01", None, None)]
    with pytest.raises(exportar.ExportacaoError, match="formato de CPF"):
        exportar.montar(dados)
    dados["contato"] = [(1, "doc 123.***.***-45", None, None)]
    with pytest.raises(exportar.ExportacaoError, match="formato de CPF"):
        exportar.montar(dados)


def test_cnpj_e_nome_de_empresa_com_cpf_no_nome_nao_sao_confundidos_com_cpf():
    dados = dados_base()
    dados["fornecedores_anuais"] = [(1, 2026, CNPJ, "CPFL ENERGIA S.A.", 100, 1)]
    assert exportar.montar(dados)["perfis"]["alan-rick"]["fornecedores"] is not None


def test_recusa_cota_cujas_categorias_nao_somam_o_total(saida):
    saida["perfis"]["alan-rick"]["cota"]["anos"][1]["categorias"][0]["total_centavos"] += 1
    with pytest.raises(exportar.ExportacaoError, match="categorias não somam"):
        exportar.conferir(saida)


def test_gravar_cria_todos_os_arquivos_do_contrato(tmp_path, saida):
    pasta = tmp_path / "dados"
    assert exportar.gravar(pasta, saida) == 6
    nomes = sorted(p.name for p in pasta.iterdir())
    assert nomes == ["metadados.json", "senadores", "senadores.json", "verificacoes.json"]
    perfil = json.loads((pasta / "senadores" / "alan-rick.json").read_text(encoding="utf-8"))
    assert perfil["nome"] == "ALAN RICK" and perfil["quem_e"]["mandato"]["inicio"] == 2023
    assert not (tmp_path / "dados.tmp").exists()


def test_gravar_troca_a_pasta_inteira_e_nao_deixa_arquivo_de_quem_saiu(tmp_path, saida):
    pasta = tmp_path / "dados"
    exportar.gravar(pasta, saida)
    assert (pasta / "senadores" / "nelsinho-trad-filho.json").exists()
    dados = dados_base()
    dados["senadores"] = dados["senadores"][:2]
    dados["metadados"] = [(k, "2" if k == "senadores" else v) for k, v in dados["metadados"]]
    exportar.gravar(pasta, exportar.montar(dados))
    assert not (pasta / "senadores" / "nelsinho-trad-filho.json").exists()


def test_se_a_montagem_falha_a_pasta_anterior_continua(tmp_path, saida):
    pasta = tmp_path / "dados"
    exportar.gravar(pasta, saida)
    dados = dados_base()
    dados["senadores"].append((4, "Alan Rick", "Titular", "AC", "X"))
    with pytest.raises(exportar.ExportacaoError):
        exportar.gravar(pasta, exportar.montar(dados))
    assert (pasta / "senadores" / "alan-rick.json").exists()


class Cursor:
    def __init__(self, linhas):
        self.linhas = linhas

    def fetchall(self):
        return self.linhas


class Conexao:
    def __init__(self, dados):
        self.dados, self.pedidos, self.fechada = dados, [], False

    def execute(self, sql):
        self.pedidos.append(sql)
        tabela = sql.split("FROM publico.")[1].split()[0]
        return Cursor(self.dados[tabela])

    def close(self):
        self.fechada = True


def test_ler_so_faz_select_no_esquema_publico_e_ordena(monkeypatch):
    conn = Conexao(dados_base())
    dados = exportar.ler(conn)
    assert set(dados) == set(exportar.LEITURAS)
    assert all(
        p.startswith("SELECT") and "FROM publico." in p and "ORDER BY" in p for p in conn.pedidos
    )
    assert not any("interno" in p for p in conn.pedidos)


def test_run_nao_mostra_a_senha_e_fecha_a_conexao(monkeypatch, tmp_path):
    conn = Conexao(dados_base())
    monkeypatch.setattr(exportar, "conectar", lambda url: conn)
    linhas = []
    url = "postgresql://sd_leitura:segredo@ep-x.neon.tech/db"
    exportar.run(url, tmp_path / "d", log=linhas.append)
    texto = "\n".join(linhas)
    assert "ep-x.neon.tech" in texto and "segredo" not in texto
    assert conn.fechada
