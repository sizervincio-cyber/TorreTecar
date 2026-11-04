"""Catálogo de produtos: decide se um item de licitação interessa à Tecar e em que segmento ele entra.

Escopo: só PRODUTOS. Serviço, locação, manutenção, frete e gestão de frota ficam fora da base.
  - Base Veículos (foco): aquisição do veículo completo. Caminhões por classe de peso (leve, médio,
    semipesado/pesado, extrapesado), vans e furgões, e ônibus em segmento próprio.
  - Base Peças, acessórios e motores: componentes de linha pesada (caminhão, ônibus, van).

Os órgãos licitam pela descrição ("caminhão basculante 6x4, PBT 23 t"), não pela marca. A classificação é por texto
normalizado, valor unitário estimado e unidade de medida, em etapas que só deixam passar o que é produto de interesse.
"""
from __future__ import annotations

import re
import unicodedata


def norm(s) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode("ascii").upper()
    return re.sub(r"\s+", " ", s).strip()


def rx(p: str) -> re.Pattern:
    return re.compile(p)


SEGMENTOS = {
    "CAMINHAO_LEVE": "Caminhões leves",
    "CAMINHAO_MEDIO": "Caminhões médios",
    "CAMINHAO_SEMIPESADO": "Caminhões semipesados e pesados",
    "CAMINHAO_EXTRAPESADO": "Caminhões extrapesados",
    "CAMINHAO_NI": "Caminhões (classe não informada)",
    "VAN_FURGAO": "Vans e furgões",
    "ONIBUS": "Ônibus e micro-ônibus",
    "MOTOR_CONJUNTO": "Motores e conjuntos",
    "PECAS": "Peças e acessórios",
}
TIPOS = {"AQUISICAO": "Aquisição de veículo completo", "PECA": "Peças e acessórios"}
BASES = {"VEICULOS": "Veículos", "POSVENDA": "Peças, acessórios e motores"}
VEICULOS = {"CAMINHAO_LEVE", "CAMINHAO_MEDIO", "CAMINHAO_SEMIPESADO", "CAMINHAO_EXTRAPESADO", "CAMINHAO_NI",
            "VAN_FURGAO", "ONIBUS"}


def base_do_segmento(seg: str) -> str:
    return "VEICULOS" if seg in VEICULOS else "POSVENDA"


# ---------- etapa 0: o objeto da contratação (filtro barato, antes de baixar itens) ----------
OBJETO_RELEVANTE = rx(r"CAMINH(?!ONETE)|ONIBUS|VEICUL|FROTA|AMBULANC|FURGA|\bVANS?\b|BASCULANT|CACAMBA|\bPIPA\b|"
                      r"COMPACTADOR|COLETOR|PRANCHA|MUNCK|GUINDAUTO|CAVALO MECANICO|CHASSI|PECAS|TRANSPORTE ESCOLAR|"
                      r"LINHA PESADA|MERCEDES|SPRINTER|ACCELO|ATEGO|ACTROS|PATRULHA MECANIZADA|MOTOR")
OBJETO_SERVICO = rx(r"^(?:\W*\[[^\]]*\]\W*)?(?:REGISTRO DE PRECOS?\W*(?:PARA|COM A FINALIDADE DE|VISANDO)?\W*)?"
                    r"(?:A\s+)?(?:FUTURA E EVENTUAL\s+)?(?:CONTRATACAO DE (?:EMPRESA|PESSOA JURIDICA)[^,;.]{0,80}?\b(?:PARA|NA|EM)\b"
                    r"[^,;.]{0,40}?\b(?:PRESTACAO|LOCACAO|EXECUCAO|SERVICO)|PRESTACAO DE SERVICO|LOCACAO|SERVICOS? DE)")
OBJETO_PRODUTO = rx(r"AQUISICAO|FORNECIMENTO|COMPRA\b|\bPECAS|MATERIA")
OBJETO_DESCARTE = rx(r"COMBUSTIV|GASOLINA|ETANOL|ABASTECIMENTO|SEGURO|LAVAGEM|RASTREAMENTO|MONITORAMENTO|LEILAO|"
                     r"CARTAO|GERENCIAMENTO DE FROTA|TRANSPORTE ESCOLAR TERCEIRIZADO")
OBJETO_FORTE = rx(r"CAMINH(?!ONETE)|ONIBUS|PECAS|AMBULANC|\bVANS?\b|FURGA")


