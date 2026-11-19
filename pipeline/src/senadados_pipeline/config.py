"""Constantes compartilhadas pelas etapas do pipeline."""

from pathlib import Path

BASE_URL = "https://adm.senado.gov.br/adm-dadosabertos/api/v1"

# Portal de transparência: a única fonte do uso mensal de moradia (não há API para isso).
PORTAL_URL = "https://www6g.senado.leg.br/transparencia"

# A cota (CEAPS) tem despesas a partir de 2008.
FIRST_YEAR = 2008

ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "data" / "raw"
CLEAN_DB = ROOT / "data" / "limpo" / "senadados.sqlite"

# Acima dessa fração de falhas num dado descritivo, ele some para todos (D037).
MAX_FAILURE_RATE = 0.05

# Identificação do pipeline nas consultas ao Senado (sem dados pessoais).
USER_AGENT = "senadados-pipeline/0.1"

# Migrações SQL do banco na nuvem (D042), aplicadas em ordem pelo `migrar`.
MIGRACOES_DIR = ROOT / "pipeline" / "migracoes"
