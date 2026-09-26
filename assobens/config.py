"""Configuração central da rotina ASSOBENS.

Credenciais vêm SOMENTE do ambiente (ASSOBENS_USER / ASSOBENS_PASSWORD),
carregadas de um .env local (gitignored) ou dos secrets do GitHub Actions.
Nada aqui guarda senha.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent

# Fonte viva que a Torre (Analitycmbb.html) lê por fetch + hash.
DATA_DIR = REPO_ROOT / "Analityc share"
MATRIZ_PATH = DATA_DIR / "consolidado_emplacamentos_2020_2026.xlsx"
ASSOBENS_DATA_DIR = DATA_DIR / "assobens"

# Arquivos versionados produzidos pela rotina (o "banco" deste projeto).
STATUS_PATH = ASSOBENS_DATA_DIR / "status.json"
SYNC_RUNS_PATH = ASSOBENS_DATA_DIR / "sync_runs.json"
KPIS_PATH = ASSOBENS_DATA_DIR / "kpis.json"
TOP10_PATH = ASSOBENS_DATA_DIR / "top10_segmentos.json"
PRECOS_HIST_PATH = ASSOBENS_DATA_DIR / "precos_historico.csv"
PRECOS_TOP10_PATH = ASSOBENS_DATA_DIR / "precos_top10.json"
EQUIVALENCIAS_PATH = ASSOBENS_DATA_DIR / "equivalencias_mb.json"

# Armazenamento local (gitignored): arquivos originais, logs e screenshots.
STORAGE_DIR = REPO_ROOT / "storage" / "app" / "assobens"
LOGS_DIR = REPO_ROOT / "storage" / "logs" / "assobens"
ERRORS_DIR = LOGS_DIR / "errors"
BACKUP_DIR = STORAGE_DIR / "backup"

SELECTORS_PATH = PACKAGE_DIR / "selectors.json"

TZ = ZoneInfo("America/Sao_Paulo")
SCHEDULE_HOURS = (8, 12, 17)          # horário local America/Sao_Paulo
SCHEDULE_CRON_LOCAL = "0 8,12,17 * * *"
SCHEDULE_CRON_UTC = "0 11,15,20 * * *"  # GitHub Actions só aceita UTC; BR sem horário de verão desde 2019

PORTAL_URL = "https://portal.assobens.org.br/"
PORTAL_LOGIN_URL = "https://portal.assobens.org.br/wp-login.php"
BI_URL = "https://bi-assobens.com.br/"
BI_API_URL = "https://api.bi-assobens.com.br/v1"
BI_MENU_EMPLACAMENTOS = "Veículos Novos Área Operacional"
BI_MENU_PRECOS = "Comparativo de Preços"
BI_STORAGE_KEY = "_pbiAssobens"

RETRY_WAITS_SECONDS = (30, 120)       # tentativa 1 -> 30s -> tentativa 2 -> 2min -> tentativa 3
MAX_ATTEMPTS = 3
DROP_ALERT_RATIO = 0.5                # queda > 50% de linhas vs. execução anterior = suspeito
MIN_QUALITY_SCORE = 75                # mesmo gate da Torre (computeQuality >= 75)
SYNC_RUNS_KEEP = 300
# Relatório "Baixar Dados" (enriquecimento) como fonte principal do ano: insere e atualiza chassis de caminhões.
# True = modo conservador (só completa proprietário de chassis já existentes na matriz).
ENRIQUECIMENTO_SOMENTE_ATUALIZA = False

# Colunas publicadas na matriz (ordem fixa, igual à matriz atual).
CANONICAL_COLUMNS = [
    "CHASSI", "DATA EMPLACAMENTO", "MODELO", "TRAÇÃO", "MARCA", "SEGMENTO", "SUBSEGMENTO",
    "PLACA", "CONCESSIONÁRIO", "CIDADE", "UF", "DEALER AOP", "AOP", "ANOFABRICACAO",
    "ANOMODELO", "TIPO TERRENO", "CPFCNPJPROPRIETARIO", "TIPOCNPJPROPRIETARIO", "NOMEPROPRIETARIO",
]
MB_BRAND = "M.BENZ"


def load_dotenv(path: Path | None = None) -> None:
    """Carrega .env da raiz sem sobrescrever variáveis já definidas. Sem dependência externa."""
    p = path or (REPO_ROOT / ".env")
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


@dataclass(frozen=True)
class Credentials:
    user: str
    password: str

    @property
    def configured(self) -> bool:
        return bool(self.user and self.password)

    def __repr__(self) -> str:  # nunca expõe a senha em logs/tracebacks
        return f"Credentials(user={self.user!r}, password='***')"


def get_credentials() -> Credentials:
    load_dotenv()
    return Credentials(os.environ.get("ASSOBENS_USER", "").strip(), os.environ.get("ASSOBENS_PASSWORD", ""))


def ensure_dirs() -> None:
    for d in (ASSOBENS_DATA_DIR, STORAGE_DIR, LOGS_DIR, ERRORS_DIR, BACKUP_DIR):
        d.mkdir(parents=True, exist_ok=True)
