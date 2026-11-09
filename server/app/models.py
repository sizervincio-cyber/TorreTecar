"""Tabelas da Fase 1: usuários, sessões de login e leads do simulador."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
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


# ---------- OAuth 2.1 (servidor de autorização para o MCP somente leitura) ----------
# Estado de autenticação, separado dos dados de negócio. Tokens e códigos: só o SHA-256 fica no banco.
class OAuthCliente(Base):
    """Cliente registrado por Dynamic Client Registration (RFC 7591), ex.: o conector do ChatGPT."""
    __tablename__ = "oauth_clientes"
    client_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    nome: Mapped[str] = mapped_column(String(160), default="")
    redirect_uris: Mapped[str] = mapped_column(Text)                # JSON (lista)
    auth_metodo: Mapped[str] = mapped_column(String(32), default="none")  # none | client_secret_post | client_secret_basic
    segredo_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    ip: Mapped[str] = mapped_column(String(64), default="")


class OAuthCodigo(Base):
    """Código de autorização: uso único, 5 minutos, amarrado a PKCE S256, redirect_uri e usuário."""
    __tablename__ = "oauth_codigos"
    codigo_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    client_id: Mapped[str] = mapped_column(ForeignKey("oauth_clientes.client_id", ondelete="CASCADE"), index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)
    redirect_uri: Mapped[str] = mapped_column(Text)
    code_challenge: Mapped[str] = mapped_column(String(128))
    escopo: Mapped[str] = mapped_column(String(200))
    recurso: Mapped[str] = mapped_column(String(300))
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class OAuthRefresh(Base):
    """Refresh token com rotação. Reuso de um token já trocado revoga a família inteira."""
    __tablename__ = "oauth_refresh"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    familia: Mapped[str] = mapped_column(String(32), index=True)
    client_id: Mapped[str] = mapped_column(ForeignKey("oauth_clientes.client_id", ondelete="CASCADE"), index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)
    escopo: Mapped[str] = mapped_column(String(200))
    recurso: Mapped[str] = mapped_column(String(300))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    usado: Mapped[bool] = mapped_column(Boolean, default=False)


# ---------- Condições comerciais temporárias (Preço Fenatran) ----------
# Separadas dos preços históricos ASSOBENS (que ficam em arquivos). Cada importação é um lote versionado: o lote
# anterior continua no banco (histórico); a campanha aponta para o lote atual. Status: draft | active | inactive |
# archived, mudado só por administrador (nunca por data). Valores sempre em centavos inteiros (BIGINT).
class ComercialCampanha(Base):
    __tablename__ = "comercial_campanhas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chave: Mapped[str] = mapped_column(String(40), unique=True, index=True)          # fenatran_2026
    nome: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(12), default="draft")                # draft|active|inactive|archived
    versao: Mapped[int] = mapped_column(Integer, default=0)                          # versão do lote atual
    lote_atual_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expira_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)  # opcional, do admin
    metadados: Mapped[str] = mapped_column(Text)            # JSON: rótulos, alíquotas declaradas, condições, fonte
    responsavel: Mapped[str] = mapped_column(String(120), default="")
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    __table_args__ = (CheckConstraint("status IN ('draft','active','inactive','archived')",
                                      name="ck_comercial_campanhas_status"),)


class ComercialLote(Base):
    """Uma importação aplicada (dry-run não grava). Guarda hashes, conferência com os PDFs e diff da versão anterior."""
    __tablename__ = "comercial_lotes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campanha_id: Mapped[int] = mapped_column(ForeignKey("comercial_campanhas.id", ondelete="RESTRICT"), index=True)
    versao: Mapped[int] = mapped_column(Integer)
    arquivo_csv: Mapped[str] = mapped_column(String(200))
    sha256_csv: Mapped[str] = mapped_column(String(64))
    linhas: Mapped[int] = mapped_column(Integer)
    por_familia: Mapped[str] = mapped_column(Text)          # JSON
    documentos: Mapped[str] = mapped_column(Text)           # JSON: PDF -> sha256, confere com manifesto
    conferencia: Mapped[str] = mapped_column(Text)          # JSON: divergências com os PDFs (vazio = conferido)
    diff: Mapped[str] = mapped_column(Text)                 # JSON: novas, removidas, alteradas
    manifesto: Mapped[str] = mapped_column(Text)            # JSON do manifesto de auditoria
    executado_por: Mapped[str] = mapped_column(String(120))
    executado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    __table_args__ = (UniqueConstraint("campanha_id", "versao", name="uq_comercial_lotes_campanha_versao"),)


class ComercialPreco(Base):
    __tablename__ = "comercial_precos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campanha_id: Mapped[int] = mapped_column(ForeignKey("comercial_campanhas.id", ondelete="RESTRICT"))
    lote_id: Mapped[int] = mapped_column(ForeignKey("comercial_lotes.id", ondelete="RESTRICT"))
    familia: Mapped[str] = mapped_column(String(12))
    modelo: Mapped[str] = mapped_column(String(40))
    modelo_busca: Mapped[str] = mapped_column(String(40))
    ano_modelo: Mapped[str] = mapped_column(String(5))
    up: Mapped[str] = mapped_column(String(4))
    variante: Mapped[str] = mapped_column(String(20))
    configuracao: Mapped[str] = mapped_column(String(5))
    preco_fabrica_5_10_centavos: Mapped[int] = mapped_column(BigInteger)
    preco_fabrica_11_15_centavos: Mapped[int] = mapped_column(BigInteger)
    preco_estoque_5_10_centavos: Mapped[int] = mapped_column(BigInteger)
    preco_estoque_11_15_centavos: Mapped[int] = mapped_column(BigInteger)
    source_file: Mapped[str] = mapped_column(String(80))
    source_page: Mapped[int] = mapped_column(Integer)
    __table_args__ = (UniqueConstraint("lote_id", "variante", name="uq_comercial_precos_lote_variante"),
                      CheckConstraint("preco_fabrica_5_10_centavos > 0 AND preco_fabrica_11_15_centavos > 0 AND "
                                      "preco_estoque_5_10_centavos > 0 AND preco_estoque_11_15_centavos > 0",
                                      name="ck_comercial_precos_positivos"),
                      Index("ix_comercial_precos_campanha_variante", "campanha_id", "variante"),
                      Index("ix_comercial_precos_lote_busca", "lote_id", "modelo_busca"))


class ComercialEvento(Base):
    """Trilha de auditoria: importação, ativação, desativação, arquivamento, expiração. Sem valores de preço."""
    __tablename__ = "comercial_eventos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campanha_id: Mapped[int] = mapped_column(ForeignKey("comercial_campanhas.id", ondelete="RESTRICT"), index=True)
    acao: Mapped[str] = mapped_column(String(30))
    de_status: Mapped[str] = mapped_column(String(12), default="")
    para_status: Mapped[str] = mapped_column(String(12), default="")
    usuario: Mapped[str] = mapped_column(String(120))
    detalhe: Mapped[str] = mapped_column(Text, default="")
    em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, index=True)
