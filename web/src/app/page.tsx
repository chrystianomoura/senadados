import Link from "next/link";

import { Cabecalho, Rodape } from "@/components/base";
import { lista, metadados } from "@/lib/dados";
import { iniciais, nomeEstado, tituloNome } from "@/lib/formato";

// Lista provisória só para navegar até os perfis. A home de verdade (busca por nome e filtros por
// estado e partido) vem depois (escopo.md, tela 4.1).
export default function Inicio() {
  const meta = metadados();
  const senadores = [...lista()].sort((a, b) => a.nome.localeCompare(b.nome, "pt-BR"));
  return (
    <>
      <Cabecalho naLista />
      <main id="conteudo" className="lista">
        <h1>Senadores em exercício</h1>
        <p>
          Os valores que o Senado publica sobre os {meta.senadores} senadores em exercício, explicados
          para qualquer pessoa. Escolha um senador para ver o que foi possível comprovar.
        </p>
        <ul className="grade">
          {senadores.map((s) => (
            <li key={s.slug}>
              <Link href={`/senador/${s.slug}/`}>
                <span className="ini" aria-hidden="true">
                  {iniciais(s.nome)}
                </span>
                <span>
                  <b>{tituloNome(s.nome)}</b>
                  <small>
                    {s.partido} · {s.uf} · {nomeEstado(s.uf)}
                  </small>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </main>
      <Rodape dataReferencia={meta.data_referencia} />
    </>
  );
}
