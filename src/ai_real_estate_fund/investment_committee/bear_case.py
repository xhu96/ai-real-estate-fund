from __future__ import annotations
from .base import CommitteeAgent, average_prior, money, pct

class BearCaseAgent(CommitteeAgent):
    name = "Bear Case Agent"
    role = "Attacks the deal by emphasizing uncertainty, downside cases, and weak assumptions."
    weight = 0.75
    category = "debate"

    def analyze(self, prop, metrics, data, prior_findings):
        concerns = [item for f in prior_findings for item in f.concerns]
        base = average_prior(prior_findings, 55.0)
        score = max(0.0, base - 10)
        selected = concerns[:5] or ["Even if base-case math works, real estate outcomes are highly assumption-sensitive."]
        if metrics.cash_flow_before_tax < 0 and "Negative cash flow" not in " ".join(selected):
            selected.insert(0, f"Property produces {money(metrics.cash_flow_before_tax)} annual cash flow before tax in base case.")
        return self.finding(
            score=score,
            confidence=0.74,
            thesis=f"Bear case: small misses in rent, expenses, financing, or exit cap rates can erase a {pct(metrics.cash_on_cash_return)} cash-on-cash return.",
            positives=["The bear case is useful because it converts assumptions into diligence tasks."],
            concerns=selected,
            evidence=[self.metric("cash_on_cash_return", round(metrics.cash_on_cash_return, 4)), self.metric("break_even_occupancy", round(metrics.break_even_occupancy, 4))],
            actions=["Run seller-credit, lower-rent, higher-rate, delayed-lease-up, and exit-cap stress cases."],
        )
