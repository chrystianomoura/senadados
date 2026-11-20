"use client";

import { useState } from "react";

import { iniciais } from "@/lib/formato";

/**
 * Foto oficial do senador, carregada do endereço do Senado (D045). Se a imagem não carregar, ou se não
 * houver endereço provado, aparecem as iniciais no lugar: o site nunca mostra uma imagem quebrada.
 */
export function FotoSenador({
  url, nome, rotulo,
}: {
  url?: string | null;
  nome: string;
  rotulo: string;
}) {
  const [falhou, setFalhou] = useState(false);
  if (!url || falhou) return <span aria-hidden="true">{iniciais(nome)}</span>;
  return (
    // eslint-disable-next-line @next/next/no-img-element -- site estático, imagem de outro endereço
    <img
      src={url}
      alt={rotulo}
      loading="lazy"
      decoding="async"
      referrerPolicy="no-referrer"
      onError={() => setFalhou(true)}
    />
  );
}
