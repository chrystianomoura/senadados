-- 002_papeis.sql: dá a cada papel de banco só o que a sua tarefa precisa (D042, menor privilégio).
--   sd_carga:   escreve. Usado pela rotina diária que recarrega os dados. Não cria nem apaga tabelas.
--   sd_leitura: só lê o esquema publico. Usado pela API. Não enxerga o esquema interno.
-- Os papéis nascem fora das migrações, sem permissão nenhuma e sem senha neste repositório; esta migração só concede.
-- Tabela nova de uma migração futura NÃO herda permissão: cada migração concede explicitamente (nada de DEFAULT PRIVILEGES).

DO $$
BEGIN
    IF (SELECT count(*) FROM pg_roles WHERE rolname IN ('sd_carga', 'sd_leitura')) < 2 THEN
        RAISE EXCEPTION 'Faltam os papéis sd_carga e/ou sd_leitura: crie-os antes (sem permissão nenhuma) e rode de novo';
    END IF;
END $$;

GRANT USAGE ON SCHEMA publico, interno TO sd_carga;
GRANT SELECT, INSERT, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA publico TO sd_carga;
-- Não há UPDATE de propósito: a carga apaga e recarrega.
GRANT SELECT, INSERT, DELETE, TRUNCATE ON
    interno.verificacao_cota, interno.verificacao_equipe, interno.verificacao_moradia,
    interno.verificacao_salario, interno.verificacao_contato, interno.verificacoes
TO sd_carga;

GRANT USAGE ON SCHEMA publico TO sd_leitura;
GRANT SELECT ON ALL TABLES IN SCHEMA publico TO sd_leitura;
-- interno.migracoes: nem sd_carga nem sd_leitura tocam; só o dono (executor das migrações).
