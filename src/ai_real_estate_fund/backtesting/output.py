from __future__ import annotations
from .models import BacktestResult


def backtest_markdown(result: BacktestResult) -> str:
    lines = [
        "# Real Estate Committee Backtest",
        "",
        f"Selected deals: {result.selected_count}",
        f"Hit rate: {result.hit_rate:.1%}",
        f"Average realized IRR: {result.average_realized_irr:.1%}",
        f"Average model score: {result.average_model_score:.1f}",
        f"Ending equity: ${result.ending_equity:,.0f}",
        "",
        "| Deal | Selected | Score | Recommendation | Realized IRR |",
        "|---|---:|---:|---|---:|",
    ]
    for trade in result.trades:
        lines.append(
            f"| {trade.deal_name} | {trade.selected} | {trade.score:.1f} | "
            f"{trade.recommendation} | {trade.realized_irr:.1%} |"
        )
    return "\n".join(lines) + "\n"
