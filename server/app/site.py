"""Arquivos do site (páginas e dados) servidos só a partir de uma lista fechada.

Nada fora da lista sai do servidor, mesmo que esteja no checkout (relatórios avulsos, backups, planilhas brutas).
As páginas HTML recebem `window.TORRE_SERVER`, que desliga o gate antigo do navegador e informa o perfil.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# Páginas e recursos estáticos (qualquer usuário logado).
_PAGINAS = [
    r"Analitycmbb\.html", r"gestao-tecar\.html", r"fenatran\.html", r"tco-simulador\.html", r"trucktest\.html", r"simule\.html",
    r"trucktest-[\w-]+\.(js|json|xlsx)", r"LOGO\.png", r"ASSETS/[\w./ -]+\.(png|jpe?g|webp|svg)",
    r"Analityc share/capa\.(jpg|png|webp)",
]
# Dados comerciais (todos os perfis menos 'simulacao').
_DADOS = [
    r"Analityc share/consolidado_emplacamentos_2020_2026\.xlsx",
    r"Analityc share/assobens/[\w.-]+\.(json|csv)",
    r"Analityc share/licitacoes/[\w.-]+\.json",
]
# Host público do simulador: só o necessário para o simule.html abrir.
_PUBLICO = [r"simule\.html", r"ASSETS/grupo-tecar-squarelogo-1553565271092\.webp", r"LOGO\.png"]

# Recursos da tela de login do painel: precisam abrir antes de existir sessão.
_LOGIN_PUBLICO = [r"ASSETS/login-fundo\.webp"]

_RE = lambda lst: re.compile("^(?:" + "|".join(lst) + ")$")  # noqa: E731
RE_PAGINAS, RE_DADOS, RE_PUBLICO, RE_LOGIN = _RE(_PAGINAS), _RE(_DADOS), _RE(_PUBLICO), _RE(_LOGIN_PUBLICO)
_HEAD = re.compile(rb"<head[^>]*>", re.I)


def classifica(rel: str) -> str | None:
    """'pagina', 'dados' ou None (fora da lista)."""
    if ".." in rel.split("/"):
        return None
    if RE_PAGINAS.match(rel):
        return "pagina"
    if RE_DADOS.match(rel):
        return "dados"
    return None


def publico(rel: str) -> bool:
    return bool(RE_PUBLICO.match(rel)) and ".." not in rel.split("/")


def recurso_do_login(rel: str) -> bool:
    return bool(RE_LOGIN.match(rel)) and ".." not in rel.split("/")


def resolve(root: Path, rel: str) -> Path | None:
    p = (root / rel).resolve()
    try:
        p.relative_to(root)
    except ValueError:
        return None
    return p if p.is_file() else None


def html_com_marcador(path: Path, marcador: dict) -> bytes:
    """Lê a página e injeta `window.TORRE_SERVER` logo depois de <head>."""
    raw = path.read_bytes()
    js = json.dumps(marcador, ensure_ascii=False).replace("</", "<\\/")
    tag = f"<script>window.TORRE_SERVER={js};</script>".encode()
    m = _HEAD.search(raw)
    return raw[: m.end()] + tag + raw[m.end():] if m else tag + raw
