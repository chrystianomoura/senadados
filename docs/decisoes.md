# Registro de decisões

Cada decisão do projeto, com o motivo. Se uma decisão mudar, **não apague a antiga**: marque-a como substituída e escreva a nova. Assim o histórico mostra o raciocínio completo.

**Formato:** contexto, decisão, por quê, alternativas descartadas, status.
**Status:** `aceita` (vale) ou `provisória` (depende de dados que ainda não medimos).

Data de todas as decisões iniciais: 11/11/2026.

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

## D006: Modelo de anomalias

- **Contexto:** medimos o `detalhamento` nos 19 anos. Está vazio até 2010, chega a mais de 80% entre 2013 e 2018 e cai para cerca de 35 a 40% nos anos recentes, que são os que mais interessam ao cidadão.
- **Decisão:** começar com Isolation Forest, que compara cada mês com o histórico do próprio senador, usando valor, categoria e fornecedor, e dá o motivo do alerta. A classificação de texto fica como complemento possível para 2013 em diante, não como base.
- **Por quê:** não depende de texto e é fácil de explicar. Como a descrição vem diminuindo, um modelo apoiado nela perderia força justamente nos dados mais atuais.
- **Ainda não testado:** a qualidade do modelo não foi avaliada, e não há "resposta certa" para checar. Antes de mostrar alertas ao público, é preciso definir como validar (por exemplo, revisar à mão uma amostra de alertas).
- **Status:** aceita como ponto de partida; revisar após os primeiros testes.

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

## D009: Citação da fonte em toda página

- **Contexto:** os termos exigem, no máximo, citar a proveniência. Não há formato definido nem licença nomeada.
- **Decisão:** cada página mostra a fonte ("Senado Federal, dados abertos"), o endereço e a data de atualização, e o rodapé repete isso.
- **Por quê:** cumpre a única exigência documentada e dá transparência ao cidadão.
- **Status:** aceita.

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

## D016: Salário ligado pelo nome completo, com validação mensal

- **Contexto:** a folha de pagamento não usa o código do parlamentar. Pelo nome completo, 78 dos 81 senadores foram encontrados, sem repetições. O salário básico é de R$ 46.366,19 para 77 deles e diferente para um.
- **Decisão:** ligar pelo nome completo (normalizado, sem acento) e, a cada atualização, registrar quem ficou sem correspondência em vez de ignorar em silêncio. Mostrar o salário de cada senador como ele aparece na folha, sem supor que seja igual para todos.
- **Por quê:** o número exibido precisa ser o real, e erros de ligação devem ficar visíveis.
- **Status:** aceita.

## D017: Custo de gabinete como estimativa agregada

- **Contexto:** é possível estimar o custo mensal da equipe ligando a lista de servidores à folha. A ligação só funciona por nome, e o resultado cobre 96,9% dos servidores e só algumas parcelas da remuneração.
- **Decisão:** exibir o custo do gabinete como **valor aproximado**, agregado por gabinete, com a explicação do que está e do que não está incluído. Nunca exibir remuneração individual de assessores (D007).
- **Por quê:** o número ajuda o cidadão a entender o peso da equipe, mas apresentá-lo como exato seria enganoso.
- **Status:** aceita; revisar a metodologia antes de publicar.

## D018: Partido do ano pela filiação mais recente

- **Contexto:** o perfil com partido e UF só existe para quem está em exercício. Para os demais, é possível reconstruir o partido a partir das datas de filiação e a UF a partir dos mandatos (cobertura de 97,8% e 100% dos pares senador-ano).
- **Decisão:** o partido de um senador em um ano é a filiação mais recente até 1º de julho daquele ano; os casos sem filiação ficam como "não informado".
- **Por quê:** regra simples, reproduzível e documentada. A escolha do dia 1º de julho é arbitrária, e quem trocou de partido no meio do ano pode aparecer com o partido "errado" em parte do ano.
- **Status:** aceita; validar com casos conhecidos de troca de partido.

## D019: Atuação parlamentar na versão 2

- **Contexto:** votações, autorias, relatorias, discursos e apartes existem e são volumosos (estimativa de cerca de 300 MB em JSON para os 81 senadores). O significado de vários códigos de voto não foi verificado, e os discursos vêm só dos últimos 30 dias por padrão.
- **Decisão:** deixar a atuação para a versão 2 e guardar no banco apenas resumos (contagens e participação), nunca o JSON cru.
- **Por quê:** o MVP já cobre quem é, quanto ganha, quanto gasta, para onde vai e quem trabalha com o senador. Calcular presença com códigos que não entendemos geraria números errados sobre pessoas reais.
- **Status:** aceita.

