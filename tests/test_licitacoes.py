"""Motor de licitações: só produtos (veículo completo × peças/motores), marca por concessionária e coleta incremental."""
import json
from datetime import date

import pytest

from licitacoes import catalogo, config
from licitacoes.coletor import Coletor, janelas_mensais, limites_mes

OBJ = "Aquisição de veículos para a frota municipal"


def seg(desc, objeto=OBJ, vu=None, un=None):
    r = catalogo.classificar(desc, objeto, vu, un)
    return r and r["segmento"]


@pytest.mark.parametrize("desc,vu,esperado", [
    # veículo completo, por classe de peso
    ("Caminhão 3/4 baú, PBT 8 toneladas", 320000, "CAMINHAO_LEVE"),
    ("CAMINHÃO TOCO 4X2, PBT 13.000 KG, CARROCERIA CARGA SECA", 420000, "CAMINHAO_MEDIO"),
    ("CAMINHÃO TRUCK 6X2 CARROCERIA CARGA SECA", 520000, "CAMINHAO_SEMIPESADO"),
    ("CAMINHÃO BASCULANTE 6X4, CAPACIDADE 12 M3, PBT 23 T", 690000, "CAMINHAO_EXTRAPESADO"),
    ("Cavalo mecânico 6x2, 0 km, para semirreboque", 780000, "CAMINHAO_EXTRAPESADO"),
    ("CAMINHAO 6X2 TRUCK, NOVO, ZERO KM, EQUIPADO COM SISTEMA ROLL-ON/ROLL-OFF", 863045, "CAMINHAO_SEMIPESADO"),
    ("Caminhão pipa 10.000 litros, zero km", 480000, "CAMINHAO_NI"),
    ("AMBULÂNCIA TIPO A SIMPLES REMOÇÃO (FURGÃO) 0 KM", 301927, "VAN_FURGAO"),
    ("Van de passageiros 15 lugares, zero km", 330000, "VAN_FURGAO"),
    ("ÔNIBUS RURAL ESCOLAR ORE 2, 44 LUGARES", 680000, "ONIBUS"),
    # peças e motores de linha pesada
    ("COMPRESSOR DE AR P/ CAMINHÃO (VW 8.150)", 2633, "PECAS"),
    ("BIELETA (VAN SPRINTER)", 130, "PECAS"),
    ("Kit embreagem para ônibus Volare", 3900, "PECAS"),
    ("Motor diesel completo para caminhão", 68000, "MOTOR_CONJUNTO"),
    ("VOLANTE DO MOTOR (VW 12170 / 11130)", 1677, "PECAS"),
    # fora: serviço, locação, passeio, picape, combustível, máquina, frota leve
    ("Locação de caminhão pipa com motorista", None, None),
    ("LOCAÇÃO DE CAMINHÃO BASCULANTE TRUCADO", 300000, None),
    ("Manutenção preventiva e corretiva de caminhões e ônibus da frota", 50000, None),
    ("CONTRATAÇÃO DE EMPRESA ESPECIALIZADA NA PRESTAÇÃO DE SERVIÇO DE ADMINISTRAÇÃO E GERENCIAMENTO", 1.5, None),
    ("Veículo picape 4x4, cabine dupla, zero quilômetro, motor a diesel", 319231, None),
    ("AQUISIÇÃO DE VEICULOS AUTOMOTORES TIPO PASSEIO ZERO KM PARA TRANSPORTE SANITÁRIO", 103637, None),
    ("Veículo tipo caminhonete cabine dupla 4x4", 294598, None),
    ("GASOLINA COMUM", 6, None),
    ("PNEU 275/80 R22.5 PARA CAMINHÃO", 2400, None),
    ("RETROESCAVADEIRA 4X4", 650000, None),
    ("Pastilha de freio", 120, None),
    ("Removex desengraxante sujeiras pesadas 5L", 55, None),
])
def test_classificar(desc, vu, esperado):
    assert seg(desc, vu=vu, un="UN") == esperado


def test_locacao_por_unidade_de_tempo_fica_fora():
    assert seg("CAMINHÃO CARROCERIA ABERTA 7.700 KG", vu=12166, un="MÊS") is None
    assert seg("CAMINHÃO PRANCHA", vu=367.82, un="HORA") is None
    assert seg("Caminhão para equipamento de limpeza a sucção", vu=405498, un="SERVIÇOS - SRV") is None


