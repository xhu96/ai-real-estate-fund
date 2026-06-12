# Backtesting

The backtesting package simulates how the committee would have selected historical deals and compares model selection against realized IRR and equity multiple.

```bash
python -m ai_real_estate_fund.backtesting.cli --examples examples/properties.csv
```

Fixture backtests are illustrative only. A serious validation program needs a real historical deal warehouse, clean timestamps, survivorship-bias controls, and out-of-sample testing.
