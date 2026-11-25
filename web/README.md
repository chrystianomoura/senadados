# Site

O site do Senadados: páginas estáticas em Next.js (TypeScript), geradas a partir dos arquivos JSON do pipeline ([D044](../docs/decisoes.md#d044-site-antes-da-api-com-dados-em-arquivos-json-gerados-do-esquema-público), [D046](../docs/decisoes.md#d046-site-em-nextjs-16-com-exportação-estática-fontes-hospedadas-e-testes-com-vitest)). O site **não** consulta o banco nem a API: só lê arquivos, na hora do build.

**Hoje existem:** a home (`/`), com a abertura (nome, o que é e retratos sorteados a cada visita), "Como funciona", a busca por nome com filtros por estado e partido, a página "Verificações" (`/verificacoes/`) e o perfil do senador (`/senador/{endereço}/`, e `/senador/{endereço}/{ano}/` para o outro ano), com o resumo do ano, as guias que se abrem e o botão para trocar de ano. O site mostra a foto na lista e no perfil quando o JSON a traz (o crédito aparece ao passar o mouse) e as iniciais quando não, e o mandato (ano de início e de fim) no cartão do perfil. O cabeçalho é fixo e não tem menu. A comparação de dois senadores (`/comparar/`, [D050](../docs/decisoes.md#d050-comparação-de-dois-senadores-lado-a-lado)) tem os dois escolhidos por busca, um cartão por guia do perfil e o link da escolha no endereço (`?a=...&b=...`); o perfil tem o botão "Comparar com outro senador". Posição entre os senadores, ranking e a página "Sobre os dados" ainda não existem.

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

Conferências: `npm run typecheck` (tipos) e `npm test` (as funções de formatação, de busca, dos anos, das verificações e da comparação, com Vitest).

## Como é organizado

| Caminho | O que é |
|---|---|
| `dados/` | Os JSON do [contrato](../docs/contrato-dos-dados.md), gerados pelo exportador. **Fora do git.** Sem eles o build para com uma mensagem que diz o que fazer |
| `src/lib/types.ts` | Os tipos do contrato |
| `src/lib/dados.ts` | Leitura dos JSON (só no build) |
| `src/lib/formato.ts` | Dinheiro, meses, nomes, partido e datas em português do Brasil, com os testes ao lado |
| `src/lib/busca.ts` | Busca por nome e filtros da home, com testes |
| `src/lib/anos.ts` | Quais anos a página do senador oferece e qual abre (o atual, quando a verba dele já tem dois meses), com testes ([D048](../docs/decisoes.md#d048-só-o-ano-atual-e-o-anterior-com-troca-de-ano-na-página-do-senador)) |
| `src/lib/comparar.ts` | O resumo de um perfil e as seis guias da comparação de dois senadores (frase, diferença e quem tem mais), com testes ([D050](../docs/decisoes.md#d050-comparação-de-dois-senadores-lado-a-lado)) |
| `src/lib/verificacoes.ts`, `src/lib/divergencias.ts` | Os nomes, a ordem e os casos da página "Verificações", com testes |
| `src/components/` | O perfil e as peças dele (guia que se abre, barras, gráfico mensal, "de onde vem este número"), o cabeçalho fixo (`CabecalhoTopo`) e a busca |
| `src/components/abertura/` | A abertura da home: nome, o que é e o mosaico de retratos sorteados no navegador |
| `public/fotos/` | As cópias reduzidas das fotos, geradas por `python -m senadados_pipeline.fotos` ([D047](../docs/decisoes.md#d047-cópias-reduzidas-das-fotos-oficiais-com-pillow)). **Fora do git.** Sem elas o site usa o endereço oficial da foto |
| `public/evidencias/` | As imagens de prova da página "Verificações", **copiadas de `docs/evidencias/`** a cada `dev` e `build` por `scripts/copiar-evidencias.mjs`. Fora do git ([D038](../docs/decisoes.md#d038-documento-público-de-divergências-com-prova-em-imagem)) |
| `public/_headers` | Cabeçalhos do Cloudflare Pages, com a política de conteúdo (CSP). Vai para `out/` no build ([D045](../docs/decisoes.md#d045-foto-e-mandato-do-senador-com-o-endereço-oficial-do-senado-e-verificação-entre-duas-listas)) |
| `src/app/` | As rotas (`/`, `/senador/{endereço}/`, `/senador/{endereço}/{ano}/` para o outro ano, `/comparar/` e `/verificacoes/`) e o CSS (a identidade da [D029](../docs/decisoes.md#d029-identidade-visual), portada do protótipo em `design/`) |

## Regras

- **Dado não provado vem como `null` e o site não mostra nada no lugar.** Sem selo, sem aviso ([D025](../docs/decisoes.md#d025-só-o-comprovado-a-prova-real)).
- **Sem lógica de negócio no site.** Ele formata e mostra o que o pipeline já provou.
- **Linguagem neutra** e nenhum julgamento sobre legalidade ([D010](../docs/decisoes.md#d010-linguagem-neutra), [D024](../docs/decisoes.md#d024-sem-camada-jurídica)).
- **Fontes hospedadas no próprio site:** o navegador só contata o próprio site.
