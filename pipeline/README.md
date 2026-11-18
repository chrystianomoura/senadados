# Pipeline

Código em Python que coleta, limpa e verifica os dados abertos do Senado. Hoje existem a **coleta**, a **validação e limpeza** e a **verificação da cota**, a **da equipe do gabinete**, a **da moradia** e a **do contato**; a última que falta é a do salário ([ordem de construção](../docs/escopo.md#13-ordem-de-construção)).

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

## O que a verificação da moradia faz

Baixa, na hora, o uso de auxílio-moradia e de imóvel funcional de cada senador e compara quatro fontes do Senado: o resumo da API, o resumo da tela do portal, a página mensal e a lista do mês ([D039](../docs/decisoes.md#d039-verificação-automática-da-moradia-mês-a-mês)).

```bash
uv run python -m senadados_pipeline.moradia
```

- Resultados: `identico`, `explicado` (a tela diz "renúncia" onde a API diz "não utilizou"), `pendente` (a lista de hoje difere do último mês da página mensal) e `sem_explicacao`.
- Só `sem_explicacao` conta para o freio de segurança de 5% (D037). O `pendente` esconde só o próprio senador.
- O resultado vai para `verificacao_moradia`, e o uso mês a mês, para `moradia_meses` (usar só quem tem `exibir = 1`).
- A página mensal é lida do portal (não há API para isso). Se o Senado mudar o formato, o senador cai em `sem_explicacao`, e não recebe um número errado.

## O que a verificação do contato faz

Baixa, na hora, o endereço do gabinete, os telefones e o e-mail da página de cada senador e compara com a API de dados abertos ([D040](../docs/decisoes.md#d040-verificação-automática-do-contato-do-gabinete)).

```bash
uv run python -m senadados_pipeline.contato
```

- Cada campo tem o seu resultado (`identico`, `explicado` ou `sem_explicacao`) e o seu freio de segurança de 5% (D037).
- Os telefones saem da página do portal, com os números abreviados ("6187 / 6188") expandidos por uma regra mecânica.
- Só o valor provado vai para a tabela `contato`; o que não foi provado fica vazio. O resultado de cada campo fica em `verificacao_contato`.
- Só guarda gabinete, telefones e e-mail. Nome civil, data de nascimento e o resto da página são ignorados.

## Testes e qualidade

```bash
uv run pytest
```

```bash
uv run ruff check .
```
