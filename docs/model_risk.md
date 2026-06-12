# Model Risk Management

A production investment workflow should include:

- model inventory and owner
- approved use cases and prohibited use cases
- validation evidence and calibration tests
- data lineage and data-quality thresholds
- human approval gates
- audit logs for inputs, prompts, outputs, and final decisions
- periodic drift and backtest reviews

For the LLM analyst layer specifically:

- LLM output is commentary only; deterministic scores and recommendations are computed before any model call and never altered.
- Analysts receive a closed fact pack (metrics, scorecards, gates, scenarios, top/bottom workstreams); prompts instruct grounding in those numbers, and the memo labels the section as model-generated.
- Model id and generation timestamp are recorded in `llm_review` for every run; treat commentary as unverified narrative until a human checks it against the scored evidence.
- The offline client keeps tests and CI fully deterministic.

This repository includes starter validation utilities, but they are not a substitute for formal governance.
