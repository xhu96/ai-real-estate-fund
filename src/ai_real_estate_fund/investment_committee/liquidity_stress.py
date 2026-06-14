from __future__ import annotations
from .base import CommitteeAgent, pct, score_range
from ..risk.stress import stress_property

class LiquidityStressAgent(CommitteeAgent):
    name = "Liquidity Stress Agent"
    role = "Applies a combined rent, expense, and rate shock to assess survivability."
    weight = 1.05
    category = "risk"

    def analyze(self, prop, metrics, data, prior_findings):
        stressed = stress_property(prop, rent_cut=0.07, expense_growth=0.12, rate_shock=0.0125)
        dscr = stressed["dscr"]
        coc = stressed["cash_on_cash_return"]
        # A no-debt deal stresses to dscr == inf; score_range clamps it to the band top (100).
        score = score_range(dscr, 0.85, 1.35) * 0.65 + score_range(coc, -0.08, 0.08) * 0.35
        positives, concerns = [], []
        if dscr >= 1.10:
            positives.append(f"Stressed DSCR remains above 1.10x at {dscr:.2f}x.")
        else:
            concerns.append(f"Stressed DSCR falls to {dscr:.2f}x.")
        if coc < 0:
            concerns.append(f"Stressed cash-on-cash return turns negative at {pct(coc)}.")
        return self.finding(score=score, confidence=0.78, thesis="Stress case cuts rent 7%, raises controllable expenses 12%, and adds 125 bps to debt cost.", positives=positives, concerns=concerns, evidence=[self.metric("stress_dscr", round(dscr,3)), self.metric("stress_cash_on_cash", round(coc,4))], actions=["Keep liquidity reserve sized to survive the stress case without forced sale or covenant breach."])
