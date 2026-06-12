from __future__ import annotations
from .base import CommitteeAgent, pct, score_range

class DebtCapitalMarketsAgent(CommitteeAgent):
    name = "Debt Capital Markets Agent"
    role = "Evaluates loan proceeds, interest-rate exposure, DSCR, and refinancing risk."
    weight = 1.15
    category = "capital_stack"

    def analyze(self, prop, metrics, data, prior_findings):
        ltc_score = score_range(metrics.loan_to_cost, 0.85, 0.60, invert=True)
        dscr_score = score_range(metrics.dscr if metrics.dscr != float("inf") else 2.0, 1.00, 1.65)
        rate_score = score_range(prop.annual_interest_rate, 0.095, 0.045, invert=True)
        score = ltc_score * 0.30 + dscr_score * 0.50 + rate_score * 0.20
        positives, concerns = [], []
        if metrics.dscr >= 1.25:
            positives.append(f"Debt-service coverage is acceptable at {metrics.dscr:.2f}x.")
        else:
            concerns.append(f"Debt-service coverage is thin at {metrics.dscr:.2f}x.")
        if metrics.loan_to_cost <= 0.75:
            positives.append(f"Loan-to-cost of {pct(metrics.loan_to_cost)} leaves some equity cushion.")
        else:
            concerns.append(f"Loan-to-cost of {pct(metrics.loan_to_cost)} increases refinance and maturity risk.")
        return self.finding(
            score=score,
            confidence=0.80,
            thesis=f"Capital stack review centers on {metrics.dscr:.2f}x DSCR, {pct(metrics.loan_to_cost)} LTC, and {pct(prop.annual_interest_rate)} coupon.",
            positives=positives,
            concerns=concerns,
            evidence=[self.metric("annual_debt_service", round(metrics.annual_debt_service, 2)), self.metric("loan_to_cost", round(metrics.loan_to_cost, 4)), self.assumption("interest_rate", round(prop.annual_interest_rate, 4))],
            actions=["Obtain lender term sheet with rate lock, prepayment, escrow, and reserve requirements."],
        )
