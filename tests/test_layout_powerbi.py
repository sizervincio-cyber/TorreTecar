"""Layout real do 'Analítico de Veículos' exportado do Power BI (run 35813082811): cabeçalhos em minúsculas,
underscore, área operacional como nome e CNPJ do concessionário ao lado da razão social."""
from assobens.normalizer import AssobensNormalizer, resolve_aop
from assobens.parser import AssobensSpreadsheetParser, norm_header
from conftest import write_xlsx

HDR = ["CHASSI", "DATA", "PLACA", "modelo", "fabricante", "segmento", "subsegmento", "ESTADO", "municipio", "CNPJ",
       "Razao_Social", "area_operacional", "tracao", "tipo_terreno", "ano_fabricacao", "ano_modelo", "cpf_cnpj_proprietario",
       "tipo_pessoa", "nome_proprietario"]
ROWS = [["93KKZ60A5SE210434", "30/4/2026", "TVE3H02", "VOLVO/VM 360 4X2 R", "VOLVO", "CAMINHAO", "EXTRAPESADO", "TO", "PALMAS",
         "02714977000953", "SUECIA VEICULOS S.A", "PALMAS", "4X2", "ON ROAD", 2025, 2026, "05.128.774/0001-16", "JURIDICA", "J R TRANSPORTES"],
        ["93KKZ60D0TE213081", "24/2/2026", "TVD4I31", "VOLVO/VM 360 6X4 R", "VOLVO", "CAMINHAO", "EXTRAPESADO", "GO", "GOIANIA",
         "02714977000104", "SUECIA VEICULOS S.A", "408", "6X4", "ON ROAD", 2025, 2026, "123.456.789-00", "FISICA", "JOAO"]]


def test_norm_header_ignora_underscore_e_caixa():
    assert norm_header("Razao_Social") == "RAZAO SOCIAL" and norm_header("área_operacional") == "AREA OPERACIONAL"


def test_layout_powerbi(tmp_path):
    p = write_xlsx(tmp_path / "pbi.xlsx", headers=HDR, rows=ROWS)
    ps = AssobensSpreadsheetParser().parse(p)
    assert not ps.missing_required and ps.unknown_headers == []
    assert ps.mapping["CONCESSIONÁRIO"] == HDR.index("Razao_Social")
    assert ps.mapping["CNPJ CONCESSIONARIO"] == HDR.index("CNPJ")          # não vira documento do proprietário
    assert ps.mapping["CPFCNPJPROPRIETARIO"] == HDR.index("cpf_cnpj_proprietario")
    b = AssobensNormalizer().normalize(ps.rows)
    r0, r1 = b.rows
    assert r0["DATA EMPLACAMENTO"] == "2026-04-30" and r0["MARCA"] == "VOLVO" and r0["UF"] == "TO"
    assert (r0["SEGMENTO"], r0["SUBSEGMENTO"]) == ("1.0-CAMINHOES", "EXTRAPESADOS")   # rótulos da matriz
    assert (r0["DEALER AOP"], r0["AOP"]) == ("PALMAS", "407")       # nome -> código
    assert (r1["DEALER AOP"], r1["AOP"]) == ("GOIANIA", "408")      # código -> nome
    assert r0["CPFCNPJPROPRIETARIO"] == "05.128.774/0001-16" and r0["CONCESSIONÁRIO"] == "SUECIA VEICULOS S.A"
    assert r1["CPFCNPJPROPRIETARIO"] == "***.***.***-**" and r1["NOMEPROPRIETARIO"] == "***"
    assert "CNPJ CONCESSIONARIO" not in r0                            # não publicado na matriz


def test_resolve_aop():
    assert resolve_aop(None, None, "ANAPOLIS") == ("406", "ANAPOLIS")
    assert resolve_aop(409, None, None) == ("409", "PRIMAVERA DO LESTE")
    assert resolve_aop("", "OUTRA", "") == ("", "OUTRA")
