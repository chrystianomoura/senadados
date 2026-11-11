# AGENTS.md

Instruções para qualquer agente (humano ou de IA) que trabalhe neste repositório. Leia este arquivo inteiro antes de agir. Em caso de conflito entre este arquivo e uma suposição sua, vale este arquivo. Em caso de conflito com um pedido direto do mantenedor, vale o pedido, e este arquivo deve ser atualizado depois.

## 1. O projeto em três linhas

**Senadados** transforma os dados oficiais de gastos e perfil dos senadores em páginas que qualquer cidadão entende. É um projeto de portfólio, **sem orçamento** (tudo precisa ser gratuito) e com **coerência documental** como diferencial. Veja o [README.md](README.md) para o contexto completo.

**Estado atual:** planejamento, sem código. O README descreve o que o projeto *vai* ser e muda com o tempo.

## 2. Princípios inegociáveis

1. **Tudo tem um porquê escrito.** Nenhuma decisão técnica, regra de limpeza ou escolha de modelo entra sem justificativa registrada em `docs/decisoes.md` (ou no commit, se for pequena).
2. **Documentação e código andam juntos.** Mudou o código? Atualize os documentos afetados **no mesmo commit**. Uma tarefa não está concluída com a documentação desatualizada.
3. **Dado verificado, não suposto.** Nunca afirme que uma fonte, coluna, limite ou preço existe sem ter conferido. O que não foi verificado deve ser escrito como "não verificado".
4. **Zero custo.** Não adote serviço, biblioteca paga, domínio ou plano pago sem **perguntar antes**. Se um plano gratuito exigir cartão, pergunte também.
5. **Neutralidade.** O projeto aponta o que é *incomum*, nunca o que é *irregular, ilegal ou suspeito*. Veja a seção 6.
6. **Simplicidade.** Não adicione ferramenta, camada ou abstração que o volume de dados não justifique. Na dúvida, escolha a opção mais simples e registre por quê.

## 3. Idioma

- **Documentação, commits, issues e textos para o usuário:** português do Brasil, em linguagem simples.
- **Código** (nomes de variáveis, funções, arquivos): inglês, exceto termos do domínio do Senado, que ficam em português (`senador`, `ceaps`, `despesa`, `gabinete`). *Esta é uma convenção inicial; se for mudar, registre em `docs/decisoes.md`.*
- Textos para o cidadão devem ser compreensíveis sem conhecimento técnico. Evite siglas sem explicação (explique CEAPS na primeira vez).

## 4. Padrão de commits

Todos os commits seguem o **mesmo formato**, sem exceção. O histórico deve poder ser lido como um diário do projeto.

### Formato

```
tipo(escopo): descrição curta no imperativo

Corpo opcional explicando O QUE mudou e, principalmente, POR QUÊ.
```

### Regras

- **Primeira linha:** até 72 caracteres, em português, no imperativo ("adiciona", "corrige", "remove"), sem ponto final.
- **Corpo:** separado por uma linha em branco. Explica o **porquê**, não repete o que o diff já mostra. Obrigatório quando a mudança envolve uma decisão.
- **Um assunto por commit.** Não misture documentação, código e configuração não relacionados.
- **Sem autoria de IA.** **Não** adicione `Co-Authored-By`, "Generated with", nem qualquer linha que atribua o commit a uma ferramenta ou modelo de IA. Os commits são do mantenedor do projeto.

### Tipos permitidos

| Tipo | Quando usar |
|---|---|
| `feat` | Funcionalidade nova |
| `fix` | Correção de erro |
| `docs` | Só documentação |
| `data` | Mudança em fonte, coleta ou regra de limpeza de dados |
| `refactor` | Reorganização sem mudar comportamento |
| `test` | Testes |
| `ci` | Automação (GitHub Actions) |
| `chore` | Manutenção e configuração |

### Escopos sugeridos

`pipeline`, `api`, `web`, `ml`, `docs`, `ci`, `dados`. Para mudanças que atravessam várias partes, omita o escopo.

### Exemplos

```
docs: adiciona README com objetivo e escolha das tecnologias

Descreve o projeto no primeiro dia para registrar o ponto de partida.
O README deve mudar conforme o escopo for validado com dados reais.
```

