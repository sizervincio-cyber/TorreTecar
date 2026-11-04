"""Cliente da API pública do PNCP, com ritmo controlado e novas tentativas em falhas transitórias."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request

from . import config


class PncpError(Exception):
    pass


class PncpClient:
    def __init__(self, pause: float = 0.3, timeout: int = 120, opener=None, sleep=time.sleep):
        self.pause = pause
        self.timeout = timeout
        self._open = opener or urllib.request.urlopen
        self._sleep = sleep
        self.requests = 0

    def _get(self, url: str):
        for tentativa in range(5):
            if self.requests:
                self._sleep(self.pause)
            self.requests += 1
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "torre-tecar/1.0"})
            try:
                with self._open(req, timeout=self.timeout) as r:
                    body = r.read()
                    return json.loads(body.decode("utf-8")) if body else None
            except urllib.error.HTTPError as e:
                if e.code in (204, 404):
                    return None
                if e.code in (429, 500, 502, 503, 504):
                    self._sleep(min(120, 15 * (tentativa + 1)))
                    continue
                raise PncpError(f"PNCP {e.code} em {url[:160]}")
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
                self._sleep(min(120, 15 * (tentativa + 1)))
        raise PncpError(f"PNCP indisponível após 5 tentativas: {url[:160]}")

    def contratacoes(self, rota: str, ini: str, fim: str, uf: str | None, modalidade: int, cnpj: str | None = None):
        """Itera as contratações de uma janela. rota = 'publicacao' (por data de publicação) ou 'atualizacao'.
        Filtra pela UF da unidade compradora e/ou pelo CNPJ do órgão (busca de órgão-alvo, em qualquer UF)."""
        pagina = 1
        while True:
            params = {"dataInicial": ini.replace("-", ""), "dataFinal": fim.replace("-", ""),
                      "codigoModalidadeContratacao": modalidade, "pagina": pagina, "tamanhoPagina": config.PAGE_SIZE}
            if uf:
                params["uf"] = uf
            if cnpj:
                params["cnpj"] = cnpj
            q = urllib.parse.urlencode(params)
            d = self._get(f"{config.CONSULTA_URL}/v1/contratacoes/{rota}?{q}")
            if not d or not d.get("data"):
                return
            yield from d["data"]
            if not d.get("paginasRestantes"):
                return
            pagina += 1

    def itens(self, cnpj: str, ano: int, seq: int) -> list[dict]:
        out, pagina = [], 1
        while True:
            d = self._get(f"{config.PNCP_URL}/v1/orgaos/{cnpj}/compras/{ano}/{seq}/itens?pagina={pagina}&tamanhoPagina=500")
            if not d:
                return out
            out += d
            if len(d) < 500:
                return out
            pagina += 1

    def resultados(self, cnpj: str, ano: int, seq: int, item: int) -> list[dict]:
        return self._get(f"{config.PNCP_URL}/v1/orgaos/{cnpj}/compras/{ano}/{seq}/itens/{item}/resultados") or []
