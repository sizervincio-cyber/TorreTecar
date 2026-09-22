import json
from datetime import date

import pytest

from assobens.errors import ImportError_
from assobens.importer import AssobensImporter
from assobens.kpi import AssobensKpiService, last_12_months
from assobens.normalizer import AssobensNormalizer
from assobens.parser import AssobensSpreadsheetParser
from assobens.price_analysis import AssobensPriceAnalysisService, PriceHistory, model_key
from assobens.validator import LEVEL_ERROR, LEVEL_OK, LEVEL_SUSPECT, validate_batch


def _rows(xlsx):
    return AssobensNormalizer().normalize(AssobensSpreadsheetParser().parse(xlsx).rows).rows


# ----------------------------------------------------------------- upsert / duplicidade / rollback
def test_upsert_idempotente_e_atualizacao(paths, sample_xlsx):
    imp = AssobensImporter(paths.MATRIZ_PATH, paths.BACKUP_DIR)
    rows = _rows(sample_xlsx)
    r1 = imp.upsert(rows)
    assert (r1.inserted, r1.updated) == (5, 0)
    imp.publish(r1.headers, r1.rows, "run1")
    assert paths.MATRIZ_PATH.exists()
    # mesmo arquivo de novo: nada duplica
    r2 = imp.upsert(rows)
    assert (r2.inserted, r2.updated, r2.unchanged) == (0, 0, 5) and r2.total == 5
    # ASSOBENS alterou um valor durante o dia: atualiza o registro, não cria outro
    rows[0]["MODELO"] = "M.BENZ/ACTROS 2653 LS"
    r3 = imp.upsert(rows)
    assert (r3.inserted, r3.updated, r3.total) == (0, 1, 5)
    imp.publish(r3.headers, r3.rows, "run3")
    h, back = imp.load_matrix()
    assert len(back) == 5 and [r for r in back if r["CHASSI"] == "9BM958267PB000001"][0]["MODELO"] == "M.BENZ/ACTROS 2653 LS"
    assert list(h[:19]) == list(paths.CANONICAL_COLUMNS)
    assert len(list(paths.BACKUP_DIR.glob("*.xlsx"))) == 1   # backup da matriz anterior


def test_upsert_preserva_historico_e_dimensao_nova(paths, sample_xlsx):
    imp = AssobensImporter(paths.MATRIZ_PATH, paths.BACKUP_DIR)
    antigos = [{"CHASSI": "ANTIGO000000000001", "DATA EMPLACAMENTO": "2020-05-05", "MARCA": "VOLVO", "MODELO": "VOLVO/FH"}]
    r0 = imp.upsert(antigos)
    imp.publish(r0.headers, r0.rows)
    rows = _rows(sample_xlsx)
    for r in rows:
        r["COMBUSTIVEL"] = "DIESEL"
    res = imp.upsert(rows)
    assert res.total == 6 and "COMBUSTIVEL" in res.headers
    assert any(r["CHASSI"] == "ANTIGO000000000001" for r in res.rows)   # histórico mantido


def test_publicacao_falha_mantem_matriz_anterior(paths, sample_xlsx, monkeypatch):
    imp = AssobensImporter(paths.MATRIZ_PATH, paths.BACKUP_DIR)
    rows = _rows(sample_xlsx)
    r1 = imp.upsert(rows)
    imp.publish(r1.headers, r1.rows)
    antes = paths.MATRIZ_PATH.read_bytes()
    import os
    def boom(*a, **k):
        raise OSError("disco cheio")
    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(ImportError_):
        imp.publish(r1.headers, r1.rows + [{"CHASSI": "X"}])
    assert paths.MATRIZ_PATH.read_bytes() == antes          # rollback: nada mudou
    assert not list(paths.MATRIZ_PATH.parent.glob("*.tmp.xlsx"))


def test_recusa_publicar_vazio(paths):
    with pytest.raises(ImportError_):
        AssobensImporter(paths.MATRIZ_PATH, paths.BACKUP_DIR).publish(["CHASSI"], [])


# ----------------------------------------------------------------- validações
def test_validacoes(sample_xlsx):
    rows = _rows(sample_xlsx)
    ok = validate_batch(rows, previous_rows_downloaded=6, unknown_headers=[], rejected=0)
    assert ok.level == LEVEL_OK and ok.checks["B_share_100"] and ok.checks["G_queda_registros"]
    queda = validate_batch(rows, previous_rows_downloaded=100, unknown_headers=[], rejected=0)
    assert queda.level == LEVEL_SUSPECT and not queda.publishable
    vazio = validate_batch([], previous_rows_downloaded=None, unknown_headers=[], rejected=0)
    assert vazio.level == LEVEL_ERROR
    mb = validate_batch(rows, previous_rows_downloaded=None, unknown_headers=[], mb_reported=2)
    assert mb.checks["C_mb_calc_vs_informado"]
    mb_dif = validate_batch(rows, previous_rows_downloaded=None, unknown_headers=[], mb_reported=3)
    assert mb_dif.level == LEVEL_SUSPECT


