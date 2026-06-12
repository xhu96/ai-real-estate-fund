from __future__ import annotations
from .base import CommitteeAgent, pct, score_range

class LeaseUpAgent(CommitteeAgent):
    name = "Lease-Up Agent"
    role = "Estimates risk around vacancy, concessions, time-to-lease, and rent stabilization."
    weight = 0.90
    category = "income"

    def analyze(self, prop, metrics, data, prior_findings):
        vacancy_delta = prop.vacancy_rate - data.market_snapshot.vacancy_rate
        vacancy_score = score_range(prop.vacancy_rate, 0.14, 0.035, invert=True)
        rent_growth_score = score_range(data.market_snapshot.rent_growth_yoy, -0.02, 0.06)
        score = vacancy_score * 0.65 + rent_growth_score * 0.35
        positives, concerns = [], []
        if vacancy_delta >= 0: positives.append("Vacancy assumption is at or above the fixture market vacancy rate.")
        else: concerns.append(f"Vacancy assumption is {pct(abs(vacancy_delta))} below fixture market vacancy.")
        if data.market_snapshot.rent_growth_yoy < 0: concerns.append("Negative rent growth would make lease-up materially harder.")
        return self.finding(score=score, confidence=0.64, thesis=f"Lease-up risk uses modeled vacancy {pct(prop.vacancy_rate)} and market rent growth {pct(data.market_snapshot.rent_growth_yoy)}.", positives=positives, concerns=concerns, evidence=[self.assumption("vacancy_rate", round(prop.vacancy_rate,4)), self.market_evidence("market_vacancy_rate", round(data.market_snapshot.vacancy_rate,4))], actions=["Collect active-listing days-on-market and concession evidence for direct competitors."])