def test_peca_de_frota_leve_fica_fora():
    assert seg("Pastilha de freio", "Peças para manutenção do veículo Fiat Siena placa MSL1831", 120, "UN") is None
    assert seg("Pastilha de freio (MB 1113)", "Aquisição de peças para caminhões", 120, "UN") == "PECAS"


def test_implemento_e_pbt():
    r = catalogo.classificar("CAMINHÃO BASCULANTE 6X4, PBT 23.000 KG", OBJ, 690000, "UN")
    assert r["impl"] == "Basculante" and r["pbt"] == 23.0
    assert catalogo.pbt_toneladas("PBT mínimo de 16 toneladas") == 16.0
    assert catalogo.pbt_toneladas("PESO BRUTO TOTAL 7.700 KG") == 7.7


@pytest.mark.parametrize("desc,esperado", [
    ("CAMINHÃO BASCULANTE 6X4, CAPACIDADE 12 M3", True),
    ("Aquisição de 01 (um) ônibus rural escolar ORE 2", True),
    ("VEICULO AUTOMOTOR NOVO, ZERO QUILOMETRO, TIPO CAMINHÃO BAÚ", True),
    ("Chassi de caminhão 6x2 com cabine", True),
    ("COMPRESSOR DE AR P/ CAMINHÃO (VW 12170 / 11130 )", False),
    ("KIT EMBREAGEM PARA ÔNIBUS VOLARE", False),
    ("Bateria 150Ah para caminhão", False),
    ("RETROVISOR DO CAMINHÃO BASCULANTE", False),
])
def test_veiculo_completo(desc, esperado):
    assert catalogo.veiculo_completo(desc) is esperado


def test_objeto_relevante():
    assert catalogo.objeto_relevante("Registro de preço para aquisição de caminhão basculante")
    assert catalogo.objeto_relevante("Aquisição de peças para manutenção da frota de caminhões")
    assert not catalogo.objeto_relevante("Fornecimento de combustíveis para a frota municipal")
    assert not catalogo.objeto_relevante("Serviços de limpeza hospitalar")
    assert not catalogo.objeto_relevante("Contratação de empresa para prestação de serviço de locação de caminhão pipa")
    assert not catalogo.objeto_relevante("CONTRATAÇÃO DE EMPRESA ESPECIALIZADA PARA PRESTAÇÃO DE SERVIÇOS DE MANUTENÇÃO DA FROTA DE VEÍCULOS")


def test_marca_descricao_e_fornecedor():
    assert catalogo.marca_descricao("Caminhão Mercedes-Benz Atego 1719 ou similar") == ("M.BENZ", True)
    assert catalogo.marca_descricao("Ônibus VW 15.190 OD") == ("VW", False)
    mapa = catalogo.mapa_fornecedor_marca({"COVEZI CAMINHOES E ONIBUS LTDA": {"IVECO": 200, "M.BENZ": 1},
                                           "X CAR VEICULOS LTDA": {"VW": 10, "FORD": 10}})
    assert catalogo.marca_fornecedor("Covezi Caminhões e Ônibus Ltda.", mapa) == "IVECO"
    assert catalogo.marca_fornecedor("TECAR DIESEL CAMINHOES E ONIBUS LTDA", mapa) == "M.BENZ"
    assert catalogo.marca_fornecedor("X CAR VEICULOS LTDA", mapa) is None


def test_janelas_e_limites():
    assert janelas_mensais(date(2026, 8, 1), date(2026, 11, 4)) == ["2026-10", "2026-09", "2026-08"]
    assert limites_mes("2024-02") == ("2024-02-01", "2024-02-29")
    assert limites_mes("2025-12") == ("2025-12-01", "2025-12-31")


def compra(seq, objeto, atual="2026-10-01T10:00:00"):
    return {"orgaoEntidade": {"cnpj": "01105329000180", "razaoSocial": "MUNICIPIO X", "esferaId": "M", "poderId": "E"},
            "anoCompra": 2026, "sequencialCompra": seq, "objetoCompra": objeto, "modalidadeId": 6,
            "modalidadeNome": "Pregão - Eletrônico", "srp": True, "numeroCompra": str(seq), "processo": "1/2026",
            "unidadeOrgao": {"ufSigla": "GO", "municipioNome": "Hidrolândia", "codigoIbge": "5209705", "nomeUnidade": "SEC OBRAS"},
            "valorTotalEstimado": 900000, "valorTotalHomologado": 850000, "dataPublicacaoPncp": "2026-09-10T08:00:00",
            "dataAtualizacaoGlobal": atual, "situacaoCompraNome": "Divulgada no PNCP"}


