"""Segunda fonte: Compras.gov.br Dados Abertos (dadosabertos.compras.gov.br), módulo legado.

Cobre os pregões feitos no Compras.gov.br pela lei antiga (8.666/10.520), de 2021 a 2023, que não foram ao PNCP.
O PNCP só recebe processos da Lei 14.133; por isso aqui só entram pregões com pertence14133=false (sem dupla
contagem). A API não filtra por UF: o recorte é pela lista de unidades compradoras (UASG) de GO, MT e TO.

Rotas usadas (documentadas no OpenAPI /v3/api-docs):
  modulo-uasg/1_consultarUasg              UASGs por UF (município, CNPJ do órgão)
  modulo-legado/3_consultarPregoes         pregões por data do edital (objeto, valores, situação)
  modulo-legado/2_consultarItemLicitacao   itens do pregão com fornecedor vencedor e valor estimado
  modulo-legado/4_consultarItensPregoes    valor homologado por item (instável: tentativa única, curta)
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://dadosabertos.compras.gov.br/"
MODALIDADE_PREGAO = 5
FIM_LEGADO = "2024-12"      # pregões da lei antiga ainda homologados até 2024; depois disso tudo vai ao PNCP


class ComprasGovError(Exception):
    pass


class ComprasGovClient:
    def __init__(self, pause: float = 0.5, timeout: int = 180, opener=None, sleep=time.sleep):
        self.pause = pause
        self.timeout = timeout
        self._open = opener or urllib.request.urlopen
        self._sleep = sleep
        self.requests = 0

    def _get(self, rota: str, params: dict, tentativas: int = 5, timeout: int | None = None):
        url = BASE + rota + "?" + urllib.parse.urlencode(params)
        for i in range(tentativas):
            if self.requests:
                self._sleep(self.pause)
            self.requests += 1
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "torre-tecar/1.0"})
            try:
                with self._open(req, timeout=timeout or self.timeout) as r:
                    body = r.read()
                    return json.loads(body.decode("utf-8")) if body else {}
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return {}
                # a API responde 400 de forma intermitente sob carga (testado): trata como transitório
                if e.code in (400, 429, 500, 502, 503, 504) and i < tentativas - 1:
                    self._sleep(min(120, 15 * (i + 1)))
                    continue
                raise ComprasGovError(f"Compras.gov.br {e.code} em {rota}")
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
                if i < tentativas - 1:
                    self._sleep(min(120, 15 * (i + 1)))
                    continue
                raise ComprasGovError(f"Compras.gov.br indisponível em {rota}")
        raise ComprasGovError(f"Compras.gov.br sem resposta em {rota}")

    def _paginas(self, rota: str, params: dict):
        pagina = 1
        while True:
            d = self._get(rota, {**params, "pagina": pagina, "tamanhoPagina": 500})
            yield from d.get("resultado") or []
            if not d.get("paginasRestantes"):
                return
            pagina += 1

    def uasgs(self, ufs) -> dict[str, dict]:
        out = {}
        for uf in ufs:
            for x in self._paginas("modulo-uasg/1_consultarUasg", {"siglaUf": uf, "statusUasg": "true"}):
                out[str(int(x["codigoUasg"]))] = {
                    "uf": x.get("siglaUf"), "municipio": x.get("nomeMunicipioIbge"), "ibge": x.get("codigoMunicipioIbge"),
                    "nome": x.get("nomeUasg"), "cnpj": x.get("cnpjCpfOrgao") or x.get("cnpjCpfUasg") or "",
                    "sisg": x.get("usoSisg"),
                }
        return out

    def pregoes(self, ini: str, fim: str):
        yield from self._paginas("modulo-legado/3_consultarPregoes",
                                 {"dt_data_edital_inicial": ini, "dt_data_edital_final": fim, "pertence14133": "false"})

    def itens(self, uasg: str, numero: int) -> list[dict]:
        return list(self._paginas("modulo-legado/2_consultarItemLicitacao",
                                  {"uasg": uasg, "numero_aviso": numero, "modalidade": MODALIDADE_PREGAO}))

    def homologados(self, uasg: str, ini: str, fim: str) -> dict[str, dict]:
        """id_compra_item → registro com valor homologado. Rota instável: uma tentativa curta; falha devolve {}."""
        try:
            d = self._get("modulo-legado/4_consultarItensPregoes",
                          {"co_uasg": uasg, "dt_hom_inicial": ini, "dt_hom_final": fim, "pagina": 1, "tamanhoPagina": 500},
                          tentativas=1, timeout=60)
        except ComprasGovError:
            return {}
        return {str(x.get("id_compra_item")): x for x in (d.get("resultado") or [])}


def link_compra(id_compra: str) -> str:
    """Página pública do processo no Compras.gov.br (mesmo formato citado nos editais publicados no PNCP)."""
    return f"https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=quadro-informativo&compra={id_compra}"
