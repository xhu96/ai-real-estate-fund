from __future__ import annotations
from .base import CommitteeAgent, money, pct, score_range

class ExitLiquidityAgent(CommitteeAgent):
    name = "Exit Liquidity Agent"
    role = "Assesses resale depth, appreciation assumptions, and terminal-value fragility."
    weight = 0.95
    category = "exit"

    def analyze(self, prop, metrics, data, prior_findings):
        m = data.market_snapshot
        appreciation_delta = prop.expected_annual_appreciation - m.appreciation_yoy
        assumption_score = score_range(abs(appreciation_delta), 0.035, 0.0, invert=True)
        liquidity_score = m.liquidity_score * 10
        exit_multiple_score = score_range(metrics.equity_multiple, 1.00, 2.25)
        score = assumption_score * 0.30 + liquidity_score * 0.35 + exit_multiple_score * 0.35
        positives, concerns = [], []
        if metrics.equity_multiple >= 1.5:
            positives.append(f"Base case equity multiple of {metrics.equity_multiple:.2f}x provides exit upside.")
        else:
            concerns.append(f"Base case equity multiple of {metrics.equity_multiple:.2f}x leaves thin terminal-value cushion.")
        if abs(appreciation_delta) > 0.015:
            concerns.append(f"Appreciation assumption differs from market snapshot by {pct(appreciation_delta)}.")
        else:
            positives.append("Appreciation assumption is close to market fixture.")
        return self.finding(
            score=score,
            confidence=0.65,
            thesis=f"Exit analysis balances {m.liquidity_score:.1f}/10 liquidity, {pct(prop.expected_annual_appreciation)} appreciation, and {money(metrics.projected_net_sale_proceeds)} net sale proceeds.",
            positives=positives,
            concerns=concerns,
            evidence=[self.metric("projected_sale_price", round(metrics.projected_sale_price, 2)), self.metric("projected_net_sale_proceeds", round(metrics.projected_net_sale_proceeds, 2)), self.market_evidence("liquidity_score", m.liquidity_score)],
            actions=["Build a downside exit cap-rate case and verify buyer depth for this asset size."],
        )