class FakeClient:
    def __init__(self, por_janela):
        self.por_janela, self.requests, self.chamadas = por_janela, 0, []

    def contratacoes(self, rota, ini, fim, uf, mod, cnpj=None):
        self.requests += 1
        self.chamadas.append((rota, ini[:7], uf, mod, cnpj))
        return list(self.por_janela.get((rota, ini[:7], uf if not cnpj else cnpj, mod), []))

    def itens(self, cnpj, ano, seq):
        self.requests += 1
        return {1: [{"numeroItem": 1, "descricao": "CAMINHÃO BASCULANTE 6X4 Mercedes-Benz ou similar", "quantidade": 2,
                     "unidadeMedida": "UN", "valorUnitarioEstimado": 700000, "valorTotal": 1400000, "temResultado": True},
                    {"numeroItem": 2, "descricao": "Gasolina comum", "quantidade": 1000, "temResultado": False}],
                2: [{"numeroItem": 1, "descricao": "Material de escritório", "quantidade": 1, "temResultado": False}]}.get(seq, [
                    {"numeroItem": 1, "descricao": "CAMINHÃO BASCULANTE 6X4, ZERO KM", "quantidade": 3, "unidadeMedida": "UN",
                     "valorUnitarioEstimado": 690000, "valorTotal": 2070000, "temResultado": False}])

    def resultados(self, cnpj, ano, seq, item):
        self.requests += 1
        return [{"niFornecedor": "02714977000953", "nomeRazaoSocialFornecedor": "TECAR CAMINHOES E SERVICOS LTDA",
                 "porteFornecedorNome": "Demais", "quantidadeHomologada": 2, "valorUnitarioHomologado": 670000,
                 "valorTotalHomologado": 1340000, "dataResultado": "2026-09-30"}]


@pytest.fixture
def lic_paths(tmp_path, monkeypatch):
    for k in ("ESTADO_PATH", "COMPRAS_PATH", "VEICULOS_PATH", "POSVENDA_PATH", "LEGADO_ITENS_PATH"):
        monkeypatch.setattr(config, k, tmp_path / (k.lower() + ".json"))
    return tmp_path


def test_coleta_incremental_com_checkpoint(lic_paths):
    hoje = date(2026, 11, 4)
    jan = {("atualizacao", "2026-11", "GO", 6): [compra(1, "Aquisição de caminhão basculante"), compra(2, "Aquisição de veículos e material de escritório")],
           ("publicacao", "2026-10", "GO", 6): [compra(3, "Serviços de limpeza")]}
    cli = FakeClient(jan)
    col = Coletor(client=cli, ufs=["GO"], modalidades=[6], inicio=date(2026, 9, 1))
    res = col.run(minutos=60, hoje=hoje)
    assert res.erro is None and res.compras_relevantes == 1 and res.itens_relevantes == 1 and res.resultados == 1
    itens = json.loads(config.VEICULOS_PATH.read_text(encoding="utf-8"))["itens"]
    assert json.loads(config.POSVENDA_PATH.read_text(encoding="utf-8"))["itens"] == []
    assert len(itens) == 1 and itens[0]["seg"] == "CAMINHAO_EXTRAPESADO" and itens[0]["impl"] == "Basculante" and itens[0]["marca_desc"] == "M.BENZ" and itens[0]["similar"]
    assert itens[0]["r"][0]["marca_forn"] == "M.BENZ" and itens[0]["r"][0]["vu"] == 670000
    est = json.loads(config.ESTADO_PATH.read_text(encoding="utf-8"))
    assert est["ultima_atualizacao"] == "2026-11-04" and est["meses_concluidos"] == 2 and est["meses_total"] == 2
    assert "01105329000180-2026-2" in est["descartadas"]

    # segunda execução: nada novo para varrer; compra inalterada não é rebaixada, alterada é
    cli2 = FakeClient({("atualizacao", "2026-11", "GO", 6): [compra(1, "Aquisição de caminhão basculante"),
                                                             compra(2, "Aquisição de veículos e material de escritório")]})
    col2 = Coletor(client=cli2, ufs=["GO"], modalidades=[6], inicio=date(2026, 9, 1))
    col2.run(minutos=60, hoje=hoje)
    assert [c[0] for c in cli2.chamadas] == ["atualizacao"] and cli2.requests == 1
    cli3 = FakeClient({("atualizacao", "2026-11", "GO", 6): [compra(1, "Aquisição de caminhão basculante", atual="2026-11-03T09:00:00")]})
    Coletor(client=cli3, ufs=["GO"], modalidades=[6], inicio=date(2026, 9, 1)).run(minutos=60, hoje=hoje)
    assert cli3.requests == 3   # atualização + itens + resultados da compra alterada


