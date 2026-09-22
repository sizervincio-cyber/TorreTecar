"""AssobensBrowserService: Playwright (Chromium headless), screenshots de erro e resolução de localizadores.

Localizadores são semânticos (role/label/texto/aria) e ficam em selectors.json — nunca coordenadas X/Y.
"""
from __future__ import annotations

import json
import re
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from . import config
from .logutil import error_artifact_paths, get_logger, redact


def load_selectors(path: Path | None = None) -> dict:
    return json.loads((path or config.SELECTORS_PATH).read_text(encoding="utf-8"))


def resolve(scope: Any, candidate: dict):
    """Converte um candidato de selectors.json num Locator (scope = Page, Frame ou FrameLocator)."""
    kind = candidate.get("kind")
    if kind == "role":
        return scope.get_by_role(candidate["value"], name=re.compile(candidate["name"], re.I))
    if kind == "text":
        return scope.get_by_text(re.compile(candidate["name"], re.I))
    if kind == "label":
        return scope.get_by_label(re.compile(candidate["name"], re.I))
    if kind == "placeholder":
        return scope.get_by_placeholder(re.compile(candidate["name"], re.I))
    if kind == "css":
        return scope.locator(candidate["value"])
    raise ValueError(f"kind desconhecido em selectors.json: {kind}")


def first_present(scope: Any, candidates: list[dict], visible: bool = True, timeout_ms: int = 0):
    """Primeiro candidato presente (e visível, se pedido). Espera até timeout_ms no total."""
    deadline = time.time() + timeout_ms / 1000
    while True:
        for c in candidates:
            try:
                loc = resolve(scope, c)
                n = loc.count()
                if n == 0:
                    continue
                if not visible:
                    return loc.first
                for i in range(min(n, 5)):
                    if loc.nth(i).is_visible():
                        return loc.nth(i)
            except Exception:
                continue
        if time.time() >= deadline:
            return None
        time.sleep(0.5)


class DownloadCatcher:
    """Captura o download disparado por um clique, aconteça ele na mesma página ou num popup."""

    def __init__(self, context, page):
        self.downloads: list = []
        self._lock = threading.Lock()
        self.context, self.page = context, page
        page.on("download", self._on)
        context.on("page", lambda p: p.on("download", self._on))

    def _on(self, d):
        with self._lock:
            self.downloads.append(d)

    def wait(self, timeout_s: float = 120):
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            with self._lock:
                if self.downloads:
                    return self.downloads[0]
            self.page.wait_for_timeout(500)
        return None


class AssobensBrowserService:
    def __init__(self, headless: bool = True, slow_mo: int = 0, timeout_ms: int = 45_000):
        self.headless, self.slow_mo, self.timeout_ms = headless, slow_mo, timeout_ms
        self.log = get_logger()
        self._pw = self.browser = self.context = self.page = None

    def __enter__(self) -> "AssobensBrowserService":
        from playwright.sync_api import sync_playwright  # import tardio: testes não exigem o browser instalado
        self._pw = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=self.headless, slow_mo=self.slow_mo)
        self.context = self.browser.new_context(accept_downloads=True, locale="pt-BR", timezone_id="America/Sao_Paulo",
                                                viewport={"width": 1600, "height": 1000})
        self.context.set_default_timeout(self.timeout_ms)
        self.page = self.context.new_page()
        return self

    def __exit__(self, *exc) -> None:
        for closer in (lambda: self.context.close(), lambda: self.browser.close(), lambda: self._pw.stop()):
            try:
                closer()
            except Exception:
                pass

    # ------------------------------------------------------------- diagnóstico
    def screenshot_error(self, page, step: str, extra: dict | None = None) -> Path | None:
        """Screenshot + metadados (timestamp, URL, etapa). Sem cookies, tokens ou headers."""
        try:
            config.ERRORS_DIR.mkdir(parents=True, exist_ok=True)
            png, meta = error_artifact_paths(step)
            page.screenshot(path=str(png), full_page=True)
            meta.write_text(json.dumps({"timestamp": datetime.now(config.TZ).isoformat(timespec="seconds"),
                                        "url": redact(page.url), "etapa": step, **(extra or {})}, ensure_ascii=False, indent=1),
                            encoding="utf-8")
            self.log.info("screenshot de erro salvo em %s", png)
            return png
        except Exception as e:  # nunca deixa o diagnóstico derrubar o fluxo
            self.log.warning("não foi possível salvar screenshot: %s", e)
            return None

    def dump_aria(self, scope, name: str) -> Path | None:
        """Árvore de acessibilidade (aria snapshot) para descobrir/ajustar seletores."""
        try:
            config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
            out = config.LOGS_DIR / f"discover_{datetime.now(config.TZ):%Y%m%d_%H%M%S}_{name}.yaml"
            out.write_text(scope.locator("body").aria_snapshot(), encoding="utf-8")
            self.log.info("árvore de acessibilidade salva em %s", out)
            return out
        except Exception as e:
            self.log.warning("aria snapshot indisponível (%s)", e)
            return None
