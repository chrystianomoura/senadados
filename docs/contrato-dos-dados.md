# Contrato dos dados do site

Quais arquivos JSON o site lê e o que cada um traz. É o elo entre o banco e as telas: o pipeline **gera** esses arquivos a partir do esquema `publico` do Neon, e o site só os **lê**. Decisão em [D044](decisoes.md#d044-site-antes-da-api-com-dados-em-arquivos-json-gerados-do-esquema-público).

**Status:** versão 1 (rascunho de 19/11/2026), **implementada pelo exportador** (`python -m senadados_pipeline.exportar`) e ensaiado com os dados reais numa branch da Neon. Define a primeira fatia do site e, desde 23/11/2026, também a foto e o mandato (`quem_e`). Será confirmado de vez pela primeira tela do site; mudança que quebra o site sobe a `versao_contrato`.

## Regras gerais

- **Só o comprovado ([D025](decisoes.md#d025-só-o-comprovado-a-prova-real)).** Os arquivos nascem do esquema `publico`, que só tem o que passou nas verificações. Um bloco que não foi provado vem como `null`, e **o site não mostra nada no lugar**: sem selo, sem aviso. O que está pendente aparece só na página "Verificações".
- **Dinheiro em centavos inteiros**, em campos terminados em `_centavos`. A formatação ("R$ 46.366,19") é do site.
- **Datas** no formato ISO (`2026-11-18`); meses de moradia como `AAAA-MM`, como o Senado publica.
- **Nenhum nome de pessoa que não seja senador e nenhum CPF** ([D007](decisoes.md#d007-equipe-do-gabinete-só-em-números), [D008](decisoes.md#d008-pessoas-físicas-agrupadas-e-cpf-nunca-exibido)). Pessoas físicas só existem como números agrupados.
- **Os arquivos não vão para o git** ([D014](decisoes.md#d014-dados-crus-fora-do-git)): são gerados na hora do build, com a URL de conexão (`DATABASE_URL_LEITURA`) numa variável de ambiente.
- **Versão:** o `metadados.json` traz `versao_contrato`. Mudança que quebra o site sobe o número.
- **Ordem estável:** listas ordenadas sempre do mesmo jeito (por código, por ano, por mês), para o resultado ser reproduzível.
- **Nome do senador:** vai como o Senado publica (em maiúsculas, "ALAN RICK"). Quem deixa o nome em formato de leitura é o site.

## Arquivos

| Arquivo | Para quê |
|---|---|
| `metadados.json` | Data dos dados, fonte e versão do contrato |
| `senadores.json` | A lista de senadores em exercício, para a busca e os filtros |
| `senadores/{slug}.json` | O perfil de um senador (um arquivo por senador, 81 hoje) |
| `verificacoes.json` | As contagens da página "Verificações" |

### `metadados.json`

| Campo | O que é | Vem de |
|---|---|---|
| `versao_contrato` | Número inteiro, começa em 1 (**2** desde 23/11/2026: `moradia` passou a ter `anos`) | O código do exportador |
| `data_referencia` | Dia da coleta, `AAAA-MM-DD` | `publico.metadados` |
| `carregado_em` | Quando a carga foi feita | `publico.metadados` |
| `anos` | Intervalo coletado, por exemplo `2008-2026` | `publico.metadados` |
| `senadores` | Quantos senadores em exercício | `publico.metadados` |
| `fonte` | Texto fixo: "Senado Federal, dados abertos" | O código do exportador ([D009](decisoes.md#d009-citação-da-fonte-em-toda-página)) |

### `senadores.json`

Uma lista, um item por senador, ordenada por `codigo`.

| Campo | O que é | Vem de |
|---|---|---|
| `codigo` | Código do parlamentar no Senado | `publico.senadores.cod_senador` |
| `slug` | Endereço da página (`alan-rick`), em minúsculas, sem acento e com hífens | Calculado do nome; os 81 são distintos em 19/11/2026 |
| `nome` | Nome parlamentar | `publico.senadores.nome` |
| `uf`, `partido` | Estado e partido | `publico.senadores` |
| `tipo` | `Titular` ou `1º Suplente` | `publico.senadores.tipo` |
| `foto_url` | **Opcional ([D045](decisoes.md#d045-foto-e-mandato-do-senador-com-o-endereço-oficial-do-senado-e-verificação-entre-duas-listas)):** o endereço da foto, só se provado. A lista da home mostra a foto quando ele existe e as iniciais quando não | `publico.perfil` |

Se dois nomes gerarem o mesmo `slug`, o exportador **para com erro** (falha fechada), em vez de escolher um.

### `senadores/{slug}.json`

```json
{
  "codigo": 0,
  "slug": "exemplo-alves",
  "nome": "EXEMPLO ALVES",
  "tipo": "Titular",
  "uf": "AC",
  "partido": "EXEMPLO",
  "quem_e": null,
  "salario": { "ano": 2026, "mes": 10, "basica_centavos": 4500000, "liquida_centavos": 3000000 },
  "cota": {
    "anos": [
      {
        "ano": 2026,
        "parcial": true,
        "total_centavos": 0,
        "meses": [{ "mes": 1, "total_centavos": 0 }],
        "categorias": [{ "nome": "Divulgação da atividade parlamentar", "nome_oficial": "Divulgação da atividade parlamentar", "total_centavos": 0 }],
        "maior_mes": { "mes": 3, "total_centavos": 0 }
      }
    ]
  },
  "fornecedores": {
    "anos": [
      {
        "ano": 2026,
        "empresas": [{ "cnpj": "00.000.000/0001-00", "nome": "EMPRESA EXEMPLO LTDA", "qtd_despesas": 0, "total_centavos": 0 }],
        "total_empresas": 0,
        "agrupados": [{ "tipo": "pessoa_fisica", "qtd_despesas": 0, "total_centavos": 0, "maior_centavos": 0 }]
      }
    ]
  },
  "equipe": { "ano": 2026, "pessoas": 0 },
  "contato": { "endereco": "…", "telefones": ["(61) 3303-0000"], "email": "…" },
  "moradia": { "anos": [{ "ano": 2026, "meses": [{ "mes": "2026-01", "auxilio_moradia": false, "imovel_funcional": true }] }] }
}
```

Todos os nomes e valores do exemplo são inventados, só mostram o formato. Cada bloco, de cima para baixo:

| Bloco | Regra | Vem de |
|---|---|---|
| `quem_e` | ([D045](decisoes.md#d045-foto-e-mandato-do-senador-com-o-endereço-oficial-do-senado-e-verificação-entre-duas-listas)) `{ mandato: {inicio, fim, inicio_data, fim_data}, foto: {url, credito} }`, cada parte `null` se não provada, e o bloco todo `null` se nenhuma foi. `inicio` e `fim` são os anos (o que o site mostra) e as datas completas vão junto, em `AAAA-MM-DD`. O `credito` é "Foto oficial publicada pelo Senado Federal" | `publico.perfil` |
| `salario` | `null` se o senador não passou nas cinco provas ([D041](decisoes.md#d041-verificação-automática-do-salário-pela-identidade-do-senador)). `basica` é o valor do salário no mês, antes dos descontos (conferido na folha de outubro; veja a D046) | `publico.salario` |
| `cota.anos` | Só os anos em que a cota do senador passou na verificação, entre o ano atual e o anterior ([D048](decisoes.md#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador)). `null` se nenhum. `parcial` é verdadeiro no ano da `data_referencia`, para o site dizer "dados parciais, até [mês]". `maior_mes` é o mês de maior valor da série, **só o fato** ([D030](decisoes.md#d030-destaque-do-maior-mês-no-lugar-do-alerta-fora-do-padrão)) | `publico.despesas_mensais` |
| `cota.anos[].categorias` | `nome` é o nome curto da tabela de [fontes-de-dados.md](fontes-de-dados.md#nomes-das-categorias-de-despesa); `nome_oficial` fica junto, para a explicação "de onde vem este número". Categoria nova do Senado usa o nome oficial nos dois campos | `publico.despesas_mensais` |
| `fornecedores.anos` | Os mesmos anos da cota (a regra de exibição é a mesma). `empresas` traz as **10 maiores** por valor, e `total_empresas` diz quantas existem, porque há em média 50 por senador e ano e no máximo 1.503. `agrupados` traz pessoas físicas, documentos fora do padrão e despesas sem documento, **sem nome e sem documento** ([D008](decisoes.md#d008-pessoas-físicas-agrupadas-e-cpf-nunca-exibido)) | `publico.fornecedores_anuais` e `publico.fornecedores_agrupados_anuais` |
| `equipe` | `null` se o gabinete não foi provado. Só o número de pessoas | `publico.equipe` |
| `contato` | `null` se nenhum campo foi provado. Dentro dele, cada campo ausente é `null`. Os telefones vêm um por linha no banco e viram uma lista | `publico.contato` |
| `moradia` | **Versão 2 do contrato ([D049](decisoes.md#d049-moradia-do-ano-anterior-com-três-fontes)):** `{ "anos": [{ano, meses}] }`, um bloco por ano provado, do mais antigo ao mais recente. `null` se nenhum ano foi provado (inclui os pendentes). Ano provado e sem nenhum mês de uso: `meses` vazio, e então o senador não usou nenhum benefício. Quem foi provado vem de `publico.moradia_verificada` (migração 003), porque `moradia_meses` não tem linha de quem não usou | `publico.moradia_verificada` e `publico.moradia_meses` |

### `verificacoes.json`

| Campo | O que é | Vem de |
|---|---|---|
| `resumo` | Por verificação e ano: `identicos`, `explicados`, `pendentes`, `ocultos` e `verificado_em` | `publico.verificacoes_resumo` |
| `motivos` | Por verificação, ano e situação (`pendente` ou `oculto`): o motivo de uma lista fechada e quantos casos | `publico.verificacoes_motivos` |

**Sem nomes de senadores** ([D042](decisoes.md#d042-banco-no-neon-só-dados-agregados-dois-esquemas-e-carga-repetível), decisão 5). Os nomes só aparecem na seção de divergências, que é texto escrito à mão com prova em imagem ([divergencias-nos-dados-do-senado.md](divergencias-nos-dados-do-senado.md)).

## O que o exportador confere antes de gravar

Falha fechada: se qualquer conferência quebrar, **nenhum arquivo é gravado**.

- `slug` único e não vazio; o número de senadores da lista é igual ao dos metadados.
- Em cada ano da cota, os meses somam o total e as categorias somam o total.
- Nada com formato de CPF, inteiro ou mascarado, em nenhum lugar (o CNPJ de empresa tem outro formato, e nomes como "CPFL" não são confundidos com CPF).
- Cada lista é ordenada pelo próprio exportador (por mês, por valor, por tipo), sem depender da ordem que o banco devolve.

## O que ainda não está neste contrato

- **Posição entre os senadores, ranking e comparação:** comparam senadores, então seguem o "tudo ou nada" da [D037](decisoes.md#d037-exibição-por-tipo-de-dado-e-freio-de-segurança). Falta definir quem entra no grupo (um senador, sem despesa em 2026, não tem valor para comparar). Ficam para uma fatia própria.
- **Como o Next.js lê os arquivos:** definido na implementação do site. O exportador grava por padrão em `web/dados/`, que o git ignora, e troca a pasta inteira a cada execução (o arquivo de quem saiu da lista não fica para trás, [D026](decisoes.md#d026-só-senadores-em-exercício)).
- **Tamanho (medido em 19/11/2026, na branch de ensaio):** 84 arquivos, 1,6 MB no total. Cada perfil tem 20 KB em média e 49 KB no máximo. O maior número de empresas num ano é 418, e o perfil leva só as 10 maiores.
