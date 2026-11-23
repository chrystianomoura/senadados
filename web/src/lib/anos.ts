// Os anos que o site mostra na página do senador (D048): o dos dados e o anterior. O que vale para um
// instante (salário, equipe, moradia e contato) só aparece no ano dos dados; a verba e os fornecedores
// existem por ano, e é por eles que o cidadão troca de ano.
import type { Perfil } from "./types";

/** Anos que a página do senador pode mostrar, do mais recente para o mais antigo. */
export function anosDisponiveis(p: Perfil, anoDosDados: number): number[] {
  const comCota = (p.cota?.anos ?? []).map((a) => a.ano);
  const temDadoDeAgora = Boolean(
    p.salario || p.equipe || p.contato || p.moradia?.anos.some((a) => a.ano === anoDosDados),
  );
  const anos = new Set<number>();
  for (const ano of [anoDosDados, anoDosDados - 1]) {
    if (comCota.includes(ano) || (ano === anoDosDados && temDadoDeAgora)) anos.add(ano);
  }
  if (anos.size === 0) anos.add(anoDosDados);
  return [...anos].sort((a, b) => b - a);
}

/**
 * O ano que a página abre: o atual, quando a verba dele já tem pelo menos dois meses; senão o anterior,
 * se houver. Com um mês só, "o mês de maior uso" e a média não dizem nada (D030).
 */
export function anoPadrao(p: Perfil, anoDosDados: number): number {
  const anos = anosDisponiveis(p, anoDosDados);
  const meses = p.cota?.anos.find((a) => a.ano === anoDosDados)?.meses.length ?? 0;
  if (anos.includes(anoDosDados) && (meses >= 2 || anos.length === 1)) return anoDosDados;
  return anos.find((a) => a !== anoDosDados) ?? anoDosDados;
}

/** O endereço da página de um ano: o ano padrão fica no endereço do senador, sem o ano. */
export function enderecoDoAno(slug: string, ano: number, padrao: number): string {
  return ano === padrao ? `/senador/${slug}/` : `/senador/${slug}/${ano}/`;
}
