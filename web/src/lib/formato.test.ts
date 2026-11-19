import { describe, expect, it } from "vitest";

import {
  NBSP, dataBr, iniciais, mesCurto, milhares, nomeEstado, nomeMes, percentual, periodo, reais,
  reaisMil, telefone, tituloNome, usoTexto,
} from "./formato";

describe("dinheiro", () => {
  it("formata centavos em reais, sem quebrar o R$ do número", () => {
    expect(reais(4636619)).toBe(`R$${NBSP}46.366,19`);
    expect(reais(0)).toBe(`R$${NBSP}0,00`);
  });

  it("arredonda para milhares", () => {
    expect(milhares(2_904_849)).toBe(29);
    expect(milhares(40_000)).toBe(0);
  });

  it("mostra 'R$ N mil' a partir de mil reais e o valor inteiro abaixo disso", () => {
    expect(reaisMil(2_904_849)).toBe(`R$${NBSP}29${NBSP}mil`);
    expect(reaisMil(5_406_297)).toBe(`R$${NBSP}54${NBSP}mil`);
    expect(reaisMil(78_000)).toBe(`R$${NBSP}780,00`);
  });
});

describe("nomes", () => {
  it("põe o nome do senador em formato de leitura", () => {
    expect(tituloNome("ALAN RICK")).toBe("Alan Rick");
    expect(tituloNome("RODRIGO DE OLIVEIRA")).toBe("Rodrigo de Oliveira");
    expect(tituloNome("MARIA DAS GRAÇAS E SILVA")).toBe("Maria das Graças e Silva");
  });

  it("gera as iniciais sem as partículas", () => {
    expect(iniciais("ALAN RICK")).toBe("AR");
    expect(iniciais("RODRIGO DE OLIVEIRA")).toBe("RO");
    expect(iniciais("ZEQUINHA")).toBe("Z");
  });

  it("traduz a UF e cai na própria sigla se não conhecer", () => {
    expect(nomeEstado("AC")).toBe("Acre");
    expect(nomeEstado("XX")).toBe("XX");
  });
});

describe("meses e períodos", () => {
  it("nomeia os meses", () => {
    expect(nomeMes(3)).toBe("março");
    expect(mesCurto(10)).toBe("out");
  });

  it("descreve o período dos meses presentes", () => {
    expect(periodo([1, 2, 3, 10])).toBe("de janeiro a outubro");
    expect(periodo([10])).toBe("em outubro");
    expect(periodo([])).toBe("");
  });

  it("conta o uso de moradia", () => {
    expect(usoTexto(0, 10)).toBe("Não usou em nenhum mês");
    expect(usoTexto(10, 10)).toBe("Usou em todos os 10 meses");
    expect(usoTexto(3, 10)).toBe("Usou em 3 de 10 meses");
  });
});

describe("outros", () => {
  it("calcula percentual sem dividir por zero nem usar valor negativo", () => {
    expect(percentual(25, 100)).toBe(25);
    expect(percentual(5, 0)).toBe(0);
    expect(percentual(-5, 100)).toBe(0);
  });

  it("mantém o telefone numa linha só", () => {
    expect(telefone("(61) 3303-0001")).toBe(`(61)${NBSP}3303-0001`);
  });

  it("escreve a data como no Brasil", () => {
    expect(dataBr("2026-11-18")).toBe("18/11/2026");
    expect(dataBr("2026-11-18T12:00:00+00:00")).toBe("18/11/2026");
  });
});
