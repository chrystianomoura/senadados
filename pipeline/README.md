# Pipeline

Código em Python que coleta, limpa e verifica os dados abertos do Senado. Hoje existem a **coleta**, a **validação e limpeza** e a **verificação da cota**; a **verificação da equipe do gabinete**; as outras (salário, moradia, contato) são a próxima etapa ([ordem de construção](../docs/escopo.md#13-ordem-de-construção)).

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
| Despesas de um ano **mais antigas que a lista de senadores**, ou sem data de coleta, **param tudo** | Um senador que entrou no intervalo ficaria sem o histórico daquele ano, sem ninguém perceber |
| Categoria vazia vira "Sem categoria" | O site mostra essas linhas com explicação |
| Valor guardado em **centavos inteiros** | A soma bate no centavo, sem erro de arredondamento |
| Fornecedor vira `empresa` (CNPJ com dígitos válidos), `pessoa_fisica`, `sem_documento` ou `outro` | O site trata cada um de um jeito |
| Pessoa física **perde nome e documento** | D008: nunca expor pessoas comuns |
| Documento fora do padrão fica como veio (`outro`) | Corrigir por suposição viola a D025 |
| Data fora de 2008 até o dia da coleta some e a linha é **marcada**, mas segue na soma | A despesa existe; só a data não se sustenta |

Se algo falhar, o banco anterior **não é substituído**. Opção `--data-referencia AAAA-MM-DD` define o dia da coleta (padrão: hoje).

## O que a verificação faz

Compara, para cada senador e ano, as despesas por categoria com o resumo oficial do Senado ([D035](../docs/decisoes.md#d035-verificação-automática-da-cota-por-categoria-na-mesma-foto-dos-dados)). O resultado vai para o banco limpo (`verificacao_cota` e `verificacoes`).

```bash
uv run python -m senadados_pipeline.verificacao
```

- **Só roda na mesma foto dos dados:** coleta, limpeza e verificação precisam ser do mesmo dia. Se não forem, ela explica o que refazer (`coleta --sobrescrever`, depois `limpeza`).
- Resultados: `identico`, `explicado` (só faltam as linhas sem categoria) e `sem_explicacao` (o número fica oculto).
- Demora cerca de 3 minutos para todos os anos (uma consulta por senador e ano). `--anos 2026` verifica um ano só.

## O que a verificação da equipe faz

Baixa o resumo de cada senador e a lista de servidores ativos **na hora** e compara, por gabinete e por vínculo, o número de pessoas ([D036](../docs/decisoes.md#d036-verificação-automática-da-equipe-do-gabinete-por-vínculo)).

```bash
uv run python -m senadados_pipeline.equipe
```

- **Nunca guarda nomes de servidores** (D007): a lista é contada por gabinete e vínculo na hora do download, e só as contagens vão para `data/raw/equipe/`.
- Precisa do banco limpo e da lista de senadores do mesmo dia (mesma regra da cota).
- Resultado em `verificacao_equipe` (a coluna `exibir` diz quem aparece); o resumo fica em `verificacoes` (`equipe`). A equipe aparece para os gabinetes idênticos e some para todos se mais de **5%** falharem ([D037](../docs/decisoes.md#d037-exibição-por-tipo-de-dado-e-freio-de-segurança)).

## Testes e qualidade

```bash
uv run pytest
```

```bash
uv run ruff check .
```
