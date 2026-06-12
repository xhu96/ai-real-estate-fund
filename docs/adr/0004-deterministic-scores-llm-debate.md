# ADR 0004: Deterministic Scores, LLM Debate

## Status

Accepted

## Context

The project needs both defensible numbers and useful qualitative reasoning. Fully LLM-scored committees are not reproducible or testable; fully rule-based memos miss the analyst-judgment layer that makes a memo worth reading.

## Decision

Scoring, policy gates, and recommendations are computed by the deterministic engine. LLM analyst personas run afterwards, receive a closed fact pack derived from the decision object, and attach commentary (`llm_review`). The LLM layer is optional, off by default, and cannot modify any computed value.

## Consequences

- CI and tests stay offline and deterministic; the LLM path is tested with a fake client.
- A hallucination can corrupt narrative but never a score, gate, or recommendation.
- Any OpenAI-compatible endpoint works (NVIDIA catalog default); model choice is a config concern.
- Commentary quality depends on the fact pack; extending it is the main lever for better debate.
