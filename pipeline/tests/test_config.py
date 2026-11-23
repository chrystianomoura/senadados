from datetime import date

from senadados_pipeline.config import anos_do_projeto


def test_o_projeto_processa_o_ano_atual_e_o_anterior():
    assert anos_do_projeto(date(2026, 11, 23)) == [2025, 2026]
    assert anos_do_projeto(date(2027, 1, 2)) == [2026, 2027]