OBJETO_VEICULO = rx(r"CAMINH(?!ONETE)|ONIBUS|MICRO-?ONIBUS|AMBULANC|FURGA|\bVANS?\b|VEICUL|CHASSI|BASCULANT|CACAMBA|"
                    r"\bPIPA\b|COMPACTADOR|COLETOR|PRANCHA|MUNCK|GUINDAUTO|CAVALO MECANICO|PATRULHA MECANIZADA|"
                    r"TRANSPORTE ESCOLAR|UNIDADE MOVEL|SPRINTER|ACCELO|ATEGO|ACTROS")


def objeto_veiculo(objeto: str) -> bool:
    """Objeto que pode ser compra de veículo completo (usado no histórico, onde o foco é veículo)."""
    o = norm(objeto)
    return objeto_relevante(objeto) and bool(OBJETO_VEICULO.search(o)) and not re.search(r"^(?:\W*\[[^\]]*\]\W*)?(?:AQUISICAO DE )?PECAS", o)


def objeto_relevante(objeto: str) -> bool:
    """Contratação que pode conter produto de interesse. Serviço puro (locação, manutenção, transporte) é descartado
    aqui mesmo, sem baixar itens."""
    o = norm(objeto)
    if not OBJETO_RELEVANTE.search(o):
        return False
    if OBJETO_SERVICO.search(o) and not OBJETO_PRODUTO.search(o):
        return False
    return not (OBJETO_DESCARTE.search(o) and not OBJETO_FORTE.search(o))


# ---------- etapa 1: não é produto de interesse ----------
SERVICO = rx(r"LOCACAO|ALUGUEL|\bLOCAR\b|LOCATIVO|PRESTACAO|SERVICO|MAO DE OBRA|MANUTENC|REVISAO|CONSERTO|REPARO|"
             r"RETIFICA|FUNILARIA|LANTERNAGEM|DIAGNOSTICO|ASSISTENCIA TECNICA|FRETE|TRANSPORTE DE|ADMINISTRACAO|"
             r"GERENCIAMENTO|INSTALACAO|MONTAGEM|COM MOTORISTA|MOTORISTA|OPERADOR|TAXA DE")
UN_TEMPO = rx(r"^(?:MES|MESES|HORA|HORAS|H|HR|DIARIA|DIARIAS|DIA|DIAS|KM|QUILOMETRO|SEMANA|SERVICOS?|SRV|SV)\b")
DESCARTE = rx(r"COMBUSTIV|GASOLINA|ETANOL|OLEO DIESEL|DIESEL S-?10|\bARLA\b|PNEU|CAMARA DE AR|SEGURO|LAVAGEM|RASTREAD|"
              r"MOTOCICL|MOTONETA|BICICLET|\bTRATOR|RETRO ?ESCAVADEIRA|MOTONIVELADORA|PA CARREGADEIRA|ESCAVADEIRA|"
              r"ROLO COMPACTADOR|COMPACTADOR DE SOLO|MINI ?CARREGADEIRA|MOTOR ?BOMBA|ROCADEIRA|GERADOR|ELETROBOMBA|"
              r"BOMBA SUBMERS|PORTAO|EMPILHADEIRA|(?<!FILTRO DE )(?<!FILTRO )OLEO LUBRIFICANTE|GRAXA|ADITIVO|DESENGRAXANTE|DETERGENTE")
PASSEIO = rx(r"PASSEIO|SEDAN|HATCH|\bSUV\b|PICK-? ?UP|PICAPE|CAMINHONETE|CAMIONETE|MINIVAN|UTILITARIO LEVE|"
             r"\b[57] LUGARES|POPULAR|\bFLEX\b|MOTOCICL|\bMOTOS?\b|"
             r"\b(?:SIENA|PALIO|UNO|MOBI|ARGO|CRONOS|STRADA|TORO|FIORINO|DOBLO|GOL|VOYAGE|SAVEIRO|POLO|VIRTUS|FOX|"
             r"AMAROK|ONIX|PRISMA|CELTA|CORSA|COBALT|SPIN|S-?10|TRACKER|HB ?20|CRETA|KWID|LOGAN|SANDERO|DUSTER|"
             r"OROCH|HILUX|ETIOS|YARIS|COROLLA|RANGER|ECOSPORT|FIESTA|KA|L ?200|CIVIC|CITY|FIT|COMPASS|RENEGADE)\b")

