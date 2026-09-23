"""AssobensAuthenticationService: login no Portal (WordPress) e sessão no BI (SSO ou login direto).

Login só é considerado bem-sucedido por evidência da área autenticada (nunca por HTTP 200):
- Portal: ausência de #login_error/#loginform e presença de body.logged-in/#wpadminbar/link do BI.
- BI: localStorage._pbiAssobens com token JWT e menu carregado.
"""
from __future__ import annotations

import json
import re

from . import config
from .browser import first_present, resolve
from .errors import AuthError, CredentialsMissingError, InterfaceChangedError, SessionExpiredError
from .logutil import get_logger

JWT_RE = re.compile(r"^[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}$")


def redact_url(u: str) -> str:
    return re.sub(r"(ssotoken|token)=[^&]+", r"\1=***", u or "")


class AssobensAuthenticationService:
    def __init__(self, credentials: config.Credentials, selectors: dict, browser=None):
        self.creds = credentials
        self.sel = selectors
        self.browser = browser  # opcional: usado só para screenshot/aria de diagnóstico
        self.log = get_logger()

    def _diag(self, page, name: str) -> None:
        if self.browser is None:
            return
        try:
            self.browser.screenshot_error(page, name)
            self.browser.dump_aria(page, name)
        except Exception:
            pass

    # ------------------------------------------------------------- portal
    def login_portal(self, page) -> None:
        if not self.creds.configured:
            raise CredentialsMissingError("ASSOBENS_USER / ASSOBENS_PASSWORD não configurados (.env ou secrets)")
        s = self.sel["portal"]
        page.goto(config.PORTAL_LOGIN_URL, wait_until="domcontentloaded")
        user = first_present(page, s["user"], timeout_ms=15_000)
        pwd = first_present(page, s["password"], timeout_ms=5_000)
        if user is None or pwd is None:
            raise AuthError("formulário de login do portal não encontrado (interface mudou?)")
        user.fill(self.creds.user)
        pwd.fill(self.creds.password)
        submit = first_present(page, s["submit"], timeout_ms=5_000)
        if submit is None:
            raise AuthError("botão de login do portal não encontrado")
        submit.click()
        try:
            page.wait_for_load_state("networkidle", timeout=30_000)
        except Exception:
            pass
        err = first_present(page, s["login_error"], timeout_ms=1_000)
        if err is not None:
            txt = (err.inner_text() or "").strip()[:160]
            raise AuthError(f"portal recusou o login: {txt or 'credenciais inválidas'}")
        if "wp-login.php" in page.url and page.locator("#loginform").count():
            raise AuthError("portal manteve o formulário de login: credenciais inválidas ou bloqueio")
        if first_present(page, s["logged_in"], visible=False, timeout_ms=10_000) is None:
            raise AuthError("login não confirmado: nenhum elemento da área autenticada do portal")
        self.log.info("login no portal confirmado (url=%s)", page.url)

    def bi_link(self, page) -> str | None:
        loc, href = self._find_bi_entry(page)
        return href if (href and "bi-assobens" in href) else None

    def _find_bi_entry(self, page):
        """Localiza a entrada do BI no portal: (locator, href). Ordem: href com bi-assobens/sso -> texto 'BI' em link/botão."""
        for c in self.sel["portal"]["bi_link"]:
            try:
                loc = resolve(page, c)
                if loc.count():
                    return loc.first, loc.first.get_attribute("href")
            except Exception:
                continue
        try:
            links = page.eval_on_selector_all(
                "a[href]", "els => els.map(e => ({href: e.href, text: (e.innerText || e.getAttribute('aria-label') || e.title || '').trim()}))")
        except Exception:
            links = []
        for pat in (r"bi-assobens|ssotoken|/sso\b", r"\bBI\b"):
            for l in links:
                alvo = l["href"] if pat.startswith("bi") else l["text"]
                if re.search(pat, alvo or "", re.I):
                    return page.locator(f'a[href="{l["href"]}"]').first, l["href"]
        btn = page.get_by_role("button", name=re.compile(r"\bBI\b", re.I))
        try:
            if btn.count():
                return btn.first, None
        except Exception:
            pass
        return None, None

    # ------------------------------------------------------------- BI
    def open_bi(self, page) -> dict:
        """Entra no BI a partir do portal (SSO). O BI não aceita a senha do portal em login direto."""
        loc, href = self._find_bi_entry(page)
        if loc is None:
            self.log.warning("entrada do BI não encontrada no portal (url=%s); salvando diagnóstico", page.url)
            self._diag(page, "portal_sem_link_bi")
            raise InterfaceChangedError("entrada do BI não encontrada na página do portal após o login (ver portal_sem_link_bi.png/.yaml)")
        self.log.info("entrada do BI encontrada (href=%s)", (href or "clique")[:120])
        if href and "bi-assobens" in href:
            page.goto(href, wait_until="domcontentloaded")
            session = self._wait_session(page, 40_000)
        else:
            session = self._enter_by_click(page, loc)
        if session is None:
            self._diag(page, "bi_sem_sessao")
            raise AuthError("BI não autenticou: sessão (_pbiAssobens) ausente após SSO")
        try:
            page.wait_for_url(re.compile(r"bi-assobens\.com\.br/(app|home|dashboard)?"), timeout=30_000)
        except Exception:
            pass
        self.log.info("BI autenticado (usuário %s, tipo %s, sso=%s)", session.get("email"), session.get("type"), session.get("isSSO"))
        return session

    def _enter_by_click(self, page, loc) -> dict | None:
        """Clica na entrada do BI; trata abertura em nova aba (popup) ou na mesma aba. A sessão fica no
        localStorage da origem bi-assobens.com.br, compartilhado por todas as abas do contexto."""
        popup = None
        try:
            with page.context.expect_page(timeout=8_000) as pi:
                loc.click()
            popup = pi.value
        except Exception:
            popup = None
        target = popup or page
        try:
            target.wait_for_load_state("domcontentloaded", timeout=30_000)
        except Exception:
            pass
        self._accept_cookies(target)
        session = self._wait_session(target, 40_000)
        if popup is not None:
            self.log.info("BI abriu em nova aba (%s); voltando para a aba principal", redact_url(popup.url))
            try:
                popup.close()
            except Exception:
                pass
            page.goto(config.BI_URL, wait_until="domcontentloaded")
            self._accept_cookies(page)
            session = self._wait_session(page, 20_000) or session
        return session

    def _bi_direct_login(self, page) -> None:
        s = self.sel["bi"]
        email = first_present(page, s["login_email"], timeout_ms=15_000)
        pwd = first_present(page, s["login_password"], timeout_ms=3_000)
        btn = first_present(page, s["login_submit"], timeout_ms=3_000)
        if email is None or pwd is None or btn is None:
            raise AuthError("formulário de login do BI não encontrado")
        email.fill(self.creds.user)
        pwd.fill(self.creds.password)
        btn.click()
        page.wait_for_timeout(3_000)
        if page.get_by_text(re.compile("login deve ser feito no Portal", re.I)).count():
            raise AuthError("BI exige autenticação via Portal (SSO) e o link do BI não foi encontrado no portal")
        if page.get_by_text(re.compile("Senha incorreta ou usu", re.I)).count():
            raise AuthError("BI recusou as credenciais do portal (usuário/senha do BI são outros): o acesso deve ser pelo SSO do portal")

    def _accept_cookies(self, page) -> None:
        # Banner de privacidade (edna): aceitar é necessário para a navegação; não há opção mais restritiva funcional.
        btn = first_present(page, self.sel["bi"]["cookie_accept"], timeout_ms=3_000)
        if btn is not None:
            try:
                btn.click()
            except Exception:
                pass

    def bi_session(self, page) -> dict | None:
        try:
            raw = page.evaluate(f"() => localStorage.getItem('{config.BI_STORAGE_KEY}')")
        except Exception:
            return None
        if not raw:
            return None
        try:
            data = json.loads(raw)
        except ValueError:
            return None
        tok = str(data.get("token", ""))
        if not JWT_RE.match(tok):
            return None
        return {k: v for k, v in data.items() if k != "token"}  # token nunca sai daqui (nem para logs)

    def _wait_session(self, page, timeout_ms: int) -> dict | None:
        waited = 0
        while waited < timeout_ms:
            s = self.bi_session(page)
            if s:
                return s
            page.wait_for_timeout(1_000)
            waited += 1_000
        return None

    def ensure_bi_session(self, page) -> dict:
        s = self.bi_session(page)
        if s is None:
            raise SessionExpiredError("sessão do BI ausente ou expirada")
        if first_present(page, self.sel["bi"]["login_email"], timeout_ms=0) is not None:
            raise SessionExpiredError("BI voltou para a tela de login: sessão expirada")
        return s
