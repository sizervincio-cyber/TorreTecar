"""Configuração do motor de licitações. Fonte: API de Consulta do PNCP (pública, sem chave)."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent

DATA_DIR = REPO_ROOT / "Analityc share" / "licitacoes"
ESTADO_PATH = DATA_DIR / "estado.json"          # checkpoint da coleta (janelas concluídas, última atualização)
COMPRAS_PATH = DATA_DIR / "compras.json"        # contratações relevantes (cabeçalho do processo)
# Itens relevantes × resultado (fornecedor, quantidade, preço), em duas bases separadas:
VEICULOS_PATH = DATA_DIR / "itens_veiculos.json"    # foco: caminhões, ônibus, vans (compra e locação)
POSVENDA_PATH = DATA_DIR / "itens_posvenda.json"    # peças, acessórios, motores e manutenção
LEGADO_ITENS_PATH = DATA_DIR / "itens.json"         # formato antigo (base única), lido só para migrar
ALVOS_PATH = DATA_DIR / "alvos.json"           # compradores públicos que emplacaram (régua e busca por CNPJ)
FORNECEDOR_MARCA_PATH =DATA_DIR / "fornecedor_marca.json"  # concessionária → marca (derivado dos emplacamentos)
MATRIZ_PATH = REPO_ROOT / "Analityc share" / "consolidado_emplacamentos_2020_2026.xlsx"

TZ = ZoneInfo("America/Sao_Paulo")
INICIO = date(2021, 1, 1)
UFS = ("GO", "MT", "TO")

# Modalidades do PNCP com compra de veículos, peças e serviços. Leilão (1), concurso (3), inexigibilidade (9)
# e credenciamento (12) ficam de fora: não são aquisição competitiva de veículo.
MODALIDADES = {
    4: "Concorrência eletrônica",
    5: "Concorrência presencial",
    6: "Pregão eletrônico",
    7: "Pregão presencial",
    8: "Dispensa",
}

# No histórico (foco em veículo) a dispensa fica de fora: veículo novo supera o limite de dispensa e o volume de
# dispensas (peças, serviços) é o que mais pesava na varredura.
MODALIDADES_HISTORICO = (6, 7, 4, 5)

CONSULTA_URL ="https://pncp.gov.br/api/consulta"   # contratações por data/UF/modalidade
PNCP_URL = "https://pncp.gov.br/api/pncp"           # itens e resultados de uma contratação
PORTAL_URL = "https://pncp.gov.br/app/editais"      # link público de evidência
PAGE_SIZE = 50
