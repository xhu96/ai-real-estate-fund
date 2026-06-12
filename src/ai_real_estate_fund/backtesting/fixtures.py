from __future__ import annotations
from dataclasses import replace
from ..data_loader import load_properties
from .models import HistoricalDeal


def example_historical_deals(path: str = "examples/properties.csv") -> list[HistoricalDeal]:
    deals = []
    for idx, prop in enumerate(load_properties(path)):
        realized_irr = [0.21, 0.12, -0.03][idx % 3]
        realized_multiple = [1.85, 1.35, 0.92][idx % 3]
        deals.append(
            HistoricalDeal(
                property=replace(prop, name=f"Historical {prop.name}"),
                acquisition_date="2019-01-01",
                exit_date="2024-01-01",
                realized_irr=realized_irr,
                realized_equity_multiple=realized_multiple,
            )
        )
    return deals
