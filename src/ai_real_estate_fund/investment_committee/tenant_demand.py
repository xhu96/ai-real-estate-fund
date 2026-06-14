from __future__ import annotations
from .base import CommitteeAgent, pct, score_range

class TenantDemandAgent(CommitteeAgent):
    name = "Tenant Demand Agent"
    role = "Assesses lease-up resilience using rent level, vacancy, schools, and neighborhood proxies."
    weight = 0.95
    category = "income"

    def analyze(self, prop, metrics, data, prior_findings):
        m = data.market_snapshot
        vacancy_score = score_range(m.vacancy_rate, 0.11, 0.035, invert=True)
        school_score = m.school_score * 10
        neighborhood_score = prop.neighborhood_score * 10
        rent_growth_score = score_range(m.rent_growth_yoy, -0.01, 0.06)
        score = vacancy_score * 0.30 + school_score * 0.25 + neighborhood_score * 0.25 + rent_growth_score * 0.20
        positives, concerns = [], []
        if m.vacancy_rate <= 0.065:
            positives.append(f"Market vacancy proxy is manageable at {pct(m.vacancy_rate)}.")
        else:
            concerns.append(f"Market vacancy proxy is elevated at {pct(m.vacancy_rate)}.")
        if prop.school_score < 5:
            concerns.append("Subject school score is weak for family-oriented long-term rental demand.")
        if m.rent_growth_yoy > 0.03:
            positives.append(f"Rent-growth proxy is above 3% at {pct(m.rent_growth_yoy)}.")
        return self.finding(
            score=score,
            confidence=0.63,
            thesis=f"Tenant-demand score reflects vacancy {pct(m.vacancy_rate)}, school {prop.school_score:.1f}/10, and rent growth {pct(m.rent_growth_yoy)}.",
            positives=positives,
            concerns=concerns,
            evidence=[self.market_evidence("rent_growth_yoy", round(m.rent_growth_yoy, 4)), self.market_evidence("market_vacancy_rate", round(m.vacancy_rate, 4)), self.assumption("school_score", prop.school_score)],
            actions=["Review days-on-market for comparable rentals and call local leasing agents."],
        )
