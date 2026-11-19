import type { Metadata } from "next";

import { Cabecalho, Rodape } from "@/components/base";
import { PerfilPagina } from "@/components/PerfilPagina";
import { metadados, perfil, slugs } from "@/lib/dados";
import { tituloNome } from "@/lib/formato";

type Props = { params: Promise<{ slug: string }> };

// Só existem as páginas dos senadores em exercício (D026); qualquer outro endereço dá 404.
export const dynamicParams = false;

export function generateStaticParams() {
  return slugs().map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const p = perfil(slug);
  return {
    title: tituloNome(p.nome),
    description: `Salário, uso da verba, gabinete e moradia de ${tituloNome(p.nome)}, com os valores que o Senado publica.`,
  };
}

export default async function PaginaDoSenador({ params }: Props) {
  const { slug } = await params;
  const dados = perfil(slug);
  const meta = metadados();
  return (
    <>
      <Cabecalho />
      <PerfilPagina perfil={dados} dataReferencia={meta.data_referencia} />
      <Rodape dataReferencia={meta.data_referencia} />
    </>
  );
}
