"""AssobensNormalizer: strings, números, datas, documentos e marcas no padrão da matriz da Torre.

Regras herdadas da matriz publicada: data ISO aaaa-mm-dd, CNPJ formatado como texto,
pessoa física mascarada (documento `***.***.***-**`, nome `***`), texto em maiúsculas sem acento
nas dimensões geográficas.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

from . import config

# Rótulos de marca já usados na matriz (a Torre agrega por este texto; variações são unificadas aqui).
BRAND_ALIASES = {
    "MERCEDES-BENZ": "M.BENZ", "MERCEDES BENZ": "M.BENZ", "MERCEDES": "M.BENZ", "M. BENZ": "M.BENZ", "MBENZ": "M.BENZ", "MB": "M.BENZ",
    "VOLKSWAGEN": "VW", "VW/MAN": "VW", "VOLKS": "VW",
    "HYUNDAI": "HYUNDA",
    "FORD CAMINHOES": "FORD",
    "IVECO/FIAT": "IVECO", "IVECO-FIAT": "IVECO", "IVECO FIAT": "IVECO",
    "AGRALE": "AGRAL",
}
# Códigos AOP presentes na matriz atual (nome da área operacional -> código). Usado só quando o ASSOBENS
# manda apenas o nome (ou apenas o código) da área operacional.
AOP_CODES = {"GOIANIA": "408", "ANAPOLIS": "406", "PALMAS": "407", "PRIMAVERA DO LESTE": "409"}
AOP_NAMES = {v: k for k, v in AOP_CODES.items()}


def resolve_aop(aop: Any, dealer_aop: Any, raw: Any) -> tuple[str, str]:
    """Devolve (código AOP, nome da área operacional) a partir das colunas disponíveis."""
    code = parse_int(aop)
    code_s = str(code) if code is not None else clean_text(aop, accents=False)
    name = clean_text(dealer_aop, accents=False)
    raw_s = clean_text(raw, accents=False)
    if raw_s:
        if parse_int(raw_s) is not None and not code_s:
            code_s = str(parse_int(raw_s))
        elif parse_int(raw_s) is None and not name:
            name = raw_s
    if not code_s and name in AOP_CODES:
        code_s = AOP_CODES[name]
    if not name and code_s in AOP_NAMES:
        name = AOP_NAMES[code_s]
    return code_s, name


# Rótulos de segmento/subsegmento da matriz (o Power BI manda no singular: EXTRAPESADO, CAMINHAO).
SUBSEG_ALIASES = {"EXTRAPESADO": "EXTRAPESADOS", "EXTRA PESADO": "EXTRAPESADOS", "EXTRA PESADOS": "EXTRAPESADOS", "EXTRA-PESADOS": "EXTRAPESADOS",
                  "SEMIPESADO": "SEMIPESADOS", "SEMI PESADO": "SEMIPESADOS", "SEMI PESADOS": "SEMIPESADOS", "SEMI-PESADOS": "SEMIPESADOS",
                  "PESADO": "PESADOS", "MEDIO": "MEDIOS", "LEVE": "LEVES"}
SEG_ALIASES = {"CAMINHAO": "1.0-CAMINHOES", "CAMINHOES": "1.0-CAMINHOES", "1.0 CAMINHOES": "1.0-CAMINHOES"}


def normalize_subseg(v: Any) -> str:
    s = clean_text(v, accents=False)
    return SUBSEG_ALIASES.get(s, s)


def normalize_seg(v: Any) -> str:
    s = clean_text(v, accents=False)
    return SEG_ALIASES.get(s, s)


PF_DOC_MASK = "***.***.***-**"
PF_NAME_MASK = "***"


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def clean_text(v: Any, upper: bool = True, accents: bool = True) -> str:
    """Remove espaços ocultos (NBSP, tabs, duplos) e opcionalmente acentos/caixa."""
    s = "" if v is None else str(v)
    s = s.replace(" ", " ").replace("\t", " ").replace("\r", " ").replace("\n", " ")
    s = " ".join(s.split())
    if not accents:
        s = strip_accents(s)
    return s.upper() if upper else s


def digits(v: Any) -> str:
    return re.sub(r"\D", "", "" if v is None else str(v))


def parse_int(v: Any) -> int | None:
    if v is None or v == "":
        return None
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return int(v)
    s = str(v).strip().replace(".", "").replace(",", ".")
    try:
        return int(float(s))
    except ValueError:
        return None


def parse_number(v: Any) -> float | None:
    """Número em formato BR (1.234,56) ou US (1234.56)."""
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    s = str(v).strip().replace("R$", "").replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def parse_date(v: Any) -> str | None:
    """Devolve ISO aaaa-mm-dd. Aceita datetime, date, serial Excel, dd/mm/aaaa, dd/mm/aa, aaaa-mm-dd."""
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v.date().isoformat()
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        if 20000 < v < 80000:  # serial Excel (1954..2119)
            return (date(1899, 12, 30) + timedelta(days=int(v))).isoformat()
        return None
    s = str(v).strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return _valid(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:  # base brasileira: sempre dd/mm
        return _valid(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{2})$", s)
    if m:
        return _valid(2000 + int(m.group(3)), int(m.group(2)), int(m.group(1)))
    m = re.match(r"^(\d{4})(\d{2})(\d{2})$", s)
    if m:
        return _valid(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


def _valid(y: int, mth: int, d: int) -> str | None:
    try:
        return date(y, mth, d).isoformat()
    except ValueError:
        return None


def format_cnpj(d: str) -> str:
    return f"{d[0:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:14]}"


def cnpj_valid(d: str) -> bool:
    if len(d) != 14 or len(set(d)) == 1:
        return False

    def calc(base: str, w: list[int]) -> int:
        s = sum(int(b) * x for b, x in zip(base, w))
        r = s % 11
        return 0 if r < 2 else 11 - r
    d1 = calc(d[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    d2 = calc(d[:12] + str(d1), [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return d.endswith(f"{d1}{d2}")


def normalize_brand(v: Any) -> str:
    s = clean_text(v, accents=False)
    s = re.sub(r"\s*/\s*", "/", s)
    return BRAND_ALIASES.get(s, s)


def normalize_doc_type(v: Any, doc_digits: str) -> str:
    s = clean_text(v, accents=False)
    if "JUR" in s or s in ("PJ", "J"):
        return "JURIDICA"
    if "FIS" in s or "CPF" in s or s in ("PF", "F"):
        return "FISICA"
    if doc_digits and len(doc_digits) == 14:
        return "JURIDICA"
    if doc_digits and len(doc_digits) == 11:
        return "FISICA"
    if "*" in str(v or ""):
        return "FISICA"
    return s or "INDETERMINADO"


@dataclass
class NormalizedBatch:
    rows: list[dict]
    rejected: list[dict] = field(default_factory=list)   # {motivo, linha}
    extra_columns: list[str] = field(default_factory=list)

    @property
    def counts(self) -> dict:
        motivos: dict[str, int] = {}
        for r in self.rejected:
            motivos[r["motivo"]] = motivos.get(r["motivo"], 0) + 1
        return {"validas": len(self.rows), "rejeitadas": len(self.rejected), "motivos": motivos}


class AssobensNormalizer:
    EXTRA_DIMENSIONS = ["COMBUSTIVEL", "GRUPO", "VERSAO", "REGIAO MB", "DISTRITO", "TIPO VEICULO"]

    def normalize(self, raw_rows: list[dict]) -> NormalizedBatch:
        out, rejected = [], []
        extras = [c for c in self.EXTRA_DIMENSIONS if raw_rows and any(c in r for r in raw_rows[:50])]
        for i, r in enumerate(raw_rows):
            row, motivo = self._normalize_row(r, extras)
            if motivo:
                rejected.append({"motivo": motivo, "linha": i + 1, "chassi": clean_text(r.get("CHASSI"))[:20]})
            else:
                out.append(row)
        return NormalizedBatch(rows=out, rejected=rejected, extra_columns=extras)

    def _normalize_row(self, r: dict, extras: list[str]) -> tuple[dict | None, str | None]:
        chassi = clean_text(r.get("CHASSI"), accents=False).replace(" ", "")
        if not chassi:
            return None, "chassi ausente"
        if len(chassi) < 11:
            return None, "chassi inválido"
        data = parse_date(r.get("DATA EMPLACAMENTO"))
        if not data:
            return None, "data inválida"
        qtd = r.get("QUANTIDADE")
        if qtd not in (None, ""):
            q = parse_number(qtd)
            if q is None or q < 0:
                return None, "quantidade negativa ou inválida"
        doc_d = digits(r.get("CPFCNPJPROPRIETARIO"))
        tipo = normalize_doc_type(r.get("TIPOCNPJPROPRIETARIO"), doc_d)
        if tipo == "FISICA":
            doc, nome = PF_DOC_MASK, PF_NAME_MASK
        else:
            doc = format_cnpj(doc_d) if len(doc_d) == 14 else clean_text(r.get("CPFCNPJPROPRIETARIO"), accents=False)
            nome = clean_text(r.get("NOMEPROPRIETARIO"))  # nomes mantêm acento (como na matriz atual)
        ano_fab = parse_int(r.get("ANOFABRICACAO"))
        ano_mod = parse_int(r.get("ANOMODELO"))
        aop_s, dealer_aop = resolve_aop(r.get("AOP"), r.get("DEALER AOP"), r.get("AREA OPERACIONAL RAW"))
        row = {
            "CHASSI": chassi,
            "DATA EMPLACAMENTO": data,
            "MODELO": clean_text(r.get("MODELO")),
            "TRAÇÃO": clean_text(r.get("TRAÇÃO"), accents=False).replace(" ", ""),
            "MARCA": normalize_brand(r.get("MARCA")),
            "SEGMENTO": normalize_seg(r.get("SEGMENTO")),
            "SUBSEGMENTO": normalize_subseg(r.get("SUBSEGMENTO")),
            "PLACA": clean_text(r.get("PLACA"), accents=False).replace("-", ""),
            "CONCESSIONÁRIO": clean_text(r.get("CONCESSIONÁRIO")),
            "CIDADE": clean_text(r.get("CIDADE"), accents=False),
            "UF": clean_text(r.get("UF"), accents=False)[:2],
            "DEALER AOP": dealer_aop,
            "AOP": aop_s,
            "ANOFABRICACAO": str(ano_fab) if ano_fab else "",
            "ANOMODELO": str(ano_mod) if ano_mod else "",
            "TIPO TERRENO": clean_text(r.get("TIPO TERRENO"), accents=False),
            "CPFCNPJPROPRIETARIO": doc,
            "TIPOCNPJPROPRIETARIO": tipo,
            "NOMEPROPRIETARIO": nome,
        }
        for c in extras:
            row[c] = clean_text(r.get(c), accents=False)
        return row, None


def quality_score(rows: list[dict]) -> dict:
    """Réplica do computeQuality da Torre (gate >= 75): cnpj 25% · geo 20% · dealer 20% · data 15% · chassi único 20%."""
    n = len(rows) or 1
    pj = [r for r in rows if r.get("TIPOCNPJPROPRIETARIO") == "JURIDICA"]
    q = {
        "cnpj": (sum(1 for r in pj if cnpj_valid(digits(r.get("CPFCNPJPROPRIETARIO")))) / len(pj)) if pj else 0.0,
        "geo": sum(1 for r in rows if r.get("CIDADE") and r.get("UF")) / n,
        "dealer": sum(1 for r in rows if r.get("CONCESSIONÁRIO") and r.get("DEALER AOP") and r.get("AOP")) / n,
        "date": sum(1 for r in rows if r.get("DATA EMPLACAMENTO")) / n,
        "uniqueChassis": len({r.get("CHASSI") for r in rows}) / n,
    }
    q["score"] = round(100 * (q["cnpj"] * .25 + q["geo"] * .2 + q["dealer"] * .2 + q["date"] * .15 + q["uniqueChassis"] * .2))
    return q
