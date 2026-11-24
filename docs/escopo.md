# Escopo

O que o Senadados vai entregar, tela por tela, e em que ordem. Este documento se baseia nos dados **medidos** (veja [fontes-de-dados.md](fontes-de-dados.md)) e nas decisões já tomadas (veja [decisoes.md](decisoes.md)). Onde algo ainda não foi verificado, está escrito.

**Status:** escrito em 11/11/2026 e atualizado em 23/11/2026 (regra de dois anos, [D048](decisoes.md#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador); moradia do ano anterior, [D049](decisoes.md#d049-moradia-do-ano-anterior-com-três-fontes); página "Verificações"). Muda conforme o projeto avançar; cada mudança relevante vira uma decisão registrada.

---

## 1. Princípio de produto

> O Senadados **mostra os valores que o Senado publica e ajuda cada pessoa a interpretá-los**. Não julga se algo está dentro ou fora da lei: quem quiser investigar isso pesquisa por conta própria ([D024](decisoes.md#d024-sem-camada-jurídica)).

Regras que valem para todas as telas:

1. **Só o comprovado** ([D025](decisoes.md#d025-só-o-comprovado-a-prova-real)): o que não tiver prova, ou tiver divergência sem explicação, não aparece. Não há aviso na tela do senador; o que está pendente fica listado só na página "Verificações".
2. **Sem estimativas.** Nada calculado por inferência que não se possa provar.
3. **Sem afirmar legalidade.** Nenhum "dentro da lei", nenhum limite legal, nenhum "quanto pode".
4. **No máximo uns 6 números em destaque** por tela. O resto fica atrás de um clique.
5. **Todo número vem com referência tirada dos dados:** comparação com os outros senadores em exercício, histórico do próprio senador, parte do total.
6. **Frases antes de tabelas.**
7. **Linguagem neutra** ([D010](decisoes.md#d010-linguagem-neutra)): descreva o fato ("o maior mês foi março"), nunca "suspeito" ou "irregular".
8. **Cada número mostra de onde vem:** o dado no Senado e a data ([D009](decisoes.md#d009-citação-da-fonte-em-toda-página)).
9. **Funciona no celular primeiro.**
10. **Tudo ou nada, para o que compara senadores:** um dado que compara senadores (ranking, posição) só aparece se todos os senadores em exercício o tiverem e se os dados baterem para todos. **Dados descritivos de cada senador** (contato, equipe do gabinete) aparecem para quem foi provado, e somem para todos se mais de 5% falharem ([D037](decisoes.md#d037-exibição-por-tipo-de-dado-e-freio-de-segurança)).

## 2. Quem usa

| Pessoa | O que quer | O que o site precisa ter |
|---|---|---|
| **Cidadão curioso** | Saber como o senador do seu estado usa os recursos | Busca simples, perfil claro, frases em vez de tabelas |
| **Jornalista ou pesquisador** | Dados confiáveis, citáveis e comparáveis | Fonte e data visíveis, relatório de verificações, API aberta |
| **Quem avalia o projeto** (portfólio) | Decisões técnicas justificadas | Repositório documentado, API documentada, README claro |

## 3. Quem entra no site

Só os **senadores em exercício**, definidos todo dia pela lista oficial do Senado ([D026](decisoes.md#d026-só-senadores-em-exercício)).

- **Em 23/11/2026:** 81 (71 titulares e 10 suplentes). Em 19/11 um titular que estava fora voltou ao exercício e o suplente dele saiu da lista; o suplente saiu do site e do banco, como a D026 manda.
- **Quando entra:** assim que aparece na lista. A página mostra "sem dados ainda" até haver dados.
- **Quando sai:** deixa o site e a API no dia em que sai da lista. Em fevereiro de 2027, 54 mandatos terminam, então até 54 páginas podem sair de uma vez, dependendo de quem for reeleito.
- **Histórico:** só o ano atual e o anterior, com troca de ano na página do senador ([D048](decisoes.md#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador)). Antes de 23/11/2026 era de 2008 em diante.
- **Fora:** ex-senadores, aposentados e pensionistas.
- **Regra de agregado:** nenhum total, mediana ou ranking é apresentado como "do Senado". Toda comparação diz "entre os senadores em exercício em [data]".

## 4. Telas do MVP

### 4.1 Início
- **Abertura:** o nome "senadados", uma frase sobre o que são os dados ("O que o Senado publica sobre cada senador, de forma simples"), seis pílulas que espelham as guias do perfil e um mosaico de 12 retratos oficiais sorteados a cada visita. Feita em 20/11/2026.
- **Como funciona:** três cartões (dados oficiais, só o comprovado, sem julgamento).
- **Busca** por nome (homem ou mulher, sem exigir acento), com filtro por estado e partido, e o selo "N senadores em exercício".
- **Ainda não existem:** destaques que comparam senadores (seguem o "tudo ou nada" da D037) e os links para "Sobre os dados" e "Verificações", que dependem de as páginas existirem.

### 4.2 Perfil do senador (a tela principal)
Cada senador tem endereço próprio (por exemplo, `/senador/nome`), e o outro ano tem o seu (`/senador/nome/2025/`): um botão perto do título do resumo troca a página inteira para o ano anterior ([D048](decisoes.md#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador)); salário, equipe e contato só aparecem no ano atual, porque não há como provar esses dados para o outro. A página tem, à esquerda e **fixa**, um cartão com a foto, o nome, o partido, a UF e os quatro dados principais. À direita, **abre com o resumo do ano em seis cartões** (salário, verba, mês de maior uso, equipe do gabinete, moradia e quem vendeu ou prestou serviço) e depois traz seis guias que se abrem, **todas fechadas** ao entrar. A "posição entre os senadores" ainda não existe (depende do ranking, 4.3).

**Molde de cada pergunta** (igual em todas, tudo recolhido por padrão):

| Linha | O que mostra |
|---|---|
| **O que é** | O termo em linguagem simples, nas palavras do próprio Senado |
| **Quanto** | O valor, com a referência tirada dos dados |
| **De onde vem este número** | Três partes fixas: **onde o Senado publica**, **como chegamos neste número** e **atualizado em**, com o link para o portal do Senado |

Não há selos como "comprovado" ou "fonte única" na tela. As palavras técnicas (API, consulta, CNPJ sem explicar) ficam fora do texto.

**Blocos do perfil:**

| Bloco | Mostra | Estado hoje |
|---|---|---|
| **Quem é** | Foto oficial com crédito, partido, estado, mandato, titular ou suplente. | Pronto. Foto e mandato são provados pela verificação "perfil" ([D045](decisoes.md#d045-foto-e-mandato-do-senador-com-o-endereço-oficial-do-senado-e-verificação-entre-duas-listas), 23/11/2026); a foto também aparece na lista da home |
| **Salário** | Salário-base do último mês da folha e o valor depois dos descontos (o Senado chama o primeiro de "remuneração básica") | Provado para 79 de 81 ([D041](decisoes.md#d041-verificação-automática-do-salário-pela-identidade-do-senador)); 2 suplentes ficam sem salário |
| **Verba (a cota)** | Total do ano e do mês, mês a mês, por categoria, e a posição entre os outros senadores em três faixas | Provado para o ano atual e o anterior ([D048](decisoes.md#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador); em 23/11/2026, 2026: 72 idênticos e 7 explicados, 2025: 67 e 5). Os anos de 2008 a 2024 deixaram de ser processados |
| **Quem vendeu ou prestou serviço** | Maiores fornecedores (empresas) e "pessoas físicas" agrupadas ([D008](decisoes.md#d008-pessoas-físicas-agrupadas-e-cpf-nunca-exibido)) | A partir de 2009 |
| **Gabinete: onde fica, contato e equipe** | **Onde fica** (endereço), **como falar** (telefones completos, um por linha, e e-mail, só para quem tem) e o número de pessoas, do resumo oficial. **Sem custo estimado** ([D031](decisoes.md#d031-onde-fica-o-gabinete-endereço-entra-telefone-e-mail-e-escritório-de-apoio-ficam-fora)) | Endereço, telefones e e-mail provados ([D040](decisoes.md#d040-verificação-automática-do-contato-do-gabinete)); equipe provada em 80 de 81 gabinetes ([D036](decisoes.md#d036-verificação-automática-da-equipe-do-gabinete-por-vínculo)) |
| **Moradia** | Uso de imóvel funcional e de auxílio-moradia **mês a mês**, no ano atual e no anterior ([D049](decisoes.md#d049-moradia-do-ano-anterior-com-três-fontes)) | Em 18/11/2026: 76 de 81 idênticos, 1 explicado, 4 pendentes ([D039](decisoes.md#d039-verificação-automática-da-moradia-mês-a-mês)); em 23/11/2026, 2026: 77 + 1 explicado + 3 pendentes e 2025: 80 + 1 explicado |
| **Mês de maior uso** | O mês de maior valor da verba, destacado no gráfico mês a mês, em um cartão do resumo e em um aviso dentro da guia da verba. **Só aparece com dois meses ou mais.** Só o fato, sem julgamento ([D030](decisoes.md#d030-destaque-do-maior-mês-no-lugar-do-alerta-fora-do-padrão)) | Sai da mesma conta do gráfico |

**O que aparece e o que não aparece:**

| Situação do número | Na tela |
|---|---|
| Bate nas bases do Senado, ou a diferença é explicada | O número, com "De onde vem este número" |
| Só existe em um lugar do Senado, e passou nas checagens internas | O número, com "De onde vem este número" |
| Não se consegue provar, ou há divergência sem explicação | **Não aparece.** Nada de caixa de aviso. Fica na página "Verificações" |

### 4.3 Ranking e comparação
- **Ranking** do uso da verba no ano, só entre os senadores em exercício, filtrável por estado, região e partido ([D022](decisoes.md#d022-ranking-nacional-com-contexto-de-estado-e-região)). Nunca com o rótulo "do Senado".
- **Comparação lado a lado de dois senadores** ([D021](decisoes.md#d021-comparação-lado-a-lado-entra-no-mvp)): salário, verba usada, equipe e gasto por categoria, com duas cores validadas para daltonismo e contraste.
- Não há aviso sobre "limites por estado": seria uma afirmação sobre regra. A justiça da comparação é mostrada com dados do próprio grupo.

### 4.4 Sobre os dados e glossário
- De onde vêm os dados, quando foram atualizados e o que significam os termos (cota, gabinete, escritório de apoio), **sempre nas palavras do próprio Senado, com a fonte**.
- O que o site **não** faz: não julga legalidade, não audita o Senado, não mostra tudo o que o Senado paga.
- **Como pesquisar mais:** links para o portal oficial de transparência e de normas do Senado, sem dizer qual norma se aplica.
- Como citar o Senadados e a fonte original.

### 4.5 Verificações (nova)
- **Estado:** feita em 23/11/2026 (`/verificacoes/`): a tabela por conferência, os motivos de quem ficou de fora, a frase fixa e a seção de divergências com as imagens. Ainda não tem o canal para reportar erro nem o registro de correções.
- A lista de checagens feitas e o resultado de cada uma, por exemplo "cota de 2026: 73 idênticos, 7 explicados".
- Uma seção **“Onde os dados do Senado não batem entre si”**, com cada divergência provada por **prints** das telas e dos arquivos do Senado, sem dizer qual número está certo, nem o motivo, nem o que faremos a respeito ([D038](decisoes.md#d038-documento-público-de-divergências-com-prova-em-imagem)). Só entra o que tem print. O texto está em [divergencias-nos-dados-do-senado.md](divergencias-nos-dados-do-senado.md).
- As divergências encontradas nos dados do Senado, **agregadas**, com a explicação quando existe. Os **nomes dos senadores só aparecem na seção de divergências**, onde o print mostra a tela do Senado, que traz o nome ([D038](decisoes.md#d038-documento-público-de-divergências-com-prova-em-imagem)).
- Os dados **ocultos** aparecem **em contagem**, por verificação, com um motivo de uma lista fechada; **nomes de senadores só na seção de divergências**, onde há prova em imagem ([D037](decisoes.md#d037-exibição-por-tipo-de-dado-e-freio-de-segurança), [D042](decisoes.md#d042-banco-no-neon-só-dados-agregados-dois-esquemas-e-carga-repetível)).
- A frase fixa: "verificamos se as bases do Senado concordam entre si. Não auditamos os dados."
- Canal para **reportar um erro** e registro público das correções.

## 5. De onde vem cada informação

| Informação | Fonte | Verificação |
|---|---|---|
| Despesas da cota | API de despesas do Senado (ano atual e anterior), com o CSV e a página de cada senador como conferência | Verificada contra o resumo (em 18/11/2026, 2010 a 2026 batiam e 2008 e 2009 não; hoje só 2025 e 2026 são processados) ([D035](decisoes.md#d035-verificação-automática-da-cota-por-categoria-na-mesma-foto-dos-dados)) |
| Perfil e foto | APIs administrativa e legislativa | Pronto |
| Salário | Folha de pagamento mensal; identidade pela página do senador | Fonte única do valor, com cinco provas ([D041](decisoes.md#d041-verificação-automática-do-salário-pela-identidade-do-senador)) |
| Equipe | Resumo oficial por senador | Provada em 80 de 81 gabinetes; aparece para esses 80, e o gabinete sem explicação fica oculto ([D036](decisoes.md#d036-verificação-automática-da-equipe-do-gabinete-por-vínculo), [D037](decisoes.md#d037-exibição-por-tipo-de-dado-e-freio-de-segurança)) |
| Moradia | Página mensal de benefícios, resumo da API e lista do mês | 77 provados; 4 pendentes até o mês fechar ([D039](decisoes.md#d039-verificação-automática-da-moradia-mês-a-mês)) |
| Escritórios de apoio | API administrativa | A verificar |

## 6. Regras de exibição

1. **Ano em andamento:** 2026 mostra "dados parciais, até [mês]".
2. **Anos sem fornecedor:** o bloco "Quem vendeu ou prestou serviço" só existe nos anos processados, o atual e o anterior ([D048](decisoes.md#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador)). Os anos de 2008 e 2009, em que o dado não existia, saíram do escopo.
3. **Pessoas físicas:** nunca com nome nem CPF; sempre agrupadas ([D008](decisoes.md#d008-pessoas-físicas-agrupadas-e-cpf-nunca-exibido)).
4. **Equipe:** só números, nunca nomes ([D007](decisoes.md#d007-equipe-do-gabinete-só-em-números)).
5. **Linhas sem categoria:** aparecem como "Sem categoria". O total da verba inclui essas linhas, e o site explica que o resumo do Senado não as conta (59 linhas, R$ 162.260,84 em 2026, entre os senadores em exercício).
6. **Valores negativos:** somados normalmente, com a nota. A causa não foi confirmada.
7. **Dado que não se comprova:** não aparece, e nunca é preenchido com estimativa. A página "Verificações" diz o que está pendente.
8. **Nenhum termo jurídico:** o site não usa "legal", "ilegal", "irregular" nem "teto".

## 7. API (MVP)

Mesma base de dados do site, aberta para quem quiser consumir. Documentação automática em `/docs`.

| Endpoint | O que devolve |
|---|---|
| `GET /senadores` | Lista dos senadores em exercício, com filtros por estado e partido |
| `GET /senadores/{codigo}` | Perfil e benefícios |
| `GET /senadores/{codigo}/despesas?ano=` | Total por mês e por categoria, com o mês de maior valor |
| `GET /senadores/{codigo}/fornecedores?ano=` | Maiores fornecedores (empresas) e total de pessoas físicas |
| `GET /ranking?ano=&uf=&partido=` | Ranking entre os senadores em exercício |
| `GET /verificacoes` | O relatório de verificações |
| `GET /metadados` | Fontes, datas de atualização e limitações |

**Regras:** só entrega o que passou na verificação. A API devolve os dados já agrupados, sem CPF e sem nome de pessoa física. O site **não depende** da API em tempo real ([D004](decisoes.md#d004-fastapi-no-render-e-o-site-não-depende-dela)).

## 8. Destaque do maior mês

- **O que faz:** no gráfico mês a mês da verba, destaca o mês de maior valor: "Mês de maior uso: março de 2026, R$ 43 mil".
- **O que não faz:** não compara com limite, não calcula "padrão", não tem alerta. É só um fato que se confere no próprio gráfico ([D030](decisoes.md#d030-destaque-do-maior-mês-no-lugar-do-alerta-fora-do-padrão)).
- **Modelo de anomalias:** fica para a versão 2, opcional. Se voltar, só entra com o critério de aprovação da [D023](decisoes.md#d023-critério-para-aprovar-o-modelo).

## 9. Versões

### Versão 0: fundação (sem tela)
Pipeline que baixa, valida (Pandera) e limpa os dados. **Camada de verificação** ([D025](decisoes.md#d025-só-o-comprovado-a-prova-real)): cruzamentos entre as bases do Senado, relatório e falha fechada. Banco no Neon. Testes com os casos de sujeira conhecidos.

### Versão 1: MVP
Telas 4.1 a 4.5, API do item 7, atualização diária e documentação completa.

**O MVP está pronto quando:**
- todos os senadores em exercício têm perfil, e cada número exibido passou na verificação, e o que não passou não aparece;
- cada número mostra de onde vem e a data;
- o pipeline roda sozinho todo dia e **falha fechado**;
- a página "Verificações" está no ar;
- o site funciona em tela de celular;
- README, `docs/` e decisões estão atualizados.

### Versão 2
- Atuação parlamentar, só com resumos ([D019](decisoes.md#d019-atuação-parlamentar-na-versão-2)). Depende de entender os códigos de voto.
- Páginas de fornecedores (empresas).
- Gastos fora da cota, se houver como explicá-los com precisão (saíram do MVP em 12/11/2026, [D028](decisoes.md#d028-gastos-fora-da-cota-e-moradia-entram-só-provados)).
- Modelo de anomalias, opcional, com critério de aprovação ([D023](decisoes.md#d023-critério-para-aprovar-o-modelo)).

### Versão 3 (talvez)
Fontes de fora do Senado, como o TSE, só para conferir identidade. Aumenta o escopo e a responsabilidade.

## 10. Fora do escopo

- **Qualquer camada jurídica:** limites legais, "quanto pode", "dentro" ou "fora" da lei.
- **Estimativas:** inclusive o custo do gabinete.
- **Ex-senadores, aposentados e pensionistas.**
- Contas de usuário, login, comentários.
- Nomes de assessores, remuneração individual de servidores ou CPF.
- Detector público de sobrenome igual ao do senador ([D008](decisoes.md#d008-pessoas-físicas-agrupadas-e-cpf-nunca-exibido)).
- Dados da Câmara dos Deputados ou de outros órgãos.
- Aplicativo móvel nativo.

## 11. Qualidade esperada

Metas a medir, não resultados já obtidos:
- Legível em tela de 375 px de largura, sem rolagem horizontal.
- Contraste adequado e navegação por teclado nas telas principais.
- Páginas leves, geradas antecipadamente.
- Testes automáticos para as regras de limpeza, para a ligação entre bases e para cada verificação da prova real.

## 12. Pendências que afetam o MVP

| Item | Situação | O que fazer |
|---|---|---|
| Moradia: 3 casos pendentes (23/11/2026; eram 4 em 18/11) | A lista é de novembro e a página mensal vai até outubro: períodos diferentes, causa provável, **não provada** | A verificação diária reconfere; quando a página mensal incluir novembro, o caso se resolve sozinho |
| Salário | 2 suplentes que assumiram em outubro: duas matrículas com o mesmo nome e folha suplementar com valores | Ficam sem salário; a verificação diária reconfere com a folha de novembro |
| Equipe | **Verificada por gabinete**: 77 de 81 idênticos em 23/11/2026 (80 de 81 em 18/11). Sem explicação: Camilo Santana (1 efetivo a mais no resumo), Esperidião Amin e Nelsinho Trad Filho (1 comissionado a mais no resumo e na tela) e Wellington Dias (voltou em 19/11; a lotação ainda não foi publicada). **A 1 caso do freio de 5%** (D037) | Perguntar ao Senado; quando explicarem, o gabinete aparece sozinho na próxima verificação. A regra do freio fica para decidir com os dados da rotina diária |
| Cota de outros anos | **Feito em 18/11/2026** ([D035](decisoes.md#d035-verificação-automática-da-cota-por-categoria-na-mesma-foto-dos-dados)): 2010 a 2026 batiam e 2008 e 2009 não (o resumo de 2008 estava vazio e o de 2009 era menor que as despesas); **desde 23/11/2026 esses anos não são mais processados** (D048) | Nenhuma: os anos antigos saíram do escopo |
| Linhas sem categoria | O Senado não explica por que o resumo as deixa de fora | Perguntar pelo canal oficial; mostrar com a explicação |
| Internet Archive | Acusa cópia, mas não consegui listar | Testar de novo |
| Virada de 2027 | Até 54 páginas saem de uma vez | Decidido: apagar os dados de quem sair (banco, arquivos brutos, site e API) |
| Pessoas físicas ([D008](decisoes.md#d008-pessoas-físicas-agrupadas-e-cpf-nunca-exibido)) | Proteções mantidas; risco de LGPD aceito pelo mantenedor, por serem dados públicos | Nenhuma ação |
| Limites dos planos gratuitos | Neon reconfirmado na página oficial em 19/11/2026 ([D042](decisoes.md#d042-banco-no-neon-só-dados-agregados-dois-esquemas-e-carga-repetível)); Render, Cloudflare Pages e GitHub Actions seguem em fontes secundárias | Reconfirmar os três antes de publicar |
| Foto dos senadores | Carregar a foto do endereço oficial do Senado, com o crédito "Foto oficial publicada pelo Senado Federal" | **Feito.** Decidido em 19/11/2026 ([D045](decisoes.md#d045-foto-e-mandato-do-senador-com-o-endereço-oficial-do-senado-e-verificação-entre-duas-listas)); em 23/11/2026 a lista da home passou a mostrar a foto e o site passou a usar cópias reduzidas do próprio site, com o endereço oficial como reserva ([D047](decisoes.md#d047-cópias-reduzidas-das-fotos-oficiais-com-pillow)) |

## 13. Ordem de construção

| # | Etapa | Estado em 23/11/2026 |
|---|---|---|
| 1 | Pipeline de despesas, com validação e testes | **Feito** ([D033](decisoes.md#d033-coleta-local-que-só-grava-quem-está-em-exercício), [D034](decisoes.md#d034-limpeza-com-validação-em-sqlite-local-sem-nome-nem-documento-de-pessoa-física)) |
| 2 | **Camada de verificação** (cruzamentos, relatório, falha fechada) | **Feito** para cota, equipe, moradia, contato e salário ([D035](decisoes.md#d035-verificação-automática-da-cota-por-categoria-na-mesma-foto-dos-dados) a [D041](decisoes.md#d041-verificação-automática-do-salário-pela-identidade-do-senador)) |
| 3 | Banco e carga completa dos senadores em exercício | **Feito em 19/11/2026** (banco no ar com os dados provados de 18/11; a atualização diária automática ainda falta; [D042](decisoes.md#d042-banco-no-neon-só-dados-agregados-dois-esquemas-e-carga-repetível)) |
| 4 | **Contrato dos dados e exportador** (arquivos JSON gerados do esquema `publico`; [contrato](contrato-dos-dados.md); [D044](decisoes.md#d044-site-antes-da-api-com-dados-em-arquivos-json-gerados-do-esquema-público)) | **Feito em 19/11/2026**, rodando contra a produção |
| 5 | Site: perfil (salário quando provado, equipe e moradia), depois início, ranking, comparação, "Sobre os dados" e "Verificações" | **Em andamento:** a home (abertura, "Como funciona" e busca) e o perfil estão feitos (20/11/2026, [D046](decisoes.md#d046-site-em-nextjs-16-com-exportação-estática-fontes-hospedadas-e-testes-com-vitest)), com foto e mandato desde 23/11/2026 ([D045](decisoes.md#d045-foto-e-mandato-do-senador-com-o-endereço-oficial-do-senado-e-verificação-entre-duas-listas)); a página "Verificações" e o botão para trocar de ano no perfil ([D048](decisoes.md#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador), [D049](decisoes.md#d049-moradia-do-ano-anterior-com-três-fontes)) desde 23/11/2026; faltam ranking, comparação e, por último, "Sobre os dados" |
| 6 | Destaque do mês de maior uso | **Feito em 20/11/2026** (cartão, gráfico e aviso no perfil) |
| 7 | Automação diária e publicação | A fazer |
| 8 | API (depois do site; [D044](decisoes.md#d044-site-antes-da-api-com-dados-em-arquivos-json-gerados-do-esquema-público)) | A fazer |
| 9 | Revisão final da documentação | A fazer (uma revisão parcial foi feita em 23/11/2026) |

A ordem foi alterada em 19/11/2026: o site vem antes da API ([D044](decisoes.md#d044-site-antes-da-api-com-dados-em-arquivos-json-gerados-do-esquema-público)).

Cada etapa termina com a documentação atualizada e um commit no padrão do [AGENTS.md](../AGENTS.md). O resumo do que existe e do que vem a seguir está em [andamento.md](andamento.md).

## 14. Perguntas em aberto para o mantenedor

Nenhuma no momento.

*Resolvidas: apagar os dados de quem sair e dispensar a revisão jurídica sobre LGPD (11/11/2026); suplentes em exercício entram e o alerta vira o destaque do maior mês (12/11/2026).*
