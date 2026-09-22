"""Agenda 08/12/17 e fuso America/Sao_Paulo."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
import yaml

from assobens import config
from assobens.runlog import next_run

WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "assobens-sync.yml"


@pytest.mark.skipif(not WORKFLOW.exists(), reason="workflow do GitHub Actions ainda não criado")
def test_workflow_agenda_08_12_17_sao_paulo():
    wf = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    on = wf.get("on", wf.get(True))
    cron = on["schedule"][0]["cron"]
    assert cron == config.SCHEDULE_CRON_UTC
    minute, hour, *_ = cron.split()
    sp = ZoneInfo("America/Sao_Paulo")
    horas_sp = sorted(datetime(2026, 9, 22, int(h), 0, tzinfo=ZoneInfo("UTC")).astimezone(sp).hour for h in hour.split(","))
    assert minute == "0" and horas_sp == list(config.SCHEDULE_HOURS)
    assert "workflow_dispatch" in on
    assert wf["env"]["TZ"] == "America/Sao_Paulo"


def test_cron_utc_equivale_a_08_12_17_local():
    sp = ZoneInfo("America/Sao_Paulo")
    horas_utc = [int(h) for h in config.SCHEDULE_CRON_UTC.split()[1].split(",")]
    for h_utc, h_sp in zip(horas_utc, config.SCHEDULE_HOURS):
        assert datetime(2026, 9, 22, h_utc, 0, tzinfo=ZoneInfo("UTC")).astimezone(sp).hour == h_sp
    assert config.SCHEDULE_CRON_LOCAL == "0 8,12,17 * * *"


def test_proxima_execucao_no_fuso_de_sao_paulo():
    sp = ZoneInfo("America/Sao_Paulo")
    assert next_run(datetime(2026, 9, 22, 9, 30, tzinfo=sp)).hour == 12
    assert next_run(datetime(2026, 9, 22, 17, 0, tzinfo=sp)) == datetime(2026, 9, 23, 8, 0, tzinfo=sp)
    assert next_run(datetime(2026, 9, 22, 14, 30, tzinfo=ZoneInfo("UTC"))).hour == 12   # 11:30 SP -> 12:00
    assert next_run(datetime(2026, 9, 22, 22, 0, tzinfo=ZoneInfo("UTC"))).hour == 8     # 19:00 SP -> 08:00 do dia seguinte