def test_coleta_respeita_prazo(lic_paths):
    t = iter(range(0, 10_000, 100))
    jan = {("atualizacao", "2026-11", "GO", 6): [], ("publicacao", "2026-10", "GO", 6): [compra(1, "caminhão basculante")]}
    col = Coletor(client=FakeClient(jan), ufs=["GO"], modalidades=[6], inicio=date(2026, 1, 1), clock=lambda: next(t))
    col.run(minutos=1, hoje=date(2026, 11, 4))
    est = json.loads(config.ESTADO_PATH.read_text(encoding="utf-8"))
    assert est["meses_concluidos"] < est["meses_total"]


def test_bases_separadas():
    assert catalogo.base_do_segmento("CAMINHAO_EXTRAPESADO") == "VEICULOS" and catalogo.base_do_segmento("ONIBUS") == "VEICULOS"
    assert {catalogo.base_do_segmento(s) for s in ("PECAS", "MOTOR_CONJUNTO")} == {"POSVENDA"}


class FakeCG:
    """Compras.gov.br simulado: dois pregões de GO (um de veículo, um já publicado no PNCP) e um de outra UF."""
    def __init__(self, homologa=True):
        self.requests, self.homologa = 0, homologa

    def uasgs(self, ufs):
        self.requests += 1
        return {"989583": {"uf": "GO", "municipio": "SANTA RITA DO ARAGUAIA", "ibge": 5219506, "nome": "PREF SANTA RITA",
                           "cnpj": "01105329000180", "sisg": False}}

    def pregoes(self, ini, fim):
        self.requests += 1
        if not ini.startswith("2022-03"):
            return []
        base = {"co_uasg": 989583, "no_orgao": "PREFEITURA MUNICIPAL DE SANTA RITA DO ARAGUAIA", "no_ausg": "PREF SANTA RITA",
                "ds_situacao_pregao": "homologado", "ds_tipo_pregao_compra": "SISRP", "dt_data_edital": "2022-03-10T00:00:00",
                "dt_resultado": "2022-04-01T10:00:00", "dt_alteracao": "2023-01-01T00:00:00", "valor_estimado_total": 700000}
        return [{**base, "id_compra": "98958305000012022", "numero": 12022, "tx_objeto": "Aquisição de caminhão basculante"},
                {**base, "id_compra": "98958305000012022", "numero": 12022, "tx_objeto": "Aquisição de caminhão basculante"},  # repetido
                {**base, "id_compra": "98958305000072022", "numero": 72022, "tx_objeto": "Aquisição de caminhão pipa"},     # já no PNCP
                {**base, "co_uasg": 111111, "id_compra": "11111105000012022", "numero": 12022, "tx_objeto": "Aquisição de caminhão"}]

    def itens(self, uasg, numero):
        self.requests += 1
        return [{"numero_item_licitacao": 1, "id_compra_item": "9895830500001202200001", "nome_material": "CAMINHÃO BASCULANTE 6X4, PBT 23.000 KG, ZERO KM",
                 "quantidade": 1, "unidade": "UN", "valor_estimado": 690000, "cnpj_fornecedor": "02714977000953", "nome_fornecedor": "TECAR CAMINHOES E SERVICOS LTDA"},
                {"numero_item_licitacao": 2, "codigo_item_servico": 123, "nome_servico": "Manutenção", "quantidade": 1, "valor_estimado": 9000}]

    def uasgs_do_orgao(self, cnpj):
        self.requests += 1
        return {}

    def homologados(self, uasg, ini, fim):
        self.requests += 1
        return {"9895830500001202200001": {"valor_homologado_item": 655000, "quantidade_item": 1, "dt_hom": "2022-04-01"}} if self.homologa else {}


