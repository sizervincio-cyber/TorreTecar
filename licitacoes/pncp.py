"""Cliente da API pública do PNCP, com ritmo controlado e novas tentativas em falhas transitórias."""
from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from . import config

# Teto de consultas simultâneas ao PNCP somando todas as etapas paralelas da coleta (carga moderada numa API pública).
# Medido em 04/11/2026: com 8 simultâneas o PNCP respondeu 429 em 13% das consultas; 5 + freio global é o ponto seguro.
MAX_SIMULTANEAS = 5


class PncpError(Exception):
    pass


class PncpClient:
    def __init__(self, pause: float = 0.3, timeout: int = 120, opener=None, sleep=time.sleep, simultaneas: int = MAX_SIMULTANEAS,
                 relogio=time.monotonic):
        self.pause = pause
        self.timeout = timeout
        self._open = opener or urllib.request.urlopen
        self._sleep = sleep
        self._relogio = relogio
        self.requests = 0
        self.limitado = 0                      # respostas 429 (o servidor pediu para desacelerar)
        self._vaga = threading.BoundedSemaphore(simultaneas)
        self._trava = threading.Lock()
        self._freio_ate = 0.0                  # freio global: após um 429 todas as etapas esperam juntas
        self._seguidos = 0
        # Disjuntor: quando o PNCP fica fora do ar, a 1ª URL já gasta as 5 tentativas (~4 min). Depois disso as
        # demais consultas falham na hora, em vez de repetir 4 min para cada órgão/janela (uma noite inteira).
        self.fora_do_ar = False

    def _frear(self) -> None:
        with self._trava:
            self.limitado += 1
            self._seguidos += 1
            self._freio_ate = max(self._freio_ate, self._relogio() + min(60, 20 * self._seguidos))

    def _esperar_freio(self) -> None:
        with self._trava:
            espera = self._freio_ate - self._relogio()
        if espera > 0:
            self._sleep(espera)

    def _get(self, url: str):
        if self.fora_do_ar:
            raise PncpError(f"PNCP fora do ar nesta execução; não tentado: {url[:160]}")
        for tentativa in range(5):
            self._esperar_freio()
            if self.requests:
                self._sleep(self.pause)
            self.requests += 1
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "torre-tecar/1.0"})
            try:
                with self._vaga, self._open(req, timeout=self.timeout) as r:
                    body = r.read()
                    with self._trava:
                        self._seguidos = 0
                        self.fora_do_ar = False
                    return json.loads(body.decode("utf-8")) if body else None
            except urllib.error.HTTPError as e:
                if e.code in (204, 404):
                    return None
                if e.code == 429:
                    self._frear()              # o próximo _esperar_freio segura todas as etapas
                    continue
                if e.code in (500, 502, 503, 504):
                    self._sleep(min(120, 15 * (tentativa + 1)))   # espera fora da vaga: as demais seguem
                    continue
                raise PncpError(f"PNCP {e.code} em {url[:160]}")
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
                self._sleep(min(120, 15 * (tentativa + 1)))
        self.fora_do_ar = True
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
