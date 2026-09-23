"""AssobensPriceDownloader: BI → "Comparativo de Preços" (relatório Power BI) → capa "ACESSAR RELATÓRIO" →
para cada modelo do filtro "MODELO MB": gráfico "Modelo × Valor Indecx" (preço nacional) e matriz por UF.

Estrutura confirmada na árvore de acessibilidade (run 35817270681): o relatório compara um modelo Mercedes-Benz
(slicer "MODELO MB") com os concorrentes definidos pelo próprio ASSOBENS; o preço é o "Valor Indecx".
Preços nunca são inventados: só o que está na árvore do relatório é gravado.
"""
from __future__ import annotations

import re
from datetime import datetime

from . import config
from .browser import first_present
from .errors import InterfaceChangedError
from .logutil import get_logger
from .normalizer import normalize_brand, parse_number

SOURCE = "assobens_precos_comparativo"


def parse_brl(v: str) -> float | None:
    """'R$ 332.545' -> 332545.0 ; 'R$ 1.234,56' -> 1234.56 (formato exibido na matriz, ponto = milhar)."""
    s = (v or "").replace("R$", "").replace(" ", "").replace(" ", "").strip()
    if not s or s == "-":
        return None
    s = s.replace(".", "").replace(",", ".") if "," in s else s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


def label_split(label: str) -> tuple[str, str]:
    """'MB 1117' -> ('M.BENZ', 'MB 1117'); 'VW 11.180' -> ('VW', 'VW 11.180')."""
    fab = label.strip().split(" ")[0] if label.strip() else ""
    return normalize_brand(fab), label.strip()


def parse_aria_prices(txt: str, mb_model: str, reference_date: str, captured_at: str) -> list[dict]:
    """Extrai preços da árvore de acessibilidade do relatório para o grupo do modelo MB selecionado."""
    out: list[dict] = []

    def block(name: str) -> list[str]:
        m = re.search(rf'listbox "{re.escape(name)}":\n((?:\s+- option "[^"]*"\n)+)', txt)
        return re.findall(r'- option "([^"]*)"', m.group(1)) if m else []

    modelos, valores = block("Modelo"), block("Valor Indecx")
    if modelos and len(modelos) == len(valores):
        for modelo, valor in zip(modelos, valores):
            preco = parse_number(valor)
            if preco is None or preco <= 0:
                continue
            fab, mod = label_split(modelo)
            out.append({"source": SOURCE, "manufacturer": fab, "model": mod, "segment": f"Nacional|grupo {mb_model}",
                        "price": round(preco, 2), "reference_date": reference_date, "captured_at": captured_at})
    # matriz por UF: cabeçalho "MODELO" (modelos, 3 colunas cada), cabeçalho "UF" (Qtde./Valor Indecx/Var.%), linhas por UF
    lines = txt.splitlines()
    models: list[str] = []
    metrics: list[str] = []
    i = 0
    while i < len(lines):
        l = lines[i].strip()
        if l.startswith('- row "MODELO'):
            models, i = _collect(lines, i + 1, "columnheader"), i + 1
            models = models[1:] if models and models[0] == "MODELO" else models
            continue
        if l.startswith('- row "UF') and models:
            metrics, i = _collect(lines, i + 1, "columnheader"), i + 1
            metrics = metrics[1:] if metrics and metrics[0] == "UF" else metrics
            continue
        m = re.match(r'- rowheader "([^"]+)"', l)
        if m and models and metrics:
            uf = m.group(1)
            cells, i = _collect(lines, i + 1, "gridcell", allow_empty=True), i + 1
            if uf.lower() != "nacional":  # Nacional já vem (com mais precisão) do gráfico
                for j, val in enumerate(cells):
                    if j < len(models) and j < len(metrics) and metrics[j].lower().startswith("valor") and val:
                        preco = parse_brl(val)
                        if preco and preco > 0:
                            fab, mod = label_split(models[j])
                            out.append({"source": SOURCE, "manufacturer": fab, "model": mod, "segment": f"{uf}|grupo {mb_model}",
                                        "price": round(preco, 2), "reference_date": reference_date, "captured_at": captured_at})
            continue
        i += 1
    return out


def _collect(lines: list[str], start: int, role: str, allow_empty: bool = False) -> list[str]:
    """Nomes dos filhos consecutivos com o papel dado (gridcell sem nome => '')."""
    out = []
    i = start
    while i < len(lines):
        l = lines[i].strip()
        m = re.match(rf'- {role}(?: "([^"]*)")?:?$', l)
        if m:
            out.append(m.group(1) or "")
            i += 1
            # pula filhos (img/text) do gridcell
            while i < len(lines) and (lines[i].startswith(" " * (len(lines[i]) - len(lines[i].lstrip()))) and
                                      re.match(r"\s+- (img|text)", lines[i]) and not re.match(rf"\s+- {role}", lines[i])):
                i += 1
            continue
        if l.startswith("- row") or (l.startswith("- ") and not l.startswith(f"- {role}") and not re.match(r"- (img|text)", l)):
            break
        i += 1
    return out if allow_empty else [x for x in out if x]


