"""Módulo Inteligência de carteira: menu Carteira da Torre, servidor e privacidade da página gerada.

A página (inteligencia-carteira.html) é gerada fora do repositório a partir do export do CRM; os testes dela só rodam
quando o arquivo existe no checkout.
"""
import re
from pathlib import Path

import pytest

from server.app import site

ROOT = Path(__file__).resolve().parents[1]
TORRE = (ROOT / "Analitycmbb.html").read_text(encoding="utf-8")
PAGINA = ROOT / "inteligencia-carteira.html"


def test_menu_carteira_tem_os_dois_motores():
    grupo = re.search(r"\{name:'Carteira',items:\[(.*?)\]\}", TORRE).group(1)
    assert "id:'carteira'" in grupo
    assert "id:'crm_atendimento',label:'Atendimento da carteira'" in grupo
    assert "id:'crm_emplacamentos',label:'Emplacamentos por região'" in grupo
    assert "crm_atendimento:['Atendimento da carteira'" in TORRE and "crm_emplacamentos:['Emplacamentos por região'" in TORRE


def test_modulo_abre_a_pagina_na_analise_escolhida():
    assert '<div id="ciModule" hidden>' in TORRE and '<iframe id="ciFrame"' in TORRE
    assert "#ciModule[hidden]{display:none}" in TORRE
    assert "ciVoltaPara:'home'" in TORRE
    assert "'inteligencia-carteira.html#'+qual" in TORRE
    assert "this.page==='crm_emplacamentos'?'emplacamentos':'cobertura'" in TORRE


def test_servidor_entrega_como_dado_comercial():
    # dado comercial: qualquer perfil logado menos 'simulacao' (bloqueio feito em main.py para tipo 'dados')
    assert site.classifica("inteligencia-carteira.html") == "dados"
    assert site.classifica("../inteligencia-carteira.html") is None


@pytest.mark.skipif(not PAGINA.exists(), reason="página gerada fora do repositório")
def test_pagina_tem_as_duas_analises_e_nenhum_dado_pessoal():
    html = PAGINA.read_text(encoding="utf-8")
    assert 'SRC["cobertura"]=' in html and 'SRC["emplacamentos"]=' in html
    assert not re.search(r"[A-Za-z0-9._-]+@[A-Za-z0-9-]+\.(com|br|net|org)", html), "e-mail na página"
    assert not re.search(r"(?<![\d.])\d{3}\.\d{3}\.\d{3}-\d{2}(?![\d])", html), "CPF formatado na página"
    assert "BELCAR" not in html.upper(), "nome de outra concessionária na página"
