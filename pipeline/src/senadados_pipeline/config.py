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
