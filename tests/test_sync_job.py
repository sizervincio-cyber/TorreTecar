"""Job completo com etapa de navegador simulada: execução manual, idempotência, falhas, retries, bloqueio por queda."""
import json

import pytest

from assobens import config
from assobens.errors import AuthError, DownloadError
from assobens.importer import AssobensImporter
from assobens.price_analysis import PriceHistory
from assobens.runlog import RunLog
from assobens.sync_job import AssobensSyncJob
from conftest import SAMPLE, write_xlsx


def _job(paths, **kw):
    kw.setdefault("credentials", config.Credentials("u", "p"))
    kw.setdefault("sleep", lambda s: None)
    return AssobensSyncJob(trigger=kw.pop("trigger", "manual"), executed_by=kw.pop("executed_by", "teste"),
                           runlog=RunLog(paths.SYNC_RUNS_PATH, paths.STATUS_PATH),
                           importer=AssobensImporter(paths.MATRIZ_PATH, paths.BACKUP_DIR),
                           kpis_path=paths.KPIS_PATH, top10_path=paths.TOP10_PATH, precos_top10_path=paths.PRECOS_TOP10_PATH,
                           price_history=PriceHistory(paths.PRECOS_HIST_PATH), equivalencias_path=paths.EQUIVALENCIAS_PATH, **kw)


def test_execucao_manual_completa(paths, sample_xlsx):
    precos = [{"source": "assobens_precos_comparativo", "manufacturer": "VW", "model": "VW/29.530", "segment": "EXTRAPESADOS",
               "price": 760000.0, "reference_date": "2026-01-20", "captured_at": "2026-01-20T08:00:00"}]
    job = _job(paths, trigger="manual", executed_by="matheus", browser_stage=lambda run, attempt: (sample_xlsx, precos))
    run = job.run()
    assert run.status == "success" and run.trigger_type == "manual" and run.executed_by == "matheus"
    assert (run.rows_downloaded, run.rows_valid, run.rows_imported, run.rows_updated, run.rows_rejected, run.prices_updated) == (5, 5, 5, 0, 0, 1)
    assert paths.MATRIZ_PATH.exists() and paths.KPIS_PATH.exists() and paths.TOP10_PATH.exists() and paths.PRECOS_TOP10_PATH.exists()
    st = json.loads(paths.STATUS_PATH.read_text(encoding="utf-8"))
    assert st["status"] == "success" and st["status_label"] == "Atualizado" and st["registros_processados"] == 5
    assert st["timezone"] == "America/Sao_Paulo" and st["proxima_execucao"]
    runs = json.loads(paths.SYNC_RUNS_PATH.read_text(encoding="utf-8"))
    assert runs[-1]["file_hash"] and runs[-1]["trigger_type"] == "manual" and runs[-1]["duration_seconds"] is not None
    # segunda execução com o mesmo arquivo: idempotente
    run2 = _job(paths, browser_stage=lambda run, attempt: (sample_xlsx, precos)).run()
    assert run2.status == "success" and (run2.rows_imported, run2.rows_updated) == (0, 0)


def test_login_recusado_falha_sem_apagar_base(paths, sample_xlsx):
    ok = _job(paths, browser_stage=lambda run, attempt: (sample_xlsx, [])).run()
    assert ok.status == "success"
    antes = paths.MATRIZ_PATH.read_bytes()
    tentativas = []

    def stage(run, attempt):
        tentativas.append(attempt)
        raise AuthError("portal recusou o login")
    run = _job(paths, browser_stage=stage).run()
    assert run.status == "failed" and "recusou" in run.error_message
    assert tentativas == [1]                                    # login recusado não faz retry
    assert paths.MATRIZ_PATH.read_bytes() == antes             # última base válida preservada
    st = json.loads(paths.STATUS_PATH.read_text(encoding="utf-8"))
    assert st["status"] == "failed" and "última sincronização válida" in st["mensagem"]
    assert st["base_valida"]["registros_processados"] == 5


def test_sem_credenciais_configuradas(paths):
    run = _job(paths, credentials=config.Credentials("", ""), browser_stage=None).run()
    assert run.status == "failed" and "[credenciais]" in run.error_message


def test_tres_tentativas_com_backoff(paths, sample_xlsx):
    esperas, chamadas = [], []

    def stage(run, attempt):
        chamadas.append(attempt)
        if attempt < 3:
            raise DownloadError("clique no Excel não gerou download em 120s")
        return sample_xlsx, []
    run = _job(paths, browser_stage=stage, sleep=lambda s: esperas.append(s)).run()
    assert run.status == "success" and chamadas == [1, 2, 3] and esperas == [30, 120]
    assert sum("falhou" in s for s in run.steps) == 2

    def sempre_falha(run, attempt):
        raise DownloadError("timeout")
    run2 = _job(paths, browser_stage=sempre_falha, sleep=lambda s: None).run()
    assert run2.status == "failed" and "[download]" in run2.error_message


def test_queda_brusca_bloqueia_publicacao(paths, sample_xlsx, tmp_path):
    ok = _job(paths, browser_stage=lambda run, attempt: (sample_xlsx, [])).run()
    assert ok.status == "success"
    antes = paths.MATRIZ_PATH.read_bytes()
    pequeno = write_xlsx(tmp_path / "pequeno.xlsx", rows=SAMPLE[:1])
    run = _job(paths, browser_stage=lambda run, attempt: (pequeno, [])).run()
    assert run.status == "partial" and any("queda" in w for w in run.warnings)
    assert paths.MATRIZ_PATH.read_bytes() == antes


def test_importar_arquivo_local_sem_navegador(paths, sample_xlsx):
    run = _job(paths, arquivo=sample_xlsx, skip_precos=True, browser_stage=lambda *a: pytest.fail("não deve abrir navegador")).run()
    assert run.status == "success" and run.source == "arquivo_local" and run.rows_imported == 5


def test_cli_execucao_manual(paths, sample_xlsx, capsys):
    from assobens.__main__ import main
    rc = main(["importar", str(sample_xlsx), "--trigger", "manual", "--executed-by", "admin"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0 and out["trigger_type"] == "manual" and out["executed_by"] == "admin" and out["status"] == "success"
