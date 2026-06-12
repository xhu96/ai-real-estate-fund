from __future__ import annotations


def debt_yield(noi: float, loan_amount: float) -> float:
    return noi / loan_amount if loan_amount > 0 else float("inf")


def refinance_proceeds(noi: float, debt_yield_threshold: float, max_ltv_value: float, max_ltv: float) -> float:
    by_debt_yield = noi / debt_yield_threshold if debt_yield_threshold > 0 else max_ltv_value * max_ltv
    by_ltv = max_ltv_value * max_ltv
    return max(0.0, min(by_debt_yield, by_ltv))


def interest_rate_shock(current_rate: float, shock_bps: int) -> float:
    return current_rate + shock_bps / 10000
