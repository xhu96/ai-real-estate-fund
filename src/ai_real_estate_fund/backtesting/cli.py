from __future__ import annotations
import argparse
from .engine import BacktestEngine
from .fixtures import example_historical_deals
from .output import backtest_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the real estate committee fixture backtest.")
    parser.add_argument("--examples", default="examples/properties.csv")
    args = parser.parse_args(argv)
    result = BacktestEngine().run(example_historical_deals(args.examples))
    print(backtest_markdown(result))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
