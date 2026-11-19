-- 001_esquemas.sql: cria os dois esquemas do banco (D042) e as tabelas.
--   publico: só o que passou nas verificações (exibir = 1). A API e o site leem só ele. Ausência de um dado = "não verificado".
--   interno: o detalhe de cada verificação (resultado e motivo). Ninguém de fora lê.
-- Valores em dinheiro ficam em centavos inteiros (D034). Nenhum nome de pessoa que não seja senador, nenhum CPF.
-- Tabelas não herdam permissão: a 002 concede, tabela por tabela, o que cada papel precisa.

CREATE SCHEMA publico;
CREATE SCHEMA interno;

-- ---------------------------------------------------------------------------
-- publico
-- ---------------------------------------------------------------------------
CREATE TABLE publico.senadores (
    cod_senador integer PRIMARY KEY,
    nome        text    NOT NULL,
    tipo        text    NOT NULL,
    uf          char(2) NOT NULL,
    partido     text    NOT NULL
);

-- Cota por senador, ano, mês e categoria. Só entram os pares senador-ano que passaram na verificação da cota (D035).
CREATE TABLE publico.despesas_mensais (
    cod_senador    integer  NOT NULL REFERENCES publico.senadores,
    ano            smallint NOT NULL,
    mes            smallint NOT NULL CHECK (mes BETWEEN 1 AND 12),
    categoria      text     NOT NULL,
    valor_centavos bigint   NOT NULL,
    qtd_despesas   integer  NOT NULL CHECK (qtd_despesas > 0),
    PRIMARY KEY (cod_senador, ano, mes, categoria)
);

-- Maiores fornecedores: só empresas (CNPJ válido), pelo mesmo critério de exibição da cota do senador-ano.
CREATE TABLE publico.fornecedores_anuais (
    cod_senador    integer  NOT NULL REFERENCES publico.senadores,
    ano            smallint NOT NULL,
    cnpj           text     NOT NULL,
    nome           text     NOT NULL,
    qtd_despesas   integer  NOT NULL CHECK (qtd_despesas > 0),
    valor_centavos bigint   NOT NULL,
    PRIMARY KEY (cod_senador, ano, cnpj)
);

-- Quem não é empresa fica agrupado, sem nome e sem documento (D008): pessoas físicas, documentos fora do padrão e sem documento.
CREATE TABLE publico.fornecedores_agrupados_anuais (
    cod_senador    integer  NOT NULL REFERENCES publico.senadores,
    ano            smallint NOT NULL,
    tipo           text     NOT NULL CHECK (tipo IN ('pessoa_fisica', 'outro', 'sem_documento')),
    qtd_despesas   integer  NOT NULL CHECK (qtd_despesas > 0),
    total_centavos bigint   NOT NULL,
    maior_centavos bigint   NOT NULL,
    PRIMARY KEY (cod_senador, ano, tipo)
);

-- Contato do gabinete. Campo vazio = não provado ou inexistente nas duas fontes (D040).
CREATE TABLE publico.contato (
    cod_senador integer PRIMARY KEY REFERENCES publico.senadores,
    endereco    text,
    telefones   text,
    email       text
);

-- Número de pessoas do gabinete (só o número, nunca nomes: D007). Só para quem foi provado (D036, D037).
CREATE TABLE publico.equipe (
    cod_senador integer  NOT NULL REFERENCES publico.senadores,
    ano         smallint NOT NULL,
    pessoas     smallint NOT NULL CHECK (pessoas >= 0),
    PRIMARY KEY (cod_senador, ano)
);

-- Uso de moradia mês a mês (D039). `mes` no formato AAAA-MM, como a página mensal do Senado.
CREATE TABLE publico.moradia_meses (
    cod_senador      integer  NOT NULL REFERENCES publico.senadores,
    ano              smallint NOT NULL,
    mes              char(7)  NOT NULL CHECK (mes ~ '^\d{4}-(0[1-9]|1[0-2])$'),
    auxilio_moradia  boolean  NOT NULL,
    imovel_funcional boolean  NOT NULL,
    PRIMARY KEY (cod_senador, mes)
);

-- Remuneração do mês da folha, só para quem passou nas cinco provas (D041).
CREATE TABLE publico.salario (
    cod_senador                  integer  NOT NULL REFERENCES publico.senadores,
    ano                          smallint NOT NULL,
    mes                          smallint NOT NULL CHECK (mes BETWEEN 1 AND 12),
    remuneracao_basica_centavos  bigint   NOT NULL CHECK (remuneracao_basica_centavos > 0),
    remuneracao_liquida_centavos bigint   NOT NULL CHECK (remuneracao_liquida_centavos > 0),
    PRIMARY KEY (cod_senador, ano, mes)
);

