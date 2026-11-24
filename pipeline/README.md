# Pipeline

Código em Python que coleta, limpa e verifica os dados abertos do Senado. Hoje existem a **coleta**, a **validação e limpeza** e a **verificação da cota**, a **da equipe do gabinete**, a **da moradia**, a **do contato**, a **do salário** e a **do perfil** (foto e mandato); as verificações estão completas, e também as **migrações** e a **carga** para o banco na nuvem ([ordem de construção](../docs/escopo.md#13-ordem-de-construção)).

## Rodar tudo, na ordem

De dentro de `pipeline/`, **no mesmo dia** (a verificação se recusa a rodar com bases de dias diferentes). Uma execução completa com o ano atual e o anterior ([D048](../docs/decisoes.md#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador)) baixa 2 arquivos de despesas, ocupa uns 15 MB de dados brutos e roda em poucos minutos (a verificação da cota faz uma consulta por senador e ano: 162, e não mais 1.539). Os números de 6 minutos, 68 MB e 34 MB são da medição de 18/11/2026, com 19 anos.

```bash
uv run python -m senadados_pipeline.coleta --sobrescrever
```

```bash
uv run python -m senadados_pipeline.limpeza
```

```bash
uv run python -m senadados_pipeline.verificacao
```

```bash
uv run python -m senadados_pipeline.equipe
```

```bash
uv run python -m senadados_pipeline.moradia
```

```bash
uv run python -m senadados_pipeline.contato
```

```bash
uv run python -m senadados_pipeline.salario
```

```bash
uv run python -m senadados_pipeline.perfil
```

Depois das verificações, para gerar as cópias reduzidas das fotos que o site usa (D047):

```bash
uv run python -m senadados_pipeline.fotos
```

E, para levar os dados provados ao banco na nuvem (precisa do `.env`, veja abaixo): `papeis` (só na primeira vez), `migrar` e `carga`, cada um **primeiro em ensaio** e só então com `--apply`.

A limpeza recria o banco do zero e **apaga as tabelas de verificação**; por isso as verificações rodam depois dela. Quem ler o banco (API e site) deve tratar a ausência de uma tabela de verificação como "não verificado" e ocultar o dado.

## O que a coleta faz

- Baixa a **lista dos senadores em exercício** (API administrativa do Senado).
- Baixa as **despesas da cota (CEAPS)** do ano atual e do anterior ([D048](../docs/decisoes.md#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador)) pela API, a fonte principal ([D005](../docs/decisoes.md#d005-api-como-fonte-principal-csv-para-conferência)).
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

Opções: `--anos` (por exemplo `2026`, `2023-2026` ou `2008,2010-2012`; o padrão é o ano atual e o anterior), `--saida` (pasta de saída; o padrão é `data/raw/`) e `--sobrescrever`.

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

- **Dois anos** ([D049](../docs/decisoes.md#d049-moradia-do-ano-anterior-com-três-fontes)): o atual, com as quatro fontes, e o anterior, com as três que existem para ele (sem a lista do mês, que só vale para hoje).
- Resultados: `identico`, `explicado` (a tela diz "renúncia" onde a API diz "não utilizou"), `pendente` (a lista de hoje difere do último mês da página mensal; só no ano atual) e `sem_explicacao`.
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

## O que a verificação do salário faz

Compara a remuneração de cada senador na folha de pagamento do Senado com a identidade dele, em cinco provas ([D041](../docs/decisoes.md#d041-verificação-automática-do-salário-pela-identidade-do-senador)).

```bash
uv run python -m senadados_pipeline.salario
```

- A identidade vem da página do próprio senador (vínculo, situação e UF), e o nome civil dela é a chave de ligação com a folha.
- A folha do mês mais recente é baixada na hora; **só as linhas dos senadores são guardadas**, e os nomes dos demais servidores são descartados na hora (D007). Se um nome tem duas matrículas, as linhas nem são guardadas.
- Resultado em `verificacao_salario`, e o valor provado (remuneração básica e líquida do mês) em `salario`, só para quem tem `exibir = 1`.
- A consulta de remuneração do portal de servidores exige reCAPTCHA, e o pipeline **não tenta contorná-lo**.

## O que a verificação do perfil faz

Confere a foto oficial e o mandato de cada senador comparando duas listas do Senado: a lista de senadores em exercício da API administrativa (a que a coleta grava) e a da API legislativa, que ela baixa na hora ([D045](../docs/decisoes.md#d045-foto-e-mandato-do-senador-com-o-endereço-oficial-do-senado-e-verificação-entre-duas-listas)).

```bash
uv run python -m senadados_pipeline.perfil
```

- **Identidade:** mesmo código nas duas listas e mesmo nome (igual, ou um inteiro dentro do outro, palavra por palavra), UF e partido. Sem isso, nem a foto nem o mandato aparecem.
- **Mandato:** o ano em que começa e o ano em que termina são iguais nas duas listas. O início é o da primeira legislatura e o fim, o da última que a lista traz.
- **Foto:** o endereço da lista legislativa, com os redirecionamentos resolvidos, termina no código do senador, está em `https://legis.senado.leg.br` e responde com um JPEG de pelo menos 10 mil bytes. **Só os primeiros 1.024 bytes** de cada foto são baixados, e as imagens não são guardadas.
- Cada campo tem o seu resultado (`identico` ou `sem_explicacao`) e o seu freio de segurança de 5% (D037). Só o valor provado vai para a tabela `perfil`; o resultado fica em `verificacao_perfil`.
- Mesma regra da cota: só roda com a lista de senadores e o banco limpo do mesmo dia. Um código que só a lista legislativa traz é apenas avisado na saída.
- O 10 mil bytes é um julgamento, e não um número pesquisado: a menor das 81 fotos medidas em 19/11/2026 tem 78 KB.

## O que o passo das fotos faz

Baixa a foto de cada senador **cuja foto foi provada hoje** pela verificação do perfil e grava duas cópias em WebP, sem metadado, em `web/public/fotos/` ([D047](../docs/decisoes.md#d047-cópias-reduzidas-das-fotos-oficiais-com-pillow)): `{código}-p.webp` (240 por 300, lista e mosaico) e `{código}-g.webp` (480 por 600, perfil).

- Baixa as fotos inteiras (uns 23 MB) e as reduz para uns 3,4 MB. A pasta inteira é refeita a cada execução (a foto de quem saiu da lista some) e o passo **só aceita refazer uma pasta chamada `fotos`**.
- Uma foto que não baixa ou não abre como JPEG é pulada e avisada; o site continua usando o endereço oficial dela.
- Precisa do banco limpo e da verificação do perfil, os dois do mesmo dia. Não vai para o banco na nuvem: as cópias são arquivos do site.

## O que as migrações e a carga fazem

Levam os dados provados para o banco na nuvem ([D042](../docs/decisoes.md#d042-banco-no-neon-só-dados-agregados-dois-esquemas-e-carga-repetível), [D043](../docs/decisoes.md#d043-migrações-em-sql-puro-driver-psycopg-e-carga-que-ensaia-antes-de-gravar)). Os dois comandos são **ensaio por padrão**: desfazem tudo no fim e só gravam com `--apply`. A conexão vem de variáveis de ambiente, que ficam num arquivo `.env` na raiz do repositório (o git o ignora) e **nunca** no código:

| Variável | Quem usa | Papel no banco |
|---|---|---|
| `DATABASE_URL` | `papeis`, `migrar` | Dono do banco (cria papéis, esquemas e tabelas) |
| `DATABASE_URL_CARGA` | `carga` | `sd_carga` (só escreve dados; não cria tabelas). Gravada pelo `papeis` |
| `DATABASE_URL_LEITURA` | o exportador do site e, depois, a API | `sd_leitura` (só lê o `publico`). Gravada pelo `papeis` |

Na primeira vez, crie os papéis (as senhas vão direto para o `.env`, sem aparecer na tela):

```bash
uv run --env-file ../.env python -m senadados_pipeline.papeis
```

```bash
uv run --env-file ../.env python -m senadados_pipeline.migrar
```

```bash
uv run --env-file ../.env python -m senadados_pipeline.carga
```

- **Migrações:** os arquivos SQL de [migracoes/](migracoes/README.md), em ordem, só os que ainda não foram aplicados. Os papéis `sd_carga` e `sd_leitura` precisam existir antes.
- **Carga:** lê o banco limpo local **só para leitura**, leva só dados **agregados** e só o que passou nas verificações, e apaga e regrava as tabelas numa transação, conferindo a contagem de cada uma. **Recusa carregar** se faltar alguma das 9 verificações ou se alguma não for do dia da coleta. As despesas linha a linha **não** vão para a nuvem.
- Os registros mostram só o endereço do servidor, **nunca a senha**.
- **Já foram ensaiados numa branch da Neon** em 19/11/2026, com logins reais (veja a D043). Foram aplicados na produção no mesmo dia, com o OK do mantenedor.

## O que o exportador faz

Gera os arquivos JSON que o site lê, a partir do esquema `publico` do banco na nuvem, seguindo o [contrato dos dados](../docs/contrato-dos-dados.md) ([D044](../docs/decisoes.md#d044-site-antes-da-api-com-dados-em-arquivos-json-gerados-do-esquema-público)). Só **lê** o banco, com o papel `sd_leitura` (`DATABASE_URL_LEITURA`).

```bash
uv run --env-file ../.env python -m senadados_pipeline.exportar
```

- Grava em `web/dados/` (o git ignora) ou na pasta de `--saida`. **Troca a pasta inteira** a cada execução, então o arquivo de quem saiu da lista não fica para trás.
- **Falha fechado:** se uma conferência quebrar (endereço repetido, soma que não fecha, algo com formato de CPF), nenhum arquivo é gravado e a pasta anterior continua.
- Dado não provado vem como `null`; o site não mostra nada no lugar.
- Com os dados de 18/11/2026 (19 anos): 84 arquivos, 1,6 MB, perfis de 20 KB em média. Com dois anos (23/11/2026): 84 arquivos, 648 KB.

## Testes e qualidade

```bash
uv run pytest
```

```bash
uv run ruff check .
```
