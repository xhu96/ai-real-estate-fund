from __future__ import annotations
from .base import CommitteeAgent, average_prior, money, pct, prior_score

class PortfolioManagerAgent(CommitteeAgent):
    name = "Portfolio Manager Agent"
    role = "Transforms deal-level diligence into allocation, sizing, and watchlist guidance."
    weight = 1.15
    category = "portfolio"

    def analyze(self, prop, metrics, data, prior_findings):
        committee_score = average_prior(prior_findings, 50.0)
        risk_score = prior_score(prior_findings, "Risk Manager Agent", committee_score)
        quality = data.data_quality.completeness_score if data.data_quality else 55
        allocation = 0.0
        if committee_score >= 80 and risk_score >= 70 and quality >= 75:
            allocation = 0.12
        elif committee_score >= 70 and risk_score >= 60:
            allocation = 0.08
        elif committee_score >= 60:
            allocation = 0.04
        score = committee_score * 0.60 + risk_score * 0.25 + quality * 0.15
        positives, concerns = [], []
        if allocation > 0:
            positives.append(f"Provisional allocation of {pct(allocation)} is supportable after diligence clears.")
        else:
            concerns.append("Allocation should remain zero until score, risk, or data-quality issues improve.")
        if metrics.cash_invested > 0:
            positives.append(f"Required cash investment is {money(metrics.cash_invested)} before reserves.")
        return self.finding(
            score=score,
            confidence=0.78,
            thesis=f"Portfolio sizing score is {score:.1f}, blending committee score {committee_score:.1f}, risk score {risk_score:.1f}, and data quality {quality:.1f}.",
            positives=positives,
            concerns=concerns,
            evidence=[self.metric("cash_invested", round(metrics.cash_invested, 2)), self.market_evidence("data_quality_score", quality)],
            actions=["Size final equity commitment only after reserves, lender covenants, and concentration limits are set."],
        )
