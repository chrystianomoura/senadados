import type { ReactNode } from "react";

import { mesCurto, milhares, percentual, reaisMil } from "@/lib/formato";
import type { MesTotal } from "@/lib/types";

const Seta = () => (
  <svg className="ic" viewBox="0 0 24 24" aria-hidden="true">
    <path d="M9 6l6 6-6 6" />
  </svg>
);

/** Uma pergunta que se abre. O corpo segue o molde fixo: o que é, quanto, de onde vem. */
export function Pergunta({
  id, titulo, resposta, children, aberta = false,
}: {
  id: string;
  titulo: string;
  resposta: string;
  children: ReactNode;
  aberta?: boolean;
}) {
  return (
    <details className="q" id={id} open={aberta}>
      <summary>
        <span className="qt">{titulo}</span>
        <span className="ans">{resposta}</span>
        <span className="chev">
          <Seta />
        </span>
      </summary>
      <div className="body">
        <dl className="tpl">{children}</dl>
      </div>
    </details>
  );
}

export function Linha({
  titulo, children, destaque = false,
}: {
  titulo: string;
  children: ReactNode;
  destaque?: boolean;
}) {
  return (
    <div className={destaque ? "row use" : "row"}>
      <dt>{titulo}</dt>
      <dd>{children}</dd>
    </div>
  );
}

/** "De onde vem este número": onde o Senado publica, como chegamos e a data (D009, D025). */
export function Origem({
  onde, como, atualizado, href, textoLink,
}: {
  onde: string;
  como: string;
  atualizado: string;
  href: string;
  textoLink: string;
}) {
  return (
    <div>
      <details className="law">
        <summary>De onde vem este número</summary>
        <div className="box">
          <p>
            <b>Onde o Senado publica</b>
            <br />
            {onde}
          </p>
          <p>
            <b>Como chegamos neste número</b>
            <br />
            {como}
          </p>
          <p className="meta">
            Atualizado em {atualizado} ·{" "}
            <a href={href} rel="noopener noreferrer" target="_blank">
              {textoLink} ↗
            </a>
          </p>
        </div>
      </details>
    </div>
  );
}

/** Barras horizontais com o percentual do total. A barra mais longa é a do maior valor. */
export function Barras({
  itens, total,
}: {
  itens: { nome: string; valor: number }[];
  total: number;
}) {
  const maior = Math.max(...itens.map((i) => i.valor), 1);
  return (
    <div className="hb">
      {itens.map(({ nome, valor }) => (
        <div className="r" key={nome}>
          <span className="n">{nome}</span>
          <span className="t">
            <i style={{ width: `${(Math.max(valor, 0) / maior) * 100}%` }} />
          </span>
          <span className="v">
            {reaisMil(valor)}
            <small>{percentual(valor, total)}% do total</small>
          </span>
        </div>
      ))}
    </div>
  );
}

/** Uma barra por mês, em milhares de reais. O mês de maior valor ganha destaque (só o fato, D030). */
export function GraficoMensal({
  meses, maiorMes, ano,
}: {
  meses: MesTotal[];
  maiorMes: number;
  ano: number;
}) {
  const altura = 170;
  const maximo = Math.max(...meses.map((m) => m.total_centavos), 1);
  return (
    <>
      <p className="cap">
        Cada barra é um mês: quanto o Senado reembolsou ao senador, em milhares de reais.
      </p>
      <div
        className="mc"
        role="img"
        aria-label={`Quanto foi reembolsado em cada mês de ${ano}, em milhares de reais`}
      >
        <div className="bars">
          {meses.map((m) => {
            const topo = m.mes === maiorMes;
            return (
              <div className={topo ? "b top" : "b"} key={m.mes}>
                <em>
                  {topo ? (
                    <>
                      maior mês
                      <br />
                    </>
                  ) : null}
                  {milhares(m.total_centavos)}
                  <small>mil</small>
                </em>
                <i style={{ height: `${(Math.max(m.total_centavos, 0) / maximo) * altura}px` }} />
              </div>
            );
          })}
        </div>
        <div className="xl">
          {meses.map((m) => (
            <span key={m.mes}>{mesCurto(m.mes)}</span>
          ))}
        </div>
      </div>
    </>
  );
}