def test_comprasgov_segunda_fonte(lic_paths):
    from licitacoes import coletor as mod
    pncp = FakeClient({})
    col = Coletor(client=pncp, ufs=["GO"], modalidades=[6], inicio=date(2022, 3, 1), cg=FakeCG())
    col.compras["01105329000180-2022-7"] = {"id": "01105329000180-2022-7", "orgao_cnpj": "01105329000180", "ano": 2022, "numero": "7",
                                            "fonte": "PNCP", "atualizada": "x", "itens_em": "x"}
    col.itens[("01105329000180-2022-7", 1)] = {"compra": "01105329000180-2022-7", "n": 1, "desc": "CAMINHÃO PIPA ZERO KM 6X4",
                                                "seg": "CAMINHAO_EXTRAPESADO", "tipo": "AQUISICAO", "qtd": 1, "un": "UN", "vu_est": 500000, "r": []}
    res = col.run(minutos=60, hoje=date(2022, 5, 10))
    cg = {k: v for k, v in col.compras.items() if k.startswith("CG-")}
    assert list(cg) == ["CG-98958305000012022"]                       # outra UF fora; o que já está no PNCP fora
    c = cg["CG-98958305000012022"]
    assert c["fonte"] == "COMPRASGOV" and c["uf"] == "GO" and c["esfera"] == "M" and c["srp"] and c["numero"] == "1" and c["ano"] == 2022
    its = [i for k, i in col.itens.items() if k[0] == "CG-98958305000012022"]
    assert len(its) == 1 and its[0]["seg"] == "CAMINHAO_EXTRAPESADO" and its[0]["impl"] == "Basculante"   # serviço ignorado
    r = its[0]["r"][0]
    assert r["vu"] == 655000 and not r["preco_pendente"] and r["marca_forn"] == "M.BENZ"
    assert "CG-98958305000072022" in col.descartadas
    est = json.loads(config.ESTADO_PATH.read_text(encoding="utf-8"))
    assert est["cg_meses_concluidos"] == est["cg_meses_total"] == 2


def test_comprasgov_sem_homologado_marca_preco_pendente(lic_paths):
    col = Coletor(client=FakeClient({}), ufs=["GO"], modalidades=[6], inicio=date(2022, 3, 1), cg=FakeCG(homologa=False))
    col.run(minutos=60, hoje=date(2022, 5, 10))
    r = col.itens[("CG-98958305000012022", 1)]["r"][0]
    assert r["vu"] is None and r["preco_pendente"] and r["nome"].startswith("TECAR")


def test_objeto_veiculo_no_historico():
    assert catalogo.objeto_veiculo("Aquisição de caminhão basculante para a Secretaria de Obras")
    assert catalogo.objeto_veiculo("Registro de preços para aquisição de veículos tipo van e micro-ônibus")
    assert not catalogo.objeto_veiculo("Aquisição de peças para manutenção da frota de caminhões")
    assert not catalogo.objeto_veiculo("Locação de caminhão pipa")


def compra_codevasf(seq, objeto):
    c = compra(seq, objeto)
    c["orgaoEntidade"] = {"cnpj": "00399857000126", "razaoSocial": "CODEVASF", "esferaId": "F", "poderId": "E"}
    c["unidadeOrgao"] = {"ufSigla": "DF", "municipioNome": "Brasília", "codigoIbge": "5300108", "nomeUnidade": "SEDE"}
    return c


