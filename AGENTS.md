# AGENTS.md

Instruções para qualquer agente (humano ou de IA) que trabalhe neste repositório. Leia este arquivo inteiro antes de agir. Em caso de conflito entre este arquivo e uma suposição sua, vale este arquivo. Em caso de conflito com um pedido direto do mantenedor, vale o pedido, e este arquivo deve ser atualizado depois.

## 1. O projeto em três linhas

**Senadados** transforma os dados oficiais de gastos e perfil dos senadores em páginas que qualquer cidadão entende. É um projeto de portfólio, **sem orçamento** (tudo precisa ser gratuito) e com **coerência documental** como diferencial. Veja o [README.md](README.md) para o contexto completo.

**Escopo de pessoas:** só os **senadores em exercício**, pela lista oficial do Senado (D026). Quem sai do mandato sai do site.

**Estado atual (12/11/2026):** escopo, regras e protótipo da página fechados; fontes e conferências documentadas; **ainda sem código de pipeline, API ou site**. Próximo passo: o pipeline (ordem de construção em [docs/escopo.md](docs/escopo.md)). Índice dos documentos em [docs/README.md](docs/README.md).

## 2. Princípios inegociáveis

1. **Tudo tem um porquê escrito.** Nenhuma decisão técnica, regra de limpeza ou escolha de modelo entra sem justificativa registrada em `docs/decisoes.md` (ou no commit, se for pequena).
2. **Documentação e código andam juntos.** Mudou o código? Atualize os documentos afetados **no mesmo commit**. Uma tarefa não está concluída com a documentação desatualizada.
3. **Dado verificado, não suposto.** Nunca afirme que uma fonte, coluna, limite ou preço existe sem ter conferido. O que não foi verificado deve ser escrito como "não verificado".
4. **Zero custo.** Não adote serviço, biblioteca paga, domínio ou plano pago sem **perguntar antes**. Se um plano gratuito exigir cartão, pergunte também.
5. **Neutralidade.** O projeto aponta o que é *incomum*, nunca o que é *irregular, ilegal ou suspeito*. Veja a seção 6.
6. **Simplicidade.** Não adicione ferramenta, camada ou abstração que o volume de dados não justifique. Na dúvida, escolha a opção mais simples e registre por quê.
7. **Só o comprovado (D025).** Nenhum número aparece sem origem oficial, consulta documentada, teste e data. Se duas fontes do Senado divergem sem explicação, o número **não aparece**. Nada de estimativas.
8. **Sem camada jurídica (D024).** O projeto mostra valores e ajuda a interpretá-los. **Nunca afirme se algo está dentro ou fora da lei**, nunca mostre limites legais nem "quanto pode". Cada pessoa pesquisa a lei por conta própria.

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
- **Equipe de gabinete: só o número de pessoas**, vindo do resumo oficial. **Nunca nomes** de assessores ou servidores e **nunca custo estimado** (D025).
- **Linguagem neutra.** Descreva fatos: "o maior mês foi março", "acima da média dele". **Nunca** use "suspeito", "irregular", "fraude", "desvio de dinheiro" ou termos que sugiram culpa.
- **Referência vinda dos dados.** Ao comparar senadores, use só números do próprio grupo (posição entre os senadores em exercício, histórico do próprio senador). Não cite limites nem regras para justificar uma comparação.
- **Diga o que cada número cobre.** A verba mostrada é só o que o Senado reembolsa pela cota; não é tudo o que o Senado paga.
- **Regra de agregado (D026).** Nenhum total, mediana ou ranking é apresentado como "do Senado". Sempre "entre os senadores em exercício em [data]".
- **O que aparece:** número idêntico nas bases, ou com divergência explicada, ou de fonte única que passou nas checagens. **O que não se comprova não aparece**, sem caixa de aviso e sem selos como "comprovado" ou "fonte única".
- **"De onde vem este número"** segue sempre o mesmo molde, em linguagem simples (sem "API", "consulta" ou siglas sem explicação): **onde o Senado publica**, **como chegamos neste número** e **atualizado em**, com o link para o portal do Senado.
- **Tudo ou nada (D025, D031).** Um dado que vale para todos os senadores só aparece se todos em exercício o tiverem e os dados baterem para todos. Se um só falhar, ninguém o recebe. **Exceção:** dados de contato (telefone, e-mail) aparecem para quem os tem.
- **Falhe fechado.** Se uma verificação quebrar, o número fica oculto e o motivo vai para o relatório de verificações. A prova real mostra consistência entre bases, não é auditoria; o site diz isso.
- **Toda informação exibida indica fonte e data de atualização.**
- **CPF nunca é exibido por inteiro, e pessoas físicas aparecem agrupadas, sem nome** (decisão D008; o mantenedor aceitou o risco de LGPD por serem dados públicos, e as proteções continuam). A coluna `CNPJ_CPF` traz CPFs completos de pessoas físicas. Veja a decisão D008 em [docs/decisoes.md](docs/decisoes.md).
- **Citação da fonte:** os termos do Senado exigem, no máximo, citar a proveniência. Toda página mostra a fonte e a data de atualização (D009). Detalhes dos termos em [docs/fontes-de-dados.md](docs/fontes-de-dados.md).
- **Fonte principal é a API;** o CSV serve para conferência (D005).

## 7. Stack aprovada

Python (Pandas, Pandera) para pipeline e verificação (scikit-learn só se o modelo voltar na versão 2); PostgreSQL no Neon como banco; FastAPI para a API; Next.js com TypeScript como site, exportado de forma estática no Cloudflare Pages; GitHub Actions para atualização diária; pytest, ruff e uv para qualidade. O motivo de cada escolha está no [README.md](README.md).

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
├── docs/            # índice, escopo, decisões, fontes de dados, verificações
├── design/          # protótipo da página do senador, folha da marca e favicon
├── data/            # README versionado; data/raw/ (dados baixados) fora do git
├── pipeline/        # (a criar) coleta, limpeza e verificação (Python)
├── api/             # (a criar) FastAPI
├── web/             # (a criar) site (Next.js)
└── .github/         # (a criar) automações
```

As pastas "a criar" nascem quando forem necessárias, não antes. Toda pasta criada ganha um `README.md` curto dizendo o que é ([D032](docs/decisoes.md#d032-organização-do-repositório-e-dos-documentos)).
