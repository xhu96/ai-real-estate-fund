from __future__ import annotations
from .models import BacktestTrade


def hit_rate(trades: list[BacktestTrade]) -> float:
    selected = [t for t in trades if t.selected]
    if not selected:
        return 0.0
    return sum(1 for t in selected if t.realized_irr > 0) / len(selected)


def average_realized_irr(trades: list[BacktestTrade]) -> float:
    selected = [t.realized_irr for t in trades if t.selected]
    return sum(selected) / len(selected) if selected else 0.0


def average_score(trades: list[BacktestTrade]) -> float:
    selected = [t.score for t in trades if t.selected]
    return sum(selected) / len(selected) if selected else 0.0
