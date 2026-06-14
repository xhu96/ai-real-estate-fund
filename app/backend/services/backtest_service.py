from __future__ import annotations
from ai_real_estate_fund.backtesting import BacktestConfig, BacktestEngine
from ai_real_estate_fund.backtesting.fixtures import example_historical_deals
from ..models.schemas import BacktestPayload

# Hardcoded bundled dataset. Never accept a client-supplied path (no traversal).
_DATASET = "examples/properties.csv"


class BacktestService:
    def run(self, body: BacktestPayload) -> dict:
        config = BacktestConfig(
            min_score=float(body.min_score),
            starting_equity=float(body.starting_equity),
            max_positions=int(body.max_positions),
            allocation_per_deal=float(body.allocation_per_deal),
        )
        result = BacktestEngine(config=config).run(example_historical_deals(_DATASET))
        return result.to_dict()
