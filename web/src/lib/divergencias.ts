// Os casos da seção "Onde os dados do Senado não batem entre si" (D038). O texto espelha
// docs/divergencias-nos-dados-do-senado.md e as imagens vêm de docs/evidencias/. Só entra caso com imagem, e
// só caso que toca dado que o site mostra: os de 2008, 2009 e 2024 saíram com a regra dos dois anos (D048).

/** Dia em que as imagens e os números dos casos foram capturados de novo. Muda junto com as imagens. */
export const CAPTURADO_EM = "23/11/2026";

export interface Imagem {
  arquivo: string;
  alt: string;
}

export interface Caso {
  id: string;
  titulo: string;
  onde: string;
  /** Parágrafos, cada um seguido das imagens que o ilustram. */
  blocos: { texto: string; imagens: Imagem[] }[];
  argumento: string;
  comoConferir: string;
  /** O que o Senadados faz com o caso. */
  noSite: string;
}

export const CASOS: Caso[] = [
  {
    id: "gabinete-27-ou-28",
    titulo: "A tela diz 27 pessoas; a exportação da mesma tela diz 28",
    onde: "Página “Recursos Utilizados em 2026” do senador Camilo Santana, bloco “Pessoal”, e o botão “Exportar HTML” da mesma página.",
    blocos: [
      {
        texto: "Na tela do portal, o gabinete tem 27 pessoas, todas comissionadas.",
        imagens: [{ arquivo: "01-portal-camilo-pessoal.png", alt: "Tela do portal de transparência: gabinete do senador Camilo Santana com 27 pessoas, todas comissionadas" }],
      },
      {
        texto: "Na exportação da mesma página, gerada às 17h56 de 23/11/2026, o gabinete tem 28 pessoas: 27 comissionadas e 1 efetiva.",
        imagens: [{ arquivo: "02-exportacao-camilo-pessoal.png", alt: "Relatório exportado pelo Senado: gabinete do senador Camilo Santana com 28 pessoas, sendo 27 comissionadas e 1 efetiva" }],
      },
    ],
    argumento: "Em 18/11/2026, o Senadados comparou a tela com a exportação nos 81 gabinetes, nos três tipos de vínculo que as duas publicam: em 80 elas concordavam e neste não. Essa contagem não foi refeita em 23/11/2026.",
    comoConferir: "Abra www6g.senado.leg.br/transparencia/sen/6336/?ano=2026, role até “Pessoal” e use “Exportar → HTML” na parte de cima da página.",
    noSite: "O número de pessoas desse gabinete não aparece; os outros aparecem.",
  },
  {
    id: "gabinete-22-ou-17",
    titulo: "“Gabinete: 22 pessoas” ou “Gabinete: 17 pessoas”?",
    onde: "Página “Recursos Utilizados em 2026” do senador Alan Rick, bloco “Pessoal”, e a exportação da mesma página.",
    blocos: [
      {
        texto: "A tela mostra 22 pessoas no gabinete: 14 comissionadas, 3 efetivas, 1 estagiária e 4 terceirizadas.",
        imagens: [{ arquivo: "03-portal-alan-pessoal.png", alt: "Tela do portal de transparência: gabinete do senador Alan Rick com 22 pessoas, somando comissionados, efetivos, estagiários e terceirizados" }],
      },
      {
        texto: "A exportação da mesma página mostra 17 pessoas, sem estagiários nem terceirizados.",
        imagens: [{ arquivo: "04-exportacao-alan-pessoal.png", alt: "Relatório exportado pelo Senado: gabinete do senador Alan Rick com 17 pessoas, sendo 14 comissionadas e 3 efetivas" }],
      },
    ],
    argumento: "As duas publicações usam o mesmo rótulo, “Gabinete”, para totais diferentes, e a exportação não traz nota dizendo que deixa de fora estagiários e terceirizados. Em 18/11/2026, o total da tela e o da exportação eram diferentes em 79 dos 81 gabinetes (contagem não refeita em 23/11/2026).",
    comoConferir: "Abra www6g.senado.leg.br/transparencia/sen/5672/?ano=2026, veja o bloco “Pessoal” e compare com “Exportar → HTML”.",
    noSite: "O Senadados usa o total da exportação (comissionados, efetivos e requisitados) e diz o que ele inclui.",
  },
  {
    id: "linhas-sem-categoria",
    titulo: "Linhas de despesa sem categoria que a tela não conta",
    onde: "Página “Recursos Utilizados em 2026” do senador Hamilton Mourão, bloco “Cotas”, e o arquivo oficial de despesas de 2026.",
    blocos: [
      {
        texto: "A tela mostra um total de cota de R$ 448.186,05, somando as sete categorias.",
        imagens: [{ arquivo: "09-portal-mourao-2026.png", alt: "Tela do portal de transparência: cota de 2026 do senador Hamilton Mourão, com total de R$ 448.186,05" }],
      },
      {
        texto: "O arquivo oficial de 2026 soma R$ 483.186,05 para o mesmo senador. A diferença, de R$ 35.000,00, é exatamente a soma de 10 linhas em que a categoria da despesa está em branco.",
        imagens: [{ arquivo: "10-arquivo-mourao-2026.png", alt: "Linhas do arquivo oficial com categoria em branco para o senador Hamilton Mourão e a conta da diferença" }],
      },
    ],
    argumento: "Essas linhas existem no arquivo de dados abertos, com valor e data, mas a tela não as conta em nenhuma das sete categorias. Quem soma as sete categorias da tela chega a um número menor do que quem soma o arquivo. Aqui a diferença tem uma explicação, e ela está nas linhas sem categoria; na tela não há nota dizendo que elas ficam de fora.",
    comoConferir: "Abra www6g.senado.leg.br/transparencia/sen/6341/?ano=2026, anote o “Total” e compare com a soma de VALOR_REEMBOLSADO do arquivo despesa_ceaps_2026.csv para “HAMILTON MOURAO”. Depois some só as linhas com TIPO_DESPESA em branco.",
    noSite: "As linhas aparecem, como “Sem categoria”, com a explicação.",
  },
];
