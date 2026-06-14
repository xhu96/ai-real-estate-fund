from __future__ import annotations


def net_present_value(cash_flows: list[float], discount_rate: float) -> float:
    if discount_rate <= -1:
        raise ValueError("discount_rate must be greater than -100%")
    return sum(value / ((1 + discount_rate) ** idx) for idx, value in enumerate(cash_flows))


def discounted_cash_flow_value(noi_year_1: float, growth_rate: float, terminal_cap_rate: float, discount_rate: float, hold_years: int, selling_cost_rate: float = 0.06) -> float:
    if hold_years <= 0:
        raise ValueError("hold_years must be positive")
    if terminal_cap_rate <= 0:
        raise ValueError("terminal_cap_rate must be positive")
    cash_flows = [0.0]
    for year in range(1, hold_years + 1):
        noi = noi_year_1 * ((1 + growth_rate) ** (year - 1))
        if year == hold_years:
            terminal_noi = noi * (1 + growth_rate)
            terminal_value = terminal_noi / terminal_cap_rate * (1 - selling_cost_rate)
            noi += terminal_value
        cash_flows.append(noi)
    return net_present_value(cash_flows, discount_rate)


def terminal_value(noi: float, terminal_cap_rate: float, selling_cost_rate: float = 0.06) -> float:
    if terminal_cap_rate <= 0:
        return 0.0
    return noi / terminal_cap_rate * (1 - selling_cost_rate)
