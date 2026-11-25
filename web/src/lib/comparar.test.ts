import { describe, expect, it } from "vitest";

import { guias, resumir } from "./comparar";
import { NBSP } from "./formato";
import type { Perfil } from "./types";

// Perfis inventados, só com o que a comparação lê.
function perfil(nome: string, extra: Partial<Perfil> = {}): Perfil {
  return {
    codigo: 1, slug: nome.toLowerCase(), nome, tipo: "Titular", uf: "AC", partido: "X",
    quem_e: null, salario: null, cota: null, fornecedores: null, equipe: null, contato: null, moradia: null,
    ...extra,
  };
}

const cota = (total: number, categoria = "Locomoção, hospedagem e alimentação") => ({
  anos: [{
    ano: 2026, parcial: true, total_centavos: total,
    meses: [{ mes: 1, total_centavos: total / 2 }, { mes: 2, total_centavos: total / 2 }],
    categorias: [{ nome: categoria, nome_oficial: categoria, total_centavos: total }],
    maior_mes: { mes: 1, total_centavos: total / 2 },
  }],
});

const ANA = perfil("ANA", {
  salario: { ano: 2026, mes: 10, basica_centavos: 4636619, liquida_centavos: 3310000 },
  cota: cota(23_800_000),
  fornecedores: { anos: [{ ano: 2026, empresas: [], total_empresas: 41, agrupados: [] }] },
  equipe: { ano: 2026, pessoas: 18 },
  moradia: { anos: [{ ano: 2026, meses: [{ mes: "2026-01", auxilio_moradia: false, imovel_funcional: true }] }] },
});
const BRUNO = perfil("BRUNO", {
  salario: { ano: 2026, mes: 10, basica_centavos: 4636619, liquida_centavos: 2985000 },
  cota: cota(30_100_000, "Passagens dentro do Brasil"),
  fornecedores: { anos: [{ ano: 2026, empresas: [], total_empresas: 63, agrupados: [] }] },
  equipe: { ano: 2026, pessoas: 22 },
  moradia: { anos: [{ ano: 2026, meses: [{ mes: "2026-01", auxilio_moradia: true, imovel_funcional: false }] }] },
});

describe("comparação de dois senadores", () => {
  const g = guias(resumir(ANA, 2026), resumir(BRUNO, 2026), 2026);

  it("traz as seis guias do perfil, na ordem", () => {
    expect(g.map((x) => x.id)).toEqual(["salario", "verba", "categorias", "fornecedores", "equipe", "moradia"]);
  });

  it("diz quem tem mais, em palavras neutras", () => {
    const verba = g.find((x) => x.id === "verba")!;
    expect(verba.frase).toContain("Bruno usou");
    expect(verba.frase).toContain("a mais da verba");
    expect(verba.diferenca).toBe(`R$${NBSP}63${NBSP}mil`);
    expect(g.find((x) => x.id === "equipe")!.diferenca).toBe("4 pessoas");
    expect(JSON.stringify(g)).not.toMatch(/gastou|suspeit|irregular/i);
  });

  it("diz que o salário-base é igual quando é", () => {
    const sal = g.find((x) => x.id === "salario")!;
    expect(sal.frase).toContain("Ana fica com");
    expect(sal.frase).toContain("O salário-base dos dois é igual");
  });

  it("diz quem tem o número maior, só onde o número é comparável", () => {
    const maior = Object.fromEntries(g.map((x) => [x.id, x.maior]));
    expect(maior).toEqual({
      salario: "a", verba: "b", categorias: null, fornecedores: "b", equipe: "b", moradia: null,
    });
  });

  it("compara categorias diferentes sem calcular diferença", () => {
    const cat = g.find((x) => x.id === "categorias")!;
    expect(cat.diferenca).toBeNull();
    expect(cat.frase).toContain("A maior fatia de Ana");
  });

  it("empate não destaca ninguém", () => {
    const igual = guias(resumir(ANA, 2026), resumir({ ...ANA, nome: "ANA2", slug: "ana2" }, 2026), 2026);
    for (const guia of igual.filter((x) => ["salario", "verba", "fornecedores", "equipe"].includes(x.id))) {
      expect(guia.maior).toBeNull();
      expect(guia.diferenca).toBeNull();
      expect(guia.frase).toMatch(/mesmo/);
    }
  });

  it("guarda o mês a mês e o maior mês só com dois meses ou mais", () => {
    expect(resumir(ANA, 2026).verba?.meses).toHaveLength(2);
    expect(resumir(ANA, 2026).verba?.maiorMes).toEqual({ mes: 1, total_centavos: 11_900_000 });
    const umMes = perfil("DUDA", { cota: { anos: [{ ...cota(100_000).anos[0], meses: [{ mes: 3, total_centavos: 100_000 }] }] } });
    expect(resumir(umMes, 2026).verba?.maiorMes).toBeNull();
  });

  it("calcula a fatia de cada categoria sobre o total do próprio senador", () => {
    expect(resumir(ANA, 2026).verba?.categorias[0]).toMatchObject({ nome: "Locomoção, hospedagem e alimentação", pct: 100 });
  });

  it("não compara o que um dos dois não tem: mostra 'sem dado' e não estima", () => {
    const sem = guias(resumir(ANA, 2026), resumir(perfil("CARLA"), 2026), 2026);
    for (const guia of sem) {
      expect(guia.b).toBeNull();
      expect(guia.diferenca).toBeNull();
      expect(guia.frase).toContain("Não há dado comprovado de Carla");
    }
  });

  it("ignora dado de outro ano", () => {
    expect(resumir(ANA, 2025).salario).toBeNull();
    expect(resumir(ANA, 2025).equipe).toBeNull();
  });

  it("resume a moradia", () => {
    expect(resumir(ANA, 2026).moradia).toEqual({ texto: "Imóvel funcional", imovel: 1, auxilio: 0, usados: 1, meses: 1 });
    expect(resumir(BRUNO, 2026).moradia?.texto).toBe("Auxílio-moradia");
  });
});
