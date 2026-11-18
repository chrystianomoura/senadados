# Dados

Esta pasta guarda os dados baixados do Senado para análise e conferência. **Nada daqui vai para o git**: o repositório guarda o código que gera os dados, não os dados ([D014](../docs/decisoes.md#d014-dados-crus-fora-do-git)). Só este arquivo é versionado.

## `raw/` (local, ignorado pelo git)

| Caminho | O que é | Origem |
|---|---|---|
| `raw/api/ceaps_AAAA.json` | Despesas da cota de 2008 a 2026 (fonte principal) | API `despesas_ceaps/{ano}` |
| `raw/recursos/{código}.json` | Resumo de recursos de cada um dos 81 senadores em exercício | API `recursos-utilizados` |
| `raw/senadores_atuais.json` | Lista dos 81 senadores em exercício | API `senadores` |
| `raw/perfil/` | Lista legislativa atual, auxílio-moradia e escritórios de apoio | APIs do Senado |
| `raw/folha/` | Folha de setembro de 2026 e lotações. A lista de servidores ativos (com nomes) foi apagada em 18/11/2026 | API `servidores` |
| `raw/equipe/` | Número de pessoas por gabinete e vínculo (lista de servidores contada na hora, **sem nomes**) e o bloco de pessoal do resumo de cada senador | Pipeline (`equipe`) |
| `raw/coleta.json` | Data e hora de cada download da lista e das despesas por ano; serve para garantir que as bases são da mesma foto dos dados | Gerado pela coleta |

Endereços completos e o que cada um traz: [docs/fontes-de-dados.md](../docs/fontes-de-dados.md).

## `limpo/` (local, ignorado pelo git)

| Caminho | O que é |
|---|---|
| `limpo/senadados.sqlite` | Despesas e senadores já validados e limpos, gerados por `pipeline/` ([D034](../docs/decisoes.md#d034-limpeza-com-validação-em-sqlite-local-sem-nome-nem-documento-de-pessoa-física)). Pode ser refeito a qualquer momento a partir de `raw/` |

## Regras

- **Só senadores em exercício** ([D026](../docs/decisoes.md#d026-só-senadores-em-exercício)). A coleta do pipeline já grava só as despesas de quem está na lista ([D033](../docs/decisoes.md#d033-coleta-local-que-só-grava-quem-está-em-exercício)).
- **Substituídos em 18/11/2026:** os `raw/api/ceaps_AAAA.json` baixados à mão em 11/11 traziam ex-senadores (em 2024, 16 dos 88 senadores da despesa não estavam na lista). Foram trocados pelos da coleta do pipeline, já filtrados: 154.298 registros em 19 arquivos, nenhum de fora da lista. O resto de `raw/` (resumos, perfil, folha) cobre só quem está em exercício, mas **não foi atualizado** e segue de 11/11 e 12/11.
- **Sem segredos e sem dados pessoais além dos públicos do Senado.** O CPF de pessoa física nunca é exibido ([D008](../docs/decisoes.md#d008-pessoas-físicas-agrupadas-e-cpf-nunca-exibido)).
- Os arquivos podem ser baixados de novo a qualquer momento; quando o pipeline existir, ele fará isso de forma repetível.
