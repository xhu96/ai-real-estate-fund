from __future__ import annotations
from .base import CommitteeAgent, money, pct, safe_median, score_range

class RentalCompsAgent(CommitteeAgent):
    name = "Rental Comps Agent"
    role = "Compares proposed rent against nearby rent comps and leasing assumptions."
    weight = 1.10
    category = "income"

    def analyze(self, prop, metrics, data, prior_findings):
        comp_rents = [c.monthly_rent for c in data.rent_comps if c.monthly_rent > 0]
        median_rent = safe_median(comp_rents)
        rent_ratio = prop.monthly_rent / median_rent if median_rent else 1.0
        comp_conf = sum(c.confidence for c in data.rent_comps) / len(data.rent_comps) if data.rent_comps else 0.35
        ratio_score = 100 - abs(rent_ratio - 0.97) * 170
        vacancy_score = score_range(1 - prop.vacancy_rate, 0.87, 0.98)
        score = ratio_score * 0.65 + vacancy_score * 0.20 + comp_conf * 100 * 0.15
        positives, concerns = [], []
        if 0.90 <= rent_ratio <= 1.03:
            positives.append(f"Modeled rent of {money(prop.monthly_rent)}/mo is near the comp median of {money(median_rent)}/mo.")
        elif rent_ratio > 1.03:
            concerns.append(f"Modeled rent is {pct(rent_ratio - 1)} above comp median and needs verification.")
        else:
            positives.append(f"Modeled rent is below comp median, leaving potential upside if condition supports it.")
        if prop.vacancy_rate <= data.market_snapshot.vacancy_rate + 0.015:
            positives.append("Vacancy assumption is broadly aligned with market snapshot.")
        else:
            concerns.append("Vacancy assumption is materially more conservative than the market snapshot.")
        return self.finding(
            score=score,
            confidence=max(0.40, min(0.90, comp_conf)),
            thesis=f"Rent support is based on {len(data.rent_comps)} comps and a rent-to-median ratio of {rent_ratio:.2f}x.",
            positives=positives,
            concerns=concerns,
            evidence=[self.assumption("subject_monthly_rent", prop.monthly_rent), self.market_evidence("median_rent_comp", median_rent), self.market_evidence("rent_comp_count", len(data.rent_comps))],
            actions=["Call at least three property managers and verify leased, not just listed, rents."],
        )
