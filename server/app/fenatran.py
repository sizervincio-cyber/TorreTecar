"""Preço Fenatran na Torre: importação auditada, status administrado, snapshot para o MCP e rotas do painel.

Fluxo:
  1. Importação (só pela linha de comando do contêiner da API, nunca pelo MCP nem por API pública):
       python -m server.app.fenatran importar --pasta /srv/importacao/fenatran --responsavel <login> [--dry-run]
     Valida o CSV linha a linha, confere contagens com o manifesto, SHA-256 e conteúdo com os PDFs e calcula o diff
     com a versão atual. Qualquer erro aborta tudo (transação única, nada parcial). Campanha nova nasce em draft.
  2. Publicação: só um administrador, no painel (Preço Fenatran > Administração) ou pela linha de comando.
  3. Snapshot: a cada mudança, a API grava <privado>/fenatran_2026.json. Com a campanha ativa, o arquivo tem os
     preços; em qualquer outro status, só os metadados (sem preços). O MCP lê esse arquivo e nada mais.
Nenhum log desta camada inclui valores de preço.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import logging
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from precos_comerciais import fenatran as F
from precos_comerciais import pdf as conferencia_pdf

from .models import ComercialCampanha, ComercialEvento, ComercialLote, ComercialPreco, Usuario, agora

log = logging.getLogger("torre.fenatran")

ARQ_CSV = "fenatran_precos_importacao.csv"
ARQ_MANIFESTO = "fenatran_manifesto_importacao.json"
PERFIS_CONSULTA = ("admin", "gestor", "vendedor")
PERFIL_ADMIN = "admin"
TRANSICOES = {
    "draft": ("active", "archived"),
    "active": ("inactive",),
    "inactive": ("active", "archived", "draft"),
    "archived": ("draft",),
}


# ---------------------------------------------------------------- importação
def _le_csv(caminho: Path) -> tuple[list[dict], str]:
    bruto = caminho.read_bytes()
    texto = bruto.decode("utf-8-sig")                    # aceita com ou sem BOM
    leitor = csv.DictReader(io.StringIO(texto))
    faltam = [c for c in F.COLUNAS if c not in (leitor.fieldnames or [])]
    if faltam:
        raise F.ErroImportacao(f"cabeçalho do CSV sem as colunas: {', '.join(faltam)}")
    return list(leitor), hashlib.sha256(bruto).hexdigest()


def _precos_do_lote(db: Session, lote_id: int | None) -> list[dict]:
    if not lote_id:
        return []
    campos = ("familia", "modelo", "modelo_busca", "ano_modelo", "up", "variante", "configuracao", *F.PRECOS,
              "source_file", "source_page")
    return [{c: getattr(p, c) for c in campos}
            for p in db.scalars(select(ComercialPreco).where(ComercialPreco.lote_id == lote_id))]


def importar(db: Session, pasta: Path, responsavel: str, *, dry_run: bool = False, aceitar_diff: bool = False,
             manter_status: bool = False, exigir_pdf: bool = True) -> dict:
    """Importa (ou simula) a tabela Fenatran. Levanta ErroImportacao com o relatório em .args[1] se algo bloquear."""
    pasta = Path(pasta)
    if not responsavel.strip():
        raise F.ErroImportacao("informe o responsável pela importação (--responsavel)")
    csv_path, man_path = pasta / ARQ_CSV, pasta / ARQ_MANIFESTO
    if not csv_path.is_file() or not man_path.is_file():
        raise F.ErroImportacao(f"a pasta precisa ter {ARQ_CSV} e {ARQ_MANIFESTO}")
    linhas, sha_csv = _le_csv(csv_path)
    manifesto = json.loads(man_path.read_text(encoding="utf-8-sig"))
    precos, erros = F.valida_linhas(linhas)
    rel = {"arquivo_csv": csv_path.name, "sha256_csv": sha_csv, "linhas_lidas": len(linhas), "linhas_validas": len(precos),
           "erros_por_linha": erros, "por_familia": {f: sum(p["familia"] == f for p in precos) for f in F.FAMILIAS},
           "manifesto": F.confere_manifesto(precos, manifesto), "avisos": F.avisos_de_conteudo(precos),
           "dry_run": dry_run}
    if exigir_pdf:
        conf = conferencia_pdf.confere(precos, pasta, manifesto)
    else:   # dispensada: o lote fica 'não conferido' e não pode ser publicado (ver muda_status)
        conf = {"documentos": {}, "divergencias": [], "fora_do_csv": [], "conferido": False,
                "aviso": "conferência com os PDFs dispensada (--sem-pdf): lote não publicável"}
    rel["documentos"], rel["conferencia_pdf"] = conf["documentos"], {k: conf.get(k) for k in
                                                                       ("conferido", "divergencias", "fora_do_csv", "aviso", "linhas_conferidas")}
    bloqueios = []
    if erros:
        bloqueios.append(f"{len(erros)} linha(s) inválida(s) no CSV")
    if rel["manifesto"]:
        bloqueios.append("contagens diferentes do manifesto")
    if conf["divergencias"] or conf["fora_do_csv"]:
        bloqueios.append("divergências com os PDFs")
    if exigir_pdf and not conf.get("conferido"):
        bloqueios.append("conferência com os PDFs não concluída (use --sem-pdf só com autorização explícita)")

    camp = db.scalar(select(ComercialCampanha).where(ComercialCampanha.chave == F.CHAVE).with_for_update())
    atual = _precos_do_lote(db, camp.lote_atual_id if camp else None)
    diff = F.diff_precos(atual, precos)
    rel["diff"] = diff
    rel["versao_atual"] = camp.versao if camp else 0
    mudou = bool(diff["novas"] or diff["removidas"] or diff["alteradas"])
    if camp and camp.lote_atual_id and not mudou:
        rel["resultado"] = "sem_mudancas"
        rel["mensagem"] = "Mesmo conteúdo da versão atual: nada importado (importação idempotente)."
        return rel
    if camp and camp.lote_atual_id and mudou and not aceitar_diff:
        bloqueios.append("há diferenças com a versão atual: revise o diff e repita com --aceitar-diff")
    rel["bloqueios"] = bloqueios
    if bloqueios:
        rel["resultado"] = "bloqueado"
        raise F.ErroImportacao("importação bloqueada: " + "; ".join(bloqueios), rel)
    if dry_run:
        rel["resultado"] = "dry_run_ok"
        rel["mensagem"] = "Validação completa sem gravar nada. Repita sem --dry-run para importar."
        return rel

    de = camp.status if camp else ""
    if camp is None:
        camp = ComercialCampanha(chave=F.CHAVE, nome=F.METADADOS_PADRAO["nome"], status="draft", versao=0,
                                 metadados=json.dumps(F.METADADOS_PADRAO, ensure_ascii=False), responsavel=responsavel)
        db.add(camp)
        db.flush()
    versao = camp.versao + 1
    lote = ComercialLote(campanha_id=camp.id, versao=versao, arquivo_csv=csv_path.name, sha256_csv=sha_csv,
                         linhas=len(precos), por_familia=json.dumps(rel["por_familia"]),
                         documentos=json.dumps(conf["documentos"], ensure_ascii=False),
                         conferencia=json.dumps(rel["conferencia_pdf"], ensure_ascii=False),
                         diff=json.dumps(diff, ensure_ascii=False), manifesto=json.dumps(manifesto, ensure_ascii=False),
                         executado_por=responsavel)
    db.add(lote)
    db.flush()
    db.add_all(ComercialPreco(campanha_id=camp.id, lote_id=lote.id, **p) for p in precos)
    camp.versao, camp.lote_atual_id, camp.atualizado_em, camp.responsavel = versao, lote.id, agora(), responsavel
    if de == "active" and not manter_status:
        camp.status = "draft"          # versão nova volta a rascunho até nova publicação
    db.add(ComercialEvento(campanha_id=camp.id, acao="importacao", de_status=de, para_status=camp.status,
                           usuario=responsavel,
                           detalhe=json.dumps({"versao": versao, "linhas": len(precos), "sha256_csv": sha_csv,
                                               "novas": len(diff["novas"]), "removidas": len(diff["removidas"]),
                                               "alteradas": len(diff["alteradas"])}, ensure_ascii=False)))
    db.flush()
    rel.update(resultado="importado", versao=versao, status=camp.status, lote_id=lote.id)
    log.info("fenatran: importada versão %s (%s linhas) por %s; status %s", versao, len(precos), responsavel, camp.status)
    return rel


# ---------------------------------------------------------------- status e expiração
def muda_status(db: Session, para: str, usuario: str, motivo: str = "") -> ComercialCampanha:
    camp = db.scalar(select(ComercialCampanha).where(ComercialCampanha.chave == F.CHAVE).with_for_update())
    if camp is None:
        raise F.ErroImportacao("campanha Fenatran ainda não importada")
    if para not in F.STATUS:
        raise F.ErroImportacao(f"status desconhecido: {para}")
    if para == camp.status:
        return camp
    if para not in TRANSICOES[camp.status]:
        raise F.ErroImportacao(f"transição {camp.status} -> {para} não permitida")
    if para == "active" and not camp.lote_atual_id:
        raise F.ErroImportacao("não há lote importado para publicar")
    if para == "active":
        lote = db.get(ComercialLote, camp.lote_atual_id)
        conf = json.loads(lote.conferencia or "{}")
        if not conf.get("conferido"):
            raise F.ErroImportacao("o lote atual não foi conferido com os PDFs; não pode ser publicado")
    de = camp.status
    camp.status, camp.atualizado_em = para, agora()
    db.add(ComercialEvento(campanha_id=camp.id, acao={"active": "ativacao", "inactive": "desativacao",
                                                      "archived": "arquivamento", "draft": "rascunho"}[para],
                           de_status=de, para_status=para, usuario=usuario, detalhe=(motivo or "")[:500]))
    log.info("fenatran: status %s -> %s por %s", de, para, usuario)
    return camp


def define_expiracao(db: Session, quando: str | None, usuario: str) -> ComercialCampanha:
    """Data opcional, decidida pelo administrador. Vazio = sem expiração (padrão)."""
    camp = db.scalar(select(ComercialCampanha).where(ComercialCampanha.chave == F.CHAVE).with_for_update())
    if camp is None:
        raise F.ErroImportacao("campanha Fenatran ainda não importada")
    novo = None
    if quando:
        try:
            novo = datetime.fromisoformat(quando)
        except ValueError as e:
            raise F.ErroImportacao("data inválida; use AAAA-MM-DDTHH:MM (horário de Brasília)") from e
        if novo.tzinfo is None:
            novo = novo.replace(tzinfo=F.TZ)
    antes = camp.expira_em.isoformat() if camp.expira_em else ""
    camp.expira_em, camp.atualizado_em = novo, agora()
    db.add(ComercialEvento(campanha_id=camp.id, acao="expiracao", de_status=camp.status, para_status=camp.status,
                           usuario=usuario, detalhe=json.dumps({"antes": antes, "depois": novo.isoformat() if novo else ""})))
    return camp


# ---------------------------------------------------------------- snapshot (o que o MCP enxerga)
def _iso(d: datetime | None) -> str | None:
    if d is None:
        return None
    return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).isoformat()


def monta_snapshot(db: Session, com_precos_em_rascunho: bool = False) -> dict:
    camp = db.scalar(select(ComercialCampanha).where(ComercialCampanha.chave == F.CHAVE))
    if camp is None:
        return {"campanha": None, "precos": []}
    lote = db.get(ComercialLote, camp.lote_atual_id) if camp.lote_atual_id else None
    meta = json.loads(camp.metadados or "{}")
    docs = json.loads(lote.documentos) if lote else {}
    c = {"chave": camp.chave, "nome": camp.nome, "status": camp.status, "versao": camp.versao,
         "expira_em": _iso(camp.expira_em), "atualizado_em": _iso(camp.atualizado_em), "metadados": meta,
         "lote": {"id": lote.id, "sha256_csv": lote.sha256_csv, "documentos": {k: v.get("sha256") for k, v in docs.items()},
                  "importado_em": _iso(lote.executado_em)} if lote else None}
    mostra = camp.status == "active" or (com_precos_em_rascunho and camp.status == "draft")
    return {"campanha": c, "precos": _precos_do_lote(db, camp.lote_atual_id) if (lote and mostra) else []}


def grava_snapshot(pasta: Path, snap: dict) -> Path:
    """Escrita atômica (arquivo temporário + rename): o MCP nunca lê um arquivo pela metade."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / f"{F.CHAVE}.json"
    fd, tmp = tempfile.mkstemp(prefix=".fenatran-", suffix=".json", dir=pasta)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(snap, f, ensure_ascii=False)
        os.chmod(tmp, 0o644)
        os.replace(tmp, destino)
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise
    return destino


