"""Preço Fenatran: importação auditada, consulta (painel e MCP), RBAC, desativação imediata e MCP só leitura.

Os testes com a tabela real só rodam quando dados_privados/fenatran/ existe (fora do git: o repositório é público).
Os demais usam uma tabela sintética de 6 variantes.
"""
import csv
import hashlib
import io
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from precos_comerciais import fenatran as F
from server.app import fenatran as SF
from server.app.auth import hash_senha
from server.app.config import Settings
from server.app.db import Base, make_engine, make_sessionmaker
from server.app.main import create_app
from server.app.models import ComercialLote, ComercialPreco, Usuario
from mcp_torre.server import criar_app

REAL = Path(__file__).resolve().parents[1] / "dados_privados" / "fenatran"
TEM_REAL = (REAL / SF.ARQ_CSV).is_file()
SENHA = "senha-forte-123"
CODEX = "torre_" + "d" * 48
ACCEPT = {"Accept": "application/json, text/event-stream"}
CAB = list(F.COLUNAS)


def linha(fam, modelo, ano, up, var, cfg, p, arq="Prelos Actros e Axor.pdf", pag=1):
    return dict(campanha="FENATRAN_2026", familia=fam, modelo=modelo, modelo_busca=modelo.replace(" ", ""),
                ano_modelo=ano, up=up, variante=var, configuracao=cfg, preco_fabrica_5_10_centavos=p[0],
                preco_fabrica_11_15_centavos=p[1], preco_estoque_5_10_centavos=p[2], preco_estoque_11_15_centavos=p[3],
                icms_fabrica_pct_informado_usuario=7, icms_estoque_pct_informado_usuario=12,
                origem_aliquotas="informado_pelo_solicitante_pendente_validacao_fiscal", source_file=arq, source_page=pag)


SINTETICAS = [
    linha("ACTROS", "2653 S/36", "27/27", "UPI", "QVV26539881C", "6X4", (10012345, 9912345, 11000000, 10900000)),
    linha("ACTROS", "2653 S/36", "27/27", "UPI", "QVV26539929C", "6X4", (10012345, 9912345, 11000000, 10900000)),
    linha("ACTROS", "2653LS/36", "27/27", "UPJ", "QVV26539933T", "6X4", (10500000, 10400000, 11500000, 11400000)),
    linha("AXOR", "2545 S/36", "27/27", "UPI", "QVV25451048T", "6X2", (8000000, 7900000, 8800000, 8700000), pag=2),
    linha("ATEGO", "2429/48", "26/27", "UPB", "QVV24294266T", "6X2", (6000000, 5900000, 6800000, 6700000),
          "Preços Accelo e Atego.pdf", 3),
    linha("ACCELO", "917/39", "26/26", "UPF", "QVV91700195T", "4X2", (4000000, 3900000, 4500000, 4400000),
          "Preços Accelo e Atego.pdf", 1),
]


def escreve(pasta: Path, linhas, manifesto=None):
    pasta.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=CAB)
    w.writeheader()
    w.writerows(linhas)
    (pasta / SF.ARQ_CSV).write_text("﻿" + buf.getvalue(), encoding="utf-8")
    fam = {}
    for r in linhas:
        fam[r["familia"]] = fam.get(r["familia"], 0) + 1
    (pasta / SF.ARQ_MANIFESTO).write_text(json.dumps(manifesto or {"campanha": "FENATRAN_2026", "qtd_registros": len(linhas),
                                                                     "por_familia": fam}), encoding="utf-8")
    return pasta


