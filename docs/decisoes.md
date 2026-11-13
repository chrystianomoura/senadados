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
| D026 | Só senadores em exercício | Vale |
| D027 | Como conferir os dados | Vale |
| D028 | Gastos fora da cota e moradia | Moradia vale; gastos fora da cota saíram do MVP |
| D029 | Identidade visual | Vale |
| D030 | Destaque do maior mês no lugar do alerta | Vale |
| D031 | Onde fica o gabinete: contato | Vale (revista em 12/11/2026) |
| D032 | Organização do repositório e dos documentos | Vale |

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
