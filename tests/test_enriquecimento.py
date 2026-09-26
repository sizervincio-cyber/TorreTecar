"""Enriquecimento de proprietário: janela de datas, upsert só-atualização e integração no job."""
import json

from assobens import config
from assobens.enriquecimento_downloader import janela_enriquecimento
from assobens.importer import AssobensImporter
from assobens.normalizer import AssobensNormalizer
from assobens.parser import AssobensSpreadsheetParser
from assobens.price_analysis import PriceHistory
from assobens.runlog import RunLog
from assobens.sync_job import AssobensSyncJob
from conftest import SAMPLE, write_xlsx

HDR_PBI = ["CHASSI", "DATA", "PLACA", "modelo", "fabricante", "segmento", "subsegmento", "ESTADO", "municipio", "CNPJ", "Razao_Social", "area_operacional"]
ROWS_PBI = [["9BM958267PB000001", "03/01/2026", "TVE3H02", "M.BENZ/ACTROS 2653", "M.BENZ", "CAMINHAO", "EXTRAPESADO", "GO", "GOIANIA", "02714977000953", "TECAR CAMINHOES", "GOIANIA"],
            ["9BM958267PB000777", "05/02/2026", "TVD4I31", "M.BENZ/ATEGO 2426", "M.BENZ", "CAMINHAO", "SEMIPESADO", "GO", "ANAPOLIS", "02714977000953", "TECAR CAMINHOES", "ANAPOLIS"]]
HDR_ENR = ["Chassi", "Data Emplacamento", "Modelo", "Marca", "Segmento", "SubSegmento", "Placa", "Concessionário", "Município", "Estado",
           "Desc. Área Operacional", "Área Operacional", "Ano Fabricação", "Ano Modelo", "CPF ou CNPJ do Proprietário", "Tipo de Pessoa", "Nome do Proprietário", "Telefone1"]
ROWS_ENR = [["9BM958267PB000777", "05/02/2026", "M.BENZ/ATEGO 2426", "M.BENZ", "1.0-CAMINHOES", "SEMIPESADOS", "TVD4I31", "TECAR CAMINHOES", "ANAPOLIS", "GO", "ANAPOLIS", 406, 2025, 2026, "19.232.679/0002-53", "JURIDICA", "LOC-LIMP LOCADORA", "6299990000"],
            ["9BM958267PB000001", "03/01/2026", "M.BENZ/ACTROS 2653 LS", "M.BENZ", "1.0-CAMINHOES", "EXTRAPESADOS", "TVE3H02", "OUTRO DEALER", "GOIANIA", "GO", "GOIANIA", 408, 2025, 2026, "05.128.774/0001-16", "JURIDICA", "J R TRANSPORTES", ""],
            ["ZZZ000000000000099", "10/02/2026", "VW/29.530", "VW", "1.0-CAMINHOES", "EXTRAPESADOS", "AAA1111", "VW DEALER", "GOIANIA", "GO", "GOIANIA", 408, 2025, 2026, "05.128.774/0001-16", "JURIDICA", "J R TRANSPORTES", ""]]


def test_janela_enriquecimento():
    rows = [{"DATA EMPLACAMENTO": "2026-01-05", "NOMEPROPRIETARIO": ""}, {"DATA EMPLACAMENTO": "2026-08-01", "NOMEPROPRIETARIO": "X"}]
    assert janela_enriquecimento(rows, "2026-09-25") == ("2026-01-01", "2026-09-25")          # ano corrente inteiro
    assert janela_enriquecimento([{"DATA EMPLACAMENTO": "2026-09-01", "NOMEPROPRIETARIO": "X"}], "2026-01-20") == ("2025-09-22", "2026-01-20")  # mínimo 120 dias
    assert janela_enriquecimento([{"DATA EMPLACAMENTO": "2020-01-01", "NOMEPROPRIETARIO": ""}], "2026-09-25")[0] == "2025-08-21"  # teto 400 dias


def test_upsert_update_only_so_campos_de_proprietario(paths, tmp_path):
    imp = AssobensImporter(paths.MATRIZ_PATH, paths.BACKUP_DIR)
    pbi = AssobensNormalizer().normalize(AssobensSpreadsheetParser().parse(write_xlsx(tmp_path / "pbi.xlsx", headers=HDR_PBI, rows=ROWS_PBI)).rows).rows
    r1 = imp.upsert(pbi)
    assert r1.inserted == 2 and all(r["NOMEPROPRIETARIO"] == "" for r in r1.rows)
    enr = AssobensNormalizer().normalize(AssobensSpreadsheetParser().parse(write_xlsx(tmp_path / "enr.xlsx", headers=HDR_ENR, rows=ROWS_ENR)).rows).rows
    r2 = imp.upsert(enr, r1.headers, r1.rows, update_only=True, only_fields=["CPFCNPJPROPRIETARIO", "TIPOCNPJPROPRIETARIO", "NOMEPROPRIETARIO"])
    assert (r2.updated, r2.ignored, r2.inserted, r2.total) == (2, 1, 0, 2)      # chassi ZZZ… não entra
    by = {r["CHASSI"]: r for r in r2.rows}
    assert by["9BM958267PB000777"]["NOMEPROPRIETARIO"] == "LOC-LIMP LOCADORA" and by["9BM958267PB000777"]["CPFCNPJPROPRIETARIO"] == "19.232.679/0002-53"
    assert by["9BM958267PB000001"]["CONCESSIONÁRIO"] == "TECAR CAMINHOES" and by["9BM958267PB000001"]["MODELO"] == "M.BENZ/ACTROS 2653"  # fora de only_fields: intocado


