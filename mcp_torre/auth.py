"""Portão de acesso do MCP da Torre: Codex (token fixo) e ChatGPT (OAuth 2.1), uma única porta.

Dois tipos de credencial no cabeçalho Authorization: Bearer
  1. Token fixo do Codex (torre_...): no servidor fica só o SHA-256 (TORRE_MCP_TOKENS_SHA256). Comportamento
     idêntico ao que já funcionava.
  2. Access token JWT (ES256) emitido pelo painel da Torre (servidor de autorização OAuth). Aqui fica só a
     CHAVE PÚBLICA: o MCP consegue verificar, mas não consegue emitir token nem tocar no banco.
     Checagens: assinatura, emissor (iss), destinatário (aud = URL deste MCP), validade (exp/iat), escopo
     torre.read e perfil do usuário na lista permitida.

Sem credencial válida: 401 com WWW-Authenticate apontando para o Protected Resource Metadata (RFC 9728), que é
como o ChatGPT descobre o OAuth. Escopo insuficiente ou perfil sem acesso: 403.

Também aqui: /health, os documentos .well-known, lista fechada de caminhos e métodos, limite por usuário,
tempo máximo por chamada e log de auditoria (sem tokens e sem argumentos de consulta).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field

import anyio
import jwt

log = logging.getLogger("torre-mcp.auditoria")

ESCOPO = "torre.read"
MAX_CORPO = 256_000          # uma chamada MCP de consulta nunca chega perto disso
TEMPO_CORPO_S = 10.0
WELL_KNOWN = "/.well-known/oauth-protected-resource"


@dataclass(frozen=True)
class Principal:
    tipo: str                 # "codex" | "oauth"
    sujeito: str              # usuario:<id> ou codex:<prefixo do hash>
    login: str = ""
    perfil: str = ""
    client_id: str = ""
    escopos: tuple[str, ...] = (ESCOPO,)


@dataclass
class ConfigAuth:
    hashes_codex: set[str] = field(default_factory=set)
    resource_url: str = ""            # https://mcp.<dominio>/mcp  (aud dos tokens)
    issuer: str = ""                  # https://torre.<dominio>    (servidor de autorização)
    chave_publica_pem: str = ""       # ES256
    perfis: frozenset[str] = frozenset({"admin", "gestor", "vendedor"})

    @property
    def oauth(self) -> bool:
        return bool(self.resource_url and self.issuer and self.chave_publica_pem)

    @property
    def metadata_url(self) -> str:
        if not self.resource_url:
            return ""
        esquema, resto = self.resource_url.split("://", 1)
        host, _, caminho = resto.partition("/")
        return f"{esquema}://{host}{WELL_KNOWN}" + (f"/{caminho}".rstrip("/") if caminho else "")


def pem_de_b64(v: str) -> str:
    """Aceita a chave em PEM puro ou em base64 de uma linha (formato do deploy/.env)."""
    v = (v or "").strip()
    if not v or v.startswith("-----BEGIN"):
        return v
    return base64.b64decode(v).decode()


class Verificador:
    def __init__(self, cfg: ConfigAuth):
        self.cfg = cfg
        self._chave = None
        if cfg.oauth:
            from cryptography.hazmat.primitives.serialization import load_pem_public_key
            self._chave = load_pem_public_key(cfg.chave_publica_pem.encode())

    def verifica(self, token: str) -> tuple[Principal | None, str]:
        """(principal, motivo). motivo != "" quando recusado: invalid_token ou insufficient_scope."""
        if not token:
            return None, "invalid_token"
        if token.startswith("torre_"):
            h = hashlib.sha256(token.encode()).hexdigest()
            if any(hmac.compare_digest(h, x) for x in self.cfg.hashes_codex):
                return Principal("codex", f"codex:{h[:12]}"), ""
            return None, "invalid_token"
        if self._chave is None:
            return None, "invalid_token"
        try:
            c = jwt.decode(token, self._chave, algorithms=["ES256"], audience=self.cfg.resource_url,
                           issuer=self.cfg.issuer, leeway=30,
                           options={"require": ["exp", "iat", "iss", "aud", "sub"]})
        except jwt.PyJWTError:
            return None, "invalid_token"
        escopos = tuple(str(c.get("scope", "")).split())
        if ESCOPO not in escopos:
            return None, "insufficient_scope"
        if c.get("perfil") not in self.cfg.perfis:
            return None, "insufficient_scope"
        return Principal("oauth", str(c["sub"]), str(c.get("login", "")), str(c.get("perfil", "")),
                         str(c.get("client_id", "")), escopos), ""


def _json(status: int, corpo: dict, extra: list[tuple[bytes, bytes]] | None = None):
    dados = json.dumps(corpo, ensure_ascii=False).encode()
    cab = [(b"content-type", b"application/json; charset=utf-8"), (b"content-length", str(len(dados)).encode()),
           (b"cache-control", b"no-store")] + (extra or [])

    async def app(scope, receive, send):
        await send({"type": "http.response.start", "status": status, "headers": cab})
        await send({"type": "http.response.body", "body": dados})
    return app


class Portao:
    """Middleware ASGI na frente do app MCP do SDK."""

    def __init__(self, app, cfg: ConfigAuth, por_minuto: int = 120, timeout_s: float = 60.0,
                 caminho_mcp: str = "/mcp"):
        self.app, self.cfg, self.por_minuto, self.timeout_s, self.caminho = app, cfg, por_minuto, timeout_s, caminho_mcp
        self.verificador = Verificador(cfg)
        self.janela: dict[str, deque] = defaultdict(deque)

    # ---------- documentos públicos ----------
    def _protected_resource(self) -> dict:
        return {"resource": self.cfg.resource_url, "authorization_servers": [self.cfg.issuer],
                "scopes_supported": [ESCOPO], "bearer_methods_supported": ["header"],
                "resource_name": "Torre Tecar (somente leitura)"}

    def _www_auth(self, erro: str) -> list[tuple[bytes, bytes]]:
        partes = [f'error="{erro}"', f'scope="{ESCOPO}"']
        if self.cfg.oauth:
            partes.insert(0, f'resource_metadata="{self.cfg.metadata_url}"')
        return [(b"www-authenticate", ("Bearer " + ", ".join(partes)).encode())]

    def _limite(self, chave: str) -> bool:
        agora = time.monotonic()
        if len(self.janela) > 5000:            # varre chaves sem chamadas no último minuto (muitos IPs distintos)
            for k in [k for k, f in self.janela.items() if not f or agora - f[-1] > 60]:
                del self.janela[k]
        fila = self.janela[chave]
        while fila and agora - fila[0] > 60:
            fila.popleft()
        if len(fila) >= self.por_minuto:
            return False
        fila.append(agora)
        return True

    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            return await self.app(scope, receive, send)
        if scope["type"] != "http":
            return await _json(404, {"erro": "não encontrado"})(scope, receive, send)
        caminho, metodo = scope.get("path", ""), scope.get("method", "")

        if caminho == "/health":
            return await _json(200, {"ok": True})(scope, receive, send)
        if caminho.startswith(WELL_KNOWN):
            if not self.cfg.oauth or metodo != "GET":
                return await _json(404, {"erro": "não encontrado"})(scope, receive, send)
            return await _json(200, self._protected_resource())(scope, receive, send)
        if caminho.rstrip("/") != self.caminho:
            return await _json(404, {"erro": "não encontrado"})(scope, receive, send)
        if metodo != "POST":   # modo sem estado: só POST; GET (SSE), DELETE, PUT etc. nunca chegam ao SDK
            return await _json(405, {"erro": "método não permitido"}, [(b"allow", b"POST")])(scope, receive, send)

        inicio, rid = time.monotonic(), _rid(scope)
        cab = dict(scope.get("headers") or [])
        auth = cab.get(b"authorization", b"").decode("latin-1")
        token = auth[7:].strip() if auth.lower().startswith("bearer ") else ""
        principal, motivo = self.verificador.verifica(token)
        ip = (scope.get("client") or ("?", 0))[0]
        if not self._limite(principal.sujeito if principal else f"ip:{ip}"):
            _audita(rid, principal, ip, "-", 429, inicio)
            return await _json(429, {"erro": "limite de chamadas por minuto"}, [(b"retry-after", b"60")])(scope, receive, send)
        if principal is None:
            status = 403 if motivo == "insufficient_scope" else 401
            _audita(rid, None, ip, "-", status, inicio, motivo)
            msg = "sem permissão para a Torre" if status == 403 else "autenticação necessária"
            return await _json(status, {"error": motivo, "error_description": msg},
                               self._www_auth(motivo))(scope, receive, send)

        # Lê o corpo (limitado) para registrar qual ferramenta foi chamada, e o devolve intacto ao SDK.
        corpo = b""
        try:
            with anyio.fail_after(TEMPO_CORPO_S):   # envio lento não segura vaga de conexão
                while True:
                    m = await receive()
                    corpo += m.get("body", b"")
                    if len(corpo) > MAX_CORPO:
                        _audita(rid, principal, ip, "-", 413, inicio)
                        return await _json(413, {"erro": "requisição grande demais"})(scope, receive, send)
                    if not m.get("more_body"):
                        break
        except TimeoutError:
            _audita(rid, principal, ip, "-", 408, inicio)
            return await _json(408, {"erro": "corpo da requisição demorou demais"})(scope, receive, send)
        acao = _acao(corpo)
        entregue = False

        async def receive2():
            nonlocal entregue
            if not entregue:
                entregue = True
                return {"type": "http.request", "body": corpo, "more_body": False}
            return await receive()

        status = {"v": 500, "iniciou": False}

        async def send2(msg):
            if msg["type"] == "http.response.start":
                status["v"], status["iniciou"] = msg["status"], True
            await send(msg)

        scope = {**scope, "state": {**(scope.get("state") or {}), "principal": principal, "request_id": rid}}
        try:
            with anyio.fail_after(self.timeout_s):
                await self.app(scope, receive2, send2)
        except TimeoutError:
            if not status["iniciou"]:
                status["v"] = 504
                await _json(504, {"erro": "a consulta passou do tempo limite"})(scope, receive, send)
        _audita(rid, principal, ip, acao, status["v"], inicio)


def _rid(scope) -> str:
    cab = dict(scope.get("headers") or [])
    v = cab.get(b"x-request-id", b"").decode("latin-1")[:64]
    return v if v and v.replace("-", "").isalnum() else uuid.uuid4().hex[:16]


def _acao(corpo: bytes) -> str:
    """Método JSON-RPC e nome da ferramenta. Nunca os argumentos (podem conter CNPJ, nomes)."""
    try:
        d = json.loads(corpo or b"{}")
    except ValueError:
        return "json-invalido"
    itens = d if isinstance(d, list) else [d]
    out = []
    for x in itens[:10]:
        if not isinstance(x, dict):
            continue
        m = str(x.get("method", "?"))[:40]
        if m == "tools/call" and isinstance(x.get("params"), dict):
            m += ":" + str(x["params"].get("name", "?"))[:60]
        out.append(m)
    return ",".join(out) or "-"


def _audita(rid, principal: Principal | None, ip, acao, status, inicio, motivo=""):
    log.info(json.dumps({
        "rid": rid, "quem": principal.sujeito if principal else None, "login": principal.login if principal else None,
        "tipo": principal.tipo if principal else None, "cliente": principal.client_id if principal else None,
        "ip": ip, "acao": acao, "status": status, "ms": round(1000 * (time.monotonic() - inicio)),
        **({"motivo": motivo} if motivo else {})}, ensure_ascii=False))
