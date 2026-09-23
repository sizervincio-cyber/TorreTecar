"""AssobensEmplacamentosDownloader: BI → menu "Veículos Novos Área Operacional" → relatório Power BI
→ página VEÍCULOS → ícone Excel → download do relatório analítico.

Região MB e Distrito não são tocados (permanecem "Todos"). Um único Excel por execução.
Se o botão não existir: seletores alternativos → screenshot → InterfaceChangedError (nunca finge sucesso).
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from . import config
from .browser import DownloadCatcher, first_present
from .errors import DownloadError, InterfaceChangedError
from .logutil import get_logger


class AssobensEmplacamentosDownloader:
    def __init__(self, browser, auth, selectors: dict):
        self.browser, self.auth, self.sel = browser, auth, selectors
        self.log = get_logger()

    # ------------------------------------------------------------- fluxo principal
    def download(self, page, out_dir: Path, stamp: str | None = None) -> Path:
        self.auth.ensure_bi_session(page)
        self.open_menu(page, config.BI_MENU_EMPLACAMENTOS)
        frame = self.report_frame(page)
        self.select_page(frame, self.sel["emplacamentos"]["page_tab"], "VEÍCULOS")
        self.log_slicers(frame)
        stamp = stamp or datetime.now(config.TZ).strftime("%H%M")
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir / f"{stamp}_emplacamentos.xlsx"
        return self.click_excel(page, frame, target)

    # ------------------------------------------------------------- navegação
    def open_menu(self, page, label: str) -> None:
        """Navega pelo menu do SPA (rota direta /dashboard devolve 404 na Netlify)."""
        if "bi-assobens" not in page.url:
            page.goto(config.BI_URL, wait_until="domcontentloaded")
        cands = [{"kind": "role", "value": "link", "name": re.escape(label)}, {"kind": "text", "name": re.escape(label)}]
        item = first_present(page, cands, timeout_ms=20_000)
        if item is None:
            toggle = first_present(page, self.sel["bi"]["menu_toggle"], timeout_ms=2_000)
            if toggle is not None:
                toggle.click()
            group = first_present(page, self.sel["bi"]["menu_group_comercializacao"], timeout_ms=3_000)
            if group is not None:
                group.click()
            item = first_present(page, cands, timeout_ms=10_000)
        if item is None:
            self.browser.screenshot_error(page, f"menu_{label}")
            raise InterfaceChangedError(f"item de menu '{label}' não encontrado no BI")
        item.click()
        self.log.info("página acessada: %s", label)

    def report_frame(self, page):
        """Aguarda o iframe do Power BI e a renderização de ao menos um visual."""
        iframe = first_present(page, self.sel["bi"]["report_iframe"], visible=False, timeout_ms=90_000)
        if iframe is None:
            self.browser.screenshot_error(page, "iframe_powerbi")
            raise InterfaceChangedError("iframe do relatório Power BI não apareceu")
        frame = page.frame_locator(self.sel["bi"]["report_iframe"][0]["value"]).first
        for c in self.sel["bi"]["report_iframe"]:
            if page.locator(c["value"]).count():
                frame = page.frame_locator(c["value"]).first
                break
        rendered = first_present(frame, self.sel["bi"]["report_rendered"], visible=False, timeout_ms=120_000)
        if rendered is None:
            self.log.warning("nenhum visual detectado no relatório após 120s; seguindo mesmo assim")
        page.wait_for_timeout(2_000)
        return frame

    def select_page(self, frame, candidates: list[dict], label: str) -> None:
        tab = first_present(frame, candidates, timeout_ms=30_000)
        if tab is None:
            self.browser.screenshot_error(self.browser.page, f"aba_{label}")
            self.browser.dump_aria(frame, f"aba_{label}")
            raise InterfaceChangedError(f"opção '{label}' não encontrada no relatório Power BI")
        tab.click()
        self.log.info("opção '%s' selecionada", label)
        self.browser.page.wait_for_timeout(3_000)

    def log_slicers(self, frame) -> None:
        """Só registra o estado dos filtros Região MB / Distrito. Nunca os altera."""
        for key in ("slicer_regiao_mb", "slicer_distrito"):
            loc = first_present(frame, self.sel["emplacamentos"][key], visible=False, timeout_ms=0)
            if loc is None:
                self.log.info("filtro %s não localizado (mantido como está no relatório)", key)
                continue
            try:
                txt = (loc.first.inner_text() or "").strip().replace("\n", " ")[:80]
            except Exception:
                txt = "?"
            self.log.info("filtro %s = '%s' (não alterado; esperado Todos)", key, txt)

    # ------------------------------------------------------------- download
    def click_excel(self, page, frame, target: Path) -> Path:
        catcher = DownloadCatcher(page.context, page)
        if not self.export_visual(page, frame, self.sel["emplacamentos"].get("visual_title")):
            btn = self._find_logged(frame, self.sel["emplacamentos"]["excel_button"], 15_000, "ícone Excel")
            if btn is None:
                self.browser.screenshot_error(page, "botao_excel")
                self.browser.dump_aria(frame, "botao_excel")
                raise InterfaceChangedError("nem 'Exportar dados' da tabela nem ícone de Excel encontrados no relatório (interface mudou)")
            self.log.info("download iniciado (ícone Excel)")
            btn.click()
        dl = catcher.wait(120)
        if dl is None:
            self.browser.screenshot_error(page, "download_timeout")
            raise DownloadError("clique no Excel não gerou download em 120s")
        suggested = dl.suggested_filename or ""
        ext = Path(suggested).suffix.lower() or ".xlsx"
        if ext not in (".xlsx", ".xls", ".csv", ".xlsm"):
            raise DownloadError(f"download com extensão inesperada: {suggested}")
        target = target.with_suffix(ext)
        dl.save_as(str(target))
        if not target.exists() or target.stat().st_size == 0:
            raise DownloadError("arquivo baixado está vazio")
        self.log.info("arquivo recebido: %s (%d bytes, nome original %s)", target.name, target.stat().st_size, suggested)
        return target

    def _find_logged(self, scope, candidates: list[dict], timeout_ms: int, label: str):
        loc = first_present(scope, candidates, timeout_ms=timeout_ms)
        self.log.info("%s %s", label, "localizado" if loc is not None else "NÃO localizado")
        return loc

    def export_visual(self, page, frame, title_rx: str | None) -> bool:
        """Fluxo documentado no próprio relatório: passar o mouse na tabela → '…' (Mais opções) →
        'Exportar dados' → 'Exportar'. Devolve True se o botão final do diálogo foi clicado."""
        s = self.sel["emplacamentos"]
        visual = None
        if title_rx:
            for css in ("visual-container", ".visualContainer", "[class*='visualContainer']", "visual-container-group"):
                try:
                    loc = frame.locator(css, has_text=re.compile(title_rx, re.I))
                    if loc.count():
                        visual = loc.first
                        break
                except Exception:
                    continue
        if visual is None:
            self.log.warning("visual '%s' não localizado no relatório", title_rx)
            return False
        try:
            visual.wait_for(state="visible", timeout=60_000)
            visual.scroll_into_view_if_needed()
            visual.hover()
            page.wait_for_timeout(1_000)
        except Exception as e:
            self.log.warning("não foi possível focar o visual: %s", e)
            return False
        self.log.info("visual '%s' localizado; abrindo menu do visual", title_rx)
        more = self._find_logged(frame, s["visual_more_options"], 8_000, "botão 'Mais opções'")
        if more is None:
            return False
        more.click()
        item = self._find_logged(frame, s["visual_export_menu"], 8_000, "item 'Exportar dados'")
        if item is None:
            try:
                page.keyboard.press("Escape")
            except Exception:
                pass
            return False
        item.click()
        btn = self._find_logged(frame, s["visual_export_confirm"], 15_000, "botão 'Exportar' do diálogo")
        if btn is None:
            return False
        self.log.info("download iniciado (Exportar dados do visual)")
        btn.click()
        return True

    # ------------------------------------------------------------- descoberta
    def discover(self, page) -> list[Path]:
        """Abre o relatório e salva screenshot + árvore de acessibilidade para ajustar selectors.json."""
        self.auth.ensure_bi_session(page)
        self.open_menu(page, config.BI_MENU_EMPLACAMENTOS)
        frame = self.report_frame(page)
        out = [p for p in (self.browser.dump_aria(frame, "emplacamentos"), self.browser.screenshot_error(page, "discover_emplacamentos")) if p]
        return out
