from __future__ import annotations
from .metrics import average_realized_irr, average_score, hit_rate
from .models import BacktestConfig, BacktestResult, BacktestTrade, HistoricalDeal
from .portfolio import BacktestPortfolio
from .strategy import ScoreThresholdStrategy
from ..investment_committee import ScreeningCommittee

class BacktestEngine:
    def __init__(self, committee: ScreeningCommittee | None = None, config: BacktestConfig | None = None) -> None:
        self.committee = committee or ScreeningCommittee()
        self.config = config or BacktestConfig()
        self.strategy = ScoreThresholdStrategy(self.config)

    def run(self, deals: list[HistoricalDeal]) -> BacktestResult:
        trades: list[BacktestTrade] = []
        portfolio = BacktestPortfolio(self.config)
        for deal in deals:
            decision = self.committee.run(deal.property)
            selected = self.strategy.should_select(decision)
            trade = BacktestTrade(
                deal_name=deal.property.name,
                selected=selected,
                score=decision.overall_score,
                recommendation=decision.recommendation.value,
                expected_irr=decision.metrics.irr,
                realized_irr=deal.realized_irr,
                realized_equity_multiple=deal.realized_equity_multiple,
            )
            portfolio.apply_trade(trade)
            trades.append(trade)
        return BacktestResult(
            trades=trades,
            selected_count=sum(1 for t in trades if t.selected),
            hit_rate=hit_rate(trades),
            average_realized_irr=average_realized_irr(trades),
            average_model_score=average_score(trades),
            ending_equity=portfolio.equity,
        )
