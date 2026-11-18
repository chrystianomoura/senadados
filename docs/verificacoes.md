# Verificações (prova real)

Resultado de cada conferência feita entre as bases do Senado, com o método e a classificação (regra em [D025](decisoes.md#d025-só-o-comprovado-a-prova-real)). Feitas em **11 e 12/11/2026**.

**O que estas conferências provam:** que os números são **consistentes entre as bases do Senado**. Não são uma auditoria, e todas as bases vêm do mesmo sistema do Senado, então provam **consistência e origem**, não independência ([D027](decisoes.md#d027-como-conferir-os-dados)).

**Classificação:** *idêntico* (aparece), *divergência explicada* (aparece) ou *divergência sem explicação* (fica oculto, com o motivo registrado aqui).

## Canais usados

Todos gratuitos e **sem chave**.

| Canal | O que traz | Observação |
|---|---|---|
| API de despesas da cota (`despesas_ceaps/{ano}`) | Cada linha de despesa | Fonte principal |
| CSV de despesas | As mesmas linhas | Congelado desde 2021 nos anos antigos |
| API de recursos por senador (`recursos-utilizados?ano=`) | Cota por categoria, benefícios e pessoal | Testado em 2023, 2025 e 2026. A profundidade do histórico não foi testada |
| Página de transparência de cada senador (`.../transparencia/sen/{código}/?ano=`) | O mesmo conteúdo, 2023 a 2026 | Valores batem com a API (conferido em um senador). Indica a origem: "Sistema Cotas" |
| Exportação dessa página (CSV e JSON) | O mesmo conteúdo, em arquivo | O endereço existe; não baixei |
| Página mensal de benefícios (`.../beneficios/?numeroFuncional=&ano=`) | Auxílio-moradia e imóvel funcional mês a mês | Resolveu a divergência de moradia |
| Relatório de moradia do Senado | Quem recebe auxílio no **mês de emissão** | Não traz meses anteriores |

**Como o Senado descreve a moradia** (página de transparência): o auxílio-moradia é para quem "não ocupa apartamentos funcionais", "com a finalidade de cobrir despesas com aluguel ou diária de hotel". A página **não diz** que o imóvel fica em Brasília.

## Resultados

| # | Conferência | Resultado | Classificação |
|---|---|---|---|
| 1 | Cota por ano: despesas detalhadas × resumo, por categoria | 2010 a 2026: tudo bate (2026: 73 idênticos, 7 explicados); 2008 e 2009: 5 senadores sem explicação em cada | 2010 a 2026 aparecem; 2008 e 2009 ficam ocultos |
| 2 | Moradia: resumo anual × lista do mês | 9 de 12 explicados; 3 pendentes | 9 aparecem; 3 ficam sem informação |
| 3 | Gabinete e contato: API × página do senador | Endereço igual nos 81; telefone e e-mail com ressalvas | Veja abaixo |
| 4 | Salário: folha × senador | 78 de 81 ligados pelo nome | Os 3 sem ligação ficam sem salário |
| 5 | Equipe: resumo × lista de servidores, por gabinete e vínculo | 80 de 81 idênticos; 1 sem explicação (18/11/2026) | Aparece para 80; 1 gabinete oculto (D037) |
| 6 | CSV × API em 2008 | 8 valores diferentes em 2.449 linhas | Sem impacto no MVP |

### 1. Cota de 2026, despesas detalhadas contra o resumo do Senado

Somei as despesas de cada senador na API e comparei com o total que o próprio Senado publica no resumo.

**Refeita em 18/11/2026**, com despesas e resumo baixados no mesmo dia:

- **74 de 81 senadores batem no centavo.** Um deles é Jorge Kajuru, que não tem despesa e tem resumo zero.
- **7 divergem**, entre R$ 748,39 e R$ 35.000,00. Em todos, a diferença é **exatamente a soma das linhas sem categoria**: a API as inclui e o resumo não. Entre os senadores em exercício são **59 linhas, R$ 162.260,84** em 2026.
- **Classificação:** idêntico (74) e divergência explicada (7). **Nenhuma divergência sem explicação.** Por que o resumo deixa de fora as linhas sem categoria **só o Senado pode explicar**.

**Primeira medição (11/11/2026):** 72 de 79 idênticos e 7 explicados, com "60 linhas, R$ 164.450,50". Dois pontos dela estavam imprecisos: o número de linhas e o valor incluíam ex-senadores (hoje, na API inteira, são 62 linhas e R$ 171.450,50, em 9 senadores; só em exercício, 59 e R$ 162.260,84), e os arquivos tinham uma foto mais antiga dos dados.

**Por que os números mudaram entre 11/11 e 18/11:** o Senado continuou publicando. O resumo mudou para 59 senadores (+R$ 674.349,27 no total, e 5 totais diminuíram, o maior em R$ 13.347,28, causa não investigada). Leany Lemos, que tinha resumo zero em 11/11, passou a ter uma despesa de R$ 15.200 (competência de novembro). Os arquivos antigos de despesas foram sobrescritos sem cópia, então a comparação linha a linha não é possível; o "antes" é o resumo de 11/11, que ainda está em `data/raw/recursos/`.

**Lição:** conferir duas bases só faz sentido se as duas forem baixadas **na mesma foto dos dados** (mesmo dia). A verificação automática do pipeline deve baixar tudo junto e registrar a data.

#### Todos os anos, pela verificação automática (18/11/2026)

Agora é código (`pipeline/`, [D035](decisoes.md#d035-verificação-automática-da-cota-por-categoria-na-mesma-foto-dos-dados)), compara **por categoria** (as 7 do resumo), e só roda se coleta, limpeza e resumo forem do mesmo dia. Pares senador-ano sem valor nos dois lados (por exemplo, Jorge Kajuru, que não tem despesa nem resumo) não entram na conta.

| Anos | Idênticos | Explicados (só linhas sem categoria) | Sem explicação |
|---|---|---|---|
| 2008 | 0 | 0 | **5** |
| 2009 | 0 | 0 | **5** |
| 2010 a 2018 | 5 a 15 por ano | 0 | 0 |
| 2019 a 2022 | 50 a 53 por ano | 0 | 0 |
| 2023 | 62 | 12 | 0 |
| 2024 | 56 | 16 | 0 |
| 2025 | 67 | 6 | 0 |
| 2026 | 73 | 7 | 0 |

**2008 e 2009:** em 2008 o resumo do Senado vem **vazio** (valor zero) para os 5 senadores que já tinham despesa; em 2009 o resumo é **menor** que as despesas (por exemplo, R$ 129.049,97 contra R$ 156.517,14 num caso), e a diferença não é a das linhas sem categoria. Não sabemos o motivo (o resumo pode cobrir só parte do ano, mas isso **não foi confirmado**). Pela regra da D025, a cota desses dois anos **não aparece**.

### 2. Moradia, resumo anual contra lista do mês

O resumo diz que **12** senadores "utilizaram" auxílio-moradia em 2026. A lista do mês diz que **1** recebe. Cruzei os 12 casos com a página mensal de benefícios:

- **Nos 12**, o resumo anual **bate** com a página mensal (por exemplo, "Utilizou (em 10 meses)").
- **9 de 12** não usaram auxílio no último mês listado, o que combina com a lista (que olha só o mês de emissão).
- **3 de 12** usaram até outubro, e a lista, de novembro, diz que não. A diferença de um mês **pode** explicar, mas **não está provada**.
- **Conclusão:** as bases não se contradizem; medem períodos diferentes. **Classificação:** 9 explicados, 3 pendentes (ficam sem informação até serem provados).

### 3. Gabinete e contato, API contra a página de cada senador (12/11/2026)

Comparei endereço do gabinete, telefones e e-mail da API (`senadores`) com a seção "Dados pessoais" da página de cada um dos 81 senadores.

- **Endereço do gabinete:** igual nos **81**.
- **Telefones:** **66 iguais** e **15 em que a página traz números a mais** que a API (11 casos com 1 número a mais, 3 com 2, 1 com 3). A API nunca lista mais de 2 números (34 senadores com 1 e 47 com 2); a página lista até 4. O padrão sugere que a API corta em 2, mas **o Senado não confirma**. Não há número "quebrado": são linhas a mais.
- **Telefones abreviados:** a página escreve, por exemplo, "(61) 3303-6187 / 6188 / 6183". Expandindo o início do primeiro número para os seguintes, o resultado inclui **todos** os números da API nos 81 senadores. O fax não é usado.
- **E-mail:** **não há divergência.** A diferença que a primeira comparação mostrou era só uma quebra de linha no fim do e-mail na API. O que existe é **ausência**: **2 suplentes não têm e-mail** em nenhuma das duas fontes. Os outros 79 têm e-mail igual nos dois lados.
- **Escritório de apoio:** 75 senadores têm escritório na lista e 75 no resumo, mas só **74 coincidem**; fica fora ([D031](decisoes.md#d031-onde-fica-o-gabinete-endereço-entra-telefone-e-mail-e-escritório-de-apoio-ficam-fora)).
- **Decisão do mantenedor (12/11/2026):** entram endereço, telefone (da página do portal) e e-mail, **para quem os tem**; o escritório fica fora.

### 4. Salário

- Ligando a folha de setembro de 2026 ao senador pelo **nome completo**, **78 dos 81** foram encontrados, sem nome repetido.
- **77 têm a mesma remuneração básica: R$ 46.366,19.** Um titular tem R$ 44.820,65; a diferença **não foi explicada**, então não se afirma que o salário é igual para todos.
- O líquido varia de cerca de R$ 26,1 mil a R$ 37,1 mil, por causa de descontos e vantagens.
- Os 3 sem correspondência são suplentes em exercício. Podem não estar na folha normal ou ter o nome escrito de outra forma; **não foi explicado**. Ficam sem salário.
- Ligar por nome funciona, mas é frágil: precisa de validação a cada mês ([D016](decisoes.md#d016-salário-ligado-pelo-nome-completo-com-validação-mensal)).

### 5. Equipe do gabinete

**Refeita em 18/11/2026 pela verificação automática** ([D036](decisoes.md#d036-verificação-automática-da-equipe-do-gabinete-por-vínculo)). Compara, para cada um dos 81 gabinetes, o total e a quebra por vínculo (comissionado, efetivo, requisitado) do resumo oficial com a lista de servidores ativos, sem contar o próprio senador. Os dois baixados no mesmo dia, e só as contagens são guardadas (nunca nomes).

- **80 de 81 gabinetes idênticos**, no total e em cada vínculo. Isso inclui o gabinete com 70 pessoas, em que as duas bases concordam.
- **1 sem explicação:** no gabinete de Camilo Santana, o resumo traz **1 efetivo** que a lista de ativos não tem (resumo 28 pessoas, lista 27). Resumo e lista concordam nos 27 comissionados. Soma de hoje: resumo 1.712, lista 1.711, e essa é a diferença de uma pessoa que já aparecia em 11/11.
- **Terceira fonte (18/11/2026, 16h49):** a **tela** do portal (`www6g.senado.leg.br/transparencia/sen/6336/?ano=2026`) mostra 27 pessoas, todas comissionadas, e o **“Exportar HTML” da mesma página** mostra 28, com 1 efetivo. Nos 81 gabinetes, a tela e a exportação concordam em comissionados, efetivos e requisitados em 80; este é o que difere. Detalhes e prints em [divergencias-nos-dados-do-senado.md](divergencias-nos-dados-do-senado.md).
- **Hipóteses testadas e que não explicam:** servidor fora da lista de ativos (a lista completa de servidores, a de efetivos e a de exercício provisório não trazem esse efetivo) e servidor cedido de outro órgão (a lista de cedidos mostra 4 pessoas no gabinete, e as 4 já estão entre os 27 comissionados). Só o Senado pode explicar.
- **Consequência ([D037](decisoes.md#d037-exibição-por-tipo-de-dado-e-freio-de-segurança)):** a equipe é um dado descritivo, então **aparece para os 80 gabinetes que batem** e fica oculta no gabinete sem explicação, que é listado aqui na página de verificações. Se mais de 5% dos gabinetes falharem, ela some para todos (freio de segurança). Quando o Senado explicar ou corrigir, o gabinete volta sozinho na próxima verificação.
- **Ligação senador-gabinete:** é feita pelo nome (81 de 81), com uma regra para os 2 casos em que o nome do gabinete difere do nome parlamentar ("Weverton" e "Nelsinho Trad Filho"). A contagem de pessoas, que vem de outra fonte, é a segunda barreira contra uma ligação errada.

**Primeira medição (11/11/2026), que ficou superada:**

- O resumo oficial soma **1.723 pessoas nos 81 gabinetes** (cerca de 21 por gabinete).
- A lista de servidores inclui o **próprio senador** (vínculo "PARLAMENTAR", 80 registros). Sem ele, soma **1.722**. A diferença de uma pessoa em 81 gabinetes **não foi explicada**.
- Vínculos na lista: 1.585 comissionados, 136 efetivos e 1 requisitado.
- Por gabinete (sem o senador): mínimo 8, mediana 17, máximo 70. O gabinete com 70 **não foi investigado**.
- Só o **número** de pessoas é usado, do resumo oficial ([D015](decisoes.md#d015-gabinete-pelo-resumo-oficial)). **Custo do gabinete:** pesquisado em 12/11/2026, **não existe valor oficial** (a ligação folha × lotação é só por nome e os encargos não são publicados), então fica fora do projeto ([D025](decisoes.md#d025-só-o-comprovado-a-prova-real)).

### 6. CSV contra API (2008)

- As duas fontes têm as **mesmas 2.449 linhas**, e todo `COD_DOCUMENTO` do CSV tem par na API.
- **8 linhas** têm valor diferente, sempre menor na API (por exemplo R$ 11.100,36 no CSV contra R$ 8.000,18). A soma difere em R$ 9.791,93 (cerca de 0,08%).
- Hipótese *não confirmada*: correções feitas depois de 2021. Sem impacto no MVP, que não exibe 2008.

## Pendências de prova

- Moradia: os **3 casos** pendentes (reconferir quando a página mensal incluir novembro).
- Salário: 3 suplentes sem correspondência e um titular com valor diferente.
- Equipe: 1 efetivo a mais no resumo do gabinete de Camilo Santana, sem explicação. A equipe desse gabinete fica oculta; os outros 80 aparecem.
- Cota de 2008 e 2009: o resumo de 2008 está vazio e o de 2009 é menor que as despesas; só o Senado pode explicar. Ficam ocultos.
- Escritórios de apoio: contagem contra a página de cada senador (hoje fora do MVP).
- Entender: por que o resumo deixa de fora as linhas sem categoria (276 entre 2023 e 2026, só em exercício, em 18/11/2026); o que são os valores negativos, os 56 documentos em formato fora do padrão e as 4 despesas com data no futuro; até que ano a API de recursos (`?ano=`) devolve dados.
- Testemunhas fora do Senado: o **Internet Archive** acusa uma cópia do CSV de 2024 (25/10/2026), mas não consegui ler as cópias (**a testar**). O Portal da Transparência federal e o TSE **não foram verificados** como fonte de conferência.

## Fora do MVP (registrado para não se perder)

**Gastos fora da cota** (resumo do Senado, 2026): seis itens (passagens aéreas por contrato, Correios, diárias de viagens oficiais, outros materiais, impulsionamento em mídias sociais, ressarcimento de passagens) somam cerca de **R$ 8,5 milhões** contra R$ 25,5 milhões dentro da cota no mesmo resumo. Cada item tem página mensal no portal do senador, sem nota fiscal nem fornecedor. Os dados **não dizem** se o dinheiro é reembolsado ao senador ou pago direto pelo Senado. Por isso o bloco saiu do MVP ([D028](decisoes.md#d028-gastos-fora-da-cota-e-moradia-entram-só-provados)).
