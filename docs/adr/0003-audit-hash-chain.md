# ADR 0003: SQLite Audit Hash Chain

## Status

Accepted

## Context

The project needs an audit trail that works locally and in small deployments without external infrastructure.

## Decision

Use an append-only SQLite table with `previous_hash` and `event_hash`. Tampering can be detected by `python -m ai_real_estate_fund audit-verify`.

## Consequences

- Local demos and staging deployments have auditability by default.
- Multi-instance production should migrate audit events to managed append-only storage or a SIEM pipeline.
