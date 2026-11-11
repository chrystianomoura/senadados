# Senadados

> Os gastos dos senadores, explicados para qualquer pessoa.

**Status:** em planejamento (dia 1, 11/11/2026). Ainda não existe código. Este documento descreve o que o projeto **vai ser** e, por isso, **vai mudar** conforme aprendermos mais. Cada mudança relevante é registrada com o motivo (veja [Como este projeto é documentado](#como-este-projeto-é-documentado)).

---

## O que é o Senadados?

O Senado Federal publica, na internet, quanto cada senador gasta e quem recebe esse dinheiro. Só que esses dados chegam como planilhas enormes, com milhares de linhas, nomes de colunas técnicos e valores misturados. Na prática, quase ninguém consegue ler.

O **Senadados** pega esses dados oficiais, limpa, organiza e mostra de um jeito que qualquer cidadão entende, sem precisar saber o que é um CSV, uma API ou uma planilha.

Pense assim: o Senado entrega uma pilha de notas fiscais. O Senadados arruma essa pilha, calcula os totais e conta a história em poucos gráficos e frases.

## Para que serve?

Para responder, em segundos, perguntas simples sobre cada senador:

| Pergunta | O que o site mostra |
|---|---|
| **Quem é?** | Foto, partido, estado, mandato |
| **Quanto ganha?** | Salário bruto e líquido |
| **Quanto gasta?** | Total da verba usada no ano, por categoria |
| **Para onde vai o dinheiro?** | Os fornecedores que mais recebem |
| **Quem trabalha com ele?** | Quantas pessoas há no gabinete e quanto custa a equipe |
| **O que faz no mandato?** | Votações, projetos e comissões (numa versão futura) |
| **Algo saiu do normal?** | Meses em que o gasto fugiu do padrão daquele senador |

## Qual é o objetivo?

1. **Transparência que se entende.** Dado aberto que ninguém consegue ler não ajuda ninguém. O objetivo é fazer o dado ser compreendido, não só publicado.
2. **Mostrar o que importa, sem ruído.** Poucos números em destaque, comparações claras, detalhes só para quem quiser clicar.
3. **Funcionar para qualquer pessoa**, inclusive no celular, sem cadastro e sem custo.
4. **Ser um projeto de portfólio bem feito**, onde cada decisão técnica tem um motivo escrito e verificável.

## O que o Senadados **não** é

- **Não é um acusador.** O sistema aponta o que é *incomum*, não o que é *irregular*. Um gasto alto pode ser uma viagem legítima. Nada aqui afirma que alguém fez algo errado.
- **Não é uma fonte oficial.** É uma leitura independente de dados oficiais. Cada informação mostra de onde veio e quando foi atualizada.
- **Não mostra o gasto total do senador.** Os dados cobrem principalmente a verba reembolsada (a chamada cota parlamentar), mais alguns itens complementares. O site precisa deixar claro o que está dentro e o que está fora.
- **Não expõe pessoas comuns.** A equipe do gabinete aparece só em números (quantidade, custo). Nomes de assessores não são exibidos.

---

## De onde vêm os dados?

Todos vêm do **próprio Senado Federal**, são públicos e **não exigem login nem chave de acesso**. Conferi isso em 11/11/2026.

| Fonte | O que traz |
|---|---|
| Arquivos de despesas da cota (CEAPS), de 2008 a 2026 | Cada nota fiscal reembolsada: senador, categoria, fornecedor, valor, data |
| API de dados abertos administrativos do Senado | Despesas, perfil dos senadores, equipe dos gabinetes, escritórios de apoio, auxílio-moradia, folha de pagamento |
| API de dados abertos legislativos do Senado | Foto, nome completo, partido, votações, projetos, comissões |

**Limitações conhecidas**
- Os dados de 2026 estão incompletos, porque o ano ainda está em andamento.
- Os arquivos têm sujeira (formatos de número misturados, datas fora do ano, valores negativos que parecem estornos). Parte do trabalho do projeto é tratar isso.
- O Senado pode corrigir dados antigos. Rodar o projeto hoje e daqui a seis meses pode dar valores ligeiramente diferentes.
- Os anos antigos têm menos informação: na amostra de 2008, **nenhuma despesa traz o CNPJ/CPF do fornecedor nem a data da nota**. Ainda falta descobrir a partir de que ano isso existe.
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
          ├──► 4. ANALISAR → um modelo aponta meses fora do padrão
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

### scikit-learn (Isolation Forest): o modelo que aponta o incomum
**Em uma frase:** aprende o que é "normal" para cada senador e destaca o que foge disso.
**Por quê:** os dados quase não têm texto livre, então classificar descrições não funciona. Comparar cada mês com o histórico do próprio senador é mais justo e mais fácil de explicar. Cada alerta mostra o motivo, por exemplo: "gasto 3 vezes acima da média dele em passagens".
**Cuidado:** "fora do padrão" **não** significa "irregular".

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

- **Toda decisão tem um porquê escrito.** Escolha de tecnologia, regra de limpeza, critério do modelo: nada entra sem justificativa.
- **A documentação muda junto com o código.** Se o código muda e o texto não, o trabalho não está terminado.
- **Dúvidas e limitações ficam visíveis.** O que não foi verificado é dito como "não verificado", não escondido.
- **Cada dado mostrado indica a fonte e a data.**
- **O histórico é padronizado.** As mensagens de commit seguem sempre o mesmo formato, descrito em [AGENTS.md](AGENTS.md), para o histórico poder ser lido como um diário do projeto.

Documentos:

- [docs/fontes-de-dados.md](docs/fontes-de-dados.md): o que cada fonte entrega, o que a amostra mostrou e os termos de uso.
- [docs/decisoes.md](docs/decisoes.md): cada decisão do projeto com o seu motivo.
- `docs/escopo.md` (telas e versões): ainda a criar.

---

## Roadmap

| Versão | O que entra |
|---|---|
| **Primeiros passos** | Baixar amostras, medir o tamanho real dos dados, conferir colunas e formatos |
| **MVP (versão 1)** | Perfil do senador, salário, despesas por categoria e mês, principais fornecedores, tamanho do gabinete, ranking e comparação, alertas do modelo |
| **Versão 2** | Atuação parlamentar (votações, projetos, comissões) e histórico desde 2008 |
| **Versão 3 (talvez)** | Dados de outras fontes públicas, como o TSE. Aumenta muito o escopo e a responsabilidade |

Este roadmap é uma intenção, não uma promessa, e será revisado conforme os dados reais mostrarem o que é possível.

## Como rodar

*Em breve.* O projeto ainda não tem código.

## Licença e citação dos dados

**Dados:** pertencem ao Senado Federal, que os disponibiliza para livre uso exigindo, no máximo, a citação da fonte. O Senadados cita a fonte e a data de atualização em cada página.

**Código:** licença ainda não escolhida. A escolha será registrada em [docs/decisoes.md](docs/decisoes.md).