# ---------- etapa 2: veículo completo ----------
S_ONIBUS = rx(r"ONIBUS|MICRO-? ?ONIBUS|MICROONIBUS")
S_VAN = rx(r"AMBULANC|\bVANS?\b|FURGAO|SPRINTER|DUCATO|\bMASTER\b|\bDAILY\b|UNIDADE MOVEL|UTI MOVEL|CONSULTORIO MOVEL")
S_CAMINHAO = rx(r"CAMINH(?!ONETE)|CHASSI|CAVALO MECANICO|TRATOR RODOVIARIO|\bVUC\b")
INICIO_VEICULO = rx(r"^(?:\W*\d+\W*)?(?:ITEM \d+\W*)?(?:AQUISICAO|COMPRA|FORNECIMENTO)?\W*(?:DE\W*)?"
                    r"(?:\(?\d+\)?\W*|UM\W*|UMA\W*|\(UM\)\W*|\(UMA\)\W*)?(?:\(?\w+\)?\W*)?"
                    r"(?:VEICULOS?|CAMINH(?!ONETE)|ONIBUS|MICRO|VANS?\b|FURGAO|AMBULANC|CHASSIS?|CAVALO|UNIDADE MOVEL|UTI MOVEL)")
COMPONENTE_DE = rx(r"\b(?:P/|PARA|PRA|DE|DO|DA|DOS|DAS|EM)\s+(?:O\s+|A\s+|OS\s+)?(?:CAMINH|ONIBUS|MICRO|VANS?\b|FURGAO|AMBULANC|VEICULO)")
MARCADOR_VEICULO = rx(r"\bNOVO\b|ZERO ?(?:QUILOMETRO|KM)|0 ?KM|ANO[ /]?MODELO|ANO DE FABRICACAO|SEMI-?NOVO|\bUSADO\b|\bPBT\b|"
                      r"PESO BRUTO|CAPACIDADE (?:DE CARGA|MINIMA|PARA \d+)|\bTRACAO\b|\b[468] ?X ?[24]\b|CABINE|LUGARES|"
                      r"POTENCIA|ENTRE-?EIXOS|CARROCERIA|BASCULANTE|PIPA|COMPACTADOR")
VU_MIN_VEICULO = 40_000      # abaixo disso, item "de caminhão/van" é peça de catálogo, não o veículo
VU_MIN_MOTOR = 15_000        # motor completo/parcial, câmbio e diferencial custam mais que isso

# Implemento: atributo do caminhão (não segmento). Ordem = prioridade do rótulo.
IMPLEMENTOS = [
    ("Basculante", rx(r"BASCULANT|CACAMBA")),
    ("Pipa / tanque", rx(r"\bPIPA\b|TANQUE|ESPARGIDOR")),
    ("Coletor / compactador de lixo", rx(r"COMPACTADOR|COLETOR")),
    ("Guindauto / munck", rx(r"MUNCK|GUINDAUTO|GUINDASTE")),
    ("Poliguindaste / roll-on", rx(r"POLIGUINDASTE|ROLL-? ?ON")),
    ("Limpa-fossa / sucção", rx(r"LIMPA ?FOSSA|SUCCAO|VACUO|HIDROJATO")),
    ("Prancha / guincho", rx(r"PRANCHA|GUINCHO|AUTO SOCORRO|PLATAFORMA")),
    ("Baú / frigorífico", rx(r"\bBAU\b|FRIGORIF|ISOTERM")),
    ("Comboio", rx(r"COMBOIO")),
    ("Cesto aéreo", rx(r"CESTO AEREO")),
    ("Bombeiro / emergência", rx(r"AUTO ?BOMBA|BOMBEIRO|BRIGADA")),
    ("Carga seca / carroceria", rx(r"CARGA SECA|CARROCERIA")),
]
EXTRAPESADO = rx(r"CAVALO|TRATOR RODOVIARIO|\b6 ?X ?4\b|\b8 ?X ?4\b|TRACAD|EXTRAPESAD")
SEMIPESADO = rx(r"\b6 ?X ?2\b|\b8 ?X ?2\b|\bTRUCK\b|TRUCAD|SEMIPESAD|\bPESADO\b|BITRUCK")
MEDIO = rx(r"\bMEDIO\b|\bTOCO\b")
LEVE = rx(r"3/4|\bVUC\b|\bLEVE\b")
PBT = rx(r"(?:PBT|PESO BRUTO TOTAL)\D{0,30}?(\d{1,3}(?:[.,]\d{3})+|\d{1,6}(?:[.,]\d{1,2})?)\s*(KG|T\b|TON)?")

