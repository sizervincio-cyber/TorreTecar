"""Configuração do servidor da Torre. Tudo vem do ambiente (.env na VPS); nada de segredo no código."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PERFIS = ("admin", "gestor", "vendedor", "simulacao")
# Perfil que as páginas atuais entendem (o modo restrito do gate antigo se chamava 'sim').
PERFIL_FRONT = {"admin": "all", "gestor": "all", "vendedor": "all", "simulacao": "sim"}


def _bool(v: str | None, default: bool) -> bool:
    return default if v is None else v.strip().lower() in ("1", "true", "sim", "yes")


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite:///./torre.db"
    site_root: Path = REPO_ROOT                  # checkout do repositório com as páginas e os dados
    cookie_secure: bool = True
    cookie_name: str = "torre_sessao"
    session_hours: int = 12
    public_host_prefix: str = "simule."          # host público: só o simulador e o POST de leads
    login_max_falhas: int = 5
    login_bloqueio_min: int = 15
    leads_por_hora_ip: int = 10


def load_settings() -> Settings:
    e = os.environ
    return Settings(
        database_url=e.get("DATABASE_URL", Settings.database_url),
        site_root=Path(e.get("TORRE_SITE_ROOT", str(REPO_ROOT))).resolve(),
        cookie_secure=_bool(e.get("TORRE_COOKIE_SECURE"), True),
        session_hours=int(e.get("TORRE_SESSION_HOURS", "12")),
        public_host_prefix=e.get("TORRE_PUBLIC_HOST_PREFIX", "simule."),
    )
