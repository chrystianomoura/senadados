"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { FotoSenador } from "./FotoSenador";
import { filtrar, opcoes } from "@/lib/busca";
import { nomeEstado, tituloNome } from "@/lib/formato";
import type { ItemLista } from "@/lib/types";

/** Busca por nome e filtros por estado e partido. Roda no navegador, sobre a lista já carregada. */
export function BuscaSenadores({ senadores }: { senadores: ItemLista[] }) {
  const [texto, setTexto] = useState("");
  const [uf, setUf] = useState("");
  const [partido, setPartido] = useState("");

  const ufs = useMemo(() => opcoes(senadores, "uf"), [senadores]);
  const partidos = useMemo(() => opcoes(senadores, "partido"), [senadores]);
  const achados = useMemo(
    () => filtrar(senadores, { texto, uf, partido }),
    [senadores, texto, uf, partido],
  );
  const filtrando = texto.trim() !== "" || uf !== "" || partido !== "";

  return (
    <section aria-labelledby="titulo-busca">
      <h2 id="titulo-busca" className="sr">
        Buscar senador
      </h2>
      <form className="busca" role="search" onSubmit={(e) => e.preventDefault()}>
        <label className="campo grande">
          <span>Nome do senador</span>
          <input
            type="search"
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            placeholder="Digite um nome, por exemplo “Alan”"
            autoComplete="off"
          />
        </label>
        <label className="campo">
          <span>Estado</span>
          <select value={uf} onChange={(e) => setUf(e.target.value)}>
            <option value="">Todos</option>
            {ufs.map((u) => (
              <option key={u} value={u}>
                {u} · {nomeEstado(u)}
              </option>
            ))}
          </select>
        </label>
        <label className="campo">
          <span>Partido</span>
          <select value={partido} onChange={(e) => setPartido(e.target.value)}>
            <option value="">Todos</option>
            {partidos.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        {filtrando ? (
          <button
            type="button"
            className="limpar"
            onClick={() => {
              setTexto("");
              setUf("");
              setPartido("");
            }}
          >
            Limpar filtros
          </button>
        ) : null}
      </form>

      <p className="contagem" aria-live="polite">
        {achados.length === senadores.length
          ? `${senadores.length} senadores em exercício`
          : `${achados.length} de ${senadores.length} senadores`}
      </p>

      {achados.length === 0 ? (
        <p className="vazio">Nenhum senador encontrado. Tente outro nome ou limpe os filtros.</p>
      ) : (
        <ul className="grade">
          {achados.map((s) => (
            <li key={s.slug}>
              <Link href={`/senador/${s.slug}/`}>
                <span className="ini">
                  <FotoSenador url={s.foto_url} nome={s.nome} rotulo={`Foto oficial de ${tituloNome(s.nome)}`} />
                </span>
                <span className="info">
                  <b>{tituloNome(s.nome)}</b>
                  <span className="selos">
                    <span className="selo partido">{s.partido}</span>
                    <span className="selo uf">{s.uf}</span>
                    {s.tipo === "Titular" ? null : <span className="selo sup">Suplente</span>}
                  </span>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
