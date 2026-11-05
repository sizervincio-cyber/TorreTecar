"""Tabelas da Fase 1: usuários, sessões de login e leads do simulador."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def agora() -> datetime:
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    nome: Mapped[str] = mapped_column(String(160), default="")
    perfil: Mapped[str] = mapped_column(String(20))          # admin | gestor | vendedor | simulacao
    senha_hash: Mapped[str] = mapped_column(String(255))     # Argon2
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    ultimo_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Sessao(Base):
    """Sessão no servidor. O cookie leva um token aleatório; aqui fica só o SHA-256 dele."""
    __tablename__ = "sessoes"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ip: Mapped[str] = mapped_column(String(64), default="")
    user_agent: Mapped[str] = mapped_column(String(300), default="")


class Lead(Base):
    """Lead do simulador público (substitui a planilha do Google Apps Script)."""
    __tablename__ = "leads"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recebido_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, index=True)
    codigo: Mapped[str] = mapped_column(String(40), default="", index=True)
    nome: Mapped[str] = mapped_column(String(160), default="")
    telefone: Mapped[str] = mapped_column(String(40), default="")
    email: Mapped[str] = mapped_column(String(160), default="")
    empresa: Mapped[str] = mapped_column(String(160), default="")
    autoriza_contato: Mapped[bool] = mapped_column(Boolean, default=False)
    payload: Mapped[str] = mapped_column(Text)               # JSON completo enviado pelo simule.html
    ip: Mapped[str] = mapped_column(String(64), default="")
