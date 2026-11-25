# Registro de decisões

Cada decisão do projeto, com o motivo. Se uma decisão mudar, **não apague a antiga**: marque-a como substituída e escreva a nova. Assim o histórico mostra o raciocínio completo.

**Formato:** contexto, decisão, por quê, alternativas descartadas, status.
**Status:** `aceita` (vale) ou `provisória` (depende de dados que ainda não medimos).

Data das decisões iniciais: 11/11/2026. As atualizações trazem a própria data.

---

## Índice

| # | Decisão | Situação em 12/11/2026 |
|---|---|---|
| D001 | Python para pipeline, análise e API | Vale |
| D002 | PostgreSQL no Neon como banco | Vale |
| D003 | Site em Next.js estático no Cloudflare Pages | Vale |
| D004 | FastAPI no Render; o site não depende dela | Vale (limites gratuitos a reconfirmar) |
| D005 | API como fonte principal, CSV para conferência | Vale |
| D006 | Modelo de anomalias | Adiada para a versão 2 (veja D030) |
| D007 | Equipe do gabinete só em números | Vale |
| D008 | Pessoas físicas agrupadas e CPF nunca exibido | Vale |
| D009 | Citação da fonte em toda página | Vale (por número, veja D025) |
| D010 | Linguagem neutra | Vale |
| D011 | Idioma | Vale |
| D012 | Commits padronizados e sem autoria de IA | Vale |
| D013 | Repositório público | Vale |
| D014 | Dados crus fora do git | Vale |
| D015 | Gabinete pelo resumo oficial | Vale (prova por gabinete antes de exibir) |
| D016 | Salário ligado pelo nome completo, com validação mensal | Vale (só ligação inequívoca) |
| D017 | Custo de gabinete como estimativa agregada | **Substituída por D025** |
| D018 | Partido do ano pela filiação mais recente | Fora do MVP (escopo D026) |
| D019 | Atuação parlamentar na versão 2 | Vale |
| D020 | O MVP não depende do modelo | Vale |
| D021 | Comparação lado a lado entra no MVP | Vale |
| D022 | Ranking nacional com contexto de estado e região | Vale (revisar quando a tabela for localizada) |
| D023 | Critério para aprovar o modelo | Não se aplica ao MVP |
| D024 | Sem camada jurídica | Vale |
| D025 | Só o comprovado (a prova real) | Vale |
| D026 | Só senadores em exercício | Vale (o histórico desde 2008 foi alterado pela D048) |
| D027 | Como conferir os dados | Vale |
| D028 | Gastos fora da cota e moradia | Moradia vale; gastos fora da cota saíram do MVP |
| D029 | Identidade visual | Vale |
| D030 | Destaque do maior mês no lugar do alerta | Vale |
| D031 | Onde fica o gabinete: contato | Vale (revista em 12/11/2026) |
| D032 | Organização do repositório e dos documentos | Vale |
| D033 | Coleta local que só grava quem está em exercício | Vale |
| D034 | Limpeza com validação, em SQLite local, sem nome nem documento de pessoa física | Vale |
| D035 | Verificação automática da cota por categoria, na mesma foto dos dados | Vale (hoje só para o ano atual e o anterior, D048) |
| D036 | Verificação automática da equipe do gabinete, por vínculo | Vale (a consequência foi substituída pela D037) |
| D037 | Exibição por tipo de dado e freio de segurança | Vale |
| D038 | Documento público de divergências, com prova em imagem | Vale |
| D039 | Verificação automática da moradia, mês a mês | Vale |
| D040 | Verificação automática do contato do gabinete | Vale |
| D041 | Verificação automática do salário pela identidade do senador | Vale (altera a ligação da D016) |
| D042 | Banco no Neon: só dados agregados, dois esquemas e carga repetível | Vale (o resumo virou tabela, ver D043) |
| D043 | Migrações em SQL puro, driver psycopg e carga que ensaia antes de gravar | Vale (aplicada na produção em 19/11/2026) |
| D044 | Site antes da API, com dados em arquivos JSON gerados do esquema público | Aceita (contrato dos JSON na versão 2 desde 23/11/2026) |
| D045 | Foto e mandato do senador, com o endereço oficial do Senado e verificação entre duas listas | Aceita (implementada em 23/11/2026) |
| D046 | Site em Next.js 16 com exportação estática, fontes hospedadas e testes com Vitest | Aceita |
| D047 | Cópias reduzidas das fotos oficiais, com Pillow | Aceita (implementada em 23/11/2026) |
| D048 | Só o ano atual e o anterior, com troca de ano na página do senador | Aceita (implementada em 23/11/2026; altera a D026) |
| D049 | Moradia do ano anterior, com três fontes | Aceita (implementada em 23/11/2026; completa a D048 e a D039) |
| D050 | Comparação de dois senadores, lado a lado | Aceita (implementada em 24/11/2026; detalha a D021) |

---

## D001: Python para pipeline, análise e API

- **Contexto:** o projeto tem quatro frentes (dados, ML, API e site) e nenhum orçamento.
- **Decisão:** usar Python (Pandas, Pandera, scikit-learn, FastAPI) em tudo, exceto o site.
- **Por quê:** a mesma linguagem cobre limpeza, modelo e API. Os arquivos são pequenos, então a lentidão do Python não pesa.
- **Descartado:** Excel/Power BI (não mostram código), R (fraco para API), JavaScript para dados (ecossistema menor).
- **Status:** aceita.

## D002: PostgreSQL no Neon como banco

