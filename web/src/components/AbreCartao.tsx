"use client";

import type { ReactNode } from "react";

/** Cartão do resumo: ao tocar, abre a pergunta correspondente e leva a tela até ela. */
export function AbreCartao({ alvo, children }: { alvo: string; children: ReactNode }) {
  return (
    <a
      className="sc"
      href={`#${alvo}`}
      onClick={(evento) => {
        const pergunta = document.getElementById(alvo);
        if (pergunta instanceof HTMLDetailsElement) {
          evento.preventDefault();
          pergunta.open = true;
          pergunta.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      }}
    >
      {children}
    </a>
  );
}
