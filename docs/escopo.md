# Escopo

O que o Senadados vai entregar, tela por tela, e em que ordem. Este documento se baseia nos dados **medidos** (veja [fontes-de-dados.md](fontes-de-dados.md)) e nas decisões já tomadas (veja [decisoes.md](decisoes.md)). Onde algo ainda não foi verificado, está escrito.

**Status:** revisado em 11/11/2026. Muda conforme o projeto avançar; cada mudança relevante vira uma decisão registrada.

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
10. **Tudo ou nada:** um dado que compara senadores só aparece se todos os senadores em exercício o tiverem e se os dados baterem para todos. **Exceção:** dados de contato (telefone, e-mail) aparecem para quem os tem.

## 2. Quem usa

| Pessoa | O que quer | O que o site precisa ter |
|---|---|---|
| **Cidadão curioso** | Saber como o senador do seu estado usa os recursos | Busca simples, perfil claro, frases em vez de tabelas |
| **Jornalista ou pesquisador** | Dados confiáveis, citáveis e comparáveis | Fonte e data visíveis, relatório de verificações, API aberta |
| **Quem avalia o projeto** (portfólio) | Decisões técnicas justificadas | Repositório documentado, API documentada, README claro |

## 3. Quem entra no site

Só os **senadores em exercício**, definidos todo dia pela lista oficial do Senado ([D026](decisoes.md#d026-só-senadores-em-exercício)).

- **Hoje:** 81 (70 titulares e 11 suplentes).
- **Quando entra:** assim que aparece na lista. A página mostra "sem dados ainda" até haver dados.
- **Quando sai:** deixa o site e a API no dia em que sai da lista. Em fevereiro de 2027, 54 mandatos terminam, então até 54 páginas podem sair de uma vez, dependendo de quem for reeleito.
- **Histórico:** o de cada senador em exercício vai de 2008 até hoje.
- **Fora:** ex-senadores, aposentados e pensionistas.
- **Regra de agregado:** nenhum total, mediana ou ranking é apresentado como "do Senado". Toda comparação diz "entre os senadores em exercício em [data]".

## 4. Telas do MVP

### 4.1 Início
- Busca por nome, com filtro por estado e partido.
- Uma frase sobre o que são os dados e de onde vêm.
- Destaques simples, sempre com a referência "entre os senadores em exercício".
- Links para "Sobre os dados" e "Verificações".

### 4.2 Perfil do senador (a tela principal)
Cada senador tem endereço próprio (por exemplo, `/senador/nome`). A página **abre com um resumo de seis cartões** (salário, verba, posição entre os senadores, maior mês, equipe e moradia) e depois traz perguntas que se abrem.

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
| **Quem é** | Foto oficial com crédito, partido, estado, mandato, titular ou suplente. | Pronto para provar |
| **Salário** | Remuneração do último mês da folha | Só onde a ligação com o senador for inequívoca |
| **Verba (a cota)** | Total do ano e do mês, mês a mês, por categoria, e a posição entre os outros senadores em três faixas | Provado em 2026 (72 de 79 idênticos, 7 explicados) |
| **Para onde vai** | Maiores fornecedores (empresas) e "pessoas físicas" agrupadas ([D008](decisoes.md#d008-pessoas-físicas-agrupadas-e-cpf-nunca-exibido)) | A partir de 2009 |
| **Gabinete: onde fica, contato e equipe** | **Onde fica** (endereço), **como falar** (telefones completos, um por linha, e e-mail, só para quem tem) e o número de pessoas, do resumo oficial. **Sem custo estimado** ([D031](decisoes.md#d031-onde-fica-o-gabinete-endereço-entra-telefone-e-mail-e-escritório-de-apoio-ficam-fora)) | Endereço, telefone e e-mail provados; número de pessoas a provar por gabinete |
| **Moradia** | Uso de imóvel funcional e de auxílio-moradia **mês a mês** | 9 de 12 divergências explicadas; 3 pendentes |
| **Maior mês** | O mês de maior valor da verba, destacado no gráfico mês a mês. Só o fato, sem julgamento ([D030](decisoes.md#d030-destaque-do-maior-mês-no-lugar-do-alerta-fora-do-padrão)) | Sai da mesma conta do gráfico |

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
- A lista de checagens feitas e o resultado de cada uma, por exemplo "cota de 2026: 72 de 79 idênticos, 7 explicados".
- As divergências encontradas nos dados do Senado, **agregadas e sem nomes**, com a explicação quando existe.
- A frase fixa: "verificamos se as bases do Senado concordam entre si. Não auditamos os dados."
- Canal para **reportar um erro** e registro público das correções.

## 5. De onde vem cada informação

| Informação | Fonte | Verificação |
|---|---|---|
| Despesas da cota | API de despesas do Senado (2008 a 2026), com o CSV e a página de cada senador como conferência | 2026 verificado contra o resumo; outros anos a verificar |
| Perfil e foto | APIs administrativa e legislativa | Pronto |
| Salário | Folha de pagamento mensal | Ligação por nome; só os casos inequívocos |
| Equipe | Resumo oficial por senador | A provar por gabinete |
| Moradia | Página mensal de benefícios | 9 de 12 explicados |
| Escritórios de apoio | API administrativa | A verificar |

## 6. Regras de exibição

1. **Ano em andamento:** 2026 mostra "dados parciais, até [mês]".
2. **Anos sem fornecedor:** o bloco "Para onde vai" começa em **2009**. Em 2008 o site explica que o dado não existe.
3. **Pessoas físicas:** nunca com nome nem CPF; sempre agrupadas ([D008](decisoes.md#d008-pessoas-físicas-agrupadas-e-cpf-nunca-exibido)).
4. **Equipe:** só números, nunca nomes ([D007](decisoes.md#d007-equipe-do-gabinete-só-em-números)).
5. **Linhas sem categoria:** aparecem como "Sem categoria". O total da verba inclui essas linhas, e o site explica que o resumo do Senado não as conta (60 linhas, R$ 164.450,50 em 2026).
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

- **O que faz:** no gráfico mês a mês da verba, destaca o mês de maior valor: "Maior mês: março, R$ 43 mil".
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
| Moradia: 3 casos sem prova | Explicação plausível (a lista é de novembro; a página mensal vai até outubro), não provada | Reconferir no mês seguinte |
| Salário | 3 suplentes sem correspondência na folha; um titular com valor diferente | Provar a ligação ou deixar sem salário |
| Equipe | Diferença de 1 pessoa entre o resumo e a lista; um gabinete com 70 pessoas | Provar por gabinete |
| Cota de outros anos | Só 2026 foi cruzada com o resumo; CSV de 2008 difere em 8 valores | Rodar a prova real ano a ano |
| Linhas sem categoria | O Senado não explica por que o resumo as deixa de fora | Perguntar pelo canal oficial; mostrar com a explicação |
| Internet Archive | Acusa cópia, mas não consegui listar | Testar de novo |
| Virada de 2027 | Até 54 páginas saem de uma vez | Decidido: apagar os dados de quem sair (banco, arquivos brutos, site e API) |
| Pessoas físicas ([D008](decisoes.md#d008-pessoas-físicas-agrupadas-e-cpf-nunca-exibido)) | Proteções mantidas; risco de LGPD aceito pelo mantenedor, por serem dados públicos | Nenhuma ação |
| Limites dos planos gratuitos | Fontes secundárias | Reconfirmar antes de publicar |
| Foto dos senadores | Conteúdo "de propriedade autoral do Senado" | Carregar do endereço oficial com crédito |

## 13. Ordem de construção

1. Pipeline de despesas, com validação e testes.
2. **Camada de verificação** (cruzamentos, relatório, falha fechada).
3. Banco e carga completa dos senadores em exercício.
4. Perfil, salário (quando provado), equipe e moradia.
5. API.
6. Site: perfil, depois início, ranking, comparação, "Sobre os dados" e "Verificações".
7. Destaque do maior mês.
8. Automação diária e publicação.
9. Revisão final da documentação.

Cada etapa termina com a documentação atualizada e um commit no padrão do [AGENTS.md](../AGENTS.md).

## 14. Perguntas em aberto para o mantenedor

Nenhuma no momento.

*Resolvidas: apagar os dados de quem sair e dispensar a revisão jurídica sobre LGPD (11/11/2026); suplentes em exercício entram e o alerta vira o destaque do maior mês (12/11/2026).*
