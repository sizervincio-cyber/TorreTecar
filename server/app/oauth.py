"""Servidor de autorização OAuth 2.1 da Torre, só para o MCP somente leitura (ChatGPT).

Reaproveita o login que já existe: quem autoriza é o usuário da Torre, na tela de login da Torre. Não há
provedor de identidade novo nem senha nova.

  GET  /.well-known/oauth-authorization-server   metadados (RFC 8414)
  GET  /oauth/jwks                               chave pública ES256 (o MCP também a recebe pelo .env)
  POST /oauth/register                           Dynamic Client Registration (RFC 7591), redirect_uri só da lista
  GET  /oauth/authorize                          Authorization Code + PKCE S256 obrigatório -> login -> consentimento
  POST /oauth/authorize                          decisão do consentimento (CSRF amarrado à sessão)
  POST /oauth/token                              authorization_code e refresh_token (rotação + detecção de reuso)
  POST /oauth/revoke                             revogação (RFC 7009)

Regras: o único escopo é torre.read; o access token (JWT ES256, 30 min) tem aud = URL do MCP (RFC 8707);
perfil 'simulacao' (que não vê dados no painel) não recebe token; usuário desativado perde o acesso no próximo
refresh e, no máximo, quando o access token vence. Nada aqui toca em dados de negócio: só nas tabelas oauth_*.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import secrets
import time
from datetime import datetime, timedelta, timezone
from html import escape
from urllib.parse import urlencode, urlsplit

import jwt
from cryptography.hazmat.primitives import serialization
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from sqlalchemy import delete, select

from .auth import Limitador
from .config import Settings
from .models import OAuthCliente, OAuthCodigo, OAuthRefresh, Usuario, agora

ESCOPO = "torre.read"
METODOS_AUTH = ("none", "client_secret_post", "client_secret_basic")
GRANTS = ("authorization_code", "refresh_token")
CODIGO_MIN = 5
_PKCE = re.compile(r"^[A-Za-z0-9._~-]{43,128}$")
_SEM_CACHE = {"Cache-Control": "no-store", "Pragma": "no-cache"}


def _h(v: str) -> str:
    return hashlib.sha256(v.encode()).hexdigest()


def _utc(d: datetime) -> datetime:
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)  # SQLite perde o fuso


def carrega_chave(v: str):
    v = (v or "").strip()
    pem = v if v.startswith("-----BEGIN") else base64.b64decode(v).decode()
    return serialization.load_pem_private_key(pem.encode(), password=None)


def redirect_permitido(uri: str, lista: tuple[str, ...]) -> bool:
    """https, sem fragmento, sem usuário/senha na URL e igual a um item da lista (ou abaixo de um item terminado em /)."""
    try:
        p = urlsplit(uri)
    except ValueError:
        return False
    if p.scheme != "https" or not p.hostname or p.fragment or p.username or p.password or "\\" in uri:
        return False
    for item in lista:
        if uri == item or (item.endswith("/") and uri.startswith(item) and ".." not in p.path):
            return True
    return False


def _com_query(uri: str, params: dict) -> str:
    params = {k: v for k, v in params.items() if v is not None}
    return uri + ("&" if urlsplit(uri).query else "?") + urlencode(params)


def _erro(erro: str, desc: str, status: int = 400, extra: dict | None = None) -> JSONResponse:
    return JSONResponse({"error": erro, "error_description": desc}, status_code=status, headers={**_SEM_CACHE, **(extra or {})})


def registrar(app: FastAPI, cfg: Settings, db, usuario_req, para_login, host_publico, ip) -> None:
    """Registra as rotas OAuth no app do painel. Sem configuração completa, nada é registrado (tudo 404)."""
    if not cfg.oauth_ligado:
        return
    chave = carrega_chave(cfg.oauth_chave_privada)
    pub = chave.public_key()
    der = pub.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    kid = hashlib.sha256(der).hexdigest()[:16]
    jwk = {**json.loads(jwt.algorithms.ECAlgorithm.to_jwk(pub)), "kid": kid, "use": "sig", "alg": "ES256"}
    iss, recurso = cfg.oauth_issuer, cfg.oauth_recurso
    registros_ip = Limitador(cfg.oauth_registros_por_hora_ip, 3600)
    falhas_token = Limitador(30, 300)

    def fora(req: Request) -> bool:
        return host_publico(req)

    def metadados() -> dict:
        return {
            "issuer": iss, "authorization_endpoint": f"{iss}/oauth/authorize", "token_endpoint": f"{iss}/oauth/token",
            "registration_endpoint": f"{iss}/oauth/register", "revocation_endpoint": f"{iss}/oauth/revoke",
            "jwks_uri": f"{iss}/oauth/jwks", "scopes_supported": [ESCOPO], "response_types_supported": ["code"],
            "response_modes_supported": ["query"], "grant_types_supported": list(GRANTS),
            "code_challenge_methods_supported": ["S256"],
            "token_endpoint_auth_methods_supported": list(METODOS_AUTH),
            "revocation_endpoint_auth_methods_supported": list(METODOS_AUTH),
            "authorization_response_iss_parameter_supported": True,
        }

    @app.get("/.well-known/oauth-authorization-server")
    def as_metadata(req: Request):
        if fora(req):
            return Response(status_code=404)
        return JSONResponse(metadados(), headers={"Cache-Control": "public, max-age=300"})

    @app.get("/oauth/jwks")
    def jwks(req: Request):
        if fora(req):
            return Response(status_code=404)
        return JSONResponse({"keys": [jwk]}, headers={"Cache-Control": "public, max-age=300"})

    # ---------- registro dinâmico ----------
    @app.post("/oauth/register")
    async def register(req: Request):
        if fora(req):
            return Response(status_code=404)
        quem = ip(req)
        if registros_ip.bloqueado(quem):
            return _erro("invalid_client_metadata", "limite de registros por hora", 429)
        corpo = await req.body()
        if len(corpo) > 16_000:
            return _erro("invalid_client_metadata", "metadados grandes demais")
        try:
            m = json.loads(corpo or b"{}")
        except ValueError:
            return _erro("invalid_client_metadata", "JSON inválido")
        if not isinstance(m, dict):
            return _erro("invalid_client_metadata", "JSON inválido")
        uris = m.get("redirect_uris")
        if not isinstance(uris, list) or not 1 <= len(uris) <= 5 or not all(isinstance(u, str) and len(u) <= 500 for u in uris):
            return _erro("invalid_redirect_uri", "redirect_uris: de 1 a 5 URLs")
        if not all(redirect_permitido(u, cfg.oauth_redirects) for u in uris):
            return _erro("invalid_redirect_uri", "redirect_uri fora da lista permitida pela Torre")
        metodo = m.get("token_endpoint_auth_method") or "client_secret_basic"   # padrão da RFC 7591
        if metodo not in METODOS_AUTH:
            return _erro("invalid_client_metadata", f"token_endpoint_auth_method: use {', '.join(METODOS_AUTH)}")
        grants = m.get("grant_types") or ["authorization_code"]
        if not isinstance(grants, list) or not set(grants) <= set(GRANTS):
            return _erro("invalid_client_metadata", "grant_types: só authorization_code e refresh_token")
        if (m.get("response_types") or ["code"]) != ["code"]:
            return _erro("invalid_client_metadata", "response_types: só code")
        nome = str(m.get("client_name") or "")[:160]
        registros_ip.registra(quem)
        client_id = "tc_" + secrets.token_urlsafe(24)
        segredo = secrets.token_urlsafe(32) if metodo != "none" else None
        with db() as s:
            s.add(OAuthCliente(client_id=client_id, nome=nome, redirect_uris=json.dumps(uris), auth_metodo=metodo,
                               segredo_hash=_h(segredo) if segredo else None, ip=quem))
        resp = {"client_id": client_id, "client_id_issued_at": int(time.time()), "client_name": nome,
                "redirect_uris": uris, "grant_types": list(dict.fromkeys(grants + ["refresh_token"])),
                "response_types": ["code"], "token_endpoint_auth_method": metodo, "scope": ESCOPO}
        if segredo:
            resp.update(client_secret=segredo, client_secret_expires_at=0)
        return JSONResponse(resp, status_code=201, headers=_SEM_CACHE)

    # ---------- autorização ----------
    def valida_pedido(s, p: dict):
        """(cliente, redirect_uri, erro_pagina, erro_redirect). Erro de cliente/redirect nunca redireciona."""
        cli = s.get(OAuthCliente, str(p.get("client_id") or "")[:64])
        if cli is None:
            return None, None, "Cliente OAuth desconhecido.", None
        uris = json.loads(cli.redirect_uris)
        ru = p.get("redirect_uri") or (uris[0] if len(uris) == 1 else "")
        if ru not in uris:
            return None, None, "redirect_uri não registrado para este cliente.", None
        if p.get("response_type") != "code":
            return cli, ru, None, ("unsupported_response_type", "use response_type=code")
        cc, metodo = p.get("code_challenge") or "", p.get("code_challenge_method") or ""
        if not _PKCE.match(cc) or metodo != "S256":
            return cli, ru, None, ("invalid_request", "PKCE obrigatório: code_challenge com code_challenge_method=S256")
        res = (p.get("resource") or "").rstrip("/")
        if res and res != recurso:
            return cli, ru, None, ("invalid_target", "resource desconhecido para este servidor")
        return cli, ru, None, None

    def pagina_erro(msg: str, status: int = 400) -> HTMLResponse:
        return HTMLResponse(_PAGINA.format(corpo=f"<h1>Não foi possível autorizar</h1><p>{escape(msg)}</p>"),
                            status_code=status, headers=_cab_pagina())

    def csrf(req: Request, cli: str, ru: str, cc: str) -> str:
        sess = req.cookies.get(cfg.cookie_name) or ""
        return hmac.new(sess.encode(), f"oauth|{cli}|{ru}|{cc}".encode(), hashlib.sha256).hexdigest()

    @app.get("/oauth/authorize")
    def authorize(req: Request):
        if fora(req):
            return Response(status_code=404)
        p = dict(req.query_params)
        with db() as s:
            cli, ru, erro_pag, erro_red = valida_pedido(s, p)
            nome_cli = cli.nome if cli else ""
        if erro_pag:
            return pagina_erro(erro_pag)
        if erro_red:
            return RedirectResponse(_com_query(ru, {"error": erro_red[0], "error_description": erro_red[1],
                                                    "state": p.get("state"), "iss": iss}), status_code=303)
        u = usuario_req(req)
        if u is None:
            return para_login(req)
        if u.perfil not in cfg.oauth_perfis:
            return RedirectResponse(_com_query(ru, {"error": "access_denied", "error_description":
                                                    "perfil sem acesso às bases da Torre", "state": p.get("state"),
                                                    "iss": iss}), status_code=303)
        campos = {"client_id": cli.client_id, "redirect_uri": ru, "response_type": "code", "state": p.get("state") or "",
                  "code_challenge": p["code_challenge"], "code_challenge_method": "S256",
                  "resource": p.get("resource") or "", "scope": ESCOPO,
                  "csrf": csrf(req, cli.client_id, ru, p["code_challenge"])}
        ocultos = "".join(f'<input type="hidden" name="{k}" value="{escape(v)}">' for k, v in campos.items())
        corpo = _CONSENTIMENTO.format(cliente=escape(nome_cli or "Aplicativo"), destino=escape(urlsplit(ru).hostname or ""),
                                      nome=escape(u.nome or u.login), login=escape(u.login), ocultos=ocultos)
        return HTMLResponse(_PAGINA.format(corpo=corpo), headers=_cab_pagina())

    @app.post("/oauth/authorize")
    async def authorize_decisao(req: Request):
        if fora(req):
            return Response(status_code=404)
        p = {k: str(v) for k, v in (await req.form()).items()}
        u = usuario_req(req)
        if u is None:
            return pagina_erro("Sua sessão expirou. Volte ao ChatGPT e conecte de novo.", 401)
        with db() as s:
            cli, ru, erro_pag, erro_red = valida_pedido(s, p)
            if erro_pag:
                return pagina_erro(erro_pag)
            if erro_red:
                return RedirectResponse(_com_query(ru, {"error": erro_red[0], "state": p.get("state"), "iss": iss}), 303)
            if not hmac.compare_digest(p.get("csrf", ""), csrf(req, cli.client_id, ru, p["code_challenge"])):
                return pagina_erro("Pedido de autorização inválido (CSRF). Tente de novo.", 403)
            if p.get("decisao") != "permitir" or u.perfil not in cfg.oauth_perfis:
                return RedirectResponse(_com_query(ru, {"error": "access_denied", "state": p.get("state"), "iss": iss}), 303)
            codigo = secrets.token_urlsafe(32)
            s.execute(delete(OAuthCodigo).where(OAuthCodigo.expira_em < agora()).execution_options(synchronize_session=False))
            s.add(OAuthCodigo(codigo_hash=_h(codigo), client_id=cli.client_id, usuario_id=u.id, redirect_uri=ru,
                              code_challenge=p["code_challenge"], escopo=ESCOPO, recurso=recurso,
                              expira_em=agora() + timedelta(minutes=CODIGO_MIN)))
        return RedirectResponse(_com_query(ru, {"code": codigo, "state": p.get("state") or None, "iss": iss}), 303)

    # ---------- token ----------
    def autentica_cliente(s, req: Request, f: dict):
        cid, segredo = f.get("client_id", ""), f.get("client_secret")
        basic = req.headers.get("authorization", "")
        if basic.lower().startswith("basic "):
            try:
                cid_b, _, segredo = base64.b64decode(basic[6:]).decode().partition(":")
                from urllib.parse import unquote
                cid_b, segredo = unquote(cid_b), unquote(segredo)
            except Exception:  # noqa: BLE001
                return None
            if cid and cid != cid_b:
                return None
            cid = cid_b
        cli = s.get(OAuthCliente, cid[:64]) if cid else None
        if cli is None:
            return None
        if cli.auth_metodo != "none":
            if not segredo or not cli.segredo_hash or not hmac.compare_digest(_h(segredo), cli.segredo_hash):
                return None
        return cli

    def emite(s, cli: OAuthCliente, u: Usuario, familia: str | None = None) -> dict:
        t = int(time.time())
        claims = {"iss": iss, "aud": recurso, "sub": f"usuario:{u.id}", "login": u.login, "perfil": u.perfil,
                  "scope": ESCOPO, "client_id": cli.client_id, "iat": t, "nbf": t, "exp": t + cfg.oauth_access_min * 60,
                  "jti": secrets.token_hex(12)}
        access = jwt.encode(claims, chave, algorithm="ES256", headers={"kid": kid, "typ": "at+jwt"})
        refresh = secrets.token_urlsafe(40)
        s.execute(delete(OAuthRefresh).where(OAuthRefresh.expira_em < agora()).execution_options(synchronize_session=False))
        s.add(OAuthRefresh(token_hash=_h(refresh), familia=familia or secrets.token_hex(16), client_id=cli.client_id,
                           usuario_id=u.id, escopo=ESCOPO, recurso=recurso,
                           expira_em=agora() + timedelta(days=cfg.oauth_refresh_dias)))
        return {"access_token": access, "token_type": "Bearer", "expires_in": cfg.oauth_access_min * 60,
                "refresh_token": refresh, "scope": ESCOPO}

    def usuario_valido(s, uid: int) -> Usuario | None:
        u = s.get(Usuario, uid)
        return u if u is not None and u.ativo and u.perfil in cfg.oauth_perfis else None

    @app.post("/oauth/token")
    async def token(req: Request):
        if fora(req):
            return Response(status_code=404)
        quem = ip(req)
        if falhas_token.bloqueado(quem):
            return _erro("invalid_request", "muitas tentativas; aguarde", 429)
        f = {k: str(v) for k, v in (await req.form()).items()}
        res = (f.get("resource") or "").rstrip("/")
        if res and res != recurso:
            falhas_token.registra(quem)
            return _erro("invalid_target", "resource desconhecido para este servidor")
        with db() as s:
            cli = autentica_cliente(s, req, f)
            if cli is None:
                falhas_token.registra(quem)
                return _erro("invalid_client", "cliente não autenticado", 401, {"WWW-Authenticate": "Basic"})
            g = f.get("grant_type")
            if g == "authorization_code":
                c = s.get(OAuthCodigo, _h(f.get("code", "")))
                if c is None:
                    falhas_token.registra(quem)
                    return _erro("invalid_grant", "código inválido ou já usado")
                s.delete(c)                       # uso único, mesmo que a troca falhe abaixo
                s.flush()
                v = f.get("code_verifier", "")
                desafio = base64.urlsafe_b64encode(hashlib.sha256(v.encode()).digest()).rstrip(b"=").decode()
                ok = (c.client_id == cli.client_id and _utc(c.expira_em) > agora() and _PKCE.match(v or "")
                      and hmac.compare_digest(desafio, c.code_challenge) and f.get("redirect_uri", c.redirect_uri) == c.redirect_uri)
                u = usuario_valido(s, c.usuario_id) if ok else None
                if u is None:
                    falhas_token.registra(quem)
                    return _erro("invalid_grant", "código, PKCE, redirect_uri ou usuário inválido")
                return JSONResponse(emite(s, cli, u), headers=_SEM_CACHE)
            if g == "refresh_token":
                r = s.get(OAuthRefresh, _h(f.get("refresh_token", "")))
                if r is None or r.client_id != cli.client_id:
                    falhas_token.registra(quem)
                    return _erro("invalid_grant", "refresh token inválido")
                if r.usado:                       # reuso: alguém copiou o token -> derruba a família toda
                    s.execute(delete(OAuthRefresh).where(OAuthRefresh.familia == r.familia))
                    return _erro("invalid_grant", "refresh token já usado; acesso revogado")
                if _utc(r.expira_em) < agora():
                    return _erro("invalid_grant", "refresh token vencido")
                if f.get("scope") and set(f["scope"].split()) - {ESCOPO}:
                    return _erro("invalid_scope", "escopo além do concedido")
                u = usuario_valido(s, r.usuario_id)
                if u is None:
                    s.execute(delete(OAuthRefresh).where(OAuthRefresh.familia == r.familia))
                    return _erro("invalid_grant", "usuário sem acesso")
                r.usado = True
                return JSONResponse(emite(s, cli, u, r.familia), headers=_SEM_CACHE)
            return _erro("unsupported_grant_type", "use authorization_code ou refresh_token")

    @app.post("/oauth/revoke")
    async def revoke(req: Request):
        if fora(req):
            return Response(status_code=404)
        f = {k: str(v) for k, v in (await req.form()).items()}
        with db() as s:
            cli = autentica_cliente(s, req, f)
            if cli is None:
                return _erro("invalid_client", "cliente não autenticado", 401)
            r = s.get(OAuthRefresh, _h(f.get("token", "")))
            if r is not None and r.client_id == cli.client_id:
                s.execute(delete(OAuthRefresh).where(OAuthRefresh.familia == r.familia))
        return Response(status_code=200, headers=_SEM_CACHE)   # RFC 7009: 200 mesmo para token desconhecido


def lista_clientes(s) -> list[OAuthCliente]:
    return list(s.scalars(select(OAuthCliente).order_by(OAuthCliente.criado_em)))


def _cab_pagina() -> dict:
    return {**_SEM_CACHE, "X-Frame-Options": "DENY",
            "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; form-action 'self' https:; frame-ancestors 'none'"}


_PAGINA = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark">
<title>Autorizar acesso · Torre Tecar</title><style>
:root{{--bg:#030c15;--tx:#f1f4f8;--mut:#9aa8b8;--bd:#2a3846;--lj:#f28c28}}
*{{box-sizing:border-box}}body{{margin:0;min-height:100vh;display:grid;place-items:center;background:var(--bg);color:var(--tx);
font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;padding:16px}}
main{{width:min(440px,100%);padding:32px 28px;border-radius:18px;background:#09111a;border:1px solid rgba(242,140,40,.6);
box-shadow:0 0 32px rgba(242,140,40,.2)}}h1{{font-size:22px;margin:0 0 12px}}p{{margin:0 0 14px;color:var(--mut)}}
strong{{color:var(--tx)}}ul{{margin:0 0 20px;padding-left:20px;color:var(--mut)}}li{{margin:4px 0}}
.acoes{{display:flex;gap:10px}}button{{flex:1;min-height:46px;border-radius:10px;font:inherit;font-weight:700;cursor:pointer}}
.ok{{background:var(--lj);border:0;color:#111}}.nao{{background:transparent;border:1px solid var(--bd);color:var(--tx)}}
button:focus-visible{{outline:3px solid #fff;outline-offset:2px}}
</style></head><body><main>{corpo}</main></body></html>"""

_CONSENTIMENTO = """<h1>Autorizar acesso à Torre Tecar</h1>
<p><strong>{cliente}</strong> ({destino}) quer consultar as bases da Torre em nome de
<strong>{nome}</strong> ({login}).</p>
<ul><li>Somente leitura: emplacamentos, CRM, licitações e preços.</li>
<li>Não cria, altera nem apaga nada na Torre.</li>
<li>Você pode revogar quando quiser (fale com o administrador da Torre).</li></ul>
<form method="post" action="/oauth/authorize">{ocultos}
<div class="acoes"><button class="nao" name="decisao" value="negar">Negar</button>
<button class="ok" name="decisao" value="permitir">Permitir leitura</button></div></form>"""
