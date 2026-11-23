import Link from "next/link";

import { AbreCartao } from "./AbreCartao";
import { FotoSenador } from "./FotoSenador";
import { Barras, GraficoMensal, Linha, Origem, Pergunta } from "./perguntas";
import {
  dataBr, mandatoTexto, mesAno, nomeEstado, nomeMes, nomePartido, periodo, periodoAno, reais, reaisMil, telefone,
  tituloNome, usoCurto, usoTexto,
} from "@/lib/formato";
import { anoPadrao, anosDisponiveis, enderecoDoAno } from "@/lib/anos";
import type { Perfil } from "@/lib/types";

const maiuscula = (texto: string) => texto.charAt(0).toLocaleUpperCase("pt-BR") + texto.slice(1);
const pessoas = (n: number) => `${n} ${n === 1 ? "pessoa" : "pessoas"}`;

const Ok = () => (
  <svg className="ic" viewBox="0 0 24 24" aria-hidden="true">
    <path d="M5 13l4 4L19 7" />
  </svg>
);
const Nao = () => (
  <svg className="ic" viewBox="0 0 24 24" aria-hidden="true">
    <path d="M6 6l12 12M18 6L6 18" />
  </svg>
);
const Info = () => (
  <svg className="ic" viewBox="0 0 24 24" aria-hidden="true">
    <circle cx="12" cy="12" r="9" />
    <path d="M12 11v6M12 7.5v.5" />
  </svg>
);

/** E-mail que só quebra de linha depois do @. */
function Email({ endereco }: { endereco: string }) {
  const [local, dominio] = endereco.split("@");
  return (
    <div>
      {local}@<wbr />
      {dominio}
    </div>
  );
}

function Chip({ usou, texto }: { usou: boolean; texto: string }) {
  return (
    <span className={usou ? "chip on" : "chip off"}>
      {usou ? <Ok /> : <Nao />} {texto}
    </span>
  );
}

