from __future__ import annotations

from dataclasses import replace

from .finance import clamp, underwrite_property
from .models import PropertyInput, Recommendation, ScenarioResult


def recommendation_from_score(score: float) -> Recommendation:
    if score >= 78:
        return Recommendation.BUY
    if score >= 68:
        return Recommendation.NEGOTIATE
    if score >= 55:
        return Recommendation.WATCHLIST
    return Recommendation.PASS


def score_metrics(metrics) -> float:  # type: ignore[no-untyped-def]
    cap_score = clamp((metrics.cap_rate - 0.045) / 0.055 * 100)
    coc_score = clamp((metrics.cash_on_cash_return - 0.02) / 0.12 * 100)
    dscr_score = 100 if metrics.dscr == float("inf") else clamp((metrics.dscr - 0.95) / 0.55 * 100)
    irr_score = 50 if metrics.irr is None else clamp((metrics.irr - 0.06) / 0.14 * 100)
    cash_flow_score = 88 if metrics.cash_flow_before_tax > 0 else max(0.0, 45 + metrics.cash_flow_before_tax / 1000)
    return round(cap_score * 0.22 + coc_score * 0.24 + dscr_score * 0.24 + irr_score * 0.18 + cash_flow_score * 0.12, 1)


def _result(name: str, prop: PropertyInput, assumptions: dict[str, float | str]) -> ScenarioResult:
    metrics = underwrite_property(prop)
    score = score_metrics(metrics)
    return ScenarioResult(
        name=name,
        score=score,
        recommendation=recommendation_from_score(score),
        cap_rate=metrics.cap_rate,
        cash_on_cash_return=metrics.cash_on_cash_return,
        dscr=metrics.dscr,
        irr=metrics.irr,
        cash_flow_before_tax=metrics.cash_flow_before_tax,
        noi=metrics.noi,
        assumptions=dict(assumptions),
    )


def build_scenarios(prop: PropertyInput) -> list[ScenarioResult]:
    """Run base, upside, downside, rate shock, and recession cases."""
    base = _result("Base", prop, {"case": "submitted assumptions"})
    upside_prop = replace(
        prop,
        monthly_rent=prop.monthly_rent * 1.05,
        vacancy_rate=max(0.0, prop.vacancy_rate - 0.015),
        expected_annual_rent_growth=prop.expected_annual_rent_growth + 0.01,
        expected_annual_appreciation=prop.expected_annual_appreciation + 0.01,
    )
    downside_prop = replace(
        prop,
        monthly_rent=prop.monthly_rent * 0.92,
        vacancy_rate=min(0.95, prop.vacancy_rate + 0.05),
        repairs_annual=prop.repairs_annual * 1.20,
        capex_annual=prop.capex_annual * 1.20,
        expected_annual_appreciation=max(0.0, prop.expected_annual_appreciation - 0.02),
    )
    rate_shock_prop = replace(
        prop,
        annual_interest_rate=min(0.95, prop.annual_interest_rate + 0.02),
    )
    recession_prop = replace(
        prop,
        monthly_rent=prop.monthly_rent * 0.90,
        vacancy_rate=min(0.95, prop.vacancy_rate + 0.08),
        annual_interest_rate=min(0.95, prop.annual_interest_rate + 0.015),
        expected_annual_rent_growth=0.0,
        expected_annual_expense_growth=prop.expected_annual_expense_growth + 0.015,
        expected_annual_appreciation=max(0.0, prop.expected_annual_appreciation - 0.03),
        selling_cost_rate=min(0.20, prop.selling_cost_rate + 0.01),
    )
    return [
        base,
        _result("Upside", upside_prop, {"rent": "+5%", "vacancy": "-1.5pp", "growth": "+1pp"}),
        _result("Downside", downside_prop, {"rent": "-8%", "vacancy": "+5pp", "repairs_capex": "+20%"}),
        _result("Rate shock", rate_shock_prop, {"interest_rate": "+2pp"}),
        _result("Recession", recession_prop, {"rent": "-10%", "vacancy": "+8pp", "rent_growth": "0%"}),
    ]
