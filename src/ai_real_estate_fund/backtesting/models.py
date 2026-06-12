from __future__ import annotations
from dataclasses import asdict, dataclass, field
from ..models import PropertyInput

@dataclass(slots=True)
class HistoricalDeal:
    property: PropertyInput
    acquisition_date: str
    exit_date: str
    realized_irr: float
    realized_equity_multiple: float
    realized_default: bool = False
    notes: str = ""

@dataclass(slots=True)
class BacktestConfig:
    min_score: float = 65.0
    starting_equity: float = 1_000_000.0
    max_positions: int = 10
    allocation_per_deal: float = 0.10

@dataclass(slots=True)
class BacktestTrade:
    deal_name: str
    selected: bool
    score: float
    recommendation: str
    expected_irr: float | None
    realized_irr: float
    realized_equity_multiple: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

@dataclass(slots=True)
class BacktestResult:
    trades: list[BacktestTrade] = field(default_factory=list)
    selected_count: int = 0
    hit_rate: float = 0.0
    average_realized_irr: float = 0.0
    average_model_score: float = 0.0
    ending_equity: float = 0.0

    def to_dict(self) -> dict[str, object]:
        return {
            "trades": [t.to_dict() for t in self.trades],
            "selected_count": self.selected_count,
            "hit_rate": self.hit_rate,
            "average_realized_irr": self.average_realized_irr,
            "average_model_score": self.average_model_score,
            "ending_equity": self.ending_equity,
        }
