"""Auditoria das execuções (assobens_sync_runs) e status resumido para a Torre.

Persistido em JSON versionado, que é o mecanismo de dados deste projeto.
"""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from . import config

STATUS_RUNNING, STATUS_SUCCESS, STATUS_PARTIAL, STATUS_FAILED = "running", "success", "partial", "failed"
TRIGGER_SCHEDULER, TRIGGER_MANUAL = "scheduler", "manual"


def now_local() -> datetime:
    return datetime.now(config.TZ)


def next_run(after: datetime | None = None) -> datetime:
    """Próxima execução agendada (08/12/17 America/Sao_Paulo) depois de `after`."""
    t = (after or now_local()).astimezone(config.TZ)
    for h in config.SCHEDULE_HOURS:
        cand = t.replace(hour=h, minute=0, second=0, microsecond=0)
        if cand > t:
            return cand
    nxt = (t + timedelta(days=1)).replace(hour=config.SCHEDULE_HOURS[0], minute=0, second=0, microsecond=0)
    return nxt


def write_json_atomic(path: Path, data: Any) -> None:
    """Escreve JSON em arquivo temporário no mesmo diretório e troca com os.replace (atômico)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1, default=str)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


@dataclass
class SyncRun:
    id: str
    started_at: str
    trigger_type: str
    executed_by: str
    source: str = "assobens"
    finished_at: str | None = None
    status: str = STATUS_RUNNING
    file_name: str | None = None
    file_hash: str | None = None
    rows_downloaded: int = 0
    rows_valid: int = 0
    rows_imported: int = 0
    rows_updated: int = 0
    rows_rejected: int = 0
    prices_updated: int = 0
    error_message: str | None = None
    duration_seconds: float | None = None
    steps: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def step(self, msg: str) -> None:
        self.steps.append(f"{now_local():%H:%M:%S} {msg}")

    def to_dict(self) -> dict:
        return asdict(self)


class RunLog:
    def __init__(self, runs_path: Path | None = None, status_path: Path | None = None):
        self.runs_path = runs_path or config.SYNC_RUNS_PATH
        self.status_path = status_path or config.STATUS_PATH

    def runs(self) -> list[dict]:
        return read_json(self.runs_path, [])

    def last_success(self) -> dict | None:
        for r in reversed(self.runs()):
            if r.get("status") in (STATUS_SUCCESS, STATUS_PARTIAL) and r.get("rows_downloaded"):
                return r
        return None

    def start(self, trigger_type: str, executed_by: str) -> SyncRun:
        t = now_local()
        base = t.strftime("%Y%m%d-%H%M%S")
        ids = {r.get("id") for r in self.runs()}
        rid, n = base, 1
        while rid in ids:  # duas execuções no mesmo segundo nunca se sobrescrevem
            n += 1
            rid = f"{base}-{n}"
        run = SyncRun(id=rid, started_at=t.isoformat(timespec="seconds"),
                      trigger_type=trigger_type, executed_by=executed_by)
        self.save(run)
        return run

    def finish(self, run: SyncRun, status: str, error_message: str | None = None) -> SyncRun:
        t = now_local()
        run.status = status
        run.error_message = error_message
        run.finished_at = t.isoformat(timespec="seconds")
        run.duration_seconds = round((t - datetime.fromisoformat(run.started_at)).total_seconds(), 1)
        self.save(run)
        self.write_status(run)
        return run

    def save(self, run: SyncRun) -> None:
        runs = [r for r in self.runs() if r.get("id") != run.id]
        runs.append(run.to_dict())
        write_json_atomic(self.runs_path, runs[-config.SYNC_RUNS_KEEP:])

    def write_status(self, run: SyncRun) -> dict:
        last_ok = run.to_dict() if run.status in (STATUS_SUCCESS, STATUS_PARTIAL) else self.last_success()
        prev = read_json(self.status_path, {})
        base_ok = prev.get("base_valida")
        if last_ok:
            base_ok = {"atualizado_em": last_ok.get("finished_at"), "registros_processados": last_ok.get("rows_downloaded"),
                       "importados": last_ok.get("rows_imported"), "atualizados": last_ok.get("rows_updated"),
                       "precos_atualizados": last_ok.get("prices_updated"), "run_id": last_ok.get("id")}
        status = {
            "fonte": "ASSOBENS",
            "ultima_execucao": run.finished_at or run.started_at,
            "status": run.status,
            "status_label": {STATUS_SUCCESS: "Atualizado", STATUS_PARTIAL: "Atualizado parcialmente",
                             STATUS_FAILED: "Falhou", STATUS_RUNNING: "Executando"}.get(run.status, run.status),
            "mensagem": ("Última atualização automática falhou. Os dados exibidos são da última sincronização válida."
                         if run.status == STATUS_FAILED else (run.error_message or "")),
            "erro": run.error_message,
            "proxima_execucao": next_run().isoformat(timespec="minutes"),
            "agenda_local": config.SCHEDULE_CRON_LOCAL,
            "timezone": "America/Sao_Paulo",
            "trigger_type": run.trigger_type,
            "executed_by": run.executed_by,
            "registros_processados": run.rows_downloaded,
            "registros_importados": run.rows_imported,
            "registros_atualizados": run.rows_updated,
            "registros_rejeitados": run.rows_rejected,
            "precos_atualizados": run.prices_updated,
            "base_valida": base_ok,
            "avisos": run.warnings,
        }
        write_json_atomic(self.status_path, status)
        return status
