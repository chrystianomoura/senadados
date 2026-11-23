// Formatação em português do Brasil. Dinheiro chega em centavos inteiros; aqui vira texto.
// Espaços que não devem quebrar linha (dinheiro, telefone) usam o espaço sem quebra (U+00A0).

export const NBSP = " ";

const MESES = [
  "janeiro", "fevereiro", "março", "abril", "maio", "junho",
  "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
];

const ESTADOS: Record<string, string> = {
  AC: "Acre", AL: "Alagoas", AP: "Amapá", AM: "Amazonas", BA: "Bahia", CE: "Ceará",
  DF: "Distrito Federal", ES: "Espírito Santo", GO: "Goiás", MA: "Maranhão", MT: "Mato Grosso",
  MS: "Mato Grosso do Sul", MG: "Minas Gerais", PA: "Pará", PB: "Paraíba", PR: "Paraná",
  PE: "Pernambuco", PI: "Piauí", RJ: "Rio de Janeiro", RN: "Rio Grande do Norte",
  RS: "Rio Grande do Sul", RO: "Rondônia", RR: "Roraima", SC: "Santa Catarina",
  SP: "São Paulo", SE: "Sergipe", TO: "Tocantins",
};

const PARTICULAS = new Set(["de", "da", "do", "das", "dos", "e"]);

const moeda = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

/** "R$ 46.366,19" (com espaço sem quebra entre o R$ e o número). */
export function reais(centavos: number): string {
  return moeda.format(centavos / 100).replace(/\s/g, NBSP);
}

/** Milhares de reais, arredondados: 2.904.849 centavos viram 29. Menos de R$ 500 vira 0. */
export function milhares(centavos: number): number {
  return Math.round(centavos / 100 / 1000);
}

/** "R$ 29 mil". Abaixo de mil reais mostra o valor inteiro, para não virar "R$ 0 mil". */
export function reaisMil(centavos: number): string {
  if (Math.abs(centavos) < 100_000) return reais(centavos);
  return `R$${NBSP}${milhares(centavos).toLocaleString("pt-BR")}${NBSP}mil`;
}

export function nomeMes(mes: number): string {
  return MESES[mes - 1] ?? String(mes);
}

export function mesCurto(mes: number): string {
  return nomeMes(mes).slice(0, 3);
}

export function nomeEstado(uf: string): string {
  return ESTADOS[uf] ?? uf;
}

/** A sigla como o Senado publica ("S/Partido") vira "Sem Partido"; as demais ficam como estão. */
export function nomePartido(sigla: string): string {
  return sigla.trim().toLocaleLowerCase("pt-BR") === "s/partido" ? "Sem Partido" : sigla;
}

/** "ALAN RICK" -> "Alan Rick"; "RODRIGO DE OLIVEIRA" -> "Rodrigo de Oliveira". */
export function tituloNome(nome: string): string {
  return nome
    .toLocaleLowerCase("pt-BR")
    .split(/\s+/)
    .filter(Boolean)
    .map((palavra, i) =>
      i > 0 && PARTICULAS.has(palavra)
        ? palavra
        : palavra.charAt(0).toLocaleUpperCase("pt-BR") + palavra.slice(1),
    )
    .join(" ");
}

/** Duas letras para o avatar: a primeira do primeiro nome e a primeira do último. */
export function iniciais(nome: string): string {
  const palavras = tituloNome(nome)
    .split(" ")
    .filter((p) => !PARTICULAS.has(p));
  if (palavras.length === 0) return "?";
  if (palavras.length === 1) return palavras[0].charAt(0);
  return palavras[0].charAt(0) + palavras[palavras.length - 1].charAt(0);
}

/** Parte inteira do percentual, sem estourar quando o total é zero ou negativo. */
export function percentual(parte: number, total: number): number {
  if (total <= 0) return 0;
  return Math.round((Math.max(parte, 0) / total) * 100);
}

/** "outubro de 2026", com espaços que não quebram: a data nunca se parte no fim da linha. */
export function mesAno(mes: number, ano: number): string {
  return `${nomeMes(mes)}${NBSP}de${NBSP}${ano}`;
}

/** Cola o ano ao último mês de um período: "de janeiro a outubro" + 2026 -> "de janeiro a outubro de 2026". */
export function periodoAno(texto: string, ano: number): string {
  return `${texto.replace(/ (\S+)$/, `${NBSP}$1`)}${NBSP}de${NBSP}${ano}`.trim();
}

/** "de janeiro a outubro", "em outubro" ou "" (sem meses). */
export function periodo(meses: number[]): string {
  if (meses.length === 0) return "";
  const primeiro = Math.min(...meses);
  const ultimo = Math.max(...meses);
  return primeiro === ultimo
    ? `em ${nomeMes(primeiro)}`
    : `de ${nomeMes(primeiro)} a ${nomeMes(ultimo)}`;
}

/** "2023 a 2031": o ano em que o mandato começa e o ano em que termina, sem quebra de linha. */
export function mandatoTexto(inicio: number, fim: number): string {
  return `${inicio}${NBSP}a${NBSP}${fim}`;
}

/** "Usou em todos os 10 meses", "Usou em 3 de 10 meses" ou "Não usou em nenhum mês". */
export function usoTexto(usados: number, total: number): string {
  if (usados === 0) return "Não usou em nenhum mês";
  if (usados === total) return total === 1 ? "Usou no mês" : `Usou em todos os ${total} meses`;
  return `Usou em ${usados} de ${total} meses`;
}

/** Versão curta para os cartões: "usou nos 10 meses", "usou em 3 de 10 meses" ou "não usou". */
export function usoCurto(usados: number, total: number): string {
  if (usados === 0) return "não usou";
  if (usados === total) return total === 1 ? "usou no mês" : `usou nos ${total} meses`;
  return `usou em ${usados} de ${total} meses`;
}

export function telefone(texto: string): string {
  return texto.replace(/\s/g, NBSP);
}

/** "2026-11-18" -> "18/11/2026". */
export function dataBr(iso: string): string {
  const [ano, mes, dia] = iso.slice(0, 10).split("-");
  return `${dia}/${mes}/${ano}`;
}
