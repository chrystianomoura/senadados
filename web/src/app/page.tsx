import { BuscaSenadores } from "@/components/BuscaSenadores";
import { Cabecalho, Rodape } from "@/components/base";
import { lista, metadados, verificacoes } from "@/lib/dados";
import { dataBr } from "@/lib/formato";

// Início (escopo.md, tela 4.1): o que são os dados, a busca por nome com filtros por estado e
// partido, e como funciona a prova real. Sem destaques que comparam senadores: eles seguem o
// "tudo ou nada" da D037 e ainda dependem de definir quem entra no grupo.
export default function Inicio() {
  const meta = metadados();
  const senadores = [...lista()].sort((a, b) => a.nome.localeCompare(b.nome, "pt-BR"));
  const titulares = senadores.filter((s) => s.tipo === "Titular").length;
  const suplentes = senadores.length - titulares;
  // Quantos tipos de conferência o Senadados faz entre as bases do Senado (cota, equipe, moradia,
  // contato e salário), contando o contato uma vez só.
  const conferencias = new Set(verificacoes().resumo.map((v) => v.verificacao.split("_")[0])).size;

  return (
    <>
      <Cabecalho naLista />
      <main id="conteudo" className="home">
        <section className="hero" aria-labelledby="titulo-home">
          <p className="eyebrow">Dados abertos do Senado, explicados</p>
          <h1 id="titulo-home">O que o Senado publica sobre cada senador, em palavras simples</h1>
          <p>
            Quanto cada senador ganha, quanto usa da verba do mandato, quem trabalha no gabinete e
            se usa moradia do Senado. Só mostramos o que se comprova.
          </p>
          <ul className="stats">
            <li className="stat">
              <b>{meta.senadores}</b>
              <span>
                senadores em exercício ({titulares} titulares e {suplentes} suplentes)
              </span>
            </li>
            <li className="stat">
              <b>{conferencias}</b>
              <span>conferências entre bases do Senado antes de mostrar um número</span>
            </li>
            <li className="stat">
              <b>{dataBr(meta.data_referencia)}</b>
              <span>data dos dados que você vê aqui</span>
            </li>
          </ul>
        </section>

        <h2 className="secao-titulo">Encontre um senador</h2>
        <BuscaSenadores senadores={senadores} />

        <h2 className="secao-titulo">Como funciona</h2>
        <ol className="como">
          <li>
            <span className="nu" aria-hidden="true">
              1
            </span>
            <h3>Dados oficiais</h3>
            <p>
              Tudo vem do próprio Senado Federal, em dados abertos. Cada número diz de onde vem e
              quando foi atualizado.
            </p>
          </li>
          <li>
            <span className="nu" aria-hidden="true">
              2
            </span>
            <h3>Só o comprovado</h3>
            <p>
              Conferimos se as publicações do Senado concordam entre si. O que não bate, ou não dá
              para provar, simplesmente não aparece.
            </p>
          </li>
          <li>
            <span className="nu" aria-hidden="true">
              3
            </span>
            <h3>Sem julgamento</h3>
            <p>
              Mostramos valores e ajudamos a entendê-los. Não dizemos se algo está dentro ou fora da
              lei: quem quiser investigar, pesquisa por conta própria.
            </p>
          </li>
        </ol>
      </main>
      <Rodape dataReferencia={meta.data_referencia} />
    </>
  );
}
