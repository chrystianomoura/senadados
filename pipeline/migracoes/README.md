# Migrações do banco

Arquivos SQL numerados que criam e alteram o banco no Neon ([D042](../../docs/decisoes.md#d042-banco-no-neon-só-dados-agregados-dois-esquemas-e-carga-repetível), [D043](../../docs/decisoes.md#d043-migrações-em-sql-puro-driver-psycopg-e-carga-que-ensaia-antes-de-gravar)). São aplicados em ordem pelo `senadados_pipeline.migrar`; o que já foi aplicado fica em `interno.migracoes`.

| Arquivo | O que faz |
|---|---|
| `001_esquemas.sql` | Cria os esquemas `publico` e `interno` e as tabelas |
| `002_papeis.sql` | Dá a `sd_carga` (escreve) e a `sd_leitura` (só lê o `publico`) o mínimo de que precisam. Exige que os papéis já existam |
| `003_moradia_verificada.sql` | `publico.moradia_verificada`: quem teve a moradia provada, mesmo sem nenhum mês de uso. Sem ela, "não usou" e "não provado" não se distinguem |
| `004_perfil.sql` | `publico.perfil` (foto e mandato provados) e `interno.verificacao_perfil`, com as permissões de cada papel ([D045](../../docs/decisoes.md#d045-foto-e-mandato-do-senador-com-o-endereço-oficial-do-senado-e-verificação-entre-duas-listas)) |

**Regras:** nome no formato `NNN_nome.sql`, numeração sem buracos; uma migração aplicada **nunca é editada** (cria-se uma nova); nenhuma senha nem URL de conexão entra aqui; tabela nova não herda permissão, então a própria migração concede o que for preciso.
