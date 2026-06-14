# ADR 0002: Keep Core Production Utilities Stdlib-Only

## Status

Accepted

## Context

The project should run tests and production-readiness checks without requiring every optional API, frontend, or observability package.

## Decision

The production settings, auth, audit, readiness, model-risk, and health utilities use Python standard library APIs. FastAPI integration remains optional under `app/backend`.

## Consequences

- CI can run fast and deterministically.
- Optional production dependencies are isolated.
- Teams can replace the provided auth, audit, and metrics adapters with platform services later.
