import { describe, expect, it } from "vitest";

import { anoPadrao, anosDisponiveis, enderecoDoAno } from "./anos";
import type { CotaAno, Perfil } from "./types";

const cota = (ano: number, meses: number): CotaAno => ({
  ano, parcial: false, total_centavos: 1, categorias: [], maior_mes: { mes: 1, total_centavos: 1 },
  meses: Array.from({ length: meses }, (_, i) => ({ mes: i + 1, total_centavos: 1 })),
});

const perfil = (anos: CotaAno[], agora = true): Perfil =>
  ({
    cota: anos.length ? { anos } : null,
    salario: agora ? { ano: 2026, mes: 10, basica_centavos: 1, liquida_centavos: 1 } : null,
    equipe: null, contato: null, moradia: null, fornecedores: null,
  }) as unknown as Perfil;

describe("anos da página do senador", () => {
  it("oferece o ano dos dados e o anterior, do mais recente para o mais antigo", () => {
    expect(anosDisponiveis(perfil([cota(2024, 12), cota(2025, 12), cota(2026, 9)]), 2026)).toEqual([2026, 2025]);
  });

  it("não oferece um ano sem verba provada", () => {
    expect(anosDisponiveis(perfil([cota(2026, 9)]), 2026)).toEqual([2026]);
    expect(anosDisponiveis(perfil([cota(2025, 12)], false), 2026)).toEqual([2025]);
  });

  it("senador sem verba mas com dado de agora ainda tem o ano dos dados", () => {
    expect(anosDisponiveis(perfil([]), 2026)).toEqual([2026]);
  });

  it("abre o ano atual quando a verba dele já tem dois meses ou mais", () => {
    expect(anoPadrao(perfil([cota(2025, 12), cota(2026, 2)]), 2026)).toBe(2026);
  });

  it("abre o ano anterior enquanto o atual tem um mês só", () => {
    expect(anoPadrao(perfil([cota(2025, 12), cota(2026, 1)]), 2026)).toBe(2025);
  });

  it("abre o ano atual se ele é o único, mesmo com um mês só", () => {
    expect(anoPadrao(perfil([cota(2026, 1)]), 2026)).toBe(2026);
  });

  it("o ano padrão fica no endereço do senador e o outro leva o ano", () => {
    expect(enderecoDoAno("alan-rick", 2026, 2026)).toBe("/senador/alan-rick/");
    expect(enderecoDoAno("alan-rick", 2025, 2026)).toBe("/senador/alan-rick/2025/");
  });
});