```
data(pipeline): converte valores com vírgula decimal para número

O CSV de 2024 mistura "583,58" e "3800". Sem padronizar, a soma por
senador fica errada.
```

## 5. Fluxo de trabalho

- Branch principal: `main`. Trabalhe em branches nomeadas `tipo/descricao-curta` (ex.: `data/limpeza-despesas`).
- Antes de commitar: rodar testes e lint (quando existirem) e conferir que a documentação afetada foi atualizada.
- **Não faça `push`, abra pull request, publique ou apague nada sem pedido explícito do mantenedor.**
- Antes de commitar mudanças grandes, mostre ao mantenedor o resultado quando ele pedir revisão.

## 6. Regras sobre dados e pessoas

- **Fontes oficiais apenas** para dados de senadores: Senado Federal (arquivos de despesas e APIs de dados abertos). Qualquer outra fonte exige aprovação e registro.
- **Dado cru nunca vai para o git.** Fica em `data/raw/` (ignorado). O que entra no repositório é o código que o gera.
- **Nenhum segredo no repositório:** senhas, chaves, tokens e strings de conexão ficam em variáveis de ambiente.
- **Equipe de gabinete: só agregados.** Mostre quantidades e custos, **nunca nomes** de assessores ou servidores.
- **Linguagem neutra.** Use "fora do padrão", "acima da média dele", "incomum". **Nunca** use "suspeito", "irregular", "fraude", "desvio de dinheiro" ou termos que sugiram culpa.
- **Contexto antes de comparação.** Ao comparar senadores, considere que a cota varia por estado. Indique isso na interface.
- **Reembolsado não é gasto total.** Sempre deixe claro o que está e o que não está nos números.
- **Toda informação exibida indica fonte e data de atualização.**
- **CPF nunca é exibido por inteiro, e pessoas físicas aparecem agrupadas, sem nome** (regra provisória até confirmação do mantenedor). A coluna `CNPJ_CPF` traz CPFs completos de pessoas físicas. Veja a decisão D008 em [docs/decisoes.md](docs/decisoes.md).
- **Citação da fonte:** os termos do Senado exigem, no máximo, citar a proveniência. Toda página mostra a fonte e a data de atualização (D009). Detalhes dos termos em [docs/fontes-de-dados.md](docs/fontes-de-dados.md).
- **Fonte principal é a API;** o CSV serve para conferência (D005).

## 7. Stack aprovada

Python (Pandas, Pandera, scikit-learn) para pipeline e modelo; PostgreSQL no Neon como banco; FastAPI para a API; Next.js com TypeScript como site, exportado de forma estática no Cloudflare Pages; GitHub Actions para atualização diária; pytest, ruff e uv para qualidade. O motivo de cada escolha está no [README.md](README.md).

Não troque nem acrescente tecnologia sem registrar a decisão e o motivo. Os limites dos planos gratuitos foram pesquisados em 11/11/2026, em grande parte em fontes secundárias, e precisam ser reconfirmados nas páginas oficiais antes de publicar.

## 8. Como se comportar

- **Verifique antes de afirmar.** Se não conferiu, diga que não conferiu.
- **Reporte com honestidade.** Se um teste falhou, algo foi pulado ou algo não foi verificado, diga isso claramente e com a saída real.
- **Explique o porquê.** Ao propor ou fazer algo, diga o motivo em linguagem simples.
- **Pergunte quando a decisão é do mantenedor:** escopo, custo, publicação, escolha de tecnologia, nomes.
- **Não aja fora do pedido.** Não baixe grandes volumes, não instale serviços, não apague nem sobrescreva sem confirmar. Antes de apagar ou sobrescrever, olhe o alvo.
- **Seja conciso.** Texto claro e curto vale mais que texto longo.
- **Atualize este arquivo** quando uma regra mudar ou uma nova for combinada.

## 9. Estrutura prevista do repositório

```
senadados/
├── README.md        # o que é o projeto e por que as escolhas
├── AGENTS.md        # este arquivo
├── docs/            # escopo, fontes de dados, registro de decisões
├── pipeline/        # coleta, limpeza e modelo (Python)
├── api/             # FastAPI
├── web/             # site (Next.js)
├── data/raw/        # dados brutos (fora do git)
└── .github/         # automações
```

Estas pastas serão criadas conforme forem necessárias, não antes.
