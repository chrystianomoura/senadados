# Fontes de dados

Registro do que cada fonte entrega, como foi verificado e quais são as limitações. Tudo aqui foi conferido em **11 e 12/11/2026**, a menos que esteja marcado como *não verificado*. Quando uma fonte mudar, este arquivo deve mudar junto.

## Resumo

- Todas as fontes são do **Senado Federal** e são públicas, **sem login, chave ou cadastro**.
- A **API é a fonte principal**; os CSVs servem para conferência (veja [decisão D005](decisoes.md#d005-api-como-fonte-principal-csv-para-conferência)).
- Os dados vão de **2008 a 2026**. O ano de 2026 está incompleto.
- **Escopo de pessoas:** só os **senadores em exercício** ([D026](decisoes.md#d026-só-senadores-em-exercício)). Dados de ex-senadores **não entram no site**.
- **Regra de qualidade:** só se mostra o que passa na prova real ([D025](decisoes.md#d025-só-o-comprovado-a-prova-real)). As conferências feitas estão em [verificacoes.md](verificacoes.md).
- **Sem camada jurídica** ([D024](decisoes.md#d024-sem-camada-jurídica)): este documento descreve dados, não regras. Limites legais, normas e tabelas de valores por estado foram descartados do escopo.

## Fontes verificadas

### 1. Despesas da cota parlamentar (CEAPS)

CEAPS é a *Cota para o Exercício da Atividade Parlamentar dos Senadores*: a verba que o Senado reembolsa a cada senador por gastos do mandato.

| Formato | Endereço | Observação |
|---|---|---|
| CSV anual | `https://www.senado.leg.br/transparencia/LAI/verba/despesa_ceaps_AAAA.csv` | Existe de 2008 a 2026. O endereço antigo `senado.gov.br` só redireciona |
| API (JSON) | `https://adm.senado.gov.br/adm-dadosabertos/api/v1/senadores/despesas_ceaps/{ano}` | Traz o código do senador e o tipo de documento. Há também a versão `/csv` |

**Colunas do CSV** (11, iguais nos anos testados):
`ANO`, `MES`, `SENADOR`, `TIPO_DESPESA`, `CNPJ_CPF`, `FORNECEDOR`, `DOCUMENTO`, `DATA`, `DETALHAMENTO`, `VALOR_REEMBOLSADO`, `COD_DOCUMENTO`.

**Campos da API:** `id`, `tipoDocumento`, `ano`, `mes`, `codSenador`, `nomeSenador`, `tipoDespesa`, `cpfCnpj`, `fornecedor`, `documento`, `data`, `detalhamento`, `valorReembolsado`.

**Formato do CSV**
- Codificação **Latin-1** (não UTF-8).
- Separador `;` e textos entre aspas.
- A **primeira linha** é um aviso (`"ULTIMA ATUALIZACAO";"data"`), e o cabeçalho real vem na segunda.
- Números com **vírgula decimal** (`583,58`), mas às vezes sem vírgula (`3800`).
- Datas no formato `dd/mm/aaaa`. Na API, `aaaa-mm-dd`.

### 2. Perfil dos senadores em exercício

| Fonte | Endereço | O que traz |
|---|---|---|
| API administrativa | `https://adm.senado.gov.br/adm-dadosabertos/api/v1/senadores` | Código, nome, UF, partido, titular ou suplente, mandato, contato, chefe de gabinete (81 senadores) |
| API legislativa | `https://legis.senado.leg.br/dadosabertos/senador/lista/atual` | Nome completo, sexo, foto oficial, bloco, partido, UF |

Os dois usam o **mesmo código de parlamentar**, que é a chave para ligar tudo. As listas cobrem os senadores **em exercício**. 

### 3. Resumo de recursos, benefícios, folha e servidores

Todos na base `https://adm.senado.gov.br/adm-dadosabertos/api/v1`. Respondem sem chave; o que foi medido de cada um está em [verificacoes.md](verificacoes.md).

| Dado | Endereço | Uso no MVP |
|---|---|---|
| Resumo de recursos por senador | `/senadores/{codigo}/recursos-utilizados` (aceita `?ano=`) | Cota por categoria, benefícios e número de pessoas na equipe |
| Auxílio-moradia e imóvel funcional | `/senadores/auxilio-moradia-imoveis-funcionais` | Só como conferência (a página mensal do senador é o canal principal) |
| Folha de pagamento por mês | `/servidores/remuneracoes/{ano}/{mes}` (~5 MB por mês) | Salário, quando a ligação por nome completo é comprovada |
| Servidores ativos | `/servidores/servidores/ativos` | Só conferência da contagem de equipe (nunca nomes) |
| Escritórios de apoio | `/senadores/escritorios-apoio` | Fora do MVP |
| Votações, autorias, comissões etc. | `legis.senado.leg.br/dadosabertos/senador/{codigo}/...` | Versão 2 |

## Achados com a API completa (2008 a 2026)

Baixei a API de despesas de **todos os anos** (174 MB em JSON, fora do git). Os números abaixo valem para os 19 anos inteiros. (Uma primeira amostra pequena e enviesada errou alguns percentuais; lição: **não tirar conclusões de amostra enviesada**.)

**Em números**
- **398.624 registros** e cerca de **R$ 450 milhões** reembolsados entre 2008 e 2026 (2026 incompleto).
- 31.658 documentos de fornecedor distintos.
- Nenhum `id` repetido e nenhum registro sem `codSenador`.
- Colocados em um SQLite com dois índices, ocuparam cerca de 126 MB. No PostgreSQL deve ser parecido, talvez maior (*estimativa, não medida*).

| Ano | Registros | CNPJ/CPF e data preenchidos | `detalhamento` preenchido | Valores negativos |
|---|---|---|---|---|
| 2008 | 2.449 | **0%** | 0% | 0% |
| 2009 | 16.480 | 95,8% | 0% | 0% |
| 2010 | 18.235 | 100% | 0% | 0% |
| 2011 | 25.574 | 100% | 19,8% | 0% |
| 2012 | 30.175 | 100% | 25,7% | 0% |
| 2013 | 29.376 | 100% | 82,2% | 0% |
| 2014 | 22.002 | 100% | 99,9% | 0% |
| 2015 | 26.055 | 100% | 84,4% | 0% |
| 2016 | 26.768 | 100% | 79,8% | 0% |
| 2017 | 27.023 | 100% | 77,2% | 0% |
| 2018 | 24.492 | 100% | 77,1% | 0% |
| 2019 | 21.634 | 100% | 60,5% | 0% |
| 2020 | 14.088 | 100% | 51,3% | 0% |
| 2021 | 16.827 | 100% | 54,7% | 0% |
| 2022 | 16.804 | 100% | 53,9% | 0% |
| 2023 | 18.822 | 100% | 44,9% | 0,37% |
| 2024 | 21.449 | 100% | 40,1% | 0,35% |
| 2025 | 23.866 | 100% | 38,9% | 0,54% |
| 2026 | 16.505 | 100% | 34,8% | 0,18% |

**O que isso significa**
1. **Fornecedor existe a partir de 2009** (95,8% em 2009 e 100% depois). Só 2008 não tem CNPJ/CPF nem data da nota. O risco anterior era menor do que parecia.
2. **A descrição (`detalhamento`) é útil só em parte e vem caindo.** Passa de 80% entre 2013 e 2018, mas está em cerca de 35 a 40% nos anos recentes, justamente os que mais interessam ao cidadão. Isso reforça que o modelo principal não pode depender de texto (veja [D006](decisoes.md#d006-modelo-de-anomalias)).
3. **Valores negativos só existem de 2023 em diante** e são raros (menos de 0,6%). Provavelmente são estornos, o que não foi confirmado.
4. **As categorias são estáveis.** Há 7 textos de categoria em todos os anos: cinco existem desde 2008, e "Passagens aéreas, aquáticas e terrestres nacionais" e "Serviços de Segurança Privada" entram em 2011. O texto das categorias não muda. Entre 2023 e 2026, 344 registros vêm sem categoria.
5. **Pessoas físicas são minoria:** 1,3% a 3,1% dos registros e 3,1% a 12,3% do valor, e a fatia vem caindo (3,5% do valor em 2024 e 2026). Mostrar só o agrupamento de pessoas físicas ([D008](decisoes.md#d008-pessoas-físicas-agrupadas-e-cpf-nunca-exibido)) esconde pouco.
6. **Concentração moderada:** os 10 maiores fornecedores (empresas) ficam com cerca de 20% do valor nos anos recentes (o cálculo usa o CNPJ completo, então filiais da mesma empresa contam separadas).
7. **Tipos de documento:** Nota Fiscal Eletrônica, Nota Fiscal, Cupom Fiscal, Passagem, Fatura, Recibo e outros; 3.144 registros sem tipo.
8. **Senadores distintos por ano (códigos):** de 83 a 127, o que inclui suplentes que assumiram.

### CPF: a API já mascara, o CSV não

Na API, o CPF de pessoa física vem mascarado (padrão `123.***.***-45`). No CSV, vem completo (44 de 1.692 linhas nos primeiros registros de 2024). Isso reforça a escolha da API como fonte principal ([D005](decisoes.md#d005-api-como-fonte-principal-csv-para-conferência)): o pipeline nunca recebe o CPF inteiro.

Há também uns 60 registros recentes com o documento em formato fora do padrão (12 ou 13 dígitos, sem pontuação), que não são nem CNPJ nem CPF. Precisam de tratamento à parte.

## Quem está no escopo (senadores em exercício)

- **81** em exercício em 12/11/2026: 70 titulares e 11 suplentes ([D026](decisoes.md#d026-só-senadores-em-exercício)).
- Eles têm **153.901 dos 398.624 registros** (39%) e **47% do valor** do histórico de 2008 a 2026.
- **79 de 81** têm despesa registrada. O primeiro ano de despesa de 33 deles é 2019, e o de 20 é 2023. Só 5 vêm de 2008.
- **54 dos 81 mandatos terminam em 2027.** Quando um senador sai, ele e os dados dele saem do site.
- Os códigos de parlamentar das legislaturas 53 a 57 (681 pessoas) cobrem os 331 códigos das despesas, mas essas listas trazem só nome e sexo; **partido e UF existem só para os 81 em exercício**.

## Sujeira encontrada nos dados

- Valor sem vírgula decimal misturado com valor com vírgula.
- Ano `0204` em uma data (erro de digitação).
- Notas de 2023 e 2025 dentro do arquivo de 2024 (CSV). O campo `ANO` é a competência do reembolso, não a data do gasto.
- Valores negativos (provavelmente estornos).
- **CPF de pessoas físicas** aparecem completos no CSV (na API vêm mascarados). Veja [D008](decisoes.md#d008-pessoas-físicas-agrupadas-e-cpf-nunca-exibido).

## Termos de uso

Lido em 11/11/2026 nas páginas de dados abertos, na política de uso do portal e no Plano de Dados Abertos 2026–2028.

**O que diz**
- Dados abertos são disponibilizados "sob licença que permita livre uso por qualquer pessoa", exigindo-se "no máximo, citar sua proveniência".
- A política de uso do portal permite usar o conteúdo "desde que seja citada a fonte e para fins lícitos", e afirma que o conteúdo é de propriedade autoral do Senado Federal.

**O que não diz**
- Não nomeia a licença (Creative Commons, ODbL ou outra).
- Não define formato de citação.
- Não menciona uso comercial, redistribuição, limite de requisições nem LGPD nos dados abertos.
- Não cita a CEAPS nem as APIs usadas aqui.

Do Plano de Dados Abertos (33 páginas), busquei palavras-chave de licença e citação; **não li o documento inteiro**.

**Como o projeto cumpre:** cita a fonte e a data de atualização em cada página e no rodapé (veja [D009](decisoes.md#d009-citação-da-fonte-em-toda-página)).

## Nomes das categorias de despesa
O site usa nomes curtos, derivados do nome oficial, para o cidadão ler sem esforço. O nome completo fica na página do senador no Senado, e "De onde vem este número" avisa isso. **Se o Senado criar uma categoria nova, o site mostra o nome oficial até existir um nome curto.**

| Nome oficial no Senado | Nome curto no site |
|---|---|
| Locomoção, hospedagem, alimentação, combustíveis e lubrificantes | Locomoção, hospedagem e alimentação |
| Contratação de consultorias, assessorias, pesquisas, trabalhos técnicos e outros serviços de apoio ao exercício do mandato parlamentar | Consultorias e serviços de apoio ao mandato |
| Divulgação da atividade parlamentar | Divulgação da atividade parlamentar |
| Aluguel de imóveis para escritório político, compreendendo despesas concernentes a eles. | Aluguel do escritório político |
| Passagens aéreas, aquáticas e terrestres nacionais | Passagens dentro do Brasil |
| Aquisição de material de consumo para uso no escritório político, inclusive aquisição ou locação de software, despesas postais, aquisição de publicações, locação de móveis e de equipamentos. | Material de consumo do escritório político |
| Serviços de Segurança Privada | Segurança privada |
| *(sem categoria)* | Sem categoria |

## Fora do MVP (registrado para não se perder)

Medido em 11/11/2026 e **fora do site** pela regra de escopo (D026) ou por ficar para a versão 2 (D019):

- **Atuação parlamentar** (votações, autorias, relatorias, discursos, apartes): existe por senador em `legis.senado.leg.br/dadosabertos/senador/{código}/...`. Os votos usam códigos como `P-NRV`, `AP`, `MIS` e `LS` cujo significado **não foi verificado**; sem isso não dá para falar de presença. Os dados pesados de 81 senadores seriam centenas de MB (estimativa), grandes demais para guardar crus no banco gratuito.
- **Profissão e formação** estão preenchidas para só 31 e 34 dos 81; **comissões e licenças** vêm em listas históricas muito longas. Nenhum entra no MVP.
- **Partido ao longo do tempo** (filiações e mandatos) existe e daria o partido de cada ano, mas só importa para a versão 2.
- **Gastos fora da cota:** veja [verificações](verificacoes.md#fora-do-mvp-registrado-para-não-se-perder).
- **Escritórios de apoio:** 81 na lista, em 75 senadores; fora do MVP ([D031](decisoes.md#d031-onde-fica-o-gabinete-endereço-entra-telefone-e-mail-e-escritório-de-apoio-ficam-fora)).
- A API converte XML em JSON, e itens únicos podem vir como objeto em vez de lista; o pipeline precisa tratar os dois casos.

## Como conferimos

Os resultados das comparações entre bases, com o que bate, o que divergiu e o que ficou pendente, estão em [verificacoes.md](verificacoes.md).


## Como reproduzir

Os arquivos baixados ficam em `data/raw/`, que não vai para o git (veja [data/README.md](../data/README.md)). Exemplo, despesas de um ano pela API (fonte principal) e pelo CSV (conferência):

```bash
curl -s -o api_2024.json "https://adm.senado.gov.br/adm-dadosabertos/api/v1/senadores/despesas_ceaps/2024"
curl -s -o ceaps_2024.csv "https://www.senado.leg.br/transparencia/LAI/verba/despesa_ceaps_2024.csv"
```

O código que baixa e confere tudo de forma repetível (pipeline) ainda não existe; é o próximo passo ([escopo.md](escopo.md), ordem de construção).
