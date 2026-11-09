"""Configuração do servidor da Torre. Tudo vem do ambiente (.env na VPS); nada de segredo no código."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PERFIS = ("admin", "gestor", "vendedor", "simulacao")
# Perfil que as páginas atuais entendem (o modo restrito do gate antigo se chamava 'sim').
PERFIL_FRONT = {"admin": "all", "gestor": "all", "vendedor": "all", "simulacao": "sim"}


# Callbacks OAuth do ChatGPT (conectores personalizados). Confira na documentação da OpenAI e ajuste por
# TORRE_OAUTH_REDIRECT_URIS se mudarem; um item terminado em "/" aceita qualquer caminho abaixo dele.
REDIRECTS_PADRAO = "https://chatgpt.com/connector_platform_oauth_redirect,https://chatgpt.com/connector/oauth/"


def _lista(v: str) -> tuple[str, ...]:
    return tuple(x.strip() for x in (v or "").split(",") if x.strip())


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
    # OAuth 2.1 para o MCP somente leitura (ChatGPT). Desligado enquanto oauth_issuer estiver vazio.
    oauth_issuer: str = ""                       # https://torre.<dominio> (URL pública deste painel)
    oauth_recurso: str = ""                      # https://mcp.<dominio>/mcp (aud dos access tokens)
    oauth_chave_privada: str = ""                # PEM ES256 (ou base64 de uma linha), só no deploy/.env
    oauth_redirects: tuple[str, ...] = ()        # redirect_uri aceitos no registro (exatos ou prefixo terminado em /)
    oauth_perfis: tuple[str, ...] = ("admin", "gestor", "vendedor")   # 'simulacao' não vê dados: sem MCP
    oauth_logins_piloto: tuple[str, ...] = ()   # piloto: só estes logins recebem token; vazio = todos os perfis acima
    oauth_access_min: int = 30
    oauth_refresh_dias: int = 30
    oauth_registros_por_hora_ip: int = 10
    # Pasta privada (volume Docker fora do git): snapshot da campanha Fenatran que o MCP lê em modo somente leitura.
    privado_dir: Path = REPO_ROOT / "dados_privados" / "runtime"

    @property
    def oauth_ligado(self) -> bool:
        return bool(self.oauth_issuer and self.oauth_recurso and self.oauth_chave_privada)


def load_settings() -> Settings:
    e = os.environ
    return Settings(
        database_url=e.get("DATABASE_URL", Settings.database_url),
        site_root=Path(e.get("TORRE_SITE_ROOT", str(REPO_ROOT))).resolve(),
        cookie_secure=_bool(e.get("TORRE_COOKIE_SECURE"), True),
        session_hours=int(e.get("TORRE_SESSION_HOURS", "12")),
        public_host_prefix=e.get("TORRE_PUBLIC_HOST_PREFIX", "simule."),
        oauth_issuer=e.get("TORRE_OAUTH_ISSUER", "").strip().rstrip("/"),
        oauth_recurso=e.get("TORRE_MCP_RESOURCE_URL", "").strip().rstrip("/"),
        oauth_chave_privada=e.get("TORRE_OAUTH_PRIVATE_KEY", "").strip(),
        oauth_redirects=_lista(e.get("TORRE_OAUTH_REDIRECT_URIS", REDIRECTS_PADRAO)),
        oauth_perfis=_lista(e.get("TORRE_MCP_PERFIS", "admin,gestor,vendedor")),
        oauth_logins_piloto=_lista(e.get("TORRE_OAUTH_LOGINS_PILOTO", "")),
        oauth_access_min=int(e.get("TORRE_OAUTH_ACCESS_MIN", "30")),
        oauth_refresh_dias=int(e.get("TORRE_OAUTH_REFRESH_DIAS", "30")),
        privado_dir=Path(e.get("TORRE_PRIVADO_DIR", str(REPO_ROOT / "dados_privados" / "runtime"))),
    )
