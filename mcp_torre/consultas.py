"""Consultas do MCP da Torre. Funções puras sobre as bases: sempre leem a base inteira e devolvem
números já calculados, com a fonte e a data de cada base, para o modelo citar de onde veio cada valor."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, timedelta

from .dados import ASSOBENS, LICITACOES, MATRIZ, TORRE_HTML, Bases, digitos, sem_acento

MB = "M.BENZ"
DIMENSOES = {
    "marca": "marca", "uf": "uf", "cidade": "cidade", "aop": "aop", "dealer_aop": "dealer_aop",
    "segmento": "segmento", "subsegmento": "subsegmento", "tracao": "tracao", "modelo": "modelo",
    "concessionario": "concessionario", "tipo_pessoa": "tipo_pessoa", "terreno": "terreno",
    "proprietario": "proprietario", "raiz_cnpj": "raiz", "ano": None, "mes": None, "ano_modelo": "ano_modelo",
}
MAX_LINHAS = 500


class ErroConsulta(ValueError):
    pass


# ---------- filtros ----------
def _lista(v) -> list[str]:
    if v is None or v == "":
        return []
    return [sem_acento(x) for x in (v if isinstance(v, (list, tuple)) else str(v).split(","))if str(x).strip()]


def _data(v: str | None, fim: bool = False) -> str | None:
    if not v:
        return None
    v = str(v).strip()
    if len(v) == 7:  # AAAA-MM
        return v + ("-31" if fim else "-01")
    if len(v) == 4:  # AAAA
        return v + ("-12-31" if fim else "-01-01")
    return v[:10]


def filtra(rows: list[dict], *, data_ini=None, data_fim=None, marca=None, uf=None, aop=None, cidade=None,
           segmento=None, subsegmento=None, tracao=None, modelo_contem=None, proprietario_contem=None, cnpj=None,
           concessionario_contem=None, tipo_pessoa=None, placa=None, chassi=None) -> list[dict]:
    di, df = _data(data_ini), _data(data_fim, True)
    sets = {k: set(_lista(v)) for k, v in (("marca", marca), ("uf", uf), ("aop", aop), ("cidade", cidade),
                                           ("segmento", segmento), ("subsegmento", subsegmento), ("tracao", tracao),
                                           ("tipo_pessoa", tipo_pessoa))}
    mod, prop, conc = sem_acento(modelo_contem), sem_acento(proprietario_contem), sem_acento(concessionario_contem)
    doc = digitos(cnpj)
    pl, ch = sem_acento(placa).replace("-", ""), sem_acento(chassi)
    out = []
    for r in rows:
        if di and r["data"] < di or df and r["data"] > df:
            continue
        if any(v and sem_acento(r[k]) not in v for k, v in sets.items()):
            continue
        if mod and mod not in sem_acento(r["modelo"]):
            continue
        if prop and prop not in sem_acento(r["proprietario"]):
            continue
        if conc and conc not in sem_acento(r["concessionario"]):
            continue
        if doc and not (r["cnpj"] == doc or (len(doc) == 8 and r["raiz"] == doc)):
            continue
        if pl and sem_acento(r["placa"]).replace("-", "") != pl:
            continue
        if ch and ch not in sem_acento(r["chassi"]):
            continue
        out.append(r)
    return out


def _chave(r: dict, dim: str):
    if dim == "ano":
        return r["data"][:4]
    if dim == "mes":
        return r["data"][:7]
    campo = DIMENSOES.get(dim)
    if campo is None and dim not in ("ano", "mes"):
        raise ErroConsulta(f"dimensão desconhecida: {dim}. Use: {', '.join(DIMENSOES)}")
    return r.get(campo) or "(vazio)"


def _num(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _pct(a, b):
    return round(100 * a / b, 2) if b else None


def _fonte(b: Bases, *rels) -> dict:
    return {rel: b.atualizado_em(rel) for rel in rels}


def _periodo(rows: list[dict]) -> dict:
    return {"de": rows[0]["data"], "ate": rows[-1]["data"]} if rows else {}


# ---------- ferramentas ----------
def status_dados(b: Bases) -> dict:
    rows = b.emplacamentos()
    st = b.json(f"{ASSOBENS}/status.json", {}) or {}
    crm = b.crm()
    lic = b.json(f"{LICITACOES}/estado.json", {}) or {}
    return {
        "emplacamentos": {"linhas": len(rows), "periodo": _periodo(rows), "ufs": sorted({r["uf"] for r in rows}),
                          "arquivo_atualizado_em": b.atualizado_em(MATRIZ)},
        "sincronizacao_assobens": {k: st.get(k) for k in ("status", "status_label", "ultima_execucao", "finished_at",
                                                          "data_maxima", "last_success_at") if k in st},
        "crm": {"contas": len(crm["contas"]), "exportado_em": crm["meta"].get("exportDate"),
                "casas": crm["meta"].get("dealers")},
        "licitacoes": {"ultima_atualizacao": lic.get("ultima_atualizacao") or lic.get("atualizado_em"),
                       "ufs": lic.get("ufs"), "inicio": lic.get("inicio")},
        "cadastro_cnpja": bool(b.json(f"{ASSOBENS}/empresas_cnpja.json")),
        "observacao": "Bases da Torre Tecar (somente leitura). Cite a data das bases ao apresentar números.",
    }


def resumo_emplacamentos(b: Bases, agrupar_por: list[str] | str = "marca", top: int = 50, **filtros) -> dict:
    dims = [d.strip() for d in (agrupar_por.split(",") if isinstance(agrupar_por, str) else agrupar_por) if d.strip()]
    if not 1 <= len(dims) <= 3:
        raise ErroConsulta("agrupar_por aceita de 1 a 3 dimensões")
    rows = filtra(b.emplacamentos(), **filtros)
    tot, mb_tot = len(rows), sum(r["marca"] == MB for r in rows)
    g = defaultdict(lambda: [0, 0])
    for r in rows:
        k = tuple(_chave(r, d) for d in dims)
        g[k][0] += 1
        g[k][1] += r["marca"] == MB
    ordem = sorted(g.items(), key=lambda kv: (-kv[1][0], kv[0]))
    top = max(1, min(int(top), MAX_LINHAS))
    return {
        "agrupar_por": dims, "filtros": {k: v for k, v in filtros.items() if v}, "periodo_encontrado": _periodo(rows),
        "total": tot, "mercedes_benz": mb_tot, "share_mb_pct": _pct(mb_tot, tot),
        "grupos": [{**dict(zip(dims, k)), "emplacamentos": n, "pct_do_total": _pct(n, tot), "mercedes_benz": m,
                    "share_mb_pct": _pct(m, n)} for k, (n, m) in ordem[:top]],
        "grupos_omitidos": max(0, len(ordem) - top), "fonte": _fonte(b, MATRIZ),
    }


def comparar_periodos(b: Bases, a_ini: str, a_fim: str, b_ini: str, b_fim: str, agrupar_por: str = "marca",
                      top: int = 30, **filtros) -> dict:
    base = b.emplacamentos()
    pa = filtra(base, data_ini=a_ini, data_fim=a_fim, **filtros)
    pb = filtra(base, data_ini=b_ini, data_fim=b_fim, **filtros)
    ca, cb = Counter(_chave(r, agrupar_por) for r in pa), Counter(_chave(r, agrupar_por) for r in pb)
    ta, tb = len(pa), len(pb)
    linhas = []
    for k in set(ca) | set(cb):
        a, bb = ca[k], cb[k]
        linhas.append({agrupar_por: k, "periodo_a": a, "periodo_b": bb, "variacao_pct": _pct(bb - a, a),
                       "share_a_pct": _pct(a, ta), "share_b_pct": _pct(bb, tb),
                       "variacao_share_pp": round((_pct(bb, tb) or 0) - (_pct(a, ta) or 0), 2)})
    linhas.sort(key=lambda x: -x["periodo_b"])
    return {"periodo_a": {"de": _data(a_ini), "ate": _data(a_fim, True), "total": ta},
            "periodo_b": {"de": _data(b_ini), "ate": _data(b_fim, True), "total": tb},
            "variacao_mercado_pct": _pct(tb - ta, ta), "agrupar_por": agrupar_por,
            "filtros": {k: v for k, v in filtros.items() if v}, "linhas": linhas[:max(1, min(int(top), MAX_LINHAS))],
            "fonte": _fonte(b, MATRIZ)}


def buscar_emplacamentos(b: Bases, limite: int = 100, mais_recentes_primeiro: bool = True, **filtros) -> dict:
    rows = filtra(b.emplacamentos(), **filtros)
    if not any(v for v in filtros.values()):
        raise ErroConsulta("informe ao menos um filtro (período, marca, UF, CNPJ, proprietário, modelo, placa ou chassi)")
    lim = max(1, min(int(limite), MAX_LINHAS))
    sel = list(reversed(rows))[:lim] if mais_recentes_primeiro else rows[:lim]
    campos = ("data", "marca", "modelo", "tracao", "subsegmento", "placa", "chassi", "cnpj", "documento", "proprietario",
              "tipo_pessoa", "cidade", "uf", "aop", "concessionario", "ano_fabricacao", "ano_modelo", "terreno")
    return {"encontrados": len(rows), "devolvidos": len(sel), "registros": [{k: r.get(k) for k in campos} for r in sel],
            "fonte": _fonte(b, MATRIZ)}


def _janela(rows, anos):
    if not rows:
        return None
    fim = date.fromisoformat(rows[-1]["data"])
    return (fim - timedelta(days=round(365.25 * anos))).isoformat()


def cliente_360(b: Bases, cnpj_ou_nome: str, limite_veiculos: int = 60) -> dict:
    alvo = str(cnpj_ou_nome or "").strip()
    if len(alvo) < 3:
        raise ErroConsulta("informe um CNPJ (completo ou raiz de 8 dígitos) ou parte do nome")
    base = b.emplacamentos()
    doc = digitos(alvo)
    if len(doc) >= 8:
        raizes = {doc[:8]}
    else:
        nome = sem_acento(alvo)
        raizes = {r["raiz"] for r in base if r["raiz"] and nome in sem_acento(r["proprietario"])}
        crm_r = {c["raiz"] for c in b.crm()["contas"] if c["raiz"] and nome in sem_acento(c["nome"])}
        raizes |= crm_r
    if not raizes:
        return {"encontrado": False, "busca": alvo}
    if len(raizes) > 15:
        raise ErroConsulta(f"{len(raizes)} grupos encontrados; refine o nome ou informe o CNPJ")
    ref12, ref36 = _janela(base, 1), _janela(base, 3)
    cad = (b.json(f"{ASSOBENS}/empresas_cnpja.json", {}) or {}).get("empresas", {})
    contas = []
    for rz in sorted(raizes):
        rs = [r for r in base if r["raiz"] == rz]
        crm = [c for c in b.crm()["contas"] if c["raiz"] == rz]
        por_ano = defaultdict(Counter)
        for r in rs:
            por_ano[r["data"][:4]][r["marca"]] += 1
        u12 = [r for r in rs if r["data"] >= ref12]
        u36 = [r for r in rs if r["data"] >= ref36]
        nomes = Counter(r["proprietario"] for r in rs) + Counter(c["nome"] for c in crm)
        contas.append({
            "raiz_cnpj": rz, "nome": nomes.most_common(1)[0][0] if nomes else "",
            "cnpjs": sorted({r["cnpj"] for r in rs} | {c["cnpj"] for c in crm}),
            "emplacamentos_total": len(rs), "ultimos_12m": len(u12), "ultimos_36m": len(u36),
            "mercedes_benz_total": sum(r["marca"] == MB for r in rs),
            "share_mb_36m_pct": _pct(sum(r["marca"] == MB for r in u36), len(u36)),
            "primeira_compra": rs[0]["data"] if rs else None, "ultima_compra": rs[-1]["data"] if rs else None,
            "por_ano_marca": {a: dict(c) for a, c in sorted(por_ano.items())},
            "modelos": Counter(r["modelo"] for r in rs).most_common(10),
            "subsegmentos": Counter(r["subsegmento"] for r in rs).most_common(),
            "cidades": Counter(r["cidade"] + "/" + r["uf"] for r in rs).most_common(8),
            "concessionarios": Counter(r["concessionario"] for r in rs).most_common(8),
            "crm": [{k: c[k] for k in ("cnpj", "nome", "casa", "responsavel", "papel", "temperatura", "classificacao",
                                       "segmento", "municipio", "uf")} for c in crm],
            "cadastro_receita": {c: cad[c] for c in sorted({r["cnpj"] for r in rs}) if c in cad},
            "veiculos_recentes": [{k: r[k] for k in ("data", "marca", "modelo", "placa", "chassi", "cnpj", "cidade", "uf",
                                                     "concessionario")} for r in reversed(rs[-max(1, min(limite_veiculos, 300)):])],
        })
    return {"encontrado": True, "busca": alvo, "janela_12m_desde": ref12, "contas": contas,
            "fonte": _fonte(b, MATRIZ, TORRE_HTML)}


def carteira_por_responsavel(b: Bases, casa: str | None = None, responsavel: str | None = None) -> dict:
    base = b.emplacamentos()
    ref12, ref60 = _janela(base, 1), _janela(base, 5)
    por_raiz = defaultdict(list)
    for r in base:
        if r["raiz"]:
            por_raiz[r["raiz"]].append(r)
    agrupado = defaultdict(lambda: {"cadastros": 0, "raizes": set(), "casas": set(), "papel": ""})
    for c in b.crm()["contas"]:
        if c["tipo"] != "PJ" or not c["raiz"] or not c["responsavel"]:
            continue
        if casa and sem_acento(casa) not in sem_acento(c["casa"]):
            continue
        if responsavel and sem_acento(responsavel) not in sem_acento(c["responsavel"]):
            continue
        a = agrupado[c["responsavel"]]
        a["cadastros"] += 1
        a["raizes"].add(c["raiz"])
        a["casas"].add(c["casa"])
        a["papel"] = c["papel"]
    linhas = []
    for nome, a in agrupado.items():
        rs = [r for rz in a["raizes"] for r in por_raiz.get(rz, [])]
        r12 = [r for r in rs if r["data"] >= ref12]
        tecar12 = [r for r in r12 if "TECAR" in sem_acento(r["concessionario"])]
        compradoras = {r["raiz"] for r in r12}
        linhas.append({"responsavel": nome, "papel": a["papel"], "casas": sorted(a["casas"]), "clientes_pj": a["cadastros"],
                       "raizes_cnpj": len(a["raizes"]), "raizes_que_compraram_12m": len(compradoras),
                       "mercado_12m": len(r12), "mercado_5a": sum(r["data"] >= ref60 for r in rs),
                       "mercedes_benz_12m": sum(r["marca"] == MB for r in r12),
                       "vendas_tecar_12m": len(tecar12), "share_tecar_12m_pct": _pct(len(tecar12), len(r12))})
    linhas.sort(key=lambda x: -x["mercado_12m"])
    # Um mesmo CNPJ pode estar com mais de um responsável (vendedor + SDR, duas casas): somar as linhas duplica.
    todas = set().union(*(a["raizes"] for a in agrupado.values())) if agrupado else set()
    rs = [r for rz in todas for r in por_raiz.get(rz, [])]
    r12 = [r for r in rs if r["data"] >= ref12]
    tec = sum("TECAR" in sem_acento(r["concessionario"]) for r in r12)
    total = {"responsaveis": len(linhas), "raizes_cnpj": len(todas), "raizes_que_compraram_12m": len({r["raiz"] for r in r12}),
             "mercado_12m": len(r12), "mercado_5a": sum(r["data"] >= ref60 for r in rs),
             "mercedes_benz_12m": sum(r["marca"] == MB for r in r12), "vendas_tecar_12m": tec,
             "share_tecar_12m_pct": _pct(tec, len(r12))}
    soma = {k: sum(l[k] for l in linhas) for k in ("clientes_pj", "mercado_12m", "vendas_tecar_12m")}
    return {"janela_12m_desde": ref12, "crm_exportado_em": b.crm()["meta"].get("exportDate"), "linhas": linhas,
            "total_sem_duplicar": total, "soma_das_linhas_com_sobreposicao": soma,
            "atencao": "As carteiras se sobrepõem (o mesmo CNPJ pode ter mais de um responsável). Não some as linhas: "
                       "para totais e share geral use total_sem_duplicar.",
            "regra": "mercado = emplacamentos de todas as marcas nos CNPJs (raiz) da carteira; vendas Tecar = "
                     "concessionário contém TECAR", "fonte": _fonte(b, MATRIZ, TORRE_HTML)}


def buscar_crm(b: Bases, texto: str | None = None, responsavel: str | None = None, casa: str | None = None,
               temperatura: str | None = None, limite: int = 100) -> dict:
    t, rp, cs, tp = (sem_acento(x) for x in (texto, responsavel, casa, temperatura))
    dt = digitos(texto)
    out = []
    for c in b.crm()["contas"]:
        if t and not (t in sem_acento(c["nome"]) or (len(dt) >= 8 and c["cnpj"].startswith(dt))):
            continue
        if rp and rp not in sem_acento(c["responsavel"]):
            continue
        if cs and cs not in sem_acento(c["casa"]):
            continue
        if tp and tp not in sem_acento(c["temperatura"]):
            continue
        out.append(c)
    lim = max(1, min(int(limite), MAX_LINHAS))
    return {"encontrados": len(out), "contas": out[:lim], "fonte": _fonte(b, TORRE_HTML)}


def _compras(b: Bases) -> dict:
    return (b.json(f"{LICITACOES}/compras.json", {}) or {}).get("compras", {})


def _itens(b: Bases, base: str) -> list[dict]:
    return (b.json(f"{LICITACOES}/itens_{base}.json", {}) or {}).get("itens", [])


def buscar_licitacoes(b: Bases, texto: str | None = None, uf: str | None = None, municipio: str | None = None,
                      orgao: str | None = None, ano: int | None = None, situacao: str | None = None,
                      somente_abertas: bool = False, limite: int = 50) -> dict:
    t, m, o, s = (sem_acento(x) for x in (texto, municipio, orgao, situacao))
    ufs = set(_lista(uf))
    hoje = date.today().isoformat()
    out = []
    for c in _compras(b).values():
        if ufs and sem_acento(c.get("uf")) not in ufs:
            continue
        if ano and int(c.get("ano") or 0) != int(ano):
            continue
        if t and t not in sem_acento(c.get("objeto")):
            continue
        if m and m not in sem_acento(c.get("municipio")):
            continue
        if o and o not in sem_acento(c.get("orgao")) and o not in sem_acento(c.get("unidade")):
            continue
        if s and s not in sem_acento(c.get("situacao")):
            continue
        if somente_abertas and not (c.get("encerramento") or "") >= hoje:
            continue
        out.append(c)
    out.sort(key=lambda c: c.get("publicada") or "", reverse=True)
    lim = max(1, min(int(limite), MAX_LINHAS))
    return {"encontradas": len(out), "valor_estimado_total": round(sum(_num(c.get("valor_estimado")) for c in out), 2),
            "licitacoes": out[:lim], "fonte": _fonte(b, f"{LICITACOES}/compras.json")}


def itens_licitacoes(b: Bases, base: str = "veiculos", segmento: str | None = None, texto: str | None = None,
                     uf: str | None = None, ano: int | None = None, vencedor_contem: str | None = None,
                     limite: int = 100) -> dict:
    if base not in ("veiculos", "posvenda"):
        raise ErroConsulta("base deve ser 'veiculos' ou 'posvenda'")
    compras = _compras(b)
    marcas = (b.json(f"{LICITACOES}/fornecedor_marca.json", {}) or {}).get("mapa", {})
    sg, t, vc = (sem_acento(x) for x in (segmento, texto, vencedor_contem))
    ufs = set(_lista(uf))
    out, por_marca = [], Counter()
    for it in _itens(b, base):
        c = compras.get(it.get("compra"), {})
        if sg and sg not in sem_acento(it.get("seg")):
            continue
        if t and t not in sem_acento(it.get("desc")):
            continue
        if ufs and sem_acento(c.get("uf")) not in ufs:
            continue
        if ano and int(c.get("ano") or 0) != int(ano):
            continue
        venc = it.get("r") or []
        if vc and not any(vc in sem_acento(v.get("nome")) for v in venc):
            continue
        for v in venc:
            por_marca[v.get("marca_forn") or marcas.get(sem_acento(v.get("nome")), "NÃO IDENTIFICADA")] += _num(v.get("qtd"))
        out.append({**{k: it.get(k) for k in ("compra", "n", "desc", "seg", "tipo", "qtd", "un", "vu_est", "vt_est", "situacao")},
                    "orgao": c.get("orgao"), "municipio": c.get("municipio"), "uf": c.get("uf"), "publicada": c.get("publicada"),
                    "link": c.get("link"), "vencedores": venc})
    lim = max(1, min(int(limite), MAX_LINHAS))
    return {"encontrados": len(out), "quantidade_vencida_por_marca": dict(por_marca.most_common()),
            "itens": out[:lim], "fonte": _fonte(b, f"{LICITACOES}/itens_{base}.json", f"{LICITACOES}/compras.json")}


def precos(b: Bases, modelo_contem: str | None = None, marca: str | None = None, grupo_contem: str | None = None,
           desde: str | None = None, limite: int = 200) -> dict:
    mc, mk, gc = sem_acento(modelo_contem), set(_lista(marca)), sem_acento(grupo_contem)
    ds = _data(desde)
    hist = []
    for h in b.csv(f"{ASSOBENS}/precos_historico.csv"):
        if mc and mc not in sem_acento(h.get("model")):
            continue
        if mk and sem_acento(h.get("manufacturer")) not in mk:
            continue
        if gc and gc not in sem_acento(h.get("segment")):
            continue
        if ds and (h.get("reference_date") or "") < ds:
            continue
        hist.append(h)
    hist.sort(key=lambda h: h.get("reference_date") or "", reverse=True)
    lim = max(1, min(int(limite), MAX_LINHAS))
    return {"historico": hist[:lim], "encontrados": len(hist),
            "top10_com_gap_mb": b.json(f"{ASSOBENS}/precos_top10.json", {}),
            "fonte": _fonte(b, f"{ASSOBENS}/precos_historico.csv", f"{ASSOBENS}/precos_top10.json")}


def indicadores_assobens(b: Bases) -> dict:
    return {"kpis": b.json(f"{ASSOBENS}/kpis.json", {}), "top10_segmentos": b.json(f"{ASSOBENS}/top10_segmentos.json", {}),
            "conferencia": b.json(f"{ASSOBENS}/conferencia.json", {}),
            "fonte": _fonte(b, f"{ASSOBENS}/kpis.json", f"{ASSOBENS}/top10_segmentos.json")}
