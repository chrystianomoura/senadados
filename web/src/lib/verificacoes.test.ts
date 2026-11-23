import { describe, expect, it } from "vitest";

import type { MotivoVerificacao, ResumoVerificacao } from "./types";
import { historico, motivosOrdenados, nomeConferencia, resumoAtual, senadores } from "./verificacoes";

const r = (verificacao: string, ano: number): ResumoVerificacao => ({
  verificacao, ano, identicos: 1, explicados: 0, pendentes: 0, ocultos: 0, verificado_em: "2026-11-23T10:00:00",
});

describe("verificações", () => {
  it("dá nome simples a cada conferência e mantém o código das desconhecidas", () => {
    expect(nomeConferencia("equipe")).toBe("Equipe do gabinete");
    expect(nomeConferencia("algo_novo")).toBe("algo_novo");
  });

  it("resumoAtual traz uma linha por conferência, a do ano mais recente, na ordem da página", () => {
    const linhas = resumoAtual([r("equipe", 2026), r("cota", 2008), r("cota", 2026), r("perfil_foto", 2026)]);
    expect(linhas.map((l) => [l.verificacao, l.ano])).toEqual([["cota", 2026], ["equipe", 2026], ["perfil_foto", 2026]]);
  });

  it("conferência desconhecida vai para o fim", () => {
    expect(resumoAtual([r("nova", 2026), r("cota", 2026)]).map((l) => l.verificacao)).toEqual(["cota", "nova"]);
  });

  it("historico lista os anos de uma conferência do mais recente para o mais antigo", () => {
    expect(historico([r("cota", 2008), r("equipe", 2026), r("cota", 2026)], "cota").map((l) => l.ano)).toEqual([2026, 2008]);
  });

  it("motivosOrdenados segue a ordem das conferências e depois o ano mais recente", () => {
    const m = (verificacao: string, ano: number): MotivoVerificacao => ({
      verificacao, ano, situacao: "oculto", motivo: "x", qtd: 1,
    });
    expect(motivosOrdenados([m("equipe", 2026), m("cota", 2008), m("cota", 2009)]).map((x) => [x.verificacao, x.ano]))
      .toEqual([["cota", 2009], ["cota", 2008], ["equipe", 2026]]);
  });

  it("senadores concorda com o número", () => {
    expect(senadores(1)).toBe("1 senador");
    expect(senadores(4)).toBe("4 senadores");
  });
});
