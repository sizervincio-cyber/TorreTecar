"""Órgãos-alvo: compradores públicos que emplacaram caminhão na base ASSOBENS desde 01/2021.

Servem de régua e de atalho de busca. Um órgão federal com sede fora da região (ex.: CODEVASF, sede no DF) compra
centralizado e entrega em GO, MT e TO; a varredura por UF do órgão nunca acha essas compras. Buscando pelo CNPJ de
quem emplacou, elas aparecem.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict

from . import catalogo, config

# Mesma lista de palavras que a Torre usa para marcar "setor público provável" (PUBLIC_WORDS em Analitycmbb.html)
PUBLICO = re.compile(r"PREFEITURA|MUNICIPIO|GOVERNO|SECRETARIA|CAMARA MUNICIPAL|FUNDO MUNICIPAL|MINISTERIO|POLICIA|"
                     r"CORPO DE BOMBEIROS|EXERCITO|UNIVERSIDADE FEDERAL|INSTITUTO FEDERAL|"
                     r"COMPANHIA DE DESENVOLVIMENTO DOS VALES|CODEVASF|DEPARTAMENTO|AGENCIA|"
                     r"CONSORCIO (?:PUBLICO|INTERMUNICIPAL|DE MUNICIPIOS)")   # "Consórcio Limpa Gyn" é concessionária privada


def cnpj_matriz(raiz: str) -> str:
    """CNPJ da matriz (/0001) a partir da raiz de 8 dígitos, com os dígitos verificadores."""
    base = re.sub(r"\D", "", raiz)[:8].zfill(8) + "0001"
    for pesos in ((5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2), (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)):
        r = sum(int(d) * p for d, p in zip(base, pesos)) % 11
        base += str(0 if r < 2 else 11 - r)
    return base


def por_matriz(alvos: dict[str, dict]) -> dict[str, dict]:
    """Agrupa filiais pela matriz: o órgão emplaca pela filial (ex.: superintendência) e licita pela matriz."""
    out: dict[str, dict] = {}
    for cnpj, v in alvos.items():
        m = cnpj_matriz(cnpj[:8])
        e = out.setdefault(m, {"nome": v["nome"], "n": 0, "filiais": []})
        e["n"] += v["n"]
        e["filiais"].append(cnpj)
    return dict(sorted(out.items(), key=lambda kv: -kv[1]["n"]))


def alvos_emplacamento(path=None, desde: str = "2021-01-01", minimo: int = 1) -> dict[str, dict]:
    """CNPJ (14 dígitos) → {nome, n, anos, ufs, marcas} dos compradores públicos com emplacamento desde `desde`."""
    import openpyxl
    p = path or config.MATRIZ_PATH
    if not p.exists():
        return {}
    ws = openpyxl.load_workbook(p, read_only=True).worksheets[0]
    head = [str(h or "").strip() for h in next(ws.iter_rows(max_row=1, values_only=True))]
    i_doc, i_tipo, i_nome = head.index("CPFCNPJPROPRIETARIO"), head.index("TIPOCNPJPROPRIETARIO"), head.index("NOMEPROPRIETARIO")
    i_data, i_uf, i_marca = head.index("DATA EMPLACAMENTO"), head.index("UF"), head.index("MARCA")
    acc: dict[str, dict] = defaultdict(lambda: {"nome": "", "n": 0, "anos": Counter(), "ufs": Counter(), "marcas": Counter(),
                                                "ano_uf": Counter(), "mb_ano_uf": Counter(), "ultimo": ""})
    for r in ws.iter_rows(min_row=2, values_only=True):
        d = str(r[i_data] or "")[:10]
        if d < desde or str(r[i_tipo] or "").upper() != "JURIDICA":
            continue
        nome = catalogo.norm(r[i_nome])
        if not PUBLICO.search(nome):
            continue
        cnpj = re.sub(r"\D", "", str(r[i_doc] or ""))
        if len(cnpj) != 14:
            continue
        a = acc[cnpj]
        a["nome"], a["n"] = a["nome"] or str(r[i_nome]), a["n"] + 1
        a["anos"][d[:4]] += 1
        a["ufs"][str(r[i_uf] or "")] += 1
        a["marcas"][str(r[i_marca] or "")] += 1
        chave = f"{d[:4]}|{r[i_uf] or ''}"           # para a Torre filtrar a régua por período (ano) e UF
        a["ano_uf"][chave] += 1
        if str(r[i_marca] or "") == "M.BENZ":
            a["mb_ano_uf"][chave] += 1
        a["ultimo"] = max(a["ultimo"], d)
    return {k: {"nome": v["nome"], "n": v["n"], "anos": dict(v["anos"]), "ufs": dict(v["ufs"]), "marcas": dict(v["marcas"]),
                "ano_uf": dict(v["ano_uf"]), "mb_ano_uf": dict(v["mb_ano_uf"]), "ultimo": v["ultimo"]}
            for k, v in sorted(acc.items(), key=lambda kv: -kv[1]["n"]) if v["n"] >= minimo}