def test_orgao_alvo_busca_por_cnpj_e_marca_escopo_nacional(lic_paths):
    jan = {("publicacao", "2026-01", "00399857000126", 6): [compra_codevasf(9, "Aquisição de caminhão basculante"),
                                                           compra_codevasf(10, "Aquisição de peças para caminhões")]}
    cli = FakeClient(jan)
    col = Coletor(client=cli, ufs=["GO"], modalidades=[6], inicio=date(2026, 1, 1))
    col.alvos = {"00399857000126": {"nome": "COMPANHIA DE DESENVOLVIMENTO DOS VALES", "n": 374}}
    col.run(minutos=60, hoje=date(2026, 3, 5))
    assert any(ch[4] == "00399857000126" and ch[2] is None for ch in cli.chamadas)      # sem filtro de UF
    c = col.compras["00399857000126-2026-9"]
    assert c["escopo"] == "NACIONAL" and c["alvo"] and c["uf"] == "DF"
    assert "00399857000126-2026-10" not in col.compras        # peças não entram no histórico/alvos
    est = json.loads(config.ESTADO_PATH.read_text(encoding="utf-8"))
    assert any(k.startswith("00399857000126|2026|") for k in est["alvos_feitos"])
    n = cli.requests
    Coletor(client=cli, ufs=["GO"], modalidades=[6], inicio=date(2026, 1, 1)).run(minutos=60, hoje=date(2026, 3, 5))
    assert not any(ch[4] for ch in cli.chamadas[n:])             # alvo do ano já varrido nesta semana: não repete


def test_alvos_emplacamento(tmp_path):
    import openpyxl
    from licitacoes.alvos import alvos_emplacamento
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["CHASSI", "DATA EMPLACAMENTO", "MARCA", "UF", "CPFCNPJPROPRIETARIO", "TIPOCNPJPROPRIETARIO", "NOMEPROPRIETARIO"])
    ws.append(["A1", "2024-05-01", "IVECO", "GO", "00.399.857/0001-26", "JURIDICA", "COMPANHIA DE DESENVOLVIMENTO DOS VALES DO SAO FRANCISCO"])
    ws.append(["A2", "2025-02-01", "VW", "TO", "00.399.857/0001-26", "JURIDICA", "COMPANHIA DE DESENVOLVIMENTO DOS VALES DO SAO FRANCISCO"])
    ws.append(["A3", "2024-05-01", "VW", "GO", "05.128.774/0001-16", "JURIDICA", "J R TRANSPORTES"])
    ws.append(["A4", "2019-05-01", "VW", "GO", "01.105.329/0001-80", "JURIDICA", "MUNICIPIO DE HIDROLANDIA"])
    wb.save(tmp_path / "m.xlsx")
    a = alvos_emplacamento(tmp_path / "m.xlsx")
    assert list(a) == ["00399857000126"] and a["00399857000126"]["n"] == 2 and a["00399857000126"]["ufs"] == {"GO": 1, "TO": 1}


def test_cnpj_matriz_e_agrupamento_por_matriz():
    from licitacoes.alvos import cnpj_matriz, por_matriz
    assert cnpj_matriz("00399857") == "00399857000126"          # CODEVASF
    assert cnpj_matriz("05128774") == "05128774000116"
    g = por_matriz({"00399857003907": {"nome": "CODEVASF GO", "n": 278}, "00399857003818": {"nome": "CODEVASF TO", "n": 88}})
    assert list(g) == ["00399857000126"] and g["00399857000126"]["n"] == 366


def test_historico_paralelo_por_uf(lic_paths):
    jan = {("publicacao", "2026-10", "GO", 6): [compra(1, "Aquisição de caminhão basculante")],
           ("publicacao", "2026-10", "MT", 6): [compra(3, "Aquisição de ônibus escolar")]}
    col = Coletor(client=FakeClient(jan), ufs=["GO", "MT"], modalidades=[6], inicio=date(2026, 9, 1))
    res = col.run(minutos=60, hoje=date(2026, 11, 4))
    est = json.loads(config.ESTADO_PATH.read_text(encoding="utf-8"))
    assert {"GO|2026-10", "MT|2026-10", "GO|2026-09", "MT|2026-09"} <= set(est["janelas"])
    assert est["meses_concluidos"] == 2 and est["meses_por_uf"] == {"GO": 2, "MT": 2}
    assert res.compras_relevantes == 2 and not res.avisos


def test_mes_so_conta_quando_todas_as_ufs_terminam(lic_paths):
    col = Coletor(client=FakeClient({}), ufs=["GO", "MT"], modalidades=[6], inicio=date(2026, 9, 1))
    col.estado["janelas"] = {"GO|2026-10": "x", "2026-09": "x"}      # formato antigo (sem UF) vale para todas
    assert not col._mes_feito("2026-10") and col._mes_feito("2026-09")
