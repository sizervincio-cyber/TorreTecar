"""AssobensPriceAnalysisService: Top 10 por segmento (derivado dos emplacamentos) x Comparativo de Preços.

Histórico de preços append-only (precos_historico.csv):
  source, manufacturer, model, segment, price, reference_date, captured_at
Chave de idempotência: (source, manufacturer, model, segment, reference_date) — mesma captura no mesmo dia
com preço diferente ATUALIZA a linha; igual não duplica.

Equivalências MB só vêm de equivalencias_mb.json. Sem cadastro => equivalente_mb = null,
observação "equivalência não cadastrada". Nunca se inventa equivalência nem preço.
"""
from __future__ import annotations

import csv
import os
import re
import tempfile
import unicodedata
from datetime import date, datetime
from pathlib import Path

from . import config
from .kpi import AssobensKpiService, last_12_months
from .normalizer import normalize_brand
from .runlog import read_json

PRICE_FIELDS = ["source", "manufacturer", "model", "segment", "price", "reference_date", "captured_at"]


def model_tokens(model: str) -> set[str]:
    """Códigos numéricos do modelo: 'VW/DELIVERY 11.180' -> {'11180'}; 'VOLVO/FH 540 6X4T' -> {'540'}; 'MB 1117' -> {'1117'}."""
    s = (model or "").upper().replace(".", "")
    return {t for t in re.findall(r"\d{3,}", s)}


def model_key(manufacturer: str, model: str) -> str:
    """Chave de casamento entre ranking e tabela de preços: sem marca no prefixo, sem acento/pontuação."""
    s = unicodedata.normalize("NFD", f"{model or ''}").upper()
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"^(M\.?BENZ|MERCEDES[- ]BENZ|VW|VOLKSWAGEN|VOLVO|SCANIA|IVECO|DAF|FORD|FOTON|HYUNDAI|HYUNDA|JAC|AGRALE|AGRAL)\s*[/ -]\s*", "", s.strip())
    return re.sub(r"[^A-Z0-9]", "", s)


class PriceHistory:
    def __init__(self, path: Path | None = None):
        self.path = Path(path or config.PRECOS_HIST_PATH)

    def read(self) -> list[dict]:
        if not self.path.exists():
            return []
        with open(self.path, encoding="utf-8", newline="") as f:
            return [dict(r) for r in csv.DictReader(f)]

    def upsert(self, captures: list[dict]) -> int:
        """Insere/atualiza capturas. Devolve quantas linhas mudaram (novas + preço alterado)."""
        rows = self.read()
        idx = {self._key(r): i for i, r in enumerate(rows)}
        changed = 0
        for c in captures:
            c = {k: ("" if c.get(k) is None else str(c.get(k))) for k in PRICE_FIELDS}
            k = self._key(c)
            i = idx.get(k)
            if i is None:
                rows.append(c)
                idx[k] = len(rows) - 1
                changed += 1
            elif rows[i]["price"] != c["price"]:
                rows[i] = c
                changed += 1
        self._write(rows)
        return changed

    def latest_by_model(self) -> dict[tuple[str, str], dict]:
        out: dict[tuple[str, str], dict] = {}
        for r in self.read():
            k = (r["manufacturer"].upper(), model_key(r["manufacturer"], r["model"]))
            if k not in out or r["reference_date"] >= out[k]["reference_date"]:
                out[k] = r
        return out

    @staticmethod
    def _key(r: dict) -> tuple:
        return (r["source"], r["manufacturer"].upper(), model_key(r["manufacturer"], r["model"]), r["segment"].upper(), r["reference_date"])

    def _write(self, rows: list[dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=self.path.name + ".", suffix=".tmp", dir=self.path.parent)
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=PRICE_FIELDS)
            w.writeheader()
            w.writerows(rows)
        os.replace(tmp, self.path)


