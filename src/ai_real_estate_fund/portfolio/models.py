from __future__ import annotations
from dataclasses import asdict, dataclass, field

@dataclass(slots=True)
class AllocationCandidate:
    name: str
    market: str
    score: float
    risk_score: float
    required_equity: float
    expected_irr: float | None
    cash_on_cash_return: float
    cap_rate: float
    recommendation: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

@dataclass(slots=True)
class PortfolioConstraints:
    total_equity_budget: float
    max_single_asset_pct: float = 0.20
    max_market_pct: float = 0.35
    min_score: float = 60.0
    min_risk_score: float = 55.0
    reserve_rate: float = 0.05

@dataclass(slots=True)
class PortfolioPlan:
    selected: list[AllocationCandidate] = field(default_factory=list)
    rejected: list[AllocationCandidate] = field(default_factory=list)
    equity_used: float = 0.0
    reserves: float = 0.0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "selected": [c.to_dict() for c in self.selected],
            "rejected": [c.to_dict() for c in self.rejected],
            "equity_used": self.equity_used,
            "reserves": self.reserves,
            "notes": self.notes,
        }