# ---------- etapa 3: peças e motores de linha pesada ----------
T_PECA = rx(r"\bPECAS?\b|FILTRO|PASTILHA|LONA DE FREIO|EMBREAGEM|AMORTECEDOR|ROLAMENTO|CORREIA|JUNTA|RETENTOR|"
            r"TAMBOR DE FREIO|DISCO DE FREIO|BATERIA|LAMPADA|PARA-?BRISA|RADIADOR|BOMBA INJETORA|BICO INJETOR|"
            r"CRUZETA|MOLA|FEIXE DE MOLA|BUCHA|TERMINAL DE DIRECAO|ALTERNADOR|MOTOR DE PARTIDA|COMPRESSOR|"
            r"RETROVISOR|PARA-?CHOQUE|FAROL|LANTERNA|VALVULA|SENSOR|MANGUEIRA|CABO|CILINDRO|BIELETA|BANDEJA|"
            r"PIVO|SEMI-?EIXO|EIXO|CUBO|ACESSORIO|TAPETE|BANCO|ASSENTO|ESPELHO|PALHETA|VIDRO|KIT\b|VOLANTE|VIRABREQUIM|"
            r"PISTAO|BIELA|BRONZINA|CARTER|SELO|ANEL|ENGRENAGEM|COROA|PINHAO|ATUADOR|INTERRUPTOR|CHAVE DE SETA")
S_MOTOR = rx(r"^(?:AQUISICAO DE |FORNECIMENTO DE )?(?:MOTOR|TURBINA|TURBO|CAIXA DE CAMBIO|CAMBIO|TRANSMISSAO|"
             r"DIFERENCIAL|CABECOTE|CONJUNTO MOTOR|BLOCO DO MOTOR)\b|MOTOR (?:DIESEL )?(?:COMPLETO|PARCIAL|REMANUFATURADO)")
LINHA_PESADA = rx(r"CAMINH(?!ONETE)|ONIBUS|MICRO-?ONIBUS|\bVANS?\b|SPRINTER|FURGAO|AMBULANC|\bMB\b|\bM\.? ?BENZ|MERCEDES|\bVW\b|"
                  r"VOLKSWAGEN|IVECO|VOLVO|SCANIA|\bFORD CARGO|AGRALE|\bDAF\b|VOLARE|LINHA PESADA|\bPESAD|"
                  r"ACCELO|ATEGO|ACTROS|AXOR|CONSTELLATION|DELIVERY|TECTOR|\b\d{1,2}\.\d{3}\b|\bOF ?1\d{3}\b")


def veiculo_completo(desc: str) -> bool:
    d = norm(desc)
    if INICIO_VEICULO.search(d):
        return True
    return bool(MARCADOR_VEICULO.search(d)) and not COMPONENTE_DE.search(d[:60])


def pbt_toneladas(desc: str) -> float | None:
    m = PBT.search(norm(desc))
    if not m:
        return None
    num, un = m.group(1), (m.group(2) or "").strip()
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", num):
        v = float(re.sub(r"[.,]", "", num))
    else:
        v = float(num.replace(",", "."))
    if un == "KG" or v >= 1000:
        v /= 1000
    return round(v, 1) if 2 <= v <= 80 else None


def classe_caminhao(desc: str) -> str:
    d = norm(desc)
    t = pbt_toneladas(d)
    if EXTRAPESADO.search(d) or (t and t >= 30):
        return "CAMINHAO_EXTRAPESADO"
    if SEMIPESADO.search(d) or (t and t >= 16):
        return "CAMINHAO_SEMIPESADO"
    if t:
        return "CAMINHAO_LEVE" if t < 10.5 else "CAMINHAO_MEDIO"
    if MEDIO.search(d):
        return "CAMINHAO_MEDIO"
    if LEVE.search(d):
        return "CAMINHAO_LEVE"
    return "CAMINHAO_NI"


def implemento(desc: str) -> str | None:
    d = norm(desc)
    for nome, p in IMPLEMENTOS:
        if p.search(d):
            return nome
    return None


