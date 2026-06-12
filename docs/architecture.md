# Architecture

AI Real Estate Fund is split into five layers:

1. **Core engine**: dataclasses, underwriting math, the deterministic workstream committee, policy gates, memo rendering.
2. **LLM analyst layer** (optional): four personas — Bull Advocate, Bear Advocate, Risk Officer, IC Chair — debate the committee's structured fact pack through NVIDIA (default), OpenAI, Anthropic, or Gemini — or any OpenAI-compatible endpoint. Analysts run sequentially so the Chair reacts to prior opinions. They attach commentary; they never modify scores.
3. **Research layer**: backtesting and historical-deal simulation over the screening committee.
4. **Service layer**: FastAPI routes, service classes, repositories, SQLite persistence, audit log.
5. **Interface layer**: CLI, React dashboard, Docker.

The split is deliberate: numbers come from rules (bit-identical reruns, testable), narrative comes from models (fragile assumptions, sponsor questions), and a model hallucination can never change a score. The fact pack handed to analysts is built only from the decision object, so every claim is checkable against the memo.