@pytest.fixture
def amb(tmp_path):
    site = tmp_path / "site"
    site.mkdir()
    (site / "fenatran.html").write_text("<html><head></head><body>fenatran</body></html>", encoding="utf-8")
    eng = make_engine(f"sqlite:///{tmp_path / 't.db'}")
    Base.metadata.create_all(eng)
    S = make_sessionmaker(eng)
    with S() as s:
        for login, perfil in (("adm", "admin"), ("ven", "vendedor"), ("ges", "gestor"), ("sim", "simulacao")):
            s.add(Usuario(login=login, nome=login, perfil=perfil, senha_hash=hash_senha(SENHA)))
        s.commit()
    priv = tmp_path / "privado"
    cfg = Settings(site_root=site.resolve(), privado_dir=priv, cookie_secure=True)
    return {"eng": eng, "S": S, "priv": priv, "cfg": cfg, "tmp": tmp_path}


def importa(amb, linhas=SINTETICAS, **kw):
    pasta = escreve(amb["tmp"] / "imp", linhas)
    with amb["S"]() as s:
        rel = SF.importar(s, pasta, "adm", exigir_pdf=False, **kw)
        s.commit()
        SF.sincroniza(s, amb["priv"])
    return rel


def marca_conferido(amb):
    """Sem os PDFs reais, o teste marca o lote como conferido para poder publicar (a regra de publicação exige isso)."""
    with amb["S"]() as s:
        for l in s.query(ComercialLote).all():
            l.conferencia = json.dumps({"conferido": True, "divergencias": []})
        s.commit()


def status(amb, para):
    with amb["S"]() as s:
        SF.muda_status(s, para, "adm")
        s.commit()
        SF.sincroniza(s, amb["priv"])


def cliente(amb, login=None):
    c = TestClient(create_app(amb["cfg"], amb["eng"]), base_url="https://torre.test")
    if login:
        assert c.post("/login", data={"login": login, "senha": SENHA}, follow_redirects=False).status_code == 303
    return c


