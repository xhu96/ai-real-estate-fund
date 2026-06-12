from __future__ import annotations
from .base import CommitteeAgent, pct, score_range

class MarketFundamentalsAgent(CommitteeAgent):
    name = "Market Fundamentals Agent"
    role = "Evaluates population, job growth, vacancy, liquidity, crime, and school proxies."
    weight = 1.10
    category = "market"

    def analyze(self, prop, metrics, data, prior_findings):
        m = data.market_snapshot
        growth_score = score_range(m.population_growth_yoy + m.job_growth_yoy, -0.005, 0.045)
        vacancy_score = score_range(m.vacancy_rate, 0.11, 0.035, invert=True)
        quality_score = (m.liquidity_score + m.school_score + (10 - m.crime_risk_score)) / 30 * 100
        score = growth_score * 0.40 + vacancy_score * 0.25 + quality_score * 0.35
        positives, concerns = [], []
        if m.population_growth_yoy > 0.01:
            positives.append(f"Population growth proxy is positive at {pct(m.population_growth_yoy)} YoY.")
        else:
            concerns.append(f"Population growth proxy is weak at {pct(m.population_growth_yoy)} YoY.")
        if m.job_growth_yoy > 0.015:
            positives.append(f"Job growth proxy is healthy at {pct(m.job_growth_yoy)} YoY.")
        if m.crime_risk_score > 6:
            concerns.append("Crime-risk proxy is elevated and requires block-level validation.")
        return self.finding(
            score=score,
            confidence=0.70,
            thesis=f"Market snapshot combines growth {pct(m.population_growth_yoy + m.job_growth_yoy)}, vacancy {pct(m.vacancy_rate)}, and liquidity score {m.liquidity_score:.1f}/10.",
            positives=positives,
            concerns=concerns,
            evidence=[self.market_evidence("population_growth_yoy", round(m.population_growth_yoy, 4)), self.market_evidence("job_growth_yoy", round(m.job_growth_yoy, 4)), self.market_evidence("vacancy_rate", round(m.vacancy_rate, 4))],
            actions=["Replace fixture market data with licensed or first-party local-market data before live use."],
        )