-- Página "Verificações": contagens por verificação e ano, sem nomes (D042, decisão 5).
CREATE TABLE publico.verificacoes_resumo (
    verificacao   text        NOT NULL,
    ano           smallint    NOT NULL,
    identicos     integer     NOT NULL CHECK (identicos >= 0),
    explicados    integer     NOT NULL CHECK (explicados >= 0),
    pendentes     integer     NOT NULL CHECK (pendentes >= 0),
    ocultos       integer     NOT NULL CHECK (ocultos >= 0),
    verificado_em timestamptz NOT NULL,
    PRIMARY KEY (verificacao, ano)
);

-- Por que cada dado ficou oculto ou pendente: um motivo de uma lista fechada, que o código da carga define. Nunca texto livre.
CREATE TABLE publico.verificacoes_motivos (
    verificacao text     NOT NULL,
    ano         smallint NOT NULL,
    situacao    text     NOT NULL CHECK (situacao IN ('pendente', 'oculto')),
    motivo      text     NOT NULL,
    qtd         integer  NOT NULL CHECK (qtd > 0),
    PRIMARY KEY (verificacao, ano, situacao, motivo)
);

-- Fontes e datas da carga (D009: toda informação indica a fonte e a data de atualização).
CREATE TABLE publico.metadados (
    chave text PRIMARY KEY,
    valor text NOT NULL
);

-- ---------------------------------------------------------------------------
-- interno (o detalhe; `detalhe` é gerado pelo código e não traz nomes de pessoas, conferido em 18/11/2026)
-- ---------------------------------------------------------------------------
CREATE TABLE interno.verificacao_cota (
    cod_senador            integer  NOT NULL,
    ano                    smallint NOT NULL,
    despesas_centavos      bigint   NOT NULL,
    resumo_centavos        bigint   NOT NULL,
    sem_categoria_centavos bigint   NOT NULL,
    resultado              text     NOT NULL CHECK (resultado IN ('identico', 'explicado', 'sem_explicacao')),
    detalhe                text,
    PRIMARY KEY (cod_senador, ano)
);

CREATE TABLE interno.verificacao_equipe (
    cod_senador   integer  NOT NULL,
    ano           smallint NOT NULL,
    equipe_resumo integer,
    equipe_lista  integer,
    resultado     text     NOT NULL CHECK (resultado IN ('identico', 'explicado', 'sem_explicacao')),
    detalhe       text,
    exibir        boolean  NOT NULL,
    PRIMARY KEY (cod_senador, ano)
);

CREATE TABLE interno.verificacao_moradia (
    cod_senador integer  NOT NULL,
    ano         smallint NOT NULL,
    resultado   text     NOT NULL CHECK (resultado IN ('identico', 'explicado', 'pendente', 'sem_explicacao')),
    detalhe     text,
    exibir      boolean  NOT NULL,
    PRIMARY KEY (cod_senador, ano)
);

CREATE TABLE interno.verificacao_salario (
    cod_senador integer  NOT NULL,
    ano         smallint NOT NULL,
    mes         smallint NOT NULL,
    resultado   text     NOT NULL CHECK (resultado IN ('identico', 'explicado', 'sem_explicacao')),
    detalhe     text,
    exibir      boolean  NOT NULL,
    PRIMARY KEY (cod_senador, ano, mes)
);

CREATE TABLE interno.verificacao_contato (
    cod_senador integer NOT NULL,
    campo       text    NOT NULL CHECK (campo IN ('endereco', 'telefones', 'email')),
    resultado   text    NOT NULL CHECK (resultado IN ('identico', 'explicado', 'sem_explicacao')),
    detalhe     text,
    exibir      boolean NOT NULL,
    PRIMARY KEY (cod_senador, campo)
);

CREATE TABLE interno.verificacoes (
    nome           text        NOT NULL,
    ano            smallint    NOT NULL,
    identicos      integer     NOT NULL,
    explicados     integer     NOT NULL,
    sem_explicacao integer     NOT NULL,
    verificado_em  timestamptz NOT NULL,
    PRIMARY KEY (nome, ano)
);

-- Controle das migrações aplicadas (o executor `senadados_pipeline.migrar` grava aqui).
CREATE TABLE interno.migracoes (
    versao      text        PRIMARY KEY,
    aplicada_em timestamptz NOT NULL DEFAULT now()
);
