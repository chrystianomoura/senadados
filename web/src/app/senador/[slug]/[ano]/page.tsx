import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { Cabecalho } from "@/components/base";
import { PerfilPagina } from "@/components/PerfilPagina";
import { anoPadrao, anosDisponiveis } from "@/lib/anos";
import { metadados, perfil, slugs } from "@/lib/dados";
import { tituloNome } from "@/lib/formato";

type Props = { params: Promise<{ slug: string; ano: string }> };

// O outro ano de cada senador (D048): `/senador/{endereço}/2025/`. O ano que a página abre fica no endereço
// do senador, sem o ano; só existem aqui os anos que têm dados provados e não são o padrão.
export const dynamicParams = false;

export function generateStaticParams() {
  const anoDosDados = Number(metadados().data_referencia.slice(0, 4));
  return slugs().flatMap((slug) => {
    const p = perfil(slug);
    const padrao = anoPadrao(p, anoDosDados);
    return anosDisponiveis(p, anoDosDados)
      .filter((ano) => ano !== padrao)
      .map((ano) => ({ slug, ano: String(ano) }));
  });
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug, ano } = await params;
  return {
    title: `${tituloNome(perfil(slug).nome)}, ${ano}`,
    description: `Uso da verba e fornecedores de ${tituloNome(perfil(slug).nome)} em ${ano}, com os valores que o Senado publica.`,
  };
}

export default async function PaginaDoSenadorEmOutroAno({ params }: Props) {
  const { slug, ano } = await params;
  const meta = metadados();
  const dados = perfil(slug);
  if (!anosDisponiveis(dados, Number(meta.data_referencia.slice(0, 4))).includes(Number(ano))) notFound();
  return (
    <>
      <Cabecalho />
      <PerfilPagina perfil={dados} dataReferencia={meta.data_referencia} ano={Number(ano)} />
    </>
  );
}
