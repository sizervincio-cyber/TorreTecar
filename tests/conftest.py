import sys
from pathlib import Path

import openpyxl
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

HEADERS_ASSOBENS = ["Chassi", "Data Emplacamento", "Modelo", "Tração", "Marca", "Segmento", "SubSegmento", "Placa",
                    "Concessionário", "Município", "Estado", "Desc. Área Operacional", "Área Operacional", "Ano Fabricação",
                    "Ano Modelo", "Tipo Terreno", "CPF ou CNPJ do Proprietário", "Tipo de Pessoa", "Nome do Proprietário",
                    "Telefone1", "E-mail"]

SAMPLE = [
    ["9BM958267PB000001", "03/01/2026", "M.BENZ/ACTROS 2653", "6X4", "MERCEDES-BENZ", "1.0-CAMINHOES", "EXTRAPESADOS", "RBQ4138",
     "TECAR CAMINHOES", "Goiânia", "GO", "GOIANIA", 408, 2025, 2026, "ON ROAD", "05.128.774/0001-16", "JURIDICA", "J R TRANSPORTES", "6299990000", "x@y.com"],
    ["9BM958267PB000002", "2026-01-05", "M.BENZ/ATEGO 2426", "6X2", "M.BENZ", "1.0-CAMINHOES", "SEMIPESADOS", "RBN5728",
     "TECAR CAMINHOES", "Anápolis", "GO", "ANAPOLIS", 406, 2025, 2026, "ON ROAD", "19.232.679/0002-53", "JURIDICA", "LOC-LIMP", "", ""],
    ["9536J8241LR000003", "10/01/2026", "VW/29.530", "6X4", "VW", "1.0-CAMINHOES", "EXTRAPESADOS", "ABC1234",
     "VW CAMINHOES", "Rio Verde", "GO", "GOIANIA", 408, 2025, 2026, "ON ROAD", "123.456.789-00", "FISICA", "JOAO DA SILVA", "6288887777", "j@s.com"],
    ["YV2RT40A8NB000004", "12/01/2026", "VOLVO/FH 540", "6X4", "VOLVO", "1.0-CAMINHOES", "EXTRAPESADOS", "DEF5678",
     "DIPESUL", "Palmas", "TO", "PALMAS", 407, 2025, 2026, "ON ROAD", "05.128.774/0001-16", "JURIDICA", "J R TRANSPORTES", "", ""],
    ["9BSR6X400N3000005", "15/01/2026", "SCANIA/R 450", "6X2", "SCANIA", "1.0-CAMINHOES", "EXTRAPESADOS", "GHI9012",
     "CODEMA", "Goiânia", "GO", "GOIANIA", 408, 2025, 2026, "ON ROAD", "19.232.679/0002-53", "JURIDICA", "LOC-LIMP", "", ""],
]


def write_xlsx(path: Path, headers=None, rows=None, blank_rows_before=0):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Relatório"
    for _ in range(blank_rows_before):
        ws.append(["", ""])
    ws.append(headers if headers is not None else HEADERS_ASSOBENS)
    for r in (rows if rows is not None else SAMPLE):
        ws.append(r)
    wb.save(path)
    return path


@pytest.fixture
def sample_xlsx(tmp_path):
    return write_xlsx(tmp_path / "0800_emplacamentos.xlsx")


@pytest.fixture
def empty_xlsx(tmp_path):
    return write_xlsx(tmp_path / "vazio.xlsx", headers=[], rows=[])


@pytest.fixture
def paths(tmp_path, monkeypatch):
    """Redireciona todos os caminhos versionados/locais para um diretório temporário."""
    from assobens import config
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setattr(config, "MATRIZ_PATH", data / "matriz.xlsx")
    monkeypatch.setattr(config, "ASSOBENS_DATA_DIR", data / "assobens")
    monkeypatch.setattr(config, "STATUS_PATH", data / "assobens" / "status.json")
    monkeypatch.setattr(config, "SYNC_RUNS_PATH", data / "assobens" / "sync_runs.json")
    monkeypatch.setattr(config, "KPIS_PATH", data / "assobens" / "kpis.json")
    monkeypatch.setattr(config, "TOP10_PATH", data / "assobens" / "top10.json")
    monkeypatch.setattr(config, "PRECOS_HIST_PATH", data / "assobens" / "precos_historico.csv")
    monkeypatch.setattr(config, "PRECOS_TOP10_PATH", data / "assobens" / "precos_top10.json")
    monkeypatch.setattr(config, "EQUIVALENCIAS_PATH", data / "assobens" / "equivalencias_mb.json")
    monkeypatch.setattr(config, "STORAGE_DIR", tmp_path / "storage" / "app")
    monkeypatch.setattr(config, "LOGS_DIR", tmp_path / "storage" / "logs")
    monkeypatch.setattr(config, "ERRORS_DIR", tmp_path / "storage" / "logs" / "errors")
    monkeypatch.setattr(config, "BACKUP_DIR", tmp_path / "storage" / "backup")
    return config
