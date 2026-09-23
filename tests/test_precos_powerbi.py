"""Comparativo de Preços: parse da árvore de acessibilidade real (run 35817270681) e casamento com o Top 10."""
from assobens.price_analysis import AssobensPriceAnalysisService, PriceHistory, model_tokens
from assobens.price_downloader import AssobensPriceDownloader, parse_aria_prices

ARIA = """    - group:
      - heading "MODELO MB" [level=3]
      - combobox "MODELO MB": MB 1117 
    - group:
      - img:
        - img:
          - listbox "Modelo":
            - option "VW 11.180"
            - option "MB 1117"
            - option "MB 1017"
            - option "IVECO 11-190"
            - option "FOTON 1217"
          - group "Área de plotagem":
            - listbox "Valor Indecx":
              - option "375741.4036"
              - option "365474.8638"
              - option "352871.4105"
              - option "342474.5761"
              - option "327439.5353"
    - group:
      - group "Atualizado em:":
        - img "Data mais recente 22/09/2026.": 22/09/2026
      - document:
        - grid:
          - row "MODELO FOTON 1217 FOTON 1217 FOTON 1217 MB 1117 MB 1117 MB 1117":
            - columnheader "MODELO"
            - columnheader "FOTON 1217"
            - columnheader "FOTON 1217"
            - columnheader "FOTON 1217"
            - columnheader "MB 1117"
            - columnheader "MB 1117"
            - columnheader "MB 1117"
          - row "UF Qtde. Valor Indecx Var.% Qtde. Valor Indecx Var.%":
            - columnheader "UF"
            - columnheader "Qtde."
            - columnheader "Valor Indecx"
            - columnheader "Var.%"
            - columnheader "Qtde."
            - columnheader "Valor Indecx"
            - columnheader "Var.%"
          - row "MT 11 R$ 332.545 Círculo vermelho -7,42% 26 R$ 359.188 -":
            - rowheader "MT"
            - gridcell "11"
            - gridcell "R$ 332.545"
            - gridcell "Círculo vermelho -7,42%":
              - img "Círculo vermelho"
              - text: "-7,42%"
            - gridcell "26"
            - gridcell "R$ 359.188"
            - gridcell "-"
          - row "Nacional 156 R$ 327.440 - 1084 R$ 365.475 -":
            - rowheader "Nacional"
            - gridcell "156"
            - gridcell "R$ 327.440"
            - gridcell "-"
            - gridcell "1084"
            - gridcell "R$ 365.475"
            - gridcell "-"
"""


def test_parse_aria_prices():
    caps = parse_aria_prices(ARIA, "MB 1117", "2026-09-22", "2026-09-23T01:15:00")
    nac = {c["model"]: c for c in caps if c["segment"].startswith("Nacional")}
    assert set(nac) == {"VW 11.180", "MB 1117", "MB 1017", "IVECO 11-190", "FOTON 1217"}
    assert nac["VW 11.180"]["price"] == 375741.4 and nac["VW 11.180"]["manufacturer"] == "VW"
    assert nac["MB 1117"]["manufacturer"] == "M.BENZ" and nac["MB 1117"]["segment"] == "Nacional|grupo MB 1117"
    mt = {c["model"]: c for c in caps if c["segment"].startswith("MT")}
    assert mt["FOTON 1217"]["price"] == 332545.0 and mt["MB 1117"]["price"] == 359188.0
    assert AssobensPriceDownloader.current_mb_model(ARIA) == "MB 1117"
    assert AssobensPriceDownloader.reference_date(AssobensPriceDownloader.__new__(AssobensPriceDownloader), ARIA) == "2026-09-22"


def test_model_tokens():
    assert model_tokens("VW/DELIVERY 11.180") == {"11180"} and model_tokens("VW 11.180") == {"11180"}
    assert model_tokens("M.BENZ/ATEGO 1419 CL") == {"1419"} and model_tokens("VOLVO/FH 540 6X4T") == {"540"}


def test_analise_top10_com_grupo_assobens(paths):
    hist = PriceHistory(paths.PRECOS_HIST_PATH)
    hist.upsert(parse_aria_prices(ARIA, "MB 1117", "2026-09-22", "2026-09-23T01:15:00"))
    svc = AssobensPriceAnalysisService(history=hist, equivalencias_path=paths.EQUIVALENCIAS_PATH)
    top = {"janela": ["2025-10", "2026-09"], "segmentos": {"MEDIOS": [
        {"posicao": 1, "fabricante": "VW", "modelo": "VW/DELIVERY 11.180", "emplacamentos": 147, "market_share": 46.5},
        {"posicao": 2, "fabricante": "M.BENZ", "modelo": "M.BENZ/ATEGO 1117", "emplacamentos": 30, "market_share": 9.5},
        {"posicao": 3, "fabricante": "IVECO", "modelo": "IVECO/TECTOR 11-190", "emplacamentos": 52, "market_share": 16.4},
        {"posicao": 4, "fabricante": "VW", "modelo": "VW/14.210 CRM 4X2", "emplacamentos": 39, "market_share": 12.3},
    ]}}
    an = svc.analyze(top, captured_at="2026-09-23T01:20:00")
    l = {x["modelo"]: x for x in an["segmentos"]["MEDIOS"]}
    vw = l["VW/DELIVERY 11.180"]
    assert vw["preco_identificado"] == 375741.4 and vw["modelo_no_comparativo"] == "VW 11.180"
    assert vw["equivalente_mb"] == "MB 1117" and vw["fonte_equivalencia"] == "grupo do Comparativo ASSOBENS"
    assert vw["preco_mb_equivalente"] == 365474.86 and vw["gap_preco_rs"] == round(365474.86 - 375741.4, 2)
    assert vw["gap_preco_pct"] == round((365474.86 / 375741.4 - 1) * 100, 2)
    mb = l["M.BENZ/ATEGO 1117"]
    assert mb["preco_identificado"] == 365474.86 and mb["gap_preco_rs"] == 0.0
    iv = l["IVECO/TECTOR 11-190"]
    assert iv["preco_identificado"] == 342474.58 and iv["equivalente_mb"] == "MB 1117"
    sem = l["VW/14.210 CRM 4X2"]
    assert sem["preco_identificado"] is None and sem["equivalente_mb"] is None and "não cadastrada" in sem["observacao"]
