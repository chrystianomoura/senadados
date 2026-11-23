"use client";

import { useEffect, useState } from "react";

import { FotoSenador } from "../FotoSenador";
import { NomeMarca } from "../NomeMarca";
import type { ItemLista } from "@/lib/types";

const QTD = 12;

/** Embaralha uma cópia da lista (Fisher-Yates). */
function embaralhar<T>(itens: T[]): T[] {
  const c = [...itens];
  for (let i = c.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [c[i], c[j]] = [c[j], c[i]];
  }
  return c;
}

/**
 * Abertura da home: o nome do projeto, o que ele é e um mosaico de retratos oficiais.
 * Os retratos mudam a cada visita. O servidor gera só os quadros vazios (para o HTML bater e nenhuma
 * foto baixar à toa) e o navegador sorteia e preenche logo depois de carregar.
 */
export function AberturaMosaico({ senadores }: { senadores: ItemLista[] }) {
  const [amostra, setAmostra] = useState<ItemLista[]>([]);
  useEffect(() => {
    const comFoto = senadores.filter((s) => s.foto_url);
    setAmostra(embaralhar(comFoto.length >= QTD ? comFoto : senadores).slice(0, QTD));
  }, [senadores]);

  return (
    <section className="ab ab-b ab-grid2" aria-labelledby="titulo-abertura">
      <div>
        <h1 id="titulo-abertura" className="ab-nome">
          <NomeMarca />
        </h1>
        <p className="ab-lead">
          O que o Senado publica sobre cada senador, <mark className="ab-m">de forma simples</mark>.
        </p>
        <ul className="ab-itens" aria-label="O que você encontra">
          <li>Quanto ganha</li>
          <li>Quanto usou da verba</li>
          <li>Em que usou a verba</li>
          <li>Quem vendeu ou prestou serviço</li>
          <li>Equipe e contato do gabinete</li>
          <li>Se usa moradia do Senado</li>
        </ul>
        <p className="ab-sub">
          <span>A fonte é sempre o Senado.</span>
          <span>O senadados só confere e explica.</span>
          <b>Só mostramos o que se comprova.</b>
        </p>
      </div>
      <div className="mosaico" aria-hidden="true">
        {Array.from({ length: QTD }, (_, i) => amostra[i]).map((s, i) => (
          <div key={s?.slug ?? i} className="m">
            {s ? (
              <FotoSenador codigo={s.codigo} url={s.foto_url} nome={s.nome} rotulo="" urgente />
            ) : null}
          </div>
        ))}
      </div>
    </section>
  );
}
