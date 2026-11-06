"""Servidor da Torre (Fase 1): login no servidor, lista fechada de arquivos, perfis, host público e leads."""
import io
import json
from datetime import timedelta

import pytest

# As rotinas (ASSOBENS, licitações) rodam no CI só com requirements-assobens.txt; o servidor tem os seus próprios.
pytest.importorskip("fastapi", reason="dependências do servidor (server/requirements.txt) não instaladas")
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import update

from server.app import cli
from server.app.auth import hash_senha
from server.app.config import Settings
from server.app.db import Base, make_engine, make_sessionmaker
from server.app.main import create_app
from server.app.models import Lead, Sessao, Usuario, agora

SENHA = "senha-forte-123"


@pytest.fixture
def ambiente(tmp_path):
    site = tmp_path / "site"
    (site / "Analityc share" / "assobens").mkdir(parents=True)
    (site / "ASSETS").mkdir()
    (site / "Analitycmbb.html").write_text("<!doctype html><html><head><title>T</title></head><body>torre</body></html>", encoding="utf-8")
    (site / "simule.html").write_text("<html><head></head><body>simule</body></html>", encoding="utf-8")
    (site / "Analityc share" / "consolidado_emplacamentos_2020_2026.xlsx").write_bytes(b"PK-matriz")
    (site / "Analityc share" / "assobens" / "status.json").write_text('{"status":"ok"}', encoding="utf-8")
    (site / "Analityc share" / "EMPLACAMENTO - ANALISE PERFIL CLIENTES.xlsx").write_bytes(b"privado")
    (site / "relatorio-avulso.html").write_text("<html><head></head>avulso</html>", encoding="utf-8")
    (site / "ASSETS" / "grupo-tecar-squarelogo-1553565271092.webp").write_bytes(b"img")
    (tmp_path / "fora.html").write_text("<html><head></head>fora</html>", encoding="utf-8")

    engine = make_engine(f"sqlite:///{tmp_path / 'torre.db'}")
    Base.metadata.create_all(engine)
    S = make_sessionmaker(engine)
    with S() as db:
        db.add_all([Usuario(login="admin", nome="Admin", perfil="admin", senha_hash=hash_senha(SENHA)),
                    Usuario(login="sim", nome="Sim", perfil="simulacao", senha_hash=hash_senha(SENHA)),
                    Usuario(login="inativo", perfil="admin", senha_hash=hash_senha(SENHA), ativo=False)])
        db.commit()
    app = create_app(Settings(site_root=site.resolve()), engine)
    return app, S, engine


def cliente(app, host="torre.test"):
    return TestClient(app, base_url=f"https://{host}", follow_redirects=False)


def entra(c, login="admin", senha=SENHA, next_="/"):
    return c.post("/login", data={"login": login, "senha": senha, "next": next_})


def test_sem_login_paginas_redirecionam_e_dados_recusam(ambiente):
    c = cliente(ambiente[0])
    r = c.get("/Analitycmbb.html")
    assert r.status_code == 303 and r.headers["location"] == "/login?next=/Analitycmbb.html"
    assert c.get("/Analityc share/consolidado_emplacamentos_2020_2026.xlsx").status_code == 401
    assert c.get("/api/me").status_code == 401
    assert c.get("/api/leads").status_code == 401
    assert c.get("/login").status_code == 200


def test_fundo_do_login_abre_sem_sessao_e_so_ele(ambiente):
    app = ambiente[0]
    site = app.state.settings.site_root
    (site / "ASSETS" / "login-fundo.webp").write_bytes(b"arte")
    (site / "ASSETS" / "hero-actros.jpg").write_bytes(b"outra")
    c = cliente(app)
    r = c.get("/ASSETS/login-fundo.webp")
    assert r.status_code == 200 and r.content == b"arte"
    assert "/ASSETS/login-fundo.webp" in c.get("/login").text
    assert c.get("/ASSETS/hero-actros.jpg").status_code == 401  # o resto dos assets segue exigindo login
    assert cliente(app, "simule.test").get("/ASSETS/login-fundo.webp").status_code == 404


def test_so_arquivos_da_lista_saem_mesmo_logado(ambiente):
    c = cliente(ambiente[0])
    assert entra(c).status_code == 303
    assert c.get("/relatorio-avulso.html").status_code == 404
    assert c.get("/Analityc share/EMPLACAMENTO - ANALISE PERFIL CLIENTES.xlsx").status_code == 404
    assert c.get("/../fora.html").status_code == 404
    assert c.get("/Analityc share/../fora.html").status_code == 404
    assert c.get("/server/app/config.py").status_code == 404
    assert c.get("/deploy/.env").status_code == 404


