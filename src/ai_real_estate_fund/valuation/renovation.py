from __future__ import annotations


def contingency_budget(hard_costs: float, contingency_rate: float = 0.12) -> float:
    return max(0.0, hard_costs * contingency_rate)


def all_in_rehab_budget(hard_costs: float, soft_costs: float = 0.0, contingency_rate: float = 0.12) -> float:
    return hard_costs + soft_costs + contingency_budget(hard_costs, contingency_rate)


def rehab_per_unit(rehab_budget: float, unit_count: int) -> float:
    return rehab_budget / unit_count if unit_count > 0 else rehab_budget
