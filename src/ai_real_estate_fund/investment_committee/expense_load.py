from __future__ import annotations
from .base import CommitteeAgent, pct, score_range

class ExpenseLoadAgent(CommitteeAgent):
    name = "Expense Load Agent"
    role = "Benchmarks operating expenses against effective gross income and flags under-reserved line items."
    weight = 1.00
    category = "expenses"

    def analyze(self, prop, metrics, data, prior_findings):
        expense_ratio = metrics.operating_expenses / metrics.effective_gross_income if metrics.effective_gross_income else 1
        controllable = (prop.repairs_annual + prop.utilities_annual + prop.hoa_annual + prop.capex_annual) / metrics.effective_gross_income if metrics.effective_gross_income else 1
        score = score_range(expense_ratio, 0.62, 0.28, invert=True) * 0.75 + score_range(controllable, 0.32, 0.08, invert=True) * 0.25
        positives, concerns = [], []
        if expense_ratio <= 0.45: positives.append(f"Expense ratio of {pct(expense_ratio)} is within a normal rental range.")
        else: concerns.append(f"Expense ratio of {pct(expense_ratio)} is high and compresses NOI.")
        if prop.capex_annual <= 0: concerns.append("Capex reserve is zero; this is rarely appropriate for production underwriting.")
        return self.finding(score=score, confidence=0.76, thesis=f"Expense load is {pct(expense_ratio)} of EGI with controllable expenses at {pct(controllable)} of EGI.", positives=positives, concerns=concerns, evidence=[self.metric("operating_expenses", round(metrics.operating_expenses,2)), self.metric("effective_gross_income", round(metrics.effective_gross_income,2))], actions=["Benchmark each expense line against operating statements, quotes, and local property manager feedback."])
