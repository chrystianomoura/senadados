// Apresentação da página "Verificações": nomes em linguagem simples e a ordem das conferências.
import type { MotivoVerificacao, ResumoVerificacao } from "./types";

/** Cada conferência, na ordem em que aparece na página, com o nome que o cidadão entende. */
const CONFERENCIAS: [string, string][] = [
  ["cota", "Verba do mandato (cota)"],
  ["salario", "Salário"],
  ["equipe", "Equipe do gabinete"],
  ["moradia", "Moradia"],
  ["contato_endereco", "Endereço do gabinete"],
  ["contato_telefones", "Telefones do gabinete"],
  ["contato_email", "E-mail do gabinete"],
  ["perfil_foto", "Foto do senador"],
  ["perfil_mandato", "Mandato do senador"],
];

export function nomeConferencia(chave: string): string {
  return CONFERENCIAS.find(([k]) => k === chave)?.[1] ?? chave;
}

function posicao(chave: string): number {
  const i = CONFERENCIAS.findIndex(([k]) => k === chave);
  return i === -1 ? CONFERENCIAS.length : i;
}

/** Uma linha por conferência, a do ano mais recente, na ordem da página. */
export function resumoAtual(resumo: ResumoVerificacao[]): ResumoVerificacao[] {
  const maisRecente = new Map<string, ResumoVerificacao>();
  for (const r of resumo) {
    const atual = maisRecente.get(r.verificacao);
    if (!atual || r.ano > atual.ano) maisRecente.set(r.verificacao, r);
  }
  return [...maisRecente.values()].sort((a, b) => posicao(a.verificacao) - posicao(b.verificacao));
}

/** Todos os anos de uma conferência, do mais recente para o mais antigo. */
export function historico(resumo: ResumoVerificacao[], chave: string): ResumoVerificacao[] {
  return resumo.filter((r) => r.verificacao === chave).sort((a, b) => b.ano - a.ano);
}

/** Os motivos de quem ficou de fora, na ordem das conferências e, dentro de cada uma, do ano mais recente. */
export function motivosOrdenados(motivos: MotivoVerificacao[]): MotivoVerificacao[] {
  return [...motivos].sort(
    (a, b) => posicao(a.verificacao) - posicao(b.verificacao) || b.ano - a.ano,
  );
}

/** "1 senador" ou "4 senadores". */
export function senadores(qtd: number): string {
  return qtd === 1 ? "1 senador" : `${qtd} senadores`;
}
