"""API da Torre Tecar (Fase 1): login no servidor, páginas protegidas e leads do simulador.

Dois nomes chegam pelo proxy:
  - torre.<dominio>   painel interno, tudo exige sessão;
  - simule.<dominio>  simulador público: só simule.html, seus recursos e POST /api/leads.
"""
from __future__ import annotations

import json
from contextlib import contextmanager
from urllib.parse import quote

from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, Response
from sqlalchemy import select, text

from . import oauth, site
from .auth import Limitador, autentica, cria_sessao, encerra_sessao, usuario_da_sessao
from .config import PERFIL_FRONT, Settings, load_settings
from .db import make_engine, make_sessionmaker
from .models import Lead
from .paginas import pagina_login

MAX_LEAD_BYTES = 32_000


def create_app(settings: Settings | None = None, engine=None) -> FastAPI:
    cfg = settings or load_settings()
    engine = engine or make_engine(cfg.database_url)
    Sessions = make_sessionmaker(engine)
    falhas_login = Limitador(cfg.login_max_falhas, cfg.login_bloqueio_min * 60)
    leads_ip = Limitador(cfg.leads_por_hora_ip, 3600)
    app = FastAPI(title="Torre Tecar", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.settings, app.state.engine = cfg, engine

    @contextmanager
    def db():
        s = Sessions()
        try:
            yield s
            s.commit()
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()

    def ip(req: Request) -> str:
        return req.client.host if req.client else ""

    def host_publico(req: Request) -> bool:
        return req.headers.get("host", "").lower().startswith(cfg.public_host_prefix)

    def usuario(req: Request):
        with db() as s:
            return usuario_da_sessao(s, req.cookies.get(cfg.cookie_name))

    def para_login(req: Request) -> RedirectResponse:
        alvo = req.url.path + (("?" + req.url.query) if req.url.query else "")
        return RedirectResponse("/login?next=" + quote(alvo, safe="/"), status_code=303)

    def destino_seguro(n: str | None) -> str:
        return n if n and n.startswith("/") and not n.startswith("//") and "\\" not in n else "/"

    @app.middleware("http")
    async def cabecalhos(req: Request, call_next):
        resp = await call_next(req)
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        return resp

    # ---------- saúde ----------
    @app.get("/api/health")
    def health():
        with engine.connect() as c:
            c.execute(text("select 1"))
        return {"ok": True}

    # ---------- login ----------
    @app.get("/login", response_class=HTMLResponse)
    def login_form(req: Request, next: str = "/"):
        if host_publico(req):
            return Response(status_code=404)
        return HTMLResponse(pagina_login(destino_seguro(next)))

    @app.post("/login")
    def login(req: Request, login: str = Form(""), senha: str = Form(""), next: str = Form("/")):
        if host_publico(req):
            return Response(status_code=404)
        chave = f"{ip(req)}|{login.strip().lower()}"
        if falhas_login.bloqueado(chave):
            return HTMLResponse(pagina_login(destino_seguro(next), "Muitas tentativas. Aguarde alguns minutos.", login), status_code=429)
        with db() as s:
            u = autentica(s, login, senha)
            if u is None:
                falhas_login.registra(chave)
                return HTMLResponse(pagina_login(destino_seguro(next), "Usuário ou senha inválidos.", login), status_code=401)
            token = cria_sessao(s, u, cfg.session_hours, ip(req), req.headers.get("user-agent", ""))
        falhas_login.limpa(chave)
        resp = RedirectResponse(destino_seguro(next), status_code=303)
        resp.set_cookie(cfg.cookie_name, token, max_age=cfg.session_hours * 3600, httponly=True,
                        secure=cfg.cookie_secure, samesite="lax", path="/")
        return resp

    @app.api_route("/logout", methods=["GET", "POST"])
    def logout(req: Request):
        with db() as s:
            encerra_sessao(s, req.cookies.get(cfg.cookie_name))
        resp = RedirectResponse("/login", status_code=303)
        resp.delete_cookie(cfg.cookie_name, path="/")
        return resp

    @app.get("/api/me")
    def me(req: Request):
        u = usuario(req)
        if u is None:
            return JSONResponse({"erro": "não autenticado"}, status_code=401)
        return {"login": u.login, "nome": u.nome, "perfil": u.perfil, "perfil_front": PERFIL_FRONT.get(u.perfil, "sim")}

    # ---------- leads do simulador ----------
    @app.post("/api/leads")
    async def recebe_lead(req: Request):
        quem = ip(req)
        if leads_ip.bloqueado(quem):
            return JSONResponse({"ok": False, "erro": "limite de envios"}, status_code=429)
        corpo = await req.body()
        if len(corpo) > MAX_LEAD_BYTES:
            return JSONResponse({"ok": False, "erro": "grande demais"}, status_code=413)
        try:
            p = json.loads(corpo or b"{}")
        except ValueError:
            return JSONResponse({"ok": False, "erro": "json inválido"}, status_code=400)
        if not isinstance(p, dict) or not str(p.get("nome", "")).strip() or not (str(p.get("telefone", "")).strip() or str(p.get("email", "")).strip()):
            return JSONResponse({"ok": False, "erro": "nome e telefone ou e-mail são obrigatórios"}, status_code=422)
        leads_ip.registra(quem)
        txt = lambda k, n: str(p.get(k) or "")[:n]  # noqa: E731
        with db() as s:
            s.add(Lead(codigo=txt("codigo", 40), nome=txt("nome", 160), telefone=txt("telefone", 40), email=txt("email", 160),
                       empresa=txt("empresa", 160), autoriza_contato=bool(p.get("autoriza_contato")),
                       payload=json.dumps(p, ensure_ascii=False), ip=quem))
        return {"ok": True}

    @app.get("/api/leads")
    def lista_leads(req: Request):
        if host_publico(req):
            return Response(status_code=404)
        u = usuario(req)
        if u is None:
            return JSONResponse({"erro": "não autenticado"}, status_code=401)
        if u.perfil == "simulacao":
            return JSONResponse({"erro": "sem permissão"}, status_code=403)
        with db() as s:
            rows = s.scalars(select(Lead).order_by(Lead.recebido_em.desc()).limit(2000)).all()
            return {"leads": [json.loads(r.payload) for r in rows]}

    # ---------- OAuth 2.1 do MCP somente leitura (antes da rota genérica de arquivos) ----------
    oauth.registrar(app, cfg, db, usuario, para_login, host_publico, ip)

    # ---------- páginas e dados ----------
    def entrega(path, rel: str, marcador: dict) -> Response:
        if rel.lower().endswith(".html"):
            return Response(site.html_com_marcador(path, marcador), media_type="text/html; charset=utf-8",
                            headers={"Cache-Control": "no-cache"})
        return FileResponse(path, headers={"Cache-Control": "no-cache"})

    @app.get("/")
    def raiz(req: Request):
        if host_publico(req):
            return arquivo(req, "simule.html")
        return RedirectResponse("/Analitycmbb.html", status_code=303)

    @app.get("/{rel:path}")
    def arquivo(req: Request, rel: str):
        if host_publico(req):
            p = site.resolve(cfg.site_root, rel) if site.publico(rel) else None
            return entrega(p, rel, {"publico": True}) if p else Response(status_code=404)
        if site.recurso_do_login(rel):
            p = site.resolve(cfg.site_root, rel)
            return FileResponse(p, headers={"Cache-Control": "public, max-age=86400"}) if p else Response(status_code=404)
        tipo = site.classifica(rel)
        p = site.resolve(cfg.site_root, rel) if tipo else None
        if p is None:
            return Response(status_code=404)
        u = usuario(req)
        if u is None:
            return para_login(req) if rel.lower().endswith(".html") else Response(status_code=401)
        if tipo == "dados" and u.perfil == "simulacao":
            return Response(status_code=403)
        return entrega(p, rel, {"perfil": PERFIL_FRONT.get(u.perfil, "sim"), "usuario": u.login, "nome": u.nome})

    return app

