from __future__ import annotations

"""Detailed underwriting model for insurance deductibles.

The model intentionally stays dependency-free so the repository can run
in educational or offline environments. Production deployments would
swap these deterministic heuristics for source-verified statements,
third-party market data, and reviewed Excel/Python model outputs.
"""

from dataclasses import dataclass, asdict
from typing import Any

from ...finance import clamp
from ...models import PropertyInput, UnderwritingMetrics


@dataclass(slots=True)
class InsuranceDeductibleModelResult:
    subject: str
    lens: str
    base_value: float
    stressed_value: float
    score: float
    confidence: float
    notes: list[str]

    def variance(self) -> float:
        return self.stressed_value - self.base_value

    def variance_pct(self) -> float:
        return self.variance() / self.base_value if self.base_value else 0.0

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["variance"] = self.variance()
        payload["variance_pct"] = self.variance_pct()
        return payload


class InsuranceDeductibleModel:
    subject = 'insurance deductibles'
    lens = 'loss retention'

    def __init__(self, stress_factor: float = 1.10, confidence: float = 0.70) -> None:
        self.stress_factor = stress_factor
        self.confidence = confidence

    def base_value(self, prop: PropertyInput, metrics: UnderwritingMetrics) -> float:
        annual_income = metrics.gross_potential_income
        expense_ratio = metrics.operating_expenses / metrics.effective_gross_income if metrics.effective_gross_income else 0.0
        rehab_ratio = prop.rehab_budget / metrics.total_project_cost if metrics.total_project_cost else 0.0
        age_factor = max(0.0, ((2026 - prop.year_built) if prop.year_built else 45) / 100.0)
        return max(0.0, annual_income * 0.015 + metrics.operating_expenses * 0.020 + prop.rehab_budget * 0.025 + expense_ratio * 500.0 + age_factor * 750.0 + rehab_ratio * 1250.0)

    def stressed_value(self, prop: PropertyInput, metrics: UnderwritingMetrics) -> float:
        return self.base_value(prop, metrics) * self.stress_factor

    def score(self, prop: PropertyInput, metrics: UnderwritingMetrics) -> float:
        base = self.base_value(prop, metrics)
        stressed = self.stressed_value(prop, metrics)
        burden = stressed / max(metrics.noi, 1.0)
        score = 100.0 - burden * 45.0
        if metrics.dscr < 1.20:
            score -= 8.0
        if metrics.cash_on_cash_return < 0.04:
            score -= 5.0
        return round(clamp(score), 1)

    def explain(self, prop: PropertyInput, metrics: UnderwritingMetrics) -> list[str]:
        notes = [
            f"Subject: {self.subject}",
            f"Analytical lens: {self.lens}",
            f"Stress factor: {self.stress_factor:.2f}x",
            f"DSCR context: {metrics.dscr:.2f}x",
            f"NOI context: ${metrics.noi:,.0f}",
        ]
        if prop.rehab_budget > 0:
            notes.append(f"Rehab budget included in burden assessment: ${prop.rehab_budget:,.0f}")
        if metrics.cash_on_cash_return < 0:
            notes.append("Negative cash-on-cash return increases sensitivity to this workstream.")
        return notes

    def evaluate(self, prop: PropertyInput, metrics: UnderwritingMetrics) -> InsuranceDeductibleModelResult:
        return InsuranceDeductibleModelResult(
            subject=self.subject,
            lens=self.lens,
            base_value=round(self.base_value(prop, metrics), 2),
            stressed_value=round(self.stressed_value(prop, metrics), 2),
            score=self.score(prop, metrics),
            confidence=self.confidence,
            notes=self.explain(prop, metrics),
        )

