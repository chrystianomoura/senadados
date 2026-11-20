// Busca e filtros da lista de senadores. Funções puras, com testes, usadas pela home.
import { nomePartido, tituloNome } from "./formato";
import type { ItemLista } from "./types";

export interface Filtros {
  texto: string;
  uf: string; // "" = todos
  partido: string; // "" = todos
}

/** Minúsculas e sem acento, para "joao" achar "João". */
export function normaliza(texto: string): string {
  return texto
    .normalize("NFD")
    .replace(/\p{M}/gu, "")
    .toLocaleLowerCase("pt-BR")
    .trim();
}

/** Todas as palavras digitadas precisam aparecer no nome (em qualquer ordem). */
export function filtrar(senadores: ItemLista[], { texto, uf, partido }: Filtros): ItemLista[] {
  const palavras = normaliza(texto).split(/\s+/).filter(Boolean);
  return senadores.filter((s) => {
    if (uf && s.uf !== uf) return false;
    if (partido && s.partido !== partido) return false;
    const nome = normaliza(tituloNome(s.nome));
    return palavras.every((p) => nome.includes(p));
  });
}

/** Valores distintos de um campo, em ordem alfabética, para as listas de escolha. */
export function opcoes(senadores: ItemLista[], campo: "uf" | "partido"): string[] {
  // O partido é ordenado pelo nome que aparece na tela ("Sem Partido" fica entre as letras S).
  const rotulo = (v: string) => (campo === "partido" ? nomePartido(v) : v);
  return [...new Set(senadores.map((s) => s[campo]))].sort((a, b) =>
    rotulo(a).localeCompare(rotulo(b), "pt-BR"),
  );
}
