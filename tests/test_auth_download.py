"""Autenticação, sessão expirada, download do Excel e mudança de interface — com Playwright simulado."""
import json
import re
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from assobens import config
from assobens.auth import AssobensAuthenticationService
from assobens.browser import load_selectors
from assobens.emplacamentos_downloader import AssobensEmplacamentosDownloader
from assobens.errors import AuthError, CredentialsMissingError, DownloadError, InterfaceChangedError, SessionExpiredError


class FakeLocator:
    def __init__(self, n=0, text="", href=None, visible=True):
        self.n, self.text, self.href, self.visible = n, text, href, visible
        self.filled, self.clicked = None, 0

    def count(self):
        return self.n

    @property
    def first(self):
        return self

    def nth(self, i):
        return self

    def is_visible(self):
        return self.visible

    def fill(self, v):
        self.filled = v

    def click(self):
        self.clicked += 1

    def inner_text(self):
        return self.text

    def get_attribute(self, k):
        return self.href

    def wait_for(self, **k):
        return None


class FakePage:
    """Resolve localizadores por regras simples: css/role/text -> FakeLocator configurado no teste."""

    def __init__(self, url="https://portal.assobens.org.br/wp-login.php", present=None, storage=None):
        self.url, self.present, self.storage = url, present or {}, storage
        self.context = MagicMock()
        self.handlers = {}

    def _find(self, key):
        for k, loc in self.present.items():
            if k in key:
                return loc
        return FakeLocator(0)

    def goto(self, url, **k):
        self.url = url

    def locator(self, css):
        return self._find(css)

    def get_by_label(self, rx):
        return self._find("label:" + rx.pattern)

    def get_by_placeholder(self, rx):
        return self._find("placeholder:" + rx.pattern)

    def get_by_role(self, role, name=None):
        return self._find(f"role:{role}:{name.pattern if name else ''}")

    def get_by_text(self, rx):
        return self._find("text:" + rx.pattern)

    def wait_for_load_state(self, *a, **k):
        pass

    def wait_for_timeout(self, ms):
        pass

    def wait_for_url(self, *a, **k):
        pass

    def evaluate(self, js):
        return self.storage

    def on(self, ev, fn):
        self.handlers[ev] = fn

    def frame_locator(self, css):
        return self

    @property
    def first(self):
        return self

    def screenshot(self, **k):
        Path(k["path"]).write_bytes(b"png")


SEL = load_selectors()
CREDS = config.Credentials("usuario@tecar.com.br", "segredo")


def test_credenciais_ausentes():
    with pytest.raises(CredentialsMissingError):
        AssobensAuthenticationService(config.Credentials("", ""), SEL).login_portal(FakePage())


def test_credenciais_invalidas_no_portal():
    page = FakePage(present={"label:usu": FakeLocator(1), "label:^senha": FakeLocator(1), "role:button:acessar": FakeLocator(1),
                             "#login_error": FakeLocator(1, text="ERRO: A senha que você digitou está incorreta."), "#loginform": FakeLocator(1)})
    with pytest.raises(AuthError) as e:
        AssobensAuthenticationService(CREDS, SEL).login_portal(page)
    assert "recusou" in str(e.value)
    assert page.present["label:usu"].filled == CREDS.user and page.present["label:^senha"].filled == "segredo"


def test_login_nao_confirmado_sem_elemento_autenticado():
    page = FakePage(present={"#user_login": FakeLocator(1), "#user_pass": FakeLocator(1), "#wp-submit": FakeLocator(1)})
    page.url = "https://portal.assobens.org.br/"
    with pytest.raises(AuthError) as e:
        AssobensAuthenticationService(CREDS, SEL).login_portal(page)
    assert "não confirmado" in str(e.value)


