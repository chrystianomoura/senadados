# Andamento do projeto

Resumo do que existe, do que foi provado e do que vem a seguir. É o documento para quem chega agora e quer saber **em que pé o projeto está**. Os detalhes de cada decisão estão em [decisoes.md](decisoes.md), e os de cada conferência, em [verificacoes.md](verificacoes.md).

**Última atualização:** 23/11/2026 (revisão geral depois da foto e do mandato, da regra de dois anos, da moradia de 2025 e da página "Verificações"; pendências refeitas).

## Em uma frase

O pipeline que coleta, limpa e **prova** os dados do Senado está pronto e roda do zero em poucos minutos (cerca de 6 com os 19 anos de 18/11/2026; hoje só 2 anos, [D048](decisoes.md#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador)), e os dados provados já estão no banco da Neon (19/11/2026). O site já tem a home, o perfil do senador (com a troca para o ano anterior) e a página "Verificações", lendo os JSON gerados do banco; ainda não há API nem atualização diária automática. Próximo passo: o ranking e a comparação, depois "Sobre os dados", a rotina diária e a API ([D044](decisoes.md#d044-site-antes-da-api-com-dados-em-arquivos-json-gerados-do-esquema-público)).

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
| Verificação do **perfil** (foto e mandato) | **Pronta (23/11/2026, D045):** 81 de 81 idênticos nos dois campos |
| Documento público de divergências nos dados do Senado | Pronto |
| Banco no Neon | **No ar, recarregado em 23/11/2026 com os dados provados do ano atual e do anterior (2025 e 2026, [D048](decisoes.md#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador)), com a moradia dos dois anos ([D049](decisoes.md#d049-moradia-do-ano-anterior-com-três-fontes)) (migração 004 aplicada em 23/11)**. Antes: dados de 18/11/2026 (20 MB, 18 tabelas, permissões testadas). A migração 003 (`moradia_verificada`) foi aplicada na produção em 19/11/2026 ([D042](decisoes.md#d042-banco-no-neon-só-dados-agregados-dois-esquemas-e-carga-repetível), [D043](decisoes.md#d043-migrações-em-sql-puro-driver-psycopg-e-carga-que-ensaia-antes-de-gravar)). Atualização diária ainda manual |
| Exportador dos JSON do site | **Pronto e rodando contra a produção** (84 arquivos, 648 KB com os dois anos, contra 1,6 MB com os 19 anos de 18/11; [contrato](contrato-dos-dados.md), versão 2). A saída da produção é igual à do ensaio, exceto pela hora da carga |
| Site (`web/`) | **Home (abertura, "Como funciona" e busca com filtros), perfil do senador (resumo do ano, seis guias e botão para trocar para o outro ano) e página "Verificações" prontos**, com os dados reais ([D046](decisoes.md#d046-site-em-nextjs-16-com-exportação-estática-fontes-hospedadas-e-testes-com-vitest)). A foto aparece na lista e no perfil, e o mandato no cartão do perfil, vindos da verificação "perfil". Faltam ranking, comparação e "Sobre os dados" |
| API, automação diária | **Não começaram** |

O código está em [pipeline/](../pipeline/README.md), com 399 testes de Python (270 em 18/11, 70 da carga, das migrações, dos papéis e do exportador, e 59 da verificação do perfil, das fotos, dos anos e da moradia do ano anterior) e 35 de TypeScript no site e 95% de cobertura nos módulos de verificação (a cobertura é de 18/11 e não foi medida de novo). Os dados ficam em `data/` e **não vão para o git**.

## Mudança de 23/11/2026: só o ano atual e o anterior

Pela [D048](decisoes.md#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador), o pipeline passou a coletar, limpar e verificar só o ano atual e o anterior, e a página do senador ganhou o botão para trocar de ano (a verba, os fornecedores e, pela [D049](decisoes.md#d049-moradia-do-ano-anterior-com-três-fontes), a moradia mudam; salário, equipe e contato só existem no ano dos dados). **Os números dos documentos que falam de "2008 a 2026" (154 mil despesas, 19 anos, 1.539 consultas, R$ 213 milhões) são da medição de 18/11/2026 e deixaram de valer para a execução diária.**

## Como rodar tudo, do zero

Detalhes em [pipeline/README.md](../pipeline/README.md#rodar-tudo-na-ordem). Em resumo, de dentro de `pipeline/`, nesta ordem e **no mesmo dia**:

1. `coleta` (baixa as despesas do ano atual e do anterior e a lista de senadores)
2. `limpeza` (valida, limpa e grava o banco SQLite local)
3. `verificacao`, `equipe`, `moradia`, `contato`, `salario` e `perfil`
4. `fotos` (as cópias reduzidas das fotos que o site usa, [D047](decisoes.md#d047-cópias-reduzidas-das-fotos-oficiais-com-pillow))
5. Para o banco na nuvem (precisa do `.env`): `papeis` (só na primeira vez), `migrar` e `carga`, cada um **primeiro em ensaio** e depois com `--apply`

Uma execução completa, feita em 18/11/2026 numa pasta vazia, **reproduziu todos os números abaixo**. Ocupava 68 MB de dados brutos e 34 MB no banco local, com 19 anos. **Com dois anos (23/11/2026): 17 MB de dados brutos e 9 MB no banco local.**

## O que está provado hoje (23/11/2026)

Com só o ano atual e o anterior ([D048](decisoes.md#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador)) e a moradia dos dois anos ([D049](decisoes.md#d049-moradia-do-ano-anterior-com-três-fontes)). Os números mudaram em relação à tabela de 18/11 abaixo porque o Senado continuou publicando e porque Wellington Dias voltou ao exercício em 19/11 (o suplente dele saiu; hoje são 71 titulares e 10 suplentes). A investigação está em [verificacoes.md](verificacoes.md#recarga-de-23112026).

| Verificação | Resultado | Aparece no site para |
|---|---|---|
| Cota de 2026 | 72 idênticos e 7 explicados | 79 |
| Cota de 2025 | 67 idênticos e 5 explicados | 72 |
| Equipe do gabinete | 77 idênticos, 4 sem explicação | 77 |
| Moradia de 2026 | 77 idênticos, 1 explicado, 3 pendentes | 78 |
| Moradia de 2025 | 80 idênticos, 1 explicado (três fontes) | 81, mas só abre a página de 2025 de quem tem a verba de 2025 |
| Endereço do gabinete | 81 idênticos | 81 |
| Telefones | 65 idênticos, 15 explicados, 1 sem explicação | 80 |
| E-mail | 81 idênticos (2 sem e-mail nas duas fontes) | 79 |
| Salário (folha de outubro) | 79 passam nas cinco provas; 2 sem explicação | 79 |
| Foto e mandato | 81 idênticos em cada um | 81 |

## O que foi provado (18/11/2026, registro histórico)

| Verificação | Resultado | Aparece no site para |
|---|---|---|
| Cota, 2010 a 2026 (medição de 18/11, registro histórico) | Nenhuma divergência sem explicação (2026: 73 idênticos e 7 explicados) | Hoje só 2025 e 2026 (23/11: 2025, 67 + 5 explicados; 2026, 72 + 7) |
| Cota, 2008 e 2009 | 5 senadores sem explicação em cada ano | **Não aparece** |
| Equipe do gabinete | 80 de 81 idênticos, 1 sem explicação | 80 |
| Moradia | 76 idênticos, 1 explicado, 4 pendentes, 0 sem explicação | 77 |
| Endereço do gabinete | 81 idênticos | 81 |
| Telefones | 66 idênticos e 15 explicados | 81 |
| E-mail | 81 idênticos (2 senadores sem e-mail nas duas fontes) | 79 |
| Salário | 79 de 81 passam em cinco provas; 2 sem explicação | 79 |
| Perfil (foto e mandato), 23/11 | 81 idênticos em cada campo | 81 |

Os números da cota são os de 2026 contra o resumo do Senado **do mesmo dia**. Os dados totais de 18/11: 81 senadores em exercício, 154.298 despesas de 2008 a 2026, R$ 213 milhões. **Em 23/11/2026, com só 2025 e 2026: 38.237 despesas e R$ 60 milhões.**

## As decisões de 18 a 23/11/2026

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
| [D045](decisoes.md#d045-foto-e-mandato-do-senador-com-o-endereço-oficial-do-senado-e-verificação-entre-duas-listas) | Foto e mandato do senador: endereço oficial do Senado, com crédito, e verificação entre duas listas (19/11) |
| [D046](decisoes.md#d046-site-em-nextjs-16-com-exportação-estática-fontes-hospedadas-e-testes-com-vitest) | Site em Next.js 16 com exportação estática, fontes hospedadas, testes com Vitest e, em 20/11, a revisão da home, do perfil e dos textos |
| [D047](decisoes.md#d047-cópias-reduzidas-das-fotos-oficiais-com-pillow) | Cópias reduzidas das fotos em WebP, de 23 MB para 3,4 MB, com Pillow (23/11) |
| [D048](decisoes.md#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador) | Só o ano atual e o anterior, com botão para trocar de ano no perfil (23/11) |
| [D049](decisoes.md#d049-moradia-do-ano-anterior-com-três-fontes) | Moradia do ano anterior com três fontes (23/11) |

## O que aprendemos

- **Os dados agregados cabem com folga.** O banco inteiro ocupa **20 MB** no PostgreSQL da Neon (17 tabelas na época; 18 desde a migração 003), contra 34 MB do SQLite com as despesas linha a linha, e o plano gratuito dá 1 GB.
- **Ensaiar antes de gravar compensa.** O ensaio numa branch e a repetição dos comandos (que não acharam nada pendente nem mudaram as contagens) deram segurança para aplicar na produção, onde a primeira carga saiu com o mesmo resultado.
- **Comparar bases de dias diferentes gera divergência falsa.** A primeira conferência da cota estava errada por isso. Hoje a verificação se recusa a rodar se as bases não forem do mesmo dia.
- **Falhar fechado funciona.** Um endereço de página sem o ano fez 81 senadores caírem em "sem explicação" e **nenhum contato foi exibido**, em vez de um dado errado aparecer.
- **O Senado mostra números diferentes em publicações do próprio Senado.** Isso virou o documento [divergencias-nos-dados-do-senado.md](divergencias-nos-dados-do-senado.md), com 11 imagens de prova. Um dos casos (a equipe do gabinete de um senador) foi visto também na API e pode ser corrigido a qualquer momento.
- **Tudo ou nada era rígido demais para dado descritivo.** Um gabinete que não bate escondia a equipe dos 81. A D037 separou os dois tipos de dado.
- **Testar a página real encontra o que o código não mostra.** A rolagem suave global fazia a página do senador abrir cortada vindo da home e a volta passar pelo topo; um clique na marca refazia a página e sorteava outras fotos. Só apareceram medindo a posição da rolagem e das fotos no navegador.
- **Conferir o dado antes de escrever o texto.** O aviso de que a remuneração básica "não é o total antes dos descontos" vinha de uma regra geral; olhando a folha de outubro, em 75 de 80 linhas o líquido é o salário-base menos previdência e imposto de renda. O texto foi corrigido (veja a D046).
- **Um total do Senado inteiro não é o que parece.** A planilha de execução orçamentária traz R$ 5,28 bilhões pagos em 2024, mas cerca de 83% é pessoal e aposentadorias; o "senadômetro" e o destaque de quem mais usou a verba foram estudados e descartados (D046).
- **Um sinal de bot é um limite, e não um obstáculo.** A consulta de remuneração do portal exige reCAPTCHA. Não foi contornada, e o salário ficou com fonte única.

## Pendências conhecidas

**Telas e infraestrutura que faltam** (a ordem está em [escopo.md](escopo.md#13-ordem-de-construção)):

- **Ranking e comparação entre senadores:** dependem de decidir quem entra no grupo de comparação (quem não tem despesa no ano, como Wellington Dias e Jorge Kajuru, não tem valor para comparar; D037, tudo ou nada). A "posição entre os senadores" do perfil vem junto.
- **Página "Sobre os dados":** fica para o fim do projeto. Deve repetir a frase "Verificamos se as bases do Senado concordam entre si. Não auditamos os dados" (hoje ela está na página "Verificações").
- **Página "Verificações":** faltam o canal para reportar um erro e o registro de correções (escopo §4.5).
- **Rotina diária (GitHub Actions):** o pipeline roda à mão. A rotina deve repetir coleta, limpeza, verificações, carga, exportação, cópias das fotos e build. Fica para o fim.
- **Publicação no Cloudflare Pages:** a política de conteúdo (`web/public/_headers`) só foi testada servindo o site localmente.
- **API:** depois do site.
- **Limites dos planos gratuitos:** os da **Neon** foram reconfirmados na página oficial em 19/11/2026 ([D042](decisoes.md#d042-banco-no-neon-só-dados-agregados-dois-esquemas-e-carga-repetível)). Os da Render, do Cloudflare Pages e do GitHub Actions seguem de fonte secundária e precisam ser reconfirmados.
- **Licença do código:** ainda não escolhida.
- **Revisão final dos documentos.**

**Decisão do mantenedor, adiada de propósito:**

- **Freio de 5% da equipe:** em 23/11/2026 a equipe aparece para 77 gabinetes, com 4 sem explicação (4,9%); **um quinto caso a esconderia de todos** ([D037](decisoes.md#d037-exibição-por-tipo-de-dado-e-freio-de-segurança)). A defasagem entre as listas do Senado pode cruzar esse limite sem erro no nosso código. Decidido esperar a rotina diária gerar dados e só então avaliar separar as falhas por causa.

**Casos que só o Senado explica, ou que se resolvem sozinhos:**

- **Equipe, 4 gabinetes:** Camilo Santana (o resumo traz 1 efetivo que a lista de servidores não tem), Esperidião Amin e Nelsinho Trad Filho (o resumo e a tela do portal trazem 1 comissionado a mais que a lista de servidores) e Wellington Dias (o exercício começou em 19/11 e a lotação ainda não foi publicada; o telefone dele também não vem).
- **Moradia, 3 pendentes:** se resolvem quando a página mensal incluir novembro.
- **Salário, 2 suplentes** que assumiram em outubro: se resolvem com a folha de novembro, que ainda não saiu. Auxílios e gratificação natalina existem na folha (3 e 5 senadores em outubro), mas não são guardados nem mostrados.
- **Equipe e salário de 2025:** ficam de fora. As provas atuais não passam para o ano anterior ([D049](decisoes.md#d049-moradia-do-ano-anterior-com-três-fontes)).
- **Anos de 2008 a 2024:** deixaram de ser processados ([D048](decisoes.md#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador)); as medições antigas ficam como registro histórico.

**Pontos pequenos:**

- **Prints do documento de divergências:** são de 23/11/2026 e **não se atualizam sozinhos**; se o Senado corrigir um caso, as imagens são refeitas com [ferramentas/provas/](../ferramentas/README.md#provas-refazer-as-imagens-da-página-verificações) e os números do texto conferidos à mão. Esperidião Amin e Nelsinho Trad Filho ainda não têm print.
- **Foto:** o crédito aparece só ao passar o mouse (não em telas de toque). O piscar das fotos ao rolar não teve a causa confirmada.
- **Navegadores:** Safari e Firefox não foram verificados no site.
- **Cópias das fotos:** falta rodar o passo na rotina diária e no build de publicação.

## O banco no Neon (feito em 19/11/2026)

Etapa 3 da ordem de construção, concluída: o projeto `senadados` na Neon (plano gratuito, `aws-us-east-2`, PostgreSQL 18) tem os esquemas `publico` e `interno`, os papéis `sd_carga` (escreve) e `sd_leitura` (só lê o `publico`), as migrações 001 e 002 e os dados provados de 18/11/2026. As decisões estão na [D042](decisoes.md#d042-banco-no-neon-só-dados-agregados-dois-esquemas-e-carga-repetível) e na [D043](decisoes.md#d043-migrações-em-sql-puro-driver-psycopg-e-carga-que-ensaia-antes-de-gravar); o que foi conferido na produção (permissões, soma das despesas igual à do SQLite, 20 MB) está na D043.

## Próximo passo: ranking e comparação (etapa 5)

O site vem antes da API ([D044](decisoes.md#d044-site-antes-da-api-com-dados-em-arquivos-json-gerados-do-esquema-público)). A ordem:

1. **Contrato dos dados e exportador** (**feito em 19/11/2026**, ensaiado numa branch e depois rodado contra a produção): arquivos JSON gerados do esquema `publico` com o papel `sd_leitura`, um por senador, mais a lista, as verificações e os metadados ([contrato-dos-dados.md](contrato-dos-dados.md)). Os JSON não vão para o git. A migração 003 já foi aplicada na produção e os dados recarregados (19/11/2026).
2. **Esqueleto do site** em `web/` (**feito em 19/11/2026**: Next.js, TypeScript, exportação estática, identidade da D029, com um `README.md` curto).
3. **Primeira página real** (**feita em 19/11/2026**): o perfil do senador, lendo o JSON do passo 1.
4. **Home** (**feita em 20/11/2026**): abertura, "Como funciona", busca e filtros, e a lista com foto e selos. Perfil e home foram refeitos em 20/11 com textos em linguagem simples.
5. **Foto e mandato** (**feito em 23/11/2026**, [D045](decisoes.md#d045-foto-e-mandato-do-senador-com-o-endereço-oficial-do-senado-e-verificação-entre-duas-listas)): verificação "perfil", migração 004, carga, exportador e o site (foto na lista e no perfil, mandato no cartão).
6. **Página "Verificações"** (**feita em 23/11/2026**): a tabela de conferências, os motivos, a frase fixa e as 5 divergências com as 11 imagens refeitas em 23/11.
7. **Regra de dois anos e moradia de 2025** (**feitas em 23/11/2026**, [D048](decisoes.md#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador) e [D049](decisoes.md#d049-moradia-do-ano-anterior-com-três-fontes)): o perfil ganhou o botão para trocar de ano.
8. **Depois, em fatias:** o ranking e a comparação (antes, decidir quem entra no grupo) e, por último, "Sobre os dados".

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
| `docs: define o contrato dos dados do site e a foto do senador (D045)` | Contrato em rascunho e decisão da foto e do mandato |
| `feat(pipeline): adiciona o exportador dos dados do site` | Migração 003, ajuste da carga e exportador (branch `feat/exportador-site`) |

Na branch `feat/site-perfil`, a partir da `feat/exportador-site`:

| Título do commit | O quê |
|---|---|
| `feat(web): adiciona o site com o perfil do senador (D046)` | Esqueleto do site, perfil com dados reais e lista provisória |
| `feat(web): adiciona a home com busca e a foto oficial` | Home, cartões de mesma altura e suporte à foto (branch `feat/site-home`) |
| `feat(web): dá estilo aos selos de partido e UF e aumenta as fotos` | Selos e retratos maiores na lista |

Na branch `feat/site-revisao`, a partir da `feat/site-home` (20/11/2026):

| Título do commit | O quê |
|---|---|
| `feat(web): adiciona o partido sem sigla, o uso curto e as datas coladas` | Funções de apresentação com testes (21 no total) |
| `feat(web): refaz a home, fixa o cabeçalho e remove o rodapé` | Abertura com retratos sorteados, "Como funciona", busca, cabeçalho fixo sem menu; rodapé removido |
| `feat(web): refaz o perfil do senador e os textos das guias` | Cartão único da foto e dos dados, resumo de seis cartões, guias fechadas e textos em linguagem simples |
| `refactor(web): remove a leitura das verificações, que nenhuma tela usa` | Código sem uso |
| `docs: registra a revisão do site e atualiza os documentos` | D046 e demais documentos |

## Registro dos commits de 23/11/2026

Três pull requests, cada um a partir da `main` do anterior:

| PR e branch | O quê |
|---|---|
| #6, `fix/uso-texto-um-mes` | Concordância de "Usou no mês" e o texto do contrato sobre o salário-base |
| #7, `feat/perfil-foto-mandato` | `feat(pipeline): verifica a foto e o mandato do senador (D045)`; `feat(web): mostra mandato e foto na lista e libera a imagem na CSP`; `feat(pipeline): reduz as fotos para o site carregar mais rápido (D047)`; `docs: registra foto, mandato, CSP, cópias das fotos e a recarga de 23/11` |
| #8, `feat/pagina-verificacoes` | `docs: refaz as imagens de prova com a captura de 23/11/2026`; `feat(pipeline): processa só o ano atual e o anterior (D048)`; `feat(pipeline): confere a moradia do ano anterior (3 fontes, D049)`; `feat(web): página Verificações, troca de ano e moradia por ano`; `docs: registra dois anos, a moradia de 2025 e a revisão geral` |

