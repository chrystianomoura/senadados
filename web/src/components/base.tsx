import Link from "next/link";

import { CabecalhoTopo } from "./CabecalhoTopo";
import { NomeMarca } from "./NomeMarca";

/** A marca no cabeçalho: o nome, que leva à página inicial. */
function Marca() {
  return (
    <Link className="wm" href="/" aria-label="senadados, página inicial">
      <NomeMarca />
    </Link>
  );
}

export function Cabecalho() {
  return (
    <CabecalhoTopo>
      <div className="in">
        <Marca />
      </div>
    </CabecalhoTopo>
  );
}
