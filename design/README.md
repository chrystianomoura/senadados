# Design

Protótipo e identidade visual do site. **São páginas estáticas de referência**, feitas antes do código, para o site final seguir.

| Arquivo | O que é |
|---|---|
| [perfil-do-senador.html](perfil-do-senador.html) | Protótipo da página do senador (a tela principal). Abre direto no navegador |
| [identidade.html](identidade.html) | Folha da marca: logo, favicon, cores e fontes |
| `assets/` | `favicon.svg` e PNGs (32, 180 e 512 px). O `.ico` não foi gerado |

## Atenção

- O senador do protótipo é **fictício** ("Senadora Exemplo Alves"). Os valores são de exemplo, **exceto** a distribuição da cota entre os 81 senadores, que é real e anônima.
- Fontes: Fraunces, Hanken Grotesk e Bricolage Grotesque, carregadas do Google Fonts (gratuitas).
- Decisões de identidade e de exibição: [D029](../docs/decisoes.md#d029-identidade-visual) e [docs/escopo.md](../docs/escopo.md).
- A logo é provisória: o anel verde, sem contorno. Uma versão final por um designer é pendência.
- O site em Next.js (`web/`) nasceu destas páginas e **já passou delas**: os textos (por exemplo "Quem recebeu o dinheiro?" e "remuneração básica"), o resumo e o cartão do senador mudaram em 20/11/2026. Em caso de diferença, vale o site e o [D046](../docs/decisoes.md#d046-site-em-nextjs-16-com-exportação-estática-fontes-hospedadas-e-testes-com-vitest). O protótipo fica como referência da identidade visual, não como especificação.
