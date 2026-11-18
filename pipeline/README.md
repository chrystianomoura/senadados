# Pipeline

Código em Python que coleta, limpa e verifica os dados abertos do Senado. Hoje existem a **coleta** e a **validação e limpeza**; a verificação entre bases é a próxima etapa ([ordem de construção](../docs/escopo.md#13-ordem-de-construção)).

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

## O que a limpeza faz

Lê `data/raw/`, valida com Pandera, limpa e grava `data/limpo/senadados.sqlite` (fora do git, [D034](../docs/decisoes.md#d034-limpeza-com-validação-em-sqlite-local-sem-nome-nem-documento-de-pessoa-física)).

```bash
uv run python -m senadados_pipeline.limpeza
```

| Regra | Motivo |
|---|---|
| Coluna nova ou faltando, `id` repetido, mês fora de 1 a 12 ou valor com mais de 2 casas **param tudo** | O Senado mudou algo: melhor avisar do que gravar dado errado |
| Categoria vazia vira "Sem categoria" | O site mostra essas linhas com explicação |
| Valor guardado em **centavos inteiros** | A soma bate no centavo, sem erro de arredondamento |
| Fornecedor vira `empresa` (CNPJ com dígitos válidos), `pessoa_fisica`, `sem_documento` ou `outro` | O site trata cada um de um jeito |
| Pessoa física **perde nome e documento** | D008: nunca expor pessoas comuns |
| Documento fora do padrão fica como veio (`outro`) | Corrigir por suposição viola a D025 |
| Data fora de 2008 até o dia da coleta some e a linha é **marcada**, mas segue na soma | A despesa existe; só a data não se sustenta |

Se algo falhar, o banco anterior **não é substituído**. Opção `--data-referencia AAAA-MM-DD` define o dia da coleta (padrão: hoje).

## Testes e qualidade

```bash
uv run pytest
```

```bash
uv run ruff check .
```
