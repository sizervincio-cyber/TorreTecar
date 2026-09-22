"""AssobensSyncJob: orquestra DOWNLOAD → VALIDAÇÃO → STAGING → NORMALIZAÇÃO → CONSISTÊNCIA →
UPSERT → REFRESH KPIs → PUBLICAÇÃO, com 3 tentativas (30s, 2min) na etapa de navegador,
auditoria em sync_runs.json e status.json. Falha nunca apaga a última base válida.
"""
from __future__ import annotations

import time
import traceback
from datetime import datetime
from pathlib import Path

from . import config
from .errors import AssobensError, AuthError, CredentialsMissingError, ValidationError
from .importer import AssobensImporter
from .kpi import AssobensKpiService
from .logutil import get_logger, redact
from .normalizer import AssobensNormalizer
from .parser import AssobensSpreadsheetParser
from .price_analysis import AssobensPriceAnalysisService, PriceHistory
from .runlog import RunLog, STATUS_FAILED, STATUS_PARTIAL, STATUS_SUCCESS, SyncRun, write_json_atomic
from .validator import LEVEL_ERROR, LEVEL_SUSPECT, validate_batch


class AssobensSyncJob:
    def __init__(self, *, trigger: str, executed_by: str, skip_precos: bool = False, headless: bool = True,
                 arquivo: str | Path | None = None, credentials: config.Credentials | None = None,
                 runlog: RunLog | None = None, importer: AssobensImporter | None = None,
                 browser_stage=None, sleep=time.sleep, kpis_path: Path | None = None, top10_path: Path | None = None,
                 precos_top10_path: Path | None = None, price_history: PriceHistory | None = None,
                 equivalencias_path: Path | None = None):
        self.trigger, self.executed_by = trigger, executed_by
        self.skip_precos, self.headless, self.arquivo = skip_precos, headless, arquivo
        self.creds = credentials or config.get_credentials()
        self.runlog = runlog or RunLog()
        self.importer = importer or AssobensImporter()
        self.parser = AssobensSpreadsheetParser()
        self.normalizer = AssobensNormalizer()
        self.kpi = AssobensKpiService()
        self.prices = AssobensPriceAnalysisService(history=price_history, equivalencias_path=equivalencias_path)
        self.kpis_path = kpis_path or config.KPIS_PATH
        self.top10_path = top10_path or config.TOP10_PATH
        self.precos_top10_path = precos_top10_path or config.PRECOS_TOP10_PATH
        self._browser_stage = browser_stage or self.browser_stage  # injetável nos testes
        self._sleep = sleep
        self.log = get_logger()

    # ------------------------------------------------------------- execução
    def run(self) -> SyncRun:
        config.ensure_dirs()
        run = self.runlog.start(self.trigger, self.executed_by)
        self.log.info("=== sync ASSOBENS iniciado (run %s, trigger %s, por %s)", run.id, run.trigger_type, run.executed_by)
        status = STATUS_SUCCESS
        try:
            # 1) DOWNLOAD (ou arquivo já baixado)
            price_captures: list[dict] | None = None
            if self.arquivo:
                xlsx = Path(self.arquivo)
                run.step(f"arquivo informado manualmente: {xlsx.name}")
                run.source = "arquivo_local"
            else:
                xlsx, price_captures = self._with_retries(run)
            # 2) VALIDAÇÃO DO ARQUIVO + STAGING (memória)
            parsed = self.parser.parse(xlsx)
            run.file_name, run.file_hash, run.rows_downloaded = parsed.file_name, parsed.file_hash, len(parsed.rows)
            run.step(f"arquivo lido: aba '{parsed.sheet}', {len(parsed.rows)} linhas, {len(parsed.mapping)} colunas mapeadas")
            if parsed.unknown_headers:
                run.warnings.append("colunas novas não mapeadas: " + ", ".join(parsed.unknown_headers[:12]))
            if parsed.blocked_headers:
                run.step(f"{len(parsed.blocked_headers)} colunas de dado pessoal ignoradas (ficam só no arquivo bruto local)")
            # 3) NORMALIZAÇÃO
            batch = self.normalizer.normalize(parsed.rows)
            run.rows_valid, run.rows_rejected = len(batch.rows), len(batch.rejected)
            run.step(f"normalização: {batch.counts}")
            # 4) CONSISTÊNCIA
            prev = self.runlog.last_success()
            report = validate_batch(batch.rows, previous_rows_downloaded=(prev or {}).get("rows_downloaded"),
                                    unknown_headers=parsed.unknown_headers, rejected=len(batch.rejected))
            run.warnings.extend(report.messages)
            run.step(f"validação: nível {report.level}, qualidade {report.quality.get('score')}/100")
            if report.level == LEVEL_ERROR:
                raise ValidationError("; ".join(report.messages))
            # 5) UPSERT + PUBLICAÇÃO ATÔMICA
            if report.level == LEVEL_SUSPECT:
                status = STATUS_PARTIAL
                run.step("publicação BLOQUEADA (dados suspeitos); base anterior mantida")
                headers, rows_all = self.importer.load_matrix()
            elif prev and prev.get("file_hash") == parsed.file_hash and prev.get("status") == STATUS_SUCCESS:
                run.step("mesmo arquivo da última execução (hash igual): nada a importar")
                headers, rows_all = self.importer.load_matrix()
            else:
                headers, existing = self.importer.load_matrix()
                res = self.importer.upsert(batch.rows, headers, existing)
                run.rows_imported, run.rows_updated = res.inserted, res.updated
                run.step(f"upsert por CHASSI: {res.inserted} inseridos, {res.updated} atualizados, {res.unchanged} iguais (matriz {res.total})")
                if res.inserted or res.updated:
                    self.importer.publish(res.headers, res.rows, run.id)
                    run.step("matriz publicada (troca atômica; backup da anterior em storage)")
                headers, rows_all = res.headers, res.rows
            # 6) REFRESH KPIs + Top 10 (sempre a partir da matriz vigente)
            kpis = self.kpi.compute(rows_all)
            write_json_atomic(self.kpis_path, kpis)
            top10 = self.prices.top10_por_segmento(rows_all)
            write_json_atomic(self.top10_path, top10)
            run.step(f"KPIs: mercado {kpis['total_mercado']}, MB {kpis['total_mercedes_benz']}, share {kpis['market_share_mb']}% "
                     f"(12m: {kpis['ultimos_12_meses']['market_share_mb']}%); Top 10 em {len(top10['segmentos'])} segmentos")
            # 7) PREÇOS
            if not self.skip_precos:
                if price_captures:
                    run.prices_updated = self.prices.history.upsert(price_captures)
                    run.step(f"histórico de preços: {run.prices_updated} linhas novas/alteradas de {len(price_captures)} capturadas")
                elif price_captures is None and not self.arquivo:
                    status = STATUS_PARTIAL
                write_json_atomic(self.precos_top10_path, self.prices.analyze(top10))
            self.runlog.finish(run, status)
        except CredentialsMissingError as e:
            self._fail(run, e)
        except AssobensError as e:
            self._fail(run, e)
        except Exception as e:  # inesperado: registra e preserva a base
            self.log.error("erro inesperado: %s\n%s", e, redact(traceback.format_exc()))
            self._fail(run, e)
        self.log.info("=== sync finalizado: %s em %ss", run.status, run.duration_seconds)
        return run

    def _fail(self, run: SyncRun, e: Exception) -> None:
        msg = f"[{getattr(e, 'step', 'erro')}] {redact(str(e))}"[:600]
        self.log.error("FALHOU: %s", msg)
        run.step("falha; base anterior mantida")
        self.runlog.finish(run, STATUS_FAILED, msg)

    # ------------------------------------------------------------- retries
    def _with_retries(self, run: SyncRun):
        last: Exception | None = None
        for attempt in range(1, config.MAX_ATTEMPTS + 1):
            try:
                run.step(f"tentativa {attempt}/{config.MAX_ATTEMPTS}")
                return self._browser_stage(run, attempt)
            except CredentialsMissingError:
                raise
            except AuthError as e:
                # credencial recusada não melhora com retry; sessão expirada sim
                if "expirada" not in str(e).lower() and "ausente" not in str(e).lower():
                    raise
                last = e
            except Exception as e:
                last = e
            self.log.warning("tentativa %d falhou: %s", attempt, redact(str(last)))
            run.step(f"tentativa {attempt} falhou: {redact(str(last))[:200]}")
            if attempt < config.MAX_ATTEMPTS:
                wait = config.RETRY_WAITS_SECONDS[min(attempt - 1, len(config.RETRY_WAITS_SECONDS) - 1)]
                self.log.info("aguardando %ds antes da próxima tentativa", wait)
                self._sleep(wait)
        raise last  # type: ignore[misc]

    # ------------------------------------------------------------- etapa de navegador
    def browser_stage(self, run: SyncRun, attempt: int):
        from .auth import AssobensAuthenticationService
        from .browser import AssobensBrowserService, load_selectors
        from .emplacamentos_downloader import AssobensEmplacamentosDownloader
        from .price_downloader import AssobensPriceDownloader

        sel = load_selectors()
        now = datetime.now(config.TZ)
        day_dir = config.STORAGE_DIR / f"{now:%Y}" / f"{now:%m}" / f"{now:%d}"
        with AssobensBrowserService(headless=self.headless) as b:
            page = b.page
            auth = AssobensAuthenticationService(self.creds, sel)
            try:
                auth.login_portal(page)
                run.step("login concluído no portal")
                auth.open_bi(page)
                run.step("BI autenticado")
            except AssobensError:
                b.screenshot_error(page, "login")
                raise
            dl = AssobensEmplacamentosDownloader(b, auth, sel)
            try:
                xlsx = dl.download(page, day_dir, now.strftime("%H%M"))
            except AssobensError:
                b.screenshot_error(page, "download_emplacamentos")
                raise
            run.step(f"download concluído: {xlsx.name}")
            prices = None
            if not self.skip_precos:
                try:
                    prices = AssobensPriceDownloader(b, auth, sel, dl).capture(page, day_dir)
                except Exception as e:  # preços não derrubam os emplacamentos: status parcial
                    b.screenshot_error(page, "precos")
                    run.warnings.append(f"comparativo de preços não capturado: {redact(str(e))[:200]}")
                    self.log.warning("preços falharam: %s", redact(str(e)))
        return xlsx, prices