# ----------------------------------------------------------------- KPIs / market share
def test_market_share(sample_xlsx):
    k = AssobensKpiService().compute(_rows(sample_xlsx), today=date(2026, 1, 20))
    assert k["total_mercado"] == 5 and k["total_mercedes_benz"] == 2 and k["market_share_mb"] == 40.0
    marcas = {m["chave"]: m for m in k["por_marca"]}
    assert marcas["M.BENZ"]["share"] == 40.0 and abs(sum(m["share"] for m in k["por_marca"]) - 100) < 0.01
    assert k["por_ano"][0] == {"periodo": "2026", "total_mercado": 5, "mercedes_benz": 2, "market_share_mb": 40.0}
    assert k["ultimos_12_meses"]["total_mercado"] == 5
    assert k["ranking_modelos_12m"]["EXTRAPESADOS"][0]["fabricante"] in ("M.BENZ", "VW", "VOLVO", "SCANIA")
    assert last_12_months(date(2026, 1, 20))[0] == "2025-02" and last_12_months(date(2026, 1, 20))[-1] == "2026-01"


# ----------------------------------------------------------------- Top 10 + preços
def test_top10_e_historico_de_precos(paths, sample_xlsx):
    rows = _rows(sample_xlsx)
    hist = PriceHistory(paths.PRECOS_HIST_PATH)
    svc = AssobensPriceAnalysisService(history=hist, equivalencias_path=paths.EQUIVALENCIAS_PATH)
    top = svc.top10_por_segmento(rows, ref=date(2026, 1, 20))
    ext = top["segmentos"]["EXTRAPESADOS"]
    assert len(ext) == 4 and ext[0]["posicao"] == 1 and all(x["market_share"] == 25.0 for x in ext)
    assert top["segmentos"]["SEMIPESADOS"][0]["modelo"] == "M.BENZ/ATEGO 2426"
    # histórico: captura, idempotência e atualização do mesmo dia
    cap = [{"source": "assobens_precos_comparativo", "manufacturer": "VW", "model": "VW/29.530", "segment": "EXTRAPESADOS",
            "price": 760000.0, "reference_date": "2026-01-20", "captured_at": "2026-01-20T08:00:00"},
           {"source": "assobens_precos_comparativo", "manufacturer": "M.BENZ", "model": "M.BENZ/ACTROS 2653", "segment": "EXTRAPESADOS",
            "price": 790000.0, "reference_date": "2026-01-20", "captured_at": "2026-01-20T08:00:00"}]
    assert hist.upsert(cap) == 2
    assert hist.upsert(cap) == 0                              # mesma captura: não duplica
    cap[0]["price"] = 765000.0
    assert hist.upsert(cap) == 1 and len(hist.read()) == 2    # preço mudou no dia: atualiza
    cap2 = [dict(cap[0], reference_date="2026-01-21", price=770000.0)]
    hist.upsert(cap2)
    assert len(hist.read()) == 3                              # novo dia: nova linha (histórico)
    # análise sem equivalência cadastrada
    an = svc.analyze(top, captured_at="2026-01-21T09:00:00")
    vw = [x for x in an["segmentos"]["EXTRAPESADOS"] if x["fabricante"] == "VW"][0]
    assert vw["preco_identificado"] == 770000.0 and vw["equivalente_mb"] is None and vw["observacao"] == "equivalência não cadastrada"
    mb = [x for x in an["segmentos"]["EXTRAPESADOS"] if x["fabricante"] == "M.BENZ"][0]
    assert mb["gap_preco_rs"] == 0.0
    # com equivalência cadastrada: gap R$ e %
    paths.EQUIVALENCIAS_PATH.parent.mkdir(parents=True, exist_ok=True)
    paths.EQUIVALENCIAS_PATH.write_text(json.dumps({"equivalencias": [{"fabricante": "VW", "modelo": "VW/29.530", "equivalente_mb": "M.BENZ/ACTROS 2653"}]}), encoding="utf-8")
    an = svc.analyze(top)
    vw = [x for x in an["segmentos"]["EXTRAPESADOS"] if x["fabricante"] == "VW"][0]
    assert vw["preco_mb_equivalente"] == 790000.0 and vw["gap_preco_rs"] == 20000.0 and vw["gap_preco_pct"] == round((790000 / 770000 - 1) * 100, 2)
    volvo = [x for x in an["segmentos"]["EXTRAPESADOS"] if x["fabricante"] == "VOLVO"][0]
    assert volvo["preco_identificado"] is None and "não identificado" in volvo["observacao"]


def test_model_key():
    assert model_key("VW", "VW/29.530 6X4") == model_key("VOLKSWAGEN", "29.530 6x4") == "295306X4"
