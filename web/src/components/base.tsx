import Link from "next/link";

import { dataBr } from "@/lib/formato";

/** O nome da marca, com o "o" desenhado como um anel verde (D029). */
export function Marca() {
  return (
    <Link className="wm" href="/" aria-label="senadados, página inicial">
      senadad
      <svg className="o" viewBox="0 0 64 64" aria-hidden="true">
        <circle cx="32" cy="32" r="21" fill="none" stroke="#c8f53a" strokeWidth="16" />
      </svg>
      s
    </Link>
  );
}

export function Cabecalho({ naLista = false }: { naLista?: boolean }) {
  return (
    <header className="top">
      <div className="in">
        <Marca />
        <nav aria-label="Principal">
          <Link href="/" aria-current={naLista ? "page" : undefined}>
            Senadores
          </Link>
        </nav>
      </div>
    </header>
  );
}

export function Rodape({ dataReferencia }: { dataReferencia: string }) {
  return (
    <footer className="base">
      Fonte dos números: Senado Federal, dados abertos, atualizado em {dataBr(dataReferencia)}.
      Verificamos se as bases do Senado concordam entre si; não auditamos os dados. O Senadados não
      julga se algo está dentro ou fora da lei: quem quiser investigar pesquisa por conta própria.
    </footer>
  );
}
