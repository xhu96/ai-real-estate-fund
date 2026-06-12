from __future__ import annotations


def implied_value_from_noi(noi: float, cap_rate: float) -> float:
    if cap_rate <= 0:
        raise ValueError("cap_rate must be positive")
    return max(0.0, noi / cap_rate)


def yield_on_cost(stabilized_noi: float, total_project_cost: float) -> float:
    if total_project_cost <= 0:
        return 0.0
    return stabilized_noi / total_project_cost


def cap_rate_spread(asset_cap_rate: float, market_cap_rate: float) -> float:
    return asset_cap_rate - market_cap_rate
