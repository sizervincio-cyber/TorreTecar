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
from .enriquecimento_downloader import janela_enriquecimento
from .errors import AssobensError, AuthError, CredentialsMissingError, InterfaceChangedError, ValidationError

# Campos que o relatório de enriquecimento pode completar/atualizar na matriz (nunca insere chassis).
OWNER_FIELDS = ["CPFCNPJPROPRIETARIO", "TIPOCNPJPROPRIETARIO", "NOMEPROPRIETARIO", "TRAÇÃO", "TIPO TERRENO", "ANOMODELO", "ANOFABRICACAO"]
from .importer import AssobensImporter
from .kpi import AssobensKpiService
from .logutil import get_logger, redact
from .normalizer import AssobensNormalizer, quality_score
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
            portal: dict = {}
            enr_path = None
            headers0, existing0 = self.importer.load_matrix()   # uma leitura só; reutilizada no upsert
            self.janela_enr = janela_enriquecimento(existing0, datetime.now(config.TZ).date().isoformat())
            self.faltam_proprietario = sum(1 for r in existing0 if not str(r.get("NOMEPROPRIETARIO", "")).strip())
            if self.arquivo:
                xlsx = Path(self.arquivo)
                run.step(f"arquivo informado manualmente: {xlsx.name}")
                run.source = "arquivo_local"
            else:
                stage = self._with_retries(run)
                xlsx, price_captures = stage[0], stage[1]
                portal = stage[2] if len(stage) > 2 and stage[2] else {}
                enr_path = stage[3] if len(stage) > 3 else None
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
            prev = self.runlog.last_success(source=run.source)  # queda de volume só é comparável com a mesma fonte
            report = validate_batch(batch.rows, previous_rows_downloaded=(prev or {}).get("rows_downloaded"),
                                    unknown_headers=parsed.unknown_headers, rejected=len(batch.rejected),
                                    mb_reported=portal.get("total_mb"), total_reported=portal.get("total_mercado"))
            run.warnings.extend(report.messages)
            run.step(f"validação: nível {report.level}, qualidade {report.quality.get('score')}/100")
            if report.level == LEVEL_ERROR:
                raise ValidationError("; ".join(report.messages))
            # 5) UPSERT + PUBLICAÇÃO ATÔMICA
            mudou = False
            if report.level == LEVEL_SUSPECT:
                status = STATUS_PARTIAL
                run.step("publicação BLOQUEADA (dados suspeitos); base anterior mantida")
                headers, rows_all = headers0, existing0
            elif prev and prev.get("file_hash") == parsed.file_hash and prev.get("status") == STATUS_SUCCESS:
                run.step("mesmo arquivo da última execução (hash igual): nada a importar")
                headers, rows_all = headers0, existing0
            else:
                res = self.importer.upsert(batch.rows, headers0, existing0)
                run.rows_imported, run.rows_updated = res.inserted, res.updated
                run.step(f"upsert por CHASSI: {res.inserted} inseridos, {res.updated} atualizados, {res.unchanged} iguais (matriz {res.total})")
                headers, rows_all = res.headers, res.rows
                mudou = bool(res.inserted or res.updated)
            # 5b) ENRIQUECIMENTO ("Baixar Dados"): fonte principal do ano corrente — traz proprietário, tipo de pessoa,
            # nome, ano modelo e terreno. Aplicado por último para prevalecer sobre o export do Power BI (que só
            # acrescenta colunas próprias, ex.: combustível). Só entram linhas do segmento caminhões.
            if enr_path and report.level != LEVEL_SUSPECT:
                try:
                    pe = self.parser.parse(enr_path)
                    be = self.normalizer.normalize(pe.rows)
                    cam = [r for r in be.rows if r.get("SEGMENTO") == "1.0-CAMINHOES"]
                    if not cam:
                        raise ValidationError(f"relatório de enriquecimento sem linhas de caminhões (segmentos: "
                                              f"{sorted({r.get('SEGMENTO') for r in be.rows})[:4]}) — filtro de segmento errado")
                    r2 = self.importer.upsert(cam, headers, rows_all, update_only=config.ENRIQUECIMENTO_SOMENTE_ATUALIZA,
                                              only_fields=OWNER_FIELDS if config.ENRIQUECIMENTO_SOMENTE_ATUALIZA else None)
                    run.rows_enriched = r2.updated
                    run.rows_imported += r2.inserted
                    run.rows_updated += r2.updated
                    headers, rows_all = r2.headers, r2.rows
                    mudou = mudou or r2.updated > 0 or r2.inserted > 0
                    run.step(f"enriquecimento: {len(cam)} chassis de caminhões no relatório ({len(be.rows) - len(cam)} de outros segmentos ignorados) · "
                             f"{r2.inserted} inseridos · {r2.updated} atualizados/com proprietário · {r2.unchanged} iguais · {r2.ignored} ignorados")
                except Exception as e:
                    status = STATUS_PARTIAL
                    run.warnings.append(f"enriquecimento não aplicado: {redact(str(e))[:200]}")
            if mudou:
                qm = quality_score(rows_all)  # gate da Torre vale para a MATRIZ publicada, não para o lote isolado
                if qm["score"] < config.MIN_QUALITY_SCORE:
                    raise ValidationError(f"matriz resultante com qualidade {qm['score']}/100 < {config.MIN_QUALITY_SCORE} (gate da Torre); publicação recusada")
                run.step(f"qualidade da matriz resultante: {qm['score']}/100")
                self.importer.publish(headers, rows_all, run.id)
                run.step("matriz publicada (troca atômica; backup da anterior em storage)")
            # 6) REFRESH KPIs + Top 10 (sempre a partir da matriz vigente)
            kpis = self.kpi.compute(rows_all)
            write_json_atomic(self.kpis_path, kpis)
            top10 = self.prices.top10_por_segmento(rows_all)
            write_json_atomic(self.top10_path, top10)
            run.step(f"KPIs: mercado {kpis['total_mercado']}, MB {kpis['total_mercedes_benz']}, share {kpis['market_share_mb']}% "
                     f"(12m: {kpis['ultimos_12_meses']['market_share_mb']}%); Top 10 em {len(top10['segmentos'])} segmentos")
            if portal:
                conf = self.kpi.conferencia(rows_all, portal)
                write_json_atomic(self.kpis_path.parent / "conferencia.json", conf)
                run.step("conferência ASSOBENS × Torre: " + "; ".join(
                    f"{c['indicador']} {c['assobens']}/{c['torre']} (Δ{c['diferenca']})" for c in conf["indicadores"][:3]))
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
            except (CredentialsMissingError, InterfaceChangedError):
                raise  # não melhora com retry: credencial ausente ou elemento inexistente
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
        from .enriquecimento_downloader import AssobensEnriquecimentoDownloader
        from .price_downloader import AssobensPriceDownloader

        sel = load_selectors()
        now = datetime.now(config.TZ)
        day_dir = config.STORAGE_DIR / f"{now:%Y}" / f"{now:%m}" / f"{now:%d}"
        with AssobensBrowserService(headless=self.headless) as b:
            page = b.page
            auth = AssobensAuthenticationService(self.creds, sel, b)
            try:
                auth.login_portal(page)
                run.step("login concluído no portal")
                auth.open_bi(page)
                page = auth.bi_page or page  # o SSO pode abrir o BI numa nova aba
                b.page = page
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
            enr = None
            if self.faltam_proprietario:
                ini, fim = self.janela_enr
                run.step(f"enriquecimento: {self.faltam_proprietario} chassis sem proprietário · janela {ini} → {fim}")
                try:
                    enr = AssobensEnriquecimentoDownloader(b, auth, sel, dl).download(page, day_dir, now.strftime("%H%M"), ini, fim)
                    run.step(f"download de enriquecimento concluído: {enr.name}")
                except Exception as e:  # também não derruba os emplacamentos
                    b.screenshot_error(page, "enriquecimento")
                    run.warnings.append(f"enriquecimento não baixado: {redact(str(e))[:200]}")
                    self.log.warning("enriquecimento falhou: %s", redact(str(e)))
            else:
                run.step("enriquecimento: nenhum chassi sem proprietário na matriz")
        return xlsx, prices, dl.last_kpis, enr
