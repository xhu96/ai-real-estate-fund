from __future__ import annotations
from .base import CommitteeAgent, money, pct, score_range

class TaxAndAssessmentAgent(CommitteeAgent):
    name = "Tax and Assessment Agent"
    role = "Reviews reassessment exposure, property-tax load, and closing-proration risk."
    weight = 0.95
    category = "expenses"

    def analyze(self, prop, metrics, data, prior_findings):
        tax_rate = prop.property_taxes_annual / prop.purchase_price if prop.purchase_price else data.market_snapshot.property_tax_rate
        market_rate = data.market_snapshot.property_tax_rate
        rate_score = score_range(tax_rate, market_rate + 0.012, max(0.001, market_rate - 0.006), invert=True)
        expense_share = prop.property_taxes_annual / metrics.effective_gross_income if metrics.effective_gross_income else 1.0
        share_score = score_range(expense_share, 0.32, 0.08, invert=True)
        score = rate_score * 0.60 + share_score * 0.40
        positives, concerns = [], []
        if tax_rate <= market_rate + 0.004:
            positives.append(f"Tax assumption of {pct(tax_rate)} is close to market fixture rate of {pct(market_rate)}.")
        else:
            concerns.append(f"Tax assumption of {pct(tax_rate)} is above fixture rate of {pct(market_rate)}.")
        if expense_share > 0.25:
            concerns.append(f"Property taxes consume {pct(expense_share)} of EGI.")
        return self.finding(
            score=score,
            confidence=0.66,
            thesis=f"Tax burden is modeled at {money(prop.property_taxes_annual)}/yr or {pct(tax_rate)} of price.",
            positives=positives,
            concerns=concerns,
            evidence=[self.assumption("property_taxes_annual", prop.property_taxes_annual), self.market_evidence("market_property_tax_rate", round(market_rate, 4))],
            actions=["Confirm reassessed taxes with county records and local tax counsel before final underwriting."],
        )