def classificar(desc: str, objeto: str = "", vu: float | None = None, un: str | None = None) -> dict | None:
    """Segmento de um item que é PRODUTO de interesse, ou None.
    vu = valor unitário estimado e un = unidade de medida do edital, quando conhecidos.
    Retorno: {"segmento", "tipo", "impl" (implemento do caminhão), "pbt" (t)}."""
    d, o = norm(desc), norm(objeto)
    # etapa 1: fora do escopo de produtos
    if not d or DESCARTE.search(d) or PASSEIO.search(d):
        return None
    if un and UN_TEMPO.search(norm(un)):
        return None                                   # caminhão por hora/mês/serviço = locação
    peca = bool(T_PECA.search(d)) or bool(S_MOTOR.search(d))
    if SERVICO.search(d) and not peca:
        return None                                   # serviço, locação, manutenção, frete, gestão
    if re.search(r"LOCACAO|ALUGUEL", o) and not re.search(r"AQUISICAO|FORNECIMENTO|COMPRA", o):
        return None
    # etapa 2: veículo completo
    eh_veic = bool(S_ONIBUS.search(d) or S_VAN.search(d) or S_CAMINHAO.search(d))
    if eh_veic and not S_MOTOR.search(d) and veiculo_completo(d) and not (vu is not None and 0 < vu < VU_MIN_VEICULO):
        if S_ONIBUS.search(d):
            seg = "ONIBUS"
        elif S_VAN.search(d) and not S_CAMINHAO.search(d):
            seg = "VAN_FURGAO"
        else:
            seg = classe_caminhao(d)
        r = {"segmento": seg, "tipo": "AQUISICAO", "impl": None, "pbt": None}
        if seg.startswith("CAMINHAO"):
            r["impl"], r["pbt"] = implemento(d), pbt_toneladas(d)
        return r
    # etapa 3: peça ou motor de linha pesada
    if LINHA_PESADA.search(d) or LINHA_PESADA.search(o):
        if S_MOTOR.search(d) and (vu is None or vu >= VU_MIN_MOTOR):
            return {"segmento": "MOTOR_CONJUNTO", "tipo": "PECA", "impl": None, "pbt": None}
        barato = vu is not None and 0 < vu < VU_MIN_VEICULO
        if peca or eh_veic or (barato and (LINHA_PESADA.search(d) or re.search(r"\bPECAS\b|AUTOPECAS", o))):
            return {"segmento": "PECAS", "tipo": "PECA", "impl": None, "pbt": None}
    return None


# ---------- marca ----------
# Marca citada na descrição. Muitas especificações trazem "ou similar": a marca da descrição é referência, não entrega.
MARCAS = [
    ("M.BENZ", rx(r"MERCEDES|M\.? ?BENZ|ACCELO|ATEGO|ACTROS|\bAXOR\b|AROCS|SPRINTER|\bOF[ -]?1[0-9]{3}\b")),
    ("VW", rx(r"VOLKSWAGEN|\bVW\b|CONSTELLATION|\bDELIVERY\b|\bMETEOR\b|VOLKSBUS")),
    ("IVECO", rx(r"IVECO|\bDAILY\b|TECTOR|S-?WAY")),
    ("VOLVO", rx(r"VOLVO|\bFH ?\d{3}\b|\bVM ?\d{3}\b")),
    ("SCANIA", rx(r"SCANIA")),
    ("DAF", rx(r"\bDAF\b")),
    ("AGRALE", rx(r"AGRALE")),
    ("VOLARE", rx(r"VOLARE")),
    ("FORD", rx(r"\bFORD\b|\bCARGO \d{3,4}\b")),
    ("FIAT", rx(r"DUCATO")),
    ("RENAULT", rx(r"RENAULT|\bMASTER\b")),
    ("FOTON", rx(r"FOTON")),
    ("HYUNDAI", rx(r"HYUNDAI")),
]
SIMILAR = rx(r"OU SIMILAR|OU EQUIVALENTE|SIMILAR|EQUIVALENTE|REFERENCIA|DE REFERENCIA")


def marca_descricao(desc: str) -> tuple[str | None, bool]:
    """(marca citada, é referência 'ou similar')."""
    d = norm(desc)
    for marca, p in MARCAS:
        if p.search(d):
            return marca, bool(SIMILAR.search(d))
    return None, False


SUFIXOS = {"LTDA", "SA", "S", "A", "EIRELI", "ME", "EPP", "CIA", "EM", "RECUPERACAO", "JUDICIAL"}


def chave_empresa(nome: str) -> str:
    toks = [t for t in re.sub(r"[^A-Z0-9 ]", " ", norm(nome)).split() if t not in SUFIXOS]
    return " ".join(toks)


def mapa_fornecedor_marca(dealers: dict[str, dict[str, int]], minimo: int = 20, dominancia: float = 0.9) -> dict[str, str]:
    """Concessionária → marca, a partir dos emplacamentos (nome do concessionário × marca emplacada).
    Só entra quem tem volume e emplaca uma marca dominante."""
    out: dict[str, str] = {}
    for nome, marcas in dealers.items():
        tot = sum(marcas.values())
        if tot < minimo:
            continue
        marca, n = max(marcas.items(), key=lambda kv: kv[1])
        if n / tot >= dominancia and marca not in ("OUTROS", ""):
            out[chave_empresa(nome)] = marca
    return out


def marca_fornecedor(nome: str, mapa: dict[str, str]) -> str | None:
    k = chave_empresa(nome)
    if not k:
        return None
    if k in mapa:
        return mapa[k]
    if re.search(r"\bTECAR\b", k):
        return "M.BENZ"
    return None
