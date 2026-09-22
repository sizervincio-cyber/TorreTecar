import pytest

from assobens.errors import EmptyFileError, SchemaError
from assobens.normalizer import AssobensNormalizer, normalize_brand, parse_date, quality_score
from assobens.parser import AssobensSpreadsheetParser
from conftest import HEADERS_ASSOBENS, SAMPLE, write_xlsx


def test_excel_valido(sample_xlsx):
    ps = AssobensSpreadsheetParser().parse(sample_xlsx)
    assert ps.sheet == "Relatório" and ps.header_row == 0
    assert len(ps.rows) == 5
    assert ps.rows[0]["CHASSI"] == "9BM958267PB000001"
    assert "CIDADE" in ps.mapping and "DEALER AOP" in ps.mapping
    assert set(ps.blocked_headers) == {"Telefone1", "E-mail"}   # dado pessoal: nunca publicado
    assert "Telefone1" not in ps.rows[0]
    assert len(ps.file_hash) == 64


def test_excel_vazio(empty_xlsx):
    with pytest.raises(EmptyFileError):
        AssobensSpreadsheetParser().parse(empty_xlsx)


def test_excel_so_cabecalho(tmp_path):
    p = write_xlsx(tmp_path / "h.xlsx", rows=[])
    with pytest.raises(EmptyFileError):
        AssobensSpreadsheetParser().parse(p)


def test_cabecalho_fora_da_primeira_linha(tmp_path):
    p = write_xlsx(tmp_path / "t.xlsx", blank_rows_before=3)
    ps = AssobensSpreadsheetParser().parse(p)
    assert ps.header_row == 3 and len(ps.rows) == 5


def test_coluna_renomeada_e_reordenada(tmp_path):
    hdr = list(HEADERS_ASSOBENS)
    hdr[1] = "DATA_COMPLETA"          # nome interno do ASSOBENS
    hdr[9] = "MUNICIPIO"
    hdr[4] = "MARCA_COMPLETA"
    hdr[16] = "C_CPFCNPJPROPRIETARIO"
    rows = [list(r) for r in SAMPLE]
    # reordena: move a coluna de data para o fim
    hdr2 = hdr[:1] + hdr[2:] + [hdr[1]]
    rows2 = [r[:1] + r[2:] + [r[1]] for r in rows]
    p = write_xlsx(tmp_path / "r.xlsx", headers=hdr2, rows=rows2)
    ps = AssobensSpreadsheetParser().parse(p)
    assert ps.rows[0]["DATA EMPLACAMENTO"] == "03/01/2026"
    assert ps.rows[0]["CIDADE"] == "Goiânia" and ps.rows[0]["MARCA"] == "MERCEDES-BENZ"


def test_coluna_obrigatoria_ausente_detecta_mudanca_de_estrutura(tmp_path):
    hdr = [h for h in HEADERS_ASSOBENS if h != "Chassi"]
    rows = [r[1:] for r in SAMPLE]
    p = write_xlsx(tmp_path / "s.xlsx", headers=hdr, rows=rows)
    with pytest.raises(SchemaError) as e:
        AssobensSpreadsheetParser().parse(p)
    assert "CHASSI" in str(e.value)


def test_extensao_invalida(tmp_path):
    p = tmp_path / "x.pdf"
    p.write_bytes(b"%PDF")
    with pytest.raises(SchemaError):
        AssobensSpreadsheetParser().parse(p)


def test_normalizacao(sample_xlsx):
    ps = AssobensSpreadsheetParser().parse(sample_xlsx)
    b = AssobensNormalizer().normalize(ps.rows)
    assert b.counts["validas"] == 5 and b.counts["rejeitadas"] == 0
    r0, r1, r2 = b.rows[0], b.rows[1], b.rows[2]
    assert r0["DATA EMPLACAMENTO"] == "2026-01-03" and r1["DATA EMPLACAMENTO"] == "2026-01-05"
    assert r0["MARCA"] == "M.BENZ"                      # MERCEDES-BENZ unificado com o rótulo da matriz
    assert r0["CIDADE"] == "GOIANIA" and r1["CIDADE"] == "ANAPOLIS"   # sem acento, maiúsculas
    assert r0["AOP"] == "408" and r0["ANOFABRICACAO"] == "2025"
    assert r0["CPFCNPJPROPRIETARIO"] == "05.128.774/0001-16"
    assert r2["TIPOCNPJPROPRIETARIO"] == "FISICA"
    assert r2["CPFCNPJPROPRIETARIO"] == "***.***.***-**" and r2["NOMEPROPRIETARIO"] == "***"   # PF mascarada
    assert "Telefone1" not in r0 and "E-mail" not in r0
    assert quality_score(b.rows)["score"] >= 75           # passa no gate da Torre


def test_normalizacao_rejeita_linhas_invalidas():
    rows = [
        {"CHASSI": "", "DATA EMPLACAMENTO": "01/01/2026", "MARCA": "VW"},
        {"CHASSI": "9BM958267PB000009", "DATA EMPLACAMENTO": "31/02/2026", "MARCA": "VW"},
        {"CHASSI": "9BM958267PB000010", "DATA EMPLACAMENTO": "01/02/2026", "MARCA": "VW", "QUANTIDADE": -1},
        {"CHASSI": "9BM958267PB000011", "DATA EMPLACAMENTO": "01/02/2026", "MARCA": "VW", "QUANTIDADE": 1},
    ]
    b = AssobensNormalizer().normalize(rows)
    assert b.counts["validas"] == 1
    assert b.counts["motivos"] == {"chassi ausente": 1, "data inválida": 1, "quantidade negativa ou inválida": 1}


@pytest.mark.parametrize("v,esperado", [
    ("03/01/2026", "2026-01-03"), ("2026-01-03", "2026-01-03"), ("3/1/26", "2026-01-03"), (46025, "2026-01-03"),
    ("20260103", "2026-01-03"), ("abc", None), ("", None), (None, None),
])
def test_parse_date(v, esperado):
    assert parse_date(v) == esperado


@pytest.mark.parametrize("v,esperado", [("Mercedes-Benz", "M.BENZ"), ("M.BENZ", "M.BENZ"), (" VOLKSWAGEN ", "VW"), ("Scania", "SCANIA"), ("hyundai", "HYUNDA")])
def test_normalize_brand(v, esperado):
    assert normalize_brand(v) == esperado
