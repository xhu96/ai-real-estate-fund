from __future__ import annotations
from .models import BacktestConfig, BacktestTrade

class BacktestPortfolio:
    def __init__(self, config: BacktestConfig) -> None:
        self.config = config
        self.equity = config.starting_equity
        self.positions = 0

    def apply_trade(self, trade: BacktestTrade) -> None:
        if not trade.selected or self.positions >= self.config.max_positions:
            return
        allocation = self.config.starting_equity * self.config.allocation_per_deal
        self.equity -= allocation
        self.equity += allocation * trade.realized_equity_multiple
        self.positions += 1
