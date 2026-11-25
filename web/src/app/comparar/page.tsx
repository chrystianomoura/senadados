import type { Metadata } from "next";

import { Cabecalho } from "@/components/base";
import { Comparador } from "@/components/Comparador";
import { resumir } from "@/lib/comparar";
import { lista, metadados, perfil } from "@/lib/dados";
import { dataBr } from "@/lib/formato";

export const metadata: Metadata = {
  title: "Comparar senadores",
  description: "Coloque dois senadores lado a lado e veja, pergunta por pergunta, o que o Senado publica sobre cada um.",
};

// Comparação de dois senadores (D021). Versão de teste: duas formas de mostrar, para o mantenedor escolher.
export default function Comparar() {
  const meta = metadados();
  const ano = Number(meta.data_referencia.slice(0, 4));
  const resumos = lista()
    .map((s) => resumir(perfil(s.slug), ano))
    .sort((x, y) => x.nome.localeCompare(y.nome, "pt-BR"));
  // Começa com dois senadores que têm as seis respostas, para a primeira tela já mostrar tudo.
  const completos = resumos.filter(
    (r) => r.salario && r.verba && r.empresas !== null && r.equipe !== null && r.moradia,
  );
  const inicial: [string, string] = [
    (completos[0] ?? resumos[0]).slug,
    (completos[1] ?? resumos[1]).slug,
  ];

  return (
    <>
      <Cabecalho />
      <main id="conteudo" className="comp">
        <h1>Comparar dois senadores</h1>
        <p className="lead">
          Escolha dois senadores e veja, pergunta por pergunta, o que o Senado publica sobre cada um.
        </p>
        <Comparador resumos={resumos} ano={ano} atualizadoEm={dataBr(meta.data_referencia)} inicial={inicial} />
      </main>
    </>
  );
}