def sincroniza(db: Session, pasta: Path) -> dict:
    snap = monta_snapshot(db)
    grava_snapshot(pasta, snap)
    return snap


def painel_admin(db: Session) -> dict:
    camp = db.scalar(select(ComercialCampanha).where(ComercialCampanha.chave == F.CHAVE))
    if camp is None:
        return {"campanha": None, "lotes": [], "eventos": []}
    lotes = db.scalars(select(ComercialLote).where(ComercialLote.campanha_id == camp.id)
                       .order_by(ComercialLote.versao.desc()).limit(20)).all()
    eventos = db.scalars(select(ComercialEvento).where(ComercialEvento.campanha_id == camp.id)
                         .order_by(ComercialEvento.em.desc(), ComercialEvento.id.desc()).limit(50)).all()
    return {
        "campanha": {"chave": camp.chave, "nome": camp.nome, "status": camp.status, "versao": camp.versao,
                     "expira_em": _iso(camp.expira_em), "atualizado_em": _iso(camp.atualizado_em),
                     "responsavel": camp.responsavel, "transicoes": list(TRANSICOES[camp.status]),
                     "aliquotas": json.loads(camp.metadados or "{}").get("aliquotas")},
        "lotes": [{"versao": l.versao, "arquivo_csv": l.arquivo_csv, "sha256_csv": l.sha256_csv, "linhas": l.linhas,
                   "por_familia": json.loads(l.por_familia), "documentos": json.loads(l.documentos),
                   "conferencia": json.loads(l.conferencia), "diff": json.loads(l.diff),
                   "executado_por": l.executado_por, "executado_em": _iso(l.executado_em),
                   "atual": l.id == camp.lote_atual_id} for l in lotes],
        "eventos": [{"acao": e.acao, "de": e.de_status, "para": e.para_status, "usuario": e.usuario,
                     "detalhe": e.detalhe, "em": _iso(e.em)} for e in eventos],
    }


