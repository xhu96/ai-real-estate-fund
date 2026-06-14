from __future__ import annotations
from .base import CommitteeAgent, money, pct, score_range

class InsuranceAgent(CommitteeAgent):
    name = "Insurance Agent"
    role = "Evaluates insurance load, catastrophe exposure proxies, and quote uncertainty."
    weight = 0.90
    category = "expenses"

    def analyze(self, prop, metrics, data, prior_findings):
        insurance_rate = prop.insurance_annual / prop.purchase_price if prop.purchase_price else data.market_snapshot.insurance_rate
        market_rate = data.market_snapshot.insurance_rate
        rate_score = score_range(insurance_rate, market_rate + 0.009, max(0.001, market_rate - 0.003), invert=True)
        score = rate_score
        positives, concerns = [], []
        if insurance_rate <= market_rate + 0.002:
            positives.append("Insurance assumption is broadly in line with fixture market rate.")
        else:
            concerns.append(f"Insurance assumption equals {pct(insurance_rate)} of purchase price, above market fixture {pct(market_rate)}.")
        if prop.year_built and prop.year_built < 1950:
            concerns.append("Older construction may increase carrier scrutiny and replacement-cost requirements.")
            score -= 8
        return self.finding(
            score=score,
            confidence=0.58,
            thesis=f"Insurance load is modeled at {money(prop.insurance_annual)}/yr or {pct(insurance_rate)} of price.",
            positives=positives,
            concerns=concerns,
            evidence=[self.assumption("insurance_annual", prop.insurance_annual), self.market_evidence("market_insurance_rate", round(market_rate, 4))],
            actions=["Collect bindable insurance quote, loss runs, flood map, roof age, and replacement-cost estimate."],
        )
