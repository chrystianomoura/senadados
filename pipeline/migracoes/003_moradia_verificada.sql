-- 003_moradia_verificada.sql: diz QUEM teve a moradia provada, mesmo sem nenhum mês de uso.
-- A tabela publico.moradia_meses só tem linhas de quem usou algum benefício. Sem esta tabela, quem foi provado e
-- não usou nenhum benefício (nenhuma linha) não se distinguia de quem não foi provado (também nenhuma linha), e o
-- site não saberia dizer "não usou" nem calar. Descoberto ao escrever o exportador dos dados do site (D044).

CREATE TABLE publico.moradia_verificada (
    cod_senador integer  NOT NULL REFERENCES publico.senadores,
    ano         smallint NOT NULL,
    PRIMARY KEY (cod_senador, ano)
);

-- Tabela nova não herda permissão (002): concede aqui o que cada papel precisa.
GRANT SELECT, INSERT, DELETE, TRUNCATE ON publico.moradia_verificada TO sd_carga;
GRANT SELECT ON publico.moradia_verificada TO sd_leitura;
