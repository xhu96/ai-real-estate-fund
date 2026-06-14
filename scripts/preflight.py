#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_real_estate_fund.production import ProductionReadinessChecker, ProductionSettings, render_readiness_markdown


def main() -> None:
    parser = argparse.ArgumentParser(description="Run production readiness checks.")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    report = ProductionReadinessChecker(root=args.root, settings=ProductionSettings.from_env()).run()
    print(json.dumps(report.to_dict(), indent=2) if args.json else render_readiness_markdown(report))
    if args.strict and not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
