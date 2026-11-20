import { describe, expect, it } from "vitest";

import { filtrar, normaliza, opcoes } from "./busca";
import type { ItemLista } from "./types";

const senadores: ItemLista[] = [
  { codigo: 1, slug: "alan-rick", nome: "ALAN RICK", tipo: "Titular", uf: "AC", partido: "REPUBLICANOS" },
  { codigo: 2, slug: "angelo-coronel", nome: "ÂNGELO CORONEL", tipo: "Titular", uf: "BA", partido: "PSD" },
  { codigo: 3, slug: "jose-de-souza", nome: "JOSÉ DE SOUZA", tipo: "1º Suplente", uf: "BA", partido: "PT" },
];

const todos = { texto: "", uf: "", partido: "" };

describe("normaliza", () => {
  it("tira acento e maiúsculas", () => {
    expect(normaliza("  ÂNGELO José ")).toBe("angelo jose");
  });
});

describe("filtrar", () => {
  it("sem filtro devolve todos, na mesma ordem", () => {
    expect(filtrar(senadores, todos).map((s) => s.codigo)).toEqual([1, 2, 3]);
  });

  it("acha pelo nome sem exigir acento", () => {
    expect(filtrar(senadores, { ...todos, texto: "angelo" }).map((s) => s.codigo)).toEqual([2]);
    expect(filtrar(senadores, { ...todos, texto: "JOSE" }).map((s) => s.codigo)).toEqual([3]);
  });

  it("exige todas as palavras, em qualquer ordem", () => {
    expect(filtrar(senadores, { ...todos, texto: "rick alan" }).map((s) => s.codigo)).toEqual([1]);
    expect(filtrar(senadores, { ...todos, texto: "alan souza" })).toEqual([]);
  });

  it("filtra por estado e por partido, e combina com o nome", () => {
    expect(filtrar(senadores, { ...todos, uf: "BA" }).map((s) => s.codigo)).toEqual([2, 3]);
    expect(filtrar(senadores, { ...todos, partido: "PT" }).map((s) => s.codigo)).toEqual([3]);
    expect(filtrar(senadores, { texto: "jose", uf: "BA", partido: "PSD" })).toEqual([]);
  });
});

describe("opcoes", () => {
  it("lista os valores distintos em ordem alfabética", () => {
    expect(opcoes(senadores, "uf")).toEqual(["AC", "BA"]);
    expect(opcoes(senadores, "partido")).toEqual(["PSD", "PT", "REPUBLICANOS"]);
  });
});