def test_job_aplica_enriquecimento(paths, tmp_path):
    pbi = write_xlsx(tmp_path / "pbi.xlsx", headers=HDR_PBI, rows=ROWS_PBI)
    enr = write_xlsx(tmp_path / "enr.xlsx", headers=HDR_ENR, rows=ROWS_ENR)
    job = AssobensSyncJob(trigger="manual", executed_by="t", credentials=config.Credentials("u", "p"), sleep=lambda s: None,
                          runlog=RunLog(paths.SYNC_RUNS_PATH, paths.STATUS_PATH), importer=AssobensImporter(paths.MATRIZ_PATH, paths.BACKUP_DIR),
                          kpis_path=paths.KPIS_PATH, top10_path=paths.TOP10_PATH, precos_top10_path=paths.PRECOS_TOP10_PATH,
                          price_history=PriceHistory(paths.PRECOS_HIST_PATH), equivalencias_path=paths.EQUIVALENCIAS_PATH,
                          browser_stage=lambda run, attempt: (pbi, [], {}, enr))
    run = job.run()
    # export do Power BI insere 2; enriquecimento (fonte principal) atualiza os 2 com proprietário e insere o 3º chassi
    assert run.status == "success" and run.rows_imported == 3 and run.rows_enriched == 2
    _, rows = AssobensImporter(paths.MATRIZ_PATH, paths.BACKUP_DIR).load_matrix()
    assert len(rows) == 3 and all(r["NOMEPROPRIETARIO"] for r in rows)
    assert all(r["SEGMENTO"] == "1.0-CAMINHOES" for r in rows)
    hdr = AssobensImporter(paths.MATRIZ_PATH, paths.BACKUP_DIR).load_matrix()[0]
    assert not any("TELEFONE" in h or "EMAIL" in h for h in hdr)           # dado pessoal nunca publicado
    st = json.loads(paths.STATUS_PATH.read_text(encoding="utf-8"))
    assert st["proprietarios_enriquecidos"] == 2


def test_enriquecimento_de_outro_segmento_e_ignorado(paths, tmp_path):
    pbi = write_xlsx(tmp_path / "pbi.xlsx", headers=HDR_PBI, rows=ROWS_PBI)
    vans = [list(r) for r in ROWS_ENR]
    for r in vans:
        r[4], r[5] = "3.0-LARGE VANS", "FURGAO"
    enr = write_xlsx(tmp_path / "enr.xlsx", headers=HDR_ENR, rows=vans)
    job = AssobensSyncJob(trigger="manual", executed_by="t", credentials=config.Credentials("u", "p"), sleep=lambda s: None,
                          runlog=RunLog(paths.SYNC_RUNS_PATH, paths.STATUS_PATH), importer=AssobensImporter(paths.MATRIZ_PATH, paths.BACKUP_DIR),
                          kpis_path=paths.KPIS_PATH, top10_path=paths.TOP10_PATH, precos_top10_path=paths.PRECOS_TOP10_PATH,
                          price_history=PriceHistory(paths.PRECOS_HIST_PATH), equivalencias_path=paths.EQUIVALENCIAS_PATH,
                          browser_stage=lambda run, attempt: (pbi, [], {}, enr))
    run = job.run()
    assert run.status == "partial" and run.rows_imported == 2 and run.rows_enriched == 0
    assert any("segmento errado" in w for w in run.warnings)


def test_parser_bloqueia_colunas_pessoais_do_enriquecimento(tmp_path):
    hdr = HDR_ENR + ["NO_LOGR", "NU_CEP", "DDD_CELULAR1", "CELULAR1", "NOME_SOCIO_DIRETOR1", "NU_CPF_CNPJ1", "DT_NASC", "SG_SEXO", "SITE"]
    rows = [r + ["RUA X", "74000000", "62", "999990000", "FULANO", "12345678900", "01/01/1980", "M", "x.com"] for r in ROWS_ENR]
    ps = AssobensSpreadsheetParser().parse(write_xlsx(tmp_path / "e.xlsx", headers=hdr, rows=rows))
    assert ps.unknown_headers == []
    assert set(ps.blocked_headers) >= {"NO_LOGR", "NU_CEP", "DDD_CELULAR1", "CELULAR1", "NOME_SOCIO_DIRETOR1", "NU_CPF_CNPJ1", "DT_NASC", "SG_SEXO", "SITE", "Telefone1"}
    assert not any(k in ps.rows[0] for k in ("NO_LOGR", "CELULAR1", "NOME_SOCIO_DIRETOR1"))
