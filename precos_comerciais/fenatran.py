"""Condições comerciais Fenatran: validação da tabela e consulta. Módulo puro, sem banco e sem rede.

Usado pelos dois lados, para que respondam sempre a mesma coisa:
  - API da Torre (painel "Preço Fenatran" e importador);
  - MCP somente leitura (ferramenta consultar_precos_fenatran), que lê só o snapshot gerado pela API.

Regras de negócio (PROMPT_CLAUDE_MODULO_PRECO_FENATRAN.md):
  - preços nominais das circulares, em centavos inteiros, por veículo; nada de recalcular ICMS ou aplicar desconto;
  - 7% (fábrica) e 12% (estoque CI 102) são rótulos informados pelo solicitante, pendentes de validação fiscal;
  - faixas 5–10 e 11–15 unidades; fora disso não há condição Fenatran (não inventar, não reaproveitar faixa);
  - Actros/Axor 27/27: entrega prevista fevereiro/2027 e programação SFAT/SFAD até 30/11/2026 (só para essas famílias);
  - o prazo de 30/11/2026 NÃO desliga o módulo; só o administrador ativa, desativa ou arquiva.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Sao_Paulo")
CHAVE = "fenatran_2026"
CAMPANHA_CSV = "FENATRAN_2026"
FAMILIAS = ("ACCELO", "ATEGO", "ACTROS", "AXOR")
STATUS = ("draft", "active", "inactive", "archived")
COLUNAS = ("campanha", "familia", "modelo", "modelo_busca", "ano_modelo", "up", "variante", "configuracao",
           "preco_fabrica_5_10_centavos", "preco_fabrica_11_15_centavos", "preco_estoque_5_10_centavos",
           "preco_estoque_11_15_centavos", "icms_fabrica_pct_informado_usuario", "icms_estoque_pct_informado_usuario",
           "origem_aliquotas", "source_file", "source_page")
PRECOS = ("preco_fabrica_5_10_centavos", "preco_fabrica_11_15_centavos",
          "preco_estoque_5_10_centavos", "preco_estoque_11_15_centavos")
ARQUIVOS = {"Preços Accelo e Atego.pdf": 5, "Prelos Actros e Axor.pdf": 2}   # "Prelos" é o nome real do arquivo
FAIXAS = {"5_10": (5, 10), "11_15": (11, 15)}

RE_VARIANTE = re.compile(r"^QVV[0-9A-Z]{6,14}$")
RE_ANO = re.compile(r"^\d{2}/\d{2}$")
RE_UP = re.compile(r"^UP[A-Z]$")
RE_CONFIG = re.compile(r"^\d{1,2}X\d$")
LIMITE_PADRAO, LIMITE_MAX = 50, 200

# Metadados da campanha gravados na importação (vêm das circulares e do pedido do solicitante, não inventados aqui).
METADADOS_PADRAO = {
    "nome": "Condições Comerciais Fenatran",
    "menu": "Preço Fenatran",
    "rotulos": {
        "fabrica": "Fábrica — ICMS 7%*",
        "estoque": "Estoque CI 102 — ICMS 12%*",
    },
    "aliquotas": {
        "icms_fabrica_pct": 7, "icms_estoque_pct": 12,
        "origem": "informado_pelo_solicitante_pendente_validacao_fiscal",
        "nota": "Alíquotas informadas pelo solicitante; as circulares só identificam “Fábrica” e “Estoque CI 102”. "
                "Validar enquadramento fiscal. Os preços são os nominais das circulares, sem recálculo de imposto.",
    },
    "condicoes": {
        "por_familia": {
            "ACTROS": {"anos_modelo": ["27/27"], "entrega_prevista": "fevereiro de 2027",
                       "prazo_programacao": "2026-11-30",
                       "texto": "Veículos 27/27: entrega prevista fevereiro/2027; programação e inserção SFAT/SFAD "
                                "antecipadamente até 30/11/2026."},
            "AXOR": {"anos_modelo": ["27/27"], "entrega_prevista": "fevereiro de 2027",
                     "prazo_programacao": "2026-11-30",
                     "texto": "Veículos 27/27: entrega prevista fevereiro/2027; programação e inserção SFAT/SFAD "
                              "antecipadamente até 30/11/2026."},
        },
        "gerais": [
            "Preços unitários por veículo, por faixa de quantidade do pedido; não são totais do lote.",
            "Volumes inferiores à condição Fenatran: trabalhar com estoque/programação da concessionária ou "
            "procurar o gestor responsável.",
            "Sujeito à confirmação comercial.",
        ],
    },
    "fonte": "Circulares comerciais internas do Grupo Tecar (uso interno; não emitidas pela Mercedes-Benz do Brasil)",
    "aviso_uso_interno": "Uso interno e exclusivo do Grupo Tecar. Não repassar a clientes como tabela oficial "
                         "nem a terceiros sem autorização comercial.",
}


class ErroImportacao(ValueError):
    pass


# ---------------------------------------------------------------- normalização
def sem_acento(s) -> str:
    return unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()


def norm(s) -> str:
    """'2653 LS/36' == '2653LS/36' == '2653ls / 36'. Mantém só letras, números e a barra."""
    return re.sub(r"[^0-9A-Z/]", "", sem_acento(s).upper())


def numero_base(modelo_busca: str) -> str:
    m = re.match(r"\d+", modelo_busca or "")
    return m.group(0) if m else ""


def norm_ano(v) -> str:
    """'27/27', '2027/2027', '27-27' -> '27/27'."""
    d = re.findall(r"\d+", str(v or ""))
    if len(d) == 2:
        return f"{int(d[0]) % 100:02d}/{int(d[1]) % 100:02d}"
    return str(v or "").strip()


def _casa_ano(ano_tabela: str, pedido) -> bool:
    """'26/27' exato; '2027' ou '27' = ano do MODELO 2027 (casa 26/27 e 27/27)."""
    d = re.findall(r"\d+", str(pedido or ""))
    if len(d) == 1:
        return ano_tabela.split("/")[-1] == f"{int(d[0]) % 100:02d}"
    return ano_tabela == norm_ano(pedido)


def norm_up(v) -> str:
    s = norm(v)
    return s if s.startswith("UP") else ("UP" + s if len(s) == 1 else s)


def brl(centavos: int | None) -> str | None:
    if centavos is None:
        return None
    reais, cent = divmod(int(centavos), 100)
    return f"R$ {reais:,}".replace(",", ".") + f",{cent:02d}"


# ---------------------------------------------------------------- validação da importação
def valida_linhas(linhas: list[dict]) -> tuple[list[dict], list[dict]]:
    """Valida o CSV linha a linha. Devolve (precos_normalizados, erros). Nunca descarta linha em silêncio."""
    erros, out, vistos = [], [], {}
    for n, r in enumerate(linhas, start=2):                       # linha 1 = cabeçalho
        e = []
        faltando = [c for c in COLUNAS if str(r.get(c, "") or "").strip() == ""]
        if faltando:
            e.append(f"campos vazios: {', '.join(faltando)}")
        camp = str(r.get("campanha", "")).strip()
        fam = str(r.get("familia", "")).strip().upper()
        modelo = str(r.get("modelo", "")).strip()
        ano = str(r.get("ano_modelo", "")).strip()
        up = str(r.get("up", "")).strip().upper()
        var = str(r.get("variante", "")).strip().upper()
        cfg = str(r.get("configuracao", "")).strip().upper()
        arq = str(r.get("source_file", "")).strip()
        if camp and camp != CAMPANHA_CSV:
            e.append(f"campanha {camp!r} diferente de {CAMPANHA_CSV}")
        if fam and fam not in FAMILIAS:
            e.append(f"família {fam!r} desconhecida")
        if ano and not RE_ANO.match(ano):
            e.append(f"ano/modelo {ano!r} fora do padrão AA/AA")
        if up and not RE_UP.match(up):
            e.append(f"UP {up!r} fora do padrão UPx")
        if var and not RE_VARIANTE.match(var):
            e.append(f"variante {var!r} fora do padrão QVV")
        if cfg and not RE_CONFIG.match(cfg):
            e.append(f"configuração {cfg!r} fora do padrão NxN")
        if modelo and norm(r.get("modelo_busca")) != norm(modelo):
            e.append(f"modelo_busca {r.get('modelo_busca')!r} não corresponde ao modelo {modelo!r}")
        precos = {}
        for c in PRECOS:
            v = str(r.get(c, "")).strip()
            if not re.fullmatch(r"\d+", v or "x"):
                e.append(f"{c} não é inteiro em centavos: {v!r}")
            elif int(v) <= 0:
                e.append(f"{c} precisa ser positivo")
            else:
                precos[c] = int(v)
        for c, esperado in (("icms_fabrica_pct_informado_usuario", "7"), ("icms_estoque_pct_informado_usuario", "12")):
            if str(r.get(c, "")).strip() not in (esperado, esperado + ".0", ""):
                e.append(f"{c} = {r.get(c)!r} (esperado {esperado}, informado pelo solicitante)")
        if arq and arq not in ARQUIVOS:
            e.append(f"source_file {arq!r} não é uma das circulares conhecidas")
        pag = str(r.get("source_page", "")).strip()
        if pag and (not pag.isdigit() or not 1 <= int(pag) <= ARQUIVOS.get(arq, 99)):
            e.append(f"source_page {pag!r} fora das páginas de {arq}")
        if var:
            if var in vistos:
                e.append(f"variante {var} repetida (também na linha {vistos[var]})")
            else:
                vistos[var] = n
        if e:
            erros.append({"linha": n, "variante": var or None, "erros": e})
            continue
        out.append({"familia": fam, "modelo": modelo, "modelo_busca": norm(modelo), "ano_modelo": ano, "up": up,
                    "variante": var, "configuracao": cfg, **precos, "source_file": arq, "source_page": int(pag)})
    return out, erros


def avisos_de_conteudo(precos: list[dict]) -> list[dict]:
    """Coerências esperadas que não bloqueiam (vão para revisão humana): desconto por volume e estoque ≥ fábrica."""
    avisos = []
    for p in precos:
        if p["preco_fabrica_11_15_centavos"] > p["preco_fabrica_5_10_centavos"]:
            avisos.append({"variante": p["variante"], "aviso": "fábrica 11–15 maior que 5–10"})
        if p["preco_estoque_11_15_centavos"] > p["preco_estoque_5_10_centavos"]:
            avisos.append({"variante": p["variante"], "aviso": "estoque 11–15 maior que 5–10"})
        if p["preco_estoque_5_10_centavos"] < p["preco_fabrica_5_10_centavos"]:
            avisos.append({"variante": p["variante"], "aviso": "estoque 5–10 menor que fábrica 5–10"})
    return avisos


def confere_manifesto(precos: list[dict], manifesto: dict) -> list[str]:
    """Contagem total e por família contra o manifesto de auditoria."""
    problemas = []
    if manifesto.get("campanha") and manifesto["campanha"] != CAMPANHA_CSV:
        problemas.append(f"manifesto é da campanha {manifesto['campanha']}")
    total = manifesto.get("qtd_registros")
    if total is not None and int(total) != len(precos):
        problemas.append(f"manifesto declara {total} registros; CSV válido tem {len(precos)}")
    cont = {f: sum(1 for p in precos if p["familia"] == f) for f in FAMILIAS}
    for fam, n in (manifesto.get("por_familia") or {}).items():
        if cont.get(fam, 0) != int(n):
            problemas.append(f"{fam}: manifesto {n}, CSV {cont.get(fam, 0)}")
    return problemas


def diff_precos(atual: list[dict], novo: list[dict]) -> dict:
    """Diferenças por variante entre o lote atual e o novo, para revisão humana antes de trocar a versão."""
    a, n = {p["variante"]: p for p in atual}, {p["variante"]: p for p in novo}
    campos = ("familia", "modelo", "ano_modelo", "up", "configuracao", *PRECOS)
    alterados = []
    for v in sorted(set(a) & set(n)):
        mud = {c: [a[v][c], n[v][c]] for c in campos if a[v][c] != n[v][c]}
        if mud:
            alterados.append({"variante": v, "mudancas": mud})
    return {"novas": sorted(set(n) - set(a)), "removidas": sorted(set(a) - set(n)), "alteradas": alterados}


# ---------------------------------------------------------------- consulta (painel e MCP)
def agora_sp() -> datetime:
    return datetime.now(TZ)


def campanha_vigente(snap: dict | None, agora: datetime | None = None) -> tuple[bool, str]:
    """(visível, status efetivo). Só 'active' e não expirada é visível. Expiração é opcional e do administrador."""
    if not snap or not snap.get("campanha"):
        return False, "indisponivel"
    c = snap["campanha"]
    st = c.get("status", "draft")
    if st != "active":
        return False, st
    exp = c.get("expira_em")
    if exp:
        try:
            limite = datetime.fromisoformat(exp)
            if limite.tzinfo is None:
                limite = limite.replace(tzinfo=TZ)
            if (agora or agora_sp()) >= limite:
                return False, "expirada"
        except ValueError:
            return False, "expiracao_invalida"
    return True, "active"


def _familia_na_busca(texto: str) -> tuple[str, str | None]:
    """Tira da busca palavras de família/marca ('Actros 2653' -> ('2653', 'ACTROS'))."""
    palavras = sem_acento(texto).upper().replace("-", " ").split()
    fam = next((p for p in palavras if p in FAMILIAS), None)
    resto = [p for p in palavras if p not in FAMILIAS and p not in ("MB", "MERCEDES", "BENZ", "MERCEDESBENZ", "PRECO",
                                                                      "FENATRAN", "DO", "DA", "O", "A")]
    return " ".join(resto), fam


def _casa_modelo(p: dict, q: str) -> str | None:
    """Critério da correspondência (mais forte primeiro) ou None."""
    nq = norm(q)
    if not nq:
        return None
    if p["modelo_busca"] == nq:
        return "modelo_completo"
    if nq.isdigit():
        return "numero_base" if numero_base(p["modelo_busca"]) == nq else None
    return "modelo_parcial" if p["modelo_busca"].startswith(nq) else None


ORDEM_CRITERIO = {"variante_exata": 0, "modelo_completo": 1, "modelo_parcial": 2, "numero_base": 3, "filtros": 4}


def _faixa(qtd: int | None) -> tuple[str | None, bool]:
    if qtd is None:
        return None, True
    for k, (a, b) in FAIXAS.items():
        if a <= qtd <= b:
            return k, True
    return None, False


def consultar(snap: dict | None, *, modelo: str | None = None, familia: str | None = None,
              ano_modelo: str | None = None, up: str | None = None, variante: str | None = None,
              configuracao: str | None = None, quantidade: int | None = None, origem: str | None = "ambos",
              calcular_total: bool = False, listar_todos: bool = False, limite: int = LIMITE_PADRAO,
              pagina: int = 1, agora: datetime | None = None, incluir_rascunho: bool = False) -> dict:
    """Consulta da tabela Fenatran. Devolve sempre um dicionário com status_consulta; nunca levanta para filtro ruim.

    incluir_rascunho: só o painel, para administradores conferirem uma campanha em rascunho. O MCP nunca usa."""
    agora = agora or agora_sp()
    c = (snap or {}).get("campanha") or {}
    meta = {**METADADOS_PADRAO, **(c.get("metadados") or {})}
    base = {
        "fonte": meta["fonte"], "campanha": {"chave": c.get("chave", CHAVE), "nome": meta["nome"]},
        "versao": c.get("versao"), "status": c.get("status", "indisponivel"),
        "consultado_em": agora.astimezone(TZ).isoformat(timespec="seconds"),
        "aviso_uso_interno": meta["aviso_uso_interno"],
    }
    visivel, st_efetivo = campanha_vigente(snap, agora)
    if not visivel and not (incluir_rascunho and st_efetivo == "draft"):
        return {**base, "status": st_efetivo, "status_consulta": "campanha_inativa",
                "mensagem": "A tabela Fenatran não está ativa para consulta. Procure o gestor comercial.",
                "total_encontrado": 0, "resultados_exibidos": 0, "resultados": []}

    origem = (origem or "ambos").strip().lower()
    if origem not in ("fabrica", "estoque", "ambos"):
        return {**base, "status_consulta": "filtro_invalido", "mensagem": "origem deve ser fabrica, estoque ou ambos",
                "total_encontrado": 0, "resultados_exibidos": 0, "resultados": []}
    filtros = {k: v for k, v in dict(modelo=modelo, familia=familia, ano_modelo=ano_modelo, up=up, variante=variante,
                                     configuracao=configuracao, quantidade=quantidade).items() if v not in (None, "")}
    if not filtros and not listar_todos:
        return {**base, "status_consulta": "filtro_obrigatorio",
                "mensagem": "Informe ao menos um filtro (modelo, família, ano/modelo, UP, variante ou configuração) "
                            "ou peça explicitamente a lista completa (listar_todos).",
                "total_encontrado": 0, "resultados_exibidos": 0, "resultados": []}

    precos = list((snap or {}).get("precos") or [])
    criterio_global = "filtros"
    fam_q = familia.strip().upper() if familia else None
    if fam_q and fam_q not in FAMILIAS:
        fam_q = norm(fam_q)
    q_modelo = None
    if modelo:
        resto, fam_txt = _familia_na_busca(modelo)
        if fam_txt and not fam_q:
            fam_q = fam_txt
        q_modelo = resto.strip()
        if RE_VARIANTE.match(norm(q_modelo)) and not variante:
            variante, q_modelo = norm(q_modelo), None

    sel = []
    for p in precos:
        crit = "filtros"
        if variante:
            if p["variante"] != norm(variante):
                continue
            crit = "variante_exata"
        if q_modelo:
            cm = _casa_modelo(p, q_modelo)
            if cm is None:
                continue
            crit = cm if crit == "filtros" else crit
        if fam_q and p["familia"] != fam_q:
            continue
        if ano_modelo and not _casa_ano(p["ano_modelo"], ano_modelo):
            continue
        if up and p["up"] != norm_up(up):
            continue
        if configuracao and p["configuracao"] != norm(configuracao):
            continue
        sel.append((crit, p))

    # prioridade: variante exata > modelo completo > modelo parcial > número-base; mantém só o melhor nível
    if sel:
        melhor = min(ORDEM_CRITERIO[c] for c, _ in sel)
        sel = [(c, p) for c, p in sel if ORDEM_CRITERIO[c] == melhor]
        criterio_global = sel[0][0]
    sel.sort(key=lambda cp: (FAMILIAS.index(cp[1]["familia"]), cp[1]["modelo_busca"], cp[1]["ano_modelo"],
                             cp[1]["up"], cp[1]["variante"]))

    faixa, qtd_ok = _faixa(quantidade)
    total = len(sel)
    limite = max(1, min(int(limite or LIMITE_PADRAO), LIMITE_MAX))
    pagina = max(1, int(pagina or 1))
    janela = sel[(pagina - 1) * limite: pagina * limite]
    rot = meta["rotulos"]
    resultados = []
    for _, p in janela:
        item = {k: p[k] for k in ("familia", "modelo", "ano_modelo", "up", "variante", "configuracao",
                                   "source_file", "source_page")}
        item["status_validacao_fiscal"] = "pendente — alíquotas informadas pelo solicitante"
        if qtd_ok:
            item["precos"] = _precos_item(p, origem, rot)
            if faixa:
                item["faixa_aplicavel"] = {"faixa": faixa.replace("_", "–") + " unidades", "quantidade": quantidade,
                                           **{o: _preco_faixa(p, o, faixa, quantidade, calcular_total)
                                              for o in (("fabrica", "estoque") if origem == "ambos" else (origem,))}}
        resultados.append(item)

    dup = {}
    for _, p in sel:
        dup.setdefault(tuple(p[k] for k in PRECOS), []).append(p["variante"])
    duplicidades = [{"variantes": v, "observacao": "variantes distintas com os mesmos quatro preços"}
                    for v in dup.values() if len(v) > 1]

    familias = sorted({p["familia"] for _, p in sel}, key=FAMILIAS.index)
    resp = {
        **base, "status_consulta": "ok" if total else "sem_resultados",
        "filtros_aplicados": {**filtros, "origem": origem, **({"familia_interpretada": fam_q} if fam_q and not familia else {})},
        "criterio": criterio_global if total else None,
        "total_encontrado": total, "resultados_exibidos": len(resultados), "pagina": pagina, "limite": limite,
        "familias_encontradas": familias, "resultados": resultados, "duplicidades_de_preco": duplicidades,
        "condicoes_comerciais": _condicoes(meta, familias, agora), "restricoes": _restricoes(meta, origem),
    }
    if c.get("status") == "draft":
        resp["previa_rascunho"] = True
        resp["aviso_rascunho"] = "Campanha em rascunho: prévia só para administradores, não publicada."
    if not qtd_ok:
        resp["status_consulta"] = "quantidade_fora_condicao_fenatran"
        resp["mensagem"] = (f"Não há condição Fenatran cadastrada para {quantidade} unidade(s); as faixas são 5–10 e "
                            "11–15. Consultar gestor/comercial (estoque ou programação da concessionária).")
    if total and q_modelo and criterio_global == "numero_base" and len(familias) > 1:
        resp["aviso_familias"] = "O número procurado aparece em mais de uma família; confira a família de cada linha."
    if total > len(resultados) + (pagina - 1) * limite:
        resp["proxima_pagina"] = pagina + 1
    return resp


def _precos_item(p: dict, origem: str, rot: dict) -> dict:
    out = {}
    for o in (("fabrica", "estoque") if origem == "ambos" else (origem,)):
        out[o] = {"rotulo": rot[o]}
        for f in FAIXAS:
            cent = p[f"preco_{o}_{f}_centavos"]
            out[o][f] = {"faixa": f.replace("_", "–") + " unidades", "centavos": cent, "valor": brl(cent)}
    return out


def _preco_faixa(p: dict, o: str, faixa: str, qtd: int, total: bool) -> dict:
    cent = p[f"preco_{o}_{faixa}_centavos"]
    d = {"unitario_centavos": cent, "unitario": brl(cent)}
    if total:
        d["total_centavos"] = cent * qtd
        d["total"] = brl(cent * qtd)
        d["total_observacao"] = f"{qtd} × preço unitário (calculado a pedido)"
    return d


def _condicoes(meta: dict, familias: list[str], agora: datetime) -> dict:
    cond = meta.get("condicoes") or {}
    out = {"gerais": list(cond.get("gerais") or []), "por_familia": {}}
    for f in familias:
        c = (cond.get("por_familia") or {}).get(f)
        if not c:
            continue
        item = dict(c)
        prazo = c.get("prazo_programacao")
        if prazo:
            vencido = agora.date() > date.fromisoformat(prazo)
            item["prazo_programacao_vencido"] = vencido
            if vencido:
                item["alerta"] = (f"Prazo de programação SFAT/SFAD ({date.fromisoformat(prazo):%d/%m/%Y}) encerrado: "
                                  "validar com o comercial antes de oferecer esta condição.")
        out["por_familia"][f] = item
    return out


def _restricoes(meta: dict, origem: str) -> list[str]:
    al = meta.get("aliquotas") or {}
    r = [al.get("nota", ""), "Faixas válidas: 5–10 e 11–15 unidades por pedido; fora delas não há preço Fenatran.",
         "“Estoque CI 102” é a origem indicada na circular; não significa pronta disponibilidade."]
    if origem != "ambos":
        r.append(f"Mostrando só a origem {origem}; peça 'ambos' para ver fábrica e estoque.")
    return [x for x in r if x]


# ---------------------------------------------------------------------------------------------------------------------
# Contrato da ferramenta MCP consultar_precos_fenatran (somente leitura). Reaproveita consultar(); não recalcula imposto.

ORIGENS_MCP = {"todas": "ambos", "fabrica": "fabrica", "estoque_ci102": "estoque", "estoque": "estoque",
               "concessionario": "ambos"}
MODALIDADES = ("fabrica", "estoque_ci102", "concessionario")
JUSTIFICATIVA_CONCESSIONARIO = ("As circulares Fenatran trazem só preço Fábrica e Estoque CI 102; não existe preço "
                                "'concessionário' cadastrado. Não estimar: consultar o gestor comercial.")
_RE_SEPARA = re.compile(r"\s*(?:,|;|\+|\b[EeOo][Uu]?\b(?=\s))\s*")


def _decimal(centavos: int) -> str:
    """Centavos inteiros -> '123456.78' (sem ponto flutuante)."""
    reais, cent = divmod(int(centavos), 100)
    return f"{reais}.{cent:02d}"


def _partes_modelo(modelo: str, versao: str | None) -> list[str]:
    """'Axor 2545 LS e S' -> ['Axor 2545 LS', 'Axor 2545 S']; versao='LS' + '2545' -> ['2545 LS']."""
    texto = (modelo or "").strip()
    if versao:
        texto = f"{texto} {versao.strip()}"
    pedacos = [p for p in _RE_SEPARA.split(texto) if p and p.strip()]
    if len(pedacos) <= 1:
        return [texto]
    m = re.search(r"\d{3,4}", pedacos[0])
    prefixo = pedacos[0][: m.end()] if m else ""
    return [p if re.search(r"\d", p) or not prefixo else f"{prefixo} {p}" for p in pedacos]


def consultar_mcp(snap: dict | None, *, modelo: str | None, quantidade: int | None = None,
                  versao: str | None = None,
                  origem: str | None = "todas", configuracao: str | None = None, ano_modelo: str | None = None,
                  up: str | None = None, agora: datetime | None = None, fonte_erro: str | None = None,
                  icms: float | None = None, uf: str | None = None, familia: str | None = None,
                  variante: str | None = None) -> dict:
    """Resposta padronizada para o ChatGPT/Codex: faixa escolhida pela quantidade, unitário e total do lote em
    decimal exato por origem, fonte documental e restrições. fonte_erro: falha ao ler o snapshot (não é 'sem modelo')."""
    agora = agora or agora_sp()
    base = {"fonte": "FENATRAN", "quantidade_solicitada": quantidade,
            "consultado_em": agora.astimezone(TZ).isoformat(timespec="seconds")}
    if fonte_erro or not snap or not snap.get("campanha"):
        return {**base, "status": "indisponivel", "status_consulta": "fonte_indisponivel", "resultados": [],
                "mensagem": "A base Fenatran não pôde ser lida agora (falha de integração, não ausência do modelo). "
                            "Não use outra fonte de preço; tente de novo ou consulte o painel da Torre.",
                **({"detalhe_erro": fonte_erro} if fonte_erro else {})}
    pedida = sem_acento((origem or "todas").strip().lower())
    o = ORIGENS_MCP.get(pedida)
    if o is None:
        return {**base, "status_consulta": "filtro_invalido", "resultados": [],
                "mensagem": "modalidade deve ser fabrica, estoque_ci102, concessionario ou todas"}
    pedida = {"estoque": "estoque_ci102"}.get(pedida, pedida)
    selecao_por_icms = None
    if icms is not None and pedida == "todas":         # ICMS identifica a condição cadastrada; nunca recalcula preço
        al = {**METADADOS_PADRAO["aliquotas"], **((((snap.get("campanha") or {}).get("metadados") or {})
                                                   .get("aliquotas")) or {})}
        if icms == al.get("icms_fabrica_pct"):
            pedida, o, selecao_por_icms = "fabrica", "fabrica", f"ICMS {icms:g}% → condição Fábrica"
        elif icms == al.get("icms_estoque_pct"):
            pedida, o, selecao_por_icms = "estoque_ci102", "estoque", f"ICMS {icms:g}% → condição Estoque CI 102"
    mods = MODALIDADES if pedida == "todas" else (pedida,)
    if not any((x or "").strip() for x in (modelo, familia, variante, configuracao)):
        return {**base, "status_consulta": "filtro_obrigatorio", "resultados": [],
                "mensagem": "Informe modelo, família, variante (QVV) ou configuração."}

    vistos, itens, ultimo = set(), [], None
    partes = _partes_modelo(modelo, versao) if (modelo or "").strip() else [None]
    for parte in partes:
        r = consultar(snap, modelo=parte, quantidade=quantidade, origem=o, configuracao=configuracao,
                      ano_modelo=ano_modelo, up=up, familia=familia, variante=variante, calcular_total=True,
                      limite=LIMITE_MAX, agora=agora)
        ultimo = r
        if r["status_consulta"] not in ("ok",):
            if r["status_consulta"] in ("campanha_inativa", "quantidade_fora_condicao_fenatran", "filtro_invalido"):
                break
            continue
        for it in r["resultados"]:
            if it["variante"] not in vistos:
                vistos.add(it["variante"])
                itens.append((it, r))
    r0 = ultimo or {}
    if selecao_por_icms:
        base["selecao_por_icms"] = selecao_por_icms
    out = {**base, "status": {"active": "ativo"}.get(r0.get("status"), r0.get("status")),
           "versao_tabela": r0.get("versao"), "aviso_uso_interno": r0.get("aviso_uso_interno")}
    st = r0.get("status_consulta")
    if st == "campanha_inativa":
        return {**out, "status_consulta": "campanha_inativa", "resultados": [], "mensagem": r0.get("mensagem")}
    if st == "quantidade_fora_condicao_fenatran":
        return {**out, "status_consulta": st, "faixa_aplicada": None, "resultados": [], "mensagem": r0.get("mensagem")}
    if st == "filtro_invalido":
        return {**out, "status_consulta": st, "resultados": [], "mensagem": r0.get("mensagem")}
    faixa, _ = _faixa(quantidade)
    rot_faixa = faixa.replace("_", "-") if faixa else None
    if not itens:
        num = re.search(r"\d{3,4}", modelo or "")
        todos = sorted({(p["familia"], p["modelo"]) for p in snap.get("precos") or []})
        alt = [f"{f} {m}" for f, m in todos if num and numero_base(norm(m))[:2] == num.group(0)[:2]][:12]
        return {**out, "status_consulta": "sem_resultados", "faixa_aplicada": rot_faixa,
                "resultados": [], "alternativas_cadastradas": alt,
                "mensagem": f"Nenhuma variante Fenatran para '{modelo or familia or variante or configuracao}'. A tabela "
                            "está ativa e só contém Mercedes-Benz Accelo, Atego, Actros e Axor. As alternativas "
                            "listadas são só modelos cadastrados com numeração próxima: não são equivalentes "
                            "comerciais e não têm preço presumido."}
    resultados, familias = [], []
    for it, r in itens:
        precos = {}
        for nome, chave in (("fabrica", "fabrica"), ("estoque_ci102", "estoque")):
            if nome not in mods:
                continue
            fx = (it.get("faixa_aplicavel") or {}).get(chave)
            if fx:
                precos[nome] = {"unitario": _decimal(fx["unitario_centavos"]), "unitario_brl": fx["unitario"],
                                "total_lote": _decimal(fx["total_centavos"]), "total_lote_brl": fx["total"]}
            elif quantidade is None and (it.get("precos") or {}).get(chave):
                # sem quantidade: as duas faixas, só unitário (total do lote depende da quantidade)
                precos[nome] = {f.replace("_", "-"): {"unitario": _decimal(v["centavos"]), "unitario_brl": v["valor"]}
                                for f, v in it["precos"][chave].items() if isinstance(v, dict) and "centavos" in v}
        if "concessionario" in mods:
            precos["concessionario"] = {"status": "indisponivel", "justificativa": JUSTIFICATIVA_CONCESSIONARIO}
        resultados.append({"modelo": it["modelo"], "familia": it["familia"], "ano_modelo": it["ano_modelo"],
                           "up": it["up"], "qvv": it["variante"], "configuracao": it["configuracao"],
                           "precos": precos, "fonte_documental": it["source_file"], "pagina": it["source_page"],
                           "status_validacao_fiscal": it["status_validacao_fiscal"]})
        if it["familia"] not in familias:
            familias.append(it["familia"])
    cond = _condicoes({**METADADOS_PADRAO, **(((snap or {}).get("campanha") or {}).get("metadados") or {})},
                      familias, agora)
    extra = {} if quantidade is not None else {
        "observacao_quantidade": "Quantidade não informada: mostrando o preço unitário das duas faixas (5-10 e "
                                 "11-15 unidades). Para o total do lote, informe a quantidade."}
    return {**out, **extra, "status_consulta": "ok", "faixa_aplicada": rot_faixa,
            "total_encontrado": len(resultados), "resultados": resultados,
            "condicoes_comerciais": cond, "restricoes": r0.get("restricoes", []),
            "condicoes_tributarias": _tributos(snap, icms, uf),
            "disponibilidade": "Preço não implica veículo disponível; confirmar estoque/programação com o comercial.",
            "atualizacao": {"versao_tabela": r0.get("versao"),
                            "expira_em": ((snap.get("campanha") or {}).get("expira_em"))}}


def _tributos(snap: dict, icms: float | None, uf: str | None) -> dict:
    meta = ((snap.get("campanha") or {}).get("metadados") or {})
    al = {**METADADOS_PADRAO["aliquotas"], **(meta.get("aliquotas") or {})}
    d = {"icms_fabrica_pct": al.get("icms_fabrica_pct"), "icms_estoque_ci102_pct": al.get("icms_estoque_pct"),
         "origem_aliquotas": al.get("origem"), "nota": al.get("nota"),
         "regra": "Preços nominais das circulares; a ferramenta não recalcula ICMS nem aplica regra por UF."}
    if icms is not None:
        d["icms_informado_na_pergunta"] = icms
        if icms not in (al.get("icms_fabrica_pct"), al.get("icms_estoque_pct")):
            d["aviso_icms"] = (f"ICMS {icms}% não corresponde às alíquotas cadastradas (fábrica "
                               f"{al.get('icms_fabrica_pct')}%, estoque {al.get('icms_estoque_pct')}%); nenhum preço "
                               "foi recalculado.")
    if uf:
        d["uf_informada"] = uf.strip().upper()[:2]
        d["aviso_uf"] = "A tabela Fenatran não diferencia preço por UF."
    return d