class AssobensPriceAnalysisService:
    def __init__(self, history: PriceHistory | None = None, equivalencias_path: Path | None = None, mb_brand: str = config.MB_BRAND):
        self.history = history or PriceHistory()
        self.equivalencias_path = Path(equivalencias_path or config.EQUIVALENCIAS_PATH)
        self.mb = mb_brand
        self.kpi = AssobensKpiService(mb_brand)

    # ------------------------------------------------------------- Top 10
    def top10_por_segmento(self, rows: list[dict], ref: date | None = None, n: int = 10) -> dict:
        dates = [r["DATA EMPLACAMENTO"] for r in rows if r.get("DATA EMPLACAMENTO")]
        ref = ref or (date.fromisoformat(max(dates)) if dates else date.today())
        meses = set(last_12_months(ref))
        r12 = [r for r in rows if r.get("DATA EMPLACAMENTO", "")[:7] in meses]
        ranking = self.kpi.ranking_modelos(r12)
        return {"janela": sorted(meses), "base": len(r12), "segmentos": {s: lst[:n] for s, lst in ranking.items()}}

    # ------------------------------------------------------------- equivalências
    def equivalencias(self) -> dict[str, dict]:
        """{chave_modelo_concorrente: {"fabricante":..., "modelo":..., "equivalente_mb": "..."}}"""
        data = read_json(self.equivalencias_path, {"equivalencias": []})
        out = {}
        for e in data.get("equivalencias", []):
            out[(str(e.get("fabricante", "")).upper(), model_key(e.get("fabricante", ""), e.get("modelo", "")))] = e
        return out

    # ------------------------------------------------------------- casamento modelo x preço
    def price_index(self) -> list[dict]:
        """Últimos preços nacionais capturados, com o grupo (modelo MB) definido pelo próprio ASSOBENS."""
        latest: dict[tuple, dict] = {}
        for r in self.history.read():
            seg = r.get("segment", "")
            if not seg.lower().startswith("nacional"):
                continue
            k = (r["manufacturer"].upper(), model_key(r["manufacturer"], r["model"]), seg)
            if k not in latest or r["reference_date"] >= latest[k]["reference_date"]:
                latest[k] = r
        out = []
        for r in latest.values():
            grupo = r["segment"].split("|grupo ", 1)[1].strip() if "|grupo " in r["segment"] else None
            out.append({**r, "grupo_mb": grupo, "tokens": model_tokens(r["model"])})
        return out

    def find_price(self, index: list[dict], fabricante: str, modelo: str) -> dict | None:
        """Casa o modelo do ranking (ex.: 'VW/DELIVERY 11.180') com o rótulo do comparativo ('VW 11.180')
        pelo fabricante e pelos códigos numéricos do modelo. Sem casamento inequívoco => None."""
        fab = normalize_brand(fabricante)
        toks = model_tokens(modelo)
        if not toks:
            return None
        cands = [p for p in index if normalize_brand(p["manufacturer"]) == fab and p["tokens"] & toks]
        if not cands:
            return None
        cands.sort(key=lambda p: (-len(p["tokens"] & toks), p["reference_date"]), reverse=False)
        best = max(cands, key=lambda p: (len(p["tokens"] & toks), p["reference_date"]))
        return best

    # ------------------------------------------------------------- análise
    def analyze(self, top10: dict, captured_at: str | None = None) -> dict:
        index = self.price_index()
        eq = self.equivalencias()
        captured_at = captured_at or datetime.now(config.TZ).isoformat(timespec="seconds")
        out = {"gerado_em": captured_at, "janela": top10.get("janela"), "fonte_precos": "ASSOBENS Comparativo de Preços (Valor Indecx, Nacional)",
               "segmentos": {}}
        for seg, lst in top10.get("segmentos", {}).items():
            linhas = []
            for item in lst:
                fab, mod = item["fabricante"], item["modelo"]
                p = self.find_price(index, fab, mod)
                preco = float(p["price"]) if p and p.get("price") else None
                e = eq.get((fab.upper(), model_key(fab, mod)))
                mb_model, fonte_eq, obs = None, None, None
                if normalize_brand(fab) == self.mb:
                    mb_model, fonte_eq = (p["model"] if p else mod), "modelo Mercedes-Benz"
                elif e and e.get("equivalente_mb"):
                    mb_model, fonte_eq = e["equivalente_mb"], "equivalencias_mb.json"
                elif p and p.get("grupo_mb"):
                    mb_model, fonte_eq = p["grupo_mb"], "grupo do Comparativo ASSOBENS"
                p_mb = None
                if mb_model:
                    p_mb = self.find_price(index, self.mb, mb_model)
                    if p and p.get("grupo_mb"):  # prefere o preço MB do mesmo grupo/captura
                        same = [x for x in index if x.get("grupo_mb") == p["grupo_mb"] and normalize_brand(x["manufacturer"]) == self.mb
                                and model_tokens(x["model"]) & model_tokens(mb_model)]
                        p_mb = same[0] if same else p_mb
                preco_mb = float(p_mb["price"]) if p_mb and p_mb.get("price") else None
                if normalize_brand(fab) == self.mb:
                    preco_mb = preco
                gap_r = round(preco_mb - preco, 2) if (preco is not None and preco_mb is not None) else None
                gap_p = round((preco_mb / preco - 1) * 100, 2) if (preco and preco_mb is not None) else None
                if mb_model is None:
                    obs = "equivalência não cadastrada"
                elif preco_mb is None and normalize_brand(fab) != self.mb:
                    obs = "preço MB equivalente não capturado"
                if preco is None:
                    obs = (obs + "; " if obs else "") + "preço não identificado no comparativo"
                linhas.append({
                    "posicao": item["posicao"], "fabricante": fab, "modelo": mod,
                    "emplacamentos": item["emplacamentos"], "market_share": item["market_share"],
                    "preco_identificado": preco, "modelo_no_comparativo": p["model"] if p else None,
                    "preco_mb_equivalente": preco_mb, "equivalente_mb": mb_model, "fonte_equivalencia": fonte_eq,
                    "gap_preco_rs": gap_r, "gap_preco_pct": gap_p,
                    "data_captura_preco": p["captured_at"] if p else None, "observacao": obs,
                })
            out["segmentos"][seg] = linhas
        return out
