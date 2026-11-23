"use client";

import { useState } from "react";

import { iniciais } from "@/lib/formato";

/** A cópia reduzida da foto, gerada pelo pipeline (D047): `p` para a lista e `g` para o perfil. */
export function fotoCopia(codigo: number, tamanho: "p" | "g"): string {
  return `/fotos/${codigo}-${tamanho}.webp`;
}

type Etapa = "copia" | "original" | "iniciais";

/**
 * Foto oficial do senador (D045). Mostra a cópia reduzida do próprio site; se ela faltar, tenta o endereço
 * oficial do Senado; se este também falhar, ou se não houver foto provada, mostram-se as iniciais. O site
 * nunca mostra uma imagem quebrada.
 */
export function FotoSenador({
  codigo, url, nome, rotulo, grande = false, urgente = false,
}: {
  codigo: number;
  url?: string | null;
  nome: string;
  rotulo: string;
  /** O cartão do perfil usa a cópia grande; a lista e o mosaico, a pequena. */
  grande?: boolean;
  /** Foto que aparece logo na abertura: baixa já e decodifica sem esperar. */
  urgente?: boolean;
}) {
  const [etapa, setEtapa] = useState<Etapa>("copia");
  if (!url || etapa === "iniciais") return <span aria-hidden="true">{iniciais(nome)}</span>;
  return (
    // eslint-disable-next-line @next/next/no-img-element -- site estático, imagem do próprio site ou do Senado
    <img
      src={etapa === "copia" ? fotoCopia(codigo, grande ? "g" : "p") : url}
      alt={rotulo}
      width={grande ? 480 : 240}
      height={grande ? 600 : 300}
      loading={urgente ? "eager" : "lazy"}
      decoding={urgente ? "sync" : "async"}
      referrerPolicy="no-referrer"
      onError={() => setEtapa(etapa === "copia" ? "original" : "iniciais")}
    />
  );
}