def snap(amb):
    return json.loads((amb["priv"] / "fenatran_2026.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- importação
def test_validacao_recusa_linhas_ruins_e_nada_e_gravado(amb):
    ruins = [dict(SINTETICAS[0]), dict(SINTETICAS[1]), dict(SINTETICAS[2])]
    ruins[0]["preco_fabrica_5_10_centavos"] = "-5"
    ruins[1]["variante"] = "QVV26539881C"                     # repetida
    ruins[2]["preco_estoque_5_10_centavos"] = "110000.00"     # decimal no lugar de centavos
    with pytest.raises(F.ErroImportacao) as e:
        importa(amb, ruins)
    rel = e.value.args[1]
    assert rel["resultado"] == "bloqueado" and {x["linha"] for x in rel["erros_por_linha"]} == {2, 3, 4}
    with amb["S"]() as s:
        assert s.query(ComercialPreco).count() == 0 and s.query(ComercialLote).count() == 0


def test_familia_ano_up_config_e_arquivo_invalidos(amb):
    r = dict(SINTETICAS[0], familia="ACTROSS", ano_modelo="2027", up="X", configuracao="6-4", source_file="outro.pdf")
    _, erros = F.valida_linhas([{k: str(v) for k, v in r.items()}])
    txt = " ".join(erros[0]["erros"])
    for trecho in ("família", "ano/modelo", "UP", "configuração", "source_file"):
        assert trecho in txt


def test_manifesto_divergente_bloqueia(amb):
    pasta = escreve(amb["tmp"] / "m", SINTETICAS, {"campanha": "FENATRAN_2026", "qtd_registros": 107,
                                                   "por_familia": {"ACCELO": 23, "ATEGO": 62, "ACTROS": 17, "AXOR": 5}})
    with amb["S"]() as s, pytest.raises(F.ErroImportacao) as e:
        SF.importar(s, pasta, "adm", exigir_pdf=False)
    assert "manifesto" in e.value.args[0]


def test_importacao_nasce_rascunho_idempotente_e_diff_exige_aceite(amb):
    rel = importa(amb)
    assert rel["resultado"] == "importado" and rel["status"] == "draft" and rel["versao"] == 1
    assert snap(amb)["precos"] == []                               # rascunho: o MCP não vê preço
    assert importa(amb)["resultado"] == "sem_mudancas"             # mesmo conteúdo: nada
    novo = [dict(r) for r in SINTETICAS]
    novo[0]["preco_fabrica_5_10_centavos"] = 10012346
    with pytest.raises(F.ErroImportacao) as e:
        importa(amb, novo)
    assert e.value.args[1]["diff"]["alteradas"][0]["variante"] == "QVV26539881C"
    marca_conferido(amb)
    status(amb, "active")
    rel = importa(amb, novo, aceitar_diff=True)
    assert rel["versao"] == 2 and rel["status"] == "draft"          # versão nova volta a rascunho
    with amb["S"]() as s:
        assert s.query(ComercialLote).count() == 2 and s.query(ComercialPreco).count() == 12   # histórico preservado


def test_dry_run_nao_grava(amb):
    pasta = escreve(amb["tmp"] / "d", SINTETICAS)
    with amb["S"]() as s:
        rel = SF.importar(s, pasta, "adm", exigir_pdf=False, dry_run=True)
        s.commit()
        assert rel["resultado"] == "dry_run_ok" and s.query(ComercialLote).count() == 0


def test_publicar_exige_lote_conferido_e_transicoes(amb):
    importa(amb)
    with amb["S"]() as s, pytest.raises(F.ErroImportacao, match="conferido"):
        SF.muda_status(s, "active", "adm")
    marca_conferido(amb)
    status(amb, "active")
    assert len(snap(amb)["precos"]) == 6
    with amb["S"]() as s, pytest.raises(F.ErroImportacao, match="não permitida"):
        SF.muda_status(s, "archived", "adm")                      # ativa precisa ser desativada antes


# ---------------------------------------------------------------- consulta (regras comerciais)
@pytest.fixture
def ativo():
    precos, erros = F.valida_linhas([{k: str(v) for k, v in r.items()} for r in SINTETICAS])
    assert not erros
    return {"campanha": {"chave": F.CHAVE, "status": "active", "versao": 1}, "precos": precos}


def test_busca_tolerante_e_prioridade(ativo):
    assert F.consultar(ativo, modelo="2653")["total_encontrado"] == 3
    assert F.consultar(ativo, modelo="Actros 2653")["filtros_aplicados"]["familia_interpretada"] == "ACTROS"
    r = F.consultar(ativo, modelo="2653 ls/36")
    assert r["criterio"] == "modelo_completo" and [x["variante"] for x in r["resultados"]] == ["QVV26539933T"]
    assert F.consultar(ativo, modelo="2653LS/36")["total_encontrado"] == 1
    assert F.consultar(ativo, modelo="qvv26539881c")["criterio"] == "variante_exata"
    assert F.consultar(ativo, modelo="2653", up="j")["total_encontrado"] == 1
    assert F.consultar(ativo, ano_modelo="2027/2027")["total_encontrado"] == 4
    assert F.consultar(ativo, configuracao="6x2")["total_encontrado"] == 2


def test_variantes_com_mesmo_preco_sao_sinalizadas_e_nenhuma_e_escolhida(ativo):
    r = F.consultar(ativo, modelo="2653 S/36")
    assert r["total_encontrado"] == 2
    assert r["duplicidades_de_preco"][0]["variantes"] == ["QVV26539881C", "QVV26539929C"]


@pytest.mark.parametrize("qtd,ok,faixa_cent", [(None, True, None), (4, False, None), (5, True, 10012345),
                                               (10, True, 10012345), (11, True, 9912345), (15, True, 9912345),
                                               (16, False, None), (0, False, None)])
def test_quantidades(ativo, qtd, ok, faixa_cent):
    r = F.consultar(ativo, variante="QVV26539881C", quantidade=qtd)
    it = r["resultados"][0]
    if not ok:
        assert r["status_consulta"] == "quantidade_fora_condicao_fenatran" and "precos" not in it
        assert "faixa_aplicavel" not in it
    else:
        assert r["status_consulta"] == "ok" and "precos" in it
        assert (it.get("faixa_aplicavel") or {}).get("fabrica", {}).get("unitario_centavos") == faixa_cent
        assert "total_centavos" not in json.dumps(it)              # total só quando pedido


def test_total_so_quando_pedido_e_origem(ativo):
    r = F.consultar(ativo, variante="QVV26539881C", quantidade=11, calcular_total=True, origem="estoque")
    fx = r["resultados"][0]["faixa_aplicavel"]
    assert "fabrica" not in fx and fx["estoque"]["total_centavos"] == 10900000 * 11
    assert set(r["resultados"][0]["precos"]) == {"estoque"}
    assert F.consultar(ativo, modelo="2653", origem="todos")["status_consulta"] == "filtro_invalido"


def test_condicoes_actros_axor_nao_vazam_para_outras_familias(ativo):
    c = F.consultar(ativo, modelo="2429")["condicoes_comerciais"]
    assert c["por_familia"] == {}
    c = F.consultar(ativo, modelo="2653", agora=datetime(2026, 11, 9, tzinfo=F.TZ))["condicoes_comerciais"]
    assert c["por_familia"]["ACTROS"]["prazo_programacao_vencido"] is False and "fevereiro" in c["por_familia"]["ACTROS"]["texto"]
    c = F.consultar(ativo, modelo="2653", agora=datetime(2026, 12, 1, tzinfo=F.TZ))["condicoes_comerciais"]
    assert c["por_familia"]["ACTROS"]["prazo_programacao_vencido"] is True and "validar" in c["por_familia"]["ACTROS"]["alerta"]
    r = F.consultar(ativo, modelo="2653", agora=datetime(2027, 3, 1, tzinfo=F.TZ))
    assert r["status_consulta"] == "ok"                            # o prazo NÃO desliga a campanha


def test_inativa_expirada_e_filtro_obrigatorio(ativo):
    for st in ("draft", "inactive", "archived"):
        r = F.consultar({**ativo, "campanha": {**ativo["campanha"], "status": st}}, modelo="2653")
        assert r["status_consulta"] == "campanha_inativa" and r["resultados"] == [] and "10012345" not in json.dumps(r)
    exp = {**ativo, "campanha": {**ativo["campanha"], "expira_em": (F.agora_sp() - timedelta(minutes=1)).isoformat()}}
    assert F.consultar(exp, modelo="2653")["status"] == "expirada"
    assert F.consultar(None, modelo="2653")["status_consulta"] == "campanha_inativa"
    assert F.consultar(ativo)["status_consulta"] == "filtro_obrigatorio"
    assert F.consultar(ativo, listar_todos=True, limite=2)["proxima_pagina"] == 2


def test_resposta_tem_campos_do_contrato(ativo):
    r = F.consultar(ativo, modelo="2653")
    for k in ("fonte", "campanha", "versao", "status", "consultado_em", "filtros_aplicados", "total_encontrado",
              "resultados_exibidos", "resultados", "condicoes_comerciais", "restricoes", "aviso_uso_interno"):
        assert k in r, k
    assert r["consultado_em"].endswith("-03:00")
    it = r["resultados"][0]
    for k in ("familia", "modelo", "ano_modelo", "up", "variante", "configuracao", "source_file", "source_page",
              "status_validacao_fiscal"):
        assert k in it
    assert it["precos"]["fabrica"]["rotulo"].startswith("Fábrica — ICMS 7%")
    assert "solicitante" in " ".join(r["restricoes"])


# ---------------------------------------------------------------- painel e RBAC
def test_rbac_e_desativacao_imediata_no_painel(amb):
    importa(amb)
    marca_conferido(amb)
    assert cliente(amb).get("/api/fenatran/consulta?modelo=2653").status_code == 401
    assert cliente(amb, "sim").get("/api/fenatran/consulta?modelo=2653").status_code == 403
    ven = cliente(amb, "ven")
    assert ven.get("/api/fenatran/consulta?modelo=2653").json()["status_consulta"] == "campanha_inativa"   # rascunho
    adm = cliente(amb, "adm")
    previa = adm.get("/api/fenatran/consulta?modelo=2653").json()
    assert previa["previa_rascunho"] and previa["total_encontrado"] == 3          # admin confere antes de publicar
    h = {"X-Torre-Acao": "1", "Origin": "https://torre.test"}
    assert ven.post("/api/admin/fenatran/status", json={"status": "active"}, headers=h).status_code == 403
    assert adm.post("/api/admin/fenatran/status", json={"status": "active"}).status_code == 403          # sem cabeçalho
    assert adm.post("/api/admin/fenatran/status", json={"status": "active"},
                    headers={"X-Torre-Acao": "1", "Origin": "https://evil.test"}).status_code == 403
    assert adm.post("/api/admin/fenatran/status", json={"status": "active", "motivo": "ok"}, headers=h).json()["status"] == "active"
    r = ven.get("/api/fenatran/consulta?modelo=2653&quantidade=11").json()
    assert r["total_encontrado"] == 3 and r["resultados"][0]["faixa_aplicavel"]["fabrica"]["unitario"]
    assert len(snap(amb)["precos"]) == 6
    assert adm.post("/api/admin/fenatran/status", json={"status": "inactive"}, headers=h).status_code == 200
    assert ven.get("/api/fenatran/consulta?modelo=2653").json()["status_consulta"] == "campanha_inativa"
    assert snap(amb)["precos"] == []
    painel = adm.get("/api/admin/fenatran").json()
    assert [e["acao"] for e in painel["eventos"]][:3] == ["desativacao", "ativacao", "importacao"]
    assert ven.get("/api/admin/fenatran").status_code == 403
    assert ven.get("/fenatran.html").status_code == 200


def test_expiracao_opcional_definida_pelo_admin(amb):
    importa(amb)
    marca_conferido(amb)
    status(amb, "active")
    adm = cliente(amb, "adm")
    h = {"X-Torre-Acao": "1"}
    passado = (F.agora_sp() - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
    assert adm.post("/api/admin/fenatran/expiracao", json={"expira_em": passado}, headers=h).status_code == 200
    assert cliente(amb, "ven").get("/api/fenatran/consulta?modelo=2653").json()["status"] == "expirada"
    assert adm.post("/api/admin/fenatran/expiracao", json={"expira_em": None}, headers=h).json()["expira_em"] is None
    assert cliente(amb, "ven").get("/api/fenatran/consulta?modelo=2653").json()["status_consulta"] == "ok"


def test_logs_nao_carregam_precos(amb, caplog):
    importa(amb)
    marca_conferido(amb)
    status(amb, "active")
    with caplog.at_level(logging.INFO):
        cliente(amb, "ven").get("/api/fenatran/consulta?variante=QVV26539881C")
    assert "100123" not in caplog.text and "10012345" not in caplog.text


# ---------------------------------------------------------------- MCP
def mcp_app(raiz, priv):
    a = criar_app(Path(raiz), {hashlib.sha256(CODEX.encode()).hexdigest()}, ["mcp.test"], privado=priv)
    return TestClient(a, base_url="https://mcp.test")


def rpc(c, nome, args, token=CODEX):
    h = {**ACCEPT, **({"Authorization": f"Bearer {token}"} if token else {})}
    return c.post("/mcp", headers=h, json={"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                                            "params": {"name": nome, "arguments": args}})


def sc(m, args, token=CODEX):
    return rpc(m, "consultar_precos_fenatran", args, token).json()["result"]["structuredContent"]


def test_mcp_consulta_respeita_status_e_continua_somente_leitura(amb):
    importa(amb)
    marca_conferido(amb)
    with mcp_app(amb["tmp"], amb["priv"]) as m:
        r = sc(m, {"modelo": "2653", "quantidade": 5})
        assert r["status_consulta"] == "campanha_inativa" and r["resultados"] == []          # Teste E: rascunho
        status(amb, "active")
        r = sc(m, {"modelo": "Actros 2653", "quantidade": 11})
        assert r["status_consulta"] == "ok" and r["faixa_aplicada"] == "11-15" and r["total_encontrado"] == 3
        r = sc(m, {"modelo": "QVV26539881C", "quantidade": 5})
        p = r["resultados"][0]["precos"]
        assert p["fabrica"] == {"unitario": "100123.45", "unitario_brl": "R$ 100.123,45",
                                "total_lote": "500617.25", "total_lote_brl": "R$ 500.617,25"}
        assert p["estoque_ci102"]["unitario"] == "110000.00" and p["estoque_ci102"]["total_lote"] == "550000.00"
        assert r["fonte"] == "FENATRAN" and r["status"] == "ativo" and r["versao_tabela"] == 1
        assert r["resultados"][0]["fonte_documental"] and r["resultados"][0]["pagina"] == 1
        status(amb, "inactive")
        r = sc(m, {"modelo": "QVV26539881C", "quantidade": 5})
        assert r["status_consulta"] == "campanha_inativa" and "100123" not in json.dumps(r)      # efeito imediato
        assert rpc(m, "consultar_precos_fenatran", {"modelo": "2653", "quantidade": 5}, token=None).status_code == 401
        assert rpc(m, "consultar_precos_fenatran", {"modelo": "2653", "quantidade": 5},
                   token="torre_" + "0" * 48).status_code == 401                               # Teste F
        tools = m.post("/mcp", headers={**ACCEPT, "Authorization": f"Bearer {CODEX}"},
                       json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"}).json()["result"]["tools"]
        t = next(x for x in tools if x["name"] == "consultar_precos_fenatran")
        assert t["annotations"]["readOnlyHint"] is True and t["annotations"]["destructiveHint"] is False
        assert set(t["inputSchema"]["required"]) == {"modelo", "quantidade"}
        assert t["inputSchema"]["properties"]["modalidade"]["enum"] == ["fabrica", "estoque_ci102", "concessionario", "todas"]
        assert "Fenatran" in t["description"] and "ASSOBENS" in t["description"]             # Teste G: roteamento
        pr = next(x for x in tools if x["name"] == "precos")
        assert "Fenatran" not in pr["description"]
        nomes = {x["name"] for x in tools}
        assert "precos" in nomes and not any(n for n in nomes if any(v in n for v in ("importar", "ativar", "desativar",
                                                                                       "apagar", "editar", "gravar")))
    with amb["S"]() as s:                                          # o MCP não tocou no banco
        assert s.query(ComercialLote).count() == 1


def test_mcp_faixas_versoes_e_quantidade(amb):
    importa(amb)
    marca_conferido(amb)
    status(amb, "active")
    with mcp_app(amb["tmp"], amb["priv"]) as m:
        r = sc(m, {"modelo": "2653 LS e S", "quantidade": 5})                              # várias versões
        assert {x["modelo"] for x in r["resultados"]} == {"2653LS/36", "2653 S/36"} or len(r["resultados"]) == 3
        r = sc(m, {"modelo": "2653", "versao": "LS", "quantidade": 5})
        assert [x["qvv"] for x in r["resultados"]] == ["QVV26539933T"]
        r = sc(m, {"modelo": "QVV26539881C", "quantidade": 12})                             # Teste C
        assert r["faixa_aplicada"] == "11-15"
        assert r["resultados"][0]["precos"]["fabrica"]["unitario"] == "99123.45"
        assert r["resultados"][0]["precos"]["fabrica"]["total_lote"] == "1189481.40"
        for q in (4, 16, 0):                                                                # Teste D
            r = sc(m, {"modelo": "2653", "quantidade": q})
            assert r["status_consulta"] == "quantidade_fora_condicao_fenatran" and r["resultados"] == []
        r = sc(m, {"modelo": "2653", "quantidade": 5, "modalidade": "estoque_ci102"})
        assert all(set(x["precos"]) == {"estoque_ci102"} for x in r["resultados"])
        r = sc(m, {"modelo": "9999", "quantidade": 5})
        assert r["status_consulta"] == "sem_resultados" and r["status"] == "ativo"


def test_mcp_sem_snapshot_ou_corrompido_e_falha_de_fonte(amb):                             # Teste I
    with mcp_app(amb["tmp"], amb["tmp"] / "vazio") as m:
        r = sc(m, {"modelo": "2653", "quantidade": 5})
        assert r["status_consulta"] == "fonte_indisponivel" and "não ausência do modelo" in r["mensagem"]
    ruim = amb["tmp"] / "corrompido"
    ruim.mkdir()
    (ruim / "fenatran_2026.json").write_text("{quebrado", encoding="utf-8")
    with mcp_app(amb["tmp"], ruim) as m:
        r = sc(m, {"modelo": "2653", "quantidade": 5})
        assert r["status_consulta"] == "fonte_indisponivel" and r["resultados"] == []


# ---------------------------------------------------------------- tabela real (só com os arquivos privados)
@pytest.mark.skipif(not TEM_REAL, reason="dados_privados/fenatran ausente (fora do git)")
def test_tabela_real_107_conferida_com_os_pdfs(amb):
    with amb["S"]() as s:
        rel = SF.importar(s, REAL, "adm")
        s.commit()
        SF.muda_status(s, "active", "adm")
        s.commit()
        snap_ = SF.monta_snapshot(s)
    assert rel["linhas_validas"] == 107 and rel["por_familia"] == {"ACCELO": 23, "ATEGO": 62, "ACTROS": 17, "AXOR": 5}
    assert rel["conferencia_pdf"]["conferido"] and rel["conferencia_pdf"]["divergencias"] == []
    assert all(d["sha256_confere"] for d in rel["documentos"].values())
    assert len({p["variante"] for p in snap_["precos"]}) == 107
    for v in ("QVV31330849T", "QVV31330851T"):                     # página 5, recuperadas na inspeção visual
        p = next(x for x in snap_["precos"] if x["variante"] == v)
        assert p["source_page"] == 5 and p["familia"] == "ATEGO"
    assert sum(p["familia"] == "AXOR" for p in snap_["precos"]) == 5          # nada duplicado do Axor na página 5
    r = F.consultar(snap_, modelo="2653")
    assert sorted(x["variante"] for x in r["resultados"]) == ["QVV26539881C", "QVV26539929C", "QVV26539931C", "QVV26539933T"]
    assert F.consultar(snap_, modelo="2548")["total_encontrado"] == 5
    assert F.consultar(snap_, modelo="2548 S/36")["total_encontrado"] == 2
    p = F.consultar(snap_, variante="QVV26539881C")["resultados"][0]["precos"]
    import csv                                                    # valores esperados vêm do CSV privado, nunca do git
    with open(REAL / "fenatran_precos_importacao.csv", encoding="utf-8-sig") as fh:
        row = next(x for x in csv.DictReader(fh) if x["variante"] == "QVV26539881C")
    assert (p["fabrica"]["5_10"]["centavos"], p["fabrica"]["11_15"]["centavos"], p["estoque"]["5_10"]["centavos"],
            p["estoque"]["11_15"]["centavos"]) == tuple(int(row[c]) for c in F.PRECOS)


@pytest.mark.skipif(not TEM_REAL, reason="dados_privados/fenatran ausente (fora do git)")
def test_real_axor_2545_ls_e_s_para_5_unidades():                                       # Testes A e B
    import csv
    with open(REAL / "fenatran_precos_importacao.csv", encoding="utf-8-sig") as fh:
        linhas = list(csv.DictReader(fh))
    precos, erros = F.valida_linhas(linhas)
    assert not erros
    snap_ = {"campanha": {"status": "active", "versao": 1}, "precos": precos}
    r = F.consultar_mcp(snap_, modelo="Axor 2545 LS e S", quantidade=5)
    assert r["status_consulta"] == "ok" and r["faixa_aplicada"] == "5-10"
    assert {x["modelo"] for x in r["resultados"]} == {"2545 LS/36", "2545 S/36"}
    for x in r["resultados"]:                                    # esperado vem do CSV privado, nunca de constante no git
        row = next(l for l in linhas if l["variante"] == x["qvv"])
        fab, est = int(row["preco_fabrica_5_10_centavos"]), int(row["preco_estoque_5_10_centavos"])
        assert x["precos"]["fabrica"]["unitario"] == f"{fab // 100}.{fab % 100:02d}"
        assert x["precos"]["fabrica"]["total_lote"] == f"{fab * 5 // 100}.{fab * 5 % 100:02d}"
        assert x["precos"]["estoque_ci102"]["unitario"] == f"{est // 100}.{est % 100:02d}"
        assert x["fonte_documental"] == row["source_file"] and x["pagina"] == int(row["source_page"])
    r12 = F.consultar_mcp(snap_, modelo="2545", quantidade=12)                              # Teste C, dados reais
    for x in r12["resultados"]:
        row = next(l for l in linhas if l["variante"] == x["qvv"])
        c = int(row["preco_fabrica_11_15_centavos"])
        assert x["precos"]["fabrica"]["unitario"] == f"{c // 100}.{c % 100:02d}"


def test_mcp_modalidades_icms_e_alternativas(amb):                                    # Testes 01–06
    importa(amb)
    marca_conferido(amb)
    status(amb, "active")
    with mcp_app(amb["tmp"], amb["priv"]) as m:
        r = sc(m, {"modelo": "Actros 2653 S", "quantidade": 15, "modalidade": "todas", "icms": 12, "uf": "go"})
        assert r["status_consulta"] == "ok" and r["faixa_aplicada"] == "11-15"
        assert {x["qvv"] for x in r["resultados"]} == {"QVV26539881C", "QVV26539929C"}
        p = r["resultados"][0]["precos"]
        assert p["fabrica"]["unitario"] == "99123.45" and p["fabrica"]["total_lote"] == "1486851.75"
        assert p["estoque_ci102"]["unitario"] == "109000.00" and p["estoque_ci102"]["total_lote"] == "1635000.00"
        assert p["concessionario"]["status"] == "indisponivel" and "unitario" not in p["concessionario"]
        t = r["condicoes_tributarias"]
        assert t["icms_fabrica_pct"] == 7 and t["icms_estoque_ci102_pct"] == 12 and "aviso_icms" not in t
        assert t["uf_informada"] == "GO" and "aviso_uf" in t
        r = sc(m, {"modelo": "2653", "quantidade": 5, "modalidade": "fabrica", "icms": 18})
        assert all(set(x["precos"]) == {"fabrica"} for x in r["resultados"])
        assert "aviso_icms" in r["condicoes_tributarias"]
        r = sc(m, {"modelo": "Actros 2699", "quantidade": 5})
        assert r["status_consulta"] == "sem_resultados" and "2653 S/36" in " ".join(r["alternativas_cadastradas"])
        assert "precos" not in json.dumps(r["alternativas_cadastradas"])
        r = rpc(m, "consultar_precos_fenatran", {"modelo": "2653", "quantidade": 5, "modalidade": "desconto"}).json()
        assert r["result"]["isError"] is True and "100123" not in json.dumps(r)          # enum barrado no esquema
