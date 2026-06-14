from __future__ import annotations
from .base import CommitteeAgent, pct, score_range

class AppreciationAssumptionAgent(CommitteeAgent):
    name = "Appreciation Assumption Agent"
    role = "Challenges embedded appreciation, ARV, and terminal-value assumptions."
    weight = 0.85
    category = "exit"

    def analyze(self, prop, metrics, data, prior_findings):
        market_app = data.market_snapshot.appreciation_yoy
        spread = prop.expected_annual_appreciation - market_app
        arv_premium = (prop.estimated_arv - prop.purchase_price) / prop.purchase_price if prop.estimated_arv else 0
        score = score_range(abs(spread), 0.04, 0.00, invert=True) * 0.55 + score_range(arv_premium, -0.05, 0.25) * 0.45
        positives, concerns = [], []
        if abs(spread) <= 0.01:
            positives.append("Appreciation assumption is close to market snapshot.")
        else:
            concerns.append(f"Appreciation assumption differs from market snapshot by {pct(spread)}.")
        if prop.estimated_arv and arv_premium > 0.15:
            positives.append(f"Estimated ARV implies {pct(arv_premium)} value uplift over purchase price.")
        return self.finding(score=score, confidence=0.62, thesis=f"Terminal value assumes {pct(prop.expected_annual_appreciation)} annual appreciation versus market fixture {pct(market_app)}.", positives=positives, concerns=concerns, evidence=[self.assumption("expected_annual_appreciation", round(prop.expected_annual_appreciation,4)), self.market_evidence("market_appreciation_yoy", round(market_app,4)), self.assumption("estimated_arv", prop.estimated_arv)], actions=["Run sensitivity with flat value growth and higher exit cap rate."])
