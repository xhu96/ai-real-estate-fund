# Agent Registry

The screening committee includes pricing, comps, cash-flow, expense, debt, tax, insurance, reserves, renovation, condition, market, neighborhood, tenant-demand, lease-up, regulatory, environmental, legal, appreciation, exit, operations, sponsor-fit, data-quality, stress, risk, bull-case, bear-case, portfolio, and IC-chair agents.

Each agent returns a structured `AgentFinding` with score, recommendation, confidence, thesis, positives, concerns, evidence, and actions.

## LLM analysts

On top of the deterministic workstreams, four optional LLM personas (Bull Advocate, Bear Advocate, Risk Officer, IC Chair) debate the committee's fact pack — see `src/ai_real_estate_fund/institutional/analysts.py`. Enable with `--llm` on the CLI or `?llm=true` on the API; choose NVIDIA, OpenAI, Anthropic, or Gemini with `--llm-provider` / `LLM_PROVIDER`. Commentary is attached as `llm_review` and rendered in the memo; scores are never model-generated.
