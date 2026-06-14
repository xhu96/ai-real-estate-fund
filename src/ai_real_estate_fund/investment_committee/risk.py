from __future__ import annotations
from .base import CommitteeAgent, average_prior, pct

class RiskManagerAgent(CommitteeAgent):
    name = "Risk Manager Agent"
    role = "Synthesizes downside risks, hard-pass triggers, and assumption fragility."
    weight = 1.30
    category = "risk"

    def analyze(self, prop, metrics, data, prior_findings):
        base = average_prior(prior_findings, 55.0)
        penalty = 0.0
        concerns, positives = [], []
        if metrics.cash_flow_before_tax < 0:
            penalty += 22
            concerns.append("Base-case cash flow is negative before tax.")
        if metrics.dscr != float("inf") and metrics.dscr < 1.15:
            penalty += 18
            concerns.append(f"DSCR below safety threshold at {metrics.dscr:.2f}x.")
        if data.data_quality and data.data_quality.completeness_score < 70:
            penalty += 12
            concerns.append("Diligence data quality is incomplete.")
        if prop.rehab_budget / prop.purchase_price > 0.25:
            penalty += 12
            concerns.append("Rehab budget is high relative to acquisition price.")
        if prop.vacancy_rate < data.market_snapshot.vacancy_rate:
            penalty += 6
            concerns.append(f"Vacancy assumption of {pct(prop.vacancy_rate)} is below market fixture {pct(data.market_snapshot.vacancy_rate)}.")
        if not concerns:
            positives.append("No hard-pass risk trigger was found in deterministic checks.")
        score = max(0.0, min(100.0, base - penalty + 5))
        return self.finding(
            score=score,
            confidence=0.86,
            thesis=f"Risk-adjusted score starts from committee average {base:.1f} and applies {penalty:.1f} points of downside penalties.",
            positives=positives,
            concerns=concerns,
            evidence=[self.metric("cash_flow_before_tax", round(metrics.cash_flow_before_tax, 2)), self.metric("dscr", round(metrics.dscr, 3)), self.assumption("vacancy_rate", round(prop.vacancy_rate, 4))],
            actions=["Do not waive inspection, financing, insurance, tax, or title contingencies until risk items are cleared."],
        )
