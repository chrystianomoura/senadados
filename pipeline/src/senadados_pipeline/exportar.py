"""Gera os arquivos JSON do site a partir do esquema `publico` do banco na nuvem.

O contrato (quais arquivos, quais campos) está em `docs/contrato-dos-dados.md` (D044). O site só lê
estes arquivos. Eles nascem do esquema `publico`, que só tem o que passou nas verificações (D025);
um bloco que não foi provado vem como `null`, e o site não mostra nada no lugar.

Lê com o papel `sd_leitura` (`DATABASE_URL_LEITURA`), que só enxerga o `publico`. Não grava nada no
banco. Falha fechado: se alguma conferência quebrar, nenhum arquivo é gravado, e a pasta de saída
anterior continua como estava. A pasta é trocada inteira, então o arquivo de quem saiu da lista
nunca fica para trás (D026).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

from senadados_pipeline.banco import BancoError, conectar, host_de, url_do_ambiente
from senadados_pipeline.config import ROOT

VERSAO_CONTRATO = 2  # 2: `moradia` passou a ter `anos` (D049)
FONTE = "Senado Federal, dados abertos"
SAIDA_PADRAO = ROOT / "web" / "dados"
MAX_EMPRESAS = 10

# CPF inteiro (123.456.789-01) ou mascarado (123.***.***-45), como o Senado publica.
CPF = re.compile(r"\b\d{3}\.(?:\d{3}|\*{3})\.(?:\d{3}|\*{3})-\d{2}\b")

# Nome oficial da categoria -> nome curto para o cidadão (tabela de docs/fontes-de-dados.md).
# Categoria nova do Senado não está aqui: o nome oficial vale nos dois campos.
NOMES_CURTOS = {
    "Locomoção, hospedagem, alimentação, combustíveis e lubrificantes":
        "Locomoção, hospedagem e alimentação",
    "Contratação de consultorias, assessorias, pesquisas, trabalhos técnicos e outros serviços "
    "de apoio ao exercício do mandato parlamentar": "Consultorias e serviços de apoio ao mandato",
    "Divulgação da atividade parlamentar": "Divulgação da atividade parlamentar",
    "Aluguel de imóveis para escritório político, compreendendo despesas concernentes a eles.":
        "Aluguel do escritório político",
    "Passagens aéreas, aquáticas e terrestres nacionais": "Passagens dentro do Brasil",
    "Aquisição de material de consumo para uso no escritório político, inclusive aquisição ou "
    "locação de software, despesas postais, aquisição de publicações, locação de móveis e de "
    "equipamentos.": "Material de consumo do escritório político",
    "Serviços de Segurança Privada": "Segurança privada",
    "Sem categoria": "Sem categoria",
}

# O que se lê do esquema publico: tabela -> (colunas, ordem). A ordem fixa ajuda a reproduzir o
# resultado; as listas do contrato também são ordenadas aqui, sem depender do banco.
LEITURAS = {
    "senadores": ("cod_senador, nome, tipo, uf, partido", "cod_senador"),
    "despesas_mensais": (
        "cod_senador, ano, mes, categoria, valor_centavos, qtd_despesas",
        "cod_senador, ano, mes, categoria",
    ),
    "fornecedores_anuais": (
        "cod_senador, ano, cnpj, nome, valor_centavos, qtd_despesas", "cod_senador, ano, cnpj"
    ),
    "fornecedores_agrupados_anuais": (
        "cod_senador, ano, tipo, qtd_despesas, total_centavos, maior_centavos",
        "cod_senador, ano, tipo",
    ),
    "contato": ("cod_senador, endereco, telefones, email", "cod_senador"),
    "perfil": ("cod_senador, foto_url, mandato_inicio, mandato_fim", "cod_senador"),
    "equipe": ("cod_senador, ano, pessoas", "cod_senador, ano"),
    "moradia_verificada": ("cod_senador, ano", "cod_senador, ano"),
    "moradia_meses": (
        "cod_senador, ano, mes, auxilio_moradia, imovel_funcional", "cod_senador, mes"
    ),
    "salario": (
        "cod_senador, ano, mes, remuneracao_basica_centavos, remuneracao_liquida_centavos",
        "cod_senador, ano, mes",
    ),
    "verificacoes_resumo": (
        "verificacao, ano, identicos, explicados, pendentes, ocultos, verificado_em",
        "verificacao, ano",
    ),
    "verificacoes_motivos": (
        "verificacao, ano, situacao, motivo, qtd", "verificacao, ano, situacao, motivo"
    ),
    "metadados": ("chave, valor", "chave"),
}


class ExportacaoError(Exception):
    """Os dados não estão em condições de virar os arquivos do site."""


def slug(nome: str) -> str:
    """Endereço da página: minúsculas, sem acento, palavras ligadas por hífen."""
    texto = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", texto).strip("-")


def _iso(valor) -> str:
    return valor.isoformat(timespec="seconds") if isinstance(valor, datetime) else str(valor)


def _por_senador(linhas: list[tuple]) -> dict[int, list[tuple]]:
    agrupado: dict[int, list[tuple]] = {}
    for linha in linhas:
        agrupado.setdefault(linha[0], []).append(linha)
    return agrupado


# ---------------------------------------------------------------------------
# Blocos do perfil
# ---------------------------------------------------------------------------
CREDITO_FOTO = "Foto oficial publicada pelo Senado Federal"


def _iso_data(valor) -> str:
    """A data como `AAAA-MM-DD`, venha do banco como `date` ou já como texto."""
    return valor.isoformat() if hasattr(valor, "isoformat") else str(valor)


def bloco_quem_e(linha: tuple | None) -> dict | None:
    """Foto e mandato, cada parte `null` se não foi provada. Sem nenhuma das duas, `null`.

    `inicio` e `fim` são os anos (o que o site mostra); as datas completas vão junto (D045).
    """
    if linha is None:
        return None
    _cod, foto, inicio, fim = linha
    foto_bloco = {"url": foto, "credito": CREDITO_FOTO} if foto else None
    mandato = None
    if inicio and fim:
        a, b = _iso_data(inicio), _iso_data(fim)
        mandato = {"inicio": int(a[:4]), "fim": int(b[:4]), "inicio_data": a, "fim_data": b}
    if foto_bloco is None and mandato is None:
        return None
    return {"foto": foto_bloco, "mandato": mandato}


def bloco_salario(linhas: list[tuple]) -> dict | None:
    if not linhas:
        return None
    _cod, ano, mes, basica, liquida = max(linhas, key=lambda linha: (linha[1], linha[2]))
    return {"ano": ano, "mes": mes, "basica_centavos": basica, "liquida_centavos": liquida}


def bloco_cota(linhas: list[tuple], ano_parcial: int) -> dict | None:
    """Verba por ano, mês e categoria. `maior_mes` é só o fato (D030): o mês de maior valor."""
    if not linhas:
        return None
    por_ano: dict[int, list[tuple]] = {}
    for linha in linhas:
        por_ano.setdefault(linha[1], []).append(linha)
    anos = []
    for ano in sorted(por_ano):
        meses: dict[int, int] = {}
        categorias: dict[str, int] = {}
        for _cod, _ano, mes, categoria, valor, _qtd in por_ano[ano]:
            meses[mes] = meses.get(mes, 0) + valor
            categorias[categoria] = categorias.get(categoria, 0) + valor
        total = sum(meses.values())
        maior = min(meses, key=lambda mes: (-meses[mes], mes))  # empate: o mês mais cedo
        anos.append(
            {
                "ano": ano,
                "parcial": ano == ano_parcial,
                "total_centavos": total,
                "meses": [{"mes": mes, "total_centavos": meses[mes]} for mes in sorted(meses)],
                "categorias": [
                    {
                        "nome": NOMES_CURTOS.get(oficial, oficial),
                        "nome_oficial": oficial,
                        "total_centavos": categorias[oficial],
                    }
                    for oficial in sorted(categorias, key=lambda c: (-categorias[c], c))
                ],
                "maior_mes": {"mes": maior, "total_centavos": meses[maior]},
            }
        )
    return {"anos": anos}


def bloco_fornecedores(empresas: list[tuple], agrupados: list[tuple]) -> dict | None:
    """As maiores empresas por ano e os grupos sem nome (D008). Há até 1.503 empresas por ano."""
    if not empresas and not agrupados:
        return None
    anos = sorted({linha[1] for linha in empresas} | {linha[1] for linha in agrupados})
    saida = []
    for ano in anos:
        do_ano = [linha for linha in empresas if linha[1] == ano]
        maiores = sorted(do_ano, key=lambda linha: (-linha[4], linha[2]))[:MAX_EMPRESAS]
        saida.append(
            {
                "ano": ano,
                "empresas": [
                    {"cnpj": cnpj, "nome": nome, "qtd_despesas": qtd, "total_centavos": valor}
                    for _cod, _ano, cnpj, nome, valor, qtd in maiores
                ],
                "total_empresas": len(do_ano),
                "agrupados": [
                    {
                        "tipo": tipo,
                        "qtd_despesas": qtd,
                        "total_centavos": total,
                        "maior_centavos": maior,
                    }
                    for _cod, a, tipo, qtd, total, maior in sorted(
                        agrupados, key=lambda linha: linha[2]
                    )
                    if a == ano
                ],
            }
        )
    return {"anos": saida}


def bloco_equipe(linhas: list[tuple]) -> dict | None:
    if not linhas:
        return None
    _cod, ano, pessoas = max(linhas, key=lambda linha: linha[1])
    return {"ano": ano, "pessoas": pessoas}


def bloco_contato(linha: tuple | None) -> dict | None:
    if linha is None:
        return None
    _cod, endereco, telefones, email = linha
    lista = [t.strip() for t in (telefones or "").splitlines() if t.strip()]
    if endereco is None and not lista and email is None:
        return None
    return {"endereco": endereco, "telefones": lista, "email": email}


def bloco_moradia(verificada: list[tuple], meses: list[tuple]) -> dict | None:
    """Moradia por ano. `null` se nenhum ano foi provado.

    Um ano provado e sem nenhum mês de uso traz `meses` vazio (o senador não usou nenhum benefício).
    """
    if not verificada:
        return None
    anos = []
    for ano in sorted({linha[1] for linha in verificada}):
        anos.append(
            {
                "ano": ano,
                "meses": [
                    {"mes": mes, "auxilio_moradia": auxilio, "imovel_funcional": imovel}
                    for _cod, a, mes, auxilio, imovel in sorted(meses, key=lambda linha: linha[2])
                    if a == ano
                ],
            }
        )
    return {"anos": anos}


# ---------------------------------------------------------------------------
# Montagem e conferência
# ---------------------------------------------------------------------------
def montar(dados: dict[str, list[tuple]]) -> dict:
    """Devolve tudo o que vai para a pasta de saída: metadados, lista, perfis e verificações."""
    meta = dict(dados["metadados"])
    ano_parcial = int(meta["data_referencia"][:4])

    slugs: dict[str, int] = {}
    for cod, nome, *_ in dados["senadores"]:
        chave = slug(nome)
        if not chave:
            raise ExportacaoError(f"o nome do senador {cod} não gera um endereço")
        if chave in slugs:
            raise ExportacaoError(f"endereço repetido '{chave}' (senadores {slugs[chave]} e {cod})")
        slugs[chave] = cod

    cota = _por_senador(dados["despesas_mensais"])
    empresas = _por_senador(dados["fornecedores_anuais"])
    agrupados = _por_senador(dados["fornecedores_agrupados_anuais"])
    contatos = {linha[0]: linha for linha in dados["contato"]}
    perfis_quem_e = {linha[0]: linha for linha in dados["perfil"]}
    equipes = _por_senador(dados["equipe"])
    moradia_ok = _por_senador(dados["moradia_verificada"])
    moradia = _por_senador(dados["moradia_meses"])
    salarios = _por_senador(dados["salario"])

    lista, perfis = [], {}
    for cod, nome, tipo, uf, partido in dados["senadores"]:
        endereco = slug(nome)
        base = {"codigo": cod, "slug": endereco, "nome": nome, "tipo": tipo, "uf": uf,
                "partido": partido}
        quem_e = bloco_quem_e(perfis_quem_e.get(cod))
        # A lista da home mostra a foto (decidido em 23/11/2026); o endereço só vai se foi provado.
        com_foto = bool(quem_e and quem_e["foto"])
        lista.append({**base, "foto_url": quem_e["foto"]["url"]} if com_foto else base)
        perfis[endereco] = {
            **base,
            "quem_e": quem_e,
            "salario": bloco_salario(salarios.get(cod, [])),
            "cota": bloco_cota(cota.get(cod, []), ano_parcial),
            "fornecedores": bloco_fornecedores(empresas.get(cod, []), agrupados.get(cod, [])),
            "equipe": bloco_equipe(equipes.get(cod, [])),
            "contato": bloco_contato(contatos.get(cod)),
            "moradia": bloco_moradia(moradia_ok.get(cod, []), moradia.get(cod, [])),
        }

    resultado = {
        "metadados": {
            "versao_contrato": VERSAO_CONTRATO,
            "data_referencia": meta["data_referencia"],
            "carregado_em": meta["carregado_em"],
            "anos": meta["anos"],
            "senadores": int(meta["senadores"]),
            "fonte": FONTE,
        },
        "senadores": lista,
        "perfis": perfis,
        "verificacoes": {
            "resumo": [
                {"verificacao": v, "ano": a, "identicos": i, "explicados": e, "pendentes": p,
                 "ocultos": o, "verificado_em": _iso(q)}
                for v, a, i, e, p, o, q in dados["verificacoes_resumo"]
            ],
            "motivos": [
                {"verificacao": v, "ano": a, "situacao": s, "motivo": m, "qtd": n}
                for v, a, s, m, n in dados["verificacoes_motivos"]
            ],
        },
    }
    conferir(resultado)
    return resultado


def conferir(resultado: dict) -> None:
    """Conferências internas. Se qualquer uma falhar, nada é gravado."""
    if len(resultado["senadores"]) != resultado["metadados"]["senadores"]:
        raise ExportacaoError(
            f"{len(resultado['senadores'])} senadores no banco contra "
            f"{resultado['metadados']['senadores']} nos metadados"
        )
    for endereco, perfil in resultado["perfis"].items():
        cota = perfil["cota"]
        for ano in (cota or {"anos": []})["anos"]:
            if sum(m["total_centavos"] for m in ano["meses"]) != ano["total_centavos"]:
                raise ExportacaoError(f"{endereco} {ano['ano']}: os meses não somam o total")
            if sum(c["total_centavos"] for c in ano["categorias"]) != ano["total_centavos"]:
                raise ExportacaoError(f"{endereco} {ano['ano']}: as categorias não somam o total")
    # Nenhum CPF, inteiro ou mascarado, em lugar nenhum (D008). O CNPJ de empresa tem outro formato.
    texto = json.dumps(resultado, ensure_ascii=False)
    if CPF.search(texto):
        raise ExportacaoError("o resultado tem algo com formato de CPF: o contrato não permite")


# ---------------------------------------------------------------------------
# Leitura do banco e gravação
# ---------------------------------------------------------------------------
def ler(conn) -> dict[str, list[tuple]]:
    """Lê as tabelas do esquema publico, só leitura."""
    dados = {}
    for tabela, (colunas, ordem) in LEITURAS.items():
        dados[tabela] = [
            tuple(linha)
            for linha in conn.execute(
                f"SELECT {colunas} FROM publico.{tabela} ORDER BY {ordem}"
            ).fetchall()
        ]
    return dados


def _gravar_json(caminho: Path, conteudo) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(
        json.dumps(conteudo, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8"
    )


def gravar(saida: Path, resultado: dict) -> int:
    """Grava numa pasta temporária e a troca pela de saída. Devolve quantos arquivos gerou."""
    temporaria = saida.with_name(saida.name + ".tmp")
    if temporaria.exists():
        shutil.rmtree(temporaria)
    try:
        _gravar_json(temporaria / "metadados.json", resultado["metadados"])
        _gravar_json(temporaria / "senadores.json", resultado["senadores"])
        _gravar_json(temporaria / "verificacoes.json", resultado["verificacoes"])
        for endereco, perfil in resultado["perfis"].items():
            _gravar_json(temporaria / "senadores" / f"{endereco}.json", perfil)
        if saida.exists():
            shutil.rmtree(saida)
        temporaria.replace(saida)
    finally:
        if temporaria.exists():
            shutil.rmtree(temporaria)
    return 3 + len(resultado["perfis"])


def run(url: str, saida: Path = SAIDA_PADRAO, log=print) -> int:
    log(f"Banco: {host_de(url)} (só leitura)")
    conn = conectar(url)
    try:
        dados = ler(conn)
    finally:
        conn.close()
    resultado = montar(dados)
    arquivos = gravar(saida, resultado)
    referencia = resultado["metadados"]["data_referencia"]
    log(f"{arquivos} arquivos gravados em {saida} (dados de {referencia})")
    return arquivos


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gera os arquivos JSON do site.")
    parser.add_argument("--saida", type=Path, default=SAIDA_PADRAO, help="pasta de saída")
    args = parser.parse_args(argv)
    try:
        run(url_do_ambiente("DATABASE_URL_LEITURA"), args.saida)
    except (ExportacaoError, BancoError) as error:
        print(f"erro: {error}", file=sys.stderr)
        return 1
    except Exception as error:  # erro do banco: nada foi gravado
        print(f"erro, nada foi gravado: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
