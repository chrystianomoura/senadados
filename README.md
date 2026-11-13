# Senadados

> Os valores que o Senado publica sobre os senadores em exercício, explicados para qualquer pessoa.

**Status (12/11/2026):** escopo e protótipo da página fechados, fontes conferidas; **o código ainda não existe**. Este documento descreve o que o projeto **vai ser** e **vai mudar** conforme aprendermos mais. Cada mudança relevante é registrada com o motivo (veja [Como este projeto é documentado](#como-este-projeto-é-documentado)).

---

## O que é o Senadados?

O Senado Federal publica, na internet, quanto cada senador gasta e quem recebe esse dinheiro. Só que esses dados chegam como planilhas enormes, com milhares de linhas, nomes de colunas técnicos e valores misturados. Na prática, quase ninguém consegue ler.

O **Senadados** pega esses dados oficiais, limpa, organiza e mostra de um jeito que qualquer cidadão entende, sem precisar saber o que é um CSV, uma API ou uma planilha.

Pense assim: o Senado entrega uma pilha de notas fiscais. O Senadados arruma essa pilha, soma os valores e conta a história em poucos gráficos e frases.

O projeto faz **duas coisas**: **mostrar os valores** e **ajudar a interpretá-los** (o que é cada número, de onde vem, como se compara). **Não julga se algo está dentro ou fora da lei.** Quem quiser investigar isso pesquisa por conta própria, e o site indica onde começar.

E só aparece o que **se comprova**: se uma informação não tem prova nos dados do Senado, ou duas bases do Senado discordam sem explicação, ela não é mostrada.

## Para que serve?

Para responder, em segundos, perguntas simples sobre cada senador:

| Pergunta | O que o site mostra |
|---|---|
| **Quem é?** | Foto, partido, estado, mandato |
| **Quanto ganha?** | A remuneração, quando a ligação com o senador é comprovada |
| **Quanto usou da verba (a cota)?** | O total por mês, por ano e por categoria, e a posição entre os outros senadores |
| **Para onde vai o dinheiro?** | Os fornecedores que mais recebem (só nos anos em que o dado existe; veja as limitações) |
| **Quem trabalha com ele?** | Quantas pessoas há no gabinete (só o número, sem estimativa de custo) |
| **Como falar com ele?** | O endereço do gabinete, o telefone e o e-mail oficiais, para quem os tem |
| **Tem benefício de moradia?** | Imóvel funcional e auxílio-moradia, mês a mês |
| **O que faz no mandato?** | Votações, projetos e comissões (numa versão futura) |
| **Qual foi o mês de maior valor?** | O mês de maior uso da verba, destacado no gráfico mês a mês (só o fato, sem julgamento) |

## Qual é o objetivo?

1. **Transparência que se entende.** Dado aberto que ninguém consegue ler não ajuda ninguém. O objetivo é fazer o dado ser compreendido, não só publicado.
2. **Mostrar o que importa, sem ruído.** Poucos números em destaque, comparações claras, detalhes só para quem quiser clicar.
3. **Funcionar para qualquer pessoa**, inclusive no celular, sem cadastro e sem custo.
4. **Ser um projeto de portfólio bem feito**, onde cada decisão técnica tem um motivo escrito e verificável.

## O que o Senadados **não** é

- **Não é um acusador nem um intérprete da lei.** O sistema aponta o que é *incomum*, não o que é *irregular*. Um valor alto pode ser legítimo. Nada aqui afirma que alguém fez algo errado, nem que algo está dentro ou fora da lei.
- **Não é uma fonte oficial.** É uma leitura independente de dados oficiais. Cada informação mostra de onde veio e quando foi atualizada.
- **Não é uma auditoria do Senado.** Verificamos se as bases do Senado **concordam entre si** e mostramos o resultado, mas não conferimos se os dados do Senado estão certos.
- **Não mostra tudo o que o Senado paga.** Mostra o que o Senado publica em dados abertos, e diz o que está dentro e o que está fora de cada número.
- **Não faz estimativas.** Nada é calculado por inferência que não se possa provar.
- **Não expõe pessoas comuns.** A equipe do gabinete aparece só em número de pessoas. Nomes de assessores não são exibidos.

## Quem aparece no site

Só os **senadores em exercício**, conforme a lista oficial do Senado (hoje, 81: 70 titulares e 11 suplentes). Quem deixa o mandato sai do site, e quem assume entra sozinho. Nenhum total ou comparação é apresentado como "do Senado": sempre diz "entre os senadores em exercício".

## Só o comprovado (a prova real)

Todo número tem origem oficial, uma consulta que o reproduz e uma data. Quando o Senado publica o mesmo número em dois lugares, os dois precisam bater:

- **Idêntico:** o número aparece.
- **Diferente, mas explicado:** aparece com a explicação.
- **Diferente e sem explicação:** não aparece.
- **Só uma fonte:** aparece, e a página explica de onde vem em palavras simples.
- **Tudo ou nada:** uma informação que compara senadores só aparece se todos a tiverem e os dados baterem para todos. Se um só falhar, ninguém a recebe. Exceção: dados de contato (telefone, e-mail) aparecem para quem os tem.
- **Sem selos na tela:** o que não se comprova simplesmente não é mostrado. A lista do que está pendente fica na página de verificações.

O primeiro teste: a cota de 2026, das despesas detalhadas contra o resumo do Senado. **72 de 79 senadores batem no centavo**, e as 7 diferenças são exatamente linhas sem categoria que o resumo não conta. Os resultados ficam numa página pública de verificações.

---

## De onde vêm os dados?

Todos vêm do **próprio Senado Federal**, são públicos e **não exigem login nem chave de acesso**. Conferi isso em 11/11/2026.

| Fonte | O que traz |
|---|---|
| Arquivos de despesas da cota (CEAPS), de 2008 a 2026 | Cada nota fiscal reembolsada: senador, categoria, fornecedor, valor, data |
| API de dados abertos administrativos do Senado | Despesas, perfil dos senadores, resumo de recursos por senador, equipe dos gabinetes, escritórios de apoio, moradia, folha de pagamento |
| Página de transparência de cada senador | Os mesmos valores por ano (2023 a 2026) e o uso de moradia mês a mês, usados para conferir |
| API de dados abertos legislativos do Senado | Foto, nome completo, partido, votações, projetos, comissões |

**Limitações conhecidas**
- Os dados de 2026 estão incompletos, porque o ano ainda está em andamento.
- Os arquivos têm sujeira (formatos de número misturados, datas fora do ano, valores negativos que parecem estornos). Parte do trabalho do projeto é tratar isso.
- O Senado pode corrigir dados antigos. Rodar o projeto hoje e daqui a seis meses pode dar valores ligeiramente diferentes.
- Os anos antigos têm menos informação: em **2008 nenhuma despesa traz o CNPJ/CPF do fornecedor nem a data da nota**. De 2009 em diante o fornecedor existe. A descrição da despesa também falha: está vazia até 2010 e vem preenchida em só cerca de 35 a 40% dos registros recentes.
- O Senado deixa de fora do resumo algumas linhas de despesa sem categoria (60 linhas em 2026, R$ 164.450,50). O site as mostra como "Sem categoria", com a explicação.
- Os termos de uso exigem, no máximo, **citar a fonte**; a licença não tem nome. Detalhes em [docs/fontes-de-dados.md](docs/fontes-de-dados.md).
- A página de navegação dos dados abertos do Senado exigiu login quando testei, mas os arquivos e as APIs em si baixaram sem nenhuma autenticação.

---

## Como funciona (visão simples)

```
  Senado publica os dados
          │
          ▼
  1. COLETAR   → baixa os dados oficiais todos os dias
          │
          ▼
  2. LIMPAR    → arruma formatos, junta anos, corrige erros
          │
          ▼
  3. GUARDAR   → grava num banco de dados organizado
          │
          ├──► 4. DESTACAR → marca o mês de maior valor
          │
          ▼
  5. SERVIR    → uma API entrega os dados a quem pedir
          │
          ▼
  6. MOSTRAR   → o site apresenta tudo de forma visual
```

---

## Por que cada tecnologia foi escolhida?

A regra do projeto: **nenhuma tecnologia entra "porque é moderna"**. Cada uma resolve um problema concreto, e o custo precisa ser **zero**, porque o projeto não tem orçamento.

### Python: para coletar, limpar e analisar
**Em uma frase:** é a ferramenta mais usada do mundo para trabalhar com dados.
**Por quê:** a mesma linguagem faz tudo (baixar, limpar, analisar, criar a API), então o projeto inteiro fica em um só lugar. Os arquivos do Senado são pequenos (algumas dezenas de MB), então a velocidade de execução, ponto fraco do Python, não atrapalha.
**Descartado:** Excel e Power BI (não mostram código nem decisões), R (bom em estatística, mas fraco para criar a API) e JavaScript para dados (ecossistema de análise bem menor).

### Pandas: para limpar os dados
**Em uma frase:** é uma "planilha superpoderosa" dentro do código.
**Por quê:** os dados chegam bagunçados, e o Pandas arruma milhares de linhas com poucas instruções.

### Pandera: para validar os dados
**Em uma frase:** é um fiscal que confere os dados antes de guardar.
**Por quê:** se o Senado mudar o nome de uma coluna, o projeto avisa na hora em vez de gravar dados errados sem ninguém perceber.

### PostgreSQL no Neon: o banco de dados
**Em uma frase:** é o arquivo organizado onde os dados limpos ficam guardados.
**Por quê:** o Neon oferece um plano gratuito, e o PostgreSQL é um banco sério usado em empresas. O plano gratuito não cobra por excesso: se o limite estourar, ele para de gravar em vez de gerar fatura. Para um projeto sem orçamento, isso protege.
**Descartado:** SQLite (mais simples, mas guardaria o dado num arquivo que só atualiza a cada nova publicação do site).

### FastAPI: a API
**Em uma frase:** é o "balcão de atendimento" dos dados.
**Por quê:** qualquer programa, inclusive o site, pede um dado (por exemplo, "gastos do senador X em 2024") e recebe a resposta organizada. A FastAPI gera de graça uma página de documentação que explica cada pedido possível.
**Observação:** o plano gratuito de hospedagem dorme quando fica parado, então a primeira chamada pode levar até um minuto. Por isso o site **não depende** dela.

### scikit-learn (modelo de anomalias): adiado
**Status:** fora do MVP ([decisão D030](docs/decisoes.md#d030-destaque-do-maior-mês-no-lugar-do-alerta-fora-do-padrão)).
**Em uma frase:** um modelo de computador que aprende o que é "normal" para cada senador e destaca o que foge disso.
**Por que adiado:** o alerta do MVP é só o **destaque do maior mês**, um fato que qualquer pessoa confere no gráfico, sem limite escolhido por nós e sem palavra que sugira culpa. O modelo precisaria de validação antes de ser usado, e só voltaria na versão 2, se ainda fizer sentido.

### Next.js (React) com TypeScript: o site
**Em uma frase:** é o que o cidadão vê e usa.
**Por quê:**
- Cada senador tem **seu próprio endereço** (por exemplo, `/senador/nome`), que dá para compartilhar.
- O site carrega rápido e funciona bem no celular, onde a maioria das pessoas vai acessar.
- Permite um design pensado para quem não é técnico.
**Descartado:** Streamlit. É mais rápido de montar, mas limita justamente o que o projeto quer garantir: endereço por senador, boa experiência no celular e visual cuidadoso.

### Site gerado antecipadamente, hospedado no Cloudflare Pages
**Em uma frase:** as páginas ficam prontas antes da visita, e não são montadas na hora.
**Por quê:** os dados do Senado mudam uma vez por dia, então não faz sentido recalcular tudo a cada visitante. Páginas prontas são rápidas e baratas de servir. O Cloudflare Pages tem plano gratuito e não restringe a "uso não comercial", como acontece com a Vercel.

### GitHub Actions: a atualização automática
**Em uma frase:** é um robô que roda o processo todo dia sozinho.
**Por quê:** gratuito para repositórios públicos, e mantém os dados atualizados sem ninguém precisar lembrar.

### pytest, ruff e uv: a qualidade do código
**Em uma frase:** testes automáticos, formatação padronizada e instalação rápida de dependências.
**Por quê:** garantem que uma correção não quebre outra coisa e que o código tenha o mesmo estilo do começo ao fim.

### O que ficou de fora de propósito
Spark, Airflow, Kafka, Kubernetes, Redis, contas de usuário e vários bancos de dados. Para o tamanho destes dados, cada um traria complexidade sem trazer benefício. Se um dia o volume justificar, a decisão será registrada com o motivo.

> **Aviso honesto sobre custos:** os limites dos planos gratuitos foram pesquisados em 11/11/2026, em sua maior parte em fontes secundárias. Eles mudam sem aviso e precisam ser reconfirmados nas páginas oficiais antes da publicação.

---

## Como este projeto é documentado

O diferencial do Senadados é a **coerência documental do início ao fim**:

- **Toda decisão tem um porquê escrito.** Escolha de tecnologia, regra de limpeza, critério de qualidade: nada entra sem justificativa.
- **A documentação muda junto com o código.** Se o código muda e o texto não, o trabalho não está terminado.
- **Dúvidas e limitações ficam visíveis.** O que não foi verificado é dito como "não verificado", não escondido.
- **Cada dado mostrado indica a fonte e a data**, e só se mostra o que passou na prova real.
- **Nenhum julgamento jurídico.** O projeto descreve valores, não interpreta leis.
- **O histórico é padronizado.** As mensagens de commit seguem sempre o mesmo formato, descrito em [AGENTS.md](AGENTS.md), para o histórico poder ser lido como um diário do projeto.

Documentos (índice completo em [docs/README.md](docs/README.md)):

- [docs/escopo.md](docs/escopo.md): telas, versões, regras de exibição e ordem de construção.
- [docs/decisoes.md](docs/decisoes.md): cada decisão do projeto com o seu motivo.
- [docs/fontes-de-dados.md](docs/fontes-de-dados.md): o que cada fonte entrega, a qualidade e os termos de uso.
- [docs/verificacoes.md](docs/verificacoes.md): resultado de cada conferência entre bases do Senado.
- [design/](design/): protótipo da página do senador e identidade visual (abra os `.html` no navegador).

---

## Roadmap

| Versão | O que entra |
|---|---|
| **Primeiros passos** (feito) | Baixar os dados, medir o tamanho real, conferir colunas, formatos e a prova real; definir escopo e protótipo |
| **MVP (versão 1)** | Perfil do senador, verba por categoria e mês, principais fornecedores (de 2009 em diante), número de pessoas na equipe, moradia mês a mês, salário (quando comprovado), ranking e comparação entre os senadores em exercício, destaque do maior mês e a página de verificações |
| **Versão 2** | Atuação parlamentar (votações, projetos, comissões), histórico desde 2008 e, se fizer sentido, um modelo de anomalias |
| **Versão 3 (talvez)** | Dados de outras fontes públicas, como o TSE. Aumenta muito o escopo e a responsabilidade |

Este roadmap é uma intenção, não uma promessa, e será revisado conforme os dados reais mostrarem o que é possível.

## Como rodar

*Em breve.* O projeto ainda não tem código. Para ver o protótipo, abra `design/perfil-do-senador.html` no navegador.

## Licença e citação dos dados

**Dados:** pertencem ao Senado Federal, que os disponibiliza para livre uso exigindo, no máximo, a citação da fonte. O Senadados cita a fonte e a data de atualização em cada página.

**Código:** licença ainda não escolhida. A escolha será registrada em [docs/decisoes.md](docs/decisoes.md).
