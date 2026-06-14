from __future__ import annotations
from .base import CommitteeAgent, money, pct, score_range

class ReservePlanningAgent(CommitteeAgent):
    name = "Reserve Planning Agent"
    role = "Checks reserves for capex, repairs, debt-service interruption, and post-close liquidity."
    weight = 0.90
    category = "capital_stack"

    def analyze(self, prop, metrics, data, prior_findings):
        annual_reserves = prop.repairs_annual + prop.capex_annual
        reserve_per_unit = annual_reserves / prop.unit_count if prop.unit_count else annual_reserves
        reserve_ratio = annual_reserves / metrics.gross_potential_income if metrics.gross_potential_income else 0
        score = score_range(reserve_ratio, 0.02, 0.12) if reserve_ratio < 0.12 else score_range(reserve_ratio, 0.28, 0.12, invert=True)
        positives, concerns = [], []
        if reserve_ratio >= 0.06:
            positives.append(f"Repairs/capex reserves equal {pct(reserve_ratio)} of GPI.")
        else:
            concerns.append(f"Repairs/capex reserves equal only {pct(reserve_ratio)} of GPI.")
        return self.finding(score=score, confidence=0.68, thesis=f"Reserve plan models {money(annual_reserves)} per year or {money(reserve_per_unit)} per unit.", positives=positives, concerns=concerns, evidence=[self.assumption("repairs_annual", prop.repairs_annual), self.assumption("capex_annual", prop.capex_annual)], actions=["Add closing liquidity reserve for insurance deductibles, vacancy, turns, and lender escrows."])
