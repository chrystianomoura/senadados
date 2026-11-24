# Ferramentas

Scripts de apoio que **não fazem parte do pipeline nem do site**: servem para refazer as imagens de prova, conferir que os dados batem de ponta a ponta e repetir pesquisas. Todos são de **leitura** (só consultam páginas públicas do Senado, o banco com o papel de leitura e os arquivos do projeto), com uma exceção: `montar_provas.py` escreve por cima das imagens de `docs/evidencias/`.

Rode a partir da **raiz do repositório**. Os arquivos temporários vão para `ferramentas/saida/` (o git ignora). Cada script traz no início o que faz e como usar.

## Provas (refazer as imagens da página "Verificações")

| Script | O que faz |
|---|---|
| `provas/fotografar.mjs` | Abre num Chrome sem janela as telas e as exportações do Senado, esconde a foto do senador e recorta o trecho de cada caso |
| `provas/montar_provas.py` | Junta os recortes, baixa de novo os arquivos de despesas e refaz as tabelas "montagem do Senadados" nas 11 imagens de `docs/evidencias/` |

```bash
node ferramentas/provas/fotografar.mjs
```

```bash
uv run --project pipeline python ferramentas/provas/montar_provas.py
```

Depois, **confira à mão** os números do texto dos casos em [docs/divergencias-nos-dados-do-senado.md](../docs/divergencias-nos-dados-do-senado.md) e em `web/src/lib/divergencias.ts`, e atualize a data da captura (`CAPTURADO_EM`). Precisa do Node 22 ou mais novo e do Chrome (no macOS o caminho já é o padrão; em outro sistema, defina `CHROME`).

## Conferência (rodar antes de publicar ou de mexer em dados)

| Script | O que confere |
|---|---|
| `conferencia/dados.py` | Banco da nuvem, banco local, JSON do site e despesas brutas do Senado: somas, verificações e cada bloco do perfil. Termina com `ERROS: 0` |
| `conferencia/site.py` | O HTML de `web/out/`: texto quebrado, palavras de culpa, CPF, links e imagens quebrados, e os botões de trocar de ano |
| `conferencia/links.py` | Links relativos e âncoras de todos os `.md` |
| `conferencia/permissoes.py` | O que cada papel do banco consegue e não consegue fazer (D042) |
| `conferencia/servir_com_csp.mjs` | Serve `web/out/` com a política de conteúdo de `web/public/_headers`, para testar no navegador |

```bash
uv run --project pipeline --env-file .env python ferramentas/conferencia/dados.py
```

```bash
python3 ferramentas/conferencia/site.py
```

```bash
python3 ferramentas/conferencia/links.py
```

## Pesquisa

| Script | O que é |
|---|---|
| `pesquisa/anos_anteriores.py` | As sondagens de 23/11/2026 sobre trazer dados de 2025 (moradia, equipe e salário). Os resultados estão na [D049](../docs/decisoes.md#d049-moradia-do-ano-anterior-com-três-fontes) |

```bash
uv run --project pipeline python ferramentas/pesquisa/anos_anteriores.py moradia
```

## Observações

- O lint vale como o do pipeline (`ferramentas/ruff.toml`), menos as linhas longas de texto: `uv run --project pipeline ruff check ferramentas`.
- Não há testes automáticos aqui: cada script termina dizendo o que achou, e a conferência é ler essa saída.
- `dados.py` fixa os anos 2025 e 2026 na conferência dos dados brutos; mude quando o ano virar.
