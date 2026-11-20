# Documentação

Leia nesta ordem se for a primeira vez no projeto.

| Documento | Para que serve |
|---|---|
| [../README.md](../README.md) | O que é o projeto, para quem, e por que cada tecnologia |
| [escopo.md](escopo.md) | O que o site mostra: telas, regras de exibição, versões e ordem de construção |
| [decisoes.md](decisoes.md) | Cada decisão com o seu porquê, com índice e situação atual |
| [fontes-de-dados.md](fontes-de-dados.md) | De onde vêm os dados, formato, qualidade e termos de uso |
| [andamento.md](andamento.md) | Em que pé o projeto está: o que existe, o que foi provado, as decisões recentes, as pendências e o próximo passo |
| [contrato-dos-dados.md](contrato-dos-dados.md) | Quais arquivos JSON o site lê e o que cada um traz (versão 1, em uso pelo site) |
| [verificacoes.md](verificacoes.md) | Resultado de cada conferência entre bases do Senado e o que ainda falta provar |
| [divergencias-nos-dados-do-senado.md](divergencias-nos-dados-do-senado.md) | Onde os dados do Senado não batem entre si, explicado para qualquer pessoa e provado com prints |
| [../AGENTS.md](../AGENTS.md) | Regras de trabalho para qualquer pessoa ou agente (commits, dados, comportamento) |
| [../design/README.md](../design/README.md) | Protótipo da página e identidade visual |
| [../data/README.md](../data/README.md) | O que fica em `data/raw/` (fora do git) |
| [../pipeline/README.md](../pipeline/README.md) | O código que coleta, limpa e verifica os dados, e como rodá-lo |

## Regra de manutenção

Mudou o código ou uma regra? Atualize o documento afetado **no mesmo commit**. Decisões não são apagadas: marcam-se como substituídas ([decisoes.md](decisoes.md)).
