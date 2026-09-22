"""AssobensSpreadsheetParser: abre o XLSX/CSV baixado, encontra o cabeçalho pelo NOME das colunas
(nunca por posição) e devolve as linhas brutas como dicionários {campo_canônico: valor}.
"""
from __future__ import annotations

import csv
import hashlib
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from .errors import EmptyFileError, SchemaError

# Nome canônico -> aliases aceitos (mesma família de aliases da Torre + nomes do relatório ASSOBENS).
ALIASES: dict[str, list[str]] = {
    "CHASSI": ["CHASSI", "VIN", "NU_CHASSI"],
    "DATA EMPLACAMENTO": ["DATA EMPLACAMENTO", "DATA DE EMPLACAMENTO", "DATA", "DATA_COMPLETA", "DT EMPLACAMENTO", "DATA EMPLAC"],
    "MODELO": ["MODELO", "MODELO VEICULO", "MODELO VEÍCULO", "DESC MODELO"],
    "TRAÇÃO": ["TRAÇÃO", "TRACAO", "TRACAO VEICULO", "TRAÇAO", "TIPO TRACAO"],
    "MARCA": ["MARCA", "MONTADORA", "FABRICANTE", "MARCA_COMPLETA", "MARCA COMPLETA"],
    "SEGMENTO": ["SEGMENTO"],
    "SUBSEGMENTO": ["SUBSEGMENTO", "SUB SEGMENTO", "SUB-SEGMENTO"],
    "PLACA": ["PLACA"],
    "CONCESSIONÁRIO": ["CONCESSIONÁRIO", "CONCESSIONARIO", "DEALER", "RAZAO_SOCIAL", "RAZAO SOCIAL", "RAZÃO SOCIAL"],
    "CIDADE": ["CIDADE", "MUNICIPIO", "MUNICÍPIO", "C_NO_CIDADE"],
    "UF": ["UF", "ESTADO", "C_SG_ESTADO"],
    "DEALER AOP": ["DEALER AOP", "AOP DEALER", "DEALER_AOP", "DESC. ÁREA OPERACIONAL", "DESC AREA OPERACIONAL", "DESC. AREA OPERACIONAL"],
    "AOP": ["AOP", "AREA_OPERACIONAL", "ÁREA OPERACIONAL", "AREA OPERACIONAL", "COD AOP"],
    "ANOFABRICACAO": ["ANOFABRICACAO", "ANO FABRICACAO", "ANO FABRICAÇÃO", "ANO_FABRICACAO", "ANO FAB"],
    "ANOMODELO": ["ANOMODELO", "ANO MODELO", "ANO_MODELO"],
    "TIPO TERRENO": ["TIPO TERRENO", "TERRENO", "TIPO_TERRENO"],
    "CPFCNPJPROPRIETARIO": ["CPFCNPJPROPRIETARIO", "CPF/CNPJ PROPRIETARIO", "CPF/CNPJ PROPRIETÁRIO", "CPF OU CNPJ DO PROPRIETÁRIO",
                            "CPF OU CNPJ DO PROPRIETARIO", "C_CPFCNPJPROPRIETARIO", "CNPJ", "CPF/CNPJ", "DOCUMENTO", "DOCUMENTO PROPRIETARIO"],
    "TIPOCNPJPROPRIETARIO": ["TIPOCNPJPROPRIETARIO", "TIPO CNPJ PROPRIETARIO", "TIPO CPF/CNPJ PROPRIETARIO", "TIPO PESSOA",
                             "TIPO DE PESSOA", "C_TIPOCNPJPROPRIETARIO"],
    "NOMEPROPRIETARIO": ["NOMEPROPRIETARIO", "NOME PROPRIETARIO", "NOME PROPRIETÁRIO", "NOME DO PROPRIETÁRIO", "NOME DO PROPRIETARIO",
                         "C_NOMEPROPRIETARIO", "RAZAO SOCIAL PROPRIETARIO", "CLIENTE"],
    # Dimensões extras do ASSOBENS que, se existirem, são preservadas na matriz.
    "COMBUSTIVEL": ["COMBUSTIVEL", "COMBUSTÍVEL", "TIPO COMBUSTIVEL"],
    "GRUPO": ["GRUPO", "GRUPO ECONOMICO", "GRUPO ECONÔMICO"],
    "VERSAO": ["VERSAO", "VERSÃO"],
    "REGIAO MB": ["REGIAO MB", "REGIÃO MB", "REGIAO_MB"],
    "DISTRITO": ["DISTRITO"],
    "TIPO VEICULO": ["TIPO VEICULO", "TIPO VEÍCULO", "TIPO DE VEICULO"],
    "QUANTIDADE": ["QUANTIDADE", "QTD", "QTDE", "EMPLACAMENTOS", "QTD EMPLACAMENTOS"],
}
REQUIRED = ["CHASSI", "DATA EMPLACAMENTO", "MODELO", "MARCA", "CIDADE", "UF"]

