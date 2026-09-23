"""AssobensPriceDownloader: BI → "Comparativo de Preços" (relatório Power BI) → leitura da tabela de preços.

Estratégias, em ordem: (1) tabela acessível (role=row/columnheader/gridcell) do relatório;
(2) "Exportar dados" do visual → CSV/XLSX → parse. Preços nunca são inventados: sem tabela = sem captura.
"""
from __future__ import annotations

import csv
import re
from datetime import datetime
from pathlib import Path

from . import config
from .browser import DownloadCatcher, first_present
from .errors import InterfaceChangedError
from .logutil import get_logger
from .normalizer import clean_text, parse_number

SOURCE = "assobens_precos_comparativo"


class AssobensPriceDownloader:
    def __init__(self, browser, auth, selectors: dict, emplacamentos_downloader):
        self.browser, self.auth, self.sel = browser, auth, selectors
        self.nav = emplacamentos_downloader
        self.log = get_logger()

    def capture(self, page, out_dir: Path | None = None) -> list[dict]:
        self.auth.ensure_bi_session(page)
        self.nav.open_menu(page, config.BI_MENU_PRECOS)
        frame = self.nav.report_frame(page)
        self.enter_report(page, frame)
        ref = self.reference_date(frame)
        rows = self._read_accessible_table(frame)
        if not rows:
            rows = self._export_and_parse(page, frame, out_dir or config.STORAGE_DIR)
        if not rows:
            self.browser.screenshot_error(page, "precos_tabela")
            self.browser.dump_aria(frame, "precos")
            raise InterfaceChangedError("tabela do Comparativo de Preços não encontrada")
        captured_at = datetime.now(config.TZ).isoformat(timespec="seconds")
        out = [{"source": SOURCE, "manufacturer": r["manufacturer"], "model": r["model"], "segment": r.get("segment", ""),
                "price": r["price"], "reference_date": ref, "captured_at": captured_at} for r in rows if r.get("price") is not None]
        self.log.info("preços capturados: %d linhas (referência %s)", len(out), ref)
        return out

    def enter_report(self, page, frame) -> None:
        """O relatório abre numa capa com o botão 'ACESSAR RELATÓRIO' (navegação de página do Power BI)."""
        entry = first_present(frame, self.sel["precos"]["entry_link"], timeout_ms=15_000)
        if entry is None:
            self.log.info("capa do Comparativo de Preços não encontrada; seguindo com a página atual")
            return
        entry.click()
        self.log.info("capa do Comparativo de Preços: 'ACESSAR RELATÓRIO' clicado")
        waited = 0
        while waited < 60_000:
            try:
                if frame.get_by_role("grid").count() or frame.get_by_role("columnheader").count() or frame.get_by_role("combobox").count() > 1:
                    break
            except Exception:
                pass
            page.wait_for_timeout(2_000)
            waited += 2_000
        page.wait_for_timeout(3_000)
        self.browser.dump_aria(frame, "precos_relatorio")

    def reference_date(self, frame) -> str:
        loc = first_present(frame, self.sel["precos"]["reference_date_text"], visible=False, timeout_ms=0)
        if loc is not None:
            m = re.search(r"(\d{2})/(\d{2})/(\d{4})", loc.inner_text() or "")
            if m:
                return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
        return datetime.now(config.TZ).date().isoformat()

    # ------------------------------------------------------------- estratégia 1
    def _read_accessible_table(self, frame) -> list[dict]:
        rows_loc = None
        for c in self.sel["precos"]["table_rows"]:
            try:
                loc = frame.get_by_role("row") if c["kind"] == "role" else frame.locator(c["value"])
                if loc.count() >= 2:
                    rows_loc = loc
                    break
            except Exception:
                continue
        if rows_loc is None:
            return []
        table = []
        for i in range(min(rows_loc.count(), 2000)):
            try:
                cells = rows_loc.nth(i).locator("[role=columnheader],[role=gridcell],[role=cell],th,td").all_inner_texts()
            except Exception:
                continue
            if cells:
                table.append([clean_text(c, upper=False) for c in cells])
        return self.parse_table(table)

    # ------------------------------------------------------------- estratégia 2
    def _export_and_parse(self, page, frame, out_dir: Path) -> list[dict]:
        catcher = DownloadCatcher(page.context, page)
        if not self.nav.export_visual(page, frame, self.sel["precos"].get("visual_title")):
            return []
        dl = catcher.wait(90)
        if dl is None:
            return []
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir / f"{datetime.now(config.TZ):%H%M}_precos{Path(dl.suggested_filename or '.csv').suffix or '.csv'}"
        dl.save_as(str(target))
        if target.suffix.lower() == ".csv":
            text = target.read_text(encoding="utf-8-sig", errors="replace")
            table = [row for row in csv.reader(text.splitlines(), delimiter=";" if text.count(";") > text.count(",") else ",")]
        else:
            import openpyxl
            wb = openpyxl.load_workbook(target, read_only=True, data_only=True)
            table = [["" if c is None else str(c) for c in r] for r in wb.worksheets[0].iter_rows(values_only=True)]
            wb.close()
        return self.parse_table(table)

    # ------------------------------------------------------------- parse
    def parse_table(self, table: list[list[str]]) -> list[dict]:
        """Identifica as colunas pelo cabeçalho (fabricante, modelo, preço, segmento) e devolve linhas de preço."""
        s = self.sel["precos"]
        hdr_i, cols = -1, {}
        for i, row in enumerate(table[:10]):
            found = {}
            for j, h in enumerate(row):
                hn = clean_text(h, accents=False)
                for key in ("col_manufacturer", "col_model", "col_price", "col_segment"):
                    if key not in found and re.search(s[key], hn, re.I):
                        found[key] = j
            if "col_model" in found and "col_price" in found and len(found) > len(cols):
                hdr_i, cols = i, found
        if hdr_i < 0:
            return []
        out = []
        for row in table[hdr_i + 1:]:
            if len(row) <= max(cols.values()):
                continue
            price = parse_number(row[cols["col_price"]])
            model = clean_text(row[cols["col_model"]], accents=False)
            if price is None or not model:
                continue
            manufacturer = clean_text(row[cols["col_manufacturer"]], accents=False) if "col_manufacturer" in cols else ""
            if not manufacturer:
                manufacturer = model.split("/")[0] if "/" in model else ""
            out.append({"manufacturer": manufacturer, "model": model, "price": price,
                        "segment": clean_text(row[cols["col_segment"]], accents=False) if "col_segment" in cols else ""})
        return out

    def discover(self, page) -> list[Path]:
        self.auth.ensure_bi_session(page)
        self.nav.open_menu(page, config.BI_MENU_PRECOS)
        frame = self.nav.report_frame(page)
        return [p for p in (self.browser.dump_aria(frame, "precos"), self.browser.screenshot_error(page, "discover_precos")) if p]
