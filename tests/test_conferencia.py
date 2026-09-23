"""KPIs do painel (árvore de acessibilidade real, run 35814261045) lidos só para conferência × Torre."""
from unittest.mock import MagicMock

from assobens.emplacamentos_downloader import AssobensEmplacamentosDownloader
from assobens.kpi import AssobensKpiService
from assobens.browser import load_selectors

ARIA = """- application:
  - region "Relatório do Power BI":
    - link "Navegação na página . Clique aqui para realizar o download do relatório analítico em Excel"
    - group "Atualizado em:":
      - img "formatted mais recente 22/09/2026.": 22/09/2026
    - group "Total Mercedes-Benz":
      - img "Total Mercedes-Benz 453.": "453"
    - group:
      - heading "Região MB" [level=3]
      - combobox "Região MB": Todos
    - group:
      - heading "Distrito" [level=3]
      - combobox "Distrito": Todos
    - group "Total de emplacado":
      - img "Quantidade de chassi total 2.749.": "2.749"
    - group "%Share Mercedes-Benz":
      - img "%Share Mercedes-Benz 16,5%.": 16,5%
    - group:
      - textbox "Data de início. Intervalo de entrada disponível 01/01/2026 a 21/09/2026":
        - /placeholder: ""
        - text: 01/01/2026
      - textbox "Data de término. Intervalo de entrada disponível 01/01/2026 a 21/09/2026":
        - /placeholder: ""
        - text: 21/09/2026
    - group "Market Share por fabricante":
      - img:
        - listbox "Área de plotagem":
          - option "fabricante VOLKSWAGEN. Total com outros 1.026 (37,32%)."
          - option "fabricante M.BENZ. Total com outros 453 (16,48%)."
          - option "fabricante IVECO-FIAT. Total com outros 329 (11,97%)."
"""


def test_capture_dashboard_kpis():
    frame = MagicMock()
    frame.locator.return_value.aria_snapshot.return_value = ARIA
    dl = AssobensEmplacamentosDownloader(MagicMock(), MagicMock(), load_selectors())
    k = dl.capture_dashboard_kpis(frame)
    assert (k["total_mercado"], k["total_mb"], k["share_mb"]) == (2749, 453, 16.5)
    assert (k["periodo_inicio"], k["periodo_fim"], k["atualizado_em"]) == ("01/01/2026", "21/09/2026", "22/09/2026")
    assert k["filtros"]["Região MB"] == "Todos" and k["filtros"]["Distrito"] == "Todos"
    assert k["fabricantes"][0] == {"fabricante": "VOLKSWAGEN", "emplacamentos": 1026, "share": 37.32}


def test_conferencia_assobens_x_torre():
    rows = ([{"DATA EMPLACAMENTO": "2026-03-01", "MARCA": "M.BENZ", "SUBSEGMENTO": "LEVES"}] * 453
            + [{"DATA EMPLACAMENTO": "2026-05-01", "MARCA": "VW", "SUBSEGMENTO": "LEVES"}] * 1026
            + [{"DATA EMPLACAMENTO": "2026-06-01", "MARCA": "IVECO", "SUBSEGMENTO": "LEVES"}] * 329
            + [{"DATA EMPLACAMENTO": "2026-07-01", "MARCA": "VOLVO", "SUBSEGMENTO": "LEVES"}] * 941
            + [{"DATA EMPLACAMENTO": "2025-12-31", "MARCA": "VOLVO", "SUBSEGMENTO": "LEVES"}] * 50)   # fora do período
    portal = {"total_mercado": 2749, "total_mb": 453, "share_mb": 16.5, "periodo_inicio": "01/01/2026", "periodo_fim": "21/09/2026",
              "fabricantes": [{"fabricante": "VOLKSWAGEN", "emplacamentos": 1026, "share": 37.32},
                              {"fabricante": "IVECO-FIAT", "emplacamentos": 329, "share": 11.97}]}
    c = AssobensKpiService().conferencia(rows, portal)
    ind = {i["indicador"]: i for i in c["indicadores"]}
    assert ind["Total Mercado"]["torre"] == 2749 and ind["Total Mercado"]["diferenca"] == 0
    assert ind["Total Mercedes-Benz"]["diferenca"] == 0
    assert abs(ind["Market Share MB (%)"]["torre"] - 16.48) < 0.01 and abs(ind["Market Share MB (%)"]["diferenca"]) < 0.05
    assert c["fabricantes"][0]["torre"] == 1026 and c["fabricantes"][1]["torre"] == 329   # VOLKSWAGEN->VW, IVECO-FIAT->IVECO
