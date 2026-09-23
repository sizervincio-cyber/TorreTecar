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
        self.last_kpis: dict = {}
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
    # ------------------------------------------------------------- KPIs do painel (só para conferência)
    KPI_PATTERNS = {
        "total_mercado": r"Quantidade de chassi total ([\d.]+)",
        "total_mb": r"Total Mercedes-Benz ([\d.]+)",
        "share_mb": r"%Share Mercedes-Benz ([\d,]+)%",
        "atualizado_em": r"mais recente (\d{2}/\d{2}/\d{4})",
        "periodo_inicio": r"Data de in[íi]cio[^\n]*\n\s*- /placeholder[^\n]*\n\s*- text: (\d{2}/\d{2}/\d{4})",
        "periodo_fim": r"Data de t[ée]rmino[^\n]*\n\s*- /placeholder[^\n]*\n\s*- text: (\d{2}/\d{2}/\d{4})",
    }

    def capture_dashboard_kpis(self, frame) -> dict:
        """Lê os totais exibidos no painel (árvore de acessibilidade) apenas para CONFERÊNCIA contra a Torre.
        A fonte dos dados importados continua sendo o Excel analítico."""
        try:
            txt = frame.locator("body").aria_snapshot()
        except Exception:
            return {}
        out: dict = {}
        for k, pat in self.KPI_PATTERNS.items():
            m = re.search(pat, txt)
            if m:
                out[k] = m.group(1)
        for k in ("total_mercado", "total_mb"):
            if k in out:
                out[k] = int(out[k].replace(".", ""))
        if "share_mb" in out:
            out["share_mb"] = float(out["share_mb"].replace(",", "."))
        out["fabricantes"] = [{"fabricante": f, "emplacamentos": int(n.replace(".", "")), "share": float(p.replace(",", "."))}
                              for f, n, p in re.findall(r'fabricante ([^.]+?)\. Total com outros ([\d.]+) \(([\d,]+)%\)', txt)]
        out["filtros"] = {k: v.strip() for k, v in re.findall(r'combobox "([^"]+)": ([^\n]*)', txt)}
        self.log.info("KPIs do painel para conferência: mercado=%s MB=%s share=%s%% período=%s..%s filtros=%s",
                      out.get("total_mercado"), out.get("total_mb"), out.get("share_mb"), out.get("periodo_inicio"),
                      out.get("periodo_fim"), {k: out["filtros"][k] for k in ("Região MB", "Distrito", "Segmentos", "Ano Emplac.") if k in out["filtros"]})
        return out

    def click_excel(self, page, frame, target: Path) -> Path:
        self.last_kpis = self.capture_dashboard_kpis(frame)
        catcher = DownloadCatcher(page.context, page)
        # O 'ícone de Excel' da página Veículos é um botão de navegação do Power BI que leva à página
        # 'Download dos dados analíticos', onde fica a tabela 'Analítico de Veículos' com 'Exportar dados'.
        nav = self._find_logged(frame, self.sel["emplacamentos"]["download_page_link"], 20_000, "link 'download do relatório analítico em Excel'")
        if nav is not None:
            nav.click()
            page.wait_for_timeout(4_000)
            try:
                frame.get_by_text(re.compile(self.sel["emplacamentos"]["visual_title"], re.I)).first.wait_for(state="visible", timeout=60_000)
                self.log.info("página de download aberta: tabela analítica visível")
            except Exception:
                self.log.warning("tabela analítica não ficou visível após a navegação")
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
        self.browser.dump_aria(frame, "relatorio_" + re.sub(r"[^a-z]", "", (title_rx or "x").lower())[:12])  # fica nos artefatos
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
            if visual is None:  # título do visual em qualquer elemento: passar o mouse nele já mostra o cabeçalho do visual
                try:
                    t = frame.get_by_text(re.compile(title_rx, re.I)).first
                    if t.count():
                        anc = t.locator("xpath=ancestor::*[self::visual-container or contains(@class,'visualContainer')][1]")
                        visual = anc.first if anc.count() else t
                        self.log.info("visual localizado pelo texto do título")
                except Exception:
                    visual = None
        if visual is None and title_rx:  # árvore real: group "Analítico de Veículos - dd-mm-aaaa" > heading + document > grid
            try:
                g = frame.get_by_role("group", name=re.compile(title_rx, re.I)).first
                if g.count():
                    visual = g
                    self.log.info("visual localizado pelo grupo acessível do título")
            except Exception:
                visual = None
        if visual is None:  # a tabela analítica é exposta como grid (role) — confirmado na árvore de acessibilidade
            try:
                g = frame.get_by_role("grid").first
                if g.count():
                    visual = g
                    self.log.info("visual localizado pelo papel 'grid' (tabela)")
            except Exception:
                visual = None
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
            self.browser.dump_aria(frame, "apos_hover")
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
