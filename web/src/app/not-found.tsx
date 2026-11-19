import Link from "next/link";

import { Cabecalho } from "@/components/base";

export default function NaoEncontrada() {
  return (
    <>
      <Cabecalho />
      <main id="conteudo" className="lista">
        <h1>Página não encontrada</h1>
        <p>
          Não achamos essa página. O Senadados só mostra os senadores em exercício; quem deixa o
          mandato sai do site. <Link href="/">Ver a lista de senadores</Link>.
        </p>
      </main>
    </>
  );
}
