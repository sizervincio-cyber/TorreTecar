"""Enriquecimento CNPJá: recorte só com dados da empresa, fila priorizada, cache por max_age e tratamento de erros."""
import io
import json
import urllib.error
from datetime import date

import pytest

from assobens.cnpja import CnpjaClient, CnpjaEnricher, CreditosEsgotados, candidatos, perfil_cnae, resumo_empresa

OFFICE = {
    "taxId": "05128774000116", "updated": "2026-10-01T10:00:00Z", "alias": "JR LOG", "founded": "2001-03-02", "head": True,
    "statusDate": "2005-11-03", "status": {"id": 2, "text": "Ativa"},
    "company": {"id": "05128774", "name": "J R TRANSPORTES E LOGISTICA LTDA", "equity": 2500000,
                "nature": {"id": 2062, "text": "Sociedade Empresária Limitada"}, "size": {"id": 5, "acronym": "DEMAIS"},
                "simples": {"optant": False}, "simei": {"optant": False},
                "members": [{"person": {"name": "FULANO DE TAL", "taxId": "***123456**"}}]},
    "address": {"municipality": 5208707, "street": "Rua X", "number": "10", "city": "Goiânia", "state": "GO", "zip": "74000000"},
    "phones": [{"area": "62", "number": "99999999"}], "emails": [{"address": "fulano@jr.com.br"}],
    "mainActivity": {"id": 4930202, "text": "Transporte rodoviário de carga"}, "sideActivities": [{"id": 5211701}],
}

ROWS = [
    {"CPFCNPJPROPRIETARIO": "05.128.774/0001-16", "TIPOCNPJPROPRIETARIO": "JURIDICA", "DATA EMPLACAMENTO": "2026-03-01"},
    {"CPFCNPJPROPRIETARIO": "19.232.679/0002-53", "TIPOCNPJPROPRIETARIO": "JURIDICA", "DATA EMPLACAMENTO": "2024-01-10"},
    {"CPFCNPJPROPRIETARIO": "19.232.679/0002-53", "TIPOCNPJPROPRIETARIO": "JURIDICA", "DATA EMPLACAMENTO": "2024-05-10"},
    {"CPFCNPJPROPRIETARIO": "***.***.***-**", "TIPOCNPJPROPRIETARIO": "FISICA", "DATA EMPLACAMENTO": "2026-04-01"},
    {"CPFCNPJPROPRIETARIO": "", "TIPOCNPJPROPRIETARIO": "JURIDICA", "DATA EMPLACAMENTO": "2026-04-01"},
]


class Resp(io.BytesIO):
    def __init__(self, status, body):
        super().__init__(json.dumps(body).encode())
        self.status = status


def opener_from(responses, calls):
    def _open(req, timeout=None):
        calls.append(req)
        st, body = responses.pop(0)
        if st >= 400:
            raise urllib.error.HTTPError(req.full_url, st, "x", {}, io.BytesIO(json.dumps(body).encode()))
        return Resp(st, body)
    return _open


def test_resumo_nao_leva_contatos_socios_nem_logradouro():
    r = resumo_empresa(OFFICE)
    assert r["razao_social"] == "J R TRANSPORTES E LOGISTICA LTDA" and r["perfil"] == "Transporte rodoviário de carga"
    assert r["cnae_principal"] == 4930202 and r["cnaes_secundarios"] == [5211701] and r["uf"] == "GO"
    texto = json.dumps(r, ensure_ascii=False)
    for proibido in ("FULANO", "99999999", "fulano@", "Rua X", "members", "phones", "emails"):
        assert proibido not in texto


def test_perfil_cnae():
    assert perfil_cnae(4930202) == "Transporte rodoviário de carga"
    assert perfil_cnae("0111-3/01") == "Agropecuária"
    assert perfil_cnae(7719599) == "Locação de veículos"
    assert perfil_cnae(2511000) == "Indústria"
    assert perfil_cnae(None) == "Não informado"


def test_candidatos_so_pj_validos_mais_recentes_primeiro():
    assert candidatos(ROWS) == ["05128774000116", "19232679000253"]


def test_client_comercial_envia_chave_e_estrategia():
    calls = []
    c = CnpjaClient("k" * 73, opener=opener_from([(200, OFFICE)], calls), sleep=lambda s: None)
    assert c.office("05128774000116")["taxId"] == "05128774000116"
    req = calls[0]
    assert req.full_url.startswith("https://api.cnpja.com/office/05128774000116?") and "strategy=CACHE" in req.full_url
    assert req.get_header("Authorization") == "k" * 73


def test_client_publico_sem_chave_e_404_vira_none():
    calls = []
    c = CnpjaClient(None, opener=opener_from([(404, {"code": 404})], calls), sleep=lambda s: None)
    assert c.publica and c.per_minute == 5
    assert c.office("05128774000116") is None
    assert calls[0].full_url == "https://open.cnpja.com/office/05128774000116" and calls[0].get_header("Authorization") is None


def test_client_429_limite_espera_e_repete_creditos_interrompe():
    waits = []
    c = CnpjaClient("k", opener=opener_from([(429, {"message": "rate limit exceeded"}), (200, OFFICE)], []), sleep=waits.append)
    assert c.office("05128774000116") and 60 in waits
    c = CnpjaClient("k", opener=opener_from([(429, {"message": "not enough credits", "required": 1, "remaining": 0})], []), sleep=lambda s: None)
    with pytest.raises(CreditosEsgotados):
        c.office("05128774000116")


def test_enricher_grava_cache_e_respeita_max_age(tmp_path):
    path = tmp_path / "empresas.json"
    calls = []
    c = CnpjaClient("k", opener=opener_from([(200, OFFICE), (404, {})], calls), sleep=lambda s: None)
    res = CnpjaEnricher(c, path=path).run(ROWS, hoje=date(2026, 10, 29))
    assert (res.consultados, res.atualizados, res.nao_encontrados, res.pendentes) == (2, 1, 1, 0)
    data = json.loads(path.read_text(encoding="utf-8"))["empresas"]
    assert data["05128774000116"]["consultado_em"] == "2026-10-29" and data["19232679000253"]["sem_dados"] is True

    # dentro de max_age nada é reconsultado; vencido, volta para a fila
    c2 = CnpjaClient("k", opener=opener_from([], calls), sleep=lambda s: None)
    assert CnpjaEnricher(c2, path=path).run(ROWS, hoje=date(2026, 11, 10)).consultados == 0
    c3 = CnpjaClient("k", opener=opener_from([(200, OFFICE), (200, OFFICE)], calls), sleep=lambda s: None)
    assert CnpjaEnricher(c3, path=path).run(ROWS, hoje=date(2026, 12, 20), limite=1).consultados == 1


def test_enricher_creditos_esgotados_salva_o_que_tem(tmp_path):
    path = tmp_path / "empresas.json"
    c = CnpjaClient("k", opener=opener_from([(200, OFFICE), (429, {"message": "not enough credits"})], []), sleep=lambda s: None)
    res = CnpjaEnricher(c, path=path).run(ROWS, hoje=date(2026, 10, 29))
    assert res.erro and res.atualizados == 1 and res.pendentes == 1
    assert "05128774000116" in json.loads(path.read_text(encoding="utf-8"))["empresas"]
