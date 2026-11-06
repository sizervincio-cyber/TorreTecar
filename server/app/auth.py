"""Senhas (Argon2), sessões no servidor e bloqueio de tentativas de login."""
from __future__ import annotations

import hashlib
import secrets
import threading
import time
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .models import OAuthCodigo, OAuthRefresh, Sessao, Usuario, agora

_ph = PasswordHasher()
# Hash fixo para gastar o mesmo tempo quando o login não existe (não revela quais logins são válidos).
_DUMMY = _ph.hash("torre-tecar-login-inexistente")


def hash_senha(senha: str) -> str:
    if len(senha) < 10:
        raise ValueError("a senha precisa de pelo menos 10 caracteres")
    return _ph.hash(senha)


def confere_senha(hash_: str, senha: str) -> bool:
    try:
        return _ph.verify(hash_, senha)
    except (VerificationError, InvalidHashError):
        return False


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def autentica(db: Session, login: str, senha: str) -> Usuario | None:
    u = db.scalar(select(Usuario).where(Usuario.login == login.strip().lower()))
    if u is None or not u.ativo:
        confere_senha(_DUMMY, senha)
        return None
    if not confere_senha(u.senha_hash, senha):
        return None
    if _ph.check_needs_rehash(u.senha_hash):
        u.senha_hash = _ph.hash(senha)
    u.ultimo_login = agora()
    return u


def cria_sessao(db: Session, u: Usuario, horas: int, ip: str = "", user_agent: str = "") -> str:
    token = secrets.token_urlsafe(32)
    db.execute(delete(Sessao).where(Sessao.expira_em < agora()))  # limpeza oportunista
    db.add(Sessao(token_hash=_token_hash(token), usuario_id=u.id, expira_em=agora() + timedelta(hours=horas),
                  ip=ip[:64], user_agent=user_agent[:300]))
    return token


def usuario_da_sessao(db: Session, token: str | None) -> Usuario | None:
    if not token:
        return None
    s = db.get(Sessao, _token_hash(token))
    if s is None:
        return None
    exp = s.expira_em if s.expira_em.tzinfo else s.expira_em.replace(tzinfo=timezone.utc)  # SQLite perde o fuso
    if exp < datetime.now(timezone.utc):
        db.delete(s)
        return None
    u = db.get(Usuario, s.usuario_id)
    return u if u is not None and u.ativo else None


def encerra_sessao(db: Session, token: str | None) -> None:
    if token:
        db.execute(delete(Sessao).where(Sessao.token_hash == _token_hash(token)))


def encerra_sessoes_do_usuario(db: Session, usuario_id: int) -> None:
    """Derruba as sessões do painel e as autorizações OAuth (ChatGPT) do usuário."""
    db.execute(delete(Sessao).where(Sessao.usuario_id == usuario_id))
    db.execute(delete(OAuthRefresh).where(OAuthRefresh.usuario_id == usuario_id))
    db.execute(delete(OAuthCodigo).where(OAuthCodigo.usuario_id == usuario_id))


class Limitador:
    """Contador em memória por chave (IP, login). Basta para um processo só, que é o caso da VPS."""

    def __init__(self, maximo: int, janela_s: int, relogio=time.monotonic):
        self.maximo, self.janela_s, self._relogio = maximo, janela_s, relogio
        self._eventos: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def _vivos(self, chave: str) -> list[float]:
        t = self._relogio()
        ev = [x for x in self._eventos.get(chave, []) if t - x < self.janela_s]
        self._eventos[chave] = ev
        return ev

    def bloqueado(self, chave: str) -> bool:
        with self._lock:
            return len(self._vivos(chave)) >= self.maximo

    def registra(self, chave: str) -> None:
        with self._lock:
            self._vivos(chave).append(self._relogio())

    def limpa(self, chave: str) -> None:
        with self._lock:
            self._eventos.pop(chave, None)