def test_login_ok_e_sso_para_o_bi():
    tok = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abcdefghijklmnop"
    page = FakePage(present={"#user_login": FakeLocator(1), "#user_pass": FakeLocator(1), "#wp-submit": FakeLocator(1),
                             "body.logged-in": FakeLocator(1), "a[href*='bi-assobens": FakeLocator(1, href="https://bi-assobens.com.br/?ssotoken=abc")},
                    storage=json.dumps({"id": 1, "token": tok, "email": "u@x", "type": "dealer", "isSSO": True}))
    page.url = "https://portal.assobens.org.br/"
    auth = AssobensAuthenticationService(CREDS, SEL)
    auth.login_portal(page)
    s = auth.open_bi(page)
    assert page.url.startswith("https://bi-assobens.com.br/?ssotoken=")
    assert s["email"] == "u@x" and "token" not in s          # token nunca é devolvido/logado


def test_sessao_expirada():
    auth = AssobensAuthenticationService(CREDS, SEL)
    with pytest.raises(SessionExpiredError):
        auth.ensure_bi_session(FakePage(url="https://bi-assobens.com.br/", storage=None))
    with pytest.raises(SessionExpiredError):   # token presente mas não é JWT
        auth.ensure_bi_session(FakePage(url="https://bi-assobens.com.br/", storage=json.dumps({"token": "invalido"})))


def _downloader(page, tmp_path, monkeypatch):
    monkeypatch.setattr(config, "ERRORS_DIR", tmp_path / "errors")
    monkeypatch.setattr(config, "LOGS_DIR", tmp_path / "logs")
    browser = MagicMock()
    browser.page = page
    browser.screenshot_error = MagicMock(return_value=tmp_path / "erro.png")
    auth = MagicMock()
    return AssobensEmplacamentosDownloader(browser, auth, SEL), browser


def test_download_do_excel(tmp_path, monkeypatch):
    page = FakePage(url="https://bi-assobens.com.br/home",
                    present={"role:link:Veículos": FakeLocator(1), "#report iframe": FakeLocator(1), ".visualContainer": FakeLocator(1),
                             "role:tab:^ve[ií]culos$": FakeLocator(1), "[title*='Excel'": FakeLocator(1)})
    dl, browser = _downloader(page, tmp_path, monkeypatch)
    fake_download = MagicMock(suggested_filename="relatorio_analitico.xlsx")
    fake_download.save_as = lambda p: Path(p).write_bytes(b"xlsx-bytes")
    monkeypatch.setattr("assobens.emplacamentos_downloader.DownloadCatcher", lambda ctx, pg: MagicMock(wait=lambda t: fake_download))
    out = dl.download(page, tmp_path / "dia", "0800")
    assert out.name == "0800_emplacamentos.xlsx" and out.read_bytes() == b"xlsx-bytes"
    assert page.present["[title*='Excel'"].clicked == 1 and page.present["role:tab:^ve[ií]culos$"].clicked == 1


def test_botao_excel_ausente_gera_screenshot_e_erro(tmp_path, monkeypatch):
    page = FakePage(url="https://bi-assobens.com.br/home",
                    present={"role:link:Veículos": FakeLocator(1), "#report iframe": FakeLocator(1), ".visualContainer": FakeLocator(1),
                             "role:tab:^ve[ií]culos$": FakeLocator(1)})
    dl, browser = _downloader(page, tmp_path, monkeypatch)
    monkeypatch.setattr("assobens.browser.time.sleep", lambda s: None)
    monkeypatch.setattr("assobens.emplacamentos_downloader.DownloadCatcher", lambda ctx, pg: MagicMock(wait=lambda t: None))
    with pytest.raises(InterfaceChangedError):
        dl.download(page, tmp_path / "dia", "0800")
    assert browser.screenshot_error.called and browser.screenshot_error.call_args[0][1] == "botao_excel"


def test_clique_sem_download_e_erro_de_download(tmp_path, monkeypatch):
    page = FakePage(url="https://bi-assobens.com.br/home",
                    present={"role:link:Veículos": FakeLocator(1), "#report iframe": FakeLocator(1), ".visualContainer": FakeLocator(1),
                             "role:tab:^ve[ií]culos$": FakeLocator(1), "[title*='Excel'": FakeLocator(1)})
    dl, browser = _downloader(page, tmp_path, monkeypatch)
    monkeypatch.setattr("assobens.emplacamentos_downloader.DownloadCatcher", lambda ctx, pg: MagicMock(wait=lambda t: None))
    with pytest.raises(DownloadError):
        dl.download(page, tmp_path / "dia", "0800")
