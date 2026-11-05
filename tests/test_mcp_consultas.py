"""MCP da Torre: leitura das bases (matriz, CRM embutido, licitações, preços) e consultas agregadas."""
import json

import openpyxl
import pytest

from mcp_torre import consultas as q
from mcp_torre.dados import Bases

CAB = ["CHASSI", "DATA EMPLACAMENTO", "MODELO", "TRAÇÃO", "MARCA", "SEGMENTO", "SUBSEGMENTO", "PLACA", "CONCESSIONÁRIO",
       "CIDADE", "UF", "DEALER AOP", "AOP", "ANOFABRICACAO", "ANOMODELO", "TIPO TERRENO", "CPFCNPJPROPRIETARIO",
       "TIPOCNPJPROPRIETARIO", "NOMEPROPRIETARIO", "COMBUSTIVEL"]


def linha(chassi, data, marca, uf, sub, cnpj, nome, conc="OUTRA", placa="AAA0A00", modelo=None):
    tipo = "JURIDICA" if cnpj else "FISICA"
    return [chassi, data, modelo or f"{marca}/X", "6X4", marca, "1.0-CAMINHOES", sub, placa, conc, "GOIANIA", uf, "GOIANIA",
            "408", 2025, 2026, "ON ROAD", cnpj or "***.***.***-**", tipo, nome if cnpj else "***", None]


@pytest.fixture
def bases(tmp_path):
    share = tmp_path / "Analityc share"
    (share / "assobens").mkdir(parents=True)
    (share / "licitacoes").mkdir()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(CAB)
    for r in [
        linha("C1", "2025-03-01", "M.BENZ", "GO", "EXTRAPESADOS", "05.128.774/0001-16", "J R TRANSPORTES", "TECAR CAMINHOES", "TFM1J30"),
        linha("C2", "2025-04-01", "VOLVO", "GO", "EXTRAPESADOS", "05.128.774/0002-05", "J R TRANSPORTES"),
        linha("C3", "2026-02-01", "M.BENZ", "GO", "EXTRAPESADOS", "05.128.774/0001-16", "J R TRANSPORTES", "TECAR CAMINHOES"),
        linha("C4", "2026-03-01", "SCANIA", "TO", "SEMIPESADOS", "19.232.679/0002-53", "LOC-LIMP"),
        linha("C5", "05/04/2026", "VOLVO", "GO", "EXTRAPESADOS", "", ""),
    ]:
        ws.append(r)
    wb.save(share / "consolidado_emplacamentos_2020_2026.xlsx")
    crm_meta = {"exportDate": "2026-08-25", "dealers": ["Aparecida", "Anápolis"], "temps": ["Frio", "Morno"],
                "classif": ["Top Cliente", "Cliente Ativo"], "segs": ["TRANSPORTE"], "muns": ["INHUMAS"]}
    crm_resp = [{"n": "Luciano L.", "role": "VEND", "casa": "Aparecida"}]
    crm_rows = [[1, 0, "J", "J R TRANSPORTES E LOGISTICA LTDA", "05128774000116", 0, 0, 1, 0, 0, "GO", "2022-05", 7, 0]]
    (tmp_path / "Analitycmbb.html").write_text(
        f"<script>\nconst CRM_META={json.dumps(crm_meta)};\nconst CRM_RESP={json.dumps(crm_resp)};\n"
        f"const CRM_ROWS={json.dumps(crm_rows)};\n</script>", encoding="utf-8")
    (share / "licitacoes" / "compras.json").write_text(json.dumps({"compras": {
        "A-2026-1": {"id": "A-2026-1", "orgao": "MUNICIPIO X", "uf": "GO", "municipio": "Goiânia", "ano": 2026,
                     "objeto": "AQUISIÇÃO DE CAMINHÃO", "valor_estimado": "1000.5", "publicada": "2026-10-01",
                     "encerramento": "2099-01-01", "situacao": "Divulgada"},
        "B-2025-2": {"id": "B-2025-2", "orgao": "ESTADO Y", "uf": "MT", "ano": 2025, "objeto": "PEÇAS",
                     "valor_estimado": 500, "publicada": "2025-05-01"}}}), encoding="utf-8")
    (share / "licitacoes" / "itens_veiculos.json").write_text(json.dumps({"itens": [
        {"compra": "A-2026-1", "n": 1, "desc": "CAMINHAO 6X4", "seg": "CAMINHAO_EXTRAPESADO", "tipo": "AQUISICAO",
         "qtd": 2, "vu_est": 900000, "vt_est": 1800000, "situacao": "Homologado",
         "r": [{"nome": "TECAR DIESEL CAMINHOES E ONIBUS", "qtd": "2", "vu": 880000}]}]}), encoding="utf-8")
    (share / "licitacoes" / "fornecedor_marca.json").write_text(json.dumps({"mapa": {"TECAR DIESEL CAMINHOES E ONIBUS": "M.BENZ"}}), encoding="utf-8")
    (share / "assobens" / "precos_historico.csv").write_text(
        "source,manufacturer,model,segment,price,reference_date,captured_at\n"
        "x,M.BENZ,MB 2429,Nacional|grupo MB 2429,504000,2026-09-22,2026-09-23\n"
        "x,VOLVO,VOLVO VM 290,Nacional|grupo MB 2429,539000,2026-09-22,2026-09-23\n", encoding="utf-8")
    return Bases(tmp_path)


