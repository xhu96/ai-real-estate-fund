from __future__ import annotations
from .base import CommitteeAgent, money, pct, score_range

class CashFlowQualityAgent(CommitteeAgent):
    name = "Cash Flow Quality Agent"
    role = "Reviews durability of cash flow after vacancy, reserves, debt service, and management fees."
    weight = 1.10
    category = "income"

    def analyze(self, prop, metrics, data, prior_findings):
        cash_margin = metrics.cash_flow_before_tax / metrics.effective_gross_income if metrics.effective_gross_income else -1
        reserve_load = (prop.repairs_annual + prop.capex_annual) / metrics.effective_gross_income if metrics.effective_gross_income else 1
        margin_score = score_range(cash_margin, -0.10, 0.22)
        reserve_score = score_range(reserve_load, 0.24, 0.06, invert=True)
        breakeven_score = score_range(metrics.break_even_occupancy, 0.98, 0.72, invert=True)
        score = margin_score * 0.45 + reserve_score * 0.20 + breakeven_score * 0.35
        positives, concerns = [], []
        if cash_margin > 0.10:
            positives.append(f"Cash-flow margin is healthy at {pct(cash_margin)} of EGI.")
        else:
            concerns.append(f"Cash-flow margin is thin at {pct(cash_margin)} of EGI.")
        if metrics.break_even_occupancy < 0.85:
            positives.append(f"Break-even occupancy of {pct(metrics.break_even_occupancy)} leaves vacancy cushion.")
        else:
            concerns.append(f"Break-even occupancy of {pct(metrics.break_even_occupancy)} is high.")
        return self.finding(score=score, confidence=0.80, thesis=f"Cash flow quality is anchored by {money(metrics.cash_flow_before_tax)} annual cash flow and {pct(metrics.break_even_occupancy)} break-even occupancy.", positives=positives, concerns=concerns, evidence=[self.metric("cash_flow_before_tax", round(metrics.cash_flow_before_tax,2)), self.metric("break_even_occupancy", round(metrics.break_even_occupancy,4)), self.assumption("capex_annual", prop.capex_annual)], actions=["Confirm repairs, capex, utilities, and bad-debt assumptions with property-manager quotes."])