# ---------------------------------------------------------------- rotas do painel
def _int(v) -> int | None:
    try:
        return int(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def registrar(app, cfg, db, usuario) -> None:
    """Rotas /api/fenatran/* (consulta) e /api/admin/fenatran/* (só perfil admin). Registrar antes da rota genérica."""
    pasta = Path(cfg.privado_dir)

    def quem(req: Request):
        u = usuario(req)
        if u is None:
            return None, JSONResponse({"erro": "não autenticado", "status_consulta": "nao_autenticado"}, status_code=401)
        if u.perfil not in PERFIS_CONSULTA:
            return None, JSONResponse({"erro": "sem permissão", "status_consulta": "sem_permissao"}, status_code=403)
        return u, None

    def mesma_origem(req: Request) -> bool:
        """Escritas administrativas: só do próprio painel (cabeçalho próprio + Origin igual ao Host)."""
        if req.headers.get("x-torre-acao") != "1":
            return False
        origem = req.headers.get("origin")
        if origem:
            host = origem.split("://", 1)[-1].split("/", 1)[0].lower()
            return host == req.headers.get("host", "").lower()
        return True

    @app.get("/api/fenatran/consulta")
    def consulta(req: Request):
        u, erro = quem(req)
        if erro:
            return erro
        qp = req.query_params
        with db() as s:
            admin = u.perfil == PERFIL_ADMIN
            snap = monta_snapshot(s, com_precos_em_rascunho=admin)
        r = F.consultar(snap, modelo=qp.get("modelo") or qp.get("q"), familia=qp.get("familia"),
                        ano_modelo=qp.get("ano_modelo"), up=qp.get("up"), variante=qp.get("variante"),
                        configuracao=qp.get("configuracao"), quantidade=_int(qp.get("quantidade")),
                        origem=qp.get("origem") or "ambos", calcular_total=qp.get("calcular_total") == "1",
                        listar_todos=qp.get("listar_todos") == "1", limite=_int(qp.get("limite")) or 200,
                        pagina=_int(qp.get("pagina")) or 1, incluir_rascunho=admin)
        r["pode_administrar"] = admin
        log.info("fenatran: consulta painel por %s -> %s (%s resultados)", u.login, r["status_consulta"],
                 r["total_encontrado"])
        return JSONResponse(r, headers={"Cache-Control": "no-store"})

    @app.get("/api/fenatran/opcoes")
    def opcoes(req: Request):
        u, erro = quem(req)
        if erro:
            return erro
        with db() as s:
            snap = monta_snapshot(s, com_precos_em_rascunho=u.perfil == PERFIL_ADMIN)
        precos = snap["precos"]
        c = snap["campanha"] or {}
        visivel, st = F.campanha_vigente(snap)
        if not visivel and not (u.perfil == PERFIL_ADMIN and st == "draft"):
            precos = []
        return JSONResponse({
            "status": st, "versao": c.get("versao"), "pode_administrar": u.perfil == PERFIL_ADMIN,
            "familias": [f for f in F.FAMILIAS if any(p["familia"] == f for p in precos)],
            "anos_modelo": sorted({p["ano_modelo"] for p in precos}), "ups": sorted({p["up"] for p in precos}),
            "configuracoes": sorted({p["configuracao"] for p in precos}),
            "lote": (c.get("lote") or {}) if precos else None,
            "fonte": (c.get("metadados") or {}).get("fonte"),
        }, headers={"Cache-Control": "no-store"})

    def admin(req: Request):
        u = usuario(req)
        if u is None:
            return None, JSONResponse({"erro": "não autenticado"}, status_code=401)
        if u.perfil != PERFIL_ADMIN:
            return None, JSONResponse({"erro": "somente administradores"}, status_code=403)
        return u, None

    @app.get("/api/admin/fenatran")
    def admin_painel(req: Request):
        u, erro = admin(req)
        if erro:
            return erro
        with db() as s:
            return JSONResponse(painel_admin(s), headers={"Cache-Control": "no-store"})

    @app.post("/api/admin/fenatran/status")
    async def admin_status(req: Request):
        u, erro = admin(req)
        if erro:
            return erro
        if not mesma_origem(req):
            return JSONResponse({"erro": "origem não permitida"}, status_code=403)
        try:
            corpo = json.loads((await req.body())[:4000] or b"{}")
        except ValueError:
            return JSONResponse({"erro": "json inválido"}, status_code=400)
        try:
            with db() as s:
                camp = muda_status(s, str(corpo.get("status", "")), u.login, str(corpo.get("motivo", "")))
                st = camp.status
                s.commit()                 # grava antes do snapshot: o MCP nunca vê um status não confirmado
                sincroniza(s, pasta)
        except F.ErroImportacao as e:
            return JSONResponse({"erro": str(e)}, status_code=409)
        return {"ok": True, "status": st}

    @app.post("/api/admin/fenatran/expiracao")
    async def admin_expiracao(req: Request):
        u, erro = admin(req)
        if erro:
            return erro
        if not mesma_origem(req):
            return JSONResponse({"erro": "origem não permitida"}, status_code=403)
        try:
            corpo = json.loads((await req.body())[:2000] or b"{}")
        except ValueError:
            return JSONResponse({"erro": "json inválido"}, status_code=400)
        try:
            with db() as s:
                camp = define_expiracao(s, corpo.get("expira_em") or None, u.login)
                s.commit()
                sincroniza(s, pasta)
                exp = _iso(camp.expira_em)
        except F.ErroImportacao as e:
            return JSONResponse({"erro": str(e)}, status_code=409)
        return {"ok": True, "expira_em": exp}

    # Ao subir, alinha o snapshot com o banco (ex.: volume novo). Falha aqui não derruba o painel.
    try:
        with db() as s:
            sincroniza(s, pasta)
    except Exception as e:  # tabela ainda não migrada ou pasta sem permissão
        log.warning("fenatran: snapshot não gravado ao subir (%s)", type(e).__name__)


# ---------------------------------------------------------------- linha de comando (contêiner da API)
def main(argv=None, engine=None, pasta_privada: Path | None = None) -> int:
    from .config import load_settings
    from .db import make_engine, make_sessionmaker

    p = argparse.ArgumentParser(prog="python -m server.app.fenatran", description="Preço Fenatran (administração)")
    sub = p.add_subparsers(dest="cmd", required=True)
    im = sub.add_parser("importar", help="valida e importa a tabela (pasta com CSV, manifesto e os 2 PDFs)")
    im.add_argument("--pasta", required=True)
    im.add_argument("--responsavel", required=True)
    im.add_argument("--dry-run", action="store_true")
    im.add_argument("--aceitar-diff", action="store_true")
    im.add_argument("--manter-status", action="store_true", help="não voltar a campanha ativa para rascunho")
    im.add_argument("--sem-pdf", action="store_true", help="aceita importar sem conferir PDFs (exige autorização)")
    for nome in ("ativar", "desativar", "arquivar", "rascunho"):
        x = sub.add_parser(nome)
        x.add_argument("--responsavel", required=True)
        x.add_argument("--motivo", default="")
    ex = sub.add_parser("expiracao", help="data opcional de expiração (vazia = sem expiração)")
    ex.add_argument("--data", default="")
    ex.add_argument("--responsavel", required=True)
    sub.add_parser("status")
    sub.add_parser("sincronizar", help="regrava o snapshot lido pelo MCP")
    a = p.parse_args(argv)

    cfg = load_settings()
    pasta = Path(pasta_privada or cfg.privado_dir)
    Sessions = make_sessionmaker(engine or make_engine(cfg.database_url))
    with Sessions() as s:
        try:
            if a.cmd == "importar":
                if a.responsavel and not s.scalar(select(Usuario).where(Usuario.login == a.responsavel.lower())):
                    print(f"aviso: {a.responsavel} não é usuário da Torre; registrado só como texto", file=sys.stderr)
                rel = importar(s, Path(a.pasta), a.responsavel, dry_run=a.dry_run, aceitar_diff=a.aceitar_diff,
                               manter_status=a.manter_status, exigir_pdf=not a.sem_pdf)
                s.commit()
                if not a.dry_run:
                    sincroniza(s, pasta)
                print(json.dumps(rel, ensure_ascii=False, indent=1))
                return 0
            if a.cmd in ("ativar", "desativar", "arquivar", "rascunho"):
                para = {"ativar": "active", "desativar": "inactive", "arquivar": "archived", "rascunho": "draft"}[a.cmd]
                camp = muda_status(s, para, a.responsavel, a.motivo)
                s.commit()
                sincroniza(s, pasta)
                print(f"ok: campanha {camp.chave} agora {camp.status}")
                return 0
            if a.cmd == "expiracao":
                camp = define_expiracao(s, a.data or None, a.responsavel)
                s.commit()
                sincroniza(s, pasta)
                print(f"ok: expira_em = {_iso(camp.expira_em) or 'sem expiração'}")
                return 0
            if a.cmd == "status":
                info = painel_admin(s)
                for l in info["lotes"]:          # sem preços e sem diff detalhado no terminal
                    l.pop("diff", None)
                print(json.dumps(info, ensure_ascii=False, indent=1))
                return 0
            if a.cmd == "sincronizar":
                snap = sincroniza(s, pasta)
                print(f"ok: snapshot gravado ({len(snap['precos'])} preços visíveis ao MCP)")
                return 0
        except F.ErroImportacao as e:
            s.rollback()
            print(f"ERRO: {e.args[0]}", file=sys.stderr)
            if len(e.args) > 1:
                print(json.dumps(e.args[1], ensure_ascii=False, indent=1), file=sys.stderr)
            return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
