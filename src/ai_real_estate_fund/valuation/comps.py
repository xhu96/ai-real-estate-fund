from __future__ import annotations
from statistics import median
from ..models import RentComp, SaleComp


def sale_comp_value_range(comps: list[SaleComp], unit_count: int, square_feet: float = 0.0) -> dict[str, float]:
    per_unit = [c.price_per_unit() for c in comps if c.price_per_unit() > 0]
    per_sqft = [c.price_per_sqft() for c in comps if c.price_per_sqft() > 0]
    values = []
    if per_unit and unit_count:
        values.append(median(per_unit) * unit_count)
    if per_sqft and square_feet:
        values.append(median(per_sqft) * square_feet)
    if not values:
        return {"low": 0.0, "mid": 0.0, "high": 0.0}
    mid = median(values)
    return {"low": mid * 0.92, "mid": mid, "high": mid * 1.08}


def rent_comp_range(comps: list[RentComp]) -> dict[str, float]:
    rents = sorted(c.monthly_rent for c in comps if c.monthly_rent > 0)
    if not rents:
        return {"low": 0.0, "mid": 0.0, "high": 0.0}
    mid = median(rents)
    return {"low": rents[0], "mid": mid, "high": rents[-1]}
