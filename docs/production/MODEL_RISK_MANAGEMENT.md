# Model Risk Management

The production layer includes model-risk checks, but it does not replace human underwriting oversight.

## Controls included

- Every decision payload must carry a no-advice educational disclaimer.
- Hard policy stops are exposed in the API response.
- Scores are normalized to `[0, 100]`.
- Agent findings are included for auditability.
- BUY recommendations require a human approval gate by default.
- Production readiness warns when human approval is disabled.

## Controls required before real use

- Outcome backtesting on historical acquisitions.
- Calibration review by deal type and market.
- Independent validation of formulas and assumptions.
- Data-source license review.
- Override and exception governance.
- Periodic drift monitoring.
- Formal approval by investment, legal, tax, lending, and compliance stakeholders.
