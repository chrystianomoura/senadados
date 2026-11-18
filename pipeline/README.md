# Pipeline

Código em Python que coleta, limpa e verifica os dados abertos do Senado. Hoje só a **coleta** existe; a validação, a limpeza e a verificação são as próximas etapas ([ordem de construção](../docs/escopo.md#13-ordem-de-construção)).

## O que a coleta faz

- Baixa a **lista dos senadores em exercício** (API administrativa do Senado).
- Baixa as **despesas da cota (CEAPS)** de cada ano pela API, a fonte principal ([D005](../docs/decisoes.md#d005-api-como-fonte-principal-csv-para-conferência)).
- **Grava só as despesas de quem está na lista** ([D026](../docs/decisoes.md#d026-só-senadores-em-exercício)). A API devolve também ex-senadores, e esses dados não ficam no disco.
- Grava o que o Senado devolve **sem alterar**; a limpeza vem depois.
- **Não sobrescreve** arquivo que já existe, a menos que se peça.
- Se o Senado devolver um formato diferente do esperado, **para com erro** em vez de gravar dado errado.

Os arquivos vão para `data/raw/` (fora do git, [D014](../docs/decisoes.md#d014-dados-crus-fora-do-git)).

## Como rodar

Precisa do [uv](https://docs.astral.sh/uv/). Dentro de `pipeline/`:

```bash
uv sync
```

```bash
uv run python -m senadados_pipeline.coleta --anos 2026
```

Opções: `--anos` (por exemplo `2026`, `2023-2026` ou `2008,2010-2012`; o padrão é 2008 até o ano atual), `--saida` (pasta de saída; o padrão é `data/raw/`) e `--sobrescrever`.

## Testes e qualidade

```bash
uv run pytest
```

```bash
uv run ruff check .
```