# Dado pessoal de terceiros: nunca sai do arquivo bruto (que fica só em storage local).
BLOCKED_HEADERS = {"C_TELEFONE1", "C_TELEFONE2", "C_TELEFONE3", "C_CELULAR1", "C_CELULAR2", "C_DDD1", "C_DDD2", "C_DDD3",
                   "C_DDD_CELULAR1", "C_DDD_CELULAR2", "C_EMAIL", "C_NO_LOGR", "C_NU_LOGR", "C_NO_COMPL", "C_NO_BAIRRO", "C_NU_CEP",
                   "TELEFONE", "TELEFONE1", "TELEFONE2", "CELULAR", "E-MAIL", "EMAIL", "ENDERECO", "ENDEREÇO", "NUMERO", "NÚMERO",
                   "COMPLEMENTO", "BAIRRO", "CEP", "LOGRADOURO", "SOCIO", "SÓCIO", "DIRETOR", "CPF SOCIO", "NOME SOCIO"}


def norm_header(s: object) -> str:
    t = unicodedata.normalize("NFD", str(s if s is not None else ""))
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return " ".join(t.replace(" ", " ").strip().upper().split())


_ALIAS_INDEX: dict[str, str] = {norm_header(a): canon for canon, als in ALIASES.items() for a in als}
_BLOCKED_NORM = {norm_header(h) for h in BLOCKED_HEADERS}


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class ParsedSheet:
    sheet: str
    header_row: int
    headers: list[str]                 # cabeçalhos originais
    mapping: dict[str, int]            # canônico -> índice da coluna
    rows: list[dict]                   # {canônico: valor bruto}
    unknown_headers: list[str] = field(default_factory=list)
    blocked_headers: list[str] = field(default_factory=list)
    file_hash: str = ""
    file_name: str = ""

    @property
    def missing_required(self) -> list[str]:
        return [c for c in REQUIRED if c not in self.mapping]


class AssobensSpreadsheetParser:
    ALLOWED_EXT = {".xlsx", ".xlsm", ".csv"}
    HEADER_SCAN_ROWS = 15
    MIN_HEADER_MATCHES = 4

    def parse(self, path: str | Path) -> ParsedSheet:
        path = Path(path)
        if not path.exists() or path.stat().st_size == 0:
            raise EmptyFileError(f"Arquivo inexistente ou vazio: {path.name}")
        if path.suffix.lower() not in self.ALLOWED_EXT:
            raise SchemaError(f"Extensão não suportada: {path.suffix} (aceito: {', '.join(sorted(self.ALLOWED_EXT))})")
        if path.suffix.lower() == ".csv":
            sheets = [("csv", self._read_csv(path))]
        else:
            sheets = self._read_xlsx(path)
        best: ParsedSheet | None = None
        for name, aoa in sheets:
            ps = self._resolve(name, aoa)
            if ps and (best is None or len(ps.mapping) > len(best.mapping)):
                best = ps
        if best is None:
            if all(not any(str(c).strip() for r in aoa for c in r) for _, aoa in sheets):
                raise EmptyFileError(f"Arquivo sem conteúdo: {path.name}")
            raise SchemaError("Cabeçalho não reconhecido: nenhuma aba tem as colunas esperadas (estrutura do Excel mudou?)")
        if best.missing_required:
            raise SchemaError("Colunas obrigatórias ausentes: " + ", ".join(best.missing_required)
                              + " | cabeçalhos encontrados: " + ", ".join(best.headers[:30]))
        if not best.rows:
            raise EmptyFileError(f"Arquivo {path.name} tem cabeçalho mas nenhuma linha de dados")
        best.file_hash = file_sha256(path)
        best.file_name = path.name
        return best

    # ------------------------------------------------------------------ leitura
    def _read_xlsx(self, path: Path) -> list[tuple[str, list[list]]]:
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        out = []
        for ws in wb.worksheets:
            out.append((ws.title, [list(r) for r in ws.iter_rows(values_only=True)]))
        wb.close()
        return out

    def _read_csv(self, path: Path) -> list[list]:
        raw = path.read_bytes()
        for enc in ("utf-8-sig", "latin-1"):
            try:
                text = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=";,\t") if text.strip() else csv.excel
        return [row for row in csv.reader(text.splitlines(), dialect)]

    # ------------------------------------------------------------------ schema
    def _resolve(self, sheet: str, aoa: list[list]) -> ParsedSheet | None:
        best_i, best_map, best_hdr = -1, {}, []
        for i, row in enumerate(aoa[: self.HEADER_SCAN_ROWS]):
            hdr = [norm_header(c) for c in row]
            mapping: dict[str, int] = {}
            for j, h in enumerate(hdr):
                canon = _ALIAS_INDEX.get(h)
                if canon and canon not in mapping:
                    mapping[canon] = j
            if len(mapping) > len(best_map):
                best_i, best_map, best_hdr = i, mapping, [str(c if c is not None else "").strip() for c in row]
        if len(best_map) < self.MIN_HEADER_MATCHES:
            return None
        norm_hdr = [norm_header(h) for h in best_hdr]
        unknown = [h for h, n in zip(best_hdr, norm_hdr) if n and n not in _ALIAS_INDEX and n not in _BLOCKED_NORM]
        blocked = [h for h, n in zip(best_hdr, norm_hdr) if n in _BLOCKED_NORM]
        rows = []
        for r in aoa[best_i + 1:]:
            if r is None or not any(str(c).strip() for c in r if c is not None):
                continue
            rows.append({canon: (r[j] if j < len(r) else None) for canon, j in best_map.items()})
        return ParsedSheet(sheet=sheet, header_row=best_i, headers=best_hdr, mapping=best_map, rows=rows,
                           unknown_headers=unknown, blocked_headers=blocked)
