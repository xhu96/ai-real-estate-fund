from __future__ import annotations
from dataclasses import replace
from ..finance import underwrite_property
from ..models import PropertyInput


def stress_property(prop: PropertyInput, *, rent_cut: float = 0.05, expense_growth: float = 0.10, rate_shock: float = 0.01) -> dict[str, float]:
    stressed = replace(
        prop,
        monthly_rent=prop.monthly_rent * (1 - rent_cut),
        property_taxes_annual=prop.property_taxes_annual * (1 + expense_growth),
        insurance_annual=prop.insurance_annual * (1 + expense_growth),
        repairs_annual=prop.repairs_annual * (1 + expense_growth),
        annual_interest_rate=prop.annual_interest_rate + rate_shock,
    )
    metrics = underwrite_property(stressed)
    return {
        "cap_rate": metrics.cap_rate,
        "cash_on_cash_return": metrics.cash_on_cash_return,
        "dscr": metrics.dscr,
        "cash_flow_before_tax": metrics.cash_flow_before_tax,
    }