def test_matriz_le_tudo_com_cnpj_placa_chassi(bases):
    rows = bases.emplacamentos()
    assert len(rows) == 5 and rows[-1]["data"] == "2026-04-05"  # dd/mm/aaaa vira ISO e a base fica ordenada
    r = rows[0]
    assert (r["chassi"], r["placa"], r["cnpj"], r["raiz"], r["tracao"]) == ("C1", "TFM1J30", "05128774000116", "05128774", "6X4")


def test_resumo_calcula_share_sobre_a_base_inteira(bases):
    r = q.resumo_emplacamentos(bases, "uf,marca", uf="GO")
    assert r["total"] == 4 and r["mercedes_benz"] == 2 and r["share_mb_pct"] == 50.0
    assert r["grupos"][0] == {"uf": "GO", "marca": "M.BENZ", "emplacamentos": 2, "pct_do_total": 50.0,
                              "mercedes_benz": 2, "share_mb_pct": 100.0}  # empate em volume: ordem alfabética
    assert q.resumo_emplacamentos(bases, "ano", data_ini="2026")["total"] == 3
    with pytest.raises(q.ErroConsulta):
        q.resumo_emplacamentos(bases, "marca,uf,ano,mes")


def test_comparar_periodos(bases):
    c = q.comparar_periodos(bases, "2025", "2025", "2026", "2026", "marca", uf="GO")
    mb = next(x for x in c["linhas"] if x["marca"] == "M.BENZ")
    assert (c["periodo_a"]["total"], c["periodo_b"]["total"], mb["periodo_a"], mb["periodo_b"]) == (2, 2, 1, 1)


def test_buscar_exige_filtro_e_devolve_identificadores(bases):
    with pytest.raises(q.ErroConsulta):
        q.buscar_emplacamentos(bases)
    r = q.buscar_emplacamentos(bases, placa="TFM-1J30")
    assert r["encontrados"] == 1 and r["registros"][0]["chassi"] == "C1"
    assert q.buscar_emplacamentos(bases, cnpj="05128774")["encontrados"] == 3  # raiz pega matriz e filial


def test_cliente_360_por_raiz_e_por_nome(bases):
    a = q.cliente_360(bases, "05.128.774/0001-16")["contas"][0]
    assert a["emplacamentos_total"] == 3 and a["mercedes_benz_total"] == 2
    assert a["crm"][0]["responsavel"] == "Luciano L." and a["crm"][0]["casa"] == "Aparecida"
    assert q.cliente_360(bases, "j r transp")["contas"][0]["raiz_cnpj"] == "05128774"
    assert q.cliente_360(bases, "inexistente")["encontrado"] is False


def test_carteira_por_responsavel(bases):
    l = q.carteira_por_responsavel(bases)["linhas"][0]
    assert (l["responsavel"], l["clientes_pj"], l["raizes_cnpj"]) == ("Luciano L.", 1, 1)
    assert l["mercado_5a"] == 3 and l["vendas_tecar_12m"] == 1  # janela de 12m termina na última data da base


def test_licitacoes_e_itens(bases):
    l = q.buscar_licitacoes(bases, texto="caminhao", uf="GO", somente_abertas=True)
    assert l["encontradas"] == 1 and l["valor_estimado_total"] == 1000.5  # valor em texto não quebra a soma
    i = q.itens_licitacoes(bases, segmento="EXTRAPESADO")
    assert i["quantidade_vencida_por_marca"] == {"M.BENZ": 2.0}


def test_precos_e_status(bases):
    assert q.precos(bases, marca="M.BENZ")["encontrados"] == 1
    s = q.status_dados(bases)
    assert s["emplacamentos"]["linhas"] == 5 and s["crm"]["contas"] == 1 and s["cadastro_cnpja"] is False


def test_caminho_fora_da_raiz_e_recusado(bases):
    with pytest.raises(ValueError):
        bases.caminho("../fora.json")
