"""AssobensKpiService: as mesmas métricas que a Torre calcula no navegador, recalculadas no backend
para (1) conferência contra o portal, (2) status/relatório e (3) Top 10 por segmento.

DE/PARA (ASSOBENS -> matriz -> KPI da Torre):
  MARCA_COMPLETA/Marca      -> MARCA         -> Total Mercado (linhas), Total MB (MARCA == M.BENZ), Market Share MB
  DATA_COMPLETA/Data        -> DATA EMPLAC.  -> ano, mês, últimos 12 meses, evolução, sazonalidade
  SUBSEGMENTO               -> SUBSEGMENTO   -> segmento comercial (LEVES/MEDIOS/SEMIPESADOS/EXTRAPESADOS)
  SEGMENTO                  -> SEGMENTO      -> família (1.0-CAMINHOES)
  TRAÇÃO                    -> TRAÇÃO        -> mix por tração
  MODELO                    -> MODELO        -> ranking de modelos
  MUNICIPIO/Estado          -> CIDADE/UF     -> território
  DEALER_AOP/AREA_OPERAC.   -> DEALER AOP/AOP-> área operacional
Nenhum KPI novo é criado; a Torre continua lendo a matriz.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date

from . import config


def _share(part: int, total: int) -> float:
    return round(100.0 * part / total, 2) if total else 0.0


def _month_key(iso: str) -> str:
    return iso[:7]


def last_12_months(ref: date) -> list[str]:
    y, m = ref.year, ref.month
    out = []
    for _ in range(12):
        out.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return sorted(out)


class AssobensKpiService:
    def __init__(self, mb_brand: str = config.MB_BRAND):
        self.mb = mb_brand

    def compute(self, rows: list[dict], today: date | None = None) -> dict:
        today = today or date.today()
        dates = [r["DATA EMPLACAMENTO"] for r in rows if r.get("DATA EMPLACAMENTO")]
        max_date = max(dates) if dates else None
        ref = date.fromisoformat(max_date) if max_date else today
        m12 = set(last_12_months(ref))

        total = len(rows)
        mb = sum(1 for r in rows if r.get("MARCA") == self.mb)
        by = {k: self._dim(rows, k) for k in ("MARCA", "SUBSEGMENTO", "TRAÇÃO", "DEALER AOP", "UF", "TIPO TERRENO")}
        por_ano = self._time(rows, lambda r: r["DATA EMPLACAMENTO"][:4])
        por_mes = self._time(rows, lambda r: _month_key(r["DATA EMPLACAMENTO"]))
        r12 = [r for r in rows if _month_key(r.get("DATA EMPLACAMENTO", "")) in m12]
        top_mun = self._dim(rows, "CIDADE", top=20, extra_key="UF")
        return {
            "gerado_em": today.isoformat(),
            "data_maxima": max_date,
            "total_mercado": total,
            "total_mercedes_benz": mb,
            "market_share_mb": _share(mb, total),
            "ultimos_12_meses": {
                "meses": sorted(m12), "total_mercado": len(r12),
                "total_mercedes_benz": sum(1 for r in r12 if r.get("MARCA") == self.mb),
                "market_share_mb": _share(sum(1 for r in r12 if r.get("MARCA") == self.mb), len(r12)),
                "por_marca": self._dim(r12, "MARCA"),
                "por_subsegmento": self._dim(r12, "SUBSEGMENTO"),
            },
            "por_ano": por_ano,
            "por_mes": por_mes,
            "por_marca": by["MARCA"],
            "por_subsegmento": by["SUBSEGMENTO"],
            "por_tracao": by["TRAÇÃO"],
            "por_area_operacional": by["DEALER AOP"],
            "por_uf": by["UF"],
            "por_terreno": by["TIPO TERRENO"],
            "top_municipios": top_mun,
            "ranking_modelos_12m": self.ranking_modelos(r12),
        }

    def _dim(self, rows: list[dict], key: str, top: int | None = None, extra_key: str | None = None) -> list[dict]:
        c: Counter = Counter()
        cmb: Counter = Counter()
        for r in rows:
            k = r.get(key) or "(vazio)"
            if extra_key:
                k = f"{k}|{r.get(extra_key, '')}"
            c[k] += 1
            if r.get("MARCA") == self.mb:
                cmb[k] += 1
        total = len(rows)
        items = [{"chave": k, "emplacamentos": v, "share": _share(v, total), "mercedes_benz": cmb[k], "share_mb_na_chave": _share(cmb[k], v)}
                 for k, v in c.most_common(top)]
        return items

    def _time(self, rows: list[dict], fn) -> list[dict]:
        c: Counter = Counter()
        cmb: Counter = Counter()
        for r in rows:
            if not r.get("DATA EMPLACAMENTO"):
                continue
            k = fn(r)
            c[k] += 1
            if r.get("MARCA") == self.mb:
                cmb[k] += 1
        return [{"periodo": k, "total_mercado": c[k], "mercedes_benz": cmb[k], "market_share_mb": _share(cmb[k], c[k])} for k in sorted(c)]

    def conferencia(self, rows: list[dict], portal: dict) -> dict:
        """ASSOBENS (painel) × Torre (matriz) no mesmo recorte de período do painel."""
        from .normalizer import normalize_brand, parse_date
        ini = parse_date(portal.get("periodo_inicio")) or "0000-00-00"
        fim = parse_date(portal.get("periodo_fim")) or "9999-99-99"
        rec = [r for r in rows if ini <= r.get("DATA EMPLACAMENTO", "") <= fim]
        tot, mb = len(rec), sum(1 for r in rec if r.get("MARCA") == self.mb)
        share = _share(mb, tot)

        def item(nome, a, t, pct=False):
            d = (round(t - a, 2) if (a is not None and t is not None) else None)
            p = (round(100 * (t - a) / a, 2) if (a not in (None, 0) and t is not None) else None)
            return {"indicador": nome, "assobens": a, "torre": t, "diferenca": d, "diferenca_pct": p}
        ind = [item("Total Mercado", portal.get("total_mercado"), tot),
               item("Total Mercedes-Benz", portal.get("total_mb"), mb),
               item("Market Share MB (%)", portal.get("share_mb"), share)]
        por_marca: dict[str, int] = {}
        for r in rec:
            por_marca[r.get("MARCA") or "(vazio)"] = por_marca.get(r.get("MARCA") or "(vazio)", 0) + 1
        fabricantes = []
        for f in portal.get("fabricantes", []):
            marca = normalize_brand(f["fabricante"])
            t = por_marca.get(marca) if marca != "OTHERS" else None
            fabricantes.append({**item(f"Fabricante {f['fabricante']}", f["emplacamentos"], t), "share_assobens": f["share"],
                                "share_torre": _share(t, tot) if t is not None else None})
        return {"periodo": {"inicio": ini, "fim": fim}, "painel_atualizado_em": portal.get("atualizado_em"),
                "filtros_painel": portal.get("filtros", {}), "indicadores": ind, "fabricantes": fabricantes,
                "por_subsegmento_torre": self._dim(rec, "SUBSEGMENTO")}

    def ranking_modelos(self, rows: list[dict], por: str = "SUBSEGMENTO") -> dict[str, list[dict]]:
        """Ranking de modelos dentro de cada segmento: base do Top 10 (nunca hardcoded)."""
        seg: dict[str, Counter] = defaultdict(Counter)
        for r in rows:
            seg[r.get(por) or "(vazio)"][(r.get("MARCA") or "(vazio)", r.get("MODELO") or "(vazio)")] += 1
        out = {}
        for s, c in seg.items():
            tot = sum(c.values())
            out[s] = [{"posicao": i + 1, "fabricante": k[0], "modelo": k[1], "emplacamentos": v, "market_share": _share(v, tot),
                       "total_segmento": tot} for i, (k, v) in enumerate(c.most_common())]
        return out
