"use client";

import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

/**
 * Cabeçalho fixo. Em qualquer página, um clique nele com a página rolada sobe suavemente ao topo
 * (inclusive o clique na marca). Já no topo, na página de um senador, o clique na marca leva à página
 * inicial. Na página inicial, o clique na marca nunca navega: ir para "/" estando em "/" refazia a
 * página e sorteava outras fotos na abertura.
 */
export function CabecalhoTopo({ children }: { children: ReactNode }) {
  const caminho = usePathname();
  const subir = () => window.scrollTo({ top: 0, behavior: "smooth" });
  return (
    <header
      className="top"
      onClickCapture={(e) => {
        const rolada = window.scrollY > 4;
        // Na inicial, ou com a página rolada, o clique só sobe (e não chega ao link da marca).
        if (caminho === "/" || rolada) {
          e.preventDefault();
          e.stopPropagation();
          subir();
        }
      }}
    >
      {children}
    </header>
  );
}
