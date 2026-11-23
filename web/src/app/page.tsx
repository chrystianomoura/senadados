import Link from "next/link";

import { BuscaSenadores } from "@/components/BuscaSenadores";
import { Cabecalho } from "@/components/base";
import { AberturaMosaico } from "@/components/abertura/Mosaico";
import { lista } from "@/lib/dados";

// Início (escopo.md, tela 4.1): a abertura (nome, o que é e retratos sorteados), "Como funciona" e a busca
// por nome com filtros por estado e partido. Sem destaques que comparam senadores: eles seguem o "tudo ou
// nada" da D037 e ainda dependem de definir quem entra no grupo.
export default function Inicio() {
  const senadores = [...lista()].sort((a, b) => a.nome.localeCompare(b.nome, "pt-BR"));

  return (
    <>
      <Cabecalho />
      <main id="conteudo" className="home">
        <AberturaMosaico senadores={senadores} />

        <h2 className="secao-titulo">Como funciona</h2>
        <ol className="como">
          <li>
            <h3>Dados oficiais</h3>
            <p>
              Tudo vem do próprio Senado Federal, em dados abertos. Cada número diz de onde vem e
              quando foi atualizado.
            </p>
          </li>
          <li>
            <h3>Só o comprovado</h3>
            <p>
              Conferimos se as publicações do Senado concordam entre si. O que não bate, ou não dá
              para provar, simplesmente não aparece.
            </p>
            <p>
              <Link href="/verificacoes/">Veja o que foi conferido</Link>
            </p>
          </li>
          <li>
            <h3>Sem julgamento</h3>
            <p>
              Mostramos valores e ajudamos a entendê-los. Não dizemos se algo está dentro ou fora da
              lei: quem quiser investigar, pesquisa por conta própria.
            </p>
          </li>
        </ol>

        <h2 className="secao-titulo">Encontre um senador</h2>
        <BuscaSenadores senadores={senadores} />
      </main>
    </>
  );
}
