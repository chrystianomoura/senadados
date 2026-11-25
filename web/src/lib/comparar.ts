// Comparação de dois senadores (D021, D050): funções puras que resumem o perfil de um ano e montam, guia a
// guia, o que a tela mostra. Só usa dado provado: o que um dos dois não tem vira "sem dado" e nunca é
// estimado (D025). Sem julgamento: a frase diz "a mais" e "a menos", nunca "gastou demais" (D010).
import { percentual, periodo, reais, reaisMil, tituloNome } from "./formato";
import type { MesTotal, Perfil } from "./types";

export interface Resumo {
  codigo: number;
  slug: string;
  nome: string;
  uf: string;
  partido: string;
  foto_url: string | null;
  salario: { base: number; liquida: number } | null;
  verba: {
    total: number;
    media: number;
    periodo: string;
    meses: MesTotal[];
    /** Só quando há dois meses ou mais: com um só, "o maior" não diz nada (D030). */
    maiorMes: MesTotal | null;
    categorias: { nome: string; total: number; pct: number }[];
  } | null;
  empresas: number | null;
  /** As três empresas que mais receberam (nome como o Senado publica). */
  maioresEmpresas: { nome: string; total: number }[];
  equipe: number | null;
  moradia: { texto: string; imovel: number; auxilio: number; usados: number; meses: number } | null;
}

export interface Lado {
  principal: string;
  sub: string;
  /** Número para a barra, na mesma escala do outro senador. `null` quando não há barra. */
  num: number | null;
}

export interface Guia {
  id: "salario" | "verba" | "categorias" | "fornecedores" | "equipe" | "moradia";
  titulo: string;
  a: Lado | null;
  b: Lado | null;
  /** Quem tem o número maior. `null` quando empata, não há como medir ou os dois são de tipos diferentes. */
  maior: "a" | "b" | null;
  /** "R$ 63 mil", "4 pessoas"... ou `null` quando não há como medir a diferença. */
  diferenca: string | null;
  frase: string;
}

const plural = (n: number, um: string, varios: string) => `${n} ${n === 1 ? um : varios}`;

/** O que a comparação precisa de um perfil, para um ano. Dado que não vale para o ano fica `null`. */
export function resumir(p: Perfil, ano: number): Resumo {
  const cota = p.cota?.anos.find((a) => a.ano === ano) ?? null;
  const meses = cota?.meses.map((m) => m.mes) ?? [];
  const nMeses = meses.length ? Math.max(...meses) - Math.min(...meses) + 1 : 1;
  const m = p.moradia?.anos.find((a) => a.ano === ano) ?? null;
  const imovel = m?.meses.filter((x) => x.imovel_funcional).length ?? 0;
  const auxilio = m?.meses.filter((x) => x.auxilio_moradia).length ?? 0;
  const forn = p.fornecedores?.anos.find((a) => a.ano === ano) ?? null;
  return {
    codigo: p.codigo,
    slug: p.slug,
    nome: p.nome,
    uf: p.uf,
    partido: p.partido,
    foto_url: p.quem_e?.foto?.url ?? null,
    salario:
      p.salario?.ano === ano
        ? { base: p.salario.basica_centavos, liquida: p.salario.liquida_centavos }
        : null,
    verba: cota
      ? {
          total: cota.total_centavos,
          media: Math.round(cota.total_centavos / nMeses),
          periodo: periodo(meses),
          meses: cota.meses,
          maiorMes: cota.meses.length > 1 ? cota.maior_mes : null,
          categorias: cota.categorias.map((c) => ({
            nome: c.nome,
            total: c.total_centavos,
            pct: percentual(c.total_centavos, cota.total_centavos),
          })),
        }
      : null,
    empresas: forn?.total_empresas ?? null,
    maioresEmpresas: (forn?.empresas ?? []).slice(0, 3).map((e) => ({ nome: e.nome, total: e.total_centavos })),
    equipe: p.equipe?.ano === ano ? p.equipe.pessoas : null,
    moradia: m
      ? {
          texto:
            imovel > 0 && auxilio > 0
              ? "Imóvel e auxílio"
              : imovel > 0
                ? "Imóvel funcional"
                : auxilio > 0
                  ? "Auxílio-moradia"
                  : "Não usou",
          imovel,
          auxilio,
          usados: m.meses.filter((x) => x.imovel_funcional || x.auxilio_moradia).length,
          meses: m.meses.length,
        }
      : null,
  };
}

