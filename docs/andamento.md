# Andamento do projeto

Resumo do que existe, do que foi provado e do que vem a seguir. É o documento para quem chega agora e quer saber **em que pé o projeto está**. Os detalhes de cada decisão estão em [decisoes.md](decisoes.md), e os de cada conferência, em [verificacoes.md](verificacoes.md).

**Última atualização:** 19/11/2026 (banco da Neon criado, com papéis, migrações e dados de 18/11 aplicados na produção).

## Em uma frase

O pipeline que coleta, limpa e **prova** os dados do Senado está pronto e roda do zero em cerca de 6 minutos, e os dados provados já estão no banco da Neon (19/11/2026). Ainda não há site, API nem atualização diária automática: o próximo passo é o contrato dos dados e o site ([D044](decisoes.md#d044-site-antes-da-api-com-dados-em-arquivos-json-gerados-do-esquema-público)).

## O que existe hoje

| Parte | Estado |
|---|---|
| Escopo, regras, protótipo da página e identidade visual | Prontos (11 e 12/11) |
| Coleta das despesas e da lista de senadores | Pronta |
| Validação (Pandera) e limpeza das despesas | Prontas |
| Verificação da **cota** | Pronta |
| Verificação da **equipe** do gabinete | Pronta |
| Verificação da **moradia** | Pronta |
| Verificação do **contato** (endereço, telefones, e-mail) | Pronta |
| Verificação do **salário** | Pronta |
| Documento público de divergências nos dados do Senado | Pronto |
| Banco no Neon | **No ar com os dados provados de 18/11/2026** (20 MB, 17 tabelas, permissões testadas) ([D042](decisoes.md#d042-banco-no-neon-só-dados-agregados-dois-esquemas-e-carga-repetível), [D043](decisoes.md#d043-migrações-em-sql-puro-driver-psycopg-e-carga-que-ensaia-antes-de-gravar)). Atualização diária ainda manual |
| API, site, automação diária | **Não começaram** |

O código está em [pipeline/](../pipeline/README.md), com 310 testes (270 em 18/11 e 40 novos da carga, das migrações e dos papéis) e 95% de cobertura nos módulos de verificação (a cobertura é de 18/11 e não foi medida de novo). Os dados ficam em `data/` e **não vão para o git**.

## Como rodar tudo, do zero

Detalhes em [pipeline/README.md](../pipeline/README.md#rodar-tudo-na-ordem). Em resumo, de dentro de `pipeline/`, nesta ordem e **no mesmo dia**:

1. `coleta` (baixa as despesas de 2008 a 2026 e a lista de senadores)
2. `limpeza` (valida, limpa e grava o banco SQLite local)
3. `verificacao`, `equipe`, `moradia`, `contato` e `salario`
4. Para o banco na nuvem (precisa do `.env`): `papeis` (só na primeira vez), `migrar` e `carga`, cada um **primeiro em ensaio** e depois com `--apply`

Uma execução completa, feita em 18/11/2026 numa pasta vazia, **reproduziu todos os números abaixo**. Ocupa 68 MB de dados brutos e 34 MB no banco local.

## O que foi provado (18/11/2026)

| Verificação | Resultado | Aparece no site para |
|---|---|---|
| Cota, 2010 a 2026 | Nenhuma divergência sem explicação (2026: 73 idênticos e 7 explicados) | Todos os anos de 2010 em diante |
| Cota, 2008 e 2009 | 5 senadores sem explicação em cada ano | **Não aparece** |
| Equipe do gabinete | 80 de 81 idênticos, 1 sem explicação | 80 |
| Moradia | 76 idênticos, 1 explicado, 4 pendentes, 0 sem explicação | 77 |
| Endereço do gabinete | 81 idênticos | 81 |
| Telefones | 66 idênticos e 15 explicados | 81 |
| E-mail | 81 idênticos (2 senadores sem e-mail nas duas fontes) | 79 |
| Salário | 79 de 81 passam em cinco provas; 2 sem explicação | 79 |

Os números da cota são os de 2026 contra o resumo do Senado **do mesmo dia**. Os dados totais: 81 senadores em exercício, 154.298 despesas de 2008 a 2026, R$ 213 milhões.

## As decisões de 18 e 19/11/2026

| Decisão | Em uma linha |
|---|---|
| [D033](decisoes.md#d033-coleta-local-que-só-grava-quem-está-em-exercício) | A coleta só grava quem está em exercício, não sobrescreve e para se o Senado mudar o formato |
| [D034](decisoes.md#d034-limpeza-com-validação-em-sqlite-local-sem-nome-nem-documento-de-pessoa-física) | Limpeza com Pandera, valores em centavos, pessoa física sem nome e documento; formato local SQLite |
| [D035](decisoes.md#d035-verificação-automática-da-cota-por-categoria-na-mesma-foto-dos-dados) | Cota por categoria contra o resumo, só se tudo for do mesmo dia |
| [D036](decisoes.md#d036-verificação-automática-da-equipe-do-gabinete-por-vínculo) | Equipe por gabinete e vínculo, sem guardar nomes |
| [D037](decisoes.md#d037-exibição-por-tipo-de-dado-e-freio-de-segurança) | Dado que compara é tudo ou nada; dado descritivo aparece para quem foi provado, com freio de 5% |
| [D038](decisoes.md#d038-documento-público-de-divergências-com-prova-em-imagem) | Divergências do Senado publicadas com prova em imagem |
| [D039](decisoes.md#d039-verificação-automática-da-moradia-mês-a-mês) | Moradia com quatro fontes; "pendente" separado de "sem explicação" |
| [D040](decisoes.md#d040-verificação-automática-do-contato-do-gabinete) | Contato campo a campo, com freio por campo |
| [D041](decisoes.md#d041-verificação-automática-do-salário-pela-identidade-do-senador) | Salário ligado pela identidade do senador, em cinco provas |
| [D042](decisoes.md#d042-banco-no-neon-só-dados-agregados-dois-esquemas-e-carga-repetível) | Banco no Neon: só dados agregados, esquemas `publico` e `interno`, três papéis de menor privilégio (19/11) |
| [D043](decisoes.md#d043-migrações-em-sql-puro-driver-psycopg-e-carga-que-ensaia-antes-de-gravar) | Migrações em SQL puro, driver psycopg e carga que ensaia antes de gravar (19/11) |
| [D044](decisoes.md#d044-site-antes-da-api-com-dados-em-arquivos-json-gerados-do-esquema-público) | Site antes da API, com dados em arquivos JSON gerados do esquema `publico` (19/11) |

## O que aprendemos

- **Os dados agregados cabem com folga.** O banco inteiro ocupa **20 MB** no PostgreSQL da Neon (17 tabelas), contra 34 MB do SQLite com as despesas linha a linha, e o plano gratuito dá 1 GB.
- **Ensaiar antes de gravar compensa.** O ensaio numa branch e a repetição dos comandos (que não acharam nada pendente nem mudaram as contagens) deram segurança para aplicar na produção, onde a primeira carga saiu com o mesmo resultado.
- **Comparar bases de dias diferentes gera divergência falsa.** A primeira conferência da cota estava errada por isso. Hoje a verificação se recusa a rodar se as bases não forem do mesmo dia.
- **Falhar fechado funciona.** Um endereço de página sem o ano fez 81 senadores caírem em "sem explicação" e **nenhum contato foi exibido**, em vez de um dado errado aparecer.
- **O Senado mostra números diferentes em publicações do próprio Senado.** Isso virou o documento [divergencias-nos-dados-do-senado.md](divergencias-nos-dados-do-senado.md), com 11 imagens de prova. Um dos casos (a equipe do gabinete de um senador) foi visto também na API e pode ser corrigido a qualquer momento.
- **Tudo ou nada era rígido demais para dado descritivo.** Um gabinete que não bate escondia a equipe dos 81. A D037 separou os dois tipos de dado.
- **Um sinal de bot é um limite, e não um obstáculo.** A consulta de remuneração do portal exige reCAPTCHA. Não foi contornada, e o salário ficou com fonte única.

## Pendências conhecidas

- **Equipe:** 1 gabinete com 1 efetivo a mais no resumo do que na lista de servidores. Sem explicação.
- **Moradia:** 4 casos pendentes, por defasagem entre períodos. Se resolvem quando a página mensal incluir novembro.
- **Salário:** 2 suplentes que assumiram em outubro. Se resolvem com a folha de novembro, que ainda não saiu.
- **Cota de 2008 e 2009:** sem explicação, só o Senado pode dar. Ficam ocultas.
- **Manter o documento de divergências:** os prints são de 18/11/2026. Se o Senado corrigir um caso, o texto deve ser atualizado.
- **Verificação diária automática:** o pipeline roda à mão. A automação (GitHub Actions) vem depois do banco e do site.
- **Limites dos planos gratuitos:** os da **Neon** foram reconfirmados na página oficial em 19/11/2026 ([D042](decisoes.md#d042-banco-no-neon-só-dados-agregados-dois-esquemas-e-carga-repetível)). Os da Render, do Cloudflare Pages e do GitHub Actions seguem de fonte secundária e precisam ser reconfirmados.
- **Licença do código:** ainda não escolhida.

## O banco no Neon (feito em 19/11/2026)

Etapa 3 da ordem de construção, concluída: o projeto `senadados` na Neon (plano gratuito, `aws-us-east-2`, PostgreSQL 18) tem os esquemas `publico` e `interno`, os papéis `sd_carga` (escreve) e `sd_leitura` (só lê o `publico`), as migrações 001 e 002 e os dados provados de 18/11/2026. As decisões estão na [D042](decisoes.md#d042-banco-no-neon-só-dados-agregados-dois-esquemas-e-carga-repetível) e na [D043](decisoes.md#d043-migrações-em-sql-puro-driver-psycopg-e-carga-que-ensaia-antes-de-gravar); o que foi conferido na produção (permissões, soma das despesas igual à do SQLite, 20 MB) está na D043.

## Próximo passo: contrato dos dados e site (etapas 4 e 5)

O site vem antes da API ([D044](decisoes.md#d044-site-antes-da-api-com-dados-em-arquivos-json-gerados-do-esquema-público)). A ordem:

1. **Contrato dos dados e exportador** (Python, com testes): arquivos JSON gerados do esquema `publico` com o papel `sd_leitura`, um por senador, mais a lista, as verificações e os metadados. Começa pela lista e por **um** perfil real, a partir do que o protótipo `design/perfil-do-senador.html` precisa. Os JSON não vão para o git.
2. **Esqueleto do site** em `web/` (Next.js, TypeScript, exportação estática, identidade da D029), com um `README.md` curto, como toda pasta nova.
3. **Primeira página real:** o perfil de um senador, lendo o JSON do passo 1.
4. **Depois, em fatias:** o perfil completo, a home com busca, a página "Verificações" (com a seção de divergências já escrita), o ranking e a comparação.

**A atualização diária** (etapa 7) é uma rotina do GitHub Actions que repete coleta, limpeza, verificações, carga e exportação; as URLs de `sd_carga` e `sd_leitura` viram segredos do repositório. Antes de publicar, reconfirmar os limites do Cloudflare Pages e do GitHub Actions. A API fica depois do site, e a hospedagem dela só precisa ser decidida então (a D004 escolheu a Render, com os limites lidos em 19/11/2026).

## Registro dos commits de 18/11/2026

A branch `feat/pipeline-coleta`, a partir da `main` (o histórico do git tem os detalhes e os hashes):

| Título do commit | O quê |
|---|---|
| `feat(pipeline): adiciona coleta das despesas e da lista de senadores` | Coleta |
| `docs: corrige números da cota e registra a lição da mesma foto dos dados` | Correção dos números da cota |
| `feat(pipeline): valida e limpa as despesas e grava um banco SQLite local` | Validação, limpeza e banco local |
| `feat(pipeline): verifica a cota por categoria contra o resumo do Senado` | Verificação da cota |
| `refactor(pipeline): consolida constantes e trava coleta inconsistente` | Constantes em um lugar só e trava da coleta |
| `feat(pipeline): verifica a equipe do gabinete e exibe por tipo de dado` | Equipe e regra de exibição |
| `docs: publica divergências dos dados do Senado com prova em imagem` | Documento de divergências |
| `feat(pipeline): verifica a moradia mês a mês com quatro fontes do Senado` | Moradia |
| `feat(pipeline): verifica o contato do gabinete campo a campo` | Contato |
| `feat(pipeline): verifica o salário pela identidade do senador` | Salário |
| `refactor(pipeline): junta constantes e a conferência da mesma foto` | Revisão geral: código |
| `docs: documenta o dia e atualiza o que ficou para trás` | Revisão geral: documentos e este arquivo |

## Registro dos commits de 19/11/2026

A branch `feat/banco-neon`, a partir da `main`:

| Título do commit | O quê |
|---|---|
| `docs: registra o desenho do banco no Neon (D042)` | Desenho do banco |
| `docs: aceita a D042 e registra a criação do projeto no Neon` | Decisão aceita e projeto criado |
| `feat(pipeline): adiciona migrações e carga dos dados no banco do Neon` | Migrações, executor e carga |
| `feat(pipeline): cria os papéis do banco e ensaia tudo numa branch da Neon` | Papéis e ensaio ponta a ponta |
| `docs: registra a aplicação do banco na produção do Neon` | Banco aplicado na produção |
| `docs: atualiza os documentos depois do banco no ar` | Revisão geral dos documentos |

Na branch `docs/site-primeiro`, a partir da `main` depois do PR #2:

| Título do commit | O quê |
|---|---|
| `docs: registra que o site vem antes da API (D044)` | Nova ordem de construção |