- **Contexto:** a API publicada não tem disco permanente, e o dado atualiza todo dia.
- **Decisão:** PostgreSQL hospedado no plano gratuito do Neon.
- **Por quê:** gratuito e, segundo a página da própria empresa, não cobra excesso: ao estourar o limite as gravações falham. Sem orçamento, isso evita surpresa de fatura.
- **Descartado:** SQLite, por só atualizar a cada nova publicação.
- **Tamanho medido:** os 398.624 registros de 2008 a 2026 ocupam cerca de 126 MB em SQLite com dois índices, então devem caber nos 1 GB do Neon. *No PostgreSQL pode ser maior; não foi medido.*
- **Riscos:** limite de 1 GB por projeto e 100 horas de computação por mês.
- **Plano B:** arquivos Parquet ou SQLite versionados, também de custo zero.
- **Status:** aceita.
- **Atualização (18/11/2026):** o banco local da D034 (SQLite) ocupa **34 MB** com os 154.298 registros dos senadores em exercício e todas as tabelas de verificação, bem abaixo dos números estimados acima, que contavam todos os ex-senadores. O Neon entra na etapa 3 da ordem de construção.
- **Atualização (19/11/2026):** só os dados **agregados** vão para o Neon, então o que será gravado lá é bem menor do que as estimativas acima (as 154.298 despesas linha a linha ficam no SQLite local). Detalhes na [D042](#d042-banco-no-neon-só-dados-agregados-dois-esquemas-e-carga-repetível).

## D003: Site em Next.js estático no Cloudflare Pages

- **Contexto:** o site precisa de endereço por senador, bom desempenho no celular e aparência cuidada, para qualquer cidadão.
- **Decisão:** Next.js (React, TypeScript) exportado como páginas prontas, hospedado no Cloudflare Pages.
- **Por quê:** os dados mudam uma vez por dia; páginas prontas são rápidas e baratas. O Cloudflare Pages tem plano gratuito sem restrição a uso não comercial.
- **Descartado:** Streamlit (limita endereço por senador e design) e Vercel (plano gratuito só para uso pessoal e não comercial).
- **Status:** aceita.

## D004: FastAPI no Render, e o site não depende dela

- **Contexto:** hospedagem gratuita de API quase sempre "dorme" quando parada. Pesquisado em 11/11/2026 em fontes secundárias: o Render dorme após 15 minutos e leva de 30 a 60 segundos para acordar.
- **Decisão:** publicar a FastAPI no plano gratuito do Render como API pública, mas o site lê arquivos JSON gerados pelo pipeline, nunca a API.
- **Por quê:** se a API dormir, o cidadão não percebe.
- **Descartado:** Fly.io e Railway (sem plano gratuito de verdade).
- **Status:** aceita. *Limites do plano gratuito a reconfirmar nas páginas oficiais.*
- **Atualização (19/11/2026):** os limites do plano gratuito da Render foram lidos na página oficial (que não traz data): **750 horas de instância por mês por workspace**, divididas entre os serviços grátis; quando acabam, a Render suspende todos os serviços grátis do workspace até o mês seguinte; o serviço dorme após 15 minutos sem tráfego e leva cerca de 1 minuto para acordar. A mesma página diz que o plano grátis **não é para aplicações em produção**. A API do senadados ficará na Render, em Ohio, conforme a [D042](#d042-banco-no-neon-só-dados-agregados-dois-esquemas-e-carga-repetível). A [D044](#d044-site-antes-da-api-com-dados-em-arquivos-json-gerados-do-esquema-público) confirma que o site vem antes da API e lê arquivos, não a API.

## D005: API como fonte principal, CSV para conferência

- **Contexto:** a amostra mostrou que o CSV de 2008 está congelado desde agosto de 2021 e que a API tem 8 valores diferentes em 2.449 linhas (sempre menores). A API também traz o código do senador.
- **Decisão:** o pipeline lê a API; o CSV serve para comparar e detectar divergências.
- **Por quê:** a API parece refletir correções posteriores e tem uma chave estável por senador (nomes podem se repetir ou mudar).
- **Reforço (API completa):** a API entrega o CPF de pessoa física **mascarado**, enquanto o CSV o traz completo. Usar a API significa que o pipeline nunca recebe o CPF inteiro.
- **Risco:** o motivo exato da diferença de valores não foi confirmado.
- **Status:** aceita.
- **Atualização (11/11/2026):** a API segue como fonte principal. A página de transparência de cada senador e sua exportação passam a ser canais de conferência (veja D027).

## D006: Modelo de anomalias

- **Contexto:** medimos o `detalhamento` nos 19 anos. Está vazio até 2010, chega a mais de 80% entre 2013 e 2018 e cai para cerca de 35 a 40% nos anos recentes, que são os que mais interessam ao cidadão.
- **Decisão:** começar com Isolation Forest, que compara cada mês com o histórico do próprio senador, usando valor, categoria e fornecedor, e dá o motivo do alerta. A classificação de texto fica como complemento possível para 2013 em diante, não como base.
- **Por quê:** não depende de texto e é fácil de explicar. Como a descrição vem diminuindo, um modelo apoiado nela perderia força justamente nos dados mais atuais.
- **Ainda não testado:** a qualidade do modelo não foi avaliada, e não há "resposta certa" para checar. Antes de mostrar alertas ao público, é preciso definir como validar (por exemplo, revisar à mão uma amostra de alertas).
- **Status:** aceita como ponto de partida; revisar após os primeiros testes.
- **Atualização (12/11/2026):** o modelo saiu do MVP e fica para a versão 2, se ainda fizer sentido (veja D030). O alerta do MVP é só o destaque do maior mês.

## D007: Equipe do gabinete só em números

- **Contexto:** a lista de servidores é pública e inclui nomes.
- **Decisão:** mostrar apenas quantidades e custos agregados, nunca nomes de assessores.
- **Por quê:** são pessoas comuns, não os agentes políticos que o projeto fiscaliza. Reduz risco com a LGPD.
- **Status:** aceita.

## D008: Pessoas físicas agrupadas e CPF nunca exibido

- **Contexto:** a coluna `CNPJ_CPF` traz CPFs completos de pessoas físicas que receberam reembolsos (por exemplo, aluguel pago a uma pessoa). Mostrar o nome permitiria, em tese, notar fornecedores com o mesmo sobrenome do senador, mas expõe pessoas comuns e pode gerar pedidos de remoção com base na LGPD.
- **Decisão (MVP):**
  - O site nunca mostra CPF, em nenhuma tela. Dados crus ficam fora do git.
  - Pessoas físicas **não aparecem com nome**. Entram agrupadas como "Pessoas físicas", com a quantidade de pagamentos, o total e o maior valor individual. Empresas (CNPJ) aparecem com nome.
  - Pessoa física e empresa são distinguidas pelo tamanho do número (CPF tem 11 dígitos; CNPJ tem 14).
  - Cada despesa aponta para a fonte oficial, para quem quiser conferir os detalhes no Senado (*a existência de uma página por documento ainda não foi verificada*).
  - O projeto **não terá** detector público de sobrenome igual ao do senador: gera falsos positivos (sobrenomes comuns) e sugere acusação, contra a regra de linguagem neutra (D010). Se for investigado, será como pesquisa à parte, e só se publica com prova externa.
- **Por quê:** a decisão é assimétrica. Esconder o nome agora pode ser desfeito depois; publicar não, porque o nome pode ser copiado, indexado e arquivado. O custo é perder transparência sobre pagamentos a pessoas físicas, atenuado pela indicação da fonte oficial. Pelos dados completos, esse custo é pequeno: pessoas físicas são de 1,3% a 3,1% dos registros e cerca de 3,5% do valor nos anos recentes.
- **Alternativa descartada por ora:** mostrar o nome e ocultar só o CPF. Mais transparência, mais risco de exposição.
- **Gatilho de revisão:** reavaliar depois de consulta a alguém com conhecimento jurídico em LGPD. Se o nome passar a ser exibido, entram as proteções: nunca CPF; páginas com nome de pessoa física sem indexação por buscadores (`noindex`) e sem busca por nome; canal de contato e procedimento escrito de remoção; base legal documentada (dado já público, finalidade de controle social).
- **Observação:** esta decisão não é aconselhamento jurídico. As afirmações sobre a LGPD não foram conferidas neste projeto.
- **Status:** aceita para o MVP, sujeita à revisão acima.
- **Atualização (11/11/2026):** o mantenedor decidiu **não tratar a LGPD como pendência**, por serem dados públicos publicados pelo Senado, e dispensou a consulta jurídica. As proteções continuam, porque custam pouco e protegem terceiros que não são políticos (fornecedores pessoas físicas e assessores): CPF nunca aparece, pessoas físicas ficam agrupadas e sem nome, e a equipe aparece só em número. Isto não é aconselhamento jurídico, e "dado público" não é isenção automática; o risco foi aceito pelo mantenedor.

## D009: Citação da fonte em toda página

- **Contexto:** os termos exigem, no máximo, citar a proveniência. Não há formato definido nem licença nomeada.
- **Decisão:** cada página mostra a fonte ("Senado Federal, dados abertos"), o endereço e a data de atualização, e o rodapé repete isso.
- **Por quê:** cumpre a única exigência documentada e dá transparência ao cidadão.
- **Status:** aceita.
- **Atualização (11/11/2026):** a citação agora vale por número: cada valor mostra "De onde vem este número", com o endereço do dado no Senado e a data (veja D025).
- **Atualização (20/11/2026):** o rodapé foi removido da home e do perfil, a pedido do mantenedor ([D046](#d046-site-em-nextjs-16-com-exportação-estática-fontes-hospedadas-e-testes-com-vitest)). A fonte e a data continuam em cada "De onde vem este número", dentro de cada guia do perfil. A home não mostra números do Senado além da contagem de senadores. A foto tem o crédito na dica que aparece ao passar o mouse.

## D010: Linguagem neutra

- **Decisão:** usar "fora do padrão", "acima da média dele", "incomum"; nunca "suspeito", "irregular" ou "fraude".
- **Por quê:** o modelo aponta o incomum, não o ilegal. Um gasto alto pode ser legítimo, e o projeto trata de pessoas reais.
- **Status:** aceita.

## D011: Idioma

- **Decisão:** documentação, commits e textos para o usuário em português do Brasil. Código em inglês, com termos do domínio do Senado em português (`senador`, `ceaps`).
- **Por quê:** o público é brasileiro, e o vocabulário do Senado não tem tradução fiel.
- **Status:** aceita (convenção inicial, pode mudar).

## D012: Commits padronizados e sem autoria de IA

- **Decisão:** commits no formato `tipo(escopo): descrição`, com o corpo explicando o porquê, e nenhuma linha atribuindo autoria a ferramentas de IA.
- **Por quê:** o histórico deve ser legível como diário do projeto, e os commits são do mantenedor. Detalhes no [AGENTS.md](../AGENTS.md).
- **Status:** aceita.

## D013: Repositório público

- **Contexto:** o plano gratuito do GitHub Actions vale para repositórios públicos, e o projeto é de portfólio.
- **Decisão:** repositório público, com dados crus e segredos fora do git.
- **Por quê:** viabiliza a atualização automática sem custo e mostra o trabalho.
- **Status:** aceita.

## D014: Dados crus fora do git

- **Decisão:** `data/raw/` fica no `.gitignore`. O repositório guarda o código que gera os dados, não os dados.
- **Por quê:** evita publicar CPFs de pessoas físicas, mantém o repositório leve e deixa claro que a fonte é o Senado.
- **Status:** aceita.

## D015: Gabinete pelo resumo oficial

- **Contexto:** há duas fontes para o tamanho do gabinete. O resumo oficial soma 1.723 pessoas. A lista de servidores inclui o próprio senador entre os lotados no gabinete (80 registros); sem ele, soma 1.722.
- **Decisão:** o site usa o número do resumo oficial e cita a data. A lista de servidores só serve para conferência e para agregados de custo, nunca para exibir nomes (D007).
- **Por quê:** é o número que o próprio Senado apresenta por senador, e a ligação não depende de casar nomes.
- **Status:** aceita. A diferença de uma pessoa entre os dois números está praticamente explicada.
- **Atualização (11/11/2026):** a diferença de uma pessoa no total foi explicada (a lista de servidores inclui o próprio senador), mas D025 exige a prova por gabinete antes de exibir. Casos que não baterem ficam ocultos.

## D016: Salário ligado pelo nome completo, com validação mensal

- **Contexto:** a folha de pagamento não usa o código do parlamentar. Pelo nome completo, 78 dos 81 senadores foram encontrados, sem repetições. O salário básico é de R$ 46.366,19 para 77 deles e diferente para um.
- **Decisão:** ligar pelo nome completo (normalizado, sem acento) e, a cada atualização, registrar quem ficou sem correspondência em vez de ignorar em silêncio. Mostrar o salário de cada senador como ele aparece na folha, sem supor que seja igual para todos.
- **Por quê:** o número exibido precisa ser o real, e erros de ligação devem ficar visíveis.
- **Status:** aceita.
- **Atualização (11/11/2026):** por D025, o salário só aparece quando a ligação for inequívoca (nome completo único na folha). Os 3 suplentes sem correspondência e o titular com valor diferente ficam sem salário até serem provados.

## D017: Custo de gabinete como estimativa agregada

- **Contexto:** é possível estimar o custo mensal da equipe ligando a lista de servidores à folha. A ligação só funciona por nome, e o resultado cobre 96,9% dos servidores e só algumas parcelas da remuneração.
- **Decisão:** exibir o custo do gabinete como **valor aproximado**, agregado por gabinete, com a explicação do que está e do que não está incluído. Nunca exibir remuneração individual de assessores (D007).
- **Por quê:** o número ajuda o cidadão a entender o peso da equipe, mas apresentá-lo como exato seria enganoso.
- **Status:** aceita; revisar a metodologia antes de publicar.
- **Atualização (11/11/2026):** **substituída por D025.** Não haverá estimativas: o custo do gabinete sai do projeto, porque só se mostra o que se comprova.

## D018: Partido do ano pela filiação mais recente

- **Contexto:** o perfil com partido e UF só existe para quem está em exercício. Para os demais, é possível reconstruir o partido a partir das datas de filiação e a UF a partir dos mandatos (cobertura de 97,8% e 100% dos pares senador-ano).
- **Decisão:** o partido de um senador em um ano é a filiação mais recente até 1º de julho daquele ano; os casos sem filiação ficam como "não informado".
- **Por quê:** regra simples, reproduzível e documentada. A escolha do dia 1º de julho é arbitrária, e quem trocou de partido no meio do ano pode aparecer com o partido "errado" em parte do ano.
- **Status:** aceita; validar com casos conhecidos de troca de partido.
- **Atualização (11/11/2026):** o escopo caiu para os senadores em exercício (D026). Partido e UF ao longo do tempo valem só para eles; a reconstrução para ex-senadores deixa de ser necessária.

## D019: Atuação parlamentar na versão 2

- **Contexto:** votações, autorias, relatorias, discursos e apartes existem e são volumosos (estimativa de cerca de 300 MB em JSON para os 81 senadores). O significado de vários códigos de voto não foi verificado, e os discursos vêm só dos últimos 30 dias por padrão.
- **Decisão:** deixar a atuação para a versão 2 e guardar no banco apenas resumos (contagens e participação), nunca o JSON cru.
- **Por quê:** o MVP já cobre quem é, quanto ganha, quanto gasta, para onde vai e quem trabalha com o senador. Calcular presença com códigos que não entendemos geraria números errados sobre pessoas reais.
- **Status:** aceita.

## D020: O MVP não depende do modelo

- **Contexto:** a qualidade do modelo de anomalias ainda não foi testada, e não existe uma "resposta certa" para conferir os alertas.
- **Decisão:** o bloco "Fora do padrão" do MVP funciona com o modelo ou com um plano B de regra simples e explicável (mês acima de um limite de desvios do próprio histórico). O modelo só entra se passar na validação manual de uma amostra de alertas, cuja meta mínima é definida antes do teste.
- **Por quê:** evita publicar alertas sobre pessoas reais sem saber se fazem sentido, e impede que o projeto fique parado esperando o modelo.
- **Status:** aceita.
- **Atualização (12/11/2026):** o plano B virou o plano único do MVP, na forma mais simples possível: destaque do maior mês (D030).

## D021: Comparação lado a lado entra no MVP

- **Contexto:** o mantenedor quer que o cidadão possa colocar dois senadores lado a lado.
- **Decisão:** a tela de comparação faz parte do MVP: salário, cota usada, tamanho e custo estimado do gabinete e gasto por categoria. Duas séries, com cores validadas para daltonismo e contraste nos modos claro e escuro, e legenda sempre presente.
- **Por quê:** responde direto à pergunta mais natural do cidadão ("e o outro senador, gasta mais?"). Com só duas séries, o gráfico continua legível.
- **Cuidado:** se os senadores forem de estados diferentes, aparece o aviso de que a cota varia por estado.
- **Status:** aceita.
- **Atualização (18/11/2026):** a comparação **não traz custo estimado do gabinete**: a D025 aboliu estimativas. Ela traz salário, verba usada, equipe e gasto por categoria, cada um só para quem foi provado (D037); se um dos dois senadores não tiver um dado, a comparação mostra "sem dado" naquela linha.

## D022: Ranking nacional com contexto de estado e região

- **Contexto:** a cota varia por estado, então comparar totais sem contexto pode ser injusto. Ordenar só dentro do mesmo estado resolveria o problema, mas cada estado tem três senadores, e um ranking de três não ajuda ninguém.
- **Decisão:** o ranking é nacional por padrão, mostra o estado de cada senador, permite filtrar por estado, região e partido e exibe sempre o aviso sobre a cota. A normalização pelo limite de cada estado (percentual do limite usado) fica como melhoria futura.
- **Por quê:** é a opção mais honesta com o que sabemos hoje. O percentual do limite seria o número mais justo, mas a tabela oficial de limites por estado **não foi encontrada** e não vamos supor valores.
- **Status:** aceita; revisar quando a tabela for localizada.
- **Atualização (11/11/2026):** o aviso "a verba varia por estado" foi retirado, porque é uma afirmação sobre regra (D024). A justiça da comparação passa a ser mostrada com dados do próprio grupo, e o ranking só compara os senadores em exercício (D026).

## D023: Critério para aprovar o modelo

- **Contexto:** o modelo de anomalias não tem "resposta certa" para conferência, e a decisão de publicar alertas sobre pessoas reais precisa de um critério fixado antes do teste.
- **Decisão (proposta do assistente, a confirmar pelo mantenedor):**
  1. Revisar **50 alertas** do modelo, sorteados com espalhamento por anos e senadores, e **25 meses sem alerta** sorteados.
  2. A avaliação é **às cegas**: o revisor vê o gráfico do mês contra o histórico do próprio senador, sem saber se o modelo o marcou.
  3. A pergunta é só "este mês é incomum para este senador?", e nunca "é irregular?".
  4. **Aprovado** se pelo menos **70%** dos alertas (35 de 50) forem considerados incomuns **e** o modelo não for pior que o plano B (regra simples) na mesma amostra.
  5. O modelo deve marcar poucos meses (meta em torno de 5% dos meses), senão vira ruído; a taxa será ajustada antes da revisão.
  6. Se ficar entre 60% e 70%, ampliar a amostra para 100 antes de decidir.
- **Por quê:** com 50 alertas, 70% de acerto tem margem de erro de mais ou menos 13 pontos, então é um teste grosseiro, mas já separa um modelo útil de um inútil. Incluir meses sem alerta evita aprovar um modelo que apenas marca muito. Comparar com o plano B impede que se pague complexidade sem ganho.
- **Observação:** os números (50, 25, 70%, 5%) são julgamentos, não resultados de pesquisa.
- **Status:** proposta aceita pelo mantenedor? **Pendente de confirmação.**
- **Atualização (12/11/2026):** **não se aplica ao MVP.** O critério só valerá se o modelo voltar na versão 2.

## D024: Sem camada jurídica

- **Contexto:** tentamos registrar a base legal de cada número (limite da cota por estado, salário, gabinete, escritório, moradia). A pesquisa mostrou que a tabela de 2026 por estado não foi localizada, que as fontes divergem sobre a norma do salário e que há um projeto de 2026 que pode mudar as regras de moradia. Cada lei e cada estado pedem uma interpretação.
- **Decisão:** o Senadados **mostra valores e ajuda a interpretá-los**: o que o número é, de onde vem, como se compara. **Não afirma se algo está dentro ou fora da lei**, não exibe limites legais nem "quanto pode". Cada pessoa pesquisa a legislação por conta própria, e o site indica onde começar (o portal oficial do Senado).
- **Por quê:** o projeto é forte no que o Senado publica como dado. Interpretar a lei exige uma responsabilidade que o projeto não tem, e um erro jurídico sobre pessoas reais seria o pior tipo de erro. Também reduz a manutenção.
- **O que sai:** as linhas "quem tem direito" e "quanto pode", a caixa "Ver o que diz a lei", a barra de percentual do limite e as etiquetas "a confirmar". O arquivo `docs/regras-legais.md` **não será criado**.
- **O que entra:** "O que é" nas palavras do próprio Senado, "De onde vem este número" e "Como pesquisar mais".
- **Status:** aceita.

## D025: Só o comprovado (a prova real)

- **Decisão:** todo número exibido precisa ter (1) um campo oficial de origem, (2) uma consulta documentada que o reproduza, (3) um teste automático e (4) uma data. Quando houver duas ou mais fontes do Senado para o mesmo número, elas devem concordar.
  - **Idêntico:** mostra.
  - **Divergência explicada e documentada:** mostra, com a explicação visível.
  - **Divergência inexplicada:** **não mostra** ("dado em verificação").
  - **Fonte única:** mostra com a etiqueta "fonte única: Senado", depois de checagens internas (as partes somam o total, sem duplicados, sem valores impossíveis).
  - **Sem estimativas:** nada que dependa de inferência não comprovada.
  - **Falha fechada:** se uma checagem quebrar num dia, o número fica oculto e o motivo vai para o relatório de verificações.
  - **Página pública "Verificações"** com as checagens e as divergências encontradas, agregadas e sem nomes.
- **O que a prova real prova:** que as bases do Senado concordam entre si e de onde o número nasce. **Não é uma auditoria**: se todas estiverem erradas do mesmo jeito, não percebemos. O site diz isso.
- **Evidência inicial:**
  - Cota de 2026: das despesas detalhadas contra o resumo de cada senador, **72 de 79 batem no centavo**. As 7 diferenças são exatamente linhas sem categoria (60 linhas, R$ 164.450,50), que a API inclui e o resumo não.
  - Moradia: resumo e lista pareciam divergir em 12 senadores. O resumo bate com a página mensal do Senado nos 12; 9 são explicados pelo período diferente (a lista cobre só o mês de emissão) e 3 seguem pendentes.
- **Substitui:** D017 (estimativa de custo do gabinete).
- **Status:** aceita.
- **Atualização (12/11/2026):** **na tela não há selos nem avisos.** Saem as etiquetas "comprovado" e "fonte única" e a caixa "dado em verificação": o que não se comprova **simplesmente não aparece**, e a lista do que está pendente fica só na página "Verificações". Em cada número, "De onde vem este número" segue um molde fixo, em linguagem simples, com três partes: **onde o Senado publica**, **como chegamos neste número** e **atualizado em**, com o link para o portal do Senado.
- **Atualização (12/11/2026):** **regra de grupo, "tudo ou nada".** Uma informação que vale para todos os senadores só aparece se todos os senadores em exercício a tiverem e se os dados baterem para todos. Se um só falhar, ninguém a recebe. Assim o site nunca mostra um dado para uns senadores e esconde de outros.
- **Atualização (12/11/2026):** **exceção à regra de tudo ou nada: dados de contato.** Telefone e e-mail aparecem para quem os tem; quem não tem, simplesmente não mostra, porque é uma informação de contato e não uma comparação entre senadores.
- **Atualização (18/11/2026):** **a conferência só vale se as duas bases forem baixadas no mesmo dia.** Ao refazer a cota de 2026 com os dados do mesmo dia, o resultado passou de "72 de 79 idênticos" para **74 de 81 idênticos e 7 explicados, nenhuma divergência sem explicação**. A diferença veio de o Senado ter atualizado os dados e de o número de linhas sem categoria da primeira medição incluir ex-senadores (agora: 59 linhas e R$ 162.260,84 entre os senadores em exercício). Detalhes em [verificacoes.md](verificacoes.md). A verificação automática do pipeline deve baixar tudo junto e registrar a data. (A contagem foi refeita depois pelo código ([D035](#d035-verificação-automática-da-cota-por-categoria-na-mesma-foto-dos-dados)): **73 idênticos e 7 explicados, entre os 80 senadores com valores**; Jorge Kajuru, sem valores nos dois lados, não entra na conta.)

## D026: Só senadores em exercício

- **Contexto:** são 81 em exercício (70 titulares e 11 suplentes), com 39% dos registros e 47% do valor do histórico. Quase todas as fontes ricas (resumo, benefícios, folha, escritórios, equipe) existem só para eles. Aposentados, pensionistas e ex-senadores antigos são pouco procurados. **54 dos 81 mandatos terminam em 2027.**
- **Decisão:**
  - O escopo é o conjunto de senadores em exercício, definido todo dia pela **lista oficial do Senado**. Os suplentes em exercício entram (confirmado pelo mantenedor em 12/11/2026). Quem tiver poucos meses de dados no período aparece com "poucos meses de dados" e fica fora das comparações.
  - **Entra** quando aparece na lista (a página mostra "sem dados ainda" até haver dados).
  - **Sai do site e da API** quando deixa a lista, inclusive quem terminar o mandato em 2027. **Não há arquivo.**
  - O histórico de cada senador em exercício **desde 2008** é mantido, porque pertence à pessoa.
  - **Aposentados, pensionistas e ex-senadores ficam fora.**
  - **Regra de agregado:** nenhum total, mediana ou ranking diz "do Senado" fora desse grupo. Toda comparação diz "entre os senadores em exercício em [data]".
- **Por quê:** concentra o projeto onde os dados são mais ricos e conferíveis, e reduz a base em 61% (de 398.624 para 153.901 registros).
- **Dados de quem sai são apagados** (decidido em 11/11/2026): no dia em que o senador deixa a lista, saem do banco de dados, dos arquivos brutos locais, do site e da API. O repositório nunca guarda dados crus (D014), então não há o que apagar no histórico do git.
- **Consequência:** a virada de fevereiro de 2027 pode retirar até 54 páginas de uma vez. Os totais e rankings são recalculados só com quem continua em exercício.
- **Status:** aceita.
- **Atualização (23/11/2026):** o histórico de cada senador desde 2008 **deixou de ser mantido**: o projeto processa só o ano atual e o anterior ([D048](#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador)). O resto da decisão (só quem está em exercício, e apagar quem sai) continua valendo.

## D027: Como conferir os dados

- **Canais oficiais do Senado, testados em 11/11/2026, sem chave:** API de despesas da cota e CSV; API de recursos por senador com `?ano=` (2023, 2025 e 2026 testados); página de transparência de cada senador e sua exportação em CSV e JSON; página mensal de benefícios; relatório de moradia do mês.
- **Limite:** todos vêm do mesmo sistema (o Sistema Cotas, da Secretaria de Finanças, Orçamento e Contabilidade). Provam a consistência e a origem, não a independência.
- **Fora do Senado:** o Internet Archive acusa uma cópia do CSV de 2024, mas não consegui listar nem ler as cópias (**a testar**). O TSE serviria só para identidade (versão 3). O Portal da Transparência do Governo Federal não mostrou sinal de cobrir a cota por senador (*não verificado*).
- **Status:** aceita; testes pendentes.

## D028: Gastos fora da cota e moradia entram, só provados

- **Gastos fora da cota:** o resumo do Senado traz seis itens "não inclusos nas cotas" (diárias de viagens oficiais, ressarcimento de passagens, material de consumo, Correios, impulsionamento em mídias sociais e passagens aéreas pela ATC 2/2023). Em 2026 somam cerca de R$ 8,5 milhões nos 81 senadores. Entram com a etiqueta de **fonte única**, e o histórico vem de `?ano=` (profundidade a confirmar).
- **Moradia:** aparece **mês a mês**, como o próprio Senado mostra. A lista de benefícios cobre só o mês de emissão e o resumo cobre o ano, por isso as duas pareciam divergir. Só entram os casos provados; os 3 pendentes ficam sem informação.
- **Status:** aceita.
- **Atualização (12/11/2026):** os gastos fora da cota entram sem selo de "fonte única"; "De onde vem este número" explica em palavras simples que o Senado informa só o total do ano de cada item e que o valor é copiado sem alteração.
- **Correção (12/11/2026):** cada item fora da cota tem uma página própria com o valor **mês a mês** no portal do Senado, sem nota fiscal nem fornecedor. O texto da tela passa a dizer, com precisão: "estes valores não fazem parte da verba (cota); o Senado os lista à parte; nos dados que usamos, não consta se o dinheiro é reembolsado ao senador ou pago direto pelo Senado".
- **Atualização (12/11/2026):** **os gastos fora da cota saem do MVP.** O bloco confundia o cidadão e não há como afirmar, com os dados do Senado, se o dinheiro é reembolso ao senador ou pagamento direto. Fica só a moradia. Os achados continuam registrados em `docs/fontes-de-dados.md`, e o assunto pode voltar se houver uma explicação precisa.
- **Atualização (18/11/2026):** a moradia ganhou verificação automática com quatro fontes, e os casos pendentes passaram de 3 para 4 (a defasagem entre a lista de novembro e a página mensal, que vai até outubro). Ver [D039](#d039-verificação-automática-da-moradia-mês-a-mês).

## D029: Identidade visual

- **Logo:** o nome **senadados** em minúsculas, em Bricolage Grotesque extra-bold, com o "o" desenhado como um anel de gráfico de rosca **todo verde (#c8f53a), sem contorno**. Em fundo claro as letras são pretas; em fundo escuro, brancas; em fundo verde, o anel é preto.
- **Favicon:** o anel verde sobre quadrado preto de cantos arredondados. Arquivos em `design/assets/`: `favicon.svg` e PNG de 32, 180 e 512 px (o `.ico` não foi gerado). A folha da marca está em `design/identidade.html`.
- **Perfil do senador:** estrutura de perguntas que abrem (opção 3), lateral fixa com os dados do senador (opção 4) e barras com percentual (opção 1). **Sem numeração** nas perguntas e **sem "Abrir todas"**.
- **Comparação com os outros senadores:** **três faixas** ("usam menos", "faixa do meio", "usam mais").
- **Fontes:** Fraunces nos títulos e Hanken Grotesk no texto. O verde-limão é o realce.
- **Cuidados:** o anel verde fica discreto em fundo claro, e a logo é um conceito: a versão final pede um designer.
- **Status:** aceita.
- **Atualização (12/11/2026):** a explicação "De onde vem este número" foi padronizada (onde o Senado publica, como chegamos, atualizado em). Os valores acima de cada barra do gráfico mensal ganharam a unidade ("29 mil") e uma legenda ("R$ 29 mil = R$ 29.000"). O escritório de apoio sai da tela do perfil, porque não se comprova.
- **Atualização (12/11/2026):** a coluna da esquerda ganhou a seção **Contato** (gabinete, telefone e e-mail, só para quem tem). A pergunta do gabinete voltou a ser só a equipe. **Quebras de linha:** em vez de exceções por elemento, há uma regra geral: dinheiro ("R$ 33.800,00"), telefone, data e palavras com hífen (como "auxílio-moradia") nunca se separam; e-mail só quebra no "@"; frases curtas ganham quebra equilibrada. Cada fato do cartão do salário fica na sua própria linha. O resumo de 2026 passa a ter **seis cartões**; o sexto está **a definir**.
- **Atualização (12/11/2026):** a coluna da esquerda voltou ao básico (cargo, mandato, salário, verba, equipe), sem a seção Contato. O **sexto cartão do resumo é "Posição entre os senadores"** ("Faixa do meio", "Usam menos" ou "Usam mais"), e o cartão da verba ficou só com o valor e a média mensal. Ordem dos cartões: salário, verba, posição, maior mês, equipe e moradia.
- **Atualização (12/11/2026):** o bloco de categorias usa **nomes curtos** derivados dos oficiais (por exemplo, "Locomoção, hospedagem e alimentação", em vez de "…combustíveis e lubrificantes"), sem tentar listar tudo o que cada categoria inclui. A tabela de equivalência está em `docs/fontes-de-dados.md`, e o nome completo fica na página do senador no Senado. A resposta fechada do bloco passou a mostrar o nome da maior categoria ("Locomoção: 33%"), e não mais "Viagens".

- **Atualização (19/11/2026):** as fontes passam a ser **hospedadas no próprio site**, e não mais carregadas do Google Fonts ([D046](#d046-site-em-nextjs-16-com-exportação-estática-fontes-hospedadas-e-testes-com-vitest)).

## D030: Destaque do maior mês no lugar do alerta "fora do padrão"

- **Contexto:** o alerta do MVP seria uma regra simples ("o mês passou de X vezes a média") ou um modelo de computador. Os dois pedem um limite escolhido por nós, e a expressão "fora do padrão" pode soar como acusação. O modelo ainda precisaria de validação (D023).
- **Decisão:** não há alerta. O gráfico mês a mês da verba **destaca o mês de maior valor** ("Maior mês: março, R$ 43 mil"). É só um fato, que qualquer pessoa confere no próprio gráfico. O modelo de anomalias (Isolation Forest) sai do MVP e fica para a versão 2, opcional.
- **Por quê:** combina com "só o comprovado" (D025) e com "sem julgamento" (D024): não há limite arbitrário nem palavra que sugira culpa. Também tira do MVP o trabalho de validar um modelo, e o endpoint de alertas.
- **Custo:** o destaque aparece todo mês, mesmo quando não há nada de estranho. Quem quiser investigar o que o pico significa faz isso por conta própria.
- **Substitui:** o alerta "fora do padrão" do escopo e a necessidade da D023 no MVP.
- **Status:** aceita.

## D031: Onde fica o gabinete (endereço) entra; telefone, e-mail e escritório de apoio ficam fora

- **Contexto:** para substituir o bloco dos gastos fora da cota, o mantenedor pediu "onde encontrar o senador", com a regra de que **só entra se todos tiverem o dado**.
- **Prova real nos 81 senadores em exercício** (API do Senado contra a página de cada senador no portal de transparência):
  - **Endereço do gabinete:** bate nos **81**.
  - **Telefone:** 66 iguais; em **15, a página traz números a mais** que a API. A API nunca lista mais de 2 números e a página lista até 4, o que sugere que a API corta em 2 (não confirmado pelo Senado).
  - **E-mail:** **sem divergência** (a diferença inicial era uma quebra de linha no fim do texto). Mas **2 suplentes não têm e-mail** em nenhuma das fontes.
  - **Escritório de apoio:** 74 de 75 batem entre duas bases, 2 senadores divergem e 3 escritórios não têm endereço.
- **Decisão:** entra **só o endereço do gabinete**, dentro do bloco "Gabinete: onde fica e quantas pessoas?". Telefone, e-mail e escritório de apoio **não aparecem para ninguém**, pela regra de tudo ou nada.
- **Pode mudar:** o **telefone** poderia entrar se a página do portal for tratada como referência (ela traz os números completos, e todos os 81 têm telefone), copiando o texto exatamente como o Senado publica. Fica registrado como alternativa, aguardando decisão do mantenedor. O **e-mail** só entraria se todos tivessem, e 2 suplentes não têm.
- **Status:** aceita.
- **Atualização (12/11/2026):** **decisão revista pelo mantenedor.** Entram o endereço do gabinete, o **telefone** (copiado da página do portal, que traz os números completos, exatamente como o Senado publica) e o **e-mail**. Para quem não tem um deles (2 suplentes sem e-mail), o campo **não aparece**: contato é uma exceção à regra de tudo ou nada. Os contatos ficam **na coluna da esquerda**, junto dos outros dados do senador. O **escritório de apoio** continua fora.
- **Atualização (12/11/2026):** os contatos **voltaram para a pergunta do gabinete** (a coluna da esquerda ficou apertada). A pergunta passou a se chamar "Gabinete: onde fica, contato e equipe", com **Onde fica**, **Como falar** e **Equipe**. **Telefones:** o Senado escreve vários números de forma abreviada ("3303-6187 / 6188 / 6183"). O site mostra **cada número completo, um por linha** ("(61) 3303-6187", "(61) 3303-6188", "(61) 3303-6183"). A regra de expansão é mecânica (o início do primeiro número vale para os seguintes) e foi conferida contra a API nos 81 senadores: reproduz exatamente os números da API em todos os casos. O número de fax que aparece em alguns casos **não é exibido**.

## D032: Organização do repositório e dos documentos

- **Contexto:** antes do primeiro código, o repositório tinha um documento de fontes com mais de 300 linhas misturando fontes, resultados de conferências e achados que saíram do escopo, e a pasta de design tinha várias páginas de exploração.
- **Decisão:** (1) `docs/fontes-de-dados.md` descreve **só as fontes** (o que existe, formato, qualidade, termos); (2) `docs/verificacoes.md` guarda **os resultados das conferências** e as pendências de prova; (3) `docs/README.md` é o índice; (4) cada pasta tem um `README.md` curto dizendo o que é; (5) a pasta `design/` guarda só o protótipo final e a folha da marca, e as páginas de exploração foram apagadas (o histórico git e as decisões D021, D029 e D030 registram o que foi escolhido); (6) dados de quem saiu do mandato e as amostras parciais foram apagados de `data/raw/`.
- **Por quê:** quem pegar o projeto precisa achar cada coisa em um lugar só, e achados fora do escopo viram ruído. Apagar o que não vale mais segue D026.
- **Alternativas descartadas:** manter as páginas de exploração "por histórico" (o git não as tem ainda, mas as decisões já registram o raciocínio); um único documento grande (difícil de manter coerente).
- **Status:** aceita.

## D033: Coleta local que só grava quem está em exercício

- **Contexto:** a ordem de construção começa pelo pipeline de despesas. A API de despesas devolve também ex-senadores (em 2024, 16 dos 88 senadores da despesa não estão na lista de quem está em exercício), e a D026 manda que os dados de quem saiu não fiquem guardados. Os arquivos baixados à mão em 11/11 trazem esses ex-senadores, apesar do que a D032 registrou.
- **Decisão (18/11/2026):**
  - O código fica em `pipeline/`, em Python com uv, httpx, pytest e ruff. Pandas e Pandera entram na etapa de validação e limpeza, não antes.
  - A coleta baixa a lista dos senadores em exercício e as despesas de cada ano pela API, e **grava só as despesas de quem está na lista**. O que a API devolve é gravado sem alteração.
  - A coleta **não sobrescreve** arquivo existente, a menos que se peça, e **para com erro** se o Senado devolver um formato inesperado ou uma lista vazia (falhar fechado).
  - Por enquanto os dados ficam **só em arquivos locais** (`data/raw/`). O banco no Neon fica para a etapa do banco; o formato local dos dados limpos (Parquet ou SQLite) será escolhido na etapa de limpeza.
- **Por quê:** o arquivo local não exige conta nem rede para testar, e é o Plano B já previsto na D002. Filtrar ao gravar cumpre a D026 sem depender de apagar depois. Não sobrescrever evita perder dados sem querer.
- **Descartado:** começar já no Neon (obriga a criar conta e conexão antes de existir algo funcionando).
- **Consequência:** a coleta traz mais linhas do que os arquivos antigos filtrados (2026: 16.033 contra 15.636), porque o Senado continuou publicando entre 11/11 e 18/11. Essa diferença vem da atualização da fonte, e não foi investigada linha a linha.
- **Executado em 18/11/2026:** os 19 arquivos de despesas foram baixados de novo e substituíram os antigos: 154.298 registros, nenhum de fora da lista, 80 senadores com despesa (a documentação de 11/11 falava em 79 de 81; o 80º é Leany Lemos, que ganhou a primeira despesa depois de 11/11; só Jorge Kajuru segue sem despesa).
- **Status:** aceita.

## D034: Limpeza com validação, em SQLite local, sem nome nem documento de pessoa física

- **Contexto:** a coleta (D033) grava o que o Senado devolve. Antes de qualquer número aparecer, os dados precisam ser validados e limpos, com cada regra provada por teste. Medi os dados reais de 18/11/2026 (154.298 despesas) para escrever as regras.
- **Decisão (18/11/2026):**
  - **Validação com Pandera em dois momentos:** o que o Senado entrega (colunas exatas, tipos, `id` único, mês de 1 a 12, valor com no máximo 2 casas) e o que o pipeline produz. Coluna nova ou faltando, `id` repetido ou valor impossível **quebram a execução e nada é gravado**.
  - **Categoria vazia vira "Sem categoria".** Categoria nova do Senado passa, com o nome oficial.
  - **Valor em centavos inteiros**, para as somas baterem no centavo sem erro de arredondamento.
  - **Fornecedor classificado pelo documento:** `empresa` (CNPJ no formato certo e com dígitos verificadores válidos), `pessoa_fisica` (CPF mascarado ou com 11 dígitos), `sem_documento` (o Senado não informou; só 2008 e 2009) e `outro` (qualquer outro formato, mantido como veio).
  - **Pessoa física não leva nome nem documento** para os dados limpos (D008, aplicada já na limpeza). Os brutos seguem em `data/raw/`, fora do git.
  - **Documento fora do padrão não é corrigido.** Testei a hipótese de CNPJ que perdeu zeros à esquerda: completando com zeros, só 2 dos 54 casos de 12 ou 13 dígitos têm dígitos verificadores válidos, então a hipótese não se sustenta e nada é inferido (D025). Ficam como `outro`.
  - **Data fora do intervalo de 1º/1/2008 até o dia da coleta (ou malformada) some, e a linha é marcada** (`data_fora_do_esperado`), sem tentar adivinhar a data certa. A linha **continua na soma**. Em 18/11/2026 são 34 linhas: anos como 0023, 0201, 0204 e 1201, datas antigas como 1965 a 2006 e 4 datas futuras.
  - **Descrição, número do documento e nome do senador da despesa não seguem** para os dados limpos: o MVP não os usa (o nome vem da lista de senadores), e o bruto continua disponível pelo `id`.
  - **Formato local: SQLite** (`data/limpo/senadados.sqlite`, fora do git), gravado de forma atômica: se qualquer validação falhar, o banco anterior fica intacto.
- **Por quê:** SQLite já vem com o Python (sem dependência nova), aceita as consultas SQL das verificações e tem o mesmo desenho que as tabelas do Neon depois. Parquet exigiria uma biblioteca grande sem ganho para 154 mil linhas. Tirar nome e documento de pessoa física na origem é mais seguro do que confiar em esconder depois.
- **Descartado:** Parquet (dependência a mais); corrigir documentos por suposição (viola D025); apagar as linhas de data ruim (a despesa existe e entra no total, só a data não se sustenta).
- **Resultado em 18/11/2026:** 154.298 despesas limpas (nenhuma perdida), soma de R$ 213.008.569,15 igual à dos arquivos brutos, 276 sem categoria, 34 datas fora do esperado, 56 documentos fora do padrão. A cota de 2026 conferida contra o resumo do mesmo dia deu **74 idênticos, 7 explicados e 0 sem explicação**; essa conferência foi feita por um roteiro avulso, e **a verificação automática ainda não existe**. A conferência feita pelo código está em [D035](#d035-verificação-automática-da-cota-por-categoria-na-mesma-foto-dos-dados): 73 idênticos e 7 explicados, entre os 80 senadores com valores.
- **Trava de coerência da coleta (18/11/2026):** a limpeza recusa dados em que as despesas de algum ano são mais antigas que a lista de senadores usada para filtrá-las, ou sem data de coleta. Sem isso, atualizar só um ano deixaria um senador novo sem o histórico dos outros anos, e ninguém perceberia. A correção é recoletar todos os anos.
- **Status:** aceita.

## D035: Verificação automática da cota por categoria, na mesma foto dos dados

- **Contexto:** a D025 manda provar cada número comparando bases do Senado. A cota de 2026 tinha sido conferida por um roteiro avulso, e a lição de 18/11/2026 mostrou que bases de dias diferentes geram divergências falsas.
- **Decisão (18/11/2026):**
  - A verificação virou código (`pipeline/`, `python -m senadados_pipeline.verificacao`). Para cada senador e ano, compara as despesas **por categoria** com o resumo oficial (`recursos-utilizados`), e não só o total. As 7 categorias do resumo têm uma tabela fixa de equivalência com os nomes oficiais das despesas.
  - Resultados: **`identico`** (todas as categorias batem no centavo), **`explicado`** (batem, e só faltam as linhas sem categoria, que o resumo não conta) e **`sem_explicacao`** (qualquer outra diferença, categoria desconhecida ou resumo que não soma o próprio total). Esta última **oculta o número** (falhar fechado) e registra o motivo.
  - **Mesma foto dos dados:** a coleta registra a data e a hora de cada download em `data/raw/coleta.json`. A verificação **se recusa a rodar** se a lista de senadores, as despesas do ano ou o banco limpo não forem de hoje. O resumo é baixado no momento da verificação.
  - O resultado fica no banco limpo (`verificacao_cota`, por senador e ano, e `verificacoes`, o resumo por ano), para a página "Verificações" ler depois.
  - Pares senador-ano sem valor nos dois lados não entram na contagem.
- **Resultado em 18/11/2026 (2008 a 2026, 1.539 consultas de resumo, cerca de 3 minutos):**
  - **2010 a 2026: nenhuma divergência sem explicação.** Em 2026, 73 idênticos e 7 explicados.
  - **2008 e 2009: 5 senadores sem explicação em cada ano.** O resumo de 2008 vem vazio, e o de 2009 é menor que as despesas. **O motivo não foi confirmado**; só o Senado pode explicar. Pela D025, a cota desses anos **não aparece** e o histórico da cota começa em 2010.
- **Por quê:** comparar por categoria é mais forte do que comparar o total (categorias trocadas com o mesmo total seriam percebidas), e o site mostra o valor por categoria. A trava de "mesma foto" impede a falha que cometi no começo da investigação.
- **Limites:** prova consistência entre bases do mesmo sistema do Senado, não é auditoria (D027). Só cobre a cota; gabinete, salário, moradia e contato ainda não têm verificação automática. O resumo de 2008 e 2009 pode ser limitado do lado do Senado, e isso **não foi confirmado**.
- **Status:** aceita.
- **Atualização (23/11/2026):** os resultados de 2010 a 2024 e o caso de 2008 e 2009 são **registro histórico** de 18/11/2026; a verificação roda hoje só para o ano atual e o anterior ([D048](#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador)).

## D036: Verificação automática da equipe do gabinete, por vínculo

- **Contexto:** a D015 manda mostrar só o **número** de pessoas do gabinete, do resumo oficial, e a D025 exige prova antes de exibir. Em 11/11 o resumo somava 1.723 pessoas e a lista de servidores 1.722, e a diferença de uma pessoa não estava explicada.
- **Decisão (18/11/2026):**
  - A verificação virou código (`python -m senadados_pipeline.equipe`). Para cada senador, compara o total e a quebra por vínculo (comissionado, efetivo, requisitado) do resumo oficial com a lista de servidores ativos lotados no gabinete, **sem contar o próprio senador** (vínculo "parlamentar", que consta na lista).
  - **Nomes de servidores nunca são guardados** (D007): a lista é contada por gabinete e vínculo na hora do download, e só as contagens vão para o disco.
  - Resultados: `identico` ou `sem_explicacao`. Não existe "explicado", porque não há diferença conhecida entre as duas fontes.
  - **A ligação senador-gabinete é pelo nome**, porque a lista de servidores não traz o código do parlamentar. Regra: nome igual (sem acento e sem caixa) e, só quando houver uma única possibilidade, um nome inteiro dentro do outro em palavras (`Nelsinho Trad` e `Nelsinho Trad Filho`). Quem não se liga fica sem explicação. A contagem de pessoas é a segunda barreira contra uma ligação errada.
  - Mesma regra da cota: só roda com a lista de senadores e o banco limpo do mesmo dia, e o resultado vai para o banco limpo (`verificacao_equipe`, e uma linha `equipe` em `verificacoes`).
- **Resultado em 18/11/2026:** 81 gabinetes, **80 idênticos** (total e cada vínculo) e **1 sem explicação**: no gabinete de Camilo Santana o resumo traz 1 efetivo que a lista de ativos não tem (28 contra 27 pessoas). Testei e descartei duas hipóteses: servidor fora da lista de ativos (as listas completa, de efetivos e de exercício provisório não o trazem) e servidor cedido de outro órgão (os 4 cedidos do gabinete já estão entre os comissionados). Só o Senado pode explicar.
- **Consequência (substituída pela [D037](decisoes.md#d037-exibição-por-tipo-de-dado-e-freio-de-segurança)):** pela regra de tudo ou nada (D025), a equipe
- **Dados locais:** `data/raw/folha/servidores_ativos.json` (de 11/11) trazia nomes de servidores. O pipeline novo não o usava, e ele foi **apagado em 18/11/2026**, a pedido do mantenedor, junto com as cópias temporárias que continham nomes.
- **Limites:** prova consistência entre bases do mesmo sistema do Senado, não é auditoria (D027). A ligação por nome é frágil se um nome mudar, e nesse caso o gabinete cai em "sem explicação" em vez de receber um número errado.
- **Status:** aceita.

## D037: Exibição por tipo de dado e freio de segurança

- **Contexto:** a regra "tudo ou nada" (D025) foi escrita para a comparação entre senadores: se um senador faltasse num ranking, a posição de todos ficaria distorcida. Ao verificar a equipe do gabinete (D036), 80 de 81 gabinetes bateram nas duas bases do Senado e 1 não, e a regra escondia a equipe dos 81 por causa de 1.
- **Decisão (18/11/2026):** os dados passam a ter **duas classes**.
  1. **Dado que compara senadores** (ranking, posição entre os senadores, mediana): segue **tudo ou nada**. Só aparece se todos em exercício o tiverem e baterem.
  2. **Dado descritivo de cada senador** (contato, equipe do gabinete): aparece **para quem foi provado**, e fica oculto para quem não foi, sem aviso no perfil. O gabinete oculto é listado na página "Verificações".
  - **Freio de segurança:** se mais de **5%** dos senadores falharem num dado descritivo, ele some para todos. Uma falha isolada é uma discrepância da fonte; muitas juntas indicam problema na nossa ligação ou mudança na API do Senado. O 5% é um julgamento, e não um número pesquisado. Com 81 senadores, até 4 falhas ainda permitem exibir.
  - **Ao criar um dado novo, classificá-lo** numa das duas classes e registrar qual.
- **Por quê:** a equipe é uma contagem descritiva e não entra em ranking, então esconder 80 números provados por causa de 1 só empobrece o site sem proteger ninguém. O que fere a credibilidade é mostrar um número que não se prova, e isso continua proibido. Mostrar o que bate e listar o que foi escondido passa mais rigor do que esconder tudo. O contato (D031) já abria esse precedente.
- **Resultado em 18/11/2026:** a equipe aparece para os 80 gabinetes idênticos e fica oculta no de Camilo Santana (1 efetivo a mais no resumo, sem explicação). A verificação diária mostra o gabinete de volta sozinha quando o Senado explicar ou corrigir.
- **Implementação:** a coluna `exibir` da tabela `verificacao_equipe` no banco limpo. Quem ler o banco (a API e o site) usa `exibir`, e **trata a ausência da tabela como "não verificado"**.
- **Altera:** a consequência da D036 e o texto da regra de tudo ou nada na D025 (que continua valendo para dados que comparam).
- **Status:** aceita.
- **Atualização (19/11/2026):** "o gabinete oculto é listado na página Verificações" passa a valer **em contagem**: a página mostra quantos ficaram ocultos em cada verificação, com um motivo de uma lista fechada. **Nomes de senadores só aparecem na seção de divergências**, onde há prova em imagem ([D038](#d038-documento-público-de-divergências-com-prova-em-imagem)), o que concilia esta decisão com o `escopo.md` §4.5. Ver [D042](#d042-banco-no-neon-só-dados-agregados-dois-esquemas-e-carga-repetível).

## D038: Documento público de divergências, com prova em imagem

- **Contexto:** a verificação (D035 e D036) achou diferenças entre publicações do próprio Senado. A primeira ideia era enviar um pedido de esclarecimento ao Senado. O mantenedor preferiu **mostrar as diferenças publicamente**, sem prometer buscar respostas.
- **Decisão (18/11/2026):** o projeto passa a ter o documento `docs/divergencias-nos-dados-do-senado.md`, que vira a seção "Onde os dados do Senado não batem entre si" do site. Regras:
  - **Só entra o que tem print.** Cada caso mostra uma captura da tela ou do relatório do próprio Senado (recortada, **sem a foto do senador**), ou, para arquivos de dados, uma tabela feita pelo Senadados com linhas copiadas sem alteração e **etiquetada como montagem do Senadados**. Contagens sobre todos os senadores são declaradas como feitas pelo Senadados.
  - **Texto neutro e fácil de entender:** não diz qual número está certo, não diz o motivo, não acusa ninguém e **não diz que o projeto vai atrás de respostas**.
  - **Cada caso traz o passo a passo para conferir** e a data e hora da captura.
  - **Os nomes dos senadores aparecem**, porque a diferença está na publicação por senador e o print mostra o nome. Isso altera a linha do `escopo.md` §4.5 que dizia "sem nomes" para a página de verificações como um todo; a regra vale para a página agregada, e não para esta seção.
  - **Dados de servidores:** nenhuma imagem mostra nome de servidor. O arquivo local `servidores_ativos.json`, que tinha nomes, foi apagado.
- **Casos publicados em 18/11/2026:** (1) tela de um gabinete com 27 pessoas contra 28 na exportação da mesma página; (2) o rótulo "Gabinete" com totais diferentes (a tela inclui estagiários e terceirizados, a exportação não); (3) cota de 2008 e 2009 de cinco senadores, em que a tela mostra menos que o arquivo de despesas; (4) linhas sem categoria que a tela não conta; (5) notas com data de ano 0204 e 0202.
- **Achados novos que a captura trouxe:**
  - A **tela do portal e a exportação da mesma página divergem** no bloco de pessoal de um gabinete. Isso reforça que o resumo da API (D015) e a tela não são a mesma coisa, e a tela está de acordo com a lista de servidores.
  - O **número "equipe" depende da definição.** O Senadados usa o do resumo (comissionados, efetivos e requisitados) e **deve dizer o que ele inclui**, para o cidadão que comparar com a tela (que soma estagiários e terceirizados) não achar um dos dois errado.
- **Cuidados:** os prints são fotos de 18/11/2026 e podem deixar de refletir a tela se o Senado atualizar os dados (de fato, a divergência do item 1 foi vista também na API às 16h46, e pode ser corrigida a qualquer momento). Os recortes não mostram foto de senador. A responsabilidade por manter o documento correto é do projeto: se o Senado corrigir um caso, ele deve ser atualizado ou retirado.
- **Status:** aceita.
- **Atualização (23/11/2026):** as 11 imagens foram **refeitas** com a captura de 23/11/2026 (telas e exportações do Senado fotografadas num Chrome sem janela, e as tabelas "montagem do Senadados" refeitas dos arquivos oficiais baixados no dia). Os mesmos cinco casos continuam valendo; mudaram só números de Hamilton Mourão (o total na tela passou a R$ 448.186,05 e o do arquivo, a R$ 483.186,05, com a mesma diferença de R$ 35.000,00) e as horas. As **contagens sobre todos os gabinetes** (80 de 81 e 79 de 81) são de 18/11/2026 e **não foram refeitas**; o texto diz isso. A página "Verificações" do site mostra o dia da captura e avisa que, se o Senado atualizar os dados, o que está lá pode deixar de valer. Os prints não se atualizam sozinhos: quando o Senado mudar um caso, as imagens precisam ser refeitas à mão.

## D039: Verificação automática da moradia, mês a mês

- **Contexto:** a D028 manda mostrar o uso de auxílio-moradia e de imóvel funcional **mês a mês**, só para quem foi provado. Em 12/11 havia 3 casos pendentes, em que o resumo anual e a lista do mês pareciam divergir.
- **Decisão (18/11/2026):** a verificação virou código (`python -m senadados_pipeline.moradia`). Para cada senador compara **quatro fontes** do Senado, baixadas na hora: (1) o resumo anual da API, (2) o resumo da tela do portal ("Utilizou (em 10 meses)", "Não utilizou" ou "Renúncia ao benefício"), (3) a **página mensal** do portal, a única com o uso mês a mês, e (4) a **lista do mês**, da API, que diz quem usa agora.
  - **`identico`:** as quatro concordam (sim ou não, número de meses e último mês).
  - **`explicado`:** a tela diz "renúncia ao benefício" onde a API diz "não utilizou". Quem renuncia não usa.
  - **`pendente`:** as três primeiras concordam, mas a lista de hoje difere do **último mês** da página mensal. São períodos diferentes, e isso **não está provado** como causa. O benefício daquele senador some até a página mensal alcançar o mês da lista.
  - **`sem_explicacao`:** qualquer outra diferença, página fora do formato ou falha de coleta do senador.
  - **Exibição (D037):** moradia é dado descritivo, aparece para `identico` e `explicado`. **Só `sem_explicacao` conta para o freio de segurança de 5%**: o `pendente` tem causa provável conhecida (defasagem entre períodos) e esconde só o próprio senador. Sem isso, a virada normal de mês poderia derrubar a moradia de todos.
  - O número funcional do senador, necessário para abrir a página mensal, é lido do link do portal e **não é guardado**.
  - O resultado vai para `verificacao_moradia` e o uso mês a mês para `moradia_meses` (usar só quem tem `exibir = 1`).
- **Resultado em 18/11/2026:** 81 senadores, **76 idênticos, 1 explicado, 4 pendentes e 0 sem explicação**, e a moradia aparece para **77**. Os 4 pendentes usaram auxílio-moradia até outubro e a lista de hoje diz que não usam. Em 12/11 eram 3 pendentes. Foram 12 senadores com auxílio-moradia e 63 com imóvel funcional, e 6 sem link para a página mensal (não usaram nenhum dos dois).
- **Por quê:** o uso mês a mês só existe na página mensal do portal, então ele precisa ser confrontado com as outras três fontes antes de aparecer. Separar `pendente` de `sem_explicacao` evita tratar uma defasagem esperada como falha do dado.
- **Limites:** (1) a página mensal é lida do **HTML do portal**, que não é uma API e pode mudar; se mudar, o senador cai em `sem_explicacao` e não recebe número errado. (2) O pendente se resolve sozinho quando a página mensal incluir novembro (a verificação diária reconfere). (3) Prova consistência entre bases do Senado, não é auditoria (D027). (4) A verificação não diz onde o imóvel fica nem afirma nada sobre o direito ao benefício (D024).
- **Status:** aceita.

## D040: Verificação automática do contato do gabinete

- **Contexto:** a D031 decidiu mostrar o endereço do gabinete, os telefones (copiados da página do portal, que traz os números completos) e o e-mail, para quem os tem. As conferências de 12/11 eram manuais.
- **Decisão (18/11/2026):** a verificação virou código (`python -m senadados_pipeline.contato`). Compara, **campo a campo**, a API de dados abertos (a lista de senadores que a coleta gravou) com a seção "Dados pessoais" da página de cada senador, baixada na hora.
  - **Endereço:** igual ignorando caixa alta e espaços repetidos. O valor mostrado é o da página.
  - **Telefones:** a página abrevia vários números ("(61) 3303-6187 / 6188 / 6183"). A regra é mecânica: o início do primeiro número vale para os seguintes que trouxerem só os 4 últimos dígitos. `identico` se os conjuntos de números são iguais; **`explicado`** se a página traz números a mais e **todos os da API estão nela**; `sem_explicacao` se a API tem número que a página não tem ou o formato é inesperado. O fax não é usado.
  - **E-mail:** igual ignorando caixa. "-" e vazio são "sem e-mail", e se **nenhuma** das fontes traz e-mail o campo é `identico` e simplesmente não aparece (D025, exceção do contato).
  - **Exibição (D037):** contato é dado descritivo. **Cada campo** aparece para quem foi provado e tem o **próprio freio de segurança de 5%**. Só o valor provado vai para a tabela `contato`; o campo não provado fica **vazio** (falhar fechado). O resultado de cada campo fica em `verificacao_contato`.
  - **Só três campos são lidos da página.** Nome civil, data de nascimento e o restante não são lidos nem guardados.
- **Resultado em 18/11/2026:** endereço **81 idênticos**; telefones **66 idênticos e 15 explicados**; e-mail **81 idênticos**, dos quais 2 sem e-mail nas duas fontes. Nenhum sem explicação. O contato aparece para 81 (endereço e telefones) e 79 (e-mail). É o mesmo resultado da conferência manual de 12/11.
- **Falhar fechado, visto na prática:** a primeira execução usou o endereço da página sem o parâmetro do ano, o portal respondeu com um redirecionamento, e os 81 senadores caíram em `sem_explicacao`, sem nenhum contato exibido. Depois da correção, passou. A regra fez o que devia: sem dado provado, nada aparece.
- **Por quê:** o contato do gabinete é o dado mais útil para o cidadão e o mais simples de provar. Verificar campo a campo evita que um telefone divergente esconda o endereço, e o freio por campo evita que um problema numa só fonte derrube os outros.
- **Limites:** (1) a página do portal é HTML, não uma API, e pode mudar; se mudar, o campo cai em `sem_explicacao`. (2) O motivo de a API listar menos telefones **não foi confirmado**. (3) Prova consistência entre bases do Senado, não é auditoria (D027). (4) O escritório de apoio continua fora (D031).
- **Status:** aceita.

## D041: Verificação automática do salário pela identidade do senador

- **Contexto:** a D016 liga a folha de pagamento ao senador pelo **nome completo da lista legislativa**, e a D025 só aceita o que se comprova. A folha **não traz o código do parlamentar** e é a **única fonte do valor**. Em 12/11, 3 suplentes não tinham correspondência e um titular tinha valor diferente.
- **Decisão (18/11/2026):** a verificação virou código (`python -m senadados_pipeline.salario`) e **muda a chave de ligação**. Em vez do nome da lista legislativa, usa o **nome civil da página de identificação do próprio senador**, alcançada pelo link "Subsídios do Senador" da página dele no portal (ou seja, pelo código do senador). Cada senador passa por **cinco provas**:
  1. **Identidade:** a página de identificação diz vínculo "parlamentar", situação "ativo" e a mesma UF que o senador tem.
  2. **Uma única matrícula** com esse nome na folha do mês. Nenhuma ou mais de uma impede a ligação, e **as linhas nem são guardadas** quando há mais de uma (podem ser de outra pessoa).
  3. **Uma única folha normal** no mês. Folhas suplementares só são aceitas se estiverem **zeradas**.
  4. **Conta interna:** a remuneração líquida é a soma dos 11 componentes. Conferido em **todas as 10.480 linhas normais** de outubro de 2026.
  5. **Remuneração básica e líquida positivas.**
- **Exibição (D037):** dado descritivo, aparece para quem passou, com o freio de segurança de 5%. O que se mostra é a **remuneração básica e a líquida do mês**. ~~O site deve dizer que a básica não é o total antes dos descontos.~~ **Corrigido em 20/11/2026 ([D046](#d046-site-em-nextjs-16-com-exportação-estática-fontes-hospedadas-e-testes-com-vitest)):** olhando a folha de outubro, a básica é o valor antes dos descontos (previdência e imposto de renda) para quase todos, e só em poucos casos a folha traz outros valores (auxílios, gratificação natalina). O site diz isso.
- **Dados de servidores (D007):** a folha do mês é baixada na hora, **só as linhas dos senadores são guardadas**, e os nomes dos demais servidores são descartados na hora. O arquivo local `data/raw/folha/remuneracao_2026_09.json`, de 11/11, tinha os nomes e a remuneração de todos os servidores. O pipeline novo não o usava, e ele foi **apagado em 18/11/2026**, a pedido do mantenedor, junto com a cópia temporária da folha de outubro.
- **A consulta de remuneração do portal de servidores exige reCAPTCHA.** O pipeline **não tenta contorná-lo** e lê só a identificação, que o portal mostra sem desafio. A consequência é que o valor continua com **fonte única**, provada por consistência interna e identidade, e não por uma segunda fonte.
- **Resultado em 18/11/2026 (folha de outubro, a de novembro ainda não existe):** **79 de 81 passam**, todos com remuneração básica de **R$ 46.366,19**, e o salário aparece para 79. **2 sem explicação**, ambos suplentes que assumiram em outubro: um tem **duas matrículas com o mesmo nome** (R$ 6.686,29 e R$ 38.887,77), e o outro tem **folha suplementar com valores** (R$ 46.366,19 em vantagens indenizatórias, além da normal de R$ 47.911,73). O suplente que antes não tinha correspondência agora é ligado.
- **Por quê:** ligar pela identidade que o próprio portal atribui ao código do senador é mais forte do que ligar por um nome vindo de outra lista, e resolve o caso do nome escrito de dois jeitos. As provas internas e a recusa de ligação ambígua substituem a segunda fonte que o reCAPTCHA impede.
- **Limites:** (1) fonte única do valor. (2) A identificação vem do HTML do portal, que pode mudar; se mudar, o senador cai em `sem_explicacao`. (3) Suplentes que assumem no meio do mês têm folhas parciais e ficam ocultos até a folha completa. (4) Prova consistência e identidade, não é auditoria (D027). (5) O site não diz se o valor está dentro ou fora de qualquer regra (D024).
- **Altera:** a ligação da D016 (nome completo da lista legislativa).
- **Status:** aceita.

## D042: Banco no Neon, só dados agregados, dois esquemas e carga repetível

- **Contexto:** a etapa 3 da ordem de construção é o banco na nuvem, de onde a API (D004) vai ler. O banco local (SQLite, D034) tem 154.298 despesas linha a linha e 34 MB. Os endpoints do escopo (§7) pedem totais por mês e por categoria, maiores fornecedores por ano, ranking, contato, equipe, moradia, salário e o relatório de verificações. **Nenhum precisa da nota fiscal linha a linha.**
- **Decidido pelo mantenedor em 19/11/2026:**
  1. **Só dados agregados vão para o Neon.** Em 18/11/2026, **antes de aplicar a regra de exibição**, são 25.902 linhas de despesa por senador, ano, mês e categoria (25.526 de 2010 em diante e 376 de 2008 e 2009, anos em que a cota não aparece, D035) e 30.992 de fornecedores (empresas) por senador e ano, de 2009 em diante (30.594 de 2010 em diante e 398 de 2009). O que for para o `publico` será menor que isso, porque só segue o que passou nas verificações. Pessoas físicas continuam agrupadas e sem nome (D008). As 154.298 despesas linha a linha **ficam só no SQLite local**.
  2. **A carga será testada numa branch do Neon com validade**, e não num Postgres local (não há Postgres instalado na máquina de desenvolvimento). A branch herda as senhas do projeto, então leva `expires_at` de 1 dia e é apagada ao terminar.
  3. **Documentar antes de criar:** o projeto no Neon só foi criado depois da revisão deste desenho pelo mantenedor (cumprido: criado em 19/11/2026, depois da aprovação abaixo).
  4. **Esquemas e papéis aprovados como propostos** (detalhes abaixo): `publico` e `interno`, e os papéis dono, `sd_carga` e `sd_leitura`.
  5. **A página "Verificações" mostra contagens, e nomes só onde há prova em imagem.** Para cada verificação, quantos dados passaram e quantos ficaram ocultos, com um motivo de uma lista fechada. **Nomes de senadores só na seção de divergências** (D038). Isso concilia a D037 ("o gabinete oculto é listado") com o `escopo.md` §4.5 ("agregada e sem nomes"). Por quê: esconder um nome agora pode ser desfeito e publicar não (a mesma lógica da D008), e uma lista de senadores sem dado provado pode ser lida como acusação, contra a D010. Custo: quem quiser saber por que um senador específico está sem um dado só encontra a explicação geral; nomes podem ser acrescentados depois, se for decidido.
  6. **Região e API.** O banco fica em `aws-us-east-2` (Ohio). A API será publicada na Render, também em Ohio, depois do site ([D044](#d044-site-antes-da-api-com-dados-em-arquivos-json-gerados-do-esquema-público); antes, na etapa 5, hoje na 8) ([D004](#d004-fastapi-no-render-e-o-site-não-depende-dela)).
- **Desenho aceito pelo mantenedor em 19/11/2026** (implementado e aplicado: ver a D043):
  - **Dois esquemas.** `publico` guarda só o que passou nas verificações (`exibir = 1`); a API e o site leem só ele, e a ausência de um dado significa "não verificado". `interno` guarda o detalhe das verificações (`resultado` e `detalhe`); o resumo da página "Verificações" sai de tabelas do `publico` calculadas na carga ([D043](#d043-migrações-em-sql-puro-driver-psycopg-e-carga-que-ensaia-antes-de-gravar); a redação original previa uma view). Os dados descritivos pequenos (contato, equipe, moradia mês a mês e salário) seguem para o `publico` só para quem tem `exibir = 1`. Conferi **todos** os valores de `detalhe` de 18/11/2026 (9 padrões de texto, nas cinco tabelas de verificação): trazem categorias, valores e contagens, **sem nome de senador nem de outra pessoa**. O texto de `detalhe` é gerado pelo código; se algum dia ele passar a incluir nomes, esta conferência precisa ser refeita antes de a carga o levar para a nuvem.
  - **Página "Verificações"** (decidido no item 5): a view pública traz contagens por verificação e ano, com motivo de lista fechada e sem nomes. **A conferir na implementação:** a tabela `verificacoes` não guarda os `pendente` da moradia (só `verificacao_moradia` os tem), então a contagem de pendentes precisa ser calculada na carga.
  - **Três papéis de banco**, de menor privilégio: o dono (só migrações), `sd_carga` (escreve; usado pela rotina diária) e `sd_leitura` (`SELECT` só no `publico`; usado pela API). Cada papel recebe só o que a sua tarefa precisa, e tabelas novas não herdam permissão.
  - **Carga repetível numa transação:** apaga e recarrega as tabelas, então quem saiu da lista some sozinho (D026). Recusa carregar se as verificações não forem da mesma foto dos dados (D035).
  - **Projeto** `senadados`, **criado na Neon em 19/11/2026** na organização que já existia: plano gratuito, PostgreSQL 18, região `aws-us-east-2`, branch `production`. Esquemas, papéis e dados aplicados em 19/11/2026 (ver a D043). A conexão (senha) fica só em variável de ambiente, nunca no repositório (`.env` está no `.gitignore`).
  - **Dados que comparam senadores** (posição, ranking): a regra de tudo ou nada (D037) vale na carga; onde calcular (no pipeline ou numa view) **fica para a implementação**.
- **Limites do plano gratuito**, conferidos em 19/11/2026 na página oficial de planos da Neon (atualizada em 12/11/2026): 1 GB de armazenamento por projeto, 100 horas de computação por mês por projeto, 10 branches por projeto, até 100 projetos por conta, o banco "dorme" após 5 minutos parado, e 6 horas de histórico para recuperação. O projeto foi criado em 19/11/2026 pelo plano gratuito sem que a operação pedisse cartão; **se há cartão cadastrado na conta, não conferi**. Os ~57 mil registros agregados devem caber com folga, **mas o tamanho no PostgreSQL não foi medido**.
- **Por quê:** levar só o que as telas usam reduz o tamanho, a carga e a superfície de dados pessoais, e mantém o que o cidadão vê reproduzível a partir do pipeline. Separar `publico` e `interno` faz "só o comprovado" (D025) valer também na leitura: quem consulta o banco não alcança um dado não provado.
- **Descartado:** levar as despesas linha a linha (ocuparia mais, sem tela que as use; **pode voltar** se um dia a D008 mudar); testar num Postgres local (exigiria instalar algo e a versão poderia diferir da Neon); criar o projeto antes de revisar o desenho.
- **Custo:** com só agregados não dá para mostrar a nota individual sem recarregar o banco com outra carga.
- **Status:** aceita (19/11/2026). Aplicada na produção no mesmo dia, depois do ensaio numa branch; a atualização diária automática ainda não existe.
- **Atualização (19/11/2026):** a migração 003 acrescenta `publico.moradia_verificada` (quem teve a moradia provada, mesmo sem mês de uso). `moradia_meses` só tem linha de quem usou algum benefício, e sem a nova tabela "não usou" e "não provado" não se distinguiam. Foi descoberto ao escrever o exportador dos dados do site ([D044](#d044-site-antes-da-api-com-dados-em-arquivos-json-gerados-do-esquema-público)). Ensaiada numa branch e **aplicada na produção em 19/11/2026**, com o OK do mantenedor: `sd_leitura` lê as 77 linhas e é negado em escrever, e `sd_carga` é negado em `UPDATE`; nenhum mês de moradia ficou sem prova; o exportador rodou contra a produção e gerou os mesmos 84 arquivos do ensaio, exceto a hora da carga.

## D043: Migrações em SQL puro, driver psycopg e carga que ensaia antes de gravar

- **Contexto:** a D042 aprovou os esquemas, os papéis e a carga repetível. Faltava decidir como aplicar as migrações e como carregar os dados.
- **Decisão (19/11/2026):**
  - **Migrações em arquivos SQL** numerados, em `pipeline/migracoes/`, aplicados em ordem por `python -m senadados_pipeline.migrar`, cada execução numa só transação. **Por padrão é um ensaio** (tudo é desfeito no fim); só `--apply` grava. As versões aplicadas ficam em `interno.migracoes`. Usa o dono do banco (`DATABASE_URL`). Migração já aplicada nunca é editada.
  - **Driver: psycopg 3** (`psycopg[binary]`, instalado a 3.3.9), a única dependência nova. A conexão vem sempre de variável de ambiente, e os registros do comando mostram só o endereço do servidor, **nunca a senha**.
  - **A carga** (`python -m senadados_pipeline.carga`) lê o SQLite limpo **só para leitura**, escolhe o que passou nas verificações, agrega, e numa transação apaga (`TRUNCATE`) e regrava as 17 tabelas (18 desde a migração 003, que a D042 registra), conferindo a contagem de cada uma antes de confirmar. Também é ensaio por padrão. Usa o papel `sd_carga` (`DATABASE_URL_CARGA`). **Recusa carregar** se faltar alguma das 7 verificações ou se alguma não for do dia da coleta (D035).
  - **O resumo da página "Verificações" é gravado como tabelas calculadas na carga** (`verificacoes_resumo` e `verificacoes_motivos`), **e não como views**. Isto altera a redação da D042 ("uma view do `publico`"). Por quê: a regra fica em Python, com teste, e os motivos saem de uma **lista fechada** no código (`MOTIVOS`), nunca do texto livre do banco, que fica no esquema `interno`.
  - **Fornecedores seguem a regra de exibição da cota do senador-ano**, porque saem das mesmas despesas (D025). Hoje isso esconde 2009, pois os 5 senadores com despesa naquele ano não passam na cota. O `escopo.md` §4.2 dizia "a partir de 2009"; vale a prova.
  - **Nome do fornecedor:** a grafia mais frequente do CNPJ, e no empate a primeira em ordem alfabética. Em 18/11/2026, 2.373 CNPJs aparecem com mais de uma grafia.
  - **Os papéis** são criados por `python -m senadados_pipeline.papeis`, **antes das migrações**: cria `sd_carga` e `sd_leitura` por SQL (o que os deixa fora do grupo de administração da Neon), gera as senhas, grava as URLs no `.env` **sem imprimir** e não troca a senha de um papel que já existe. A `002` só concede permissões e se recusa a rodar sem os papéis.
- **Resultado da seleção sobre o banco local de 18/11/2026** (nada foi enviado): 81 senadores, 25.526 linhas de despesa mensal (2010 em diante), 30.594 de fornecedor (empresas), 279 de fornecedores agrupados (sem nome), 81 de contato, 80 de equipe, 686 meses de moradia, 79 de salário, 25 resumos e 5 motivos. São 40 testes novos, **310 no total**, e o lint passa.
- **Ensaio ponta a ponta em 19/11/2026**, numa branch com validade (`ensaio-ponta-a-ponta`), com o executor, a carga e logins reais:
  - Papéis criados pelo comando; migrações 001 e 002 aplicadas pelo executor (ensaio, gravação e uma repetição, que não achou nada pendente); carga em ensaio, gravada e repetida, sempre com as mesmas contagens. O driver aceitou cada arquivo de migração numa só chamada.
  - **Permissões, testadas conectando como cada papel:** `sd_leitura` lê o `publico` (79 salários) e é **negado** em ler o `interno`, inserir, apagar, truncar e criar tabela. `sd_carga` é negado em `UPDATE`, em ler `interno.migracoes`, em criar ou apagar tabela e em criar papel.
  - **Integridade:** em 610 pares senador-ano, a soma de `despesas_mensais` bate com a da verificação da cota; nada de 2008 e 2009 em despesas nem em fornecedores; a soma das despesas provadas é a mesma no SQLite e na nuvem (R$ 211.550.675,21). O banco inteiro ocupa **20 MB** no PostgreSQL, bem abaixo do 1 GB do plano gratuito.
- **Aplicada na produção em 19/11/2026**, com o OK do mantenedor. Antes de mexer, conferi que o alvo era o endpoint da produção (o mesmo que a Neon informa) e que estava vazio (nenhum esquema do projeto, nenhum papel `sd_`). Os mesmos comandos do ensaio rodaram, cada um primeiro em ensaio: papéis, migrações 001 e 002 e carga, com as mesmas 17 tabelas e contagens do ensaio. As conferências repetidas na produção deram o mesmo resultado: permissões de `sd_leitura` e `sd_carga` como esperado, soma das despesas igual à do SQLite (R$ 211.550.675,21), nada de 2008 e 2009, banco com 20 MB.
- **Ainda não feito:** a **atualização diária automática** (GitHub Actions, que guardaria as URLs como segredos do repositório) e a API, que vai ler com o papel `sd_leitura`.
- **Descartado:** ORM e Alembic (complexidade sem ganho para 2 migrações); asyncpg (não há necessidade de assincronia); views para o resumo (menos testáveis).
- **Status:** aceita e aplicada. Falta a atualização diária automática.

## D044: Site antes da API, com dados em arquivos JSON gerados do esquema público

- **Contexto:** a ordem de construção do `escopo.md` §13 punha a API (etapa 5) antes do site (etapa 6). Mas a D004 já diz que o site **não depende da API**: ele lê arquivos gerados pelo pipeline. O banco da Neon está no ar desde 19/11/2026 ([D042](#d042-banco-no-neon-só-dados-agregados-dois-esquemas-e-carga-repetível), [D043](#d043-migrações-em-sql-puro-driver-psycopg-e-carga-que-ensaia-antes-de-gravar)). O público principal é o cidadão, que usa o site; a API serve a jornalistas e pesquisadores (`escopo.md` §2).
- **Decisão (19/11/2026, do mantenedor):**
  1. **O site vem antes da API.** A ordem passa a ser: contrato dos dados e exportador, site, destaque do maior mês, automação diária e, só depois, a API. A API continua no escopo do MVP, mas sem data.
  2. **Os dados do site são arquivos JSON gerados pelo pipeline a partir do esquema `publico`**, lendo com o papel `sd_leitura` (`DATABASE_URL_LEITURA`). Assim o site, e depois a API, leem a mesma fronteira pública (só o provado; ausência = "não verificado").
  3. **Um arquivo por senador**, mais a lista de senadores, as verificações e os metadados. Em arquivos pequenos o celular baixa só o que usa. **Os nomes e os campos exatos** estão em rascunho em [contrato-dos-dados.md](contrato-dos-dados.md), a partir do que o protótipo `design/perfil-do-senador.html` precisa.
  4. **Os JSON não vão para o git**, como os dados brutos (D014) e os limpos (`data/limpo/`, ignorado): são gerados na hora do build, com as URLs de conexão em variáveis de ambiente.
  5. **O site é Next.js com TypeScript, exportado como páginas estáticas, no Cloudflare Pages** (D003 mantida), na pasta `web/`, com a identidade da D029.
- **Primeira fatia:** o contrato e um exportador em Python, com testes, começando pela lista de senadores e **um** perfil real; depois o esqueleto do site com a página de perfil lendo esse JSON.
- **Por quê:** o site é o que o cidadão vê, e fazê-lo primeiro não gasta as horas grátis de hospedagem da API (D004). Gerar os JSON do `publico` força o site a respeitar a regra "só o comprovado" e exercita o caminho que a API usaria depois. Um contrato de dados definido antes da tela evita refazer a tela.
- **Descartado:** gerar os JSON do SQLite local (dependeria de arquivos que só existem numa máquina e não exercitaria a fronteira pública); um único arquivo grande (pesado no celular); fazer a API primeiro (sem público imediato).
- **Não verificado:** os limites atuais do Cloudflare Pages e do GitHub Actions, que precisam ser reconfirmados nas páginas oficiais antes de publicar (AGENTS.md, seção 7). Na máquina de desenvolvimento há Node 24 e npm 11 (conferido em 19/11/2026).
- **Altera:** a ordem de construção do `escopo.md` §13.
- **Status:** aceita quanto à ordem e à direção. O contrato dos JSON está em [contrato-dos-dados.md](contrato-dos-dados.md) e já foi implementado pelo exportador (19/11/2026); a primeira tela do site o confirma.

## D045: Foto e mandato do senador, com o endereço oficial do Senado e verificação entre duas listas

- **Contexto:** o perfil do senador mostra "Mandato" e a foto oficial (`escopo.md` §4.2), mas o pipeline ainda não coleta nenhum dos dois. Os dois estão na lista de senadores em exercício da API legislativa (`lista/atual`): o endereço da foto (`UrlFotoParlamentar`) e as datas do mandato.
- **Medido em 19/11/2026** (a lista legislativa baixada à mão em 11/11 e pedidos só de cabeçalho feitos nesse dia; **nenhuma imagem foi baixada**):
  - os 81 senadores têm endereço de foto, no padrão `…/fotos-oficiais/senador{código}.jpg`, com os mesmos 81 códigos da lista administrativa;
  - o endereço da API é `http://` e redireciona para `https://legis.senado.leg.br/senadores/fotos-oficiais/{código}`; nos 81 a resposta final é 200 com tipo `image/jpeg`;
  - os arquivos têm de 78 KB a 1,4 MB, média de 280 KB e soma de 22 MB;
  - as duas listas concordam em UF (81 de 81), partido (81 de 81) e anos do mandato (81 de 81), e em nome em 80 de 81 (a exceção é "Nelsinho Trad" contra "NELSINHO TRAD FILHO", o caso que a [D036](#d036-verificação-automática-da-equipe-do-gabinete-por-vínculo) já trata com a regra de nome inteiro dentro do outro).
- **Decisão (19/11/2026, do mantenedor): opção A.**
  1. **O site carrega a foto do endereço oficial do Senado, com o crédito "Foto oficial publicada pelo Senado Federal"**, sem copiar nem hospedar as imagens. É o que o `escopo.md` §12 já previa. O crédito diz só o que se prova: que a foto é a que o Senado publica para aquele parlamentar, e não que "esta é a foto de fulano".
  2. **A foto só aparece na página do perfil.** A lista de senadores usa as iniciais: as 81 fotos somam 22 MB e não há controle do tamanho de uma imagem que não é nossa.
  3. **O mandato** mostra o ano em que começa e o ano em que termina, tirados das datas da lista legislativa; as datas completas vão no JSON.
  4. **Verificação nova, "perfil"**, no mesmo dia da coleta (D035): a lista legislativa deve ter os mesmos códigos da administrativa; nome (pela regra da D036), UF, partido e anos do mandato devem ser iguais nas duas listas; e o endereço da foto, já com o redirecionamento resolvido e em `https`, deve responder 200 com `image/jpeg` no dia da carga. O endereço guardado é o final.
  5. **Exibição (D037):** é dado descritivo. Foto e mandato aparecem para quem foi provado, cada um com o seu freio de segurança de 5%. Falhou, o campo some, sem aviso no perfil, e a página "Verificações" conta o caso.
  6. **A política de conteúdo do site** (CSP) passa a liberar `https://legis.senado.leg.br` em `img-src`.
  7. **Checagem opcional, ainda não aprovada:** pedir só os primeiros bytes de cada foto, para confirmar que é um JPEG de tamanho razoável e não uma imagem substituta (o menor dos 81 arquivos tem 78 KB). Pelo `AGENTS.md`, baixar arquivos pede o aval do mantenedor; sem ele, vale só a conferência de cabeçalho do item 4.
- **Quando:** depois da primeira fatia do site, que sai sem foto e sem mandato. A implementação será um módulo novo do pipeline, a migração 003 (`publico.perfil`) e a carga, com testes; o JSON do perfil ganha o bloco `quem_e` ([contrato dos dados](contrato-dos-dados.md)).
- **Por quê:** carregar do endereço oficial não copia conteúdo de autoria do Senado e mantém a foto atualizada. A verificação segue a regra "só o comprovado" (D025): duas publicações do Senado precisam concordar sobre quem é a pessoa.
- **Limites:** a verificação prova **consistência** entre listas do Senado, e não que a foto é mesmo da pessoa. A ligação entre o código e a foto é a que o próprio Senado publica. Os riscos que sobram são uma foto desatualizada, uma imagem substituta ou um erro do Senado: os dois primeiros são cobertos pelas checagens acima, e o canal para reportar erros do `escopo.md` §4.5 cobre o resto. A foto depende do servidor do Senado: se ele sair do ar, a imagem some até voltar. Nada garante que o endereço oficial continue o mesmo; por isso a verificação roda a cada carga.
- **Descartado em 19/11/2026:** copiar as fotos e reduzi-las para uns 200 px (opção B). **Retomado e feito em 23/11/2026**, pela [D047](decisoes.md#d047-cópias-reduzidas-das-fotos-oficiais-com-pillow).
- **Também descartado (19/11/2026):** confirmar a identidade pelo CPF ou comparando rostos com outra base, como a do TSE. O pipeline não tem o CPF dos senadores (a D005 mantém o CPF fora do pipeline), o arquivo da foto não carrega CPF, e comparar rostos é reconhecimento facial sobre dados biométricos de pessoas reais: sensível pela LGPD, sujeito a erro e dependente de uma fonte fora do Senado, que só entra com aprovação (AGENTS.md, seção 6).
- **Status:** aceita.
- **Implementação (23/11/2026), com três decisões do mantenedor:**
  1. **A lista da home mostra a foto** ("tem que mostrar a foto"). **Altera o item 2 da decisão acima**, que a limitava ao perfil: a lista passa a carregar a foto de quem foi provado, e mostra as iniciais para quem não foi ou quando a imagem não carrega. O custo é o peso: as 81 fotos somam 22 MB, mas o navegador só baixa as que aparecem na tela (`loading="lazy"`).
  2. **A migração 004 foi autorizada para a produção**, depois do ensaio numa branch da Neon (como as anteriores).
  3. **A checagem dos primeiros bytes de cada foto foi aprovada** (item 7 acima, que estava pendente de aval). O pipeline baixa só os **primeiros 1.024 bytes** de cada uma (pedido com `Range`) e não guarda imagem nenhuma.
  - **O que o código faz** (`python -m senadados_pipeline.perfil`, [pipeline/README.md](../pipeline/README.md)): baixa a lista legislativa na hora e, para cada senador, exige identidade igual nas duas listas (código, nome pela regra de "um nome inteiro dentro do outro", UF e partido) antes de provar o mandato e a foto. O **mandato** vale se o ano de início e o de fim são iguais nas duas listas (início da primeira legislatura, fim da última que a lista traz). A **foto** vale se o endereço final está em `https://legis.senado.leg.br`, termina no código do senador, responde 200 ou 206 com `image/jpeg`, começa com os bytes de um JPEG e tem pelo menos 10 mil bytes. **O 10 mil é um julgamento:** a menor foto medida tem 78 KB.
  - **Exibição:** dado descritivo (D037), cada campo com o seu freio de 5%. Só o valor provado vai para `publico.perfil`; o resultado fica em `interno.verificacao_perfil`. Um código que só a lista legislativa traz é avisado na saída e não bloqueia nada (a redação original pedia códigos iguais nas duas listas); um que só a administrativa traz fica sem explicação.
  - **No JSON:** `quem_e.mandato` traz os anos (`inicio`, `fim`) e as datas completas (`inicio_data`, `fim_data`), e `foto_url` vai na lista só para quem foi provado ([contrato](contrato-dos-dados.md)). O perfil passou a mostrar a linha "Mandato" no cartão.
  - **Resultado em 23/11/2026** (coleta e verificações do dia, banco da produção): **81 de 81 idênticos na foto e 81 de 81 no mandato**; as duas listas concordaram em código, nome, UF e partido nos 81. Ensaio numa branch da Neon (`ensaio-perfil-20261123`) e depois a produção: migração 004, carga (81 linhas em `publico.perfil` e 162 em `interno.verificacao_perfil`) e o exportador (84 arquivos, com `foto_url` nos 81). Permissões conferidas conectando como cada papel: `sd_leitura` lê `publico.perfil` e é negado em `interno.verificacao_perfil`, em inserir e em apagar; `sd_carga` é negado em `UPDATE` e em criar tabela.
  - **Política de conteúdo (item 6), feita em 23/11/2026:** `web/public/_headers` (o Cloudflare Pages o lê) traz a CSP, que libera só o próprio endereço e, em `img-src`, `https://legis.senado.leg.br`. `script-src` e `style-src` levam `'unsafe-inline'`, porque o Next.js escreve o script de início e os estilos dentro do HTML. **Testada** servindo `out/` com o cabeçalho e abrindo no navegador do app: a foto do Senado carrega (480 por 600), as fontes hospedadas carregam, nenhuma violação aparece, e uma imagem de outro endereço é bloqueada por `img-src`. **Não testada** no Cloudflare Pages de verdade (a publicação não foi feita).
  - **Peso das fotos (medido em 23/11/2026):** 81 arquivos JPEG de 480 por 600, 23,2 MB no total, média de 287 KB, mediana de 253 KB, quatro com mais de 1,2 MB. A lista mostra cada uma com 84 pontos de largura e o mosaico da home baixa 12 de uma vez. O Senado as serve com `cache-control: max-age=600`, não aceita parâmetro de tamanho e não entrega WebP. Opções: **(a) sem copiar:** `preconnect` ao endereço do Senado, menos fotos no mosaico em tela pequena ou com economia de dados, e reservar o espaço da imagem; **(b) copiar e reduzir** as fotos (uns 15 KB cada em WebP), que resolve o peso; **(c) redimensionar na hora no Cloudflare**, que exige conferir os limites do plano gratuito (não verificado). Escolhida a (b), na D047.
  - **Escolhida a opção (b)** pelo mantenedor em 23/11/2026: ver a [D047](#d047-cópias-reduzidas-das-fotos-oficiais-com-pillow).
- **Prévia (20/11/2026):** o mantenedor viu as fotos no perfil e na lista dos 81 senadores, com o endereço oficial preenchido **só nos arquivos locais de teste** (a verificação "perfil" ainda não existe, e o exportador apaga esse preenchimento na próxima execução). As imagens têm 480 por 600 pontos, na proporção 4 por 5, e cabem na caixa do perfil sem corte. A página mostra as iniciais no lugar de uma foto que não carrega. **Em aberto, decisão do mantenedor:** a lista de senadores mostra a foto (como na prévia) ou só as iniciais (como decidido acima, por causa do peso: 22 MB para as 81, mesmo carregando só as que aparecem na tela).

## D046: Site em Next.js 16 com exportação estática, fontes hospedadas e testes com Vitest

- **Contexto:** a [D003](#d003-site-em-nextjs-estático-no-cloudflare-pages) escolheu Next.js estático no Cloudflare Pages, a [D044](#d044-site-antes-da-api-com-dados-em-arquivos-json-gerados-do-esquema-público) pôs o site antes da API, com dados em JSON, e a [D029](#d029-identidade-visual) carregava as fontes do Google Fonts. Faltava decidir as versões, como o site lê os dados e o que fazer com as fontes.
- **Decisão (19/11/2026; o mantenedor aprovou as fontes hospedadas e a instalação das dependências):**
  1. **Next.js 16.4.6, React 19.3.1 e TypeScript 5.9**, com `output: "export"` e `trailingSlash`: `next build` gera as páginas prontas em `web/out/`, sem servidor. A versão 7.0.2 do TypeScript existe e **não foi testada** com o Next.js; usei a 5.9 por prudência. Todos os componentes rodam no build, exceto um pequeno componente de cliente que abre a pergunta quando se toca num cartão do resumo.
  2. **Os JSON são lidos na hora do build** (`web/dados/`, gerados pelo exportador e fora do git). Sem eles, o build para com uma mensagem que diz o que rodar.
  3. **As fontes ficam no próprio site** (pacotes `@fontsource-variable` de Fraunces, Hanken Grotesk e Bricolage Grotesque), e não mais no Google Fonts. **Altera a D029.** Conferido no navegador: a página só faz pedidos ao próprio endereço, nenhum ao Google.
  4. **Testes: Vitest** para as funções de formatação (12 testes), mais `tsc --noEmit` e o próprio build. Não há teste automatizado de tela nesta fatia.
  5. **`agentRules: false`:** o `next dev` escreve sozinho um `AGENTS.md` em `web/` com regras para agentes de código. Desliguei, porque as regras do projeto estão no `AGENTS.md` da raiz e um segundo arquivo, gerado por uma dependência, só confunde.
  6. **Primeira fatia:** o perfil do senador e uma lista provisória só para navegar. Ficam de fora foto e mandato (D045), posição entre os senadores, ranking, comparação, busca e a página "Verificações".
  7. **O perfil segue o protótipo** (`design/perfil-do-senador.html`) com os dados reais, em texto neutro quanto a gênero ("Quanto ganha?", "Usa moradia do Senado?"), porque o banco não tem o sexo do senador. O texto do salário seguiu a [D041](#d041-verificação-automática-do-salário-pela-identidade-do-senador) até 20/11/2026; depois foi corrigido (veja a atualização dessa data).
- **Conferido em 19/11/2026:** o build gera 84 páginas (os 81 perfis, a lista e a de erro), 14 MB no total, contando as fontes; as dependências instaladas são 62 pacotes e o `npm install` não acusou vulnerabilidade. No navegador, o perfil completo de um senador e o de outro com poucos blocos abrem sem erro de console e sem rolagem lateral em 375 px; tocar num cartão do resumo abre a pergunta; nenhum texto mostra `NaN`, `undefined` ou `null`.
- **Não verificado:** Safari e Firefox, leitor de tela, contraste medido e desempenho. A publicação no Cloudflare Pages (cabeçalhos de segurança e política de conteúdo) ainda não foi feita, e os limites do Cloudflare Pages seguem por reconfirmar.
- **Por quê:** páginas prontas são rápidas e baratas e não dependem de servidor nem da API ([D004](#d004-fastapi-no-render-e-o-site-não-depende-dela)). Hospedar as fontes evita que cada visita entregue o endereço do visitante ao Google, no mesmo espírito da D008.
- **Descartado:** `create-next-app` interativo (os arquivos foram escritos à mão, para entrarem só os necessários); ESLint e outras ferramentas nesta fatia (menos dependências); carregar as fontes do Google Fonts.
- **Altera:** a D029, no que diz respeito às fontes.
- **Status:** aceita.
- **Atualização (20/11/2026):** a home passou a ter a busca por nome (sem exigir acento) e os filtros por estado e partido, e os cartões da lista têm todos a mesma altura. O site já sabe mostrar a foto e o crédito quando o JSON os trouxer (`quem_e.foto` no perfil e `foto_url` na lista); sem eles, mostra as iniciais. Mais 6 testes (18 no total).
- **Atualização (20/11/2026, a pedido do mantenedor):** os cartões da lista passaram a ter a foto em retrato (proporção 4 por 5, 84 pontos de largura) e **selos** de partido (verde, com fundo da cor da marca), UF (escuro) e "suplente" (tracejado), em vez de texto cinza. Os selos **não usam cor por partido**, para não sugerir um lado (D010). A foto do perfil subiu de 200 para 260 pontos de largura. Medi que as imagens do Senado variam de 480 para 1.152 pontos de largura nos arquivos maiores (até 1,4 MB), o que pesa na decisão sobre a foto na lista (D045).
- **Atualização (20/11/2026, a pedido do mantenedor):** revisão visual e de textos do site.
  - **Home:** a abertura virou o nome "senadados", a frase "O que o Senado publica sobre cada senador, de forma simples", seis pílulas do que se encontra e um mosaico de 12 retratos oficiais **sorteados no navegador a cada visita** (o servidor manda só os quadros vazios, para o HTML bater). Vem depois "Como funciona", a busca e a lista. Saíram os três números do bloco antigo (81, conferências e data). O selo "81 senadores em exercício" passou a mostrar "N de 81" ao filtrar. "S/Partido" aparece como "Sem Partido" só na tela (`nomePartido`); o valor do filtro continua o do Senado.
  - **Cabeçalho:** só a marca, fixa no topo (62 px, linha suave). Com a página rolada, um clique nele (inclusive na marca) sobe suavemente, em qualquer página. Já no topo, na página do senador, a marca leva à home. Na home o clique na marca **nunca navega** (navegar para "/" estando em "/" refazia a página e sorteava outras fotos). A rolagem suave global saiu: ela deixava a página do senador cortada ao vir da home e fazia a volta passar pelo topo. A suavidade ficou só no clique do cabeçalho e nos "Entender".
  - **Perfil:** foto, nome, partido, UF e os quatro dados formam um cartão só, fixo na coluna da esquerda (não se move em nenhuma posição da rolagem: o espaço do fim da página fica na coluna da direita e o topo do cartão coincide com o ponto em que ele gruda). No celular e no tablet o cartão é o mesmo, sem ser fixo (no tablet, com no máximo 420 pontos de largura). O resumo ganhou o título "Resumo de 2026" num bloco verde (centralizado no celular), sem a pílula do período e sem "toque num cartão". Os avisos e o cartão da equipe dentro das guias são brancos com borda, para não ficarem verdes sobre o verde da linha "Quanto". Todas as guias começam fechadas. Entrou o cartão "Quem vendeu ou prestou serviço" (contagem de empresas do ano, sem nomes), o que completa a grade do resumo. O crédito da foto sai do texto e fica na dica ao passar o mouse.
  - **Textos em linguagem simples**, sem mudar nenhum número: "remuneração básica" virou **"salário-base"** (o texto explica que é a parte principal e que não é o total antes dos descontos, como a [D041](#d041-verificação-automática-do-salário-pela-identidade-do-senador) pede), "líquido" virou "depois dos descontos", "Maior mês" virou "Mês de maior uso", "Quem recebeu o dinheiro?" virou **"Quem vendeu ou prestou serviço?"** (o reembolso vai ao senador; a nota mostra quem recebeu dele), "Gabinete: onde fica, contato e equipe" virou "endereço, contato e equipe". O texto sobre pessoas físicas trocou "porque essas pessoas não são políticas" por "para proteger a privacidade delas" (D008). Datas e meses não se partem no fim da linha. Com **um mês só** de verba, o cartão e o aviso de "maior mês" não aparecem, porque o "maior" de um mês só não diz nada.
  - **Rodapé removido** da home e do perfil. Ele trazia a fonte, a data e a frase de que a conferência entre bases **não é auditoria** e de que o site não julga a legalidade. Cada guia mantém "De onde vem este número" (fonte e data), mas a frase sobre auditoria e legalidade **deixou de aparecer em qualquer lugar da home e do perfil**, apesar de o `AGENTS.md` pedir que o site a diga. **Pendente:** a página "Sobre os dados" (prevista no escopo) deve recebê-la. **Atualização (23/11/2026):** a frase da auditoria voltou na página "Verificações" ([escopo §4.5](escopo.md)); a "Sobre os dados" deve repeti-la.
  - **Descartado depois de estudado:** o "senadômetro" (total do que o Senado gasta). A planilha de execução orçamentária mostra um total pago (R$ 5,28 bilhões em 2024), mas cerca de 83% é pessoal e aposentadorias, o salário do ano não está provado mês a mês e a D026 proíbe totais "do Senado"; o mantenedor decidiu não fazer. Também descartado o destaque do "senador que mais usou a verba" no ano e no mês: o do ano é provável (empate técnico de R$ 2.343,69), o do mês tem fonte única.
  - **Salário (corrige o texto da [D041](#d041-verificação-automática-do-salário-pela-identidade-do-senador)):** a folha de outubro foi conferida de novo (baixada só para isso, sem guardar nomes). Em 75 das 80 linhas com R$ 46.366,19 o líquido é o salário-base menos previdência e imposto de renda; 3 linhas trazem "auxílios" e 5 "gratificação natalina", e os outros campos estavam zerados. Por isso o texto deixou de dizer que a remuneração básica "não é o total antes dos descontos" e passou a dizer que o salário-base é o valor antes dos descontos, que os descontos são previdência e imposto de renda e que em alguns meses a folha traz outros valores. O pipeline continua guardando só o salário-base e o valor depois dos descontos.
  - **Média e período da verba:** a média por mês agora divide pelos meses do período (do primeiro ao último com nota), inclusive os vazios; antes dividia só pelos meses com nota e ficava maior para 5 senadores com meses sem nota. Quando as notas terminam bem antes da última atualização (Efraim Filho e Ana Paula Lobato, até julho), a guia diz que não há nota reembolsada depois daquele mês, o que é verdade porque o total do ano bate com o resumo do Senado (D035).
  - **Pílulas da abertura:** passaram a espelhar as seis guias do perfil, na mesma ordem ("Quanto ganha", "Quanto usou da verba", "Em que usou a verba", "Quem vendeu ou prestou serviço", "Equipe e contato do gabinete", "Se usa moradia do Senado").
  - **Varredura (20/11/2026):** removidos o `.eyebrow`, a classe `com-foto`, a leitura das verificações (`verificacoes()` e seus tipos, que nenhuma tela usa ainda; o arquivo `verificacoes.json` continua sendo gerado, para a futura página "Verificações"), regras de CSS repetidas (`.grade a`, o mosaico no celular, `.av` e `.ficha .av`) e a cópia do desenho do nome em dois lugares (agora `NomeMarca`). `tsc` com `noUnusedLocals`, 21 testes, `ruff` e 340 testes de Python passam, e o build estático gera as 84 páginas.
  - **Testes:** 21 (mais `usoCurto`, `mesAno` e `periodoAno`). **Não verificado:** Safari e Firefox; o piscar das fotos ao rolar (troquei a decodificação para síncrona, sem confirmar a causa).

## D047: Cópias reduzidas das fotos oficiais, com Pillow

- **Contexto:** a [D045](#d045-foto-e-mandato-do-senador-com-o-endereço-oficial-do-senado-e-verificação-entre-duas-listas) carregava a foto direto do endereço do Senado. Medido em 23/11/2026: 81 JPEG de 480 por 600, 23,2 MB no total, 287 KB em média e quatro com mais de 1,2 MB, mostrados na maior parte com uns 170 pontos de largura. O Senado as serve com `cache-control: max-age=600`, não aceita parâmetro de tamanho e não entrega WebP. A home baixava 12 fotos de uma vez e a lista, as que aparecem na tela: pesado em celular.
- **Decisão (23/11/2026, do mantenedor, opção (b) da D045):** um passo novo do pipeline, `python -m senadados_pipeline.fotos`, baixa a foto de cada senador **cuja foto foi provada hoje** pela verificação do perfil e grava duas cópias em WebP, sem metadado: `{código}-p.webp` (240 por 300, lista e mosaico) e `{código}-g.webp` (480 por 600, cartão do perfil), cortadas na proporção 4 por 5, com qualidade 78. Ficam em `web/public/fotos/`, **fora do git** (como `web/dados/`), e a pasta inteira é refeita a cada execução, então a foto de quem saiu da lista some (D026). O passo só apaga e refaz uma pasta chamada `fotos`.
- **No site:** a imagem vem da cópia do próprio site; se ela faltar, o site usa o endereço oficial do Senado; se este falhar, ou se não houver foto provada, mostra as iniciais. O crédito segue sendo "Foto oficial publicada pelo Senado Federal". `public/_headers` dá uma semana de cache às cópias.
- **Tecnologia nova: Pillow** (13.0.0), o único acréscimo. Sem custo. Era preciso um redimensionador, e o WebP vem pronto nele.
- **Resultado medido em 23/11/2026:** as 81 fotos viraram 162 arquivos que somam **3,4 MB** (contra 23 MB): a cópia pequena tem 10 KB em média (17 KB no máximo) e a grande, 32 KB (54 KB no máximo). No navegador, a home carregou 26 imagens, todas do próprio site, com **251 KB** no total (antes, só as 12 do mosaico passavam de 3 MB), e o cartão do Alan Rick passou de 241 KB para 27 KB. Conferido também o caminho de reserva: com uma cópia apagada, o perfil carregou a foto do Senado.
- **Reserva:** se uma cópia faltar, o site usa o endereço oficial da foto; apagar `web/public/fotos/` devolve o site a esse comportamento.
- **Por quê:** é a única opção que resolve o peso sem depender de um serviço de terceiros e sem custo, e a de reserva mantém o site funcionando se a cópia faltar.
- **Descartado:** só `preconnect` e menos fotos no mosaico (ajuda, mas não reduz o peso de cada foto); redimensionar na hora no Cloudflare (os limites do plano gratuito não foram verificados).
- **Pendente:** rodar este passo faz parte do build do site; ele ainda não está na rotina diária (que não existe).
- **Status:** aceita.

## D048: Só o ano atual e o anterior, com troca de ano na página do senador

- **Contexto:** o site só mostrava o último ano com dados ("Resumo de 2026"), mas o pipeline coletava, limpava e verificava as despesas de 2008 a 2026 em toda execução: 19 arquivos, 154 mil despesas, 1.539 consultas de resumo por verificação (uns 3 minutos) e 25 mil linhas de despesa mensal no banco. Os anos antigos não apareciam em tela nenhuma.
- **Decisão (23/11/2026, do mantenedor):**
  1. **O projeto processa só o ano atual e o anterior** (`anos_do_projeto()`, em `config.py`). A coleta, a limpeza e as verificações usam esses dois anos por padrão (`--anos` continua aceitando outro intervalo). A limpeza ignora arquivos de outros anos, mesmo que existam em `data/raw/`.
  2. **A página do senador abre num ano e deixa trocar para o outro.** O botão "Ver os dados de 2025 →" muda a página inteira para o ano escolhido. O endereço do ano que abre é o do senador (`/senador/{endereço}/`); o outro ano leva o ano no endereço (`/senador/{endereço}/2025/`), o que permite compartilhar o link de um ano.
  3. **Qual ano abre (regra de dois anos):** o atual, quando a verba dele já tem **pelo menos dois meses** (com um mês só, o "mês de maior uso" e a média não dizem nada, D030); senão o anterior, se houver. Se o atual for o único, abre o atual. Um ano só é oferecido se a verba dele foi provada (D035), ou se é o ano dos dados e há algo provado "de agora".
  4. **O que muda com o ano:** a verba (total, mês a mês, categorias, mês de maior uso), os fornecedores e, desde a D049, a moradia. **Salário, equipe e contato valem para um instante** (a folha do último mês, a lista de servidores e a página mensal de hoje) e **só aparecem no ano dos dados**: o Senadados não tem como provar essas coisas para o ano anterior, então, pela D025, elas simplesmente não aparecem quando se escolhe 2025.
- **Por quê:** o histórico antigo custava tempo e manutenção e não chegava ao cidadão. Dois anos bastam para a regra do início de cada ano: em janeiro, o ano novo ainda não tem despesa, e o perfil continua mostrando o último ano completo. Sai também o problema da cota de 2008 e 2009, que o Senado não explica.
- **O que se perde:** qualquer gráfico de tendência de vários anos, a "versão 2" do README ("histórico desde 2008") e a frase "de 2010 a 2026 tudo bate", que fica só como registro histórico em [verificacoes.md](verificacoes.md). **É reversível:** o Senado mantém os arquivos antigos, e `--anos` recoleta qualquer intervalo.
- **Altera:** a D026 (o histórico de cada senador desde 2008 deixa de ser mantido) e o resultado da D035 (2010 a 2026 viram registro histórico).
- **Fora de escopo nesta decisão:** salário, equipe e moradia do ano anterior. **A moradia foi feita logo depois, na [D049](#d049-moradia-do-ano-anterior-com-três-fontes); salário e equipe seguem de fora.** Teriam de ser provados à parte (a folha de cada mês e, no caso da equipe, uma lista de servidores da época). **Não verificado:** se a API do Senado guarda a lista de servidores de 2025 e se o resumo de 2025 traz a moradia mês a mês; não testei.
- **Status:** aceita.

## D049: Moradia do ano anterior, com três fontes

- **Contexto:** a D048 deixou de fora, no ano anterior, tudo o que é "foto de hoje". Em 23/11/2026 pesquisei, só em leitura, o que dava para provar de 2025 ([D048](decisoes.md#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador)). A **moradia** foi a única que passou: o resumo da API, o resumo da tela do portal e a página mensal de benefícios existem por ano. O que não existe para 2025 é a quarta fonte da [D039](#d039-verificação-automática-da-moradia-mês-a-mês), a lista do mês, que só diz quem usa o benefício **hoje**.
- **Decisão (23/11/2026):** o passo `moradia` confere **dois anos**: o atual, com as quatro fontes (como antes), e o anterior, com as **três** que existem para ele (`compare_moradia(..., usar_lista=False)`). Os resultados são `identico` ou `explicado` (a tela diz "renúncia" onde a API diz "não utilizou") ou `sem_explicacao`; **não há `pendente` no ano anterior**, porque ele nasce da comparação com a lista de hoje. Cada ano tem o seu freio de 5% (D037). A coleta do ano anterior grava `data/raw/moradia/uso_{ano}.json`, sem a lista.
- **No JSON (contrato, versão 2):** `moradia` deixou de ser `{ano, meses}` e passou a `{ "anos": [{ano, meses}] }`, um bloco por ano provado, do mais antigo ao mais recente. A carga já aceitava vários anos (as tabelas têm a coluna `ano`) e não mudou. **Quebra o site:** `versao_contrato` sobe para 2.
- **No site:** a moradia aparece na visão de 2025 (cartão, chips e a guia), e o texto "de onde vem este número" diz "três publicações" em 2025 e "quatro" em 2026. Só quem tem a verba de 2025 provada tem a página de 2025 (D048), então quem não era senador naquele ano não aparece como "não usou".
- **Resultado em 23/11/2026:** 2025: **80 idênticos e 1 explicado, e a moradia aparece para 81**; 72 senadores usaram algum benefício. 2026: 77 idênticos, 1 explicado e 3 pendentes (como antes). Ensaio da carga na produção: `moradia_verificada` 78 → 159 linhas, `moradia_meses` 1.559.
- **Limite:** com três fontes em vez de quatro, a prova do ano anterior é um pouco mais fraca: não há como saber se a página mensal estava atrasada em relação ao fim do ano. As três fontes vêm do mesmo sistema do Senado (D027). **Não verificado:** se o Senado corrige a página mensal de 2025 depois; o pipeline reconfere todo dia.
- **Não entram:** o salário de 2025 (em nenhum mês de 2025 as cinco provas da D041 passam: de 8 a 35 senadores por mês têm folha suplementar com valores, contra 2 em outubro de 2026) e a equipe de 2025 (a conferência do resumo contra a tela dá 67 iguais, 6 diferentes e 8 sem dado, e 6 de 73 passa do freio de 5%; também **não verificado** a que data de 2025 o resumo se refere).
- **Status:** aceita.

## D050: Comparação de dois senadores, lado a lado

- **Contexto:** a [D021](#d021-comparação-lado-a-lado-entra-no-mvp) pôs a comparação de dois senadores no MVP, e o público do Senadados é quem "não entende nada" de dados. Em 24/11/2026 montei seis formas de mostrar a mesma comparação (lado a lado, só frases, barras pareadas, a diferença em destaque, uma pergunta por vez, e régua com os meses) numa tela de teste, e o mantenedor escolheu a **lado a lado**.
- **Decisão (24/11/2026, do mantenedor):**
  1. **A tela é `/comparar/`**, com os dois senadores escolhidos por busca de nome. O endereço guarda a escolha (`?a=alan-rick&b=ana-paula-lobato`), para o link da comparação poder ser copiado e compartilhado; como o site é estático, a escolha é lida no navegador, e não há uma página por par (seriam 6.480). O perfil ganhou o botão "Comparar com outro senador →".
  2. **Uma barra fixa abaixo do cabeçalho** mostra sempre os dois senadores (foto e nome) e o botão de trocá-los de lugar, para que no celular nunca se perca quem é quem.
  3. **Seis cartões, um por guia do perfil**, na mesma ordem: salário, verba, em que usou, quem vendeu ou prestou serviço, gabinete e moradia. O contato fica de fora, porque endereço e telefone não se comparam. Cada cartão traz os dois valores, uma barra pareada na mesma escala (onde há um número comparável), a diferença, quem tem o maior número e uma frase pronta. A verba traz ainda o gráfico mês a mês dos dois e o mês de maior uso de cada um; "em que usou" traz todas as categorias, cada uma com as duas barras; "quem vendeu" traz as três empresas que mais receberam de cada um; a moradia traz os dois benefícios de cada um.
  4. **Só o ano dos dados**, igual para os dois. Dado que não vale para o ano (salário e gabinete só existem no ano dos dados, [D048](#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador)) fica sem valor.
  5. **Só o comprovado (D025):** o que um dos dois não tem vira "Sem dado", e a frase diz de quem é a falta. Nada é estimado nem preenchido.
  6. **Sem julgamento (D010, D024):** a frase diz "a mais" e "a menos", nunca "gastou demais"; o destaque marca só o número maior, sem cor de "bom" ou "ruim". As duas cores são o preto e o verde-limão com contorno, que se distinguem sem depender do tom. Quando os períodos com notas são diferentes (um senador com notas até outubro e outro até novembro), a frase avisa e o cartão mostra a média por mês.
  7. **Os dois senadores têm de ser diferentes:** a lista não deixa escolher o mesmo duas vezes.
- **Por quê:** o lado a lado é a forma mais parecida com o que as pessoas já conhecem de uma tabela de comparação, e a barra pareada e a frase tiram a necessidade de fazer conta. As regras 4 a 6 só repetem, para a comparação, o que o resto do site já exige.
- **Não entra nesta decisão:** a posição entre os senadores, o ranking e a comparação com a média do grupo. Eles comparam com o grupo todo e seguem o "tudo ou nada" da [D037](#d037-exibição-por-tipo-de-dado-e-freio-de-segurança), que ainda depende de definir quem entra no grupo. A comparação de dois senadores não depende disso.
- **Descartado:** as outras cinco formas (só frases, barras pareadas isoladas, diferença em destaque, uma pergunta por vez, régua); uma página por par de senadores (6.480 páginas); um aviso sobre "limites por estado" (seria uma afirmação sobre regra, [D022](#d022-ranking-nacional-com-contexto-de-estado-e-região)).
- **Não verificado:** Safari e Firefox, leitor de tela e o contraste medido.
- **Implementação:** `web/src/lib/comparar.ts` (regras, com testes), `web/src/components/Comparador.tsx` e `web/src/app/comparar/page.tsx`.
- **Status:** aceita.
