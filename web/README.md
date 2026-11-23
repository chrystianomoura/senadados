# Site

O site do Senadados: páginas estáticas em Next.js (TypeScript), geradas a partir dos arquivos JSON do pipeline ([D044](../docs/decisoes.md#d044-site-antes-da-api-com-dados-em-arquivos-json-gerados-do-esquema-público), [D046](../docs/decisoes.md#d046-site-em-nextjs-16-com-exportação-estática-fontes-hospedadas-e-testes-com-vitest)). O site **não** consulta o banco nem a API: só lê arquivos, na hora do build.

**Hoje existem:** a home (`/`), com a abertura (nome, o que é e retratos sorteados a cada visita), "Como funciona", a busca por nome com filtros por estado e partido, e o perfil do senador (`/senador/{endereço}/`), com o resumo do ano e as guias que se abrem. O site mostra a foto na lista e no perfil quando o JSON a traz (o crédito aparece ao passar o mouse) e as iniciais quando não, e o mandato (ano de início e de fim) no cartão do perfil. O cabeçalho é fixo e não tem menu. Posição entre os senadores, ranking, comparação e as páginas "Verificações" e "Sobre os dados" ainda não existem.

## Como rodar

Precisa de Node 22.12 ou mais novo. Primeiro, gere os arquivos de dados e as cópias das fotos (de dentro de `pipeline/`, com o `.env` na raiz; veja [pipeline/README.md](../pipeline/README.md)). As fotos pedem a coleta e as verificações do mesmo dia; sem elas o site funciona, com as fotos vindas do Senado:

```bash
uv run --env-file ../.env python -m senadados_pipeline.exportar
```

Depois, de dentro de `web/`:

```bash
npm install
```

```bash
npm run dev
```

Abra `http://localhost:3000`. Para gerar as páginas prontas em `out/`:

```bash
npm run build
```

Conferências: `npm run typecheck` (tipos) e `npm test` (22 testes das funções de formatação e de busca, com Vitest).

## Como é organizado

| Caminho | O que é |
|---|---|
| `dados/` | Os JSON do [contrato](../docs/contrato-dos-dados.md), gerados pelo exportador. **Fora do git.** Sem eles o build para com uma mensagem que diz o que fazer |
| `src/lib/types.ts` | Os tipos do contrato |
| `src/lib/dados.ts` | Leitura dos JSON (só no build) |
| `src/lib/formato.ts` | Dinheiro, meses, nomes, partido e datas em português do Brasil, com os testes ao lado |
| `src/lib/busca.ts` | Busca por nome e filtros da home, com testes |
| `src/components/` | O perfil e as peças dele (guia que se abre, barras, gráfico mensal, "de onde vem este número"), o cabeçalho fixo (`CabecalhoTopo`) e a busca |
| `src/components/abertura/` | A abertura da home: nome, o que é e o mosaico de retratos sorteados no navegador |
| `public/fotos/` | As cópias reduzidas das fotos, geradas por `python -m senadados_pipeline.fotos` ([D047](../docs/decisoes.md#d047-cópias-reduzidas-das-fotos-oficiais-com-pillow)). **Fora do git.** Sem elas o site usa o endereço oficial da foto |
| `public/_headers` | Cabeçalhos do Cloudflare Pages, com a política de conteúdo (CSP). Vai para `out/` no build ([D045](../docs/decisoes.md#d045-foto-e-mandato-do-senador-com-o-endereço-oficial-do-senado-e-verificação-entre-duas-listas)) |
| `src/app/` | As rotas e o CSS (a identidade da [D029](../docs/decisoes.md#d029-identidade-visual), portada do protótipo em `design/`) |

## Regras

- **Dado não provado vem como `null` e o site não mostra nada no lugar.** Sem selo, sem aviso ([D025](../docs/decisoes.md#d025-só-o-comprovado-a-prova-real)).
- **Sem lógica de negócio no site.** Ele formata e mostra o que o pipeline já provou.
- **Linguagem neutra** e nenhum julgamento sobre legalidade ([D010](../docs/decisoes.md#d010-linguagem-neutra), [D024](../docs/decisoes.md#d024-sem-camada-jurídica)).
- **Fontes hospedadas no próprio site:** o navegador só contata o próprio site.