def test_login_cria_sessao_segura_e_injeta_perfil(ambiente):
    c = cliente(ambiente[0])
    r = entra(c, next_="/Analitycmbb.html")
    assert r.status_code == 303 and r.headers["location"] == "/Analitycmbb.html"
    ck = r.headers["set-cookie"].lower()
    assert "httponly" in ck and "secure" in ck and "samesite=lax" in ck
    html = c.get("/Analitycmbb.html").text
    assert html.index("<head>") < html.index("window.TORRE_SERVER") < html.index("<title>")
    assert '"perfil": "all"' in html and '"usuario": "admin"' in html
    assert c.get("/Analityc share/consolidado_emplacamentos_2020_2026.xlsx").content == b"PK-matriz"
    assert c.get("/api/me").json()["perfil_front"] == "all"
    assert c.get("/").headers["location"] == "/Analitycmbb.html"


def test_senha_errada_inativo_e_bloqueio_por_tentativas(ambiente):
    c = cliente(ambiente[0])
    assert entra(c, senha="errada-errada").status_code == 401
    assert entra(c, login="inativo").status_code == 401
    assert entra(c, login="naoexiste").status_code == 401
    for _ in range(4):
        entra(c, senha="errada-errada")
    r = entra(c)  # 5 falhas: mesmo a senha certa fica bloqueada
    assert r.status_code == 429 and "set-cookie" not in r.headers


def test_next_externo_vira_raiz(ambiente):
    c = cliente(ambiente[0])
    assert entra(c, next_="//malicioso.example/x").headers["location"] == "/"
    assert entra(c, next_="https://malicioso.example").headers["location"] == "/"


def test_perfil_simulacao_nao_ve_dados_nem_leads(ambiente):
    c = cliente(ambiente[0])
    entra(c, login="sim")
    assert '"perfil": "sim"' in c.get("/Analitycmbb.html").text
    assert c.get("/Analityc share/consolidado_emplacamentos_2020_2026.xlsx").status_code == 403
    assert c.get("/Analityc share/assobens/status.json").status_code == 403
    assert c.get("/api/leads").status_code == 403


def test_logout_e_sessao_expirada(ambiente):
    app, S, engine = ambiente
    c = cliente(app)
    entra(c)
    assert c.get("/logout").headers["location"] == "/login"
    assert c.get("/Analitycmbb.html").status_code == 303

    entra(c)
    with S() as db:
        db.execute(update(Sessao).values(expira_em=agora() - timedelta(minutes=1)))
        db.commit()
    assert c.get("/api/me").status_code == 401


def test_host_publico_so_simulador_e_post_de_leads(ambiente):
    app, S, _ = ambiente
    pub = cliente(app, "simule.test")
    r = pub.get("/")
    assert r.status_code == 200 and "simule" in r.text and '"publico": true' in r.text
    assert pub.get("/ASSETS/grupo-tecar-squarelogo-1553565271092.webp").status_code == 200
    for caminho in ("/Analitycmbb.html", "/login", "/Analityc share/consolidado_emplacamentos_2020_2026.xlsx", "/api/leads"):
        assert pub.get(caminho).status_code == 404, caminho

    lead = {"codigo": "TCO-1", "nome": "Fulano", "telefone": "62999990000", "email": "", "empresa": "Transp X",
            "autoriza_contato": True, "mb": "Actros 2651", "resultado": {"economia": 123}}
    assert pub.post("/api/leads", content=json.dumps(lead), headers={"content-type": "text/plain"}).json() == {"ok": True}
    assert pub.post("/api/leads", content='{"nome":""}').status_code == 422
    assert pub.post("/api/leads", content="não é json").status_code == 400
    assert pub.post("/api/leads", content="x" * 40_000).status_code == 413
    with S() as db:
        assert db.query(Lead).count() == 1

    c = cliente(app)
    entra(c)
    assert c.get("/api/leads").json()["leads"][0]["resultado"] == {"economia": 123}


def test_limite_de_leads_por_ip(ambiente):
    pub = cliente(ambiente[0], "simule.test")
    ok = [pub.post("/api/leads", content='{"nome":"A","telefone":"1"}').status_code for _ in range(11)]
    assert ok[:10] == [200] * 10 and ok[10] == 429


def test_cli_cria_e_desativa_usuario(ambiente, monkeypatch, capsys):
    app, S, engine = ambiente
    monkeypatch.setattr("sys.stdin", io.StringIO("outra-senha-forte\n"))
    assert cli.main(["criar", "--login", "Matheus", "--perfil", "gestor", "--senha-stdin"], engine=engine) == 0
    c = cliente(app)
    assert entra(c, login="matheus", senha="outra-senha-forte").status_code == 303
    assert cli.main(["desativar", "--login", "matheus"], engine=engine) == 0
    assert c.get("/api/me").status_code == 401  # desativar encerra as sessões
    monkeypatch.setattr("sys.stdin", io.StringIO("curta\n"))
    with pytest.raises(ValueError):
        cli.main(["criar", "--login", "x", "--perfil", "admin", "--senha-stdin"], engine=engine)
