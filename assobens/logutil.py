"""Logging com redação de segredos. Nunca grava senha, token JWT, cookie ou header sensível."""
from __future__ import annotations

import logging
import os
import re
from datetime import datetime
from pathlib import Path

from . import config

_SENSITIVE_PATTERNS = [
    re.compile(r"(?i)(password|senha|pwd)(\s*[=:]\s*)([^\s&,;\"']+)"),
    re.compile(r"(?i)(token|ssotoken|authorization|bearer|cookie|set-cookie)(\s*[=:]\s*)([^\s&,;\"']+)"),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}"),  # JWT
]


def redact(text: str) -> str:
    out = str(text)
    pwd = os.environ.get("ASSOBENS_PASSWORD")
    if pwd:
        out = out.replace(pwd, "***")
    for pat in _SENSITIVE_PATTERNS:
        out = pat.sub(lambda m: (m.group(1) + m.group(2) + "***") if m.lastindex else "***", out)
    return out


class RedactFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact(record.getMessage())
        record.args = ()
        return True


def get_logger(name: str = "assobens") -> logging.Logger:
    log = logging.getLogger(name)
    if getattr(log, "_assobens_ready", False):
        return log
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    sh.addFilter(RedactFilter())
    log.addHandler(sh)
    try:
        if "PYTEST_CURRENT_TEST" in os.environ:  # testes não escrevem no log real
            raise OSError
        config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(config.LOGS_DIR / f"sync-{datetime.now(config.TZ):%Y%m%d}.log", encoding="utf-8")
        fh.setFormatter(fmt)
        fh.addFilter(RedactFilter())
        log.addHandler(fh)
    except OSError:
        pass
    log._assobens_ready = True  # type: ignore[attr-defined]
    return log


def error_artifact_paths(step: str, when: datetime | None = None) -> tuple[Path, Path]:
    """Caminhos (png, json) do screenshot de erro: storage/logs/assobens/errors/<ts>_<etapa>."""
    ts = (when or datetime.now(config.TZ)).strftime("%Y%m%d_%H%M%S")
    base = config.ERRORS_DIR / f"{ts}_{re.sub(r'[^a-z0-9_-]+', '_', step.lower())}"
    return base.with_suffix(".png"), base.with_suffix(".json")
