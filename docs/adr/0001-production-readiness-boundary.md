# ADR 0001: Production Readiness Boundary

## Status

Accepted

## Context

The project is a real estate diligence system. Users may ask whether it is production-ready. Software operations can be hardened, but investment production readiness requires professional review, data licensing, legal/tax/lending controls, and model governance.

## Decision

The repository will target production-grade software operations while explicitly preserving no-advice language and human approval controls. The `readiness` command gates software deployment readiness and flags investment-specific limitations.

## Consequences

- The API can be deployed, monitored, and audited.
- Outputs remain decision-support artifacts, not automated investment instructions.
- Production deployments must keep `REQUIRE_HUMAN_APPROVAL_FOR_BUY=true` unless a separate governance process approves otherwise.
