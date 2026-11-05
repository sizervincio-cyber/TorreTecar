"""Leitura das bases da Torre para o MCP (somente leitura, com cache por data de modificação).

Fontes, todas dentro do checkout do repositório montado como somente leitura:
  - Analityc share/consolidado_emplacamentos_2020_2026.xlsx   matriz de emplacamentos (CNPJ, placa e chassi completos)
  - Analitycmbb.html                                          CRM embutido (CRM_META, CRM_RESP, CRM_ROWS)
  - Analityc share/assobens/*.json|csv                        status, KPIs, preços, cadastro CNPJá
  - Analityc share/licitacoes/*.json                          compras e itens do PNCP
Nada aqui grava em disco ou em banco.
"""
from __future__ import annotations

import csv
import json
import re
import threading
import unicodedata
from datetime import date, datetime
from pathlib import Path

MATRIZ = "Analityc share/consolidado_emplacamentos_2020_2026.xlsx"
TORRE_HTML = "Analitycmbb.html"
ASSOBENS = "Analityc share/assobens"
LICITACOES = "Analityc share/licitacoes"

# Cabeçalho da matriz (sem acento, maiúsculo) -> chave usada nas consultas.
COLUNAS = {
    "CHASSI": "chassi", "DATA EMPLACAMENTO": "data", "MODELO": "modelo", "TRACAO": "tracao", "MARCA": "marca",
    "SEGMENTO": "segmento", "SUBSEGMENTO": "subsegmento", "PLACA": "placa", "CONCESSIONARIO": "concessionario",
    "CIDADE": "cidade", "UF": "uf", "DEALER AOP": "dealer_aop", "AOP": "aop", "ANOFABRICACAO": "ano_fabricacao",
    "ANOMODELO": "ano_modelo", "TIPO TERRENO": "terreno", "CPFCNPJPROPRIETARIO": "documento",
    "TIPOCNPJPROPRIETARIO": "tipo_pessoa", "NOMEPROPRIETARIO": "proprietario", "COMBUSTIVEL": "combustivel",
}


def sem_acento(s) -> str:
    return unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().upper().strip()


def digitos(s) -> str:
    return re.sub(r"\D", "", str(s or ""))


def _iso(v) -> str:
    if isinstance(v, (datetime, date)):
        return v.strftime("%Y-%m-%d")
    s = str(v or "").strip()
    m = re.match(r"^(\d{2})/(\d{2})/(\d{4})", s)
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else s[:10]


class Bases:
    """Carrega cada arquivo uma vez e recarrega só quando ele muda (o contêiner atualiza-dados faz git pull)."""

    def __init__(self, raiz: Path):
        self.raiz = Path(raiz).resolve()
        self._cache: dict[str, tuple[float, object]] = {}
        self._lock = threading.Lock()

    def caminho(self, rel: str) -> Path:
        p = (self.raiz / rel).resolve()
        p.relative_to(self.raiz)  # nunca sai da raiz
        return p

    def _carrega(self, rel: str, leitor):
        p = self.caminho(rel)
        mt = p.stat().st_mtime
        with self._lock:
            hit = self._cache.get(rel)
            if hit and hit[0] == mt:
                return hit[1]
        valor = leitor(p)
        with self._lock:
            self._cache[rel] = (mt, valor)
        return valor

    def atualizado_em(self, rel: str) -> str | None:
        try:
            return datetime.fromtimestamp(self.caminho(rel).stat().st_mtime).isoformat(timespec="seconds")
        except FileNotFoundError:
            return None

    # ---------- matriz ----------
    def emplacamentos(self) -> list[dict]:
        return self._carrega(MATRIZ, _le_matriz)

    # ---------- CRM embutido na Torre ----------
    def crm(self) -> dict:
        return self._carrega(TORRE_HTML, _le_crm)

    # ---------- JSON / CSV ----------
    def json(self, rel: str, padrao=None):
        try:
            return self._carrega(rel, lambda p: json.loads(p.read_text(encoding="utf-8-sig")))
        except FileNotFoundError:
            return padrao

    def csv(self, rel: str) -> list[dict]:
        try:
            return self._carrega(rel, lambda p: list(csv.DictReader(p.open(encoding="utf-8-sig", newline=""))))
        except FileNotFoundError:
            return []


def _le_matriz(p: Path) -> list[dict]:
    from openpyxl import load_workbook
    wb = load_workbook(p, read_only=True, data_only=True)
    try:
        ws = wb.worksheets[0]
        it = ws.iter_rows(values_only=True)
        cab = [COLUNAS.get(sem_acento(h)) for h in next(it)]
        out = []
        for r in it:
            if not r or not r[0]:
                continue
            o = {k: v for k, v in zip(cab, r) if k}
            o["data"] = _iso(o.get("data"))
            for k in ("chassi", "modelo", "marca", "segmento", "subsegmento", "placa", "concessionario", "cidade", "uf",
                      "dealer_aop", "aop", "terreno", "documento", "tipo_pessoa", "proprietario", "combustivel", "tracao"):
                o[k] = "" if o.get(k) is None else str(o[k]).strip()
            d = digitos(o["documento"])
            o["cnpj"] = d if o["tipo_pessoa"].upper() == "JURIDICA" and len(d) == 14 else ""
            o["raiz"] = o["cnpj"][:8]
            out.append(o)
        out.sort(key=lambda o: o["data"])
        return out
    finally:
        wb.close()


def _bloco(txt: str, nome: str):
    m = re.search(r"const " + nome + r"=(.*?);\s*\n", txt, re.S)
    return json.loads(m.group(1)) if m else None


def _le_crm(p: Path) -> dict:
    txt = p.read_text(encoding="utf-8", errors="replace")
    meta, resp, rows = _bloco(txt, "CRM_META") or {}, _bloco(txt, "CRM_RESP") or [], _bloco(txt, "CRM_ROWS") or []
    lst = lambda k, i: (meta.get(k) or [])[i] if isinstance(i, int) and 0 <= i < len(meta.get(k) or []) else ""  # noqa: E731
    contas = []
    for r in rows:
        r = list(r) + [None] * (14 - len(r))
        rp = resp[r[6]] if isinstance(r[6], int) and 0 <= r[6] < len(resp) else None
        cnpj = digitos(r[4])
        contas.append({
            "id": r[0], "casa": lst("dealers", r[1]), "tipo": "PJ" if r[2] == "J" else "PF", "nome": r[3] or "",
            "cnpj": cnpj, "raiz": cnpj[:8] if len(cnpj) == 14 else "", "temperatura": lst("temps", r[5]),
            "responsavel": rp["n"] if rp else "", "papel": rp["role"] if rp else "", "classificacao": lst("classif", r[7]),
            "segmento": lst("segs", r[8]), "municipio": lst("muns", r[9]), "uf": r[10] or "", "criado": r[11] or "",
        })
    return {"meta": {k: v for k, v in meta.items() if not isinstance(v, list) or len(v) < 50}, "responsaveis": resp,
            "contas": contas}
