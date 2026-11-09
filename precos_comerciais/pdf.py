"""Conferência das linhas importadas contra as circulares em PDF (SHA-256 e conteúdo, linha a linha).

Usa PyMuPDF quando instalado. A extração de texto entrega, para cada variante, a sequência
modelo · ano/modelo · UP · variante · configuração · 4 preços — é isso que se confere.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

RE_PRECO = re.compile(r"^R\$\s*([\d.]+),(\d{2})$")
RE_VAR = re.compile(r"^QVV[0-9A-Z]+$")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 16), b""):
            h.update(bloco)
    return h.hexdigest()


def disponivel() -> bool:
    try:
        import pymupdf  # noqa: F401
        return True
    except ImportError:
        return False


def extrai(path: Path) -> dict[str, list[dict]]:
    import pymupdf
    out: dict[str, list[dict]] = {}
    with pymupdf.open(str(path)) as doc:
        for pagina, p in enumerate(doc, 1):
            toks = [t.strip() for t in p.get_text().split("\n") if t.strip()]
            for i, t in enumerate(toks):
                if not RE_VAR.match(t) or i < 3 or i + 5 >= len(toks):
                    continue
                precos = []
                for x in toks[i + 2:i + 6]:
                    m = RE_PRECO.match(x)
                    precos.append(int(m.group(1).replace(".", "") + m.group(2)) if m else None)
                out.setdefault(t, []).append({"pagina": pagina, "modelo": toks[i - 3], "ano_modelo": toks[i - 2],
                                              "up": toks[i - 1], "configuracao": toks[i + 1].upper(), "precos": precos})
    return out


def confere(precos: list[dict], pasta: Path, manifesto: dict | None = None) -> dict:
    """Relatório de conferência. 'divergencias' vazio = todas as linhas batem com a página declarada do PDF."""
    pasta = Path(pasta)
    rel = {"documentos": {}, "divergencias": [], "fora_do_csv": [], "conferido": False}
    fontes = (manifesto or {}).get("sources") or {}
    extraidos: dict[str, dict] = {}
    for arq in sorted({p["source_file"] for p in precos}):
        caminho = pasta / arq
        if not caminho.is_file():
            rel["documentos"][arq] = {"encontrado": False}
            rel["divergencias"].append({"arquivo": arq, "problema": "PDF não encontrado na pasta de importação"})
            continue
        h = sha256(caminho)
        esperado = (fontes.get(arq) or {}).get("sha256")
        rel["documentos"][arq] = {"encontrado": True, "sha256": h, "sha256_manifesto": esperado,
                                  "sha256_confere": (h == esperado) if esperado else None}
        if esperado and h != esperado:
            rel["divergencias"].append({"arquivo": arq, "problema": "SHA-256 diferente do manifesto"})
        if disponivel():
            extraidos[arq] = extrai(caminho)
    if not disponivel():
        rel["aviso"] = "PyMuPDF indisponível: conferência de conteúdo não executada (só hashes)."
        return rel
    for p in precos:
        ocs = extraidos.get(p["source_file"], {}).get(p["variante"], [])
        alvo = [p["preco_fabrica_5_10_centavos"], p["preco_fabrica_11_15_centavos"],
                p["preco_estoque_5_10_centavos"], p["preco_estoque_11_15_centavos"]]
        ok = [o for o in ocs if o["precos"] == alvo and o["modelo"] == p["modelo"] and o["ano_modelo"] == p["ano_modelo"]
              and o["up"] == p["up"] and o["configuracao"] == p["configuracao"]]
        if not ocs:
            rel["divergencias"].append({"variante": p["variante"], "problema": "variante não encontrada no PDF declarado"})
        elif not ok:
            rel["divergencias"].append({"variante": p["variante"], "problema": "conteúdo diferente do PDF",
                                        "pdf": ocs})
        elif p["source_page"] not in {o["pagina"] for o in ok}:
            rel["divergencias"].append({"variante": p["variante"], "problema": "página declarada diferente",
                                        "paginas_pdf": sorted({o["pagina"] for o in ok})})
    csv = {p["variante"] for p in precos}
    for arq, ex in extraidos.items():
        rel["fora_do_csv"] += [{"arquivo": arq, "variante": v} for v in sorted(set(ex) - csv)]
    rel["linhas_conferidas"] = len(precos)
    rel["conferido"] = not rel["divergencias"] and not rel["fora_do_csv"]
    return rel
