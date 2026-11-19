import { AbreCartao } from "./AbreCartao";
import { Barras, GraficoMensal, Linha, Origem, Pergunta } from "./perguntas";
import {
  dataBr, iniciais, nomeEstado, nomeMes, periodo, reais, reaisMil, telefone, tituloNome, usoTexto,
} from "@/lib/formato";
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

export function PerfilPagina({ perfil, dataReferencia }: { perfil: Perfil; dataReferencia: string }) {
  const nome = tituloNome(perfil.nome);
  const atualizado = dataBr(dataReferencia);
  const portal = `https://www6g.senado.leg.br/transparencia/sen/${perfil.codigo}/`;

  const cota = perfil.cota?.anos.at(-1) ?? null;
  const mesesCota = cota?.meses.map((m) => m.mes) ?? [];
  const periodoCota = periodo(mesesCota);
  const mediaMensal = cota ? Math.round(cota.total_centavos / Math.max(cota.meses.length, 1)) : 0;
  const forn =
    perfil.fornecedores?.anos.find((a) => a.ano === cota?.ano) ??
    perfil.fornecedores?.anos.at(-1) ??
    null;

  const { salario, equipe, contato, moradia } = perfil;
  const anoResumo = cota?.ano ?? salario?.ano ?? equipe?.ano ?? moradia?.ano ?? null;

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
        <div className="av" aria-hidden="true">
          {iniciais(perfil.nome)}
        </div>
        <div>
          <h1>{nome}</h1>
          <div className="tags">
            <span className="tag fill">{perfil.partido}</span>
            <span className="tag">
              {perfil.uf} · {nomeEstado(perfil.uf)}
            </span>
          </div>
        </div>
        <dl>
          <dt>Cargo</dt>
          <dd>{perfil.tipo}</dd>
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
        <p className="help">Fonte: Senado Federal. Dados de {atualizado}.</p>
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
              <span>
                {periodoCota ? `${maiuscula(periodoCota.replace(/^de /, ""))} · ` : ""}toque num
                cartão para entender
              </span>
            </div>
            <div className="sum">
              {salario ? (
                <AbreCartao alvo="q1">
                  <span className="lb">Salário</span>
                  <span className="n">{reais(salario.basica_centavos)}</span>
                  <span className="s">remuneração básica do mês.</span>
                  <span className="s">Líquido: {reais(salario.liquida_centavos)}</span>
                  <span className="go">Entender →</span>
                </AbreCartao>
              ) : null}
              {cota ? (
                <>
                  <AbreCartao alvo="q2">
                    <span className="lb">Verba do mandato usada (cota)</span>
                    <span className="n">{reaisMil(cota.total_centavos)}</span>
                    <span className="s">
                      Em média {reaisMil(mediaMensal)} por mês{periodoCota ? `, ${periodoCota}` : ""}.
                    </span>
                    <span className="go">Entender →</span>
                  </AbreCartao>
                  <AbreCartao alvo="q2">
                    <span className="lb">Maior mês da verba</span>
                    <span className="n">{maiuscula(nomeMes(cota.maior_mes.mes))}</span>
                    <span className="s">
                      {reaisMil(cota.maior_mes.total_centavos)}, o valor mais alto {periodoCota}.
                    </span>
                    <span className="go">Ver no gráfico →</span>
                  </AbreCartao>
                </>
              ) : null}
              {equipe ? (
                <AbreCartao alvo="q5">
                  <span className="lb">Quem trabalha no gabinete</span>
                  <span className="n">{pessoas(equipe.pessoas)}</span>
                  <span className="s">no gabinete do Senado Federal.</span>
                  <span className="go">Entender →</span>
                </AbreCartao>
              ) : null}
              {moradia ? (
                <AbreCartao alvo="q7">
                  <span className="lb">Moradia</span>
                  <div className="chips">
                    <Chip usou={imovel > 0} texto={`Imóvel funcional: ${imovel > 0 ? usoTexto(imovel, mesesMoradia).toLowerCase().replace("usou em ", "") : "não usou"}`} />
                    <Chip usou={auxilio > 0} texto={`Auxílio-moradia: ${auxilio > 0 ? usoTexto(auxilio, mesesMoradia).toLowerCase().replace("usou em ", "") : "não usou"}`} />
                  </div>
                  <span className="go">Entender →</span>
                </AbreCartao>
              ) : null}
            </div>
          </>
        )}

        {salario ? (
          <Pergunta id="q1" titulo="Quanto ganha?" resposta={reais(salario.basica_centavos)}>
            <Linha titulo="O que é">
              O pagamento mensal do senador pelo mandato, como aparece na folha de pagamento do
              Senado. É diferente da verba, que reembolsa despesas.
            </Linha>
            <Linha titulo="Quanto" destaque>
              <mark>{reais(salario.basica_centavos)}</mark> de remuneração básica e{" "}
              <b>{reais(salario.liquida_centavos)}</b> líquidos em {nomeMes(salario.mes)} de{" "}
              {salario.ano}, depois dos descontos.
              <p className="src">
                A remuneração básica não é o total antes dos descontos: a folha do Senado tem outros
                componentes.
              </p>
            </Linha>
            <Origem
              onde="Na folha de pagamento mensal que o Senado publica no portal de transparência."
              como="Ligamos a folha ao senador pela página de identificação que o próprio portal mostra para o código dele. Só mostramos o valor quando há uma única matrícula e uma única folha normal no mês."
              atualizado={atualizado}
              href={portal}
              textoLink="Ver a página do senador no portal do Senado"
            />
          </Pergunta>
        ) : null}

        {cota ? (
          <Pergunta id="q2" titulo="Quanto usou da verba?" resposta={reaisMil(cota.total_centavos)} aberta>
            <Linha titulo="O que é">
              Dinheiro que o Senado <b>reembolsa</b> ao senador por despesas ligadas ao mandato, como
              passagens, escritório e divulgação. O Senado chama de{" "}
              <b>Cota para o Exercício da Atividade Parlamentar dos Senadores</b> (CEAPS).
            </Linha>
            <Linha titulo="Quanto" destaque>
              <mark>
                {reaisMil(cota.total_centavos)} {periodoCota} de {cota.ano}
              </mark>
              , em média {reaisMil(mediaMensal)} por mês.
              <GraficoMensal meses={cota.meses} maiorMes={cota.maior_mes.mes} ano={cota.ano} />
              {cota.parcial ? (
                <p className="src">Os dados de {cota.ano} estão incompletos, porque o ano ainda está em andamento.</p>
              ) : null}
            </Linha>
            <Origem
              onde="Na página do senador, no portal de transparência do Senado, em “Recursos utilizados”, e nas planilhas de despesas que o Senado publica."
              como={`Somamos o valor de cada nota reembolsada ao senador ${periodoCota} de ${cota.ano} e conferimos o resultado com o resumo que o próprio Senado publica.`}
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
              O Senado classifica cada nota reembolsada em um grupo, chamado de categoria. Notas sem
              grupo aparecem como “Sem categoria”.
            </Linha>
            <Linha titulo="Quanto" destaque>
              Como os <mark>{reaisMil(cota.total_centavos)}</mark> usados {periodoCota} de {cota.ano} se
              dividem:
              <Barras
                itens={cota.categorias.map((c) => ({ nome: c.nome, valor: c.total_centavos }))}
                total={cota.total_centavos}
              />
            </Linha>
            <Origem
              onde="Na página do senador, no portal de transparência do Senado, e nas planilhas de despesas. Cada nota reembolsada informa a sua categoria."
              como="Somamos o valor das notas de cada categoria. Notas sem categoria entram em “Sem categoria”. Usamos nomes mais curtos para as categorias; o nome completo de cada uma está na página do senador, no Senado."
              atualizado={atualizado}
              href={portal}
              textoLink="Ver a página do senador no portal do Senado"
            />
          </Pergunta>
        ) : null}

        {forn ? (
          <Pergunta id="q4" titulo="Quem recebeu o dinheiro?" resposta="Empresas e pessoas">
            <Linha titulo="O que é">
              As empresas e as pessoas que receberam os reembolsos. Só aparece quem foi reembolsado.
            </Linha>
            <Linha titulo="Quanto" destaque>
              {forn.empresas.length > 0 ? (
                <>
                  Empresas que mais receberam em {forn.ano}
                  {forn.total_empresas > forn.empresas.length
                    ? ` (as ${forn.empresas.length} maiores, de ${forn.total_empresas})`
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
                  Além das empresas, o senador reembolsou{" "}
                  <b>{pessoasFisicas.qtd_despesas} pagamentos feitos diretamente a pessoas</b>, que somam{" "}
                  <b>{reaisMil(pessoasFisicas.total_centavos)}</b>. Aqui mostramos só o total, sem nome e
                  sem CPF, porque essas pessoas não são políticas. Os nomes estão nas planilhas de
                  despesas do Senado.
                </div>
              ) : null}
              {outrosQtd > 0 ? (
                <p className="src">
                  Mais {outrosQtd} {outrosQtd === 1 ? "pagamento tem" : "pagamentos têm"} documento fora do
                  padrão ou não informado pelo Senado, somando {reaisMil(outrosTotal)}.
                </p>
              ) : null}
            </Linha>
            <Origem
              onde="Nas planilhas de despesas que o Senado publica: cada nota informa quem recebeu o dinheiro, uma empresa ou uma pessoa."
              como="Somamos o valor recebido por cada empresa, identificada pelo CNPJ. Os pagamentos a pessoas ficam todos juntos, sem nome nem CPF."
              atualizado={atualizado}
              href={portal}
              textoLink="Ver a página do senador no portal do Senado"
            />
          </Pergunta>
        ) : null}

        {temContato || equipe ? (
          <Pergunta
            id="q5"
            titulo="Gabinete: onde fica, contato e equipe"
            resposta={equipe ? pessoas(equipe.pessoas) : "Contato"}
          >
            <Linha titulo="O que é">
              O <b>gabinete</b> é o espaço do senador dentro do Senado Federal. Aqui estão o endereço, o
              contato oficial e a quantidade de pessoas que o Senado informa que trabalham nele.
            </Linha>
            {contato?.endereco ? <Linha titulo="Onde fica">{contato.endereco}</Linha> : null}
            {contato && (contato.telefones.length > 0 || contato.email) ? (
              <Linha titulo="Como falar">
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
              como="Copiamos o endereço, o telefone e o e-mail como o Senado publica. Quando o Senado escreve vários telefones de forma abreviada (por exemplo, “3303-6187 / 6188”), mostramos cada número completo. Do gabinete, mostramos só a quantidade de pessoas, nunca nomes."
              atualizado={atualizado}
              href={portal}
              textoLink="Ver a página do senador no portal do Senado"
            />
          </Pergunta>
        ) : null}

        {moradia ? (
          <Pergunta id="q7" titulo="Usa moradia do Senado?" resposta={respostaMoradia}>
            <Linha titulo="O que é">
              O <b>imóvel funcional</b> é um imóvel residencial de propriedade da União cedido ao
              senador. O <b>auxílio-moradia</b> é um valor pago ao senador que não ocupa apartamento
              funcional, para cobrir aluguel ou diária de hotel.
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
                  ? `Período analisado: ${periodo(moradia.meses.map((m) => Number(m.mes.slice(5))))} de ${moradia.ano}.`
                  : `O Senado não registra uso de nenhum dos dois em ${moradia.ano}.`}
              </p>
            </Linha>
            <Origem
              onde="Na página de benefícios do senador, no portal de transparência do Senado, que informa o uso mês a mês."
              como="Contamos os meses em que o Senado informa que o senador usou cada benefício, e conferimos quatro publicações do Senado entre si."
              atualizado={atualizado}
              href={portal}
              textoLink="Ver a página do senador no portal do Senado"
            />
          </Pergunta>
        ) : null}

        {cota ? (
          <div className="note alert">
            <Info />
            <div>
              <b>
                Maior mês: {nomeMes(cota.maior_mes.mes)} de {cota.ano}, {reaisMil(cota.maior_mes.total_centavos)}.
              </b>{" "}
              É o valor mais alto {periodoCota}. Mostramos só o fato; o que ele significa, cada pessoa
              avalia.
            </div>
          </div>
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