interface Textos {
  /** `{dif}` vira a diferença formatada. */
  maisA: string;
  maisB: string;
  igual: string;
}

/** Diferença, frase e quem tem mais, numa guia em que os dois têm um número comparável. */
function numerica(
  na: number,
  nb: number,
  formatar: (dif: number) => string,
  t: Textos,
): Pick<Guia, "diferenca" | "frase" | "maior"> {
  const dif = Math.abs(na - nb);
  if (dif === 0) return { diferenca: null, frase: t.igual, maior: null };
  const texto = formatar(dif);
  return na > nb
    ? { diferenca: texto, frase: t.maisA.replace("{dif}", texto), maior: "a" }
    : { diferenca: texto, frase: t.maisB.replace("{dif}", texto), maior: "b" };
}

function semDado(nomeA: string, nomeB: string, temA: boolean, temB: boolean): string {
  if (!temA && !temB) return "Nenhum dos dois tem dado comprovado nesta pergunta.";
  const quem = temA ? nomeB : nomeA;
  return `Não há dado comprovado de ${quem} nesta pergunta, então não dá para comparar.`;
}

/** As seis guias do perfil, lado a lado. Cada uma traz só o que foi provado para os dois. */
export function guias(a: Resumo, b: Resumo, ano: number): Guia[] {
  const A = tituloNome(a.nome);
  const B = tituloNome(b.nome);
  const vazio = { diferenca: null, maior: null } as const;

  const salario = (): Guia => {
    const base = { id: "salario", titulo: "Quanto ganha?" } as const;
    const lado = (r: Resumo): Lado | null =>
      r.salario && {
        principal: reais(r.salario.liquida),
        sub: `depois dos descontos · salário-base ${reais(r.salario.base)}`,
        num: r.salario.liquida,
      };
    if (!a.salario || !b.salario) {
      return { ...base, a: lado(a), b: lado(b), ...vazio, frase: semDado(A, B, !!a.salario, !!b.salario) };
    }
    const n = numerica(a.salario.liquida, b.salario.liquida, reais, {
      maisA: `Depois dos descontos, ${A} fica com {dif} a mais.`,
      maisB: `Depois dos descontos, ${B} fica com {dif} a mais.`,
      igual: "Os dois ficam com o mesmo valor depois dos descontos.",
    });
    const complemento =
      a.salario.base === b.salario.base
        ? ` O salário-base dos dois é igual: ${reais(a.salario.base)}.`
        : ` O salário-base é ${reais(a.salario.base)} para ${A} e ${reais(b.salario.base)} para ${B}.`;
    return { ...base, a: lado(a), b: lado(b), ...n, frase: n.frase + complemento };
  };

  const verba = (): Guia => {
    const base = { id: "verba", titulo: "Quanto usou da verba do mandato?" } as const;
    const lado = (r: Resumo): Lado | null =>
      r.verba && {
        principal: reaisMil(r.verba.total),
        sub: `${r.verba.periodo}, média de ${reaisMil(r.verba.media)} por mês`,
        num: r.verba.total,
      };
    if (!a.verba || !b.verba) {
      return { ...base, a: lado(a), b: lado(b), ...vazio, frase: semDado(A, B, !!a.verba, !!b.verba) };
    }
    const n = numerica(a.verba.total, b.verba.total, reaisMil, {
      maisA: `${A} usou {dif} a mais da verba em ${ano}.`,
      maisB: `${B} usou {dif} a mais da verba em ${ano}.`,
      igual: `Os dois usaram o mesmo valor da verba em ${ano}.`,
    });
    const aviso =
      a.verba.periodo === b.verba.periodo
        ? ""
        : " Os períodos com notas não são os mesmos; a média por mês ajuda a comparar.";
    return { ...base, a: lado(a), b: lado(b), ...n, frase: n.frase + aviso };
  };

  const categorias = (): Guia => {
    const base = { id: "categorias", titulo: "Em que usou a verba?" } as const;
    const lado = (r: Resumo): Lado | null => {
      const maior = r.verba?.categorias[0];
      return maior ? { principal: maior.nome, sub: `${maior.pct}% da verba`, num: maior.pct } : null;
    };
    const ma = a.verba?.categorias[0];
    const mb = b.verba?.categorias[0];
    if (!ma || !mb) {
      return { ...base, a: lado(a), b: lado(b), ...vazio, frase: semDado(A, B, !!ma, !!mb) };
    }
    const mesma = ma.nome === mb.nome;
    return {
      ...base,
      a: lado(a),
      b: lado(b),
      maior: null,
      diferenca: null,
      frase: mesma
        ? `A maior fatia dos dois é ${ma.nome}: ${ma.pct}% da verba de ${A} e ${mb.pct}% da de ${B}.`
        : `A maior fatia de ${A} foi ${ma.nome} (${ma.pct}%). A de ${B} foi ${mb.nome} (${mb.pct}%).`,
    };
  };

  const contagem = (
    id: "fornecedores" | "equipe",
    titulo: string,
    na: number | null,
    nb: number | null,
    [um, varios]: [string, string],
    sub: string,
    mais: (quem: string) => string,
    igual: string,
  ): Guia => {
    const lado = (n: number | null): Lado | null => (n !== null ? { principal: plural(n, um, varios), sub, num: n } : null);
    if (na === null || nb === null) {
      return { id, titulo, a: lado(na), b: lado(nb), ...vazio, frase: semDado(A, B, na !== null, nb !== null) };
    }
    const n = numerica(na, nb, (d) => plural(d, um, varios), {
      maisA: mais(A),
      maisB: mais(B),
      igual,
    });
    return { id, titulo, a: lado(na), b: lado(nb), ...n };
  };

  const moradia = (): Guia => {
    const base = { id: "moradia", titulo: "Usa moradia do Senado?" } as const;
    const lado = (r: Resumo): Lado | null =>
      r.moradia && {
        principal: r.moradia.texto,
        sub: r.moradia.usados === 0 ? "nenhum mês do ano" : `em ${r.moradia.usados} de ${r.moradia.meses} meses`,
        num: r.moradia.usados,
      };
    const descreve = (r: Resumo) =>
      !r.moradia || r.moradia.usados === 0
        ? "não usou nenhum benefício"
        : `${r.moradia.texto.toLowerCase()} em ${r.moradia.usados} de ${r.moradia.meses} meses`;
    if (!a.moradia || !b.moradia) {
      return { ...base, a: lado(a), b: lado(b), ...vazio, frase: semDado(A, B, !!a.moradia, !!b.moradia) };
    }
    const dif = Math.abs(a.moradia.usados - b.moradia.usados);
    return {
      ...base,
      a: lado(a),
      b: lado(b),
      maior: null,
      diferenca: dif === 0 ? null : plural(dif, "mês", "meses"),
      frase: `${A}: ${descreve(a)}. ${B}: ${descreve(b)}.`,
    };
  };

  return [
    salario(),
    verba(),
    categorias(),
    contagem(
      "fornecedores", "Quem vendeu ou prestou serviço?", a.empresas, b.empresas, ["empresa", "empresas"],
      "tiveram notas reembolsadas", (q) => `${q} teve notas de {dif} a mais.`,
      "Os dois tiveram notas do mesmo número de empresas.",
    ),
    contagem(
      "equipe", "Quantas pessoas no gabinete?", a.equipe, b.equipe, ["pessoa", "pessoas"],
      "segundo o Senado", (q) => `O gabinete de ${q} tem {dif} a mais.`,
      "Os dois gabinetes têm o mesmo número de pessoas.",
    ),
    moradia(),
  ];
}
