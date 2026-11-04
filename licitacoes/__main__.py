"""CLI do motor de licitações.

  python -m licitacoes sync [--minutos 50] [--sem-historico] [--ufs GO,MT,TO] [--fontes pncp,comprasgov]
  python -m licitacoes marcas        # recalcula concessionária → marca a partir dos emplacamentos
  python -m licitacoes status
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter, defaultdict

from . import catalogo, config


def mapa_marcas() -> dict[str, str]:
    """Concessionária → marca dominante nos emplacamentos ASSOBENS (gravado para auditoria)."""
    import openpyxl
    from .coletor import _write
    if not config.MATRIZ_PATH.exists():
        return {}
    wb = openpyxl.load_workbook(config.MATRIZ_PATH, read_only=True)
    ws = wb.worksheets[0]
    head = [str(h or "").strip() for h in next(ws.iter_rows(max_row=1, values_only=True))]
    i_dealer, i_marca = head.index("CONCESSIONÁRIO"), head.index("MARCA")
    dealers: dict[str, Counter] = defaultdict(Counter)
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[i_dealer] and r[i_marca]:
            dealers[str(r[i_dealer])][str(r[i_marca])] += 1
    mapa = catalogo.mapa_fornecedor_marca(dealers)
    _write(config.FORNECEDOR_MARCA_PATH, {"_doc": "Concessionária (razão social normalizada) → marca dominante nos "
                                          "emplacamentos ASSOBENS (mín. 20 veículos, 90% de uma marca).", "mapa": mapa})
    return mapa


def cmd_sync(a) -> int:
    from .coletor import Coletor
    ufs = [u.strip().upper() for u in a.ufs.split(",") if u.strip()]
    fontes = {f.strip().lower() for f in a.fontes.split(",") if f.strip()}
    cg = None
    if "comprasgov" in fontes:
        from .comprasgov import ComprasGovClient
        cg = ComprasGovClient()
    col = Coletor(mapa_marca=mapa_marcas(), ufs=ufs, cg=cg)
    res = col.run(minutos=a.minutos, historico=not a.sem_historico)
    print(res.resumo())
    e = col.estado
    print(f"PNCP: {e.get('meses_concluidos')}/{e.get('meses_total')} meses · Compras.gov.br: {e.get('cg_meses_concluidos', 0)}/{e.get('cg_meses_total', 0)} meses · compras {len(col.compras)} · itens {len(col.itens)}")
    for aviso in res.avisos:
        print("aviso:", aviso)
    return 0 if res.erro is None or res.contratacoes_lidas else 1


def cmd_marcas(a) -> int:
    m = mapa_marcas()
    print(f"{len(m)} concessionárias com marca dominante")
    for k, v in sorted(m.items())[:40]:
        print(f"  {v:8} {k}")
    return 0


def cmd_status(a) -> int:
    from .coletor import _read
    e = _read(config.ESTADO_PATH, {})
    e.pop("descartadas", None)
    print(json.dumps(e, ensure_ascii=False, indent=1))
    return 0


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
    p = argparse.ArgumentParser(prog="licitacoes", description="Licitações PNCP → Torre Tecar")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sync", help="coleta incremental (atualizações + histórico até o orçamento de tempo)")
    s.add_argument("--minutos", type=float, default=50)
    s.add_argument("--sem-historico", action="store_true", help="só a rota de atualização (rápido)")
    s.add_argument("--ufs", default=",".join(config.UFS))
    s.add_argument("--fontes", default="pncp,comprasgov", help="pncp e/ou comprasgov (pregões da lei antiga, 2021–2024)")
    s.set_defaults(fn=cmd_sync)
    sub.add_parser("marcas", help="concessionária → marca a partir dos emplacamentos").set_defaults(fn=cmd_marcas)
    sub.add_parser("status", help="estado da coleta").set_defaults(fn=cmd_status)
    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
