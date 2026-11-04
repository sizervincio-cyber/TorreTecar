"""Coleta incremental do PNCP para GO, MT e TO.

Cada execução tem um orçamento de tempo e faz, nesta ordem:
  1. Atualização: contratações publicadas ou alteradas desde a última execução (rota /atualizacao). Pega editais
     novos, homologações e resultados que chegaram depois.
  2. Histórico: janelas mensais ainda não varridas, da mais recente para 01/2021 (rota /publicacao).
Para cada contratação cujo objeto interessa, baixa os itens, classifica e, nos itens relevantes com resultado,
baixa fornecedor, quantidade e preço homologados. Tudo é salvo a cada janela, então uma execução interrompida
continua de onde parou na próxima.
"""
from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from . import catalogo, config
from .comprasgov import FIM_LEGADO, ComprasGovClient, ComprasGovError, link_compra
from .pncp import PncpClient, PncpError

log = logging.getLogger("licitacoes")


def _read(path, default):
    import json
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _write(path, data) -> None:
    import json
    import os
    import tempfile
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, path)


def janelas_mensais(inicio: date, hoje: date) -> list[str]:
    """Meses de inicio até o mês anterior ao atual, do mais recente para o mais antigo (o mês corrente vem pela atualização)."""
    out, y, m = [], hoje.year, hoje.month
    while True:
        m -= 1
        if m == 0:
            y, m = y - 1, 12
        if (y, m) < (inicio.year, inicio.month):
            return out
        out.append(f"{y:04d}-{m:02d}")


def limites_mes(ym: str) -> tuple[str, str]:
    y, m = int(ym[:4]), int(ym[5:])
    ini = date(y, m, 1)
    fim = (date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1))
    return ini.isoformat(), fim.isoformat()


def compra_id(c: dict) -> str:
    return f"{c['orgaoEntidade']['cnpj']}-{c['anoCompra']}-{c['sequencialCompra']}"


def resumo_compra(c: dict) -> dict:
    org, un = c.get("orgaoEntidade") or {}, c.get("unidadeOrgao") or {}
    cnpj, ano, seq = org.get("cnpj"), c.get("anoCompra"), c.get("sequencialCompra")
    return {
        "id": compra_id(c), "orgao_cnpj": cnpj, "orgao": org.get("razaoSocial"), "esfera": org.get("esferaId"),
        "poder": org.get("poderId"), "uf": un.get("ufSigla"), "municipio": un.get("municipioNome"),
        "ibge": un.get("codigoIbge"), "unidade": un.get("nomeUnidade"),
        "modalidade": c.get("modalidadeId"), "modalidade_nome": c.get("modalidadeNome"), "srp": c.get("srp"),
        "numero": c.get("numeroCompra"), "ano": ano, "processo": c.get("processo"),
        "objeto": (c.get("objetoCompra") or "")[:400],
        "valor_estimado": c.get("valorTotalEstimado"), "valor_homologado": c.get("valorTotalHomologado"),
        "publicada": (c.get("dataPublicacaoPncp") or "")[:10], "abertura": (c.get("dataAberturaProposta") or "")[:16],
        "encerramento": (c.get("dataEncerramentoProposta") or "")[:16], "situacao": c.get("situacaoCompraNome"),
        "atualizada": c.get("dataAtualizacaoGlobal") or c.get("dataAtualizacao"),
        "emenda": bool(c.get("emendaParlamentar")),
        "link": f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}",
        "fonte": "PNCP",
    }


class _PrazoEsgotado(Exception):
    pass


@dataclass
class Resultado:
    contratacoes_lidas: int = 0
    compras_relevantes: int = 0
    itens_relevantes: int = 0
    resultados: int = 0
    janelas: int = 0
    requisicoes: int = 0
    erro: str | None = None
    avisos: list[str] = field(default_factory=list)

    def resumo(self) -> str:
        s = (f"{self.janelas} janelas · {self.contratacoes_lidas} contratações lidas · {self.compras_relevantes} relevantes · "
             f"{self.itens_relevantes} itens · {self.resultados} resultados · {self.requisicoes} requisições")
        return s + (f" · interrompido: {self.erro}" if self.erro else "")


