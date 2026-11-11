# Fontes de dados

Registro do que cada fonte entrega, como foi verificado e quais são as limitações. Tudo aqui foi conferido em **11/11/2026**, a menos que esteja marcado como *não verificado*. Quando uma fonte mudar, este arquivo deve mudar junto.

## Resumo

- Todas as fontes são do **Senado Federal** e são públicas, **sem login, chave ou cadastro**.
- A **API é a fonte principal**; os CSVs servem para conferência (veja [decisão D005](decisoes.md#d005-api-como-fonte-principal-csv-para-conferência)).
- Os dados vão de **2008 a 2026**. O ano de 2026 está incompleto.

## Fontes verificadas

### 1. Despesas da cota parlamentar (CEAPS)

CEAPS é a *Cota para o Exercício da Atividade Parlamentar dos Senadores*: a verba que o Senado reembolsa a cada senador por gastos do mandato.

| Formato | Endereço | Observação |
|---|---|---|
| CSV anual | `https://www.senado.leg.br/transparencia/LAI/verba/despesa_ceaps_AAAA.csv` | Existe de 2008 a 2026. O endereço antigo `senado.gov.br` só redireciona |
| API (JSON) | `https://adm.senado.gov.br/adm-dadosabertos/api/v1/senadores/despesas_ceaps/{ano}` | Traz o código do senador e o tipo de documento. Há também a versão `/csv` |

**Colunas do CSV** (11, iguais em 2008, 2015 e 2024 nas amostras):
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

Os dois usam o **mesmo código de parlamentar**, que é a chave para ligar tudo. As listas cobrem os senadores **em exercício**. Para ex-senadores das despesas antigas, o endpoint histórico ainda *não foi verificado*.

### 3. Outras fontes (existem; conteúdo ainda não analisado)

Os endpoints abaixo responderam com sucesso, mas **não li o conteúdo de cada um**:

| Dado | Endereço (base `adm-dadosabertos/api/v1`) | Uso previsto |
|---|---|---|
| Resumo de recursos por senador | `/senadores/{codigo}/recursos-utilizados` | Cota, gastos fora da cota, benefícios e equipe (MVP) |
| Auxílio-moradia e imóvel funcional | `/senadores/auxilio-moradia-imoveis-funcionais` | MVP |
| Escritórios de apoio | `/senadores/escritorios-apoio` | Versão 2 |
| Lotação e servidores ativos | `/servidores/servidores/ativos` | Contar a equipe de cada gabinete (só agregados) |
| Folha de pagamento por mês | `/servidores/remuneracoes/{ano}/{mes}` | Salário do senador (~5 MB por mês) |
| Votações, autorias, comissões, discursos etc. | `legis.senado.leg.br/dadosabertos/senador/{codigo}/...` | Versão 2 |

**Salário:** na folha de setembro de 2026, o senador Alan Rick aparece com remuneração básica de R$ 46.366,19 e líquido de R$ 29.048,49. Só conferi **um** senador. A folha não usa o código do parlamentar, então a ligação é pelo nome completo (cuidado com homônimos).

**Equipe do gabinete:** para o mesmo senador, o resumo oficial indica 17 pessoas no gabinete e 20 no escritório de apoio, e a lista de servidores indica 18 e 20. A diferença de uma pessoa **não foi explicada**.

## Achados com a API completa (2008 a 2026)

Baixei a API de despesas de **todos os anos** (174 MB em JSON, fora do git). Os números abaixo valem para os 19 anos inteiros e **substituem** os percentuais da primeira amostra, que era enviesada (veja mais abaixo).

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

Na API, o CPF de pessoa física vem mascarado (padrão `123.***.***-45`). No CSV, vem completo (44 de 1.692 linhas na amostra de 2024). Isso reforça a escolha da API como fonte principal ([D005](decisoes.md#d005-api-como-fonte-principal-csv-para-conferência)): o pipeline nunca recebe o CPF inteiro.

Há também uns 60 registros recentes com o documento em formato fora do padrão (12 ou 13 dígitos, sem pontuação), que não são nem CNPJ nem CPF. Precisam de tratamento à parte.

## Primeira amostra (histórico)

Antes de baixar tudo, usei uma amostra pequena em `data/raw/`: CSV de 2008 inteiro e o começo dos CSVs de 2015 e 2024 (cerca de 400 KB cada, com 6 e 9 senadores, os primeiros em ordem alfabética). Ela **errou** em alguns números porque era enviesada: indicou 99% de descrição em 2015 (real: 84,4%) e 30% em 2024 (real: 40,1%). Fica registrada como lição: **não tirar conclusões de amostra enviesada**.

### Comparação CSV × API (2008)

- As duas fontes têm as **mesmas 2.449 linhas**, e todo `COD_DOCUMENTO` do CSV tem par na API.
- **8 linhas** têm valor diferente, sempre menor na API (por exemplo R$ 11.100,36 no CSV contra R$ 8.000,18 na API). A soma total difere em R$ 9.791,93 (cerca de 0,08%).
- Hipótese *não confirmada*: correções feitas depois de 2021.

## Qualidade dos dados: sujeira encontrada

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

## Pendências

- Entender os 344 registros sem categoria e os ~60 documentos em formato fora do padrão.
- Confirmar o que são os valores negativos (estornos?) e a diferença de 8 valores entre CSV e API em 2008.
- Confirmar o endpoint de ex-senadores.
- Entender a diferença de contagem da equipe do gabinete.
- Confirmar com o Senado o nome da licença (opcional).
- Ler o Plano de Dados Abertos por inteiro.

## Como reproduzir os achados

```bash
curl -s -o ceaps_2008.csv "https://www.senado.leg.br/transparencia/LAI/verba/despesa_ceaps_2008.csv"
curl -s -o api_2008.json  "https://adm.senado.gov.br/adm-dadosabertos/api/v1/senadores/despesas_ceaps/2008"
```

Os arquivos baixados ficam em `data/raw/`, que não vai para o git.
