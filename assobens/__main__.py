"""CLI da rotina ASSOBENS.

  python -m assobens sync [--trigger scheduler|manual] [--skip-precos] [--headed]
  python -m assobens importar <arquivo.xlsx>     # importa um Excel já baixado (sem navegador)
  python -m assobens discover                    # login + screenshots/aria dos relatórios (ajuste de seletores)
  python -m assobens kpis                        # recalcula kpis.json / top10 a partir da matriz atual
  python -m assobens status                      # imprime status.json
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import sys

from . import config


def _executed_by(v: str | None) -> str:
    return v or os.environ.get("GITHUB_ACTOR") or getpass.getuser() or "desconhecido"


def cmd_sync(a) -> int:
    from .sync_job import AssobensSyncJob
    job = AssobensSyncJob(trigger=a.trigger, executed_by=_executed_by(a.executed_by), skip_precos=a.skip_precos,
                          headless=not a.headed, arquivo=getattr(a, "arquivo", None))
    run = job.run()
    print(json.dumps(run.to_dict(), ensure_ascii=False, indent=1))
    return 0 if run.status in ("success", "partial") else 1


def cmd_discover(a) -> int:
    from .auth import AssobensAuthenticationService
    from .browser import AssobensBrowserService, load_selectors
    from .emplacamentos_downloader import AssobensEmplacamentosDownloader
    from .price_downloader import AssobensPriceDownloader
    config.ensure_dirs()
    sel = load_selectors()
    with AssobensBrowserService(headless=not a.headed) as b:
        auth = AssobensAuthenticationService(config.get_credentials(), sel, b)
        auth.login_portal(b.page)
        b.dump_aria(b.page, "portal")
        b.screenshot_error(b.page, "discover_portal")
        auth.open_bi(b.page)
        dl = AssobensEmplacamentosDownloader(b, auth, sel)
        outs = dl.discover(b.page)
        try:
            outs += AssobensPriceDownloader(b, auth, sel, dl).discover(b.page)
        except Exception as e:
            print("preços:", e)
    for p in outs:
        print(p)
    return 0


def cmd_kpis(a) -> int:
    from .importer import AssobensImporter
    from .kpi import AssobensKpiService
    from .price_analysis import AssobensPriceAnalysisService
    from .runlog import write_json_atomic
    _, rows = AssobensImporter().load_matrix()
    k = AssobensKpiService().compute(rows)
    write_json_atomic(config.KPIS_PATH, k)
    svc = AssobensPriceAnalysisService()
    top = svc.top10_por_segmento(rows)
    write_json_atomic(config.TOP10_PATH, top)
    write_json_atomic(config.PRECOS_TOP10_PATH, svc.analyze(top))
    print(f"matriz: {len(rows)} | mercado {k['total_mercado']} | MB {k['total_mercedes_benz']} | share {k['market_share_mb']}% | "
          f"12m share {k['ultimos_12_meses']['market_share_mb']}% | data máxima {k['data_maxima']}")
    for seg, lst in top["segmentos"].items():
        print(f"  Top 10 {seg}: " + ", ".join(f"{x['fabricante']} {x['modelo']} ({x['emplacamentos']})" for x in lst[:3]) + " …")
    return 0


def cmd_status(a) -> int:
    from .runlog import read_json
    print(json.dumps(read_json(config.STATUS_PATH, {"status": "nunca executado"}), ensure_ascii=False, indent=1))
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="assobens", description="Sincronização ASSOBENS → Torre Tecar")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sync", help="executa a sincronização completa (navegador)")
    s.add_argument("--trigger", choices=["scheduler", "manual"], default="manual")
    s.add_argument("--executed-by", default=None)
    s.add_argument("--skip-precos", action="store_true")
    s.add_argument("--headed", action="store_true", help="navegador visível (depuração)")
    s.set_defaults(fn=cmd_sync)
    i = sub.add_parser("importar", help="importa um Excel já baixado, sem navegador")
    i.add_argument("arquivo")
    i.add_argument("--trigger", choices=["scheduler", "manual"], default="manual")
    i.add_argument("--executed-by", default=None)
    i.add_argument("--skip-precos", action="store_true", default=True)
    i.add_argument("--headed", action="store_true")
    i.set_defaults(fn=cmd_sync)
    d = sub.add_parser("discover", help="salva screenshots e árvore de acessibilidade dos relatórios")
    d.add_argument("--headed", action="store_true")
    d.set_defaults(fn=cmd_discover)
    sub.add_parser("kpis", help="recalcula KPIs e Top 10 da matriz atual").set_defaults(fn=cmd_kpis)
    sub.add_parser("status", help="mostra o status da última sincronização").set_defaults(fn=cmd_status)
    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
