from __future__ import annotations
from .base import CommitteeAgent, average_prior, money, pct

class BullCaseAgent(CommitteeAgent):
    name = "Bull Case Agent"
    role = "Writes the strongest reasonable pro-investment case using prior agent evidence."
    weight = 0.65
    category = "debate"

    def analyze(self, prop, metrics, data, prior_findings):
        positives = [item for f in prior_findings for item in f.positives]
        base = average_prior(prior_findings, 55.0)
        score = min(100.0, base + 8)
        selected = positives[:4] or ["The deal has a plausible path if underwriting assumptions are verified."]
        return self.finding(
            score=score,
            confidence=0.70,
            thesis=f"Bull case: {prop.name} can work if {pct(metrics.cap_rate)} cap rate, {metrics.dscr:.2f}x DSCR, and {money(metrics.projected_net_sale_proceeds)} terminal proceeds are confirmed.",
            positives=selected,
            concerns=["Bull case depends on independent verification of rent, taxes, insurance, condition, and exit liquidity."],
            evidence=[self.metric("cap_rate", round(metrics.cap_rate, 4)), self.metric("equity_multiple", round(metrics.equity_multiple, 3))],
            actions=["Turn the bull case into a falsifiable diligence checklist."],
        )
