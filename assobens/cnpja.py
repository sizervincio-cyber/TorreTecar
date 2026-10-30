"""Enriquecimento cadastral dos CNPJs da matriz pela CNPJá (https://cnpja.com/api).

Só dados da EMPRESA entram no arquivo versionado: razão social, situação, CNAE, porte, capital, Simples/MEI e
município. Telefones, e-mails, sócios (QSA) e logradouro são dados pessoais ou de contato e nunca são gravados.

Duas fontes, mesmo formato de resposta:
  - API Comercial  https://api.cnpja.com/office/{cnpj}   header Authorization: CNPJA_API_KEY
                   strategy=CACHE não consome créditos (base já armazenada na CNPJá); consulta online = 1 crédito.
  - API Pública    https://open.cnpja.com/office/{cnpj}  sem chave, 5 consultas/min por IP, defasagem até 45 dias.

O próprio empresas_cnpja.json serve de cache entre execuções (o runner do CI é efêmero): um CNPJ só é consultado de
novo quando a consulta anterior passou de max_age dias.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime

from . import config
from .logutil import get_logger
from .runlog import read_json, write_json_atomic

API_URL = "https://api.cnpja.com"
OPEN_URL = "https://open.cnpja.com"
OPEN_PER_MINUTE = 5

# Perfil de negócio pelo CNAE principal (prefixo do código de 7 dígitos). O mais específico vem primeiro.
PERFIS_CNAE = [
    ("4930", "Transporte rodoviário de carga"),
    ("492", "Transporte de passageiros"),
    ("5211", "Armazenagem e logística"), ("5250", "Armazenagem e logística"), ("52", "Armazenagem e logística"),
    ("7711", "Locação de veículos"), ("7719", "Locação de veículos"), ("77", "Locação de máquinas e equipamentos"),
    ("45", "Comércio de veículos e peças"),
    ("01", "Agropecuária"), ("02", "Agropecuária"), ("03", "Agropecuária"),
    ("05", "Mineração"), ("06", "Mineração"), ("07", "Mineração"), ("08", "Mineração"), ("09", "Mineração"),
    ("41", "Construção"), ("42", "Construção"), ("43", "Construção"),
    ("36", "Saneamento e resíduos"), ("37", "Saneamento e resíduos"), ("38", "Saneamento e resíduos"), ("39", "Saneamento e resíduos"),
    ("10", "Indústria de alimentos e bebidas"), ("11", "Indústria de alimentos e bebidas"),
    ("46", "Comércio atacadista"), ("47", "Comércio varejista"),
    ("84", "Administração pública"),
]


def perfil_cnae(codigo) -> str:
    c = re.sub(r"\D", "", str(codigo or "")).zfill(7) if codigo else ""
    if not c:
        return "Não informado"
    for pref, nome in PERFIS_CNAE:
        if c.startswith(pref):
            return nome
    if "12" <= c[:2] <= "33":
        return "Indústria"
    return "Outros"


def cnpj_digits(v) -> str | None:
    d = re.sub(r"\D", "", str(v or ""))
    return d if len(d) == 14 and len(set(d)) > 1 else None


def resumo_empresa(o: dict) -> dict:
    """Recorta a resposta de /office só com campos da empresa. Contatos, sócios e logradouro ficam de fora."""
    co = o.get("company") or {}
    ad = o.get("address") or {}
    main = o.get("mainActivity") or {}
    simples, simei = co.get("simples") or {}, co.get("simei") or {}
    return {
        "razao_social": co.get("name"),
        "nome_fantasia": o.get("alias"),
        "situacao": (o.get("status") or {}).get("text"),
        "data_situacao": o.get("statusDate"),
        "abertura": o.get("founded"),
        "matriz": o.get("head"),
        "natureza": (co.get("nature") or {}).get("text"),
        "porte": (co.get("size") or {}).get("acronym") or (co.get("size") or {}).get("text"),
        "capital_social": co.get("equity"),
        "cnae_principal": main.get("id"),
        "cnae_descricao": main.get("text"),
        "cnaes_secundarios": [a.get("id") for a in (o.get("sideActivities") or []) if a.get("id")],
        "perfil": perfil_cnae(main.get("id")),
        "simples": simples.get("optant"),
        "mei": simei.get("optant"),
        "municipio_ibge": ad.get("municipality"),
        "cidade": ad.get("city"),
        "uf": ad.get("state"),
        "cep": ad.get("zip"),
        "fonte_atualizada_em": o.get("updated"),
    }


class CnpjaError(Exception):
    pass


class CreditosEsgotados(CnpjaError):
    pass


class CnpjaClient:
    """GET /office/{cnpj} com controle de ritmo. Sem chave usa a API Pública."""

    def __init__(self, api_key: str | None = None, per_minute: int | None = None, timeout: int = 60, opener=None, sleep=time.sleep):
        self.api_key = (api_key or "").strip() or None
        self.base = API_URL if self.api_key else OPEN_URL
        self.per_minute = per_minute or (60 if self.api_key else OPEN_PER_MINUTE)
        self.timeout = timeout
        self._open = opener or urllib.request.urlopen
        self._sleep = sleep
        self._last = 0.0

    @property
    def publica(self) -> bool:
        return self.api_key is None

    def _get(self, path: str, params: dict | None = None) -> tuple[int, dict]:
        url = self.base + path + ("?" + urllib.parse.urlencode(params) if params else "")
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "torre-tecar/1.0",
                                                   **({"Authorization": self.api_key} if self.api_key else {})})
        try:
            with self._open(req, timeout=self.timeout) as r:
                return r.status, json.loads(r.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as e:
            try:
                body = json.loads(e.read().decode("utf-8") or "{}")
            except Exception:
                body = {}
            return e.code, body

    def _pace(self) -> None:
        gap = 60.0 / self.per_minute
        wait = self._last + gap - time.monotonic()
        if wait > 0:
            self._sleep(wait)
        self._last = time.monotonic()

    def credit(self) -> dict | None:
        if self.publica:
            return None
        st, body = self._get("/credit")
        return body if st == 200 else None

    def office(self, cnpj: str, strategy: str = "CACHE", max_age: int = 45) -> dict | None:
        """Dados do estabelecimento, ou None se a CNPJá não tem o CNPJ (404 / ausente do cache)."""
        params = None if self.publica else {"strategy": strategy, "maxAge": max_age, "simples": "true"}
        for tentativa in range(3):
            self._pace()
            st, body = self._get(f"/office/{cnpj}", params)
            if st == 200:
                return body
            if st == 404:
                return None
            if st == 429:
                if "credit" in str(body.get("message", "")).lower():
                    raise CreditosEsgotados(f"créditos CNPJá esgotados (necessários {body.get('required')}, restantes {body.get('remaining')})")
                self._sleep(60)  # limite por minuto: espera a janela virar
                continue
            if st in (500, 502, 503, 504):
                self._sleep(10 * (tentativa + 1))
                continue
            if st == 401:
                raise CnpjaError("chave CNPJá inválida (401): confira o secret CNPJA_API_KEY")
            raise CnpjaError(f"CNPJá respondeu {st}: {body.get('message', '')}"[:200])
        raise CnpjaError(f"CNPJá indisponível para {cnpj[:8]}… após 3 tentativas")


@dataclass
class CnpjaResult:
    consultados: int = 0
    atualizados: int = 0
    nao_encontrados: int = 0
    pendentes: int = 0
    erro: str | None = None
    perfis: dict = field(default_factory=dict)

    def resumo(self) -> str:
        s = (f"CNPJá: {self.consultados} consultados · {self.atualizados} atualizados · "
             f"{self.nao_encontrados} sem dados · {self.pendentes} pendentes")
        return s + (f" · interrompido: {self.erro}" if self.erro else "")


def candidatos(rows: list[dict]) -> list[str]:
    """CNPJs de pessoa jurídica da matriz, os de compra mais recente primeiro e, no empate, as maiores frotas."""
    ult, qtd = {}, Counter()
    for r in rows:
        if str(r.get("TIPOCNPJPROPRIETARIO", "")).upper() != "JURIDICA":
            continue
        c = cnpj_digits(r.get("CPFCNPJPROPRIETARIO"))
        if not c:
            continue
        qtd[c] += 1
        d = str(r.get("DATA EMPLACAMENTO") or "")[:10]
        if d > ult.get(c, ""):
            ult[c] = d
    return sorted(qtd, key=lambda c: (ult.get(c, "")[:4], qtd[c], ult.get(c, "")), reverse=True)


def _vencido(reg: dict | None, hoje: date, max_age: int) -> bool:
    if not reg or not reg.get("consultado_em"):
        return True
    try:
        return (hoje - date.fromisoformat(reg["consultado_em"][:10])).days >= max_age
    except ValueError:
        return True


class CnpjaEnricher:
    def __init__(self, client: CnpjaClient, path=None, log=None):
        self.client = client
        self.path = path or config.EMPRESAS_CNPJA_PATH
        self.log = log or get_logger()

    def run(self, rows: list[dict], *, limite: int | None = None, strategy: str = "CACHE", max_age: int = 45,
            hoje: date | None = None) -> CnpjaResult:
        hoje = hoje or datetime.now(config.TZ).date()
        base = read_json(self.path, {}) or {}
        empresas: dict = base.get("empresas", {})
        fila = [c for c in candidatos(rows) if _vencido(empresas.get(c), hoje, max_age)]
        res = CnpjaResult(pendentes=len(fila))
        lote = fila[:limite] if limite else fila
        fonte = "publica" if self.client.publica else f"comercial/{strategy}"
        self.log.info("CNPJá (%s): %d CNPJs na fila, %d nesta execução", fonte, len(fila), len(lote))
        try:
            for i, cnpj in enumerate(lote, 1):
                o = self.client.office(cnpj, strategy=strategy, max_age=max_age)
                res.consultados += 1
                if o is None:
                    res.nao_encontrados += 1
                    empresas[cnpj] = {"consultado_em": hoje.isoformat(), "fonte": fonte, "sem_dados": True}
                else:
                    res.atualizados += 1
                    empresas[cnpj] = {**resumo_empresa(o), "consultado_em": hoje.isoformat(), "fonte": fonte}
                res.pendentes -= 1
                if i % 50 == 0:
                    self._save(empresas, hoje)
        except CnpjaError as e:
            res.erro = str(e)
            self.log.warning("%s", e)
        finally:
            self._save(empresas, hoje)
        res.perfis = dict(Counter(v.get("perfil") for v in empresas.values() if not v.get("sem_dados")).most_common())
        self.log.info("%s", res.resumo())
        return res

    def _save(self, empresas: dict, hoje: date) -> None:
        write_json_atomic(self.path, {
            "_doc": "Cadastro de empresas (CNPJ de pessoa jurídica da matriz) pela CNPJá. Só dados da empresa: "
                    "sem telefones, e-mails, sócios ou logradouro.",
            "gerado_em": hoje.isoformat(),
            "total": len(empresas),
            "empresas": dict(sorted(empresas.items())),
        })


def api_key_from_env() -> str | None:
    config.load_dotenv()
    return os.environ.get("CNPJA_API_KEY", "").strip() or None
