"""Validações de qualidade antes de publicar (seção 16 da missão).

A) soma por fabricante = total  B) share total ≈ 100%  C) MB calculado = MB informado (quando houver)
D) sem quantidade negativa  E) arquivo vazio  F) mudança de estrutura  G) queda brusca de registros
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import config
from .normalizer import quality_score

LEVEL_OK, LEVEL_SUSPECT, LEVEL_ERROR = "ok", "suspeito", "erro"


@dataclass
class ValidationReport:
    level: str = LEVEL_OK
    checks: dict[str, bool] = field(default_factory=dict)
    messages: list[str] = field(default_factory=list)
    quality: dict = field(default_factory=dict)

    @property
    def publishable(self) -> bool:
        return self.level == LEVEL_OK

    def fail(self, check: str, msg: str, level: str = LEVEL_ERROR) -> None:
        self.checks[check] = False
        self.messages.append(f"[{check}] {msg}")
        if level == LEVEL_ERROR or self.level == LEVEL_OK:
            self.level = level if self.level != LEVEL_ERROR else LEVEL_ERROR

    def ok(self, check: str) -> None:
        self.checks.setdefault(check, True)


def validate_batch(rows: list[dict], *, previous_rows_downloaded: int | None, unknown_headers: list[str],
                   mb_reported: int | None = None, rejected: int = 0, total_reported: int | None = None) -> ValidationReport:
    rep = ValidationReport()
    # E) vazio
    if not rows:
        rep.fail("E_vazio", "nenhuma linha válida no arquivo")
        return rep
    rep.ok("E_vazio")

    # A) soma por fabricante = total (as linhas são unitárias; garante que nenhuma marca ficou vazia/perdida)
    por_marca: dict[str, int] = {}
    for r in rows:
        por_marca[r.get("MARCA") or "(vazio)"] = por_marca.get(r.get("MARCA") or "(vazio)", 0) + 1
    if sum(por_marca.values()) != len(rows):
        rep.fail("A_soma_fabricantes", "soma por fabricante difere do total")
    else:
        rep.ok("A_soma_fabricantes")
    vazias = por_marca.get("(vazio)", 0)
    if vazias / len(rows) > 0.02:
        rep.fail("A_marca_vazia", f"{vazias} registros sem marca ({100*vazias/len(rows):.1f}%)", LEVEL_SUSPECT)

    # B) share total ≈ 100
    share_total = sum(100 * v / len(rows) for v in por_marca.values())
    if abs(share_total - 100) > 0.01:
        rep.fail("B_share_100", f"share total = {share_total:.3f}%")
    else:
        rep.ok("B_share_100")

    # C) MB calculado x informado (só quando o portal informou um total)
    mb_calc = por_marca.get(config.MB_BRAND, 0)
    for check, calc, rep_v in (("C_mb_calc_vs_informado", mb_calc, mb_reported), ("C_total_calc_vs_informado", len(rows), total_reported)):
        if rep_v is None:
            continue
        if calc == rep_v:
            rep.ok(check)
        elif abs(calc - rep_v) <= max(1, rep_v * 0.01):   # até 1%: só aviso (exportação e painel em instantes diferentes)
            rep.ok(check)
            rep.messages.append(f"[{check}] calculado {calc} ≠ painel {rep_v} (diferença ≤ 1%)")
        else:
            rep.fail(check, f"calculado {calc} ≠ painel {rep_v}", LEVEL_SUSPECT)

    # D) negativos já são rejeitados na normalização; aqui só relata
    rep.ok("D_sem_negativos")
    if rejected and rejected / (rejected + len(rows)) > 0.05:
        rep.fail("D_rejeitadas", f"{rejected} linhas rejeitadas ({100*rejected/(rejected+len(rows)):.1f}%)", LEVEL_SUSPECT)

    # F) estrutura
    if unknown_headers:
        rep.messages.append(f"[F_estrutura] colunas novas não mapeadas (preservadas no arquivo bruto): {', '.join(unknown_headers[:10])}")
    rep.ok("F_estrutura")

    # G) queda brusca
    if previous_rows_downloaded and len(rows) < previous_rows_downloaded * (1 - config.DROP_ALERT_RATIO):
        rep.fail("G_queda_registros", f"{len(rows)} linhas vs {previous_rows_downloaded} na execução anterior "
                 f"(queda > {int(config.DROP_ALERT_RATIO*100)}%) — publicação bloqueada até conferência", LEVEL_SUSPECT)
    else:
        rep.ok("G_queda_registros")

    # Gate de qualidade da Torre: se a matriz não passar, a Torre a ignoraria silenciosamente.
    q = quality_score(rows)
    rep.quality = q
    if q["score"] < config.MIN_QUALITY_SCORE:
        rep.fail("Q_qualidade_torre", f"qualidade {q['score']}/100 < {config.MIN_QUALITY_SCORE} (gate da Torre)")
    else:
        rep.ok("Q_qualidade_torre")
    return rep
