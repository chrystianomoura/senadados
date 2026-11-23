-- 004_perfil.sql: a foto oficial e o mandato de cada senador, provados por duas listas do Senado (D045).
-- publico.perfil só tem linha de quem teve foto ou mandato provado; campo vazio = não provado (cada um tem o seu
-- freio de segurança, D037). O detalhe da verificação fica no esquema interno, sem texto livre no publico.

CREATE TABLE publico.perfil (
    cod_senador    integer PRIMARY KEY REFERENCES publico.senadores,
    foto_url       text,
    mandato_inicio date,
    mandato_fim    date
);

CREATE TABLE interno.verificacao_perfil (
    cod_senador integer NOT NULL,
    campo       text    NOT NULL CHECK (campo IN ('foto', 'mandato')),
    resultado   text    NOT NULL CHECK (resultado IN ('identico', 'explicado', 'sem_explicacao')),
    detalhe     text,
    exibir      boolean NOT NULL,
    PRIMARY KEY (cod_senador, campo)
);

-- Tabela nova não herda permissão (002): concede aqui o que cada papel precisa.
GRANT SELECT, INSERT, DELETE, TRUNCATE ON publico.perfil, interno.verificacao_perfil TO sd_carga;
GRANT SELECT ON publico.perfil TO sd_leitura;
