"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";

import { FotoSenador } from "./FotoSenador";
import { normaliza } from "@/lib/busca";
import { guias, type Guia, type Lado, type Resumo } from "@/lib/comparar";
import { mesCurto, nomeMes, nomePartido, reaisMil, tituloNome, usoCurto } from "@/lib/formato";

type Lugar = "a" | "b";

const Ponto = ({ lado }: { lado: Lugar }) => <span className={`cmp-dot ${lado}`} aria-hidden="true" />;

const Seta = () => (
  <svg className="ic" viewBox="0 0 24 24" aria-hidden="true">
    <path d="M6 9l6 6 6-6" />
  </svg>
);

const Troca = () => (
  <svg className="ic" viewBox="0 0 24 24" aria-hidden="true">
    <path d="M7 4L3 8l4 4M3 8h14M17 20l4-4-4-4M21 16H7" />
  </svg>
);

// ---------------------------------------------------------------------------
// Escolha dos senadores: botão com a foto e o nome, e uma lista com busca
// ---------------------------------------------------------------------------
function Escolha({
  lado, r, outro, resumos, aoEscolher,
}: {
  lado: Lugar;
  r: Resumo;
  outro: Resumo;
  resumos: Resumo[];
  aoEscolher: (slug: string) => void;
}) {
  const [aberto, setAberto] = useState(false);
  const [texto, setTexto] = useState("");
  const raiz = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!aberto) return;
    const fora = (e: MouseEvent) => {
      if (!raiz.current?.contains(e.target as Node)) setAberto(false);
    };
    const esc = (e: KeyboardEvent) => {
      if (e.key === "Escape") setAberto(false);
    };
    document.addEventListener("mousedown", fora);
    document.addEventListener("keydown", esc);
    return () => {
      document.removeEventListener("mousedown", fora);
      document.removeEventListener("keydown", esc);
    };
  }, [aberto]);

  const achados = useMemo(() => {
    const palavras = normaliza(texto).split(/\s+/).filter(Boolean);
    return resumos.filter((s) => {
      const nome = normaliza(tituloNome(s.nome));
      return palavras.every((p) => nome.includes(p));
    });
  }, [resumos, texto]);

  return (
    <div className={`cmp-esc ${lado}`} ref={raiz}>
      <button
        type="button"
        className="cmp-pk"
        aria-expanded={aberto}
        aria-haspopup="listbox"
        onClick={() => {
          setAberto(!aberto);
          setTexto("");
        }}
      >
        <span className="cmp-av">
          <FotoSenador codigo={r.codigo} url={r.foto_url} nome={r.nome} rotulo={`Foto oficial de ${tituloNome(r.nome)}`} />
        </span>
        <span className="cmp-pt">
          <span className="cmp-rot">
            <Ponto lado={lado} />
            {lado === "a" ? "Primeiro" : "Segundo"}
          </span>
          <b>{tituloNome(r.nome)}</b>
          <small>
            {nomePartido(r.partido)} · {r.uf}
          </small>
        </span>
        <Seta />
      </button>
      {aberto ? (
        <div className="cmp-pop">
          <input
            type="search"
            autoFocus
            autoComplete="off"
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            placeholder="Digite um nome: “Alan” ou “Ana”"
            aria-label="Buscar senador"
          />
          <ul role="listbox" aria-label="Senadores">
            {achados.map((s) => {
              const jaEscolhido = s.slug === outro.slug;
              return (
                <li key={s.slug}>
                  <button
                    type="button"
                    role="option"
                    aria-selected={s.slug === r.slug}
                    disabled={jaEscolhido}
                    onClick={() => {
                      aoEscolher(s.slug);
                      setAberto(false);
                    }}
                  >
                    <span>{tituloNome(s.nome)}</span>
                    <small>{jaEscolhido ? "já escolhido" : `${nomePartido(s.partido)} · ${s.uf}`}</small>
                  </button>
                </li>
              );
            })}
            {achados.length === 0 ? <li className="nada">Nenhum senador encontrado.</li> : null}
          </ul>
        </div>
      ) : null}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Peças de cada cartão
// ---------------------------------------------------------------------------
function Metade({ r, lado, l, maior }: { r: Resumo; lado: Lugar; l: Lado | null; maior: boolean }) {
  return (
    <div className="cmp-lado">
      <div className="quem">
        <Ponto lado={lado} />
        {tituloNome(r.nome)}
      </div>
      {l ? (
        <>
          <div className="v">{maior ? <mark>{l.principal}</mark> : l.principal}</div>
          <div className="s">{l.sub}</div>
        </>
      ) : (
        <div className="v sem">Sem dado</div>
      )}
    </div>
  );
}

/** Duas barras na mesma escala: o olho vê a diferença antes de ler o número. */
function BarrasPar({ g, a, b }: { g: Guia; a: Resumo; b: Resumo }) {
  if (g.a?.num == null || g.b?.num == null) return null;
  const topo = Math.max(g.a.num, g.b.num, 1);
  return (
    <div className="cmp-barras" aria-hidden="true">
      {(
        [
          ["a", a, g.a],
          ["b", b, g.b],
        ] as const
      ).map(([lado, r, l]) => (
        <div className="cmp-b" key={lado}>
          <span className="nm">{tituloNome(r.nome)}</span>
          <span className="t">
            <i className={lado} style={{ width: `${Math.max((l.num ?? 0) / topo, 0.015) * 100}%` }} />
          </span>
        </div>
      ))}
    </div>
  );
}

/** A verba mês a mês, os dois senadores no mesmo gráfico. */
function MesAMes({ a, b }: { a: Resumo; b: Resumo }) {
  if (!a.verba || !b.verba) return null;
  const va = new Map(a.verba.meses.map((m) => [m.mes, m.total_centavos]));
  const vb = new Map(b.verba.meses.map((m) => [m.mes, m.total_centavos]));
  const meses = [...new Set([...va.keys(), ...vb.keys()])].sort((x, y) => x - y);
  const topo = Math.max(...va.values(), ...vb.values(), 1);
  const maiores = (
    [
      ["a", a],
      ["b", b],
    ] as const
  ).filter(([, r]) => r.verba?.maiorMes);
  return (
    <div className="cmp-mes">
      <p className="cap">Mês a mês: cada par de barras é um mês, com os dois senadores na mesma escala.</p>
      <div className="cmp-mc" role="img" aria-label="Quanto foi reembolsado em cada mês, os dois senadores no mesmo gráfico">
        {meses.map((m) => (
          <div className="g" key={m}>
            <span className="p">
              <i className="a" style={{ height: `${((va.get(m) ?? 0) / topo) * 100}%` }} />
              <i className="b" style={{ height: `${((vb.get(m) ?? 0) / topo) * 100}%` }} />
            </span>
            <span className="l">{mesCurto(m)}</span>
          </div>
        ))}
      </div>
      {maiores.length > 0 ? (
        <ul className="cmp-maiores">
          {maiores.map(([lado, r]) => (
            <li key={lado}>
              <Ponto lado={lado} />
              <b>{tituloNome(r.nome)}:</b> mês de maior uso foi {nomeMes(r.verba!.maiorMes!.mes)},{" "}
              {reaisMil(r.verba!.maiorMes!.total_centavos)}.
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}

/** Todas as categorias da verba, cada uma com as duas barras. */
function Fatias({ a, b }: { a: Resumo; b: Resumo }) {
  if (!a.verba || !b.verba) return null;
  const pa = new Map(a.verba.categorias.map((c) => [c.nome, c]));
  const pb = new Map(b.verba.categorias.map((c) => [c.nome, c]));
  const nomes = [...new Set([...pa.keys(), ...pb.keys()])].sort(
    (x, y) => Math.max(pb.get(y)?.pct ?? 0, pa.get(y)?.pct ?? 0) - Math.max(pb.get(x)?.pct ?? 0, pa.get(x)?.pct ?? 0),
  );
  const topo = Math.max(...nomes.map((n) => Math.max(pa.get(n)?.pct ?? 0, pb.get(n)?.pct ?? 0)), 1);
  return (
    <div className="cmp-fatias">
      <p className="cap">Cada barra é a parte da verba daquele senador. O tamanho das barras vale para as duas.</p>
      {nomes.map((n) => (
        <div className="cmp-fat" key={n}>
          <div className="n">{n}</div>
          {(
            [
              ["a", pa.get(n)],
              ["b", pb.get(n)],
            ] as const
          ).map(([lado, c]) => (
            <div className="cmp-b2" key={lado}>
              <span className="t" aria-hidden="true">
                <i className={lado} style={{ width: `${((c?.pct ?? 0) / topo) * 100}%` }} />
              </span>
              <span className="v">
                <Ponto lado={lado} />
                {c ? `${c.pct}% · ${reaisMil(c.total)}` : "nenhuma nota"}
              </span>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

function MaioresEmpresas({ a, b }: { a: Resumo; b: Resumo }) {
  return (
    <div className="cmp-par cmp-emp">
      {(
        [
          ["a", a],
          ["b", b],
        ] as const
      ).map(([lado, r]) => (
        <div key={lado}>
          <div className="quem">
            <Ponto lado={lado} />
            As que mais receberam
          </div>
          {r.maioresEmpresas.length > 0 ? (
            <ol>
              {r.maioresEmpresas.map((e) => (
                <li key={e.nome}>
                  {e.nome} <b>{reaisMil(e.total)}</b>
                </li>
              ))}
            </ol>
          ) : (
            <p className="s">Nenhuma empresa.</p>
          )}
        </div>
      ))}
    </div>
  );
}

function ChipsMoradia({ a, b }: { a: Resumo; b: Resumo }) {
  return (
    <div className="cmp-par cmp-chips">
      {(
        [
          ["a", a],
          ["b", b],
        ] as const
      ).map(([lado, r]) =>
        r.moradia ? (
          <div className="chips" key={lado}>
            <span className={r.moradia.imovel > 0 ? "chip on" : "chip off"}>
              Imóvel funcional: {usoCurto(r.moradia.imovel, r.moradia.meses)}
            </span>
            <span className={r.moradia.auxilio > 0 ? "chip on" : "chip off"}>
              Auxílio-moradia: {usoCurto(r.moradia.auxilio, r.moradia.meses)}
            </span>
          </div>
        ) : (
          <div key={lado} />
        ),
      )}
    </div>
  );
}

function Cartao({ g, a, b }: { g: Guia; a: Resumo; b: Resumo }) {
  const comBarras = g.id !== "categorias" && g.id !== "moradia";
  const quemTemMais = g.maior === "a" ? a : g.maior === "b" ? b : null;
  return (
    <section className="cmp-card" aria-labelledby={`cmp-${g.id}`}>
      <h3 id={`cmp-${g.id}`}>{g.titulo}</h3>
      <div className="cmp-par">
        <Metade r={a} lado="a" l={g.a} maior={g.maior === "a"} />
        <Metade r={b} lado="b" l={g.b} maior={g.maior === "b"} />
      </div>
      {comBarras ? <BarrasPar g={g} a={a} b={b} /> : null}
      {g.id === "verba" ? <MesAMes a={a} b={b} /> : null}
      {g.id === "categorias" ? <Fatias a={a} b={b} /> : null}
      {g.id === "fornecedores" && g.a && g.b ? <MaioresEmpresas a={a} b={b} /> : null}
      {g.id === "moradia" && g.a && g.b ? <ChipsMoradia a={a} b={b} /> : null}
      {g.diferenca ? (
        <p className="cmp-dif">
          <span className="pill">Diferença: {g.diferenca}</span>
          {quemTemMais && g.maior ? (
            <span>
              <Ponto lado={g.maior} />
              {tituloNome(quemTemMais.nome)} tem mais
            </span>
          ) : null}
        </p>
      ) : null}
      <p className="cmp-frase">{g.frase}</p>
    </section>
  );
}

// ---------------------------------------------------------------------------
// A tela
// ---------------------------------------------------------------------------
/** Compara dois senadores guia a guia, lado a lado (D050). */
export function Comparador({
  resumos, ano, atualizadoEm, inicial,
}: {
  resumos: Resumo[];
  ano: number;
  atualizadoEm: string;
  inicial: [string, string];
}) {
  const [sa, setSa] = useState(inicial[0]);
  const [sb, setSb] = useState(inicial[1]);
  const [pronto, setPronto] = useState(false);
  const [copia, setCopia] = useState<"" | "ok" | "erro">("");

  // O endereço guarda a escolha (?a=...&b=...), para o link da comparação poder ser compartilhado.
  useEffect(() => {
    const p = new URLSearchParams(window.location.search);
    const existe = (s: string | null) => (s && resumos.some((r) => r.slug === s) ? s : null);
    const x = existe(p.get("a")) ?? inicial[0];
    let y = existe(p.get("b")) ?? inicial[1];
    if (x === y) y = [inicial[0], inicial[1]].find((s) => s !== x) ?? resumos.find((r) => r.slug !== x)!.slug;
    setSa(x);
    setSb(y);
    setPronto(true);
  }, [resumos, inicial]);

  useEffect(() => {
    if (pronto) window.history.replaceState(null, "", `${window.location.pathname}?a=${sa}&b=${sb}`);
  }, [pronto, sa, sb]);

  const a = resumos.find((r) => r.slug === sa) ?? resumos[0];
  const b = resumos.find((r) => r.slug === sb) ?? resumos[1];
  const lista = useMemo(() => guias(a, b, ano), [a, b, ano]);

  const copiar = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopia("ok");
    } catch {
      setCopia("erro");
    }
    setTimeout(() => setCopia(""), 2500);
  };

  return (
    <>
      <div className="cmp-bar">
        <Escolha lado="a" r={a} outro={b} resumos={resumos} aoEscolher={setSa} />
        <button
          type="button"
          className="cmp-troca"
          aria-label="Trocar os dois senadores de lugar"
          title="Trocar de lugar"
          onClick={() => {
            setSa(sb);
            setSb(sa);
          }}
        >
          <Troca />
        </button>
        <Escolha lado="b" r={b} outro={a} resumos={resumos} aoEscolher={setSb} />
      </div>

      <div className="cmp-meta">
        <span>Dados de {ano}, atualizados em {atualizadoEm}.</span>
        <button type="button" className="cmp-copiar" onClick={copiar}>
          {copia === "ok" ? "Link copiado" : copia === "erro" ? "Não foi possível copiar" : "Copiar o link desta comparação"}
        </button>
      </div>

      {lista.map((g) => (
        <Cartao key={g.id} g={g} a={a} b={b} />
      ))}

      <div className="more">
        <h3>De onde vêm estes números</h3>
        <p>
          São os mesmos números do perfil de cada senador, de {ano}, com a mesma conferência entre as
          publicações do Senado. Onde um dos dois não tem dado comprovado, a tela diz “sem dado” e não
          estima nada. As barras e os destaques mostram só qual número é maior: não dizem se é melhor ou pior.
        </p>
        <p>
          Mostramos valores, não dizemos se algo está dentro ou fora da lei.{" "}
          <Link href={`/senador/${a.slug}/`}>Perfil de {tituloNome(a.nome)}</Link> ·{" "}
          <Link href={`/senador/${b.slug}/`}>Perfil de {tituloNome(b.nome)}</Link>
        </p>
      </div>
    </>
  );
}
