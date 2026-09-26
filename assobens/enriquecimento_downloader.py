"""AssobensEnriquecimentoDownloader: BI → Enriquecimento → "Baixar Dados" → botão Excel "Clientes".

O relatório de enriquecimento traz CPF/CNPJ, tipo de pessoa e nome do proprietário por chassi (o próprio BI avisa
que ele "não deve ser considerado para fins de market share"). Por isso ele é usado SOMENTE para completar os
campos de proprietário dos chassis que já estão na matriz — nunca para inserir ou contar emplacamentos.
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from . import config
from .browser import DownloadCatcher, first_present
from .errors import DownloadError, InterfaceChangedError
from .logutil import get_logger


class AssobensEnriquecimentoDownloader:
    def __init__(self, browser, auth, selectors: dict, emplacamentos_downloader):
        self.browser, self.auth, self.sel = browser, auth, selectors
        self.nav = emplacamentos_downloader
        self.log = get_logger()

    def download(self, page, out_dir: Path, stamp: str, date_from: str, date_to: str) -> Path:
        s = self.sel["enriquecimento"]
        self.auth.ensure_bi_session(page)
        self.nav.open_menu(page, s["menu"])
        try:
            page.locator(s["date_from"]).first.wait_for(state="visible", timeout=60_000)
        except Exception:
            self.browser.screenshot_error(page, "enriquecimento_pagina")
            raise InterfaceChangedError("página 'Baixar Dados' (enriquecimento) não carregou os filtros")
        page.wait_for_timeout(4_000)  # mounted(): carrega usuário, contratos, datas e opções
        self._fill_date(page, s["date_from"], date_from)
        self._fill_date(page, s["date_to"], date_to)
        self._ensure_todos(page, s["area_oper"])
        self.log.info("filtros aplicados: %s → %s · área operacional = Todas · segmento e marca da associação do usuário", date_from, date_to)
        catcher = DownloadCatcher(page.context, page)
        btn = first_present(page, s["excel_clientes"], timeout_ms=15_000)
        if btn is None:
            self.browser.screenshot_error(page, "enriquecimento_botao")
            raise InterfaceChangedError("botão Excel 'Clientes' não encontrado na página de enriquecimento")
        self.log.info("download iniciado (Excel 'Clientes' do enriquecimento)")
        btn.click()
        dl = catcher.wait(240)  # o arquivo é gerado no servidor e aberto em nova aba
        if dl is None:
            err = first_present(page, [{"kind": "text", "name": s["erro_associacao"]}], timeout_ms=0)
            self.browser.screenshot_error(page, "enriquecimento_download")
            if err is not None:
                raise DownloadError("BI recusou: usuário sem associação de Segmento, Área Operacional ou Marca")
            raise DownloadError("Excel de enriquecimento não foi gerado em 240s")
        ext = Path(dl.suggested_filename or "").suffix.lower() or ".xlsx"
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir / f"{stamp}_enriquecimento{ext}"
        dl.save_as(str(target))
        if not target.exists() or target.stat().st_size == 0:
            raise DownloadError("arquivo de enriquecimento vazio")
        self.log.info("arquivo recebido: %s (%d bytes, nome original %s)", target.name, target.stat().st_size, dl.suggested_filename)
        return target

    def _fill_date(self, page, css: str, value: str) -> None:
        loc = page.locator(css).first
        loc.fill(value)
        try:
            loc.dispatch_event("change")
        except Exception:
            pass

    def _ensure_todos(self, page, css: str) -> None:
        loc = page.locator(css).first
        try:
            if loc.count() == 0:
                return
            atual = loc.input_value()
            if str(atual).upper() != "TODOS":
                loc.select_option("TODOS")
                loc.dispatch_event("change")
        except Exception as e:
            self.log.info("área operacional mantida como está (%s)", str(e).splitlines()[0][:80])


def janela_enriquecimento(rows: list[dict], hoje: str, min_dias: int = 120, max_dias: int = 400) -> tuple[str, str]:
    """Janela de datas: cobre todos os chassis da matriz sem proprietário (limitada a max_dias) e pelo menos min_dias."""
    from datetime import date, timedelta
    h = date.fromisoformat(hoje)
    faltando = [r["DATA EMPLACAMENTO"] for r in rows if not str(r.get("NOMEPROPRIETARIO", "")).strip() and r.get("DATA EMPLACAMENTO")]
    ini = h - timedelta(days=min_dias)
    if faltando:
        ini = min(ini, date.fromisoformat(min(faltando)))
    ini = max(ini, h - timedelta(days=max_dias))
    return ini.isoformat(), h.isoformat()
