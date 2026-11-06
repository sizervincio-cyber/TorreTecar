"""Disjuntor do cliente PNCP: fora do ar, não repete as 5 tentativas em cada URL."""
import pytest


def test_pncp_fora_do_ar_nao_repete_as_5_tentativas_para_cada_url():
    """Quando o PNCP cai, a 1ª URL gasta as 5 tentativas; as seguintes falham na hora (disjuntor)."""
    import urllib.error
    from licitacoes.pncp import PncpClient, PncpError
    esperas, chamadas = [], []

    def opener(req, timeout=None):
        chamadas.append(req.full_url)
        raise urllib.error.URLError("conexão recusada")
    c = PncpClient(opener=opener, sleep=esperas.append, pause=0)
    with pytest.raises(PncpError, match="5 tentativas"):
        c._get("https://pncp.gov.br/a")
    with pytest.raises(PncpError, match="fora do ar"):
        c._get("https://pncp.gov.br/b")
    assert len(chamadas) == 5 and c.fora_do_ar
