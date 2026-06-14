from __future__ import annotations

from ..models import DiligenceDataBundle, PropertyInput, UnderwritingMetrics
from .models import GateSeverity, InvestmentPolicy, PolicyLimit, PolicyResult
from .scoring import safe_divide

# A no-debt deal has metrics.dscr == inf. Policy gate values are rendered into
# gate messages (f"{value:.4g}") and JSON (where non-finite floats normalize to
# None), so we substitute a finite display value here. It clears every minimum
# DSCR gate while keeping the policy payload strict-JSON serializable.
NO_DEBT_DSCR_DISPLAY = 9.99


def metric_value(metric: str, prop: PropertyInput, metrics: UnderwritingMetrics, data: DiligenceDataBundle, committee_score: float) -> float:
    if metric == "dscr":
        return metrics.dscr if metrics.dscr != float("inf") else NO_DEBT_DSCR_DISPLAY
    if metric == "debt_yield":
        return safe_divide(metrics.noi, prop.loan_amount)
    if metric == "loan_to_cost":
        return metrics.loan_to_cost
    if metric == "break_even_occupancy":
        return metrics.break_even_occupancy
    if metric == "data_quality":
        return data.data_quality.completeness_score if data.data_quality else 45.0
    if metric == "liquidity_score":
        return data.market_snapshot.liquidity_score or prop.liquidity_score
    if metric == "rehab_to_cost":
        return safe_divide(prop.rehab_budget, metrics.total_project_cost)
    if metric == "cash_on_cash":
        return metrics.cash_on_cash_return
    if metric == "cap_rate":
        return metrics.cap_rate
    if metric == "crime_risk_score":
        return data.market_snapshot.crime_risk_score or prop.crime_risk_score
    if metric == "committee_score":
        return committee_score
    raise KeyError(f"Unsupported policy metric: {metric}")


def evaluate_limit(limit: PolicyLimit, value: float) -> PolicyResult:
    passed = True
    threshold_parts: list[str] = []
    if limit.min_value is not None:
        threshold_parts.append(f">= {limit.min_value:g}")
        passed = passed and value >= limit.min_value
    if limit.max_value is not None:
        threshold_parts.append(f"<= {limit.max_value:g}")
        passed = passed and value <= limit.max_value
    threshold = " and ".join(threshold_parts) or "informational"
    if passed:
        message = f"{limit.name} passed: {value:.4g} meets {threshold}."
        remediation = ""
    else:
        message = f"{limit.name} failed: {value:.4g} does not meet {threshold}."
        if limit.severity == GateSeverity.HARD_STOP:
            remediation = "Resolve this hard-stop item or document a formal IC override before closing."
        else:
            remediation = "Quantify sensitivity and assign a diligence owner before investment committee approval."
    return PolicyResult(limit=limit, value=value, passed=passed, message=message, remediation=remediation)


def evaluate_policy(
    policy: InvestmentPolicy,
    prop: PropertyInput,
    metrics: UnderwritingMetrics,
    data: DiligenceDataBundle,
    committee_score: float,
) -> list[PolicyResult]:
    results: list[PolicyResult] = []
    for limit in policy.limits():
        value = metric_value(limit.metric, prop, metrics, data, committee_score)
        results.append(evaluate_limit(limit, value))
    return results


def summarize_policy_results(results: list[PolicyResult]) -> dict[str, int]:
    return {
        "passed": sum(1 for result in results if result.passed),
        "warnings_failed": sum(1 for result in results if not result.passed and result.severity == GateSeverity.WARNING),
        "hard_stops_failed": sum(1 for result in results if not result.passed and result.severity == GateSeverity.HARD_STOP),
        "total": len(results),
    }

