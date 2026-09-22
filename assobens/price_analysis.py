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
from .runlog import read_json

PRICE_FIELDS = ["source", "manufacturer", "model", "segment", "price", "reference_date", "captured_at"]


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

    # ------------------------------------------------------------- análise
    def analyze(self, top10: dict, captured_at: str | None = None) -> dict:
        prices = self.history.latest_by_model()
        eq = self.equivalencias()
        captured_at = captured_at or datetime.now(config.TZ).isoformat(timespec="seconds")
        out = {"gerado_em": captured_at, "janela": top10.get("janela"), "segmentos": {}}
        for seg, lst in top10.get("segmentos", {}).items():
            linhas = []
            for item in lst:
                fab, mod = item["fabricante"], item["modelo"]
                p = prices.get((fab.upper(), model_key(fab, mod)))
                e = eq.get((fab.upper(), model_key(fab, mod)))
                mb_model = e.get("equivalente_mb") if e else None
                p_mb = prices.get((self.mb, model_key(self.mb, mb_model))) if mb_model else None
                preco = float(p["price"]) if p and p.get("price") else None
                preco_mb = float(p_mb["price"]) if p_mb and p_mb.get("price") else None
                gap_r = round(preco_mb - preco, 2) if (preco is not None and preco_mb is not None) else None
                gap_p = round((preco_mb / preco - 1) * 100, 2) if (preco and preco_mb is not None) else None
                obs = None
                if fab == self.mb:
                    mb_model, obs = mod, "modelo Mercedes-Benz"
                    preco_mb, gap_r, gap_p = preco, 0.0 if preco is not None else None, 0.0 if preco is not None else None
                elif not e:
                    obs = "equivalência não cadastrada"
                elif preco_mb is None:
                    obs = "preço MB equivalente não capturado"
                if preco is None:
                    obs = (obs + "; " if obs else "") + "preço não identificado no comparativo"
                linhas.append({
                    "posicao": item["posicao"], "fabricante": fab, "modelo": mod,
                    "emplacamentos": item["emplacamentos"], "market_share": item["market_share"],
                    "preco_identificado": preco, "preco_mb_equivalente": preco_mb, "equivalente_mb": mb_model,
                    "gap_preco_rs": gap_r, "gap_preco_pct": gap_p,
                    "data_captura_preco": p["captured_at"] if p else None, "observacao": obs,
                })
            out["segmentos"][seg] = linhas
        return out