export function PerfilPagina({
  perfil, dataReferencia, ano,
}: {
  perfil: Perfil;
  dataReferencia: string;
  /** O ano que a página mostra (D048). */
  ano: number;
}) {
  const nome = tituloNome(perfil.nome);
  const atualizado = dataBr(dataReferencia);
  const portal = `https://www6g.senado.leg.br/transparencia/sen/${perfil.codigo}/`;

  // O ano mostrado muda a verba e os fornecedores. Salário, equipe, moradia e contato valem para um instante
  // e só aparecem no ano dos dados: o que não foi provado para o ano escolhido não aparece (D025).
  const anoDosDados = Number(dataReferencia.slice(0, 4));
  const anos = anosDisponiveis(perfil, anoDosDados);
  const padrao = anoPadrao(perfil, anoDosDados);
  const cota = perfil.cota?.anos.find((a) => a.ano === ano) ?? null;
  const mesesCota = cota?.meses.map((m) => m.mes) ?? [];
  const periodoCota = periodo(mesesCota);
  // Com um mês só, "o maior mês" não diz nada: o destaque e o aviso só aparecem com 2 meses ou mais.
  const variosMeses = (cota?.meses.length ?? 0) > 1;
  // A média usa todos os meses do período (do primeiro ao último com nota), inclusive os que não têm
  // nenhuma: assim ela combina com o texto "de janeiro a julho" e não fica inflada por meses vazios.
  const ultimoMesCota = mesesCota.length ? Math.max(...mesesCota) : 0;
  const mesesDoPeriodo = mesesCota.length ? ultimoMesCota - Math.min(...mesesCota) + 1 : 1;
  const mediaMensal = cota ? Math.round(cota.total_centavos / mesesDoPeriodo) : 0;
  // O Senado só publicou notas até um mês bem anterior ao da última atualização: vale avisar.
  const mesReferencia = Number(dataReferencia.slice(5, 7));
  const semNotasRecentes =
    cota !== null &&
    cota.ano === Number(dataReferencia.slice(0, 4)) &&
    ultimoMesCota > 0 &&
    ultimoMesCota < mesReferencia - 1;
  const forn = perfil.fornecedores?.anos.find((a) => a.ano === ano) ?? null;

  const salario = perfil.salario?.ano === ano ? perfil.salario : null;
  const equipe = perfil.equipe?.ano === ano ? perfil.equipe : null;
  const moradia = perfil.moradia?.anos.find((a) => a.ano === ano) ?? null;
  const contato = ano === anoDosDados ? perfil.contato : null;
  const anoResumo = cota || salario || equipe || moradia ? ano : null;

  const imovel = moradia?.meses.filter((m) => m.imovel_funcional).length ?? 0;
  const auxilio = moradia?.meses.filter((m) => m.auxilio_moradia).length ?? 0;
  const mesesMoradia = moradia?.meses.length ?? 0;
  const respostaMoradia =
    imovel > 0 && auxilio > 0
      ? "Imóvel e auxílio"
      : imovel > 0
        ? "Imóvel funcional"
        : auxilio > 0
          ? "Auxílio-moradia"
          : "Não usou";

  const pessoasFisicas = forn?.agrupados.find((g) => g.tipo === "pessoa_fisica") ?? null;
  const outros = forn?.agrupados.filter((g) => g.tipo !== "pessoa_fisica") ?? [];
  const outrosQtd = outros.reduce((s, g) => s + g.qtd_despesas, 0);
  const outrosTotal = outros.reduce((s, g) => s + g.total_centavos, 0);

  const temContato = Boolean(contato && (contato.endereco || contato.telefones.length || contato.email));

  return (
    <div className="lay">
      <aside>
        <div className="ficha">
          <div
            className="av"
            title={perfil.quem_e?.foto ? `${perfil.quem_e.foto.credito}.` : undefined}
          >
            <FotoSenador
              codigo={perfil.codigo}
              grande
              url={perfil.quem_e?.foto?.url}
              nome={perfil.nome}
              rotulo={`Foto oficial de ${nome}`}
            />
          </div>
          <div className="quem">
            <h1>{nome}</h1>
            <div className="tags">
              <span className="tag fill">{nomePartido(perfil.partido)}</span>
              <span className="tag">
                {perfil.uf} · {nomeEstado(perfil.uf)}
              </span>
            </div>
          </div>
          <dl>
            <dt>Cargo</dt>
            <dd>{perfil.tipo}</dd>
            {perfil.quem_e?.mandato ? (
              <>
                <dt>Mandato</dt>
                <dd>{mandatoTexto(perfil.quem_e.mandato.inicio, perfil.quem_e.mandato.fim)}</dd>
              </>
            ) : null}
            {salario ? (
              <>
                <dt>Salário</dt>
                <dd>{reais(salario.basica_centavos)}</dd>
              </>
            ) : null}
            {cota ? (
              <>
                <dt>Verba {cota.ano}</dt>
                <dd>{reaisMil(cota.total_centavos)}</dd>
              </>
            ) : null}
            {equipe ? (
              <>
                <dt>Gabinete</dt>
                <dd>{pessoas(equipe.pessoas)}</dd>
              </>
            ) : null}
          </dl>
        </div>
      </aside>

      <main id="conteudo">
        {anoResumo === null ? (
          <div className="note">
            Ainda não há dados comprovados para este senador. O que não se comprova não aparece.
          </div>
        ) : (
          <>
            <div className="sumhead">
              <h2>Resumo de {anoResumo}</h2>
              {anos.length > 1 ? (
                <nav className="anos" aria-label="Trocar o ano dos dados">
                  {anos
                    .filter((a) => a !== ano)
                    .map((a) => (
                      <Link key={a} href={enderecoDoAno(perfil.slug, a, padrao)} className="ver-ano">
                        Ver os dados de {a} →
                      </Link>
                    ))}
                </nav>
              ) : null}
            </div>
            <div className="sum">
              {salario ? (
                <AbreCartao alvo="q1">
                  <span className="lb">Salário por mês</span>
                  <span className="n">{reais(salario.basica_centavos)}</span>
                  <span className="s">salário-base de {nomeMes(salario.mes)}.</span>
                  <span className="s">Depois dos descontos: {reais(salario.liquida_centavos)}</span>
                  <span className="go">Entender →</span>
                </AbreCartao>
              ) : null}
              {cota ? (
                <>
                  <AbreCartao alvo="q2">
                    <span className="lb">Verba do mandato usada</span>
                    <span className="n">{reaisMil(cota.total_centavos)}</span>
                    <span className="s">
                      {variosMeses
                        ? `Média de ${reaisMil(mediaMensal)} por mês${periodoCota ? `, ${periodoCota}` : ""}.`
                        : `Valor registrado ${periodoCota}.`}
                    </span>
                    <span className="go">Entender →</span>
                  </AbreCartao>
                  {variosMeses ? (
                    <AbreCartao alvo="q2">
                      <span className="lb">Mês de maior uso da verba</span>
                      <span className="n">{maiuscula(nomeMes(cota.maior_mes.mes))}</span>
                      <span className="s">
                        {reaisMil(cota.maior_mes.total_centavos)}: o maior valor {periodoCota}.
                      </span>
                      <span className="go">Ver no gráfico →</span>
                    </AbreCartao>
                  ) : null}
                </>
              ) : null}
              {equipe ? (
                <AbreCartao alvo="q5">
                  <span className="lb">Equipe do gabinete</span>
                  <span className="n">{pessoas(equipe.pessoas)}</span>
                  <span className="s">trabalham no gabinete, segundo o Senado.</span>
                  <span className="go">Entender →</span>
                </AbreCartao>
              ) : null}
              {moradia ? (
                <AbreCartao alvo="q7">
                  <span className="lb">Moradia</span>
                  <div className="chips">
                    <Chip usou={imovel > 0} texto={`Imóvel funcional: ${usoCurto(imovel, mesesMoradia)}`} />
                    <Chip usou={auxilio > 0} texto={`Auxílio-moradia: ${usoCurto(auxilio, mesesMoradia)}`} />
                  </div>
                  <span className="go">Entender →</span>
                </AbreCartao>
              ) : null}
              {forn ? (
                <AbreCartao alvo="q4">
                  <span className="lb">Quem vendeu ou prestou serviço</span>
                  <span className="n">
                    {forn.total_empresas === 0
                      ? "Nenhuma empresa"
                      : `${forn.total_empresas} ${forn.total_empresas === 1 ? "empresa" : "empresas"}`}
                  </span>
                  <span className="s">
                    {forn.total_empresas === 0
                      ? `teve nota reembolsada em ${forn.ano}.`
                      : `${forn.total_empresas === 1 ? "teve" : "tiveram"} notas reembolsadas em ${forn.ano}.`}
                  </span>
                  <span className="go">Entender →</span>
                </AbreCartao>
              ) : null}
            </div>
          </>
        )}

        {salario ? (
          <Pergunta id="q1" titulo="Quanto ganha?" resposta={reais(salario.basica_centavos)}>
            <Linha titulo="O que é">
              O que o Senado paga ao senador todo mês pelo trabalho no mandato, como aparece na folha
              de pagamento do Senado. Não é a verba para despesas, que é outra coisa e aparece mais
              abaixo.
            </Linha>
            <Linha titulo="Quanto" destaque>
              <mark>{reais(salario.basica_centavos)}</mark> de salário-base e{" "}
              <b>{reais(salario.liquida_centavos)}</b> depois dos descontos, em {mesAno(salario.mes, salario.ano)}.
              <p className="src">
                O salário-base (que o Senado chama de remuneração básica) é o valor do salário no mês,
                antes dos descontos. Os descontos que aparecem na folha são a previdência e o imposto
                de renda. Em alguns meses a folha traz também outros valores, como auxílios e
                gratificação natalina (13º), que entram na conta do valor depois dos descontos.
              </p>
            </Linha>
            <Origem
              onde="Na folha de pagamento mensal que o Senado publica no portal de transparência."
              como="A folha traz nomes, e não o código do senador. Ligamos os dois pela página de identificação do próprio portal do Senado e só mostramos o valor quando a ligação é segura: um único cadastro (matrícula) com esse nome e uma única folha normal no mês."
              atualizado={atualizado}
              href={portal}
              textoLink="Ver a página do senador no portal do Senado"
            />
          </Pergunta>
        ) : null}

        {cota ? (
          <Pergunta id="q2" titulo="Quanto usou da verba do mandato?" resposta={reaisMil(cota.total_centavos)}>
            <Linha titulo="O que é">
              Dinheiro que o Senado <b>devolve</b> (reembolsa) ao senador por despesas do trabalho no
              mandato, como passagens, aluguel de escritório e divulgação. Não é salário. O nome
              oficial é{" "}
              <b>Cota para o Exercício da Atividade Parlamentar dos Senadores</b> (CEAPS).
            </Linha>
            <Linha titulo="Quanto" destaque>
              <mark>
                {reaisMil(cota.total_centavos)} {periodoAno(periodoCota, cota.ano)}
              </mark>
              {variosMeses ? `, uma média de ${reaisMil(mediaMensal)} por mês.` : "."}
              <GraficoMensal
                meses={cota.meses}
                maiorMes={variosMeses ? cota.maior_mes.mes : 0}
                ano={cota.ano}
              />
              {cota.parcial ? (
                <p className="src">
                  {cota.ano} ainda não terminou: os números mudam conforme o Senado publica novas
                  despesas.
                </p>
              ) : null}
              {semNotasRecentes ? (
                <p className="src">
                  Nos dados do Senado não há nota reembolsada depois de {nomeMes(ultimoMesCota)}. Por
                  isso o período termina em {nomeMes(ultimoMesCota)}.
                </p>
              ) : null}
              {variosMeses ? (
                <div className="note alert">
                  <Info />
                  <div>
                    <b>
                      Mês de maior uso: {mesAno(cota.maior_mes.mes, cota.ano)},{" "}
                      {reaisMil(cota.maior_mes.total_centavos)}.
                    </b>{" "}
                    É o maior valor {periodoCota}. Mostramos só o número; cada pessoa tira a sua
                    conclusão.
                  </div>
                </div>
              ) : null}
            </Linha>
            <Origem
              onde="Na página do senador, no portal de transparência do Senado, em “Recursos utilizados”, e nas planilhas de despesas que o Senado publica."
              como={`Somamos o valor de cada nota reembolsada ao senador ${periodoAno(periodoCota, cota.ano)} e conferimos o resultado com o resumo que o próprio Senado publica.`}
              atualizado={atualizado}
              href={portal}
              textoLink="Ver a página do senador no portal do Senado"
            />
          </Pergunta>
        ) : null}

        {cota ? (
          <Pergunta
            id="q3"
            titulo="Em que usou a verba?"
            resposta={`${cota.categorias[0].nome}: ${Math.round((Math.max(cota.categorias[0].total_centavos, 0) / Math.max(cota.total_centavos, 1)) * 100)}%`}
          >
            <Linha titulo="O que é">
              O Senado coloca cada nota reembolsada em um tipo de despesa, como passagens ou escritório.
              Esse tipo se chama categoria. Notas que o Senado não classificou aparecem como “Sem
              categoria”.
            </Linha>
            <Linha titulo="Quanto" destaque>
              Os <mark>{reaisMil(cota.total_centavos)}</mark> usados {periodoAno(periodoCota, cota.ano)} se
              dividem assim:
              <Barras
                itens={cota.categorias.map((c) => ({ nome: c.nome, valor: c.total_centavos }))}
                total={cota.total_centavos}
              />
            </Linha>
            <Origem
              onde="Na página do senador, no portal de transparência do Senado, e nas planilhas de despesas. Cada nota reembolsada informa a sua categoria."
              como="Somamos o valor das notas de cada categoria. Notas sem categoria entram em “Sem categoria”. Usamos nomes mais curtos para as categorias; o nome completo de cada uma está na página do senador no portal do Senado."
              atualizado={atualizado}
              href={portal}
              textoLink="Ver a página do senador no portal do Senado"
            />
          </Pergunta>
        ) : null}

        {forn ? (
          <Pergunta id="q4" titulo="Quem vendeu ou prestou serviço?" resposta="Empresas e pessoas">
            <Linha titulo="O que é">
              As empresas e as pessoas que venderam algo ou prestaram um serviço ao senador, e cujas
              notas o Senado reembolsou. O reembolso vai para o senador; a nota mostra quem recebeu
              dele.
            </Linha>
            <Linha titulo="Quanto" destaque>
              {forn.empresas.length > 0 ? (
                <>
                  Empresas que mais receberam em {forn.ano}
                  {forn.total_empresas > forn.empresas.length
                    ? ` (as ${forn.empresas.length} com os maiores valores, de ${forn.total_empresas})`
                    : ""}
                  :
                  <Barras
                    itens={forn.empresas.map((e) => ({ nome: e.nome, valor: e.total_centavos }))}
                    total={cota?.ano === forn.ano ? cota.total_centavos : forn.empresas.reduce((s, e) => s + e.total_centavos, 0)}
                  />
                </>
              ) : (
                <>Nenhuma empresa recebeu reembolso em {forn.ano}.</>
              )}
              {pessoasFisicas ? (
                <div className="note">
                  <b>Pagamentos a pessoas (não a empresas)</b>
                  <br />
                  Além das empresas, houve{" "}
                  <b>{pessoasFisicas.qtd_despesas} pagamentos feitos diretamente a pessoas</b>, que somam{" "}
                  <b>{reaisMil(pessoasFisicas.total_centavos)}</b>. Mostramos só o total, sem nomes nem
                  CPF, para proteger a privacidade delas. Os nomes estão nas planilhas de despesas do
                  Senado.
                </div>
              ) : null}
              {outrosQtd > 0 ? (
                <p className="src">
                  {outrosQtd === 1 ? "Outro pagamento não traz" : `Outros ${outrosQtd} pagamentos não trazem`}{" "}
                  um CNPJ ou CPF que possamos usar (o Senado não informou ou informou fora do
                  padrão), somando {reaisMil(outrosTotal)}. Por isso não entram na lista de empresas.
                </p>
              ) : null}
            </Linha>
            <Origem
              onde="Nas planilhas de despesas que o Senado publica: cada nota informa quem vendeu o produto ou prestou o serviço, uma empresa ou uma pessoa."
              como="Somamos o valor das notas de cada empresa, identificada pelo CNPJ (o número de registro da empresa). Os pagamentos a pessoas ficam todos juntos, sem nome nem CPF."
              atualizado={atualizado}
              href={portal}
              textoLink="Ver a página do senador no portal do Senado"
            />
          </Pergunta>
        ) : null}

        {temContato || equipe ? (
          <Pergunta
            id="q5"
            titulo="Gabinete: endereço, contato e equipe"
            resposta={equipe ? pessoas(equipe.pessoas) : "Contato"}
          >
            <Linha titulo="O que é">
              O <b>gabinete</b> é o escritório do senador dentro do Senado Federal. Aqui estão o
              endereço, os contatos oficiais e quantas pessoas, segundo o Senado, trabalham nele.
            </Linha>
            {contato?.endereco ? <Linha titulo="Onde fica">{contato.endereco}</Linha> : null}
            {contato && (contato.telefones.length > 0 || contato.email) ? (
              <Linha titulo="Contato">
                {contato.telefones.map((t) => (
                  <div key={t}>{telefone(t)}</div>
                ))}
                {contato.email ? <Email endereco={contato.email} /> : null}
              </Linha>
            ) : null}
            {equipe ? (
              <Linha titulo="Equipe" destaque>
                <div className="two">
                  <div className="place">
                    <h4>Gabinete</h4>
                    <p className="big">{equipe.pessoas}</p>
                    <p>{equipe.pessoas === 1 ? "pessoa na equipe" : "pessoas na equipe"}</p>
                  </div>
                </div>
                <p className="src">Mostramos só o número de pessoas, nunca nomes.</p>
              </Linha>
            ) : null}
            <Origem
              onde="Na página do senador, no portal de transparência do Senado: endereço, telefone e e-mail em “Dados pessoais”, e o número de pessoas em “Recursos utilizados”."
              como="Copiamos o endereço, o telefone e o e-mail como o Senado publica. Quando o Senado abrevia vários telefones (por exemplo, “3303-6187 / 6188”), mostramos cada número completo. Da equipe, mostramos só quantas pessoas são, nunca nomes."
              atualizado={atualizado}
              href={portal}
              textoLink="Ver a página do senador no portal do Senado"
            />
          </Pergunta>
        ) : null}

        {moradia ? (
          <Pergunta id="q7" titulo="Usa moradia do Senado?" resposta={respostaMoradia}>
            <Linha titulo="O que é">
              O <b>imóvel funcional</b> é uma moradia que pertence à União (o governo federal) e é cedida
              ao senador. O <b>auxílio-moradia</b> é um valor em dinheiro pago ao senador que não
              ocupa imóvel funcional, para ajudar com aluguel ou hotel.
            </Linha>
            <Linha titulo="Quanto" destaque>
              <div className="ben2">
                <div className="bn">
                  <b>Imóvel funcional</b>
                  <Chip usou={imovel > 0} texto={usoTexto(imovel, mesesMoradia)} />
                </div>
                <div className="bn">
                  <b>Auxílio-moradia</b>
                  <Chip usou={auxilio > 0} texto={usoTexto(auxilio, mesesMoradia)} />
                </div>
              </div>
              <p className="src">
                {mesesMoradia > 0
                  ? `Período analisado: ${periodoAno(periodo(moradia.meses.map((m) => Number(m.mes.slice(5)))), moradia.ano)}.`
                  : `O Senado não registra uso de nenhum dos dois em ${moradia.ano}.`}
              </p>
            </Linha>
            <Origem
              onde="Na página de benefícios do senador, no portal de transparência do Senado, que informa o uso mês a mês."
              como={`Contamos os meses em que o Senado informa que o senador usou cada benefício, e conferimos ${ano === anoDosDados ? "quatro" : "três"} publicações do Senado entre si.`}
              atualizado={atualizado}
              href={portal}
              textoLink="Ver a página do senador no portal do Senado"
            />
          </Pergunta>
        ) : null}

        <div className="more">
          <h3>Como pesquisar mais</h3>
          <p>
            O Senadados mostra valores e ajuda a entendê-los, mas{" "}
            <b>não julga se algo está dentro ou fora da lei</b>. Para investigar, comece pelo portal de
            transparência do próprio Senado, onde ficam as páginas de cada senador e as normas
            publicadas.
          </p>
          <p>
            <a href={portal} rel="noopener noreferrer" target="_blank">
              Página de {nome} no portal de transparência do Senado ↗
            </a>
          </p>
        </div>
      </main>
    </div>
  );
}
