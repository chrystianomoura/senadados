"""Constantes compartilhadas pelas etapas do pipeline."""

from pathlib import Path

BASE_URL = "https://adm.senado.gov.br/adm-dadosabertos/api/v1"

# A cota (CEAPS) tem despesas a partir de 2008.
FIRST_YEAR = 2008

ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "data" / "raw"
CLEAN_DB = ROOT / "data" / "limpo" / "senadados.sqlite"
