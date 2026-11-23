import type { Metadata } from "next";

import { Cabecalho } from "@/components/base";
import { CAPTURADO_EM, CASOS } from "@/lib/divergencias";
import { metadados, verificacoes } from "@/lib/dados";
import { dataBr } from "@/lib/formato";
import { historico, motivosOrdenados, nomeConferencia, resumoAtual, senadores } from "@/lib/verificacoes";

export const metadata: Metadata = {
  title: "Verificações",
  description: "O que o Senadados conferiu entre as publicações do Senado e o que ficou de fora.",
};

// Verificações (escopo.md, tela 4.5): o resultado de cada conferência, em contagem e sem nomes de senadores
// (D042), e a seção de divergências, onde só entra o que tem imagem de prova (D038).
export default function PaginaVerificacoes() {
  const meta = metadados();
  const { resumo, motivos } = verificacoes();
  const linhas = resumoAtual(resumo);
  const anosDaCota = historico(resumo, "cota");

  return (
    <>
      <Cabecalho />
      <main id="conteudo" className="verif">
        <h1>Verificações</h1>
        <p className="lead">
          O Senadados só mostra um número quando as publicações do Senado concordam entre si. Aqui está o
          resultado de cada conferência, com os dados de {dataBr(meta.data_referencia)}.
        </p>
        <p className="aviso-verif">
          <b>Verificamos se as bases do Senado concordam entre si. Não auditamos os dados</b> e não dizemos se
          algo está dentro ou fora da lei.
        </p>

        <h2>O que foi conferido</h2>
        <div className="tabela-rolavel">
          <table>
            <thead>
              <tr>
                <th>Conferência</th>
                <th className="n">Iguais</th>
                <th className="n">Diferença explicada</th>
                <th className="n">Pendentes</th>
                <th className="n">Ocultos</th>
              </tr>
            </thead>
            <tbody>
              {linhas.map((l) => (
                <tr key={l.verificacao}>
                  <th scope="row">
                    {nomeConferencia(l.verificacao)} <small>({l.ano})</small>
                  </th>
                  <td className="n">{l.identicos}</td>
                  <td className="n">{l.explicados}</td>
                  <td className="n">{l.pendentes}</td>
                  <td className="n">{l.ocultos}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <ul className="legenda">
          <li><b>Iguais:</b> as publicações do Senado dizem a mesma coisa, e o dado aparece.</li>
          <li><b>Diferença explicada:</b> dizem coisas um pouco diferentes, mas a diferença tem explicação, e o dado aparece.</li>
          <li><b>Pendentes:</b> ainda é cedo para concluir, por exemplo porque uma publicação é de um mês mais recente que a outra. O dado fica de fora até as duas se alinharem.</li>
          <li><b>Ocultos:</b> a diferença não tem explicação. O dado não aparece.</li>
        </ul>

        <details>
          <summary>A verba do mandato (cota), ano a ano</summary>
          <div className="tabela-rolavel">
            <table>
              <thead>
                <tr>
                  <th>Ano</th>
                  <th className="n">Iguais</th>
                  <th className="n">Diferença explicada</th>
                  <th className="n">Ocultos</th>
                </tr>
              </thead>
              <tbody>
                {anosDaCota.map((l) => (
                  <tr key={l.ano}>
                    <th scope="row">{l.ano}</th>
                    <td className="n">{l.identicos}</td>
                    <td className="n">{l.explicados}</td>
                    <td className="n">{l.ocultos}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>

        <h2>O que ficou de fora, e por quê</h2>
        <ul className="motivos">
          {motivosOrdenados(motivos).map((m) => (
            <li key={`${m.verificacao}-${m.ano}-${m.situacao}`}>
              <b>{nomeConferencia(m.verificacao)}, {m.ano}:</b> {senadores(m.qtd)}{" "}
              {m.situacao === "pendente"
                ? m.qtd === 1 ? "pendente" : "pendentes"
                : m.qtd === 1 ? "oculto" : "ocultos"}, porque {m.motivo}.
            </li>
          ))}
        </ul>
        <p className="nota-verif">Não mostramos nomes aqui: uma lista de senadores sem um dado poderia ser lida como acusação.</p>

        <h2 id="divergencias">Onde os dados do Senado não batem entre si</h2>
        <p>
          Em alguns lugares, <b>duas publicações oficiais do próprio Senado mostram números diferentes para a
          mesma coisa</b>. Cada caso abaixo traz imagens das telas e dos arquivos do Senado, para qualquer pessoa
          conferir sozinha. As imagens foram capturadas de novo em <b>{CAPTURADO_EM}</b>; se o Senado atualizar
          os dados depois, o que está aqui pode deixar de valer.
        </p>
        <ul className="legenda">
          <li>Não afirmamos qual dos números está certo, nem o motivo, nem que alguém fez algo errado.</li>
          <li>Os senadores aparecem porque o Senado publica os dados por senador, e é nessa publicação que a diferença está.</li>
          <li>As imagens com a etiqueta “montagem do Senadados” são tabelas feitas por nós, com linhas do arquivo oficial copiadas sem alterar nenhum valor.</li>
        </ul>

        {CASOS.map((c, i) => (
          <section key={c.id} className="caso" aria-labelledby={`caso-${c.id}`}>
            <h3 id={`caso-${c.id}`}>{i + 1}. {c.titulo}</h3>
            <p className="onde"><b>Onde:</b> {c.onde}</p>
            {c.blocos.map((b) => (
              <div key={b.texto}>
                <p>{b.texto}</p>
                {b.imagens.map((im) => (
                  // eslint-disable-next-line @next/next/no-img-element -- site estático, imagem do próprio site
                  <img key={im.arquivo} src={`/evidencias/${im.arquivo}`} alt={im.alt} loading="lazy" className="prova" />
                ))}
              </div>
            ))}
            <p><b>O argumento:</b> {c.argumento}</p>
            <p><b>Como conferir:</b> {c.comoConferir}</p>
            <p className="no-site"><b>O que aparece no Senadados:</b> {c.noSite}</p>
          </section>
        ))}
      </main>
    </>
  );
}
