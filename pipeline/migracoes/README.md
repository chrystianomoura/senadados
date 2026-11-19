# Migrações do banco

Arquivos SQL numerados que criam e alteram o banco no Neon ([D042](../../docs/decisoes.md#d042-banco-no-neon-só-dados-agregados-dois-esquemas-e-carga-repetível), [D043](../../docs/decisoes.md#d043-migrações-em-sql-puro-driver-psycopg-e-carga-que-ensaia-antes-de-gravar)). São aplicados em ordem pelo `senadados_pipeline.migrar`; o que já foi aplicado fica em `interno.migracoes`.

| Arquivo | O que faz |
|---|---|
| `001_esquemas.sql` | Cria os esquemas `publico` e `interno` e as tabelas |
| `002_papeis.sql` | Dá a `sd_carga` (escreve) e a `sd_leitura` (só lê o `publico`) o mínimo de que precisam. Exige que os papéis já existam |

**Regras:** nome no formato `NNN_nome.sql`, numeração sem buracos; uma migração aplicada **nunca é editada** (cria-se uma nova); nenhuma senha nem URL de conexão entra aqui; tabela nova não herda permissão, então a própria migração concede o que for preciso.