class AssobensPriceDownloader:
    MAX_MODELOS = 60

    def __init__(self, browser, auth, selectors: dict, emplacamentos_downloader):
        self.browser, self.auth, self.sel = browser, auth, selectors
        self.nav = emplacamentos_downloader
        self.log = get_logger()

    def aria(self, frame) -> str:
        try:
            return frame.locator("body").aria_snapshot()
        except Exception:
            return ""

    def capture(self, page, out_dir=None) -> list[dict]:
        self.auth.ensure_bi_session(page)
        self.nav.open_menu(page, config.BI_MENU_PRECOS)
        frame = self.nav.report_frame(page)
        self.enter_report(page, frame)
        txt = self.aria(frame)
        ref = self.reference_date(txt)
        captured_at = datetime.now(config.TZ).isoformat(timespec="seconds")
        atual = self.current_mb_model(txt)
        modelos = self.list_mb_models(page, frame, txt)
        self.log.info("modelos MB no filtro: %d (atual: %s)", len(modelos), atual)
        out: list[dict] = []
        for n, mb in enumerate(modelos[: self.MAX_MODELOS]):
            if mb != atual and not self.select_mb_model(page, frame, mb):
                self.log.warning("não foi possível selecionar '%s' no filtro MODELO MB", mb)
                continue
            t = self.aria(frame)
            caps = parse_aria_prices(t, mb, ref, captured_at)
            if not caps and n == 0:
                self.browser.dump_aria(frame, "precos_sem_valores")
            out.extend(caps)
            atual = mb
        if not out:
            self.browser.screenshot_error(page, "precos_tabela")
            raise InterfaceChangedError("nenhum preço encontrado no Comparativo de Preços (gráfico 'Valor Indecx' ausente)")
        self.log.info("preços capturados: %d linhas em %d grupos (referência %s)", len(out), len({c['segment'].split('|')[1] for c in out}), ref)
        return out

    # ------------------------------------------------------------- navegação
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
                if frame.get_by_role("combobox", name=re.compile("MODELO MB", re.I)).count() and frame.get_by_role("grid").count():
                    break
            except Exception:
                pass
            page.wait_for_timeout(2_000)
            waited += 2_000
        page.wait_for_timeout(3_000)
        self.browser.dump_aria(frame, "precos_relatorio")

    def reference_date(self, txt: str) -> str:
        m = re.search(r"(?:mais recente|atualizad[oa])[^\d]{0,30}(\d{2})/(\d{2})/(\d{4})", txt, re.I)
        if m:
            return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
        return datetime.now(config.TZ).date().isoformat()

    @staticmethod
    def current_mb_model(txt: str) -> str:
        m = re.search(r'combobox "MODELO MB": ([^\n]+)', txt)
        return re.sub(r"[-]", "", m.group(1)).strip() if m else ""

    def list_mb_models(self, page, frame, txt_before: str) -> list[str]:
        """Abre o filtro 'MODELO MB' e lê as opções (as que só existem com o dropdown aberto)."""
        before = set(re.findall(r'- (?:option|checkbox) "([^"]+)"', txt_before))
        combo = frame.get_by_role("combobox", name=re.compile("MODELO MB", re.I)).first
        try:
            combo.click(timeout=10_000)
            page.wait_for_timeout(1_500)
        except Exception as e:
            self.log.warning("filtro MODELO MB não abriu: %s", str(e).splitlines()[0][:100])
            return [self.current_mb_model(txt_before)] if self.current_mb_model(txt_before) else []
        txt = self.aria(frame)
        self.browser.dump_aria(frame, "precos_dropdown")
        opts = []
        for o in re.findall(r'- (?:option|checkbox) "([^"]+)"', txt):
            o = re.sub(r"[-]", "", o).strip()
            if o and o not in before and o.lower() not in ("todos", "selecionar tudo", "select all") and o not in opts:
                opts.append(o)
        try:
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)
        except Exception:
            pass
        atual = self.current_mb_model(txt_before)
        if not opts:
            return [atual] if atual else []
        return opts

    def select_mb_model(self, page, frame, mb: str) -> bool:
        combo = frame.get_by_role("combobox", name=re.compile("MODELO MB", re.I)).first
        try:
            combo.click(timeout=10_000)
            page.wait_for_timeout(1_000)
        except Exception:
            return False
        rx = re.compile(rf"^\s*{re.escape(mb)}\s*$")
        for role in ("option", "checkbox"):
            loc = frame.get_by_role(role, name=rx)
            try:
                n = loc.count()
            except Exception:
                n = 0
            for k in range(n - 1, -1, -1):  # o dropdown fica depois dos visuais no DOM
                try:
                    if not loc.nth(k).is_visible():
                        continue
                    loc.nth(k).click(timeout=5_000)
                    page.wait_for_timeout(2_500)
                    if self.current_mb_model(self.aria(frame)) == mb:
                        return True
                except Exception:
                    continue
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass
        return False

    def discover(self, page):
        self.auth.ensure_bi_session(page)
        self.nav.open_menu(page, config.BI_MENU_PRECOS)
        frame = self.nav.report_frame(page)
        self.enter_report(page, frame)
        return [p for p in (self.browser.dump_aria(frame, "precos"), self.browser.screenshot_error(page, "discover_precos")) if p]
