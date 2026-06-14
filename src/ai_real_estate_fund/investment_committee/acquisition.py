from __future__ import annotations
from .base import CommitteeAgent, money, pct, score_range
from ..finance import max_price_for_target_cap_rate

class AcquisitionPricingAgent(CommitteeAgent):
    name = "Acquisition Pricing Agent"
    role = "Tests the ask against stabilized income, max-offer math, and margin of safety."
    weight = 1.25
    category = "pricing"

    def analyze(self, prop, metrics, data, prior_findings):
        max_offer = max_price_for_target_cap_rate(prop, target_cap_rate=0.075)
        margin = (max_offer - prop.purchase_price) / prop.purchase_price if prop.purchase_price else -1
        cap_score = score_range(metrics.cap_rate, 0.045, 0.095)
        margin_score = score_range(margin, -0.15, 0.20)
        # A no-debt deal has metrics.dscr == inf; score_range clamps it to the band top (100).
        dscr_score = score_range(metrics.dscr, 0.95, 1.75)
        score = cap_score * 0.45 + margin_score * 0.40 + dscr_score * 0.15
        positives = []
        concerns = []
        if metrics.cap_rate >= 0.075:
            positives.append(f"Stabilized cap rate is attractive at {pct(metrics.cap_rate)}.")
        else:
            concerns.append(f"Cap rate of {pct(metrics.cap_rate)} is below the 7.5% target used by the committee.")
        if margin > 0:
            positives.append(f"Modeled max offer of {money(max_offer)} is above the ask by {pct(margin)}.")
        else:
            concerns.append(f"Modeled max offer of {money(max_offer)} is below the ask by {pct(abs(margin))}.")
        return self.finding(
            score=score,
            confidence=0.82,
            thesis=f"Pricing is driven by {pct(metrics.cap_rate)} cap rate, {pct(margin)} margin of safety, and {metrics.dscr:.2f}x DSCR.",
            positives=positives,
            concerns=concerns,
            evidence=[self.metric("cap_rate", round(metrics.cap_rate, 4)), self.metric("max_offer_price", round(max_offer, 2)), self.metric("dscr", round(metrics.dscr, 3))],
            actions=["Re-trade if confirmed rents, taxes, or insurance weaken the modeled NOI."],
        )
