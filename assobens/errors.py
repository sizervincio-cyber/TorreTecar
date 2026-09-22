"""Exceções da rotina ASSOBENS. Cada uma marca uma etapa distinta do fluxo."""


class AssobensError(Exception):
    step = "geral"


class CredentialsMissingError(AssobensError):
    step = "credenciais"


class AuthError(AssobensError):
    step = "login"


class SessionExpiredError(AuthError):
    step = "sessao"


class InterfaceChangedError(AssobensError):
    """Elemento esperado não encontrado: a interface do ASSOBENS mudou ou o seletor precisa de ajuste."""
    step = "interface"


class DownloadError(AssobensError):
    step = "download"


class EmptyFileError(AssobensError):
    step = "arquivo_vazio"


class SchemaError(AssobensError):
    step = "schema"


class ValidationError(AssobensError):
    step = "validacao"


class ImportError_(AssobensError):
    step = "importacao"
