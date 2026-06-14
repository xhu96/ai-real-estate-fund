from __future__ import annotations

from dataclasses import replace

from .investment_committee import run_property_committee
from .models import CommitteeDecision, PropertyInput


def default_sensitivity_cases(prop: PropertyInput) -> dict[str, PropertyInput]:
    """Return a standard set of underwriting sensitivity cases."""
    return {
        "Base case": prop,
        "Rent -10%": replace(prop, monthly_rent=prop.monthly_rent * 0.90),
        "Rent +10%": replace(prop, monthly_rent=prop.monthly_rent * 1.10),
        "Vacancy +5pp": replace(prop, vacancy_rate=min(prop.vacancy_rate + 0.05, 0.95)),
        "Rate +2pp": replace(prop, annual_interest_rate=min(prop.annual_interest_rate + 0.02, 0.95)),
        "Downside case": replace(
            prop,
            monthly_rent=prop.monthly_rent * 0.90,
            vacancy_rate=min(prop.vacancy_rate + 0.05, 0.95),
            annual_interest_rate=min(prop.annual_interest_rate + 0.02, 0.95),
            repairs_annual=prop.repairs_annual * 1.15,
            capex_annual=prop.capex_annual * 1.15,
            expected_annual_appreciation=max(0.0, prop.expected_annual_appreciation - 0.02),
        ),
    }


def run_sensitivity(prop: PropertyInput) -> list[tuple[str, CommitteeDecision]]:
    return [(name, run_property_committee(case_prop)) for name, case_prop in default_sensitivity_cases(prop).items()]


def render_sensitivity_markdown(prop: PropertyInput) -> str:
    from .report import pct

    lines = [f"# Sensitivity Analysis: {prop.name}", ""]
    lines.append("| Case | Decision | Score | Cap Rate | CoC | DSCR | IRR | Cash Flow |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for name, memo in run_sensitivity(prop):
        cash_flow = f"${memo.metrics.cash_flow_before_tax:,.0f}"
        irr = pct(memo.metrics.irr)
        lines.append(
            f"| {name} | {memo.recommendation.value} | {memo.overall_score:.1f} | "
            f"{pct(memo.metrics.cap_rate)} | {pct(memo.metrics.cash_on_cash_return)} | "
            f"{memo.metrics.dscr:.2f}x | {irr} | {cash_flow} |"
        )
    lines.append("")
    return "\n".join(lines)