class Coletor:
    def __init__(self, client: PncpClient | None = None, mapa_marca: dict | None = None, ufs=config.UFS,
                 modalidades=None, inicio: date = config.INICIO, clock=time.monotonic, cg: ComprasGovClient | None = None):
        self.client = client or PncpClient()
        self.cg = cg
        self.mapa_marca = mapa_marca or {}
        self.ufs = tuple(ufs)
        self.modalidades = tuple(modalidades or config.MODALIDADES)
        self.inicio = inicio
        self.clock = clock
        self.estado = _read(config.ESTADO_PATH, {}) or {}
        self.compras = (_read(config.COMPRAS_PATH, {}) or {}).get("compras", {})
        brutos = []
        for p in (config.VEICULOS_PATH, config.POSVENDA_PATH, config.LEGADO_ITENS_PATH):
            brutos += (_read(p, {}) or {}).get("itens", [])
        self.itens = {(i["compra"], i["n"]): i for i in brutos}
        self.descartadas = set(self.estado.get("descartadas", []))
        self.reclassificar()

    def reclassificar(self) -> int:
        """Aplica o catálogo atual aos itens já coletados (as regras evoluem; a base acompanha sem recoletar)."""
        mudou = 0
        for k, i in list(self.itens.items()):
            c = self.compras.get(i["compra"]) or {}
            cl = catalogo.classificar(i.get("desc"), c.get("objeto", ""), i.get("vu_est"), i.get("un"))
            if not cl:
                del self.itens[k]
                mudou += 1
                continue
            novo = {"seg": cl["segmento"], "tipo": cl["tipo"], "impl": cl.get("impl"), "pbt": cl.get("pbt")}
            if any(i.get(x) != v for x, v in novo.items()):
                i.update(novo)
                mudou += 1
        com_itens = {k[0] for k in self.itens}
        for cid in [cid for cid in self.compras if cid not in com_itens]:
            self.compras.pop(cid)
        return mudou

    # ---------- processamento de uma contratação ----------
    def processar(self, c: dict, res: Resultado, prazo: float = float("inf")) -> None:
        """Baixa e classifica os itens de uma contratação. Grava tudo ou nada: se o prazo estoura no meio de um
        catálogo grande, a contratação fica para a próxima execução (não entra pela metade)."""
        cid = compra_id(c)
        atual = c.get("dataAtualizacaoGlobal") or c.get("dataAtualizacao")
        antiga = self.compras.get(cid)
        if cid in self.descartadas or (antiga and antiga.get("atualizada") == atual and antiga.get("itens_em")):
            return
        if not catalogo.objeto_relevante(c.get("objetoCompra")):
            return
        cnpj, ano, seq = c["orgaoEntidade"]["cnpj"], c["anoCompra"], c["sequencialCompra"]
        rel = []
        for it in self.client.itens(cnpj, ano, seq):
            cl = catalogo.classificar(it.get("descricao"), c.get("objetoCompra"), it.get("valorUnitarioEstimado"), it.get("unidadeMedida"))
            if cl:
                rel.append((it, cl))
        if not rel:
            self.descartadas.add(cid)
            self.compras.pop(cid, None)
            for k in [k for k in self.itens if k[0] == cid]:
                del self.itens[k]
            return
        rows, nres = [], 0
        for it, cl in rel:
            if self.clock() > prazo:
                raise _PrazoEsgotado()
            marca, similar = catalogo.marca_descricao(it.get("descricao"))
            row = {
                "compra": cid, "n": it.get("numeroItem"), "desc": (it.get("descricao") or "")[:300],
                "seg": cl["segmento"], "tipo": cl["tipo"], "impl": cl.get("impl"), "pbt": cl.get("pbt"),
                "qtd": it.get("quantidade"), "un": it.get("unidadeMedida"),
                "vu_est": it.get("valorUnitarioEstimado"), "vt_est": it.get("valorTotal"),
                "situacao": it.get("situacaoCompraItemNome"), "marca_desc": marca, "similar": similar, "r": [],
            }
            if it.get("temResultado"):
                for r in self.client.resultados(cnpj, ano, seq, it.get("numeroItem")):
                    if r.get("dataCancelamento"):
                        continue
                    row["r"].append({
                        "ni": r.get("niFornecedor"), "nome": r.get("nomeRazaoSocialFornecedor"),
                        "porte": r.get("porteFornecedorNome"), "qtd": r.get("quantidadeHomologada"),
                        "vu": r.get("valorUnitarioHomologado"), "vt": r.get("valorTotalHomologado"),
                        "data": r.get("dataResultado"),
                        # SRP: 1º colocado é o fornecedor da ata; os demais são cadastro de reserva (não somar)
                        "ordem": r.get("ordemClassificacaoSrp"),
                        "marca_forn": catalogo.marca_fornecedor(r.get("nomeRazaoSocialFornecedor"), self.mapa_marca),
                    })
                    nres += 1
            rows.append(row)
        comp = resumo_compra(c)
        comp["itens_em"] = datetime.now(config.TZ).date().isoformat()
        comp["n_itens"] = len(rows)
        for k in [k for k in self.itens if k[0] == cid]:
            del self.itens[k]
        self.compras[cid] = comp
        for row in rows:
            self.itens[(cid, row["n"])] = row
        res.compras_relevantes += 1
        res.itens_relevantes += len(rows)
        res.resultados += nres

    def _varrer(self, rota: str, ini: str, fim: str, res: Resultado, prazo: float) -> bool:
        """Varre UFs × modalidades de uma janela. False se o prazo acabou no meio (a janela não conta como concluída)."""
        for uf in self.ufs:
            for mod in self.modalidades:
                for c in self.client.contratacoes(rota, ini, fim, uf, mod):
                    res.contratacoes_lidas += 1
                    antes = res.compras_relevantes
                    try:
                        self.processar(c, res, prazo)
                    except _PrazoEsgotado:
                        return False
                    if res.compras_relevantes != antes and res.compras_relevantes % 25 == 0:
                        self.salvar(self.hoje)   # janelas longas: grava o parcial para a Torre já enxergar
                    if self.clock() > prazo:
                        return False
        return True

    # ---------- segunda fonte: Compras.gov.br (pregões da lei antiga) ----------
    def _indice_pncp(self) -> set:
        """(CNPJ do órgão, ano, número) das compras do PNCP, para não repetir o mesmo pregão vindo das duas fontes."""
        idx = set()
        for c in self.compras.values():
            if c.get("fonte", "PNCP") == "PNCP":
                n = "".join(ch for ch in str(c.get("numero") or "") if ch.isdigit()).lstrip("0")
                idx.add((c.get("orgao_cnpj"), str(c.get("ano")), n))
        return idx

    def processar_cg(self, p: dict, uasgs: dict, idx_pncp: set, res: Resultado, prazo: float) -> None:
        uasg = str(p.get("co_uasg"))
        info = uasgs.get(uasg)
        if not info:
            return
        cid = "CG-" + str(p.get("id_compra"))
        antiga = self.compras.get(cid)
        if cid in self.descartadas or (antiga and antiga.get("atualizada") == p.get("dt_alteracao") and antiga.get("itens_em")):
            return
        if not catalogo.objeto_relevante(p.get("tx_objeto")):
            return
        num = str(p.get("numero") or "")
        seq, ano = num[:-4].lstrip("0"), num[-4:]
        if (info["cnpj"], ano, seq) in idx_pncp:
            self.descartadas.add(cid)        # mesmo pregão já veio pelo PNCP
            return
        rel = []
        for it in self.cg.itens(uasg, int(num)):
            if it.get("codigo_item_servico"):
                continue                     # item de serviço: fora do escopo de produtos
            desc = it.get("nome_material") or it.get("descricao_item") or ""
            cl = catalogo.classificar(desc, p.get("tx_objeto"), it.get("valor_estimado"), it.get("unidade"))
            if cl:
                rel.append((it, desc, cl))
        if not rel:
            self.descartadas.add(cid)
            self.compras.pop(cid, None)
            return
        if self.clock() > prazo:
            raise _PrazoEsgotado()
        hom = {}
        if str(p.get("ds_situacao_pregao") or "").lower().startswith("homolog") and any(it.get("cnpj_fornecedor") for it, _, _ in rel):
            ed = (p.get("dt_data_edital") or "")[:10]
            if ed:
                fim = (date.fromisoformat(ed) + timedelta(days=540)).isoformat()
                hom = self.cg.homologados(uasg, ed, fim)
        rows, nres = [], 0
        for it, desc, cl in rel:
            marca, similar = catalogo.marca_descricao(desc)
            qtd, vu_est = it.get("quantidade"), it.get("valor_estimado")
            row = {
                "compra": cid, "n": it.get("numero_item_licitacao"), "desc": desc[:300],
                "seg": cl["segmento"], "tipo": cl["tipo"], "impl": cl.get("impl"), "pbt": cl.get("pbt"),
                "qtd": qtd, "un": it.get("unidade"), "vu_est": vu_est, "vt_est": (qtd or 0) * (vu_est or 0),
                "situacao": p.get("ds_situacao_pregao"), "marca_desc": marca, "similar": similar, "r": [],
            }
            if it.get("cnpj_fornecedor") or it.get("nome_fornecedor"):
                h = hom.get(str(it.get("id_compra_item"))) or {}
                vu = h.get("valor_homologado_item")
                row["r"].append({
                    "ni": it.get("cnpj_fornecedor"), "nome": it.get("nome_fornecedor"), "porte": None,
                    "qtd": h.get("quantidade_item") or qtd, "vu": vu, "vt": (vu * (h.get("quantidade_item") or qtd or 0)) if vu else None,
                    "data": (h.get("dt_hom") or p.get("dt_resultado") or "")[:10] or None, "ordem": None,
                    "preco_pendente": vu is None,
                    "marca_forn": catalogo.marca_fornecedor(it.get("nome_fornecedor"), self.mapa_marca),
                })
                nres += 1
            rows.append(row)
        nome = str(p.get("no_orgao") or "")
        esfera = "F" if info.get("sisg") else ("M" if re.search(r"MUNIC|PREFEIT|CAMARA|FUNDO M|FMS|SAAE", catalogo.norm(nome + " " + str(p.get("no_ausg") or ""))) else "E")
        self.compras[cid] = {
            "id": cid, "orgao_cnpj": info["cnpj"], "orgao": nome or info["nome"], "esfera": esfera, "poder": None,
            "uf": info["uf"], "municipio": (info["municipio"] or "").title(), "ibge": info["ibge"], "unidade": p.get("no_ausg"),
            "modalidade": None, "modalidade_nome": "Pregão (lei antiga) · Compras.gov.br",
            "srp": str(p.get("ds_tipo_pregao_compra") or "").upper() == "SISRP",
            "numero": seq, "ano": int(ano) if ano.isdigit() else None, "processo": p.get("co_processo"),
            "objeto": (p.get("tx_objeto") or "")[:400],
            "valor_estimado": p.get("valor_estimado_total"), "valor_homologado": p.get("valor_homologado_total"),
            "publicada": (p.get("dt_data_edital") or "")[:10], "abertura": (p.get("dt_inicio_proposta") or "")[:16],
            "encerramento": (p.get("dt_fim_proposta") or "")[:16], "situacao": p.get("ds_situacao_pregao"),
            "atualizada": p.get("dt_alteracao"), "emenda": False, "link": link_compra(str(p.get("id_compra"))),
            "fonte": "COMPRASGOV", "uasg": uasg,
            "itens_em": datetime.now(config.TZ).date().isoformat(), "n_itens": len(rows),
        }
        for k in [k for k in self.itens if k[0] == cid]:
            del self.itens[k]
        for row in rows:
            self.itens[(cid, row["n"])] = row
        res.compras_relevantes += 1
        res.itens_relevantes += len(rows)
        res.resultados += nres

    def _comprasgov(self, hoje: date, res: Resultado, prazo: float) -> None:
        janelas = self.estado.setdefault("cg_janelas", {})
        meses = [m for m in janelas_mensais(self.inicio, hoje) if m <= FIM_LEGADO]
        pendentes = [m for m in meses if m not in janelas]
        self.estado["cg_meses_total"], self.estado["cg_meses_concluidos"] = len(meses), len(meses) - len(pendentes)
        if not pendentes or self.clock() > prazo:
            return
        uasgs = self.cg.uasgs(self.ufs)
        idx = self._indice_pncp()
        for ym in pendentes:
            if self.clock() > prazo:
                return
            a, b = limites_mes(ym)
            log.info("Compras.gov.br %s", ym)
            vistos = set()
            try:
                for p in self.cg.pregoes(a, b):
                    if p.get("id_compra") in vistos:
                        continue                     # a rota repete o mesmo pregão em páginas diferentes
                    vistos.add(p.get("id_compra"))
                    res.contratacoes_lidas += 1
                    self.processar_cg(p, uasgs, idx, res, prazo)
                    if self.clock() > prazo:
                        return
            except _PrazoEsgotado:
                return
            janelas[ym] = datetime.now(config.TZ).isoformat(timespec="seconds")
            self.estado["cg_meses_concluidos"] = len([m for m in meses if m in janelas])
            res.janelas += 1
            self.salvar(hoje)

    # ---------- execução ----------
    def run(self, minutos: float = 50, hoje: date | None = None, historico: bool = True) -> Resultado:
        hoje = self.hoje = hoje or datetime.now(config.TZ).date()
        prazo_total = self.clock() + minutos * 60
        prazo = self.clock() + minutos * 60 * (0.6 if self.cg else 1)   # PNCP primeiro; o restante vai ao Compras.gov.br
        res = Resultado()
        janelas = self.estado.setdefault("janelas", {})
        try:
            ult = self.estado.get("ultima_atualizacao")
            ini = (date.fromisoformat(ult) - timedelta(days=2)).isoformat() if ult else hoje.replace(day=1).isoformat()
            log.info("atualização PNCP %s → %s", ini, hoje)
            if self._varrer("atualizacao", ini, hoje.isoformat(), res, prazo):
                self.estado["ultima_atualizacao"] = hoje.isoformat()
            res.janelas += 1
            self.salvar(hoje)
            if historico:
                for ym in janelas_mensais(self.inicio, hoje):
                    if ym in janelas or self.clock() > prazo:
                        continue
                    a, b = limites_mes(ym)
                    log.info("histórico %s", ym)
                    if not self._varrer("publicacao", a, b, res, prazo):
                        break
                    janelas[ym] = datetime.now(config.TZ).isoformat(timespec="seconds")
                    res.janelas += 1
                    self.salvar(hoje)
        except PncpError as e:
            res.erro = str(e)
            log.warning("%s", e)
        try:
            if self.cg:
                self._comprasgov(hoje, res, prazo_total)
        except ComprasGovError as e:
            res.avisos.append(str(e))
            log.warning("%s", e)
        finally:
            res.requisicoes = self.client.requests + (self.cg.requests if self.cg else 0)
            self.salvar(hoje, res)
        return res

    def salvar(self, hoje: date, res: Resultado | None = None) -> None:
        total_meses = len(janelas_mensais(self.inicio, hoje))
        feitas = sorted(self.estado.get("janelas", {}))
        self.estado.update({
            "fonte": "PNCP — API de Consulta (pncp.gov.br/api/consulta) e API PNCP (itens e resultados)",
            "ufs": list(self.ufs), "modalidades": {str(k): config.MODALIDADES.get(k, str(k)) for k in self.modalidades},
            "inicio": self.inicio.isoformat(), "meses_total": total_meses, "meses_concluidos": len(feitas),
            "mais_antigo_concluido": feitas[0] if feitas else None,
            "descartadas": sorted(self.descartadas),
            "atualizado_em": datetime.now(config.TZ).isoformat(timespec="seconds"),
        })
        if res is not None:
            runs = self.estado.setdefault("execucoes", [])
            runs.append({"em": self.estado["atualizado_em"], "resumo": res.resumo()})
            del runs[:-30]
        _write(config.ESTADO_PATH, self.estado)
        _write(config.COMPRAS_PATH, {"gerado_em": self.estado["atualizado_em"], "compras": self.compras})
        itens = sorted(self.itens.values(), key=lambda i: (i["compra"], i["n"] or 0))
        for base, path in (("VEICULOS", config.VEICULOS_PATH), ("POSVENDA", config.POSVENDA_PATH)):
            segs = {k: v for k, v in catalogo.SEGMENTOS.items() if catalogo.base_do_segmento(k) == base}
            _write(path, {"gerado_em": self.estado["atualizado_em"], "base": base, "base_nome": catalogo.BASES[base],
                          "segmentos": segs, "tipos": catalogo.TIPOS,
                          "itens": [i for i in itens if catalogo.base_do_segmento(i["seg"]) == base]})
        if config.LEGADO_ITENS_PATH.exists():
            config.LEGADO_ITENS_PATH.unlink()
