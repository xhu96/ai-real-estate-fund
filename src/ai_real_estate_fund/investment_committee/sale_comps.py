from __future__ import annotations
from .base import CommitteeAgent, money, safe_median, score_range

class SaleCompsAgent(CommitteeAgent):
    name = "Sale Comps Agent"
    role = "Checks acquisition price against sale comps on per-unit and per-square-foot bases."
    weight = 1.05
    category = "valuation"

    def analyze(self, prop, metrics, data, prior_findings):
        ppu_values = [c.price_per_unit() for c in data.sale_comps if c.price_per_unit() > 0]
        ppsf_values = [c.price_per_sqft() for c in data.sale_comps if c.price_per_sqft() > 0]
        median_ppu = safe_median(ppu_values)
        median_ppsf = safe_median(ppsf_values)
        subject_ppu = prop.purchase_price / prop.unit_count if prop.unit_count else prop.purchase_price
        subject_ppsf = prop.purchase_price / prop.square_feet if prop.square_feet else median_ppsf
        ppu_ratio = subject_ppu / median_ppu if median_ppu else 1.0
        ppsf_ratio = subject_ppsf / median_ppsf if median_ppsf else 1.0
        score = (100 - abs(ppu_ratio - 0.95) * 170) * 0.60 + (100 - abs(ppsf_ratio - 0.95) * 150) * 0.40
        positives, concerns = [], []
        if ppu_ratio <= 0.98:
            positives.append(f"Subject price per unit of {money(subject_ppu)} is below comp median of {money(median_ppu)}.")
        else:
            concerns.append(f"Subject price per unit of {money(subject_ppu)} exceeds comp median of {money(median_ppu)}.")
        if prop.square_feet:
            if ppsf_ratio <= 1.0:
                positives.append(f"Subject price per sqft of {money(subject_ppsf)} is supported by sale comps.")
            else:
                concerns.append(f"Subject price per sqft of {money(subject_ppsf)} is above the comp median of {money(median_ppsf)}.")
        return self.finding(
            score=score,
            confidence=0.72 if data.sale_comps else 0.35,
            thesis=f"Sale comp analysis uses {len(data.sale_comps)} comps with {ppu_ratio:.2f}x price-per-unit ratio.",
            positives=positives,
            concerns=concerns,
            evidence=[self.market_evidence("median_price_per_unit", median_ppu), self.market_evidence("median_price_per_sqft", median_ppsf), self.assumption("subject_price", prop.purchase_price)],
            actions=["Normalize sale comps for condition, financing concessions, and renovation scope."],
        )
