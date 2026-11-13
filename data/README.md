# Dados

Esta pasta guarda os dados baixados do Senado para análise e conferência. **Nada daqui vai para o git**: o repositório guarda o código que gera os dados, não os dados ([D014](../docs/decisoes.md#d014-dados-crus-fora-do-git)). Só este arquivo é versionado.

## `raw/` (local, ignorado pelo git)

| Caminho | O que é | Origem |
|---|---|---|
| `raw/api/ceaps_AAAA.json` | Despesas da cota de 2008 a 2026 (fonte principal) | API `despesas_ceaps/{ano}` |
| `raw/recursos/{código}.json` | Resumo de recursos de cada um dos 81 senadores em exercício | API `recursos-utilizados` |
| `raw/senadores_atuais.json` | Lista dos 81 senadores em exercício | API `senadores` |
| `raw/perfil/` | Lista legislativa atual, auxílio-moradia e escritórios de apoio | APIs do Senado |
| `raw/folha/` | Folha de setembro de 2026, servidores ativos e lotações | API `servidores` |

Endereços completos e o que cada um traz: [docs/fontes-de-dados.md](../docs/fontes-de-dados.md).

## Regras

- **Só senadores em exercício** ([D026](../docs/decisoes.md#d026-só-senadores-em-exercício)). Dados de quem saiu do mandato foram apagados e não devem ser baixados de novo.
- **Sem segredos e sem dados pessoais além dos públicos do Senado.** O CPF de pessoa física nunca é exibido ([D008](../docs/decisoes.md#d008-pessoas-físicas-agrupadas-e-cpf-nunca-exibido)).
- Os arquivos podem ser baixados de novo a qualquer momento; quando o pipeline existir, ele fará isso de forma repetível.
