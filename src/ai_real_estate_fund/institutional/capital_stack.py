from __future__ import annotations

from ..models import PropertyInput, UnderwritingMetrics
from .models import AllocationPlan, CapitalStackLayer
from .scoring import bounded, safe_divide


def build_capital_stack(prop: PropertyInput, metrics: UnderwritingMetrics) -> list[CapitalStackLayer]:
    senior_debt = max(0.0, prop.loan_amount)
    sponsor_equity = max(0.0, metrics.cash_invested)
    reserve = max(0.0, prop.rehab_budget * 0.10 + metrics.operating_expenses * 0.10)
    stack = []
    if senior_debt:
        stack.append(
            CapitalStackLayer(
                name="Senior mortgage debt",
                amount=senior_debt,
                priority=1,
                coupon_or_required_return=prop.annual_interest_rate,
                amortizing=True,
                maturity_years=prop.loan_term_years,
                notes="Derived from input loan assumptions.",
            )
        )
    if sponsor_equity:
        stack.append(
            CapitalStackLayer(
                name="Common equity",
                amount=sponsor_equity,
                priority=2,
                coupon_or_required_return=0.12,
                amortizing=False,
                maturity_years=prop.holding_period_years,
                notes="Residual equity after debt proceeds.",
            )
        )
    if reserve:
        stack.append(
            CapitalStackLayer(
                name="Operating and capex reserve",
                amount=reserve,
                priority=0,
                coupon_or_required_return=0.02,
                amortizing=False,
                maturity_years=1,
                notes="Suggested reserve held outside acquisition basis.",
            )
        )
    return stack


def total_capital(stack: list[CapitalStackLayer]) -> float:
    return sum(layer.amount for layer in stack)


def weighted_average_capital_cost(stack: list[CapitalStackLayer]) -> float:
    total = total_capital(stack)
    if total <= 0:
        return 0.0
    return sum(layer.cost_weight(total) * layer.coupon_or_required_return for layer in stack)


def equity_cushion_score(prop: PropertyInput, metrics: UnderwritingMetrics) -> float:
    project_cost = metrics.total_project_cost
    equity = max(0.0, project_cost - prop.loan_amount)
    equity_pct = safe_divide(equity, project_cost)
    return bounded((equity_pct - 0.12) / 0.30 * 100.0)


def build_allocation_plan(prop: PropertyInput, metrics: UnderwritingMetrics, score: float, risk_score: float, data_quality: float) -> AllocationPlan:
    if score < 52 or risk_score < 45:
        target = 0.0
    else:
        base = min(0.18, max(0.0, (score - 50.0) / 260.0))
        risk_modifier = min(1.0, max(0.30, risk_score / 85.0))
        quality_modifier = min(1.0, max(0.35, data_quality / 90.0))
        target = round(base * risk_modifier * quality_modifier, 4)
    maximum = round(min(0.25, target * 1.5 + 0.015), 4) if target else 0.0
    equity = metrics.cash_invested * target / max(target, 0.001) if target else 0.0
    reserve = max(0.0, metrics.operating_expenses * 0.10 + prop.rehab_budget * 0.10) if target else 0.0
    reasons = [
        f"Committee score {score:.1f}/100",
        f"Risk agent score {risk_score:.1f}/100",
        f"Data quality {data_quality:.1f}/100",
    ]
    constraints = []
    if metrics.dscr < 1.20:
        constraints.append("DSCR below institutional threshold")
    if metrics.loan_to_cost > 0.78:
        constraints.append("Leverage above target range")
    if data_quality < 70:
        constraints.append("Data room not complete enough for final IC approval")
    return AllocationPlan(
        target_allocation_pct=target,
        maximum_allocation_pct=maximum,
        equity_commitment=round(equity, 2),
        reserve_commitment=round(reserve, 2),
        reasons=reasons,
        constraints=constraints,
    )

